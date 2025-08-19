# elevenlabs_speech_to_speech.py - ElevenLabs Speech-to-Speech integration for Pareng Boyong

import base64
import asyncio
import aiohttp
import json
from python.helpers.print_style import PrintStyle

# Import configuration from elevenlabs_tts
try:
    from python.helpers.elevenlabs_tts import ELEVENLABS_API_KEY, ENABLE_ELEVENLABS, ELEVENLABS_API_URL, VOICE_SETTINGS
except ImportError:
    # Fallback configuration
    import os
    ELEVENLABS_API_KEY = os.environ.get("ELEVENLABS_API_KEY", "")
    ENABLE_ELEVENLABS = bool(ELEVENLABS_API_KEY and len(ELEVENLABS_API_KEY) > 10)
    ELEVENLABS_API_URL = "https://api.elevenlabs.io/v1"
    VOICE_SETTINGS = {
        "stability": 0.75,
        "similarity_boost": 0.85,
        "style": 0.20,
        "use_speaker_boost": True
    }

# Global session state for Speech-to-Speech
_sts_session = None
is_initializing_sts = False

async def preload_sts():
    """Preload ElevenLabs Speech-to-Speech session"""
    try:
        return await _preload_sts()
    except Exception as e:
        PrintStyle.error(f"ElevenLabs Speech-to-Speech not available: {e}")
        return False

async def _preload_sts():
    """Initialize aiohttp session for ElevenLabs Speech-to-Speech API"""
    global _sts_session, is_initializing_sts
    
    while is_initializing_sts:
        await asyncio.sleep(0.1)
    
    try:
        is_initializing_sts = True
        if not _sts_session and ENABLE_ELEVENLABS:
            PrintStyle.standard("Initializing ElevenLabs Speech-to-Speech...")
            
            # Validate API key format
            if not ELEVENLABS_API_KEY.startswith("sk_"):
                raise Exception("Invalid ElevenLabs API key format")
            
            timeout = aiohttp.ClientTimeout(total=90)  # Longer timeout for speech conversion
            _sts_session = aiohttp.ClientSession(
                timeout=timeout,
                headers={
                    "xi-api-key": ELEVENLABS_API_KEY,
                }
            )
            
            PrintStyle.standard("✅ ElevenLabs Speech-to-Speech ready")
                
        elif not ENABLE_ELEVENLABS:
            PrintStyle.standard("ElevenLabs Speech-to-Speech disabled - no valid API key configured")
    finally:
        is_initializing_sts = False

async def voice_conversion(source_audio: bytes, target_voice_id: str, model: str = "eleven_english_sts_v2",
                          voice_settings: dict = None, remove_background_noise: bool = False,
                          output_format: str = "mp3_44100_128") -> dict:
    """
    Convert source audio to target voice using ElevenLabs Speech-to-Speech
    
    Args:
        source_audio: Input audio data (various formats supported)
        target_voice_id: ID of the target voice
        model: Speech-to-Speech model ("eleven_english_sts_v2" or "eleven_multilingual_sts_v2")
        voice_settings: Voice configuration settings
        remove_background_noise: Whether to remove background noise
        output_format: Output audio format
        
    Returns:
        dict: Conversion result with audio data and metadata
    """
    if not ENABLE_ELEVENLABS:
        return {
            "status": "disabled",
            "audio": "",
            "message": "ElevenLabs Speech-to-Speech disabled - no API key configured"
        }
    
    try:
        await _preload_sts()
        
        if not _sts_session:
            raise Exception("ElevenLabs Speech-to-Speech not initialized")
        
        PrintStyle.info(f"ElevenLabs Speech-to-Speech converting {len(source_audio)} bytes to voice {target_voice_id}...")
        
        url = f"{ELEVENLABS_API_URL}/speech-to-speech/{target_voice_id}"
        
        # Use default voice settings if none provided
        if not voice_settings:
            voice_settings = VOICE_SETTINGS.copy()
        
        # Prepare multipart form data according to official API spec
        data = aiohttp.FormData()
        data.add_field('audio', source_audio, filename='source_audio.wav', content_type='audio/wav')
        data.add_field('model_id', model)
        data.add_field('voice_settings', json.dumps(voice_settings))
        data.add_field('remove_background_noise', str(remove_background_noise).lower())
        
        # Add query parameters
        params = {
            'output_format': output_format
        }
        
        async with _sts_session.post(url, data=data, params=params) as response:
            if response.status == 200:
                # Get the converted audio data
                audio_data = await response.read()
                
                PrintStyle.success(f"ElevenLabs Speech-to-Speech completed ({len(audio_data)} bytes generated)")
                
                return {
                    "status": "success",
                    "audio": base64.b64encode(audio_data).decode('utf-8'),
                    "target_voice_id": target_voice_id,
                    "model": model,
                    "output_format": output_format,
                    "audio_size": len(audio_data),
                    "voice_settings": voice_settings
                }
            else:
                error_text = await response.text()
                error_msg = f"ElevenLabs Speech-to-Speech API error {response.status}: {error_text}"
                PrintStyle.error(error_msg)
                
                return {
                    "status": "error",
                    "audio": "",
                    "message": error_msg
                }
                
    except asyncio.TimeoutError:
        error_msg = "ElevenLabs Speech-to-Speech timeout"
        PrintStyle.error(error_msg)
        return {
            "status": "error",
            "audio": "",
            "message": error_msg
        }
    except Exception as e:
        error_msg = f"ElevenLabs Speech-to-Speech error: {e}"
        PrintStyle.error(error_msg)
        return {
            "status": "error",
            "audio": "",
            "message": error_msg
        }

