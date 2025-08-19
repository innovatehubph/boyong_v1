"""
Audio Generation Helper for Pareng Boyong  
Supports AudioCraft/MusicGen, Bark, and enhanced TTS
"""

import asyncio
import base64
import logging
from typing import Optional, Dict, Any, List
import aiohttp
import json
import tempfile
import os
import subprocess
from pathlib import Path

logger = logging.getLogger(__name__)

class AudioGenerator:
    def __init__(self):
        self.musicgen_available = False
        self.bark_available = False
        self.audiocraft_url = None
        self.bark_url = None
        
    async def initialize(self):
        """Initialize and detect available audio generation services"""
        
        # Check for AudioCraft/MusicGen API
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get('http://localhost:8000/health', timeout=5) as resp:
                    if resp.status == 200:
                        self.musicgen_available = True
                        self.audiocraft_url = 'http://localhost:8000'
                        logger.info("✅ AudioCraft/MusicGen available")
        except:
            logger.info("❌ AudioCraft/MusicGen not available")
            
        # Check for Bark API
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get('http://localhost:8001/health', timeout=5) as resp:
                    if resp.status == 200:
                        self.bark_available = True
                        self.bark_url = 'http://localhost:8001'
                        logger.info("✅ Bark TTS available")
        except:
            logger.info("❌ Bark TTS not available")
    
    async def generate_music(
        self, 
        prompt: str, 
        duration: int = 10,  # seconds
        model: str = "facebook/musicgen-medium",
        top_k: int = 250,
        top_p: float = 0.0,
        temperature: float = 1.0
    ) -> Optional[str]:
        """
        Generate music using MusicGen
        Returns base64 encoded audio or None if failed
        """
        
        if not self.musicgen_available:
            logger.error("MusicGen not available")
            return None
            
        try:
            payload = {
                "prompt": prompt,
                "duration": duration,
                "model": model,
                "top_k": top_k,
                "top_p": top_p,
                "temperature": temperature
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(f'{self.audiocraft_url}/generate/music', json=payload, timeout=120) as resp:
                    if resp.status == 200:
                        result = await resp.json()
                        return result.get('audio_base64')
                    else:
                        error = await resp.text()
                        logger.error(f"MusicGen API error: {error}")
                        return None
                        
        except Exception as e:
            logger.error(f"Music generation failed: {e}")
            return None
    
    async def generate_sound_effect(
        self, 
        prompt: str, 
        duration: int = 5
    ) -> Optional[str]:
        """
        Generate sound effects using AudioGen
        """
        
        if not self.musicgen_available:
            logger.error("AudioGen not available")
            return None
            
        try:
            payload = {
                "prompt": prompt,
                "duration": duration,
                "model": "facebook/audiogen-medium"
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(f'{self.audiocraft_url}/generate/audio', json=payload, timeout=60) as resp:
                    if resp.status == 200:
                        result = await resp.json()
                        return result.get('audio_base64')
                    else:
                        error = await resp.text()
                        logger.error(f"AudioGen API error: {error}")
                        return None
                        
        except Exception as e:
            logger.error(f"Sound effect generation failed: {e}")
            return None
    
    async def generate_speech_bark(
        self, 
        text: str, 
        voice_preset: str = "v2/en_speaker_6",
        temperature: float = 0.7,
        silence_duration: float = 0.25
    ) -> Optional[str]:
        """
        Generate speech using Bark TTS with emotion and music capabilities
        """
        
        if not self.bark_available:
            logger.error("Bark TTS not available")
            return None
            
        try:
            payload = {
                "text": text,
                "voice_preset": voice_preset,
                "temperature": temperature,
                "silence_duration": silence_duration
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(f'{self.bark_url}/generate', json=payload, timeout=60) as resp:
                    if resp.status == 200:
                        result = await resp.json()
                        return result.get('audio_base64')
                    else:
                        error = await resp.text()
                        logger.error(f"Bark TTS API error: {error}")
                        return None
                        
        except Exception as e:
            logger.error(f"Bark speech generation failed: {e}")
            return None
    
    async def get_available_voices(self) -> List[str]:
        """Get list of available Bark voice presets"""
        
        if not self.bark_available:
            return []
            
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f'{self.bark_url}/voices') as resp:
                    if resp.status == 200:
                        result = await resp.json()
                        return result.get('voices', [])
        except:
            pass
            
        # Default voices if API not available
        return [
            "v2/en_speaker_0", "v2/en_speaker_1", "v2/en_speaker_2", 
            "v2/en_speaker_3", "v2/en_speaker_4", "v2/en_speaker_5",
            "v2/en_speaker_6", "v2/en_speaker_7", "v2/en_speaker_8", "v2/en_speaker_9"
        ]
    
    async def generate_ambient_sound(
        self, 
        description: str,
        duration: int = 30,
        fade_in: bool = True,
        fade_out: bool = True
    ) -> Optional[str]:
        """
        Generate ambient sounds/backgrounds using AudioGen
        """
        
        # Enhance prompt for ambient sounds
        ambient_prompt = f"ambient {description}, looping background sound, peaceful, continuous"
        
        result = await self.generate_sound_effect(ambient_prompt, duration)
        
        if result and (fade_in or fade_out):
            # Apply fade effects using FFmpeg if available
            try:
                result = await self._apply_audio_effects(result, fade_in, fade_out)
            except:
                pass  # Return without effects if FFmpeg not available
                
        return result
    
    async def _apply_audio_effects(self, audio_base64: str, fade_in: bool, fade_out: bool) -> str:
        """Apply audio effects using FFmpeg"""
        
        # Decode base64 audio
        audio_data = base64.b64decode(audio_base64)
        
        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as input_file:
            input_file.write(audio_data)
            input_path = input_file.name
            
        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as output_file:
            output_path = output_file.name
            
        try:
            # Build FFmpeg command
            cmd = ['ffmpeg', '-i', input_path, '-y']
            
            filters = []
            if fade_in:
                filters.append('afade=t=in:d=2')
            if fade_out:
                filters.append('afade=t=out:d=2')
                
            if filters:
                cmd.extend(['-af', ','.join(filters)])
                
            cmd.append(output_path)
            
            # Run FFmpeg
            subprocess.run(cmd, check=True, capture_output=True)
            
            # Read processed audio
            with open(output_path, 'rb') as f:
                processed_audio = f.read()
                
            return base64.b64encode(processed_audio).decode('utf-8')
            
        finally:
            # Clean up temp files
            for path in [input_path, output_path]:
                try:
                    os.unlink(path)
                except:
                    pass
    
    async def create_audio_story(
        self, 
        script_segments: List[Dict[str, str]], 
        background_music: Optional[str] = None
    ) -> Optional[str]:
        """
        Create an audio story with multiple voices and background music
        
        script_segments: [{"text": "Hello", "voice": "v2/en_speaker_1", "type": "speech"}, ...]
        background_music: Description for background music
        """
        
        if not self.bark_available:
            logger.error("Bark TTS not available for audio story creation")
            return None
            
        try:
            audio_segments = []
            
            # Generate background music if requested
            bg_music_base64 = None
            if background_music:
                bg_music_base64 = await self.generate_music(
                    f"soft instrumental background music, {background_music}", 
                    duration=60
                )
            
            # Generate speech segments
            for segment in script_segments:
                if segment.get('type') == 'speech':
                    audio = await self.generate_speech_bark(
                        segment['text'], 
                        segment.get('voice', 'v2/en_speaker_0')
                    )
                    if audio:
                        audio_segments.append({
                            'audio': audio,
                            'type': 'speech'
                        })
                elif segment.get('type') == 'music':
                    audio = await self.generate_music(segment['text'], duration=10)
                    if audio:
                        audio_segments.append({
                            'audio': audio,
                            'type': 'music'
                        })
                elif segment.get('type') == 'sound':
                    audio = await self.generate_sound_effect(segment['text'], duration=5)
                    if audio:
                        audio_segments.append({
                            'audio': audio,
                            'type': 'sound'
                        })
            
            # For now, return the first speech segment
            # TODO: Implement proper audio mixing with FFmpeg
            if audio_segments:
                return audio_segments[0]['audio']
                
        except Exception as e:
            logger.error(f"Audio story creation failed: {e}")
            
        return None

# Global instance
audio_generator = AudioGenerator()

async def generate_music(prompt: str, **kwargs) -> Optional[str]:
    """Convenience function for music generation"""
    if not audio_generator.musicgen_available:
        await audio_generator.initialize()
    
    return await audio_generator.generate_music(prompt, **kwargs)

async def generate_sound_effect(prompt: str, **kwargs) -> Optional[str]:
    """Convenience function for sound effect generation"""
    if not audio_generator.musicgen_available:
        await audio_generator.initialize()
    
    return await audio_generator.generate_sound_effect(prompt, **kwargs)

async def generate_speech_bark(text: str, **kwargs) -> Optional[str]:
    """Convenience function for Bark speech generation"""
    if not audio_generator.bark_available:
        await audio_generator.initialize()
    
    return await audio_generator.generate_speech_bark(text, **kwargs)

# Test function
async def test_generation():
    """Test audio generation capabilities"""
    await audio_generator.initialize()
    
    if audio_generator.musicgen_available:
        # Test music generation
        music_result = await generate_music("happy upbeat melody", duration=5)
        if music_result:
            print("✅ Music generation test successful!")
        else:
            print("❌ Music generation test failed")
    
    if audio_generator.bark_available:
        # Test speech generation
        speech_result = await generate_speech_bark("Hello, this is a test of Bark TTS!")
        if speech_result:
            print("✅ Bark TTS test successful!")
        else:
            print("❌ Bark TTS test failed")
    
    if not audio_generator.musicgen_available and not audio_generator.bark_available:
        print("❌ No audio generation services available")
        return False
        
    return True

if __name__ == "__main__":
    asyncio.run(test_generation())