# Conflict Prevention Guidelines for Pareng Boyong

## 🚨 Critical System Updates - Conflict Prevention

### **Updated File Path References**

**OLD vs NEW Path Usage:**

#### **❌ OLD - Limited Access (Causes Conflicts)**
```bash
# These paths may cause "access denied" errors
/var/www/projects.innovatehub.ph/
/var/www/pareng-boyong-apps/
/root/some-config-file
/tmp/temporary-file
```

#### **✅ NEW - Full VPS Access (Conflict-Free)**
```bash
# Always use these paths for VPS files
/a0/vps-www/projects.innovatehub.ph/
/a0/vps-www/pareng-boyong-apps/
/a0/vps-root/some-config-file
/a0/vps-tmp/temporary-file
```

### **Automatic Path Translation**

When users request file operations, Pareng Boyong should automatically translate:

#### **Web Projects:**
- `"/var/www/anything"` → `"/a0/vps-www/anything"`
- `"www directory"` → `"/a0/vps-www/"`
- `"web projects"` → `"/a0/vps-www/"`

#### **System Files:**
- `"/root/anything"` → `"/a0/vps-root/anything"`
- `"home directory"` → `"/a0/vps-root/"`
- `"user files"` → `"/a0/vps-root/"`

#### **Temporary Files:**
- `"/tmp/anything"` → `"/a0/vps-tmp/anything"`
- `"temp files"` → `"/a0/vps-tmp/"`
- `"cache files"` → `"/a0/vps-tmp/"`

### **Tool Usage Guidelines**

#### **File Operations - Use These Patterns:**

**✅ CORRECT:**
```bash
# Reading project files
Read file_path="/a0/vps-www/projects.innovatehub.ph/frontend/package.json"

# Listing directories  
LS path="/a0/vps-www/pareng-boyong-apps/"

# Searching in projects
Grep pattern="import" path="/a0/vps-www/" type="js"

# Editing configuration files
Edit file_path="/a0/vps-www/pareng-boyong-apps/espresso-depot/backend/config/database.js"
```

**❌ INCORRECT (May cause conflicts):**
```bash
# These may fail with access denied
Read file_path="/var/www/projects.innovatehub.ph/frontend/package.json"
LS path="/var/www/pareng-boyong-apps/"
```

### **Common Conflict Scenarios & Solutions**

#### **Scenario 1: User asks "show me my web projects"**
```bash
# ❌ OLD approach (may fail)
LS path="/var/www"

# ✅ NEW approach (always works)
LS path="/a0/vps-www"
```

#### **Scenario 2: User asks "edit the Espresso Depot config"**
```bash
# ❌ OLD approach (access denied)
Edit file_path="/var/www/pareng-boyong-apps/espresso-depot/backend/config/database.js"

# ✅ NEW approach (full access)
Edit file_path="/a0/vps-www/pareng-boyong-apps/espresso-depot/backend/config/database.js"
```

#### **Scenario 3: User asks "check the logs"**
```bash
# ❌ OLD approach (limited access)
Read file_path="/var/log/nginx/access.log"

# ✅ NEW approach (check both locations)
# First try VPS root mount
Read file_path="/a0/vps-root/var/log/nginx/access.log"
# Or project-specific logs
Read file_path="/a0/vps-www/projects.innovatehub.ph/backend/logs/combined.log"
```

### **File Browser Integration**

#### **Web Interface Navigation:**
When users interact with the file browser through the web interface:

1. **Default Directory**: Always start at `/a0/` for full system overview
2. **Quick Access Links**: 
   - "Web Projects" → `/a0/vps-www/`
   - "User Files" → `/a0/vps-root/`
   - "Temp Files" → `/a0/vps-tmp/`
3. **Path Display**: Show both container path and description
4. **Permissions Check**: Always verify read/write access before operations

### **Backward Compatibility**

#### **Handling Legacy References:**
If Pareng Boyong encounters old file references in documentation or user requests:

1. **Auto-translate paths** to new VPS-accessible locations
2. **Inform users** about the path translation when necessary
3. **Update any stored references** to use new paths
4. **Maintain functionality** while using enhanced file access

### **Error Prevention Checklist**

Before performing any file operation, verify:

- [ ] **Path starts with `/a0/`** for VPS file access
- [ ] **File/directory exists** using LS tool first
- [ ] **Permissions are appropriate** for the intended operation
- [ ] **Backup created** if modifying critical files
- [ ] **Alternative paths checked** if primary path fails

### **Emergency Fallback**

If new paths fail unexpectedly:

1. **Try direct mount paths**: `/mnt/vps-www/`, `/mnt/vps-root/`, `/mnt/vps-tmp/`
2. **Check container status**: `docker ps | grep agent-zero`
3. **Verify mounts**: `docker inspect agent-zero-dev | grep Mounts`
4. **Report issue** and use known working paths from `/a0/`

### **System Verification Commands**

To verify the system is working correctly:

```bash
# Test VPS access
LS path="/a0/vps-www/"
LS path="/a0/vps-root/"  
LS path="/a0/vps-tmp/"

# Test symbolic links
Bash command="ls -la /a0/ | grep vps"

# Test file operations
Read file_path="/a0/vps-www/pareng-boyong-apps/espresso-depot/backend/package.json"
```

Following these guidelines ensures Pareng Boyong operates with full VPS access capabilities while preventing conflicts and access errors.