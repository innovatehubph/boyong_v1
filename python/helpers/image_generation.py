"""
Image Generation Helper for Pareng Boyong  
Enhanced with Docker service integration and fallback support
"""

import asyncio
import base64
import io
import logging
from typing import Optional, Dict, Any
import aiohttp
import json
from PIL import Image
from python.helpers.docker_multimedia_client import generate_image_with_docker
from python.helpers.print_style import PrintStyle

logger = logging.getLogger(__name__)

class ImageGenerator:
    def __init__(self):
        self.flux_available = False
        self.sd_available = False
        self.docker_available = False
        self.comfyui_url = None
        self.a1111_url = None
        
    async def initialize(self):
        """Initialize and detect available image generation services"""
        # Check for Docker Pollinations service first
        try:
            from python.helpers.docker_multimedia_client import check_docker_services
            services = await check_docker_services()
            self.docker_available = services.get('pollinations', False)
            if self.docker_available:
                logger.info("✅ Docker Pollinations service available")
                PrintStyle(font_color="green").print("✅ Docker Pollinations service detected")
        except:
            logger.info("❌ Docker Pollinations service not available")
            
        # Check for ComfyUI (FLUX.1)
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get('http://localhost:8188/system_stats', timeout=5) as resp:
                    if resp.status == 200:
                        self.flux_available = True
                        self.comfyui_url = 'http://localhost:8188'
                        logger.info("✅ ComfyUI (FLUX.1) available")
        except:
            logger.info("❌ ComfyUI (FLUX.1) not available")
            
        # Check for Automatic1111 (Stable Diffusion)
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get('http://localhost:7860/sdapi/v1/options', timeout=5) as resp:
                    if resp.status == 200:
                        self.sd_available = True
                        self.a1111_url = 'http://localhost:7860'
                        logger.info("✅ Automatic1111 (Stable Diffusion) available")
        except:
            logger.info("❌ Automatic1111 (Stable Diffusion) not available")
    
    async def generate_image(
        self, 
        prompt: str, 
        negative_prompt: str = "", 
        width: int = 1024, 
        height: int = 1024,
        steps: int = 20,
        model_preference: str = "flux"
    ) -> Optional[str]:
        """
        Generate image using available models with priority order:
        1. Docker Pollinations service (preferred)
        2. ComfyUI/FLUX.1 (if available)
        3. Automatic1111/Stable Diffusion (if available)
        4. External API fallback
        Returns base64 encoded image or None if failed
        """
        
        # First priority: Docker Pollinations service (fastest and most reliable)
        if self.docker_available:
            try:
                PrintStyle(font_color="cyan").print("🎨 Using Docker Pollinations service...")
                style = self._map_model_to_style(model_preference)
                result = await generate_image_with_docker(
                    prompt=prompt,
                    width=width,
                    height=height,
                    style=style
                )
                if result:
                    PrintStyle(font_color="green").print("✅ Image generated with Docker Pollinations")
                    return result
                else:
                    PrintStyle(font_color="yellow").print("⚠️ Docker Pollinations failed, trying local services...")
            except Exception as e:
                logger.warning(f"Docker Pollinations failed: {e}")
                PrintStyle(font_color="yellow").print(f"⚠️ Docker service error, trying alternatives...")
        
        # Second priority: Local ComfyUI/FLUX.1
        if model_preference == "flux" and self.flux_available:
            PrintStyle(font_color="cyan").print("🎨 Using local ComfyUI/FLUX.1...")
            result = await self._generate_with_flux(prompt, negative_prompt, width, height, steps)
            if result:
                return result
            else:
                PrintStyle(font_color="yellow").print("⚠️ ComfyUI/FLUX.1 failed, trying Stable Diffusion...")
        
        # Third priority: Local Stable Diffusion
        elif self.sd_available:
            PrintStyle(font_color="cyan").print("🎨 Using local Stable Diffusion...")
            result = await self._generate_with_sd(prompt, negative_prompt, width, height, steps)
            if result:
                return result
            else:
                PrintStyle(font_color="yellow").print("⚠️ Stable Diffusion failed, trying external API...")
        
        # Final fallback: External Pollinations API
        PrintStyle(font_color="cyan").print("🎨 Using external Pollinations API as final fallback...")
        return await self._generate_with_external_api(prompt, width, height)
    
    def _map_model_to_style(self, model: str) -> str:
        """Map model preference to Pollinations style"""
        model_to_style = {
            "flux": "realistic",
            "flux.1": "realistic",
            "sd": "artistic", 
            "stable-diffusion": "artistic",
            "photorealistic": "realistic",
            "anime": "anime",
            "cartoon": "cartoon",
            "portrait": "portrait",
            "landscape": "landscape",
            "cinematic": "cinematic"
        }
        return model_to_style.get(model.lower(), "realistic")
    
    async def _generate_with_external_api(self, prompt: str, width: int, height: int) -> Optional[str]:
        """Generate using external Pollinations API as final fallback"""
        try:
            import urllib.parse
            encoded_prompt = urllib.parse.quote(prompt + ", photorealistic, highly detailed, professional photography")
            url = f"https://image.pollinations.ai/prompt/{encoded_prompt}"
            params = {
                "width": width,
                "height": height, 
                "nologo": "true"
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params, timeout=aiohttp.ClientTimeout(total=60)) as response:
                    if response.status == 200:
                        image_data = await response.read()
                        PrintStyle(font_color="green").print("✅ Image generated with external API")
                        return base64.b64encode(image_data).decode()
                    else:
                        PrintStyle(font_color="red").print(f"❌ External API failed: {response.status}")
                        
        except Exception as e:
            logger.error(f"External API generation failed: {e}")
            PrintStyle(font_color="red").print(f"❌ All image generation methods failed")
            
        return None
    
    async def _generate_with_flux(self, prompt: str, negative_prompt: str, width: int, height: int, steps: int) -> Optional[str]:
        """Generate image using FLUX.1 via ComfyUI"""
        try:
            # ComfyUI workflow for FLUX.1 schnell
            workflow = {
                "5": {
                    "inputs": {
                        "width": width,
                        "height": height,
                        "batch_size": 1
                    },
                    "class_type": "EmptyLatentImage"
                },
                "6": {
                    "inputs": {
                        "text": prompt,
                        "clip": ["11", 0]
                    },
                    "class_type": "CLIPTextEncode"
                },
                "8": {
                    "inputs": {
                        "samples": ["13", 0],
                        "vae": ["10", 0]
                    },
                    "class_type": "VAEDecode"
                },
                "9": {
                    "inputs": {
                        "filename_prefix": "ComfyUI",
                        "images": ["8", 0]
                    },
                    "class_type": "SaveImage"
                },
                "10": {
                    "inputs": {
                        "vae_name": "ae.safetensors"
                    },
                    "class_type": "VAELoader"
                },
                "11": {
                    "inputs": {
                        "clip_name1": "t5xxl_fp8_e4m3fn.safetensors",
                        "clip_name2": "clip_l.safetensors"
                    },
                    "class_type": "DualCLIPLoader"
                },
                "12": {
                    "inputs": {
                        "unet_name": "flux1-schnell.safetensors"
                    },
                    "class_type": "UNETLoader"
                },
                "13": {
                    "inputs": {
                        "noise": ["25", 0],
                        "guider": ["22", 0],
                        "sampler": ["16", 0],
                        "sigmas": ["17", 0],
                        "latent_image": ["5", 0]
                    },
                    "class_type": "SamplerCustomAdvanced"
                },
                "16": {
                    "inputs": {
                        "sampler_name": "euler"
                    },
                    "class_type": "KSamplerSelect"
                },
                "17": {
                    "inputs": {
                        "scheduler": "simple",
                        "steps": steps,
                        "denoise": 1.0,
                        "model": ["12", 0]
                    },
                    "class_type": "BasicScheduler"
                },
                "22": {
                    "inputs": {
                        "model": ["12", 0],
                        "conditioning": ["6", 0]
                    },
                    "class_type": "BasicGuider"
                },
                "25": {
                    "inputs": {
                        "noise_seed": -1
                    },
                    "class_type": "RandomNoise"
                }
            }
            
            async with aiohttp.ClientSession() as session:
                # Queue the prompt
                async with session.post(f'{self.comfyui_url}/prompt', json={"prompt": workflow}) as resp:
                    if resp.status != 200:
                        return None
                    result = await resp.json()
                    prompt_id = result['prompt_id']
                
                # Wait for completion and get image
                return await self._wait_for_comfyui_result(session, prompt_id)
                
        except Exception as e:
            logger.error(f"FLUX generation failed: {e}")
            return None
    
    async def _generate_with_sd(self, prompt: str, negative_prompt: str, width: int, height: int, steps: int) -> Optional[str]:
        """Generate image using Stable Diffusion via Automatic1111"""
        try:
            payload = {
                "prompt": prompt,
                "negative_prompt": negative_prompt,
                "width": width,
                "height": height,
                "steps": steps,
                "cfg_scale": 7,
                "sampler_name": "DPM++ 2M Karras",
                "batch_size": 1,
                "n_iter": 1
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(f'{self.a1111_url}/sdapi/v1/txt2img', json=payload) as resp:
                    if resp.status == 200:
                        result = await resp.json()
                        return result['images'][0]  # Base64 image
                    
        except Exception as e:
            logger.error(f"Stable Diffusion generation failed: {e}")
            return None
    
    async def _wait_for_comfyui_result(self, session: aiohttp.ClientSession, prompt_id: str) -> Optional[str]:
        """Wait for ComfyUI to complete and return base64 image"""
        for _ in range(60):  # 60 second timeout
            try:
                async with session.get(f'{self.comfyui_url}/history/{prompt_id}') as resp:
                    if resp.status == 200:
                        history = await resp.json()
                        if prompt_id in history:
                            outputs = history[prompt_id].get('outputs', {})
                            for node_id, node_output in outputs.items():
                                if 'images' in node_output:
                                    image_info = node_output['images'][0]
                                    filename = image_info['filename']
                                    
                                    # Download the image
                                    async with session.get(f'{self.comfyui_url}/view', params={'filename': filename}) as img_resp:
                                        if img_resp.status == 200:
                                            image_data = await img_resp.read()
                                            return base64.b64encode(image_data).decode('utf-8')
                await asyncio.sleep(1)
            except:
                await asyncio.sleep(1)
                
        return None

# Global instance
image_generator = ImageGenerator()

async def generate_image(prompt: str, **kwargs) -> Optional[str]:
    """
    Convenience function for image generation with Docker service integration
    Automatically initializes services and uses best available option
    """
    # Initialize all services if not already done
    if not (image_generator.docker_available or image_generator.flux_available or image_generator.sd_available):
        await image_generator.initialize()
    
    return await image_generator.generate_image(prompt, **kwargs)

# New enhanced function for direct Docker service usage
async def generate_image_docker(prompt: str, style: str = "realistic", width: int = 1024, height: int = 1024, seed: Optional[int] = None) -> Optional[str]:
    """
    Generate image directly using Docker Pollinations service
    Bypasses local services for faster, more reliable generation
    """
    try:
        return await generate_image_with_docker(
            prompt=prompt,
            width=width, 
            height=height,
            style=style,
            seed=seed
        )
    except Exception as e:
        logger.error(f"Docker image generation failed: {e}")
        return None

# Test function
async def test_generation():
    """Test image generation capabilities"""
    await image_generator.initialize()
    
    test_prompt = "A beautiful sunset over mountains, digital art"
    result = await generate_image(test_prompt)
    
    if result:
        print("✅ Image generation test successful!")
        return True
    else:
        print("❌ Image generation test failed")
        return False

if __name__ == "__main__":
    asyncio.run(test_generation())