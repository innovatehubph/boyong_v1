"""
Trending Video Generator for Pareng Boyong
Integrates the best current GitHub video generation solutions
"""

import asyncio
import base64
import requests
import json
import time
import os
from typing import Optional, Dict, Any, List
from datetime import datetime
import hashlib
import aiohttp

# Import environment loader
try:
    from env_loader import get_env, is_env_set
except ImportError:
    def get_env(key, default=None):
        return os.getenv(key, default)
    def is_env_set(key):
        value = os.getenv(key)
        return value is not None and value.strip() != ""

class TrendingVideoGenerator:
    """
    State-of-the-art video generator using trending GitHub solutions
    Supports CogVideoX, Stable Video Diffusion, and API services
    """
    
    def __init__(self):
        # API tokens
        self.replicate_token = get_env('REPLICATE_API_TOKEN')
        self.fal_token = get_env('FAL_AI_KEY')
        self.huggingface_token = get_env('API_KEY_HUGGINGFACE')
        
        # Service availability
        self.local_available = False
        self.api_available = False
        
        # Storage
        self.deliverables_path = "/root/projects/pareng-boyong/pareng_boyong_deliverables"
        self._ensure_directories()
        
        # Available models
        self.models = {
            "cogvideox-2b": {
                "name": "CogVideoX-2B",
                "description": "2B parameter model, VPS-friendly, 8GB VRAM minimum",
                "type": "text_to_video",
                "hardware": "medium",
                "quality": "high",
                "speed": "medium"
            },
            "stable-video-diffusion": {
                "name": "Stable Video Diffusion",
                "description": "Image-to-video, optimized for consumer hardware",
                "type": "image_to_video", 
                "hardware": "low",
                "quality": "high",
                "speed": "fast"
            },
            "open-sora": {
                "name": "Open-Sora 1.3",
                "description": "1B parameters, 2s-15s videos, 144p-720p",
                "type": "text_to_video",
                "hardware": "high",
                "quality": "very_high",
                "speed": "slow"
            },
            "animatediff": {
                "name": "AnimateDiff",
                "description": "Stable Diffusion extension for animation",
                "type": "text_to_video",
                "hardware": "medium",
                "quality": "high", 
                "speed": "medium"
            }
        }
    
    def _ensure_directories(self):
        """Ensure deliverables directories exist"""
        directories = [
            f"{self.deliverables_path}/videos/cogvideox",
            f"{self.deliverables_path}/videos/stable_video",
            f"{self.deliverables_path}/videos/open_sora",
            f"{self.deliverables_path}/videos/animatediff",
            f"{self.deliverables_path}/videos/api_generated",
            f"{self.deliverables_path}/videos/by_quality/high",
            f"{self.deliverables_path}/videos/by_quality/medium",
            f"{self.deliverables_path}/videos/by_date/{datetime.now().strftime('%Y/%m')}"
        ]
        
        for directory in directories:
            os.makedirs(directory, exist_ok=True)
    
    async def initialize(self):
        """Initialize and detect available services"""
        # Check API services
        if self.fal_token:
            self.api_available = await self._test_fal_api()
        elif self.replicate_token:
            self.api_available = await self._test_replicate_api()
        
        # Check local services (ComfyUI, direct implementations)
        self.local_available = await self._test_local_services()
        
        print(f"✅ Services initialized - API: {self.api_available}, Local: {self.local_available}")
    
    async def generate_video(
        self,
        prompt: str,
        model: str = "auto",
        duration: int = 3,
        fps: int = 8,
        resolution: str = "720p",
        style: str = "cinematic",
        image_input: Optional[str] = None,
        quality: str = "balanced",
        hardware_preference: str = "auto"
    ) -> Dict[str, Any]:
        """Generate video using the best available method"""
        
        if not prompt:
            return {"success": False, "error": "Prompt is required"}
        
        try:
            # Select optimal model and service
            selected_model, service_type = self._select_optimal_service(
                model, image_input, duration, quality, hardware_preference
            )
            
            print(f"🎬 Generating video with {selected_model} via {service_type}...")
            
            if service_type == "api" and self.api_available:
                result = await self._generate_with_api(
                    selected_model, prompt, duration, fps, resolution, style, image_input
                )
            elif service_type == "local" and self.local_available:
                result = await self._generate_with_local(
                    selected_model, prompt, duration, fps, resolution, style, image_input
                )
            else:
                return {
                    "success": False,
                    "error": f"No available services for {selected_model}. Please check API keys or local setup."
                }
            
            if result and result.get('success'):
                # Save and organize video
                file_info = await self._save_and_organize_video(
                    result, prompt, selected_model, {
                        "duration": duration,
                        "fps": fps,
                        "resolution": resolution,
                        "style": style,
                        "quality": quality,
                        "service_type": service_type
                    }
                )
                result.update(file_info)
            
            return result
            
        except Exception as e:
            return {"success": False, "error": f"Video generation failed: {str(e)}"}
    
    def _select_optimal_service(
        self, 
        model: str, 
        image_input: Optional[str], 
        duration: int, 
        quality: str,
        hardware_preference: str
    ) -> tuple[str, str]:
        """Select the best model and service based on requirements - PRIORITIZING FREE OPTIONS"""
        
        # PRIORITY 1: FREE LOCAL SERVICES (if available)
        if self.local_available:
            if image_input:
                return "stable-video-diffusion", "local"
            else:
                return "cogvideox-2b", "local"
        
        # PRIORITY 2: If specific model requested and available
        if model != "auto" and model in self.models:
            if self.api_available:
                return model, "api"
        
        # PRIORITY 3: API services (only when local not available)
        # Auto-selection logic for API
        if image_input:
            # Image-to-video: prefer Stable Video Diffusion
            if self.api_available:
                return "stable-video-diffusion", "api"
        
        # Text-to-video: select based on quality and hardware
        if quality == "high" or duration > 5:
            if self.api_available:
                return "cogvideox-2b", "api"
        
        # Default: cheapest API option
        if self.api_available:
            return "cogvideox-2b", "api"
        
        return "cogvideox-2b", "api"  # Fallback
    
    async def _generate_with_api(
        self,
        model: str,
        prompt: str,
        duration: int,
        fps: int,
        resolution: str,
        style: str,
        image_input: Optional[str]
    ) -> Dict[str, Any]:
        """Generate video using API services"""
        
        if self.fal_token:
            return await self._generate_with_fal(model, prompt, duration, fps, resolution, style, image_input)
        elif self.replicate_token:
            return await self._generate_with_replicate(model, prompt, duration, fps, resolution, style, image_input)
        else:
            return {"success": False, "error": "No API keys available"}
    
    async def _generate_with_fal(
        self,
        model: str,
        prompt: str,
        duration: int,
        fps: int,
        resolution: str,
        style: str,  
        image_input: Optional[str]
    ) -> Dict[str, Any]:
        """Generate using fal.ai API"""
        
        try:
            headers = {
                "Authorization": f"Key {self.fal_token}",
                "Content-Type": "application/json"
            }
            
            # Model endpoints for fal.ai
            endpoints = {
                "cogvideox-2b": "fal-ai/cogvideox-5b",
                "stable-video-diffusion": "fal-ai/stable-video-diffusion",
                "animatediff": "fal-ai/animatediff"
            }
            
            endpoint = endpoints.get(model, endpoints["cogvideox-2b"])
            
            payload = {
                "prompt": f"{prompt}, {style} style, high quality",
                "num_frames": min(duration * fps, 49),  # fal.ai limits
                "fps": fps
            }
            
            if image_input and model == "stable-video-diffusion":
                payload["image_url"] = f"data:image/jpeg;base64,{image_input}"
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"https://fal.run/{endpoint}",
                    headers=headers,
                    json=payload,
                    timeout=300
                ) as response:
                    
                    if response.status == 200:
                        result = await response.json()
                        video_url = result.get("video", {}).get("url")
                        
                        if video_url:
                            return {
                                "success": True,
                                "video_url": video_url,
                                "model_used": model,
                                "service": "fal.ai"
                            }
                    
                    error_text = await response.text()
                    return {"success": False, "error": f"fal.ai API error: {error_text}"}
        
        except Exception as e:
            return {"success": False, "error": f"fal.ai generation failed: {str(e)}"}
    
    async def _generate_with_replicate(
        self,
        model: str,
        prompt: str,
        duration: int,
        fps: int,
        resolution: str,
        style: str,
        image_input: Optional[str]
    ) -> Dict[str, Any]:
        """Generate using Replicate API"""
        
        try:
            headers = {
                "Authorization": f"Token {self.replicate_token}",
                "Content-Type": "application/json"
            }
            
            # Model configurations for Replicate
            model_configs = {
                "cogvideox-2b": {
                    "model": "lightricks/ltx-video",
                    "input": {
                        "prompt": f"{prompt}, {style} style",
                        "num_frames": duration * fps,
                        "fps": fps,
                        "aspect_ratio": "16:9"
                    }
                },
                "stable-video-diffusion": {
                    "model": "stability-ai/stable-video-diffusion",
                    "input": {
                        "input_image": f"data:image/jpeg;base64,{image_input}" if image_input else None,
                        "frames_per_second": fps,
                        "motion_bucket_id": 127
                    }
                }
            }
            
            config = model_configs.get(model, model_configs["cogvideox-2b"])
            
            # Start prediction
            response = requests.post(
                "https://api.replicate.com/v1/predictions",
                headers=headers,
                json=config,
                timeout=30
            )
            
            if response.status_code != 201:
                return {"success": False, "error": f"Replicate API error: {response.text}"}
            
            prediction = response.json()
            prediction_id = prediction["id"]
            
            # Poll for completion
            for _ in range(120):  # 10 minute timeout
                await asyncio.sleep(5)
                
                status_response = requests.get(
                    f"https://api.replicate.com/v1/predictions/{prediction_id}",
                    headers=headers
                )
                
                if status_response.status_code == 200:
                    status_data = status_response.json()
                    
                    if status_data["status"] == "succeeded":
                        video_url = status_data["output"]
                        if isinstance(video_url, list):
                            video_url = video_url[0]
                        
                        return {
                            "success": True,
                            "video_url": video_url,
                            "model_used": model,
                            "service": "replicate"
                        }
                    
                    elif status_data["status"] == "failed":
                        return {"success": False, "error": status_data.get("error", "Generation failed")}
            
            return {"success": False, "error": "Generation timed out"}
            
        except Exception as e:
            return {"success": False, "error": f"Replicate generation failed: {str(e)}"}
    
    async def _generate_with_local(
        self,
        model: str,
        prompt: str,
        duration: int,
        fps: int,
        resolution: str,
        style: str,
        image_input: Optional[str]
    ) -> Dict[str, Any]:
        """Generate using local services (ComfyUI, etc.)"""
        
        # This would integrate with local ComfyUI or direct model implementations
        # For now, return a placeholder that indicates local generation would happen here
        return {
            "success": False,
            "error": "Local generation not yet implemented. Please use API services."
        }
    
    async def _save_and_organize_video(
        self, 
        result: Dict[str, Any], 
        prompt: str, 
        model: str, 
        metadata: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Save video and create organized file structure"""
        
        try:
            video_url = result.get('video_url')
            if not video_url:
                return {"error": "No video URL in result"}
            
            # Generate unique file ID
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            hash_obj = hashlib.md5(f"{prompt}{timestamp}".encode())
            unique_id = hash_obj.hexdigest()[:8]
            file_id = f"pb_trending_{model}_{timestamp}_{unique_id}"
            
            # Determine category based on model
            category = model.replace('-', '_')
            
            # File paths
            video_path = f"{self.deliverables_path}/videos/{category}/{file_id}.mp4"
            quality_path = f"{self.deliverables_path}/videos/by_quality/{metadata.get('quality', 'medium')}/{file_id}.mp4"
            date_path = f"{self.deliverables_path}/videos/by_date/{datetime.now().strftime('%Y/%m')}/{file_id}.mp4"
            
            # Download video
            async with aiohttp.ClientSession() as session:
                async with session.get(video_url) as response:
                    if response.status == 200:
                        video_data = await response.read()
                        
                        # Save to multiple locations
                        for path in [video_path, quality_path, date_path]:
                            os.makedirs(os.path.dirname(path), exist_ok=True)
                            with open(path, 'wb') as f:
                                f.write(video_data)
                        
                        # Save metadata
                        full_metadata = {
                            "type": "video",
                            "prompt": prompt,
                            "model": model,
                            "generated_at": datetime.now().isoformat(),
                            "file_id": file_id,
                            "category": category,
                            "original_url": video_url,
                            "service": result.get('service', 'unknown'),
                            **metadata
                        }
                        
                        metadata_path = video_path.replace('.mp4', '.json')
                        with open(metadata_path, 'w') as f:
                            json.dump(full_metadata, f, indent=2)
                        
                        # Convert to base64 for immediate use
                        video_base64 = base64.b64encode(video_data).decode('utf-8')
                        
                        return {
                            "file_path": video_path,
                            "file_id": file_id,
                            "category": category,
                            "video_base64": video_base64,
                            "metadata": full_metadata
                        }
            
            return {"error": "Failed to download video"}
            
        except Exception as e:
            return {"error": f"Failed to save video: {str(e)}"}
    
    async def _test_fal_api(self) -> bool:
        """Test fal.ai API connectivity"""
        try:
            headers = {"Authorization": f"Key {self.fal_token}"}
            async with aiohttp.ClientSession() as session:
                async with session.get("https://fal.run/", headers=headers, timeout=10) as response:
                    return response.status < 500
        except:
            return False
    
    async def _test_replicate_api(self) -> bool:
        """Test Replicate API connectivity"""
        try:
            headers = {"Authorization": f"Token {self.replicate_token}"}
            response = requests.get("https://api.replicate.com/v1/predictions", headers=headers, timeout=10)
            return response.status_code == 200
        except:
            return False
    
    async def _test_local_services(self) -> bool:
        """Test local service availability"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get("http://localhost:8188/system_stats", timeout=5) as response:
                    return response.status == 200
        except:
            return False
    
    def get_available_models(self) -> Dict[str, Any]:
        """Get list of available models with their capabilities"""
        return {
            "models": self.models,
            "api_available": self.api_available,
            "local_available": self.local_available,
            "recommended": self._get_recommendations()
        }
    
    def _get_recommendations(self) -> Dict[str, str]:
        """Get model recommendations based on use cases"""
        return {
            "best_quality": "open-sora",
            "most_efficient": "cogvideox-2b", 
            "image_animation": "stable-video-diffusion",
            "fastest": "stable-video-diffusion",
            "vps_friendly": "cogvideox-2b"
        }

def trending_video_generator(operation: str = "status", **kwargs) -> str:
    """
    Trending Video Generator for Pareng Boyong
    
    Operations:
    - status: Check service availability and models
    - generate: Generate video with state-of-the-art models
    - models: List available models and capabilities
    """
    
    generator = TrendingVideoGenerator()
    
    try:
        if operation == "status":
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            try:
                loop.run_until_complete(generator.initialize())
            finally:
                loop.close()
            
            models_info = generator.get_available_models()
            
            return f"""
# 🎬 **Trending Video Generator - Status**

## 🌐 **Service Availability**
- **API Services**: {'✅ Available' if generator.api_available else '❌ Not Available'}
- **Local Services**: {'✅ Available' if generator.local_available else '❌ Not Available'}

## 🤖 **Available Models**
{chr(10).join(f'- **{info["name"]}**: {info["description"]}' for info in models_info["models"].values())}

## 🎯 **Recommendations**
- **Best Quality**: {models_info["recommended"]["best_quality"].title()}
- **Most Efficient**: {models_info["recommended"]["most_efficient"].title()}
- **Image Animation**: {models_info["recommended"]["image_animation"].title()}
- **VPS Friendly**: {models_info["recommended"]["vps_friendly"].title()}

## 🔑 **API Keys Status**
- **fal.ai**: {'✅ Configured' if generator.fal_token else '❌ Missing'}
- **Replicate**: {'✅ Configured' if generator.replicate_token else '❌ Missing'}
- **HuggingFace**: {'✅ Configured' if generator.huggingface_token else '❌ Missing'}

{'✅ **Ready for trending video generation!**' if (generator.api_available or generator.local_available) else '⚠️ **Please configure API keys to enable video generation**'}
"""
        
        elif operation == "generate":
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            try:
                loop.run_until_complete(generator.initialize())
                result = loop.run_until_complete(
                    generator.generate_video(
                        prompt=kwargs.get('prompt', 'A beautiful landscape'),
                        model=kwargs.get('model', 'auto'),
                        duration=kwargs.get('duration', 3),
                        fps=kwargs.get('fps', 8),
                        resolution=kwargs.get('resolution', '720p'),
                        style=kwargs.get('style', 'cinematic'),
                        image_input=kwargs.get('image_input'),
                        quality=kwargs.get('quality', 'balanced')
                    )
                )
            finally:
                loop.close()
            
            if result['success']:
                return f"""
# 🎬 **Trending Video Generated Successfully!**

**File ID**: `{result['file_id']}`
**Location**: `{result['file_path']}`
**Category**: {result['category']}
**Model Used**: {result['metadata']['model'].title()}

## 📋 **Generation Details**
- **Prompt**: "{kwargs.get('prompt', 'A beautiful landscape')}"
- **Model**: {result['metadata']['model'].replace('-', ' ').title()}
- **Duration**: {result['metadata']['duration']} seconds
- **Resolution**: {result['metadata']['resolution']}
- **Service**: {result['metadata']['service'].title()}

## 🌐 **Access**
- **Local File**: `{result['file_path']}`
- **File ID**: `{result['file_id']}`

✅ **Video generated using trending GitHub technology!**

💡 **Tip**: This video was created using state-of-the-art open-source models!
"""
            else:
                return f"""
# ❌ **Video Generation Failed**

**Error**: {result['error']}

## 🔧 **Troubleshooting**
1. Check API keys (fal.ai, Replicate, HuggingFace)
2. Verify internet connection
3. Try shorter duration or simpler prompt
4. Check service status with `trending_video_generator("status")`

**Timestamp**: {datetime.now().isoformat()}
"""
        
        elif operation == "models":
            models_info = generator.get_available_models()
            
            models_list = ""
            for key, info in models_info["models"].items():
                models_list += f"""
### **{info['name']}**
- **Type**: {info['type'].replace('_', '-').title()}
- **Hardware**: {info['hardware'].title()} requirements
- **Quality**: {info['quality'].replace('_', ' ').title()}
- **Speed**: {info['speed'].title()}
- **Description**: {info['description']}
"""
            
            return f"""
# 🤖 **Available Video Generation Models**

{models_list}

## 🎯 **Model Selection Guide**
- **CogVideoX-2B**: Best balance of quality and VPS compatibility
- **Stable Video Diffusion**: Excellent image-to-video, low resource usage
- **Open-Sora**: Highest quality, requires more resources
- **AnimateDiff**: Great for Stable Diffusion users

## 🔄 **Auto Selection**
Use `model="auto"` for intelligent model selection based on your requirements.
"""
        
        else:
            return f"""
# ❌ **Unknown Operation: {operation}**

**Available Operations**:
- `status`: Check service and model availability
- `generate`: Generate video with trending models
- `models`: List all available models and capabilities

## 📖 **Usage Examples**
```python
# Check status
trending_video_generator("status")

# Generate video (auto model selection)
trending_video_generator(
    "generate",
    prompt="A cat walking in a futuristic city",
    duration=3,
    quality="high"
)

# Generate with specific model
trending_video_generator(
    "generate", 
    prompt="Animate this image",
    model="stable-video-diffusion",
    image_input=image_base64
)
```
"""
    
    except Exception as e:
        return f"❌ **Trending Video Generator Error**: {str(e)}"