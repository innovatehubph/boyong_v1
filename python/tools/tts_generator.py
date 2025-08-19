"""
TTS Generator Tool for Agent Zero
Provides text-to-speech functionality for Pareng Boyong
"""

import asyncio
from python.helpers.simple_tts import synthesize_speech, check_tts_availability, TTS_BACKENDS

class TTSGenerator:
    """Text-to-Speech generator tool for Agent Zero"""
    
    def __init__(self, agent=None):
        self.agent = agent
        self.available_backends = check_tts_availability()
    
    async def generate_speech(self, text: str, voice: str = "default", speed: float = 1.0, language: str = "en"):
        """
        🔊 Generate text-to-speech audio from text
        
        This tool converts text to speech using multiple TTS backends with automatic fallback.
        Supports multiple voices and languages including Filipino pronunciation.
        
        Args:
            text (str): Text to convert to speech
            voice (str): Voice type - "default", "male", "female", "filipino"
            speed (float): Speech speed from 0.5 to 2.0 (1.0 = normal)
            language (str): Language code - "en" for English, "fil" for Filipino
            
        Returns:
            Dict with status, audio_data (base64), or html for browser TTS
            
        Example:
            result = await generate_speech("Hello, kumusta ka?", "filipino", 1.2)
            if result["status"] == "success":
                # Audio data available as base64 or HTML player
                audio = result["audio_data"]
        """
        
        try:
            # Adjust voice based on language
            if language == "fil" or language == "filipino":
                voice = "filipino"
            
            # Generate speech
            audio_result = await synthesize_speech(text, voice, speed)
            
            # Determine result type
            if len(audio_result) > 1000 and not audio_result.startswith('<'):
                # Base64 encoded audio
                return {
                    "status": "success",
                    "type": "audio",
                    "audio_data": audio_result,
                    "format": "wav_base64",
                    "metadata": {
                        "text": text,
                        "voice": voice,
                        "speed": speed,
                        "language": language,
                        "backend": "espeak-ng" if TTS_BACKENDS["espeak_ng"] else "pyttsx3"
                    }
                }
            else:
                # HTML browser TTS
                return {
                    "status": "success", 
                    "type": "html",
                    "html_player": audio_result,
                    "metadata": {
                        "text": text,
                        "voice": voice,
                        "speed": speed,
                        "language": language,
                        "backend": "browser"
                    }
                }
                
        except Exception as e:
            return {
                "status": "error",
                "message": str(e),
                "available_backends": self.available_backends
            }
    
    async def get_tts_status(self):
        """
        📊 Check TTS system status and available backends
        
        Returns information about available TTS engines and their capabilities.
        
        Returns:
            Dict with backend availability and system information
        """
        
        backends = check_tts_availability()
        
        return {
            "status": "operational" if any(backends.values()) else "degraded",
            "available_backends": backends,
            "supported_voices": ["default", "male", "female", "filipino"],
            "supported_languages": ["en", "filipino"],
            "speed_range": {"min": 0.5, "max": 2.0, "default": 1.0},
            "output_formats": ["wav_base64", "html_player"]
        }

# Create global instance for Agent Zero tool loading
tts_tool = TTSGenerator()

# Agent Zero tool functions
async def generate_speech(text: str, voice: str = "default", speed: float = 1.0, language: str = "en"):
    """Generate text-to-speech audio"""
    return await tts_tool.generate_speech(text, voice, speed, language)

async def get_tts_status():
    """Get TTS system status"""
    return await tts_tool.get_tts_status()

# Export for tool discovery
__all__ = ['TTSGenerator', 'generate_speech', 'get_tts_status']