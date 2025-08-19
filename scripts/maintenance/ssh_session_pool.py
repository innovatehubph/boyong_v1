#!/usr/bin/env python3
"""
SSH Session Pool Manager
Persistent SSH session management with automatic recreation and load balancing
Based on Pareng Boyong recommendations for robust SSH handling
"""

import threading
import time
import queue
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
import json
from pathlib import Path

from ssh_connection_manager import SSHConnectionManager, SSHConfig


@dataclass
class SessionStats:
    """Session usage statistics"""
    created_at: datetime
    last_used: datetime
    command_count: int = 0
    success_count: int = 0
    error_count: int = 0
    total_uptime: timedelta = timedelta(0)


class SSHSessionPool:
    """Manages a pool of persistent SSH sessions with automatic recreation"""
    
    def __init__(self, 
                 config: SSHConfig, 
                 pool_size: int = 3,
                 max_session_age: int = 3600,
                 max_idle_time: int = 600,
                 log_dir: str = "/tmp/ssh_pool"):
        
        self.config = config
        self.pool_size = pool_size
        self.max_session_age = max_session_age
        self.max_idle_time = max_idle_time
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(exist_ok=True)
        
        # Session management
        self.sessions: Dict[str, SSHConnectionManager] = {}
        self.session_stats: Dict[str, SessionStats] = {}
        self.available_sessions = queue.Queue()
        self.session_lock = threading.RLock()
        
        # Pool management
        self.pool_active = False
        self.maintenance_thread: Optional[threading.Thread] = None
        self.maintenance_stop = threading.Event()
        
        # Statistics
        self.total_requests = 0
        self.pool_hits = 0
        self.pool_misses = 0
        
    def start_pool(self):
        """Start the session pool"""
        with self.session_lock:
            if self.pool_active:
                return
            
            self.pool_active = True
            
            # Create initial sessions
            self._create_initial_sessions()
            
            # Start maintenance thread
            self.maintenance_stop.clear()
            self.maintenance_thread = threading.Thread(
                target=self._maintenance_worker, 
                daemon=True
            )
            self.maintenance_thread.start()
            
            print(f"SSH session pool started with {self.pool_size} sessions for {self.config.host}")
    
    def stop_pool(self):
        """Stop the session pool and close all sessions"""
        with self.session_lock:
            if not self.pool_active:
                return
            
            self.pool_active = False
            
            # Stop maintenance thread
            self.maintenance_stop.set()
            if self.maintenance_thread:
                self.maintenance_thread.join(timeout=10)
            
            # Close all sessions
            for session_id, session in self.sessions.items():
                try:
                    session.disconnect()
                except:
                    pass
            
            self.sessions.clear()
            self.session_stats.clear()
            
            # Clear queue
            while not self.available_sessions.empty():
                try:
                    self.available_sessions.get_nowait()
                except queue.Empty:
                    break
            
            print(f"SSH session pool stopped")
    
    def _create_initial_sessions(self):
        """Create initial pool of SSH sessions"""
        for i in range(self.pool_size):
            session_id = f"session_{i}_{int(time.time())}"
            self._create_session(session_id)
    
    def _create_session(self, session_id: str) -> bool:
        """Create a new SSH session"""
        try:
            session = SSHConnectionManager(self.config, str(self.log_dir))
            
            if session.connect():
                self.sessions[session_id] = session
                self.session_stats[session_id] = SessionStats(
                    created_at=datetime.now(),
                    last_used=datetime.now()
                )
                self.available_sessions.put(session_id)
                print(f"Created SSH session: {session_id}")
                return True
            else:
                print(f"Failed to create SSH session: {session_id}")
                return False
                
        except Exception as e:
            print(f"Error creating session {session_id}: {e}")
            return False
    
    def _maintenance_worker(self):
        """Background maintenance worker"""
        while not self.maintenance_stop.wait(30):  # Check every 30 seconds
            try:
                self._perform_maintenance()
            except Exception as e:
                print(f"Maintenance error: {e}")
    
    def _perform_maintenance(self):
        """Perform session pool maintenance"""
        with self.session_lock:
            current_time = datetime.now()
            sessions_to_remove = []
            
            # Check each session
            for session_id, session in self.sessions.items():
                stats = self.session_stats[session_id]
                
                # Check session age
                age = current_time - stats.created_at
                if age.total_seconds() > self.max_session_age:
                    sessions_to_remove.append((session_id, "age_limit"))
                    continue
                
                # Check idle time
                idle_time = current_time - stats.last_used
                if idle_time.total_seconds() > self.max_idle_time:
                    sessions_to_remove.append((session_id, "idle_timeout"))
                    continue
                
                # Health check
                if not session.is_session_healthy():
                    sessions_to_remove.append((session_id, "unhealthy"))
                    continue
            
            # Remove stale sessions
            for session_id, reason in sessions_to_remove:
                self._remove_session(session_id, reason)
            
            # Ensure minimum pool size
            active_sessions = len(self.sessions)
            if active_sessions < self.pool_size:
                needed = self.pool_size - active_sessions
                for i in range(needed):
                    new_session_id = f"session_{active_sessions + i}_{int(time.time())}"
                    self._create_session(new_session_id)
    
    def _remove_session(self, session_id: str, reason: str):
        """Remove a session from the pool"""
        if session_id in self.sessions:
            try:
                self.sessions[session_id].disconnect()
            except:
                pass
            
            del self.sessions[session_id]
            del self.session_stats[session_id]
            print(f"Removed session {session_id} (reason: {reason})")
    
    def get_session(self, timeout: int = 30) -> Optional[SSHConnectionManager]:
        """Get an available session from the pool"""
        if not self.pool_active:
            raise RuntimeError("Session pool is not active")
        
        self.total_requests += 1
        
        try:
            # Try to get available session
            session_id = self.available_sessions.get(timeout=timeout)
            
            with self.session_lock:
                if session_id in self.sessions:
                    session = self.sessions[session_id]
                    stats = self.session_stats[session_id]
                    
                    # Verify session is still healthy
                    if session.is_session_healthy():
                        stats.last_used = datetime.now()
                        self.pool_hits += 1
                        return SessionWrapper(self, session_id, session)
                    else:
                        # Session is unhealthy, remove it
                        self._remove_session(session_id, "unhealthy_on_get")
                        
        except queue.Empty:
            pass
        
        # No available session, create temporary one
        self.pool_misses += 1
        temp_session = SSHConnectionManager(self.config, str(self.log_dir))
        if temp_session.connect():
            return TempSessionWrapper(temp_session)
        else:
            raise ConnectionError("Failed to create temporary SSH session")
    
    def return_session(self, session_id: str):
        """Return a session to the pool"""
        with self.session_lock:
            if session_id in self.sessions and self.pool_active:
                # Verify session is still healthy before returning
                session = self.sessions[session_id]
                if session.is_session_healthy():
                    self.available_sessions.put(session_id)
                else:
                    self._remove_session(session_id, "unhealthy_on_return")
    
    def execute_command(self, command: str, timeout: int = 30):
        """Execute command using pool session"""
        with self.get_session() as session:
            return session.execute_command(command, timeout)
    
    def get_pool_stats(self) -> Dict[str, Any]:
        """Get pool statistics"""
        with self.session_lock:
            active_sessions = len(self.sessions)
            available_sessions = self.available_sessions.qsize()
            
            # Calculate efficiency
            hit_rate = (self.pool_hits / self.total_requests * 100) if self.total_requests > 0 else 0
            
            # Session details
            session_details = {}
            for session_id, stats in self.session_stats.items():
                uptime = datetime.now() - stats.created_at
                session_details[session_id] = {
                    'age_seconds': int(uptime.total_seconds()),
                    'last_used': stats.last_used.isoformat(),
                    'command_count': stats.command_count,
                    'success_rate': (stats.success_count / max(1, stats.command_count)) * 100
                }
            
            return {
                'pool_active': self.pool_active,
                'pool_size': self.pool_size,
                'active_sessions': active_sessions,
                'available_sessions': available_sessions,
                'total_requests': self.total_requests,
                'pool_hits': self.pool_hits,
                'pool_misses': self.pool_misses,
                'hit_rate_percent': round(hit_rate, 2),
                'session_details': session_details
            }
    
    def save_pool_report(self):
        """Save pool statistics report"""
        report_file = self.log_dir / f"pool_report_{self.config.host.replace('.', '_')}.json"
        
        report = {
            'host': self.config.host,
            'generated': datetime.now().isoformat(),
            'pool_stats': self.get_pool_stats()
        }
        
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2, default=str)


