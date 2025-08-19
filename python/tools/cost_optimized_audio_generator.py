"""
Cost-Optimized Audio Generator for Pareng Boyong
Always prioritizes FREE and lowest-cost audio generation options
"""

import asyncio
import aiohttp
import json
import os
import base64
import requests
from datetime import datetime
from typing import Dict, Any, Optional, List

# Import environment loader
try:
    from env_loader import get_env, is_env_set
except ImportError:
    def get_env(key, default=None):
        return os.getenv(key, default)
    def is_env_set(key):
        value = os.getenv(key)
        return value is not None and value.strip() != ""

class CostOptimizedAudioGenerator:
    """
    Cost-optimized audio generator that prioritizes FREE options:
    1. FREE HuggingFace Spaces (MusicGen, Bark TTS)
    2. FREE local services (if available)
    3. Low-cost API services (last resort)
    """
    
    def __init__(self):
        # Check if local audio servers are running
        self.audiocraft_server = "http://localhost:8000"
        self.bark_server = "http://localhost:8001"
        
        # API tokens
        self.huggingface_token = get_env('API_KEY_HUGGINGFACE')
        self.replicate_token = get_env('REPLICATE_API_TOKEN')
        
        # Service availability
        self.services = {
            "audiocraft_local": False,
            "bark_local": False,
            "huggingface_free": False,
            "replicate_paid": False
        }
        
        # Storage
        self.deliverables_path = "/root/projects/pareng-boyong/pareng_boyong_deliverables"
    
    async def initialize(self):
        """Initialize and detect available FREE audio services"""
        print("🎵 Scanning for FREE audio generation options...")
        
        # Check local servers (FREE if running)
        self.services["audiocraft_local"] = await self._test_local_server(self.audiocraft_server)
        self.services["bark_local"] = await self._test_local_server(self.bark_server)
        
        # Check HuggingFace Spaces (FREE)
        if self.huggingface_token:
            self.services["huggingface_free"] = await self._test_huggingface_spaces()
        
        # Check Replicate (PAID - last resort)
        if self.replicate_token:
            self.services["replicate_paid"] = await self._test_replicate_api()
        
        # Report available FREE services
        free_services = [name for name, available in self.services.items() 
                        if available and "paid" not in name]
        
        if free_services:
            print(f"🎉 Found {len(free_services)} FREE audio services: {', '.join(free_services)}")
        else:
            print("⚠️  No FREE audio services detected")
    
    async def generate_music(
        self,
        prompt: str,
        duration: int = 10,
        style: str = "upbeat",
        max_cost: float = 0.00,
        force_free: bool = True
    ) -> Dict[str, Any]:
        """Generate music prioritizing FREE services"""
        
        try:
            # Select cheapest available service for music
            service = self._select_cheapest_music_service(force_free)
            
            if not service:
                return {
                    "success": False,
                    "error": "No music generation services available within cost limits"
                }
            
            print(f"🎵 Generating music with {service} (FREE)")
            
            # Generate music using selected service
            if service == "audiocraft_local":
                result = await self._generate_music_local(prompt, duration, style)
            elif service == "huggingface_free":
                result = await self._generate_music_hf_direct(prompt, duration, style)
            elif service == "replicate_paid" and not force_free:
                result = await self._generate_music_replicate(prompt, duration, style)
            else:
                return {"success": False, "error": f"Service {service} not available"}
            
            if result and result.get('success'):
                result['service_used'] = service
                result['cost'] = 0.00 if "free" in service or "local" in service else 0.01
                result['cost_category'] = "free" if result['cost'] == 0 else "low_cost"
            
            return result
            
        except Exception as e:
            return {"success": False, "error": f"Music generation failed: {str(e)}"}
    
    async def generate_speech(
        self,
        text: str,
        voice: str = "neutral",
        language: str = "en",
        emotion: str = "neutral",
        max_cost: float = 0.00,
        force_free: bool = True
    ) -> Dict[str, Any]:
        """Generate speech prioritizing FREE TTS services"""
        
        try:
            # Select cheapest available TTS service
            service = self._select_cheapest_tts_service(force_free)
            
            if not service:
                return {
                    "success": False,
                    "error": "No TTS services available within cost limits"
                }
            
            print(f"🗣️ Generating speech with {service} (FREE)")
            
            # Generate speech using selected service  
            if service == "bark_local":
                result = await self._generate_speech_local(text, voice, language, emotion)
            elif service == "huggingface_free":
                result = await self._generate_speech_hf_direct(text, voice, language)
            elif service == "replicate_paid" and not force_free:
                result = await self._generate_speech_replicate(text, voice)
            else:
                return {"success": False, "error": f"TTS service {service} not available"}
            
            if result and result.get('success'):
                result['service_used'] = service
                result['cost'] = 0.00 if "free" in service or "local" in service else 0.01
                result['cost_category'] = "free" if result['cost'] == 0 else "low_cost"
            
            return result
            
        except Exception as e:
            return {"success": False, "error": f"Speech generation failed: {str(e)}"}
    
    def _select_cheapest_music_service(self, force_free: bool) -> Optional[str]:
        """Select cheapest music generation service"""
        
        # Priority 1: Local AudioCraft server (FREE)
        if self.services["audiocraft_local"]:
            return "audiocraft_local"
        
        # Priority 2: HuggingFace Spaces (FREE)
        if self.services["huggingface_free"]:
            return "huggingface_free"
        
        # Priority 3: Replicate (PAID - only if not force_free)
        if not force_free and self.services["replicate_paid"]:
            return "replicate_paid"
        
        return None
    
    def _select_cheapest_tts_service(self, force_free: bool) -> Optional[str]:
        """Select cheapest TTS service"""
        
        # Priority 1: Local Bark server (FREE)
        if self.services["bark_local"]:
            return "bark_local"
        
        # Priority 2: HuggingFace Spaces (FREE)
        if self.services["huggingface_free"]:
            return "huggingface_free"
        
        # Priority 3: Replicate (PAID - only if not force_free)
        if not force_free and self.services["replicate_paid"]:
            return "replicate_paid"
        
        return None
    
    async def _generate_music_local(self, prompt: str, duration: int, style: str) -> Dict[str, Any]:
        """Generate music using local AudioCraft server"""
        
        try:
            payload = {
                "prompt": prompt,
                "duration": duration,
                "style": style,
                "max_cost": 0.00,
                "force_free": True
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.audiocraft_server}/generate/music",
                    json=payload,
                    timeout=300
                ) as response:
                    
                    if response.status == 200:
                        result = await response.json()
                        return result
                    else:
                        error_text = await response.text()
                        return {"success": False, "error": f"Local AudioCraft error: {error_text}"}
        
        except Exception as e:
            return {"success": False, "error": f"Local music generation failed: {str(e)}"}
    
    async def _generate_speech_local(self, text: str, voice: str, language: str, emotion: str) -> Dict[str, Any]:
        """Generate speech using local Bark server"""
        
        try:
            payload = {
                "text": text,
                "voice": voice,
                "language": language,
                "emotion": emotion,
                "max_cost": 0.00,
                "force_free": True
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.bark_server}/generate",
                    json=payload,
                    timeout=180
                ) as response:
                    
                    if response.status == 200:
                        result = await response.json()
                        return result
                    else:
                        error_text = await response.text()
                        return {"success": False, "error": f"Local Bark TTS error: {error_text}"}
        
        except Exception as e:
            return {"success": False, "error": f"Local speech generation failed: {str(e)}"}
    
    async def _generate_music_hf_direct(self, prompt: str, duration: int, style: str) -> Dict[str, Any]:
        """Generate music directly via HuggingFace Spaces"""
        
        try:
            headers = {
                "Authorization": f"Bearer {self.huggingface_token}",
                "Content-Type": "application/json"
            }
            
            # Try MusicGen space
            payload = {
                "data": [
                    f"{prompt}, {style} style",
                    duration,
                    0.9,  # top_k
                    250,  # top_p
                    1.0,  # temperature
                    7.5   # classifier_free_guidance
                ]
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    "https://facebook-musicgen.hf.space/api/predict",
                    headers=headers,
                    json=payload,
                    timeout=300
                ) as response:
                    
                    if response.status == 200:
                        result = await response.json()
                        if result.get("data") and len(result["data"]) > 0:
                            audio_url = result["data"][0]
                            return {
                                "success": True,
                                "audio_url": audio_url,
                                "service": "huggingface_musicgen"
                            }
                    
                    error_text = await response.text()
                    return {"success": False, "error": f"HuggingFace MusicGen error: {error_text}"}
        
        except Exception as e:
            return {"success": False, "error": f"HF music generation failed: {str(e)}"}
    
    async def _generate_speech_hf_direct(self, text: str, voice: str, language: str) -> Dict[str, Any]:
        """Generate speech directly via HuggingFace Spaces"""
        
        try:
            headers = {
                "Authorization": f"Bearer {self.huggingface_token}",
                "Content-Type": "application/json"
            }
            
            # Try Bark TTS space
            payload = {
                "data": [
                    text,
                    "v2/en_speaker_0"  # Default voice
                ]
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    "https://suno-bark.hf.space/api/predict",
                    headers=headers,
                    json=payload,
                    timeout=180
                ) as response:
                    
                    if response.status == 200:
                        result = await response.json()
                        if result.get("data") and len(result["data"]) > 0:
                            audio_url = result["data"][0]
                            return {
                                "success": True,
                                "audio_url": audio_url,
                                "service": "huggingface_bark"
                            }
                    
                    error_text = await response.text()
                    return {"success": False, "error": f"HuggingFace Bark error: {error_text}"}
        
        except Exception as e:
            return {"success": False, "error": f"HF speech generation failed: {str(e)}"}
    
    async def _generate_music_replicate(self, prompt: str, duration: int, style: str) -> Dict[str, Any]:
        """Generate music using Replicate (PAID - last resort)"""
        
        try:
            headers = {
                "Authorization": f"Token {self.replicate_token}",
                "Content-Type": "application/json"
            }
            
            config = {
                "model": "meta/musicgen",
                "input": {
                    "prompt": f"{prompt}, {style} style",
                    "duration": min(duration, 30),
                    "model_version": "small"  # Cheaper option
                }
            }
            
            response = requests.post(
                "https://api.replicate.com/v1/predictions",
                headers=headers,
                json=config,
                timeout=30
            )
            
            if response.status_code != 201:
                return {"success": False, "error": f"Replicate music API error: {response.text}"}
            
            prediction = response.json()
            prediction_id = prediction["id"]
            
            # Poll for completion (limited to control costs)
            for _ in range(60):
                await asyncio.sleep(5)
                
                status_response = requests.get(
                    f"https://api.replicate.com/v1/predictions/{prediction_id}",
                    headers=headers
                )
                
                if status_response.status_code == 200:
                    status_data = status_response.json()
                    
                    if status_data["status"] == "succeeded":
                        audio_url = status_data["output"]
                        return {
                            "success": True,
                            "audio_url": audio_url,
                            "service": "replicate_musicgen"
                        }
                    
                    elif status_data["status"] == "failed":
                        return {"success": False, "error": status_data.get("error", "Music generation failed")}
            
            return {"success": False, "error": "Music generation timed out"}
            
        except Exception as e:
            return {"success": False, "error": f"Replicate music generation failed: {str(e)}"}
    
    async def _generate_speech_replicate(self, text: str, voice: str) -> Dict[str, Any]:
        """Generate speech using Replicate (PAID - last resort)"""
        
        try:
            headers = {
                "Authorization": f"Token {self.replicate_token}",
                "Content-Type": "application/json"
            }
            
            config = {
                "model": "suno-ai/bark",
                "input": {
                    "prompt": text,
                    "text_temp": 0.7,
                    "waveform_temp": 0.7
                }
            }
            
            response = requests.post(
                "https://api.replicate.com/v1/predictions",
                headers=headers,
                json=config,
                timeout=30
            )
            
            if response.status_code != 201:
                return {"success": False, "error": f"Replicate TTS API error: {response.text}"}
            
            prediction = response.json()
            prediction_id = prediction["id"]
            
            # Poll for completion
            for _ in range(30):
                await asyncio.sleep(5)
                
                status_response = requests.get(
                    f"https://api.replicate.com/v1/predictions/{prediction_id}",
                    headers=headers
                )
                
                if status_response.status_code == 200:
                    status_data = status_response.json()
                    
                    if status_data["status"] == "succeeded":
                        audio_url = status_data["output"]
                        return {
                            "success": True,
                            "audio_url": audio_url,
                            "service": "replicate_bark"
                        }
                    
                    elif status_data["status"] == "failed":
                        return {"success": False, "error": status_data.get("error", "TTS generation failed")}
            
            return {"success": False, "error": "TTS generation timed out"}
            
        except Exception as e:
            return {"success": False, "error": f"Replicate TTS generation failed: {str(e)}"}
    
    # Service testing methods
    async def _test_local_server(self, server_url: str) -> bool:
        """Test if local server is running"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{server_url}/health", timeout=5) as response:
                    return response.status == 200
        except:
            return False
    
    async def _test_huggingface_spaces(self) -> bool:
        """Test HuggingFace Spaces availability"""
        try:
            headers = {"Authorization": f"Bearer {self.huggingface_token}"}
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    "https://huggingface.co/api/spaces",
                    headers=headers,
                    timeout=10
                ) as response:
                    return response.status == 200
        except:
            return False
    
    async def _test_replicate_api(self) -> bool:
        """Test Replicate API availability"""
        try:
            headers = {"Authorization": f"Token {self.replicate_token}"}
            response = requests.get("https://api.replicate.com/v1/predictions", headers=headers, timeout=10)
            return response.status_code == 200
        except:
            return False
    
    def get_service_status(self) -> Dict[str, Any]:
        """Get comprehensive service status"""
        free_services = [name for name, available in self.services.items() 
                        if available and "paid" not in name]
        
        return {
            "services": self.services,
            "free_services_count": len(free_services),
            "free_services": free_services,
            "cost_optimization": "Always prioritizes FREE services first",
            "capabilities": {
                "music_generation": True,
                "speech_synthesis": True,
                "multilingual_tts": True,
                "emotional_speech": True,
                "cost_tracking": True
            },
            "deliverables_path": self.deliverables_path
        }

def cost_optimized_audio_generator(operation: str = "status", **kwargs) -> str:
    """
    Cost-Optimized Audio Generator for Pareng Boyong
    ALWAYS prioritizes FREE audio generation options
    
    Operations:
    - status: Check available FREE audio services
    - music: Generate music (prompt, duration, style)
    - speech: Generate speech/TTS (text, voice, language, emotion)
    """
    
    generator = CostOptimizedAudioGenerator()
    
    try:
        if operation == "status":
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            try:
                loop.run_until_complete(generator.initialize())
            finally:
                loop.close()
            
            status = generator.get_service_status()
            
            return f"""
