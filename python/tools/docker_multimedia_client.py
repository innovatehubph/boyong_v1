"""
Docker Multimedia Client - Tool for accessing Docker-based multimedia services
Integrates LocalAI, Pollinations.AI, and Wan2GP services with Pareng Boyong
"""

import asyncio
import aiohttp
import base64
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional, Union, List

class DockerMultimediaClient:
    """Client for Docker-based multimedia services integration"""
    
    def __init__(self):
        self.services = {
            "localai": {
                "url": "http://localhost:8090",
                "health": "/health",  # Use health endpoint
                "chat": "/v1/chat/completions",
                "models": "/v1/models",
                "embeddings": "/v1/embeddings"
            },
            "pollinations": {
                "url": "http://localhost:8091", 
                "health": "/health",
                "generate": "/generate"
            },
            "wan2gp": {
                "url": "http://localhost:8092",
                "health": "/health", 
                "generate": "/generate_video"
            }
        }
        
        # Storage paths
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
        """Check if a Docker service is healthy and responsive"""
        if service_name not in self.services:
            return {"status": "error", "message": f"Unknown service: {service_name}"}
        
        service = self.services[service_name]
        health_url = f"{service['url']}{service['health']}"
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(health_url, timeout=10) as response:
                    if response.status == 200:
                        data = await response.json()
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
                            "status_code": response.status
                        }
        except Exception as e:
            return {
                "status": "error", 
                "service": service_name,
                "error": str(e)
            }
    
    async def generate_image_pollinations(
        self, 
        prompt: str, 
        width: int = 1024, 
        height: int = 1024,
        category: str = "artwork"
    ) -> Dict[str, Any]:
        """Generate image using Pollinations.AI service"""
        service_url = f"{self.services['pollinations']['url']}/generate"
        
        try:
            async with aiohttp.ClientSession() as session:
                payload = {
                    "prompt": prompt,
                    "width": width,
                    "height": height,
                    "style": "photorealistic",
                    "quality": "high"
                }
                
                async with session.post(service_url, json=payload, timeout=60) as response:
                    if response.status == 200:
                        result = await response.json()
                        
                        if result.get("status") == "success" and result.get("image_base64"):
                            # Save to organized storage
                            file_info = self._save_generated_content(
                                base64_content=result["image_base64"],
                                content_type="image",
                                category=category,
                                metadata={
                                    "prompt": prompt,
                                    "dimensions": f"{width}x{height}",
                                    "service": "pollinations",
                                    "model": "flux.1"
                                }
                            )
                            
                            return {
                                "status": "success",
                                "image_base64": result["image_base64"],
                                "file_path": file_info["file_path"],
                                "metadata": file_info["metadata"]
                            }
                        else:
                            return {"status": "error", "message": result.get("message", "Generation failed")}
                    else:
                        error_text = await response.text()
                        return {"status": "error", "message": f"HTTP {response.status}: {error_text}"}
                        
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
        """Generate video using Wan2GP service"""
        service_url = f"{self.services['wan2gp']['url']}/generate_video"
        
        try:
            async with aiohttp.ClientSession() as session:
                payload = {
                    "prompt": prompt,
                    "duration": duration,
                    "resolution": resolution,
                    "model": model,
                    "style": "realistic"
                }
                
                async with session.post(service_url, json=payload, timeout=300) as response:
                    if response.status == 200:
                        result = await response.json()
                        
                        if result.get("status") == "success" and result.get("video_base64"):
                            # Save to organized storage
                            file_info = self._save_generated_content(
                                base64_content=result["video_base64"],
                                content_type="video",
                                category=category,
                                metadata={
                                    "prompt": prompt,
                                    "duration": duration,
                                    "resolution": resolution,
                                    "service": "wan2gp",
                                    "model": model
                                }
                            )
                            
                            return {
                                "status": "success",
                                "video_base64": result["video_base64"],
                                "file_path": file_info["file_path"],
                                "metadata": file_info["metadata"]
                            }
                        else:
                            return {"status": "error", "message": result.get("message", "Generation failed")}
                    else:
                        error_text = await response.text()
                        return {"status": "error", "message": f"HTTP {response.status}: {error_text}"}
                        
        except Exception as e:
            self.logger.error(f"Wan2GP generation error: {e}")
            return {"status": "error", "message": str(e)}
    
    async def chat_with_localai(
        self, 
        messages: List[Dict[str, str]], 
        model: str = "gpt-4",
        max_tokens: int = 1000
    ) -> Dict[str, Any]:
        """Chat with LocalAI service"""
        service_url = f"{self.services['localai']['url']}/v1/chat/completions"
        
        try:
            async with aiohttp.ClientSession() as session:
                payload = {
                    "model": model,
                    "messages": messages,
                    "max_tokens": max_tokens,
                    "temperature": 0.7
                }
                
                async with session.post(service_url, json=payload, timeout=60) as response:
                    if response.status == 200:
                        result = await response.json()
                        return {
                            "status": "success",
                            "response": result.get("choices", [{}])[0].get("message", {}).get("content", ""),
                            "usage": result.get("usage", {})
                        }
                    else:
                        error_text = await response.text()
                        return {"status": "error", "message": f"HTTP {response.status}: {error_text}"}
                        
        except Exception as e:
            self.logger.error(f"LocalAI chat error: {e}")
            return {"status": "error", "message": str(e)}
    
    async def get_localai_models(self) -> Dict[str, Any]:
        """Get available models from LocalAI"""
        service_url = f"{self.services['localai']['url']}/v1/models"
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(service_url, timeout=10) as response:
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
        """Save generated content to organized storage with metadata"""
        
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
        
        # Determine storage path
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
            },
            "audio": {
                "music": "audio/music/ambient",
                "voiceover": "audio/voiceovers/english",
                "ambient": "audio/music/ambient"
            }
        }
        
        # Get primary storage path
        category_path = category_paths.get(content_type, {}).get(category, f"{content_type}s/by_date")
        primary_path = self.deliverables_path / category_path / filename
        
        # Also save to date-based backup
        date_path = datetime.now().strftime("%Y/%m")
        backup_path = self.deliverables_path / f"{content_type}s/by_date" / date_path / filename
        
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
                "generated_at": datetime.now().isoformat(),
                "file_size": len(content_bytes),
                "content_type": content_type,
                "category": category
            }
            
            metadata_filename = filename.rsplit('.', 1)[0] + '.json'
            metadata_path = primary_path.parent / metadata_filename
            
            with open(metadata_path, 'w') as f:
                json.dump(metadata_extended, f, indent=2)
            
            return {
                "file_path": str(primary_path),
                "backup_path": str(backup_path),
                "metadata_path": str(metadata_path),
                "metadata": metadata_extended
            }
            
        except Exception as e:
            self.logger.error(f"File save error: {e}")
            return {
                "file_path": None,
                "error": str(e),
                "metadata": metadata
            }
    
    async def check_all_services(self) -> Dict[str, Any]:
        """Check health of all Docker multimedia services"""
        results = {}
        
        for service_name in self.services.keys():
            results[service_name] = await self.check_service_health(service_name)
        
        healthy_count = sum(1 for result in results.values() if result.get("status") == "healthy")
        
        return {
            "overall_status": "healthy" if healthy_count == len(self.services) else "partial",
            "healthy_services": healthy_count,
            "total_services": len(self.services),
            "services": results
        }

