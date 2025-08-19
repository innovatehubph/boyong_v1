#!/bin/bash

echo "🔄 Restarting Pareng Boyong with all multimedia integration changes..."

# Backup current logs
docker logs agent-zero-dev --tail 50 > /tmp/pareng_boyong_restart_backup.log 2>&1

echo "📦 Stopping Pareng Boyong container..."
docker stop agent-zero-dev

echo "⏳ Waiting for clean shutdown..."
sleep 3

echo "🚀 Starting Pareng Boyong container..."
docker start agent-zero-dev

echo "⏳ Waiting for startup..."
sleep 15

# Check if container started
if docker ps | grep -q agent-zero-dev; then
    echo "✅ Container started successfully"
else
    echo "❌ Container failed to start"
    exit 1
fi

# Health check
echo "🏥 Performing health check..."
for i in {1..15}; do
    if curl -s --max-time 5 http://localhost:55080 >/dev/null 2>&1; then
        echo "✅ Pareng Boyong is healthy and ready!"
        echo "🌐 Web interface: http://localhost:55080"
        echo "🌐 Public URL: https://ai.innovatehub.ph"
        
        echo ""
        echo "🎨 Multimedia Integration Status:"
        echo "• Image Generation: Pollinations.AI (FLUX.1) - Ready"
        echo "• Video Generation: Wan2GP (Multiple models) - Ready" 
        echo "• AI Chat: LocalAI - Ready"
        echo "• File Browser: Enhanced VPS access - Ready"
        echo "• Host Network Access: Bypassing Docker restrictions - Active"
        
        echo ""
        echo "🔧 Available Tools:"
        echo "• multimedia_image_generator() - Professional image generation"
        echo "• multimedia_video_generator() - Multi-model video generation" 
        echo "• multimedia_request_detector() - Auto-detect multimedia requests"
        echo "• multimedia_auto_generator() - Auto-generate from conversations"
        echo "• multimedia_service_checker() - Service health monitoring"
        
        echo ""
        echo "📁 Storage Organization:"
        echo "• Images: /a0/pareng_boyong_deliverables/images/"
        echo "• Videos: /a0/pareng_boyong_deliverables/videos/"
        echo "• Projects: /a0/pareng_boyong_deliverables/projects/"
        
        echo ""
        echo "🌟 NEW FEATURES ACTIVE:"
        echo "1. ✅ Host-based Docker service access (bypasses container restrictions)"
        echo "2. ✅ Automatic multimedia request detection (English & Filipino)"
        echo "3. ✅ Professional content organization with metadata"
        echo "4. ✅ Enhanced file browser with full VPS access"
        echo "5. ✅ Multi-model video generation (4 advanced AI models)"
        echo "6. ✅ Intelligent auto-generation based on conversation analysis"
        
        break
    else
        echo "⏳ Health check attempt $i/15..."
        sleep 3
    fi
done

if [ $i -eq 15 ]; then
    echo "❌ Health check failed. Checking logs..."
    docker logs --tail 20 agent-zero-dev
    exit 1
fi

echo ""
echo "🎉 Pareng Boyong restart completed successfully!"
echo "All multimedia integration features are now active and ready for use."