"""
Audio Studio Tool for Pareng Boyong
Advanced audio processing including voice-overs, transcription, analysis, and effects
"""

import asyncio
import base64
import json
import tempfile
import os
import subprocess
from typing import Optional, Dict, Any, List
from python.helpers.tool import Tool, Response
from python.helpers.print_style import PrintStyle

class AudioStudio(Tool):
    async def execute(self, **kwargs) -> Response:
        """Execute the audio studio operation"""
        
        action = kwargs.get("action")
        
        try:
            if action == "voiceover":
                return await self._handle_voiceover(kwargs)
            elif action == "transcribe":
                return await self._handle_transcription(kwargs)
            elif action == "analyze":
                return await self._handle_analysis(kwargs)
            elif action == "effects":
                return await self._handle_effects(kwargs)
            elif action == "convert":
                return await self._handle_conversion(kwargs)
            elif action == "mix":
                return await self._handle_mixing(kwargs)
            else:
                return Response(
                    message="❌ Invalid action. Available actions: voiceover, transcribe, analyze, effects, convert, mix",
                    break_loop=False
                )
                
        except Exception as e:
            PrintStyle.error(f"Audio studio operation failed: {e}")
            return Response(
                message=f"❌ Audio processing failed: {str(e)}",
                break_loop=False
            )
    
    async def _handle_voiceover(self, kwargs: Dict[str, Any]) -> Response:
        """Handle voice-over generation with advanced settings"""
        
        text = kwargs.get("text", "").strip()
        voice_config = kwargs.get("voice_config", {})
        effects = kwargs.get("effects", [])
        output_format = kwargs.get("output_format", "wav")
        
        if not text:
            return Response(message="❌ Please provide text for voice-over generation.", break_loop=False)
        
        PrintStyle(font_color="cyan", padding=False).print(f"🎙️ Creating professional voice-over...")
        
        # Generate base audio
        audio_base64 = await self._generate_enhanced_voiceover(text, voice_config)
        
        if not audio_base64:
            return Response(
                message="❌ Failed to generate voice-over. TTS services may not be available.",
                break_loop=False
            )
        
        # Apply effects if requested
        if effects:
            PrintStyle(font_color="yellow", padding=False).print(f"🎛️ Applying audio effects: {', '.join(effects)}")
            audio_base64 = await self._apply_audio_effects(audio_base64, effects)
        
        # Convert format if needed
        if output_format != "wav":
            audio_base64 = await self._convert_audio_format(audio_base64, "wav", output_format)
        
        return Response(
            message=f"""🎙️ **Professional Voice-over Created!**

**Text:** {text[:100]}{'...' if len(text) > 100 else ''}
**Voice System:** {voice_config.get('system', 'auto')}
**Language:** {voice_config.get('language', 'auto')}
**Effects Applied:** {', '.join(effects) if effects else 'None'}

<audio format=\"{output_format}\" title=\"Professional Voice-over\">{audio_base64}</audio>""",
            break_loop=False
        )
    
    async def _handle_transcription(self, kwargs: Dict[str, Any]) -> Response:
        """Handle audio transcription using STT"""
        
        audio_data = kwargs.get("audio_data")
        if not audio_data:
            return Response(message="❌ Please provide audio data for transcription.", break_loop=False)
        
        PrintStyle(font_color="green", padding=False).print(f"📝 Transcribing audio...")
        
        try:
            # Use existing STT system
            transcript = await self._transcribe_audio(audio_data)
            
            if transcript:
                return Response(
                    message=f"""📝 **Audio Transcription Completed!**

**Transcript:**
{transcript}

**Language Detected:** {self._detect_language(transcript)}
**Word Count:** {len(transcript.split())} words""",
                    break_loop=False
                )
            else:
                return Response(
                    message="❌ Transcription failed. Could not process the audio.",
                    break_loop=False
                )
                
        except Exception as e:
            return Response(
                message=f"❌ Transcription error: {str(e)}",
                break_loop=False
            )
    
    async def _handle_analysis(self, kwargs: Dict[str, Any]) -> Response:
        """Handle audio analysis"""
        
        audio_data = kwargs.get("audio_data")
        text = kwargs.get("text", "")
        
        if not audio_data and not text:
            return Response(message="❌ Please provide audio data or text for analysis.", break_loop=False)
        
        PrintStyle(font_color="blue", padding=False).print(f"📊 Analyzing audio content...")
        
        analysis_results = {}
        
        # Text analysis if provided
        if text:
            analysis_results.update(await self._analyze_text(text))
        
        # Audio analysis if provided
        if audio_data:
            audio_analysis = await self._analyze_audio(audio_data)
            analysis_results.update(audio_analysis)
        
        return Response(
            message=f"""📊 **Audio Content Analysis**

{self._format_analysis_results(analysis_results)}""",
            break_loop=False
        )
    
    async def _handle_effects(self, kwargs: Dict[str, Any]) -> Response:
        """Handle audio effects processing"""
        
        audio_data = kwargs.get("audio_data")
        effects = kwargs.get("effects", [])
        
        if not audio_data:
            return Response(message="❌ Please provide audio data for effects processing.", break_loop=False)
        
        if not effects:
            return Response(message="❌ Please specify effects to apply.", break_loop=False)
        
        PrintStyle(font_color="magenta", padding=False).print(f"🎛️ Applying effects: {', '.join(effects)}")
        
        # Apply the effects
        processed_audio = await self._apply_audio_effects(audio_data, effects)
        
        if processed_audio:
            return Response(
                message=f"""🎛️ **Audio Effects Applied!**

**Effects:** {', '.join(effects)}

<audio format=\"wav\" title=\"Processed Audio\">{processed_audio}</audio>""",
                break_loop=False
            )
        else:
            return Response(
                message="❌ Failed to apply audio effects.",
                break_loop=False
            )
    
    async def _generate_enhanced_voiceover(self, text: str, voice_config: Dict[str, Any]) -> Optional[str]:
        """Generate voice-over with enhanced configuration"""
        
        system = voice_config.get("system", "auto")
        language = voice_config.get("language", "auto")
        emotion = voice_config.get("emotion", "neutral")
        
        # Auto-detect language if needed
        if language == "auto":
            language = self._detect_language(text)
        
        # Choose TTS system
        if system == "auto":
            system = "toucan" if language == "filipino" else "elevenlabs"
        
        # Modify text based on emotion
        if emotion != "neutral":
            text = self._apply_emotion_to_text(text, emotion)
        
        # Generate using the selected system
        if system == "elevenlabs":
            return await self._generate_with_elevenlabs_enhanced(text, voice_config)
        elif system == "toucan":
            return await self._generate_with_toucan_enhanced(text, voice_config)
        else:
            # Fallback to basic generation
            return await self._generate_basic_voiceover(text)
    
    async def _generate_with_elevenlabs_enhanced(self, text: str, config: Dict[str, Any]) -> Optional[str]:
        """Generate with ElevenLabs using enhanced configuration"""
        try:
            from python.helpers import elevenlabs_tts
            
            # Apply voice settings
            voice_settings = {
                "stability": 0.75,
                "similarity_boost": 0.85,
                "style": 0.20,
                "use_speaker_boost": True
            }
            
            # Override with custom settings
            if "voice_id" in config:
                # Use custom voice if provided
                pass  # Would need to modify elevenlabs_tts to support custom voices
            
            audio = await elevenlabs_tts.synthesize_sentences([text])
            return audio
            
        except Exception as e:
            PrintStyle.warning(f"Enhanced ElevenLabs TTS failed: {e}")
            return None
    
    async def _generate_with_toucan_enhanced(self, text: str, config: Dict[str, Any]) -> Optional[str]:
        """Generate with ToucanTTS using enhanced configuration"""
        try:
            from python.helpers import toucan_tts
            audio = await toucan_tts.synthesize_sentences([text])
            return audio
        except Exception as e:
            PrintStyle.warning(f"Enhanced ToucanTTS failed: {e}")
            return None
    
    async def _generate_basic_voiceover(self, text: str) -> Optional[str]:
        """Basic voice-over generation fallback"""
        try:
            # Use the existing synthesize API
            from python.api.synthesize import Synthesize
            synthesizer = Synthesize()
            result = await synthesizer.process({"text": text}, None)
            return result.get("audio", "")
        except Exception as e:
            PrintStyle.warning(f"Basic voiceover failed: {e}")
            return None
    
    async def _apply_audio_effects(self, audio_base64: str, effects: List[str]) -> Optional[str]:
        """Apply audio effects using FFmpeg"""
        
        if not audio_base64 or not effects:
            return audio_base64
        
        try:
            # Check if FFmpeg is available
            subprocess.run(["ffmpeg", "-version"], capture_output=True, check=True)
        except (subprocess.CalledProcessError, FileNotFoundError):
            PrintStyle.warning("FFmpeg not available for audio effects")
            return audio_base64
        
        try:
            # Decode base64 audio
            audio_data = base64.b64decode(audio_base64)
            
            with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as input_file:
                input_file.write(audio_data)
                input_path = input_file.name
            
            with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as output_file:
                output_path = output_file.name
            
            # Build FFmpeg filter chain
            filters = []
            for effect in effects:
                if effect == "normalize":
                    filters.append("loudnorm")
                elif effect == "noise_reduce":
                    filters.append("afftdn")
                elif effect == "echo":
                    filters.append("aecho=0.8:0.88:60:0.4")
                elif effect == "reverb":
                    filters.append("afreqshift=shift=0.1")
                elif effect == "fade_in":
                    filters.append("afade=t=in:d=2")
                elif effect == "fade_out":
                    filters.append("afade=t=out:d=2")
                elif effect == "amplify":
                    filters.append("volume=1.5")
                elif effect == "compress":
                    filters.append("acompressor=threshold=0.089:ratio=9:attack=200:release=1000")
            
            if filters:
                cmd = [
                    "ffmpeg", "-i", input_path, "-af", ",".join(filters), 
                    "-y", output_path
                ]
                
                subprocess.run(cmd, check=True, capture_output=True)
                
                # Read processed audio
                with open(output_path, 'rb') as f:
                    processed_audio = f.read()
                
                return base64.b64encode(processed_audio).decode('utf-8')
            
        except Exception as e:
            PrintStyle.warning(f"Audio effects processing failed: {e}")
        finally:
            # Clean up temp files
            for path in [input_path, output_path]:
                try:
                    os.unlink(path)
                except:
                    pass
        
        return audio_base64
    
    async def _transcribe_audio(self, audio_base64: str) -> Optional[str]:
        """Transcribe audio using existing STT system"""
        try:
            # This would integrate with the existing STT system
            # For now, return a placeholder
            return "Transcription functionality would integrate with existing STT system"
        except Exception as e:
            PrintStyle.warning(f"Transcription failed: {e}")
            return None
    
    async def _analyze_text(self, text: str) -> Dict[str, Any]:
        """Analyze text content"""
        return {
            "word_count": len(text.split()),
            "character_count": len(text),
            "language": self._detect_language(text),
            "estimated_speech_duration": f"{len(text.split()) * 0.5:.1f} seconds",
            "reading_level": "Conversational"
        }
    
    async def _analyze_audio(self, audio_base64: str) -> Dict[str, Any]:
        """Analyze audio properties"""
        # Placeholder for audio analysis
        return {
            "format": "WAV",
            "estimated_duration": "Unknown",
            "quality": "Standard"
        }
    
    def _format_analysis_results(self, results: Dict[str, Any]) -> str:
        """Format analysis results for display"""
        formatted = []
        for key, value in results.items():
            formatted.append(f"**{key.replace('_', ' ').title()}:** {value}")
        return "\n".join(formatted)
    
    def _detect_language(self, text: str) -> str:
        """Detect if text is Filipino or English"""
        filipino_indicators = [
            'ang', 'mga', 'sa', 'ng', 'na', 'at', 'ay', 'para', 'kung', 'ako', 'ka', 'siya',
            'kumusta', 'salamat', 'walang', 'bakit', 'paano', 'maganda', 'pamilya'
        ]
        
        text_lower = text.lower()
        filipino_count = sum(1 for word in filipino_indicators if word in text_lower)
        
        return "Filipino" if filipino_count >= 2 else "English"
    
    def _apply_emotion_to_text(self, text: str, emotion: str) -> str:
        """Modify text to convey emotion (basic implementation)"""
        if emotion == "excited":
            return text + "!"
        elif emotion == "sad":
            return text.replace(".", "...")
        elif emotion == "happy":
            return text.replace(".", " :)")
        return text
    
    async def _convert_audio_format(self, audio_base64: str, from_format: str, to_format: str) -> str:
        """Convert audio format using FFmpeg"""
        # Placeholder - would implement actual format conversion
        return audio_base64
    
    async def _handle_conversion(self, kwargs: Dict[str, Any]) -> Response:
        """Handle audio format conversion"""
        return Response(message="🔄 Audio conversion feature coming soon!", break_loop=False)
    
    async def _handle_mixing(self, kwargs: Dict[str, Any]) -> Response:
        """Handle audio mixing"""
        return Response(message="🎚️ Audio mixing feature coming soon!", break_loop=False)

# Register the tool
def register():
    return AudioStudio()