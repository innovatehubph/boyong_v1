#!/bin/bash

# Pareng Boyong Production Restore Script
# Restores from a backup to recover working state
# Usage: ./restore_production.sh --backup=backup_directory [--force] [--skip-services]

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

# Restore configuration
BACKUP_PATH=""
FORCE_RESTORE=false
SKIP_SERVICES=false
RESTORE_LOGS=false
RESTORE_MODELS=false

# Parse arguments
for arg in "$@"; do
    case $arg in
        --backup=*)
            BACKUP_PATH="${arg#*=}"
            shift
            ;;
        --force)
            FORCE_RESTORE=true
            shift
            ;;
        --skip-services)
            SKIP_SERVICES=true
            shift
            ;;
        --restore-logs)
            RESTORE_LOGS=true
            shift
            ;;
        --restore-models)
            RESTORE_MODELS=true
            shift
            ;;
        --help)
            echo "Usage: $0 --backup=backup_directory [--force] [--skip-services]"
            echo "  --backup=PATH     Path to backup directory or archive"
            echo "  --force           Skip confirmation prompts"
            echo "  --skip-services   Don't restart services after restore"
            echo "  --restore-logs    Also restore log files"
            echo "  --restore-models  Also restore AI model files"
            exit 0
            ;;
    esac
done

# Validate backup path
if [ -z "$BACKUP_PATH" ]; then
    echo -e "${RED}Error: No backup specified!${NC}"
    echo "Usage: $0 --backup=backup_directory"
    echo ""
    echo "Available backups:"
    if [ -d "backups" ]; then
        ls -la backups/ | grep "^d" | awk '{print "  " $NF}' | grep -v "^\.$\|^\.\.$"
    fi
    exit 1
fi

# Handle compressed archives
if [[ "$BACKUP_PATH" == *.tar.gz ]]; then
    echo -e "${YELLOW}Extracting archive...${NC}"
    TEMP_DIR="/tmp/restore_$(date +%s)"
    mkdir -p "$TEMP_DIR"
    tar -xzf "$BACKUP_PATH" -C "$TEMP_DIR"
    BACKUP_PATH="$TEMP_DIR/$(ls "$TEMP_DIR")"
fi

# Verify backup exists and is valid
if [ ! -d "$BACKUP_PATH" ]; then
    echo -e "${RED}Error: Backup directory not found: $BACKUP_PATH${NC}"
    exit 1
fi

if [ ! -f "$BACKUP_PATH/backup_info.json" ]; then
    echo -e "${RED}Error: Invalid backup - missing backup_info.json${NC}"
    exit 1
fi

echo -e "${CYAN}═══════════════════════════════════════════════════════════════${NC}"
echo -e "${CYAN}       Pareng Boyong Production Restore${NC}"
echo -e "${CYAN}═══════════════════════════════════════════════════════════════${NC}\n"

# Display backup information
echo -e "${BLUE}Backup Information:${NC}"
if command -v jq &> /dev/null; then
    jq -r '. | "  Date: \(.date)\n  Name: \(.backup_name)\n  Size: \(.backup_size)\n  Git: \(.git_commit)"' "$BACKUP_PATH/backup_info.json"
else
    echo -e "  Path: ${GREEN}$BACKUP_PATH${NC}"
    grep -E "date|backup_name|backup_size" "$BACKUP_PATH/backup_info.json" | sed 's/^/  /'
fi
echo ""

# Confirmation prompt
if [ "$FORCE_RESTORE" != true ]; then
    echo -e "${YELLOW}⚠️  WARNING: This will replace your current configuration!${NC}"
    echo -e "${YELLOW}   It's recommended to create a backup first:${NC}"
    echo -e "${YELLOW}   ./backup_production.sh --name=before_restore${NC}\n"
    read -p "Do you want to continue? (yes/no): " confirm
    if [ "$confirm" != "yes" ]; then
        echo -e "${RED}Restore cancelled.${NC}"
        exit 0
    fi
fi

