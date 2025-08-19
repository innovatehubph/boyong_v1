"""
Pollinations.AI Integration Tool for Pareng Boyong
Provides access to Pollinations.AI Docker container for image generation
"""

import asyncio
import os
import base64
from typing import Optional, Dict, Any
from python.helpers.tool import Tool, Response
from python.helpers.print_style import PrintStyle
from python.helpers.docker_multimedia_client import DockerMultimediaClient
from python.helpers.files import create_folder, write_file

class PollinationsIntegration(Tool):
    """
    Generate high-quality images using Pollinations.AI Docker service
    
    Args:
        operation (str): Operation to perform - 'generate', 'health', 'status'
        prompt (str): Image description for generation (required for 'generate')
        width (int): Image width in pixels (default: 1024, max: 2048)
        height (int): Image height in pixels (default: 1024, max: 2048)  
        style (str): Style modifier for the image (optional)
        seed (int): Random seed for reproducible results (optional)
        save_to_file (bool): Save image to deliverables folder (default: True)
        
    Examples:
        pollinations_integration operation=health
        pollinations_integration operation=generate prompt="A beautiful sunset over mountains"
        pollinations_integration operation=generate prompt="Professional headshot" width=512 height=768 style="portrait photography"
        pollinations_integration operation=generate prompt="Abstract art" seed=12345 save_to_file=true
    """
    
    def __init__(self):
        super().__init__()
        self.deliverables_path = "/root/projects/pareng-boyong/pareng_boyong_deliverables"
    
    async def execute(self, **kwargs) -> Response:
        """Execute Pollinations.AI integration operation"""
        
        operation = kwargs.get("operation", "generate").lower()
        
        try:
            async with DockerMultimediaClient() as client:
                
                if operation == "health":
                    return await self._check_health(client)
                elif operation == "status":
                    return await self._get_status(client)
                elif operation == "generate":
                    return await self._generate_image(client, kwargs)
                else:
                    return Response(
                        message=f"❌ Unknown operation '{operation}'. Available: health, status, generate",
                        break_loop=False
                    )
                    
        except Exception as e:
            PrintStyle.error(f"Pollinations integration error: {e}")
            return Response(
                message=f"❌ Pollinations integration failed: {str(e)}",
                break_loop=False
            )
    
    async def _check_health(self, client: DockerMultimediaClient) -> Response:
        """Check Pollinations.AI service health"""
        
        health_status = await client.check_services_health()
        pollinations_healthy = health_status.get('pollinations', False)
        
        if pollinations_healthy:
            message = f"✅ **Pollinations.AI Service Status: HEALTHY**\n\n"
            message += f"🎨 **Image Generation Ready**\n"
            message += f"• **Service URL**: {client.services['pollinations']['url']}\n"
            message += f"• **Health Endpoint**: ✅ Responding\n"
            message += f"• **Max Resolution**: 2048x2048 pixels\n"
            message += f"• **Supported Formats**: PNG (Base64)\n"
            message += f"• **Style Support**: ✅ Available\n"
            message += f"• **Seed Control**: ✅ Available\n\n"
            
            message += f"💡 **Quick Start:**\n"
            message += f"```\npollinations_integration operation=generate prompt=\"Your image description\"\n```"
            
            return Response(message=message, break_loop=False)
        else:
            message = f"❌ **Pollinations.AI Service Status: UNAVAILABLE**\n\n"
            message += f"🔧 **Troubleshooting:**\n"
            message += f"• Check Docker container: `docker ps | grep pollinations`\n"
            message += f"• Restart service: `docker-compose -f docker-compose.multimodal-new.yml restart pollinations`\n"
            message += f"• Check logs: `docker logs pareng-boyong-pollinations-1`\n"
            message += f"• Verify port 8091 is available\n"
            
            return Response(message=message, break_loop=False)
    
    async def _get_status(self, client: DockerMultimediaClient) -> Response:
        """Get detailed Pollinations.AI status information"""
        
        status = client.get_service_status()
        pollinations_status = status.get('pollinations', {})
        
        message = f"🎨 **Pollinations.AI Service Status Report**\n\n"
        
        if pollinations_status.get('available'):
            message += f"✅ **Service**: Online and Ready\n"
            message += f"🌐 **API Endpoint**: {pollinations_status['url']}\n"
            message += f"🏥 **Health Check**: {pollinations_status['endpoint']}\n"
            message += f"🐳 **Container**: pareng-boyong-pollinations-1\n"
            message += f"🔌 **Port Mapping**: 8091:8081\n\n"
            
            message += f"⚙️ **Capabilities:**\n"
            message += f"• **Image Generation**: Text-to-Image\n"
            message += f"• **Resolution Range**: 256x256 to 2048x2048\n"
            message += f"• **Style Modifiers**: Photography, art, cartoon, etc.\n"
            message += f"• **Seed Support**: Reproducible generation\n"
            message += f"• **Format Output**: PNG (Base64 encoded)\n\n"
            
            message += f"🎯 **Usage Examples:**\n"
            message += f"• Simple: `operation=generate prompt=\"Beautiful landscape\"`\n"
            message += f"• Styled: `prompt=\"Portrait\" style=\"professional photography\"`\n"
            message += f"• Custom size: `prompt=\"Logo\" width=512 height=512`\n"
            message += f"• Reproducible: `prompt=\"Art\" seed=12345`\n"
            
        else:
            message += f"❌ **Service**: Offline\n"
            message += f"🔧 **Issue**: Container not responding\n"
            message += f"📋 **Recovery Steps**:\n"
            message += f"1. Check container status: `docker ps | grep pollinations`\n"
            message += f"2. View logs: `docker logs pareng-boyong-pollinations-1`\n"
            message += f"3. Restart: `docker restart pareng-boyong-pollinations-1`\n"
            message += f"4. Full restart: `docker-compose -f docker-compose.multimodal-new.yml restart pollinations`\n"
        
        return Response(message=message, break_loop=False)
    
    async def _generate_image(self, client: DockerMultimediaClient, kwargs: Dict[str, Any]) -> Response:
        """Generate image using Pollinations.AI"""
        
        prompt = kwargs.get("prompt", "").strip()
        if not prompt:
            return Response(
                message="❌ Please provide a 'prompt' parameter describing the image to generate.",
                break_loop=False
            )
        
        if not client.is_service_available('pollinations'):
            return Response(
                message="❌ Pollinations.AI service is not available. Use 'pollinations_integration operation=health' to check status.",
                break_loop=False
            )
        
        # Parse parameters with validation
        width = int(kwargs.get("width", 1024))
        height = int(kwargs.get("height", 1024))
        style = kwargs.get("style", "").strip()
        seed = kwargs.get("seed")
        save_to_file = kwargs.get("save_to_file", True)
        
        # Validate dimensions
        width = max(256, min(width, 2048))
        height = max(256, min(height, 2048))
        
        # Convert seed to int if provided
        if seed is not None:
            try:
                seed = int(seed)
            except (ValueError, TypeError):
                seed = None
        
        PrintStyle(font_color="cyan").print(f"🎨 Generating image with Pollinations.AI...")
        PrintStyle(font_color="white", background_color="magenta", padding=True).print(f"Prompt: {prompt}")
        
        if style:
            PrintStyle(font_color="cyan").print(f"🎭 Style: {style}")
        if seed is not None:
            PrintStyle(font_color="cyan").print(f"🎲 Seed: {seed}")
            
        PrintStyle(font_color="cyan").print(f"📐 Dimensions: {width}x{height}")
        
        # Generate image
        image_base64 = await client.generate_image_pollinations(
            prompt=prompt,
            width=width,
            height=height,
            style=style,
            seed=seed
        )
        
        if not image_base64:
            return Response(
                message="❌ Failed to generate image with Pollinations.AI. Check service logs for details.",
                break_loop=False
            )
        
        # Save to file if requested
        file_path = None
        if save_to_file:
            file_path = await self._save_image_to_deliverables(image_base64, prompt)
        
        # Prepare response message
        message = f"🎨 **Image Generated Successfully with Pollinations.AI!**\n\n"
        message += f"**Prompt**: {prompt}\n"
        if style:
            message += f"**Style**: {style}\n"
        message += f"**Dimensions**: {width} × {height} pixels\n"
        if seed is not None:
            message += f"**Seed**: {seed} (use same seed to reproduce)\n"
        
        if file_path:
            message += f"**Saved to**: `{file_path}`\n"
        
        message += f"\n<image>{image_base64}</image>\n\n"
        
        message += f"💡 **Tips for better results:**\n"
        message += f"• Be specific about details, colors, and composition\n"
        message += f"• Add style keywords like 'photorealistic', 'artistic', 'cartoon'\n"
        message += f"• Use lighting terms like 'golden hour', 'studio lighting'\n"
        message += f"• Save the seed number to recreate similar images\n"
        
        return Response(message=message, break_loop=False)
    
    async def _save_image_to_deliverables(self, image_base64: str, prompt: str) -> Optional[str]:
        """Save generated image to deliverables folder with organized structure"""
        
        try:
            import datetime
            import hashlib
            
            # Create organized folder structure
            images_dir = os.path.join(self.deliverables_path, "images")
            await create_folder(images_dir)
            
            # Determine category based on prompt
            category = self._categorize_prompt(prompt)
            category_dir = os.path.join(images_dir, category)
            await create_folder(category_dir)
            
            # Create by-date backup folder
            date_str = datetime.datetime.now().strftime("%Y/%m/%d")
            date_dir = os.path.join(images_dir, "by_date", date_str)
            await create_folder(date_dir)
            
            # Generate unique filename
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            prompt_hash = hashlib.md5(prompt.encode()).hexdigest()[:8]
            filename = f"pb_img_{category}_{timestamp}_{prompt_hash}.png"
            
            # Save to primary category location
            primary_path = os.path.join(category_dir, filename)
            
            # Decode and save image
            image_data = base64.b64decode(image_base64)
            await write_file(primary_path, image_data, mode='wb')
            
            # Create backup in date folder
            backup_path = os.path.join(date_dir, filename)
            await write_file(backup_path, image_data, mode='wb')
            
            # Create metadata file
            metadata = {
                "prompt": prompt,
                "timestamp": datetime.datetime.now().isoformat(),
                "category": category,
                "service": "pollinations.ai",
                "filename": filename,
                "paths": {
                    "primary": primary_path,
                    "backup": backup_path
                }
            }
            
            metadata_path = os.path.join(category_dir, filename.replace('.png', '.json'))
            await write_file(metadata_path, str(metadata))
            
            PrintStyle(font_color="green").print(f"💾 Image saved to: {primary_path}")
            return primary_path
            
        except Exception as e:
            PrintStyle.warning(f"Failed to save image: {e}")
            return None
    
    def _categorize_prompt(self, prompt: str) -> str:
        """Categorize image prompt for organized storage"""
        
        prompt_lower = prompt.lower()
        
        # Portrait/Character detection
        if any(word in prompt_lower for word in ['portrait', 'headshot', 'person', 'face', 'human', 'character', 'selfie', 'avatar']):
            return 'portraits'
        
        # Landscape/Nature detection
        if any(word in prompt_lower for word in ['landscape', 'mountain', 'forest', 'beach', 'nature', 'sunset', 'sunrise', 'scenery', 'outdoor']):
            return 'landscapes'
        
        # Artwork/Creative detection
        if any(word in prompt_lower for word in ['abstract', 'artistic', 'painting', 'drawing', 'creative', 'art', 'illustration', 'design']):
            return 'artwork'
        
        # Product/Commercial detection
        if any(word in prompt_lower for word in ['product', 'commercial', 'advertisement', 'marketing', 'brand', 'logo', 'business']):
            return 'product_photos'
        
        # Social media detection
        if any(word in prompt_lower for word in ['social media', 'instagram', 'facebook', 'post', 'story', 'thumbnail', 'cover']):
            return 'social_media'
        
        # Educational detection
        if any(word in prompt_lower for word in ['educational', 'diagram', 'infographic', 'chart', 'instruction', 'tutorial', 'learning']):
            return 'educational'
        
        # Default category
        return 'general'

# Register the tool
def register():
    return PollinationsIntegration()