#!/usr/bin/env python3
"""
SSH Diagnostic and Logging Tool
Comprehensive logging, monitoring, and diagnostic capabilities
Based on Pareng Boyong recommendations for SSH troubleshooting
"""

import logging
import json
import time
import os
import subprocess
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
import threading

from ssh_connection_manager import SSHConnectionManager, SSHConfig
from ssh_health_monitor import SSHHealthMonitor
from ssh_session_pool import SSHSessionPool


@dataclass
class DiagnosticResult:
    """Diagnostic test result"""
    test_name: str
    status: str  # 'pass', 'fail', 'warning'
    message: str
    details: Dict[str, Any]
    timestamp: datetime = datetime.now()


class SSHDiagnosticTool:
    """Comprehensive SSH diagnostic and logging tool"""
    
    def __init__(self, config: SSHConfig, log_dir: str = "/tmp/ssh_diagnostics"):
        self.config = config
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(exist_ok=True)
        
        # Setup comprehensive logging
        self._setup_logging()
        
        # Diagnostic components
        self.health_monitor = SSHHealthMonitor(config.host, str(self.log_dir))
        self.session_pool = SSHSessionPool(config, pool_size=2, log_dir=str(self.log_dir))
        
        # Test results
        self.diagnostic_results: List[DiagnosticResult] = []
        
        # Monitoring
        self.monitoring_active = False
        self.monitor_thread: Optional[threading.Thread] = None
        self.monitor_stop = threading.Event()
    
    def _setup_logging(self):
        """Setup comprehensive logging system"""
        # Main diagnostic log
        log_file = self.log_dir / f"ssh_diagnostics_{self.config.host}.log"
        
        # Configure root logger
        logging.basicConfig(
            level=logging.DEBUG,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler()
            ]
        )
        
        self.logger = logging.getLogger(f"SSH_Diagnostics_{self.config.host}")
        
        # Create specialized loggers
        self.connection_logger = logging.getLogger("SSH_Connections")
        self.performance_logger = logging.getLogger("SSH_Performance")
        self.error_logger = logging.getLogger("SSH_Errors")
        
        # Connection events log
        connection_handler = logging.FileHandler(self.log_dir / "connection_events.log")
        connection_handler.setFormatter(logging.Formatter('%(asctime)s - %(message)s'))
        self.connection_logger.addHandler(connection_handler)
        
        # Performance log
        performance_handler = logging.FileHandler(self.log_dir / "performance.log")
        performance_handler.setFormatter(logging.Formatter('%(asctime)s - %(message)s'))
        self.performance_logger.addHandler(performance_handler)
        
        # Error log
        error_handler = logging.FileHandler(self.log_dir / "errors.log")
        error_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
        self.error_logger.addHandler(error_handler)
        
        self.logger.info(f"SSH diagnostics initialized for {self.config.host}")
    
    def run_comprehensive_diagnostics(self) -> List[DiagnosticResult]:
        """Run comprehensive SSH diagnostics"""
        self.logger.info("Starting comprehensive SSH diagnostics")
        
        tests = [
            self._test_basic_connectivity,
            self._test_ssh_authentication,
            self._test_command_execution,
            self._test_session_persistence,
            self._test_network_stability,
            self._test_system_resources,
            self._test_ssh_configuration,
            self._test_performance_metrics,
            self._test_concurrent_connections,
            self._test_large_data_transfer,
            self._test_connection_recovery
        ]
        
        results = []
        for test in tests:
            try:
                result = test()
                results.append(result)
                self.diagnostic_results.append(result)
                
                if result.status == 'fail':
                    self.error_logger.error(f"Test failed: {result.test_name} - {result.message}")
                elif result.status == 'warning':
                    self.logger.warning(f"Test warning: {result.test_name} - {result.message}")
                else:
                    self.logger.info(f"Test passed: {result.test_name}")
                    
            except Exception as e:
                error_result = DiagnosticResult(
                    test_name=test.__name__,
                    status='fail',
                    message=f"Test execution failed: {str(e)}",
                    details={'exception': str(e)}
                )
                results.append(error_result)
                self.error_logger.error(f"Test execution error: {test.__name__} - {e}")
        
        self._generate_diagnostic_report(results)
        return results
    
    def _test_basic_connectivity(self) -> DiagnosticResult:
        """Test basic network connectivity"""
        start_time = time.time()
        
        try:
            # Test ping
            ping_result = subprocess.run(
                ['ping', '-c', '3', '-W', '5', self.config.host],
                capture_output=True,
                text=True,
                timeout=20
            )
            
            if ping_result.returncode == 0:
                # Extract latency
                output = ping_result.stdout
                if 'avg' in output:
                    latency = float(output.split('/')[-2])
                else:
                    latency = 0
                
                end_time = time.time()
                
                status = 'pass' if latency < 100 else 'warning'
                message = f"Connectivity OK, average latency: {latency}ms"
                
                return DiagnosticResult(
                    test_name="Basic Connectivity",
                    status=status,
                    message=message,
                    details={
                        'latency_ms': latency,
                        'test_duration': round(end_time - start_time, 2),
                        'ping_output': output
                    }
                )
            else:
                return DiagnosticResult(
                    test_name="Basic Connectivity",
                    status='fail',
                    message="Ping failed - host unreachable",
                    details={'ping_error': ping_result.stderr}
                )
                
        except Exception as e:
            return DiagnosticResult(
                test_name="Basic Connectivity",
                status='fail',
                message=f"Connectivity test failed: {str(e)}",
                details={'exception': str(e)}
            )
    
    def _test_ssh_authentication(self) -> DiagnosticResult:
        """Test SSH authentication"""
        start_time = time.time()
        
        try:
            ssh_client = SSHConnectionManager(self.config, str(self.log_dir))
            
            if ssh_client.connect():
                end_time = time.time()
                connect_time = round(end_time - start_time, 2)
                
                ssh_client.disconnect()
                
                self.connection_logger.info(f"Authentication successful in {connect_time}s")
                
                return DiagnosticResult(
                    test_name="SSH Authentication",
                    status='pass',
                    message=f"Authentication successful in {connect_time}s",
                    details={
                        'connection_time': connect_time,
                        'auth_method': 'password' if self.config.password else 'key'
                    }
                )
            else:
                return DiagnosticResult(
                    test_name="SSH Authentication",
                    status='fail',
                    message="SSH authentication failed",
                    details={'connection_attempts': ssh_client.connection_attempts}
                )
                
        except Exception as e:
            self.error_logger.error(f"Authentication test error: {e}")
            return DiagnosticResult(
                test_name="SSH Authentication",
                status='fail',
                message=f"Authentication test failed: {str(e)}",
                details={'exception': str(e)}
            )
    
    def _test_command_execution(self) -> DiagnosticResult:
        """Test command execution reliability"""
        commands = [
            "echo 'test'",
            "date",
            "uptime",
            "uname -a",
            "pwd"
        ]
        
        successful = 0
        total_time = 0
        errors = []
        
        try:
            with SSHConnectionManager(self.config, str(self.log_dir)) as ssh:
                for cmd in commands:
                    try:
                        start_time = time.time()
                        exit_code, stdout, stderr = ssh.execute_command(cmd, timeout=10)
                        end_time = time.time()
                        
                        cmd_time = end_time - start_time
                        total_time += cmd_time
                        
                        if exit_code == 0:
                            successful += 1
                            self.performance_logger.info(f"Command '{cmd}' executed in {cmd_time:.3f}s")
                        else:
                            errors.append(f"Command '{cmd}' failed with exit code {exit_code}")
                            
                    except Exception as e:
                        errors.append(f"Command '{cmd}' exception: {str(e)}")
            
            success_rate = (successful / len(commands)) * 100
            avg_time = total_time / len(commands)
            
            if success_rate == 100:
                status = 'pass'
                message = f"All commands executed successfully, avg time: {avg_time:.3f}s"
            elif success_rate >= 80:
                status = 'warning'
                message = f"Most commands successful ({success_rate}%), avg time: {avg_time:.3f}s"
            else:
                status = 'fail'
                message = f"Command execution unreliable ({success_rate}% success)"
            
            return DiagnosticResult(
                test_name="Command Execution",
                status=status,
                message=message,
                details={
                    'success_rate': success_rate,
                    'avg_execution_time': avg_time,
                    'total_commands': len(commands),
                    'successful_commands': successful,
                    'errors': errors
                }
            )
            
        except Exception as e:
            return DiagnosticResult(
                test_name="Command Execution",
                status='fail',
                message=f"Command execution test failed: {str(e)}",
                details={'exception': str(e)}
            )
    
    def _test_session_persistence(self) -> DiagnosticResult:
        """Test session persistence and reconnection"""
        try:
            ssh_client = SSHConnectionManager(self.config, str(self.log_dir))
            
            if not ssh_client.connect():
                return DiagnosticResult(
                    test_name="Session Persistence",
                    status='fail',
                    message="Initial connection failed",
                    details={}
                )
            
            # Execute commands over time to test persistence
            persistence_results = []
            for i in range(5):
                try:
                    start_time = time.time()
                    exit_code, stdout, stderr = ssh_client.execute_command(f"echo 'persistence test {i}'")
                    end_time = time.time()
                    
                    persistence_results.append({
                        'iteration': i,
                        'success': exit_code == 0,
                        'execution_time': end_time - start_time,
                        'session_healthy': ssh_client.is_session_healthy()
                    })
                    
                    time.sleep(2)  # Wait between commands
                    
                except Exception as e:
                    persistence_results.append({
                        'iteration': i,
                        'success': False,
                        'error': str(e)
                    })
            
            ssh_client.disconnect()
            
            successful_iterations = sum(1 for r in persistence_results if r.get('success', False))
            success_rate = (successful_iterations / len(persistence_results)) * 100
            
            if success_rate == 100:
                status = 'pass'
                message = "Session remained persistent throughout test"
            elif success_rate >= 80:
                status = 'warning'
                message = f"Session mostly persistent ({success_rate}% success)"
            else:
                status = 'fail'
                message = f"Session persistence issues ({success_rate}% success)"
            
            return DiagnosticResult(
                test_name="Session Persistence",
                status=status,
                message=message,
                details={
                    'success_rate': success_rate,
                    'iterations': persistence_results
                }
            )
            
        except Exception as e:
            return DiagnosticResult(
                test_name="Session Persistence",
                status='fail',
                message=f"Session persistence test failed: {str(e)}",
                details={'exception': str(e)}
            )
    
    def _test_network_stability(self) -> DiagnosticResult:
        """Test network stability"""
        try:
            # Use health monitor for network tests
            health_results = []
            for i in range(3):
                health = self.health_monitor.perform_health_check()
                health_results.append(health)
                time.sleep(5)
            
            # Analyze results
            avg_latency = sum(h.ping_latency for h in health_results) / len(health_results)
            avg_packet_loss = sum(h.packet_loss for h in health_results) / len(health_results)
            dns_failures = sum(1 for h in health_results if h.dns_resolution_time < 0)
            firewall_issues = sum(1 for h in health_results if h.firewall_issues)
            
            issues = []
            if avg_latency > 200:
                issues.append(f"High latency: {avg_latency:.1f}ms")
            if avg_packet_loss > 2:
                issues.append(f"Packet loss: {avg_packet_loss:.1f}%")
            if dns_failures > 0:
                issues.append(f"DNS failures: {dns_failures}")
            if firewall_issues > 0:
                issues.append("Firewall interference detected")
            
            if not issues:
                status = 'pass'
                message = "Network stability is good"
            elif len(issues) <= 1:
                status = 'warning'
                message = f"Minor network issues: {', '.join(issues)}"
            else:
                status = 'fail'
                message = f"Network stability problems: {', '.join(issues)}"
            
            return DiagnosticResult(
                test_name="Network Stability",
                status=status,
                message=message,
                details={
                    'avg_latency': avg_latency,
                    'avg_packet_loss': avg_packet_loss,
                    'dns_failures': dns_failures,
                    'firewall_issues': firewall_issues,
                    'health_checks': [asdict(h) for h in health_results]
                }
            )
            
        except Exception as e:
            return DiagnosticResult(
                test_name="Network Stability",
                status='fail',
                message=f"Network stability test failed: {str(e)}",
                details={'exception': str(e)}
            )
    
    def _test_system_resources(self) -> DiagnosticResult:
        """Test system resource availability"""
        try:
            system_health = self.health_monitor.get_system_health()
            
            issues = []
            if system_health.cpu_usage > 90:
                issues.append(f"High CPU usage: {system_health.cpu_usage}%")
            if system_health.memory_usage > 90:
                issues.append(f"High memory usage: {system_health.memory_usage}%")
            if system_health.disk_usage > 90:
                issues.append(f"High disk usage: {system_health.disk_usage}%")
            
            if not issues:
                status = 'pass'
                message = "System resources are healthy"
            elif len(issues) <= 1:
                status = 'warning'
                message = f"Resource concerns: {', '.join(issues)}"
            else:
                status = 'fail'
                message = f"Resource problems: {', '.join(issues)}"
            
            return DiagnosticResult(
                test_name="System Resources",
                status=status,
                message=message,
                details=asdict(system_health)
            )
            
        except Exception as e:
            return DiagnosticResult(
                test_name="System Resources",
                status='fail',
                message=f"System resource test failed: {str(e)}",
                details={'exception': str(e)}
            )
    
    def _test_ssh_configuration(self) -> DiagnosticResult:
        """Test SSH configuration optimizations"""
        try:
            config_issues = []
            config_file = Path.home() / '.ssh' / 'config'
            
            if config_file.exists():
                config_content = config_file.read_text()
                
                # Check for recommended settings
                recommended_settings = {
                    'ServerAliveInterval': '60',
                    'ServerAliveCountMax': '3',
                    'TCPKeepAlive': 'yes',
                    'ConnectTimeout': '30'
                }
                
                for setting, value in recommended_settings.items():
                    if setting not in config_content:
                        config_issues.append(f"Missing {setting}")
                
            else:
                config_issues.append("SSH config file does not exist")
            
            if not config_issues:
                status = 'pass'
                message = "SSH configuration is optimized"
            else:
                status = 'warning'
                message = f"SSH configuration could be improved: {', '.join(config_issues)}"
            
            return DiagnosticResult(
                test_name="SSH Configuration",
                status=status,
                message=message,
                details={
                    'config_file_exists': config_file.exists(),
                    'issues': config_issues
                }
            )
            
        except Exception as e:
            return DiagnosticResult(
                test_name="SSH Configuration",
                status='fail',
                message=f"SSH configuration test failed: {str(e)}",
                details={'exception': str(e)}
            )
    
    def _test_performance_metrics(self) -> DiagnosticResult:
        """Test SSH performance metrics"""
        try:
            # Test connection time
            start_time = time.time()
            ssh_client = SSHConnectionManager(self.config, str(self.log_dir))
            
            if ssh_client.connect():
                connect_time = time.time() - start_time
                
                # Test command execution speed
                cmd_times = []
                for i in range(5):
                    cmd_start = time.time()
                    ssh_client.execute_command("echo 'performance test'")
                    cmd_time = time.time() - cmd_start
                    cmd_times.append(cmd_time)
                
                ssh_client.disconnect()
                
                avg_cmd_time = sum(cmd_times) / len(cmd_times)
                
                # Evaluate performance
                performance_issues = []
                if connect_time > 5:
                    performance_issues.append(f"Slow connection: {connect_time:.2f}s")
                if avg_cmd_time > 1:
                    performance_issues.append(f"Slow commands: {avg_cmd_time:.3f}s avg")
                
                if not performance_issues:
                    status = 'pass'
                    message = f"Good performance: connect {connect_time:.2f}s, commands {avg_cmd_time:.3f}s avg"
                else:
                    status = 'warning'
                    message = f"Performance issues: {', '.join(performance_issues)}"
                
                return DiagnosticResult(
                    test_name="Performance Metrics",
                    status=status,
                    message=message,
                    details={
                        'connection_time': connect_time,
                        'avg_command_time': avg_cmd_time,
                        'command_times': cmd_times
                    }
                )
            else:
                return DiagnosticResult(
                    test_name="Performance Metrics",
                    status='fail',
                    message="Could not establish connection for performance test",
                    details={}
                )
                
        except Exception as e:
            return DiagnosticResult(
                test_name="Performance Metrics",
                status='fail',
                message=f"Performance test failed: {str(e)}",
                details={'exception': str(e)}
            )
    
    def _test_concurrent_connections(self) -> DiagnosticResult:
        """Test concurrent connection handling"""
        try:
            self.session_pool.start_pool()
            
            # Test concurrent execution
            import concurrent.futures
            
            def execute_test_command(i):
                try:
                    exit_code, stdout, stderr = self.session_pool.execute_command(f"echo 'concurrent test {i}'")
                    return i, exit_code == 0, time.time()
                except Exception as e:
                    return i, False, str(e)
            
            # Execute 10 concurrent commands
            with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
                futures = [executor.submit(execute_test_command, i) for i in range(10)]
                results = [future.result() for future in concurrent.futures.as_completed(futures)]
            
            self.session_pool.stop_pool()
            
            successful = sum(1 for _, success, _ in results if success)
            success_rate = (successful / len(results)) * 100
            
            if success_rate == 100:
                status = 'pass'
                message = f"All concurrent connections successful ({successful}/{len(results)})"
            elif success_rate >= 80:
                status = 'warning'
                message = f"Most concurrent connections successful ({successful}/{len(results)})"
            else:
                status = 'fail'
                message = f"Concurrent connection issues ({successful}/{len(results)} successful)"
            
            return DiagnosticResult(
                test_name="Concurrent Connections",
                status=status,
                message=message,
                details={
                    'total_connections': len(results),
                    'successful_connections': successful,
                    'success_rate': success_rate,
                    'results': results
                }
            )
            
        except Exception as e:
            return DiagnosticResult(
                test_name="Concurrent Connections",
                status='fail',
                message=f"Concurrent connection test failed: {str(e)}",
                details={'exception': str(e)}
            )
    
    def _test_large_data_transfer(self) -> DiagnosticResult:
        """Test large data transfer capability"""
        try:
            with SSHConnectionManager(self.config, str(self.log_dir)) as ssh:
                # Create test data
                test_data = "x" * 10000  # 10KB of data
                
                start_time = time.time()
                exit_code, stdout, stderr = ssh.execute_command(f"echo '{test_data}' | wc -c")
                end_time = time.time()
                
                transfer_time = end_time - start_time
                
                if exit_code == 0 and "10001" in stdout:  # 10000 chars + newline
                    if transfer_time < 5:
                        status = 'pass'
                        message = f"Large data transfer successful in {transfer_time:.2f}s"
                    else:
                        status = 'warning'
                        message = f"Large data transfer slow: {transfer_time:.2f}s"
                else:
                    status = 'fail'
                    message = "Large data transfer failed"
                
                return DiagnosticResult(
                    test_name="Large Data Transfer",
                    status=status,
                    message=message,
                    details={
                        'data_size': len(test_data),
                        'transfer_time': transfer_time,
                        'exit_code': exit_code
                    }
                )
                
        except Exception as e:
            return DiagnosticResult(
                test_name="Large Data Transfer",
                status='fail',
                message=f"Large data transfer test failed: {str(e)}",
                details={'exception': str(e)}
            )
    
    def _test_connection_recovery(self) -> DiagnosticResult:
        """Test connection recovery after failure"""
        try:
            ssh_client = SSHConnectionManager(self.config, str(self.log_dir))
            
            # Initial connection
            if not ssh_client.connect():
                return DiagnosticResult(
                    test_name="Connection Recovery",
                    status='fail',
                    message="Initial connection failed",
                    details={}
                )
            
            # Simulate connection loss by closing client
            ssh_client.disconnect()
            
            # Test recovery
            recovery_start = time.time()
            recovery_success = ssh_client.reconnect()
            recovery_time = time.time() - recovery_start
            
            ssh_client.disconnect()
            
            if recovery_success:
                if recovery_time < 10:
                    status = 'pass'
                    message = f"Connection recovery successful in {recovery_time:.2f}s"
                else:
                    status = 'warning'
                    message = f"Connection recovery slow: {recovery_time:.2f}s"
            else:
                status = 'fail'
                message = "Connection recovery failed"
            
            return DiagnosticResult(
                test_name="Connection Recovery",
                status=status,
                message=message,
                details={
                    'recovery_time': recovery_time,
                    'recovery_successful': recovery_success
                }
            )
            
        except Exception as e:
            return DiagnosticResult(
                test_name="Connection Recovery",
                status='fail',
                message=f"Connection recovery test failed: {str(e)}",
                details={'exception': str(e)}
            )
    
    def _generate_diagnostic_report(self, results: List[DiagnosticResult]):
        """Generate comprehensive diagnostic report"""
        report_file = self.log_dir / f"diagnostic_report_{self.config.host}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        # Summary statistics
        total_tests = len(results)
        passed_tests = sum(1 for r in results if r.status == 'pass')
        warning_tests = sum(1 for r in results if r.status == 'warning')
        failed_tests = sum(1 for r in results if r.status == 'fail')
        
        summary = {
            'host': self.config.host,
            'generated': datetime.now().isoformat(),
            'summary': {
                'total_tests': total_tests,
                'passed': passed_tests,
                'warnings': warning_tests,
                'failed': failed_tests,
                'success_rate': round((passed_tests / total_tests) * 100, 2) if total_tests > 0 else 0
            },
            'test_results': [asdict(r) for r in results],
            'recommendations': self._generate_recommendations(results)
        }
        
        with open(report_file, 'w') as f:
            json.dump(summary, f, indent=2, default=str)
        
        self.logger.info(f"Diagnostic report saved to {report_file}")
        return summary
    
    def _generate_recommendations(self, results: List[DiagnosticResult]) -> List[str]:
        """Generate recommendations based on test results"""
        recommendations = []
        
        failed_tests = [r for r in results if r.status == 'fail']
        warning_tests = [r for r in results if r.status == 'warning']
        
        if any('Connectivity' in r.test_name for r in failed_tests):
            recommendations.append("Check network connectivity and firewall settings")
        
        if any('Authentication' in r.test_name for r in failed_tests):
            recommendations.append("Verify SSH credentials and authentication method")
        
        if any('Performance' in r.test_name for r in warning_tests):
            recommendations.append("Consider optimizing network connection or SSH configuration")
        
        if any('Configuration' in r.test_name for r in warning_tests):
            recommendations.append("Update SSH client configuration with recommended settings")
        
        if any('Session Persistence' in r.test_name for r in failed_tests):
            recommendations.append("Investigate session timeout and keepalive settings")
        
        if any('Network Stability' in r.test_name for r in warning_tests):
            recommendations.append("Monitor network stability and consider backup connections")
        
        if not recommendations:
            recommendations.append("SSH configuration appears to be working well!")
        
        return recommendations
    
    def start_continuous_monitoring(self, interval: int = 300):
        """Start continuous monitoring and logging"""
        if self.monitoring_active:
            return
        
        self.monitoring_active = True
        self.monitor_stop.clear()
        
        def monitor():
            while not self.monitor_stop.wait(interval):
                try:
                    self.logger.info("Running scheduled diagnostics...")
                    results = self.run_comprehensive_diagnostics()
                    
                    failed_count = sum(1 for r in results if r.status == 'fail')
                    if failed_count > 0:
                        self.error_logger.error(f"Scheduled diagnostics found {failed_count} failures")
                    
                except Exception as e:
                    self.error_logger.error(f"Scheduled diagnostics error: {e}")
        
        self.monitor_thread = threading.Thread(target=monitor, daemon=True)
        self.monitor_thread.start()
        self.logger.info(f"Started continuous monitoring (interval: {interval}s)")
    
    def stop_continuous_monitoring(self):
        """Stop continuous monitoring"""
        if not self.monitoring_active:
            return
        
        self.monitoring_active = False
        self.monitor_stop.set()
        
        if self.monitor_thread:
            self.monitor_thread.join(timeout=10)
        
        self.logger.info("Stopped continuous monitoring")


def main():
    """Example usage"""
    config = SSHConfig(
        host="example.com",
        username="root",
        password="your_password"
    )
    
    diagnostic_tool = SSHDiagnosticTool(config)
    
    try:
        # Run comprehensive diagnostics
        results = diagnostic_tool.run_comprehensive_diagnostics()
        
        # Print summary
        passed = sum(1 for r in results if r.status == 'pass')
        warnings = sum(1 for r in results if r.status == 'warning')
        failed = sum(1 for r in results if r.status == 'fail')
        
        print(f"\nDiagnostic Results:")
        print(f"Passed: {passed}")
        print(f"Warnings: {warnings}")
        print(f"Failed: {failed}")
        
        # Show failed tests
        failed_tests = [r for r in results if r.status == 'fail']
        if failed_tests:
            print(f"\nFailed Tests:")
            for test in failed_tests:
                print(f"- {test.test_name}: {test.message}")
        
    except KeyboardInterrupt:
        print("\nDiagnostics interrupted")


if __name__ == "__main__":
    main()