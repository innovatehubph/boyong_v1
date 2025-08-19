"""
Host Multimedia Client - Direct access to Docker services from host system
Bypasses container Docker restrictions by accessing services via network
"""

import asyncio
import aiohttp
import base64
import json
import logging
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional, Union, List

class HostMultimediaClient:
    """Client for accessing Docker multimedia services from host system via network"""
    
    def __init__(self):
        # Network access to Docker services (no Docker daemon required)
        self.services = {
            "localai": {
                "url": "http://localhost:8090",
                "health": "/v1/models",
                "chat": "/v1/chat/completions",
                "models": "/v1/models",
                "embeddings": "/v1/embeddings"
            },
            "pollinations": {
                "url": "http://localhost:8091", 
                "health": "/health",
                "generate": "/generate/image"
            },
            "wan2gp": {
                "url": "http://localhost:8092",
                "health": "/health", 
                "generate": "/generate_video"
            }
        }
        
        # Storage paths accessible from container
        self.deliverables_path = Path("/root/projects/pareng-boyong/pareng_boyong_deliverables")
        self.ensure_storage_structure()
        
        # Setup logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
    
    def ensure_storage_structure(self):
        """Create organized storage structure for deliverables"""
        storage_dirs = [
            "images/portraits", "images/landscapes", "images/artwork", 
            "images/product_photos", "images/social_media", "images/by_date",
            "videos/cinematic", "videos/conversational", "videos/educational",
            "videos/marketing", "videos/by_model/wan_vace_14b", "videos/by_model/fusionix",
            "videos/by_model/multitalk", "videos/by_model/wan2gp", "videos/by_date",
            "audio/music/ambient", "audio/music/upbeat", "audio/music/cinematic",
            "audio/voiceovers/english", "audio/voiceovers/filipino", "audio/by_date",
            "projects/completed", "projects/in_progress", "exports/social_media_ready"
        ]
        
        for dir_path in storage_dirs:
            (self.deliverables_path / dir_path).mkdir(parents=True, exist_ok=True)
    
    async def check_service_health(self, service_name: str) -> Dict[str, Any]:
        """Check if a Docker service is healthy via network access"""
        if service_name not in self.services:
            return {"status": "error", "message": f"Unknown service: {service_name}"}
        
        service = self.services[service_name]
        health_url = f"{service['url']}{service['health']}"
        
        try:
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=10)) as session:
                async with session.get(health_url) as response:
                    if response.status == 200:
                        try:
                            data = await response.json()
                        except:
                            data = {"message": "Service responding"}
                        
                        return {
                            "status": "healthy",
                            "service": service_name,
                            "url": service['url'],
                            "response": data
                        }
                    else:
                        return {
                            "status": "unhealthy",
                            "service": service_name,
                            "status_code": response.status,
                            "message": f"HTTP {response.status}"
                        }
        except asyncio.TimeoutError:
            return {
                "status": "timeout", 
                "service": service_name,
                "message": "Service not responding (timeout)"
            }
        except Exception as e:
            return {
                "status": "error", 
                "service": service_name,
                "error": str(e)
            }
    
    def check_docker_services_via_host(self) -> Dict[str, Any]:
        """Check Docker services status via host system commands"""
        try:
            # Use host system to check Docker containers
            result = subprocess.run([
                "curl", "-s", "--max-time", "5", "http://localhost:8091/health"
            ], capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0:
                return {
                    "status": "accessible",
                    "message": "Docker services accessible via host network",
                    "pollinations_health": result.stdout
                }
            else:
                return {
                    "status": "inaccessible", 
                    "message": "Docker services not accessible",
                    "error": result.stderr
                }
        except Exception as e:
            return {
                "status": "error",
                "message": f"Host check failed: {str(e)}"
            }
    
    async def generate_image_pollinations(
        self, 
        prompt: str, 
        width: int = 1024, 
        height: int = 1024,
        category: str = "artwork"
    ) -> Dict[str, Any]:
        """Generate image using Pollinations.AI service via network"""
        service_url = f"{self.services['pollinations']['url']}{self.services['pollinations']['generate']}"
        
        try:
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=120)) as session:
                payload = {
                    "prompt": prompt,
                    "width": width,
                    "height": height,
                    "style": "photorealistic",
                    "quality": "high"
                }
                
                self.logger.info(f"Generating image: {prompt[:50]}...")
                
                async with session.post(service_url, json=payload) as response:
                    if response.status == 200:
                        result = await response.json()
                        
                        if result.get("success") and result.get("image_base64"):
                            # Save to accessible storage location
                            file_info = self._save_generated_content(
                                base64_content=result["image_base64"],
                                content_type="image",
                                category=category,
                                metadata={
                                    "prompt": prompt,
                                    "dimensions": f"{width}x{height}",
                                    "service": "pollinations",
                                    "model": "flux.1",
                                    "access_method": "host_network"
                                }
                            )
                            
                            return {
                                "status": "success",
                                "image_base64": result["image_base64"],
                                "file_path": file_info["file_path"],
                                "metadata": file_info["metadata"],
                                "access_url": f"/pareng_boyong_deliverables/{file_info['relative_path']}"
                            }
                        else:
                            return {"status": "error", "message": result.get("message", "Generation failed")}
                    else:
                        error_text = await response.text()
                        return {"status": "error", "message": f"HTTP {response.status}: {error_text}"}
                        
        except asyncio.TimeoutError:
            return {"status": "error", "message": "Generation timeout - service took too long"}
        except Exception as e:
            self.logger.error(f"Pollinations generation error: {e}")
            return {"status": "error", "message": str(e)}
    
    async def generate_video_wan2gp(
        self, 
        prompt: str, 
        duration: int = 4,
        resolution: str = "720p",
        model: str = "wan2gp",
        category: str = "cinematic"
    ) -> Dict[str, Any]:
        """Generate video using Wan2GP service via network"""
        service_url = f"{self.services['wan2gp']['url']}/generate_video"
        
        try:
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=600)) as session:
                payload = {
                    "prompt": prompt,
                    "duration": duration,
                    "resolution": resolution,
                    "model": model,
                    "style": "realistic"
                }
                
                self.logger.info(f"Generating video: {prompt[:50]}... (Duration: {duration}s)")
                
                async with session.post(service_url, json=payload) as response:
                    if response.status == 200:
                        result = await response.json()
                        
                        if result.get("status") == "success" and result.get("video_base64"):
                            # Save to accessible storage location
                            file_info = self._save_generated_content(
                                base64_content=result["video_base64"],
                                content_type="video",
                                category=category,
                                metadata={
                                    "prompt": prompt,
                                    "duration": duration,
                                    "resolution": resolution,
                                    "service": "wan2gp",
                                    "model": model,
                                    "access_method": "host_network"
                                }
                            )
                            
                            return {
                                "status": "success",
                                "video_base64": result["video_base64"],
                                "file_path": file_info["file_path"],
                                "metadata": file_info["metadata"],
                                "access_url": f"/pareng_boyong_deliverables/{file_info['relative_path']}"
                            }
                        else:
                            return {"status": "error", "message": result.get("message", "Generation failed")}
                    else:
                        error_text = await response.text()
                        return {"status": "error", "message": f"HTTP {response.status}: {error_text}"}
                        
        except asyncio.TimeoutError:
            return {"status": "error", "message": "Video generation timeout - process took too long"}
        except Exception as e:
            self.logger.error(f"Wan2GP generation error: {e}")
            return {"status": "error", "message": str(e)}
    
    async def chat_with_localai(
        self, 
        messages: List[Dict[str, str]], 
        model: str = "galatolo-Q4_K.gguf",
        max_tokens: int = 1000
    ) -> Dict[str, Any]:
        """Chat with LocalAI service via network"""
        service_url = f"{self.services['localai']['url']}/v1/chat/completions"
        
        try:
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=120)) as session:
                payload = {
                    "model": model,
                    "messages": messages,
                    "max_tokens": max_tokens,
                    "temperature": 0.7
                }
                
                async with session.post(service_url, json=payload) as response:
                    if response.status == 200:
                        result = await response.json()
                        return {
                            "status": "success",
                            "response": result.get("choices", [{}])[0].get("message", {}).get("content", ""),
                            "usage": result.get("usage", {}),
                            "model": model
                        }
                    else:
                        error_text = await response.text()
                        return {"status": "error", "message": f"HTTP {response.status}: {error_text}"}
                        
        except Exception as e:
            self.logger.error(f"LocalAI chat error: {e}")
            return {"status": "error", "message": str(e)}
    
    async def get_localai_models(self) -> Dict[str, Any]:
        """Get available models from LocalAI via network"""
        service_url = f"{self.services['localai']['url']}/v1/models"
        
        try:
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=30)) as session:
                async with session.get(service_url) as response:
                    if response.status == 200:
                        result = await response.json()
                        return {
                            "status": "success",
                            "models": result.get("data", [])
                        }
                    else:
                        return {"status": "error", "message": f"HTTP {response.status}"}
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    def _save_generated_content(
        self, 
        base64_content: str, 
        content_type: str, 
        category: str,
        metadata: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Save generated content to accessible storage location"""
        
        # Generate unique filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        unique_id = base64.b32encode(base64_content[:10].encode()).decode()[:8].lower()
        
        # Determine file extension
        extensions = {
            "image": "png",
            "video": "mp4", 
            "audio": "wav"
        }
        ext = extensions.get(content_type, "bin")
        
        # Create filename
        filename = f"pb_{content_type}_{category}_{timestamp}_{unique_id}.{ext}"
        
        # Determine storage paths
        category_paths = {
            "image": {
                "portraits": "images/portraits",
                "landscapes": "images/landscapes", 
                "artwork": "images/artwork",
                "product_photos": "images/product_photos",
                "social_media": "images/social_media"
            },
            "video": {
                "cinematic": "videos/cinematic",
                "conversational": "videos/conversational",
                "educational": "videos/educational",
                "marketing": "videos/marketing"
            }
        }
        
        # Get primary storage path
        category_path = category_paths.get(content_type, {}).get(category, f"{content_type}s/by_date")
        relative_path = f"{category_path}/{filename}"
        primary_path = self.deliverables_path / relative_path
        
        # Also save to date-based backup
        date_path = datetime.now().strftime("%Y/%m")
        backup_relative = f"{content_type}s/by_date/{date_path}/{filename}"
        backup_path = self.deliverables_path / backup_relative
        
        try:
            # Decode and save content
            content_bytes = base64.b64decode(base64_content)
            
            # Save primary file
            primary_path.parent.mkdir(parents=True, exist_ok=True)
            with open(primary_path, 'wb') as f:
                f.write(content_bytes)
            
            # Save backup file
            backup_path.parent.mkdir(parents=True, exist_ok=True) 
            with open(backup_path, 'wb') as f:
                f.write(content_bytes)
            
            # Save metadata
            metadata_extended = {
                **metadata,
                "filename": filename,
                "primary_path": str(primary_path),
                "backup_path": str(backup_path),
                "relative_path": relative_path,
                "generated_at": datetime.now().isoformat(),
                "file_size": len(content_bytes),
                "content_type": content_type,
                "category": category,
                "access_method": "host_network_via_container"
            }
            
            metadata_filename = filename.rsplit('.', 1)[0] + '.json'
            metadata_path = primary_path.parent / metadata_filename
            
            with open(metadata_path, 'w') as f:
                json.dump(metadata_extended, f, indent=2)
            
            self.logger.info(f"Saved {content_type} to: {primary_path}")
            
            return {
                "file_path": str(primary_path),
                "backup_path": str(backup_path),
                "relative_path": relative_path,
                "metadata_path": str(metadata_path),
                "metadata": metadata_extended
            }
            
        except Exception as e:
            self.logger.error(f"File save error: {e}")
            return {
                "file_path": None,
                "error": str(e),
                "metadata": metadata,
                "relative_path": None
            }
    
    async def check_all_services(self) -> Dict[str, Any]:
        """Check health of all multimedia services via network"""
        results = {}
        
        # Check services via network (no Docker daemon needed)
        for service_name in self.services.keys():
            results[service_name] = await self.check_service_health(service_name)
        
        # Also check via host system
        host_check = self.check_docker_services_via_host()
        results["host_access"] = host_check
        
        healthy_count = sum(1 for result in results.values() 
                           if result.get("status") in ["healthy", "accessible"])
        
        return {
            "overall_status": "healthy" if healthy_count >= len(self.services) else "partial",
            "healthy_services": healthy_count,
            "total_services": len(self.services),
            "services": results,
            "access_method": "host_network_bypass"
        }

# Global client instance
host_multimedia_client = HostMultimediaClient()

# Synchronous wrappers for Agent Zero tools
def host_check_multimedia_services() -> Dict[str, Any]:
    """Agent Zero tool: Check multimedia services via host network"""
    return asyncio.run(host_multimedia_client.check_all_services())

def host_generate_image(prompt: str, category: str = "artwork", width: int = 1024, height: int = 1024) -> Dict[str, Any]:
    """Agent Zero tool: Generate image via host network access"""
    return asyncio.run(
        host_multimedia_client.generate_image_pollinations(prompt, width, height, category)
    )

def host_generate_video(prompt: str, category: str = "cinematic", duration: int = 4, resolution: str = "720p") -> Dict[str, Any]:
    """Agent Zero tool: Generate video via host network access"""
    return asyncio.run(
        host_multimedia_client.generate_video_wan2gp(prompt, duration, resolution, "wan2gp", category)
    )

def host_chat_localai(messages: List[Dict[str, str]], model: str = "galatolo-Q4_K.gguf") -> Dict[str, Any]:
    """Agent Zero tool: Chat with LocalAI via host network access"""
    return asyncio.run(host_multimedia_client.chat_with_localai(messages, model))

def host_get_localai_models() -> Dict[str, Any]:
    """Agent Zero tool: Get LocalAI models via host network access"""
    return asyncio.run(host_multimedia_client.get_localai_models())

# Export tools
__all__ = [
    'host_check_multimedia_services',
    'host_generate_image', 
    'host_generate_video',
    'host_chat_localai',
    'host_get_localai_models',
    'host_multimedia_client'
]