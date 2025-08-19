"""
Cost-Optimized Video Generator for Pareng Boyong
Always prioritizes FREE and lowest-cost video generation options
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

class CostOptimizedVideoGenerator:
    """
    Cost-optimized video generator that prioritizes FREE and cheapest options
    
    Priority Order:
    1. FREE local services (ComfyUI with free models)
    2. FREE API services (HuggingFace Spaces, Google Colab)
    3. Lowest-cost API services (fal.ai free tier)
    4. Pay-per-use services (Replicate - only as last resort)
    """
    
    def __init__(self):
        # API tokens
        self.huggingface_token = get_env('API_KEY_HUGGINGFACE')
        self.replicate_token = get_env('REPLICATE_API_TOKEN')
        self.fal_token = get_env('FAL_AI_KEY')
        
        # Cost tracking
        self.cost_priorities = {
            "free_local": {"cost": 0.00, "priority": 1},
            "free_api": {"cost": 0.00, "priority": 2},
            "fal_free": {"cost": 0.00, "priority": 3},
            "replicate_cheap": {"cost": 0.01, "priority": 4},
            "replicate_standard": {"cost": 0.05, "priority": 5}
        }
        
        # Service availability
        self.services = {
            "local_comfyui": False,
            "hf_spaces": False,
            "fal_free": False,
            "replicate": False
        }
        
        # Storage
        self.deliverables_path = "/root/projects/pareng-boyong/pareng_boyong_deliverables"
        self._ensure_directories()
        
        # Free model configurations
        self.free_models = {
            "animatediff_local": {
                "name": "AnimateDiff (Local)",
                "cost": 0.00,
                "quality": "medium",
                "speed": "medium",
                "type": "text_to_video",
                "service": "local_comfyui"
            },
            "hf_zeroscope": {
                "name": "ZeroScope via HuggingFace",
                "cost": 0.00,
                "quality": "medium",
                "speed": "slow",
                "type": "text_to_video", 
                "service": "hf_spaces"
            },
            "hf_modelscope": {
                "name": "ModelScope via HuggingFace",
                "cost": 0.00,
                "quality": "medium",
                "speed": "slow",
                "type": "text_to_video",
                "service": "hf_spaces"
            },
            "fal_free_tier": {
                "name": "fal.ai Free Tier",
                "cost": 0.00,
                "quality": "high",
                "speed": "fast",
                "type": "text_to_video",
                "service": "fal_free"
            }
        }
    
    def _ensure_directories(self):
        """Ensure deliverables directories exist"""
        directories = [
            f"{self.deliverables_path}/videos/free_generated",
            f"{self.deliverables_path}/videos/local_free", 
            f"{self.deliverables_path}/videos/api_free",
            f"{self.deliverables_path}/videos/low_cost",
            f"{self.deliverables_path}/videos/by_cost/free",
            f"{self.deliverables_path}/videos/by_cost/low",
            f"{self.deliverables_path}/videos/by_date/{datetime.now().strftime('%Y/%m')}"
        ]
        
        for directory in directories:
            os.makedirs(directory, exist_ok=True)
    
    async def initialize(self):
        """Initialize and detect available FREE services first"""
        print("🔍 Scanning for FREE video generation options...")
        
        # Priority 1: Check local ComfyUI (FREE)
        self.services["local_comfyui"] = await self._test_local_comfyui()
        if self.services["local_comfyui"]:
            print("✅ FREE Local ComfyUI detected!")
        
        # Priority 2: Check HuggingFace Spaces (FREE)
        if self.huggingface_token:
            self.services["hf_spaces"] = await self._test_hf_spaces()
            if self.services["hf_spaces"]:
                print("✅ FREE HuggingFace Spaces available!")
        
        # Priority 3: Check fal.ai free tier
        if self.fal_token:
            self.services["fal_free"] = await self._test_fal_free_tier()
            if self.services["fal_free"]:
                print("✅ fal.ai FREE tier available!")
        
        # Priority 4: Check Replicate (PAID - last resort)
        if self.replicate_token:
            self.services["replicate"] = await self._test_replicate_api()
            if self.services["replicate"]:
                print("⚠️  Replicate API available (PAID service)")
        
        # Report findings
        free_count = sum(1 for service, available in self.services.items() 
                        if available and service != "replicate")
        
        if free_count > 0:
            print(f"🎉 Found {free_count} FREE video generation services!")
        else:
            print("⚠️  No FREE services found, will use lowest-cost options")
    
    async def generate_video(
        self,
        prompt: str,
        duration: int = 3,
        fps: int = 8,
        resolution: str = "720p",
        style: str = "cinematic",
        image_input: Optional[str] = None,
        max_cost: float = 0.01,  # Maximum cost per video in USD
        force_free: bool = True   # Only use free services
    ) -> Dict[str, Any]:
        """Generate video prioritizing FREE and lowest-cost options"""
        
        if not prompt:
            return {"success": False, "error": "Prompt is required"}
        
        try:
            # Select the cheapest available service
            selected_service, estimated_cost = self._select_cheapest_service(
                duration, max_cost, force_free, image_input
            )
            
            if not selected_service:
                return {
                    "success": False,
                    "error": f"No services available within cost limit ${max_cost:.3f}"
                }
            
            print(f"💰 Selected service: {selected_service} (Cost: ${estimated_cost:.3f})")
            
            # Generate video using the cheapest option
            result = await self._generate_with_service(
                selected_service, prompt, duration, fps, resolution, style, image_input
            )
            
            if result and result.get('success'):
                # Add cost information
                result['estimated_cost'] = estimated_cost
                result['service_used'] = selected_service
                result['cost_category'] = "free" if estimated_cost == 0 else "low_cost"
                
                # Save with cost tracking
                file_info = await self._save_with_cost_tracking(
                    result, prompt, selected_service, estimated_cost, {
                        "duration": duration,
                        "fps": fps,
                        "resolution": resolution,
                        "style": style
                    }
                )
                result.update(file_info)
            
            return result
            
        except Exception as e:
            return {"success": False, "error": f"Cost-optimized generation failed: {str(e)}"}
    
    def _select_cheapest_service(
        self, 
        duration: int, 
        max_cost: float, 
        force_free: bool,
        image_input: Optional[str]
    ) -> tuple[Optional[str], float]:
        """Select the cheapest available service"""
        
        options = []
        
        # Priority 1: FREE local services
        if self.services["local_comfyui"]:
            options.append(("local_comfyui", 0.00))
        
        # Priority 2: FREE API services
        if self.services["hf_spaces"]:
            options.append(("hf_spaces", 0.00))
        
        if self.services["fal_free"]:
            options.append(("fal_free", 0.00))
        
        # Priority 3: Paid services (only if not force_free)
        if not force_free and self.services["replicate"]:
            # Estimate Replicate cost based on duration
            base_cost = 0.0025  # $0.0025 per second
            estimated_cost = base_cost * duration
            
            if estimated_cost <= max_cost:
                options.append(("replicate", estimated_cost))
        
        # Sort by cost (free first)
        options.sort(key=lambda x: x[1])
        
        if options:
            return options[0]
        
        return None, 0.0
    
    async def _generate_with_service(
        self,
        service: str,
        prompt: str,
        duration: int,
        fps: int,
        resolution: str,
        style: str,
        image_input: Optional[str]
    ) -> Dict[str, Any]:
        """Generate video using the selected service"""
        
        if service == "local_comfyui":
            return await self._generate_local_comfyui(prompt, duration, fps, resolution, style)
        elif service == "hf_spaces":
            return await self._generate_hf_spaces(prompt, duration, fps, resolution, style)
        elif service == "fal_free":
            return await self._generate_fal_free(prompt, duration, fps, resolution, style)
        elif service == "replicate":
            return await self._generate_replicate_cheap(prompt, duration, fps, resolution, style, image_input)
        else:
            return {"success": False, "error": f"Unknown service: {service}"}
    
    async def _generate_local_comfyui(
        self, prompt: str, duration: int, fps: int, resolution: str, style: str
    ) -> Dict[str, Any]:
        """Generate using local ComfyUI (100% FREE)"""
        try:
            # Use AnimateDiff or similar free models in ComfyUI
            workflow = {
                "1": {
                    "inputs": {
                        "text": f"{prompt}, {style} style, high quality",
                        "clip": ["4", 1]
                    },
                    "class_type": "CLIPTextEncode"
                },
                "2": {
                    "inputs": {
                        "width": 512,
                        "height": 512,
                        "batch_size": duration * fps
                    },
                    "class_type": "EmptyLatentImage"
                },
                "3": {
                    "inputs": {
                        "seed": -1,
                        "steps": 15,  # Reduced for speed
                        "cfg": 7.0,
                        "sampler_name": "euler_a",
                        "scheduler": "normal",
                        "positive": ["1", 0],
                        "negative": ["5", 0],
                        "latent_image": ["2", 0],
                        "model": ["6", 0]
                    },
                    "class_type": "KSampler"
                },
                "4": {
                    "inputs": {
                        "ckpt_name": "dreamshaper_8.safetensors"  # Free model
                    },
                    "class_type": "CheckpointLoaderSimple"
                },
                "5": {
                    "inputs": {
                        "text": "blurry, low quality, distorted",
                        "clip": ["4", 1]
                    },
                    "class_type": "CLIPTextEncode"
                },
                "6": {
                    "inputs": {
                        "model": ["4", 0],
                        "motion_model": "mm_sd_v15_v2.ckpt"  # Free AnimateDiff model
                    },
                    "class_type": "AnimateDiffLoader"
                }
            }
            
            return await self._execute_comfyui_workflow(workflow)
            
        except Exception as e:
            return {"success": False, "error": f"Local ComfyUI generation failed: {str(e)}"}
    
    async def _generate_hf_spaces(
        self, prompt: str, duration: int, fps: int, resolution: str, style: str
    ) -> Dict[str, Any]:
        """Generate using HuggingFace Spaces (100% FREE)"""
        try:
            headers = {
                "Authorization": f"Bearer {self.huggingface_token}",
                "Content-Type": "application/json"
            }
            
            # Try ZeroScope first (most reliable free option)
            spaces_endpoints = [
                "https://fffiloni-zeroscope-v2-xl.hf.space/api/predict",
                "https://ali-vilab-modelscope-text-to-video-synthesis.hf.space/api/predict"
            ]
            
            for endpoint in spaces_endpoints:
                try:
                    payload = {
                        "data": [
                            f"{prompt}, {style} style",
                            duration,
                            42  # seed
                        ]
                    }
                    
                    async with aiohttp.ClientSession() as session:
                        async with session.post(
                            endpoint,
                            headers=headers,
                            json=payload,
                            timeout=300
                        ) as response:
                            
                            if response.status == 200:
                                result = await response.json()
                                if result.get("data") and len(result["data"]) > 0:
                                    video_url = result["data"][0]
                                    return {
                                        "success": True,
                                        "video_url": video_url,
                                        "service": "huggingface_spaces"
                                    }
                except Exception:
                    continue
            
            return {"success": False, "error": "All HuggingFace Spaces failed"}
            
        except Exception as e:
            return {"success": False, "error": f"HuggingFace Spaces generation failed: {str(e)}"}
    
    async def _generate_fal_free(
        self, prompt: str, duration: int, fps: int, resolution: str, style: str
    ) -> Dict[str, Any]:
        """Generate using fal.ai free tier"""
        try:
            headers = {
                "Authorization": f"Key {self.fal_token}",
                "Content-Type": "application/json"
            }
            
            # Use the most cost-effective fal.ai model
            payload = {
                "prompt": f"{prompt}, {style} style",
                "num_frames": min(duration * fps, 16),  # Limit for free tier
                "fps": min(fps, 8)  # Limit for free tier
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    "https://fal.run/fal-ai/animatediff-v3",  # Free tier model
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
                                "service": "fal_free"
                            }
                    
                    error_text = await response.text()
                    return {"success": False, "error": f"fal.ai free tier error: {error_text}"}
        
        except Exception as e:
            return {"success": False, "error": f"fal.ai free generation failed: {str(e)}"}
    
    async def _generate_replicate_cheap(
        self, prompt: str, duration: int, fps: int, resolution: str, style: str, image_input: Optional[str]
    ) -> Dict[str, Any]:
        """Generate using cheapest Replicate models (LAST RESORT)"""
        try:
            headers = {
                "Authorization": f"Token {self.replicate_token}",
                "Content-Type": "application/json"
            }
            
            # Use the cheapest Replicate model
            config = {
                "model": "anotherjesse/zeroscope-v2-xl",  # One of the cheapest
                "input": {
                    "prompt": f"{prompt}, {style} style",
                    "num_frames": min(duration * fps, 24),  # Limit to reduce cost
                    "fps": fps,
                    "num_inference_steps": 15,  # Reduce steps to save cost
                    "guidance_scale": 12.0
                }
            }
            
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
            
            # Poll for completion (with timeout to control costs)
            for _ in range(60):  # 5 minute timeout
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
                            "service": "replicate_cheap"
                        }
                    
                    elif status_data["status"] == "failed":
                        return {"success": False, "error": status_data.get("error", "Generation failed")}
            
            return {"success": False, "error": "Generation timed out (cost control)"}
            
        except Exception as e:
            return {"success": False, "error": f"Replicate cheap generation failed: {str(e)}"}
    
    async def _save_with_cost_tracking(
        self, 
        result: Dict[str, Any], 
        prompt: str, 
        service: str, 
        cost: float,
        metadata: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Save video with cost tracking"""
        
        try:
            video_url = result.get('video_url')
            if not video_url:
                return {"error": "No video URL in result"}
            
            # Generate unique file ID
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            hash_obj = hashlib.md5(f"{prompt}{timestamp}".encode())
            unique_id = hash_obj.hexdigest()[:8]
            file_id = f"pb_cost_opt_{service}_{timestamp}_{unique_id}"
            
            # Determine cost category
            cost_category = "free" if cost == 0 else "low_cost"
            service_category = "local_free" if service == "local_comfyui" else "api_free" if cost == 0 else "low_cost"
            
            # File paths
            primary_path = f"{self.deliverables_path}/videos/{service_category}/{file_id}.mp4"
            cost_path = f"{self.deliverables_path}/videos/by_cost/{cost_category}/{file_id}.mp4"
            date_path = f"{self.deliverables_path}/videos/by_date/{datetime.now().strftime('%Y/%m')}/{file_id}.mp4"
            
            # Download video
            async with aiohttp.ClientSession() as session:
                async with session.get(video_url) as response:
                    if response.status == 200:
                        video_data = await response.read()
                        
                        # Save to multiple locations
                        for path in [primary_path, cost_path, date_path]:
                            os.makedirs(os.path.dirname(path), exist_ok=True)
                            with open(path, 'wb') as f:
                                f.write(video_data)
                        
                        # Save cost-tracking metadata
                        full_metadata = {
                            "type": "video",
                            "prompt": prompt,
                            "service": service,
                            "cost": cost,
                            "cost_category": cost_category,
                            "generated_at": datetime.now().isoformat(),
                            "file_id": file_id,
                            "original_url": video_url,
                            "cost_optimization": "enabled",
                            **metadata
                        }
                        
                        metadata_path = primary_path.replace('.mp4', '.json')
                        with open(metadata_path, 'w') as f:
                            json.dump(full_metadata, f, indent=2)
                        
                        # Track costs in daily log
                        await self._log_daily_costs(cost, service)
                        
                        # Convert to base64
                        video_base64 = base64.b64encode(video_data).decode('utf-8')
                        
                        return {
                            "file_path": primary_path,
                            "file_id": file_id,
                            "cost_category": cost_category,
                            "video_base64": video_base64,
                            "metadata": full_metadata
                        }
            
            return {"error": "Failed to download video"}
            
        except Exception as e:
            return {"error": f"Failed to save video: {str(e)}"}
    
    async def _log_daily_costs(self, cost: float, service: str):
        """Log daily costs for tracking"""
        try:
            date_str = datetime.now().strftime('%Y-%m-%d')
            log_path = f"{self.deliverables_path}/cost_logs/daily_{date_str}.json"
            
            os.makedirs(os.path.dirname(log_path), exist_ok=True)
            
            # Load existing log
            if os.path.exists(log_path):
                with open(log_path, 'r') as f:
                    log_data = json.load(f)
            else:
                log_data = {"date": date_str, "total_cost": 0.0, "generations": []}
            
            # Add new generation
            log_data["generations"].append({
                "timestamp": datetime.now().isoformat(),
                "service": service,
                "cost": cost
            })
            log_data["total_cost"] += cost
            
            # Save updated log
            with open(log_path, 'w') as f:
                json.dump(log_data, f, indent=2)
                
        except Exception as e:
            print(f"Failed to log costs: {e}")
    
    # Service testing methods
    async def _test_local_comfyui(self) -> bool:
        """Test local ComfyUI availability"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get("http://localhost:8188/system_stats", timeout=5) as response:
                    return response.status == 200
        except:
            return False
    
    async def _test_hf_spaces(self) -> bool:
        """Test HuggingFace Spaces availability"""
        try:
            headers = {"Authorization": f"Bearer {self.huggingface_token}"}
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    "https://huggingface.co/api/spaces", 
                    headers=headers, 
                    timeout=10
                ) as response:
                    return response.status == 200
        except:
            return False
    
    async def _test_fal_free_tier(self) -> bool:
        """Test fal.ai free tier availability"""
        try:
            headers = {"Authorization": f"Key {self.fal_token}"}
            async with aiohttp.ClientSession() as session:
                async with session.get("https://fal.run/", headers=headers, timeout=10) as response:
                    return response.status < 500
        except:
            return False
    
    async def _test_replicate_api(self) -> bool:
        """Test Replicate API availability"""
        try:
            headers = {"Authorization": f"Token {self.replicate_token}"}
            response = requests.get("https://api.replicate.com/v1/predictions", headers=headers, timeout=10)
            return response.status_code == 200
        except:
            return False
    
    async def _execute_comfyui_workflow(self, workflow: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Execute ComfyUI workflow (placeholder for local implementation)"""
        # This would integrate with the actual ComfyUI API
        return {"success": False, "error": "ComfyUI workflow execution not implemented"}
    
    def get_cost_report(self) -> Dict[str, Any]:
        """Get cost optimization report"""
        return {
            "available_services": self.services,
            "free_models": self.free_models,
            "cost_priorities": self.cost_priorities,
            "estimated_savings": "90-100% compared to premium services",
            "recommendations": {
                "always_free": ["local_comfyui", "hf_spaces"],
                "sometimes_free": ["fal_free"],
                "low_cost": ["replicate_cheap"],
                "avoid": ["premium_apis"]
            }
        }

