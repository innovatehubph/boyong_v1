#!/bin/bash

# Agent Zero Development Container Setup
# Following official Agent Zero development guide

set -e

PROJECT_DIR="/root/projects/pareng-boyong"
CONTAINER_NAME="agent-zero-dev"
HTTP_PORT="55080"
SSH_PORT="55022"

echo "🚀 Starting Agent Zero Development Container Setup..."

# Stop and remove existing container if it exists
if docker ps -a | grep -q "$CONTAINER_NAME"; then
    echo "🔄 Stopping existing development container..."
    docker stop "$CONTAINER_NAME" 2>/dev/null || true
    docker rm "$CONTAINER_NAME" 2>/dev/null || true
fi

# Run the development container
echo "🐳 Starting Agent Zero development container..."
echo "   - Container name: $CONTAINER_NAME"
echo "   - HTTP port: $HTTP_PORT (RFC HTTP + Web UI)"
echo "   - SSH port: $SSH_PORT (RFC SSH)"
echo "   - Volume mapping: $PROJECT_DIR:/a0"

docker run -d \
    --name "$CONTAINER_NAME" \
    -p "$HTTP_PORT:80" \
    -p "$SSH_PORT:22" \
    -v "$PROJECT_DIR:/a0" \
    agent0ai/agent-zero:latest

# Wait for container to start
echo "⏳ Waiting for container to initialize..."
sleep 10

# Check if container is running
if docker ps | grep -q "$CONTAINER_NAME"; then
    echo "✅ Development container is running!"
    
    # Display connection info
    echo ""
    echo "🔗 Development Container Information:"
    echo "   📡 Web UI: http://localhost:$HTTP_PORT"
    echo "   🔐 SSH: ssh root@localhost -p $SSH_PORT"
    echo "   📁 Volume: $PROJECT_DIR mapped to /a0"
    echo ""
    
    # Get container IP for internal communication
    CONTAINER_IP=$(docker inspect -f '{{range.NetworkSettings.Networks}}{{.IPAddress}}{{end}}' "$CONTAINER_NAME")
    echo "🌐 Container IP: $CONTAINER_IP"
    echo ""
    
    echo "📋 Next Steps:"
    echo "1. Configure RFC in main Agent Zero settings:"
    echo "   - RFC URL: localhost"
    echo "   - RFC HTTP Port: $HTTP_PORT"
    echo "   - RFC SSH Port: $SSH_PORT"
    echo "   - RFC Password: (set a secure password)"
    echo ""
    echo "2. Configure the same RFC password in development container at:"
    echo "   http://localhost:$HTTP_PORT/settings"
    echo ""
    echo "3. Test RFC connection by asking agent to execute code"
    echo ""
    
    # Show container logs (last 20 lines)
    echo "📜 Container startup logs:"
    docker logs --tail 20 "$CONTAINER_NAME"
    
else
    echo "❌ Failed to start development container"
    echo "📜 Container logs:"
    docker logs "$CONTAINER_NAME" 2>/dev/null || echo "No logs available"
    exit 1
fi