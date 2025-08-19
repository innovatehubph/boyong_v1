from python.helpers.tool import Tool, Response
from python.helpers.print_style import PrintStyle
from dataclasses import dataclass
import json
import asyncio
from typing import Optional, Dict, Any, List


@dataclass
class ModelDiscoveryTool(Tool):
    """
    Advanced Model Discovery Tool
    Automatically discovers available AI models from multiple providers
    Provides intelligent recommendations based on user requirements
    """
    
    async def execute(self, **kwargs):
        await self.agent.handle_intervention()
        
        operation = self.args.get("operation", "discover").lower()
        provider = self.args.get("provider", "all")
        use_case = self.args.get("use_case", "chat")
        budget_level = self.args.get("budget_level", "balanced")
        
        try:
            if operation == "discover":
                return await self.discover_models(provider)
            elif operation == "recommend":
                return await self.get_recommendations(use_case, budget_level)
            elif operation == "validate":
                model_name = self.args.get("model_name")
                if not model_name:
                    return Response(message="❌ Model name required for validation", break_loop=False)
                return await self.validate_model(provider, model_name)
            elif operation == "search":
                query = self.args.get("query", "")
                return await self.search_models(query)
            else:
                return Response(
                    message=f"❌ Unknown operation: {operation}. Available: discover, recommend, validate, search",
                    break_loop=False
                )
                
        except Exception as e:
            PrintStyle.error(f"Model discovery failed: {str(e)}")
            return Response(
                message=f"❌ Model discovery error: {str(e)}",
                break_loop=False
            )
    
    async def discover_models(self, provider: str = "all") -> Response:
        """Discover available models from providers"""
        try:
            from python.helpers.model_discovery import ModelDiscoveryService
            
            async with ModelDiscoveryService() as service:
                if provider.lower() == "all":
                    PrintStyle(color="blue").print("🔍 Discovering models from all providers...")
                    all_models = await service.discover_all_models()
                    
                    total_models = sum(len(models) for models in all_models.values())
                    result_summary = {
                        "total_models": total_models,
                        "providers": {}
                    }
                    
                    for prov, models in all_models.items():
                        result_summary["providers"][prov] = {
                            "count": len(models),
                            "models": [{"name": m.name, "id": m.id, "performance_tier": m.performance_tier} for m in models[:5]]  # Top 5
                        }
                    
                    PrintStyle(color="green").print(f"✅ Discovered {total_models} models across {len(all_models)} providers")
                    
                    return Response(
                        message=f"🔍 **Model Discovery Results**\n\n" +
                               f"**Total Models Found**: {total_models}\n" +
                               f"**Providers**: {', '.join(all_models.keys())}\n\n" +
                               "\n".join([f"**{prov.title()}**: {len(models)} models" for prov, models in all_models.items()]) +
                               f"\n\n💡 Use `model_discovery operation=recommend` to get personalized recommendations!",
                        break_loop=False
                    )
                    
                else:
                    PrintStyle(color="blue").print(f"🔍 Discovering models for {provider}...")
                    models = await service.discover_models(provider)
                    
                    models_info = []
                    for model in models[:10]:  # Top 10 models
                        info = f"• **{model.name}** ({model.id})"
                        if model.context_length > 0:
                            info += f" - {model.context_length:,} tokens"
                        if model.input_cost > 0:
                            info += f" - ${model.input_cost:.2f}/1M tokens"
                        models_info.append(info)
                    
                    PrintStyle(color="green").print(f"✅ Found {len(models)} models for {provider}")
                    
                    return Response(
                        message=f"🔍 **{provider.title()} Models** ({len(models)} found)\n\n" +
                               "\n".join(models_info) +
                               (f"\n\n*(Showing top 10 of {len(models)} models)*" if len(models) > 10 else ""),
                        break_loop=False
                    )
                    
        except Exception as e:
            return Response(
                message=f"❌ Discovery failed: {str(e)}",
                break_loop=False
            )
    
    async def get_recommendations(self, use_case: str = "chat", budget_level: str = "balanced") -> Response:
        """Get intelligent model recommendations"""
        try:
            from python.helpers.model_discovery import ModelRequirements, get_model_recommendations
            
            PrintStyle(color="blue").print(f"🎯 Getting recommendations for {use_case} use case...")
            
            requirements = ModelRequirements(
                use_case=use_case,
                budget_level=budget_level,
                context_length_needed=4000,
                streaming_required=True
            )
            
            recommendations = await get_model_recommendations(requirements)
            
            if not recommendations:
                return Response(
                    message="❌ No recommendations found. Try different parameters.",
                    break_loop=False
                )
            
            rec_text = []
            for i, rec in enumerate(recommendations[:5], 1):
                model = rec.model
                score_percent = int(rec.score * 100)
                
                rec_info = f"**{i}. {model.name}** ({model.provider})\n"
                rec_info += f"   • **Match Score**: {score_percent}%\n"
                rec_info += f"   • **Context**: {model.context_length:,} tokens\n"
                if model.input_cost > 0:
                    rec_info += f"   • **Cost**: ${model.input_cost:.2f}/1M tokens\n"
                rec_info += f"   • **Tier**: {model.performance_tier.title()}\n"
                
                capabilities = []
                if model.supports_vision:
                    capabilities.append("Vision")
                if model.supports_function_calling:
                    capabilities.append("Functions")
                if model.supports_streaming:
                    capabilities.append("Streaming")
                if capabilities:
                    rec_info += f"   • **Features**: {', '.join(capabilities)}\n"
                
                rec_info += f"   • **Why**: {rec.reasoning}\n"
                rec_info += f"   • **Estimated Cost**: {rec.estimated_cost}"
                
                rec_text.append(rec_info)
            
            PrintStyle(color="green").print(f"✅ Generated {len(recommendations)} recommendations")
            
            return Response(
                message=f"🎯 **AI Model Recommendations** for {use_case}\n" +
                       f"*Budget Level: {budget_level}*\n\n" +
                       "\n\n".join(rec_text) +
                       f"\n\n💡 Use `model_discovery operation=validate provider=<provider> model_name=<model>` to test a specific model!",
                break_loop=False
            )
            
        except Exception as e:
            return Response(
                message=f"❌ Recommendations failed: {str(e)}",
                break_loop=False
            )
    
    async def validate_model(self, provider: str, model_name: str) -> Response:
        """Validate if a specific model exists and works"""
        try:
            from python.helpers.model_discovery import validate_model_exists
            
            PrintStyle(color="blue").print(f"🔍 Validating {provider}/{model_name}...")
            
            validation = await validate_model_exists(provider, model_name)
            
            if validation.get("valid", False):
                PrintStyle(color="green").print(f"✅ Model {provider}/{model_name} is valid")
                
                return Response(
                    message=f"✅ **Model Validation Successful**\n\n" +
                           f"**Model**: {model_name}\n" +
                           f"**Provider**: {provider.title()}\n" +
                           f"**Status**: Available and accessible\n" +
                           f"**Message**: {validation.get('message', 'Model is working correctly')}",
                    break_loop=False
                )
            else:
                error = validation.get("error", "Model not found")
                suggestions = validation.get("suggestions", [])
                
                PrintStyle(color="red").print(f"❌ Model {provider}/{model_name} validation failed")
                
                message = f"❌ **Model Validation Failed**\n\n" + \
                         f"**Model**: {model_name}\n" + \
                         f"**Provider**: {provider.title()}\n" + \
                         f"**Error**: {error}"
                
                if suggestions:
                    message += f"\n\n**Suggested Alternatives**:\n" + "\n".join([f"• {s}" for s in suggestions[:5]])
                
                return Response(message=message, break_loop=False)
                
        except Exception as e:
            return Response(
                message=f"❌ Validation failed: {str(e)}",
                break_loop=False
            )
    
    async def search_models(self, query: str) -> Response:
        """Search for models by name or capability"""
        try:
            from python.helpers.enhanced_model_selector import search_available_models
            
            if not query.strip():
                return Response(
                    message="❌ Search query required. Example: `model_discovery operation=search query=gpt`",
                    break_loop=False
                )
            
            PrintStyle(color="blue").print(f"🔍 Searching models for '{query}'...")
            
            results = await search_available_models(query)
            
            if not results:
                return Response(
                    message=f"❌ No models found matching '{query}'. Try different search terms.",
                    break_loop=False
                )
            
            search_results = []
            for model in results[:10]:  # Top 10 results
                result_info = f"• **{model.name}** ({model.provider})"
                if model.context_length > 0:
                    result_info += f" - {model.context_length:,} tokens"
                if model.input_cost > 0:
                    result_info += f" - ${model.input_cost:.2f}/1M"
                
                capabilities = []
                if model.supports_vision:
                    capabilities.append("Vision")
                if model.supports_function_calling:
                    capabilities.append("Functions")
                if capabilities:
                    result_info += f" - {', '.join(capabilities)}"
                
                search_results.append(result_info)
            
            PrintStyle(color="green").print(f"✅ Found {len(results)} models matching '{query}'")
            
            return Response(
                message=f"🔍 **Search Results** for '{query}'\n" +
                       f"*Found {len(results)} models*\n\n" +
                       "\n".join(search_results) +
                       (f"\n\n*(Showing top 10 of {len(results)} results)*" if len(results) > 10 else ""),
                break_loop=False
            )
            
        except Exception as e:
            return Response(
                message=f"❌ Search failed: {str(e)}",
                break_loop=False
            )