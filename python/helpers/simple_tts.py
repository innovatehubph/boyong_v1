"""
Simple TTS Helper - Direct implementation for Pareng Boyong
Works with espeak-ng and pyttsx3 without complex dependencies
"""

import base64
import tempfile
import os
import subprocess
import asyncio

# Simple print functions
def log_info(msg):
    print(f"[TTS INFO] {msg}")

def log_error(msg):
    print(f"[TTS ERROR] {msg}")

def log_warning(msg):
    print(f"[TTS WARNING] {msg}")

# TTS Backend availability
TTS_BACKENDS = {
    "pyttsx3": False,
    "espeak_ng": False,
    "browser": True
}

def check_tts_availability():
    """Check which TTS backends are available"""
    global TTS_BACKENDS
    
    # Check pyttsx3
    try:
        import pyttsx3
        engine = pyttsx3.init()
        engine.stop()
        TTS_BACKENDS["pyttsx3"] = True
        log_info("✅ pyttsx3 TTS backend available")
    except Exception as e:
        log_warning(f"pyttsx3 not available: {e}")
    
    # Check espeak-ng
    try:
        result = subprocess.run(['espeak-ng', '--version'], 
                              capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            TTS_BACKENDS["espeak_ng"] = True
            log_info("✅ espeak-ng TTS backend available")
    except Exception as e:
        log_warning(f"espeak-ng not available: {e}")
    
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
    
    # Try espeak-ng first (more reliable in containers)
    if TTS_BACKENDS["espeak_ng"]:
        try:
            return await _synthesize_espeak(text, voice, speed)
        except Exception as e:
            log_warning(f"espeak-ng synthesis failed: {e}")
    
    # Try pyttsx3
    if TTS_BACKENDS["pyttsx3"]:
        try:
            return await _synthesize_pyttsx3(text, voice, speed)
        except Exception as e:
            log_warning(f"pyttsx3 synthesis failed: {e}")
    
    # Fallback to browser TTS
    return _generate_browser_tts(text, voice, speed)

async def _synthesize_espeak(text: str, voice: str, speed: float) -> str:
    """Synthesize using espeak-ng"""
    
    # Configure voice
    voice_param = "en"
    if voice == "filipino":
        voice_param = "en+f3"  # English with female voice for Filipino
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
            
            if len(audio_data) > 0:
                return base64.b64encode(audio_data).decode('utf-8')
            else:
                raise Exception("Generated audio file is empty")
        else:
            raise Exception(f"espeak-ng failed: {result.stderr}")
            
    finally:
        if os.path.exists(temp_file):
            os.unlink(temp_file)

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
            engine.stop()
            
            # Read and encode audio
            if os.path.exists(temp_file):
                with open(temp_file, 'rb') as f:
                    audio_data = f.read()
                
                if len(audio_data) > 0:
                    return base64.b64encode(audio_data).decode('utf-8')
                else:
                    raise Exception("Generated audio file is empty")
            else:
                raise Exception("Audio file was not created")
            
        finally:
            if os.path.exists(temp_file):
                os.unlink(temp_file)
    
    # Run in thread to avoid blocking
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, _generate)

def _generate_browser_tts(text: str, voice: str, speed: float) -> str:
    """Generate browser-based TTS HTML"""
    
    tts_html = f"""
    <div class="tts-player" style="padding: 12px; border: 2px solid #4CAF50; border-radius: 10px; margin: 15px 0; background: linear-gradient(135deg, #f8f9fa, #e9ecef);">
        <div style="display: flex; align-items: center; gap: 12px; flex-wrap: wrap;">
            <button onclick="playTTS(this)" class="tts-play-btn" 
                    data-text="{text.replace('"', '&quot;')}" data-voice="{voice}" data-speed="{speed}"
                    style="padding: 10px 20px; background: linear-gradient(45deg, #4CAF50, #45a049); color: white; border: none; border-radius: 6px; cursor: pointer; font-weight: bold; box-shadow: 0 2px 4px rgba(0,0,0,0.2);">
                🔊 Play Speech
            </button>
            <span style="color: #555; font-size: 14px; font-weight: 500;">
                Voice: {voice.title()} | Speed: {speed}x
            </span>
        </div>
        <div style="margin-top: 12px; padding: 10px; background: #ffffff; border-radius: 6px; font-style: italic; border-left: 4px solid #4CAF50;">
            <strong>Text:</strong> "{text}"
        </div>
    </div>
    
    <script>
    function playTTS(button) {{
        const text = button.getAttribute('data-text');
        const voice = button.getAttribute('data-voice');
        const speed = parseFloat(button.getAttribute('data-speed'));
        
        if ('speechSynthesis' in window) {{
            window.speechSynthesis.cancel();
            
            const utterance = new SpeechSynthesisUtterance(text);
            utterance.rate = speed;
            
            const voices = window.speechSynthesis.getVoices();
            if (voices.length > 0) {{
                if (voice === 'female') {{
                    const femaleVoice = voices.find(v => v.name.toLowerCase().includes('female') || v.name.toLowerCase().includes('woman') || v.gender === 'female');
                    if (femaleVoice) utterance.voice = femaleVoice;
                }} else if (voice === 'male') {{
                    const maleVoice = voices.find(v => v.name.toLowerCase().includes('male') || v.name.toLowerCase().includes('man') || v.gender === 'male');
                    if (maleVoice) utterance.voice = maleVoice;
                }} else if (voice === 'filipino') {{
                    const filipinoVoice = voices.find(v => v.lang.includes('ph') || v.lang.includes('fil') || v.name.toLowerCase().includes('filipino'));
                    if (filipinoVoice) utterance.voice = filipinoVoice;
                }}
            }}
            
            const originalText = button.innerHTML;
            button.innerHTML = '⏸️ Playing...';
            button.disabled = true;
            button.style.background = 'linear-gradient(45deg, #ff9800, #f57c00)';
            
            utterance.onend = function() {{
                button.innerHTML = originalText;
                button.disabled = false;
                button.style.background = 'linear-gradient(45deg, #4CAF50, #45a049)';
            }};
            
            utterance.onerror = function() {{
                button.innerHTML = '❌ Error';
                setTimeout(() => {{
                    button.innerHTML = originalText;
                    button.disabled = false;
                    button.style.background = 'linear-gradient(45deg, #4CAF50, #45a049)';
                }}, 2000);
            }};
            
            window.speechSynthesis.speak(utterance);
        }} else {{
            alert('Speech synthesis not supported in this browser');
        }}
    }}
    </script>
    """
    
    return tts_html

# Test function for verification
def test_tts():
    """Test TTS functionality"""
    backends = check_tts_availability()
    log_info(f"Available TTS backends: {backends}")
    
    if backends["espeak_ng"]:
        try:
            # Test direct espeak-ng
            result = subprocess.run([
                'espeak-ng', '-v', 'en+f3', '-s', '150', 
                'Hello, this is a TTS test from Pareng Boyong'
            ], capture_output=True, timeout=10)
            
            if result.returncode == 0:
                log_info("✅ Direct espeak-ng test passed")
                return True
            else:
                log_error(f"espeak-ng test failed: {result.stderr}")
        except Exception as e:
            log_error(f"espeak-ng test error: {e}")
    
    return False

# Initialize on import
check_tts_availability()

# Export functions
__all__ = ['synthesize_speech', 'check_tts_availability', 'test_tts', 'TTS_BACKENDS']