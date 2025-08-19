#!/usr/bin/env python3
"""
Pareng Boyong Auto-Start Self-Healing System
Automatically starts the self-healing system when Pareng Boyong boots up
"""

import asyncio
import sys
import os
from pathlib import Path

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from python.helpers.log import Log
from python.helpers.self_healing_system import get_self_healing_system
from python.helpers.print_style import PrintStyle

async def auto_start_self_healing():
    """Automatically start self-healing system on Pareng Boyong startup"""
    
    PrintStyle(font_color="cyan").print("🚀 Pareng Boyong Auto-Start Self-Healing")
    PrintStyle(font_color="cyan").print("Initializing autonomous protection system...")
    
    try:
        # Initialize logger
        logger = Log()
        
        # Get self-healing system
        healing_system = get_self_healing_system(logger, None)
        
        # Check if already running
        if healing_system.enabled and healing_system.health_monitor.monitoring:
            PrintStyle(font_color="green").print("✅ Self-healing system already active")
            return True
        
        # Start self-healing system
        PrintStyle(font_color="cyan").print("🛡️ Starting self-healing protection...")
        
        # Start in background
        asyncio.create_task(healing_system.start_self_healing_system())
        
        # Wait a moment for initialization
        await asyncio.sleep(5)
        
        # Verify startup
        status = healing_system.get_self_healing_status()
        
        if status['system_enabled']:
            PrintStyle(font_color="green").print("🎉 Self-healing system successfully started!")
            PrintStyle(font_color="green").print("🛡️ Pareng Boyong is now protected by autonomous healing")
            
            # Show protection summary
            print("\n" + "=" * 60)
            print("🤖 PARENG BOYONG AUTONOMOUS PROTECTION ACTIVE")
            print("=" * 60)
            print("✅ Continuous health monitoring")
            print("✅ Automatic error detection")  
            print("✅ AI-powered recovery planning")
            print("✅ External AI integration (Claude Code)")
            print("✅ Automated healing execution")
            print("✅ System restoration verification")
            print("✅ Post-healing stability monitoring")
            print("=" * 60)
            
            return True
        else:
            PrintStyle(font_color="red").print("❌ Failed to start self-healing system")
            return False
            
    except Exception as e:
        PrintStyle(font_color="red").print(f"💥 Auto-start failed: {e}")
        return False

def create_startup_integration():
    """Create integration files for automatic self-healing startup"""
    
    PrintStyle(font_color="cyan").print("🔧 Creating startup integration...")
    
    # Create systemd service file (for Linux systems)
    systemd_service = """[Unit]
Description=Pareng Boyong Self-Healing System
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/root/projects/pareng-boyong
ExecStart=/usr/bin/python3 /root/projects/pareng-boyong/auto_start_self_healing.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
"""
    
    try:
        systemd_path = Path("/etc/systemd/system/pareng-boyong-healing.service")
        if systemd_path.parent.exists():
            systemd_path.write_text(systemd_service)
            PrintStyle(font_color="green").print(f"✅ Created systemd service: {systemd_path}")
    except:
        PrintStyle(font_color="yellow").print("⚠️ Could not create systemd service (permissions)")
    
    # Create startup script for manual use
    startup_script = """#!/bin/bash
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
"""
    
    startup_script_path = Path("/root/projects/pareng-boyong/start_with_healing.sh")
    startup_script_path.write_text(startup_script)
    startup_script_path.chmod(0o755)
    
    PrintStyle(font_color="green").print(f"✅ Created startup script: {startup_script_path}")
    
    # Create integration for run_ui.py
    integration_code = """
# Pareng Boyong Self-Healing Auto-Start Integration
# Add this to the beginning of run_ui.py main function

import asyncio
import sys
from pathlib import Path

# Auto-start self-healing system
try:
    sys.path.insert(0, str(Path(__file__).parent))
    from auto_start_self_healing import auto_start_self_healing
    
    # Start self-healing in background
    asyncio.create_task(auto_start_self_healing())
    print("🛡️ Self-healing system auto-started")
    
except Exception as e:
    print(f"⚠️ Self-healing auto-start failed: {e}")
"""
    
    integration_path = Path("/root/projects/pareng-boyong/self_healing_integration.py")
    integration_path.write_text(integration_code)
    
    PrintStyle(font_color="green").print(f"✅ Created integration code: {integration_path}")
    PrintStyle(font_color="cyan").print("🔧 Startup integration files created successfully")

if __name__ == "__main__":
    print("🤖 Pareng Boyong Self-Healing Auto-Start System")
    print("Autonomous protection initialization...")
    
    # Check if this is being run as startup integration
    if len(sys.argv) > 1 and sys.argv[1] == "--create-integration":
        create_startup_integration()
        sys.exit(0)
    
    # Run auto-start
    try:
        success = asyncio.run(auto_start_self_healing())
        
        if success:
            PrintStyle(font_color="green").print("🎯 Self-healing system is now protecting Pareng Boyong!")
            
            # Keep running to maintain the healing system
            print("Press Ctrl+C to stop self-healing system")
            
            try:
                # Keep the process alive
                while True:
                    asyncio.run(asyncio.sleep(60))
            except KeyboardInterrupt:
                PrintStyle(font_color="yellow").print("🛑 Self-healing system stopped by user")
                
        else:
            PrintStyle(font_color="red").print("❌ Failed to start self-healing protection")
            sys.exit(1)
            
    except Exception as e:
        PrintStyle(font_color="red").print(f"💥 Critical error: {e}")
        sys.exit(1)