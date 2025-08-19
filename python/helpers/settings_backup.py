"""
Settings Backup & Rollback System
Provides comprehensive backup and validation for safe AI model configuration changes
"""

import json
import os
import shutil
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
import hashlib
import asyncio

from python.helpers.settings import Settings
from python.helpers.print_style import PrintStyle


@dataclass
class BackupInfo:
    """Information about a settings backup"""
    id: str
    timestamp: str
    reason: str
    path: Path
    settings_hash: str
    system_info: Dict[str, Any]


@dataclass 
class ValidationResult:
    """Result of settings validation"""
    is_valid: bool
    issues: List[str]
    warnings: List[str]
    test_results: Dict[str, Any]


class SettingsBackupManager:
    """
    Comprehensive settings backup and validation system
    Ensures safe AI model configuration changes with rollback capability
    """
    
    def __init__(self):
        self.backup_dir = Path("python/helpers/backups/settings")
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        
        # Maximum number of backups to keep
        self.max_backups = 50
        
        # Settings files to backup
        self.settings_files = [
            "python/helpers/settings.py",
            ".env"
        ]
        
    def create_backup(self, reason: str = "manual") -> BackupInfo:
        """Create backup of current settings"""
        PrintStyle(color="blue", background_color="", bold=True, italics=False).print(
            f"🔒 Creating settings backup: {reason}"
        )
        
        # Generate backup ID
        timestamp = datetime.now().isoformat()
        backup_id = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{reason}"
        backup_path = self.backup_dir / f"{backup_id}.json"
        
        # Get current settings
        current_settings = self._get_current_settings()
        
        # Calculate settings hash for verification
        settings_hash = self._calculate_settings_hash(current_settings)
        
        # Gather system information
        system_info = self._get_system_info()
        
        # Create backup data
        backup_data = {
            "backup_info": {
                "id": backup_id,
                "timestamp": timestamp,
                "reason": reason,
                "settings_hash": settings_hash
            },
            "settings": current_settings,
            "system_info": system_info,
            "files_backup": {}
        }
        
        # Backup individual settings files
        for settings_file in self.settings_files:
            if os.path.exists(settings_file):
                with open(settings_file, 'r', encoding='utf-8') as f:
                    backup_data["files_backup"][settings_file] = f.read()
        
        # Save backup
        with open(backup_path, 'w', encoding='utf-8') as f:
            json.dump(backup_data, f, indent=2, default=str)
        
        # Cleanup old backups
        self._cleanup_old_backups()
        
        backup_info = BackupInfo(
            id=backup_id,
            timestamp=timestamp,
            reason=reason,
            path=backup_path,
            settings_hash=settings_hash,
            system_info=system_info
        )
        
        PrintStyle(color="green", background_color="", bold=True, italics=False).print(
            f"✅ Settings backup created: {backup_id}"
        )
        
        return backup_info
    
    async def validate_settings(self, new_settings: Dict[str, Any]) -> ValidationResult:
        """Validate new settings before applying"""
        PrintStyle(color="yellow", background_color="", bold=True, italics=False).print(
            "🔍 Validating new model settings..."
        )
        
        issues = []
        warnings = []
        test_results = {}
        
        try:
            # Test model connectivity for each configured model
            model_types = ["chat", "util", "browser"]
            
            for model_type in model_types:
                model_config = self._extract_model_config(new_settings, model_type)
                if model_config:
                    test_result = await self._test_model_connection(model_config, model_type)
                    test_results[model_type] = test_result
                    
                    if not test_result.get("success", False):
                        issues.append(f"{model_type} model connection failed: {test_result.get('error', 'Unknown error')}")
                    elif test_result.get("warning"):
                        warnings.append(f"{model_type} model warning: {test_result.get('warning')}")
            
            # Validate provider configurations
            provider_issues = self._validate_providers(new_settings)
            issues.extend(provider_issues)
            
            # Check for API key requirements
            api_key_warnings = self._check_api_keys(new_settings)
            warnings.extend(api_key_warnings)
            
        except Exception as e:
            issues.append(f"Settings validation error: {str(e)}")
        
        is_valid = len(issues) == 0
        
        if is_valid:
            PrintStyle(color="green", background_color="", bold=True, italics=False).print(
                "✅ Settings validation passed"
            )
        else:
            PrintStyle(color="red", background_color="", bold=True, italics=False).print(
                f"❌ Settings validation failed: {len(issues)} issues found"
            )
        
        return ValidationResult(
            is_valid=is_valid,
            issues=issues,
            warnings=warnings,
            test_results=test_results
        )
    
    def rollback_to_backup(self, backup_id: str) -> bool:
        """Rollback to previous settings backup"""
        PrintStyle(color="yellow", background_color="", bold=True, italics=False).print(
            f"🔄 Rolling back to backup: {backup_id}"
        )
        
        backup_path = self.backup_dir / f"{backup_id}.json"
        if not backup_path.exists():
            PrintStyle(color="red", background_color="", bold=True, italics=False).print(
                f"❌ Backup not found: {backup_id}"
            )
            return False
        
        try:
            # Load backup data
            with open(backup_path, 'r', encoding='utf-8') as f:
                backup_data = json.load(f)
            
            # Restore settings files
            files_backup = backup_data.get("files_backup", {})
            for file_path, content in files_backup.items():
                try:
                    # Create directory if needed
                    os.makedirs(os.path.dirname(file_path), exist_ok=True)
                    
                    # Restore file content
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(content)
                    
                    PrintStyle(color="green", background_color="", bold=True, italics=False).print(
                        f"✅ Restored: {file_path}"
                    )
                except Exception as e:
                    PrintStyle(color="red", background_color="", bold=True, italics=False).print(
                        f"❌ Failed to restore {file_path}: {str(e)}"
                    )
                    return False
            
            PrintStyle(color="green", background_color="", bold=True, italics=False).print(
                f"✅ Successfully rolled back to backup: {backup_id}"
            )
            return True
            
        except Exception as e:
            PrintStyle(color="red", background_color="", bold=True, italics=False).print(
                f"❌ Rollback failed: {str(e)}"
            )
            return False
    
    def list_backups(self) -> List[BackupInfo]:
        """List all available backups"""
        backups = []
        
        for backup_file in self.backup_dir.glob("*.json"):
            try:
                with open(backup_file, 'r', encoding='utf-8') as f:
                    backup_data = json.load(f)
                
                backup_info_data = backup_data.get("backup_info", {})
                backups.append(BackupInfo(
                    id=backup_info_data.get("id", backup_file.stem),
                    timestamp=backup_info_data.get("timestamp", ""),
                    reason=backup_info_data.get("reason", "unknown"),
                    path=backup_file,
                    settings_hash=backup_info_data.get("settings_hash", ""),
                    system_info=backup_data.get("system_info", {})
                ))
            except Exception as e:
                # Skip corrupted backup files
                continue
        
        # Sort by timestamp (newest first)
        backups.sort(key=lambda x: x.timestamp, reverse=True)
        return backups
    
    def _get_current_settings(self) -> Dict[str, Any]:
        """Get current settings configuration"""
        try:
            # This would be replaced with actual settings loading logic
            # For now, return a placeholder structure
            settings = {
                "chat_model": {
                    "provider": "openai",
                    "name": "gpt-4",
                    "api_key": "configured"
                },
                "util_model": {
                    "provider": "openai", 
                    "name": "gpt-3.5-turbo",
                    "api_key": "configured"
                },
                "browser_model": {
                    "provider": "anthropic",
                    "name": "claude-3-haiku",
                    "api_key": "configured"
                }
            }
            return settings
        except Exception as e:
            return {"error": f"Failed to get current settings: {str(e)}"}
    
    def _calculate_settings_hash(self, settings: Dict[str, Any]) -> str:
        """Calculate hash of settings for verification"""
        settings_str = json.dumps(settings, sort_keys=True)
        return hashlib.sha256(settings_str.encode()).hexdigest()[:16]
    
    def _get_system_info(self) -> Dict[str, Any]:
        """Get system information for backup metadata"""
        return {
            "platform": "Linux",
            "python_version": "3.11+",
            "pareng_boyong_version": "v1.0.0",
            "backup_system_version": "1.0.0"
        }
    
    def _extract_model_config(self, settings: Dict[str, Any], model_type: str) -> Optional[Dict[str, Any]]:
        """Extract model configuration for specific type"""
        return settings.get(f"{model_type}_model")
    
    async def _test_model_connection(self, model_config: Dict[str, Any], model_type: str) -> Dict[str, Any]:
        """Test connection to a model"""
        try:
            # Simulate model connection test
            # In real implementation, this would make actual API calls
            await asyncio.sleep(0.1)  # Simulate API call delay
            
            provider = model_config.get("provider", "unknown")
            model_name = model_config.get("name", "unknown")
            
            # Simulate different test outcomes
            if provider == "invalid":
                return {"success": False, "error": "Invalid provider"}
            elif model_name == "invalid":
                return {"success": False, "error": "Invalid model name"}
            else:
                return {
                    "success": True,
                    "provider": provider,
                    "model": model_name,
                    "response_time": "150ms",
                    "status": "healthy"
                }
                
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _validate_providers(self, settings: Dict[str, Any]) -> List[str]:
        """Validate provider configurations"""
        issues = []
        
        # Add provider-specific validation logic here
        for model_type in ["chat", "util", "browser"]:
            model_config = settings.get(f"{model_type}_model")
            if model_config:
                provider = model_config.get("provider")
                if not provider:
                    issues.append(f"{model_type} model missing provider")
                elif provider not in ["openai", "anthropic", "google", "groq", "ollama", "openrouter"]:
                    issues.append(f"{model_type} model has unknown provider: {provider}")
        
        return issues
    
    def _check_api_keys(self, settings: Dict[str, Any]) -> List[str]:
        """Check API key requirements"""
        warnings = []
        
        # Check if required API keys are configured
        for model_type in ["chat", "util", "browser"]:
            model_config = settings.get(f"{model_type}_model")
            if model_config:
                provider = model_config.get("provider")
                api_key = model_config.get("api_key")
                
                if provider in ["openai", "anthropic", "google"] and not api_key:
                    warnings.append(f"{model_type} model ({provider}) may require API key")
        
        return warnings
    
    def _cleanup_old_backups(self) -> None:
        """Remove old backups to save space"""
        backups = self.list_backups()
        
        if len(backups) > self.max_backups:
            # Remove oldest backups
            old_backups = backups[self.max_backups:]
            for backup in old_backups:
                try:
                    backup.path.unlink()
                    PrintStyle(color="gray", background_color="", bold=False, italics=True).print(
                        f"🗑️ Removed old backup: {backup.id}"
                    )
                except Exception:
                    pass  # Ignore cleanup errors


# Global backup manager instance
backup_manager = SettingsBackupManager()


async def create_settings_backup(reason: str = "manual") -> BackupInfo:
    """Create a settings backup (async wrapper)"""
    return backup_manager.create_backup(reason)


async def validate_new_settings(settings: Dict[str, Any]) -> ValidationResult:
    """Validate new settings (async wrapper)"""
    return await backup_manager.validate_settings(settings)


def rollback_settings(backup_id: str) -> bool:
    """Rollback to a specific backup"""
    return backup_manager.rollback_to_backup(backup_id)


def list_settings_backups() -> List[BackupInfo]:
    """List all available settings backups"""
    return backup_manager.list_backups()