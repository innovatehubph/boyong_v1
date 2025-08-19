"""
Pareng Boyong Enhanced Execution Manager
Provides reliable code execution with multiple fallback strategies
Addresses SSH socket closure issues by preferring local execution
"""

import asyncio
import os
import subprocess
import sys
from typing import Optional, Tuple, Union
from python.helpers.log import Log
from python.helpers.shell_local_optimized import OptimizedLocalInteractiveSession
from python.helpers.shell_ssh import SSHInteractiveSession
from python.helpers.print_style import PrintStyle
from python.helpers.error_recovery_system import get_recovery_system, auto_recover

class ExecutionStrategy:
    """Base class for execution strategies"""
    
    def __init__(self, logger: Log):
        self.logger = logger
        self.session = None
        
    async def connect(self) -> bool:
        """Connect to execution environment"""
        raise NotImplementedError
        
    def send_command(self, command: str):
        """Send command to execution environment"""
        raise NotImplementedError
        
    async def read_output(self, timeout: float = 0, reset_full_output: bool = False) -> Tuple[str, Optional[str]]:
        """Read output from execution environment"""
        raise NotImplementedError
        
    def close(self):
        """Close execution environment"""
        raise NotImplementedError

class LocalExecutionStrategy(ExecutionStrategy):
    """Local process execution strategy - most reliable"""
    
    def __init__(self, logger: Log):
        super().__init__(logger)
        self.session = OptimizedLocalInteractiveSession()
        
    async def connect(self) -> bool:
        try:
            await self.session.connect()
            self.logger.log("Local execution strategy connected successfully")
            return True
        except Exception as e:
            self.logger.log(f"Local execution strategy failed: {e}")
            return False
            
    def send_command(self, command: str):
        return self.session.send_command(command)
        
    async def read_output(self, timeout: float = 0, reset_full_output: bool = False) -> Tuple[str, Optional[str]]:
        return await self.session.read_output(timeout, reset_full_output)
    
    def is_command_finished(self) -> bool:
        """Check if command has finished executing"""
        if hasattr(self.session, 'is_command_finished'):
            return self.session.is_command_finished()
        return False
    
    async def kill_hanging_processes(self):
        """Kill any hanging child processes"""
        if hasattr(self.session, 'kill_hanging_processes'):
            await self.session.kill_hanging_processes()
        
    def close(self):
        return self.session.close()

class DirectProcessStrategy(ExecutionStrategy):
    """Direct subprocess execution - fallback for simple commands"""
    
    def __init__(self, logger: Log):
        super().__init__(logger)
        self.cwd = os.getcwd()
        
    async def connect(self) -> bool:
        self.logger.log("Direct process strategy ready")
        return True
        
    def send_command(self, command: str):
        """Execute command directly using subprocess"""
        try:
            # Store command for read_output
            self.last_command = command
            self.last_result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                cwd=self.cwd,
                timeout=30
            )
            return True
        except Exception as e:
            self.logger.log(f"Direct process execution failed: {e}")
            self.last_result = None
            return False
            
    async def read_output(self, timeout: float = 0, reset_full_output: bool = False) -> Tuple[str, Optional[str]]:
        if hasattr(self, 'last_result') and self.last_result:
            output = self.last_result.stdout
            if self.last_result.stderr:
                output += "\n" + self.last_result.stderr
            return output, output
        return "", None
        
    def close(self):
        pass

class SSHExecutionStrategy(ExecutionStrategy):
    """SSH execution strategy - last resort with enhanced resilience"""
    
    def __init__(self, logger: Log, hostname: str, port: int, username: str, password: str):
        super().__init__(logger)
        self.hostname = hostname
        self.port = port
        self.username = username
        self.password = password
        self.session = None
        
    async def connect(self) -> bool:
        try:
            self.session = SSHInteractiveSession(
                self.logger, self.hostname, self.port, self.username, self.password
            )
            await self.session.connect()
            self.logger.log(f"SSH execution strategy connected to {self.hostname}")
            return True
        except Exception as e:
            self.logger.log(f"SSH execution strategy failed: {e}")
            return False
            
    def send_command(self, command: str):
        if self.session:
            return self.session.send_command(command)
        raise Exception("SSH session not connected")
        
    async def read_output(self, timeout: float = 0, reset_full_output: bool = False) -> Tuple[str, Optional[str]]:
        if self.session:
            return await self.session.read_output(timeout, reset_full_output)
        return "", None
        
    def close(self):
        if self.session:
            self.session.close()

