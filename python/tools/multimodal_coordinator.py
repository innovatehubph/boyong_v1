"""
Multimodal Coordinator Tool for Pareng Boyong
Intelligently detects and routes multimedia generation requests
"""

import asyncio
import re
from typing import Optional, Dict, Any, List
from python.helpers.tool import Tool, Response
from python.helpers.print_style import PrintStyle

class MultimodalCoordinator(Tool):
    async def execute(self, **kwargs) -> Response:
        """Coordinate multimodal generation based on user request"""
        
        user_request = kwargs.get("user_request", "").strip()
        context = kwargs.get("context", {})
        auto_execute = kwargs.get("auto_execute", True)
        
        if not user_request:
            return Response(message="❌ Please provide a user request to analyze.", break_loop=False)
        
        try:
            # Detect generation intent
            generation_requests = self._detect_generation_requests(user_request, context)
            
            if not generation_requests:
                return Response(
                    message="ℹ️ No multimedia generation requests detected in the user input.",
                    break_loop=False
                )
            
            if not auto_execute:
                # Just return the detected requests for review
                requests_summary = "\n".join([
                    f"• **{req['type'].title()}**: {req['prompt']}" 
                    for req in generation_requests
                ])
                return Response(
                    message=f"🎨 **Detected Multimedia Generation Requests:**\n\n{requests_summary}\n\nUse specific generation tools to execute these requests.",
                    break_loop=False
                )
            
            # Execute generation requests
            results = []
            for request in generation_requests:
                PrintStyle(font_color="cyan", padding=False).print(f"🎨 Processing {request['type']} request...")
                result = await self._execute_generation_request(request)
                if result:
                    results.append(result)
            
            if not results:
                return Response(
                    message="❌ Failed to generate any multimedia content. Generation services may not be available.",
                    break_loop=False
                )
            
            # Combine results
            return self._combine_results(results)
                
        except Exception as e:
            PrintStyle.error(f"Multimodal coordination failed: {e}")
            return Response(
                message=f"❌ Multimodal coordination failed: {str(e)}",
                break_loop=False
            )
    
    def _detect_generation_requests(self, user_request: str, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Detect and parse multimedia generation requests from user input"""
        
        requests = []
        lower_request = user_request.lower()
        
        # Image generation detection
        image_patterns = [
            r'create\s+(?:an?\s+)?image\s+(?:of\s+)?(.*?)(?:\.|$|and|then)',
            r'generate\s+(?:an?\s+)?(?:image|picture|photo)\s+(?:of\s+)?(.*?)(?:\.|$|and|then)',
            r'draw\s+(?:me\s+)?(?:an?\s+)?(.*?)(?:\.|$|and|then)',
            r'make\s+(?:an?\s+)?(?:image|picture|photo)\s+(?:of\s+)?(.*?)(?:\.|$|and|then)',
            r'show\s+me\s+(?:an?\s+)?(?:image|picture|photo)\s+(?:of\s+)?(.*?)(?:\.|$|and|then)',
            # Filipino patterns
            r'gumawa\s+ng\s+(?:larawan|image)\s+(?:ng\s+)?(.*?)(?:\.|$|at|tapos)',
            r'lumikha\s+ng\s+(?:larawan|image)\s+(?:ng\s+)?(.*?)(?:\.|$|at|tapos)'
        ]
        
        for pattern in image_patterns:
            matches = re.finditer(pattern, lower_request, re.IGNORECASE)
            for match in matches:
                prompt = match.group(1).strip()
                if prompt and len(prompt) > 3:
                    requests.append({
                        'type': 'image',
                        'prompt': prompt,
                        'original_text': match.group(0)
                    })
        
        # Video generation detection
        video_patterns = [
            r'create\s+(?:a\s+)?video\s+(?:of\s+)?(.*?)(?:\.|$|and|then)',
            r'generate\s+(?:a\s+)?video\s+(?:of\s+)?(.*?)(?:\.|$|and|then)',
            r'make\s+(?:a\s+)?video\s+(?:of\s+)?(.*?)(?:\.|$|and|then)',
            r'animate\s+(?:this\s+|the\s+)?(?:image\s+)?(?:of\s+)?(.*?)(?:\.|$|and|then)',
            # Filipino patterns
            r'gumawa\s+ng\s+video\s+(?:ng\s+)?(.*?)(?:\.|$|at|tapos)',
            r'lumikha\s+ng\s+video\s+(?:ng\s+)?(.*?)(?:\.|$|at|tapos)'
        ]
        
        for pattern in video_patterns:
            matches = re.finditer(pattern, lower_request, re.IGNORECASE)
            for match in matches:
                prompt = match.group(1).strip()
                if prompt and len(prompt) > 3:
                    # Check if this is image animation request
                    is_animation = 'animate' in match.group(0).lower()
                    requests.append({
                        'type': 'video',
                        'prompt': prompt,
                        'original_text': match.group(0),
                        'is_animation': is_animation,
                        'image_to_animate': context.get('previous_images', [None])[0] if is_animation else None
                    })
        
        # Music generation detection
        music_patterns = [
            r'create\s+(?:some\s+)?music\s+(?:that\s+is\s+|about\s+)?(.*?)(?:\.|$|and|then)',
            r'generate\s+(?:some\s+)?(?:music|song)\s+(?:that\s+is\s+|about\s+)?(.*?)(?:\.|$|and|then)',
            r'make\s+(?:some\s+)?(?:music|song)\s+(?:that\s+is\s+|about\s+)?(.*?)(?:\.|$|and|then)',
            r'compose\s+(?:some\s+)?(?:music|song)\s+(?:that\s+is\s+|about\s+)?(.*?)(?:\.|$|and|then)',
            r'play\s+(?:some\s+)?music\s+(?:that\s+is\s+)?(.*?)(?:\.|$|and|then)',
            # Filipino patterns
            r'gumawa\s+ng\s+(?:kanta|music)\s+(?:na\s+)?(.*?)(?:\.|$|at|tapos)',
            r'lumikha\s+ng\s+(?:kanta|music)\s+(?:na\s+)?(.*?)(?:\.|$|at|tapos)'
        ]
        
        for pattern in music_patterns:
            matches = re.finditer(pattern, lower_request, re.IGNORECASE)
            for match in matches:
                prompt = match.group(1).strip()
                if prompt and len(prompt) > 3:
                    requests.append({
                        'type': 'music',
                        'prompt': prompt,
                        'original_text': match.group(0)
                    })
        
        # Sound effect detection
        sound_patterns = [
            r'create\s+(?:a\s+)?sound\s+(?:effect\s+)?(?:of\s+)?(.*?)(?:\.|$|and|then)',
            r'generate\s+(?:a\s+)?sound\s+(?:effect\s+)?(?:of\s+)?(.*?)(?:\.|$|and|then)',
            r'make\s+(?:a\s+)?sound\s+(?:effect\s+)?(?:of\s+)?(.*?)(?:\.|$|and|then)',
            r'(?:sound\s+effect|sfx)\s+(?:of\s+)?(.*?)(?:\.|$|and|then)',
            # Filipino patterns
            r'gumawa\s+ng\s+tunog\s+(?:ng\s+)?(.*?)(?:\.|$|at|tapos)'
        ]
        
        for pattern in sound_patterns:
            matches = re.finditer(pattern, lower_request, re.IGNORECASE)
            for match in matches:
                prompt = match.group(1).strip()
                if prompt and len(prompt) > 3:
                    requests.append({
                        'type': 'sound_effect',
                        'prompt': prompt,
                        'original_text': match.group(0)
                    })
        
        return requests
    
    async def _execute_generation_request(self, request: Dict[str, Any]) -> Optional[str]:
        """Execute a single generation request"""
        
        try:
            request_type = request['type']
            prompt = request['prompt']
            
            if request_type == 'image':
                return await self._generate_image(prompt)
            elif request_type == 'video':
                if request.get('image_to_animate'):
                    return await self._animate_image(request['image_to_animate'], prompt)
                else:
                    return await self._generate_video(prompt)
            elif request_type == 'music':
                return await self._generate_music(prompt)
            elif request_type == 'sound_effect':
                return await self._generate_sound_effect(prompt)
            
        except Exception as e:
            PrintStyle.error(f"Failed to execute {request['type']} generation: {e}")
            return None
    
    async def _generate_image(self, prompt: str) -> Optional[str]:
        """Generate image using image generator"""
        try:
            from python.helpers.image_generation import generate_image
            image_base64 = await generate_image(prompt)
            if image_base64:
                return f"🎨 **Generated Image:** {prompt}\n\n<image>{image_base64}</image>"
        except Exception as e:
            PrintStyle.warning(f"Image generation failed: {e}")
        return None
    
    async def _generate_video(self, prompt: str) -> Optional[str]:
        """Generate video using video generator"""
        try:
            from python.helpers.video_generation import generate_video
            video_base64 = await generate_video(prompt, duration=4, fps=8)
            if video_base64:
                return f"🎬 **Generated Video:** {prompt}\n\n<video format=\"mp4\">{video_base64}</video>"
        except Exception as e:
            PrintStyle.warning(f"Video generation failed: {e}")
        return None
    
    async def _animate_image(self, image_base64: str, prompt: str) -> Optional[str]:
        """Animate image using video generator"""
        try:
            from python.helpers.video_generation import animate_image
            video_base64 = await animate_image(image_base64, prompt, duration=3, fps=8)
            if video_base64:
                return f"🎬 **Animated Image:** {prompt}\n\n<video format=\"mp4\">{video_base64}</video>"
        except Exception as e:
            PrintStyle.warning(f"Image animation failed: {e}")
        return None
    
    async def _generate_music(self, prompt: str) -> Optional[str]:
        """Generate music using music generator"""
        try:
            from python.helpers.audio_generation import generate_music
            audio_base64 = await generate_music(prompt, duration=15)
            if audio_base64:
                return f"🎵 **Generated Music:** {prompt}\n\n<audio format=\"wav\" title=\"Generated Music\">{audio_base64}</audio>"
        except Exception as e:
            PrintStyle.warning(f"Music generation failed: {e}")
        return None
    
    async def _generate_sound_effect(self, prompt: str) -> Optional[str]:
        """Generate sound effect using audio generator"""
        try:
            from python.helpers.audio_generation import generate_sound_effect
            audio_base64 = await generate_sound_effect(prompt, duration=5)
            if audio_base64:
                return f"🔊 **Generated Sound Effect:** {prompt}\n\n<audio format=\"wav\" title=\"Sound Effect\">{audio_base64}</audio>"
        except Exception as e:
            PrintStyle.warning(f"Sound effect generation failed: {e}")
        return None
    
    def _combine_results(self, results: List[str]) -> Response:
        """Combine multiple generation results into a single response"""
        
        if len(results) == 1:
            return Response(message=results[0], break_loop=False)
        
        combined_message = "🎨 **Multiple Media Generated Successfully!**\n\n"
        combined_message += "\n\n---\n\n".join(results)
        
        return Response(message=combined_message, break_loop=False)

# Register the tool
def register():
    return MultimodalCoordinator()