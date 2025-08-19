import os
from pathlib import Path
import shutil
import base64
from typing import Dict, List, Tuple, Optional, Any
import zipfile
from werkzeug.utils import secure_filename
from datetime import datetime

from python.helpers import files, runtime
from python.helpers.print_style import PrintStyle

class EnhancedFileBrowser:
    """
    Enhanced File Browser for Pareng Boyong with full VPS file system access
    
    Provides secure access to the entire VPS file system while maintaining
    appropriate security controls and preventing dangerous operations.
    """
    
    ALLOWED_EXTENSIONS = {
        'image': {'jpg', 'jpeg', 'png', 'bmp', 'gif', 'webp', 'svg'},
        'code': {'py', 'js', 'sh', 'html', 'css', 'ts', 'jsx', 'tsx', 'vue', 'php', 'rb', 'go', 'rs', 'cpp', 'c', 'h', 'java'},
        'document': {'md', 'pdf', 'txt', 'csv', 'json', 'yaml', 'yml', 'xml', 'log'},
        'config': {'conf', 'config', 'ini', 'env', 'properties'},
        'archive': {'zip', 'tar', 'gz', 'rar', '7z', 'bz2', 'xz'},
        'video': {'mp4', 'avi', 'mkv', 'mov', 'wmv', 'flv', 'webm'},
        'audio': {'mp3', 'wav', 'ogg', 'flac', 'm4a', 'wma'}
    }

    MAX_FILE_SIZE = 500 * 1024 * 1024  # 500MB increased from 100MB
    
    # Predefined safe navigation roots based on CLAUDE.md
    NAVIGATION_ROOTS = {
        "$VPS_ROOT": "/",
        "$A0": "/a0",
        "$VPS_WWW": "/var/www", 
        "$VPS_ROOT_HOME": "/root",
        "$VPS_TMP": "/tmp",
        "$WORK_DIR": "/",  # Full VPS access instead of restricting to /a0
        "$PROJECTS": "/a0/pareng-boyong-projects",
        "$DELIVERABLES": "/a0/pareng_boyong_deliverables",
        "$WEBAPPS": "/var/www",
        "$HOME": "/root",
        "$USR": "/usr",
        "$OPT": "/opt",
        "$ETC": "/etc"
    }
    
    # Directories to hide for security (sensitive system dirs)
    HIDDEN_DIRS = {
        '/proc', '/sys', '/dev', '/run', '/boot',
        '/lost+found', '/snap', '/media', '/mnt'
    }
    
    # Directories to mark as protected (show but warn before editing)
    PROTECTED_DIRS = {
        '/etc', '/usr', '/var/lib', '/var/log', '/opt'
    }

    def __init__(self):
        self.current_root = "/"  # Allow full VPS access
        self.base_dir = Path("/")  # VPS root
        
    def _is_hidden_path(self, path_str: str) -> bool:
        """Check if a path should be hidden from the file browser"""
        path = Path(path_str)
        
        # Check if any parent is in hidden dirs
        for hidden in self.HIDDEN_DIRS:
            if str(path).startswith(hidden):
                return True
                
        # Hide dot files in root directories (but allow in user dirs)
        if path.name.startswith('.') and len(path.parts) <= 2:
            return True
            
        return False
        
    def _is_protected_path(self, path_str: str) -> bool:
        """Check if a path is protected (show warning)"""
        for protected in self.PROTECTED_DIRS:
            if str(path_str).startswith(protected):
                return True
        return False

    def _get_navigation_root(self, root_alias: str) -> str:
        """Convert root alias to actual path"""
        if root_alias in self.NAVIGATION_ROOTS:
            return self.NAVIGATION_ROOTS[root_alias]
        return root_alias if os.path.exists(root_alias) else "/"

    def _check_file_size(self, file) -> bool:
        try:
            file.seek(0, os.SEEK_END)
            size = file.tell()
            file.seek(0)
            return size <= self.MAX_FILE_SIZE
        except (AttributeError, IOError):
            return False

    def _sanitize_path(self, path: str) -> str:
        """Sanitize path while allowing VPS access"""
        if not path:
            return ""
            
        # Handle root aliases
        if path in self.NAVIGATION_ROOTS:
            path = self.NAVIGATION_ROOTS[path]
            
        # Convert to absolute path
        abs_path = os.path.abspath(path)
        
        # Ensure it's a valid path
        try:
            Path(abs_path).resolve()
            return abs_path
        except:
            return "/"  # Fallback to VPS root for full access

    def save_file_b64(self, current_path: str, filename: str, base64_content: str):
        try:
            # Sanitize paths
            current_path = self._sanitize_path(current_path)
            target_file = Path(current_path) / secure_filename(filename)
            
            # Check if target directory is protected
            if self._is_protected_path(str(target_file.parent)):
                PrintStyle.warning(f"Writing to protected directory: {target_file.parent}")
            
            os.makedirs(target_file.parent, exist_ok=True)
            
            # Save file
            with open(target_file, "wb") as file:
                file.write(base64.b64decode(base64_content))
            return True
            
        except Exception as e:
            PrintStyle.error(f"Error saving file {filename}: {e}")
            return False

    def save_files(self, files: List, current_path: str = "") -> Tuple[List[str], List[str]]:
        """Save uploaded files and return successful and failed filenames"""
        successful = []
        failed = []
        
        try:
            # Sanitize the target directory path
            target_dir = Path(self._sanitize_path(current_path))
            
            # Check if we're writing to a protected directory
            if self._is_protected_path(str(target_dir)):
                PrintStyle.warning(f"Uploading to protected directory: {target_dir}")
                
            os.makedirs(target_dir, exist_ok=True)
            
            for file in files:
                try:
                    if file and self._is_allowed_file(file.filename, file):
                        filename = secure_filename(file.filename)
                        file_path = target_dir / filename

                        file.save(str(file_path))
                        successful.append(filename)
                    else:
                        failed.append(file.filename)
                except Exception as e:
                    PrintStyle.error(f"Error saving file {file.filename}: {e}")
                    failed.append(file.filename)
                    
            return successful, failed
            
        except Exception as e:
            PrintStyle.error(f"Error in save_files: {e}")
            return successful, failed

    def delete_file(self, file_path: str) -> bool:
        """Delete a file or directory with protection checks"""
        try:
            # Sanitize path
            full_path = Path(self._sanitize_path(file_path))
            
            # Prevent deletion of critical system files
            critical_paths = {'/bin', '/sbin', '/usr/bin', '/usr/sbin', '/etc/passwd', '/etc/shadow'}
            if any(str(full_path).startswith(critical) for critical in critical_paths):
                PrintStyle.error(f"Cannot delete critical system path: {full_path}")
                return False
                
            # Check if it's a protected directory
            if self._is_protected_path(str(full_path)):
                PrintStyle.warning(f"Deleting from protected directory: {full_path}")
                
            if os.path.exists(full_path):
                if os.path.isfile(full_path):
                    os.remove(full_path)
                elif os.path.isdir(full_path):
                    shutil.rmtree(full_path)
                return True
                
            return False
            
        except Exception as e:
            PrintStyle.error(f"Error deleting {file_path}: {e}")
            return False

    def _is_allowed_file(self, filename: str, file) -> bool:
        """Enhanced file validation with better security"""
        if not filename:
            return False
            
        # Check file size
        if not self._check_file_size(file):
            return False
            
        # Allow most files but block dangerous executables
        dangerous_exts = {'exe', 'msi', 'deb', 'rpm', 'dmg', 'pkg'}
        ext = self._get_file_extension(filename)
        
        if ext in dangerous_exts:
            return False
            
        return True

    def _get_file_extension(self, filename: str) -> str:
        return filename.rsplit('.', 1)[1].lower() if '.' in filename else ''
        
    def get_files(self, current_path: str = "") -> Dict:
        """Enhanced file listing with VPS-wide access"""
        try:
            # Handle root aliases and sanitize path
            if current_path == "$WORK_DIR":
                current_path = "/"
            elif current_path in self.NAVIGATION_ROOTS:
                current_path = self.NAVIGATION_ROOTS[current_path]
            
            full_path = Path(self._sanitize_path(current_path))
            
            files = []
            folders = []

            # List all entries in the current directory
            try:
                entries = list(os.scandir(full_path))
            except PermissionError:
                PrintStyle.warning(f"Permission denied accessing: {full_path}")
                return {"entries": [], "current_path": str(current_path), "parent_path": str(full_path.parent) if full_path != Path("/") else ""}

            for entry in entries:
                # Skip hidden paths
                if self._is_hidden_path(entry.path):
                    continue
                    
                try:
                    stat_info = entry.stat()
                    relative_path = str(Path(entry.path))
                    
                    entry_data: Dict[str, Any] = {
                        "name": entry.name,
                        "path": relative_path,
                        "modified": datetime.fromtimestamp(stat_info.st_mtime).isoformat(),
                        "protected": self._is_protected_path(entry.path)
                    }

                    if entry.is_file():
                        entry_data.update({
                            "type": self._get_file_type(entry.name),
                            "size": stat_info.st_size,
                            "is_dir": False
                        })
                        files.append(entry_data)
                    elif entry.is_dir():
                        # Get directory size (file count for performance)
                        try:
                            dir_count = len(list(os.scandir(entry.path)))
                        except (PermissionError, OSError):
                            dir_count = 0
                            
                        entry_data.update({
                            "type": "folder",
                            "size": dir_count,  # Show file count instead of bytes
                            "is_dir": True
                        })
                        folders.append(entry_data)
                        
                except (OSError, PermissionError) as e:
                    # Skip files we can't access
                    continue

            # Combine folders and files, folders first
            all_entries = folders + files

            # Get parent directory path
            parent_path = ""
            if str(full_path) != "/":
                parent_path = str(full_path.parent)

            return {
                "entries": all_entries,
                "current_path": str(current_path),
                "parent_path": parent_path,
                "navigation_roots": self.NAVIGATION_ROOTS
            }

        except Exception as e:
            PrintStyle.error(f"Error reading directory {current_path}: {e}")
            return {"entries": [], "current_path": current_path, "parent_path": ""}
        
    def get_full_path(self, file_path: str, allow_dir: bool = False) -> str:
        """Get full file path if it exists"""
        sanitized_path = self._sanitize_path(file_path)
        full_path = Path(sanitized_path)
        
        if not full_path.exists():
            raise ValueError(f"File {file_path} not found")
            
        return str(full_path)
        
    def _get_file_type(self, filename: str) -> str:
        """Enhanced file type detection"""
        ext = self._get_file_extension(filename)
        
        for file_type, extensions in self.ALLOWED_EXTENSIONS.items():
            if ext in extensions:
                return file_type
                
        return 'unknown'
        
    def get_navigation_summary(self) -> Dict[str, Any]:
        """Get a summary of available navigation options"""
        return {
            "roots": self.NAVIGATION_ROOTS,
            "current_user": os.getenv("USER", "root"),
            "vps_access": True,
            "protected_dirs": list(self.PROTECTED_DIRS),
            "hidden_dirs": list(self.HIDDEN_DIRS)
        }