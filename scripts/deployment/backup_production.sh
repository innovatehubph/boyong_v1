#!/bin/bash

# Pareng Boyong Production Backup Script
# Creates a complete backup of the current working state
# Usage: ./backup_production.sh [--name custom_name] [--include-logs] [--include-models]

set -e  # Exit on error

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
MAGENTA='\033[0;35m'
NC='\033[0m' # No Color

# Script configuration
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# Backup configuration
BACKUP_BASE_DIR="${SCRIPT_DIR}/backups"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_NAME=""
INCLUDE_LOGS=false
INCLUDE_MODELS=false
BACKUP_DIR=""

# Parse arguments
for arg in "$@"; do
    case $arg in
        --name=*)
            BACKUP_NAME="${arg#*=}"
            shift
            ;;
        --include-logs)
            INCLUDE_LOGS=true
            shift
            ;;
        --include-models)
            INCLUDE_MODELS=true
            shift
            ;;
        --help)
            echo "Usage: $0 [--name=custom_name] [--include-logs] [--include-models]"
            echo "  --name=NAME       Custom backup name (default: timestamp)"
            echo "  --include-logs    Include log files in backup"
            echo "  --include-models  Include AI model files (large!)"
            exit 0
            ;;
    esac
done

# Set backup directory name
if [ -n "$BACKUP_NAME" ]; then
    BACKUP_DIR="${BACKUP_BASE_DIR}/${BACKUP_NAME}_${TIMESTAMP}"
else
    BACKUP_DIR="${BACKUP_BASE_DIR}/backup_${TIMESTAMP}"
fi

echo -e "${CYAN}═══════════════════════════════════════════════════════════════${NC}"
echo -e "${CYAN}       Pareng Boyong Production Backup${NC}"
echo -e "${CYAN}       Creating backup of working state${NC}"
echo -e "${CYAN}═══════════════════════════════════════════════════════════════${NC}\n"

echo -e "${BLUE}Backup Configuration:${NC}"
echo -e "  Destination: ${GREEN}${BACKUP_DIR}${NC}"
echo -e "  Include logs: ${YELLOW}${INCLUDE_LOGS}${NC}"
echo -e "  Include models: ${YELLOW}${INCLUDE_MODELS}${NC}\n"

# Create backup directory
echo -e "${YELLOW}[1/10] Creating backup directory...${NC}"
mkdir -p "$BACKUP_DIR"
echo -e "${GREEN}  ✓ Backup directory created${NC}"

# Save current git state
echo -e "${YELLOW}[2/10] Saving git repository state...${NC}"
if [ -d .git ]; then
    git rev-parse HEAD > "$BACKUP_DIR/git_commit_hash.txt" 2>/dev/null || echo "No git commit" > "$BACKUP_DIR/git_commit_hash.txt"
    git status --porcelain > "$BACKUP_DIR/git_status.txt" 2>/dev/null || true
    git diff > "$BACKUP_DIR/git_uncommitted_changes.diff" 2>/dev/null || true
    echo -e "${GREEN}  ✓ Git state saved${NC}"
else
    echo -e "${YELLOW}  ⚠ No git repository found${NC}"
fi

# Backup critical configuration files
echo -e "${YELLOW}[3/10] Backing up configuration files...${NC}"
mkdir -p "$BACKUP_DIR/config"

# Core configuration files
[ -f .env ] && cp .env "$BACKUP_DIR/config/.env"
[ -f requirements.txt ] && cp requirements.txt "$BACKUP_DIR/config/"
[ -f requirements-stable.txt ] && cp requirements-stable.txt "$BACKUP_DIR/config/"
[ -f package.json ] && cp package.json "$BACKUP_DIR/config/"
[ -f package-lock.json ] && cp package-lock.json "$BACKUP_DIR/config/"
[ -f docker-compose.yml ] && cp docker-compose.yml "$BACKUP_DIR/config/"
[ -f mcp_servers_config.json ] && cp mcp_servers_config.json "$BACKUP_DIR/config/"

# Settings
[ -d tmp ] && cp -r tmp "$BACKUP_DIR/config/"

echo -e "${GREEN}  ✓ Configuration files backed up${NC}"

