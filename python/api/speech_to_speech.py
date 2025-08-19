# api/speech_to_speech.py - Speech-to-Speech API endpoint for Pareng Boyong

from python.helpers.api import ApiHandler, Request, Response
from python.helpers import settings
from python.helpers.print_style import PrintStyle
import base64

class SpeechToSpeech(ApiHandler):
    async def process(self, input: dict, request: Request) -> dict | Response:
        """
        Process speech-to-speech voice conversion request
        
        Expected input:
        {
            "audio": "base64_encoded_source_audio",     # Required
            "target_voice_id": "voice_id",             # Required
            "model": "eleven_english_sts_v2",          # Optional
            "remove_noise": false,                     # Optional
            "streaming": true,                         # Optional
            "voice_settings": {                        # Optional
                "stability": 0.75,
                "similarity_boost": 0.85,
                "style": 0.20,
                "use_speaker_boost": true
            }
        }
        """
        try:
            # Validate required input
            audio_base64 = input.get("audio", "")
            target_voice_id = input.get("target_voice_id", "")
            
            if not audio_base64:
                return {
                    "success": False,
                    "error": "Missing required 'audio' field with base64 encoded audio data"
                }
            
            if not target_voice_id:
                # Get current settings for default voice
                current_settings = settings.get_settings()
                target_voice_id = current_settings.get("tts_speech_to_speech_voice_id", "21m00Tcm4TlvDq8ikWAM")
                
                if not target_voice_id:
                    return {
                        "success": False,
                        "error": "Missing required 'target_voice_id' field"
                    }
            
            # Get current settings
            current_settings = settings.get_settings()
            
            # Check if Speech-to-Speech is enabled
            if not current_settings.get("tts_speech_to_speech_enable", False):
                return {
                    "success": False,
                    "error": "ElevenLabs Speech-to-Speech is disabled in settings"
                }
            
            # Extract parameters with defaults from settings
            model = input.get("model", current_settings.get("tts_speech_to_speech_model", "eleven_english_sts_v2"))
            remove_noise = input.get("remove_noise", current_settings.get("tts_speech_to_speech_remove_noise", False))
            streaming = input.get("streaming", current_settings.get("tts_speech_to_speech_streaming", True))
            output_format = input.get("output_format", current_settings.get("tts_speech_to_speech_output_format", "mp3_44100_128"))
            
            # Voice settings with defaults from settings
            voice_settings = input.get("voice_settings", {})
            if not voice_settings:
                voice_settings = {
                    "stability": current_settings.get("tts_speech_to_speech_stability", 0.75),
                    "similarity_boost": current_settings.get("tts_elevenlabs_similarity", 0.85),
                    "style": current_settings.get("tts_elevenlabs_style", 0.20),
                    "use_speaker_boost": current_settings.get("tts_elevenlabs_speaker_boost", True)
                }
            
            PrintStyle.info(f"Speech-to-Speech request: target={target_voice_id}, model={model}, streaming={streaming}")
            
            # Import and use ElevenLabs Speech-to-Speech
            from python.helpers import elevenlabs_speech_to_speech
            
            # Convert base64 to bytes
            try:
                audio_bytes = base64.b64decode(audio_base64)
            except Exception as e:
                return {
                    "success": False,
                    "error": f"Invalid base64 audio data: {e}"
                }
            
            # Perform voice conversion
            if streaming:
                result = await elevenlabs_speech_to_speech.voice_conversion_streaming(
                    audio_bytes, target_voice_id, model, voice_settings, remove_noise, output_format
                )
            else:
                result = await elevenlabs_speech_to_speech.voice_conversion(
                    audio_bytes, target_voice_id, model, voice_settings, remove_noise, output_format
                )
            
            if result["status"] == "success":
                return {
                    "success": True,
                    "audio": result["audio"],
                    "target_voice_id": result["target_voice_id"],
                    "model_used": result["model"],
                    "output_format": result["output_format"],
                    "streaming": result.get("streaming", False),
                    "metadata": {
                        "source_audio_size": len(audio_bytes),
                        "output_audio_size": result.get("audio_size", 0),
                        "voice_settings": result.get("voice_settings", voice_settings),
                        "settings_used": {
                            "model": model,
                            "remove_noise": remove_noise,
                            "streaming": streaming,
                            "output_format": output_format
                        }
                    }
                }
            elif result["status"] == "disabled":
                return {
                    "success": False,
                    "error": "ElevenLabs Speech-to-Speech is not configured. Please check API key settings."
                }
            else:
                return {
                    "success": False,
                    "error": result.get("message", "Speech-to-Speech processing failed"),
                    "details": result
                }
                
        except Exception as e:
            PrintStyle.error(f"Speech-to-Speech API error: {e}")
            return {
                "success": False,
                "error": f"Internal Speech-to-Speech error: {e}"
            }