"""
Simple Video Generation Tool for Pareng Boyong
Uses cloud-based APIs for video generation to avoid heavy dependencies
"""

import asyncio
import base64
import requests
import json
import time
import os
from typing import Optional, Dict, Any
from datetime import datetime
import hashlib

# Import environment loader
try:
    from env_loader import get_env, is_env_set
except ImportError:
    def get_env(key, default=None):
        return os.getenv(key, default)
    def is_env_set(key):
        value = os.getenv(key)
        return value is not None and value.strip() != ""

class SimpleVideoGenerator:
    """
    Simple video generator using cloud APIs
    Provides fallback video generation when ComfyUI is not available
    """
    
    def __init__(self):
        self.replicate_token = get_env('REPLICATE_API_TOKEN')
        self.deliverables_path = "/root/projects/pareng-boyong/pareng_boyong_deliverables"
        self._ensure_directories()
    
    def _ensure_directories(self):
        """Ensure deliverables directories exist"""
        directories = [
            f"{self.deliverables_path}/videos/cinematic",
            f"{self.deliverables_path}/videos/conversational", 
            f"{self.deliverables_path}/videos/educational",
            f"{self.deliverables_path}/videos/marketing",
            f"{self.deliverables_path}/videos/social_media",
            f"{self.deliverables_path}/videos/animations",
            f"{self.deliverables_path}/videos/by_date/{datetime.now().strftime('%Y/%m')}"
        ]
        
        for directory in directories:
            os.makedirs(directory, exist_ok=True)
    
    def _generate_file_id(self, prompt: str) -> str:
        """Generate unique file ID"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        hash_obj = hashlib.md5(f"{prompt}{timestamp}".encode())
        unique_id = hash_obj.hexdigest()[:8]
        return f"pb_video_{timestamp}_{unique_id}"
    
    def _categorize_content(self, prompt: str, video_type: str) -> str:
        """Categorize content based on prompt and type"""
        prompt_lower = prompt.lower()
        
        if video_type == "conversational" or any(word in prompt_lower for word in ['conversation', 'dialogue', 'talking', 'discussion']):
            return 'conversational'
        elif any(word in prompt_lower for word in ['cinematic', 'film', 'dramatic', 'movie']):
            return 'cinematic'
        elif any(word in prompt_lower for word in ['educational', 'tutorial', 'learning', 'explain']):
            return 'educational'
        elif any(word in prompt_lower for word in ['marketing', 'advertisement', 'commercial', 'product']):
            return 'marketing'
        elif any(word in prompt_lower for word in ['social media', 'instagram', 'tiktok', 'short']):
            return 'social_media'
        elif any(word in prompt_lower for word in ['animation', 'cartoon', 'animate']):
            return 'animations'
        else:
            return 'cinematic'  # Default category
    
    async def generate_video(
        self, 
        prompt: str,
        duration: int = 5,
        fps: int = 24,
        resolution: str = "720p",
        style: str = "cinematic",
        video_type: str = "text_to_video",
        model_preference: str = "auto"
    ) -> Dict[str, Any]:
        """Generate video using cloud APIs"""
        
        if not self.replicate_token:
            return {
                "success": False,
                "error": "Replicate API token not found. Video generation requires API access."
            }
        
        try:
            # Select appropriate model based on requirements
            selected_model = self._select_model(video_type, style, duration, model_preference)
            
            # Generate video
            result = await self._generate_with_replicate(
                model=selected_model,
                prompt=prompt,
                duration=duration,
                fps=fps,
                resolution=resolution,
                style=style
            )
            
            if result and result.get('success'):
                # Save video and metadata
                file_id = self._generate_file_id(prompt)
                category = self._categorize_content(prompt, video_type)
                
                video_path = f"{self.deliverables_path}/videos/{category}/{file_id}.mp4"
                
                # Download and save video
                video_url = result['video_url']
                saved_path = await self._save_video_from_url(video_url, video_path, {
                    "type": "video",
                    "prompt": prompt,
                    "duration": duration,
                    "fps": fps,
                    "resolution": resolution,
                    "style": style,
                    "video_type": video_type,
                    "model": selected_model,
                    "generated_at": datetime.now().isoformat(),
                    "file_id": file_id,
                    "category": category,
                    "original_url": video_url
                })
                
                # Convert to base64 for response
                with open(saved_path, 'rb') as f:
                    video_base64 = base64.b64encode(f.read()).decode('utf-8')
                
                return {
                    "success": True,
                    "video_base64": video_base64,
                    "file_path": saved_path,
                    "file_id": file_id,
                    "category": category,
                    "video_url": video_url,
                    "message": f"Video generated successfully with {selected_model}: {category}/{file_id}.mp4"
                }
            else:
                return {
                    "success": False,
                    "error": result.get('error', 'Unknown error during video generation')
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": f"Video generation failed: {str(e)}"
            }
    
    def _select_model(self, video_type: str, style: str, duration: int, preference: str) -> str:
        """Select appropriate model for video generation"""
        
        if preference != "auto":
            return preference
        
        # Model selection based on requirements
        if video_type == "conversational" or style == "realistic":
            return "stable-video-diffusion"
        elif style == "cinematic" or duration > 5:
            return "zeroscope-v2"
        else:
            return "animatediff"  # Default
    
    async def _generate_with_replicate(
        self,
        model: str,
        prompt: str,
        duration: int,
        fps: int,
        resolution: str,
        style: str
    ) -> Dict[str, Any]:
        """Generate video using Replicate API"""
        
        try:
            headers = {
                "Authorization": f"Token {self.replicate_token}",
                "Content-Type": "application/json"
            }
            
            # Model-specific configurations
            model_configs = {
                "stable-video-diffusion": {
                    "model": "stability-ai/stable-video-diffusion",
                    "input": {
                        "input_image": prompt,  # This would need an image for SVD
                        "frames_per_second": fps,
                        "motion_bucket_id": 127
                    }
                },
                "zeroscope-v2": {
                    "model": "anotherjesse/zeroscope-v2-xl",
                    "input": {
                        "prompt": f"{prompt}, {style} style, high quality",
                        "num_frames": min(duration * fps, 24),  # ZeroScope limit
                        "fps": fps,
                        "num_inference_steps": 20,
                        "guidance_scale": 15.0
                    }
                },
                "animatediff": {
                    "model": "lucataco/animate-diff",
                    "input": {
                        "prompt": f"{prompt}, {style} style, smooth animation",
                        "num_frames": duration * fps,
                        "guidance_scale": 7.5,
                        "num_inference_steps": 25
                    }
                }
            }
            
            config = model_configs.get(model, model_configs["zeroscope-v2"])
            
            # Start prediction
            response = requests.post(
                f"https://api.replicate.com/v1/predictions",
                headers=headers,
                json=config,
                timeout=30
            )
            
            if response.status_code != 201:
                return {
                    "success": False,
                    "error": f"Failed to start prediction: {response.status_code} - {response.text}"
                }
            
            prediction = response.json()
            prediction_id = prediction["id"]
            
            # Poll for completion
            max_attempts = 120  # 10 minutes max wait
            for attempt in range(max_attempts):
                await asyncio.sleep(5)
                
                status_response = requests.get(
                    f"https://api.replicate.com/v1/predictions/{prediction_id}",
                    headers=headers,
                    timeout=10
                )
                
                if status_response.status_code != 200:
                    continue
                
                status_data = status_response.json()
                
                if status_data["status"] == "succeeded":
                    video_url = status_data["output"]
                    if isinstance(video_url, list):
                        video_url = video_url[0]
                    
                    return {
                        "success": True,
                        "video_url": video_url,
                        "prediction_id": prediction_id
                    }
                
                elif status_data["status"] == "failed":
                    error_msg = status_data.get("error", "Unknown error")
                    return {
                        "success": False,
                        "error": f"Video generation failed: {error_msg}"
                    }
                
                elif status_data["status"] in ["starting", "processing"]:
                    continue
                else:
                    return {
                        "success": False,
                        "error": f"Unexpected status: {status_data['status']}"
                    }
            
            return {
                "success": False,
                "error": "Video generation timed out after 10 minutes"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"API request failed: {str(e)}"
            }
    
    async def _save_video_from_url(self, video_url: str, file_path: str, metadata: Dict) -> str:
        """Download and save video from URL"""
        try:
            # Download video
            response = requests.get(video_url, timeout=60)
            response.raise_for_status()
            
            # Save video
            with open(file_path, 'wb') as f:
                f.write(response.content)
            
            # Save metadata
            metadata_path = file_path.replace('.mp4', '.json')
            with open(metadata_path, 'w') as f:
                json.dump(metadata, f, indent=2)
            
            # Create backup in date folder
            date_folder = f"{self.deliverables_path}/videos/by_date/{datetime.now().strftime('%Y/%m')}"
            os.makedirs(date_folder, exist_ok=True)
            backup_path = os.path.join(date_folder, os.path.basename(file_path))
            
            with open(backup_path, 'wb') as f:
                f.write(response.content)
            
            return file_path
        
        except Exception as e:
            raise Exception(f"Failed to save video: {str(e)}")
    
    def get_service_status(self) -> Dict[str, Any]:
        """Check service availability"""
        if not self.replicate_token:
            return {
                "available": False,
                "error": "Replicate API token not configured"
            }
        
        try:
            headers = {
                "Authorization": f"Token {self.replicate_token}",
                "Content-Type": "application/json"
            }
            
            # Test API connection
            response = requests.get(
                "https://api.replicate.com/v1/predictions",
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                return {
                    "available": True,
                    "models": ["zeroscope-v2", "stable-video-diffusion", "animatediff"],
                    "deliverables_path": self.deliverables_path,
                    "features": [
                        "Text-to-video generation",
                        "Multiple video styles",
                        "Customizable duration and FPS",
                        "Organized file storage",
                        "Automatic categorization"
                    ]
                }
            else:
                return {
                    "available": False,
                    "error": f"API error: {response.status_code}"
                }
        
        except Exception as e:
            return {
                "available": False,
                "error": f"Connection error: {str(e)}"
            }

def simple_video_generator(operation: str = "status", **kwargs) -> str:
    """
    Simple Video Generator for Pareng Boyong
    
    Operations:
    - status: Check service availability
    - generate: Generate video (prompt, duration, fps, resolution, style, video_type)
    """
    
    generator = SimpleVideoGenerator()
    
    try:
        if operation == "status":
            status = generator.get_service_status()
            
            if status["available"]:
                return f"""
