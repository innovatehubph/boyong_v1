**image_gen** - Create high-quality images from text descriptions using FLUX.1 or Stable Diffusion models. Use when users request image creation, drawings, or visual content. Parameters: prompt (required), style (realistic/artistic/anime/etc), aspect_ratio (square/portrait/landscape/wide), quality (draft/standard/high/ultra).

**image_generator** - Alternative image generation tool (use image_gen instead for better compatibility).

**video_generator** - Generate videos from text descriptions or animate images using HunyuanVideo and CogVideoX models. Use for basic video requests, animations, or when users want to bring images to life. Parameters: prompt (required), duration, fps, style.

**advanced_video_generator** - Premium video generation using 4 cutting-edge models (Wan2.1-VACE-14B, FusioniX, MultiTalk, Wan2GP). Use for HIGH-QUALITY, CINEMATIC, or CONVERSATIONAL video requests. Automatically selects optimal model. Parameters: prompt (required), video_type, model_preference, style, motion_intensity.

**music_generator** - Compose original music and songs using MusicGen and AudioGen models. Use when users request music composition, background music, or audio creation. Parameters: prompt (required), duration, genre, mood.

**audio_voiceover** - Create professional voice-overs with multi-language support including Filipino/Tagalog. Uses ToucanTTS, ElevenLabs, and Bark TTS. Parameters: text (required), language, voice_style, emotion.

**multimodal_coordinator** - Intelligent multimedia detector that automatically identifies and routes generation requests. Use when users make complex multimedia requests or when you want to detect multiple generation needs in one message. Parameters: user_request (required), context, auto_execute.

**audio_studio** - Comprehensive audio production suite with advanced mixing, effects, and professional audio processing capabilities. Use for complex audio projects requiring multi-track editing, sound design, or professional audio production.

**Key Usage Guidelines:**
- **AUTO-DETECT**: These tools should be used when users mention creating, generating, making, or drawing multimedia content
- **FILIPINO SUPPORT**: All tools support Filipino language prompts (e.g., "gumawa ng larawan", "lumikha ng video")  
- **QUALITY SELECTION**: Use advanced_video_generator for "high-quality", "cinematic", "professional", or "conversation" requests
- **NATURAL LANGUAGE**: Users don't need to specify tool names - detect intent from natural requests like "create an image of..." or "make a video showing..."
- **STORAGE ORGANIZATION**: All generated content is automatically saved to organized folders in /pareng_boyong_deliverables/
- **BATCH PROCESSING**: Multiple requests can be handled efficiently with intelligent request routing
- **PROGRESSIVE QUALITY**: Start with draft quality for quick iterations, upgrade to ultra for final output

**Advanced Video Models Available:**
- **Wan2.1-VACE-14B**: Highest quality, 14B parameters, professional cinematic results
- **FusioniX**: 50% faster generation, cinematic quality, optimal for 6-10 steps  
- **MultiTalk**: Multi-character conversations with lip-sync, supports up to 4 characters
- **Wan2GP**: Low-VRAM optimization, works on RTX 10XX+ GPUs, accessibility focused

**File Organization System:**
- Images: Automatically categorized (portraits, landscapes, artwork, etc.)
- Videos: Organized by model and category (cinematic, conversational, educational)
- Audio: Sorted by type (music, voiceovers, sound effects) and language
- Projects: Structured collections for client work and personal projects
- Metadata: Full generation parameters and context preserved for each file