class SessionWrapper:
    """Wrapper for pool sessions with automatic return"""
    
    def __init__(self, pool: SSHSessionPool, session_id: str, session: SSHConnectionManager):
        self.pool = pool
        self.session_id = session_id
        self.session = session
        self._returned = False
    
    def execute_command(self, command: str, timeout: int = 30):
        """Execute command and update statistics"""
        if self._returned:
            raise RuntimeError("Session has been returned to pool")
        
        stats = self.pool.session_stats[self.session_id]
        stats.command_count += 1
        
        try:
            result = self.session.execute_command(command, timeout)
            stats.success_count += 1
            return result
        except Exception as e:
            stats.error_count += 1
            raise
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if not self._returned:
            self.pool.return_session(self.session_id)
            self._returned = True


class TempSessionWrapper:
    """Wrapper for temporary sessions"""
    
    def __init__(self, session: SSHConnectionManager):
        self.session = session
    
    def execute_command(self, command: str, timeout: int = 30):
        return self.session.execute_command(command, timeout)
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.session.disconnect()


def main():
    """Example usage"""
    config = SSHConfig(
        host="example.com",
        username="root",
        password="your_password",
        max_retries=3
    )
    
    pool = SSHSessionPool(config, pool_size=2)
    
    try:
        pool.start_pool()
        
        # Test pool usage
        for i in range(10):
            try:
                exit_code, stdout, stderr = pool.execute_command(f"echo 'Test command {i}'")
                print(f"Command {i}: {stdout.strip()}")
                time.sleep(1)
            except Exception as e:
                print(f"Command {i} failed: {e}")
        
        # Show pool statistics
        stats = pool.get_pool_stats()
        print(f"Pool stats: {json.dumps(stats, indent=2)}")
        
    finally:
        pool.stop_pool()


if __name__ == "__main__":
    main()