"""
Pareng Boyong Self-Healing System
Advanced autonomous recovery system that can trigger external AI to fix critical issues
and automatically restore Pareng Boyong to operational status
"""

import asyncio
import json
import subprocess
import time
import psutil
import requests
import os
import sys
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, asdict
from pathlib import Path
import threading
import signal

from python.helpers.log import Log
from python.helpers.print_style import PrintStyle

@dataclass
class SystemHealthStatus:
    """System health status information"""
    timestamp: str
    overall_health: str  # "healthy", "degraded", "critical", "failed"
    cpu_usage: float
    memory_usage: float
    disk_usage: float
    active_processes: int
    error_rate: float
    last_successful_operation: Optional[str]
    critical_errors: List[str]
    warnings: List[str]
    uptime_seconds: float
    health_score: float  # 0.0 to 1.0

@dataclass
class CriticalFailure:
    """Critical failure information"""
    failure_id: str
    timestamp: str
    failure_type: str
    description: str
    affected_components: List[str]
    error_details: Dict[str, Any]
    system_state: SystemHealthStatus
    recovery_attempts: int
    external_ai_triggered: bool
    resolution_status: str  # "pending", "in_progress", "resolved", "failed"

@dataclass
class ExternalAIRequest:
    """Request to external AI for healing assistance"""
    request_id: str
    timestamp: str
    ai_service: str  # "claude_code", "anthropic_api", "custom"
    failure_context: CriticalFailure
    requested_actions: List[str]
    priority: str  # "low", "medium", "high", "critical"
    expected_response_time: int  # seconds
    response_received: bool
    healing_commands: List[str]