# 🎬 **Simple Video Generator - Service Status**

## ✅ **Service Available**
- **Models**: {', '.join(status['models'])}
- **Features**: {len(status['features'])} capabilities

## 📁 **Storage Location**
**Deliverables**: `{status['deliverables_path']}`

## 🎯 **Capabilities**
{chr(10).join(f"- {feature}" for feature in status['features'])}

## 📊 **Available Models**
- **ZeroScope V2**: High-quality text-to-video (up to 3 seconds)
- **Stable Video Diffusion**: Image-to-video animation
- **AnimateDiff**: Smooth video animation

## 🎨 **Supported Styles**
- Cinematic, Realistic, Animated, Artistic

✅ **Ready for video generation!**
"""
            else:
                return f"""
# ❌ **Simple Video Generator - Service Error**

**Status**: Unavailable
**Error**: {status['error']}

## 🔧 **Troubleshooting**
1. Check if REPLICATE_API_TOKEN is set in .env file
2. Verify API token is valid
3. Check internet connection
4. Try again in a few minutes

**Current Token**: {'✅ Set' if generator.replicate_token else '❌ Missing'}
"""
        
        elif operation == "generate":
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            try:
                result = loop.run_until_complete(
                    generator.generate_video(
                        prompt=kwargs.get('prompt', 'A beautiful landscape'),
                        duration=kwargs.get('duration', 3),
                        fps=kwargs.get('fps', 8),
                        resolution=kwargs.get('resolution', '720p'),
                        style=kwargs.get('style', 'cinematic'),
                        video_type=kwargs.get('video_type', 'text_to_video'),
                        model_preference=kwargs.get('model_preference', 'auto')
                    )
                )
            finally:
                loop.close()
            
            if result['success']:
                return f"""
