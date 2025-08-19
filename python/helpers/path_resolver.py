"""
Path Resolver for Pareng Boyong
Permanent fix for /a0/ path usage - maps all /a0/ paths to actual VPS paths
"""

import os
from pathlib import Path

class PathResolver:
    """
    Centralized path resolution to ensure Pareng Boyong uses full VPS paths
    instead of being restricted to the imaginary /a0/ boundary.
    """
    
    # Mapping of /a0/ paths to actual VPS paths
    PATH_MAPPINGS = {
        "/a0/": "/root/projects/pareng-boyong/",
        "/a0/vps-www/": "/var/www/",
        "/a0/vps-root/": "/root/",
        "/a0/vps-tmp/": "/tmp/",
        "/a0/tmp/": "/root/projects/pareng-boyong/tmp/",
        "/a0/pareng_boyong_deliverables/": "/root/projects/pareng-boyong/pareng_boyong_deliverables/",
        "/a0/pareng-boyong-projects/": "/root/projects/pareng-boyong/pareng-boyong-projects/",
        "/a0/python/": "/root/projects/pareng-boyong/python/",
        "/a0/webui/": "/root/projects/pareng-boyong/webui/",
        "/a0/knowledge/": "/root/projects/pareng-boyong/knowledge/",
    }
    
    @classmethod
    def resolve(cls, path: str) -> str:
        """
        Resolve any path, converting /a0/ paths to actual VPS paths.
        
        In container context, /a0 is already mounted correctly, so no resolution is needed.
        
        Args:
            path: The path to resolve (can be /a0/ path or regular path)
            
        Returns:
            The resolved absolute path on the VPS filesystem
        """
        if not path:
            # Check if we're running in container (where /a0 exists and is mounted)
            if os.path.exists("/a0") and os.path.ismount("/a0"):
                return "/a0"
            return "/root/projects/pareng-boyong"
        
        # Convert Path object to string
        path = str(path)
        
        # Check if we're running in container context
        # In container: /a0 exists as a mount point and should not be resolved
        if os.path.exists("/a0") and os.path.ismount("/a0"):
            # In container - use paths as-is, no resolution needed
            if path.startswith("/a0"):
                return os.path.normpath(path)
            if os.path.isabs(path):
                return os.path.normpath(path)
            # For relative paths in container, join with /a0
            return os.path.normpath(os.path.join("/a0", path))
        
        # Host context - do path resolution
        # Special case: if path is exactly "/a0" or "/a0/"
        if path in ["/a0", "/a0/"]:
            return "/root/projects/pareng-boyong"
        
        # Check each mapping and replace if found
        for a0_path, vps_path in cls.PATH_MAPPINGS.items():
            if path.startswith(a0_path):
                # Replace the /a0/ part with the actual VPS path
                resolved = path.replace(a0_path, vps_path, 1)
                # Clean up any double slashes
                resolved = os.path.normpath(resolved)
                return resolved
        
        # If it's already an absolute path (not /a0/), return as-is
        if os.path.isabs(path):
            return os.path.normpath(path)
        
        # For relative paths, join with the base directory
        base_dir = "/root/projects/pareng-boyong"
        return os.path.normpath(os.path.join(base_dir, path))
    
    @classmethod
    def reverse_resolve(cls, vps_path: str) -> str:
        """
        Convert a VPS path back to /a0/ format for backward compatibility.
        Only used when Pareng Boyong needs to communicate with legacy code.
        
        Args:
            vps_path: The actual VPS path
            
        Returns:
            The /a0/ formatted path
        """
        vps_path = str(vps_path)
        
        # Find the longest matching VPS path and convert back
        best_match = ""
        best_a0_path = ""
        
        for a0_path, mapped_vps_path in cls.PATH_MAPPINGS.items():
            if vps_path.startswith(mapped_vps_path) and len(mapped_vps_path) > len(best_match):
                best_match = mapped_vps_path
                best_a0_path = a0_path
        
        if best_match:
            # Replace the VPS part with /a0/ part
            return vps_path.replace(best_match, best_a0_path, 1)
        
        # If no match found, return original
        return vps_path
    
    @classmethod
    def exists(cls, path: str) -> bool:
        """Check if a path exists after resolution."""
        resolved = cls.resolve(path)
        return os.path.exists(resolved)
    
    @classmethod
    def is_file(cls, path: str) -> bool:
        """Check if path is a file after resolution."""
        resolved = cls.resolve(path)
        return os.path.isfile(resolved)
    
    @classmethod
    def is_dir(cls, path: str) -> bool:
        """Check if path is a directory after resolution."""
        resolved = cls.resolve(path)
        return os.path.isdir(resolved)
    
    @classmethod
    def makedirs(cls, path: str, exist_ok: bool = True):
        """Create directories for the resolved path."""
        resolved = cls.resolve(path)
        Path(resolved).mkdir(parents=True, exist_ok=exist_ok)
    
    @classmethod
    def join(cls, *paths) -> str:
        """Join paths and resolve them."""
        # First resolve the initial path
        if paths:
            base = cls.resolve(paths[0])
            if len(paths) > 1:
                # Join remaining paths
                full_path = os.path.join(base, *paths[1:])
                # Resolve again in case the joined path contains /a0/
                return cls.resolve(full_path)
            return base
        return "/root/projects/pareng-boyong"


# Create a global instance for easy import
path_resolver = PathResolver()
resolve_path = path_resolver.resolve
reverse_path = path_resolver.reverse_resolve