async def voice_conversion_streaming(source_audio: bytes, target_voice_id: str, model: str = "eleven_english_sts_v2",
                                   voice_settings: dict = None, remove_background_noise: bool = False,
                                   output_format: str = "mp3_44100_128") -> dict:
    """
    Convert source audio to target voice using ElevenLabs Speech-to-Speech streaming
    
    Args:
        source_audio: Input audio data
        target_voice_id: ID of the target voice
        model: Speech-to-Speech model
        voice_settings: Voice configuration settings
        remove_background_noise: Whether to remove background noise
        output_format: Output audio format
        
    Returns:
        dict: Streaming conversion result
    """
    if not ENABLE_ELEVENLABS:
        return {
            "status": "disabled",
            "audio": "",
            "message": "ElevenLabs Speech-to-Speech disabled - no API key configured"
        }
    
    try:
        await _preload_sts()
        
        if not _sts_session:
            raise Exception("ElevenLabs Speech-to-Speech not initialized")
        
        PrintStyle.info(f"ElevenLabs Speech-to-Speech streaming conversion to voice {target_voice_id}...")
        
        url = f"{ELEVENLABS_API_URL}/speech-to-speech/{target_voice_id}/stream"
        
        # Use default voice settings if none provided
        if not voice_settings:
            voice_settings = VOICE_SETTINGS.copy()
        
        # Prepare multipart form data
        data = aiohttp.FormData()
        data.add_field('audio', source_audio, filename='source_audio.wav', content_type='audio/wav')
        data.add_field('model_id', model)
        
        # Add query parameters according to API spec
        params = {
            'output_format': output_format,
            'enable_logging': 'true',
            'remove_background_noise': str(remove_background_noise).lower()
        }
        
        async with _sts_session.post(url, data=data, params=params) as response:
            if response.status == 200:
                # Collect all streaming chunks
                audio_chunks = []
                async for chunk in response.content.iter_chunked(8192):
                    if chunk:
                        audio_chunks.append(chunk)
                
                audio_data = b''.join(audio_chunks)
                
                PrintStyle.success(f"ElevenLabs Speech-to-Speech streaming completed ({len(audio_data)} bytes)")
                
                return {
                    "status": "success",
                    "audio": base64.b64encode(audio_data).decode('utf-8'),
                    "target_voice_id": target_voice_id,
                    "model": model,
                    "output_format": output_format,
                    "audio_size": len(audio_data),
                    "streaming": True
                }
            else:
                error_text = await response.text()
                error_msg = f"ElevenLabs Speech-to-Speech streaming API error {response.status}: {error_text}"
                PrintStyle.error(error_msg)
                
                return {
                    "status": "error",
                    "audio": "",
                    "message": error_msg
                }
                
    except asyncio.TimeoutError:
        error_msg = "ElevenLabs Speech-to-Speech streaming timeout"
        PrintStyle.error(error_msg)
        return {
            "status": "error",
            "audio": "",
            "message": error_msg
        }
    except Exception as e:
        error_msg = f"ElevenLabs Speech-to-Speech streaming error: {e}"
        PrintStyle.error(error_msg)
        return {
            "status": "error",
            "audio": "",
            "message": error_msg
        }

