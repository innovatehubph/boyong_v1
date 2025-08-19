"""
VPS Capabilities Helper for Pareng Boyong
Provides full access to VPS resources and services
"""

import subprocess
import asyncio
import os
import json
import psutil
import socket
from typing import Dict, Any, Optional, List
from python.helpers.print_style import PrintStyle

class VPSCapabilities:
    """Helper class to leverage full VPS capabilities from within container"""
    
    def __init__(self):
        self.container_name = "agent-zero-dev"
        self.vps_resources = self._check_resources()
        
    def _check_resources(self) -> Dict[str, Any]:
        """Check available VPS resources"""
        try:
            # Get system info
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            return {
                "memory": {
                    "total_gb": round(memory.total / (1024**3), 1),
                    "available_gb": round(memory.available / (1024**3), 1),
                    "percent_used": memory.percent
                },
                "disk": {
                    "total_gb": round(disk.total / (1024**3), 1),
                    "available_gb": round(disk.free / (1024**3), 1),
                    "percent_used": disk.percent
                },
                "cpu": {
                    "cores": psutil.cpu_count(),
                    "percent": psutil.cpu_percent(interval=1)
                },
                "network": {
                    "hostname": socket.gethostname(),
                    "ip": self._get_ip_address()
                }
            }
        except Exception as e:
            PrintStyle.error(f"Error checking resources: {e}")
            return {}
    
    def _get_ip_address(self) -> str:
        """Get the primary IP address"""
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
            return ip
        except:
            return "127.0.0.1"
    
    async def run_in_container(self, command: str, timeout: int = 30) -> Dict[str, Any]:
        """Execute command in container with proper environment"""
        try:
            # Prepare the command with proper environment
            docker_cmd = [
                "docker", "exec", 
                "-e", "NODE_ENV=production",
                "-e", "N8N_ENFORCE_SETTINGS_FILE_PERMISSIONS=false",
                "-e", "N8N_RUNNERS_ENABLED=true",
                self.container_name,
                "bash", "-c", command
            ]
            
            # Run with timeout
            process = await asyncio.create_subprocess_exec(
                *docker_cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            try:
                stdout, stderr = await asyncio.wait_for(
                    process.communicate(), 
                    timeout=timeout
                )
                
                return {
                    "success": process.returncode == 0,
                    "stdout": stdout.decode('utf-8'),
                    "stderr": stderr.decode('utf-8'),
                    "returncode": process.returncode
                }
            except asyncio.TimeoutError:
                process.kill()
                return {
                    "success": False,
                    "error": f"Command timed out after {timeout} seconds"
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    async def start_n8n(self, port: int = 5678) -> Dict[str, Any]:
        """Start n8n workflow automation service"""
        try:
            PrintStyle.info(f"Starting n8n on port {port}...")
            
            # Check if already running
            check_cmd = f"ps aux | grep 'n8n start' | grep -v grep"
            result = await self.run_in_container(check_cmd, timeout=5)
            
            if result["success"] and result["stdout"].strip():
                return {
                    "success": True,
                    "message": f"n8n already running",
                    "url": f"http://localhost:{port}"
                }
            
            # Start n8n in background
            start_cmd = f"""
            export N8N_PORT={port}
            export N8N_ENFORCE_SETTINGS_FILE_PERMISSIONS=false
            export N8N_RUNNERS_ENABLED=true
            export N8N_BASIC_AUTH_ACTIVE=false
            export N8N_HOST=0.0.0.0
            
            # Start in background with nohup
            nohup n8n start > /tmp/n8n.log 2>&1 &
            echo $! > /tmp/n8n.pid
            
            # Wait for startup
            sleep 3
            
            # Check if running
            if ps -p $(cat /tmp/n8n.pid) > /dev/null; then
                echo "SUCCESS: n8n started with PID $(cat /tmp/n8n.pid)"
            else
                echo "FAILED: n8n did not start"
                cat /tmp/n8n.log
            fi
            """
            
            result = await self.run_in_container(start_cmd, timeout=10)
            
            if result["success"] and "SUCCESS" in result["stdout"]:
                PrintStyle.success(f"n8n started successfully on port {port}")
                return {
                    "success": True,
                    "message": "n8n started successfully",
                    "url": f"http://localhost:{port}",
                    "output": result["stdout"]
                }
            else:
                PrintStyle.error(f"Failed to start n8n: {result.get('stderr', result.get('error'))}")
                return {
                    "success": False,
                    "error": result.get("stderr", result.get("error", "Unknown error")),
                    "output": result.get("stdout", "")
                }
                
        except Exception as e:
            PrintStyle.error(f"Error starting n8n: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def stop_n8n(self) -> Dict[str, Any]:
        """Stop n8n service"""
        try:
            stop_cmd = """
            if [ -f /tmp/n8n.pid ]; then
                kill $(cat /tmp/n8n.pid) 2>/dev/null
                rm /tmp/n8n.pid
                echo "n8n stopped"
            else
                pkill -f "n8n start" 2>/dev/null
                echo "n8n processes terminated"
            fi
            """
            
            result = await self.run_in_container(stop_cmd, timeout=5)
            return {
                "success": True,
                "message": result["stdout"].strip()
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    async def check_service_status(self, service_name: str) -> Dict[str, Any]:
        """Check status of a service"""
        try:
            check_cmd = f"ps aux | grep '{service_name}' | grep -v grep"
            result = await self.run_in_container(check_cmd, timeout=5)
            
            if result["success"] and result["stdout"].strip():
                processes = result["stdout"].strip().split('\n')
                return {
                    "running": True,
                    "processes": len(processes),
                    "details": processes[0] if processes else ""
                }
            else:
                return {
                    "running": False,
                    "processes": 0
                }
                
        except Exception as e:
            return {
                "running": False,
                "error": str(e)
            }
    
    async def install_npm_package(self, package_name: str, global_install: bool = True) -> Dict[str, Any]:
        """Install npm package in container"""
        try:
            scope = "-g" if global_install else ""
            install_cmd = f"npm install {scope} {package_name}"
            
            PrintStyle.info(f"Installing npm package: {package_name}")
            result = await self.run_in_container(install_cmd, timeout=120)
            
            if result["success"]:
                PrintStyle.success(f"Successfully installed {package_name}")
                return {
                    "success": True,
                    "message": f"Installed {package_name}",
                    "output": result["stdout"]
                }
            else:
                PrintStyle.error(f"Failed to install {package_name}")
                return {
                    "success": False,
                    "error": result.get("stderr", "Installation failed"),
                    "output": result.get("stdout", "")
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    async def run_node_script(self, script_content: str, timeout: int = 30) -> Dict[str, Any]:
        """Run Node.js script in container"""
        try:
            # Save script to temp file
            script_file = "/tmp/temp_script.js"
            save_cmd = f"cat > {script_file} << 'EOF'\n{script_content}\nEOF"
            
            result = await self.run_in_container(save_cmd, timeout=5)
            if not result["success"]:
                return result
            
            # Execute script
            run_cmd = f"node {script_file}"
            result = await self.run_in_container(run_cmd, timeout=timeout)
            
            # Clean up
            await self.run_in_container(f"rm -f {script_file}", timeout=5)
            
            return result
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def get_system_info(self) -> Dict[str, Any]:
        """Get comprehensive system information"""
        return {
            "resources": self.vps_resources,
            "container": {
                "name": self.container_name,
                "node_version": "v24.5.0",
                "npm_version": "11.5.1",
                "n8n_version": "1.105.4"
            },
            "capabilities": {
                "memory_gb": self.vps_resources.get("memory", {}).get("total_gb", 0),
                "disk_gb": self.vps_resources.get("disk", {}).get("available_gb", 0),
                "cpu_cores": self.vps_resources.get("cpu", {}).get("cores", 0),
                "can_run_n8n": True,
                "can_run_nodejs": True,
                "can_install_packages": True
            }
        }
    
    async def port_is_available(self, port: int) -> bool:
        """Check if a port is available"""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            result = sock.connect_ex(('localhost', port))
            sock.close()
            return result != 0  # Port is available if connection fails
        except:
            return False

# Singleton instance
vps_capabilities = VPSCapabilities()

# Helper functions for easy access
async def start_n8n(port: int = 5678):
    """Start n8n workflow automation"""
    return await vps_capabilities.start_n8n(port)

async def stop_n8n():
    """Stop n8n workflow automation"""
    return await vps_capabilities.stop_n8n()

async def check_service(service_name: str):
    """Check if a service is running"""
    return await vps_capabilities.check_service_status(service_name)

async def run_node_script(script: str):
    """Run Node.js script"""
    return await vps_capabilities.run_node_script(script)

def get_vps_info():
    """Get VPS system information"""
    return vps_capabilities.get_system_info()