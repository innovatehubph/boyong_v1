#!/bin/bash

# Pareng Boyong Production Restart Script
# This script performs a clean restart of the entire system
# Usage: ./restart_production.sh [--quick] [--logs]

set -e  # Exit on error

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Script configuration
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# Parse arguments
QUICK_MODE=false
SHOW_LOGS=false
for arg in "$@"; do
    case $arg in
        --quick)
            QUICK_MODE=true
            ;;
        --logs)
            SHOW_LOGS=true
            ;;
        --help)
            echo "Usage: $0 [--quick] [--logs]"
            echo "  --quick  Quick restart (just restart containers, don't stop/start)"
            echo "  --logs   Show logs after restarting"
            exit 0
            ;;
    esac
done

echo -e "${CYAN}═══════════════════════════════════════════════════════════════${NC}"
echo -e "${CYAN}       Pareng Boyong Production Restart${NC}"
echo -e "${CYAN}       Target: https://ai.innovatehub.ph${NC}"
echo -e "${CYAN}═══════════════════════════════════════════════════════════════${NC}\n"

if [ "$QUICK_MODE" = true ]; then
    # Quick restart - just restart the main container
    echo -e "${YELLOW}Performing quick restart...${NC}\n"
    
    echo -e "${BLUE}[1/2] Restarting Agent Zero container...${NC}"
    docker restart agent-zero-dev
    echo -e "${GREEN}  ✓ Agent Zero restarted${NC}"
    
    echo -e "${BLUE}[2/2] Verifying services...${NC}"
    sleep 3
    if curl -s -o /dev/null -w "%{http_code}" http://localhost:55080 | grep -q "200\|401"; then
        echo -e "${GREEN}  ✓ Web UI responding${NC}"
    else
        echo -e "${RED}  ✗ Web UI not responding yet (may still be starting)${NC}"
    fi
    
else
    # Full restart - stop everything and start again
    echo -e "${YELLOW}Performing full restart...${NC}\n"
    
    # Stop all services
    echo -e "${BLUE}Phase 1: Stopping all services${NC}"
    ./stop_production.sh
    
    echo -e "\n${BLUE}Waiting for clean shutdown...${NC}"
    sleep 3
    
    # Start all services
    echo -e "\n${BLUE}Phase 2: Starting all services${NC}"
    ./start_production.sh
fi

echo -e "\n${CYAN}═══════════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}✓ Restart complete!${NC}"
echo -e "${CYAN}═══════════════════════════════════════════════════════════════${NC}\n"

# Show status
echo -e "${BLUE}Current Status:${NC}"
docker ps --format "table {{.Names}}\t{{.Status}}" | grep -E "agent-zero|redis|searxng" || true

# Show logs if requested
if [ "$SHOW_LOGS" = true ]; then
    echo -e "\n${BLUE}Recent Logs:${NC}"
    docker logs agent-zero-dev --tail 20
fi

echo -e "\n${GREEN}Access the application at: https://ai.innovatehub.ph${NC}"