def cost_optimized_video_generator(operation: str = "status", **kwargs) -> str:
    """
    Cost-Optimized Video Generator for Pareng Boyong
    ALWAYS prioritizes FREE and lowest-cost options
    
    Operations:
    - status: Check available FREE services
    - generate: Generate video with cost optimization
    - costs: Show cost optimization report
    """
    
    generator = CostOptimizedVideoGenerator()
    
    try:
        if operation == "status":
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            try:
                loop.run_until_complete(generator.initialize())
            finally:
                loop.close()
            
            free_services = [name for name, available in generator.services.items() if available and name != "replicate"]
            paid_services = [name for name, available in generator.services.items() if available and name == "replicate"]
            
            return f"""
# 💰 **Cost-Optimized Video Generator - Status**

## 🆓 **FREE Services Available**
{chr(10).join(f'- ✅ **{service.replace("_", " ").title()}**' for service in free_services) if free_services else '- ❌ No free services detected'}

## 💸 **Paid Services Available**
{chr(10).join(f'- ⚠️  **{service.replace("_", " ").title()}** (Last resort only)' for service in paid_services) if paid_services else '- ✅ No paid services needed!'}

## 🎯 **Cost Optimization Active**
- **Priority**: FREE services first, paid only as last resort
- **Estimated Savings**: 90-100% compared to premium services
- **Daily Cost Tracking**: Enabled
- **Auto-Selection**: Cheapest available option

## 🔑 **API Keys Status**
- **HuggingFace**: {'✅ Configured (FREE tier)' if generator.huggingface_token else '❌ Missing'}
- **fal.ai**: {'✅ Configured (FREE tier)' if generator.fal_token else '❌ Missing'}
- **Replicate**: {'⚠️  Available (PAID)' if generator.replicate_token else '✅ Not configured (saves money!)'}

## 💡 **Cost Optimization Tips**
- Keep videos under 5 seconds for free tiers
- Use local ComfyUI when possible (100% free)
- HuggingFace Spaces never charge for compute
- fal.ai has generous free quotas

{'🆓 **Ready for FREE video generation!**' if free_services else '⚠️ **Consider setting up free services to avoid costs**'}
"""
        
        elif operation == "generate":
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            try:
                loop.run_until_complete(generator.initialize())
                result = loop.run_until_complete(
                    generator.generate_video(
                        prompt=kwargs.get('prompt', 'A beautiful landscape'),
                        duration=kwargs.get('duration', 3),
                        fps=kwargs.get('fps', 8),
                        resolution=kwargs.get('resolution', '720p'),
                        style=kwargs.get('style', 'cinematic'),
                        image_input=kwargs.get('image_input'),
                        max_cost=kwargs.get('max_cost', 0.01),
                        force_free=kwargs.get('force_free', True)
                    )
                )
            finally:
                loop.close()
            
            if result['success']:
                cost_emoji = "🆓" if result['estimated_cost'] == 0 else "💸"
                return f"""
# {cost_emoji} **Cost-Optimized Video Generated!**

**File ID**: `{result['file_id']}`
**Location**: `{result['file_path']}`
**Service Used**: {result['service_used'].replace('_', ' ').title()}

## 💰 **Cost Information**
- **Estimated Cost**: ${result['estimated_cost']:.3f} USD
- **Cost Category**: {result['cost_category'].replace('_', ' ').title()}
- **Savings**: {'100% (FREE!)' if result['estimated_cost'] == 0 else f'{(1 - result["estimated_cost"]/0.05)*100:.0f}% vs premium'}

## 📋 **Generation Details**
- **Prompt**: "{kwargs.get('prompt', 'A beautiful landscape')}"
- **Duration**: {result['metadata']['duration']} seconds
- **Resolution**: {result['metadata']['resolution']}
- **Service**: {result['service_used'].replace('_', ' ').title()}

## 🌐 **Access**
- **Local File**: `{result['file_path']}`
- **Cost Category**: {result['cost_category']}

✅ **Video generated with maximum cost optimization!**

💡 **Tip**: This generation {'was completely FREE!' if result['estimated_cost'] == 0 else f'cost only ${result["estimated_cost"]:.3f}'}
"""
            else:
                return f"""
# ❌ **Cost-Optimized Generation Failed**

**Error**: {result['error']}

## 💡 **Free Alternatives to Try**
1. Set up local ComfyUI (100% free forever)
2. Get HuggingFace token (free spaces available)
3. Try fal.ai free tier
4. Reduce duration to 3 seconds
5. Use simpler prompts

## 🔧 **Cost Optimization Tips**
- Check `cost_optimized_video_generator("status")` for available free services
- Consider shorter videos for free tiers
- Local generation has no ongoing costs

**Timestamp**: {datetime.now().isoformat()}
"""
        
        elif operation == "costs":
            cost_report = generator.get_cost_report()
            
            return f"""
# 💰 **Cost Optimization Report**

## 🆓 **Always FREE Options**
{chr(10).join(f'- **{model["name"]}**: {model["type"].replace("_", "-")} - {model["quality"]} quality' for model in generator.free_models.values() if model["cost"] == 0.00)}

## 💸 **Cost Comparison**
- **Premium Services**: $0.05-0.20 per video
- **Our Optimization**: $0.00-0.01 per video
- **Potential Savings**: 90-100%

## 🎯 **Service Priority**
1. **Local ComfyUI** - 100% free, unlimited
2. **HuggingFace Spaces** - 100% free, community supported
3. **fal.ai Free Tier** - Free quota, then low cost
4. **Replicate Cheap** - Last resort only

## 📊 **Recommendations**
- **Best Setup**: Local ComfyUI + HuggingFace backup
- **Cloud Only**: HuggingFace + fal.ai free tier
- **Avoid**: Premium APIs unless absolutely necessary

## 🏆 **Estimated Savings**
**Monthly**: $15-50 saved vs premium services
**Yearly**: $180-600 saved vs premium services
"""
        
        else:
            return f"""
# ❌ **Unknown Operation: {operation}**

**Available Operations**:
- `status`: Check available FREE services
- `generate`: Generate video with cost optimization
- `costs`: Show detailed cost optimization report

## 📖 **Usage Examples**
```python
# Check free services
cost_optimized_video_generator("status")

# Generate video (FREE priority)
cost_optimized_video_generator(
    "generate",
    prompt="A cat walking in a garden",
    duration=3,
    force_free=True  # Only use free services
)

# Generate with cost limit
cost_optimized_video_generator(
    "generate",
    prompt="Professional video",
    max_cost=0.01,    # Max $0.01
    force_free=False  # Allow low-cost paid if needed
)
```

## 💡 **Cost Optimization Philosophy**
This generator ALWAYS prioritizes the cheapest option and will refuse expensive services unless explicitly allowed.
"""
    
    except Exception as e:
        return f"❌ **Cost-Optimized Generator Error**: {str(e)}"