"""
Pareng Boyong Multimedia Integration - Final unified interface
This file provides seamless multimedia generation capabilities for Agent Zero
bypassing Docker daemon restrictions through host network access
"""

try:
    from .multimedia_service_integration import (
        generate_multimedia_content,
        analyze_multimedia_request,
        multimedia_service_status,
        multimedia_service_report,
        host_generate_image,
        host_generate_video,
        host_check_multimedia_services,
        host_chat_localai,
        host_get_localai_models
    )
except ImportError:
    from multimedia_service_integration import (
        generate_multimedia_content,
        analyze_multimedia_request,
        multimedia_service_status,
        multimedia_service_report,
        host_generate_image,
        host_generate_video,
        host_check_multimedia_services,
        host_chat_localai,
        host_get_localai_models
    )

# Main multimedia generation tools for Agent Zero
def multimedia_image_generator(prompt, category=None, width=1024, height=1024):
    """
    🖼️ Generate professional images using Pollinations.AI (FLUX.1 model)
    
    This tool creates high-quality images using Docker services accessible via host network.
    Images are automatically organized and saved to structured deliverables folders.
    
    Args:
        prompt (str): Detailed description of image to generate
        category (str): Image category (portraits, landscapes, artwork, product_photos, social_media)
                       Auto-detected if not provided
        width (int): Image width in pixels (default: 1024)
        height (int): Image height in pixels (default: 1024)
    
    Returns:
        Dict with status, file_path, access_url, and metadata
        
    Example:
        result = multimedia_image_generator("A beautiful sunset over mountains", "landscapes", 1920, 1080)
        if result["status"] == "success":
            print(f"Image saved: {result['file_path']}")
    """
    return generate_multimedia_content(prompt, "image", category=category, width=width, height=height)

def multimedia_video_generator(prompt, category=None, duration=4, resolution="720p", model=None):
    """
    🎬 Generate professional videos using Wan2GP (CPU-optimized models)
    
    This tool creates high-quality videos using multiple AI models optimized for VPS environments.
    Videos are automatically organized and saved with comprehensive metadata.
    
    Args:
        prompt (str): Detailed description of video to generate
        category (str): Video category (cinematic, conversational, educational, marketing)
                       Auto-detected if not provided
        duration (int): Video duration in seconds (2-15, default: 4)
        resolution (str): Video resolution (480p, 720p, 1080p, default: 720p)
        model (str): AI model selection (wan_vace_14b, fusionix, multitalk, wan2gp, auto)
                    Auto-selected based on prompt content if not provided
    
    Returns:
        Dict with status, file_path, access_url, and metadata
        
    Example:
        result = multimedia_video_generator("A cinematic scene of rain falling", "cinematic", 6, "1080p")
        if result["status"] == "success":
            print(f"Video saved: {result['file_path']}")
    """
    return generate_multimedia_content(prompt, "video", category=category, duration=duration, 
                                     resolution=resolution, model=model)

def multimedia_request_detector(message):
    """
    🔍 Automatically detect multimedia generation requests in user messages
    
    This tool analyzes user messages to identify requests for images, videos, or audio content.
    Supports English and Filipino with confidence scoring and intelligent tool suggestions.
    
    Args:
        message (str): User message to analyze for multimedia requests
        
    Returns:
        Dict with detection results, confidence scores, and tool recommendations
        
    Example:
        analysis = multimedia_request_detector("Create a beautiful landscape image")
        if analysis["should_activate"]:
            print(f"Detected: {analysis['types']} (Confidence: {analysis['overall_confidence']:.1%})")
    """
    return analyze_multimedia_request(message)

def multimedia_auto_generator(message, threshold=0.7):
    """
    🤖 Automatically generate multimedia content based on message analysis
    
    This tool combines detection and generation - analyzes messages and automatically
    generates content if confidence threshold is met. Perfect for seamless user experience.
    
    Args:
        message (str): User message to analyze and potentially generate content for
        threshold (float): Confidence threshold for auto-generation (default: 0.7)
        
    Returns:
        Generation result if auto-generated, None if confidence too low
        
    Example:
        result = multimedia_auto_generator("I want a professional portrait of a businessman")
        if result and result["status"] == "success":
            print(f"Auto-generated: {result['file_path']}")
    """
    analysis = analyze_multimedia_request(message)
    if analysis["should_activate"] and analysis["overall_confidence"] >= threshold:
        primary_type = analysis["primary_type"]
        if primary_type in ["image", "video"]:
            return generate_multimedia_content(message, primary_type)
    return None

def multimedia_service_checker():
    """
    🔧 Check health status of all multimedia services
    
    This tool monitors Docker services (LocalAI, Pollinations.AI, Wan2GP) accessibility
    and provides detailed status information for troubleshooting.
    
    Returns:
        Dict with overall status, service health details, and capabilities
        
    Example:
        status = multimedia_service_checker()
        print(f"Services: {status['healthy_services']}/{status['total_services']} healthy")
    """
    return multimedia_service_status()

def multimedia_system_report():
    """
    📊 Generate comprehensive multimedia services report
    
    This tool provides a formatted report of all multimedia capabilities,
    service status, and usage instructions in human-readable format.
    
    Returns:
        Formatted string with service status and capabilities
        
    Example:
        print(multimedia_system_report())
    """
    return multimedia_service_report()

