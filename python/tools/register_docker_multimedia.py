"""
Register Docker Multimedia Tools with Agent Zero
This script registers all Docker-based multimedia generation tools
"""

# Import all the Docker multimedia tools
from .docker_multimedia_generator import (
    generate_image_docker_tool,
    generate_video_docker_tool,
    check_docker_multimedia_services,
    batch_generate_multimedia
)
from .docker_multimedia_detector import (
    detect_multimedia_request,
    auto_generate_multimedia
)

# Tool descriptions for Agent Zero
DOCKER_MULTIMEDIA_TOOLS = {
    "generate_image_docker_tool": {
        "function": generate_image_docker_tool,
        "description": """Generate high-quality images using Docker Pollinations.AI service.
        
        This tool creates professional images using the FLUX.1 model running in Docker.
        Perfect for portraits, landscapes, artwork, product photos, and social media content.
        
        Args:
            prompt (str): Detailed description of the image to generate
            width (int): Image width in pixels (default: 1024)
            height (int): Image height in pixels (default: 1024) 
            category (str): Image category for organization (auto-detected if not provided)
                          Options: portraits, landscapes, artwork, product_photos, social_media
        
        Returns:
            Dict with status, image_base64, file_path, and metadata
            
        Example Usage:
            result = generate_image_docker_tool("A beautiful sunset over mountains", width=1920, height=1080, category="landscapes")
        """,
        "enabled": True
    },
    
    "generate_video_docker_tool": {
        "function": generate_video_docker_tool,
        "description": """Generate professional videos using Docker Wan2GP service.
        
        This tool creates high-quality videos using CPU-optimized AI models.
        Supports multiple models for different quality and speed requirements.
        
        Args:
            prompt (str): Detailed description of the video to generate
            duration (int): Video duration in seconds (2-15, default: 4)
            resolution (str): Video resolution (480p, 720p, 1080p, default: 720p)
            model (str): AI model to use (auto-detected if not provided)
                        Options: wan_vace_14b, fusionix, multitalk, wan2gp, auto
            category (str): Video category for organization (auto-detected if not provided)
                           Options: cinematic, conversational, educational, marketing
        
        Returns:
            Dict with status, video_base64, file_path, and metadata
            
        Example Usage:
            result = generate_video_docker_tool("A cinematic scene of rain falling", duration=6, resolution="1080p", model="fusionix")
        """,
        "enabled": True
    },
    
    "check_docker_multimedia_services": {
        "function": check_docker_multimedia_services,
        "description": """Check the health status of all Docker multimedia services.
        
        This tool monitors LocalAI, Pollinations.AI, and Wan2GP services running in Docker containers.
        Use this to troubleshoot issues or verify service availability before generation.
        
        Returns:
            Dict with overall status, healthy service count, and individual service details
            
        Example Usage:
            status = check_docker_multimedia_services()
            if status["overall_status"] == "healthy":
                print("All services ready for multimedia generation!")
        """,
        "enabled": True
    },
    
    "batch_generate_multimedia": {
        "function": batch_generate_multimedia,
        "description": """Generate multiple multimedia items efficiently in batch.
        
        This tool processes multiple generation requests simultaneously for better performance.
        Supports mixed content types (images and videos) in a single batch.
        
        Args:
            requests (List[Dict]): List of generation requests
                Each request should have: type, prompt, and optional parameters
                
        Returns:
            List of generation results with request_index for tracking
            
        Example Usage:
            requests = [
                {"type": "image", "prompt": "A sunset", "category": "landscapes"},
                {"type": "video", "prompt": "Ocean waves", "duration": 5}
            ]
            results = batch_generate_multimedia(requests)
        """,
        "enabled": True
    },
    
    "detect_multimedia_request": {
        "function": detect_multimedia_request,
        "description": """Automatically detect multimedia generation requests in user messages.
        
        This tool analyzes user messages to identify requests for images, videos, or audio content.
        Supports both English and Filipino language detection with confidence scoring.
        
        Args:
            message (str): User message to analyze for multimedia requests
            
        Returns:
            Dict with detection results, confidence scores, and tool suggestions
            
        Example Usage:
            analysis = detect_multimedia_request("Create a beautiful landscape image")
            if analysis["should_activate"]:
                print(f"Detected {analysis['types']} request with {analysis['overall_confidence']:.1%} confidence")
        """,
        "enabled": True
    },
    
    "auto_generate_multimedia": {
        "function": auto_generate_multimedia,
        "description": """Automatically generate multimedia content based on message detection.
        
        This tool combines detection and generation - it analyzes messages and automatically
        generates content if confidence is high enough. Perfect for seamless user experience.
        
        Args:
            message (str): User message to analyze and potentially generate content for
            threshold (float): Confidence threshold for auto-generation (default: 0.7)
            
        Returns:
            Generation result if auto-generated, None if confidence too low
            
        Example Usage:
            result = auto_generate_multimedia("I want a professional portrait of a businessman")
            if result and result["status"] == "success":
                print(f"Auto-generated image saved to: {result['file_path']}")
        """,
        "enabled": True
    }
}

