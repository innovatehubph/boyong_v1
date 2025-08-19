#!/usr/bin/env python3
"""
SSH Connection Manager Tool
Based on Pareng Boyong recommendations for handling SSH socket closure errors

Features:
- Retry logic with exponential backoff
- Socket health checks
- Persistent session management
- Automatic session recreation
- Connection failure logging
- Network stability monitoring
"""

import paramiko
import time
import socket
import logging
import json
import os
import threading
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List, Tuple
from dataclasses import dataclass, asdict
from pathlib import Path


@dataclass
class SSHConfig:
    """SSH connection configuration"""
    host: str
    port: int = 22
    username: str = "root"
    password: Optional[str] = None
    key_filename: Optional[str] = None
    timeout: int = 30
    keepalive_interval: int = 60
    max_retries: int = 5
    retry_backoff: float = 1.0
    session_timeout: int = 3600  # 1 hour


@dataclass
class ConnectionHealth:
    """Connection health status"""
    is_healthy: bool
    last_check: datetime
    error_count: int = 0
    last_error: Optional[str] = None
    uptime: timedelta = timedelta(0)


class SSHConnectionManager:
    """Robust SSH connection manager with error handling and persistence"""
    
    def __init__(self, config: SSHConfig, log_dir: str = "/tmp/ssh_logs"):
        self.config = config
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(exist_ok=True)
        
        # Connection state
        self.client: Optional[paramiko.SSHClient] = None
        self.session_start: Optional[datetime] = None
        self.health: ConnectionHealth = ConnectionHealth(
            is_healthy=False,
            last_check=datetime.now()
        )
        
        # Monitoring
        self.connection_attempts = 0
        self.successful_commands = 0
        self.failed_commands = 0
        self.connection_history: List[Dict] = []
        
        # Threading
        self.health_check_thread: Optional[threading.Thread] = None
        self.health_check_stop = threading.Event()
        
        # Setup logging
        self._setup_logging()
        
        # Configure SSH client
        self._configure_ssh_client()
    
    def _setup_logging(self):
        """Setup comprehensive logging"""
        log_file = self.log_dir / f"ssh_manager_{self.config.host}.log"
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(f"SSH_{self.config.host}")
    
    def _configure_ssh_client(self):
        """Configure SSH client with optimal settings"""
        if self.client:
            self.client.close()
        
        self.client = paramiko.SSHClient()
        self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        
        # Configure transport options for better stability
        transport_args = {
            'gss_auth': False,
            'gss_kex': False,
            'disabled_algorithms': {'pubkeys': ['rsa-sha2-256', 'rsa-sha2-512']}
        }
    
    def _health_check(self) -> bool:
        """Perform connection health check"""
        try:
            if not self.client or not self.client.get_transport():
                return False
            
            transport = self.client.get_transport()
            if not transport.is_active():
                return False
            
            # Send keepalive
            transport.send_ignore()
            
            # Test with simple command
            stdin, stdout, stderr = self.client.exec_command("echo 'health_check'", timeout=5)
            result = stdout.read().decode().strip()
            
            if result == "health_check":
                self.health.is_healthy = True
                self.health.last_check = datetime.now()
                self.health.error_count = 0
                return True
            
        except Exception as e:
            self.logger.warning(f"Health check failed: {e}")
            self.health.is_healthy = False
            self.health.error_count += 1
            self.health.last_error = str(e)
            
        return False
    
    def _start_health_monitoring(self):
        """Start background health monitoring"""
        def monitor():
            while not self.health_check_stop.wait(30):  # Check every 30 seconds
                if self.client:
                    healthy = self._health_check()
                    if not healthy and self.health.error_count > 2:
                        self.logger.warning("Connection unhealthy, attempting reconnection...")
                        self.reconnect()
        
        if self.health_check_thread and self.health_check_thread.is_alive():
            self.health_check_stop.set()
            self.health_check_thread.join()
        
        self.health_check_stop.clear()
        self.health_check_thread = threading.Thread(target=monitor, daemon=True)
        self.health_check_thread.start()
    
    def connect(self) -> bool:
        """Establish SSH connection with retry logic"""
        for attempt in range(self.config.max_retries):
            try:
                self.connection_attempts += 1
                self.logger.info(f"SSH connection attempt {attempt + 1}/{self.config.max_retries} to {self.config.host}")
                
                # Configure fresh client
                self._configure_ssh_client()
                
                # Connection parameters
                connect_kwargs = {
                    'hostname': self.config.host,
                    'port': self.config.port,
                    'username': self.config.username,
                    'timeout': self.config.timeout,
                    'allow_agent': False,
                    'look_for_keys': False
                }
                
                # Add authentication method
                if self.config.key_filename:
                    connect_kwargs['key_filename'] = self.config.key_filename
                elif self.config.password:
                    connect_kwargs['password'] = self.config.password
                
                # Attempt connection
                self.client.connect(**connect_kwargs)
                
                # Configure keepalive
                transport = self.client.get_transport()
                transport.set_keepalive(self.config.keepalive_interval)
                
                # Update state
                self.session_start = datetime.now()
                self.health.is_healthy = True
                self.health.last_check = datetime.now()
                self.health.error_count = 0
                
                # Log success
                self.logger.info(f"SSH connection established to {self.config.host}")
                self.connection_history.append({
                    'timestamp': datetime.now().isoformat(),
                    'action': 'connect',
                    'success': True,
                    'attempt': attempt + 1
                })
                
                # Start health monitoring
                self._start_health_monitoring()
                
                return True
                
            except (paramiko.AuthenticationException, 
                   paramiko.SSHException, 
                   socket.error,
                   socket.timeout) as e:
                
                self.logger.error(f"Connection attempt {attempt + 1} failed: {e}")
                self.connection_history.append({
                    'timestamp': datetime.now().isoformat(),
                    'action': 'connect',
                    'success': False,
                    'attempt': attempt + 1,
                    'error': str(e)
                })
                
                if attempt < self.config.max_retries - 1:
                    backoff_time = self.config.retry_backoff * (2 ** attempt)
                    self.logger.info(f"Retrying in {backoff_time:.1f} seconds...")
                    time.sleep(backoff_time)
                
            except Exception as e:
                self.logger.error(f"Unexpected error during connection: {e}")
                break
        
        self.logger.error(f"Failed to establish SSH connection after {self.config.max_retries} attempts")
        return False
    
    def reconnect(self) -> bool:
        """Reconnect SSH session"""
        self.logger.info("Reconnecting SSH session...")
        self.disconnect()
        return self.connect()
    
    def disconnect(self):
        """Clean disconnect"""
        self.health_check_stop.set()
        if self.health_check_thread:
            self.health_check_thread.join(timeout=5)
        
        if self.client:
            try:
                self.client.close()
            except:
                pass
            self.client = None
        
        self.session_start = None
        self.health.is_healthy = False
        self.logger.info("SSH connection closed")
    
    def execute_command(self, command: str, timeout: int = 30) -> Tuple[int, str, str]:
        """Execute command with robust error handling"""
        if not self.is_session_healthy():
            if not self.reconnect():
                raise ConnectionError("Unable to establish SSH connection")
        
        for attempt in range(3):  # Retry command execution
            try:
                self.logger.debug(f"Executing command: {command}")
                
                stdin, stdout, stderr = self.client.exec_command(
                    command, 
                    timeout=timeout,
                    get_pty=True
                )
                
                # Read output
                stdout_data = stdout.read().decode('utf-8', errors='ignore')
                stderr_data = stderr.read().decode('utf-8', errors='ignore')
                exit_code = stdout.channel.recv_exit_status()
                
                self.successful_commands += 1
                self.logger.debug(f"Command executed successfully (exit code: {exit_code})")
                
                return exit_code, stdout_data, stderr_data
                
            except (paramiko.SSHException, socket.error) as e:
                self.failed_commands += 1
                self.logger.warning(f"Command execution attempt {attempt + 1} failed: {e}")
                
                if attempt < 2:  # Retry
                    if not self.reconnect():
                        break
                else:
                    raise
                    
            except Exception as e:
                self.failed_commands += 1
                self.logger.error(f"Unexpected error executing command: {e}")
                raise
        
        raise ConnectionError("Failed to execute command after retries")
    
    def is_session_healthy(self) -> bool:
        """Check if current session is healthy"""
        if not self.client:
            return False
        
        # Check if session expired
        if self.session_start:
            session_age = datetime.now() - self.session_start
            if session_age.total_seconds() > self.config.session_timeout:
                self.logger.info("Session expired, needs reconnection")
                return False
        
        # Quick health check
        return self._health_check()
    
    def get_stats(self) -> Dict[str, Any]:
        """Get connection statistics"""
        uptime = timedelta(0)
        if self.session_start:
            uptime = datetime.now() - self.session_start
        
        return {
            'host': self.config.host,
            'connected': self.client is not None and self.health.is_healthy,
            'session_uptime': str(uptime),
            'connection_attempts': self.connection_attempts,
            'successful_commands': self.successful_commands,
            'failed_commands': self.failed_commands,
            'health': asdict(self.health),
            'last_check': self.health.last_check.isoformat(),
            'connection_history': self.connection_history[-10:]  # Last 10 events
        }
    
    def save_stats(self):
        """Save statistics to file"""
        stats_file = self.log_dir / f"ssh_stats_{self.config.host}.json"
        with open(stats_file, 'w') as f:
            json.dump(self.get_stats(), f, indent=2, default=str)
    
    def __enter__(self):
        """Context manager entry"""
        if not self.connect():
            raise ConnectionError("Failed to establish SSH connection")
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.save_stats()
        self.disconnect()


