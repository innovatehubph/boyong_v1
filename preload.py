import asyncio
from python.helpers import runtime, whisper, settings
from python.helpers.print_style import PrintStyle
from python.helpers import kokoro_tts
try:
    from python.helpers import elevenlabs_tts
    ELEVENLABS_AVAILABLE = True
except ImportError:
    ELEVENLABS_AVAILABLE = False
import models


async def preload():
    try:
        set = settings.get_default_settings()

        # preload whisper model
        async def preload_whisper():
            try:
                return await whisper.preload(set["stt_model_size"])
            except Exception as e:
                PrintStyle().error(f"Error in preload_whisper: {e}")

        # preload embedding model
        async def preload_embedding():
            if set["embed_model_provider"] == models.ModelProvider.HUGGINGFACE.name:
                try:
                    # Use the new LiteLLM-based model system
                    emb_mod = models.get_embedding_model(
                        models.ModelProvider.HUGGINGFACE, set["embed_model_name"]
                    )
                    emb_txt = await emb_mod.aembed_query("test")
                    return emb_txt
                except Exception as e:
                    PrintStyle().error(f"Error in preload_embedding: {e}")

        # preload enhanced TTS system
        async def preload_tts():
            try:
                # Try ElevenLabs TTS first
                if ELEVENLABS_AVAILABLE:
                    try:
                        PrintStyle().print("🎤 Initializing ElevenLabs TTS (Pareng Boyong voice)...")
                        await elevenlabs_tts.preload()
                        PrintStyle().print("✅ ElevenLabs TTS ready")
                    except Exception as e:
                        PrintStyle().warning(f"ElevenLabs TTS initialization failed: {e}")
                
                # Preload Kokoro TTS as fallback if enabled
                if set.get("tts_kokoro", True):  # Default to True for fallback
                    try:
                        PrintStyle().print("🎤 Initializing Kokoro TTS fallback...")
                        await kokoro_tts.preload()
                        PrintStyle().print("✅ Kokoro TTS fallback ready")
                    except Exception as e:
                        PrintStyle().warning(f"Kokoro TTS fallback failed: {e}")
                
                PrintStyle().print("🎤 Enhanced TTS system ready with fallback support")
            except Exception as e:
                PrintStyle().error(f"Error in preload_tts: {e}")

        # async tasks to preload
        tasks = [
            preload_embedding(),
            preload_whisper(),
            preload_tts()
        ]

        await asyncio.gather(*tasks, return_exceptions=True)
        PrintStyle().print("Preload completed")
    except Exception as e:
        PrintStyle().error(f"Error in preload: {e}")


# preload transcription model
if __name__ == "__main__":
    PrintStyle().print("Running preload...")
    runtime.initialize()
    asyncio.run(preload())
