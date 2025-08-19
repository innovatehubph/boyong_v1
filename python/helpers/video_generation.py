"""
Video Generation Helper for Pareng Boyong
Enhanced with Docker Wan2GP integration and fallback support
"""

import asyncio
import base64
import logging
from typing import Optional, Dict, Any
import aiohttp
import json
import tempfile
import os
from python.helpers.docker_multimedia_client import generate_video_with_docker
from python.helpers.print_style import PrintStyle

logger = logging.getLogger(__name__)

class VideoGenerator:
    def __init__(self):
        self.hunyuan_available = False
        self.cogvideo_available = False
        self.animatediff_available = False
        self.docker_available = False
        self.comfyui_url = None
        
    async def initialize(self):
        """Initialize and detect available video generation services"""
        # Check for Docker Wan2GP service first
        try:
            from python.helpers.docker_multimedia_client import check_docker_services
            services = await check_docker_services()
            self.docker_available = services.get('wan2gp', False)
            if self.docker_available:
                logger.info("✅ Docker Wan2GP service available")
                PrintStyle(font_color="green").print("✅ Docker Wan2GP service detected")
        except:
            logger.info("❌ Docker Wan2GP service not available")
        
        # Check for ComfyUI with video models
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get('http://localhost:8188/system_stats', timeout=5) as resp:
                    if resp.status == 200:
                        # Check for video models
                        async with session.get('http://localhost:8188/object_info') as model_resp:
                            if model_resp.status == 200:
                                models = await model_resp.json()
                                
                                # Check for specific video generation nodes
                                if any('CogVideoX' in str(models) for _ in [1]):
                                    self.cogvideo_available = True
                                    logger.info("✅ CogVideoX available")
                                    
                                if any('AnimateDiff' in str(models) for _ in [1]):
                                    self.animatediff_available = True
                                    logger.info("✅ AnimateDiff available")
                                    
                                if any('Hunyuan' in str(models) for _ in [1]):
                                    self.hunyuan_available = True
                                    logger.info("✅ HunyuanVideo available")
                                    
                        self.comfyui_url = 'http://localhost:8188'
        except Exception as e:
            logger.info(f"❌ Local video generation services not available: {e}")
    
    async def generate_video(
        self, 
        prompt: str, 
        duration: int = 6,  # seconds
        fps: int = 8,
        width: int = 720,
        height: int = 480,
        model_preference: str = "cogvideo"
    ) -> Optional[str]:
        """
        Generate video using available models with priority order:
        1. Docker Wan2GP service (preferred - CPU optimized)
        2. Local ComfyUI models (HunyuanVideo, CogVideoX, AnimateDiff)
        3. Fallback to basic generation if available
        Returns base64 encoded video or None if failed
        """
        
        # First priority: Docker Wan2GP service (CPU optimized and reliable)
        if self.docker_available:
            try:
                PrintStyle(font_color="cyan").print("🎬 Using Docker Wan2GP service...")
                
                # Map model preference to Wan2GP models
                wan2gp_model = self._map_model_to_wan2gp(model_preference)
                style = self._determine_video_style(prompt)
                motion_intensity = self._determine_motion_intensity(prompt)
                
                result = await generate_video_with_docker(
                    prompt=prompt,
                    model=wan2gp_model,
                    duration=duration,
                    fps=fps,
                    width=width,
                    height=height,
                    motion_intensity=motion_intensity,
                    style=style
                )
                
                if result:
                    PrintStyle(font_color="green").print("✅ Video generated with Docker Wan2GP")
                    return result
                else:
                    PrintStyle(font_color="yellow").print("⚠️ Docker Wan2GP failed, trying local services...")
                    
            except Exception as e:
                logger.warning(f"Docker Wan2GP failed: {e}")
                PrintStyle(font_color="yellow").print(f"⚠️ Docker service error, trying local alternatives...")
        
        # Second priority: Local ComfyUI models
        if model_preference == "hunyuan" and self.hunyuan_available:
            PrintStyle(font_color="cyan").print("🎬 Using local HunyuanVideo...")
            return await self._generate_with_hunyuan(prompt, duration, fps, width, height)
        elif model_preference == "cogvideo" and self.cogvideo_available:
            PrintStyle(font_color="cyan").print("🎬 Using local CogVideoX...")
            return await self._generate_with_cogvideo(prompt, duration, fps, width, height)
        elif self.animatediff_available:
            PrintStyle(font_color="cyan").print("🎬 Using local AnimateDiff...")
            return await self._generate_with_animatediff(prompt, duration, fps, width, height)
        else:
            PrintStyle(font_color="red").print("❌ No video generation services available")
            logger.error("No video generation services available")
            return None
    
    def _map_model_to_wan2gp(self, model_preference: str) -> str:
        """Map model preference to Wan2GP model"""
        model_mapping = {
            "hunyuan": "wan2gp",          # Use basic model for Hunyuan requests
            "cogvideo": "fusionix",       # Use cinematic model for CogVideo
            "animatediff": "wan2gp",      # Use basic model for AnimateDiff
            "wan2gp": "wan2gp",
            "fusionix": "fusionix", 
            "multitalk": "multitalk",
            "wan_vace_14b": "wan_vace_14b"
        }
        return model_mapping.get(model_preference.lower(), "wan2gp")
    
    def _determine_video_style(self, prompt: str) -> str:
        """Analyze prompt to determine appropriate video style"""
        prompt_lower = prompt.lower()
        
        if any(word in prompt_lower for word in ['cinematic', 'dramatic', 'epic', 'film', 'movie']):
            return "cinematic"
        elif any(word in prompt_lower for word in ['anime', 'manga', 'cartoon', 'animated']):
            return "anime"
        elif any(word in prompt_lower for word in ['realistic', 'real', 'photo', 'lifelike']):
            return "realistic"
        elif any(word in prompt_lower for word in ['art', 'artistic', 'creative', 'stylized']):
            return "artistic"
        elif any(word in prompt_lower for word in ['cartoon', 'comic', 'illustration']):
            return "cartoon"
        else:
            return "realistic"  # Default
    
    def _determine_motion_intensity(self, prompt: str) -> str:
        """Analyze prompt to determine motion intensity"""
        prompt_lower = prompt.lower()
        
        if any(word in prompt_lower for word in ['fast', 'quick', 'rapid', 'energetic', 'dynamic', 'action']):
            return "dynamic"
        elif any(word in prompt_lower for word in ['dramatic', 'intense', 'powerful', 'explosive']):
            return "dramatic"
        elif any(word in prompt_lower for word in ['slow', 'gentle', 'calm', 'peaceful', 'subtle']):
            return "minimal"
        else:
            return "moderate"  # Default
    
    async def animate_image(
        self, 
        image_base64: str, 
        prompt: str = "",
        duration: int = 4,
        fps: int = 8
    ) -> Optional[str]:
        """
        Animate an existing image using AnimateDiff
        """
        if not self.animatediff_available:
            logger.error("AnimateDiff not available for image animation")
            return None
            
        return await self._animate_with_animatediff(image_base64, prompt, duration, fps)
    
    async def _generate_with_cogvideo(self, prompt: str, duration: int, fps: int, width: int, height: int) -> Optional[str]:
        """Generate video using CogVideoX"""
        try:
            # CogVideoX workflow for ComfyUI
            workflow = {
                "1": {
                    "inputs": {
                        "prompt": prompt,
                        "num_videos_per_prompt": 1,
                        "num_inference_steps": 50,
                        "num_frames": duration * fps,
                        "guidance_scale": 6.0,
                        "width": width,
                        "height": height,
                        "fps": fps
                    },
                    "class_type": "CogVideoXText2Video"
                },
                "2": {
                    "inputs": {
                        "frames": ["1", 0],
                        "filename_prefix": "cogvideo",
                        "fps": fps,
                        "compress_level": 4
                    },
                    "class_type": "VHS_VideoCombine"
                }
            }
            
            return await self._execute_comfyui_workflow(workflow)
            
        except Exception as e:
            logger.error(f"CogVideoX generation failed: {e}")
            return None
    
    async def _generate_with_hunyuan(self, prompt: str, duration: int, fps: int, width: int, height: int) -> Optional[str]:
        """Generate video using HunyuanVideo"""
        try:
            # HunyuanVideo workflow
            workflow = {
                "1": {
                    "inputs": {
                        "prompt": prompt,
                        "negative_prompt": "blurry, low quality, distorted",
                        "num_frames": duration * fps,
                        "height": height,
                        "width": width,
                        "num_inference_steps": 30,
                        "guidance_scale": 6.0,
                        "fps": fps
                    },
                    "class_type": "HunyuanVideoText2Video"
                },
                "2": {
                    "inputs": {
                        "frames": ["1", 0],
                        "filename_prefix": "hunyuan",
                        "fps": fps,
                        "compress_level": 4
                    },
                    "class_type": "VHS_VideoCombine"
                }
            }
            
            return await self._execute_comfyui_workflow(workflow)
            
        except Exception as e:
            logger.error(f"HunyuanVideo generation failed: {e}")
            return None
    
    async def _generate_with_animatediff(self, prompt: str, duration: int, fps: int, width: int, height: int) -> Optional[str]:
        """Generate video using AnimateDiff"""
        try:
            # AnimateDiff workflow
            workflow = {
                "1": {
                    "inputs": {
                        "text": prompt,
                        "clip": ["4", 1]
                    },
                    "class_type": "CLIPTextEncode"
                },
                "2": {
                    "inputs": {
                        "text": "blurry, low quality",
                        "clip": ["4", 1]
                    },
                    "class_type": "CLIPTextEncode"
                },
                "3": {
                    "inputs": {
                        "seed": -1,
                        "steps": 20,
                        "cfg": 8.0,
                        "sampler_name": "euler",
                        "scheduler": "normal",
                        "positive": ["1", 0],
                        "negative": ["2", 0],
                        "latent_image": ["5", 0],
                        "model": ["6", 0]
                    },
                    "class_type": "KSampler"
                },
                "4": {
                    "inputs": {
                        "ckpt_name": "sd_xl_base_1.0.safetensors"
                    },
                    "class_type": "CheckpointLoaderSimple"
                },
                "5": {
                    "inputs": {
                        "width": width,
                        "height": height,
                        "batch_size": duration * fps
                    },
                    "class_type": "EmptyLatentImage"
                },
                "6": {
                    "inputs": {
                        "model": ["4", 0],
                        "motion_model": "mm_sd_v15_v2.ckpt",
                        "context_options": {
                            "context_length": 16,
                            "context_overlap": 4
                        }
                    },
                    "class_type": "AnimateDiffLoader"
                },
                "7": {
                    "inputs": {
                        "samples": ["3", 0],
                        "vae": ["4", 2]
                    },
                    "class_type": "VAEDecode"
                },
                "8": {
                    "inputs": {
                        "images": ["7", 0],
                        "filename_prefix": "animatediff",
                        "fps": fps,
                        "compress_level": 4
                    },
                    "class_type": "VHS_VideoCombine"
                }
            }
            
            return await self._execute_comfyui_workflow(workflow)
            
        except Exception as e:
            logger.error(f"AnimateDiff generation failed: {e}")
            return None
    
    async def _animate_with_animatediff(self, image_base64: str, prompt: str, duration: int, fps: int) -> Optional[str]:
        """Animate existing image with AnimateDiff"""
        try:
            # Save base64 image temporarily
            with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp_file:
                image_data = base64.b64decode(image_base64)
                tmp_file.write(image_data)
                tmp_path = tmp_file.name
            
            # Upload image to ComfyUI
            async with aiohttp.ClientSession() as session:
                with open(tmp_path, 'rb') as f:
                    data = aiohttp.FormData()
                    data.add_field('image', f, filename='input.png')
                    
                    async with session.post(f'{self.comfyui_url}/upload/image', data=data) as resp:
                        if resp.status != 200:
                            return None
                        
                        result = await resp.json()
                        image_name = result['name']
            
            # AnimateDiff image-to-video workflow
            workflow = {
                "1": {
                    "inputs": {
                        "image": image_name,
                        "upload": "image"
                    },
                    "class_type": "LoadImage"
                },
                "2": {
                    "inputs": {
                        "text": prompt or "animate this image",
                        "clip": ["5", 1]
                    },
                    "class_type": "CLIPTextEncode"
                },
                "3": {
                    "inputs": {
                        "pixels": ["1", 0],
                        "vae": ["5", 2]
                    },
                    "class_type": "VAEEncode"
                },
                "4": {
                    "inputs": {
                        "seed": -1,
                        "steps": 20,
                        "cfg": 7.5,
                        "sampler_name": "euler",
                        "scheduler": "normal",
                        "positive": ["2", 0],
                        "negative": ["7", 0],
                        "latent_image": ["3", 0],
                        "model": ["6", 0]
                    },
                    "class_type": "KSampler"
                },
                "5": {
                    "inputs": {
                        "ckpt_name": "sd_xl_base_1.0.safetensors"
                    },
                    "class_type": "CheckpointLoaderSimple"
                },
                "6": {
                    "inputs": {
                        "model": ["5", 0],
                        "motion_model": "mm_sd_v15_v2.ckpt",
                    },
                    "class_type": "AnimateDiffLoader"
                },
                "7": {
                    "inputs": {
                        "text": "blurry, distorted",
                        "clip": ["5", 1]
                    },
                    "class_type": "CLIPTextEncode"
                },
                "8": {
                    "inputs": {
                        "samples": ["4", 0],
                        "vae": ["5", 2]
                    },
                    "class_type": "VAEDecode"
                },
                "9": {
                    "inputs": {
                        "images": ["8", 0],
                        "filename_prefix": "animated",
                        "fps": fps,
                        "compress_level": 4
                    },
                    "class_type": "VHS_VideoCombine"
                }
            }
            
            result = await self._execute_comfyui_workflow(workflow)
            
            # Clean up temp file
            os.unlink(tmp_path)
            
            return result
            
        except Exception as e:
            logger.error(f"Image animation failed: {e}")
            return None
    
    async def _execute_comfyui_workflow(self, workflow: Dict[str, Any]) -> Optional[str]:
        """Execute ComfyUI workflow and return base64 video"""
        try:
            async with aiohttp.ClientSession() as session:
                # Queue the prompt
                async with session.post(f'{self.comfyui_url}/prompt', json={"prompt": workflow}) as resp:
                    if resp.status != 200:
                        return None
                    result = await resp.json()
                    prompt_id = result['prompt_id']
                
                # Wait for completion and get video
                return await self._wait_for_video_result(session, prompt_id)
                
        except Exception as e:
            logger.error(f"ComfyUI workflow execution failed: {e}")
            return None
    
    async def _wait_for_video_result(self, session: aiohttp.ClientSession, prompt_id: str) -> Optional[str]:
        """Wait for ComfyUI to complete and return base64 video"""
        for _ in range(300):  # 5 minute timeout for video generation
            try:
                async with session.get(f'{self.comfyui_url}/history/{prompt_id}') as resp:
                    if resp.status == 200:
                        history = await resp.json()
                        if prompt_id in history:
                            outputs = history[prompt_id].get('outputs', {})
                            for node_id, node_output in outputs.items():
                                if 'gifs' in node_output:
                                    # Get the video file
                                    video_info = node_output['gifs'][0]
                                    filename = video_info['filename']
                                    
                                    # Download the video
                                    async with session.get(f'{self.comfyui_url}/view', params={'filename': filename}) as vid_resp:
                                        if vid_resp.status == 200:
                                            video_data = await vid_resp.read()
                                            return base64.b64encode(video_data).decode('utf-8')
                await asyncio.sleep(1)
            except:
                await asyncio.sleep(1)
                
        return None

