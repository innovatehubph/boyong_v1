import asyncio
import select
import subprocess
import time
import sys
import os
import signal
from typing import Optional, Tuple
import fcntl

class OptimizedLocalInteractiveSession:
    """Optimized shell session with proper process completion detection and zombie cleanup"""
    
    def __init__(self):
        self.process = None
        self.full_output = ''
        self.command_finished = False
        self.last_command = None
        self.process_tracker = []
        
    async def connect(self):
        """Start a new subprocess with optimized settings"""
        env = os.environ.copy()
        env['PS1'] = '[$?]>>> '  # Custom prompt for easy detection
        env['PS2'] = '... '      # Continuation prompt
        
        if sys.platform.startswith('win'):
            # Windows
            self.process = subprocess.Popen(
                ['cmd.exe'],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,  # Combine stderr with stdout
                text=True,
                bufsize=0,  # Unbuffered for real-time output
                env=env
            )
        else:
            # macOS and Linux - optimized bash settings
            self.process = subprocess.Popen(
                ['/bin/bash', '--norc', '--noprofile'],  # Skip slow RC files
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,  # Combine stderr with stdout
                text=True,
                bufsize=0,  # Unbuffered for real-time output
                env=env,
                preexec_fn=os.setsid  # Create new process group for better control
            )
            
            # Make stdout non-blocking for faster reads
            if self.process.stdout:
                fd = self.process.stdout.fileno()
                fl = fcntl.fcntl(fd, fcntl.F_GETFL)
                fcntl.fcntl(fd, fcntl.F_SETFL, fl | os.O_NONBLOCK)
        
        # Set custom prompt immediately
        if not sys.platform.startswith('win'):
            await self._send_silent_command('export PS1="[$?]>>> "')
            await self._send_silent_command('export PS2="... "')
            await self._send_silent_command('set +o history')  # Disable history for speed
            
        return True

    def close(self):
        """Properly close the shell and cleanup zombie processes"""
        if self.process:
            try:
                # Kill process group on Unix
                if not sys.platform.startswith('win') and self.process.pid:
                    os.killpg(os.getpgid(self.process.pid), signal.SIGTERM)
                else:
                    self.process.terminate()
                
                # Wait briefly for graceful termination
                try:
                    self.process.wait(timeout=2)
                except subprocess.TimeoutExpired:
                    # Force kill if needed
                    self.process.kill()
                    self.process.wait()
            except:
                pass
            finally:
                self.process = None
                
        # Clean up any tracked child processes
        for pid in self.process_tracker:
            try:
                os.kill(pid, signal.SIGTERM)
            except:
                pass
        self.process_tracker.clear()

    async def _send_silent_command(self, command: str):
        """Send a command without tracking output (for setup commands)"""
        if not self.process or not self.process.stdin:
            return
        self.process.stdin.write(command + '\n')
        self.process.stdin.flush()
        await asyncio.sleep(0.1)  # Brief wait for command to process

    def send_command(self, command: str):
        """Send command with completion marker for accurate detection"""
        if not self.process or not self.process.stdin:
            raise Exception("Shell not connected")
        
        self.full_output = ""
        self.command_finished = False
        self.last_command = command
        
        # Add echo marker to detect command completion
        marked_command = f"{command}; echo '__CMD_DONE_$?__'"
        
        self.process.stdin.write(marked_command + '\n')
        self.process.stdin.flush()
        
        # Track potential child processes
        if 'python' in command or 'node' in command:
            # Mark as potentially long-running
            self.track_child_processes()
    
    def track_child_processes(self):
        """Track child processes for cleanup"""
        if self.process and self.process.pid:
            try:
                # Get child PIDs on Unix
                if not sys.platform.startswith('win'):
                    import psutil
                    parent = psutil.Process(self.process.pid)
                    for child in parent.children(recursive=True):
                        if child.pid not in self.process_tracker:
                            self.process_tracker.append(child.pid)
            except:
                pass

    async def read_output(self, timeout: float = 0, reset_full_output: bool = False) -> Tuple[str, Optional[str]]:
        """Optimized output reading with proper completion detection"""
        if not self.process or not self.process.stdout:
            raise Exception("Shell not connected")

        if reset_full_output:
            self.full_output = ""
            
        partial_output = ''
        start_time = time.time()
        completion_marker = '__CMD_DONE_'
        prompt_marker = '[$?]>>>'
        
        # Adaptive timeout based on command type
        if self.last_command:
            if any(x in self.last_command for x in ['pip install', 'npm install', 'apt', 'yum']):
                timeout = max(timeout, 30)  # Longer timeout for package installs
            elif any(x in self.last_command for x in ['sleep', 'wait']):
                timeout = max(timeout, 10)  # Respect sleep commands
        
        consecutive_empty_reads = 0
        max_empty_reads = 3  # Stop after 3 consecutive empty reads
        
        while (timeout <= 0 or time.time() - start_time < timeout):
            try:
                # Non-blocking read with short select timeout
                if sys.platform.startswith('win'):
                    rlist, _, _ = select.select([self.process.stdout], [], [], 0.05)
                else:
                    # Even shorter timeout on Unix for responsiveness
                    rlist, _, _ = select.select([self.process.stdout], [], [], 0.01)
                
                if rlist:
                    # Read available data
                    try:
                        # Read up to 4KB at once for efficiency
                        chunk = os.read(self.process.stdout.fileno(), 4096).decode('utf-8', errors='ignore')
                        if chunk:
                            partial_output += chunk
                            self.full_output += chunk
                            consecutive_empty_reads = 0
                            
                            # Check for completion marker
                            if completion_marker in chunk:
                                # Extract output before marker
                                marker_pos = self.full_output.find(completion_marker)
                                if marker_pos >= 0:
                                    clean_output = self.full_output[:marker_pos]
                                    # Extract exit code if present
                                    exit_code_str = self.full_output[marker_pos:marker_pos+20]
                                    if '__CMD_DONE_' in exit_code_str:
                                        parts = exit_code_str.split('__')
                                        if len(parts) >= 2:
                                            exit_code = parts[1].strip()
                                            if exit_code and exit_code != '0':
                                                clean_output += f"\n[Exit code: {exit_code}]"
                                    
                                    self.full_output = clean_output
                                    self.command_finished = True
                                    return self.full_output, partial_output.replace(completion_marker, '').replace(exit_code_str, '')
                            
                            # Check for prompt (command likely finished)
                            if prompt_marker in chunk:
                                self.command_finished = True
                                # Clean prompt from output
                                self.full_output = self.full_output.replace(prompt_marker, '')
                                return self.full_output, partial_output.replace(prompt_marker, '')
                        else:
                            consecutive_empty_reads += 1
                    except BlockingIOError:
                        # No data available right now
                        consecutive_empty_reads += 1
                    except Exception:
                        consecutive_empty_reads += 1
                else:
                    consecutive_empty_reads += 1
                
                # Early exit if process terminated
                if self.process.poll() is not None:
                    # Process has terminated
                    self.command_finished = True
                    # Read any remaining output
                    try:
                        remaining = self.process.stdout.read()
                        if remaining:
                            partial_output += remaining
                            self.full_output += remaining
                    except:
                        pass
                    return self.full_output, partial_output
                
                # Early exit on consecutive empty reads (command likely done)
                if consecutive_empty_reads >= max_empty_reads and partial_output:
                    # Got some output and nothing new for a bit - likely done
                    self.command_finished = True
                    return self.full_output, partial_output
                
                # Very short sleep to prevent CPU spinning
                await asyncio.sleep(0.01)
                
            except Exception as e:
                # Handle any read errors gracefully
                if partial_output:
                    return self.full_output, partial_output
                break

        # Timeout reached or no more output
        if not partial_output:
            return self.full_output, None
        
        return self.full_output, partial_output

    def is_command_finished(self) -> bool:
        """Check if the last command has finished executing"""
        return self.command_finished

    async def kill_hanging_processes(self):
        """Kill any hanging child processes"""
        for pid in self.process_tracker:
            try:
                os.kill(pid, signal.SIGKILL)
            except:
                pass
        self.process_tracker.clear()

# Make it compatible with existing code
LocalInteractiveSession = OptimizedLocalInteractiveSession