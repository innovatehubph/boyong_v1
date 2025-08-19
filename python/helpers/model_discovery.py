"""
Model Discovery Service
Automatically discovers available models from various AI providers
Eliminates manual model research and reduces configuration errors
"""

import asyncio
import aiohttp
import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum
import os

from python.helpers.dotenv import get_dotenv_value
from python.helpers.print_style import PrintStyle


class ModelCapability(Enum):
    CHAT = "chat"
    VISION = "vision"
    FUNCTION_CALLING = "function_calling"
    STREAMING = "streaming"
    JSON_MODE = "json_mode"
    REASONING = "reasoning"


@dataclass
class ModelInfo:
    """Information about an AI model"""
    id: str
    name: str
    provider: str
    capabilities: List[ModelCapability] = field(default_factory=list)
    context_length: int = 0
    input_cost: float = 0.0  # Cost per 1M tokens
    output_cost: float = 0.0  # Cost per 1M tokens
    performance_tier: str = "standard"  # fast, standard, premium
    description: str = ""
    max_output_tokens: int = 0
    supports_streaming: bool = True
    supports_vision: bool = False
    supports_function_calling: bool = False
    last_updated: str = ""


@dataclass
class ModelRecommendation:
    """Model recommendation with scoring"""
    model: ModelInfo
    score: float
    reasoning: str
    estimated_cost: str
    use_cases: List[str] = field(default_factory=list)


@dataclass
class ModelRequirements:
    """Requirements for model selection"""
    use_case: str  # chat, utility, vision, function_calling
    budget_level: str = "balanced"  # cost_effective, balanced, premium
    context_length_needed: int = 4000
    streaming_required: bool = True
    vision_required: bool = False
    function_calling_required: bool = False
    performance_priority: str = "balanced"  # speed, balanced, quality


class ModelCache:
    """Cache for model discovery results"""
    
    def __init__(self, ttl_hours: int = 24):
        self.ttl_hours = ttl_hours
        self.cache: Dict[str, Dict[str, Any]] = {}
    
    def get(self, provider: str) -> Optional[Dict[str, Any]]:
        """Get cached models for provider"""
        if provider in self.cache:
            cached_data = self.cache[provider]
            timestamp = datetime.fromisoformat(cached_data["timestamp"])
            
            # Check if cache is still valid
            if datetime.now() - timestamp < timedelta(hours=self.ttl_hours):
                return cached_data
            else:
                # Remove expired cache
                del self.cache[provider]
        
        return None
    
    def set(self, provider: str, models: List[ModelInfo]) -> None:
        """Cache models for provider"""
        self.cache[provider] = {
            "timestamp": datetime.now().isoformat(),
            "models": [self._model_to_dict(model) for model in models]
        }
    
    def _model_to_dict(self, model: ModelInfo) -> Dict[str, Any]:
        """Convert ModelInfo to dictionary"""
        return {
            "id": model.id,
            "name": model.name,
            "provider": model.provider,
            "capabilities": [cap.value for cap in model.capabilities],
            "context_length": model.context_length,
            "input_cost": model.input_cost,
            "output_cost": model.output_cost,
            "performance_tier": model.performance_tier,
            "description": model.description,
            "max_output_tokens": model.max_output_tokens,
            "supports_streaming": model.supports_streaming,
            "supports_vision": model.supports_vision,
            "supports_function_calling": model.supports_function_calling,
            "last_updated": model.last_updated
        }


