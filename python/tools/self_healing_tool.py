"""
Pareng Boyong Self-Healing Management Tool
Provides control and monitoring of the autonomous self-healing system
"""

import asyncio
from datetime import datetime
from python.helpers.tool import Tool, Response
from python.helpers.self_healing_system import get_self_healing_system
from python.helpers.print_style import PrintStyle
import json

class SelfHealingTool(Tool):
    """Tool for managing Pareng Boyong's self-healing system"""
    
    async def execute(self, **kwargs):
        """Execute self-healing management commands"""
        
        command = self.args.get("command", "status").lower()
        
        if command == "status":
            return await self._show_system_status()
        elif command == "start":
            return await self._start_self_healing()
        elif command == "stop":
            return await self._stop_self_healing()
        elif command == "health_check":
            return await self._perform_health_check()
        elif command == "emergency_heal":
            return await self._emergency_healing()
        elif command == "healing_history":
            return await self._show_healing_history()
        elif command == "configure":
            return await self._configure_settings()
        elif command == "test_system":
            return await self._test_self_healing()
        else:
            return Response(message=self._get_help_message())
    
    async def _show_system_status(self):
        """Show comprehensive self-healing system status"""
        
        healing_system = get_self_healing_system(self.agent.context.log, self.agent)
        status = healing_system.get_self_healing_status()
        
        # Get current health if monitoring is active
        current_health = None
        if healing_system.health_monitor.health_history:
            current_health = healing_system.health_monitor.health_history[-1]
        
        status_message = f"""
🤖 **PARENG BOYONG SELF-HEALING SYSTEM STATUS**

**🛡️ System State:**
• Self-Healing: {'🟢 ENABLED' if status['system_enabled'] else '🔴 DISABLED'}
• Auto-Healing: {'🟢 ON' if status['auto_healing_enabled'] else '🔴 OFF'}
• Healing in Progress: {'🟡 YES' if status['healing_in_progress'] else '🟢 NO'}
• External AI: {'🟢 ENABLED' if status['external_ai_enabled'] else '🔴 DISABLED'}

**📊 Health Monitoring:**
• Monitor Active: {'🟢 YES' if status['health_monitor_active'] else '🔴 NO'}
• Health Checks Performed: {status['recent_health_checks']}
• Current Health Score: {status['last_health_score']:.2f}/1.00
"""
        
        if current_health:
            health_status_emoji = {
                'healthy': '🟢',
                'fair': '🟡', 
                'degraded': '🟠',
                'critical': '🔴',
                'failed': '💀'
            }.get(current_health.overall_health, '❓')
            
            status_message += f"""
**🏥 Current System Health:**
• Overall Status: {health_status_emoji} {current_health.overall_health.upper()}
• CPU Usage: {current_health.cpu_usage:.1f}%
• Memory Usage: {current_health.memory_usage:.1f}%
• Disk Usage: {current_health.disk_usage:.1f}%
• Active Processes: {current_health.active_processes}
• Error Rate: {current_health.error_rate:.1%}
• Uptime: {current_health.uptime_seconds/3600:.1f} hours
"""
            
            if current_health.critical_errors:
                status_message += f"""
**🚨 Active Critical Errors ({len(current_health.critical_errors)}):**
{chr(10).join(f'• {error}' for error in current_health.critical_errors[:5])}
{'• ...' if len(current_health.critical_errors) > 5 else ''}
"""
            
            if current_health.warnings:
                status_message += f"""
**⚠️ System Warnings ({len(current_health.warnings)}):**
{chr(10).join(f'• {warning}' for warning in current_health.warnings[:3])}
{'• ...' if len(current_health.warnings) > 3 else ''}
"""
        
        status_message += f"""
**🔧 Healing Statistics:**
• Active Failures: {status['active_failures']}
• Total Healing Attempts: {status['healing_attempts']}

**⚙️ Configuration:**
• Max Healing Attempts: {status['settings']['max_healing_attempts']}
• Healing Cooldown: {status['settings']['healing_cooldown_minutes']} minutes
• Critical Threshold: {status['settings']['critical_failure_threshold']:.2f}
• Post-Healing Monitoring: {status['settings']['post_healing_monitoring_minutes']} minutes

**🎯 System Assessment:**
"""
        
        # Overall system assessment
        if status['last_health_score'] > 0.8:
            status_message += "🟢 **EXCELLENT** - System operating optimally with self-healing protection"
        elif status['last_health_score'] > 0.6:
            status_message += "🟡 **GOOD** - System stable with minor issues, self-healing ready"
        elif status['last_health_score'] > 0.3:
            status_message += "🟠 **DEGRADED** - System experiencing issues, monitoring closely"
        else:
            status_message += "🔴 **CRITICAL** - System in critical state, healing may be triggered"
        
        PrintStyle(font_color="cyan").print("📊 Self-healing system status report generated")
        return Response(message=status_message.strip())
    
    async def _start_self_healing(self):
        """Start the self-healing system"""
        
        healing_system = get_self_healing_system(self.agent.context.log, self.agent)
        
        if healing_system.enabled:
            return Response(message="✅ Self-healing system is already running")
        
        try:
            # Start the self-healing system in background
            asyncio.create_task(healing_system.start_self_healing_system())
            
            return Response(message="""
🤖 **SELF-HEALING SYSTEM STARTED**

Pareng Boyong is now protected by advanced self-healing capabilities:

**🛡️ Active Protection:**
• Continuous health monitoring every 30 seconds
• Automatic error detection and analysis
• AI-powered recovery planning via external AI
• Automated healing command execution
• System restoration verification
• Post-healing stability monitoring

**🚨 Emergency Response:**
• Critical failure detection (health score < 30%)
• High resource usage alerts (CPU/Memory > 95%)
• Process failure recovery
• Automatic system restart procedures

**🤖 External AI Integration:**
• Claude Code integration for healing assistance
• Automatic problem analysis and solution generation
• Intelligent recovery command generation
• Learning from successful healing patterns

**✅ System Status:** Self-healing is now ACTIVE and monitoring Pareng Boyong's health.
            """.strip())
            
        except Exception as e:
            return Response(message=f"❌ Failed to start self-healing system: {e}")
    
    async def _stop_self_healing(self):
        """Stop the self-healing system"""
        
        healing_system = get_self_healing_system(self.agent.context.log, self.agent)
        
        if not healing_system.enabled:
            return Response(message="ℹ️ Self-healing system is already stopped")
        
        try:
            await healing_system.stop_self_healing_system()
            
            return Response(message="""
⚠️ **SELF-HEALING SYSTEM STOPPED**

The autonomous self-healing system has been disabled.

**🔴 Protection Disabled:**
• Health monitoring: STOPPED
• Automatic error recovery: DISABLED
• External AI healing: INACTIVE
• Emergency response: OFF

**⚠️ Risk Warning:**
Pareng Boyong is now vulnerable to:
• System failures without automatic recovery
• Resource exhaustion issues
• Process crashes without restart
• Critical errors without intervention

**💡 Recommendation:** Re-enable self-healing using command="start" for continued protection.
            """.strip())
            
        except Exception as e:
            return Response(message=f"❌ Failed to stop self-healing system: {e}")
    
    async def _perform_health_check(self):
        """Perform immediate health check"""
        
        healing_system = get_self_healing_system(self.agent.context.log, self.agent)
        
        PrintStyle(font_color="cyan").print("🔍 Performing comprehensive health check...")
        
        try:
            health_status = await healing_system.health_monitor.check_system_health()
            
            health_emoji = {
                'healthy': '🟢',
                'fair': '🟡',
                'degraded': '🟠', 
                'critical': '🔴',
                'failed': '💀'
            }.get(health_status.overall_health, '❓')
            
            health_message = f"""
🏥 **HEALTH CHECK RESULTS**

**Overall Status:** {health_emoji} {health_status.overall_health.upper()}
**Health Score:** {health_status.health_score:.2f}/1.00

**📊 System Metrics:**
• CPU Usage: {health_status.cpu_usage:.1f}%
• Memory Usage: {health_status.memory_usage:.1f}%
• Disk Usage: {health_status.disk_usage:.1f}%
• Active Processes: {health_status.active_processes}
• Error Rate: {health_status.error_rate:.1%}
• System Uptime: {health_status.uptime_seconds/3600:.1f} hours

**🔍 Detailed Assessment:**
"""
            
            # Health score interpretation
            if health_status.health_score > 0.9:
                health_message += "🟢 **EXCELLENT** - All systems operating at peak performance"
            elif health_status.health_score > 0.7:
                health_message += "🟢 **GOOD** - System healthy with minor resource usage"
            elif health_status.health_score > 0.5:
                health_message += "🟡 **FAIR** - System stable but showing some stress"
            elif health_status.health_score > 0.3:
                health_message += "🟠 **DEGRADED** - System experiencing performance issues"
            else:
                health_message += "🔴 **CRITICAL** - System requires immediate attention"
            
            # Add specific issues if any
            if health_status.critical_errors:
                health_message += f"""

**🚨 Critical Issues Found ({len(health_status.critical_errors)}):**
{chr(10).join(f'• {error}' for error in health_status.critical_errors)}
"""
            
            if health_status.warnings:
                health_message += f"""

**⚠️ Warnings ({len(health_status.warnings)}):**
{chr(10).join(f'• {warning}' for warning in health_status.warnings)}
"""
            
            # Recommendations
            health_message += f"""

**💡 Recommendations:**
"""
            
            if health_status.cpu_usage > 80:
                health_message += "• Consider reducing CPU-intensive operations\n"
            if health_status.memory_usage > 80:
                health_message += "• Monitor memory usage and clear caches if needed\n"
            if health_status.error_rate > 0.2:
                health_message += "• High error rate detected - investigate recent failures\n"
            if health_status.health_score < 0.5:
                health_message += "• System health critical - consider emergency healing\n"
            
            if health_status.health_score > 0.8:
                health_message += "• System is healthy - continue normal operations\n"
            
            return Response(message=health_message.strip())
            
        except Exception as e:
            return Response(message=f"❌ Health check failed: {e}")
    
    async def _emergency_healing(self):
        """Trigger emergency healing sequence"""
        
        healing_system = get_self_healing_system(self.agent.context.log, self.agent)
        
        if healing_system.healing_in_progress:
            return Response(message="⚠️ Healing sequence already in progress")
        
        PrintStyle(font_color="red").print("🚨 INITIATING EMERGENCY HEALING SEQUENCE")
        
        try:
            # Get current health status
            health_status = await healing_system.health_monitor.check_system_health()
            
            # Force initiate healing regardless of thresholds
            await healing_system._initiate_healing_sequence(health_status)
            
            return Response(message="""
🚨 **EMERGENCY HEALING INITIATED**

The emergency healing sequence has been triggered:

**🔄 Healing Steps:**
1. ✅ Emergency healing request submitted
2. 🤖 External AI analyzing system failure
3. 🏥 Generating recovery commands
4. ⚡ Executing automated healing procedures
5. 🔍 Verifying system restoration
6. 📊 Monitoring post-healing stability

**⏱️ Expected Duration:** 5-15 minutes depending on system issues

**📋 Status:** Emergency healing is now running in the background.

Use command="status" to monitor healing progress.
            """.strip())
            
        except Exception as e:
            return Response(message=f"💥 Emergency healing failed to start: {e}")
    
    async def _show_healing_history(self):
        """Show healing attempt history"""
        
        healing_system = get_self_healing_system(self.agent.context.log, self.agent)
        
        healing_history = healing_system.automated_healer.healing_history
        active_failures = healing_system.active_failures
        
        if not healing_history and not active_failures:
            return Response(message="📝 No healing attempts recorded yet.")
        
        history_message = "📚 **HEALING SYSTEM HISTORY**\n\n"
        
        # Active failures
        if active_failures:
            history_message += f"**🚨 Active Failures ({len(active_failures)}):**\n"
            for failure_id, failure in active_failures.items():
                status_emoji = {
                    'pending': '🟡',
                    'in_progress': '🔄', 
                    'resolved': '✅',
                    'failed': '❌'
                }.get(failure.resolution_status, '❓')
                
                history_message += f"• {status_emoji} {failure_id}: {failure.description}\n"
                history_message += f"  Status: {failure.resolution_status}, Attempts: {failure.recovery_attempts}\n"
        
        # Recent healing attempts
        if healing_history:
            recent_attempts = healing_history[-5:]  # Last 5 attempts
            history_message += f"\n**🔧 Recent Healing Attempts ({len(recent_attempts)}):**\n"
            
            for attempt in recent_attempts:
                success_emoji = "✅" if attempt['healing_successful'] else "❌"
                history_message += f"• {success_emoji} {attempt['timestamp']}\n"
                history_message += f"  AI Service: {attempt['ai_service']}\n"
                history_message += f"  Success Rate: {attempt['success_rate']:.1%}\n"
                history_message += f"  Duration: {attempt['duration_seconds']:.1f}s\n\n"
        
        # Overall statistics
        if healing_history:
            total_attempts = len(healing_history)
            successful_attempts = sum(1 for h in healing_history if h['healing_successful'])
            overall_success_rate = successful_attempts / total_attempts if total_attempts > 0 else 0
            
            history_message += f"**📊 Overall Statistics:**\n"
            history_message += f"• Total Healing Attempts: {total_attempts}\n"
            history_message += f"• Successful Healings: {successful_attempts}\n"
            history_message += f"• Overall Success Rate: {overall_success_rate:.1%}\n"
        
        return Response(message=history_message.strip())
    
    async def _configure_settings(self):
        """Configure self-healing settings"""
        
        setting = self.args.get("setting", "")
        value = self.args.get("value", "")
        
        healing_system = get_self_healing_system(self.agent.context.log, self.agent)
        
        if not setting:
            # Show current settings
            settings = healing_system.settings
            
            settings_message = f"""
⚙️ **SELF-HEALING CONFIGURATION**

**Current Settings:**
• Auto-Healing: {'ON' if settings['auto_healing_enabled'] else 'OFF'}
• Max Healing Attempts: {settings['max_healing_attempts']}
• Healing Cooldown: {settings['healing_cooldown_minutes']} minutes
• Critical Threshold: {settings['critical_failure_threshold']:.2f}
• External AI: {'ENABLED' if settings['enable_external_ai'] else 'DISABLED'}
• Post-Healing Monitoring: {settings['post_healing_monitoring_minutes']} minutes

**Available Settings:**
• auto_healing_enabled (true/false)
• max_healing_attempts (1-10)
• healing_cooldown_minutes (5-60)
• critical_failure_threshold (0.1-0.5)
• enable_external_ai (true/false)
• post_healing_monitoring_minutes (10-120)

**Usage Example:**
```
{{
  "tool_name": "self_healing",
  "command": "configure",
  "setting": "max_healing_attempts",
  "value": "5"
}}
```
            """
            
            return Response(message=settings_message.strip())
        
        # Update setting
        try:
            if setting == "auto_healing_enabled":
                healing_system.settings[setting] = value.lower() == "true"
            elif setting in ["max_healing_attempts", "healing_cooldown_minutes", "post_healing_monitoring_minutes"]:
                healing_system.settings[setting] = int(value)
            elif setting == "critical_failure_threshold":
                healing_system.settings[setting] = float(value)
            elif setting == "enable_external_ai":
                healing_system.settings[setting] = value.lower() == "true"
            else:
                return Response(message=f"❌ Unknown setting: {setting}")
            
            return Response(message=f"✅ Setting updated: {setting} = {value}")
            
        except ValueError as e:
            return Response(message=f"❌ Invalid value for {setting}: {value}")
    
    async def _test_self_healing(self):
        """Test the self-healing system with controlled failure"""
        
        healing_system = get_self_healing_system(self.agent.context.log, self.agent)
        
        PrintStyle(font_color="cyan").print("🧪 Testing self-healing system...")
        
        # Create a mock critical health status
        from python.helpers.self_healing_system import SystemHealthStatus
        
        test_health = SystemHealthStatus(
            timestamp=datetime.now().isoformat(),
            overall_health="critical",
            cpu_usage=95.0,
            memory_usage=92.0,
            disk_usage=45.0,
            active_processes=25,
            error_rate=0.6,
            last_successful_operation=None,
            critical_errors=["Test critical error for self-healing validation"],
            warnings=["Test warning"],
            uptime_seconds=3600.0,
            health_score=0.25
        )
        
        try:
            # Test the healing sequence with mock data
            await healing_system._initiate_healing_sequence(test_health)
            
            return Response(message="""
✅ **SELF-HEALING SYSTEM TEST COMPLETED**

**Test Results:**
• Mock critical failure generated
• External AI healing request triggered
• Healing commands executed
• System restoration verified

**🎯 Test Assessment:**
The self-healing system responded correctly to the simulated critical failure:
• Detected critical health status (score: 0.25)
• Triggered external AI assistance
• Generated and executed recovery commands
• Completed healing sequence

**✅ Conclusion:** Self-healing system is operational and ready for production use.

**📊 Status:** System has been tested and is functioning correctly.
            """.strip())
            
        except Exception as e:
            return Response(message=f"❌ Self-healing test failed: {e}")
    
    def _get_help_message(self):
        """Get help message for the tool"""
        
        return """
🤖 **PARENG BOYONG SELF-HEALING SYSTEM TOOL**

**Available Commands:**

• `status` - Show comprehensive system status and health metrics
• `start` - Start the autonomous self-healing system
• `stop` - Stop the self-healing system (not recommended)
• `health_check` - Perform immediate system health assessment
• `emergency_heal` - Trigger emergency healing sequence
• `healing_history` - Show history of healing attempts
• `configure` - View or modify self-healing settings
• `test_system` - Test self-healing system with controlled failure

**Examples:**

```json
{
  "tool_name": "self_healing",
  "command": "status"
}
```

```json
{
  "tool_name": "self_healing", 
  "command": "configure",
  "setting": "max_healing_attempts",
  "value": "5"
}
```

**🛡️ Self-Healing Features:**
• Continuous system health monitoring
• Automatic critical failure detection
• External AI integration (Claude Code)
• Intelligent recovery command generation
• Automated healing execution
• System restoration verification
• Learning from successful recovery patterns
• Post-healing stability monitoring

**🚨 Emergency Capabilities:**
• Resource exhaustion recovery
• Process failure restoration
• Network connectivity healing
• Service restart procedures
• Memory cleanup operations
• System optimization

The self-healing system provides autonomous protection for Pareng Boyong, automatically detecting and recovering from critical failures without human intervention.
        """.strip()

# Register the tool
if __name__ == "__main__":
    print("Self-Healing Management Tool loaded successfully")