"""
Multimedia Service Integration - Main interface for Pareng Boyong
Provides unified access to multimedia services regardless of container restrictions
"""

import logging
from typing import Dict, Any, Optional, List

# Handle imports for both direct execution and module import
try:
    from .host_multimedia_client import host_multimedia_client
except ImportError:
    from host_multimedia_client import host_multimedia_client

class MultimediaServiceIntegration:
    """Unified multimedia service integration for Pareng Boyong"""
    
    def __init__(self):
        self.client = host_multimedia_client
        self.logger = logging.getLogger(__name__)
        
        # Detection patterns for auto-routing
        self.category_detection = {
            "image": {
                "portrait": ["person", "face", "portrait", "human", "character", "headshot", "selfie"],
                "landscape": ["landscape", "nature", "mountain", "ocean", "forest", "sunset", "scenery"],
                "product": ["product", "commercial", "advertisement", "showcase", "item", "brand"],
                "social_media": ["social", "instagram", "facebook", "post", "story", "share"],
                "artwork": ["art", "artistic", "creative", "abstract", "drawing", "painting"]
            },
            "video": {
                "cinematic": ["cinematic", "film", "movie", "dramatic", "professional", "cinematic"],
                "conversational": ["conversation", "dialogue", "talking", "discussion", "characters"],
                "educational": ["tutorial", "educational", "learning", "instruction", "teaching"],
                "marketing": ["marketing", "commercial", "advertisement", "promotional", "business"]
            }
        }
    
    def detect_content_category(self, prompt: str, content_type: str) -> str:
        """Smart category detection based on prompt content"""
        prompt_lower = prompt.lower()
        
        categories = self.category_detection.get(content_type, {})
        
        # Score each category based on keyword matches
        category_scores = {}
        for category, keywords in categories.items():
            score = sum(1 for keyword in keywords if keyword in prompt_lower)
            if score > 0:
                category_scores[category] = score
        
        # Return highest scoring category, or default
        if category_scores:
            return max(category_scores, key=category_scores.get)
        
        # Defaults
        return "artwork" if content_type == "image" else "cinematic"
    
    def analyze_multimedia_request(self, message: str) -> Dict[str, Any]:
        """Analyze message for multimedia generation requests"""
        message_lower = message.lower()
        
        # Detection patterns
        image_keywords = [
            "image", "picture", "photo", "artwork", "illustration", "visual", "portrait", "landscape",
            "create image", "generate image", "make image", "draw", "design", "render image",
            "larawan", "litrato", "gumawa ng larawan"  # Filipino
        ]
        
        video_keywords = [
            "video", "animation", "clip", "movie", "film", "cinematic",
            "create video", "generate video", "make video", "animate", "render video",
            "gumawa ng video", "video animation"  # Filipino
        ]
        
        audio_keywords = [
            "music", "song", "audio", "voice", "voiceover", "sound", "compose",
            "create music", "generate music", "make song", "voice over",
            "musika", "kanta", "tunog"  # Filipino
        ]
        
        detected_types = []
        confidence_scores = {}
        
        # Check for each content type
        image_matches = sum(1 for keyword in image_keywords if keyword in message_lower)
        video_matches = sum(1 for keyword in video_keywords if keyword in message_lower)
        audio_matches = sum(1 for keyword in audio_keywords if keyword in message_lower)
        
        if image_matches > 0:
            detected_types.append("image")
            confidence_scores["image"] = min(0.7 + (image_matches * 0.1), 0.95)
        
        if video_matches > 0:
            detected_types.append("video") 
            confidence_scores["video"] = min(0.7 + (video_matches * 0.1), 0.95)
        
        if audio_matches > 0:
            detected_types.append("audio")
            confidence_scores["audio"] = min(0.6 + (audio_matches * 0.1), 0.9)
        
        overall_confidence = max(confidence_scores.values()) if confidence_scores else 0.0
        
        return {
            "detected": len(detected_types) > 0,
            "types": detected_types,
            "confidence_scores": confidence_scores,
            "overall_confidence": overall_confidence,
            "should_activate": overall_confidence >= 0.6,
            "primary_type": max(confidence_scores.keys(), key=confidence_scores.get) if confidence_scores else None
        }
    
    async def smart_generate(self, prompt: str, content_type: str = None, **kwargs) -> Dict[str, Any]:
        """Smart generation with auto-detection and routing"""
        
        if not content_type:
            # Auto-detect content type
            analysis = self.analyze_multimedia_request(prompt)
            if analysis["detected"]:
                content_type = analysis["primary_type"]
            else:
                return {"status": "error", "message": "Could not detect content type from prompt"}
        
        # Auto-detect category
        category = kwargs.get('category') or self.detect_content_category(prompt, content_type)
        
        try:
            if content_type == "image":
                return await self.client.generate_image_pollinations(
                    prompt=prompt,
                    width=kwargs.get('width', 1024),
                    height=kwargs.get('height', 1024),
                    category=category
                )
            
            elif content_type == "video":
                return await self.client.generate_video_wan2gp(
                    prompt=prompt,
                    duration=kwargs.get('duration', 4),
                    resolution=kwargs.get('resolution', '720p'),
                    model=kwargs.get('model', 'wan2gp'),
                    category=category
                )
            
            else:
                return {"status": "error", "message": f"Unsupported content type: {content_type}"}
                
        except Exception as e:
            self.logger.error(f"Smart generation error: {e}")
            return {"status": "error", "message": str(e)}
    
    def check_service_status(self) -> Dict[str, Any]:
        """Check all multimedia services status"""
        import asyncio
        return asyncio.run(self.client.check_all_services())
    
    def generate_service_report(self) -> str:
        """Generate a comprehensive service status report"""
        status = self.check_service_status()
        
        report = "🎨 **Pareng Boyong Multimedia Services Report**\\n\\n"
        
        # Overall status
        overall_status = status.get("overall_status", "unknown")
        if overall_status == "healthy":
            report += "✅ **Status**: All services operational\\n"
        elif overall_status == "partial":
            report += "⚠️ **Status**: Some services available\\n"
        else:
            report += "❌ **Status**: Services unavailable\\n"
        
        report += f"🔧 **Access Method**: {status.get('access_method', 'Network bypass')}\\n"
        report += f"📊 **Services**: {status.get('healthy_services', 0)}/{status.get('total_services', 0)} healthy\\n\\n"
        
        # Individual services
        services = status.get("services", {})
        for service_name, service_info in services.items():
            if service_name == "host_access":
                continue
                
            service_status = service_info.get("status", "unknown")
            if service_status == "healthy":
                report += f"✅ **{service_name.title()}**: Ready for generation\\n"
                report += f"   - URL: {service_info.get('url', 'N/A')}\\n"
            elif service_status == "unhealthy":
                report += f"⚠️ **{service_name.title()}**: Service issues detected\\n"
                report += f"   - Error: {service_info.get('message', 'Unknown error')}\\n"
            else:
                report += f"❌ **{service_name.title()}**: Not accessible\\n"
                report += f"   - Error: {service_info.get('error', 'Connection failed')}\\n"
        
        # Capabilities
        report += "\\n🎯 **Available Capabilities**:\\n"
        if services.get("pollinations", {}).get("status") == "healthy":
            report += "• 🖼️ **Image Generation** via Pollinations.AI (FLUX.1)\\n"
        if services.get("wan2gp", {}).get("status") == "healthy":
            report += "• 🎬 **Video Generation** via Wan2GP (Multiple models)\\n"
        if services.get("localai", {}).get("status") == "healthy":
            report += "• 🤖 **AI Chat** via LocalAI\\n"
        
        # Usage instructions
        report += "\\n📋 **Usage Instructions**:\\n"
        report += "• Use `host_generate_image('prompt', category='artwork')` for images\\n"
        report += "• Use `host_generate_video('prompt', duration=4)` for videos\\n"
        report += "• Use `host_check_multimedia_services()` for status updates\\n"
        
        return report

