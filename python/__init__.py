"""
Agent Zero Python Package
Includes multimedia integration and advanced tools
"""

import sys
import os

# Add project root to path for multimedia module access
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Ensure pareng_boyong_multimedia is available
try:
    # Import from the /a0 directory (Agent Zero's working directory)
    from pareng_boyong_multimedia import (
        multimedia_image_generator,
        multimedia_video_generator, 
        multimedia_request_detector,
        multimedia_auto_generator,
        multimedia_service_checker
    )
    print("✅ Multimedia system loaded for Agent Zero")
    
except ImportError as e:
    print(f"⚠️  Multimedia system not available: {e}")