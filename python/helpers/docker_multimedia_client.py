"""
Docker Multimedia Service Client for Pareng Boyong
Provides integration with LocalAI, Pollinations.AI, and Wan2GP containers
"""

import aiohttp
import asyncio
import base64
import json
import logging
from typing import Optional, Dict, Any, List
from python.helpers.print_style import PrintStyle

class DockerMultimediaClient:
    def __init__(self):
        """Initialize Docker multimedia service client"""
        self.services = {
            'localai': {
                'url': 'http://localhost:8090',
                'health_endpoint': '/health',
                'available': False
            },
            'pollinations': {
                'url': 'http://localhost:8091', 
                'health_endpoint': '/health',
                'available': False
            },
            'wan2gp': {
                'url': 'http://localhost:8092',
                'health_endpoint': '/health', 
                'available': False
            }
        }
        self.session = None
        self.logger = logging.getLogger(__name__)
    
    async def __aenter__(self):
        """Async context manager entry"""
        self.session = aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=300))
        await self.check_services_health()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.session:
            await self.session.close()
    
    async def check_services_health(self) -> Dict[str, bool]:
        """Check health status of all Docker multimedia services"""
        health_status = {}
        
        for service_name, config in self.services.items():
            try:
                async with self.session.get(
                    f"{config['url']}{config['health_endpoint']}", 
                    timeout=aiohttp.ClientTimeout(total=10)
                ) as response:
                    if response.status == 200:
                        config['available'] = True
                        health_status[service_name] = True
                        PrintStyle(font_color="green").print(f"✅ {service_name.title()} service available")
                    else:
                        config['available'] = False
                        health_status[service_name] = False
                        PrintStyle(font_color="yellow").print(f"⚠️ {service_name.title()} service not responding")
            except Exception as e:
                config['available'] = False
                health_status[service_name] = False
                PrintStyle(font_color="red").print(f"❌ {service_name.title()} service unavailable: {e}")
        
        return health_status
    
    async def generate_image_pollinations(
        self, 
        prompt: str, 
        width: int = 1024, 
        height: int = 1024,
        style: Optional[str] = None,
        seed: Optional[int] = None
    ) -> Optional[str]:
        """Generate image using Pollinations.AI Docker service"""
        
        if not self.services['pollinations']['available']:
            PrintStyle(font_color="red").print("❌ Pollinations service not available")
            return None
        
        try:
            # Enhance prompt with style if provided
            enhanced_prompt = prompt
            if style:
                enhanced_prompt = f"{prompt}, {style} style"
            
            payload = {
                'prompt': enhanced_prompt,
                'width': width,
                'height': height,
                'seed': seed
            }
            
            PrintStyle(font_color="cyan").print(f"🎨 Generating image with Pollinations.AI: {prompt}")
            
            async with self.session.post(
                f"{self.services['pollinations']['url']}/generate/image",
                json=payload,
                timeout=aiohttp.ClientTimeout(total=120)
            ) as response:
                
                if response.status == 200:
                    data = await response.json()
                    if data.get('success') and data.get('image_base64'):
                        PrintStyle(font_color="green").print("✅ Image generated successfully with Pollinations.AI")
                        return data['image_base64']
                    else:
                        PrintStyle(font_color="red").print(f"❌ Pollinations generation failed: {data.get('error', 'Unknown error')}")
                        return None
                else:
                    error_text = await response.text()
                    PrintStyle(font_color="red").print(f"❌ Pollinations API error {response.status}: {error_text}")
                    return None
                    
        except asyncio.TimeoutError:
            PrintStyle(font_color="red").print("❌ Pollinations image generation timed out")
            return None
        except Exception as e:
            PrintStyle(font_color="red").print(f"❌ Pollinations image generation error: {e}")
            return None
    
    async def generate_video_wan2gp(
        self,
        prompt: str,
        model: str = "wan2gp",
        duration: int = 4,
        fps: int = 8,
        width: int = 512,
        height: int = 512,
        motion_intensity: str = "moderate",
        style: str = "realistic"
    ) -> Optional[str]:
        """Generate video using Wan2GP Docker service"""
        
        if not self.services['wan2gp']['available']:
            PrintStyle(font_color="red").print("❌ Wan2GP service not available")
            return None
        
        try:
            payload = {
                'prompt': prompt,
                'model': model,
                'duration': duration,
                'fps': fps,
                'width': width,
                'height': height,
                'motion_intensity': motion_intensity,
                'style': style
            }
            
            PrintStyle(font_color="cyan").print(f"🎬 Generating video with Wan2GP: {prompt}")
            
            async with self.session.post(
                f"{self.services['wan2gp']['url']}/generate/video",
                json=payload,
                timeout=aiohttp.ClientTimeout(total=300)  # 5 minutes for video generation
            ) as response:
                
                if response.status == 200:
                    data = await response.json()
                    if data.get('success') and data.get('video_base64'):
                        PrintStyle(font_color="green").print("✅ Video generated successfully with Wan2GP")
                        return data['video_base64']
                    else:
                        PrintStyle(font_color="red").print(f"❌ Wan2GP generation failed: {data.get('error', 'Unknown error')}")
                        return None
                else:
                    error_text = await response.text()
                    PrintStyle(font_color="red").print(f"❌ Wan2GP API error {response.status}: {error_text}")
                    return None
                    
        except asyncio.TimeoutError:
            PrintStyle(font_color="red").print("❌ Wan2GP video generation timed out")
            return None
        except Exception as e:
            PrintStyle(font_color="red").print(f"❌ Wan2GP video generation error: {e}")
            return None
    
    async def generate_text_localai(
        self,
        prompt: str,
        model: str = "gpt-3.5-turbo",
        max_tokens: int = 1000,
        temperature: float = 0.7
    ) -> Optional[str]:
        """Generate text/chat completion using LocalAI Docker service"""
        
        if not self.services['localai']['available']:
            PrintStyle(font_color="red").print("❌ LocalAI service not available")
            return None
        
        try:
            payload = {
                'model': model,
                'messages': [{'role': 'user', 'content': prompt}],
                'max_tokens': max_tokens,
                'temperature': temperature
            }
            
            PrintStyle(font_color="cyan").print(f"🧠 Processing with LocalAI: {prompt[:50]}...")
            
            async with self.session.post(
                f"{self.services['localai']['url']}/v1/chat/completions",
                json=payload,
                timeout=aiohttp.ClientTimeout(total=60)
            ) as response:
                
                if response.status == 200:
                    data = await response.json()
                    if data.get('choices') and len(data['choices']) > 0:
                        content = data['choices'][0]['message']['content']
                        PrintStyle(font_color="green").print("✅ Text generated successfully with LocalAI")
                        return content
                    else:
                        PrintStyle(font_color="red").print("❌ LocalAI: No response content")
                        return None
                else:
                    error_text = await response.text()
                    PrintStyle(font_color="red").print(f"❌ LocalAI API error {response.status}: {error_text}")
                    return None
                    
        except asyncio.TimeoutError:
            PrintStyle(font_color="red").print("❌ LocalAI text generation timed out")
            return None
        except Exception as e:
            PrintStyle(font_color="red").print(f"❌ LocalAI text generation error: {e}")
            return None
    
    async def get_localai_models(self) -> List[str]:
        """Get available models from LocalAI"""
        
        if not self.services['localai']['available']:
            return []
        
        try:
            async with self.session.get(
                f"{self.services['localai']['url']}/v1/models",
                timeout=aiohttp.ClientTimeout(total=30)
            ) as response:
                
                if response.status == 200:
                    data = await response.json()
                    models = [model['id'] for model in data.get('data', [])]
                    return models
                else:
                    PrintStyle(font_color="red").print(f"❌ Failed to get LocalAI models: {response.status}")
                    return []
                    
        except Exception as e:
            PrintStyle(font_color="red").print(f"❌ Error getting LocalAI models: {e}")
            return []
    
    def get_service_status(self) -> Dict[str, Dict[str, Any]]:
        """Get status of all multimedia services"""
        return {
            name: {
                'available': config['available'],
                'url': config['url'],
                'endpoint': config['health_endpoint']
            }
            for name, config in self.services.items()
        }
    
    def is_service_available(self, service_name: str) -> bool:
        """Check if a specific service is available"""
        return self.services.get(service_name, {}).get('available', False)

# Convenience functions for easy access
async def create_docker_client():
    """Create and return a configured Docker multimedia client"""
    return DockerMultimediaClient()

async def generate_image_with_docker(prompt: str, **kwargs) -> Optional[str]:
    """Generate image using Docker Pollinations service"""
    async with DockerMultimediaClient() as client:
        return await client.generate_image_pollinations(prompt, **kwargs)

async def generate_video_with_docker(prompt: str, **kwargs) -> Optional[str]:
    """Generate video using Docker Wan2GP service"""
    async with DockerMultimediaClient() as client:
        return await client.generate_video_wan2gp(prompt, **kwargs)

async def chat_with_localai(prompt: str, **kwargs) -> Optional[str]:
    """Chat/complete text with LocalAI Docker service"""
    async with DockerMultimediaClient() as client:
        return await client.generate_text_localai(prompt, **kwargs)

async def check_docker_services() -> Dict[str, bool]:
    """Check health of all Docker multimedia services"""
    async with DockerMultimediaClient() as client:
        return await client.check_services_health()