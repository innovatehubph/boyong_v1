"""
Working TTS Helper - Functional text-to-speech for Pareng Boyong
Provides multiple TTS backends with fallback options
"""

import base64
import io
import tempfile
import os
import subprocess
import asyncio
from pathlib import Path
from python.helpers.print_style import PrintStyle

# TTS Backend availability
TTS_BACKENDS = {
    "pyttsx3": False,
    "espeak_ng": False,
    "browser": True  # Always available as fallback
}

def check_tts_availability():
    """Check which TTS backends are available"""
    global TTS_BACKENDS
    
    # Check pyttsx3
    try:
        import pyttsx3
        engine = pyttsx3.init()
        TTS_BACKENDS["pyttsx3"] = True
        PrintStyle.standard("✅ pyttsx3 TTS backend available")
    except Exception as e:
        PrintStyle.warning(f"pyttsx3 not available: {e}")
    
    # Check espeak-ng
    try:
        result = subprocess.run(['espeak-ng', '--version'], 
                              capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            TTS_BACKENDS["espeak_ng"] = True
            PrintStyle.standard("✅ espeak-ng TTS backend available")
    except Exception as e:
        PrintStyle.warning(f"espeak-ng not available: {e}")
    
    return TTS_BACKENDS

async def synthesize_speech(text: str, voice: str = "default", speed: float = 1.0) -> str:
    """
    Synthesize speech from text using available TTS backend
    
    Args:
        text (str): Text to synthesize
        voice (str): Voice to use ("default", "male", "female", "filipino")
        speed (float): Speech speed (0.5 to 2.0)
    
    Returns:
        str: Base64 encoded audio data or browser TTS HTML
    """
    
    # Check backends if not done already
    if not any(TTS_BACKENDS.values()):
        check_tts_availability()
    
    # Try pyttsx3 first
    if TTS_BACKENDS["pyttsx3"]:
        try:
            return await _synthesize_pyttsx3(text, voice, speed)
        except Exception as e:
            PrintStyle.warning(f"pyttsx3 synthesis failed: {e}")
    
    # Try espeak-ng
    if TTS_BACKENDS["espeak_ng"]:
        try:
            return await _synthesize_espeak(text, voice, speed)
        except Exception as e:
            PrintStyle.warning(f"espeak-ng synthesis failed: {e}")
    
    # Fallback to browser TTS
    return _generate_browser_tts(text, voice, speed)

async def _synthesize_pyttsx3(text: str, voice: str, speed: float) -> str:
    """Synthesize using pyttsx3"""
    import pyttsx3
    
    def _generate():
        engine = pyttsx3.init()
        
        # Configure voice
        voices = engine.getProperty('voices')
        if voices:
            if voice == "female" and len(voices) > 1:
                engine.setProperty('voice', voices[1].id)
            elif voice == "male" and len(voices) > 0:
                engine.setProperty('voice', voices[0].id)
        
        # Configure speed
        rate = engine.getProperty('rate')
        engine.setProperty('rate', int(rate * speed))
        
        # Generate to temporary file
        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as tmp:
            temp_file = tmp.name
        
        try:
            engine.save_to_file(text, temp_file)
            engine.runAndWait()
            
            # Read and encode audio
            with open(temp_file, 'rb') as f:
                audio_data = f.read()
            
            return base64.b64encode(audio_data).decode('utf-8')
            
        finally:
            if os.path.exists(temp_file):
                os.unlink(temp_file)
    
    # Run in thread to avoid blocking
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, _generate)