# Global client instance
docker_multimedia_client = DockerMultimediaClient()

async def check_docker_services():
    """Tool function: Check Docker multimedia services health"""
    return await docker_multimedia_client.check_all_services()

async def generate_image_with_docker(prompt: str, category: str = "artwork", width: int = 1024, height: int = 1024):
    """Tool function: Generate image using Docker Pollinations service"""
    return await docker_multimedia_client.generate_image_pollinations(prompt, width, height, category)

async def generate_video_with_docker(prompt: str, category: str = "cinematic", duration: int = 4, resolution: str = "720p"):
    """Tool function: Generate video using Docker Wan2GP service"""
    return await docker_multimedia_client.generate_video_wan2gp(prompt, duration, resolution, "wan2gp", category)

async def chat_with_docker_localai(messages: List[Dict[str, str]], model: str = "gpt-4"):
    """Tool function: Chat with Docker LocalAI service"""
    return await docker_multimedia_client.chat_with_localai(messages, model)

# Main execution for testing
if __name__ == "__main__":
    import asyncio
    
    async def test_services():
        client = DockerMultimediaClient()
        
        print("🔍 Checking service health...")
        health_status = await client.check_all_services()
        print(f"Services Status: {health_status}")
        
        if health_status["healthy_services"] > 0:
            print("\n🖼️ Testing image generation...")
            image_result = await client.generate_image_pollinations(
                "A beautiful sunset over mountains", 
                category="landscapes"
            )
            print(f"Image generation: {image_result.get('status')}")
            if image_result.get("file_path"):
                print(f"Saved to: {image_result['file_path']}")
    
    asyncio.run(test_services())