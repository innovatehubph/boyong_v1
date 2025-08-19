#!/usr/bin/env python3
"""
SSH Health Monitor and Network Stability Checker
Advanced monitoring for SSH connections based on Pareng Boyong recommendations
"""

import subprocess
import time
import json
import socket
import dns.resolver
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
import threading
import psutil


@dataclass
class NetworkHealth:
    """Network health metrics"""
    dns_resolution_time: float
    ping_latency: float
    packet_loss: float
    bandwidth_test: Optional[float] = None
    firewall_issues: bool = False
    timestamp: datetime = datetime.now()


@dataclass
class SystemHealth:
    """System resource health"""
    cpu_usage: float
    memory_usage: float
    disk_usage: float
    network_connections: int
    ssh_processes: int
    timestamp: datetime = datetime.now()


class SSHHealthMonitor:
    """Comprehensive SSH and network health monitoring"""
    
    def __init__(self, target_host: str, log_dir: str = "/tmp/ssh_health"):
        self.target_host = target_host
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(exist_ok=True)
        
        self.health_history: List[NetworkHealth] = []
        self.system_history: List[SystemHealth] = []
        self.monitoring = False
        self.monitor_thread: Optional[threading.Thread] = None
        
    def check_dns_resolution(self) -> Tuple[bool, float]:
        """Check DNS resolution speed and reliability"""
        try:
            start_time = time.time()
            dns.resolver.resolve(self.target_host, 'A')
            resolution_time = time.time() - start_time
            return True, resolution_time
        except Exception:
            return False, 0.0
    
    def check_ping_connectivity(self) -> Tuple[float, float]:
        """Check ping latency and packet loss"""
        try:
            result = subprocess.run(
                ['ping', '-c', '10', '-W', '5', self.target_host],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                output = result.stdout
                
                # Extract latency
                latency_line = [line for line in output.split('\n') if 'avg' in line]
                if latency_line:
                    latency = float(latency_line[0].split('/')[-2])
                else:
                    latency = 0.0
                
                # Extract packet loss
                loss_line = [line for line in output.split('\n') if 'packet loss' in line]
                if loss_line:
                    loss_percent = float(loss_line[0].split('%')[0].split()[-1])
                else:
                    loss_percent = 0.0
                
                return latency, loss_percent
            
        except Exception:
            pass
        
        return 0.0, 100.0  # Failed ping
    
    def check_port_connectivity(self, port: int = 22) -> bool:
        """Check if SSH port is accessible"""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(10)
            result = sock.connect_ex((self.target_host, port))
            sock.close()
            return result == 0
        except Exception:
            return False
    
    def check_firewall_interference(self) -> bool:
        """Detect potential firewall interference"""
        # Check multiple ports to detect filtering
        test_ports = [22, 80, 443, 53]
        accessible_ports = 0
        
        for port in test_ports:
            if self.check_port_connectivity(port):
                accessible_ports += 1
        
        # If only some ports are accessible, likely firewall interference
        return accessible_ports > 0 and accessible_ports < len(test_ports)
    
    def get_system_health(self) -> SystemHealth:
        """Get current system health metrics"""
        return SystemHealth(
            cpu_usage=psutil.cpu_percent(interval=1),
            memory_usage=psutil.virtual_memory().percent,
            disk_usage=psutil.disk_usage('/').percent,
            network_connections=len(psutil.net_connections(kind='inet')),
            ssh_processes=len([p for p in psutil.process_iter(['name']) if 'ssh' in p.info['name'].lower()])
        )
    
    def perform_health_check(self) -> NetworkHealth:
        """Perform comprehensive network health check"""
        dns_ok, dns_time = self.check_dns_resolution()
        latency, packet_loss = self.check_ping_connectivity()
        firewall_issues = self.check_firewall_interference()
        
        health = NetworkHealth(
            dns_resolution_time=dns_time if dns_ok else -1,
            ping_latency=latency,
            packet_loss=packet_loss,
            firewall_issues=firewall_issues,
            timestamp=datetime.now()
        )
        
        self.health_history.append(health)
        
        # Keep only last 100 entries
        if len(self.health_history) > 100:
            self.health_history = self.health_history[-100:]
        
        return health
    
    def start_monitoring(self, interval: int = 60):
        """Start continuous monitoring"""
        def monitor():
            self.monitoring = True
            while self.monitoring:
                try:
                    # Network health check
                    network_health = self.perform_health_check()
                    
                    # System health check
                    system_health = self.get_system_health()
                    self.system_history.append(system_health)
                    
                    if len(self.system_history) > 100:
                        self.system_history = self.system_history[-100:]
                    
                    # Log critical issues
                    self._log_issues(network_health, system_health)
                    
                    # Save current state
                    self.save_health_report()
                    
                    time.sleep(interval)
                    
                except Exception as e:
                    print(f"Monitoring error: {e}")
                    time.sleep(interval)
        
        if not self.monitor_thread or not self.monitor_thread.is_alive():
            self.monitor_thread = threading.Thread(target=monitor, daemon=True)
            self.monitor_thread.start()
            print(f"Started health monitoring for {self.target_host}")
    
    def stop_monitoring(self):
        """Stop monitoring"""
        self.monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=5)
        print("Health monitoring stopped")
    
    def _log_issues(self, network_health: NetworkHealth, system_health: SystemHealth):
        """Log critical issues"""
        issues = []
        
        # Network issues
        if network_health.dns_resolution_time < 0:
            issues.append("DNS resolution failed")
        elif network_health.dns_resolution_time > 5.0:
            issues.append(f"Slow DNS resolution: {network_health.dns_resolution_time:.2f}s")
        
        if network_health.packet_loss > 5.0:
            issues.append(f"High packet loss: {network_health.packet_loss}%")
        
        if network_health.ping_latency > 1000:
            issues.append(f"High latency: {network_health.ping_latency:.0f}ms")
        
        if network_health.firewall_issues:
            issues.append("Potential firewall interference detected")
        
        # System issues
        if system_health.cpu_usage > 90:
            issues.append(f"High CPU usage: {system_health.cpu_usage}%")
        
        if system_health.memory_usage > 90:
            issues.append(f"High memory usage: {system_health.memory_usage}%")
        
        if system_health.disk_usage > 90:
            issues.append(f"High disk usage: {system_health.disk_usage}%")
        
        # Log issues
        if issues:
            timestamp = datetime.now().isoformat()
            issue_log = self.log_dir / "health_issues.log"
            with open(issue_log, 'a') as f:
                f.write(f"{timestamp} - {self.target_host}: {'; '.join(issues)}\n")
    
    def get_health_summary(self) -> Dict:
        """Get health summary report"""
        if not self.health_history:
            return {"error": "No health data available"}
        
        recent_health = self.health_history[-10:]  # Last 10 checks
        recent_system = self.system_history[-10:] if self.system_history else []
        
        # Calculate averages
        avg_dns_time = sum(h.dns_resolution_time for h in recent_health if h.dns_resolution_time > 0) / len([h for h in recent_health if h.dns_resolution_time > 0]) if any(h.dns_resolution_time > 0 for h in recent_health) else 0
        avg_latency = sum(h.ping_latency for h in recent_health) / len(recent_health)
        avg_packet_loss = sum(h.packet_loss for h in recent_health) / len(recent_health)
        
        # System averages
        avg_cpu = sum(s.cpu_usage for s in recent_system) / len(recent_system) if recent_system else 0
        avg_memory = sum(s.memory_usage for s in recent_system) / len(recent_system) if recent_system else 0
        
        # Issues count
        firewall_issues = sum(1 for h in recent_health if h.firewall_issues)
        
        return {
            "target_host": self.target_host,
            "monitoring_active": self.monitoring,
            "last_check": self.health_history[-1].timestamp.isoformat(),
            "network_health": {
                "avg_dns_resolution_time": round(avg_dns_time, 3),
                "avg_ping_latency": round(avg_latency, 2),
                "avg_packet_loss": round(avg_packet_loss, 2),
                "firewall_issues_detected": firewall_issues,
                "ssh_port_accessible": self.check_port_connectivity(22)
            },
            "system_health": {
                "avg_cpu_usage": round(avg_cpu, 1),
                "avg_memory_usage": round(avg_memory, 1),
                "current_ssh_connections": recent_system[-1].ssh_processes if recent_system else 0
            },
            "health_score": self._calculate_health_score(recent_health, recent_system),
            "recommendations": self._get_recommendations(recent_health, recent_system)
        }
    
    def _calculate_health_score(self, network_health: List[NetworkHealth], system_health: List[SystemHealth]) -> int:
        """Calculate overall health score (0-100)"""
        score = 100
        
        if not network_health:
            return 0
        
        # Network penalties
        avg_latency = sum(h.ping_latency for h in network_health) / len(network_health)
        avg_packet_loss = sum(h.packet_loss for h in network_health) / len(network_health)
        
        if avg_latency > 100:
            score -= min(20, avg_latency / 50)
        if avg_packet_loss > 0:
            score -= min(30, avg_packet_loss * 3)
        if any(h.firewall_issues for h in network_health):
            score -= 15
        if any(h.dns_resolution_time < 0 for h in network_health):
            score -= 20
        
        # System penalties
        if system_health:
            avg_cpu = sum(s.cpu_usage for s in system_health) / len(system_health)
            avg_memory = sum(s.memory_usage for s in system_health) / len(system_health)
            
            if avg_cpu > 80:
                score -= 10
            if avg_memory > 80:
                score -= 10
        
        return max(0, int(score))
    
    def _get_recommendations(self, network_health: List[NetworkHealth], system_health: List[SystemHealth]) -> List[str]:
        """Get health improvement recommendations"""
        recommendations = []
        
        if not network_health:
            return ["Start monitoring to get recommendations"]
        
        avg_latency = sum(h.ping_latency for h in network_health) / len(network_health)
        avg_packet_loss = sum(h.packet_loss for h in network_health) / len(network_health)
        
        if avg_latency > 200:
            recommendations.append("High latency detected - check network connection quality")
        if avg_packet_loss > 2:
            recommendations.append("Packet loss detected - investigate network stability")
        if any(h.firewall_issues for h in network_health):
            recommendations.append("Firewall interference detected - check firewall rules")
        if any(h.dns_resolution_time > 2 for h in network_health):
            recommendations.append("Slow DNS resolution - consider using different DNS servers")
        if any(h.dns_resolution_time < 0 for h in network_health):
            recommendations.append("DNS resolution failures - check DNS configuration")
        
        if system_health:
            avg_cpu = sum(s.cpu_usage for s in system_health) / len(system_health)
            avg_memory = sum(s.memory_usage for s in system_health) / len(system_health)
            
            if avg_cpu > 80:
                recommendations.append("High CPU usage - consider reducing system load")
            if avg_memory > 80:
                recommendations.append("High memory usage - check for memory leaks")
        
        if not recommendations:
            recommendations.append("Connection health looks good!")
        
        return recommendations
    
    def save_health_report(self):
        """Save detailed health report"""
        report_file = self.log_dir / f"health_report_{self.target_host.replace('.', '_')}.json"
        
        report = {
            "target_host": self.target_host,
            "generated": datetime.now().isoformat(),
            "summary": self.get_health_summary(),
            "recent_network_health": [asdict(h) for h in self.health_history[-20:]],
            "recent_system_health": [asdict(s) for s in self.system_history[-20:]]
        }
        
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2, default=str)


def main():
    """Example usage"""
    monitor = SSHHealthMonitor("example.com")
    
    print("Starting SSH health monitoring...")
    monitor.start_monitoring(interval=30)  # Check every 30 seconds
    
    try:
        # Monitor for a while
        time.sleep(120)  # 2 minutes
        
        # Get health summary
        summary = monitor.get_health_summary()
        print(json.dumps(summary, indent=2))
        
    except KeyboardInterrupt:
        print("\nStopping monitoring...")
    finally:
        monitor.stop_monitoring()


if __name__ == "__main__":
    main()