class ParengBoyongExecutionManager:
    """
    Comprehensive execution manager with multiple fallback strategies
    Designed to eliminate SSH socket closure issues
    """
    
    def __init__(self, logger: Log, config=None, agent_instance=None):
        self.logger = logger
        self.config = config
        self.agent = agent_instance
        self.current_strategy = None
        self.strategies = []
        self.recovery_system = get_recovery_system(agent_instance, logger)
        self._initialize_strategies()
        
    def _initialize_strategies(self):
        """Initialize execution strategies in order of reliability"""
        
        # Strategy 1: Local execution (most reliable)
        self.strategies.append(LocalExecutionStrategy(self.logger))
        
        # Strategy 2: Direct process execution (fallback)
        self.strategies.append(DirectProcessStrategy(self.logger))
        
        # Strategy 3: SSH execution (last resort, only if configured)
        if (self.config and 
            hasattr(self.config, 'code_exec_ssh_enabled') and 
            self.config.code_exec_ssh_enabled):
            
            ssh_strategy = SSHExecutionStrategy(
                self.logger,
                getattr(self.config, 'code_exec_ssh_addr', 'localhost'),
                getattr(self.config, 'code_exec_ssh_port', 22),
                getattr(self.config, 'code_exec_ssh_user', 'root'),
                getattr(self.config, 'code_exec_ssh_pass', '')
            )
            self.strategies.append(ssh_strategy)
            
    @auto_recover("establish execution connection")
    async def connect(self) -> bool:
        """Connect using the first available strategy with AI error recovery"""
        
        for i, strategy in enumerate(self.strategies):
            try:
                PrintStyle(font_color="cyan").print(f"Trying execution strategy {i+1}/{len(self.strategies)}: {strategy.__class__.__name__}")
                
                if await strategy.connect():
                    self.current_strategy = strategy
                    PrintStyle(font_color="green").print(f"✅ Connected using {strategy.__class__.__name__}")
                    return True
                    
            except Exception as e:
                self.logger.log(f"Strategy {strategy.__class__.__name__} failed: {e}")
                
                # Let the recovery system handle this error
                if self.recovery_system.enabled:
                    success, result = await self.recovery_system.handle_error_with_recovery(
                        e, strategy.connect, "establish connection for execution strategy"
                    )
                    if success:
                        self.current_strategy = strategy
                        PrintStyle(font_color="green").print(f"🔄 Recovery successful for {strategy.__class__.__name__}")
                        return True
                
                continue
                
        PrintStyle(font_color="red").print("❌ All execution strategies failed")
        return False
        
    @auto_recover("execute command")
    def send_command(self, command: str) -> bool:
        """Send command using current strategy with AI error recovery"""
        
        if not self.current_strategy:
            raise Exception("No execution strategy available")
            
        try:
            self.current_strategy.send_command(command)
            return True
        except Exception as e:
            self.logger.log(f"Command execution failed with {self.current_strategy.__class__.__name__}: {e}")
            
            # Use AI recovery system first, then fallback to strategy switching
            if self.recovery_system.enabled:
                success, result = asyncio.run(self.recovery_system.handle_error_with_recovery(
                    e, self.current_strategy.send_command, f"execute command: {command[:50]}...", command
                ))
                if success:
                    PrintStyle(font_color="green").print("🔄 Command execution recovered via AI")
                    return True
            
            # If AI recovery failed, try strategy switching
            return self._handle_execution_failure(command)
            
    def _handle_execution_failure(self, command: str) -> bool:
        """Handle execution failure by switching strategies"""
        
        current_index = self.strategies.index(self.current_strategy)
        
        # Try remaining strategies
        for strategy in self.strategies[current_index + 1:]:
            try:
                PrintStyle(font_color="yellow").print(f"🔄 Switching to {strategy.__class__.__name__}")
                
                if asyncio.run(strategy.connect()):
                    self.current_strategy = strategy
                    strategy.send_command(command)
                    PrintStyle(font_color="green").print(f"✅ Recovery successful with {strategy.__class__.__name__}")
                    return True
                    
            except Exception as e:
                self.logger.log(f"Fallback strategy {strategy.__class__.__name__} failed: {e}")
                continue
                
        return False
        
    async def read_output(self, timeout: float = 0, reset_full_output: bool = False) -> Tuple[str, Optional[str]]:
        """Read output from current strategy"""
        
        if not self.current_strategy:
            raise Exception("No execution strategy available")
            
        return await self.current_strategy.read_output(timeout, reset_full_output)
    
    def is_command_finished(self) -> bool:
        """Check if command has finished executing (for optimized sessions)"""
        if self.current_strategy and hasattr(self.current_strategy, 'is_command_finished'):
            return self.current_strategy.is_command_finished()
        return False
    
    async def kill_hanging_processes(self):
        """Kill any hanging child processes (for optimized sessions)"""
        if self.current_strategy and hasattr(self.current_strategy, 'kill_hanging_processes'):
            await self.current_strategy.kill_hanging_processes()
        
    def close(self):
        """Close current execution strategy"""
        
        if self.current_strategy:
            self.current_strategy.close()
            
    def get_strategy_info(self) -> str:
        """Get information about current execution strategy"""
        
        if self.current_strategy:
            return f"Using {self.current_strategy.__class__.__name__}"
        return "No active strategy"
        
    def is_local_execution(self) -> bool:
        """Check if currently using local execution"""
        
        return isinstance(self.current_strategy, (LocalExecutionStrategy, DirectProcessStrategy))
        
    def force_local_execution(self):
        """Force switch to local execution strategies only"""
        
        # Remove SSH strategies
        self.strategies = [s for s in self.strategies if not isinstance(s, SSHExecutionStrategy)]
        
        # Reset current strategy if it was SSH
        if isinstance(self.current_strategy, SSHExecutionStrategy):
            self.current_strategy = None
            
        PrintStyle(font_color="green").print("🔒 Forced local execution mode - SSH disabled")

# Global instance for easy access
_execution_manager = None

def get_execution_manager(logger: Log, config=None, agent_instance=None) -> ParengBoyongExecutionManager:
    """Get or create global execution manager instance"""
    global _execution_manager
    
    if _execution_manager is None:
        _execution_manager = ParengBoyongExecutionManager(logger, config, agent_instance)
        
    return _execution_manager

def reset_execution_manager():
    """Reset global execution manager - useful for testing"""
    global _execution_manager
    
    if _execution_manager:
        _execution_manager.close()
        _execution_manager = None