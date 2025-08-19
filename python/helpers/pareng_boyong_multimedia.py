"""
Pareng Boyong Multimedia Module - Standalone Import
This module provides easy access to multimedia generation capabilities
"""

import sys
import os

# Add the python tools directory to path
current_dir = os.path.dirname(os.path.abspath(__file__))
tools_dir = os.path.join(current_dir, 'python', 'tools')

if tools_dir not in sys.path:
    sys.path.insert(0, tools_dir)

# Import all multimedia functions
try:
    from pareng_boyong_multimedia_core import (
        multimedia_image_generator,
        multimedia_video_generator, 
        multimedia_request_detector,
        multimedia_auto_generator,
        multimedia_service_checker
    )
    
    # Re-export for easy access
    __all__ = [
        'multimedia_image_generator',
        'multimedia_video_generator', 
        'multimedia_request_detector',
        'multimedia_auto_generator',
        'multimedia_service_checker'
    ]
    
    print("✅ Pareng Boyong multimedia system loaded successfully")
    
except ImportError as e:
    print(f"❌ Failed to import multimedia functions: {e}")
    
    # Provide fallback functions
    def multimedia_image_generator(*args, **kwargs):
        return {"status": "error", "message": "Multimedia system not available"}
    
    def multimedia_video_generator(*args, **kwargs):
        return {"status": "error", "message": "Multimedia system not available"}
        
    def multimedia_request_detector(*args, **kwargs):
        return False
        
    def multimedia_auto_generator(*args, **kwargs):
        return None
        
    def multimedia_service_checker(*args, **kwargs):
        return {"overall_status": "unavailable"}
    
    __all__ = [
        'multimedia_image_generator',
        'multimedia_video_generator', 
        'multimedia_request_detector',
        'multimedia_auto_generator',
        'multimedia_service_checker'
    ]