def multimedia_localai_chat(messages, model="galatolo-Q4_K.gguf"):
    """
    💬 Chat with LocalAI service for additional AI capabilities
    
    This tool provides access to the LocalAI service running in Docker
    for text generation, analysis, and other AI tasks.
    
    Args:
        messages (List[Dict]): Chat messages in OpenAI format
        model (str): Model name (default: galatolo-Q4_K.gguf)
        
    Returns:
        Dict with response content and usage information
        
    Example:
        messages = [{"role": "user", "content": "Explain machine learning"}]
        result = multimedia_localai_chat(messages)
        print(result["response"])
    """
    return host_chat_localai(messages, model)

# Legacy/Direct access functions (for backward compatibility)
def check_multimedia_services():
    """Legacy function - use multimedia_service_checker() instead"""
    return multimedia_service_checker()

def generate_image_pollinations(prompt, category="artwork", width=1024, height=1024):
    """Legacy function - use multimedia_image_generator() instead"""
    return multimedia_image_generator(prompt, category, width, height)

def generate_video_wan2gp(prompt, category="cinematic", duration=4, resolution="720p"):
    """Legacy function - use multimedia_video_generator() instead"""
    return multimedia_video_generator(prompt, category, duration, resolution)

# Export all functions for Agent Zero tool system
__all__ = [
    # Main tools
    'multimedia_image_generator',
    'multimedia_video_generator', 
    'multimedia_request_detector',
    'multimedia_auto_generator',
    'multimedia_service_checker',
    'multimedia_system_report',
    'multimedia_localai_chat',
    
    # Legacy functions
    'check_multimedia_services',
    'generate_image_pollinations',
    'generate_video_wan2gp'
]

# Tool documentation for Agent Zero
TOOL_DESCRIPTIONS = {
    "multimedia_image_generator": {
        "description": "Generate professional images using FLUX.1 model via Pollinations.AI",
        "category": "multimedia",
        "parameters": ["prompt", "category", "width", "height"],
        "example": 'multimedia_image_generator("A sunset over mountains", "landscapes")'
    },
    "multimedia_video_generator": {
        "description": "Generate professional videos using CPU-optimized AI models via Wan2GP", 
        "category": "multimedia",
        "parameters": ["prompt", "category", "duration", "resolution", "model"],
        "example": 'multimedia_video_generator("Rain falling scene", "cinematic", 6)'
    },
    "multimedia_request_detector": {
        "description": "Detect multimedia generation requests in user messages",
        "category": "analysis",
        "parameters": ["message"],
        "example": 'multimedia_request_detector("Create a beautiful image")'
    },
    "multimedia_auto_generator": {
        "description": "Automatically generate multimedia content based on message analysis",
        "category": "automation", 
        "parameters": ["message", "threshold"],
        "example": 'multimedia_auto_generator("I need a portrait photo")'
    },
    "multimedia_service_checker": {
        "description": "Check health status of all multimedia Docker services",
        "category": "system",
        "parameters": [],
        "example": 'multimedia_service_checker()'
    }
}

def get_multimedia_capabilities():
    """
    Get comprehensive overview of multimedia capabilities
    
    Returns:
        Dict with all available tools and their descriptions
    """
    return {
        "status": "operational",
        "access_method": "host_network_bypass",
        "services": {
            "pollinations": {
                "description": "FLUX.1 image generation",
                "capabilities": ["photorealistic images", "artistic rendering", "multiple styles"],
                "formats": ["PNG"],
                "max_resolution": "2048x2048"
            },
            "wan2gp": {
                "description": "CPU-optimized video generation",
                "capabilities": ["text-to-video", "multiple models", "cinematic quality"],
                "formats": ["MP4"],
                "max_duration": "15 seconds",
                "resolutions": ["480p", "720p", "1080p"]
            },
            "localai": {
                "description": "General AI capabilities",
                "capabilities": ["chat", "text generation", "analysis"],
                "models": ["galatolo-Q4_K.gguf"]
            }
        },
        "storage": {
            "base_path": "/root/projects/pareng-boyong/pareng_boyong_deliverables",
            "organization": "automatic by type and category",
            "backup": "multiple locations with metadata"
        },
        "tools": TOOL_DESCRIPTIONS
    }

if __name__ == "__main__":
    # Test the integration
    print("🎨 Pareng Boyong Multimedia Integration")
    print("=" * 50)
    
    # Check services
    status = multimedia_service_checker()
    print(f"Services Status: {status['overall_status']}")
    print(f"Healthy Services: {status['healthy_services']}/{status['total_services']}")
    
    # Show capabilities
    capabilities = get_multimedia_capabilities()
    print(f"\nAccess Method: {capabilities['access_method']}")
    print(f"Available Tools: {len(capabilities['tools'])}")
    
    print("\n📋 Available Functions:")
    for tool_name, tool_info in TOOL_DESCRIPTIONS.items():
        print(f"• {tool_name}: {tool_info['description']}")
    
    print("\n✅ Integration ready for Agent Zero!")