# Create pre-restore backup
echo -e "${YELLOW}[1/8] Creating safety backup...${NC}"
SAFETY_BACKUP="backups/pre_restore_$(date +%Y%m%d_%H%M%S)"
mkdir -p "$SAFETY_BACKUP"
cp .env "$SAFETY_BACKUP/.env" 2>/dev/null || true
cp -r python "$SAFETY_BACKUP/" 2>/dev/null || true
cp -r prompts "$SAFETY_BACKUP/" 2>/dev/null || true
echo -e "${GREEN}  ✓ Safety backup created at: $SAFETY_BACKUP${NC}"

# Stop services if not skipped
if [ "$SKIP_SERVICES" != true ]; then
    echo -e "${YELLOW}[2/8] Stopping current services...${NC}"
    ./stop_production.sh 2>/dev/null || true
    echo -e "${GREEN}  ✓ Services stopped${NC}"
else
    echo -e "${YELLOW}[2/8] Skipping service shutdown (--skip-services)${NC}"
fi

# Restore configuration files
echo -e "${YELLOW}[3/8] Restoring configuration files...${NC}"
if [ -d "$BACKUP_PATH/config" ]; then
    [ -f "$BACKUP_PATH/config/.env" ] && cp "$BACKUP_PATH/config/.env" .env
    [ -f "$BACKUP_PATH/config/requirements.txt" ] && cp "$BACKUP_PATH/config/requirements.txt" requirements.txt
    [ -f "$BACKUP_PATH/config/requirements-stable.txt" ] && cp "$BACKUP_PATH/config/requirements-stable.txt" requirements-stable.txt
    [ -f "$BACKUP_PATH/config/package.json" ] && cp "$BACKUP_PATH/config/package.json" package.json
    [ -f "$BACKUP_PATH/config/package-lock.json" ] && cp "$BACKUP_PATH/config/package-lock.json" package-lock.json
    [ -f "$BACKUP_PATH/config/mcp_servers_config.json" ] && cp "$BACKUP_PATH/config/mcp_servers_config.json" mcp_servers_config.json
    [ -d "$BACKUP_PATH/config/tmp" ] && cp -r "$BACKUP_PATH/config/tmp" ./
    echo -e "${GREEN}  ✓ Configuration restored${NC}"
else
    echo -e "${YELLOW}  ⚠ No configuration files in backup${NC}"
fi

# Restore Python code
echo -e "${YELLOW}[4/8] Restoring Python code...${NC}"
if [ -d "$BACKUP_PATH/code" ]; then
    # Backup current code first
    [ -d python ] && mv python python.old_$(date +%s) 2>/dev/null || true
    [ -d prompts ] && mv prompts prompts.old_$(date +%s) 2>/dev/null || true
    
    # Restore from backup
    [ -d "$BACKUP_PATH/code/python" ] && cp -r "$BACKUP_PATH/code/python" ./
    [ -d "$BACKUP_PATH/code/prompts" ] && cp -r "$BACKUP_PATH/code/prompts" ./
    [ -d "$BACKUP_PATH/code/knowledge" ] && cp -r "$BACKUP_PATH/code/knowledge" ./
    [ -d "$BACKUP_PATH/code/instruments" ] && cp -r "$BACKUP_PATH/code/instruments" ./
    
    # Restore Python files in root
    find "$BACKUP_PATH/code" -maxdepth 1 -name "*.py" -exec cp {} ./ \;
    
    echo -e "${GREEN}  ✓ Python code restored${NC}"
else
    echo -e "${YELLOW}  ⚠ No code files in backup${NC}"
fi

# Restore web UI
echo -e "${YELLOW}[5/8] Restoring web interface...${NC}"
if [ -d "$BACKUP_PATH/webui" ]; then
    # Backup current webui
    [ -d webui ] && mv webui webui.old_$(date +%s) 2>/dev/null || true
    mkdir -p webui
    cp -r "$BACKUP_PATH/webui/"* webui/ 2>/dev/null || true
    echo -e "${GREEN}  ✓ Web interface restored${NC}"
else
    echo -e "${YELLOW}  ⚠ No webui files in backup${NC}"
fi

# Restore memory system
echo -e "${YELLOW}[6/8] Restoring memory system...${NC}"
if [ -d "$BACKUP_PATH/memory" ]; then
    mkdir -p memory
    cp -r "$BACKUP_PATH/memory/"* memory/ 2>/dev/null || true
    echo -e "${GREEN}  ✓ Memory system restored${NC}"
