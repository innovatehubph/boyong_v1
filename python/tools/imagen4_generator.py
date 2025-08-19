import os
import requests
import json
import base64
import time
import hashlib
from typing import Dict, List, Any, Optional
from datetime import datetime
import urllib.request

# Import our environment loader
try:
    from env_loader import get_env, is_env_set
except ImportError:
    # Fallback if env_loader not available
    def get_env(key, default=None):
        return os.getenv(key, default)
    def is_env_set(key):
        value = os.getenv(key)
        return value is not None and value.strip() != ""

class Imagen4Generator:
    """
    Google Imagen 4 Fast integration for Pareng Boyong
    Provides high-quality, fast image generation
    """
    
    def __init__(self):
        self.api_token = get_env('REPLICATE_API_TOKEN')
        self.base_url = "https://api.replicate.com/v1"
        self.model = "google/imagen-4-fast"
        self.deliverables_path = "/root/projects/pareng-boyong/pareng_boyong_deliverables"
        self._ensure_directories()
    
    def _ensure_directories(self):
        """Ensure deliverables directories exist"""
        directories = [
            f"{self.deliverables_path}/images/portraits",
            f"{self.deliverables_path}/images/landscapes",
            f"{self.deliverables_path}/images/artwork",
            f"{self.deliverables_path}/images/social_media",
            f"{self.deliverables_path}/images/professional",
            f"{self.deliverables_path}/by_date/{datetime.now().strftime('%Y/%m')}"
        ]
        
        for directory in directories:
            os.makedirs(directory, exist_ok=True)
    
    def _generate_file_id(self, prompt: str) -> str:
        """Generate unique file ID"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        hash_obj = hashlib.md5(f"{prompt}{timestamp}".encode())
        unique_id = hash_obj.hexdigest()[:8]
        return f"pb_imagen4_{timestamp}_{unique_id}"
    
    def _categorize_content(self, prompt: str) -> str:
        """Categorize content based on prompt analysis"""
        prompt_lower = prompt.lower()
        
        if any(word in prompt_lower for word in ['portrait', 'person', 'face', 'character', 'selfie', 'headshot']):
            return 'portraits'
        elif any(word in prompt_lower for word in ['landscape', 'nature', 'mountain', 'ocean', 'forest', 'sunset', 'sunrise']):
            return 'landscapes'
        elif any(word in prompt_lower for word in ['social media', 'instagram', 'facebook', 'post', 'story']):
            return 'social_media'
        elif any(word in prompt_lower for word in ['professional', 'business', 'corporate', 'office', 'formal']):
            return 'professional'
        else:
            return 'artwork'
    
    def _save_image_from_url(self, image_url: str, file_path: str, metadata: Dict) -> str:
        """Download and save image from URL"""
        try:
            # Download image
            response = requests.get(image_url, timeout=30)
            response.raise_for_status()
            
            # Save image
            with open(file_path, 'wb') as f:
                f.write(response.content)
            
            # Save metadata
            metadata_path = file_path.replace('.jpg', '.json').replace('.png', '.json')
            with open(metadata_path, 'w') as f:
                json.dump(metadata, f, indent=2)
            
            # Create backup in date folder
            date_folder = f"{self.deliverables_path}/by_date/{datetime.now().strftime('%Y/%m')}"
            os.makedirs(date_folder, exist_ok=True)
            backup_path = os.path.join(date_folder, os.path.basename(file_path))
            
            with open(backup_path, 'wb') as f:
                f.write(response.content)
            
            return file_path
        
        except Exception as e:
            raise Exception(f"Failed to save image: {str(e)}")
    
    def generate_image(self, prompt: str, aspect_ratio: str = "1:1", 
                      output_format: str = "jpg", safety_filter_level: str = "block_medium_and_above") -> Dict[str, Any]:
        """Generate image using Google Imagen 4 Fast"""
        
        if not self.api_token:
            return {
                "success": False,
                "error": "Replicate API token not found in environment variables"
            }
        
        try:
            # Prepare the API request
            headers = {
                "Authorization": f"Token {self.api_token}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "input": {
                    "prompt": prompt,
                    "aspect_ratio": aspect_ratio,
                    "output_format": output_format,
                    "safety_filter_level": safety_filter_level
                }
            }
            
            # Start the prediction
            response = requests.post(
                f"{self.base_url}/models/{self.model}/predictions",
                headers=headers,
                json=payload,
                timeout=30
            )
            
            if response.status_code != 201:
                return {
                    "success": False,
                    "error": f"Failed to start prediction: {response.status_code} - {response.text}"
                }
            
            prediction = response.json()
            prediction_id = prediction["id"]
            
            # Poll for completion
            max_attempts = 60  # 5 minutes max wait time
            attempt = 0
            
            while attempt < max_attempts:
                time.sleep(5)  # Wait 5 seconds between checks
                
                # Check prediction status
                status_response = requests.get(
                    f"{self.base_url}/predictions/{prediction_id}",
                    headers=headers,
                    timeout=10
                )
                
                if status_response.status_code != 200:
                    return {
                        "success": False,
                        "error": f"Failed to check status: {status_response.status_code}"
                    }
                
                status_data = status_response.json()
                
                if status_data["status"] == "succeeded":
                    # Get the generated image URL
                    image_url = status_data["output"]
                    
                    # Generate file info
                    file_id = self._generate_file_id(prompt)
                    category = self._categorize_content(prompt)
                    file_extension = output_format.lower()
                    file_path = f"{self.deliverables_path}/images/{category}/{file_id}.{file_extension}"
                    
                    # Metadata
                    metadata = {
                        "type": "image",
                        "prompt": prompt,
                        "aspect_ratio": aspect_ratio,
                        "output_format": output_format,
                        "safety_filter_level": safety_filter_level,
                        "model": "Google Imagen 4 Fast",
                        "generated_at": datetime.now().isoformat(),
                        "file_id": file_id,
                        "category": category,
                        "original_url": image_url,
                        "prediction_id": prediction_id
                    }
                    
                    # Save the image
                    saved_path = self._save_image_from_url(image_url, file_path, metadata)
                    
                    return {
                        "success": True,
                        "file_path": saved_path,
                        "file_id": file_id,
                        "metadata": metadata,
                        "image_url": image_url,
                        "message": f"Image generated successfully with Imagen 4 Fast: {category}/{file_id}.{file_extension}"
                    }
                
                elif status_data["status"] == "failed":
                    error_msg = status_data.get("error", "Unknown error")
                    return {
                        "success": False,
                        "error": f"Image generation failed: {error_msg}"
                    }
                
                elif status_data["status"] in ["starting", "processing"]:
                    attempt += 1
                    continue
                
                else:
                    return {
                        "success": False,
                        "error": f"Unexpected status: {status_data['status']}"
                    }
            
            return {
                "success": False,
                "error": "Image generation timed out after 5 minutes"
            }
        
        except Exception as e:
            return {
                "success": False,
                "error": f"Image generation error: {str(e)}"
            }
    
    def get_service_status(self) -> Dict[str, Any]:
        """Check if Imagen 4 service is available"""
        if not self.api_token:
            return {
                "available": False,
                "error": "API token not configured"
            }
        
        try:
            headers = {
                "Authorization": f"Token {self.api_token}",
                "Content-Type": "application/json"
            }
            
            # Test API connection
            response = requests.get(
                f"{self.base_url}/models/{self.model}",
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                model_info = response.json()
                return {
                    "available": True,
                    "model": self.model,
                    "model_info": {
                        "name": model_info.get("name", ""),
                        "description": model_info.get("description", ""),
                        "visibility": model_info.get("visibility", ""),
                        "latest_version": model_info.get("latest_version", {}).get("id", "")
                    },
                    "deliverables_path": self.deliverables_path
                }
            else:
                return {
                    "available": False,
                    "error": f"API error: {response.status_code}"
                }
        
        except Exception as e:
            return {
                "available": False,
                "error": f"Connection error: {str(e)}"
            }


def imagen4_generator(operation: str = "status", **kwargs) -> str:
    """
    Google Imagen 4 Fast Generator for Pareng Boyong
    
    Operations:
    - status: Check service availability
    - generate: Generate image (prompt, aspect_ratio, output_format, safety_filter_level)
    """
    
    generator = Imagen4Generator()
    
    try:
        if operation == "status":
            status = generator.get_service_status()
            
            if status["available"]:
                return f"""
