#!/bin/bash
# Pareng Boyong Self-Healing Auto-Start Script

echo "🚀 Starting Pareng Boyong with Self-Healing Protection"
cd /root/projects/pareng-boyong

# Start self-healing system in background
python3 auto_start_self_healing.py &
HEALING_PID=$!

# Start main Pareng Boyong application
python3 run_ui.py &
MAIN_PID=$!

echo "🛡️ Self-healing system PID: $HEALING_PID"
echo "🤖 Main application PID: $MAIN_PID"

# Keep both running
wait
