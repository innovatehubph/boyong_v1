
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
