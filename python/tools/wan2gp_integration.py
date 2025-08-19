"""
Wan2GP Integration Tool for Pareng Boyong
Provides access to Wan2GP Docker container for CPU-optimized video generation
"""

import asyncio
import os
import base64
from typing import Optional, Dict, Any
from python.helpers.tool import Tool, Response
from python.helpers.print_style import PrintStyle
from python.helpers.docker_multimedia_client import DockerMultimediaClient
from python.helpers.files import create_folder, write_file

class Wan2GPIntegration(Tool):
    """
    Generate videos using Wan2GP Docker service - optimized for CPU/low-VRAM systems
    
    Args:
        operation (str): Operation to perform - 'generate', 'health', 'status'
        prompt (str): Video description for generation (required for 'generate')
        model (str): Model to use - 'wan2gp', 'fusionix', 'multitalk', 'wan_vace_14b' (default: 'wan2gp')
        duration (int): Video duration in seconds (default: 4, max: 15)
        fps (int): Frames per second - 8, 12, 16, 24, 30 (default: 8)
        width (int): Video width in pixels (default: 512, options: 480, 512, 720, 1024)
        height (int): Video height in pixels (default: 512, options: 480, 512, 720, 1024)
        motion_intensity (str): Motion level - 'minimal', 'moderate', 'dynamic', 'dramatic' (default: 'moderate')
        style (str): Video style - 'realistic', 'cinematic', 'cartoon', 'anime', 'artistic' (default: 'realistic')
        save_to_file (bool): Save video to deliverables folder (default: True)
        
    Examples:
        wan2gp_integration operation=health
        wan2gp_integration operation=generate prompt="A cat walking in a garden"
        wan2gp_integration operation=generate prompt="Cinematic spaceship battle" model=fusionix style=cinematic
        wan2gp_integration operation=generate prompt="Two people talking" model=multitalk duration=8
        wan2gp_integration operation=generate prompt="High quality nature scene" model=wan_vace_14b width=1024 height=1024
    """
    
    def __init__(self):
        super().__init__()
        self.deliverables_path = "/root/projects/pareng-boyong/pareng_boyong_deliverables"
        
        # Model capabilities
        self.models = {
            'wan2gp': {
                'name': 'Wan2GP',
                'description': 'CPU-optimized, low VRAM requirements, accessible',
                'max_duration': 10,
                'max_resolution': 720,
                'speciality': 'accessibility'
            },
            'fusionix': {
                'name': 'FusioniX',
                'description': '50% faster generation, cinematic quality',
                'max_duration': 12,
                'max_resolution': 1024,
                'speciality': 'cinematic'
            },
            'multitalk': {
                'name': 'MultiTalk',
                'description': 'Multi-character conversations with lip-sync',
                'max_duration': 15,
                'max_resolution': 720,
                'speciality': 'conversation'
            },
            'wan_vace_14b': {
                'name': 'Wan2.1-VACE-14B',
                'description': 'Highest quality, 14B parameters, professional results',
                'max_duration': 8,
                'max_resolution': 1024,
                'speciality': 'quality'
            }
        }
    
    async def execute(self, **kwargs) -> Response:
        """Execute Wan2GP integration operation"""
        
        operation = kwargs.get("operation", "generate").lower()
        
        try:
            async with DockerMultimediaClient() as client:
                
                if operation == "health":
                    return await self._check_health(client)
                elif operation == "status":
                    return await self._get_status(client)
                elif operation == "generate":
                    return await self._generate_video(client, kwargs)
                else:
                    return Response(
                        message=f"❌ Unknown operation '{operation}'. Available: health, status, generate",
                        break_loop=False
                    )
                    
        except Exception as e:
            PrintStyle.error(f"Wan2GP integration error: {e}")
            return Response(
                message=f"❌ Wan2GP integration failed: {str(e)}",
                break_loop=False
            )
    
    async def _check_health(self, client: DockerMultimediaClient) -> Response:
        """Check Wan2GP service health"""
        
        health_status = await client.check_services_health()
        wan2gp_healthy = health_status.get('wan2gp', False)
        
        if wan2gp_healthy:
            message = f"✅ **Wan2GP Service Status: HEALTHY**\n\n"
            message += f"🎬 **Video Generation Ready**\n"
            message += f"• **Service URL**: {client.services['wan2gp']['url']}\n"
            message += f"• **Health Endpoint**: ✅ Responding\n"
            message += f"• **CPU Optimized**: ✅ Low VRAM requirements\n"
            message += f"• **Max Duration**: 15 seconds (model dependent)\n"
            message += f"• **Supported Models**: 4 available\n\n"
            
            message += f"🧠 **Available Models:**\n"
            for model_id, info in self.models.items():
                message += f"• **{info['name']}**: {info['description']}\n"
            
            message += f"\n💡 **Quick Start:**\n"
            message += f"```\nwan2gp_integration operation=generate prompt=\"Your video description\"\n```"
            
            return Response(message=message, break_loop=False)
        else:
            message = f"❌ **Wan2GP Service Status: UNAVAILABLE**\n\n"
            message += f"🔧 **Troubleshooting:**\n"
            message += f"• Check Docker container: `docker ps | grep wan2gp`\n"
            message += f"• Restart service: `docker-compose -f docker-compose.multimodal-new.yml restart wan2gp`\n"
            message += f"• Check logs: `docker logs pareng-boyong-wan2gp-1`\n"
            message += f"• Verify port 8092 is available\n"
            
            return Response(message=message, break_loop=False)
    
    async def _get_status(self, client: DockerMultimediaClient) -> Response:
        """Get detailed Wan2GP status information"""
        
        status = client.get_service_status()
        wan2gp_status = status.get('wan2gp', {})
        
        message = f"🎬 **Wan2GP Service Status Report**\n\n"
        
        if wan2gp_status.get('available'):
            message += f"✅ **Service**: Online and Ready\n"
            message += f"🌐 **API Endpoint**: {wan2gp_status['url']}\n"
            message += f"🏥 **Health Check**: {wan2gp_status['endpoint']}\n"
            message += f"🐳 **Container**: pareng-boyong-wan2gp-1\n"
            message += f"🔌 **Port Mapping**: 8092:8082\n\n"
            
            message += f"🎯 **Specialized Models:**\n"
            for model_id, info in self.models.items():
                message += f"**{model_id}**: {info['name']}\n"
                message += f"  • {info['description']}\n"
                message += f"  • Max Duration: {info['max_duration']}s\n"
                message += f"  • Max Resolution: {info['max_resolution']}p\n"
                message += f"  • Speciality: {info['speciality'].title()}\n\n"
            
            message += f"⚙️ **Generation Options:**\n"
            message += f"• **Duration**: 2-15 seconds (model dependent)\n"
            message += f"• **FPS**: 8, 12, 16, 24, 30\n"
            message += f"• **Resolution**: 480p to 1024p\n"
            message += f"• **Motion Control**: Minimal to Dramatic\n"
            message += f"• **Styles**: Realistic, Cinematic, Cartoon, Anime, Artistic\n\n"
            
            message += f"🚀 **Usage Examples:**\n"
            message += f"• Basic: `prompt=\"Cat walking\" model=wan2gp`\n"
            message += f"• Cinematic: `prompt=\"Epic scene\" model=fusionix style=cinematic`\n"
            message += f"• Conversation: `prompt=\"Two people talking\" model=multitalk`\n"
            message += f"• High Quality: `prompt=\"Nature\" model=wan_vace_14b duration=6`\n"
            
        else:
            message += f"❌ **Service**: Offline\n"
            message += f"🔧 **Issue**: Container not responding\n"
            message += f"📋 **Recovery Steps**:\n"
            message += f"1. Check container: `docker ps | grep wan2gp`\n"
            message += f"2. View logs: `docker logs pareng-boyong-wan2gp-1`\n"
            message += f"3. Restart container: `docker restart pareng-boyong-wan2gp-1`\n"
            message += f"4. Full restart: `docker-compose -f docker-compose.multimodal-new.yml restart wan2gp`\n"
        
        return Response(message=message, break_loop=False)
    
    async def _generate_video(self, client: DockerMultimediaClient, kwargs: Dict[str, Any]) -> Response:
        """Generate video using Wan2GP"""
        
        prompt = kwargs.get("prompt", "").strip()
        if not prompt:
            return Response(
                message="❌ Please provide a 'prompt' parameter describing the video to generate.",
                break_loop=False
            )
        
        if not client.is_service_available('wan2gp'):
            return Response(
                message="❌ Wan2GP service is not available. Use 'wan2gp_integration operation=health' to check status.",
                break_loop=False
            )
        
        # Parse and validate parameters
        model = kwargs.get("model", "wan2gp").lower()
        if model not in self.models:
            return Response(
                message=f"❌ Invalid model '{model}'. Available: {', '.join(self.models.keys())}",
                break_loop=False
            )
        
        model_info = self.models[model]
        
        # Parse parameters with model-specific validation
        duration = int(kwargs.get("duration", 4))
        fps = int(kwargs.get("fps", 8))
        width = int(kwargs.get("width", 512))
        height = int(kwargs.get("height", 512))
        motion_intensity = kwargs.get("motion_intensity", "moderate").lower()
        style = kwargs.get("style", "realistic").lower()
        save_to_file = kwargs.get("save_to_file", True)
        
        # Validate parameters
        duration = max(2, min(duration, model_info['max_duration']))
        fps = min(fps, 30) if fps in [8, 12, 16, 24, 30] else 8
        width = min(width, model_info['max_resolution']) if width in [480, 512, 720, 1024] else 512
        height = min(height, model_info['max_resolution']) if height in [480, 512, 720, 1024] else 512
        
        if motion_intensity not in ['minimal', 'moderate', 'dynamic', 'dramatic']:
            motion_intensity = 'moderate'
        if style not in ['realistic', 'cinematic', 'cartoon', 'anime', 'artistic']:
            style = 'realistic'
        
        # Show generation info
        PrintStyle(font_color="cyan").print(f"🎬 Generating video with {model_info['name']}...")
        PrintStyle(font_color="white", background_color="blue", padding=True).print(f"Prompt: {prompt}")
        PrintStyle(font_color="cyan").print(f"🤖 Model: {model_info['name']} ({model_info['speciality']})")
        PrintStyle(font_color="cyan").print(f"⏱️ Duration: {duration}s @ {fps} FPS")
        PrintStyle(font_color="cyan").print(f"📐 Resolution: {width}x{height}")
        PrintStyle(font_color="cyan").print(f"🎭 Style: {style.title()}, Motion: {motion_intensity.title()}")
        
        # Generate video
        video_base64 = await client.generate_video_wan2gp(
            prompt=prompt,
            model=model,
            duration=duration,
            fps=fps,
            width=width,
            height=height,
            motion_intensity=motion_intensity,
            style=style
        )
        
        if not video_base64:
            return Response(
                message=f"❌ Failed to generate video with {model_info['name']}. Check service logs for details.",
                break_loop=False
            )
        
        # Save to file if requested
        file_path = None
        if save_to_file:
            file_path = await self._save_video_to_deliverables(video_base64, prompt, model)
        
        # Prepare response
        message = f"🎬 **Video Generated Successfully with {model_info['name']}!**\n\n"
        message += f"**Prompt**: {prompt}\n"
        message += f"**Model**: {model_info['name']} - {model_info['description']}\n"
        message += f"**Duration**: {duration} seconds\n"
        message += f"**Quality**: {width} × {height} @ {fps} FPS\n"
        message += f"**Style**: {style.title()}\n"
        message += f"**Motion**: {motion_intensity.title()}\n"
        
        if file_path:
            message += f"**Saved to**: `{file_path}`\n"
        
        message += f"\n<video format=\"mp4\">{video_base64}</video>\n\n"
        
        # Model-specific tips
        if model == 'multitalk':
            message += f"💬 **MultiTalk Tips:**\n"
            message += f"• Perfect for dialogue scenes and character interactions\n"
            message += f"• Add character descriptions for better lip-sync\n"
        elif model == 'fusionix':
            message += f"🎭 **FusioniX Tips:**\n"
            message += f"• Excellent for cinematic and dramatic scenes\n"
            message += f"• 50% faster generation than other high-quality models\n"
        elif model == 'wan_vace_14b':
            message += f"💎 **Wan2.1-VACE Tips:**\n"
            message += f"• Highest quality results with 14B parameters\n"
            message += f"• Best for professional and detailed scenes\n"
        elif model == 'wan2gp':
            message += f"⚡ **Wan2GP Tips:**\n"
            message += f"• Optimized for CPU and low-VRAM systems\n"
            message += f"• Great balance of speed and quality\n"
        
        message += f"• Try different motion intensities for varied results\n"
        message += f"• Combine with style keywords for unique looks\n"
        
        return Response(message=message, break_loop=False)
    
    async def _save_video_to_deliverables(self, video_base64: str, prompt: str, model: str) -> Optional[str]:
        """Save generated video to deliverables folder with organized structure"""
        
        try:
            import datetime
            import hashlib
            
            # Create organized folder structure
            videos_dir = os.path.join(self.deliverables_path, "videos")
            await create_folder(videos_dir)
            
            # Determine category based on prompt and model
            category = self._categorize_video(prompt, model)
            category_dir = os.path.join(videos_dir, category)
            await create_folder(category_dir)
            
            # Create model-specific backup folder
            model_dir = os.path.join(videos_dir, "by_model", model)
            await create_folder(model_dir)
            
            # Create by-date backup folder
            date_str = datetime.datetime.now().strftime("%Y/%m/%d")
            date_dir = os.path.join(videos_dir, "by_date", date_str)
            await create_folder(date_dir)
            
            # Generate unique filename
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            prompt_hash = hashlib.md5(prompt.encode()).hexdigest()[:8]
            filename = f"pb_vid_{model}_{category}_{timestamp}_{prompt_hash}.mp4"
            
            # Save to primary category location
            primary_path = os.path.join(category_dir, filename)
            
            # Decode and save video
            video_data = base64.b64decode(video_base64)
            await write_file(primary_path, video_data, mode='wb')
            
            # Create backups
            model_backup_path = os.path.join(model_dir, filename)
            date_backup_path = os.path.join(date_dir, filename)
            
            await write_file(model_backup_path, video_data, mode='wb')
            await write_file(date_backup_path, video_data, mode='wb')
            
            # Create metadata file
            metadata = {
                "prompt": prompt,
                "model": model,
                "timestamp": datetime.datetime.now().isoformat(),
                "category": category,
                "service": "wan2gp",
                "filename": filename,
                "paths": {
                    "primary": primary_path,
                    "model_backup": model_backup_path,
                    "date_backup": date_backup_path
                }
            }
            
            metadata_path = os.path.join(category_dir, filename.replace('.mp4', '.json'))
            await write_file(metadata_path, str(metadata))
            
            PrintStyle(font_color="green").print(f"💾 Video saved to: {primary_path}")
            return primary_path
            
        except Exception as e:
            PrintStyle.warning(f"Failed to save video: {e}")
            return None
    
    def _categorize_video(self, prompt: str, model: str) -> str:
        """Categorize video prompt for organized storage"""
        
        prompt_lower = prompt.lower()
        
        # Model-specific categorization
        if model == 'multitalk':
            return 'conversational'
        elif model == 'fusionix':
            return 'cinematic'
        
        # Content-based categorization
        if any(word in prompt_lower for word in ['cinematic', 'dramatic', 'epic', 'film', 'movie', 'scene']):
            return 'cinematic'
        
        if any(word in prompt_lower for word in ['conversation', 'talking', 'dialogue', 'interview', 'discussion', 'chat']):
            return 'conversational'
        
        if any(word in prompt_lower for word in ['education', 'tutorial', 'lesson', 'learning', 'instruction', 'demonstration']):
            return 'educational'
        
        if any(word in prompt_lower for word in ['marketing', 'advertisement', 'commercial', 'brand', 'product', 'business']):
            return 'marketing'
        
        if any(word in prompt_lower for word in ['social media', 'instagram', 'tiktok', 'shorts', 'reel', 'story']):
            return 'social_media'
        
        if any(word in prompt_lower for word in ['animation', 'cartoon', 'character', 'animate', 'moving']):
            return 'animations'
        
        if any(word in prompt_lower for word in ['product', 'demo', 'showcase', 'demonstration', 'review', 'unboxing']):
            return 'product_demos'
        
        if any(word in prompt_lower for word in ['tutorial', 'how to', 'guide', 'instruction', 'step by step']):
            return 'tutorials'
        
        # Default category
        return 'general'

# Register the tool
def register():
    return Wan2GPIntegration()