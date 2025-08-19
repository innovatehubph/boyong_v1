"""
Wan14BT2VFusioniX Video Generation Helper
Integrates with the enhanced FusioniX model for fast, cinematic video generation
"""

import asyncio
import base64
import json
import requests
from typing import Optional, Dict, Any
from python.helpers.print_style import PrintStyle

class FusioniXGenerator:
    def __init__(self):
        self.base_url = "http://localhost:8190"  # FusioniX service port
        self.model_loaded = False
        
    async def initialize_model(self) -> bool:
        """Initialize the FusioniX model"""
        try:
            # Check if service is running
            response = requests.get(f"{self.base_url}/health", timeout=5)
            if response.status_code == 200:
                self.model_loaded = True
                return True
        except Exception as e:
            PrintStyle.warning(f"FusioniX service not available: {e}")
        return False
        
    async def generate_video(
        self,
        prompt: str,
        video_type: str = "text_to_video",
        image_input: Optional[str] = None,
        duration: int = 5,
        resolution: str = "720p",
        fps: int = 24,
        sampling_steps: int = 8,  # Optimized for FusioniX
        guidance_scale: float = 7.5,
        seed: Optional[int] = None,
        temporal_smoothing: bool = True,
        detail_enhancement: bool = True,
        color_grading: str = "none"
    ) -> Optional[str]:
        """Generate video using FusioniX model for fast, cinematic results"""
        
        if not await self.initialize_model():
            return None
            
        try:
            # Prepare generation parameters optimized for FusioniX
            params = {
                "prompt": prompt,
                "video_type": video_type,
                "duration": duration,
                "resolution": resolution,
                "fps": fps,
                "num_inference_steps": sampling_steps,  # 6-10 steps optimal
                "guidance_scale": guidance_scale,
                "temporal_smoothing": temporal_smoothing,
                "detail_enhancement": detail_enhancement,
                "color_grading": color_grading
            }
            
            if image_input:
                params["image"] = image_input
                
            if seed is not None:
                params["seed"] = seed
                
            # Generate video with FusioniX optimization
            PrintStyle(font_color="cyan", padding=False).print(f"⚡ Fast generation with FusioniX: {resolution} @ {fps}fps ({sampling_steps} steps)")
            
            response = requests.post(
                f"{self.base_url}/generate",
                json=params,
                timeout=180  # Faster generation, shorter timeout
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get("success"):
                    PrintStyle.success("FusioniX generation completed in record time!")
                    return result.get("video_base64")
                else:
                    PrintStyle.error(f"Generation failed: {result.get('error', 'Unknown error')}")
            else:
                PrintStyle.error(f"HTTP {response.status_code}: {response.text}")
                
        except Exception as e:
            PrintStyle.error(f"FusioniX generation error: {e}")
            
        return None

# Global generator instance
_fusionix_generator = FusioniXGenerator()

async def generate_fusionix_video(
    prompt: str,
    video_type: str = "text_to_video",
    image_input: Optional[str] = None,
    duration: int = 5,
    resolution: str = "720p",
    fps: int = 24,
    sampling_steps: int = 8,
    guidance_scale: float = 7.5,
    seed: Optional[int] = None,
    temporal_smoothing: bool = True,
    detail_enhancement: bool = True,
    color_grading: str = "none"
) -> Optional[str]:
    """Generate video using FusioniX model"""
    
    return await _fusionix_generator.generate_video(
        prompt=prompt,
        video_type=video_type,
        image_input=image_input,
        duration=duration,
        resolution=resolution,
        fps=fps,
        sampling_steps=sampling_steps,
        guidance_scale=guidance_scale,
        seed=seed,
        temporal_smoothing=temporal_smoothing,
        detail_enhancement=detail_enhancement,
        color_grading=color_grading
    )

def get_fusionix_capabilities() -> Dict[str, Any]:
    """Get FusioniX model capabilities"""
    return {
        "name": "Wan14BT2VFusioniX",
        "type": "enhanced_text_to_video",
        "supported_types": ["text_to_video", "image_to_video", "cinematic"],
        "max_duration": 10,
        "resolutions": ["480p", "720p", "1080p"],
        "fps_options": [8, 12, 16, 24, 30],
        "features": [
            "50% faster rendering",
            "Cinematic motion quality",
            "Enhanced detail preservation",
            "6-10 step optimization",
            "Temporal smoothing",
            "Color grading options",
            "Motion stabilization"
        ],
        "fusion_components": [
            "CausVid (motion modeling)",
            "AccVideo (temporal alignment)", 
            "MoviiGen1.1 (cinematic smoothness)",
            "MPS Reward LoRA (detail tuning)"
        ],
        "optimization": {
            "optimal_steps": "8-10",
            "speed_improvement": "50%",
            "quality_level": "Professional"
        }
    }