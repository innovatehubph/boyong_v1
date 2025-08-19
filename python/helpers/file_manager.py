"""
File Management Helper for Pareng Boyong Deliverables
Handles organized storage and retrieval of generated content
"""

import os
import json
import shutil
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any, List
import uuid

class ParengBoyongFileManager:
    def __init__(self):
        self.base_path = Path('/root/projects/pareng-boyong')
        self.deliverables_root = self.base_path / 'pareng_boyong_deliverables'
        self.config_path = self.deliverables_root / 'deliverables_config.json'
        self.config = self._load_config()
        
    def _load_config(self) -> Dict[str, Any]:
        """Load deliverables configuration"""
        try:
            if self.config_path.exists():
                with open(self.config_path, 'r') as f:
                    return json.load(f)
            else:
                return self._create_default_config()
        except Exception as e:
            print(f"Warning: Could not load config: {e}")
            return self._create_default_config()
    
    def _create_default_config(self) -> Dict[str, Any]:
        """Create default configuration if none exists"""
        return {
            "pareng_boyong_deliverables_config": {
                "version": "1.0.0",
                "base_path": str(self.deliverables_root),
                "file_naming_conventions": {
                    "images": "pb_img_{category}_{timestamp}_{id}.{ext}",
                    "videos": "pb_vid_{model}_{category}_{timestamp}_{id}.{ext}",
                    "audio": "pb_audio_{type}_{category}_{timestamp}_{id}.{ext}"
                }
            }
        }
    
    def _generate_timestamp(self) -> str:
        """Generate timestamp for file naming"""
        return datetime.now().strftime("%Y%m%d_%H%M%S")
    
    def _generate_unique_id(self) -> str:
        """Generate unique ID for file naming"""
        return str(uuid.uuid4())[:8]
    
    def save_image(
        self, 
        image_data: bytes, 
        category: str = "general", 
        filename: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, str]:
        """
        Save generated image to organized folder structure
        
        Args:
            image_data: Raw image bytes
            category: Image category (portraits, landscapes, artwork, etc.)
            filename: Optional custom filename
            metadata: Generation metadata
            
        Returns:
            Dict with file paths and info
        """
        
        # Determine category folder
        category_map = {
            "portrait": "portraits",
            "landscape": "landscapes", 
            "artwork": "artwork",
            "product": "product_photos",
            "social": "social_media",
            "thumbnail": "thumbnails",
            "logo": "logos_branding",
            "educational": "educational",
            "general": "artwork"  # Default fallback
        }
        
        folder_category = category_map.get(category.lower(), "artwork")
        
        # Create paths
        category_path = self.deliverables_root / "images" / folder_category
        date_path = self.deliverables_root / "images" / "by_date" / str(datetime.now().year) / f"{datetime.now().month:02d}"
        
        # Ensure directories exist
        category_path.mkdir(parents=True, exist_ok=True)
        date_path.mkdir(parents=True, exist_ok=True)
        
        # Generate filename if not provided
        if not filename:
            timestamp = self._generate_timestamp()
            unique_id = self._generate_unique_id()
            filename = f"pb_img_{folder_category}_{timestamp}_{unique_id}.png"
        
        # Save to category folder (primary location)
        primary_path = category_path / filename
        with open(primary_path, 'wb') as f:
            f.write(image_data)
        
        # Save to date folder (backup/reference)
        date_backup_path = date_path / filename
        shutil.copy2(primary_path, date_backup_path)
        
        # Save metadata if provided
        if metadata:
            metadata_file = primary_path.with_suffix('.json')
            with open(metadata_file, 'w') as f:
                json.dump({
                    "generation_metadata": metadata,
                    "file_info": {
                        "created": datetime.now().isoformat(),
                        "category": category,
                        "size_bytes": len(image_data),
                        "primary_path": str(primary_path),
                        "backup_path": str(date_backup_path)
                    }
                }, f, indent=2)
        
        return {
            "primary_path": str(primary_path),
            "backup_path": str(date_backup_path),
            "category": folder_category,
            "filename": filename,
            "size_bytes": len(image_data),
            "url_path": f"/deliverables/images/{folder_category}/{filename}"
        }
    
    def save_video(
        self,
        video_data: bytes,
        model_used: str,
        category: str = "general",
        filename: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, str]:
        """
        Save generated video to organized folder structure
        
        Args:
            video_data: Raw video bytes
            model_used: AI model used (wan_vace_14b, fusionix, multitalk, etc.)
            category: Video category (cinematic, conversational, educational, etc.)
            filename: Optional custom filename
            metadata: Generation metadata
            
        Returns:
            Dict with file paths and info
        """
        
        # Determine category folder
        category_map = {
            "cinematic": "cinematic",
            "conversation": "conversational",
            "dialogue": "conversational", 
            "educational": "educational",
            "marketing": "marketing",
            "social": "social_media",
            "animation": "animations",
            "product": "product_demos",
            "tutorial": "tutorials",
            "general": "cinematic"  # Default fallback
        }
        
        folder_category = category_map.get(category.lower(), "cinematic")
        
        # Create paths
        category_path = self.deliverables_root / "videos" / folder_category
        model_path = self.deliverables_root / "videos" / "by_model" / model_used.lower()
        date_path = self.deliverables_root / "videos" / "by_date" / str(datetime.now().year) / f"{datetime.now().month:02d}"
        
        # Ensure directories exist
        category_path.mkdir(parents=True, exist_ok=True)
        model_path.mkdir(parents=True, exist_ok=True)
        date_path.mkdir(parents=True, exist_ok=True)
        
        # Generate filename if not provided
        if not filename:
            timestamp = self._generate_timestamp()
            unique_id = self._generate_unique_id()
            filename = f"pb_vid_{model_used}_{folder_category}_{timestamp}_{unique_id}.mp4"
        
        # Save to category folder (primary location)
        primary_path = category_path / filename
        with open(primary_path, 'wb') as f:
            f.write(video_data)
        
        # Save to model folder (organized by AI model)
        model_backup_path = model_path / filename
        shutil.copy2(primary_path, model_backup_path)
        
        # Save to date folder (chronological backup)
        date_backup_path = date_path / filename
        shutil.copy2(primary_path, date_backup_path)
        
        # Save metadata if provided
        if metadata:
            metadata_file = primary_path.with_suffix('.json')
            with open(metadata_file, 'w') as f:
                json.dump({
                    "generation_metadata": metadata,
                    "file_info": {
                        "created": datetime.now().isoformat(),
                        "model_used": model_used,
                        "category": category,
                        "size_bytes": len(video_data),
                        "primary_path": str(primary_path),
                        "model_backup_path": str(model_backup_path),
                        "date_backup_path": str(date_backup_path)
                    }
                }, f, indent=2)
        
        return {
            "primary_path": str(primary_path),
            "model_backup_path": str(model_backup_path),
            "date_backup_path": str(date_backup_path),
            "category": folder_category,
            "model_used": model_used,
            "filename": filename,
            "size_bytes": len(video_data),
            "url_path": f"/deliverables/videos/{folder_category}/{filename}"
        }
    
    def save_audio(
        self,
        audio_data: bytes,
        audio_type: str,
        category: str = "general",
        filename: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, str]:
        """
        Save generated audio to organized folder structure
        
        Args:
            audio_data: Raw audio bytes
            audio_type: Type of audio (music, voice, effect)
            category: Audio category (ambient, professional, character, etc.)
            filename: Optional custom filename
            metadata: Generation metadata
            
        Returns:
            Dict with file paths and info
        """
        
        # Determine base type folder
        if audio_type.lower() in ["music", "song", "composition"]:
            base_folder = "music"
            category_map = {
                "ambient": "ambient",
                "upbeat": "upbeat", 
                "cinematic": "cinematic",
                "folk": "folk",
                "electronic": "electronic",
                "classical": "classical",
                "general": "ambient"
            }
        elif audio_type.lower() in ["voice", "speech", "voiceover", "narration"]:
            base_folder = "voiceovers"
            category_map = {
                "english": "english",
                "filipino": "filipino",
                "character": "character_voices",
                "professional": "professional",
                "educational": "educational",
                "general": "professional"
            }
        else:
            base_folder = "sound_effects"
            category_map = {"general": ""}
        
        folder_category = category_map.get(category.lower(), list(category_map.values())[0])
        
        # Create paths
        if folder_category:
            category_path = self.deliverables_root / "audio" / base_folder / folder_category
        else:
            category_path = self.deliverables_root / "audio" / base_folder
            
        date_path = self.deliverables_root / "audio" / "by_date" / str(datetime.now().year) / f"{datetime.now().month:02d}"
        
        # Ensure directories exist
        category_path.mkdir(parents=True, exist_ok=True)
        date_path.mkdir(parents=True, exist_ok=True)
        
        # Generate filename if not provided
        if not filename:
            timestamp = self._generate_timestamp()
            unique_id = self._generate_unique_id()
            filename = f"pb_audio_{audio_type}_{category}_{timestamp}_{unique_id}.wav"
        
        # Save to category folder (primary location)
        primary_path = category_path / filename
        with open(primary_path, 'wb') as f:
            f.write(audio_data)
        
        # Save to date folder (backup/reference)
        date_backup_path = date_path / filename
        shutil.copy2(primary_path, date_backup_path)
        
        # Save metadata if provided
        if metadata:
            metadata_file = primary_path.with_suffix('.json')
            with open(metadata_file, 'w') as f:
                json.dump({
                    "generation_metadata": metadata,
                    "file_info": {
                        "created": datetime.now().isoformat(),
                        "audio_type": audio_type,
                        "category": category,
                        "size_bytes": len(audio_data),
                        "primary_path": str(primary_path),
                        "backup_path": str(date_backup_path)
                    }
                }, f, indent=2)
        
        return {
            "primary_path": str(primary_path),
            "backup_path": str(date_backup_path),
            "category": folder_category,
            "audio_type": audio_type,
            "filename": filename,
            "size_bytes": len(audio_data),
            "url_path": f"/deliverables/audio/{base_folder}/{folder_category}/{filename}" if folder_category else f"/deliverables/audio/{base_folder}/{filename}"
        }
    
    def list_files(self, content_type: str, category: Optional[str] = None, limit: int = 50) -> List[Dict[str, Any]]:
        """
        List generated files by type and category
        
        Args:
            content_type: "images", "videos", or "audio"
            category: Optional category filter
            limit: Maximum number of files to return
            
        Returns:
            List of file information dictionaries
        """
        
        base_path = self.deliverables_root / content_type
        if not base_path.exists():
            return []
        
        files = []
        search_paths = []
        
        if category:
            category_path = base_path / category
            if category_path.exists():
                search_paths = [category_path]
        else:
            # Search all category folders
            search_paths = [p for p in base_path.iterdir() if p.is_dir() and p.name != "by_date"]
        
        for search_path in search_paths:
            for file_path in search_path.rglob("*"):
                if file_path.is_file() and not file_path.name.startswith('.') and not file_path.suffix == '.json':
                    
                    # Get metadata if exists
                    metadata_path = file_path.with_suffix('.json')
                    metadata = {}
                    if metadata_path.exists():
                        try:
                            with open(metadata_path, 'r') as f:
                                metadata = json.load(f)
                        except:
                            pass
                    
                    file_info = {
                        "filename": file_path.name,
                        "path": str(file_path),
                        "category": search_path.name,
                        "size_bytes": file_path.stat().st_size,
                        "created": datetime.fromtimestamp(file_path.stat().st_ctime).isoformat(),
                        "modified": datetime.fromtimestamp(file_path.stat().st_mtime).isoformat(),
                        "metadata": metadata.get("generation_metadata", {}),
                        "url_path": f"/deliverables/{content_type}/{search_path.name}/{file_path.name}"
                    }
                    
                    files.append(file_info)
        
        # Sort by creation date (newest first) and limit
        files.sort(key=lambda x: x["created"], reverse=True)
        return files[:limit]
    
    def get_storage_stats(self) -> Dict[str, Any]:
        """Get storage statistics for deliverables"""
        
        stats = {
            "total_files": 0,
            "total_size_bytes": 0,
            "by_type": {
                "images": {"count": 0, "size_bytes": 0},
                "videos": {"count": 0, "size_bytes": 0},
                "audio": {"count": 0, "size_bytes": 0}
            },
            "recent_activity": [],
            "top_categories": {}
        }
        
        for content_type in ["images", "videos", "audio"]:
            type_path = self.deliverables_root / content_type
            if type_path.exists():
                for file_path in type_path.rglob("*"):
                    if file_path.is_file() and not file_path.name.startswith('.') and not file_path.suffix == '.json':
                        file_size = file_path.stat().st_size
                        stats["total_files"] += 1
                        stats["total_size_bytes"] += file_size
                        stats["by_type"][content_type]["count"] += 1
                        stats["by_type"][content_type]["size_bytes"] += file_size
                        
                        # Track recent activity (last 7 days)
                        file_age = datetime.now() - datetime.fromtimestamp(file_path.stat().st_ctime)
                        if file_age.days <= 7:
                            stats["recent_activity"].append({
                                "filename": file_path.name,
                                "type": content_type,
                                "created": datetime.fromtimestamp(file_path.stat().st_ctime).isoformat()
                            })
        
        # Sort recent activity
        stats["recent_activity"].sort(key=lambda x: x["created"], reverse=True)
        stats["recent_activity"] = stats["recent_activity"][:20]  # Last 20 files
        
        return stats

# Global instance
file_manager = ParengBoyongFileManager()