import os
from python.helpers.api import ApiHandler, Input, Output, Request, Response
from python.helpers import files, runtime
from typing import TypedDict

def resolve_file_path(path: str) -> str:
    """
    Enhanced path resolution that handles:
    - Regular relative paths (converts via get_abs_path)
    - Absolute paths starting with /a0/ (direct container paths)
    - URLs or web-accessible paths (converts to filesystem paths)
    - Pareng Boyong deliverables paths (both relative and absolute)
    """
    if not path:
        return ""
    
    # Handle absolute paths (full VPS access)
    if path.startswith('/'):
        return path
    
    # Handle web-accessible deliverables paths
    if path.startswith('pareng_boyong_deliverables/'):
        return '/root/projects/pareng-boyong/' + path
    
    # Handle full filesystem paths that already exist
    if os.path.isabs(path) and os.path.exists(path):
        return path
    
    # Handle relative paths - check multiple possibilities
    possible_paths = [
        files.get_abs_path(path),  # Standard resolution
        path if path.startswith('/') else '/' + path,  # Try as VPS absolute first
        os.path.join('/root/projects/pareng-boyong', path),  # Map to actual working directory
        os.path.join('/root', path),  # Try /root directory
        os.path.join('/var/www', path),  # Try web directory
    ]
    
    # Return the first path that exists
    for test_path in possible_paths:
        if os.path.exists(test_path):
            return test_path
    
    # If none exist, return the standard resolution
    return files.get_abs_path(path)

class FileInfoApi(ApiHandler):
    async def process(self, input: Input, request: Request) -> Output:
        path = input.get("path", "")
        info = await runtime.call_development_function(get_file_info, path)
        return info

class FileInfo(TypedDict):
    input_path: str
    abs_path: str
    exists: bool
    is_dir: bool
    is_file: bool
    is_link: bool
    size: int
    modified: float
    created: float
    permissions: int
    dir_path: str
    file_name: str
    file_ext: str
    message: str

async def get_file_info(path: str) -> FileInfo:
    # Enhanced path handling for different formats
    abs_path = resolve_file_path(path)
    exists = os.path.exists(abs_path)
    message = ""

    if not exists:
        message = f"File {path} not found. Tried: {abs_path}"

    return {
        "input_path": path,
        "abs_path": abs_path,
        "exists": exists,
        "is_dir": os.path.isdir(abs_path) if exists else False,
        "is_file": os.path.isfile(abs_path) if exists else False,
        "is_link": os.path.islink(abs_path) if exists else False,
        "size": os.path.getsize(abs_path) if exists else 0,
        "modified": os.path.getmtime(abs_path) if exists else 0,
        "created": os.path.getctime(abs_path) if exists else 0,
        "permissions": os.stat(abs_path).st_mode if exists else 0,
        "dir_path": os.path.dirname(abs_path),
        "file_name": os.path.basename(abs_path),
        "file_ext": os.path.splitext(abs_path)[1],
        "message": message
    }