# 🎨 **Google Imagen 4 Fast - Service Status**

## ✅ **Service Available**
- **Model**: {status['model']}
- **Name**: {status['model_info']['name']}
- **Description**: {status['model_info']['description']}
- **Visibility**: {status['model_info']['visibility']}
- **Latest Version**: {status['model_info']['latest_version'][:20]}...

## 📁 **Storage Location**
**Deliverables**: `{status['deliverables_path']}`

## 🎯 **Capabilities**
- **High-Quality Images**: Up to 2K resolution
- **Fast Generation**: Up to 10x faster than Imagen 3
- **Style Versatility**: Photorealistic and abstract styles
- **Typography**: Enhanced text rendering
- **Aspect Ratios**: Various ratios supported

## 📊 **Available Formats**
- **Output**: JPG, PNG
- **Aspect Ratios**: 1:1, 4:3, 3:4, 16:9, 9:16
- **Safety Levels**: block_only_high, block_medium_and_above, block_low_and_above

✅ **Ready for image generation!**
"""
            else:
                return f"""
# ❌ **Google Imagen 4 Fast - Service Error**

**Status**: Unavailable
**Error**: {status['error']}

## 🔧 **Troubleshooting**
1. Check if REPLICATE_API_TOKEN is set in .env file
2. Verify API token is valid
3. Check internet connection
4. Try again in a few minutes

