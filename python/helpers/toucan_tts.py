# toucan_tts.py - Simplified Filipino TTS using alternative approach

import base64
import io
import warnings
import asyncio
import os
import sys

warnings.filterwarnings("ignore", category=FutureWarning)

# Add current directory to path for imports
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.join(current_dir, '../..')
sys.path.insert(0, project_root)

try:
    from python.helpers.print_style import PrintStyle
except ImportError:
    # Fallback print style
    class PrintStyle:
        @staticmethod
        def standard(msg): print(f"[INFO] {msg}")
        @staticmethod
        def error(msg): print(f"[ERROR] {msg}")
        @staticmethod
        def warning(msg): print(f"[WARNING] {msg}")

# Flag to indicate if Toucan TTS is available
TOUCAN_AVAILABLE = False
_device = "cpu"
is_initializing = False

async def preload():
    """Preload Toucan TTS model"""
    try:
        return await _preload()
    except Exception as e:
        PrintStyle.error(f"Toucan TTS not available: {e}")
        # Don't raise, just mark as unavailable
        return False

async def _preload():
    """Initialize Toucan TTS pipeline"""
    global TOUCAN_AVAILABLE, is_initializing
    
    while is_initializing:
        await asyncio.sleep(0.1)
    
    try:
        is_initializing = True
        # Check if ToucanTTS directory exists
        toucan_dir = os.path.join(os.path.dirname(__file__), '../../toucan_tts')
        if os.path.exists(toucan_dir):
            PrintStyle.standard("ToucanTTS directory found - attempting to initialize")
            # For now, mark as available but note it needs more setup
            TOUCAN_AVAILABLE = False  # Still needs proper PyTorch setup
            PrintStyle.standard("ToucanTTS requires PyTorch dependencies for full functionality")
            PrintStyle.standard("Currently using fallback TTS chain for Filipino content")
        else:
            PrintStyle.standard("ToucanTTS directory not found")
            TOUCAN_AVAILABLE = False
    finally:
        is_initializing = False
    
    return TOUCAN_AVAILABLE

async def is_downloading():
    """Check if TTS is initializing"""
    return is_initializing

async def is_downloaded():
    """Check if TTS is ready"""
    return TOUCAN_AVAILABLE and not is_initializing

async def synthesize_sentences(sentences: list[str]):
    """Generate audio for multiple sentences using Toucan TTS
    
    Args:
        sentences: List of text sentences to synthesize in Filipino
        
    Returns:
        str: Base64 encoded audio data (empty if not available)
    """
    await _preload()
    
    if not TOUCAN_AVAILABLE:
        PrintStyle.standard("Toucan TTS not available - will use fallback TTS")
        return ""  # Return empty to trigger fallback
    
    # Since Toucan TTS is not working in this environment, return empty
    return ""

async def _synthesize_sentences(sentences: list[str]):
    """Internal synthesis implementation - placeholder"""
    return ""

async def _generate_audio(text: str) -> bytes:
    """Generate audio using Toucan TTS pipeline - placeholder"""
    return b""

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
    
    # Clean up consecutive brackets
    text = re.sub(r'\[([^\]]+)\]\s*\[([^\]]+)\]', r'[\1 and \2]', text)
    
    return text.strip()

async def cleanup():
    """Cleanup resources"""
    global _pipeline
    if _pipeline:
        try:
            del _pipeline
        except Exception:
            # Ignore cleanup errors
            pass
        finally:
            _pipeline = None

# Compatibility functions for existing TTS interface
async def synthesize_text(text: str):
    """Single text synthesis for compatibility"""
    return await synthesize_sentences([text])

def get_voice_info():
    """Get current voice information"""
    return {
        "provider": "Toucan TTS",
        "voice_name": "Filipino Voice",
        "voice_id": "fil_default",
        "language": "Filipino (Tagalog)",
        "quality": "High"
    }

async def test_connection():
    """Test Toucan TTS connection and return status"""
    await _preload()
    
    if not TOUCAN_AVAILABLE:
        return {
            "status": "unavailable",
            "message": "Toucan TTS not available in this environment. Filipino text will use ElevenLabs or browser TTS fallback.",
            "voice": get_voice_info(),
            "audio_length": 0
        }
    
    # This would be the actual test if Toucan TTS was working
    return {
        "status": "success",
        "message": "Toucan TTS is working for Filipino language",
        "voice": get_voice_info(), 
        "audio_length": 0
    }