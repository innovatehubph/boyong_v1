#!/bin/bash

# Pareng Boyong Production Startup Script
# This script starts the complete Pareng Boyong system as configured for ai.innovatehub.ph
# Usage: ./start_production.sh [--restart] [--logs]

set -e  # Exit on error

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Script configuration
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# Parse arguments
RESTART_MODE=false
SHOW_LOGS=false
for arg in "$@"; do
    case $arg in
        --restart)
            RESTART_MODE=true
            ;;
        --logs)
            SHOW_LOGS=true
            ;;
        --help)
            echo "Usage: $0 [--restart] [--logs]"
            echo "  --restart  Stop all services before starting"
            echo "  --logs     Show logs after starting"
            exit 0
            ;;
    esac
done

echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}       Pareng Boyong Production Startup Script${NC}"
echo -e "${BLUE}       Target: https://ai.innovatehub.ph${NC}"
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

# Function to wait for port to be available
wait_for_port() {
    local port=$1
    local max_attempts=30
    local attempt=0
    
    while [ $attempt -lt $max_attempts ]; do
        if nc -z localhost $port 2>/dev/null; then
            return 0
        fi
        attempt=$((attempt + 1))
        sleep 1
    done
    return 1
}

# Stop existing services if restart mode
if [ "$RESTART_MODE" = true ]; then
    echo -e "${YELLOW}[1/7] Stopping existing services...${NC}"
    
    # Stop main application
    if check_container "agent-zero-dev"; then
        echo "  Stopping agent-zero-dev..."
        docker stop agent-zero-dev 2>/dev/null || true
    fi
    
    # Stop support services
    for container in agent-zero-redis agent-zero-searxng; do
        if check_container "$container"; then
            echo "  Stopping $container..."
            docker stop $container 2>/dev/null || true
        fi
    done
    
    # Stop multimodal services
    for container in comfyui audiocraft bark localai pollinations wan2gp; do
        if check_container "$container"; then
            echo "  Stopping $container..."
            docker stop $container 2>/dev/null || true
        fi
    done
    
    echo -e "${GREEN}  ✓ All services stopped${NC}\n"
    sleep 2
fi

# Start Redis (required for session management)
echo -e "${YELLOW}[2/7] Starting Redis cache service...${NC}"
if ! check_container "agent-zero-redis"; then
    docker run -d \
        --name agent-zero-redis \
        --restart unless-stopped \
        --network bridge \
        redis:alpine
    echo -e "${GREEN}  ✓ Redis started${NC}"
else
    docker start agent-zero-redis 2>/dev/null || true
    echo -e "${GREEN}  ✓ Redis already running${NC}"
fi

# Start SearXNG (search engine)
echo -e "${YELLOW}[3/7] Starting SearXNG search engine...${NC}"
if ! check_container "agent-zero-searxng"; then
    docker run -d \
        --name agent-zero-searxng \
        --restart unless-stopped \
        --network bridge \
        -p 55510:8080 \
        searxng/searxng:latest
    echo -e "${GREEN}  ✓ SearXNG started${NC}"
else
    docker start agent-zero-searxng 2>/dev/null || true
    echo -e "${GREEN}  ✓ SearXNG already running${NC}"
fi

# Start main Agent Zero container
echo -e "${YELLOW}[4/7] Starting Agent Zero main application...${NC}"
if ! check_container "agent-zero-dev"; then
    # Check if we need to remove old container
    if docker ps -a --format '{{.Names}}' | grep -q "^agent-zero-dev$"; then
        echo "  Removing old container..."
        docker rm agent-zero-dev 2>/dev/null || true
    fi
    
    docker run -d \
        --name agent-zero-dev \
        --restart unless-stopped \
        --network bridge \
        -p 127.0.0.1:55080:80 \
        -p 127.0.0.1:55022:22 \
        -p 9000-9009:9000-9009 \
        -v "$SCRIPT_DIR:/a0" \
        -v "/var/www:/mnt/vps-www" \
        -v "/root:/mnt/vps-root" \
        -v "/tmp:/mnt/vps-tmp" \
        --cap-add SYS_ADMIN \
        --security-opt apparmor:unconfined \
        agent0ai/agent-zero:latest
    
    echo "  Waiting for application to start..."
    if wait_for_port 55080; then
        echo -e "${GREEN}  ✓ Agent Zero started successfully${NC}"
    else
        echo -e "${RED}  ✗ Agent Zero failed to start on port 55080${NC}"
    fi