**Current Token**: {'✅ Set' if generator.api_token else '❌ Missing'}
"""
        
        elif operation == "generate":
            prompt = kwargs.get('prompt', 'A beautiful landscape')
            aspect_ratio = kwargs.get('aspect_ratio', '1:1')
            output_format = kwargs.get('output_format', 'jpg')
            safety_filter_level = kwargs.get('safety_filter_level', 'block_medium_and_above')
            
            result = generator.generate_image(prompt, aspect_ratio, output_format, safety_filter_level)
            
            if result['success']:
                return f"""
# 🖼️ **Image Generated Successfully with Imagen 4 Fast!**

**File ID**: `{result['file_id']}`
**Location**: `{result['file_path']}`
**Category**: {result['metadata']['category']}

## 📋 **Generation Details**
- **Prompt**: "{result['metadata']['prompt']}"
- **Aspect Ratio**: {result['metadata']['aspect_ratio']}
- **Format**: {result['metadata']['output_format'].upper()}
- **Safety Level**: {result['metadata']['safety_filter_level']}
- **Model**: {result['metadata']['model']}

## 🌐 **Access**
- **Local File**: `{result['file_path']}`
- **Original URL**: [View Image]({result['image_url']})

**Generated**: {result['metadata']['generated_at']}

✅ {result['message']}

💡 **Tip**: Image is automatically saved to organized folders and backed up by date!
"""
            else:
                return f"""
# ❌ **Image Generation Failed**

**Error**: {result['error']}

## 🔧 **Possible Solutions**
1. Check your prompt for content policy violations
2. Try a different safety filter level
3. Verify API token is valid
4. Check internet connection
5. Try again with a simpler prompt

**Timestamp**: {datetime.now().isoformat()}
"""
        
        else:
            return f"""
# ❌ **Unknown Operation**

**Operation**: {operation}
**Available Operations**:
- `status`: Check service availability
- `generate`: Generate image

## 📖 **Usage Examples**
```python
# Check status
imagen4_generator(operation="status")

# Generate image
imagen4_generator(
    operation="generate",
    prompt="A futuristic AI assistant in a modern office",
    aspect_ratio="16:9",
    output_format="jpg",
    safety_filter_level="block_medium_and_above"
)
```
"""
    
    except Exception as e:
        return f"❌ **Imagen 4 Generator Error**: {str(e)}"