"""
Video Generation Tool for Pareng Boyong
Uses HunyuanVideo, CogVideoX, and AnimateDiff for video generation
"""

import asyncio
import base64
from typing import Optional, Dict, Any
from python.helpers.tool import Tool, Response
from python.helpers.print_style import PrintStyle

class VideoGenerator(Tool):
    async def execute(self, **kwargs) -> Response:
        """Execute video generation"""
        
        prompt = kwargs.get("prompt", "").strip()
        image_to_animate = kwargs.get("image_to_animate")
        duration = kwargs.get("duration", 4)
        fps = kwargs.get("fps", 8)
        style = kwargs.get("style", "realistic")
        motion_intensity = kwargs.get("motion_intensity", "moderate")
        aspect_ratio = kwargs.get("aspect_ratio", "16:9")
        model_preference = kwargs.get("model_preference", "auto")
        
        if not prompt:
            return Response(message="❌ Please provide a description for the video to generate.", break_loop=False)
        
        try:
            if image_to_animate:
                PrintStyle(font_color="magenta", padding=False).print(f"🎬 Animating image: {prompt[:50]}...")
                generation_type = "Image-to-Video"
            else:
                PrintStyle(font_color="magenta", padding=False).print(f"🎬 Generating video: {prompt[:50]}...")
                generation_type = "Text-to-Video"
            
            # Enhance prompt with style and motion
            enhanced_prompt = self._enhance_prompt(prompt, style, motion_intensity)
            
            # Get dimensions from aspect ratio
            width, height = self._get_dimensions(aspect_ratio)
            
            # Generate the video
            if image_to_animate:
                video_base64 = await self._animate_image(
                    image_to_animate,
                    enhanced_prompt,
                    duration,
                    fps
                )
            else:
                video_base64 = await self._generate_video(
                    enhanced_prompt,
                    duration,
                    fps,
                    width,
                    height,
                    model_preference
                )
            
            if not video_base64:
                return Response(
                    message="❌ Failed to generate video. Video generation services may not be available.\n\n**Tip:** Make sure ComfyUI with video models is running.",
                    break_loop=False
                )
            
            return Response(
                message=f"""🎬 **Video Generated Successfully!**

**Type:** {generation_type}
**Prompt:** {prompt}
**Style:** {style.title()}
**Duration:** {duration} seconds ({duration * fps} frames)
**Resolution:** {width}x{height}
**Motion:** {motion_intensity.title()}

<video format="mp4">{video_base64}</video>""",
                break_loop=False
            )
                
        except Exception as e:
            PrintStyle.error(f"Video generation failed: {e}")
            return Response(
                message=f"❌ Video generation failed: {str(e)}\n\n**Possible solutions:**\n- Ensure ComfyUI with video models is running\n- Check that HunyuanVideo, CogVideoX, or AnimateDiff nodes are installed\n- Try a shorter duration or simpler prompt",
                break_loop=False
            )
    
    async def _generate_video(
        self, 
        prompt: str, 
        duration: int, 
        fps: int, 
        width: int, 
        height: int,
        model_preference: str
    ) -> Optional[str]:
        """Generate video from text"""
        
        try:
            # Import the video generation helper
            from python.helpers.video_generation import generate_video
            
            return await generate_video(
                prompt=prompt,
                duration=duration,
                fps=fps,
                width=width,
                height=height,
                model_preference=model_preference
            )
            
        except ImportError:
            PrintStyle.warning("Video generation module not available")
            return None
        except Exception as e:
            PrintStyle.error(f"Video generation error: {e}")
            return None
    
    async def _animate_image(
        self, 
        image_base64: str, 
        prompt: str, 
        duration: int, 
        fps: int
    ) -> Optional[str]:
        """Animate an existing image"""
        
        try:
            # Import the video generation helper
            from python.helpers.video_generation import animate_image
            
            return await animate_image(
                image_base64=image_base64,
                prompt=prompt,
                duration=duration,
                fps=fps
            )
            
        except ImportError:
            PrintStyle.warning("Video animation module not available")
            return None
        except Exception as e:
            PrintStyle.error(f"Image animation error: {e}")
            return None
    
    def _enhance_prompt(self, prompt: str, style: str, motion_intensity: str) -> str:
        """Enhance prompt with style and motion keywords"""
        
        style_enhancements = {
            "realistic": "photorealistic, natural lighting, high quality",
            "cinematic": "cinematic, dramatic lighting, film quality, professional",
            "animated": "smooth animation, fluid motion, animated style",
            "artistic": "artistic, creative, expressive, beautiful",
            "documentary": "documentary style, natural, informative"
        }
        
        motion_enhancements = {
            "subtle": "gentle movement, soft motion, calm",
            "moderate": "smooth motion, balanced movement",
            "dynamic": "dynamic motion, active movement, energetic", 
            "intense": "fast motion, dramatic movement, high energy"
        }
        
        enhancements = []
        if style in style_enhancements:
            enhancements.append(style_enhancements[style])
        if motion_intensity in motion_enhancements:
            enhancements.append(motion_enhancements[motion_intensity])
        
        if enhancements:
            return f"{prompt}, {', '.join(enhancements)}"
        return prompt
    
    def _get_dimensions(self, aspect_ratio: str) -> tuple[int, int]:
        """Get video dimensions based on aspect ratio"""
        
        # Standard video resolutions
        aspect_ratios = {
            "16:9": (1280, 720),   # HD Landscape
            "9:16": (720, 1280),   # Vertical/Portrait
            "1:1": (1024, 1024),   # Square
            "4:3": (1024, 768)     # Classic TV
        }
        
        return aspect_ratios.get(aspect_ratio, (1280, 720))

# Register the tool
def register():
    return VideoGenerator()