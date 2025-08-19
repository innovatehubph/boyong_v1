"""
Docker Multimedia Service Status Tool for Pareng Boyong
Unified status checker for all multimedia Docker services
"""

import asyncio
from typing import Dict, Any
from python.helpers.tool import Tool, Response
from python.helpers.print_style import PrintStyle
from python.helpers.docker_multimedia_client import DockerMultimediaClient

class DockerMultimediaStatus(Tool):
    """
    Check status and health of all Docker multimedia services
    
    Args:
        operation (str): Operation to perform - 'health', 'detailed', 'services', 'restart_all'
        service (str): Specific service to check - 'localai', 'pollinations', 'wan2gp', or 'all' (default: 'all')
        
    Examples:
        docker_multimedia_status
        docker_multimedia_status operation=health
        docker_multimedia_status operation=detailed
        docker_multimedia_status operation=services
        docker_multimedia_status service=pollinations
    """
    
    async def execute(self, **kwargs) -> Response:
        """Execute Docker multimedia status check"""
        
        operation = kwargs.get("operation", "health").lower()
        service = kwargs.get("service", "all").lower()
        
        try:
            async with DockerMultimediaClient() as client:
                
                if operation == "health":
                    return await self._check_health(client, service)
                elif operation == "detailed":
                    return await self._detailed_status(client, service)
                elif operation == "services":
                    return await self._list_services(client)
                elif operation == "restart_all":
                    return await self._restart_services_info(client)
                else:
                    return Response(
                        message=f"❌ Unknown operation '{operation}'. Available: health, detailed, services, restart_all",
                        break_loop=False
                    )
                    
        except Exception as e:
            PrintStyle.error(f"Docker multimedia status check failed: {e}")
            return Response(
                message=f"❌ Status check failed: {str(e)}",
                break_loop=False
            )
    
    async def _check_health(self, client: DockerMultimediaClient, service: str) -> Response:
        """Check health status of services"""
        
        health_status = await client.check_services_health()
        
        if service != "all" and service in health_status:
            # Single service health check
            is_healthy = health_status[service]
            service_config = client.services[service]
            
            status_icon = "✅" if is_healthy else "❌"
            status_text = "HEALTHY" if is_healthy else "UNHEALTHY"
            
            message = f"{status_icon} **{service.title()} Service: {status_text}**\n\n"
            message += f"🌐 **URL**: {service_config['url']}\n"
            message += f"🏥 **Health Endpoint**: {service_config['health_endpoint']}\n"
            
            if is_healthy:
                message += f"🟢 **Status**: Ready for requests\n"
            else:
                message += f"🔴 **Status**: Service unavailable\n"
                message += f"🔧 **Troubleshooting**: Use `docker logs pareng-boyong-{service}-1` to check logs\n"
            
            return Response(message=message, break_loop=False)
        
        # All services health check
        total_services = len(health_status)
        healthy_services = sum(1 for status in health_status.values() if status)
        
        message = f"🏥 **Docker Multimedia Services Health Report**\n\n"
        message += f"📊 **Overall Status**: {healthy_services}/{total_services} services healthy\n\n"
        
        for service_name, is_healthy in health_status.items():
            status_icon = "✅" if is_healthy else "❌"
            message += f"{status_icon} **{service_name.title()}**: {'Healthy' if is_healthy else 'Unhealthy'}\n"
        
        if healthy_services == total_services:
            message += f"\n🎉 **All services are operational!**\n"
            message += f"Ready for multimedia generation tasks.\n"
        elif healthy_services > 0:
            message += f"\n⚠️ **Partial service availability**\n"
            message += f"Some multimedia features may be limited.\n"
        else:
            message += f"\n🚨 **All services are down**\n"
            message += f"Multimedia generation is currently unavailable.\n"
        
        message += f"\n🔧 **Management Commands:**\n"
        message += f"• Check detailed status: `docker_multimedia_status operation=detailed`\n"
        message += f"• Restart all services: `docker-compose -f docker-compose.multimodal-new.yml restart`\n"
        message += f"• View service logs: `docker logs pareng-boyong-[service]-1`\n"
        
        return Response(message=message, break_loop=False)
    
    async def _detailed_status(self, client: DockerMultimediaClient, service: str) -> Response:
        """Get detailed status information for services"""
        
        health_status = await client.check_services_health()
        service_status = client.get_service_status()
        
        if service != "all" and service in service_status:
            # Single service detailed status
            status = service_status[service]
            is_healthy = health_status.get(service, False)
            
            message = f"📊 **{service.title()} Service Detailed Status**\n\n"
            message += f"{'✅' if is_healthy else '❌'} **Health**: {'Operational' if is_healthy else 'Unavailable'}\n"
            message += f"🌐 **Endpoint**: {status['url']}\n"
            message += f"🔍 **Health Check**: {status['endpoint']}\n\n"
            
            # Service-specific capabilities
            if service == 'localai':
                if is_healthy:
                    models = await client.get_localai_models()
                    message += f"🧠 **Available Models**: {len(models)}\n"
                    if models:
                        message += f"**Model List**: {', '.join(models[:3])}{'...' if len(models) > 3 else ''}\n"
                message += f"⚙️ **Capabilities**: Text generation, chat completion\n"
                message += f"🔧 **Usage**: `localai_integration operation=chat prompt=\"Your question\"`\n"
                
            elif service == 'pollinations':
                message += f"🎨 **Capabilities**: High-quality image generation\n"
                message += f"📐 **Resolution**: Up to 2048x2048 pixels\n"
                message += f"🎭 **Styles**: Photography, art, cartoon, etc.\n"
                message += f"🔧 **Usage**: `pollinations_integration operation=generate prompt=\"Your image\"`\n"
                
            elif service == 'wan2gp':
                message += f"🎬 **Capabilities**: CPU-optimized video generation\n"
                message += f"🤖 **Models**: 4 specialized models available\n"
                message += f"⏱️ **Duration**: 2-15 seconds (model dependent)\n"
                message += f"🔧 **Usage**: `wan2gp_integration operation=generate prompt=\"Your video\"`\n"
            
            return Response(message=message, break_loop=False)
        
        # All services detailed status
        message = f"📊 **All Docker Multimedia Services - Detailed Status**\n\n"
        
        for service_name in service_status.keys():
            status = service_status[service_name]
            is_healthy = health_status.get(service_name, False)
            
            message += f"{'✅' if is_healthy else '❌'} **{service_name.title()}**\n"
            message += f"  • URL: {status['url']}\n"
            message += f"  • Status: {'Online' if is_healthy else 'Offline'}\n"
            
            if service_name == 'localai' and is_healthy:
                models = await client.get_localai_models()
                message += f"  • Models: {len(models)} available\n"
            
            message += f"\n"
        
        # Service integration information
        message += f"🔗 **Service Integration Tools:**\n"
        message += f"• **LocalAI**: `localai_integration` - AI text and chat\n"
        message += f"• **Pollinations**: `pollinations_integration` - Image generation\n"
        message += f"• **Wan2GP**: `wan2gp_integration` - Video generation\n\n"
        
        message += f"🚀 **Quick Health Check:**\n"
        message += f"`docker_multimedia_status operation=health`\n"
        
        return Response(message=message, break_loop=False)
    
    async def _list_services(self, client: DockerMultimediaClient) -> Response:
        """List all available multimedia services and their capabilities"""
        
        message = f"🐳 **Docker Multimedia Services Overview**\n\n"
        
        services_info = {
            'localai': {
                'name': 'LocalAI',
                'description': 'Local AI model server with OpenAI API compatibility',
                'capabilities': ['Text generation', 'Chat completion', 'Model management'],
                'port': '8090',
                'container': 'pareng-boyong-localai-1',
                'tool': 'localai_integration'
            },
            'pollinations': {
                'name': 'Pollinations.AI',
                'description': 'High-quality image generation service',
                'capabilities': ['Image generation', 'Style control', 'Seed-based reproduction'],
                'port': '8091',
                'container': 'pareng-boyong-pollinations-1',
                'tool': 'pollinations_integration'
            },
            'wan2gp': {
                'name': 'Wan2GP',
                'description': 'CPU-optimized video generation with multiple models',
                'capabilities': ['Video generation', '4 specialized models', 'Motion control'],
                'port': '8092',
                'container': 'pareng-boyong-wan2gp-1',
                'tool': 'wan2gp_integration'
            }
        }
        
        for service_id, info in services_info.items():
            message += f"📦 **{info['name']}** ({service_id})\n"
            message += f"  🔸 **Description**: {info['description']}\n"
            message += f"  🔸 **Port**: {info['port']}\n"
            message += f"  🔸 **Container**: {info['container']}\n"
            message += f"  🔸 **Tool**: `{info['tool']}`\n"
            message += f"  🔸 **Capabilities**:\n"
            for capability in info['capabilities']:
                message += f"    • {capability}\n"
            message += f"\n"
        
        message += f"🔧 **Management Commands:**\n"
        message += f"• **Start all**: `docker-compose -f docker-compose.multimodal-new.yml up -d`\n"
        message += f"• **Stop all**: `docker-compose -f docker-compose.multimodal-new.yml down`\n"
        message += f"• **Restart all**: `docker-compose -f docker-compose.multimodal-new.yml restart`\n"
        message += f"• **View logs**: `docker logs [container-name]`\n\n"
        
        message += f"📊 **Status Check**: `docker_multimedia_status operation=health`\n"
        
        return Response(message=message, break_loop=False)
    
    async def _restart_services_info(self, client: DockerMultimediaClient) -> Response:
        """Provide information about restarting services"""
        
        message = f"🔄 **Docker Multimedia Services Restart Guide**\n\n"
        message += f"⚠️ **Note**: This tool provides restart commands but doesn't execute them.\n\n"
        
        message += f"🐳 **Individual Service Restart:**\n"
        message += f"• LocalAI: `docker restart pareng-boyong-localai-1`\n"
        message += f"• Pollinations: `docker restart pareng-boyong-pollinations-1`\n"
        message += f"• Wan2GP: `docker restart pareng-boyong-wan2gp-1`\n\n"
        
        message += f"📦 **All Services Restart:**\n"
        message += f"```bash\n"
        message += f"docker-compose -f docker-compose.multimodal-new.yml restart\n"
        message += f"```\n\n"
        
        message += f"🛠️ **Full Rebuild (if needed):**\n"
        message += f"```bash\n"
        message += f"docker-compose -f docker-compose.multimodal-new.yml down\n"
        message += f"docker-compose -f docker-compose.multimodal-new.yml up -d --build\n"
        message += f"```\n\n"
        
        message += f"📋 **Troubleshooting Steps:**\n"
        message += f"1. Check current status: `docker_multimedia_status`\n"
        message += f"2. View container logs: `docker logs [container-name]`\n"
        message += f"3. Check port conflicts: `netstat -tlnp | grep 809[0-2]`\n"
        message += f"4. Verify compose file: `docker-compose -f docker-compose.multimodal-new.yml config`\n\n"
        
        message += f"🔍 **After Restart Verification:**\n"
        message += f"`docker_multimedia_status operation=health`\n"
        
        return Response(message=message, break_loop=False)

# Register the tool
def register():
    return DockerMultimediaStatus()