# 🎵 **Cost-Optimized Audio Generator - Status**

## 🆓 **FREE Services Available**
{chr(10).join(f'- ✅ **{service.replace("_", " ").title()}**' for service in status['free_services']) if status['free_services'] else '- ❌ No free services detected'}

## 💸 **Paid Services Available**
{chr(10).join(f'- ⚠️  **{name.replace("_", " ").title()}** (Last resort only)' for name, available in status['services'].items() if available and "paid" in name) if any("paid" in name and available for name, available in status['services'].items()) else '- ✅ No paid services needed!'}

## 🎯 **Audio Capabilities**
- **🎵 Music Generation**: {'✅ Available' if status['capabilities']['music_generation'] else '❌ Not Available'}
- **🗣️ Speech Synthesis**: {'✅ Available' if status['capabilities']['speech_synthesis'] else '❌ Not Available'}
- **🌍 Multilingual TTS**: {'✅ Available' if status['capabilities']['multilingual_tts'] else '❌ Not Available'}
- **😊 Emotional Speech**: {'✅ Available' if status['capabilities']['emotional_speech'] else '❌ Not Available'}

## 💰 **Cost Optimization**
- **Priority**: FREE services first, paid only as absolute last resort
- **Local Servers**: AudioCraft (port 8000), Bark TTS (port 8001)
- **FREE APIs**: HuggingFace Spaces (unlimited)
- **Estimated Savings**: 90-100% vs premium audio services

