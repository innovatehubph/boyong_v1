# api/speech_to_text.py - Speech-to-Text API endpoint for Pareng Boyong

from python.helpers.api import ApiHandler, Request, Response
from python.helpers import settings
from python.helpers.print_style import PrintStyle
import base64

class SpeechToText(ApiHandler):
    async def process(self, input: dict, request: Request) -> dict | Response:
        """
        Process speech-to-text conversion request
        
        Expected input:
        {
            "audio": "base64_encoded_audio_data",  # Required
            "model": "scribe_v1",                  # Optional, from settings if not provided
            "language": "auto",                    # Optional
            "diarize": false,                      # Optional
            "timestamps": "word"                   # Optional: "none", "word", "character"
        }
        """
        try:
            # Validate required input
            audio_base64 = input.get("audio", "")
            if not audio_base64:
                return {
                    "success": False,
                    "error": "Missing required 'audio' field with base64 encoded audio data"
                }
            
            # Get current settings
            current_settings = settings.get_settings()
            
            # Check if ElevenLabs STT is enabled
            if not current_settings.get("stt_elevenlabs_enable", False):
                return {
                    "success": False,
                    "error": "ElevenLabs Speech-to-Text is disabled in settings"
                }
            
            # Extract parameters with defaults from settings
            model = input.get("model", current_settings.get("stt_elevenlabs_model", "scribe_v1"))
            language_code = input.get("language", None)  # Auto-detect if None
            diarize = input.get("diarize", current_settings.get("stt_elevenlabs_diarization", False))
            timestamps = input.get("timestamps", current_settings.get("stt_elevenlabs_timestamps", "word"))
            
            PrintStyle.info(f"STT request: model={model}, diarize={diarize}, timestamps={timestamps}")
            
            # Import and use ElevenLabs STT
            from python.helpers import elevenlabs_stt
            
            # Convert base64 to bytes
            try:
                audio_bytes = base64.b64decode(audio_base64)
            except Exception as e:
                return {
                    "success": False,
                    "error": f"Invalid base64 audio data: {e}"
                }
            
            # Perform transcription
            result = await elevenlabs_stt.transcribe_audio(
                audio_bytes, model, language_code, diarize, timestamps
            )
            
            if result["status"] == "success":
                return {
                    "success": True,
                    "transcription": result["text"],
                    "language": result.get("language_code", "unknown"),
                    "confidence": result.get("language_probability", 0.0),
                    "model_used": model,
                    "words": result.get("words", []),
                    "diarization": result.get("diarization_enabled", False),
                    "metadata": {
                        "audio_size": len(audio_bytes),
                        "settings_used": {
                            "model": model,
                            "diarize": diarize,
                            "timestamps": timestamps
                        }
                    }
                }
            elif result["status"] == "disabled":
                return {
                    "success": False,
                    "error": "ElevenLabs STT is not configured. Please check API key settings."
                }
            else:
                return {
                    "success": False,
                    "error": result.get("message", "STT processing failed"),
                    "details": result
                }
                
        except Exception as e:
            PrintStyle.error(f"Speech-to-Text API error: {e}")
            return {
                "success": False,
                "error": f"Internal STT error: {e}"
            }