# Backup Python code
echo -e "${YELLOW}[4/10] Backing up Python code...${NC}"
mkdir -p "$BACKUP_DIR/code"
cp -r python "$BACKUP_DIR/code/"
cp -r prompts "$BACKUP_DIR/code/"
cp -r instruments "$BACKUP_DIR/code/" 2>/dev/null || true
cp -r knowledge "$BACKUP_DIR/code/"
cp *.py "$BACKUP_DIR/code/" 2>/dev/null || true
echo -e "${GREEN}  ✓ Python code backed up${NC}"

# Backup web UI
echo -e "${YELLOW}[5/10] Backing up web interface...${NC}"
mkdir -p "$BACKUP_DIR/webui"
cp -r webui/* "$BACKUP_DIR/webui/" 2>/dev/null || true
echo -e "${GREEN}  ✓ Web interface backed up${NC}"

# Backup memory and embeddings
echo -e "${YELLOW}[6/10] Backing up memory system...${NC}"
if [ -d memory ]; then
    mkdir -p "$BACKUP_DIR/memory"
    cp -r memory/default "$BACKUP_DIR/memory/" 2>/dev/null || true
    # Don't backup large embedding files by default
    find memory -name "*.json" -o -name "*.faiss" -o -name "*.pkl" -o -name "*.md" | while read file; do
        dest_dir=$(dirname "$BACKUP_DIR/$file")
        mkdir -p "$dest_dir"
        cp "$file" "$dest_dir/" 2>/dev/null || true
    done
    echo -e "${GREEN}  ✓ Memory system backed up${NC}"
else
    echo -e "${YELLOW}  ⚠ No memory directory found${NC}"
fi

# Backup Docker configuration
echo -e "${YELLOW}[7/10] Backing up Docker configuration...${NC}"
mkdir -p "$BACKUP_DIR/docker"

# Save Docker container information
docker ps -a --format "table {{.Names}}\t{{.Image}}\t{{.Status}}\t{{.Ports}}" > "$BACKUP_DIR/docker/containers.txt"
docker images --format "table {{.Repository}}\t{{.Tag}}\t{{.ID}}\t{{.Size}}" > "$BACKUP_DIR/docker/images.txt"

# Export container configurations
for container in agent-zero-dev agent-zero-redis agent-zero-searxng; do
    if docker ps -a --format '{{.Names}}' | grep -q "^${container}$"; then
        docker inspect "$container" > "$BACKUP_DIR/docker/${container}_inspect.json" 2>/dev/null || true
    fi
done

# Copy Docker compose files
cp docker-compose.*.yml "$BACKUP_DIR/docker/" 2>/dev/null || true
[ -d docker ] && cp -r docker "$BACKUP_DIR/" 2>/dev/null || true

echo -e "${GREEN}  ✓ Docker configuration backed up${NC}"

# Backup scripts
echo -e "${YELLOW}[8/10] Backing up scripts...${NC}"
mkdir -p "$BACKUP_DIR/scripts"
cp *.sh "$BACKUP_DIR/scripts/" 2>/dev/null || true
echo -e "${GREEN}  ✓ Scripts backed up${NC}"

# Optional: Backup logs
if [ "$INCLUDE_LOGS" = true ]; then
    echo -e "${YELLOW}[9/10] Backing up logs...${NC}"
    if [ -d logs ]; then
        mkdir -p "$BACKUP_DIR/logs"
        cp -r logs/* "$BACKUP_DIR/logs/" 2>/dev/null || true
        echo -e "${GREEN}  ✓ Logs backed up${NC}"
    else
        echo -e "${YELLOW}  ⚠ No logs directory found${NC}"
    fi
else
    echo -e "${YELLOW}[9/10] Skipping logs backup (use --include-logs to include)${NC}"
fi

# Optional: Backup AI models
if [ "$INCLUDE_MODELS" = true ]; then
    echo -e "${YELLOW}[10/10] Backing up AI models (this may take time)...${NC}"
    mkdir -p "$BACKUP_DIR/models"
    
    # LocalAI models
    [ -d localai_models ] && cp -r localai_models "$BACKUP_DIR/models/" 2>/dev/null || true
    
    # Wan2GP models
    [ -d wan2gp_models ] && cp -r wan2gp_models "$BACKUP_DIR/models/" 2>/dev/null || true
    
    # ToucanTTS models
    [ -d toucan_tts ] && cp -r toucan_tts "$BACKUP_DIR/models/" 2>/dev/null || true
    
    echo -e "${GREEN}  ✓ AI models backed up${NC}"
else
    echo -e "${YELLOW}[10/10] Skipping AI models backup (use --include-models to include)${NC}"
fi

# Create backup metadata
echo -e "${YELLOW}Creating backup metadata...${NC}"
cat > "$BACKUP_DIR/backup_info.json" << EOF
{
  "timestamp": "${TIMESTAMP}",
  "date": "$(date)",
  "hostname": "$(hostname)",
  "user": "$(whoami)",
  "backup_name": "${BACKUP_NAME:-automatic}",
  "include_logs": ${INCLUDE_LOGS},
  "include_models": ${INCLUDE_MODELS},
  "docker_version": "$(docker --version 2>/dev/null || echo 'Not available')",
  "python_version": "$(python --version 2>/dev/null || echo 'Not available')",
  "git_commit": "$(git rev-parse HEAD 2>/dev/null || echo 'No git')",
  "backup_size": "pending"
}
EOF

# Create restore instructions
cat > "$BACKUP_DIR/RESTORE_INSTRUCTIONS.md" << 'EOF'
# Restore Instructions

## Quick Restore
Run the restore script from the pareng-boyong directory:
```bash
./restore_production.sh --backup=backups/[backup_directory_name]
```

## Manual Restore Steps

1. **Stop all services:**
   ```bash
   ./stop_production.sh --remove
   ```

2. **Restore code files:**
   ```bash
   cp -r backups/[backup_name]/code/python ./
   cp -r backups/[backup_name]/code/prompts ./
   cp -r backups/[backup_name]/code/knowledge ./
   cp backups/[backup_name]/code/*.py ./
   ```

3. **Restore configuration:**
   ```bash
   cp backups/[backup_name]/config/.env ./
   cp -r backups/[backup_name]/config/tmp ./
   ```

4. **Restore web UI:**
   ```bash
   cp -r backups/[backup_name]/webui/* ./webui/
   ```

5. **Restore memory (optional):**
   ```bash
   cp -r backups/[backup_name]/memory/* ./memory/
   ```

6. **Restart services:**
   ```bash
   ./start_production.sh
   ```

## Verify Restoration
- Check https://ai.innovatehub.ph is accessible
- Verify all services are running: `docker ps`
- Test core functionality
EOF

# Calculate backup size
BACKUP_SIZE=$(du -sh "$BACKUP_DIR" | cut -f1)
sed -i "s/\"backup_size\": \"pending\"/\"backup_size\": \"$BACKUP_SIZE\"/" "$BACKUP_DIR/backup_info.json" 2>/dev/null || true

# Create compressed archive
echo -e "${YELLOW}Creating compressed archive...${NC}"
ARCHIVE_NAME="${BACKUP_DIR}.tar.gz"
tar -czf "$ARCHIVE_NAME" -C "$BACKUP_BASE_DIR" "$(basename "$BACKUP_DIR")"
ARCHIVE_SIZE=$(du -sh "$ARCHIVE_NAME" | cut -f1)

echo -e "${GREEN}  ✓ Archive created: ${ARCHIVE_NAME} (${ARCHIVE_SIZE})${NC}"

# Summary
echo -e "\n${CYAN}═══════════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}✓ Backup completed successfully!${NC}"
echo -e "${CYAN}═══════════════════════════════════════════════════════════════${NC}\n"

echo -e "${BLUE}Backup Details:${NC}"
echo -e "  Location:     ${GREEN}${BACKUP_DIR}${NC}"
echo -e "  Archive:      ${GREEN}${ARCHIVE_NAME}${NC}"
echo -e "  Size:         ${YELLOW}${BACKUP_SIZE}${NC} (${ARCHIVE_SIZE} compressed)"
echo -e "  Restore cmd:  ${CYAN}./restore_production.sh --backup=${BACKUP_DIR}${NC}"

echo -e "\n${MAGENTA}Important:${NC} This backup contains your current working configuration."
echo "Keep it safe before making any major changes!"