def configure_system_ssh():
    """Configure system SSH settings for better stability"""
    ssh_config_additions = """
# SSH stability improvements
ServerAliveInterval 60
ServerAliveCountMax 3
TCPKeepAlive yes
ConnectTimeout 30
"""
    
    config_file = Path.home() / '.ssh' / 'config'
    config_file.parent.mkdir(exist_ok=True)
    
    # Read existing config
    existing_config = ""
    if config_file.exists():
        existing_config = config_file.read_text()
    
    # Add new settings if not present
    if "ServerAliveInterval" not in existing_config:
        with open(config_file, 'a') as f:
            f.write('\n' + ssh_config_additions)
        print("SSH client configuration updated")


def main():
    """Example usage and testing"""
    # Configure system SSH
    configure_system_ssh()
    
    # Example configuration
    config = SSHConfig(
        host="example.com",
        username="root",
        password="your_password",  # or use key_filename="/path/to/key"
        max_retries=5,
        keepalive_interval=60
    )
    
    # Test the SSH manager
    try:
        with SSHConnectionManager(config) as ssh:
            # Test commands
            exit_code, stdout, stderr = ssh.execute_command("uptime")
            print(f"Uptime: {stdout.strip()}")
            
            exit_code, stdout, stderr = ssh.execute_command("df -h")
            print(f"Disk usage:\n{stdout}")
            
            # Show statistics
            stats = ssh.get_stats()
            print(f"Connection stats: {json.dumps(stats, indent=2)}")
            
    except Exception as e:
        print(f"SSH operation failed: {e}")


if __name__ == "__main__":
    main()