"""
Fixed Image Generation Tool for Pareng Boyong
Uses FLUX.1 and Stable Diffusion for high-quality image generation
"""

import asyncio
from typing import Optional, Dict, Any
from python.helpers.tool import Tool, Response
from python.helpers.print_style import PrintStyle

class ImageGen(Tool):
    
    async def execute(self, **kwargs) -> Response:
        """Execute image generation"""
        
        # Get parameters from tool args
        prompt = self.args.get("prompt", "").strip()
        negative_prompt = self.args.get("negative_prompt", "blurry, low quality, distorted, ugly")
        style = self.args.get("style", "realistic")
        aspect_ratio = self.args.get("aspect_ratio", "square")
        quality = self.args.get("quality", "standard")
        model_preference = self.args.get("model_preference", "auto")
        
        if not prompt:
            return Response(message="❌ Please provide a description for the image to generate.", break_loop=False)
        
        try:
            PrintStyle(font_color="cyan", padding=False).print(f"🎨 Generating image: {prompt[:50]}...")
            
            # Enhance prompt with style
            enhanced_prompt = self._enhance_prompt_with_style(prompt, style)
            
            # Determine dimensions based on aspect ratio and quality
            width, height = self._get_dimensions(aspect_ratio, quality)
            
            # Determine steps based on quality
            steps = self._get_steps(quality)
            
            # Generate the image
            image_base64 = await self._generate_image(
                enhanced_prompt, 
                negative_prompt, 
                width, 
                height, 
                steps, 
                model_preference
            )
            
            if not image_base64:
                return Response(
                    message="❌ Failed to generate image. Image generation services may not be available.\\n\\n**Tip:** Make sure ComfyUI or Automatic1111 is running with the required models.",
                    break_loop=False
                )
            
            return Response(
                message=f"""🎨 **Image Generated Successfully!**

**Prompt:** {prompt}
**Style:** {style.replace('_', ' ').title()}
**Dimensions:** {width}x{height}
**Model:** {model_preference.replace('_', ' ').title()}

<image>{image_base64}</image>""",
                break_loop=False
            )
                
        except Exception as e:
            PrintStyle.error(f"Image generation failed: {e}")
            return Response(
                message=f"❌ Image generation failed: {str(e)}\\n\\n**Possible solutions:**\\n- Ensure ComfyUI or Automatic1111 is running\\n- Check that required models are installed\\n- Try a simpler prompt",
                break_loop=False
            )
    
    async def _generate_image(
        self, 
        prompt: str, 
        negative_prompt: str, 
        width: int, 
        height: int, 
        steps: int,
        model_preference: str
    ) -> Optional[str]:
        """Generate image using available services"""
        
        try:
            # Import the image generation helper
            from python.helpers.image_generation import generate_image
            
            return await generate_image(
                prompt=prompt,
                negative_prompt=negative_prompt,
                width=width,
                height=height,
                steps=steps,
                model_preference=model_preference
            )
            
        except ImportError:
            PrintStyle.warning("Image generation module not available")
            return None
        except Exception as e:
            PrintStyle.error(f"Image generation error: {e}")
            return None
    
    def _enhance_prompt_with_style(self, prompt: str, style: str) -> str:
        """Enhance prompt with style-specific keywords"""
        
        style_enhancements = {
            "realistic": "photorealistic, high resolution, detailed",
            "artistic": "artistic, creative, expressive, masterpiece",
            "anime": "anime style, manga, cel shaded, vibrant colors",
            "digital_art": "digital art, concept art, trending on artstation",
            "photography": "professional photography, sharp focus, good lighting",
            "painting": "oil painting, brush strokes, artistic composition",
            "sketch": "pencil sketch, hand drawn, artistic lines"
        }
        
        enhancement = style_enhancements.get(style, "")
        if enhancement:
            return f"{prompt}, {enhancement}"
        return prompt
    
    def _get_dimensions(self, aspect_ratio: str, quality: str) -> tuple[int, int]:
        """Get image dimensions based on aspect ratio and quality"""
        
        # Base dimensions for different qualities
        quality_multipliers = {
            "draft": 0.5,    # 512x512 base
            "standard": 1.0,  # 1024x1024 base  
            "high": 1.5,     # 1536x1536 base
            "ultra": 2.0     # 2048x2048 base
        }
        
        base_size = int(1024 * quality_multipliers.get(quality, 1.0))
        
        # Aspect ratio configurations
        if aspect_ratio == "square":
            return (base_size, base_size)
        elif aspect_ratio == "portrait":
            return (int(base_size * 0.75), base_size)
        elif aspect_ratio == "landscape":
            return (base_size, int(base_size * 0.75))
        elif aspect_ratio == "wide":
            return (int(base_size * 1.78), base_size)  # 16:9
        else:
            return (base_size, base_size)
    
    def _get_steps(self, quality: str) -> int:
        """Get generation steps based on quality"""
        
        quality_steps = {
            "draft": 10,
            "standard": 20,
            "high": 30,
            "ultra": 50
        }
        
        return quality_steps.get(quality, 20)