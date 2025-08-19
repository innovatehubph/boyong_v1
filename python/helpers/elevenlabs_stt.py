# elevenlabs_stt.py - ElevenLabs Speech-to-Text integration for Pareng Boyong

import base64
import asyncio
import aiohttp
import json
from python.helpers.print_style import PrintStyle

# Import configuration from elevenlabs_tts
try:
    from python.helpers.elevenlabs_tts import ELEVENLABS_API_KEY, ENABLE_ELEVENLABS, ELEVENLABS_API_URL
except ImportError:
    # Fallback configuration
    import os
    ELEVENLABS_API_KEY = os.environ.get("ELEVENLABS_API_KEY", "")
    ENABLE_ELEVENLABS = bool(ELEVENLABS_API_KEY and len(ELEVENLABS_API_KEY) > 10)
    ELEVENLABS_API_URL = "https://api.elevenlabs.io/v1"

# Global session state
_stt_session = None
is_initializing_stt = False

async def preload_stt():
    """Preload ElevenLabs STT session"""
    try:
        return await _preload_stt()
    except Exception as e:
        PrintStyle.error(f"ElevenLabs STT not available: {e}")
        return False

async def _preload_stt():
    """Initialize aiohttp session for ElevenLabs STT API"""
    global _stt_session, is_initializing_stt
    
    while is_initializing_stt:
        await asyncio.sleep(0.1)
    
    try:
        is_initializing_stt = True
        if not _stt_session and ENABLE_ELEVENLABS:
            PrintStyle.standard("Initializing ElevenLabs STT...")
            
            # Validate API key format
            if not ELEVENLABS_API_KEY.startswith("sk_"):
                raise Exception("Invalid ElevenLabs API key format")
            
            timeout = aiohttp.ClientTimeout(total=60)  # Longer timeout for STT
            _stt_session = aiohttp.ClientSession(
                timeout=timeout,
                headers={
                    "xi-api-key": ELEVENLABS_API_KEY,
                }
            )
            
            PrintStyle.standard("✅ ElevenLabs STT ready")
                
        elif not ENABLE_ELEVENLABS:
            PrintStyle.standard("ElevenLabs STT disabled - no valid API key configured")
    finally:
        is_initializing_stt = False

async def transcribe_audio(audio_data: bytes, model: str = "scribe_v1", language_code: str = None, 
                          diarize: bool = False, timestamps: str = "word") -> dict:
    """
    Transcribe audio using ElevenLabs STT API
    
    Args:
        audio_data: Raw audio data (supported formats: mp3, wav, flac, m4a, webm, etc.)
        model: STT model to use ("scribe_v1" or "scribe_v1_experimental")
        language_code: ISO language code (auto-detect if None)
        diarize: Enable speaker diarization
        timestamps: Timestamp granularity ("none", "word", "character")
        
    Returns:
        dict: Transcription result with text, language, and metadata
    """
    if not ENABLE_ELEVENLABS:
        return {
            "status": "disabled",
            "text": "",
            "message": "ElevenLabs STT disabled - no API key configured"
        }
        
    try:
        await _preload_stt()
        
        if not _stt_session:
            raise Exception("ElevenLabs STT not initialized")
        
        PrintStyle.info(f"ElevenLabs STT transcribing {len(audio_data)} bytes with model {model}...")
        
        url = f"{ELEVENLABS_API_URL}/speech-to-text"
        
        # Prepare multipart form data according to official API spec
        data = aiohttp.FormData()
        data.add_field('file', audio_data, filename='audio.wav', content_type='audio/wav')
        data.add_field('model_id', model)
        
        # Optional parameters based on API spec
        if language_code:
            data.add_field('language_code', language_code)
        
        data.add_field('diarize', str(diarize).lower())
        data.add_field('timestamps_granularity', timestamps)
        data.add_field('tag_audio_events', 'true')
        
        # Set Content-Type header for multipart data
        headers = {'xi-api-key': ELEVENLABS_API_KEY}
        
        async with _stt_session.post(url, data=data, headers=headers) as response:
            if response.status == 200:
                result = await response.json()
                
                transcription_text = result.get("text", "")
                language = result.get("language_code", "unknown")
                language_prob = result.get("language_probability", 0.0)
                words = result.get("words", [])
                
                PrintStyle.success(f"ElevenLabs STT completed (language: {language}, confidence: {language_prob:.2f})")
                
                return {
                    "status": "success",
                    "text": transcription_text,
                    "language_code": language,
                    "language_probability": language_prob,
                    "model": model,
                    "words": words,
                    "diarization_enabled": diarize
                }
            else:
                error_text = await response.text()
                error_msg = f"ElevenLabs STT API error {response.status}: {error_text}"
                PrintStyle.error(error_msg)
                
                return {
                    "status": "error",
                    "text": "",
                    "message": error_msg
                }
                
    except asyncio.TimeoutError:
        error_msg = "ElevenLabs STT timeout"
        PrintStyle.error(error_msg)
        return {
            "status": "error", 
            "text": "",
            "message": error_msg
        }
    except Exception as e:
        error_msg = f"ElevenLabs STT error: {e}"
        PrintStyle.error(error_msg)
        return {
            "status": "error",
            "text": "",
            "message": error_msg
        }

