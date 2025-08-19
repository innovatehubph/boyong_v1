"""
Audio Voiceover Tool for Pareng Boyong
Leverages existing STT/TTS systems and ElevenLabs for professional voice-overs
"""

import asyncio
import base64
import json
import tempfile
import os
from typing import Optional, Dict, Any, List
from python.helpers.tool import Tool, Response
from python.helpers.print_style import PrintStyle

class AudioVoiceover(Tool):
    async def execute(self, **kwargs) -> Response:
        """Execute the audio voice-over generation"""
        
        text = kwargs.get("text", "").strip()
        voice_type = kwargs.get("voice_type", "auto")
        language = kwargs.get("language", "auto")
        voice_settings = kwargs.get("voice_settings", {})
        output_format = kwargs.get("output_format", "audio")
        
        if not text:
            return Response(message="❌ Please provide text for voice-over generation.", break_loop=False)
        
        try:
            PrintStyle(font_color="cyan", padding=False).print(f"🎤 Creating voice-over: {text[:50]}...")
            
            # Generate the audio using the enhanced TTS system
            audio_base64 = await self._generate_voiceover(text, voice_type, language, voice_settings)
            
            if not audio_base64:
                return Response(
                    message="❌ Failed to generate voice-over. TTS services may not be available.",
                    break_loop=False
                )
            
            # Format the output based on requested format
            if output_format == "audio":
                # Return as audio tag for inline playback
                return Response(
                    message=f"🎤 **Voice-over generated successfully!**\n\n<audio format=\"wav\" title=\"Voice-over: {text[:30]}...\">{audio_base64}</audio>",
                    break_loop=False
                )
            elif output_format == "embedded":
                # Return as embedded audio player
                return Response(
                    message=f"""🎤 **Voice-over ready for playback:**

<div class="generated-media-container audio-container glass-card">
    <div class="audio-header">
        <span class="material-symbols-outlined">record_voice_over</span>
        <span class="audio-title">Voice-over: {text[:50]}...</span>
    </div>
    <audio class="generated-media-audio" controls preload="metadata" style="width: 100%;">
        <source src="data:audio/wav;base64,{audio_base64}" type="audio/wav">
        <p>Your browser doesn't support audio playback.</p>
    </audio>
    <div class="media-controls">
        <button class="btn-secondary btn-sm" onclick="downloadMedia('data:audio/wav;base64,{audio_base64}', 'voiceover.wav')">
            <span class="material-symbols-outlined">download</span> Download
        </button>
    </div>
</div>""",
                    break_loop=False
                )
            else:  # download format
                return Response(
                    message=f"🎤 **Voice-over generated!** \n\n[Download Voice-over](data:audio/wav;base64,{audio_base64})\n\n*Text: {text[:100]}...*",
                    break_loop=False
                )
                
        except Exception as e:
            PrintStyle.error(f"Voice-over generation failed: {e}")
            return Response(
                message=f"❌ Voice-over generation failed: {str(e)}",
                break_loop=False
            )
    
    async def _generate_voiceover(
        self, 
        text: str, 
        voice_type: str, 
        language: str, 
        voice_settings: Dict[str, Any]
    ) -> Optional[str]:
        """Generate voice-over using the specified TTS system"""
        
        # Detect language if auto
        if language == "auto":
            language = self._detect_language(text)
        
        # Determine TTS system if auto
        if voice_type == "auto":
            voice_type = self._choose_optimal_tts(language)
        
        # Generate audio using the selected TTS system
        if voice_type == "elevenlabs":
            return await self._generate_with_elevenlabs(text, voice_settings)
        elif voice_type == "toucan":
            return await self._generate_with_toucan(text)
        elif voice_type == "browser":
            return await self._generate_with_browser_fallback(text)
        else:
            # Fallback chain: try best available options
            return await self._generate_with_fallback_chain(text, language, voice_settings)
    
    async def _generate_with_elevenlabs(self, text: str, voice_settings: Dict[str, Any]) -> Optional[str]:
        """Generate voice-over using ElevenLabs"""
        try:
            from python.helpers import elevenlabs_tts
            
            # Override settings if provided
            if voice_settings:
                original_settings = elevenlabs_tts.VOICE_SETTINGS.copy()
                elevenlabs_tts.VOICE_SETTINGS.update(voice_settings)
            
            audio = await elevenlabs_tts.synthesize_sentences([text])
            
            # Restore original settings
            if voice_settings:
                elevenlabs_tts.VOICE_SETTINGS = original_settings
                
            return audio
            
        except Exception as e:
            PrintStyle.warning(f"ElevenLabs TTS failed: {e}")
            return None
    
    async def _generate_with_toucan(self, text: str) -> Optional[str]:
        """Generate voice-over using ToucanTTS (Filipino optimized)"""
        try:
            from python.helpers import toucan_tts
            audio = await toucan_tts.synthesize_sentences([text])
            return audio
        except Exception as e:
            PrintStyle.warning(f"ToucanTTS failed: {e}")
            return None
    
    async def _generate_with_browser_fallback(self, text: str) -> Optional[str]:
        """Generate voice-over using browser TTS (fallback)"""
        try:
            # This would typically be handled by the frontend
            # For now, return None to indicate browser TTS should be used
            PrintStyle.warning("Browser TTS should be handled by frontend")
            return None
        except Exception as e:
            PrintStyle.warning(f"Browser TTS setup failed: {e}")
            return None
    
    async def _generate_with_fallback_chain(
        self, 
        text: str, 
        language: str, 
        voice_settings: Dict[str, Any]
    ) -> Optional[str]:
        """Try multiple TTS systems in order of preference"""
        
        # For Filipino text, prioritize ToucanTTS
        if language == "filipino":
            audio = await self._generate_with_toucan(text)
            if audio:
                return audio
        
        # Try ElevenLabs for high quality
        audio = await self._generate_with_elevenlabs(text, voice_settings)
        if audio:
            return audio
        
        # Try ToucanTTS as fallback for Filipino
        if language == "filipino":
            audio = await self._generate_with_toucan(text)
            if audio:
                return audio
        
        # Browser TTS as final fallback (handled by frontend)
        PrintStyle.warning("All TTS services failed, falling back to browser TTS")
        return None
    
    def _detect_language(self, text: str) -> str:
        """Detect if text is Filipino or English"""
        filipino_indicators = [
            # Common Filipino words
            'ang', 'mga', 'sa', 'ng', 'na', 'at', 'ay', 'para', 'kung', 'ako', 'ka', 'siya',
            'kami', 'kayo', 'sila', 'ito', 'iyan', 'iyon', 'dito', 'dyan', 'doon',
            'kumusta', 'salamat', 'walang', 'anong', 'bakit', 'paano', 'saan', 'kailan',
            'maganda', 'ganda', 'pangit', 'mabait', 'masama', 'malaki', 'maliit',
            'pamilya', 'bahay', 'eskwela', 'trabaho', 'pera', 'pagkain', 'tubig',
            'mahal', 'libre', 'oo', 'hindi', 'siguro', 'baka', 'kasi', 'pero',
            'tapos', 'muna', 'lang', 'din', 'rin', 'naman', 'pala', 'kaya', 'daw',
            # Filipino phrases
            'kumusta ka', 'salamat po', 'walang anuman', 'paalam na', 'ingat ka'
        ]
        
        text_lower = text.lower()
        filipino_count = sum(1 for word in filipino_indicators if word in text_lower)
        
        # If we find Filipino indicators, classify as Filipino
        if filipino_count >= 2 or any(phrase in text_lower for phrase in filipino_indicators[-5:]):
            return "filipino"
        
        return "english"
    
    def _choose_optimal_tts(self, language: str) -> str:
        """Choose the best TTS system based on language and availability"""
        
        if language == "filipino":
            # For Filipino, prefer ToucanTTS, then ElevenLabs
            return "toucan"
        else:
            # For English, prefer ElevenLabs for quality
            return "elevenlabs"

# Register the tool
def register():
    return AudioVoiceover()