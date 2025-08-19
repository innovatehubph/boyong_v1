"""
Music Generation Tool for Pareng Boyong
Uses AudioCraft/MusicGen for music and sound generation
"""

import asyncio
from typing import Optional, Dict, Any
from python.helpers.tool import Tool, Response
from python.helpers.print_style import PrintStyle

class MusicGenerator(Tool):
    async def execute(self, **kwargs) -> Response:
        """Execute music generation"""
        
        prompt = kwargs.get("prompt", "").strip()
        audio_type = kwargs.get("type", "music")
        duration = kwargs.get("duration", 15)
        genre = kwargs.get("genre", "any")
        mood = kwargs.get("mood", "any")
        tempo = kwargs.get("tempo", "medium")
        instruments = kwargs.get("instruments", "")
        model_size = kwargs.get("model_size", "medium")
        
        if not prompt:
            return Response(message="❌ Please provide a description for the music to generate.", break_loop=False)
        
        try:
            PrintStyle(font_color="green", padding=False).print(f"🎵 Generating {audio_type}: {prompt[:50]}...")
            
            # Build enhanced prompt
            enhanced_prompt = self._build_enhanced_prompt(
                prompt, audio_type, genre, mood, tempo, instruments
            )
            
            # Generate the audio
            if audio_type == "sound_effect":
                audio_base64 = await self._generate_sound_effect(enhanced_prompt, duration)
                title = f"Sound Effect: {prompt[:30]}"
            elif audio_type == "ambient":
                audio_base64 = await self._generate_ambient(enhanced_prompt, duration)
                title = f"Ambient: {prompt[:30]}"
            else:
                audio_base64 = await self._generate_music(enhanced_prompt, duration, model_size)
                title = f"Music: {prompt[:30]}"
            
            if not audio_base64:
                return Response(
                    message="❌ Failed to generate audio. Music generation services may not be available.\n\n**Tip:** Make sure AudioCraft/MusicGen server is running.",
                    break_loop=False
                )
            
            # Build response with metadata
            metadata_lines = []
            if genre != "any":
                metadata_lines.append(f"**Genre:** {genre.replace('_', ' ').title()}")
            if mood != "any":
                metadata_lines.append(f"**Mood:** {mood.title()}")
            if tempo != "medium":
                metadata_lines.append(f"**Tempo:** {tempo.title()}")
            if instruments:
                metadata_lines.append(f"**Instruments:** {instruments}")
            
            metadata = "\n".join(metadata_lines) if metadata_lines else ""
            
            return Response(
                message=f"""🎵 **{audio_type.replace('_', ' ').title()} Generated Successfully!**

**Prompt:** {prompt}
**Duration:** {duration} seconds
**Type:** {audio_type.replace('_', ' ').title()}
{metadata}

<audio format="wav" title="{title}">{audio_base64}</audio>""",
                break_loop=False
            )
                
        except Exception as e:
            PrintStyle.error(f"Music generation failed: {e}")
            return Response(
                message=f"❌ Music generation failed: {str(e)}\n\n**Possible solutions:**\n- Ensure AudioCraft/MusicGen server is running\n- Try a shorter duration\n- Simplify the prompt",
                break_loop=False
            )
    
    async def _generate_music(self, prompt: str, duration: int, model_size: str) -> Optional[str]:
        """Generate music using MusicGen"""
        
        try:
            # Import the audio generation helper
            from python.helpers.audio_generation import generate_music
            
            # Map model size to actual model names
            model_map = {
                "small": "facebook/musicgen-small",
                "medium": "facebook/musicgen-medium", 
                "large": "facebook/musicgen-large"
            }
            
            return await generate_music(
                prompt=prompt,
                duration=duration,
                model=model_map.get(model_size, "facebook/musicgen-medium")
            )
            
        except ImportError:
            PrintStyle.warning("Music generation module not available")
            return None
        except Exception as e:
            PrintStyle.error(f"Music generation error: {e}")
            return None
    
    async def _generate_sound_effect(self, prompt: str, duration: int) -> Optional[str]:
        """Generate sound effects using AudioGen"""
        
        try:
            # Import the audio generation helper
            from python.helpers.audio_generation import generate_sound_effect
            
            return await generate_sound_effect(
                prompt=prompt,
                duration=duration
            )
            
        except ImportError:
            PrintStyle.warning("Sound effect generation module not available")
            return None
        except Exception as e:
            PrintStyle.error(f"Sound effect generation error: {e}")
            return None
    
    async def _generate_ambient(self, prompt: str, duration: int) -> Optional[str]:
        """Generate ambient sounds"""
        
        try:
            # Import the audio generation helper
            from python.helpers.audio_generation import audio_generator
            
            return await audio_generator.generate_ambient_sound(
                description=prompt,
                duration=duration,
                fade_in=True,
                fade_out=True
            )
            
        except ImportError:
            PrintStyle.warning("Ambient sound generation module not available")
            return None
        except Exception as e:
            PrintStyle.error(f"Ambient sound generation error: {e}")
            return None
    
    def _build_enhanced_prompt(
        self, 
        prompt: str, 
        audio_type: str, 
        genre: str, 
        mood: str, 
        tempo: str, 
        instruments: str
    ) -> str:
        """Build enhanced prompt with additional specifications"""
        
        enhancements = []
        
        # Add type-specific enhancements
        if audio_type == "sound_effect":
            enhancements.append("realistic sound effect")
        elif audio_type == "ambient":
            enhancements.append("ambient background sound, looping")
        elif audio_type == "jingle":
            enhancements.append("short musical jingle, catchy")
        elif audio_type == "loop":
            enhancements.append("seamless loop, repetitive")
        
        # Add genre if specified
        if genre != "any":
            enhancements.append(f"{genre.replace('_', ' ')} style")
        
        # Add mood if specified
        if mood != "any":
            enhancements.append(f"{mood} mood")
        
        # Add tempo characteristics
        tempo_descriptions = {
            "slow": "slow tempo, relaxed pace",
            "medium": "moderate tempo",
            "fast": "fast tempo, energetic pace",
            "variable": "variable tempo, dynamic pacing"
        }
        if tempo in tempo_descriptions:
            enhancements.append(tempo_descriptions[tempo])
        
        # Add instruments if specified
        if instruments:
            enhancements.append(f"featuring {instruments}")
        
        # Combine with original prompt
        if enhancements:
            return f"{prompt}, {', '.join(enhancements)}"
        return prompt

# Register the tool
def register():
    return MusicGenerator()