async def transcribe_base64_audio(base64_audio: str, model: str = "scribe_v1") -> dict:
    """
    Transcribe base64-encoded audio using ElevenLabs STT
    
    Args:
        base64_audio: Base64 encoded audio data
        model: STT model to use
        
    Returns:
        dict: Transcription result
    """
    try:
        # Decode base64 audio
        audio_data = base64.b64decode(base64_audio)
        return await transcribe_audio(audio_data, model)
        
    except Exception as e:
        error_msg = f"Error decoding base64 audio: {e}"
        PrintStyle.error(error_msg)
        return {
            "status": "error",
            "text": "",
            "message": error_msg
        }

async def test_stt_connection() -> dict:
    """Test ElevenLabs STT connection and return status"""
    if not ENABLE_ELEVENLABS:
        return {
            "status": "disabled",
            "message": "ElevenLabs STT disabled. Configure API key to enable.",
            "models_available": []
        }
    
    try:
        await _preload_stt()
        
        # Create a small test audio (silence)
        import wave
        import io
        
        # Create 1 second of silence at 16kHz
        test_audio_data = io.BytesIO()
        with wave.open(test_audio_data, 'wb') as wav_file:
            wav_file.setnchannels(1)  # Mono
            wav_file.setsampwidth(2)  # 16-bit
            wav_file.setframerate(16000)  # 16kHz
            wav_file.writeframes(b'\x00' * 32000)  # 1 second of silence
        
        test_audio_bytes = test_audio_data.getvalue()
        
        # Test transcription
        result = await transcribe_audio(test_audio_bytes, "scribe_v1")
        
        if result["status"] == "success":
            return {
                "status": "success",
                "message": "ElevenLabs STT is working",
                "models_available": [
                    "eleven_multilingual_v2",
                    "eleven_english_sts_v2"
                ],
                "test_result": result
            }
        else:
            return {
                "status": "error",
                "message": f"STT test failed: {result.get('message', 'Unknown error')}",
                "models_available": []
            }
            
    except Exception as e:
        return {
            "status": "error",
            "message": f"STT connection test failed: {e}",
            "models_available": []
        }

async def get_available_models() -> list:
    """Get list of available STT models"""
    return [
        {
            "id": "scribe_v1",
            "name": "Scribe V1",
            "description": "Production-ready speech-to-text model with high accuracy",
            "features": ["multilingual", "speaker_diarization", "timestamps", "audio_events"]
        },
        {
            "id": "scribe_v1_experimental", 
            "name": "Scribe V1 Experimental",
            "description": "Experimental version with latest features and improvements",
            "features": ["multilingual", "speaker_diarization", "timestamps", "audio_events", "experimental"]
        }
    ]

async def cleanup_stt():
    """Cleanup STT resources"""
    global _stt_session
    if _stt_session:
        try:
            await _stt_session.close()
        except Exception:
            pass
        finally:
            _stt_session = None

# Compatibility function for unified interface
async def speech_to_text(audio_data: bytes, settings: dict = None) -> dict:
    """
    Unified speech-to-text interface using settings
    
    Args:
        audio_data: Audio bytes to transcribe
        settings: Settings dict containing STT preferences
        
    Returns:
        dict: Transcription result
    """
    if not settings:
        settings = {}
    
    model = settings.get("stt_elevenlabs_model", "scribe_v1")
    
    return await transcribe_audio(audio_data, model)