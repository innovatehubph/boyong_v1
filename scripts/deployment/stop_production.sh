#!/bin/bash

# Pareng Boyong Production Stop Script
# This script cleanly stops all Pareng Boyong services
# Usage: ./stop_production.sh [--remove]

set -e  # Exit on error

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Parse arguments
REMOVE_CONTAINERS=false
for arg in "$@"; do
    case $arg in
        --remove)
            REMOVE_CONTAINERS=true
            ;;
        --help)
            echo "Usage: $0 [--remove]"
            echo "  --remove  Remove containers after stopping (clean shutdown)"
            exit 0
            ;;
    esac
done

echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}       Pareng Boyong Production Stop Script${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}\n"

# Function to check if container is running
check_container() {
    local container_name=$1
    if docker ps --format '{{.Names}}' | grep -q "^${container_name}$"; then
        return 0
    else
        return 1
    fi
}

# Stop main application
echo -e "${YELLOW}[1/4] Stopping Agent Zero application...${NC}"
if check_container "agent-zero-dev"; then
    docker stop agent-zero-dev
    echo -e "${GREEN}  ✓ Agent Zero stopped${NC}"
    if [ "$REMOVE_CONTAINERS" = true ]; then
        docker rm agent-zero-dev 2>/dev/null || true
        echo -e "${GREEN}  ✓ Agent Zero container removed${NC}"
    fi
else
    echo -e "${YELLOW}  ⚠ Agent Zero not running${NC}"
fi

# Stop multimodal services
echo -e "${YELLOW}[2/4] Stopping multimodal services...${NC}"
for container in comfyui audiocraft bark localai pollinations wan2gp; do
    if check_container "$container"; then
        echo "  Stopping $container..."
        docker stop $container 2>/dev/null || true
        if [ "$REMOVE_CONTAINERS" = true ]; then
            docker rm $container 2>/dev/null || true
        fi
    fi
done
echo -e "${GREEN}  ✓ Multimodal services stopped${NC}"

# Stop support services
echo -e "${YELLOW}[3/4] Stopping support services...${NC}"

if check_container "agent-zero-searxng"; then
    docker stop agent-zero-searxng
    echo -e "${GREEN}  ✓ SearXNG stopped${NC}"
    if [ "$REMOVE_CONTAINERS" = true ]; then
        docker rm agent-zero-searxng 2>/dev/null || true
        echo -e "${GREEN}  ✓ SearXNG container removed${NC}"
    fi
else
    echo -e "${YELLOW}  ⚠ SearXNG not running${NC}"
fi

if check_container "agent-zero-redis"; then
    docker stop agent-zero-redis
    echo -e "${GREEN}  ✓ Redis stopped${NC}"
    if [ "$REMOVE_CONTAINERS" = true ]; then
        docker rm agent-zero-redis 2>/dev/null || true
        echo -e "${GREEN}  ✓ Redis container removed${NC}"
    fi
else
    echo -e "${YELLOW}  ⚠ Redis not running${NC}"
fi

# Final status
echo -e "${YELLOW}[4/4] Verifying shutdown...${NC}"
RUNNING_CONTAINERS=$(docker ps --format '{{.Names}}' | grep -E "agent-zero|redis|searxng" || true)
if [ -z "$RUNNING_CONTAINERS" ]; then
    echo -e "${GREEN}  ✓ All services stopped successfully${NC}"
else
    echo -e "${RED}  ✗ Some services still running:${NC}"
    echo "$RUNNING_CONTAINERS"
fi

echo -e "\n${BLUE}═══════════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}✓ Pareng Boyong shutdown complete!${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}\n"

if [ "$REMOVE_CONTAINERS" = false ]; then
    echo -e "${BLUE}Note:${NC} Containers were stopped but not removed."
    echo "Use './stop_production.sh --remove' for complete cleanup."
else
    echo -e "${BLUE}Note:${NC} All containers have been removed."
    echo "Use './start_production.sh' to start fresh."
fi