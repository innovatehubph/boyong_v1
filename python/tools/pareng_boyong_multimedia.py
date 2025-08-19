"""
Pareng Boyong Multimedia Tools - Direct Import Module
Provides multimedia generation without complex dependencies
"""

import requests
import json
import os
import datetime
from pathlib import Path

def multimedia_auto_generator(user_message):
    """
    Auto-detect and generate multimedia content from user messages
    """
    try:
        # Simple pattern matching for multimedia requests
        message = user_message.lower()
        
        # Image detection patterns
        image_patterns = ['image', 'picture', 'photo', 'draw', 'create', 'generate', 'larawan', 'gumawa']
        video_patterns = ['video', 'animation', 'movie', 'clip', 'animate', 'pelikula']
        
        if any(pattern in message for pattern in image_patterns):
            return multimedia_image_generator(user_message)
        elif any(pattern in message for pattern in video_patterns):
            return multimedia_video_generator(user_message)
        
        return None
    except Exception as e:
        return {"status": "error", "message": str(e)}

def multimedia_image_generator(prompt, category="general", width=1024, height=1024):
    """
    Generate images using Pollinations.AI
    """
    try:
        # Create deliverables directory
        base_dir = Path("/root/projects/pareng-boyong/pareng_boyong_deliverables/images")
        base_dir.mkdir(parents=True, exist_ok=True)
        
        # Generate unique filename
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"pb_img_{category}_{timestamp}.png"
        file_path = base_dir / filename
        
        # Call Pollinations API via host service
        try:
            response = requests.get(
                "http://localhost:8091/generate_image",
                params={"prompt": prompt, "width": width, "height": height},
                timeout=60
            )
            
            if response.status_code == 200:
                with open(file_path, "wb") as f:
                    f.write(response.content)
                
                return {
                    "status": "success",
                    "file_path": str(file_path),
                    "access_url": f"/pareng_boyong_deliverables/images/{filename}",
                    "metadata": {
                        "prompt": prompt,
                        "category": category,
                        "dimensions": f"{width}x{height}",
                        "timestamp": timestamp
                    }
                }
            else:
                return {"status": "error", "message": f"Service error: {response.status_code}"}
                
        except requests.exceptions.RequestException:
            # Fallback to direct Pollinations API
            response = requests.get(
                f"https://pollinations.ai/p/{prompt}",
                timeout=30
            )
            
            if response.status_code == 200:
                with open(file_path, "wb") as f:
                    f.write(response.content)
                
                return {
                    "status": "success",
                    "file_path": str(file_path),
                    "access_url": f"/pareng_boyong_deliverables/images/{filename}",
                    "metadata": {
                        "prompt": prompt,
                        "category": category,
                        "dimensions": f"{width}x{height}",
                        "timestamp": timestamp,
                        "source": "direct_api"
                    }
                }
    except Exception as e:
        return {"status": "error", "message": str(e)}

def multimedia_video_generator(prompt, category="general", duration=6):
    """
    Generate videos using available video services
    """
    try:
        # Create deliverables directory
        base_dir = Path("/root/projects/pareng-boyong/pareng_boyong_deliverables/videos")
        base_dir.mkdir(parents=True, exist_ok=True)
        
        # Generate unique filename
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"pb_vid_{category}_{timestamp}.mp4"
        file_path = base_dir / filename
        
        # Try Wan2GP service first
        try:
            response = requests.post(
                "http://localhost:8092/generate_video",
                json={"prompt": prompt, "duration": duration},
                timeout=120
            )
            
            if response.status_code == 200:
                with open(file_path, "wb") as f:
                    f.write(response.content)
                
                return {
                    "status": "success",
                    "file_path": str(file_path),
                    "access_url": f"/pareng_boyong_deliverables/videos/{filename}",
                    "metadata": {
                        "prompt": prompt,
                        "category": category,
                        "duration": duration,
                        "timestamp": timestamp
                    }
                }
        except requests.exceptions.RequestException:
            pass
            
        # Return placeholder for now
        return {
            "status": "pending",
            "message": "Video generation service unavailable, please try again",
            "file_path": None
        }
        
    except Exception as e:
        return {"status": "error", "message": str(e)}

def multimedia_service_checker():
    """
    Check status of multimedia services
    """
    services = {
        "pollinations": "http://localhost:8091/health",
        "wan2gp": "http://localhost:8092/health", 
        "localai": "http://localhost:8090/health"
    }
    
    status = {"overall_status": "healthy", "services": {}}
    
    for service, url in services.items():
        try:
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                status["services"][service] = "healthy"
            else:
                status["services"][service] = "unhealthy"
                status["overall_status"] = "degraded"
        except:
            status["services"][service] = "unreachable"
            status["overall_status"] = "degraded"
    
    return status

def multimedia_request_detector(user_message):
    """
    Detect if user message contains multimedia requests
    """
    message = user_message.lower()
    
    # Detection patterns
    patterns = {
        "image": ["image", "picture", "photo", "draw", "create", "generate", "larawan", "gumawa"],
        "video": ["video", "animation", "movie", "clip", "animate", "pelikula"],
        "audio": ["music", "sound", "voice", "audio", "tunog", "musika"]
    }
    
    detected = []
    confidence = 0
    
    for media_type, keywords in patterns.items():
        if any(keyword in message for keyword in keywords):
            detected.append(media_type)
            confidence += 0.3
    
    return {
        "detected_types": detected,
        "confidence": min(confidence, 1.0),
        "should_generate": confidence > 0.6
    }

# Export main functions for easy import
__all__ = [
    'multimedia_auto_generator',
    'multimedia_image_generator', 
    'multimedia_video_generator',
    'multimedia_service_checker',
    'multimedia_request_detector'
]