#!/bin/bash

echo "🎬 Setting up Video Generation Services for Pareng Boyong..."

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker first."
    exit 1
fi

# Check if NVIDIA Docker runtime is available
if docker run --rm --gpus all nvidia/cuda:11.8-base nvidia-smi > /dev/null 2>&1; then
    echo "✅ NVIDIA GPU support detected"
    USE_GPU=true
else
    echo "⚠️  No GPU support detected, using CPU-only mode"
    USE_GPU=false
fi

# Build and start ComfyUI container
echo "🔨 Building ComfyUI container..."
if [ "$USE_GPU" = true ]; then
    docker-compose -f docker-compose.comfyui.yml up -d --build
else
    # Modify for CPU-only mode
    sed -i 's/nvidia\/cuda:11.8-devel-ubuntu22.04/python:3.11-slim/' Dockerfile.comfyui
    sed -i '/deploy:/,/capabilities: \[gpu\]/d' docker-compose.comfyui.yml
    docker-compose -f docker-compose.comfyui.yml up -d --build
fi

# Wait for ComfyUI to be ready
echo "⏳ Waiting for ComfyUI to start..."
timeout 120 bash -c 'until curl -s http://localhost:8188/system_stats > /dev/null; do sleep 2; done'

if curl -s http://localhost:8188/system_stats > /dev/null; then
    echo "✅ ComfyUI is running on http://localhost:8188"
else
    echo "❌ ComfyUI failed to start"
    docker-compose -f docker-compose.comfyui.yml logs comfyui
    exit 1
fi

# Test video generation
echo "🧪 Testing video generation capabilities..."
python3 -c "
import asyncio
import sys
sys.path.append('python/helpers')

async def test():
    try:
        from video_generation import test_generation
        result = await test_generation()
        if result:
            print('✅ Video generation test passed!')
        else:
            print('⚠️  Video generation test incomplete - may need models')
    except Exception as e:
        print(f'⚠️  Video generation test failed: {e}')

asyncio.run(test())
"

echo ""
echo "🎉 Video Generation Setup Complete!"
echo ""
echo "📋 Available Services:"
echo "  🖼️  ComfyUI Web Interface: http://localhost:8188"
echo "  🎬 Video Processor API: http://localhost:8189"
echo ""
echo "📖 Usage:"
echo "  - Basic video generation: Use video_generator tool"
echo "  - Advanced video generation: Use advanced_video_generator tool"
echo "  - Image animation: Both tools support image-to-video"
echo ""
echo "🔧 Management Commands:"
echo "  - Start: docker-compose -f docker-compose.comfyui.yml up -d"
echo "  - Stop: docker-compose -f docker-compose.comfyui.yml down"
echo "  - Logs: docker-compose -f docker-compose.comfyui.yml logs -f"
echo "  - Status: docker-compose -f docker-compose.comfyui.yml ps"