async def convert_base64_audio(base64_audio: str, target_voice_id: str, settings: dict = None) -> dict:
    """
    Convert base64-encoded audio using Speech-to-Speech
    
    Args:
        base64_audio: Base64 encoded source audio
        target_voice_id: Target voice ID for conversion
        settings: Settings dict with conversion preferences
        
    Returns:
        dict: Conversion result
    """
    try:
        # Decode base64 audio
        source_audio = base64.b64decode(base64_audio)
        
        if not settings:
            settings = {}
        
        # Extract settings
        model = settings.get("tts_speech_to_speech_model", "eleven_english_sts_v2")
        stability = settings.get("tts_speech_to_speech_stability", 0.75)
        voice_settings = {
            "stability": stability,
            "similarity_boost": settings.get("tts_elevenlabs_similarity", 0.85),
            "style": settings.get("tts_elevenlabs_style", 0.20),
            "use_speaker_boost": settings.get("tts_elevenlabs_speaker_boost", True)
        }
        remove_noise = settings.get("tts_speech_to_speech_remove_noise", False)
        output_format = settings.get("tts_speech_to_speech_output_format", "mp3_44100_128")
        
        # Use streaming if enabled
        if settings.get("tts_speech_to_speech_streaming", True):
            return await voice_conversion_streaming(
                source_audio, target_voice_id, model, voice_settings, remove_noise, output_format
            )
        else:
            return await voice_conversion(
                source_audio, target_voice_id, model, voice_settings, remove_noise, output_format
            )
        
    except Exception as e:
        error_msg = f"Error decoding base64 audio: {e}"
        PrintStyle.error(error_msg)
        return {
            "status": "error",
            "audio": "",
            "message": error_msg
        }

async def get_available_sts_models() -> list:
    """Get list of available Speech-to-Speech models"""
    return [
        {
            "id": "eleven_english_sts_v2",
            "name": "English STS V2",
            "description": "Optimized for English speech-to-speech conversion",
            "languages": ["en"],
            "features": ["voice_conversion", "emotion_preservation", "timing_preservation"]
        },
        {
            "id": "eleven_multilingual_sts_v2", 
            "name": "Multilingual STS V2",
            "description": "Supports multiple languages for speech-to-speech conversion",
            "languages": ["en", "es", "fr", "de", "it", "pt", "pl", "tr", "ru", "ar", "zh", "ja", "hi", "ko"],
            "features": ["voice_conversion", "emotion_preservation", "timing_preservation", "multilingual"]
        }
    ]

async def test_sts_connection() -> dict:
    """Test ElevenLabs Speech-to-Speech connection and return status"""
    if not ENABLE_ELEVENLABS:
        return {
            "status": "disabled",
            "message": "ElevenLabs Speech-to-Speech disabled. Configure API key to enable.",
            "models_available": []
        }
    
    try:
        await _preload_sts()
        
        # Create a small test audio (1 second of sine wave)
        import wave
        import io
        import math
        
        # Generate 1 second of 440Hz sine wave at 16kHz
        sample_rate = 16000
        duration = 1.0
        frequency = 440.0
        
        test_audio_data = io.BytesIO()
        with wave.open(test_audio_data, 'wb') as wav_file:
            wav_file.setnchannels(1)  # Mono
            wav_file.setsampwidth(2)  # 16-bit
            wav_file.setframerate(sample_rate)
            
            # Generate sine wave samples
            samples = []
            for i in range(int(sample_rate * duration)):
                sample = int(32767 * math.sin(2 * math.pi * frequency * i / sample_rate))
                samples.extend([sample & 0xff, (sample >> 8) & 0xff])
            
            wav_file.writeframes(bytes(samples))
        
        test_audio_bytes = test_audio_data.getvalue()
        
        # Test with a default voice (Rachel - commonly available)
        default_voice_id = "21m00Tcm4TlvDq8ikWAM"  # Rachel
        
        # Test voice conversion
        result = await voice_conversion(test_audio_bytes, default_voice_id, "eleven_english_sts_v2")
        
        if result["status"] == "success":
            return {
                "status": "success",
                "message": "ElevenLabs Speech-to-Speech is working",
                "models_available": await get_available_sts_models(),
                "test_result": {
                    "audio_size": result.get("audio_size", 0),
                    "target_voice": default_voice_id
                }
            }
        else:
            return {
                "status": "error",
                "message": f"Speech-to-Speech test failed: {result.get('message', 'Unknown error')}",
                "models_available": []
            }
            
    except Exception as e:
        return {
            "status": "error",
            "message": f"Speech-to-Speech connection test failed: {e}",
            "models_available": []
        }

async def cleanup_sts():
    """Cleanup Speech-to-Speech resources"""
    global _sts_session
    if _sts_session:
        try:
            await _sts_session.close()
        except Exception:
            pass
        finally:
            _sts_session = None

# Unified interface function for settings-based usage
async def speech_to_speech_convert(source_audio: bytes, settings: dict = None) -> dict:
    """
    Unified speech-to-speech conversion using settings
    
    Args:
        source_audio: Source audio bytes to convert
        settings: Settings dict containing Speech-to-Speech preferences
        
    Returns:
        dict: Conversion result
    """
    if not settings:
        settings = {}
    
    target_voice_id = settings.get("tts_speech_to_speech_voice_id", "21m00Tcm4TlvDq8ikWAM")  # Rachel
    
    return await convert_base64_audio(
        base64.b64encode(source_audio).decode('utf-8'),
        target_voice_id,
        settings
    )