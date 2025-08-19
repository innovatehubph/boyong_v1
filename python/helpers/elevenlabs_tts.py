# elevenlabs_tts.py - ElevenLabs TTS integration for Pareng Boyong

import base64
import io
import warnings
import asyncio
import aiohttp
import json
import atexit
from python.helpers.print_style import PrintStyle

warnings.filterwarnings("ignore", category=FutureWarning)

# ElevenLabs Configuration
import os
import sys
from pathlib import Path

# Add project tools path for env_loader
sys.path.append(str(Path(__file__).parent.parent / "tools"))

try:
    from env_loader import get_env, is_env_set
    ELEVENLABS_API_KEY = get_env("ELEVENLABS_API_KEY", "")
except ImportError:
    # Fallback to os.environ if env_loader is not available
    ELEVENLABS_API_KEY = os.environ.get("ELEVENLABS_API_KEY", "")
KUYA_ARCHER_VOICE_ID = "ZmDKIF1W70PJVAMJee2h"  # Custom voice
VOICE_SETTINGS = {
    "stability": 0.75,
    "similarity_boost": 0.85,
    "style": 0.20,
    "use_speaker_boost": True
}
# Auto-enable if valid API key is configured
ENABLE_ELEVENLABS = bool(ELEVENLABS_API_KEY and len(ELEVENLABS_API_KEY) > 10)

ELEVENLABS_API_URL = "https://api.elevenlabs.io/v1"

# Global state
_session = None
is_initializing = False

async def preload():
    """Preload ElevenLabs TTS session - Kokoro-style wrapper"""
    try:
        await _preload()
        return True
    except Exception as e:
        PrintStyle.error(f"ElevenLabs TTS not available: {e}")
        return False

async def _preload():
    """Initialize aiohttp session for ElevenLabs API"""
    global _session, is_initializing
    
    while is_initializing:
        await asyncio.sleep(0.1)
    
    try:
        is_initializing = True
        if not _session and ENABLE_ELEVENLABS:
            PrintStyle.standard("Initializing ElevenLabs TTS with Rachel voice...")
            
            # Validate API key format
            if not ELEVENLABS_API_KEY.startswith("sk_"):
                raise Exception("Invalid ElevenLabs API key format")
            
            timeout = aiohttp.ClientTimeout(total=30)
            _session = aiohttp.ClientSession(
                timeout=timeout,
                headers={
                    "xi-api-key": ELEVENLABS_API_KEY,
                    "Content-Type": "application/json"
                }
            )
            
            # Test API key validity
            try:
                user_info = await check_user_info()
                if user_info:
                    subscription = user_info.get('subscription', {}).get('tier', 'Free')
                    PrintStyle.standard(f"✅ ElevenLabs TTS ready with custom voice ({subscription} tier)")
                else:
                    PrintStyle.warning("⚠️ ElevenLabs API key may have limited permissions")
                    PrintStyle.warning("⚠️ Note: API key may lack 'text_to_speech' permission")
                    PrintStyle.standard("✅ Fallback TTS systems (Kokoro/ToucanTTS) will be used instead")
            except Exception as e:
                PrintStyle.warning(f"⚠️ ElevenLabs API key validation failed: {e}")
                PrintStyle.standard("✅ Fallback TTS systems (Kokoro/ToucanTTS) will be used instead")
                
        elif not ENABLE_ELEVENLABS:
            PrintStyle.standard("ElevenLabs TTS disabled - no valid API key configured")
    finally:
        is_initializing = False

async def is_downloading():
    """Check if TTS is initializing"""
    return is_initializing

async def is_downloaded():
    """Check if TTS is ready"""
    return _session is not None and not is_initializing and ENABLE_ELEVENLABS

async def synthesize_sentences(sentences: list[str]):
    """Generate audio for multiple sentences using ElevenLabs TTS
    
    Args:
        sentences: List of text sentences to synthesize
        
    Returns:
        str: Base64 encoded audio data (empty string if not available)
    """
    if not ENABLE_ELEVENLABS:
        PrintStyle.warning("ElevenLabs disabled - falling back to other TTS")
        return ""  # Return empty bytes to trigger fallback
        
    try:
        PrintStyle.info(f"ElevenLabs attempting synthesis for: {sentences[0][:50] if sentences else 'empty'}...")
        result = await _synthesize_sentences(sentences)
        
        if result:
            PrintStyle.success(f"ElevenLabs generated {len(result)} bytes of audio")
        else:
            PrintStyle.warning("ElevenLabs returned empty audio - triggering fallback")
        
        return result if result else ""
    except Exception as e:
        PrintStyle.error(f"ElevenLabs TTS synthesis error: {e}")
        PrintStyle.warning("Falling back to Kokoro TTS")
        return ""
    # Note: Keep session persistent like Kokoro keeps its pipeline
    # Only cleanup on explicit shutdown, not after every call

async def _synthesize_sentences(sentences: list[str]):
    """Internal synthesis implementation - Kokoro-style error handling"""
    # Ensure session is ready
    await _preload()
    
    if not sentences or not any(s.strip() for s in sentences):
        return ""
    
    # Combine sentences for natural flow
    combined_text = " ".join(s.strip() for s in sentences if s.strip())
    
    # Clean text for better TTS output
    cleaned_text = _clean_text_for_tts(combined_text)
    
    if not cleaned_text.strip():
        return ""
    
    try:
        # Call ElevenLabs TTS API with session reuse
        audio_data = await _call_elevenlabs_api(cleaned_text)
        
        # Return base64 encoded audio for web UI compatibility
        return base64.b64encode(audio_data).decode("utf-8")
        
    except Exception as e:
        PrintStyle.error(f"Error in ElevenLabs TTS synthesis: {e}")
        
        # Reset session on error for next attempt (like Kokoro resets pipeline)
        global _session, is_initializing
        if _session:
            try:
                await _session.close()
            except:
                pass
            _session = None
            is_initializing = False
        
        raise

