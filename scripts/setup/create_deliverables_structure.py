#!/usr/bin/env python3
"""
Create Organized Deliverables Storage Structure for Pareng Boyong
"""

import os
import json
from datetime import datetime
from pathlib import Path

def create_deliverables_structure():
    """Create comprehensive folder structure for Pareng Boyong deliverables"""
    
    base_path = Path('/root/projects/pareng-boyong')
    deliverables_root = base_path / 'pareng_boyong_deliverables'
    
    # Main deliverables structure
    structure = {
        'pareng_boyong_deliverables': {
            'images': {
                'portraits': {},
                'landscapes': {},
                'artwork': {},
                'product_photos': {},
                'social_media': {},
                'thumbnails': {},
                'logos_branding': {},
                'educational': {},
                'by_date': {
                    str(datetime.now().year): {
                        f"{datetime.now().month:02d}": {}
                    }
                }
            },
            'videos': {
                'cinematic': {},
                'conversational': {},
                'educational': {},
                'marketing': {},
                'social_media': {},
                'animations': {},
                'product_demos': {},
                'tutorials': {},
                'by_quality': {
                    '480p': {},
                    '720p': {},
                    '1080p': {},
                    '4k': {}
                },
                'by_model': {
                    'wan_vace_14b': {},
                    'fusionix': {},
                    'multitalk': {},
                    'wan2gp': {},
                    'basic_models': {}
                },
                'by_date': {
                    str(datetime.now().year): {
                        f"{datetime.now().month:02d}": {}
                    }
                }
            },
            'audio': {
                'music': {
                    'ambient': {},
                    'upbeat': {},
                    'cinematic': {},
                    'folk': {},
                    'electronic': {},
                    'classical': {}
                },
                'voiceovers': {
                    'english': {},
                    'filipino': {},
                    'multilingual': {},
                    'character_voices': {},
                    'professional': {},
                    'educational': {}
                },
                'sound_effects': {},
                'podcasts': {},
                'by_date': {
                    str(datetime.now().year): {
                        f"{datetime.now().month:02d}": {}
                    }
                }
            },
            'projects': {
                'completed': {},
                'in_progress': {},
                'templates': {},
                'client_work': {},
                'personal': {}
            },
            'exports': {
                'social_media_ready': {
                    'instagram': {},
                    'tiktok': {},
                    'youtube': {},
                    'facebook': {}
                },
                'professional': {
                    'presentations': {},
                    'marketing': {},
                    'training': {}
                }
            },
            'raw_outputs': {
                'comfyui_raw': {},
                'advanced_video_raw': {},
                'audio_raw': {}
            },
            'metadata': {
                'generation_logs': {},
                'user_preferences': {},
                'usage_analytics': {}
            }
        }
    }
    
    # Create the folder structure
    def create_folders(base, structure_dict):
        for folder_name, sub_structure in structure_dict.items():
            folder_path = base / folder_name
            folder_path.mkdir(parents=True, exist_ok=True)
            
            # Create README for each main folder
            if folder_name in ['images', 'videos', 'audio', 'projects']:
                readme_content = get_folder_description(folder_name)
                readme_path = folder_path / 'README.md'
                with open(readme_path, 'w') as f:
                    f.write(readme_content)
            
            # Create .gitkeep for empty folders
            gitkeep_path = folder_path / '.gitkeep'
            with open(gitkeep_path, 'w') as f:
                f.write('# This file keeps the folder in git\n')
            
            # Recursively create subfolders
            if isinstance(sub_structure, dict) and sub_structure:
                create_folders(folder_path, sub_structure)
    
    create_folders(base_path, structure)
    
    # Create master configuration file
    config = {
        "pareng_boyong_deliverables_config": {
            "version": "1.0.0",
            "created": datetime.now().isoformat(),
            "base_path": str(deliverables_root),
            "structure_info": {
                "total_categories": 8,
                "main_folders": ["images", "videos", "audio", "projects", "exports", "raw_outputs", "metadata"],
                "organization_method": "content_based_with_date_backup"
            },
            "storage_paths": {
                "images": {
                    "base": str(deliverables_root / "images"),
                    "portraits": str(deliverables_root / "images" / "portraits"),
                    "landscapes": str(deliverables_root / "images" / "landscapes"),
                    "artwork": str(deliverables_root / "images" / "artwork"),
                    "social_media": str(deliverables_root / "images" / "social_media"),
                    "by_date": str(deliverables_root / "images" / "by_date")
                },
                "videos": {
                    "base": str(deliverables_root / "videos"),
                    "cinematic": str(deliverables_root / "videos" / "cinematic"),
                    "conversational": str(deliverables_root / "videos" / "conversational"),
                    "educational": str(deliverables_root / "videos" / "educational"),
                    "by_model": {
                        "wan_vace_14b": str(deliverables_root / "videos" / "by_model" / "wan_vace_14b"),
                        "fusionix": str(deliverables_root / "videos" / "by_model" / "fusionix"),
                        "multitalk": str(deliverables_root / "videos" / "by_model" / "multitalk"),
                        "wan2gp": str(deliverables_root / "videos" / "by_model" / "wan2gp")
                    },
                    "by_date": str(deliverables_root / "videos" / "by_date")
                },
                "audio": {
                    "base": str(deliverables_root / "audio"),
                    "music": str(deliverables_root / "audio" / "music"),
                    "voiceovers": str(deliverables_root / "audio" / "voiceovers"),
                    "by_date": str(deliverables_root / "audio" / "by_date")
                },
                "projects": {
                    "base": str(deliverables_root / "projects"),
                    "completed": str(deliverables_root / "projects" / "completed"),
                    "in_progress": str(deliverables_root / "projects" / "in_progress"),
                    "templates": str(deliverables_root / "projects" / "templates")
                }
            },
            "file_naming_conventions": {
                "images": "pb_img_{category}_{timestamp}_{id}.{ext}",
                "videos": "pb_vid_{model}_{category}_{timestamp}_{id}.{ext}",
                "audio": "pb_audio_{type}_{category}_{timestamp}_{id}.{ext}",
                "projects": "pb_project_{name}_{timestamp}"
            },
            "usage_guidelines": {
                "automatic_organization": True,
                "date_based_backup": True,
                "content_based_primary": True,
                "cleanup_after_days": 90,
                "max_file_size_mb": 500
            }
        }
    }
    
    config_path = deliverables_root / 'deliverables_config.json'
    with open(config_path, 'w') as f:
        json.dump(config, f, indent=2)
    
    print(f"✅ Deliverables structure created at: {deliverables_root}")
    print(f"✅ Configuration saved to: {config_path}")
    
    return str(deliverables_root), str(config_path)

