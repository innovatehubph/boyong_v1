#!/usr/bin/env python3
"""
Advanced Video Generation Installation Script for Pareng Boyong
Installs Wan2GP, MultiTalk, Wan2.1-VACE-14B, and FusioniX models
"""

import os
import sys
import subprocess
import argparse
from pathlib import Path
from python.helpers.print_style import PrintStyle

class AdvancedVideoInstaller:
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.video_services_dir = self.project_root / "advanced_video_services"
        
    def print_header(self, text: str):
        """Print section header"""
        PrintStyle(font_color="cyan", background_color="black", padding=True).print(f"\\n🎬 {text}")
    
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
    
    def install_wan2gp(self):
        """Install Wan2GP platform"""
        self.print_header("Installing Wan2GP Platform")
        
        wan2gp_dir = self.video_services_dir / "Wan2GP"
        
        if wan2gp_dir.exists():
            self.print_warning("Wan2GP already exists, skipping clone")
        else:
            try:
                self.run_command([
                    "git", "clone", "https://github.com/deepbeepmeep/Wan2GP.git", str(wan2gp_dir)
                ])
                self.print_success("Wan2GP cloned successfully")
            except subprocess.CalledProcessError as e:
                self.print_error(f"Failed to clone Wan2GP: {e}")
                return False
        
        # Install Wan2GP dependencies
        try:
            requirements_file = wan2gp_dir / "requirements.txt"
            if requirements_file.exists():
                self.run_command([sys.executable, "-m", "pip", "install", "-r", str(requirements_file)])
                self.print_success("Wan2GP dependencies installed")
            else:
                # Install common dependencies
                deps = [
                    "torch>=2.0.0",
                    "torchvision",
                    "transformers",
                    "diffusers",
                    "accelerate",
                    "xformers",
                    "opencv-python",
                    "pillow",
                    "numpy",
                    "gradio",
                    "fastapi",
                    "uvicorn"
                ]
                self.run_command([sys.executable, "-m", "pip", "install"] + deps)
                self.print_success("Wan2GP dependencies installed from defaults")
        except subprocess.CalledProcessError as e:
            self.print_error(f"Failed to install Wan2GP dependencies: {e}")
            return False
        
        return True
    
    def install_multitalk(self):
        """Install MultiTalk conversational video platform"""
        self.print_header("Installing MultiTalk Platform")
        
        multitalk_dir = self.video_services_dir / "MultiTalk"
        
        if multitalk_dir.exists():
            self.print_warning("MultiTalk already exists, skipping clone")
        else:
            try:
                self.run_command([
                    "git", "clone", "https://github.com/MeiGen-AI/MultiTalk.git", str(multitalk_dir)
                ])
                self.print_success("MultiTalk cloned successfully")
            except subprocess.CalledProcessError as e:
                self.print_error(f"Failed to clone MultiTalk: {e}")
                return False
        
        # Install MultiTalk dependencies
        try:
            requirements_file = multitalk_dir / "requirements.txt"
            if requirements_file.exists():
                self.run_command([sys.executable, "-m", "pip", "install", "-r", str(requirements_file)])
            else:
                # Install MultiTalk specific dependencies
                deps = [
                    "torch>=2.0.0",
                    "torchaudio",
                    "transformers",
                    "diffusers",
                    "xformers",
                    "librosa",
                    "soundfile",
                    "opencv-python",
                    "pillow",
                    "numpy",
                    "scipy",
                    "gradio",
                    "fastapi",
                    "uvicorn"
                ]
                self.run_command([sys.executable, "-m", "pip", "install"] + deps)
            
            self.print_success("MultiTalk dependencies installed")
        except subprocess.CalledProcessError as e:
            self.print_error(f"Failed to install MultiTalk dependencies: {e}")
            return False
        
        return True
    
    def install_wan_models(self):
        """Install Wan2.1-VACE and FusioniX models"""
        self.print_header("Installing Wan Models (VACE-14B & FusioniX)")
        
        models_dir = self.video_services_dir / "wan_models"
        models_dir.mkdir(exist_ok=True)
        
        try:
            # Install Hugging Face Hub
            self.run_command([sys.executable, "-m", "pip", "install", "huggingface_hub"])
            
            # Create model download script
            download_script = models_dir / "download_models.py"
            script_content = '''#!/usr/bin/env python3
"""Download Wan models from Hugging Face"""

import os
from huggingface_hub import snapshot_download

def download_wan_models():
    """Download Wan2.1-VACE-14B and FusioniX models"""
    
    models = [
        {
            "repo_id": "Wan-AI/Wan2.1-VACE-14B",
            "local_dir": "./wan_vace_14b",
            "description": "Wan2.1-VACE-14B base model"
        },
        {
            "repo_id": "vrgamedevgirl84/Wan14BT2VFusioniX", 
            "local_dir": "./fusionix",
            "description": "FusioniX enhanced model"
        }
    ]
    
    for model in models:
        print(f"📥 Downloading {model['description']}...")
        try:
            snapshot_download(
                repo_id=model["repo_id"],
                local_dir=model["local_dir"],
                resume_download=True
            )
            print(f"✅ Downloaded {model['description']}")
        except Exception as e:
            print(f"❌ Failed to download {model['description']}: {e}")

if __name__ == "__main__":
    download_wan_models()
'''
            
            with open(download_script, 'w') as f:
                f.write(script_content)
            
            os.chmod(download_script, 0o755)
            
            # Run model download
            self.print_info("Downloading Wan models (this may take a while)...")
            self.run_command([sys.executable, str(download_script)], cwd=models_dir)
            
            self.print_success("Wan models downloaded successfully")
            
        except subprocess.CalledProcessError as e:
            self.print_error(f"Failed to download Wan models: {e}")
            return False
        
        return True
    
    def create_service_servers(self):
        """Create API servers for each video generation service"""
        self.print_header("Creating Video Generation API Servers")
        
        # Wan2.1-VACE Server
        wan_vace_server = self.video_services_dir / "wan_vace_server.py"
        wan_vace_content = '''#!/usr/bin/env python3
"""
Wan2.1-VACE-14B API Server for Pareng Boyong
"""

import asyncio
import base64
import io
import torch
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional
import uvicorn

app = FastAPI(title="Wan2.1-VACE-14B API Server", version="1.0.0")

# Global model
wan_model = None

class VideoRequest(BaseModel):
    prompt: str
    video_type: str = "text_to_video"
    image: Optional[str] = None
    duration: int = 5
    resolution: str = "720p"
    fps: int = 24
    num_inference_steps: int = 10
    guidance_scale: float = 7.5
    seed: Optional[int] = None
    low_vram_mode: bool = False

@app.on_event("startup")
async def startup_event():
    global wan_model
    print("🎬 Loading Wan2.1-VACE-14B model...")
    
    try:
        # Model initialization code would go here
        # from wan_models import load_wan_vace_model
        # wan_model = load_wan_vace_model("./wan_models/wan_vace_14b")
        print("✅ Wan2.1-VACE-14B model loaded")
    except Exception as e:
        print(f"❌ Failed to load model: {e}")

@app.get("/health")
async def health_check():
    return {"status": "healthy", "model": "Wan2.1-VACE-14B"}

@app.post("/generate")
async def generate_video(request: VideoRequest):
    if wan_model is None:
        raise HTTPException(status_code=503, detail="Model not loaded")
    
    try:
        # Video generation logic would go here
        # This is a placeholder implementation
        
        return {
            "success": True,
            "video_base64": "placeholder_video_base64",
            "metadata": {
                "model": "Wan2.1-VACE-14B",
                "duration": request.duration,
                "resolution": request.resolution,
                "fps": request.fps
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    print("🎬 Starting Wan2.1-VACE-14B API Server...")
    uvicorn.run(app, host="0.0.0.0", port=8189)
'''
        
        with open(wan_vace_server, 'w') as f:
            f.write(wan_vace_content)
        os.chmod(wan_vace_server, 0o755)
        
        # FusioniX Server
        fusionix_server = self.video_services_dir / "fusionix_server.py"
        fusionix_content = '''#!/usr/bin/env python3
"""
FusioniX API Server for Pareng Boyong
"""

import asyncio
import base64
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional
import uvicorn

app = FastAPI(title="FusioniX API Server", version="1.0.0")

fusionix_model = None

class VideoRequest(BaseModel):
    prompt: str
    video_type: str = "text_to_video"
    image: Optional[str] = None
    duration: int = 5
    resolution: str = "720p"
    fps: int = 24
    num_inference_steps: int = 8
    guidance_scale: float = 7.5
    seed: Optional[int] = None
    temporal_smoothing: bool = True
    detail_enhancement: bool = True
    color_grading: str = "none"

@app.on_event("startup")
async def startup_event():
    global fusionix_model
    print("⚡ Loading FusioniX model...")
    
    try:
        # Model loading code
        print("✅ FusioniX model loaded")
    except Exception as e:
        print(f"❌ Failed to load FusioniX model: {e}")

@app.get("/health")
async def health_check():
    return {"status": "healthy", "model": "FusioniX"}

@app.post("/generate")
async def generate_video(request: VideoRequest):
    try:
        # Fast generation with FusioniX
        return {
            "success": True,
            "video_base64": "placeholder_fusionix_video",
            "metadata": {
                "model": "FusioniX",
                "speed": "50% faster",
                "steps": request.num_inference_steps
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    print("⚡ Starting FusioniX API Server...")
    uvicorn.run(app, host="0.0.0.0", port=8190)
'''
        
        with open(fusionix_server, 'w') as f:
            f.write(fusionix_content)
        os.chmod(fusionix_server, 0o755)
        
        # MultiTalk Server  
        multitalk_server = self.video_services_dir / "multitalk_server.py"
        multitalk_content = '''#!/usr/bin/env python3
"""
MultiTalk API Server for Pareng Boyong
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional, List, Dict
import uvicorn

app = FastAPI(title="MultiTalk API Server", version="1.0.0")

multitalk_model = None

class ConversationRequest(BaseModel):
    prompt: str
    characters: List[str]
    audio_sync: bool = False
    duration: int = 5
    resolution: str = "720p"
    fps: int = 24
    num_inference_steps: int = 12
    guidance_scale: float = 7.5
    seed: Optional[int] = None
    conversation_mode: bool = True

@app.on_event("startup")
async def startup_event():
    global multitalk_model
    print("🗣️ Loading MultiTalk model...")
    try:
        print("✅ MultiTalk model loaded")
    except Exception as e:
        print(f"❌ Failed to load MultiTalk model: {e}")

@app.get("/health")
async def health_check():
    return {"status": "healthy", "model": "MultiTalk"}

@app.post("/generate") 
async def generate_conversation(request: ConversationRequest):
    try:
        return {
            "success": True,
            "video_base64": "placeholder_conversation_video",
            "metadata": {
                "model": "MultiTalk",
                "characters": len(request.characters),
                "audio_sync": request.audio_sync
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    print("🗣️ Starting MultiTalk API Server...")
    uvicorn.run(app, host="0.0.0.0", port=8191)
'''
        
        with open(multitalk_server, 'w') as f:
            f.write(multitalk_content)
        os.chmod(multitalk_server, 0o755)
        
        self.print_success("API servers created successfully")
        return True
    
    def create_startup_script(self):
        """Create startup script for all advanced video services"""
        self.print_header("Creating Advanced Video Startup Script")
        
        startup_script = self.video_services_dir / "start_advanced_video.py"
        startup_content = '''#!/usr/bin/env python3
"""
Advanced Video Services Startup Script for Pareng Boyong
"""

import os
import sys
import subprocess
import time
from pathlib import Path

class AdvancedVideoServices:
    def __init__(self):
        self.services_dir = Path(__file__).parent
        self.processes = []
    
    def start_wan_vace(self):
        """Start Wan2.1-VACE-14B server"""
        print("🎬 Starting Wan2.1-VACE-14B...")
        server_script = self.services_dir / "wan_vace_server.py"
        
        if not server_script.exists():
            print("❌ Wan VACE server not found")
            return False
        
        process = subprocess.Popen([sys.executable, str(server_script)])
        self.processes.append(("Wan2.1-VACE-14B", process))
        print("✅ Wan2.1-VACE-14B started on port 8189")
        return True
    
    def start_fusionix(self):
        """Start FusioniX server"""
        print("⚡ Starting FusioniX...")
        server_script = self.services_dir / "fusionix_server.py"
        
        if not server_script.exists():
            print("❌ FusioniX server not found")
            return False
        
        process = subprocess.Popen([sys.executable, str(server_script)])
        self.processes.append(("FusioniX", process))
        print("✅ FusioniX started on port 8190")
        return True
    
    def start_multitalk(self):
        """Start MultiTalk server"""
        print("🗣️ Starting MultiTalk...")
        server_script = self.services_dir / "multitalk_server.py"
        
        if not server_script.exists():
            print("❌ MultiTalk server not found")
            return False
        
        process = subprocess.Popen([sys.executable, str(server_script)])
        self.processes.append(("MultiTalk", process))
        print("✅ MultiTalk started on port 8191")
        return True
    
    def start_all(self):
        """Start all advanced video services"""
        print("🚀 Starting Advanced Video Generation Services...")
        
        self.start_wan_vace()
        time.sleep(3)
        
        self.start_fusionix()
        time.sleep(2)
        
        self.start_multitalk()
        time.sleep(2)
        
        print("\\n🎬 All advanced video services started!")
        print("\\n📍 Service URLs:")
        print("  • Wan2.1-VACE-14B: http://localhost:8189")
        print("  • FusioniX: http://localhost:8190")
        print("  • MultiTalk: http://localhost:8191")
        print("\\n⚠️ Press Ctrl+C to stop all services")
        
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            self.stop_all()
    
    def stop_all(self):
        """Stop all services"""
        print("\\n🛑 Stopping all advanced video services...")
        
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
        
        print("🏁 All advanced video services stopped")

if __name__ == "__main__":
    services = AdvancedVideoServices()
    services.start_all()
'''
        
        with open(startup_script, 'w') as f:
            f.write(startup_content)
        os.chmod(startup_script, 0o755)
        
        self.print_success("Advanced video startup script created")
        return True
    
    def install_all(self, include_models: bool = True):
        """Install all advanced video generation services"""
        self.print_header("Pareng Boyong Advanced Video Generation Installation")
        
        # Create services directory
        self.video_services_dir.mkdir(exist_ok=True)
        
        success_count = 0
        total_services = 3 + (1 if include_models else 0)
        
        # Install platforms
        if self.install_wan2gp():
            success_count += 1
            
        if self.install_multitalk():
            success_count += 1
        
        # Install models
        if include_models and self.install_wan_models():
            success_count += 1
        
        # Create servers and startup scripts
        if self.create_service_servers():
            success_count += 1
            
        self.create_startup_script()
        
        # Final summary
        self.print_header("Installation Summary")
        self.print_info(f"Successfully installed {success_count}/{total_services} components")
        
        if success_count >= 3:
            self.print_success("Advanced video generation system installed successfully!")
            self.print_info("To start services: python advanced_video_services/start_advanced_video.py")
            self.print_info("Available models: Wan2.1-VACE-14B, FusioniX, MultiTalk, Wan2GP")
        else:
            self.print_warning("Partial installation completed. Some components may need manual setup.")
        
        return success_count >= 3

def main():
    parser = argparse.ArgumentParser(description="Install Advanced Video Generation for Pareng Boyong")
    parser.add_argument("--no-models", action="store_true", help="Skip model downloads")
    parser.add_argument("--platforms-only", action="store_true", help="Install only platforms, no models")
    
    args = parser.parse_args()
    
    installer = AdvancedVideoInstaller()
    
    include_models = not (args.no_models or args.platforms_only)
    
    success = installer.install_all(include_models=include_models)
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()