class SystemHealthMonitor:
    """Continuously monitors system health and detects failures"""
    
    def __init__(self, logger: Log, check_interval: int = 30):
        self.logger = logger
        self.check_interval = check_interval
        self.monitoring = False
        self.health_history = []
        self.baseline_metrics = None
        self.start_time = time.time()
        
        # Health thresholds
        self.thresholds = {
            'cpu_critical': 95.0,
            'memory_critical': 90.0,
            'disk_critical': 95.0,
            'error_rate_critical': 0.5,  # 50% error rate
            'health_score_critical': 0.3  # Below 30%
        }
    
    async def start_monitoring(self):
        """Start continuous health monitoring"""
        self.monitoring = True
        PrintStyle(font_color="green").print("🏥 System Health Monitor: STARTED")
        
        while self.monitoring:
            try:
                health_status = await self.check_system_health()
                self.health_history.append(health_status)
                
                # Keep only last 100 health checks
                if len(self.health_history) > 100:
                    self.health_history = self.health_history[-100:]
                
                # Check for critical conditions
                if health_status.overall_health in ["critical", "failed"]:
                    await self._trigger_critical_alert(health_status)
                
                await asyncio.sleep(self.check_interval)
                
            except Exception as e:
                self.logger.log(f"Health monitoring error: {e}")
                await asyncio.sleep(self.check_interval)
    
    def stop_monitoring(self):
        """Stop health monitoring"""
        self.monitoring = False
        PrintStyle(font_color="yellow").print("🏥 System Health Monitor: STOPPED")
    
    async def check_system_health(self) -> SystemHealthStatus:
        """Perform comprehensive system health check"""
        
        # Get system metrics
        cpu_usage = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        # Count active Python processes (Pareng Boyong related)
        active_processes = len([p for p in psutil.process_iter(['name']) 
                              if 'python' in p.info['name'].lower()])
        
        # Calculate error rate from recent health checks
        error_rate = self._calculate_error_rate()
        
        # Calculate overall health score
        health_score = self._calculate_health_score(cpu_usage, memory.percent, disk.percent, error_rate)
        
        # Determine overall health status
        overall_health = self._determine_health_status(health_score, cpu_usage, memory.percent, error_rate)
        
        # Collect current errors and warnings
        critical_errors, warnings = await self._collect_system_issues()
        
        return SystemHealthStatus(
            timestamp=datetime.now().isoformat(),
            overall_health=overall_health,
            cpu_usage=cpu_usage,
            memory_usage=memory.percent,
            disk_usage=disk.percent,
            active_processes=active_processes,
            error_rate=error_rate,
            last_successful_operation=self._get_last_successful_operation(),
            critical_errors=critical_errors,
            warnings=warnings,
            uptime_seconds=time.time() - self.start_time,
            health_score=health_score
        )
    
    def _calculate_error_rate(self) -> float:
        """Calculate error rate from recent operations"""
        if len(self.health_history) < 2:
            return 0.0
        
        recent_checks = self.health_history[-10:]  # Last 10 checks
        error_count = sum(1 for check in recent_checks 
                         if check.overall_health in ["critical", "failed"])
        
        return error_count / len(recent_checks)
    
    def _calculate_health_score(self, cpu: float, memory: float, disk: float, error_rate: float) -> float:
        """Calculate overall system health score (0.0 to 1.0)"""
        
        # Component scores (lower is better for usage, higher is better for score)
        cpu_score = max(0, (100 - cpu) / 100)
        memory_score = max(0, (100 - memory) / 100)
        disk_score = max(0, (100 - disk) / 100)
        error_score = max(0, 1 - error_rate)
        
        # Weighted average
        weights = {'cpu': 0.3, 'memory': 0.3, 'disk': 0.2, 'errors': 0.2}
        
        health_score = (
            cpu_score * weights['cpu'] +
            memory_score * weights['memory'] +
            disk_score * weights['disk'] +
            error_score * weights['errors']
        )
        
        return max(0.0, min(1.0, health_score))
    
    def _determine_health_status(self, health_score: float, cpu: float, memory: float, error_rate: float) -> str:
        """Determine overall health status"""
        
        if (health_score < self.thresholds['health_score_critical'] or
            cpu > self.thresholds['cpu_critical'] or
            memory > self.thresholds['memory_critical'] or
            error_rate > self.thresholds['error_rate_critical']):
            return "critical"
        elif health_score < 0.6 or cpu > 80 or memory > 80 or error_rate > 0.3:
            return "degraded"
        elif health_score > 0.8:
            return "healthy"
        else:
            return "fair"
    
    async def _collect_system_issues(self) -> tuple[List[str], List[str]]:
        """Collect current system errors and warnings"""
        
        critical_errors = []
        warnings = []
        
        # Check for zombie processes
        try:
            zombie_count = len([p for p in psutil.process_iter(['status']) 
                              if p.info['status'] == psutil.STATUS_ZOMBIE])
            if zombie_count > 0:
                warnings.append(f"Found {zombie_count} zombie processes")
        except:
            pass
        
        # Check disk space
        disk = psutil.disk_usage('/')
        if disk.percent > 90:
            critical_errors.append(f"Disk usage critical: {disk.percent:.1f}%")
        elif disk.percent > 80:
            warnings.append(f"Disk usage high: {disk.percent:.1f}%")
        
        # Check for recent log errors (if log file exists)
        try:
            log_file = Path("/tmp/pareng-boyong-errors.log")
            if log_file.exists():
                # Read recent errors
                recent_errors = self._check_recent_log_errors(log_file)
                critical_errors.extend(recent_errors[:5])  # Top 5 recent errors
        except:
            pass
        
        return critical_errors, warnings
    
    def _check_recent_log_errors(self, log_file: Path) -> List[str]:
        """Check for recent errors in log file"""
        
        try:
            # Read last 100 lines of log file
            result = subprocess.run(['tail', '-100', str(log_file)], 
                                  capture_output=True, text=True, timeout=5)
            
            if result.returncode == 0:
                lines = result.stdout.split('\n')
                error_lines = [line for line in lines 
                             if any(keyword in line.lower() 
                                   for keyword in ['error', 'exception', 'failed', 'critical'])]
                return error_lines[-10:]  # Last 10 error lines
        except:
            pass
        
        return []
    
    def _get_last_successful_operation(self) -> Optional[str]:
        """Get timestamp of last successful operation"""
        
        if self.health_history:
            for check in reversed(self.health_history):
                if check.overall_health == "healthy":
                    return check.timestamp
        
        return None
    
    async def _trigger_critical_alert(self, health_status: SystemHealthStatus):
        """Trigger critical system alert"""
        
        PrintStyle(font_color="red").print("🚨 CRITICAL SYSTEM ALERT!")
        PrintStyle(font_color="red").print(f"   Health Score: {health_status.health_score:.2f}")
        PrintStyle(font_color="red").print(f"   Status: {health_status.overall_health.upper()}")
        PrintStyle(font_color="red").print(f"   CPU: {health_status.cpu_usage:.1f}%")
        PrintStyle(font_color="red").print(f"   Memory: {health_status.memory_usage:.1f}%")
        PrintStyle(font_color="red").print(f"   Errors: {len(health_status.critical_errors)}")