else
    echo -e "${YELLOW}  ⚠ No memory files in backup${NC}"
fi

# Restore scripts
echo -e "${YELLOW}[7/8] Restoring scripts...${NC}"
if [ -d "$BACKUP_PATH/scripts" ]; then
    find "$BACKUP_PATH/scripts" -name "*.sh" -exec cp {} ./ \;
    chmod +x *.sh 2>/dev/null || true
    echo -e "${GREEN}  ✓ Scripts restored${NC}"
else
    echo -e "${YELLOW}  ⚠ No scripts in backup${NC}"
fi

# Optional: Restore logs
if [ "$RESTORE_LOGS" = true ] && [ -d "$BACKUP_PATH/logs" ]; then
    echo -e "${YELLOW}[8/8] Restoring logs...${NC}"
    mkdir -p logs
    cp -r "$BACKUP_PATH/logs/"* logs/ 2>/dev/null || true
    echo -e "${GREEN}  ✓ Logs restored${NC}"
else
    echo -e "${YELLOW}[8/8] Skipping logs restore${NC}"
fi

# Optional: Restore AI models
if [ "$RESTORE_MODELS" = true ] && [ -d "$BACKUP_PATH/models" ]; then
    echo -e "${YELLOW}Restoring AI models (this may take time)...${NC}"
    [ -d "$BACKUP_PATH/models/localai_models" ] && cp -r "$BACKUP_PATH/models/localai_models" ./
    [ -d "$BACKUP_PATH/models/wan2gp_models" ] && cp -r "$BACKUP_PATH/models/wan2gp_models" ./
    [ -d "$BACKUP_PATH/models/toucan_tts" ] && cp -r "$BACKUP_PATH/models/toucan_tts" ./
    echo -e "${GREEN}  ✓ AI models restored${NC}"
fi

# Apply git patches if available
if [ -f "$BACKUP_PATH/git_uncommitted_changes.diff" ] && [ -s "$BACKUP_PATH/git_uncommitted_changes.diff" ]; then
    echo -e "${YELLOW}Applying uncommitted changes from backup...${NC}"
    git apply "$BACKUP_PATH/git_uncommitted_changes.diff" 2>/dev/null || echo -e "${YELLOW}  ⚠ Could not apply git patches${NC}"
fi

# Restart services if not skipped
if [ "$SKIP_SERVICES" != true ]; then
    echo -e "${YELLOW}Starting services...${NC}"
    ./start_production.sh
    
    # Verify restoration
    echo -e "${YELLOW}Verifying restoration...${NC}"
    sleep 5
    if curl -s -o /dev/null -w "%{http_code}" http://localhost:55080 | grep -q "200\|401"; then
        echo -e "${GREEN}  ✓ Application is responding${NC}"
    else
        echo -e "${RED}  ✗ Application not responding - check logs${NC}"
    fi
fi

# Clean up temp directory if used
if [ -n "$TEMP_DIR" ] && [ -d "$TEMP_DIR" ]; then
    rm -rf "$TEMP_DIR"
fi

# Summary
echo -e "\n${CYAN}═══════════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}✓ Restore completed successfully!${NC}"
echo -e "${CYAN}═══════════════════════════════════════════════════════════════${NC}\n"

echo -e "${BLUE}Post-Restore Checklist:${NC}"
echo -e "  ✓ Configuration files restored"
echo -e "  ✓ Code and prompts restored"
echo -e "  ✓ Web interface restored"
echo -e "  ✓ Memory system restored"

if [ "$SKIP_SERVICES" != true ]; then
    echo -e "\n${BLUE}Services Status:${NC}"
    docker ps --format "table {{.Names}}\t{{.Status}}" | grep -E "agent-zero|redis|searxng" || true
fi

echo -e "\n${MAGENTA}Important:${NC}"
echo "1. Test the application at: ${GREEN}https://ai.innovatehub.ph${NC}"
echo "2. Check logs if issues: ${YELLOW}docker logs agent-zero-dev${NC}"
echo "3. Safety backup saved at: ${YELLOW}$SAFETY_BACKUP${NC}"

if [ "$SKIP_SERVICES" = true ]; then
    echo -e "\n${YELLOW}Note: Services were not restarted. Run './start_production.sh' when ready.${NC}"
fi