class ModelDiscoveryService:
    """
    Discovers available models from AI providers
    Provides intelligent recommendations based on requirements
    """
    
    def __init__(self):
        self.cache = ModelCache(ttl_hours=6)  # 6 hour cache
        self.session: Optional[aiohttp.ClientSession] = None
        
        # Provider API endpoints
        self.provider_apis = {
            "openrouter": "https://openrouter.ai/api/v1/models",
            "openai": "https://api.openai.com/v1/models",
            "anthropic": "https://api.anthropic.com/v1/models", 
            "groq": "https://api.groq.com/openai/v1/models",
            "ollama": "http://localhost:11434/api/tags"
        }
        
        # Fallback model lists (in case APIs are unavailable)
        self.fallback_models = self._get_fallback_models()
    
    async def __aenter__(self):
        """Async context manager entry"""
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=30),
            headers={"User-Agent": "Pareng-Boyong/1.0"}
        )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.session:
            await self.session.close()
    
    async def discover_models(self, provider: str) -> List[ModelInfo]:
        """Discover available models from a provider"""
        # Check cache first
        cached = self.cache.get(provider)
        if cached:
            PrintStyle(color="green").print(f"📋 Using cached models for {provider}")
            return [self._dict_to_model(model_dict) for model_dict in cached["models"]]
        
        PrintStyle(color="blue").print(f"🔍 Discovering models for {provider}...")
        
        try:
            models = await self._fetch_provider_models(provider)
            
            if models:
                # Cache results
                self.cache.set(provider, models)
                PrintStyle(color="green").print(f"✅ Found {len(models)} models for {provider}")
                return models
            else:
                # Use fallback models
                fallback = self.fallback_models.get(provider, [])
                PrintStyle(color="yellow").print(f"⚠️ Using fallback models for {provider}: {len(fallback)} models")
                return fallback
                
        except Exception as e:
            PrintStyle(color="red").print(f"❌ Failed to discover models for {provider}: {str(e)}")
            # Return fallback models
            return self.fallback_models.get(provider, [])
    
    async def discover_all_models(self) -> Dict[str, List[ModelInfo]]:
        """Discover models from all providers"""
        all_models = {}
        
        tasks = []
        for provider in self.provider_apis.keys():
            tasks.append(self._discover_provider_with_name(provider))
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        for result in results:
            if isinstance(result, tuple) and len(result) == 2:
                provider, models = result
                all_models[provider] = models
            elif isinstance(result, Exception):
                PrintStyle(color="red").print(f"❌ Provider discovery failed: {str(result)}")
        
        return all_models
    
    async def recommend_models(self, requirements: ModelRequirements) -> List[ModelRecommendation]:
        """Recommend models based on requirements"""
        PrintStyle(color="blue").print(f"🎯 Finding recommendations for {requirements.use_case} use case...")
        
        # Get all available models
        all_models = await self.discover_all_models()
        
        # Flatten models list
        models_list = []
        for provider_models in all_models.values():
            models_list.extend(provider_models)
        
        # Score and filter models
        recommendations = []
        for model in models_list:
            score = self._calculate_compatibility_score(model, requirements)
            
            if score > 0.3:  # Only recommend decent matches
                reasoning = self._generate_reasoning(model, requirements, score)
                estimated_cost = self._estimate_cost(model, requirements)
                use_cases = self._determine_use_cases(model)
                
                recommendations.append(ModelRecommendation(
                    model=model,
                    score=score,
                    reasoning=reasoning,
                    estimated_cost=estimated_cost,
                    use_cases=use_cases
                ))
        
        # Sort by score (highest first) and return top 10
        recommendations.sort(key=lambda x: x.score, reverse=True)
        top_recommendations = recommendations[:10]
        
        PrintStyle(color="green").print(f"✅ Found {len(top_recommendations)} model recommendations")
        return top_recommendations
    
    async def validate_model(self, provider: str, model_name: str) -> Dict[str, Any]:
        """Validate if a specific model exists and is accessible"""
        try:
            models = await self.discover_models(provider)
            
            # Find the model
            for model in models:
                if model.id == model_name or model.name == model_name:
                    return {
                        "valid": True,
                        "model": model,
                        "message": "Model found and accessible"
                    }
            
            return {
                "valid": False,
                "error": f"Model '{model_name}' not found for provider '{provider}'",
                "suggestions": [m.name for m in models[:5]]  # Suggest alternatives
            }
            
        except Exception as e:
            return {
                "valid": False,
                "error": f"Validation failed: {str(e)}",
                "suggestions": []
            }
    
    async def _discover_provider_with_name(self, provider: str) -> Tuple[str, List[ModelInfo]]:
        """Helper to discover models with provider name"""
        models = await self.discover_models(provider)
        return provider, models
    
    async def _fetch_provider_models(self, provider: str) -> List[ModelInfo]:
        """Fetch models from a specific provider API"""
        if not self.session:
            raise RuntimeError("Session not initialized. Use 'async with' context manager.")
        
        api_url = self.provider_apis.get(provider)
        if not api_url:
            raise ValueError(f"Unknown provider: {provider}")
        
        # Get API key for the provider
        api_key = self._get_api_key(provider)
        headers = self._get_headers(provider, api_key)
        
        try:
            async with self.session.get(api_url, headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    return self._parse_provider_response(provider, data)
                else:
                    raise Exception(f"API request failed with status {response.status}")
                    
        except asyncio.TimeoutError:
            raise Exception("API request timeout")
        except Exception as e:
            raise Exception(f"API request failed: {str(e)}")
    
    def _get_api_key(self, provider: str) -> Optional[str]:
        """Get API key for provider"""
        key_mapping = {
            "openrouter": "OPENROUTER_API_KEY",
            "openai": "OPENAI_API_KEY", 
            "anthropic": "ANTHROPIC_API_KEY",
            "groq": "GROQ_API_KEY"
        }
        
        env_key = key_mapping.get(provider)
        if env_key:
            return get_dotenv_value(env_key) or os.getenv(env_key)
        return None
    
    def _get_headers(self, provider: str, api_key: Optional[str]) -> Dict[str, str]:
        """Get headers for provider API request"""
        headers = {"Content-Type": "application/json"}
        
        if api_key:
            if provider == "anthropic":
                headers["x-api-key"] = api_key
            else:
                headers["Authorization"] = f"Bearer {api_key}"
        
        # Add provider-specific headers
        if provider == "openrouter":
            headers["HTTP-Referer"] = "https://pareng-boyong.ai"
            headers["X-Title"] = "Pareng Boyong"
        
        return headers
    
    def _parse_provider_response(self, provider: str, data: Dict[str, Any]) -> List[ModelInfo]:
        """Parse provider API response into ModelInfo objects"""
        models = []
        
        try:
            if provider == "openrouter":
                model_data = data.get("data", [])
                for model in model_data:
                    models.append(self._parse_openrouter_model(model))
            
            elif provider == "openai":
                model_data = data.get("data", [])
                for model in model_data:
                    models.append(self._parse_openai_model(model))
            
            elif provider == "anthropic":
                model_data = data.get("models", [])
                for model in model_data:
                    models.append(self._parse_anthropic_model(model))
            
            elif provider == "groq":
                model_data = data.get("data", [])
                for model in model_data:
                    models.append(self._parse_groq_model(model))
            
            elif provider == "ollama":
                model_data = data.get("models", [])
                for model in model_data:
                    models.append(self._parse_ollama_model(model))
        
        except Exception as e:
            PrintStyle(color="red").print(f"❌ Failed to parse {provider} response: {str(e)}")
        
        return models
    
    def _parse_openrouter_model(self, model_data: Dict[str, Any]) -> ModelInfo:
        """Parse OpenRouter model data"""
        return ModelInfo(
            id=model_data.get("id", ""),
            name=model_data.get("name", model_data.get("id", "")),
            provider="openrouter",
            context_length=model_data.get("context_length", 4000),
            input_cost=float(model_data.get("pricing", {}).get("prompt", 0)) * 1000000,
            output_cost=float(model_data.get("pricing", {}).get("completion", 0)) * 1000000,
            description=model_data.get("description", ""),
            supports_vision="vision" in model_data.get("architecture", {}).get("modality", ""),
            supports_function_calling="tool_use" in model_data.get("top_provider", {}).get("capabilities", []),
            last_updated=datetime.now().isoformat()
        )
    
    def _parse_openai_model(self, model_data: Dict[str, Any]) -> ModelInfo:
        """Parse OpenAI model data"""
        model_id = model_data.get("id", "")
        
        # Determine capabilities based on model ID
        supports_vision = "vision" in model_id or "gpt-4" in model_id
        supports_function_calling = "gpt-" in model_id and model_id not in ["gpt-3.5-turbo-instruct"]
        
        return ModelInfo(
            id=model_id,
            name=model_id,
            provider="openai",
            context_length=self._get_openai_context_length(model_id),
            input_cost=self._get_openai_pricing(model_id)["input"],
            output_cost=self._get_openai_pricing(model_id)["output"],
            description=f"OpenAI {model_id}",
            supports_vision=supports_vision,
            supports_function_calling=supports_function_calling,
            performance_tier=self._get_openai_performance_tier(model_id),
            last_updated=datetime.now().isoformat()
        )
    
    def _parse_anthropic_model(self, model_data: Dict[str, Any]) -> ModelInfo:
        """Parse Anthropic model data"""
        model_id = model_data.get("id", "")
        
        return ModelInfo(
            id=model_id,
            name=model_id,
            provider="anthropic",
            context_length=model_data.get("max_tokens_to_sample", 100000),
            input_cost=self._get_anthropic_pricing(model_id)["input"],
            output_cost=self._get_anthropic_pricing(model_id)["output"], 
            description=f"Anthropic {model_id}",
            supports_vision="claude-3" in model_id and "haiku" not in model_id,
            supports_function_calling=True,
            performance_tier=self._get_anthropic_performance_tier(model_id),
            last_updated=datetime.now().isoformat()
        )
    
    def _parse_groq_model(self, model_data: Dict[str, Any]) -> ModelInfo:
        """Parse Groq model data"""
        model_id = model_data.get("id", "")
        
        return ModelInfo(
            id=model_id,
            name=model_id,
            provider="groq",
            context_length=model_data.get("context_window", 8192),
            input_cost=0.0,  # Groq is often free/very cheap
            output_cost=0.0,
            description=f"Groq {model_id}",
            supports_vision=False,
            supports_function_calling="llama" in model_id.lower(),
            performance_tier="fast",
            last_updated=datetime.now().isoformat()
        )
    
    def _parse_ollama_model(self, model_data: Dict[str, Any]) -> ModelInfo:
        """Parse Ollama model data"""
        model_name = model_data.get("name", "")
        
        return ModelInfo(
            id=model_name,
            name=model_name,
            provider="ollama",
            context_length=8192,  # Default for most local models
            input_cost=0.0,  # Local models are free
            output_cost=0.0,
            description=f"Ollama {model_name}",
            supports_vision="vision" in model_name or "llava" in model_name,
            supports_function_calling="llama" in model_name or "mistral" in model_name,
            performance_tier="local",
            last_updated=datetime.now().isoformat()
        )
    
    def _calculate_compatibility_score(self, model: ModelInfo, requirements: ModelRequirements) -> float:
        """Calculate compatibility score between model and requirements"""
        score = 0.0
        
        # Base score for working model
        score += 0.3
        
        # Context length requirement
        if model.context_length >= requirements.context_length_needed:
            score += 0.2
        elif model.context_length > 0:
            ratio = model.context_length / requirements.context_length_needed
            score += 0.2 * min(ratio, 1.0)
        
        # Vision requirement
        if requirements.vision_required:
            if model.supports_vision:
                score += 0.15
            else:
                score -= 0.3  # Penalty for missing required feature
        
        # Function calling requirement
        if requirements.function_calling_required:
            if model.supports_function_calling:
                score += 0.15
            else:
                score -= 0.3
        
        # Budget considerations
        if requirements.budget_level == "cost_effective":
            if model.input_cost <= 1.0:  # $1 per 1M tokens
                score += 0.2
            elif model.input_cost <= 5.0:
                score += 0.1
        elif requirements.budget_level == "premium":
            if model.performance_tier in ["premium", "fast"]:
                score += 0.15
        
        # Performance tier matching
        if requirements.performance_priority == "speed" and model.performance_tier == "fast":
            score += 0.1
        elif requirements.performance_priority == "quality" and model.performance_tier == "premium":
            score += 0.1
        
        return min(score, 1.0)  # Cap at 1.0
    
    def _generate_reasoning(self, model: ModelInfo, requirements: ModelRequirements, score: float) -> str:
        """Generate human-readable reasoning for recommendation"""
        reasons = []
        
        if score > 0.8:
            reasons.append("Excellent match for your requirements")
        elif score > 0.6:
            reasons.append("Good fit with minor trade-offs")
        else:
            reasons.append("Acceptable option with some limitations")
        
        if model.context_length >= requirements.context_length_needed:
            reasons.append(f"Supports required context length ({model.context_length:,} tokens)")
        
        if requirements.vision_required and model.supports_vision:
            reasons.append("Supports vision/image processing")
        
        if requirements.function_calling_required and model.supports_function_calling:
            reasons.append("Supports function calling")
        
        if model.input_cost == 0.0:
            reasons.append("Free to use")
        elif model.input_cost <= 1.0:
            reasons.append("Very cost-effective")
        elif model.input_cost <= 5.0:
            reasons.append("Reasonably priced")
        
        if model.performance_tier == "fast":
            reasons.append("Optimized for speed")
        elif model.performance_tier == "premium":
            reasons.append("Premium quality results")
        
        return " • ".join(reasons)
    
    def _estimate_cost(self, model: ModelInfo, requirements: ModelRequirements) -> str:
        """Estimate cost for typical usage"""
        if model.input_cost == 0.0 and model.output_cost == 0.0:
            return "Free"
        
        # Estimate typical usage (1000 requests, avg 500 input + 200 output tokens)
        monthly_input_tokens = 1000 * 500
        monthly_output_tokens = 1000 * 200
        
        monthly_cost = (
            (monthly_input_tokens / 1_000_000) * model.input_cost +
            (monthly_output_tokens / 1_000_000) * model.output_cost
        )
        
        if monthly_cost < 0.01:
            return "< $0.01/month"
        elif monthly_cost < 1.0:
            return f"~${monthly_cost:.2f}/month"
        else:
            return f"~${monthly_cost:.0f}/month"
    
    def _determine_use_cases(self, model: ModelInfo) -> List[str]:
        """Determine suitable use cases for a model"""
        use_cases = []
        
        # Always suitable for chat
        use_cases.append("Chat & Conversations")
        
        if model.supports_function_calling:
            use_cases.append("Function Calling")
            use_cases.append("API Integration")
        
        if model.supports_vision:
            use_cases.append("Image Analysis")
            use_cases.append("Visual Q&A")
        
        if model.context_length > 32000:
            use_cases.append("Long Document Analysis")
            use_cases.append("Code Review")
        
        if model.performance_tier == "fast":
            use_cases.append("Real-time Applications")
        
        if model.input_cost <= 1.0:
            use_cases.append("High-volume Processing")
        
        return use_cases
    
    def _dict_to_model(self, model_dict: Dict[str, Any]) -> ModelInfo:
        """Convert dictionary back to ModelInfo"""
        return ModelInfo(
            id=model_dict.get("id", ""),
            name=model_dict.get("name", ""),
            provider=model_dict.get("provider", ""),
            capabilities=[ModelCapability(cap) for cap in model_dict.get("capabilities", [])],
            context_length=model_dict.get("context_length", 0),
            input_cost=model_dict.get("input_cost", 0.0),
            output_cost=model_dict.get("output_cost", 0.0),
            performance_tier=model_dict.get("performance_tier", "standard"),
            description=model_dict.get("description", ""),
            max_output_tokens=model_dict.get("max_output_tokens", 0),
            supports_streaming=model_dict.get("supports_streaming", True),
            supports_vision=model_dict.get("supports_vision", False),
            supports_function_calling=model_dict.get("supports_function_calling", False),
            last_updated=model_dict.get("last_updated", "")
        )
    
    def _get_fallback_models(self) -> Dict[str, List[ModelInfo]]:
        """Get fallback models when APIs are unavailable"""
        return {
            "openai": [
                ModelInfo(
                    id="gpt-4o", name="GPT-4o", provider="openai",
                    context_length=128000, input_cost=5.0, output_cost=15.0,
                    supports_vision=True, supports_function_calling=True,
                    performance_tier="premium", description="Most capable GPT-4 model"
                ),
                ModelInfo(
                    id="gpt-4o-mini", name="GPT-4o Mini", provider="openai",
                    context_length=128000, input_cost=0.15, output_cost=0.6,
                    supports_vision=True, supports_function_calling=True,
                    performance_tier="fast", description="Fast and affordable GPT-4"
                ),
                ModelInfo(
                    id="gpt-3.5-turbo", name="GPT-3.5 Turbo", provider="openai",
                    context_length=16385, input_cost=0.5, output_cost=1.5,
                    supports_function_calling=True,
                    performance_tier="fast", description="Fast and cost-effective"
                )
            ],
            "anthropic": [
                ModelInfo(
                    id="claude-3-5-sonnet-20241022", name="Claude 3.5 Sonnet", provider="anthropic",
                    context_length=200000, input_cost=3.0, output_cost=15.0,
                    supports_vision=True, supports_function_calling=True,
                    performance_tier="premium", description="Most intelligent Claude model"
                ),
                ModelInfo(
                    id="claude-3-haiku-20240307", name="Claude 3 Haiku", provider="anthropic",
                    context_length=200000, input_cost=0.25, output_cost=1.25,
                    supports_vision=True, supports_function_calling=True,
                    performance_tier="fast", description="Fastest Claude model"
                )
            ],
            "groq": [
                ModelInfo(
                    id="llama-3.1-70b-versatile", name="Llama 3.1 70B", provider="groq",
                    context_length=131072, input_cost=0.0, output_cost=0.0,
                    supports_function_calling=True,
                    performance_tier="fast", description="Large open-source model on Groq"
                ),
                ModelInfo(
                    id="llama-3.1-8b-instant", name="Llama 3.1 8B", provider="groq",
                    context_length=131072, input_cost=0.0, output_cost=0.0,
                    supports_function_calling=True,
                    performance_tier="fast", description="Fast open-source model"
                )
            ]
        }
    
    def _get_openai_context_length(self, model_id: str) -> int:
        """Get context length for OpenAI models"""
        context_lengths = {
            "gpt-4o": 128000,
            "gpt-4o-mini": 128000,
            "gpt-4-turbo": 128000,
            "gpt-4": 8192,
            "gpt-3.5-turbo": 16385
        }
        return context_lengths.get(model_id, 4000)
    
    def _get_openai_pricing(self, model_id: str) -> Dict[str, float]:
        """Get pricing for OpenAI models (per 1M tokens)"""
        pricing = {
            "gpt-4o": {"input": 5.0, "output": 15.0},
            "gpt-4o-mini": {"input": 0.15, "output": 0.6},
            "gpt-4-turbo": {"input": 10.0, "output": 30.0},
            "gpt-4": {"input": 30.0, "output": 60.0},
            "gpt-3.5-turbo": {"input": 0.5, "output": 1.5}
        }
        return pricing.get(model_id, {"input": 1.0, "output": 2.0})
    
    def _get_openai_performance_tier(self, model_id: str) -> str:
        """Get performance tier for OpenAI models"""
        if "gpt-4o" in model_id:
            return "premium" if "mini" not in model_id else "fast"
        elif "gpt-4" in model_id:
            return "premium"
        else:
            return "fast"
    
    def _get_anthropic_pricing(self, model_id: str) -> Dict[str, float]:
        """Get pricing for Anthropic models (per 1M tokens)"""
        pricing = {
            "claude-3-5-sonnet-20241022": {"input": 3.0, "output": 15.0},
            "claude-3-opus-20240229": {"input": 15.0, "output": 75.0},
            "claude-3-haiku-20240307": {"input": 0.25, "output": 1.25}
        }
        return pricing.get(model_id, {"input": 3.0, "output": 15.0})
    
    def _get_anthropic_performance_tier(self, model_id: str) -> str:
        """Get performance tier for Anthropic models"""
        if "opus" in model_id:
            return "premium"
        elif "haiku" in model_id:
            return "fast"
        else:
            return "premium"


# Global discovery service instance
discovery_service = ModelDiscoveryService()


async def discover_models_for_provider(provider: str) -> List[ModelInfo]:
    """Discover models for a specific provider"""
    async with ModelDiscoveryService() as service:
        return await service.discover_models(provider)


async def get_model_recommendations(requirements: ModelRequirements) -> List[ModelRecommendation]:
    """Get model recommendations based on requirements"""
    async with ModelDiscoveryService() as service:
        return await service.recommend_models(requirements)


async def validate_model_exists(provider: str, model_name: str) -> Dict[str, Any]:
    """Validate if a model exists for a provider"""
    async with ModelDiscoveryService() as service:
        return await service.validate_model(provider, model_name)