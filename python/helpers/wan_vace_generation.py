"""
Wan2.1-VACE-14B Video Generation Helper
Integrates with the Wan2.1-VACE-14B model for high-quality video generation
"""

import asyncio
import base64
import json
import requests
from typing import Optional, Dict, Any
from python.helpers.print_style import PrintStyle

class WanVACEGenerator:
    def __init__(self):
        self.base_url = "http://localhost:8189"  # Wan2.1-VACE service port
        self.model_loaded = False
        
    async def initialize_model(self) -> bool:
        """Initialize the Wan2.1-VACE-14B model"""
        try:
            # Check if service is running
            response = requests.get(f"{self.base_url}/health", timeout=5)
            if response.status_code == 200:
                self.model_loaded = True
                return True
        except Exception as e:
            PrintStyle.warning(f"Wan2.1-VACE service not available: {e}")
        return False
        
    async def generate_video(
        self,
        prompt: str,
        video_type: str = "text_to_video",
        image_input: Optional[str] = None,
        duration: int = 5,
        resolution: str = "720p",
        fps: int = 24,
        sampling_steps: int = 10,
        guidance_scale: float = 7.5,
        seed: Optional[int] = None,
        low_vram: bool = False
    ) -> Optional[str]:
        """Generate video using Wan2.1-VACE-14B model"""
        
        if not await self.initialize_model():
            return None
            
        try:
            # Prepare generation parameters
            params = {
                "prompt": prompt,
                "video_type": video_type,
                "duration": duration,
                "resolution": resolution,
                "fps": fps,
                "num_inference_steps": sampling_steps,
                "guidance_scale": guidance_scale,
                "low_vram_mode": low_vram
            }
            
            if image_input:
                params["image"] = image_input
                
            if seed is not None:
                params["seed"] = seed
                
            # Generate video
            PrintStyle(font_color="blue", padding=False).print(f"🎬 Generating with Wan2.1-VACE-14B: {resolution} @ {fps}fps")
            
            response = requests.post(
                f"{self.base_url}/generate",
                json=params,
                timeout=300  # 5 minutes timeout for video generation
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get("success"):
                    return result.get("video_base64")
                else:
                    PrintStyle.error(f"Generation failed: {result.get('error', 'Unknown error')}")
            else:
                PrintStyle.error(f"HTTP {response.status_code}: {response.text}")
                
        except Exception as e:
            PrintStyle.error(f"Wan2.1-VACE generation error: {e}")
            
        return None

# Global generator instance
_wan_vace_generator = WanVACEGenerator()

async def generate_wan_video(
    prompt: str,
    video_type: str = "text_to_video",
    image_input: Optional[str] = None,
    duration: int = 5,
    resolution: str = "720p",
    fps: int = 24,
    sampling_steps: int = 10,
    guidance_scale: float = 7.5,
    seed: Optional[int] = None,
    low_vram: bool = False
) -> Optional[str]:
    """Generate video using Wan2.1-VACE-14B model"""
    
    return await _wan_vace_generator.generate_video(
        prompt=prompt,
        video_type=video_type,
        image_input=image_input,
        duration=duration,
        resolution=resolution,
        fps=fps,
        sampling_steps=sampling_steps,
        guidance_scale=guidance_scale,
        seed=seed,
        low_vram=low_vram
    )

def get_wan_vace_capabilities() -> Dict[str, Any]:
    """Get Wan2.1-VACE-14B model capabilities"""
    return {
        "name": "Wan2.1-VACE-14B",
        "type": "text_to_video",
        "supported_types": ["text_to_video", "image_to_video"],
        "max_duration": 15,
        "resolutions": ["480p", "720p"],
        "fps_options": [8, 12, 16, 24],
        "features": [
            "High-quality generation",
            "Multilingual support",
            "Low VRAM optimization",
            "Advanced 3D VAE",
            "Flow Matching architecture"
        ],
        "hardware_requirements": {
            "min_vram": "8GB",
            "recommended_vram": "16GB",
            "gpu_support": ["RTX 30XX", "RTX 40XX", "A100", "H100"]
        }
    }