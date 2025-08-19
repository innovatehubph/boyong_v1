"""
Pareng Boyong Tools Package
Contains multimedia generation and other advanced tools
"""

# Import multimedia functions for easy access
try:
    from .pareng_boyong_multimedia import (
        multimedia_image_generator,
        multimedia_video_generator, 
        multimedia_request_detector,
        multimedia_auto_generator,
        multimedia_service_checker
    )
    
    # Make multimedia functions available at package level
    __all__ = [
        'multimedia_image_generator',
        'multimedia_video_generator', 
        'multimedia_request_detector',
        'multimedia_auto_generator',
        'multimedia_service_checker'
    ]
    
except ImportError as e:
    print(f"Warning: Could not import multimedia functions: {e}")
    __all__ = []