def register_tools_with_agent_zero():
    """Register all Docker multimedia tools with Agent Zero system"""
    
    registered_tools = []
    
    for tool_name, tool_info in DOCKER_MULTIMEDIA_TOOLS.items():
        if tool_info["enabled"]:
            # Register the tool function
            globals()[tool_name] = tool_info["function"]
            registered_tools.append(tool_name)
            
            print(f"✅ Registered: {tool_name}")
    
    return registered_tools

def get_tools_documentation():
    """Get comprehensive documentation for all Docker multimedia tools"""
    
    documentation = """
# Docker Multimedia Tools Documentation

Pareng Boyong now has access to advanced Docker-based multimedia generation tools:

## 🎨 Image Generation Tools

### generate_image_docker_tool
- **Service**: Pollinations.AI (FLUX.1 model)
- **Quality**: Professional, photorealistic
- **Categories**: Portraits, landscapes, artwork, product photos, social media
- **Auto-organization**: Files saved to organized folders with metadata
- **Performance**: Fast generation, excellent quality

## 🎬 Video Generation Tools  

### generate_video_docker_tool
- **Service**: Wan2GP (CPU-optimized)
- **Models**: 4 advanced models with auto-selection
  - **wan_vace_14b**: Highest quality (14B parameters)
  - **fusionix**: 50% faster, cinematic quality
  - **multitalk**: Multi-character conversations
  - **wan2gp**: Low-VRAM, accessible on older GPUs
- **Categories**: Cinematic, conversational, educational, marketing
- **Durations**: 2-15 seconds
- **Resolutions**: 480p, 720p, 1080p

## 🔍 Smart Detection System

### detect_multimedia_request & auto_generate_multimedia
- **Languages**: English and Filipino support
- **Confidence Scoring**: AI-powered accuracy assessment
- **Auto-activation**: High confidence requests auto-generate
- **Context Awareness**: Understands user intent and preferences

## 🔧 System Management

### check_docker_multimedia_services
- **Monitoring**: Real-time service health checks
- **Services**: LocalAI, Pollinations.AI, Wan2GP
- **Troubleshooting**: Detailed status information

### batch_generate_multimedia
- **Efficiency**: Multiple items in parallel
- **Mixed Content**: Images and videos in same batch
- **Performance**: Optimal resource utilization

## 📁 File Organization

All generated content is automatically organized in:
```
/root/projects/pareng-boyong/pareng_boyong_deliverables/
├── images/
│   ├── portraits/
│   ├── landscapes/  
│   ├── artwork/
│   ├── product_photos/
│   └── social_media/
├── videos/
│   ├── cinematic/
│   ├── conversational/
│   ├── educational/
│   └── marketing/
└── projects/
    ├── completed/
    └── in_progress/
```

## 🚀 Usage Examples

**Simple Image Generation:**
```python
result = generate_image_docker_tool("A professional portrait of a businessman in a modern office")
```

**Advanced Video Generation:**
```python
result = generate_video_docker_tool(
    "A cinematic scene of rain falling on a city street", 
    duration=8, 
    resolution="1080p", 
    model="fusionix"
)
```

**Automatic Detection:**
```python
analysis = detect_multimedia_request("Create a beautiful sunset image")
if analysis["should_activate"]:
    result = auto_generate_multimedia("Create a beautiful sunset image")
```

All tools return comprehensive results with file paths, metadata, and generation details.
"""
    
    return documentation

# Register tools on import
if __name__ == "__main__":
    print("🚀 Registering Docker Multimedia Tools...")
    registered = register_tools_with_agent_zero()
    print(f"✅ Successfully registered {len(registered)} tools")
    print("\nAvailable tools:")
    for tool in registered:
        print(f"  • {tool}")
else:
    # Auto-register when imported
    register_tools_with_agent_zero()

# Export tools for external use
__all__ = [
    'DOCKER_MULTIMEDIA_TOOLS',
    'register_tools_with_agent_zero',
    'get_tools_documentation',
    'generate_image_docker_tool',
    'generate_video_docker_tool',
    'check_docker_multimedia_services',
    'batch_generate_multimedia',
    'detect_multimedia_request',
    'auto_generate_multimedia'
]