# VPS Path System - No /a0/ Required

## IMPORTANT: Use Actual VPS Paths Directly

As of August 2025, Pareng Boyong uses **actual VPS filesystem paths** directly. There is no need to use `/a0/` prefix anymore.

## Correct Path Usage

### ✅ USE THESE PATHS:
```
/root/projects/pareng-boyong/         # Your working directory
/root/projects/pareng-boyong/tmp/     # Temporary files and uploads
/var/www/                              # Web projects and applications
/root/                                 # User home directory
/tmp/                                  # System temporary files
```

### ❌ DO NOT USE:
```
/a0/                                   # Old imaginary boundary (deprecated)
/a0/vps-www/                          # Use /var/www/ instead
/a0/vps-root/                         # Use /root/ instead
/a0/vps-tmp/                          # Use /tmp/ instead
```

## File Operations

### Reading Files
```python
from python.helpers import files

# Read from actual paths
content = files.read_file('/var/www/projects/index.html')
content = files.read_file('tmp/uploads/document.pdf')  # Relative to working dir
```

### Writing Files
```python
# Write to actual paths
files.write_file('/tmp/output.txt', 'content')
files.write_file('pareng_boyong_deliverables/report.txt', 'content')
```

### File Uploads
- Upload directory: `/root/projects/pareng-boyong/tmp/uploads/`
- Web URL pattern: `/image_get?path=/root/projects/pareng-boyong/tmp/uploads/<filename>`

## Deliverables Storage
- Main path: `/root/projects/pareng-boyong/pareng_boyong_deliverables/`
- Images: `/root/projects/pareng-boyong/pareng_boyong_deliverables/images/`
- Videos: `/root/projects/pareng-boyong/pareng_boyong_deliverables/videos/`
- Audio: `/root/projects/pareng-boyong/pareng_boyong_deliverables/audio/`

## Web Projects Access
```
/var/www/projects.innovatehub.ph/     # InnovateHub platform
/var/www/pareng-boyong-apps/          # Pareng Boyong applications
/var/www/html/                        # Default web root
```

## Environment Configuration
- Config file: `/root/projects/pareng-boyong/.env`
- Settings: `/root/projects/pareng-boyong/tmp/settings.json`

## Path Resolution System

A permanent path resolver is in place that:
1. Automatically converts any legacy `/a0/` paths to actual VPS paths
2. Provides full VPS filesystem access
3. Maintains backward compatibility with old code

However, **you should always use actual VPS paths directly** in new code.

## Key Points

1. **Full VPS Access**: You can access ANY path on the VPS filesystem
2. **No Restrictions**: No imaginary `/a0/` boundary exists
3. **Direct Paths**: Always use actual filesystem paths
4. **Backward Compatible**: Old `/a0/` references still work but are deprecated

## Examples

### ❌ OLD WAY (Deprecated):
```python
# Don't use these anymore
path = '/a0/tmp/uploads/file.txt'
deliverables = '/a0/pareng_boyong_deliverables/'
```

### ✅ NEW WAY (Correct):
```python
# Use actual paths
path = '/root/projects/pareng-boyong/tmp/uploads/file.txt'
deliverables = '/root/projects/pareng-boyong/pareng_boyong_deliverables/'
```

## Container Information
- Container name: `agent-zero-dev`
- Working directory: `/root/projects/pareng-boyong/`
- Full VPS filesystem access enabled
- No path restrictions or boundaries

Remember: **Always use actual VPS paths. No /a0/ prefix needed!**