# Global integration instance
multimedia_integration = MultimediaServiceIntegration()

# Main Agent Zero tools
def generate_multimedia_content(prompt: str, content_type: str = None, **kwargs) -> Dict[str, Any]:
    """
    Main multimedia generation tool for Agent Zero
    
    Args:
        prompt: Description of content to generate
        content_type: 'image', 'video', or auto-detected if None
        **kwargs: Additional parameters (width, height, duration, resolution, category, etc.)
    
    Returns:
        Dict with generation results and file information
    """
    import asyncio
    return asyncio.run(multimedia_integration.smart_generate(prompt, content_type, **kwargs))

def analyze_multimedia_request(message: str) -> Dict[str, Any]:
    """
    Analyze message for multimedia generation requests
    
    Args:
        message: User message to analyze
        
    Returns:
        Dict with detection results and confidence scores
    """
    return multimedia_integration.analyze_multimedia_request(message)

def multimedia_service_status() -> Dict[str, Any]:
    """
    Get comprehensive status of all multimedia services
    
    Returns:
        Dict with service health, availability, and access information
    """
    return multimedia_integration.check_service_status()

def multimedia_service_report() -> str:
    """
    Generate human-readable multimedia services report
    
    Returns:
        Formatted report string with service status and capabilities
    """
    return multimedia_integration.generate_service_report()

# Re-export host tools for direct access
try:
    from .host_multimedia_client import (
        host_check_multimedia_services,
        host_generate_image,
        host_generate_video,
        host_chat_localai,
        host_get_localai_models
    )
except ImportError:
    from host_multimedia_client import (
        host_check_multimedia_services,
        host_generate_image,
        host_generate_video,
        host_chat_localai,
        host_get_localai_models
    )

# Export all tools
__all__ = [
    # Main unified tools
    'generate_multimedia_content',
    'analyze_multimedia_request', 
    'multimedia_service_status',
    'multimedia_service_report',
    
    # Direct host tools
    'host_check_multimedia_services',
    'host_generate_image',
    'host_generate_video', 
    'host_chat_localai',
    'host_get_localai_models',
    
    # Integration instance
    'multimedia_integration'
]