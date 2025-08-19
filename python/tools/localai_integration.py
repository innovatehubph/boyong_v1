"""
LocalAI Integration Tool for Pareng Boyong
Provides access to LocalAI Docker container for AI model capabilities
"""

import asyncio
from typing import Optional, Dict, Any, List
from python.helpers.tool import Tool, Response
from python.helpers.print_style import PrintStyle
from python.helpers.docker_multimedia_client import DockerMultimediaClient

class LocalAIIntegration(Tool):
    """
    Access LocalAI Docker service for AI text generation and model management
    
    Args:
        operation (str): Operation to perform - 'chat', 'models', 'health', 'status'
        prompt (str): Text prompt for chat completion (required for 'chat' operation)
        model (str): Model name to use (default: auto-select available model)
        max_tokens (int): Maximum tokens to generate (default: 1000)
        temperature (float): Sampling temperature 0.0-1.0 (default: 0.7)
        
    Examples:
        localai_integration operation=health
        localai_integration operation=models
        localai_integration operation=chat prompt="Explain quantum computing"
        localai_integration operation=chat prompt="Write Python code" model=gpt-3.5-turbo temperature=0.3
    """
    
    async def execute(self, **kwargs) -> Response:
        """Execute LocalAI integration operation"""
        
        operation = kwargs.get("operation", "health").lower()
        
        try:
            async with DockerMultimediaClient() as client:
                
                if operation == "health":
                    return await self._check_health(client)
                elif operation == "status":
                    return await self._get_status(client)
                elif operation == "models":
                    return await self._list_models(client)
                elif operation == "chat":
                    return await self._chat_completion(client, kwargs)
                else:
                    return Response(
                        message=f"❌ Unknown operation '{operation}'. Available: health, status, models, chat",
                        break_loop=False
                    )
                    
        except Exception as e:
            PrintStyle.error(f"LocalAI integration error: {e}")
            return Response(
                message=f"❌ LocalAI integration failed: {str(e)}",
                break_loop=False
            )
    
    async def _check_health(self, client: DockerMultimediaClient) -> Response:
        """Check LocalAI service health"""
        
        health_status = await client.check_services_health()
        localai_healthy = health_status.get('localai', False)
        
        if localai_healthy:
            # Get additional info
            models = await client.get_localai_models()
            model_count = len(models)
            
            message = f"✅ **LocalAI Service Status: HEALTHY**\n\n"
            message += f"📊 **Service Details:**\n"
            message += f"• **URL**: {client.services['localai']['url']}\n"
            message += f"• **Available Models**: {model_count}\n"
            message += f"• **Health Endpoint**: ✅ Responding\n"
            
            if models:
                message += f"\n🧠 **Available Models:**\n"
                for model in models[:5]:  # Show first 5 models
                    message += f"• {model}\n"
                if len(models) > 5:
                    message += f"• ... and {len(models) - 5} more\n"
            
            return Response(message=message, break_loop=False)
        else:
            message = f"❌ **LocalAI Service Status: UNAVAILABLE**\n\n"
            message += f"🔧 **Troubleshooting:**\n"
            message += f"• Check if Docker container is running: `docker ps | grep localai`\n"
            message += f"• Restart service: `docker-compose -f docker-compose.multimodal-new.yml restart localai`\n"
            message += f"• Check logs: `docker logs pareng-boyong-localai-1`\n"
            
            return Response(message=message, break_loop=False)
    
    async def _get_status(self, client: DockerMultimediaClient) -> Response:
        """Get detailed LocalAI status information"""
        
        status = client.get_service_status()
        localai_status = status.get('localai', {})
        
        message = f"📊 **LocalAI Service Status Report**\n\n"
        
        if localai_status.get('available'):
            message += f"✅ **Service**: Online\n"
            message += f"🌐 **Endpoint**: {localai_status['url']}\n"
            message += f"🏥 **Health Check**: {localai_status['endpoint']}\n"
            
            # Get models if available
            models = await client.get_localai_models()
            message += f"🧠 **Models Available**: {len(models)}\n"
            
            if models:
                message += f"\n**Model List:**\n"
                for i, model in enumerate(models, 1):
                    message += f"{i}. `{model}`\n"
            
            message += f"\n💡 **Usage Examples:**\n"
            message += f"```\nlocalai_integration operation=chat prompt=\"Your question here\"\n```"
            
        else:
            message += f"❌ **Service**: Offline\n"
            message += f"🔧 **Issue**: Container not responding\n"
            message += f"📋 **Next Steps**:\n"
            message += f"1. Check Docker status\n"
            message += f"2. Restart LocalAI container\n"
            message += f"3. Verify port 8090 availability\n"
        
        return Response(message=message, break_loop=False)
    
    async def _list_models(self, client: DockerMultimediaClient) -> Response:
        """List available LocalAI models"""
        
        if not client.is_service_available('localai'):
            return Response(
                message="❌ LocalAI service is not available. Check service health first.",
                break_loop=False
            )
        
        models = await client.get_localai_models()
        
        if not models:
            message = f"📝 **LocalAI Models: None Found**\n\n"
            message += f"⚠️ **Status**: No models are currently loaded\n"
            message += f"🔧 **Solution**: LocalAI needs models to be configured\n\n"
            message += f"**Typical models that can be loaded:**\n"
            message += f"• `gpt-3.5-turbo` (OpenAI API compatible)\n"
            message += f"• `llama2` (Local Llama model)\n"
            message += f"• `mistral` (Mistral 7B model)\n"
            message += f"• `codellama` (Code generation model)\n"
            
            return Response(message=message, break_loop=False)
        
        message = f"🧠 **LocalAI Available Models ({len(models)} found)**\n\n"
        
        for i, model in enumerate(models, 1):
            message += f"{i}. **`{model}`**\n"
        
        message += f"\n💡 **Usage Example:**\n"
        message += f"```\nlocalai_integration operation=chat prompt=\"Hello!\" model={models[0]}\n```"
        
        return Response(message=message, break_loop=False)
    
    async def _chat_completion(self, client: DockerMultimediaClient, kwargs: Dict[str, Any]) -> Response:
        """Perform chat completion with LocalAI"""
        
        prompt = kwargs.get("prompt", "").strip()
        if not prompt:
            return Response(
                message="❌ Please provide a 'prompt' parameter for chat completion.",
                break_loop=False
            )
        
        if not client.is_service_available('localai'):
            return Response(
                message="❌ LocalAI service is not available. Use 'localai_integration operation=health' to check status.",
                break_loop=False
            )
        
        # Get parameters with defaults
        model = kwargs.get("model", "gpt-3.5-turbo")
        max_tokens = int(kwargs.get("max_tokens", 1000))
        temperature = float(kwargs.get("temperature", 0.7))
        
        # Validate parameters
        max_tokens = max(1, min(max_tokens, 4096))  # Clamp between 1-4096
        temperature = max(0.0, min(temperature, 1.0))  # Clamp between 0-1
        
        PrintStyle(font_color="cyan").print(f"🧠 Sending chat request to LocalAI...")
        PrintStyle(font_color="white", background_color="blue", padding=True).print(f"Prompt: {prompt}")
        
        # Generate response
        response_text = await client.generate_text_localai(
            prompt=prompt,
            model=model,
            max_tokens=max_tokens,
            temperature=temperature
        )
        
        if response_text:
            message = f"🧠 **LocalAI Response** (Model: `{model}`)\n\n"
            message += f"**Prompt**: {prompt}\n\n"
            message += f"**Response**:\n{response_text}\n\n"
            message += f"📊 **Generation Parameters:**\n"
            message += f"• Model: `{model}`\n"
            message += f"• Max Tokens: {max_tokens}\n"
            message += f"• Temperature: {temperature}\n"
            
            return Response(message=message, break_loop=False)
        else:
            return Response(
                message="❌ LocalAI failed to generate a response. Check service logs for details.",
                break_loop=False
            )

# Register the tool
def register():
    return LocalAIIntegration()