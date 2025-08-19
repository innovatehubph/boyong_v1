"""
VPS Manager Tool for Pareng Boyong
Provides full access to VPS capabilities
"""

from python.helpers.tool import Tool, Response
from python.helpers.print_style import PrintStyle
import asyncio
import json

class VPSManager(Tool):
    """Tool to manage VPS resources and services"""
    
    async def execute(self, **kwargs) -> Response:
        """Execute VPS management commands"""
        
        action = kwargs.get("action", "info").lower()
        
        try:
            from python.helpers.vps_capabilities import (
                vps_capabilities, 
                start_n8n, 
                stop_n8n,
                check_service,
                run_node_script,
                get_vps_info
            )
            
            if action == "info":
                # Get system information
                info = get_vps_info()
                
                message = f"""🖥️ **VPS System Information**

**Resources:**
• Memory: {info['resources']['memory']['total_gb']}GB total, {info['resources']['memory']['available_gb']}GB available
• Disk: {info['resources']['disk']['available_gb']}GB available
• CPU: {info['resources']['cpu']['cores']} cores

**Container Environment:**
• Node.js: {info['container']['node_version']}
• npm: {info['container']['npm_version']}
• n8n: {info['container']['n8n_version']}

**Capabilities:**
• Can run n8n: ✅
• Can run Node.js: ✅
• Can install packages: ✅
• Process limits: UNLIMITED"""
                
                return Response(message=message, break_loop=False)
            
            elif action == "start_n8n":
                # Start n8n workflow automation
                port = kwargs.get("port", 5678)
                
                PrintStyle.info(f"Starting n8n on port {port}...")
                
                # Check if already running
                status = await check_service("n8n")
                if status["running"]:
                    return Response(
                        message=f"⚠️ n8n is already running with {status['processes']} process(es)",
                        break_loop=False
                    )
                
                # Start n8n
                result = await start_n8n(port)
                
                if result["success"]:
                    message = f"""✅ **n8n Workflow Automation Started!**

• Status: Running
• Access URL: {result['url']}
• Port: {port}

You can now:
1. Open the n8n editor at {result['url']}
2. Create workflows
3. Connect to external services
4. Automate tasks

To stop n8n, use: `action: "stop_n8n"`"""
                    
                    return Response(message=message, break_loop=False)
                else:
                    return Response(
                        message=f"❌ Failed to start n8n: {result.get('error', 'Unknown error')}",
                        break_loop=False
                    )
            
            elif action == "stop_n8n":
                # Stop n8n
                result = await stop_n8n()
                
                if result["success"]:
                    return Response(
                        message=f"✅ n8n stopped: {result['message']}",
                        break_loop=False
                    )
                else:
                    return Response(
                        message=f"❌ Failed to stop n8n: {result.get('error', 'Unknown error')}",
                        break_loop=False
                    )
            
            elif action == "check_service":
                # Check service status
                service = kwargs.get("service", "n8n")
                status = await check_service(service)
                
                if status["running"]:
                    message = f"✅ **{service} is running**\n• Processes: {status['processes']}"
                    if status.get("details"):
                        message += f"\n• Details: {status['details'][:100]}..."
                else:
                    message = f"❌ **{service} is not running**"
                
                return Response(message=message, break_loop=False)
            
            elif action == "run_node":
                # Run Node.js code
                code = kwargs.get("code", "console.log('Hello from Node.js!')")
                
                PrintStyle.info("Executing Node.js code...")
                result = await run_node_script(code)
                
                if result["success"]:
                    output = result["stdout"][:500] if result["stdout"] else "No output"
                    message = f"""✅ **Node.js Execution Successful**

**Output:**
```
{output}
```"""
                else:
                    error = result.get("stderr", result.get("error", "Unknown error"))
                    message = f"""❌ **Node.js Execution Failed**

**Error:**
```
{error[:500]}
```"""
                
                return Response(message=message, break_loop=False)
            
            elif action == "install_npm":
                # Install npm package
                package = kwargs.get("package", "")
                if not package:
                    return Response(
                        message="❌ Please specify a package name",
                        break_loop=False
                    )
                
                PrintStyle.info(f"Installing npm package: {package}")
                result = await vps_capabilities.install_npm_package(package)
                
                if result["success"]:
                    return Response(
                        message=f"✅ Successfully installed npm package: {package}",
                        break_loop=False
                    )
                else:
                    return Response(
                        message=f"❌ Failed to install {package}: {result.get('error', 'Unknown error')}",
                        break_loop=False
                    )
            
            else:
                # Help message
                return Response(
                    message="""📋 **VPS Manager Actions:**

• `action: "info"` - Get system information
• `action: "start_n8n"` - Start n8n workflow automation
• `action: "stop_n8n"` - Stop n8n
• `action: "check_service", service: "name"` - Check if service is running
• `action: "run_node", code: "..."` - Run Node.js code
• `action: "install_npm", package: "name"` - Install npm package

**Example:**
```
action: "start_n8n", port: 5678
```""",
                    break_loop=False
                )
                
        except Exception as e:
            PrintStyle.error(f"VPS Manager error: {e}")
            return Response(
                message=f"❌ VPS Manager error: {str(e)}",
                break_loop=False
            )

def register():
    return VPSManager()