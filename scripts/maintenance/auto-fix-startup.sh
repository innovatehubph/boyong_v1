#!/bin/bash

# Pareng Boyong Auto-Fix Startup Script
# This script automatically fixes common dependency issues on container startup

CONTAINER_NAME="agent-zero-dev"
LOG_FILE="/root/projects/pareng-boyong/auto-fix.log"

# Logging function
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

log "🚀 Auto-fix startup initiated..."

# Check if container exists
if ! docker ps -a --format "table {{.Names}}" | grep -q "^${CONTAINER_NAME}$"; then
    log "❌ Container ${CONTAINER_NAME} does not exist"
    exit 1
fi

# Start container if it's not running
if ! docker ps --format "table {{.Names}}" | grep -q "^${CONTAINER_NAME}$"; then
    log "🔄 Starting container ${CONTAINER_NAME}..."
    docker start ${CONTAINER_NAME}
    sleep 10
fi

# Check for common dependency errors in logs
log "🔍 Checking for dependency issues..."
if docker logs --tail 50 ${CONTAINER_NAME} 2>&1 | grep -q "ModuleNotFoundError\|ImportError"; then
    log "⚠️ Dependency issues detected. Running fix..."
    
    # Run the dependency fix script
    /root/projects/pareng-boyong/fix-dependencies.sh
    
    if [ $? -eq 0 ]; then
        log "✅ Dependency fix completed successfully"
    else
        log "❌ Dependency fix failed"
        exit 1
    fi
else
    log "✅ No dependency issues found"
fi

# Final health check
log "🏥 Performing final health check..."
for i in {1..15}; do
    if curl -s --max-time 5 http://localhost:55080 >/dev/null 2>&1; then
        log "✅ Pareng Boyong is healthy and ready!"
        log "🌐 Web interface: http://localhost:55080"
        log "🌐 Public URL: https://ai.innovatehub.ph"
        
        # Check Docker multimedia services
        docker ps --format "table {{.Names}}\t{{.Status}}" | grep -E "pollinations|wan2gp|localai" | while read line; do
            log "🐳 $line"
        done
        
        exit 0
    fi
    log "⏳ Health check attempt $i/15..."
    sleep 2
done

log "❌ Health check failed. Service may not be responding properly."
log "📋 Recent logs:"
docker logs --tail 10 ${CONTAINER_NAME} | while read line; do
    log "LOG: $line"
done

exit 1