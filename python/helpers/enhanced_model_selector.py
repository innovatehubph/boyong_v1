"""
Enhanced Model Selector UI
Provides intelligent model selection with search, recommendations, and real-time validation
Integrates with model discovery service and settings backup system
"""

import asyncio
import json
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from pathlib import Path
import hashlib

from python.helpers.model_discovery import (
    ModelDiscoveryService, ModelInfo, ModelRecommendation, ModelRequirements,
    get_model_recommendations, validate_model_exists
)
from python.helpers.settings_backup import (
    SettingsBackupManager, create_settings_backup, validate_new_settings
)
from python.helpers.print_style import PrintStyle


@dataclass
class ModelSelectorState:
    """State management for model selector"""
    current_provider: Optional[str] = None
    current_model: Optional[str] = None
    available_models: Dict[str, List[ModelInfo]] = field(default_factory=dict)
    recommendations: List[ModelRecommendation] = field(default_factory=list)
    search_results: List[ModelInfo] = field(default_factory=list)
    last_search_query: str = ""
    validation_results: Dict[str, Any] = field(default_factory=dict)
    
    
@dataclass
class ModelSelectionOptions:
    """Configuration options for model selection"""
    show_recommendations: bool = True
    show_cost_estimates: bool = True
    show_performance_info: bool = True
    enable_real_time_validation: bool = True
    max_recommendations: int = 5
    search_debounce_ms: int = 300
    