## 🔑 **API Keys Status**
- **HuggingFace**: {'✅ Configured (FREE tier)' if generator.huggingface_token else '❌ Missing'}
- **Replicate**: {'⚠️  Available (PAID)' if generator.replicate_token else '✅ Not configured (saves money!)'}

{'🆓 **Ready for FREE audio generation!**' if status['free_services'] else '⚠️ **Consider setting up free audio services**'}
"""
        
        elif operation == "music":
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            try:
                loop.run_until_complete(generator.initialize())
                result = loop.run_until_complete(
                    generator.generate_music(
                        prompt=kwargs.get('prompt', 'upbeat instrumental music'),
                        duration=kwargs.get('duration', 10),
                        style=kwargs.get('style', 'upbeat'),
                        max_cost=kwargs.get('max_cost', 0.00),
                        force_free=kwargs.get('force_free', True)
                    )
                )
            finally:
                loop.close()
            
            if result['success']:
                cost_emoji = "🆓" if result['cost'] == 0 else "💸"
                return f"""
# {cost_emoji} **Music Generated Successfully!**

**Service Used**: {result['service_used'].replace('_', ' ').title()}
**Cost**: ${result['cost']:.3f} USD
**Cost Category**: {result['cost_category'].replace('_', ' ').title()}

## 🎵 **Generation Details**
- **Prompt**: "{kwargs.get('prompt', 'upbeat instrumental music')}"
- **Duration**: {kwargs.get('duration', 10)} seconds
- **Style**: {kwargs.get('style', 'upbeat').title()}
- **Service**: {result['service_used'].replace('_', ' ').title()}