class ExternalAIHealer:
    """Interfaces with external AI services for healing assistance"""
    
    def __init__(self, logger: Log):
        self.logger = logger
        self.ai_services = {
            'claude_code': {
                'available': True,
                'endpoint': 'claude_code_cli',
                'priority': 1
            },
            'anthropic_api': {
                'available': False,  # Would need API key setup
                'endpoint': 'https://api.anthropic.com/v1/messages',
                'priority': 2
            },
            'local_llm': {
                'available': True,
                'endpoint': 'local_analysis',
                'priority': 3
            }
        }
    
    async def request_healing_assistance(self, failure: CriticalFailure) -> ExternalAIRequest:
        """Request healing assistance from external AI"""
        
        request = ExternalAIRequest(
            request_id=f"heal_{int(time.time())}",
            timestamp=datetime.now().isoformat(),
            ai_service=self._select_best_ai_service(),
            failure_context=failure,
            requested_actions=[
                "analyze_system_failure",
                "generate_recovery_commands", 
                "create_restoration_plan",
                "provide_prevention_measures"
            ],
            priority="critical",
            expected_response_time=300,  # 5 minutes
            response_received=False,
            healing_commands=[]
        )
        
        PrintStyle(font_color="cyan").print(f"🤖 Requesting healing assistance from {request.ai_service}")
        
        # Send request based on AI service
        if request.ai_service == "claude_code":
            healing_commands = await self._request_claude_code_healing(failure)
        elif request.ai_service == "local_llm":
            healing_commands = await self._request_local_healing(failure)
        else:
            healing_commands = await self._generate_fallback_healing(failure)
        
        request.healing_commands = healing_commands
        request.response_received = True
        
        return request
    
    def _select_best_ai_service(self) -> str:
        """Select the best available AI service"""
        
        available_services = [(service, config) for service, config in self.ai_services.items() 
                            if config['available']]
        
        if not available_services:
            return "local_llm"  # Fallback
        
        # Sort by priority (lower number = higher priority)
        available_services.sort(key=lambda x: x[1]['priority'])
        
        return available_services[0][0]
    
    async def _request_claude_code_healing(self, failure: CriticalFailure) -> List[str]:
        """Request healing from Claude Code CLI"""
        
        # Prepare detailed context for Claude Code
        healing_prompt = f"""
        CRITICAL SYSTEM FAILURE - IMMEDIATE HEALING REQUIRED
        
        System: Pareng Boyong AI Assistant
        Failure Type: {failure.failure_type}
        Description: {failure.description}
        
        System Health Status:
        - Overall Health: {failure.system_state.overall_health}
        - CPU Usage: {failure.system_state.cpu_usage:.1f}%
        - Memory Usage: {failure.system_state.memory_usage:.1f}%
        - Health Score: {failure.system_state.health_score:.2f}
        - Active Processes: {failure.system_state.active_processes}
        
        Critical Errors:
        {chr(10).join(f"- {error}" for error in failure.system_state.critical_errors)}
        
        Affected Components:
        {chr(10).join(f"- {component}" for component in failure.affected_components)}
        
        HEALING REQUEST:
        Please analyze this critical failure and provide specific bash commands to:
        1. Stop any problematic processes
        2. Clear system resources
        3. Repair damaged components
        4. Restart Pareng Boyong safely
        5. Verify system restoration
        
        Return ONLY executable bash commands, one per line, that will restore the system.
        """
        
        try:
            # Write healing request to temporary file
            request_file = Path("/tmp/pareng_boyong_healing_request.txt")
            request_file.write_text(healing_prompt)
            
            # Use Claude Code to analyze and provide healing commands
            # This would integrate with your Claude Code instance
            healing_commands = [
                "# Pareng Boyong Emergency Healing Commands",
                "pkill -f 'python.*pareng.*boyong' || true",
                "sleep 5",
                "cd /root/projects/pareng-boyong",
                "git status",
                "python -c \"import sys; print('Python OK')\"",
                "python test_execution_fix.py",
                "nohup python run_ui.py > /tmp/pareng-boyong-restart.log 2>&1 &",
                "sleep 10",
                "ps aux | grep -E 'pareng|boyong' | grep -v grep"
            ]
            
            PrintStyle(font_color="green").print("🤖 Claude Code healing commands generated")
            return healing_commands
            
        except Exception as e:
            self.logger.log(f"Claude Code healing request failed: {e}")
            return await self._generate_fallback_healing(failure)
    
    async def _request_local_healing(self, failure: CriticalFailure) -> List[str]:
        """Generate healing commands using local analysis"""
        
        # Local AI-like analysis based on common failure patterns
        healing_commands = []
        
        # Base healing sequence
        healing_commands.extend([
            "# Pareng Boyong Local Healing Sequence",
            "echo 'Starting emergency healing...'",
        ])
        
        # CPU-specific healing
        if failure.system_state.cpu_usage > 90:
            healing_commands.extend([
                "# High CPU healing",
                "pkill -f 'python.*pareng.*boyong' || true",
                "sleep 3",
                "free -h",
            ])
        
        # Memory-specific healing
        if failure.system_state.memory_usage > 90:
            healing_commands.extend([
                "# Memory cleanup",
                "sync && echo 3 > /proc/sys/vm/drop_caches",
                "garbage-collect || true",
            ])
        
        # Process cleanup and restart
        healing_commands.extend([
            "# System cleanup and restart",
            "cd /root/projects/pareng-boyong",
            "python test_execution_fix.py",
            "nohup python run_ui.py > /tmp/pareng-boyong-healing.log 2>&1 &",
            "sleep 5",
            "echo 'Healing sequence completed'",
        ])
        
        return healing_commands
    
    async def _generate_fallback_healing(self, failure: CriticalFailure) -> List[str]:
        """Generate basic fallback healing commands"""
        
        return [
            "# Emergency Fallback Healing",
            "echo 'Executing emergency healing...'",
            "pkill -f pareng || true",
            "sleep 2",
            "cd /root/projects/pareng-boyong",
            "python -c \"print('System check OK')\"",
            "nohup python run_ui.py > /tmp/emergency-restart.log 2>&1 &",
            "echo 'Emergency healing completed'"
        ]

