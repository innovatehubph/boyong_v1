"""
Advanced Video Generation Tool for Pareng Boyong
Integrates Wan2GP, MultiTalk, Wan2.1-VACE-14B, and FusioniX models
"""

import asyncio
import base64
import json
from typing import Optional, Dict, Any, List
from python.helpers.tool import Tool, Response
from python.helpers.print_style import PrintStyle

class AdvancedVideoGenerator(Tool):
    async def execute(self, **kwargs) -> Response:
        """Execute advanced video generation"""
        
        prompt = kwargs.get("prompt", "").strip()
        video_type = kwargs.get("video_type", "text_to_video")
        model_preference = kwargs.get("model_preference", "auto")
        image_to_animate = kwargs.get("image_to_animate")
        duration = kwargs.get("duration", 5)
        resolution = kwargs.get("resolution", "720p")
        fps = kwargs.get("fps", 24)
        style = kwargs.get("style", "cinematic")
        motion_intensity = kwargs.get("motion_intensity", "moderate")
        characters = kwargs.get("characters", [])
        audio_sync = kwargs.get("audio_sync", False)
        enhancement_options = kwargs.get("enhancement_options", {})
        advanced_settings = kwargs.get("advanced_settings", {})
        
        if not prompt:
            return Response(message="❌ Please provide a description for the video to generate.", break_loop=False)
        
        try:
            # Select optimal model based on request type and preferences
            selected_model = self._select_optimal_model(
                video_type, model_preference, characters, audio_sync, duration, resolution
            )
            
            PrintStyle(font_color="magenta", padding=False).print(
                f"🎬 Generating {video_type} video with {selected_model}: {prompt[:50]}..."
            )
            
            # Enhance prompt based on style and model capabilities
            enhanced_prompt = self._enhance_prompt(prompt, style, motion_intensity, selected_model)
            
            # Generate video using selected model
            generation_result = await self._generate_with_model(
                selected_model=selected_model,
                prompt=enhanced_prompt,
                video_type=video_type,
                image_to_animate=image_to_animate,
                duration=duration,
                resolution=resolution,
                fps=fps,
                characters=characters,
                audio_sync=audio_sync,
                enhancement_options=enhancement_options,
                advanced_settings=advanced_settings
            )
            
            if not generation_result:
                return Response(
                    message=f"❌ Failed to generate video with {selected_model}. Video generation services may not be available.\\n\\n**Tip:** Ensure advanced video models are installed and running.",
                    type="error"
                )
            
            # Build comprehensive response
            return Response(
                message=f"""🎬 **Advanced Video Generated Successfully!**

**Model Used**: {selected_model.replace('_', ' ').title()}
**Type**: {video_type.replace('_', '-').title()}
**Prompt**: {prompt}
**Style**: {style.title()}
**Resolution**: {resolution} @ {fps}fps
**Duration**: {duration} seconds ({duration * fps} frames)
**Motion**: {motion_intensity.title()}

<video format="mp4">{generation_result}</video>

*Generated using state-of-the-art AI models for professional quality results.*""",
                type="info"
            )
                
        except Exception as e:
            PrintStyle.error(f"Advanced video generation failed: {e}")
            return Response(
                message=f"❌ Advanced video generation failed: {str(e)}\\n\\n**Possible solutions:**\\n- Ensure Wan2GP/MultiTalk services are running\\n- Check GPU memory and model availability\\n- Try shorter duration or lower resolution\\n- Verify model installations",
                type="error"
            )

    def _select_optimal_model(
        self, 
        video_type: str, 
        model_preference: str, 
        characters: List[str], 
        audio_sync: bool,
        duration: int,
        resolution: str
    ) -> str:
        """Intelligently select the best model for the request"""
        
        # If user specified a preference, respect it (unless it's auto)
        if model_preference != "auto":
            return model_preference
        
        # Intelligent model selection based on request characteristics
        
        # MultiTalk for conversational videos
        if video_type == "conversational" or characters or audio_sync:
            return "multitalk"
        
        # FusioniX for speed and cinematic quality
        if video_type == "cinematic" or duration <= 8:
            return "fusionix"
        
        # Wan2GP for low-resource environments
        if resolution == "480p" or duration > 10:
            return "wan2gp"
        
        # Wan VACE 14B for best quality
        if video_type in ["text_to_video", "image_to_video"] and resolution in ["720p", "1080p"]:
            return "wan_vace_14b"
        
        # Default to FusioniX for balanced performance
        return "fusionix"

    def _enhance_prompt(self, prompt: str, style: str, motion_intensity: str, model: str) -> str:
        """Enhance prompt based on style, motion, and model capabilities"""
        
        enhancements = []
        
        # Style-specific enhancements
        style_enhancements = {
            "realistic": "photorealistic, natural lighting, high detail, real-world",
            "cinematic": "cinematic composition, dramatic lighting, film-quality, professional cinematography",
            "cartoon": "cartoon style, animated, colorful, stylized characters",
            "anime": "anime style, detailed animation, vibrant colors, expressive characters",
            "photorealistic": "ultra-realistic, high-resolution, detailed textures, natural physics",
            "artistic": "artistic interpretation, creative visual style, unique aesthetic"
        }
        
        # Motion-specific enhancements
        motion_enhancements = {
            "minimal": "subtle movement, gentle motion, calm atmosphere",
            "subtle": "soft movement, natural flow, elegant transitions",
            "moderate": "balanced motion, dynamic movement, engaging action",
            "dynamic": "energetic movement, active scenes, fluid motion", 
            "dramatic": "intense motion, dramatic action, powerful movement"
        }
        
        # Model-specific optimizations
        if model == "wan_vace_14b":
            enhancements.append("high-quality, detailed, professional")
        elif model == "fusionix":
            enhancements.append("smooth motion, cinematic flow")
        elif model == "multitalk":
            enhancements.append("conversational, character-focused, expressive")
        elif model == "wan2gp":
            enhancements.append("optimized generation, efficient processing")
        
        # Add style and motion enhancements
        if style in style_enhancements:
            enhancements.append(style_enhancements[style])
        if motion_intensity in motion_enhancements:
            enhancements.append(motion_enhancements[motion_intensity])
        
        # Combine with original prompt
        if enhancements:
            return f"{prompt}, {', '.join(enhancements)}"
        return prompt

    async def _generate_with_model(
        self,
        selected_model: str,
        prompt: str,
        video_type: str,
        image_to_animate: Optional[str] = None,
        duration: int = 5,
        resolution: str = "720p",
        fps: int = 24,
        characters: List[str] = None,
        audio_sync: bool = False,
        enhancement_options: Dict[str, Any] = None,
        advanced_settings: Dict[str, Any] = None
    ) -> Optional[str]:
        """Generate video using the selected model"""
        
        try:
            if selected_model == "wan_vace_14b":
                return await self._generate_wan_vace(
                    prompt, video_type, image_to_animate, duration, resolution, fps, advanced_settings
                )
            elif selected_model == "fusionix":
                return await self._generate_fusionix(
                    prompt, video_type, image_to_animate, duration, resolution, fps, enhancement_options, advanced_settings
                )
            elif selected_model == "multitalk":
                return await self._generate_multitalk(
                    prompt, characters, audio_sync, duration, resolution, fps, advanced_settings
                )
            elif selected_model == "wan2gp":
                return await self._generate_wan2gp(
                    prompt, video_type, image_to_animate, duration, resolution, fps, advanced_settings
                )
            else:
                # Fallback to existing video generation
                from python.helpers.video_generation import generate_video
                return await generate_video(
                    prompt=prompt,
                    duration=duration,
                    fps=fps,
                    width=self._get_resolution_width(resolution),
                    height=self._get_resolution_height(resolution)
                )
                
        except ImportError:
            PrintStyle.warning(f"Model {selected_model} not available, using fallback")
            return None
        except Exception as e:
            PrintStyle.error(f"Generation failed with {selected_model}: {e}")
            return None

    async def _generate_wan_vace(
        self, prompt: str, video_type: str, image_to_animate: Optional[str], 
        duration: int, resolution: str, fps: int, advanced_settings: Dict[str, Any]
    ) -> Optional[str]:
        """Generate video using Wan2.1-VACE-14B model"""
        
        try:
            from python.helpers.wan_vace_generation import generate_wan_video
            
            settings = advanced_settings or {}
            
            return await generate_wan_video(
                prompt=prompt,
                video_type=video_type,
                image_input=image_to_animate,
                duration=duration,
                resolution=resolution,
                fps=fps,
                sampling_steps=settings.get("sampling_steps", 10),
                guidance_scale=settings.get("guidance_scale", 7.5),
                seed=settings.get("seed"),
                low_vram=settings.get("low_vram", False)
            )
            
        except ImportError:
            PrintStyle.warning("Wan2.1-VACE-14B model not available")
            return None

    async def _generate_fusionix(
        self, prompt: str, video_type: str, image_to_animate: Optional[str],
        duration: int, resolution: str, fps: int, enhancement_options: Dict[str, Any], 
        advanced_settings: Dict[str, Any]
    ) -> Optional[str]:
        """Generate video using Wan14BT2VFusioniX model"""
        
        try:
            from python.helpers.fusionix_generation import generate_fusionix_video
            
            settings = advanced_settings or {}
            enhancements = enhancement_options or {}
            
            return await generate_fusionix_video(
                prompt=prompt,
                video_type=video_type,
                image_input=image_to_animate,
                duration=duration,
                resolution=resolution,
                fps=fps,
                sampling_steps=settings.get("sampling_steps", 8),  # Optimized for FusioniX
                guidance_scale=settings.get("guidance_scale", 7.5),
                seed=settings.get("seed"),
                temporal_smoothing=enhancements.get("temporal_smoothing", True),
                detail_enhancement=enhancements.get("detail_enhancement", True),
                color_grading=enhancements.get("color_grading", "none")
            )
            
        except ImportError:
            PrintStyle.warning("FusioniX model not available")
            return None

    async def _generate_multitalk(
        self, prompt: str, characters: List[str], audio_sync: bool,
        duration: int, resolution: str, fps: int, advanced_settings: Dict[str, Any]
    ) -> Optional[str]:
        """Generate conversational video using MultiTalk"""
        
        try:
            from python.helpers.multitalk_generation import generate_conversation_video
            
            settings = advanced_settings or {}
            
            return await generate_conversation_video(
                prompt=prompt,
                characters=characters or ["Speaker 1", "Speaker 2"],
                audio_sync=audio_sync,
                duration=duration,
                resolution=resolution,
                fps=fps,
                sampling_steps=settings.get("sampling_steps", 12),
                guidance_scale=settings.get("guidance_scale", 7.5),
                seed=settings.get("seed")
            )
            
        except ImportError:
            PrintStyle.warning("MultiTalk model not available")
            return None

    async def _generate_wan2gp(
        self, prompt: str, video_type: str, image_to_animate: Optional[str],
        duration: int, resolution: str, fps: int, advanced_settings: Dict[str, Any]
    ) -> Optional[str]:
        """Generate video using Wan2GP platform"""
        
        try:
            from python.helpers.wan2gp_generation import generate_wan2gp_video
            
            settings = advanced_settings or {}
            
            return await generate_wan2gp_video(
                prompt=prompt,
                video_type=video_type,
                image_input=image_to_animate,
                duration=duration,
                resolution=resolution,
                fps=fps,
                low_vram=settings.get("low_vram", True),  # Wan2GP optimized for low VRAM
                sampling_steps=settings.get("sampling_steps", 15),
                guidance_scale=settings.get("guidance_scale", 7.5),
                seed=settings.get("seed")
            )
            
        except ImportError:
            PrintStyle.warning("Wan2GP platform not available")
            return None

    def _get_resolution_width(self, resolution: str) -> int:
        """Get width for resolution"""
        resolution_map = {
            "480p": 854,
            "720p": 1280,
            "1080p": 1920
        }
        return resolution_map.get(resolution, 1280)

    def _get_resolution_height(self, resolution: str) -> int:
        """Get height for resolution"""
        resolution_map = {
            "480p": 480,
            "720p": 720,
            "1080p": 1080
        }
        return resolution_map.get(resolution, 720)

# Register the tool
def register():
    return AdvancedVideoGenerator()