"""
Wan2GP Video Generation Helper
Integrates with Wan2GP platform for low-VRAM, accessible video generation
"""

import asyncio
import base64
import json
import requests
from typing import Optional, Dict, Any
from python.helpers.print_style import PrintStyle

class Wan2GPGenerator:
    def __init__(self):
        self.base_url = "http://localhost:8192"  # Wan2GP service port
        self.model_loaded = False
        
    async def initialize_model(self) -> bool:
        """Initialize the Wan2GP platform"""
        try:
            # Check if service is running
            response = requests.get(f"{self.base_url}/health", timeout=5)
            if response.status_code == 200:
                self.model_loaded = True
                return True
        except Exception as e:
            PrintStyle.warning(f"Wan2GP service not available: {e}")
        return False
        
    async def generate_video(
        self,
        prompt: str,
        video_type: str = "text_to_video",
        image_input: Optional[str] = None,
        duration: int = 5,
        resolution: str = "720p",
        fps: int = 24,
        low_vram: bool = True,
        sampling_steps: int = 15,
        guidance_scale: float = 7.5,
        seed: Optional[int] = None,
        model_variant: str = "wan",
        use_controlnet: bool = False,
        mask_editing: bool = False
    ) -> Optional[str]:
        """Generate video using Wan2GP platform"""
        
        if not await self.initialize_model():
            return None
            
        try:
            # Prepare generation parameters optimized for Wan2GP
            params = {
                "prompt": prompt,
                "video_type": video_type,
                "duration": duration,
                "resolution": resolution,
                "fps": fps,
                "low_vram_mode": low_vram,
                "num_inference_steps": sampling_steps,
                "guidance_scale": guidance_scale,
                "model_variant": model_variant,  # wan, hunyuan, ltv
                "use_controlnet": use_controlnet,
                "mask_editing": mask_editing
            }
            
            if image_input:
                params["image"] = image_input
                
            if seed is not None:
                params["seed"] = seed
                
            # Generate video with Wan2GP optimization
            PrintStyle(font_color="yellow", padding=False).print(f"⚙️ Generating with Wan2GP ({model_variant}): Low-VRAM optimized")
            
            response = requests.post(
                f"{self.base_url}/generate",
                json=params,
                timeout=300  # 5 minutes timeout
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get("success"):
                    PrintStyle.success("Wan2GP generation completed successfully!")
                    return result.get("video_base64")
                else:
                    PrintStyle.error(f"Generation failed: {result.get('error', 'Unknown error')}")
            else:
                PrintStyle.error(f"HTTP {response.status_code}: {response.text}")
                
        except Exception as e:
            PrintStyle.error(f"Wan2GP generation error: {e}")
            
        return None
        
    async def generate_with_advanced_features(
        self,
        prompt: str,
        video_type: str = "text_to_video",
        image_input: Optional[str] = None,
        duration: int = 5,
        resolution: str = "720p",
        fps: int = 24,
        pose_control: Optional[str] = None,
        depth_control: Optional[str] = None,
        flow_control: Optional[str] = None,
        lora_weights: Optional[Dict[str, float]] = None,
        post_processing: bool = True
    ) -> Optional[str]:
        """Generate video with advanced Wan2GP features"""
        
        if not await self.initialize_model():
            return None
            
        try:
            params = {
                "prompt": prompt,
                "video_type": video_type,
                "duration": duration,
                "resolution": resolution,
                "fps": fps,
                "advanced_mode": True,
                "post_processing": post_processing
            }
            
            if image_input:
                params["image"] = image_input
                
            if pose_control:
                params["pose_control"] = pose_control
                
            if depth_control:
                params["depth_control"] = depth_control
                
            if flow_control:
                params["flow_control"] = flow_control
                
            if lora_weights:
                params["lora_weights"] = lora_weights
                
            PrintStyle(font_color="orange", padding=False).print("🎛️ Advanced Wan2GP generation with ControlNet features")
            
            response = requests.post(
                f"{self.base_url}/generate_advanced",
                json=params,
                timeout=360  # 6 minutes for advanced features
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get("success"):
                    return result.get("video_base64")
                else:
                    PrintStyle.error(f"Advanced generation failed: {result.get('error', 'Unknown error')}")
            else:
                PrintStyle.error(f"HTTP {response.status_code}: {response.text}")
                
        except Exception as e:
            PrintStyle.error(f"Advanced Wan2GP generation error: {e}")
            
        return None

# Global generator instance
_wan2gp_generator = Wan2GPGenerator()

async def generate_wan2gp_video(
    prompt: str,
    video_type: str = "text_to_video",
    image_input: Optional[str] = None,
    duration: int = 5,
    resolution: str = "720p",
    fps: int = 24,
    low_vram: bool = True,
    sampling_steps: int = 15,
    guidance_scale: float = 7.5,
    seed: Optional[int] = None
) -> Optional[str]:
    """Generate video using Wan2GP platform"""
    
    return await _wan2gp_generator.generate_video(
        prompt=prompt,
        video_type=video_type,
        image_input=image_input,
        duration=duration,
        resolution=resolution,
        fps=fps,
        low_vram=low_vram,
        sampling_steps=sampling_steps,
        guidance_scale=guidance_scale,
        seed=seed
    )

async def generate_advanced_wan2gp_video(
    prompt: str,
    video_type: str = "text_to_video",
    image_input: Optional[str] = None,
    duration: int = 5,
    resolution: str = "720p",
    fps: int = 24,
    pose_control: Optional[str] = None,
    depth_control: Optional[str] = None,
    flow_control: Optional[str] = None,
    lora_weights: Optional[Dict[str, float]] = None
) -> Optional[str]:
    """Generate video with advanced Wan2GP features"""
    
    return await _wan2gp_generator.generate_with_advanced_features(
        prompt=prompt,
        video_type=video_type,
        image_input=image_input,
        duration=duration,
        resolution=resolution,
        fps=fps,
        pose_control=pose_control,
        depth_control=depth_control,
        flow_control=flow_control,
        lora_weights=lora_weights
    )

def get_wan2gp_capabilities() -> Dict[str, Any]:
    """Get Wan2GP platform capabilities"""
    return {
        "name": "Wan2GP",
        "type": "multi_model_platform",
        "supported_models": ["Wan", "Hunyuan Video", "LTV Video"],
        "supported_types": ["text_to_video", "image_to_video", "video_editing"],
        "max_duration": 10,
        "resolutions": ["480p", "720p"],
        "fps_options": [8, 12, 16, 24],
        "features": [
            "Low-VRAM optimization (6GB+)",
            "Multi-model support",
            "ControlNet integration",
            "LoRA customization",
            "Mask editing",
            "Pose/depth/flow control",
            "Advanced post-processing",
            "Sliding window generation",
            "Real-time statistics"
        ],
        "hardware_support": [
            "RTX 10XX series",
            "RTX 20XX series", 
            "RTX 30XX series",
            "RTX 40XX series",
            "Low-end GPUs"
        ],
        "optimization": {
            "min_vram": "6GB",
            "low_vram_techniques": "NAG implementation",
            "multi_gpu": True,
            "older_gpu_support": True
        }
    }