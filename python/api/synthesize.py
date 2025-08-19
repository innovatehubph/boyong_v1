# api/synthesize.py - Enhanced Multi-TTS system for Pareng Boyong

from python.helpers.api import ApiHandler, Request, Response
from python.helpers import runtime, settings
from python.helpers.print_style import PrintStyle
import re

class Synthesize(ApiHandler):
    async def process(self, input: dict, request: Request) -> dict | Response:
        text = input.get("text", "")
        ctxid = input.get("ctxid", "")
        
        context = self.get_context(ctxid)
        
        try:
            # Enhanced TTS system: ElevenLabs -> Kokoro -> Browser fallback
            audio = await self._synthesize_with_fallback(text, context)
            return {"audio": audio, "success": True}
        except Exception as e:
            PrintStyle.error(f"TTS synthesis failed: {e}")
            return {"error": str(e), "success": False, "audio": ""}
    
    async def _synthesize_with_fallback(self, text: str, context):
        """Enhanced TTS with settings-based priority system"""
        if not text.strip():
            return ""
        
        # Get current settings
        from python.helpers import settings
        current_settings = settings.get_settings()
        
        # Detect Filipino text for optimal TTS routing
        is_filipino = self._detect_filipino_text(text)
        
        # Get TTS provider priority from settings
        tts_priority = current_settings.get("tts_provider_priority", "auto")
        
        PrintStyle.info(f"TTS Priority: {tts_priority}, Filipino text: {is_filipino}")
        
        # Build TTS provider chain based on settings and priority
        providers = self._build_tts_provider_chain(current_settings, tts_priority, is_filipino)
        
        # Try each provider in order
        for provider_name in providers:
            try:
                audio = await self._try_tts_provider(provider_name, text, current_settings, context, is_filipino)
                if audio:
                    return audio
            except Exception as e:
                PrintStyle.warning(f"{provider_name} TTS failed: {e}")
        
        # Final fallback: return empty string for browser TTS
        if current_settings.get("tts_browser_fallback", True):
            context.log.log(type="info", content="🎤 Using browser TTS fallback")
            return ""
        else:
            context.log.log(type="error", content="❌ All TTS providers failed")
            return ""
    
    def _build_tts_provider_chain(self, settings_dict: dict, priority: str, is_filipino: bool) -> list[str]:
        """Build TTS provider chain based on settings and priority"""
        providers = []
        
        if priority == "auto":
            # ElevenLabs first, then Kokoro fallback (new default behavior)
            if settings_dict.get("tts_elevenlabs_enable", True):
                providers.append("elevenlabs")
                
            # Kokoro as primary fallback
            if settings_dict.get("tts_kokoro_enable", True):
                providers.append("kokoro")
            
            # ToucanTTS for Filipino if enabled
            if is_filipino and settings_dict.get("tts_toucan_enable", True):
                providers.append("toucan")
                
        elif priority == "elevenlabs" or priority == "elevenlabs_first":
            # ElevenLabs as primary with Kokoro fallback
            if settings_dict.get("tts_elevenlabs_enable", True):
                providers.append("elevenlabs")
            # Kokoro as primary fallback
            if settings_dict.get("tts_kokoro_enable", True):
                providers.append("kokoro")
            # ToucanTTS as secondary fallback
            if settings_dict.get("tts_toucan_enable", True):
                providers.append("toucan")
                
        elif priority == "toucan":
            if settings_dict.get("tts_toucan_enable", True):
                providers.append("toucan")
            # Add fallbacks
            if settings_dict.get("tts_elevenlabs_enable", True):
                providers.append("elevenlabs")
            if settings_dict.get("tts_kokoro_enable", True):
                providers.append("kokoro")
                
        elif priority == "kokoro":
            if settings_dict.get("tts_kokoro_enable", True):
                providers.append("kokoro")
            # Add fallbacks
            if settings_dict.get("tts_elevenlabs_enable", True):
                providers.append("elevenlabs")
            if settings_dict.get("tts_toucan_enable", True):
                providers.append("toucan")
        
        # Remove duplicates while preserving order
        seen = set()
        unique_providers = []
        for provider in providers:
            if provider not in seen:
                seen.add(provider)
                unique_providers.append(provider)
        
        return unique_providers
    
    async def _try_tts_provider(self, provider: str, text: str, settings_dict: dict, context, is_filipino: bool) -> str:
        """Try a specific TTS provider"""
        
        if provider == "elevenlabs":
            from python.helpers import elevenlabs_tts
            
            if not elevenlabs_tts.ENABLE_ELEVENLABS:
                PrintStyle.info("ElevenLabs disabled - no API key configured")
                return ""
            
            # Update ElevenLabs settings from user preferences
            self._update_elevenlabs_settings(elevenlabs_tts, settings_dict)
            
            PrintStyle.info(f"Attempting ElevenLabs TTS (Voice: {settings_dict.get('tts_elevenlabs_voice_id', 'default')})")
            audio = await elevenlabs_tts.synthesize_sentences([text])
            
            if audio:
                voice_msg = "🎤 Pareng Boyong speaking"
                if is_filipino:
                    voice_msg += " in Filipino"
                voice_msg += " (ElevenLabs - Premium Quality)"
                context.log.log(type="info", content=voice_msg)
                PrintStyle.success(f"ElevenLabs TTS generated {len(audio)} bytes")
                return audio
            else:
                PrintStyle.warning("ElevenLabs returned empty audio")
                return ""
                
        elif provider == "toucan":
            from python.helpers import toucan_tts
            audio = await toucan_tts.synthesize_sentences([text])
            if audio:
                voice_msg = "🎤 Pareng Boyong speaking"
                if is_filipino:
                    voice_msg += " in Filipino"
                voice_msg += " (ToucanTTS - Filipino Optimized)"
                context.log.log(type="info", content=voice_msg)
                PrintStyle.success(f"ToucanTTS generated {len(audio)} bytes")
                return audio
            return ""
            
        elif provider == "kokoro":
            from python.helpers import kokoro_tts
            if not await kokoro_tts.is_downloaded():
                context.log.log(type="info", content="Loading Kokoro TTS...")
            
            audio = await kokoro_tts.synthesize_sentences([text])
            if audio:
                context.log.log(type="info", content="🎤 Pareng Boyong speaking (Kokoro TTS - Fallback)")
                PrintStyle.success(f"Kokoro TTS generated {len(audio)} bytes")
                return audio
            return ""
        
        return ""
    
    def _update_elevenlabs_settings(self, elevenlabs_module, settings_dict: dict):
        """Update ElevenLabs module settings from user preferences"""
        
        # Update voice ID
        voice_id = settings_dict.get("tts_elevenlabs_voice_id", "ZmDKIF1W70PJVAMJee2h")
        if voice_id and voice_id != elevenlabs_module.KUYA_ARCHER_VOICE_ID:
            elevenlabs_module.KUYA_ARCHER_VOICE_ID = voice_id
            PrintStyle.info(f"Updated ElevenLabs voice ID to: {voice_id}")
        
        # Update voice settings
        new_settings = {
            "stability": settings_dict.get("tts_elevenlabs_stability", 0.75),
            "similarity_boost": settings_dict.get("tts_elevenlabs_similarity", 0.85),
            "style": settings_dict.get("tts_elevenlabs_style", 0.20),
            "use_speaker_boost": settings_dict.get("tts_elevenlabs_speaker_boost", True)
        }
        
        elevenlabs_module.VOICE_SETTINGS.update(new_settings)
        PrintStyle.info(f"Updated ElevenLabs voice settings: {new_settings}")
    
    def _detect_filipino_text(self, text: str) -> bool:
        """Detect if text contains Filipino/Tagalog content"""
        filipino_indicators = [
            # Common Filipino words
            'ako', 'ikaw', 'siya', 'kami', 'kayo', 'sila',
            'ang', 'ng', 'sa', 'mga', 'na', 'pa', 'po',
            'kumusta', 'salamat', 'mabuti', 'hindi', 'oo',
            'magandang', 'umaga', 'tanghali', 'gabi',
            'pareng', 'kuya', 'ate', 'boss', 'pre',
            # Technical Filipino terms
            'kompyuter', 'programa', 'sistema', 'aplikasyon',
            'website', 'internet', 'email', 'password',
            # Business Filipino terms
            'negosyo', 'trabaho', 'opisina', 'meeting',
            'project', 'deadline', 'budget', 'client'
        ]
        
        text_lower = text.lower()
        filipino_count = sum(1 for word in filipino_indicators if word in text_lower)
        
        # Consider it Filipino if we find 2+ Filipino words or specific patterns
        return filipino_count >= 2 or 'pareng boyong' in text_lower
    
    # def _clean_text(self, text: str) -> str:
    #     """Clean text by removing markdown, tables, code blocks, and other formatting"""
    #     # Remove code blocks
    #     text = re.sub(r'```[\s\S]*?```', '', text)
    #     text = re.sub(r'`[^`]*`', '', text)
        
    #     # Remove markdown links
    #     text = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', text)
        
    #     # Remove markdown formatting
    #     text = re.sub(r'[*_#]+', '', text)
        
    #     # Remove tables (basic cleanup)
    #     text = re.sub(r'\|[^\n]*\|', '', text)
        
    #     # Remove extra whitespace and newlines
    #     text = re.sub(r'\n+', ' ', text)
    #     text = re.sub(r'\s+', ' ', text)
        
    #     # Remove URLs
    #     text = re.sub(r'https?://[^\s]+', '', text)
        
    #     # Remove email addresses
    #     text = re.sub(r'\S+@\S+', '', text)
        
    #     return text.strip()
    
    # def _chunk_text(self, text: str) -> list[str]:
    #     """Split text into manageable chunks for TTS"""
    #     # If text is short enough, return as single chunk
    #     if len(text) <= 300:
    #         return [text]
        
    #     # Split into sentences first
    #     sentences = re.split(r'(?<=[.!?])\s+', text)
        
    #     chunks = []
    #     current_chunk = ""
        
    #     for sentence in sentences:
    #         sentence = sentence.strip()
    #         if not sentence:
    #             continue
                
    #         # If adding this sentence would make chunk too long, start new chunk
    #         if current_chunk and len(current_chunk + " " + sentence) > 300:
    #             chunks.append(current_chunk.strip())
    #             current_chunk = sentence
    #         else:
    #             current_chunk += (" " if current_chunk else "") + sentence
        
    #     # Add the last chunk if it has content
    #     if current_chunk.strip():
    #         chunks.append(current_chunk.strip())
        
    #     return chunks if chunks else [text]