else
    docker start agent-zero-dev 2>/dev/null || true
    echo -e "${GREEN}  ✓ Agent Zero already running${NC}"
fi

# Create symbolic links in container if needed
echo -e "${YELLOW}[5/7] Setting up VPS file access...${NC}"
docker exec agent-zero-dev bash -c "
    [ ! -L /a0/vps-www ] && ln -s /mnt/vps-www /a0/vps-www
    [ ! -L /a0/vps-root ] && ln -s /mnt/vps-root /a0/vps-root
    [ ! -L /a0/vps-tmp ] && ln -s /mnt/vps-tmp /a0/vps-tmp
" 2>/dev/null || true
echo -e "${GREEN}  ✓ VPS file access configured${NC}"

# Start multimodal services (optional)
echo -e "${YELLOW}[6/7] Starting multimodal services...${NC}"

# Check if docker-compose files exist
if [ -f "docker-compose.localai.yml" ]; then
    echo "  Starting LocalAI..."
    docker-compose -f docker-compose.localai.yml up -d 2>/dev/null || true
fi

if [ -f "docker-compose.comfyui.yml" ]; then
    echo "  Starting ComfyUI..."
    docker-compose -f docker-compose.comfyui.yml up -d 2>/dev/null || true
fi

# Start Pollinations server if script exists
if [ -f "pollinations_server.py" ]; then
    echo "  Starting Pollinations server..."
    docker exec -d agent-zero-dev bash -c "cd /a0 && python pollinations_server.py > /dev/null 2>&1" || true
fi

# Start Wan2GP server if script exists
if [ -f "wan2gp_server.py" ]; then
    echo "  Starting Wan2GP server..."
    docker exec -d agent-zero-dev bash -c "cd /a0 && python wan2gp_server.py > /dev/null 2>&1" || true
fi

echo -e "${GREEN}  ✓ Multimodal services initialization complete${NC}"

# Verify services
echo -e "${YELLOW}[7/7] Verifying services...${NC}"

# Check main application
if curl -s -o /dev/null -w "%{http_code}" http://localhost:55080 | grep -q "200\|401"; then
    echo -e "${GREEN}  ✓ Web UI responding on port 55080${NC}"
else
    echo -e "${RED}  ✗ Web UI not responding on port 55080${NC}"
fi

# Check Redis
if docker exec agent-zero-redis redis-cli ping 2>/dev/null | grep -q PONG; then
    echo -e "${GREEN}  ✓ Redis cache operational${NC}"
else
    echo -e "${YELLOW}  ⚠ Redis cache not responding${NC}"
fi

# Check SearXNG
if curl -s -o /dev/null -w "%{http_code}" http://localhost:55510 | grep -q "200"; then
    echo -e "${GREEN}  ✓ SearXNG search engine operational${NC}"
else
    echo -e "${YELLOW}  ⚠ SearXNG not responding${NC}"
fi

echo -e "\n${BLUE}═══════════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}✓ Pareng Boyong startup complete!${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}\n"

echo -e "${BLUE}Access Points:${NC}"
echo -e "  Web UI (Public):  ${GREEN}https://ai.innovatehub.ph${NC}"
echo -e "  Web UI (Local):   ${GREEN}http://localhost:55080${NC}"
echo -e "  SSH Access:       ${GREEN}ssh -p 55022 root@localhost${NC}"
echo -e "  Search Engine:    ${GREEN}http://localhost:55510${NC}\n"

echo -e "${BLUE}Container Status:${NC}"
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}" | grep -E "agent-zero|redis|searxng" || true

# Show logs if requested
if [ "$SHOW_LOGS" = true ]; then
    echo -e "\n${BLUE}Recent Logs:${NC}"
    docker logs agent-zero-dev --tail 20
fi

echo -e "\n${BLUE}Useful Commands:${NC}"
echo "  View logs:        docker logs agent-zero-dev --tail 50"
echo "  Enter container:  docker exec -it agent-zero-dev bash"
echo "  Restart app:      docker restart agent-zero-dev"
echo "  Stop all:         docker stop agent-zero-dev agent-zero-redis agent-zero-searxng"
echo ""