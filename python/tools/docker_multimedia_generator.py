"""
Docker Multimedia Generator Tool - Enhanced multimedia generation using Docker services
Integrates with Pareng Boyong's tool system for seamless multimedia generation
"""

from .docker_multimedia_client import docker_multimedia_client
import asyncio
import logging
from typing import Dict, Any, Optional, List

class DockerMultimediaGenerator:
    """High-level multimedia generator using Docker services"""
    
    def __init__(self):
        self.client = docker_multimedia_client
        self.logger = logging.getLogger(__name__)
    
    def detect_content_category(self, prompt: str, content_type: str) -> str:
        """Intelligent category detection based on prompt content"""
        
        prompt_lower = prompt.lower()
        
        if content_type == "image":
            if any(word in prompt_lower for word in ["person", "face", "portrait", "human", "character"]):
                return "portraits"
            elif any(word in prompt_lower for word in ["landscape", "nature", "mountain", "ocean", "forest", "sunset"]):
                return "landscapes"
            elif any(word in prompt_lower for word in ["product", "commercial", "advertisement", "showcase"]):
                return "product_photos"
            elif any(word in prompt_lower for word in ["social media", "instagram", "facebook", "post", "story"]):
                return "social_media"
            else:
                return "artwork"
        
        elif content_type == "video":
            if any(word in prompt_lower for word in ["cinematic", "film", "movie", "dramatic", "professional"]):
                return "cinematic"
            elif any(word in prompt_lower for word in ["conversation", "dialogue", "talking", "characters discussing"]):
                return "conversational"
            elif any(word in prompt_lower for word in ["tutorial", "educational", "learning", "instruction"]):
                return "educational"
            elif any(word in prompt_lower for word in ["marketing", "commercial", "advertisement", "promotional"]):
                return "marketing"
            else:
                return "cinematic"  # Default to cinematic for quality
        
        elif content_type == "audio":
            if any(word in prompt_lower for word in ["voice", "speak", "say", "pronunciation"]):
                return "voiceover"
            else:
                return "music"
        
        return "general"
    
    def determine_video_model(self, prompt: str, category: str) -> str:
        """Select optimal video model based on content requirements"""
        
        prompt_lower = prompt.lower()
        
        # High-quality requirements
        if any(word in prompt_lower for word in ["high-quality", "professional", "cinematic", "film-quality"]):
            return "wan_vace_14b"  # Highest quality 14B model
        
        # Conversation requirements  
        if any(word in prompt_lower for word in ["conversation", "dialogue", "characters talking", "discussion"]):
            return "multitalk"  # Multi-character dialogue specialist
        
        # Speed requirements
        if any(word in prompt_lower for word in ["quick", "fast", "rapid", "50% faster"]):
            return "fusionix"  # 50% faster generation
        
        # Accessibility requirements
        if any(word in prompt_lower for word in ["low-vram", "6gb", "older gpu", "accessible"]):
            return "wan2gp"  # Low-VRAM optimization
        
        # Default selection based on category
        if category == "conversational":
            return "multitalk"
        elif category == "cinematic":
            return "fusionix"  # Good balance of quality and speed
        else:
            return "wan2gp"  # Most accessible option
    
    async def generate_multimedia_content(
        self,
        prompt: str,
        content_type: str,  # "image", "video", "audio"
        **kwargs
    ) -> Dict[str, Any]:
        """Generate multimedia content with intelligent routing"""
        
        try:
            # Auto-detect category
            category = kwargs.get('category') or self.detect_content_category(prompt, content_type)
            
            self.logger.info(f"Generating {content_type} with category '{category}' for prompt: {prompt[:100]}...")
            
            if content_type == "image":
                result = await self.client.generate_image_pollinations(
                    prompt=prompt,
                    width=kwargs.get('width', 1024),
                    height=kwargs.get('height', 1024),
                    category=category
                )
            
            elif content_type == "video":
                model = kwargs.get('model') or self.determine_video_model(prompt, category)
                result = await self.client.generate_video_wan2gp(
                    prompt=prompt,
                    duration=kwargs.get('duration', 4),
                    resolution=kwargs.get('resolution', '720p'),
                    model=model,
                    category=category
                )
            
            else:
                return {"status": "error", "message": f"Unsupported content type: {content_type}"}
            
            # Enhance result with generation info
            if result.get("status") == "success":
                result["generation_info"] = {
                    "content_type": content_type,
                    "category": category,
                    "prompt": prompt,
                    "service": "docker_services"
                }
            
            return result
            
        except Exception as e:
            self.logger.error(f"Generation error: {e}")
            return {"status": "error", "message": str(e)}
    
    async def batch_generate(
        self,
        requests: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Generate multiple multimedia items efficiently"""
        
        tasks = []
        for request in requests:
            content_type = request.get("type")
            prompt = request.get("prompt")
            kwargs = {k: v for k, v in request.items() if k not in ["type", "prompt"]}
            
            task = self.generate_multimedia_content(prompt, content_type, **kwargs)
            tasks.append(task)
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Process results and handle exceptions
        processed_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                processed_results.append({
                    "status": "error",
                    "request_index": i,
                    "message": str(result)
                })
            else:
                processed_results.append({
                    **result,
                    "request_index": i
                })
        
        return processed_results

# Global generator instance
docker_multimedia_generator = DockerMultimediaGenerator()

def generate_image_docker_tool(
    prompt: str,
    width: int = 1024,
    height: int = 1024,
    category: str = None
) -> Dict[str, Any]:
    """
    Agent Zero tool for generating images using Docker Pollinations service
    
    Args:
        prompt: Description of the image to generate
        width: Image width (default: 1024)
        height: Image height (default: 1024) 
        category: Image category for organization (auto-detected if not provided)
    
    Returns:
        Dict with status, image_base64, file_path, and metadata
    """
    return asyncio.run(
        docker_multimedia_generator.generate_multimedia_content(
            prompt=prompt,
            content_type="image",
            width=width,
            height=height,
            category=category
        )
    )

def generate_video_docker_tool(
    prompt: str,
    duration: int = 4,
    resolution: str = "720p",
    model: str = None,
    category: str = None
) -> Dict[str, Any]:
    """
    Agent Zero tool for generating videos using Docker Wan2GP service
    
    Args:
        prompt: Description of the video to generate
        duration: Video duration in seconds (2-15)
        resolution: Video resolution (480p, 720p, 1080p)
        model: AI model to use (wan_vace_14b, fusionix, multitalk, wan2gp, auto)
        category: Video category for organization (auto-detected if not provided)
    
    Returns:
        Dict with status, video_base64, file_path, and metadata
    """
    return asyncio.run(
        docker_multimedia_generator.generate_multimedia_content(
            prompt=prompt,
            content_type="video",
            duration=duration,
            resolution=resolution,
            model=model,
            category=category
        )
    )

def check_docker_multimedia_services() -> Dict[str, Any]:
    """
    Agent Zero tool for checking Docker multimedia services health
    
    Returns:
        Dict with service health status and details
    """
    return asyncio.run(docker_multimedia_client.check_all_services())

def batch_generate_multimedia(requests: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Agent Zero tool for batch multimedia generation
    
    Args:
        requests: List of generation requests, each with 'type', 'prompt', and optional parameters
    
    Returns:
        List of generation results
    """
    return asyncio.run(docker_multimedia_generator.batch_generate(requests))

# Export tools for Agent Zero integration
__all__ = [
    'generate_image_docker_tool',
    'generate_video_docker_tool', 
    'check_docker_multimedia_services',
    'batch_generate_multimedia',
    'docker_multimedia_generator',
    'docker_multimedia_client'
]