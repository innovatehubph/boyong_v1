#!/usr/bin/env python3
"""
Create Comprehensive Backup of Pareng Boyong v1
Before implementing AI model configuration enhancements
"""

import os
import shutil
import json
from datetime import datetime
from pathlib import Path
import subprocess
import hashlib

def create_comprehensive_backup():
    """Create complete backup of current Pareng Boyong state"""
    
    print("🔒 Creating Comprehensive Pareng Boyong v1 Backup")
    print("=" * 60)
    
    # Create backup directory with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_dir = Path(f"/root/projects/pareng-boyong-backup-{timestamp}")
    backup_dir.mkdir(exist_ok=True)
    
    # Create backup metadata
    backup_metadata = {
        "backup_info": {
            "created": datetime.now().isoformat(),
            "version": "Pareng Boyong v1 - Pre Model Enhancement",
            "purpose": "Backup before AI model configuration enhancement",
            "location": str(backup_dir),
            "creator": "Claude Code Assistant"
        },
        "system_state": {
            "multimodal_system": "Complete - 6 tools implemented",
            "advanced_video": "Complete - 4 cutting-edge models",
            "file_management": "Complete - Organized deliverables system",
            "token_optimization": "Complete - Smart compression system",
            "mobile_support": "Complete - Responsive glassmorphism UI"
        },
        "files_backed_up": [],
        "directories_backed_up": [],
        "checksums": {}
    }
    
    # Critical files and directories to backup
    critical_items = [
        # Core system files
        "agent.py",
        "models.py", 
        "main.py",
        "webui.py",
        
        # Configuration and settings
        "python/helpers/settings.py",
        ".env",
        
        # Complete Python helpers
        "python/helpers/",
        
        # All multimodal tools
        "python/tools/",
        
        # Enhanced documentation
        "CLAUDE.md",
        "PARENG_BOYONG_ENHANCED.md", 
        "ADVANCED_VIDEO_SYSTEM.md",
        "AI_IMPLEMENTATION_ARCHITECTURE.md",
        "AI_MODEL_ENHANCEMENT_PLAN.md",
        "PROJECT_COMPLETION_REPORT.md",
        
        # Multimodal services
        "install_multimodal.py",
        "install_advanced_video.py",
        "multimodal_services/",
        "advanced_video_services/",
        
        # File management system
        "pareng_boyong_deliverables/",
        "python/helpers/file_manager.py",
        
        # Web UI and interface
        "webui/",
        "original-webui/",
        
        # Installation and configuration
        "requirements*.txt",
        "package*.json",
        
        # Test and validation files
        "test_*.py",
        "simple_*.py",
        "verify_*.py",
        
        # Documentation and knowledge
        "docs/",
        "knowledge/",
        
        # Project structure
        "prompts/",
        "memory/",
        
        # Any additional enhancement files
        "create_*.py"
    ]
    
    print("\n📁 Backing up critical files and directories...")
    
    for item in critical_items:
        source_path = Path("/root/projects/pareng-boyong") / item
        
        if source_path.exists():
            relative_path = item
            dest_path = backup_dir / relative_path
            
            try:
                if source_path.is_file():
                    # Backup file
                    dest_path.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(source_path, dest_path)
                    
                    # Calculate checksum
                    with open(source_path, 'rb') as f:
                        checksum = hashlib.md5(f.read()).hexdigest()
                    backup_metadata["checksums"][str(relative_path)] = checksum
                    backup_metadata["files_backed_up"].append(str(relative_path))
                    
                    print(f"  ✅ File: {relative_path}")
                    
                elif source_path.is_dir():
                    # Backup directory
                    if dest_path.exists():
                        shutil.rmtree(dest_path)
                    shutil.copytree(source_path, dest_path, symlinks=False, ignore_dangling_symlinks=True)
                    backup_metadata["directories_backed_up"].append(str(relative_path))
                    
                    print(f"  ✅ Dir:  {relative_path}/")
                    
            except Exception as e:
                print(f"  ⚠️ Warning: Could not backup {relative_path}: {e}")
        else:
            print(f"  ⚠️ Not found: {relative_path}")
    
    # Create system information
    print("\n🖥️ Gathering system information...")
    
    system_info = {
        "platform": "Linux",
        "python_version": None,
        "git_status": None,
        "disk_usage": None,
        "installed_packages": None
    }
    
    try:
        # Python version
        result = subprocess.run(["python", "--version"], capture_output=True, text=True)
        if result.returncode == 0:
            system_info["python_version"] = result.stdout.strip()
            
        # Git status
        result = subprocess.run(["git", "status", "--porcelain"], 
                              cwd="/root/projects/pareng-boyong", 
                              capture_output=True, text=True)
        if result.returncode == 0:
            system_info["git_status"] = result.stdout.strip()
            
        # Disk usage
        result = subprocess.run(["du", "-sh", "/root/projects/pareng-boyong"], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            system_info["disk_usage"] = result.stdout.strip()
            
        # Installed packages (first 50)
        result = subprocess.run(["pip", "list"], capture_output=True, text=True)
        if result.returncode == 0:
            lines = result.stdout.strip().split('\n')
            system_info["installed_packages"] = lines[:50]  # Limit for backup size
            
    except Exception as e:
        print(f"  ⚠️ Could not gather some system info: {e}")
    
    backup_metadata["system_info"] = system_info
    
    # Save backup metadata
    metadata_file = backup_dir / "backup_metadata.json"
    with open(metadata_file, 'w') as f:
        json.dump(backup_metadata, f, indent=2)
    
    # Create backup summary
    summary_file = backup_dir / "BACKUP_SUMMARY.md"
    with open(summary_file, 'w') as f:
        f.write(f"""# 🔒 Pareng Boyong v1 Backup Summary

## Backup Information
- **Created**: {backup_metadata['backup_info']['created']}
- **Version**: {backup_metadata['backup_info']['version']}
- **Purpose**: {backup_metadata['backup_info']['purpose']}
- **Location**: {backup_metadata['backup_info']['location']}

## System State at Backup
- **Multimodal System**: {backup_metadata['system_state']['multimodal_system']}
- **Advanced Video**: {backup_metadata['system_state']['advanced_video']}
- **File Management**: {backup_metadata['system_state']['file_management']}
- **Token Optimization**: {backup_metadata['system_state']['token_optimization']}
- **Mobile Support**: {backup_metadata['system_state']['mobile_support']}

## Backup Contents
- **Files Backed Up**: {len(backup_metadata['files_backed_up'])}
- **Directories Backed Up**: {len(backup_metadata['directories_backed_up'])}
- **Checksums Calculated**: {len(backup_metadata['checksums'])}

## System Information
- **Platform**: {system_info.get('platform', 'Unknown')}
- **Python Version**: {system_info.get('python_version', 'Unknown')}
- **Disk Usage**: {system_info.get('disk_usage', 'Unknown')}

## What's Backed Up
### Core Files:
{chr(10).join(['- ' + f for f in backup_metadata['files_backed_up'][:20]])}
{'- ... and more' if len(backup_metadata['files_backed_up']) > 20 else ''}

### Directories:
{chr(10).join(['- ' + d + '/' for d in backup_metadata['directories_backed_up']])}

## Next Steps
This backup was created before implementing AI model configuration enhancements.
The backup will be uploaded to GitHub repository 'boyong_v1' for version control.

## Restoration
To restore from this backup:
1. Copy contents back to `/root/projects/pareng-boyong/`
2. Verify checksums using `backup_metadata.json`
3. Reinstall dependencies from `requirements.txt`
4. Test system functionality

🎉 **Pareng Boyong v1 - Complete multimodal AI system with world-class capabilities!**
""")
    
    # Calculate total backup size
    total_size = sum(f.stat().st_size for f in backup_dir.rglob('*') if f.is_file())
    size_mb = total_size / (1024 * 1024)
    
    print(f"\n📊 Backup Summary:")
    print(f"   📁 Location: {backup_dir}")
    print(f"   📄 Files: {len(backup_metadata['files_backed_up'])} files")
    print(f"   📂 Directories: {len(backup_metadata['directories_backed_up'])} directories") 
    print(f"   💾 Size: {size_mb:.1f} MB")
    print(f"   🔐 Checksums: {len(backup_metadata['checksums'])} calculated")
    
    print(f"\n✅ Comprehensive backup completed successfully!")
    print(f"📍 Backup location: {backup_dir}")
    
    return str(backup_dir), backup_metadata

if __name__ == "__main__":
    backup_path, metadata = create_comprehensive_backup()
    print(f"\n🎉 Pareng Boyong v1 backup ready for GitHub repository creation!")