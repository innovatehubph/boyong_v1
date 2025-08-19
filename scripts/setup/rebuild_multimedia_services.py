#!/usr/bin/env python3
"""
Pareng Boyong - Rebuild Multimedia Services
Ensures multimedia services are properly configured after Agent Zero updates.
"""

import os
import sys
import subprocess
import json
from pathlib import Path

def rebuild_multimedia_services():
    """Rebuild multimedia services after update."""
    print("🎨 Rebuilding Pareng Boyong multimedia services...")
    
    try:
        # Ensure multimedia directories exist
        multimedia_dirs = [
            "services/multimodal",
            "services/tts", 
            "services/localai",
            "multimodal_services",
            "pareng_boyong_deliverables/images",
            "pareng_boyong_deliverables/videos",
            "pareng_boyong_deliverables/audio"
        ]
        
        for dir_path in multimedia_dirs:
            Path(dir_path).mkdir(parents=True, exist_ok=True)
        
        # Regenerate multimedia configuration
        multimedia_config = {
            "image_generation": {
                "enabled": True,
                "default_model": "flux.1",
                "providers": ["pollinations", "comfyui"],
                "output_dir": "pareng_boyong_deliverables/images"
            },
            "video_generation": {
                "enabled": True,
                "models": ["wan_vace_14b", "fusionix", "multitalk", "wan2gp"],
                "output_dir": "pareng_boyong_deliverables/videos"
            },
            "audio_generation": {
                "enabled": True,
                "tts_providers": ["elevenlabs", "toucan", "bark"],
                "music_providers": ["audiocraft"],
                "output_dir": "pareng_boyong_deliverables/audio"
            }
        }
        
        with open("config/multimedia_config.json", "w") as f:
            json.dump(multimedia_config, f, indent=2)
        
        # Rebuild Docker services if needed
        docker_compose_files = [
            "config/docker/docker-compose.multimodal-all.yml",
            "config/docker/docker-compose.multimodal-new.yml"
        ]
        
        for compose_file in docker_compose_files:
            if Path(compose_file).exists():
                print(f"🐳 Rebuilding Docker services: {compose_file}")
                try:
                    subprocess.run([
                        "docker-compose", "-f", compose_file, "build"
                    ], check=True, capture_output=True)
                except subprocess.CalledProcessError:
                    print(f"⚠️ Docker rebuild failed for {compose_file}")
        
        # Validate multimedia tools
        multimedia_tools = [
            "python/tools/multimedia_generator.py",
            "python/tools/advanced_video_generator.py", 
            "python/tools/audio_studio.py",
            "python/tools/image_gen.py"
        ]
        
        missing_tools = []
        for tool in multimedia_tools:
            if not Path(tool).exists():
                missing_tools.append(tool)
        
        if missing_tools:
            print(f"⚠️ Missing multimedia tools: {missing_tools}")
            print("🔄 These will need to be restored from backup")
        
        print("✅ Multimedia services rebuilt successfully")
        return True
        
    except Exception as e:
        print(f"❌ Multimedia rebuild failed: {e}")
        return False

if __name__ == "__main__":
    success = rebuild_multimedia_services()
    sys.exit(0 if success else 1)