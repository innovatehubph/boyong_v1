import os
import sys
import psutil
import docker
import subprocess
import json
import time
from datetime import datetime
from typing import Dict, List, Any, Optional

class SystemSelfAwareness:
    """
    Pareng Boyong Self-Awareness and Protection System
    
    This tool provides system monitoring, self-protection mechanisms,
    and awareness of actions that could affect system stability.
    """
    
    def __init__(self):
        self.system_info = self._get_system_info()
        self.critical_processes = [
            'agent-zero-dev',  # Main container
            'run_ui.py',       # UI process
            'nginx',           # Web server
            'docker',          # Container management
        ]
        self.critical_ports = [55080, 55022, 55510, 5000, 27017, 6379]
        self.safe_memory_threshold = 0.85  # 85% memory usage threshold
        self.safe_cpu_threshold = 0.90     # 90% CPU usage threshold
        
    def _get_system_info(self) -> Dict[str, Any]:
        """Get comprehensive system information"""
        return {
            'hostname': os.uname().nodename,
            'platform': sys.platform,
            'python_version': sys.version,
            'working_directory': os.getcwd(),
            'process_id': os.getpid(),
            'user': os.getenv('USER', 'unknown'),
            'home': os.getenv('HOME', '/root'),
            'pareng_boyong_root': '/root/projects/pareng-boyong',
            'container_runtime': self._detect_container_runtime()
        }
    
    def _detect_container_runtime(self) -> str:
        """Detect if running inside container"""
        if os.path.exists('/.dockerenv'):
            return 'docker'
        elif os.path.exists('/proc/1/cgroup'):
            with open('/proc/1/cgroup', 'r') as f:
                if 'docker' in f.read():
                    return 'docker'
        return 'host'
    
    def assess_action_risk(self, action: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Assess the risk level of a proposed action
        
        Returns risk assessment with recommendations
        """
        risk_level = "low"
        warnings = []
        recommendations = []
        
        # High-risk patterns
        high_risk_patterns = [
            'kill -9', 'pkill', 'killall',
            'docker stop', 'docker kill', 'docker rm',
            'systemctl stop', 'systemctl kill',
            'shutdown', 'reboot', 'halt',
            'rm -rf', 'rm -f /root/projects/pareng-boyong',
            'chmod 000', 'chown root:root',
            'iptables -F', 'ufw disable',
            'pip uninstall -y', 'npm uninstall',
            'git reset --hard', 'git clean -fd'
        ]
        
        # Medium-risk patterns  
        medium_risk_patterns = [
            'docker restart', 'systemctl restart',
            'pip install', 'npm install',
            'chmod', 'chown',
            'mv /root/projects/pareng-boyong',
            'cp -r /root/projects/pareng-boyong',
            'git pull', 'git checkout',
            'python -m pip', 'apt-get remove'
        ]
        
        action_lower = action.lower()
        
        # Check for high-risk patterns
        for pattern in high_risk_patterns:
            if pattern in action_lower:
                risk_level = "high"
                warnings.append(f"High-risk action detected: {pattern}")
                
                if 'kill' in pattern and any(proc in action_lower for proc in ['agent-zero', 'run_ui', 'nginx']):
                    warnings.append("This action could terminate critical Pareng Boyong processes")
                    recommendations.append("Consider using graceful shutdown methods instead")
                
                if 'docker' in pattern and 'agent-zero' in action_lower:
                    warnings.append("This action affects the main Agent Zero container")
                    recommendations.append("Ensure you have a recovery plan before proceeding")
                
                if 'rm' in pattern and 'pareng-boyong' in action_lower:
                    warnings.append("This action could delete critical system files")
                    recommendations.append("Create a backup before proceeding")
                
                break
        
        # Check for medium-risk patterns if not high-risk
        if risk_level != "high":
            for pattern in medium_risk_patterns:
                if pattern in action_lower:
                    risk_level = "medium"
                    warnings.append(f"Medium-risk action detected: {pattern}")
                    
                    if 'restart' in pattern:
                        recommendations.append("This may cause temporary service interruption")
                    
                    if 'install' in pattern:
                        recommendations.append("Monitor system resources during installation")
                    
                    break
        
        # Check current system state
        system_state = self.get_system_health()
        if system_state['memory_usage'] > 0.8:
            warnings.append("High memory usage detected - action may cause instability")
            risk_level = "high" if risk_level == "low" else risk_level
        
        if system_state['cpu_usage'] > 0.9:
            warnings.append("High CPU usage detected - action may cause system freeze")
            risk_level = "high" if risk_level == "low" else risk_level
        
        return {
            'risk_level': risk_level,
            'warnings': warnings,
            'recommendations': recommendations,
            'system_state': system_state,
            'safe_to_proceed': risk_level in ["low", "medium"] and len(warnings) <= 2
        }
    
    def get_system_health(self) -> Dict[str, Any]:
        """Get current system health status"""
        try:
            # System resources
            memory = psutil.virtual_memory()
            cpu_percent = psutil.cpu_percent(interval=1)
            disk = psutil.disk_usage('/')
            
            # Process information
            critical_processes_status = {}
            for proc_name in self.critical_processes:
                critical_processes_status[proc_name] = self._check_process_running(proc_name)
            
            # Port availability
            port_status = {}
            for port in self.critical_ports:
                port_status[port] = self._check_port_listening(port)
            
            # Docker containers
            container_status = self._get_container_status()
            
            # Service health checks
            service_health = self._check_service_health()
            
            return {
                'timestamp': datetime.now().isoformat(),
                'memory_usage': memory.percent / 100,
                'memory_available_gb': memory.available / (1024**3),
                'cpu_usage': cpu_percent / 100,
                'disk_usage': disk.percent / 100,
                'disk_free_gb': disk.free / (1024**3),
                'critical_processes': critical_processes_status,
                'critical_ports': port_status,
                'containers': container_status,
                'services': service_health,
                'overall_health': self._calculate_overall_health(
                    memory.percent/100, cpu_percent/100, 
                    critical_processes_status, service_health
                )
            }
        except Exception as e:
            return {
                'error': str(e),
                'timestamp': datetime.now().isoformat(),
                'overall_health': 'unknown'
            }
    
    def _check_process_running(self, process_name: str) -> bool:
        """Check if a specific process is running"""
        try:
            result = subprocess.run(
                ['pgrep', '-f', process_name], 
                capture_output=True, text=True
            )
            return result.returncode == 0
        except:
            return False
    
    def _check_port_listening(self, port: int) -> bool:
        """Check if a port is listening"""
        try:
            result = subprocess.run(
                ['netstat', '-tlnp'], 
                capture_output=True, text=True
            )
            return f':{port}' in result.stdout
        except:
            return False
    
    def _get_container_status(self) -> Dict[str, str]:
        """Get Docker container status"""
        try:
            client = docker.from_env()
            containers = client.containers.list(all=True)
            status = {}
            for container in containers:
                if any(name in container.name for name in ['agent-zero', 'pareng-boyong']):
                    status[container.name] = container.status
            return status
        except:
            return {'error': 'Docker not accessible'}
    
    def _check_service_health(self) -> Dict[str, Any]:
        """Check health of critical services"""
        services = {}
        
        # Check Agent Zero UI
        try:
            result = subprocess.run(
                ['curl', '-s', 'https://ai.innovatehub.ph/health'], 
                capture_output=True, text=True, timeout=10
            )
            services['agent_zero_ui'] = 'healthy' if result.returncode == 0 else 'unhealthy'
        except:
            services['agent_zero_ui'] = 'unknown'
        
        # Check Dashboard Backend
        try:
            result = subprocess.run(
                ['curl', '-s', 'http://localhost:5000/api/health'], 
                capture_output=True, text=True, timeout=5
            )
            services['dashboard_backend'] = 'healthy' if result.returncode == 0 else 'unhealthy'
        except:
            services['dashboard_backend'] = 'unknown'
        
        # Check SearXNG
        try:
            result = subprocess.run(
                ['curl', '-s', 'http://localhost:55510'], 
                capture_output=True, text=True, timeout=5
            )
            services['searxng'] = 'healthy' if result.returncode == 0 else 'unhealthy'
        except:
            services['searxng'] = 'unknown'
        
        return services
    
    def _calculate_overall_health(self, memory_usage: float, cpu_usage: float, 
                                 processes: Dict, services: Dict) -> str:
        """Calculate overall system health score"""
        score = 100
        
        # Resource usage penalties
        if memory_usage > 0.9:
            score -= 30
        elif memory_usage > 0.8:
            score -= 15
        elif memory_usage > 0.7:
            score -= 5
        
        if cpu_usage > 0.9:
            score -= 25
        elif cpu_usage > 0.8:
            score -= 10
        
        # Process penalties
        critical_down = sum(1 for status in processes.values() if not status)
        score -= critical_down * 20
        
        # Service penalties
        services_down = sum(1 for status in services.values() if status == 'unhealthy')
        score -= services_down * 15
        
        if score >= 90:
            return 'excellent'
        elif score >= 75:
            return 'good'
        elif score >= 60:
            return 'fair'
        elif score >= 40:
            return 'poor'
        else:
            return 'critical'
    
    def create_system_backup(self) -> Dict[str, Any]:
        """Create a quick system backup for recovery"""
        backup_info = {
            'timestamp': datetime.now().isoformat(),
            'system_state': self.get_system_health(),
            'running_processes': [],
            'docker_containers': [],
            'backup_location': '/root/pareng_boyong_backup'
        }
        
        try:
            # Get running processes
            for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                if any(keyword in ' '.join(proc.info['cmdline'] or []) 
                      for keyword in ['pareng-boyong', 'agent-zero', 'run_ui']):
                    backup_info['running_processes'].append(proc.info)
            
            # Get container info
            try:
                client = docker.from_env()
                containers = client.containers.list(all=True)
                for container in containers:
                    if any(name in container.name for name in ['agent-zero', 'pareng-boyong']):
                        backup_info['docker_containers'].append({
                            'name': container.name,
                            'status': container.status,
                            'image': container.image.tags[0] if container.image.tags else 'unknown'
                        })
            except:
                backup_info['docker_containers'] = ['docker_unavailable']
            
            # Save backup info
            os.makedirs('/root/pareng_boyong_backup', exist_ok=True)
            with open('/root/pareng_boyong_backup/system_state.json', 'w') as f:
                json.dump(backup_info, f, indent=2)
            
            return backup_info
        except Exception as e:
            return {'error': str(e), 'timestamp': datetime.now().isoformat()}
    
    def get_recovery_recommendations(self) -> List[str]:
        """Get recovery recommendations based on current state"""
        health = self.get_system_health()
        recommendations = []
        
        if health.get('overall_health') in ['poor', 'critical']:
            recommendations.append("System health is degraded - consider immediate attention")
        
        if health.get('memory_usage', 0) > 0.9:
            recommendations.append("Memory usage critical - restart memory-intensive processes")
        
        if health.get('cpu_usage', 0) > 0.9:
            recommendations.append("CPU usage critical - check for runaway processes")
        
        # Check critical services
        services = health.get('services', {})
        if services.get('agent_zero_ui') != 'healthy':
            recommendations.append("Restart Agent Zero container: docker restart agent-zero-dev")
        
        if services.get('dashboard_backend') != 'healthy':
            recommendations.append("Check dashboard backend process on port 5000")
        
        if services.get('searxng') != 'healthy':
            recommendations.append("Restart SearXNG service")
        
        if not recommendations:
            recommendations.append("System appears healthy - no immediate action needed")
        
        return recommendations


def system_self_awareness(action: str = "", operation: str = "health_check") -> str:
    """
    Pareng Boyong System Self-Awareness Tool
    
    Operations:
    - health_check: Get comprehensive system health status
    - assess_risk: Assess risk of a proposed action
    - backup: Create system backup
    - recovery: Get recovery recommendations
    """
    
    awareness = SystemSelfAwareness()
    
    try:
        if operation == "health_check":
            health = awareness.get_system_health()
            return f"""
# 🏥 **Pareng Boyong System Health Report**

## 📊 **Resource Usage**
- **Memory**: {health['memory_usage']*100:.1f}% ({health['memory_available_gb']:.1f}GB available)
- **CPU**: {health['cpu_usage']*100:.1f}%
- **Disk**: {health['disk_usage']*100:.1f}% ({health['disk_free_gb']:.1f}GB free)

## 🔧 **Critical Services**
{chr(10).join(f"- **{service}**: {'✅ Healthy' if status == 'healthy' else '❌ Unhealthy' if status == 'unhealthy' else '❓ Unknown'}" for service, status in health['services'].items())}

## 🖥️ **System Processes**
{chr(10).join(f"- **{proc}**: {'✅ Running' if status else '❌ Not Running'}" for proc, status in health['critical_processes'].items())}

## 🐳 **Docker Containers**
{chr(10).join(f"- **{name}**: {status}" for name, status in health['containers'].items()) if isinstance(health['containers'], dict) else "❌ Docker unavailable"}

## 🎯 **Overall Health**: {health['overall_health'].upper()}

**Timestamp**: {health['timestamp']}
"""
        
        elif operation == "assess_risk":
            if not action:
                return "❌ **Error**: No action specified for risk assessment"
            
            risk = awareness.assess_action_risk(action)
            
            risk_emoji = {"low": "✅", "medium": "⚠️", "high": "🚨"}
            
            result = f"""
# 🔍 **Action Risk Assessment**

## 📋 **Action**: `{action}`
## 🎯 **Risk Level**: {risk_emoji.get(risk['risk_level'], '❓')} **{risk['risk_level'].upper()}**

## ⚠️ **Warnings**:
{chr(10).join(f"- {warning}" for warning in risk['warnings']) if risk['warnings'] else "- No warnings detected"}

## 💡 **Recommendations**:
{chr(10).join(f"- {rec}" for rec in risk['recommendations']) if risk['recommendations'] else "- No specific recommendations"}

## 🚦 **Safe to Proceed**: {'✅ Yes' if risk['safe_to_proceed'] else '❌ No - Exercise Caution'}

**Current System State**: {risk['system_state']['overall_health']}
"""
            return result
        
        elif operation == "backup":
            backup = awareness.create_system_backup()
            if 'error' in backup:
                return f"❌ **Backup Failed**: {backup['error']}"
            
            return f"""
# 💾 **System Backup Created**

**Timestamp**: {backup['timestamp']}
**Location**: {backup['backup_location']}
**System Health**: {backup['system_state']['overall_health']}

## 📊 **Backup Contents**:
- System state snapshot
- Running processes: {len(backup['running_processes'])}
- Docker containers: {len(backup['docker_containers'])}

✅ **Backup completed successfully**
"""
        
        elif operation == "recovery":
            recommendations = awareness.get_recovery_recommendations()
            
            return f"""
# 🔧 **Recovery Recommendations**

{chr(10).join(f"- {rec}" for rec in recommendations)}

**Generated**: {datetime.now().isoformat()}
"""
        
        else:
            return f"❌ **Error**: Unknown operation '{operation}'. Available: health_check, assess_risk, backup, recovery"
    
    except Exception as e:
        return f"❌ **System Self-Awareness Error**: {str(e)}"