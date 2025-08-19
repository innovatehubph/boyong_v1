# VPS File System Access for Pareng Boyong

## Full VPS File System Access

Pareng Boyong now has complete access to the VPS file system through mounted directories:

### Mounted Directories
- **`/mnt/vps-www`** → Full access to `/var/www` (all web projects)
- **`/mnt/vps-root`** → Full access to `/root` (user home directory)  
- **`/mnt/vps-tmp`** → Full access to `/tmp` (temporary files)
- **`/a0`** → Agent Zero working directory (original mount)

### Convenient Symlinks
For easier access, symbolic links are available in the working directory:
- **`/a0/vps-www`** → `/mnt/vps-www` (VPS web directory)
- **`/a0/vps-root`** → `/mnt/vps-root` (VPS root directory)
- **`/a0/vps-tmp`** → `/mnt/vps-tmp` (VPS temp directory)

## Available Projects and Applications

### InnovateHub Projects (/a0/vps-www/)
1. **`projects.innovatehub.ph/`** - Main projects platform
2. **`pareng-boyong-apps/`** - Pareng Boyong applications
   - `espresso-depot/` - Coffee shop management system
3. **`html/`** - Default nginx web root

### File Browser Capabilities

Pareng Boyong can now:
- **Browse all VPS directories** including system files
- **Access web applications** in /var/www
- **Read configuration files** throughout the system
- **Modify project files** with proper permissions
- **View logs and system files** for troubleshooting
- **Access user data** in /root directory

### File Path Examples

#### Web Projects
```bash
# Main projects platform
/a0/vps-www/projects.innovatehub.ph/

# Pareng Boyong apps
/a0/vps-www/pareng-boyong-apps/espresso-depot/

# Static web files
/a0/vps-www/html/
```

#### User Files
```bash
# User home directory
/a0/vps-root/

# User projects
/a0/vps-root/projects/

# SSH keys and configs
/a0/vps-root/.ssh/
```

#### System Access
```bash
# Temporary files
/a0/vps-tmp/

# Application logs (if accessible)
/a0/vps-root/logs/
```

## File Browser Usage Guidelines

### When browsing files, Pareng Boyong should:
1. **Use relative paths** from /a0/ for easier navigation
2. **Check permissions** before attempting modifications
3. **Respect system files** and avoid unnecessary changes
4. **Use appropriate tools** (Read, LS, Glob, Grep) for file operations
5. **Maintain security** when accessing sensitive files

### Security Considerations
- **Avoid modifying system files** unless explicitly requested
- **Check file permissions** before making changes
- **Backup important files** before modifications
- **Respect application integrity** when editing project files

## Troubleshooting Common Issues

### File Access Problems
```bash
# Check if file exists
ls -la /a0/vps-www/path/to/file

# Check permissions
stat /a0/vps-www/path/to/file

# Use full mounted path if symlink fails
ls -la /mnt/vps-www/path/to/file
```

### Permission Issues
```bash
# Check current user in container
whoami

# Check file ownership
ls -la /a0/vps-www/

# Use sudo if needed for system files
sudo ls -la /mnt/vps-root/
```

This enhanced file access ensures Pareng Boyong can effectively manage and troubleshoot the entire VPS infrastructure while maintaining security and proper file handling practices.