async def _synthesize_espeak(text: str, voice: str, speed: float) -> str:
    """Synthesize using espeak-ng"""
    
    # Configure voice
    voice_param = "en"  # Default English
    if voice == "filipino":
        voice_param = "en+f3"  # English with female voice
    elif voice == "female":
        voice_param = "en+f3"
    elif voice == "male":
        voice_param = "en+m3"
    
    # Configure speed (espeak uses words per minute)
    speed_wpm = int(175 * speed)  # Default 175 wpm
    
    with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as tmp:
        temp_file = tmp.name
    
    try:
        # Generate speech
        cmd = [
            'espeak-ng',
            '-v', voice_param,
            '-s', str(speed_wpm),
            '-w', temp_file,
            text
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0 and os.path.exists(temp_file):
            with open(temp_file, 'rb') as f:
                audio_data = f.read()
            
            return base64.b64encode(audio_data).decode('utf-8')
        else:
            raise Exception(f"espeak-ng failed: {result.stderr}")
            
    finally:
        if os.path.exists(temp_file):
            os.unlink(temp_file)

def _generate_browser_tts(text: str, voice: str, speed: float) -> str:
    """Generate browser-based TTS HTML"""
    
    # Voice mapping for browser TTS
    browser_voice = "default"
    if voice == "female":
        browser_voice = "female"
    elif voice == "male":
        browser_voice = "male"
    elif voice == "filipino":
        browser_voice = "filipino"
    
    # Create browser TTS HTML
    tts_html = f"""
    <div class="tts-player" style="padding: 10px; border: 1px solid #ddd; border-radius: 8px; margin: 10px 0;">
        <div style="display: flex; align-items: center; gap: 10px;">
            <button onclick="playTTS(this)" class="tts-play-btn" 
                    data-text="{text}" data-voice="{browser_voice}" data-speed="{speed}"
                    style="padding: 8px 16px; background: #4CAF50; color: white; border: none; border-radius: 4px; cursor: pointer;">
                🔊 Play Speech
            </button>
            <span style="color: #666; font-size: 14px;">
                Voice: {voice.title()}, Speed: {speed}x
            </span>
        </div>
        <div style="margin-top: 8px; padding: 8px; background: #f9f9f9; border-radius: 4px; font-style: italic;">
            "{text}"
        </div>
    </div>
    
    <script>
    function playTTS(button) {{
        const text = button.getAttribute('data-text');
        const voice = button.getAttribute('data-voice');
        const speed = parseFloat(button.getAttribute('data-speed'));
        
        if ('speechSynthesis' in window) {{
            // Stop any current speech
            window.speechSynthesis.cancel();
            
            // Create utterance
            const utterance = new SpeechSynthesisUtterance(text);
            utterance.rate = speed;
            
            // Set voice if available
            const voices = window.speechSynthesis.getVoices();
            if (voices.length > 0) {{
                if (voice === 'female') {{
                    const femaleVoice = voices.find(v => v.name.toLowerCase().includes('female') || v.name.toLowerCase().includes('woman'));
                    if (femaleVoice) utterance.voice = femaleVoice;
                }} else if (voice === 'male') {{
                    const maleVoice = voices.find(v => v.name.toLowerCase().includes('male') || v.name.toLowerCase().includes('man'));
                    if (maleVoice) utterance.voice = maleVoice;
                }} else if (voice === 'filipino') {{
                    const filipinoVoice = voices.find(v => v.lang.includes('ph') || v.lang.includes('fil'));
                    if (filipinoVoice) utterance.voice = filipinoVoice;
                }}
            }}
            
            // Update button during speech
            const originalText = button.textContent;
            button.textContent = '⏸️ Playing...';
            button.disabled = true;
            
            utterance.onend = function() {{
                button.textContent = originalText;
                button.disabled = false;
            }};
            
            // Start speech
            window.speechSynthesis.speak(utterance);
        }} else {{
            alert('Speech synthesis not supported in this browser');
        }}
    }}
    
    // Load voices when available
    if ('speechSynthesis' in window) {{
        window.speechSynthesis.getVoices();
    }}
    </script>
    """
    
    return tts_html

# Initialize TTS backends on import
check_tts_availability()

# Export main functions
__all__ = ['synthesize_speech', 'check_tts_availability', 'TTS_BACKENDS']