async def _call_elevenlabs_api(text: str) -> bytes:
    """Call ElevenLabs TTS API using streaming endpoint"""
    if not _session:
        raise Exception("ElevenLabs TTS not initialized")
        
    url = f"{ELEVENLABS_API_URL}/text-to-speech/{KUYA_ARCHER_VOICE_ID}/stream"
    
    payload = {
        "text": text,
        "model_id": "eleven_multilingual_v2",  # Supports Filipino context
        "voice_settings": VOICE_SETTINGS,
        "output_format": "mp3_44100_128"  # High quality MP3 format
    }
    
    try:
        async with _session.post(url, json=payload) as response:
            if response.status == 200:
                # Collect all streaming chunks
                audio_chunks = []
                async for chunk in response.content.iter_chunked(8192):
                    if chunk:
                        audio_chunks.append(chunk)
                return b''.join(audio_chunks)
            else:
                error_text = await response.text()
                raise Exception(f"ElevenLabs API error {response.status}: {error_text}")
                
    except asyncio.TimeoutError:
        raise Exception("ElevenLabs API timeout")
    except aiohttp.ClientError as e:
        raise Exception(f"ElevenLabs connection error: {e}")

def _clean_text_for_tts(text: str) -> str:
    """Clean text for better TTS output"""
    import re
    
    # Remove code blocks
    text = re.sub(r'```[\s\S]*?```', ' [code block] ', text)
    text = re.sub(r'`[^`]*`', ' [code] ', text)
    
    # Remove HTML tags
    text = re.sub(r'<[^>]+>', '', text)
    
    # Remove markdown formatting
    text = re.sub(r'[*_#]+', '', text)
    text = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', text)  # [text](url) -> text
    
    # Remove URLs
    text = re.sub(r'https?://[^\s]+', ' [link] ', text)
    
    # Remove email addresses
    text = re.sub(r'\S+@\S+', ' [email] ', text)
    
    # Replace UUIDs
    text = re.sub(r'[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}', ' [ID] ', text)
    
    # Remove excessive whitespace
    text = re.sub(r'\s+', ' ', text)
    
    return text.strip()

async def cleanup():
    """Cleanup resources - call only on shutdown"""
    global _session, is_initializing
    if _session:
        try:
            await _session.close()
        except Exception:
            pass
        finally:
            _session = None
            is_initializing = False

async def shutdown():
    """Explicit shutdown function for graceful cleanup"""
    await cleanup()

def _sync_shutdown():
    """Synchronous shutdown for atexit"""
    if _session and not _session.closed:
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                loop.create_task(cleanup())
            else:
                asyncio.run(cleanup())
        except:
            pass

# Register cleanup on exit to prevent asyncio warnings
atexit.register(_sync_shutdown)

# Compatibility functions for existing interface
async def synthesize_text(text: str):
    """Single text synthesis for compatibility"""
    return await synthesize_sentences([text])

def get_voice_info():
    """Get current voice information"""
    return {
        "provider": "ElevenLabs",
        "voice_name": "Rachel",
        "voice_id": KUYA_ARCHER_VOICE_ID,
        "language": "English",
        "quality": "High"
    }

async def test_connection():
    """Test ElevenLabs TTS connection and return status"""
    if not ENABLE_ELEVENLABS:
        return {
            "status": "disabled",
            "message": "ElevenLabs TTS disabled. Configure API key to enable.",
            "voice": get_voice_info(),
            "audio_length": 0
        }
    
    try:
        await _preload()
        
        # First check user info to validate API key
        user_info = await check_user_info()
        if not user_info:
            return {
                "status": "error",
                "message": "Invalid API key or no access to user info",
                "voice": get_voice_info(),
                "audio_length": 0
            }
        
        test_audio = await synthesize_sentences(["Test"])
        return {
            "status": "success",
            "message": f"ElevenLabs TTS is working. Subscription: {user_info.get('subscription', {}).get('tier', 'Free')}",
            "voice": get_voice_info(),
            "audio_length": len(test_audio) if test_audio else 0,
            "user_info": user_info
        }
    except Exception as e:
        error_message = str(e)
        if "missing_permissions" in error_message and "text_to_speech" in error_message:
            return {
                "status": "limited", 
                "message": "ElevenLabs API key lacks text_to_speech permission. Using fallback TTS systems.",
                "voice": get_voice_info(),
                "audio_length": 0,
                "fallback_available": True
            }
        else:
            return {
                "status": "error", 
                "message": error_message,
                "voice": get_voice_info(),
                "audio_length": 0
            }

async def check_user_info():
    """Check user subscription and quota information"""
    if not _session:
        await _preload()
        
    try:
        url = f"{ELEVENLABS_API_URL}/user"
        async with _session.get(url) as response:
            if response.status == 200:
                return await response.json()
            else:
                return None
    except Exception as e:
        PrintStyle.error(f"Error checking user info: {e}")
        return None