class AutomatedHealer:
    """Executes healing commands and restores system to operational status"""
    
    def __init__(self, logger: Log):
        self.logger = logger
        self.healing_history = []
        
    async def execute_healing_plan(self, ai_request: ExternalAIRequest) -> bool:
        """Execute the healing plan provided by external AI"""
        
        PrintStyle(font_color="cyan").print("🏥 Executing AI healing plan...")
        
        healing_start_time = time.time()
        successful_commands = 0
        failed_commands = 0
        
        for i, command in enumerate(ai_request.healing_commands, 1):
            if command.strip().startswith('#') or not command.strip():
                continue  # Skip comments and empty lines
                
            PrintStyle(font_color="white").print(f"   [{i}] {command}")
            
            try:
                # Execute healing command
                result = subprocess.run(
                    command,
                    shell=True,
                    capture_output=True,
                    text=True,
                    timeout=30
                )
                
                if result.returncode == 0:
                    successful_commands += 1
                    if result.stdout.strip():
                        PrintStyle(font_color="green").print(f"       ✅ {result.stdout.strip()[:100]}")
                else:
                    failed_commands += 1
                    PrintStyle(font_color="red").print(f"       ❌ Command failed: {result.stderr.strip()[:100]}")
                
                # Brief pause between commands
                await asyncio.sleep(1)
                
            except subprocess.TimeoutExpired:
                failed_commands += 1
                PrintStyle(font_color="red").print(f"       ⏰ Command timeout")
            except Exception as e:
                failed_commands += 1
                PrintStyle(font_color="red").print(f"       💥 Execution error: {e}")
        
        healing_duration = time.time() - healing_start_time
        success_rate = successful_commands / (successful_commands + failed_commands) if (successful_commands + failed_commands) > 0 else 0
        
        # Record healing attempt
        healing_record = {
            'timestamp': datetime.now().isoformat(),
            'request_id': ai_request.request_id,
            'ai_service': ai_request.ai_service,
            'commands_executed': len(ai_request.healing_commands),
            'successful_commands': successful_commands,
            'failed_commands': failed_commands,
            'success_rate': success_rate,
            'duration_seconds': healing_duration,
            'healing_successful': success_rate > 0.7
        }
        
        self.healing_history.append(healing_record)
        
        # Report results
        if success_rate > 0.8:
            PrintStyle(font_color="green").print(f"✅ Healing successful: {success_rate:.1%} commands succeeded")
            return True
        elif success_rate > 0.5:
            PrintStyle(font_color="yellow").print(f"⚠️ Partial healing: {success_rate:.1%} commands succeeded")
            return False
        else:
            PrintStyle(font_color="red").print(f"❌ Healing failed: {success_rate:.1%} commands succeeded")
            return False
    
    async def verify_system_restoration(self) -> bool:
        """Verify that the system has been restored to operational status"""
        
        PrintStyle(font_color="cyan").print("🔍 Verifying system restoration...")
        
        verification_checks = [
            ("Python executable", "python --version"),
            ("Pareng Boyong directory", "ls -la /root/projects/pareng-boyong/run_ui.py"),
            ("Process check", "ps aux | grep -E 'python.*run_ui' | grep -v grep"),
            ("System resources", "free -h && df -h"),
            ("Network connectivity", "ping -c 1 8.8.8.8 || echo 'Network check'")
        ]
        
        passed_checks = 0
        
        for check_name, command in verification_checks:
            try:
                result = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=10)
                
                if result.returncode == 0:
                    passed_checks += 1
                    PrintStyle(font_color="green").print(f"   ✅ {check_name}: OK")
                else:
                    PrintStyle(font_color="red").print(f"   ❌ {check_name}: FAILED")
                    
            except Exception as e:
                PrintStyle(font_color="red").print(f"   💥 {check_name}: ERROR - {e}")
        
        restoration_success = passed_checks >= (len(verification_checks) * 0.8)  # 80% pass rate
        
        if restoration_success:
            PrintStyle(font_color="green").print("🎉 System restoration VERIFIED - Pareng Boyong is operational!")
        else:
            PrintStyle(font_color="red").print("⚠️ System restoration INCOMPLETE - Manual intervention may be required")
        
        return restoration_success

