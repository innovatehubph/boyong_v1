#!/usr/bin/env python3
"""
Multimodal AI Services Installation Script for Pareng Boyong
Installs and configures image, video, and audio generation services
"""

import os
import sys
import subprocess
import argparse
from pathlib import Path
from python.helpers.print_style import PrintStyle

class MultimodalInstaller:
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.services_dir = self.project_root / "multimodal_services"
        
    def print_header(self, text: str):
        """Print section header"""
        PrintStyle(font_color="cyan", background_color="black", padding=True).print(f"\n🎨 {text}")
    
    def print_success(self, text: str):
        """Print success message"""
        PrintStyle(font_color="green", padding=False).print(f"✅ {text}")
    
    def print_warning(self, text: str):
        """Print warning message"""
        PrintStyle(font_color="yellow", padding=False).print(f"⚠️ {text}")
    
    def print_error(self, text: str):
        """Print error message"""
        PrintStyle(font_color="red", padding=False).print(f"❌ {text}")
    
    def print_info(self, text: str):
        """Print info message"""
        PrintStyle(font_color="blue", padding=False).print(f"ℹ️ {text}")
    
    def run_command(self, cmd: list, cwd: Path = None, check: bool = True) -> subprocess.CompletedProcess:
        """Run a command and return the result"""
        self.print_info(f"Running: {' '.join(cmd)}")
        return subprocess.run(cmd, cwd=cwd, check=check, capture_output=True, text=True)
    
    def install_comfyui(self):
        """Install ComfyUI for image and video generation"""
        self.print_header("Installing ComfyUI for Image/Video Generation")
        
        comfyui_dir = self.services_dir / "ComfyUI"
        
        if comfyui_dir.exists():
            self.print_warning("ComfyUI already exists, skipping clone")
        else:
            try:
                self.run_command([
                    "git", "clone", "https://github.com/comfyanonymous/ComfyUI.git", str(comfyui_dir)
                ])
                self.print_success("ComfyUI cloned successfully")
            except subprocess.CalledProcessError as e:
                self.print_error(f"Failed to clone ComfyUI: {e}")
                return False
        
        # Install ComfyUI dependencies
        try:
            self.run_command([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], cwd=comfyui_dir)
            self.print_success("ComfyUI dependencies installed")
        except subprocess.CalledProcessError as e:
            self.print_error(f"Failed to install ComfyUI dependencies: {e}")
            return False
        
        # Install additional video nodes
        self.install_comfyui_video_nodes(comfyui_dir)
        
        return True
    
    def install_comfyui_video_nodes(self, comfyui_dir: Path):
        """Install video generation nodes for ComfyUI"""
        self.print_header("Installing Video Generation Nodes")
        
        custom_nodes_dir = comfyui_dir / "custom_nodes"
        custom_nodes_dir.mkdir(exist_ok=True)
        
        # Video nodes to install
        video_nodes = [
            {
                "name": "ComfyUI-VideoHelperSuite",
                "url": "https://github.com/Kosinkadink/ComfyUI-VideoHelperSuite.git",
                "description": "Video processing utilities"
            },
            {
                "name": "ComfyUI-AnimateDiff-Evolved",
                "url": "https://github.com/Kosinkadink/ComfyUI-AnimateDiff-Evolved.git",
                "description": "AnimateDiff integration"
            }
        ]
        
        for node in video_nodes:
            node_dir = custom_nodes_dir / node["name"]
            if node_dir.exists():
                self.print_warning(f"{node['name']} already exists, skipping")
                continue
            
            try:
                self.run_command(["git", "clone", node["url"], str(node_dir)])
                self.print_success(f"Installed {node['name']}: {node['description']}")
                
                # Install node dependencies if requirements.txt exists
                requirements_file = node_dir / "requirements.txt"
                if requirements_file.exists():
                    self.run_command([sys.executable, "-m", "pip", "install", "-r", str(requirements_file)])
                    
            except subprocess.CalledProcessError as e:
                self.print_error(f"Failed to install {node['name']}: {e}")
    
    def install_audiocraft(self):
        """Install AudioCraft for music and sound generation"""
        self.print_header("Installing AudioCraft for Music/Audio Generation")
        
        try:
            # Install audiocraft
            self.run_command([sys.executable, "-m", "pip", "install", "-U", "audiocraft"])
            self.print_success("AudioCraft installed successfully")
            
            # Create AudioCraft server script
            self.create_audiocraft_server()
            
            return True
            
        except subprocess.CalledProcessError as e:
            self.print_error(f"Failed to install AudioCraft: {e}")
            return False
    
    def create_audiocraft_server(self):
        """Create AudioCraft API server"""
        server_script = self.services_dir / "audiocraft_server.py"
        server_content = '''#!/usr/bin/env python3
"""
AudioCraft API Server for Pareng Boyong
Provides REST API for MusicGen and AudioGen
"""

import asyncio
import base64
import io
import torch
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional
import uvicorn
import numpy as np
import scipy.io.wavfile as wavfile

# Import audiocraft
try:
    from audiocraft.models import MusicGen, AudioGen
    from audiocraft.data.audio import audio_write
    AUDIOCRAFT_AVAILABLE = True
except ImportError:
    AUDIOCRAFT_AVAILABLE = False

app = FastAPI(title="AudioCraft API Server", version="1.0.0")

# Global models
musicgen_model = None
audiogen_model = None

class MusicRequest(BaseModel):
    prompt: str
    duration: int = 10
    model: str = "facebook/musicgen-medium"
    top_k: int = 250
    top_p: float = 0.0
    temperature: float = 1.0

class AudioRequest(BaseModel):
    prompt: str
    duration: int = 5
    model: str = "facebook/audiogen-medium"

@app.on_event("startup")
async def startup_event():
    global musicgen_model, audiogen_model
    
    if not AUDIOCRAFT_AVAILABLE:
        print("❌ AudioCraft not available")
        return
    
    print("🎵 Loading AudioCraft models...")
    
    try:
        # Load MusicGen model
        musicgen_model = MusicGen.get_pretrained('facebook/musicgen-medium')
        musicgen_model.set_generation_params(duration=10)
        print("✅ MusicGen model loaded")
        
        # Load AudioGen model  
        audiogen_model = AudioGen.get_pretrained('facebook/audiogen-medium')
        print("✅ AudioGen model loaded")
        
    except Exception as e:
        print(f"❌ Failed to load models: {e}")

@app.get("/health")
async def health_check():
    return {"status": "healthy", "audiocraft_available": AUDIOCRAFT_AVAILABLE}

@app.post("/generate/music")
async def generate_music(request: MusicRequest):
    if not AUDIOCRAFT_AVAILABLE or musicgen_model is None:
        raise HTTPException(status_code=503, detail="MusicGen not available")
    
    try:
        # Set generation parameters
        musicgen_model.set_generation_params(
            duration=request.duration,
            top_k=request.top_k,
            top_p=request.top_p,
            temperature=request.temperature
        )
        
        # Generate music
        descriptions = [request.prompt]
        wav = musicgen_model.generate(descriptions)
        
        # Convert to base64
        audio_base64 = wav_to_base64(wav[0].cpu().numpy(), musicgen_model.sample_rate)
        
        return {
            "success": True,
            "audio_base64": audio_base64,
            "sample_rate": musicgen_model.sample_rate,
            "duration": request.duration
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/generate/audio")  
async def generate_audio(request: AudioRequest):
    if not AUDIOCRAFT_AVAILABLE or audiogen_model is None:
        raise HTTPException(status_code=503, detail="AudioGen not available")
    
    try:
        # Set generation parameters
        audiogen_model.set_generation_params(duration=request.duration)
        
        # Generate audio
        descriptions = [request.prompt]
        wav = audiogen_model.generate(descriptions)
        
        # Convert to base64
        audio_base64 = wav_to_base64(wav[0].cpu().numpy(), audiogen_model.sample_rate)
        
        return {
            "success": True,
            "audio_base64": audio_base64,
            "sample_rate": audiogen_model.sample_rate,
            "duration": request.duration
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

def wav_to_base64(audio_data: np.ndarray, sample_rate: int) -> str:
    """Convert audio numpy array to base64 WAV"""
    # Ensure audio is in the right format
    if audio_data.dtype != np.int16:
        audio_data = (audio_data * 32767).astype(np.int16)
    
    # Create WAV file in memory
    buffer = io.BytesIO()
    wavfile.write(buffer, sample_rate, audio_data)
    buffer.seek(0)
    
    # Convert to base64
    audio_base64 = base64.b64encode(buffer.read()).decode('utf-8')
    return audio_base64

if __name__ == "__main__":
    print("🎵 Starting AudioCraft API Server...")
    uvicorn.run(app, host="0.0.0.0", port=8000)
'''
        
        server_script.parent.mkdir(exist_ok=True)
        with open(server_script, 'w') as f:
            f.write(server_content)
        
        # Make executable
        os.chmod(server_script, 0o755)
        
        self.print_success("AudioCraft server script created")
    
    def install_bark(self):
        """Install Bark TTS for enhanced speech generation"""
        self.print_header("Installing Bark TTS for Enhanced Speech")
        
        try:
            # Install bark
            self.run_command([sys.executable, "-m", "pip", "install", "git+https://github.com/suno-ai/bark.git"])
            self.print_success("Bark TTS installed successfully")
            
            # Create Bark server script
            self.create_bark_server()
            
            return True
            
        except subprocess.CalledProcessError as e:
            self.print_error(f"Failed to install Bark TTS: {e}")
            return False
    
    def create_bark_server(self):
        """Create Bark TTS API server"""
        server_script = self.services_dir / "bark_server.py"
        server_content = '''#!/usr/bin/env python3
"""
Bark TTS API Server for Pareng Boyong
Provides REST API for Bark text-to-speech
"""

import asyncio
import base64
import io
import numpy as np
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional
import uvicorn
import scipy.io.wavfile as wavfile

# Import Bark
try:
    from bark import SAMPLE_RATE, generate_audio, preload_models
    from bark.generation import set_seed
    BARK_AVAILABLE = True
except ImportError:
    BARK_AVAILABLE = False

app = FastAPI(title="Bark TTS API Server", version="1.0.0")

class SpeechRequest(BaseModel):
    text: str
    voice_preset: str = "v2/en_speaker_6"
    temperature: float = 0.7
    silence_duration: float = 0.25

@app.on_event("startup")
async def startup_event():
    if not BARK_AVAILABLE:
        print("❌ Bark TTS not available")
        return
    
    print("🗣️ Loading Bark TTS models...")
    
    try:
        # Preload models
        preload_models()
        print("✅ Bark TTS models loaded")
        
    except Exception as e:
        print(f"❌ Failed to load Bark models: {e}")

@app.get("/health")
async def health_check():
    return {"status": "healthy", "bark_available": BARK_AVAILABLE}

@app.get("/voices")
async def get_voices():
    """Get available voice presets"""
    voices = [
        "v2/en_speaker_0", "v2/en_speaker_1", "v2/en_speaker_2", 
        "v2/en_speaker_3", "v2/en_speaker_4", "v2/en_speaker_5",
        "v2/en_speaker_6", "v2/en_speaker_7", "v2/en_speaker_8", "v2/en_speaker_9"
    ]
    return {"voices": voices}

@app.post("/generate")
async def generate_speech(request: SpeechRequest):
    if not BARK_AVAILABLE:
        raise HTTPException(status_code=503, detail="Bark TTS not available")
    
    try:
        # Set random seed for reproducibility
        set_seed(42)
        
        # Generate audio
        audio_array = generate_audio(
            request.text,
            history_prompt=request.voice_preset,
            text_temp=request.temperature,
            waveform_temp=request.temperature
        )
        
        # Convert to base64
        audio_base64 = wav_to_base64(audio_array, SAMPLE_RATE)
        
        return {
            "success": True,
            "audio_base64": audio_base64,
            "sample_rate": SAMPLE_RATE,
            "voice_preset": request.voice_preset
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

def wav_to_base64(audio_data: np.ndarray, sample_rate: int) -> str:
    """Convert audio numpy array to base64 WAV"""
    # Ensure audio is in the right format
    if audio_data.dtype != np.int16:
        audio_data = (audio_data * 32767).astype(np.int16)
    
    # Create WAV file in memory
    buffer = io.BytesIO()
    wavfile.write(buffer, sample_rate, audio_data)
    buffer.seek(0)
    
    # Convert to base64
    audio_base64 = base64.b64encode(buffer.read()).decode('utf-8')
    return audio_base64

if __name__ == "__main__":
    print("🗣️ Starting Bark TTS API Server...")
    uvicorn.run(app, host="0.0.0.0", port=8001)
'''
        
        server_script.parent.mkdir(exist_ok=True)
        with open(server_script, 'w') as f:
            f.write(server_content)
        
        # Make executable
        os.chmod(server_script, 0o755)
        
        self.print_success("Bark TTS server script created")
    
    def create_startup_scripts(self):
        """Create startup scripts for all services"""
        self.print_header("Creating Startup Scripts")
        
        # Create main startup script
        startup_script = self.services_dir / "start_multimodal.py"
        startup_content = '''#!/usr/bin/env python3
"""
Multimodal Services Startup Script for Pareng Boyong
Starts all multimodal AI services
"""

import os
import sys
import subprocess
import time
import signal
from pathlib import Path

class MultimodalServices:
    def __init__(self):
        self.services_dir = Path(__file__).parent
        self.processes = []
    
    def start_comfyui(self):
        """Start ComfyUI server"""
        print("🎨 Starting ComfyUI...")
        comfyui_dir = self.services_dir / "ComfyUI"
        
        if not comfyui_dir.exists():
            print("❌ ComfyUI not found. Run install_multimodal.py first.")
            return False
        
        cmd = [sys.executable, "main.py", "--listen", "--port", "8188"]
        process = subprocess.Popen(cmd, cwd=comfyui_dir)
        self.processes.append(("ComfyUI", process))
        print("✅ ComfyUI started on port 8188")
        return True
    
    def start_audiocraft(self):
        """Start AudioCraft server"""
        print("🎵 Starting AudioCraft...")
        server_script = self.services_dir / "audiocraft_server.py"
        
        if not server_script.exists():
            print("❌ AudioCraft server not found. Run install_multimodal.py first.")
            return False
        
        process = subprocess.Popen([sys.executable, str(server_script)])
        self.processes.append(("AudioCraft", process))
        print("✅ AudioCraft started on port 8000")
        return True
    
    def start_bark(self):
        """Start Bark TTS server"""
        print("🗣️ Starting Bark TTS...")
        server_script = self.services_dir / "bark_server.py"
        
        if not server_script.exists():
            print("❌ Bark server not found. Run install_multimodal.py first.")
            return False
        
        process = subprocess.Popen([sys.executable, str(server_script)])
        self.processes.append(("Bark TTS", process))
        print("✅ Bark TTS started on port 8001")
        return True
    
    def start_all(self):
        """Start all services"""
        print("🚀 Starting Pareng Boyong Multimodal Services...")
        
        # Start services
        self.start_comfyui()
        time.sleep(3)  # Give ComfyUI time to start
        
        self.start_audiocraft()
        time.sleep(2)
        
        self.start_bark()
        time.sleep(2)
        
        print("\\n🎨 All multimodal services started!")
        print("\\n📍 Service URLs:")
        print("  • ComfyUI: http://localhost:8188")
        print("  • AudioCraft: http://localhost:8000")
        print("  • Bark TTS: http://localhost:8001")
        print("\\n⚠️ Press Ctrl+C to stop all services")
        
        # Wait for interrupt
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            self.stop_all()
    
    def stop_all(self):
        """Stop all services"""
        print("\\n🛑 Stopping all services...")
        
        for name, process in self.processes:
            try:
                process.terminate()
                process.wait(timeout=5)
                print(f"✅ {name} stopped")
            except subprocess.TimeoutExpired:
                process.kill()
                print(f"⚠️ {name} force killed")
            except Exception as e:
                print(f"❌ Error stopping {name}: {e}")
        
        print("🏁 All services stopped")

if __name__ == "__main__":
    services = MultimodalServices()
    services.start_all()
'''
        
        startup_script.parent.mkdir(exist_ok=True)
        with open(startup_script, 'w') as f:
            f.write(startup_content)
        
        # Make executable
        os.chmod(startup_script, 0o755)
        
        self.print_success("Startup script created: start_multimodal.py")
        
        # Create individual service scripts
        self.create_service_scripts()
    
    def create_service_scripts(self):
        """Create individual service startup scripts"""
        
        # ComfyUI start script
        comfyui_script = self.services_dir / "start_comfyui.sh"
        with open(comfyui_script, 'w') as f:
            f.write(f"""#!/bin/bash
echo "🎨 Starting ComfyUI..."
cd "{self.services_dir}/ComfyUI"
python main.py --listen --port 8188
""")
        os.chmod(comfyui_script, 0o755)
        
        # AudioCraft start script
        audiocraft_script = self.services_dir / "start_audiocraft.sh"
        with open(audiocraft_script, 'w') as f:
            f.write(f"""#!/bin/bash
echo "🎵 Starting AudioCraft..."
cd "{self.services_dir}"
python audiocraft_server.py
""")
        os.chmod(audiocraft_script, 0o755)
        
        # Bark start script
        bark_script = self.services_dir / "start_bark.sh"
        with open(bark_script, 'w') as f:
            f.write(f"""#!/bin/bash
echo "🗣️ Starting Bark TTS..." 
cd "{self.services_dir}"
python bark_server.py
""")
        os.chmod(bark_script, 0o755)
        
        self.print_success("Individual service scripts created")
    
    def create_readme(self):
        """Create README with instructions"""
        readme_file = self.services_dir / "README.md"
        readme_content = '''# Pareng Boyong Multimodal AI Services

This directory contains the multimodal AI services for Pareng Boyong, enabling image, video, and audio generation capabilities.

## 🚀 Quick Start

### Start All Services
```bash
python start_multimodal.py
```

### Start Individual Services
```bash
# ComfyUI (Image/Video Generation)
./start_comfyui.sh

# AudioCraft (Music/Sound Generation)  
./start_audiocraft.sh

# Bark TTS (Enhanced Speech)
./start_bark.sh
```

## 📍 Service URLs

- **ComfyUI**: http://localhost:8188
- **AudioCraft API**: http://localhost:8000
- **Bark TTS API**: http://localhost:8001

## 🎨 Capabilities

### Image Generation
- **Models**: FLUX.1, Stable Diffusion
- **Features**: High-quality images, multiple styles, custom dimensions
- **Interface**: ComfyUI web interface + API

### Video Generation  
- **Models**: HunyuanVideo, CogVideoX, AnimateDiff
- **Features**: Text-to-video, image animation, multiple formats
- **Interface**: ComfyUI custom nodes

### Music & Audio Generation
- **Models**: MusicGen, AudioGen
- **Features**: Music composition, sound effects, ambient audio
- **Interface**: FastAPI REST endpoints

### Enhanced Speech
- **Models**: Bark TTS
- **Features**: Emotional speech, multiple voices, music generation
- **Interface**: FastAPI REST endpoints

## 🛠️ Requirements

- Python 3.8+
- CUDA-capable GPU (recommended)
- 16GB+ RAM (32GB recommended for video)
- 50GB+ free disk space

## 📚 Usage Examples

### Generate Image
```python
from python.helpers.image_generation import generate_image

image_base64 = await generate_image("A beautiful sunset over mountains")
```

### Generate Music
```python  
from python.helpers.audio_generation import generate_music

audio_base64 = await generate_music("upbeat electronic music", duration=30)
```

### Generate Video
```python
from python.helpers.video_generation import generate_video

video_base64 = await generate_video("A cat walking in a garden", duration=5)
```

## 🔧 Troubleshooting

### ComfyUI Issues
- Ensure CUDA is properly installed
- Check model files are downloaded
- Verify custom nodes are installed

### AudioCraft Issues  
- Check PyTorch installation
- Ensure sufficient GPU memory
- Verify model downloads

### Performance Tips
- Use smaller models for faster generation
- Reduce resolution/duration for testing
- Close other GPU-intensive applications

## 📄 Logs

Service logs are written to:
- ComfyUI: `ComfyUI/logs/`
- AudioCraft: stdout/stderr
- Bark TTS: stdout/stderr

For issues, check the logs or contact support.
'''
        
        with open(readme_file, 'w') as f:
            f.write(readme_content)
        
        self.print_success("README.md created")
    
    def install_all(self, include_video: bool = True, include_audio: bool = True, include_speech: bool = True):
        """Install all multimodal services"""
        self.print_header("Pareng Boyong Multimodal AI Installation")
        
        # Create services directory
        self.services_dir.mkdir(exist_ok=True)
        
        success_count = 0
        total_services = 1 + (1 if include_audio else 0) + (1 if include_speech else 0)
        
        # Install ComfyUI (required for images, optional video nodes)
        if self.install_comfyui():
            success_count += 1
        
        # Install AudioCraft (optional)
        if include_audio and self.install_audiocraft():
            success_count += 1
            
        # Install Bark TTS (optional)
        if include_speech and self.install_bark():
            success_count += 1
        
        # Create startup scripts and documentation
        self.create_startup_scripts()
        self.create_readme()
        
        # Final summary
        self.print_header("Installation Summary")
        self.print_info(f"Successfully installed {success_count}/{total_services} services")
        
        if success_count > 0:
            self.print_success("Multimodal AI services installed successfully!")
            self.print_info("To start services: python multimodal_services/start_multimodal.py")
            self.print_info("Documentation: multimodal_services/README.md")
        else:
            self.print_error("Installation failed. Check error messages above.")
            return False
        
        return True

def main():
    parser = argparse.ArgumentParser(description="Install Pareng Boyong Multimodal AI Services")
    parser.add_argument("--no-video", action="store_true", help="Skip video generation components")
    parser.add_argument("--no-audio", action="store_true", help="Skip audio/music generation components")  
    parser.add_argument("--no-speech", action="store_true", help="Skip enhanced speech components")
    parser.add_argument("--minimal", action="store_true", help="Install only ComfyUI for images")
    
    args = parser.parse_args()
    
    installer = MultimodalInstaller()
    
    if args.minimal:
        include_video = False
        include_audio = False
        include_speech = False
    else:
        include_video = not args.no_video
        include_audio = not args.no_audio
        include_speech = not args.no_speech
    
    success = installer.install_all(
        include_video=include_video,
        include_audio=include_audio, 
        include_speech=include_speech
    )
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()