# 🎬 **Video Generated Successfully!**

**File ID**: `{result['file_id']}`
**Location**: `{result['file_path']}`
**Category**: {result['category']}

## 📋 **Generation Details**
- **Prompt**: "{kwargs.get('prompt', 'A beautiful landscape')}"
- **Duration**: {kwargs.get('duration', 3)} seconds
- **FPS**: {kwargs.get('fps', 8)}
- **Resolution**: {kwargs.get('resolution', '720p')}
- **Style**: {kwargs.get('style', 'cinematic')}

## 🌐 **Access**
- **Local File**: `{result['file_path']}`
- **Original URL**: [View Video]({result['video_url']})

✅ {result['message']}

💡 **Tip**: Video is automatically saved to organized folders and backed up by date!
"""
            else:
                return f"""
# ❌ **Video Generation Failed**

**Error**: {result['error']}

## 🔧 **Possible Solutions**
1. Check your prompt for content policy violations
2. Try a shorter duration (3 seconds recommended)
3. Verify API token is valid
4. Check internet connection
5. Try again with a simpler prompt

**Timestamp**: {datetime.now().isoformat()}
"""
        
        else:
            return f"""
# ❌ **Unknown Operation**

**Operation**: {operation}
**Available Operations**:
- `status`: Check service availability
- `generate`: Generate video

## 📖 **Usage Examples**
```python
# Check status
simple_video_generator(operation="status")

# Generate video
simple_video_generator(
    operation="generate",
    prompt="A cat walking in a garden",
    duration=3,
    fps=8,
    resolution="720p",
    style="cinematic"
)
```
"""
    
    except Exception as e:
        return f"❌ **Simple Video Generator Error**: {str(e)}"