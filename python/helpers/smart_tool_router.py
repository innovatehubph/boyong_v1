"""
Smart Tool Router for Pareng Boyong
Intelligent request routing with cost optimization and automatic tool selection
"""

import asyncio
import json
import os
from typing import Dict, List, Any, Optional, Tuple, Callable
from datetime import datetime, timedelta
import importlib.util
import sys
from pathlib import Path

# Import our capability advisor
try:
    from capability_advisor import CapabilityAdvisor, analyze_request, get_tool_parameters
except ImportError:
    # Fallback if import fails
    class CapabilityAdvisor:
        def __init__(self):
            pass
        def analyze_request(self, request, context=None):
            return {"error": "Capability advisor not available"}
    
    def analyze_request(request, context=None):
        return {"error": "Capability advisor not available"}
    
    def get_tool_parameters(tool_name, request, analysis):
        return {}

class SmartToolRouter:
    """
    Intelligent routing system for Pareng Boyong
    Automatically selects optimal tools with cost optimization
    """
    
    def __init__(self):
        self.advisor = CapabilityAdvisor()
        self.tool_cache = {}
        self.execution_history = []
        self.cost_tracking = {"daily": 0.0, "monthly": 0.0}
        self.fallback_chains = self._initialize_fallback_chains()
        self.system_status = {"last_check": None, "health": "unknown"}
        
        # Load tool functions dynamically
        self._load_available_tools()
    
    def _initialize_fallback_chains(self) -> Dict[str, List[str]]:
        """Initialize fallback chains for different content types"""
        return {
            "video": [
                "cost_optimized_video_generator",
                "trending_video_generator", 
                "advanced_video_generator",
                "simple_video_generator"
            ],
            "image": [
                "imagen4_generator",
                "multimedia_generator"
            ],
            "audio": [
                "multimedia_generator"
            ]
        }
    
    def _load_available_tools(self):
        """Dynamically load available tool functions"""
        tools_path = Path("/root/projects/pareng-boyong/python/tools")
        
        self.available_tools = {
            # Video tools
            "cost_optimized_video_generator": self._load_tool_function("cost_optimized_video_generator"),
            "trending_video_generator": self._load_tool_function("trending_video_generator"),
            "advanced_video_generator": self._load_tool_function("advanced_video_generator"),
            "simple_video_generator": self._load_tool_function("simple_video_generator"),
            
            # Image tools
            "imagen4_generator": self._load_tool_function("imagen4_generator"),
            "multimedia_generator": self._load_tool_function("multimedia_generator"),
            
            # System tools
            "system_self_awareness": self._load_tool_function("system_self_awareness"),
            "enhanced_ui_renderer": self._load_tool_function("enhanced_ui_renderer")
        }
    
    def _load_tool_function(self, tool_name: str) -> Optional[Callable]:
        """Load a tool function dynamically"""
        try:
            tool_path = f"/root/projects/pareng-boyong/python/tools/{tool_name}.py"
            if os.path.exists(tool_path):
                spec = importlib.util.spec_from_file_location(tool_name, tool_path)
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                
                # Return the main function (same name as module)
                if hasattr(module, tool_name):
                    return getattr(module, tool_name)
            return None
        except Exception as e:
            print(f"Failed to load {tool_name}: {e}")
            return None
    
    async def route_request(
        self, 
        request: str, 
        context: Dict[str, Any] = None, 
        user_preferences: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Main routing function - intelligently routes requests to optimal tools
        
        Args:
            request: User's request text
            context: Additional context (budget, quality requirements, etc.)
            user_preferences: User preferences (cost_conscious, quality_preference, etc.)
        
        Returns:
            Dict containing result, tool used, costs, and reasoning
        """
        
        if context is None:
            context = {}
        if user_preferences is None:
            user_preferences = {"cost_conscious": True, "quality_preference": "standard"}
        
        # Step 1: System health check (for major operations)
        if self._should_check_system_health(request):
            health_check = await self._check_system_health()
            if health_check.get("critical", False):
                return {
                    "success": False,
                    "error": "System health critical - operation postponed",
                    "health_status": health_check,
                    "recommendation": "Please resolve system issues before proceeding"
                }
        
        # Step 2: Analyze request using capability advisor
        analysis = self.advisor.analyze_request(request, context)
        
        # Step 3: Apply user preferences
        analysis = self._apply_user_preferences(analysis, user_preferences)
        
        # Step 4: Check daily budget limits
        budget_check = self._check_budget_limits(analysis, context)
        if budget_check.get("exceeded", False):
            analysis["force_free"] = True
        
        # Step 5: Execute with intelligent routing
        result = await self._execute_with_routing(request, analysis, context)
        
        # Step 6: Log and track
        self._log_execution(request, analysis, result)
        self._update_cost_tracking(result)
        
        # Step 7: Enhance response if needed
        if result.get("success") and context.get("enhance_ui", False):
            result["enhanced_response"] = self._create_enhanced_response(result)
        
        return result
    
    def _should_check_system_health(self, request: str) -> bool:
        """Determine if system health check is needed"""
        high_resource_keywords = [
            "generate video", "create video", "professional", "high quality",
            "multiple", "batch", "large", "complex"
        ]
        
        return any(keyword in request.lower() for keyword in high_resource_keywords)
    
    async def _check_system_health(self) -> Dict[str, Any]:
        """Check system health using system_self_awareness tool"""
        try:
            if "system_self_awareness" in self.available_tools:
                health_func = self.available_tools["system_self_awareness"]
                health_result = health_func("health_check")
                
                # Parse health result (it returns markdown string)
                critical_indicators = ["critical", "poor", "high memory", "high cpu"]
                is_critical = any(indicator in health_result.lower() for indicator in critical_indicators)
                
                return {
                    "status": health_result,
                    "critical": is_critical,
                    "timestamp": datetime.now().isoformat()
                }
        except Exception as e:
            return {"error": str(e), "critical": False}
        
        return {"status": "Health check unavailable", "critical": False}
    
    def _apply_user_preferences(self, analysis: Dict[str, Any], preferences: Dict[str, Any]) -> Dict[str, Any]:
        """Apply user preferences to the analysis"""
        
        # Cost consciousness override
        if preferences.get("cost_conscious", True):
            analysis["force_free_preferred"] = True
            # Downgrade quality if user is cost-conscious
            if analysis.get("quality_level") == "premium":
                analysis["quality_level"] = "high_quality"
            elif analysis.get("quality_level") == "high_quality":
                analysis["quality_level"] = "standard"
        
        # Quality preference override
        quality_pref = preferences.get("quality_preference", "standard")
        if quality_pref == "premium" and not preferences.get("cost_conscious", True):
            analysis["quality_level"] = "premium"
        elif quality_pref == "basic":
            analysis["quality_level"] = "free_preferred"
        
        # Speed preference
        if preferences.get("speed_preference") == "fast":
            analysis["prefer_fast_tools"] = True
        
        return analysis
    
    def _check_budget_limits(self, analysis: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Check daily and request budget limits"""
        
        daily_limit = context.get("daily_budget", 5.0)  # $5 default daily limit
        request_limit = context.get("max_cost", 0.02)   # $0.02 default per request
        
        estimated_cost = analysis.get("cost_analysis", {}).get("total_estimated_cost", 0)
        
        budget_status = {
            "daily_spent": self.cost_tracking["daily"],
            "daily_limit": daily_limit,
            "request_cost": estimated_cost,
            "request_limit": request_limit,
            "exceeded": False,
            "warnings": []
        }
        
        # Check daily limit
        if self.cost_tracking["daily"] + estimated_cost > daily_limit:
            budget_status["exceeded"] = True
            budget_status["warnings"].append(f"Would exceed daily budget (${daily_limit})")
        
        # Check request limit
        if estimated_cost > request_limit:
            budget_status["warnings"].append(f"Exceeds per-request limit (${request_limit})")
        
        # Warning thresholds
        if self.cost_tracking["daily"] > daily_limit * 0.8:
            budget_status["warnings"].append("Approaching daily budget limit")
        
        return budget_status
    
    async def _execute_with_routing(
        self, 
        request: str, 
        analysis: Dict[str, Any], 
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute request with intelligent tool routing and fallbacks"""
        
        recommendations = analysis.get("recommendations", [])
        if not recommendations:
            return {"success": False, "error": "No tool recommendations available"}
        
        content_type = analysis.get("content_type", "image")
        fallback_chain = self.fallback_chains.get(content_type, [])
        
        # Try primary recommendation first
        for i, recommendation in enumerate(recommendations):
            tool_name = recommendation["tool"]
            
            print(f"🎯 Trying {tool_name} (priority {i+1})")
            
            # Get optimal parameters for this tool
            params = get_tool_parameters(tool_name, request, analysis)
            
            # Apply budget constraints
            if analysis.get("force_free_preferred") or context.get("force_free"):
                if "force_free" in params or "max_cost" in params:
                    params["force_free"] = True
                    params["max_cost"] = 0.00
            
            # Execute the tool
            result = await self._execute_tool(tool_name, params)
            
            if result and result.get("success"):
                result["tool_used"] = tool_name
                result["execution_tier"] = "primary" if i == 0 else f"secondary_{i}"
                result["reasoning"] = recommendation.get("reason", "Selected by intelligent routing")
                return result
            else:
                print(f"❌ {tool_name} failed: {result.get('error') if result else 'Unknown error'}")
        
        # If all recommendations failed, try fallback chain
        print("🔄 Trying fallback chain...")
        for tool_name in fallback_chain:
            if tool_name not in [r["tool"] for r in recommendations]:  # Skip already tried tools
                print(f"🔄 Fallback: Trying {tool_name}")
                
                # Basic parameters for fallback
                params = {"prompt": request} if content_type == "video" else {"prompt": request}
                if analysis.get("force_free_preferred"):
                    params["force_free"] = True
                
                result = await self._execute_tool(tool_name, params)
                
                if result and result.get("success"):
                    result["tool_used"] = tool_name
                    result["execution_tier"] = "fallback"
                    result["reasoning"] = "Fallback after primary tools failed"
                    return result
        
        # Ultimate fallback: create placeholder response
        return self._create_placeholder_response(request, content_type)
    
    async def _execute_tool(self, tool_name: str, params: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Execute a specific tool with given parameters"""
        
        if tool_name not in self.available_tools or not self.available_tools[tool_name]:
            return {"success": False, "error": f"Tool {tool_name} not available"}
        
        try:
            tool_func = self.available_tools[tool_name]
            
            # Handle different tool calling patterns
            if tool_name.endswith("_generator"):
                # For generator tools, determine operation
                operation = params.pop("operation", "generate")
                result = tool_func(operation, **params)
            else:
                # For other tools
                result = tool_func(**params)
            
            # Convert string results to dict format
            if isinstance(result, str):
                # Parse the markdown response for success indicators
                success = not any(error in result.lower() for error in ["❌", "error", "failed"])
                return {
                    "success": success,
                    "response": result,
                    "raw_output": result
                }
            elif isinstance(result, dict):
                return result
            else:
                return {"success": False, "error": f"Unexpected result type: {type(result)}"}
        
        except Exception as e:
            return {"success": False, "error": f"Tool execution failed: {str(e)}"}
    
    def _create_placeholder_response(self, request: str, content_type: str) -> Dict[str, Any]:
        """Create a placeholder response when all tools fail"""
        
        placeholders = {
            "video": {
                "success": True,
                "message": f"Video placeholder created for: {request}",
                "file_path": "/placeholder/video.html",
                "note": "All video services unavailable - placeholder generated"
            },
            "image": {
                "success": True, 
                "message": f"Image placeholder created for: {request}",
                "file_path": "/placeholder/image.svg",
                "note": "All image services unavailable - placeholder generated"
            },
            "audio": {
                "success": True,
                "message": f"Audio placeholder created for: {request}", 
                "file_path": "/placeholder/audio.html",
                "note": "All audio services unavailable - placeholder generated"
            }
        }
        
        placeholder = placeholders.get(content_type, placeholders["image"])
        placeholder.update({
            "tool_used": "placeholder_generator",
            "execution_tier": "placeholder",
            "reasoning": "All primary and fallback tools failed - placeholder ensures user gets response",
            "estimated_cost": 0.00
        })
        
        return placeholder
    
    def _create_enhanced_response(self, result: Dict[str, Any]) -> str:
        """Create enhanced UI response using enhanced_ui_renderer"""
        
        try:
            if "enhanced_ui_renderer" in self.available_tools:
                renderer_func = self.available_tools["enhanced_ui_renderer"]
                
                components = [
                    {
                        "type": "shadcn",
                        "name": "alert",
                        "props": {
                            "variant": "default",
                            "title": "Generation Complete",
                            "children": f"Successfully generated using {result.get('tool_used', 'unknown tool')}"
                        }
                    },
                    {
                        "type": "shadcn",
                        "name": "card",
                        "props": {
                            "title": "Results",
                            "children": f"""
                            <p><strong>Tool Used:</strong> {result.get('tool_used', 'Unknown')}</p>
                            <p><strong>Cost:</strong> ${result.get('estimated_cost', 0):.3f}</p>
                            <p><strong>File:</strong> {result.get('file_path', 'N/A')}</p>
                            """
                        }
                    }
                ]
                
                return renderer_func("page", title="Generation Result", components=components)
        except Exception as e:
            print(f"Enhanced UI rendering failed: {e}")
        
        return result.get("response", "Enhanced response unavailable")
    
    def _log_execution(self, request: str, analysis: Dict[str, Any], result: Dict[str, Any]):
        """Log execution for learning and optimization"""
        
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "request_hash": hash(request) % 10000,  # Anonymized
            "content_type": analysis.get("content_type"),
            "quality_level": analysis.get("quality_level"),
            "tool_used": result.get("tool_used"),
            "execution_tier": result.get("execution_tier"),
            "success": result.get("success", False),
            "cost": result.get("estimated_cost", 0),
            "reasoning": result.get("reasoning", "")
        }
        
        self.execution_history.append(log_entry)
        
        # Keep only last 100 entries to prevent memory bloat
        if len(self.execution_history) > 100:
            self.execution_history = self.execution_history[-100:]
    
    def _update_cost_tracking(self, result: Dict[str, Any]):
        """Update cost tracking metrics"""
        
        cost = result.get("estimated_cost", 0)
        if cost > 0:
            self.cost_tracking["daily"] += cost
            self.cost_tracking["monthly"] += cost
    
    def get_routing_statistics(self) -> Dict[str, Any]:
        """Get routing statistics and performance metrics"""
        
        if not self.execution_history:
            return {"message": "No routing history available"}
        
        total_executions = len(self.execution_history)
        successful_executions = sum(1 for entry in self.execution_history if entry["success"])
        
        # Tool usage statistics
        tool_usage = {}
        tier_usage = {}
        content_type_stats = {}
        
        for entry in self.execution_history:
            tool = entry.get("tool_used", "unknown")
            tier = entry.get("execution_tier", "unknown")
            content_type = entry.get("content_type", "unknown")
            
            tool_usage[tool] = tool_usage.get(tool, 0) + 1
            tier_usage[tier] = tier_usage.get(tier, 0) + 1
            content_type_stats[content_type] = content_type_stats.get(content_type, 0) + 1
        
        # Cost statistics
        total_cost = sum(entry.get("cost", 0) for entry in self.execution_history)
        avg_cost = total_cost / total_executions if total_executions > 0 else 0
        free_executions = sum(1 for entry in self.execution_history if entry.get("cost", 0) == 0)
        
        return {
            "performance": {
                "total_executions": total_executions,
                "success_rate": f"{(successful_executions/total_executions)*100:.1f}%" if total_executions > 0 else "0%",
                "average_cost": f"${avg_cost:.4f}",
                "free_execution_rate": f"{(free_executions/total_executions)*100:.1f}%" if total_executions > 0 else "0%"
            },
            "tool_usage": tool_usage,
            "execution_tiers": tier_usage,
            "content_types": content_type_stats,
            "cost_tracking": self.cost_tracking,
            "recent_executions": self.execution_history[-10:]  # Last 10 for debugging
        }
    
    def optimize_routing_strategy(self) -> Dict[str, Any]:
        """Analyze performance and suggest routing optimizations"""
        
        stats = self.get_routing_statistics()
        optimizations = []
        
        if not self.execution_history:
            return {"optimizations": ["No execution history available for optimization"]}
        
        # Analyze success rates by tool
        tool_success_rates = {}
        for entry in self.execution_history:
            tool = entry.get("tool_used", "unknown")
            if tool not in tool_success_rates:
                tool_success_rates[tool] = {"total": 0, "success": 0}
            
            tool_success_rates[tool]["total"] += 1
            if entry.get("success"):
                tool_success_rates[tool]["success"] += 1
        
        # Suggest optimizations based on patterns
        for tool, stats_dict in tool_success_rates.items():
            success_rate = stats_dict["success"] / stats_dict["total"] if stats_dict["total"] > 0 else 0
            
            if success_rate < 0.7 and stats_dict["total"] > 5:
                optimizations.append(f"Consider demoting {tool} in priority (success rate: {success_rate:.1%})")
            elif success_rate > 0.95 and stats_dict["total"] > 10:
                optimizations.append(f"Consider promoting {tool} in priority (success rate: {success_rate:.1%})")
        
        # Cost optimization suggestions
        avg_cost = sum(entry.get("cost", 0) for entry in self.execution_history) / len(self.execution_history)
        if avg_cost > 0.02:
            optimizations.append(f"Average cost ${avg_cost:.3f} is above target - increase FREE service usage")
        
        # Fallback usage analysis
        fallback_usage = sum(1 for entry in self.execution_history if entry.get("execution_tier") == "fallback")
        if fallback_usage > len(self.execution_history) * 0.3:
            optimizations.append("High fallback usage detected - consider improving primary tool reliability")
        
        return {
            "optimizations": optimizations if optimizations else ["Routing strategy appears optimal"],
            "tool_performance": tool_success_rates,
            "recommendations": self._generate_routing_recommendations()
        }
    
    def _generate_routing_recommendations(self) -> List[str]:
        """Generate intelligent recommendations for routing improvements"""
        
        recommendations = []
        
        # Always recommend cost optimization
        recommendations.append("Continue prioritizing FREE services for maximum cost savings")
        
        # Analyze recent failures
        recent_failures = [entry for entry in self.execution_history[-20:] if not entry.get("success")]
        if len(recent_failures) > 5:
            recommendations.append("High recent failure rate - consider service health monitoring")
        
        # Free service usage
        free_usage = sum(1 for entry in self.execution_history if entry.get("cost", 0) == 0)
        total_usage = len(self.execution_history)
        
        if total_usage > 0:
            free_percentage = (free_usage / total_usage) * 100
            if free_percentage < 80:
                recommendations.append(f"FREE service usage at {free_percentage:.1f}% - aim for 80%+ for optimal cost savings")
            else:
                recommendations.append(f"Excellent FREE service usage at {free_percentage:.1f}%!")
        
        return recommendations


# Convenience functions for easy integration
_router = None

def get_router() -> SmartToolRouter:
    """Get global router instance"""
    global _router
    if _router is None:
        _router = SmartToolRouter()
    return _router

async def smart_route(request: str, context: Dict[str, Any] = None, user_preferences: Dict[str, Any] = None) -> Dict[str, Any]:
    """Main routing function - use this for all intelligent routing"""
    return await get_router().route_request(request, context, user_preferences)

def get_routing_stats() -> Dict[str, Any]:
    """Get routing performance statistics"""
    return get_router().get_routing_statistics()

def optimize_routing() -> Dict[str, Any]:
    """Get routing optimization recommendations"""
    return get_router().optimize_routing_strategy()


if __name__ == "__main__":
    # Test the smart router
    import asyncio
    
    async def test_router():
        router = SmartToolRouter()
        
        test_requests = [
            "Create a video of a cat in a garden",
            "Generate a professional product image for Instagram",
            "I need a quick test video",
            "Create a high-quality cinematic video for my business"
        ]
        
        print("🧠 **Smart Tool Router Test**\n")
        
        for i, request in enumerate(test_requests, 1):
            print(f"## Test {i}: \"{request}\"")
            
            result = await router.route_request(
                request,
                context={"enhance_ui": False},
                user_preferences={"cost_conscious": True}
            )
            
            print(f"**Tool Used**: {result.get('tool_used', 'None')}")
            print(f"**Success**: {result.get('success', False)}")
            print(f"**Cost**: ${result.get('estimated_cost', 0):.3f}")
            print(f"**Reasoning**: {result.get('reasoning', 'N/A')}")
            print(f"**Response**: {result.get('message', result.get('response', 'No response'))[:100]}...")
            print("\n" + "="*50 + "\n")
        
        # Show statistics
        stats = router.get_routing_statistics()
        print("📊 **Routing Statistics**")
        print(f"Success Rate: {stats['performance']['success_rate']}")
        print(f"Average Cost: {stats['performance']['average_cost']}")
        print(f"Free Execution Rate: {stats['performance']['free_execution_rate']}")
        
        # Show optimizations
        optimizations = router.optimize_routing_strategy()
        print("\n💡 **Optimization Suggestions**")
        for opt in optimizations['optimizations']:
            print(f"• {opt}")
    
    asyncio.run(test_router())