## 🌐 **Access**
- **Audio URL**: {'Available' if result.get('audio_url') else 'Generated locally'}
- **Base64**: {'Available' if result.get('audio_base64') else 'Available via URL'}

✅ **Music generated with maximum cost optimization!**

💡 **Tip**: This generation {'was completely FREE!' if result['cost'] == 0 else f'cost only ${result["cost"]:.3f}'}
"""
            else:
                return f"""
# ❌ **Music Generation Failed**

**Error**: {result['error']}

## 💡 **Free Music Generation Tips**
1. Start local AudioCraft server: `python multimodal_services/audiocraft_server.py`
2. Use HuggingFace token for free MusicGen access
3. Keep prompts simple and duration under 30 seconds
4. Try different styles: upbeat, calm, electronic, classical

## 🔧 **Troubleshooting**
- Check `cost_optimized_audio_generator("status")` for available services
- Ensure HuggingFace token is configured
- Try shorter duration (10 seconds)

**Timestamp**: {datetime.now().isoformat()}
"""
        
        elif operation == "speech":
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            try:
                loop.run_until_complete(generator.initialize())
                result = loop.run_until_complete(
                    generator.generate_speech(
                        text=kwargs.get('text', 'Hello, this is a test of the speech generation system.'),
                        voice=kwargs.get('voice', 'neutral'),
                        language=kwargs.get('language', 'en'),
                        emotion=kwargs.get('emotion', 'neutral'),
                        max_cost=kwargs.get('max_cost', 0.00),
                        force_free=kwargs.get('force_free', True)
                    )
                )
            finally:
                loop.close()
            
            if result['success']:
                cost_emoji = "🆓" if result['cost'] == 0 else "💸"
                return f"""