def get_folder_description(folder_name):
    """Get description for folder README files"""
    descriptions = {
        'images': """# 🖼️ Pareng Boyong Generated Images

This folder contains all images generated by Pareng Boyong's multimodal AI system.

## Subfolders:
- **portraits/**: Human portraits and character images
- **landscapes/**: Nature scenes, cityscapes, environments  
- **artwork/**: Artistic and creative images
- **product_photos/**: Product photography and commercial images
- **social_media/**: Images optimized for social platforms
- **thumbnails/**: Video thumbnails and preview images
- **logos_branding/**: Brand assets and logo designs
- **educational/**: Images for learning and instruction
- **by_date/**: Chronological organization backup

## Generated Using:
- FLUX.1 Schnell (primary)
- Stable Diffusion XL (artistic styles)
- ComfyUI workflows

## File Naming:
`pb_img_{category}_{YYYYMMDD_HHMMSS}_{unique_id}.png`
""",
        
        'videos': """# 🎬 Pareng Boyong Generated Videos

This folder contains all videos generated by Pareng Boyong's advanced video generation system.

## Subfolders:
- **cinematic/**: Film-quality videos with dramatic lighting
- **conversational/**: Multi-character dialogue videos  
- **educational/**: Learning and instruction videos
- **marketing/**: Commercial and promotional content
- **social_media/**: Platform-optimized videos
- **animations/**: Character and object animations
- **product_demos/**: Product showcase videos
- **tutorials/**: How-to and instructional content
- **by_quality/**: Organized by resolution (480p, 720p, 1080p, 4k)
- **by_model/**: Organized by generation model used
- **by_date/**: Chronological organization backup

## Models Available:
- **Wan2.1-VACE-14B**: Highest quality (14B parameters)
- **FusioniX**: 50% faster, cinematic quality
- **MultiTalk**: Multi-character conversations with lip-sync
- **Wan2GP**: Low-VRAM accessibility platform

## File Naming:
`pb_vid_{model}_{category}_{YYYYMMDD_HHMMSS}_{unique_id}.mp4`
""",
        
        'audio': """# 🎵 Pareng Boyong Generated Audio

This folder contains all audio generated by Pareng Boyong's multi-TTS and music generation system.

## Subfolders:
- **music/**: Original music compositions by category
  - ambient/, upbeat/, cinematic/, folk/, electronic/, classical/
- **voiceovers/**: Generated speech in multiple languages
  - english/, filipino/, multilingual/, character_voices/, professional/
- **sound_effects/**: Audio effects and ambient sounds
- **podcasts/**: Long-form audio content
- **by_date/**: Chronological organization backup

## Generated Using:
- **MusicGen**: Facebook's music composition AI
- **ElevenLabs**: Professional voice synthesis (29+ languages)
- **ToucanTTS**: Filipino/Tagalog native pronunciation
- **Bark TTS**: Emotional speech expressions

## File Naming:
`pb_audio_{type}_{category}_{YYYYMMDD_HHMMSS}_{unique_id}.wav`
""",
        
        'projects': """# 📁 Pareng Boyong Projects

This folder contains organized projects and collections of generated content.

## Subfolders:
- **completed/**: Finished multimedia projects
- **in_progress/**: Projects currently being worked on
- **templates/**: Reusable project templates and workflows
- **client_work/**: Professional client deliverables
- **personal/**: Personal creative projects

## Project Structure:
Each project folder contains:
- Generated assets (images, videos, audio)
- Project metadata and parameters
- Source prompts and generation logs
- Export-ready versions

## File Naming:
`pb_project_{name}_{YYYYMMDD_HHMMSS}/`
"""
    }
    
    return descriptions.get(folder_name, f"# {folder_name.title()} Folder\n\nGenerated content organized by Pareng Boyong.")

if __name__ == "__main__":
    deliverables_path, config_path = create_deliverables_structure()
    print(f"\n🎉 Pareng Boyong deliverables structure ready!")
    print(f"📁 Location: {deliverables_path}")
    print(f"⚙️ Config: {config_path}")