# Global instance
video_generator = VideoGenerator()

async def generate_video(prompt: str, **kwargs) -> Optional[str]:
    """
    Convenience function for video generation with Docker service integration
    Automatically initializes services and uses best available option
    """
    # Initialize all services if not already done
    if not (video_generator.docker_available or 
            video_generator.hunyuan_available or 
            video_generator.cogvideo_available or 
            video_generator.animatediff_available):
        await video_generator.initialize()
    
    return await video_generator.generate_video(prompt, **kwargs)

async def animate_image(image_base64: str, prompt: str = "", **kwargs) -> Optional[str]:
    """Convenience function for image animation"""
    # Initialize services if not already done
    if not (video_generator.docker_available or video_generator.animatediff_available):
        await video_generator.initialize()
    
    return await video_generator.animate_image(image_base64, prompt, **kwargs)

# New enhanced function for direct Docker service usage
async def generate_video_docker(
    prompt: str, 
    model: str = "wan2gp",
    duration: int = 4, 
    fps: int = 8,
    width: int = 512,
    height: int = 512,
    motion_intensity: str = "moderate",
    style: str = "realistic"
) -> Optional[str]:
    """
    Generate video directly using Docker Wan2GP service
    Bypasses local services for faster, more reliable generation
    """
    try:
        return await generate_video_with_docker(
            prompt=prompt,
            model=model,
            duration=duration,
            fps=fps,
            width=width,
            height=height,
            motion_intensity=motion_intensity,
            style=style
        )
    except Exception as e:
        logger.error(f"Docker video generation failed: {e}")
        return None

# Test function
async def test_generation():
    """Test video generation capabilities"""
    await video_generator.initialize()
    
    test_prompt = "A cat walking in a garden, smooth motion"
    result = await generate_video(test_prompt, duration=3)
    
    if result:
        print("✅ Video generation test successful!")
        return True
    else:
        print("❌ Video generation test failed")
        return False

if __name__ == "__main__":
    asyncio.run(test_generation())