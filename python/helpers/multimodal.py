"""
Multimodal AI Integration for Pareng Boyong
Integrates image, video, and audio generation capabilities
"""

import asyncio
import logging
from typing import Optional, Dict, Any, List
import re

from .image_generation import image_generator, generate_image
from .video_generation import video_generator, generate_video, animate_image
from .audio_generation import audio_generator, generate_music, generate_sound_effect, generate_speech_bark

logger = logging.getLogger(__name__)

class MultimodalProcessor:
    def __init__(self):
        self.initialized = False
        
    async def initialize(self):
        """Initialize all multimodal services"""
        if self.initialized:
            return
            
        logger.info("🎨 Initializing multimodal AI services...")
        
        # Initialize all generators
        await asyncio.gather(
            image_generator.initialize(),
            video_generator.initialize(),
            audio_generator.initialize()
        )
        
        self.initialized = True
        
        # Log available services
        services = []
        if image_generator.flux_available or image_generator.sd_available:
            services.append("🖼️ Image Generation")
        if any([video_generator.hunyuan_available, video_generator.cogvideo_available, video_generator.animatediff_available]):
            services.append("🎬 Video Generation")
        if audio_generator.musicgen_available or audio_generator.bark_available:
            services.append("🎵 Audio Generation")
            
        if services:
            logger.info(f"✅ Multimodal services ready: {', '.join(services)}")
        else:
            logger.warning("⚠️ No multimodal services available")
    
    async def process_generation_request(self, user_input: str, message_context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Process user requests for multimedia generation
        Returns dict with generated content and metadata
        """
        
        if not self.initialized:
            await self.initialize()
        
        # Detect generation intent and type
        generation_type = self._detect_generation_type(user_input)
        
        if not generation_type:
            return {"type": "none", "content": None}
        
        try:
            if generation_type == "image":
                return await self._handle_image_generation(user_input, message_context)
            elif generation_type == "video":
                return await self._handle_video_generation(user_input, message_context)
            elif generation_type == "audio":
                return await self._handle_audio_generation(user_input, message_context)
            elif generation_type == "music":
                return await self._handle_music_generation(user_input, message_context)
            elif generation_type == "animation":
                return await self._handle_animation_request(user_input, message_context)
        except Exception as e:
            logger.error(f"Multimodal generation failed: {e}")
            return {"type": "error", "content": str(e)}
        
        return {"type": "none", "content": None}
    
    def _detect_generation_type(self, user_input: str) -> Optional[str]:
        """Detect what type of multimedia generation is requested"""
        
        lower_input = user_input.lower()
        
        # Image generation keywords
        image_keywords = [
            "create image", "generate image", "draw", "make picture", "create art",
            "paint", "sketch", "illustrate", "design", "create illustration",
            "gumawa ng larawan", "lumikha ng image", "mag-drawing"  # Filipino
        ]
        
        # Video generation keywords  
        video_keywords = [
            "create video", "generate video", "make video", "animate",
            "create animation", "moving picture", "short clip",
            "gumawa ng video", "lumikha ng animation"  # Filipino
        ]
        
        # Music generation keywords
        music_keywords = [
            "create music", "generate music", "compose", "make song",
            "create beat", "make melody", "background music",
            "gumawa ng kanta", "lumikha ng music"  # Filipino
        ]
        
        # Audio/Sound generation keywords
        audio_keywords = [
            "create sound", "sound effect", "make audio", "generate audio",
            "ambient sound", "background sound", "create sfx",
            "gumawa ng tunog", "sound effects"  # Filipino
        ]
        
        # Animation keywords (for existing images)
        animation_keywords = [
            "animate this", "animate the image", "make it move", 
            "add movement", "bring to life"
        ]
        
        # Check for each type
        if any(keyword in lower_input for keyword in image_keywords):
            return "image"
        elif any(keyword in lower_input for keyword in video_keywords):
            return "video"
        elif any(keyword in lower_input for keyword in music_keywords):
            return "music"
        elif any(keyword in lower_input for keyword in audio_keywords):
            return "audio"
        elif any(keyword in lower_input for keyword in animation_keywords):
            return "animation"
        
        return None
    
    async def _handle_image_generation(self, user_input: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Handle image generation requests"""
        
        # Extract prompt from user input
        prompt = self._extract_generation_prompt(user_input, "image")
        
        # Generate image
        image_base64 = await generate_image(prompt)
        
        if image_base64:
            return {
                "type": "image",
                "content": f"<image>{image_base64}</image>",
                "prompt": prompt,
                "message": f"🎨 Generated image: {prompt}"
            }
        else:
            return {
                "type": "error",
                "content": "Sorry, I couldn't generate the image. Image generation services may not be available."
            }
    
    async def _handle_video_generation(self, user_input: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Handle video generation requests"""
        
        # Extract prompt from user input
        prompt = self._extract_generation_prompt(user_input, "video")
        
        # Generate video
        video_base64 = await generate_video(prompt, duration=6, fps=8)
        
        if video_base64:
            return {
                "type": "video", 
                "content": f"<video format=\"mp4\">{video_base64}</video>",
                "prompt": prompt,
                "message": f"🎬 Generated video: {prompt}"
            }
        else:
            return {
                "type": "error",
                "content": "Sorry, I couldn't generate the video. Video generation services may not be available."
            }
    
    async def _handle_audio_generation(self, user_input: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Handle audio/sound effect generation requests"""
        
        # Extract prompt from user input
        prompt = self._extract_generation_prompt(user_input, "audio")
        
        # Generate sound effect
        audio_base64 = await generate_sound_effect(prompt, duration=5)
        
        if audio_base64:
            return {
                "type": "audio",
                "content": f"<audio format=\"wav\" title=\"{prompt}\">{audio_base64}</audio>",
                "prompt": prompt,
                "message": f"🔊 Generated sound effect: {prompt}"
            }
        else:
            return {
                "type": "error", 
                "content": "Sorry, I couldn't generate the audio. Audio generation services may not be available."
            }
    
    async def _handle_music_generation(self, user_input: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Handle music generation requests"""
        
        # Extract prompt from user input
        prompt = self._extract_generation_prompt(user_input, "music")
        
        # Generate music
        audio_base64 = await generate_music(prompt, duration=15)
        
        if audio_base64:
            return {
                "type": "audio",
                "content": f"<audio format=\"wav\" title=\"{prompt}\">{audio_base64}</audio>",
                "prompt": prompt,
                "message": f"🎵 Generated music: {prompt}"
            }
        else:
            return {
                "type": "error",
                "content": "Sorry, I couldn't generate the music. Music generation services may not be available."
            }
    
    async def _handle_animation_request(self, user_input: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Handle requests to animate existing images"""
        
        # Look for images in the context or conversation
        # For now, return instruction to generate image first
        return {
            "type": "text",
            "content": "To animate an image, first share or generate an image, then ask me to animate it. For example: 'Create an image of a cat, then animate it walking.'"
        }
    
    def _extract_generation_prompt(self, user_input: str, generation_type: str) -> str:
        """Extract the actual generation prompt from user input"""
        
        # Remove common prefixes
        common_prefixes = [
            f"create {generation_type}", f"generate {generation_type}", f"make {generation_type}",
            f"draw", f"sketch", f"compose", f"create", f"generate", f"make",
            "gumawa ng", "lumikha ng", "mag-"  # Filipino prefixes
        ]
        
        prompt = user_input.lower()
        
        # Remove prefixes
        for prefix in common_prefixes:
            if prompt.startswith(prefix):
                prompt = prompt[len(prefix):].strip()
                break
        
        # Remove common conjunctions
        prompt = re.sub(r'^(of|about|that shows|showing|with)\s+', '', prompt)
        
        # Clean up
        prompt = prompt.strip('.,!?')
        
        # If prompt is too short, use original input
        if len(prompt) < 5:
            prompt = user_input
        
        return prompt
    
    def get_capabilities_summary(self) -> str:
        """Get a summary of available multimodal capabilities"""
        
        capabilities = []
        
        if image_generator.flux_available or image_generator.sd_available:
            capabilities.append("🖼️ **Image Generation**: Create images from text descriptions")
            
        if any([video_generator.hunyuan_available, video_generator.cogvideo_available, video_generator.animatediff_available]):
            capabilities.append("🎬 **Video Generation**: Create short videos and animations")
            
        if audio_generator.musicgen_available:
            capabilities.append("🎵 **Music Generation**: Compose music and melodies")
            capabilities.append("🔊 **Sound Effects**: Generate audio effects and ambient sounds")
            
        if audio_generator.bark_available:
            capabilities.append("🗣️ **Enhanced Speech**: Generate expressive speech with emotion")
        
        if capabilities:
            return "**🎨 Multimodal Capabilities Available:**\n\n" + "\n".join(capabilities) + "\n\nJust ask me to create, generate, or make images, videos, music, or sounds!"
        else:
            return "⚠️ No multimodal generation services are currently available. You may need to install and start the generation services."

# Global instance
multimodal_processor = MultimodalProcessor()

# Convenience functions for integration
async def process_multimedia_request(user_input: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
    """Main function for processing multimedia generation requests"""
    return await multimodal_processor.process_generation_request(user_input, context)

async def initialize_multimodal() -> bool:
    """Initialize multimodal services"""
    try:
        await multimodal_processor.initialize()
        return True
    except Exception as e:
        logger.error(f"Failed to initialize multimodal services: {e}")
        return False

def get_multimodal_capabilities() -> str:
    """Get summary of available capabilities"""
    return multimodal_processor.get_capabilities_summary()

# Test function
async def test_multimodal():
    """Test multimodal capabilities"""
    await initialize_multimodal()
    
    # Test image generation
    image_result = await process_multimedia_request("Create an image of a sunset over mountains")
    print(f"Image test: {'✅ SUCCESS' if image_result['type'] != 'error' else '❌ FAILED'}")
    
    # Test video generation
    video_result = await process_multimedia_request("Generate a video of waves crashing")
    print(f"Video test: {'✅ SUCCESS' if video_result['type'] != 'error' else '❌ FAILED'}")
    
    # Test music generation
    music_result = await process_multimedia_request("Create music that is peaceful and relaxing")
    print(f"Music test: {'✅ SUCCESS' if music_result['type'] != 'error' else '❌ FAILED'}")
    
    print("\n" + get_multimodal_capabilities())

if __name__ == "__main__":
    asyncio.run(test_multimodal())