"""
Pareng Boyong Multimedia Initialization
Simple one-line import for all multimedia capabilities
"""

# Import all multimedia functions for immediate use
from pareng_boyong_multimedia import (
    multimedia_image_generator,
    multimedia_video_generator, 
    multimedia_request_detector,
    multimedia_auto_generator,
    multimedia_service_checker
)

print("✅ Pareng Boyong multimedia system ready!")
print("Available functions:")
print("  - multimedia_auto_generator(message)")
print("  - multimedia_image_generator(prompt, category, width, height)")
print("  - multimedia_video_generator(prompt, category, duration, resolution)")
print("  - multimedia_service_checker()")

# Quick status check
status = multimedia_service_checker()
print(f"🔍 Service Status: {status['overall_status']} ({status['healthy_services']}/{status['total_services']} services)")