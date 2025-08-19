"""
Multimedia Generator Tool for Pareng Boyong
Docker-based multimedia generation using LocalAI, Pollinations.AI, and Wan2GP services
"""

from python.helpers.tool import Tool, Response
from python.helpers.print_style import PrintStyle
import re


class MultimediaGenerator(Tool):
    
    def detect_multimedia_request(self, text: str) -> dict:
        """Detect multimedia request patterns in natural language"""
        
        text_lower = text.lower()
        
        # Image detection patterns
        image_patterns = [
            r'\b(create|generate|make|draw|design|gumawa ng)\s+(an?\s+)?(image|picture|photo|artwork|larawan)',
            r'\b(show me|i want|can you)\s+.*\b(image|picture|photo)',
            r'\bgumawa\s+ng\s+larawan',
            r'\blumikha\s+ng\s+.*larawan'
        ]
        
        # Video detection patterns  
        video_patterns = [
            r'\b(create|generate|make|produce)\s+(a\s+)?(video|animation|clip|movie)',
            r'\b(cinematic|film)\s+(video|scene)',
            r'\bgumawa\s+ng\s+video',
            r'\bmake.*\banimation'
        ]
        
        # Check for image requests
        for pattern in image_patterns:
            if re.search(pattern, text_lower):
                return {
                    "type": "image",
                    "confidence": 0.8,
                    "prompt": text
                }
        
        # Check for video requests
        for pattern in video_patterns:
            if re.search(pattern, text_lower):
                return {
                    "type": "video", 
                    "confidence": 0.8,
                    "prompt": text
                }
        
        return {"type": None, "confidence": 0.0}
    
    async def execute(self, **kwargs) -> Response:
        """Execute multimedia generation with Docker services integration"""
        
        # Get the user message/request
        user_message = self.args.get("prompt", self.args.get("message", self.args.get("text", ""))).strip()
        
        if not user_message:
            return Response(
                message="❌ Please provide a description for what you want to generate.", 
                break_loop=False
            )
        
        try:
            # Import Docker multimedia tools
            from python.tools.docker_multimedia_generator import (
                generate_image_docker_tool,
                generate_video_docker_tool,
                check_docker_multimedia_services
            )
            
            PrintStyle(font_color="cyan", padding=False).print(f"🎨 Processing multimedia request with Docker services...")
            
            # Check service health first
            health_status = check_docker_multimedia_services()
            if health_status["overall_status"] not in ["healthy", "partial"]:
                return Response(
                    message=f"❌ Docker multimedia services are not available. Status: {health_status['overall_status']}\n\n**Service Details:**\n" + 
                           "\n".join([f"- {name}: {info.get('status', 'unknown')}" for name, info in health_status.get('services', {}).items()]),
                    break_loop=False
                )
            
            # Detect content type
            detection = self.detect_multimedia_request(user_message)
            
            if detection["type"] == "image":
                PrintStyle(font_color="green").print("🖼️ Generating image with Pollinations.AI...")
                
                result = generate_image_docker_tool(
                    prompt=user_message,
                    width=1024,
                    height=1024
                )
                
                if result.get("status") == "success":
                    file_path = result.get("file_path", "")
                    metadata = result.get("metadata", {})
                    
                    # Create web-accessible URL
                    web_path = file_path.replace("/root/projects/pareng-boyong/pareng_boyong_deliverables/", "/pareng_boyong_deliverables/")
                    
                    return Response(
                        message=f"""🎨 **Image Generated Successfully!**

**Request:** {user_message}
**Service:** Pollinations.AI (FLUX.1 model)
**Category:** {metadata.get('category', 'artwork').replace('_', ' ').title()}
**Dimensions:** {metadata.get('dimensions', '1024x1024')}
**File:** `{file_path}`
**View in browser:** [Click here to view]({web_path})

<image>{result.get('image_base64', '')}</image>

The image has been saved and organized in your deliverables folder with metadata.""",
                        break_loop=False
                    )
                else:
                    return Response(
                        message=f"❌ Image generation failed: {result.get('message', 'Unknown error')}\n\n**Try:**\n- Check if Pollinations service is running\n- Use a simpler description\n- Verify network connection",
                        break_loop=False
                    )
            
            elif detection["type"] == "video":
                PrintStyle(font_color="green").print("🎬 Generating video with Wan2GP...")
                
                result = generate_video_docker_tool(
                    prompt=user_message,
                    duration=4,
                    resolution="720p"
                )
                
                if result.get("status") == "success":
                    file_path = result.get("file_path", "")
                    metadata = result.get("metadata", {})
                    
                    # Create web-accessible URL
                    web_path = file_path.replace("/root/projects/pareng-boyong/pareng_boyong_deliverables/", "/pareng_boyong_deliverables/")
                    
                    return Response(
                        message=f"""🎬 **Video Generated Successfully!**

**Request:** {user_message}  
**Service:** Wan2GP (CPU-optimized video generation)
**Model:** {metadata.get('model', 'wan2gp')}
**Category:** {metadata.get('category', 'cinematic').replace('_', ' ').title()}
**Duration:** {metadata.get('duration', 4)} seconds
**Resolution:** {metadata.get('resolution', '720p')}
**File:** `{file_path}`
**View in browser:** [Click here to view]({web_path})

<video>{result.get('video_base64', '')}</video>

The video has been saved and organized in your deliverables folder with metadata.""",
                        break_loop=False
                    )
                else:
                    return Response(
                        message=f"❌ Video generation failed: {result.get('message', 'Unknown error')}\n\n**Try:**\n- Check if Wan2GP service is running\n- Use a shorter or simpler description\n- Verify network connection",
                        break_loop=False
                    )
            
            else:
                # No multimedia request detected, provide helpful guidance
                return Response(
                    message=f"""ℹ️ **No multimedia content detected in your request.**

Your message: "{user_message}"

**🎨 To generate images, try:**
- "Create an image of a sunset over mountains"
- "Generate a professional portrait"
- "Gumawa ng magandang larawan ng tanawin"

**🎬 To generate videos, try:**
- "Create a cinematic video of rain falling"
- "Make an animation of a cat walking"
- "Generate a professional marketing video"

**📊 Current Docker Services Status:**
{health_status["healthy_services"]}/{health_status["total_services"]} services healthy
- Pollinations.AI: {health_status['services'].get('pollinations', {}).get('status', 'unknown')}
- Wan2GP: {health_status['services'].get('wan2gp', {}).get('status', 'unknown')}
- LocalAI: {health_status['services'].get('localai', {}).get('status', 'unknown')}""",
                    break_loop=False
                )
                
        except ImportError as e:
            return Response(
                message=f"❌ Docker multimedia system is not available: {e}\n\nPlease ensure the Docker multimedia services are installed and the containers are running.",
                break_loop=False
            )
        except Exception as e:
            PrintStyle.error(f"Docker multimedia generation failed: {e}")
            return Response(
                message=f"❌ Multimedia generation failed: {str(e)}\n\n**Troubleshooting steps:**\n1. Check Docker containers: `docker ps | grep pareng-boyong`\n2. Restart services: `docker-compose restart`\n3. Check service health: `curl localhost:8091/health`\n4. Try a simpler request",
                break_loop=False
            )