class EnhancedModelSelector:
    """
    Enhanced model selector with intelligent features
    - Real-time model discovery from providers
    - Smart recommendations based on use case
    - Search and filtering capabilities
    - Real-time validation and testing
    - Settings backup integration
    """
    
    def __init__(self):
        self.discovery_service = ModelDiscoveryService()
        self.backup_manager = SettingsBackupManager()
        
        self.state = ModelSelectorState()
        self.options = ModelSelectionOptions()
        
        # Model categories for organization
        self.model_categories = {
            "chat": ["conversational", "general", "assistant"],
            "coding": ["code", "programming", "development"],
            "analysis": ["analysis", "reasoning", "research"],
            "creative": ["creative", "writing", "artistic"],
            "vision": ["vision", "multimodal", "image"],
            "function_calling": ["tools", "api", "function"]
        }
        
        # Provider display names and colors
        self.provider_config = {
            "openai": {"name": "OpenAI", "color": "blue", "icon": "🤖"},
            "anthropic": {"name": "Anthropic", "color": "purple", "icon": "🧠"},
            "google": {"name": "Google", "color": "green", "icon": "🔍"},
            "groq": {"name": "Groq", "color": "orange", "icon": "⚡"},
            "ollama": {"name": "Ollama", "color": "gray", "icon": "🏠"},
            "openrouter": {"name": "OpenRouter", "color": "cyan", "icon": "🌐"}
        }
    
    async def initialize(self) -> Dict[str, Any]:
        """Initialize the model selector with available models"""
        PrintStyle(color="blue").print("🔄 Initializing enhanced model selector...")
        
        try:
            # Discover all available models
            async with self.discovery_service as service:
                all_models = await service.discover_all_models()
                self.state.available_models = all_models
            
            # Get initial recommendations for general chat use
            requirements = ModelRequirements(
                use_case="chat",
                budget_level="balanced",
                context_length_needed=4000,
                streaming_required=True
            )
            
            self.state.recommendations = await get_model_recommendations(requirements)
            
            return {
                "success": True,
                "total_models": sum(len(models) for models in all_models.values()),
                "providers": list(all_models.keys()),
                "recommendations_count": len(self.state.recommendations)
            }
            
        except Exception as e:
            PrintStyle(color="red").print(f"❌ Failed to initialize model selector: {str(e)}")
            return {"success": False, "error": str(e)}
    
    async def get_recommendations(self, requirements: ModelRequirements) -> List[ModelRecommendation]:
        """Get personalized model recommendations"""
        PrintStyle(color="blue").print(f"🎯 Getting recommendations for {requirements.use_case} use case...")
        
        try:
            recommendations = await get_model_recommendations(requirements)
            self.state.recommendations = recommendations
            
            # Limit to configured maximum
            if len(recommendations) > self.options.max_recommendations:
                recommendations = recommendations[:self.options.max_recommendations]
            
            PrintStyle(color="green").print(f"✅ Found {len(recommendations)} recommendations")
            return recommendations
            
        except Exception as e:
            PrintStyle(color="red").print(f"❌ Failed to get recommendations: {str(e)}")
            return []
    
    async def search_models(self, query: str, filters: Optional[Dict[str, Any]] = None) -> List[ModelInfo]:
        """Search models with intelligent filtering"""
        if not query.strip():
            return []
        
        self.state.last_search_query = query
        search_results = []
        
        try:
            # Search across all available models
            for provider, models in self.state.available_models.items():
                for model in models:
                    if self._matches_search_query(model, query, filters):
                        search_results.append(model)
            
            # Sort by relevance
            search_results = self._sort_by_relevance(search_results, query)
            
            self.state.search_results = search_results
            return search_results
            
        except Exception as e:
            PrintStyle(color="red").print(f"❌ Search failed: {str(e)}")
            return []
    
    async def validate_model_selection(self, provider: str, model_name: str) -> Dict[str, Any]:
        """Validate a model selection in real-time"""
        if not self.options.enable_real_time_validation:
            return {"skipped": True, "reason": "Real-time validation disabled"}
        
        try:
            validation_result = await validate_model_exists(provider, model_name)
            
            # Store validation results
            key = f"{provider}:{model_name}"
            self.state.validation_results[key] = {
                **validation_result,
                "timestamp": datetime.now().isoformat()
            }
            
            return validation_result
            
        except Exception as e:
            error_result = {"valid": False, "error": str(e)}
            key = f"{provider}:{model_name}"
            self.state.validation_results[key] = error_result
            return error_result
    
    async def apply_model_selection(self, provider: str, model_name: str, 
                                  model_type: str = "chat", backup_reason: str = "model_change") -> Dict[str, Any]:
        """Apply model selection with backup and validation"""
        PrintStyle(color="blue").print(f"🔄 Applying model selection: {provider}/{model_name}")
        
        try:
            # Create backup before changes
            backup_info = await create_settings_backup(backup_reason)
            
            # Validate model selection
            validation = await self.validate_model_selection(provider, model_name)
            if not validation.get("valid", False):
                return {
                    "success": False,
                    "error": f"Model validation failed: {validation.get('error', 'Unknown error')}",
                    "backup_id": backup_info.id
                }
            
            # Apply the model configuration
            # This would integrate with the actual settings system
            new_settings = self._create_settings_update(provider, model_name, model_type)
            
            # Validate complete settings
            settings_validation = await validate_new_settings(new_settings)
            if not settings_validation.is_valid:
                return {
                    "success": False,
                    "error": "Settings validation failed",
                    "issues": settings_validation.issues,
                    "backup_id": backup_info.id
                }
            
            # Update state
            self.state.current_provider = provider
            self.state.current_model = model_name
            
            PrintStyle(color="green").print(f"✅ Successfully applied model selection")
            
            return {
                "success": True,
                "provider": provider,
                "model": model_name,
                "backup_id": backup_info.id,
                "validation": validation,
                "warnings": settings_validation.warnings
            }
            
        except Exception as e:
            PrintStyle(color="red").print(f"❌ Failed to apply model selection: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def get_model_categories(self, models: List[ModelInfo]) -> Dict[str, List[ModelInfo]]:
        """Categorize models for better organization"""
        categorized = {}
        
        for model in models:
            # Determine primary category
            category = self._determine_model_category(model)
            
            if category not in categorized:
                categorized[category] = []
            categorized[category].append(model)
        
        # Sort models within each category
        for category in categorized:
            categorized[category].sort(key=lambda m: (m.performance_tier, -m.context_length))
        
        return categorized
    
    def get_provider_summary(self) -> Dict[str, Any]:
        """Get summary of available providers and their models"""
        summary = {}
        
        for provider, models in self.state.available_models.items():
            config = self.provider_config.get(provider, {})
            
            summary[provider] = {
                "display_name": config.get("name", provider.title()),
                "color": config.get("color", "gray"),
                "icon": config.get("icon", "🤖"),
                "model_count": len(models),
                "best_model": self._get_best_model(models),
                "cost_range": self._get_cost_range(models),
                "capabilities": self._get_provider_capabilities(models)
            }
        
        return summary
    
    def generate_ui_config(self) -> Dict[str, Any]:
        """Generate UI configuration for frontend components"""
        return {
            "providers": self.get_provider_summary(),
            "categories": list(self.model_categories.keys()),
            "options": {
                "show_recommendations": self.options.show_recommendations,
                "show_cost_estimates": self.options.show_cost_estimates,
                "show_performance_info": self.options.show_performance_info,
                "max_recommendations": self.options.max_recommendations,
                "search_debounce_ms": self.options.search_debounce_ms
            },
            "state": {
                "current_provider": self.state.current_provider,
                "current_model": self.state.current_model,
                "has_recommendations": len(self.state.recommendations) > 0,
                "has_search_results": len(self.state.search_results) > 0,
                "last_search_query": self.state.last_search_query
            }
        }
    
    def _matches_search_query(self, model: ModelInfo, query: str, filters: Optional[Dict[str, Any]] = None) -> bool:
        """Check if model matches search query and filters"""
        query_lower = query.lower()
        
        # Text matching
        text_match = (
            query_lower in model.name.lower() or
            query_lower in model.id.lower() or
            query_lower in model.provider.lower() or
            query_lower in model.description.lower()
        )
        
        if not text_match:
            return False
        
        # Apply filters if provided
        if filters:
            if "provider" in filters and model.provider != filters["provider"]:
                return False
            
            if "min_context_length" in filters and model.context_length < filters["min_context_length"]:
                return False
            
            if "supports_vision" in filters and model.supports_vision != filters["supports_vision"]:
                return False
            
            if "supports_function_calling" in filters and model.supports_function_calling != filters["supports_function_calling"]:
                return False
            
            if "max_cost" in filters and model.input_cost > filters["max_cost"]:
                return False
        
        return True
    
    def _sort_by_relevance(self, models: List[ModelInfo], query: str) -> List[ModelInfo]:
        """Sort models by relevance to search query"""
        def relevance_score(model: ModelInfo) -> float:
            score = 0.0
            query_lower = query.lower()
            
            # Exact matches get highest score
            if query_lower == model.name.lower():
                score += 10.0
            elif query_lower == model.id.lower():
                score += 9.0
            
            # Partial matches
            if query_lower in model.name.lower():
                score += 5.0
            if query_lower in model.id.lower():
                score += 4.0
            if query_lower in model.description.lower():
                score += 2.0
            
            # Quality factors
            if model.performance_tier == "premium":
                score += 1.0
            elif model.performance_tier == "fast":
                score += 0.5
            
            # Context length bonus
            score += min(model.context_length / 100000, 2.0)
            
            return score
        
        return sorted(models, key=relevance_score, reverse=True)
    
    def _determine_model_category(self, model: ModelInfo) -> str:
        """Determine the primary category for a model"""
        model_text = f"{model.name} {model.description}".lower()
        
        # Check capabilities first
        if model.supports_vision:
            return "vision"
        
        if model.supports_function_calling:
            return "function_calling"
        
        # Check text patterns
        for category, keywords in self.model_categories.items():
            if any(keyword in model_text for keyword in keywords):
                return category
        
        # Default category
        return "chat"
    
    def _get_best_model(self, models: List[ModelInfo]) -> Optional[Dict[str, Any]]:
        """Get the best model from a list"""
        if not models:
            return None
        
        # Sort by quality factors
        best = max(models, key=lambda m: (
            m.performance_tier == "premium",
            m.context_length,
            m.supports_vision,
            m.supports_function_calling,
            -m.input_cost if m.input_cost > 0 else 1000  # Prefer lower cost, but not free models
        ))
        
        return {
            "name": best.name,
            "id": best.id,
            "context_length": best.context_length,
            "performance_tier": best.performance_tier
        }
    
    def _get_cost_range(self, models: List[ModelInfo]) -> Dict[str, float]:
        """Get cost range for models"""
        costs = [m.input_cost for m in models if m.input_cost > 0]
        
        if not costs:
            return {"min": 0.0, "max": 0.0}
        
        return {"min": min(costs), "max": max(costs)}
    
    def _get_provider_capabilities(self, models: List[ModelInfo]) -> Dict[str, bool]:
        """Get capabilities summary for provider"""
        return {
            "vision": any(m.supports_vision for m in models),
            "function_calling": any(m.supports_function_calling for m in models),
            "high_context": any(m.context_length > 50000 for m in models),
            "premium_models": any(m.performance_tier == "premium" for m in models)
        }
    
    def _create_settings_update(self, provider: str, model_name: str, model_type: str) -> Dict[str, Any]:
        """Create settings update for model selection"""
        # This would create the actual settings structure
        # For now, return a sample structure
        return {
            f"{model_type}_model": {
                "provider": provider,
                "name": model_name,
                "api_key": "configured"  # Would be handled by secure key management
            }
        }


# Global enhanced model selector instance
model_selector = EnhancedModelSelector()


async def initialize_model_selector() -> Dict[str, Any]:
    """Initialize the enhanced model selector"""
    return await model_selector.initialize()


async def get_smart_recommendations(use_case: str = "chat", budget: str = "balanced") -> List[ModelRecommendation]:
    """Get smart model recommendations"""
    requirements = ModelRequirements(
        use_case=use_case,
        budget_level=budget,
        context_length_needed=4000,
        streaming_required=True
    )
    
    return await model_selector.get_recommendations(requirements)


async def search_available_models(query: str, filters: Optional[Dict[str, Any]] = None) -> List[ModelInfo]:
    """Search available models with filters"""
    return await model_selector.search_models(query, filters)


async def apply_model_configuration(provider: str, model_name: str, model_type: str = "chat") -> Dict[str, Any]:
    """Apply model configuration with backup and validation"""
    return await model_selector.apply_model_selection(provider, model_name, model_type)


def get_ui_configuration() -> Dict[str, Any]:
    """Get UI configuration for frontend integration"""
    return model_selector.generate_ui_config()


def get_model_categories_list() -> Dict[str, List[ModelInfo]]:
    """Get categorized model list"""
    all_models = []
    for models in model_selector.state.available_models.values():
        all_models.extend(models)
    
    return model_selector.get_model_categories(all_models)