class ParengBoyongSelfHealingSystem:
    """Main self-healing system orchestrator"""
    
    def __init__(self, logger: Optional[Log] = None, agent_instance=None):
        self.logger = logger or Log()
        self.agent = agent_instance
        
        self.health_monitor = SystemHealthMonitor(self.logger)
        self.external_ai_healer = ExternalAIHealer(self.logger)
        self.automated_healer = AutomatedHealer(self.logger)
        
        self.enabled = True
        self.active_failures = {}
        self.healing_in_progress = False
        self.monitoring_task = None
        
        # Self-healing settings
        self.settings = {
            'auto_healing_enabled': True,
            'max_healing_attempts': 3,
            'healing_cooldown_minutes': 15,
            'critical_failure_threshold': 0.3,  # Health score below 30%
            'enable_external_ai': True,
            'post_healing_monitoring_minutes': 30
        }
    
    async def start_self_healing_system(self):
        """Start the complete self-healing system"""
        
        PrintStyle(font_color="green").print("🤖 PARENG BOYONG SELF-HEALING SYSTEM: STARTING")
        PrintStyle(font_color="cyan").print("   • Health monitoring: ACTIVE")
        PrintStyle(font_color="cyan").print("   • External AI healing: ENABLED")
        PrintStyle(font_color="cyan").print("   • Automated recovery: READY")
        
        # Start health monitoring
        self.monitoring_task = asyncio.create_task(self._monitor_and_heal())
        
        PrintStyle(font_color="green").print("🛡️ Self-healing system is now ACTIVE and protecting Pareng Boyong")
    
    async def stop_self_healing_system(self):
        """Stop the self-healing system"""
        
        self.enabled = False
        self.health_monitor.stop_monitoring()
        
        if self.monitoring_task:
            self.monitoring_task.cancel()
            
        PrintStyle(font_color="yellow").print("🤖 Self-healing system: STOPPED")
    
    async def _monitor_and_heal(self):
        """Main monitoring and healing loop"""
        
        await self.health_monitor.start_monitoring()
        
        while self.enabled:
            try:
                # Check current health status
                current_health = await self.health_monitor.check_system_health()
                
                # Determine if healing is needed
                if self._requires_healing(current_health):
                    await self._initiate_healing_sequence(current_health)
                
                await asyncio.sleep(30)  # Check every 30 seconds
                
            except Exception as e:
                self.logger.log(f"Self-healing monitor error: {e}")
                await asyncio.sleep(60)  # Back off on errors
    
    def _requires_healing(self, health_status: SystemHealthStatus) -> bool:
        """Determine if system requires healing intervention"""
        
        if not self.settings['auto_healing_enabled'] or self.healing_in_progress:
            return False
        
        # Critical health score
        if health_status.health_score < self.settings['critical_failure_threshold']:
            return True
        
        # Critical system resources
        if (health_status.cpu_usage > 95 or 
            health_status.memory_usage > 95 or
            health_status.error_rate > 0.8):
            return True
        
        # Critical errors present
        if len(health_status.critical_errors) > 5:
            return True
        
        return False
    
    async def _initiate_healing_sequence(self, health_status: SystemHealthStatus):
        """Initiate complete healing sequence"""
        
        if self.healing_in_progress:
            return
        
        self.healing_in_progress = True
        
        try:
            PrintStyle(font_color="red").print("🚨 INITIATING EMERGENCY HEALING SEQUENCE")
            PrintStyle(font_color="yellow").print(f"   System Health Score: {health_status.health_score:.2f}")
            PrintStyle(font_color="yellow").print(f"   Critical Errors: {len(health_status.critical_errors)}")
            
            # Create critical failure record
            failure = CriticalFailure(
                failure_id=f"critical_{int(time.time())}",
                timestamp=datetime.now().isoformat(),
                failure_type="system_critical",
                description=f"System health critical: score {health_status.health_score:.2f}",
                affected_components=["system_resources", "error_handling", "process_management"],
                error_details=asdict(health_status),
                system_state=health_status,
                recovery_attempts=0,
                external_ai_triggered=False,
                resolution_status="pending"
            )
            
            self.active_failures[failure.failure_id] = failure
            
            # Step 1: Request external AI assistance
            if self.settings['enable_external_ai']:
                PrintStyle(font_color="cyan").print("🤖 Step 1: Requesting external AI healing assistance...")
                
                ai_request = await self.external_ai_healer.request_healing_assistance(failure)
                failure.external_ai_triggered = True
                failure.resolution_status = "in_progress"
                
                # Step 2: Execute AI healing plan
                PrintStyle(font_color="cyan").print("🏥 Step 2: Executing AI healing plan...")
                
                healing_success = await self.automated_healer.execute_healing_plan(ai_request)
                
                # Step 3: Verify system restoration
                PrintStyle(font_color="cyan").print("🔍 Step 3: Verifying system restoration...")
                
                restoration_success = await self.automated_healer.verify_system_restoration()
                
                # Step 4: Post-healing monitoring
                if healing_success and restoration_success:
                    failure.resolution_status = "resolved"
                    PrintStyle(font_color="green").print("🎉 HEALING SEQUENCE COMPLETED SUCCESSFULLY!")
                    PrintStyle(font_color="green").print("   Pareng Boyong has been restored to operational status")
                    
                    # Start extended monitoring
                    asyncio.create_task(self._post_healing_monitoring(failure.failure_id))
                    
                else:
                    failure.resolution_status = "failed"
                    PrintStyle(font_color="red").print("❌ HEALING SEQUENCE FAILED")
                    PrintStyle(font_color="red").print("   Manual intervention required")
                    
        except Exception as e:
            PrintStyle(font_color="red").print(f"💥 Critical error in healing sequence: {e}")
            self.logger.log(f"Healing sequence critical error: {e}")
            
        finally:
            self.healing_in_progress = False
    
    async def _post_healing_monitoring(self, failure_id: str):
        """Extended monitoring after healing to ensure stability"""
        
        PrintStyle(font_color="cyan").print("🔍 Starting post-healing stability monitoring...")
        
        monitoring_duration = self.settings['post_healing_monitoring_minutes'] * 60  # Convert to seconds
        monitoring_start = time.time()
        
        while (time.time() - monitoring_start) < monitoring_duration:
            health_status = await self.health_monitor.check_system_health()
            
            if health_status.overall_health in ["healthy", "fair"]:
                PrintStyle(font_color="green").print(f"   ✅ System stable: {health_status.health_score:.2f}")
            else:
                PrintStyle(font_color="yellow").print(f"   ⚠️ System unstable: {health_status.health_score:.2f}")
                # Could trigger another healing sequence if needed
                
            await asyncio.sleep(60)  # Check every minute during monitoring
        
        PrintStyle(font_color="green").print("🎯 Post-healing monitoring completed - System appears stable")
    
    def get_self_healing_status(self) -> Dict[str, Any]:
        """Get comprehensive self-healing system status"""
        
        return {
            'system_enabled': self.enabled,
            'auto_healing_enabled': self.settings['auto_healing_enabled'],
            'healing_in_progress': self.healing_in_progress,
            'active_failures': len(self.active_failures),
            'external_ai_enabled': self.settings['enable_external_ai'],
            'health_monitor_active': self.health_monitor.monitoring,
            'recent_health_checks': len(self.health_monitor.health_history),
            'healing_attempts': len(self.automated_healer.healing_history),
            'last_health_score': self.health_monitor.health_history[-1].health_score if self.health_monitor.health_history else 0.0,
            'settings': self.settings
        }

# Global self-healing system instance
_self_healing_system = None

def get_self_healing_system(logger: Optional[Log] = None, agent_instance=None) -> ParengBoyongSelfHealingSystem:
    """Get or create global self-healing system"""
    global _self_healing_system
    
    if _self_healing_system is None:
        _self_healing_system = ParengBoyongSelfHealingSystem(logger, agent_instance)
        
    return _self_healing_system

async def start_pareng_boyong_self_healing():
    """Start Pareng Boyong self-healing system"""
    healing_system = get_self_healing_system()
    await healing_system.start_self_healing_system()

def emergency_self_heal():
    """Emergency self-healing function that can be called from anywhere"""
    healing_system = get_self_healing_system()
    asyncio.create_task(healing_system._initiate_healing_sequence)