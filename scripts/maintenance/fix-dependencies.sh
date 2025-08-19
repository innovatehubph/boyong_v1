#!/bin/bash

# Pareng Boyong Dependency Fix Script
# Permanent solution for recurring dependency issues

echo "🔧 Fixing Pareng Boyong Dependencies..."

CONTAINER_NAME="agent-zero-dev"

# Check if container is running
if ! docker ps --format "table {{.Names}}" | grep -q "^${CONTAINER_NAME}$"; then
    echo "❌ Container ${CONTAINER_NAME} is not running"
    exit 1
fi

echo "📦 Installing/Upgrading problematic packages..."

# Fix transformers and sentence-transformers compatibility issues
docker exec ${CONTAINER_NAME} /opt/venv/bin/pip install --upgrade \
    transformers==4.44.2 \
    sentence-transformers==2.7.0 \
    torch==2.4.0 \
    tokenizers==0.19.1 \
    huggingface-hub==0.24.7 \
    accelerate==0.34.2 \
    scipy==1.11.4

# Fix additional AI/ML dependencies that cause conflicts
docker exec ${CONTAINER_NAME} /opt/venv/bin/pip install --upgrade \
    numpy==1.24.4 \
    scikit-learn==1.3.2 \
    safetensors==0.4.5 \
    datasets==2.21.0

# Fix web/API dependencies
docker exec ${CONTAINER_NAME} /opt/venv/bin/pip install --upgrade \
    aiohttp==3.10.6 \
    flask==3.0.3 \
    werkzeug==3.0.4 \
    requests==2.32.3

# Fix litellm and related dependencies
docker exec ${CONTAINER_NAME} /opt/venv/bin/pip install --upgrade \
    litellm==1.47.4 \
    openai==1.51.2 \
    anthropic==0.34.2

# Install additional stability packages
docker exec ${CONTAINER_NAME} /opt/venv/bin/pip install \
    protobuf==4.25.5 \
    grpcio==1.66.2 \
    pydantic==2.9.2

echo "🔄 Restarting container..."
docker restart ${CONTAINER_NAME}

echo "⏳ Waiting for container to start..."
sleep 20

# Check if service is responding
echo "🏥 Health checking..."
for i in {1..30}; do
    if curl -s --max-time 5 http://localhost:55080 >/dev/null 2>&1; then
        echo "✅ Pareng Boyong is back online!"
        echo "🌐 Available at: http://localhost:55080"
        echo "🌐 Available at: https://ai.innovatehub.ph"
        exit 0
    fi
    echo "⏳ Attempt $i/30 - Still starting..."
    sleep 2
done

echo "❌ Service did not come back online. Check logs:"
echo "docker logs --tail 20 ${CONTAINER_NAME}"
exit 1