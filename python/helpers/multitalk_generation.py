"""
MultiTalk Conversational Video Generation Helper
Integrates with MultiTalk for generating multi-person conversational videos with lip-sync
"""

import asyncio
import base64
import json
import requests
from typing import Optional, Dict, Any, List
from python.helpers.print_style import PrintStyle

class MultiTalkGenerator:
    def __init__(self):
        self.base_url = "http://localhost:8191"  # MultiTalk service port
        self.model_loaded = False
        
    async def initialize_model(self) -> bool:
        """Initialize the MultiTalk model"""
        try:
            # Check if service is running
            response = requests.get(f"{self.base_url}/health", timeout=5)
            if response.status_code == 200:
                self.model_loaded = True
                return True
        except Exception as e:
            PrintStyle.warning(f"MultiTalk service not available: {e}")
        return False
        
    async def generate_conversation_video(
        self,
        prompt: str,
        characters: List[str] = None,
        audio_sync: bool = False,
        duration: int = 5,
        resolution: str = "720p",
        fps: int = 24,
        sampling_steps: int = 12,
        guidance_scale: float = 7.5,
        seed: Optional[int] = None,
        character_styles: Optional[Dict[str, str]] = None,
        conversation_flow: Optional[List[Dict[str, str]]] = None
    ) -> Optional[str]:
        """Generate conversational video using MultiTalk"""
        
        if not await self.initialize_model():
            return None
            
        try:
            # Prepare conversation parameters
            params = {
                "prompt": prompt,
                "characters": characters or ["Speaker 1", "Speaker 2"],
                "audio_sync": audio_sync,
                "duration": duration,
                "resolution": resolution,
                "fps": fps,
                "num_inference_steps": sampling_steps,
                "guidance_scale": guidance_scale,
                "conversation_mode": True
            }
            
            if character_styles:
                params["character_styles"] = character_styles
                
            if conversation_flow:
                params["conversation_flow"] = conversation_flow
                
            if seed is not None:
                params["seed"] = seed
                
            # Generate conversational video
            PrintStyle(font_color="green", padding=False).print(f"🗣️ Generating conversation with MultiTalk: {len(characters or [])} characters")
            
            response = requests.post(
                f"{self.base_url}/generate",
                json=params,
                timeout=240  # 4 minutes for conversation generation
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get("success"):
                    PrintStyle.success("MultiTalk conversation generated successfully!")
                    return result.get("video_base64")
                else:
                    PrintStyle.error(f"Generation failed: {result.get('error', 'Unknown error')}")
            else:
                PrintStyle.error(f"HTTP {response.status_code}: {response.text}")
                
        except Exception as e:
            PrintStyle.error(f"MultiTalk generation error: {e}")
            
        return None
        
    async def generate_with_tts_integration(
        self,
        dialogue_script: List[Dict[str, str]],
        characters: List[str],
        character_voices: Optional[Dict[str, str]] = None,
        duration: int = 10,
        resolution: str = "720p",
        fps: int = 24
    ) -> Optional[str]:
        """Generate conversational video with TTS integration"""
        
        if not await self.initialize_model():
            return None
            
        try:
            # Prepare TTS-integrated parameters
            params = {
                "dialogue_script": dialogue_script,
                "characters": characters,
                "character_voices": character_voices or {},
                "duration": duration,
                "resolution": resolution,
                "fps": fps,
                "tts_integration": True,
                "lip_sync": True
            }
            
            PrintStyle(font_color="purple", padding=False).print(f"🎭 Generating TTS-integrated conversation: {len(dialogue_script)} dialogue turns")
            
            response = requests.post(
                f"{self.base_url}/generate_with_tts",
                json=params,
                timeout=300  # 5 minutes for TTS integration
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get("success"):
                    return result.get("video_base64")
                else:
                    PrintStyle.error(f"TTS generation failed: {result.get('error', 'Unknown error')}")
            else:
                PrintStyle.error(f"HTTP {response.status_code}: {response.text}")
                
        except Exception as e:
            PrintStyle.error(f"MultiTalk TTS integration error: {e}")
            
        return None

# Global generator instance
_multitalk_generator = MultiTalkGenerator()

async def generate_conversation_video(
    prompt: str,
    characters: List[str] = None,
    audio_sync: bool = False,
    duration: int = 5,
    resolution: str = "720p",
    fps: int = 24,
    sampling_steps: int = 12,
    guidance_scale: float = 7.5,
    seed: Optional[int] = None
) -> Optional[str]:
    """Generate conversational video using MultiTalk"""
    
    return await _multitalk_generator.generate_conversation_video(
        prompt=prompt,
        characters=characters,
        audio_sync=audio_sync,
        duration=duration,
        resolution=resolution,
        fps=fps,
        sampling_steps=sampling_steps,
        guidance_scale=guidance_scale,
        seed=seed
    )

async def generate_dialogue_video(
    dialogue_script: List[Dict[str, str]],
    characters: List[str],
    character_voices: Optional[Dict[str, str]] = None,
    duration: int = 10,
    resolution: str = "720p",
    fps: int = 24
) -> Optional[str]:
    """Generate video from dialogue script with TTS integration"""
    
    return await _multitalk_generator.generate_with_tts_integration(
        dialogue_script=dialogue_script,
        characters=characters,
        character_voices=character_voices,
        duration=duration,
        resolution=resolution,
        fps=fps
    )

def get_multitalk_capabilities() -> Dict[str, Any]:
    """Get MultiTalk model capabilities"""
    return {
        "name": "MultiTalk",
        "type": "conversational_video",
        "supported_types": ["conversation", "dialogue", "character_animation"],
        "max_duration": 15,
        "resolutions": ["480p", "720p"],
        "fps_options": [8, 12, 16, 24],
        "features": [
            "Multi-person conversations",
            "Lip synchronization",
            "Audio-driven animation",
            "Character customization",
            "TTS integration",
            "Cartoon and realistic styles",
            "Interactive character control",
            "Singing scenarios support"
        ],
        "character_support": {
            "max_characters": 4,
            "voice_cloning": True,
            "expression_control": True,
            "pose_customization": True
        },
        "integrations": [
            "ToucanTTS",
            "ElevenLabs",
            "ComfyUI",
            "Custom TTS systems"
        ]
    }