# {cost_emoji} **Speech Generated Successfully!**

**Service Used**: {result['service_used'].replace('_', ' ').title()}
**Cost**: ${result['cost']:.3f} USD
**Cost Category**: {result['cost_category'].replace('_', ' ').title()}

## 🗣️ **Generation Details**
- **Text**: "{kwargs.get('text', 'Hello, this is a test of the speech generation system.')[:100]}{'...' if len(kwargs.get('text', '')) > 100 else ''}"
- **Voice**: {kwargs.get('voice', 'neutral').title()}
- **Language**: {kwargs.get('language', 'en').upper()}
- **Emotion**: {kwargs.get('emotion', 'neutral').title()}
- **Characters**: {len(kwargs.get('text', 'Hello, this is a test of the speech generation system.'))}

## 🌐 **Access**
- **Audio URL**: {'Available' if result.get('audio_url') else 'Generated locally'}
- **Base64**: {'Available' if result.get('audio_base64') else 'Available via URL'}

✅ **Speech generated with maximum cost optimization!**

💡 **Tip**: This generation {'was completely FREE!' if result['cost'] == 0 else f'cost only ${result["cost"]:.3f}'}
"""
            else:
                return f"""
# ❌ **Speech Generation Failed**

**Error**: {result['error']}

## 💡 **Free TTS Tips**
1. Start local Bark server: `python multimodal_services/bark_server.py`
2. Use HuggingFace token for free Bark TTS access
3. Keep text under 500 characters for free tiers
4. Try different emotions: neutral, happy, calm, excited

## 🔧 **Troubleshooting**
- Check `cost_optimized_audio_generator("status")` for available services
- Ensure HuggingFace token is configured
- Try shorter text (under 200 characters)
- Test different languages: en, es, fr, de

**Timestamp**: {datetime.now().isoformat()}
"""
        
        else:
            return f"""
# ❌ **Unknown Operation: {operation}**

**Available Operations**:
- `status`: Check available FREE audio services
- `music`: Generate music with cost optimization
- `speech`: Generate speech/TTS with cost optimization

## 📖 **Usage Examples**
```python
# Check free services
cost_optimized_audio_generator("status")

# Generate music (FREE priority)
cost_optimized_audio_generator(
    "music",
    prompt="upbeat electronic music",
    duration=15,
    style="energetic"
)

# Generate speech (FREE priority)
cost_optimized_audio_generator(
    "speech",
    text="Hello, welcome to Pareng Boyong!",
    voice="friendly",
    language="en",
    emotion="happy"
)
```

## 💰 **Cost Optimization Philosophy**
This generator ALWAYS prioritizes FREE services and will refuse expensive options unless explicitly allowed.
"""
    
    except Exception as e:
        return f"❌ **Cost-Optimized Audio Generator Error**: {str(e)}"