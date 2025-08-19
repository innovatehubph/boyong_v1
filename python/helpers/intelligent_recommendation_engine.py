"""
Intelligent Model Recommendation Engine
Advanced ML-powered system for personalized model recommendations
Analyzes user patterns, preferences, and requirements to suggest optimal models
"""

import json
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from pathlib import Path
import hashlib
import numpy as np
from collections import defaultdict, Counter
import math

from python.helpers.model_discovery import ModelInfo, ModelRecommendation, ModelRequirements
from python.helpers.model_validation_service import ValidationResult, validate_single_model
from python.helpers.print_style import PrintStyle


@dataclass
class UserProfile:
    """User profile for personalized recommendations"""
    user_id: str
    created_at: str
    
    # Usage patterns
    preferred_use_cases: Dict[str, float] = field(default_factory=dict)  # use_case -> frequency
    cost_sensitivity: float = 0.5  # 0=cost-insensitive, 1=very cost-sensitive
    performance_priority: str = "balanced"  # speed, balanced, quality
    
    # Model preferences
    preferred_providers: Dict[str, float] = field(default_factory=dict)  # provider -> preference score
    preferred_models: Dict[str, float] = field(default_factory=dict)  # model_id -> satisfaction score
    avoided_models: Dict[str, str] = field(default_factory=dict)  # model_id -> reason
    
    # Feature preferences
    vision_usage_frequency: float = 0.0
    function_calling_frequency: float = 0.0
    streaming_preference: float = 0.8
    context_length_needs: List[int] = field(default_factory=list)
    
    # Historical performance
    total_requests: int = 0
    successful_requests: int = 0
    average_satisfaction: float = 0.0
    
    # Learning data
    interaction_history: List[Dict[str, Any]] = field(default_factory=list)
    feedback_scores: Dict[str, List[float]] = field(default_factory=dict)  # model_id -> scores
    last_updated: str = field(default_factory=lambda: datetime.now().isoformat())


@dataclass
class RecommendationContext:
    """Context for generating recommendations"""
    use_case: str
    budget_constraint: Optional[float] = None
    performance_requirement: str = "balanced"
    required_features: List[str] = field(default_factory=list)
    context_length_needed: int = 4000
    real_time_requirement: bool = False
    previous_models_tried: List[str] = field(default_factory=list)
    session_context: Optional[Dict[str, Any]] = None


@dataclass
class RecommendationExplanation:
    """Detailed explanation for a recommendation"""
    primary_reasons: List[str]
    performance_prediction: Dict[str, float]
    cost_analysis: Dict[str, Any]
    alternatives: List[str]
    confidence_score: float
    potential_issues: List[str]


class IntelligentRecommendationEngine:
    """
    Advanced recommendation engine that learns from user behavior
    and provides personalized, context-aware model suggestions
    """
    
    def __init__(self):
        self.profiles_dir = Path("python/helpers/data/user_profiles")
        self.profiles_dir.mkdir(parents=True, exist_ok=True)
        
        self.analytics_dir = Path("python/helpers/data/analytics")
        self.analytics_dir.mkdir(parents=True, exist_ok=True)
        
        # Recommendation algorithms
        self.algorithms = {
            "collaborative_filtering": 0.3,
            "content_based": 0.4,
            "performance_based": 0.2,
            "cost_optimization": 0.1
        }
        
        # Global model statistics
        self.global_stats = {
            "model_popularity": defaultdict(int),
            "model_satisfaction": defaultdict(list),
            "use_case_model_success": defaultdict(lambda: defaultdict(list)),
            "provider_reliability": defaultdict(list)
        }
        
        # Feature weights for different use cases
        self.use_case_weights = {
            "chat": {
                "response_time": 0.3,
                "quality": 0.4,
                "cost": 0.2,
                "reliability": 0.1
            },
            "coding": {
                "accuracy": 0.4,
                "function_calling": 0.3,
                "response_time": 0.2,
                "cost": 0.1
            },
            "analysis": {
                "quality": 0.4,
                "context_length": 0.3,
                "accuracy": 0.2,
                "cost": 0.1
            },
            "creative": {
                "quality": 0.5,
                "creativity": 0.3,
                "response_time": 0.1,
                "cost": 0.1
            },
            "vision": {
                "vision_capability": 0.5,
                "accuracy": 0.3,
                "response_time": 0.1,
                "cost": 0.1
            }
        }
        
        self.load_global_statistics()
    
    async def get_intelligent_recommendations(self, 
                                           user_id: str,
                                           context: RecommendationContext,
                                           available_models: List[ModelInfo],
                                           max_recommendations: int = 5) -> List[Tuple[ModelRecommendation, RecommendationExplanation]]:
        """Get intelligent, personalized model recommendations"""
        
        PrintStyle(color="blue").print(f"🧠 Generating intelligent recommendations for {user_id}")
        
        # Load or create user profile
        user_profile = await self.get_user_profile(user_id)
        
        # Generate recommendations using multiple algorithms
        recommendations = []
        
        # 1. Collaborative Filtering Recommendations
        collab_recs = await self._collaborative_filtering(user_profile, context, available_models)
        
        # 2. Content-Based Recommendations
        content_recs = await self._content_based_filtering(user_profile, context, available_models)
        
        # 3. Performance-Based Recommendations
        performance_recs = await self._performance_based_recommendations(context, available_models)
        
        # 4. Cost-Optimized Recommendations
        cost_recs = await self._cost_optimized_recommendations(user_profile, context, available_models)
        
        # Combine and rank recommendations
        combined_scores = self._combine_recommendation_scores([
            (collab_recs, self.algorithms["collaborative_filtering"]),
            (content_recs, self.algorithms["content_based"]),
            (performance_recs, self.algorithms["performance_based"]),
            (cost_recs, self.algorithms["cost_optimization"])
        ])
        
        # Select top recommendations
        top_models = sorted(combined_scores.items(), key=lambda x: x[1], reverse=True)[:max_recommendations]
        
        # Generate detailed recommendations with explanations
        for model_id, score in top_models:
            model = next((m for m in available_models if m.id == model_id), None)
            if model:
                recommendation = ModelRecommendation(
                    model=model,
                    score=score,
                    reasoning=f"AI-powered recommendation based on your preferences",
                    estimated_cost=self._estimate_personalized_cost(user_profile, model),
                    use_cases=self._predict_use_cases(user_profile, model)
                )
                
                explanation = await self._generate_recommendation_explanation(
                    user_profile, context, model, score
                )
                
                recommendations.append((recommendation, explanation))
        
        # Update user profile with recommendation request
        await self._update_user_profile_with_request(user_profile, context)
        
        PrintStyle(color="green").print(f"✅ Generated {len(recommendations)} intelligent recommendations")
        return recommendations
    
    async def record_user_feedback(self, user_id: str, model_id: str, 
                                 satisfaction_score: float, feedback: Dict[str, Any]) -> None:
        """Record user feedback to improve future recommendations"""
        
        user_profile = await self.get_user_profile(user_id)
        
        # Update satisfaction scores
        if model_id not in user_profile.feedback_scores:
            user_profile.feedback_scores[model_id] = []
        
        user_profile.feedback_scores[model_id].append(satisfaction_score)
        
        # Update model preferences
        if satisfaction_score >= 4.0:  # High satisfaction
            user_profile.preferred_models[model_id] = user_profile.preferred_models.get(model_id, 0.5) + 0.1
        elif satisfaction_score <= 2.0:  # Low satisfaction
            user_profile.avoided_models[model_id] = feedback.get("reason", "User reported low satisfaction")
        
        # Update global statistics
        self.global_stats["model_satisfaction"][model_id].append(satisfaction_score)
        
        # Save updated profile
        await self.save_user_profile(user_profile)
        
        PrintStyle(color="green").print(f"✅ Recorded feedback for {model_id}: {satisfaction_score}/5.0")
    
    async def analyze_user_patterns(self, user_id: str) -> Dict[str, Any]:
        """Analyze user patterns and provide insights"""
        
        user_profile = await self.get_user_profile(user_id)
        
        analysis = {
            "profile_summary": {
                "total_requests": user_profile.total_requests,
                "success_rate": user_profile.successful_requests / max(user_profile.total_requests, 1),
                "average_satisfaction": user_profile.average_satisfaction,
                "profile_age_days": (datetime.now() - datetime.fromisoformat(user_profile.created_at)).days
            },
            
            "usage_patterns": {
                "top_use_cases": sorted(user_profile.preferred_use_cases.items(), 
                                      key=lambda x: x[1], reverse=True)[:5],
                "preferred_providers": sorted(user_profile.preferred_providers.items(),
                                            key=lambda x: x[1], reverse=True)[:3],
                "feature_usage": {
                    "vision": user_profile.vision_usage_frequency,
                    "function_calling": user_profile.function_calling_frequency,
                    "streaming": user_profile.streaming_preference
                }
            },
            
            "preferences": {
                "cost_sensitivity": user_profile.cost_sensitivity,
                "performance_priority": user_profile.performance_priority,
                "average_context_length": np.mean(user_profile.context_length_needs) if user_profile.context_length_needs else 4000
            },
            
            "model_performance": {
                "top_rated_models": self._get_top_rated_models(user_profile),
                "avoided_models": list(user_profile.avoided_models.keys()),
                "model_loyalty": self._calculate_model_loyalty(user_profile)
            },
            
            "recommendations": {
                "suggested_improvements": self._suggest_profile_improvements(user_profile),
                "cost_optimization_potential": self._analyze_cost_optimization_potential(user_profile),
                "new_features_to_try": self._suggest_new_features(user_profile)
            }
        }
        
        return analysis
    
    async def get_user_profile(self, user_id: str) -> UserProfile:
        """Get or create user profile"""
        profile_path = self.profiles_dir / f"{user_id}.json"
        
        if profile_path.exists():
            try:
                with open(profile_path, 'r') as f:
                    data = json.load(f)
                    return UserProfile(**data)
            except Exception as e:
                PrintStyle(color="yellow").print(f"⚠️ Error loading profile for {user_id}: {str(e)}")
        
        # Create new profile
        profile = UserProfile(
            user_id=user_id,
            created_at=datetime.now().isoformat()
        )
        
        await self.save_user_profile(profile)
        return profile
    
    async def save_user_profile(self, profile: UserProfile) -> None:
        """Save user profile to disk"""
        profile.last_updated = datetime.now().isoformat()
        profile_path = self.profiles_dir / f"{profile.user_id}.json"
        
        try:
            # Convert to dict for JSON serialization
            profile_dict = {
                'user_id': profile.user_id,
                'created_at': profile.created_at,
                'preferred_use_cases': profile.preferred_use_cases,
                'cost_sensitivity': profile.cost_sensitivity,
                'performance_priority': profile.performance_priority,
                'preferred_providers': profile.preferred_providers,
                'preferred_models': profile.preferred_models,
                'avoided_models': profile.avoided_models,
                'vision_usage_frequency': profile.vision_usage_frequency,
                'function_calling_frequency': profile.function_calling_frequency,
                'streaming_preference': profile.streaming_preference,
                'context_length_needs': profile.context_length_needs,
                'total_requests': profile.total_requests,
                'successful_requests': profile.successful_requests,
                'average_satisfaction': profile.average_satisfaction,
                'interaction_history': profile.interaction_history[-100:],  # Keep only recent history
                'feedback_scores': profile.feedback_scores,
                'last_updated': profile.last_updated
            }
            
            with open(profile_path, 'w') as f:
                json.dump(profile_dict, f, indent=2)
                
        except Exception as e:
            PrintStyle(color="red").print(f"❌ Error saving profile for {profile.user_id}: {str(e)}")
    
    async def _collaborative_filtering(self, user_profile: UserProfile, 
                                     context: RecommendationContext,
                                     available_models: List[ModelInfo]) -> Dict[str, float]:
        """Generate recommendations based on similar users"""
        recommendations = {}
        
        # Find similar users based on preferences
        similar_users = await self._find_similar_users(user_profile)
        
        if not similar_users:
            return recommendations
        
        # Aggregate preferences from similar users
        for model in available_models:
            score = 0.0
            weight_sum = 0.0
            
            for similar_user_id, similarity_score in similar_users:
                similar_profile = await self.get_user_profile(similar_user_id)
                
                # Get model preference from similar user
                model_pref = similar_profile.preferred_models.get(model.id, 0.0)
                
                # Weight by similarity and recency
                weight = similarity_score * self._get_recency_weight(similar_profile.last_updated)
                score += model_pref * weight
                weight_sum += weight
            
            if weight_sum > 0:
                recommendations[model.id] = score / weight_sum
        
        return self._normalize_scores(recommendations)
    
    async def _content_based_filtering(self, user_profile: UserProfile,
                                     context: RecommendationContext,
                                     available_models: List[ModelInfo]) -> Dict[str, float]:
        """Generate recommendations based on model characteristics and user preferences"""
        recommendations = {}
        
        for model in available_models:
            score = 0.0
            
            # Provider preference
            provider_pref = user_profile.preferred_providers.get(model.provider, 0.5)
            score += provider_pref * 0.2
            
            # Use case alignment
            use_case_score = user_profile.preferred_use_cases.get(context.use_case, 0.1)
            score += use_case_score * 0.3
            
            # Feature alignment
            if context.use_case in user_profile.preferred_use_cases:
                # Vision capability alignment
                if user_profile.vision_usage_frequency > 0.5 and model.supports_vision:
                    score += 0.15
                elif user_profile.vision_usage_frequency < 0.1 and not model.supports_vision:
                    score += 0.05
                
                # Function calling alignment
                if user_profile.function_calling_frequency > 0.5 and model.supports_function_calling:
                    score += 0.15
                elif user_profile.function_calling_frequency < 0.1 and not model.supports_function_calling:
                    score += 0.05
                
                # Streaming preference
                if user_profile.streaming_preference > 0.7 and model.supports_streaming:
                    score += 0.1
            
            # Cost sensitivity alignment
            if user_profile.cost_sensitivity > 0.7:  # Very cost sensitive
                if model.input_cost == 0.0:  # Free model
                    score += 0.2
                elif model.input_cost < 1.0:  # Cheap model
                    score += 0.1
                else:  # Expensive model
                    score -= 0.1
            
            # Performance tier alignment
            if user_profile.performance_priority == "speed" and model.performance_tier == "fast":
                score += 0.1
            elif user_profile.performance_priority == "quality" and model.performance_tier == "premium":
                score += 0.1
            
            # Context length needs
            if user_profile.context_length_needs:
                avg_context_need = np.mean(user_profile.context_length_needs)
                if model.context_length >= avg_context_need:
                    score += 0.1
                else:
                    score -= 0.05
            
            recommendations[model.id] = max(0.0, min(1.0, score))
        
        return self._normalize_scores(recommendations)
    
    async def _performance_based_recommendations(self, context: RecommendationContext,
                                               available_models: List[ModelInfo]) -> Dict[str, float]:
        """Generate recommendations based on model performance data"""
        recommendations = {}
        
        for model in available_models:
            score = 0.0
            
            # Global satisfaction score
            model_satisfaction = self.global_stats["model_satisfaction"].get(model.id, [])
            if model_satisfaction:
                avg_satisfaction = np.mean(model_satisfaction)
                score += (avg_satisfaction / 5.0) * 0.4
            else:
                score += 0.5  # Neutral score for unknown models
            
            # Use case specific performance
            use_case_performance = self.global_stats["use_case_model_success"].get(context.use_case, {}).get(model.id, [])
            if use_case_performance:
                avg_performance = np.mean(use_case_performance)
                score += avg_performance * 0.3
            
            # Provider reliability
            provider_reliability = self.global_stats["provider_reliability"].get(model.provider, [])
            if provider_reliability:
                avg_reliability = np.mean(provider_reliability)
                score += avg_reliability * 0.2
            
            # Model popularity (network effect)
            popularity = self.global_stats["model_popularity"].get(model.id, 0)
            if popularity > 0:
                popularity_score = min(math.log(popularity + 1) / 10, 0.1)
                score += popularity_score
            
            recommendations[model.id] = max(0.0, min(1.0, score))
        
        return self._normalize_scores(recommendations)
    
    async def _cost_optimized_recommendations(self, user_profile: UserProfile,
                                           context: RecommendationContext,
                                           available_models: List[ModelInfo]) -> Dict[str, float]:
        """Generate cost-optimized recommendations"""
        recommendations = {}
        
        # Calculate cost efficiency scores
        for model in available_models:
            score = 0.0
            
            # Base cost score (inversely related to cost)
            if model.input_cost == 0.0:
                cost_score = 1.0  # Free models get highest score
            else:
                # Normalize cost score (assumes typical range 0.1-30 per 1M tokens)
                normalized_cost = min(model.input_cost / 30.0, 1.0)
                cost_score = 1.0 - normalized_cost
            
            # Weight by user's cost sensitivity
            score += cost_score * user_profile.cost_sensitivity
            
            # Value proposition (performance per dollar)
            if model.input_cost > 0:
                # Estimate value based on performance tier
                performance_multiplier = {
                    "premium": 1.0,
                    "fast": 0.8,
                    "standard": 0.6,
                    "local": 0.4
                }.get(model.performance_tier, 0.5)
                
                value_score = performance_multiplier / max(model.input_cost, 0.1)
                score += value_score * 0.3
            
            # Budget constraint consideration
            if context.budget_constraint:
                estimated_monthly_cost = self._estimate_monthly_cost(model, user_profile)
                if estimated_monthly_cost <= context.budget_constraint:
                    score += 0.2
                else:
                    score -= 0.3  # Penalize over-budget models
            
            recommendations[model.id] = max(0.0, min(1.0, score))
        
        return self._normalize_scores(recommendations)
    
    def _combine_recommendation_scores(self, algorithm_results: List[Tuple[Dict[str, float], float]]) -> Dict[str, float]:
        """Combine scores from different recommendation algorithms"""
        combined_scores = defaultdict(float)
        total_weight = sum(weight for _, weight in algorithm_results)
        
        for scores, weight in algorithm_results:
            normalized_weight = weight / total_weight
            for model_id, score in scores.items():
                combined_scores[model_id] += score * normalized_weight
        
        return dict(combined_scores)
    
    async def _generate_recommendation_explanation(self, user_profile: UserProfile,
                                                 context: RecommendationContext,
                                                 model: ModelInfo,
                                                 score: float) -> RecommendationExplanation:
        """Generate detailed explanation for recommendation"""
        
        primary_reasons = []
        
        # Analyze why this model was recommended
        if user_profile.preferred_providers.get(model.provider, 0) > 0.6:
            primary_reasons.append(f"You frequently use {model.provider} models")
        
        if user_profile.preferred_models.get(model.id, 0) > 0.6:
            primary_reasons.append("You've had positive experiences with this model")
        
        use_case_pref = user_profile.preferred_use_cases.get(context.use_case, 0)
        if use_case_pref > 0.5:
            primary_reasons.append(f"Optimized for {context.use_case} tasks you frequently perform")
        
        if model.input_cost == 0.0 and user_profile.cost_sensitivity > 0.7:
            primary_reasons.append("Free model aligns with your cost preferences")
        
        if model.performance_tier == "premium" and user_profile.performance_priority == "quality":
            primary_reasons.append("High-quality model matches your performance preferences")
        
        # Performance prediction
        performance_prediction = {
            "response_quality": min(0.9, score + 0.1),
            "response_speed": 0.8 if model.performance_tier == "fast" else 0.7,
            "reliability": 0.85,
            "cost_efficiency": 1.0 if model.input_cost == 0 else max(0.3, 1 - model.input_cost / 10)
        }
        
        # Cost analysis
        estimated_monthly_cost = self._estimate_monthly_cost(model, user_profile)
        cost_analysis = {
            "estimated_monthly_cost_usd": estimated_monthly_cost,
            "cost_tier": "free" if model.input_cost == 0 else "budget" if estimated_monthly_cost < 5 else "standard",
            "value_rating": "excellent" if estimated_monthly_cost < 10 else "good"
        }
        
        # Alternative suggestions
        alternatives = []
        if model.input_cost > 5.0:
            alternatives.append("Consider GPT-4o Mini for better cost efficiency")
        if not model.supports_function_calling and context.use_case == "coding":
            alternatives.append("Consider Claude 3.5 Sonnet for better coding support")
        
        # Potential issues
        potential_issues = []
        if model.context_length < 32000 and context.context_length_needed > 32000:
            potential_issues.append("Limited context length may affect long conversations")
        if not model.supports_vision and user_profile.vision_usage_frequency > 0.3:
            potential_issues.append("No vision support - consider multimodal alternatives")
        
        return RecommendationExplanation(
            primary_reasons=primary_reasons,
            performance_prediction=performance_prediction,
            cost_analysis=cost_analysis,
            alternatives=alternatives,
            confidence_score=score,
            potential_issues=potential_issues
        )
    
    async def _find_similar_users(self, user_profile: UserProfile) -> List[Tuple[str, float]]:
        """Find users with similar preferences"""
        similar_users = []
        
        # In a production system, this would query a database
        # For now, return mock similar users
        similar_users = [
            ("user_123", 0.85),
            ("user_456", 0.78),
            ("user_789", 0.72)
        ]
        
        return similar_users
    
    def _normalize_scores(self, scores: Dict[str, float]) -> Dict[str, float]:
        """Normalize scores to 0-1 range"""
        if not scores:
            return scores
        
        values = list(scores.values())
        min_val = min(values)
        max_val = max(values)
        
        if max_val == min_val:
            return {k: 0.5 for k in scores.keys()}
        
        return {
            model_id: (score - min_val) / (max_val - min_val)
            for model_id, score in scores.items()
        }
    
    def _get_recency_weight(self, timestamp: str) -> float:
        """Calculate recency weight for user data"""
        try:
            last_update = datetime.fromisoformat(timestamp)
            days_ago = (datetime.now() - last_update).days
            
            # Exponential decay: recent data has higher weight
            return math.exp(-days_ago / 30.0)  # Half-life of 30 days
        except:
            return 0.1  # Very low weight for invalid timestamps
    
    def _estimate_personalized_cost(self, user_profile: UserProfile, model: ModelInfo) -> str:
        """Estimate personalized cost based on user patterns"""
        if model.input_cost == 0.0:
            return "Free"
        
        # Estimate based on user's historical usage
        monthly_requests = max(user_profile.total_requests * 30 / 365, 100)  # Minimum 100/month
        avg_tokens_per_request = 750  # Reasonable estimate
        
        monthly_input_tokens = monthly_requests * avg_tokens_per_request
        monthly_output_tokens = monthly_requests * (avg_tokens_per_request * 0.3)  # 30% output ratio
        
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
    
    def _estimate_monthly_cost(self, model: ModelInfo, user_profile: UserProfile) -> float:
        """Estimate monthly cost for budget analysis"""
        if model.input_cost == 0.0:
            return 0.0
        
        monthly_requests = max(user_profile.total_requests * 30 / 365, 100)
        avg_tokens_per_request = 750
        
        monthly_input_tokens = monthly_requests * avg_tokens_per_request
        monthly_output_tokens = monthly_requests * (avg_tokens_per_request * 0.3)
        
        return (
            (monthly_input_tokens / 1_000_000) * model.input_cost +
            (monthly_output_tokens / 1_000_000) * model.output_cost
        )
    
    def _predict_use_cases(self, user_profile: UserProfile, model: ModelInfo) -> List[str]:
        """Predict suitable use cases for a model based on user patterns"""
        use_cases = []
        
        # Add user's frequent use cases if model is suitable
        for use_case, frequency in user_profile.preferred_use_cases.items():
            if frequency > 0.3:  # User frequently does this
                if use_case == "vision" and model.supports_vision:
                    use_cases.append("Image Analysis")
                elif use_case == "coding" and model.supports_function_calling:
                    use_cases.append("Code Generation")
                elif use_case == "chat":
                    use_cases.append("Conversations")
                elif use_case == "analysis" and model.context_length > 32000:
                    use_cases.append("Document Analysis")
        
        # Add general use cases based on model capabilities
        if model.supports_vision:
            use_cases.append("Visual Q&A")
        if model.supports_function_calling:
            use_cases.append("API Integration")
        if model.context_length > 50000:
            use_cases.append("Long Document Processing")
        
        return use_cases[:4]  # Limit to 4 use cases
    
    async def _update_user_profile_with_request(self, user_profile: UserProfile, 
                                              context: RecommendationContext) -> None:
        """Update user profile based on recommendation request"""
        
        # Update use case frequency
        current_freq = user_profile.preferred_use_cases.get(context.use_case, 0.0)
        user_profile.preferred_use_cases[context.use_case] = min(1.0, current_freq + 0.1)
        
        # Update feature usage patterns
        if "vision" in context.required_features:
            user_profile.vision_usage_frequency = min(1.0, user_profile.vision_usage_frequency + 0.1)
        
        if "function_calling" in context.required_features:
            user_profile.function_calling_frequency = min(1.0, user_profile.function_calling_frequency + 0.1)
        
        # Update context length needs
        if context.context_length_needed > 0:
            user_profile.context_length_needs.append(context.context_length_needed)
            # Keep only recent 20 context length requests
            user_profile.context_length_needs = user_profile.context_length_needs[-20:]
        
        # Update request count
        user_profile.total_requests += 1
        
        # Add to interaction history
        interaction = {
            "timestamp": datetime.now().isoformat(),
            "use_case": context.use_case,
            "context_length_needed": context.context_length_needed,
            "performance_requirement": context.performance_requirement,
            "required_features": context.required_features
        }
        
        user_profile.interaction_history.append(interaction)
        
        # Save updated profile
        await self.save_user_profile(user_profile)
    
    def _get_top_rated_models(self, user_profile: UserProfile) -> List[Tuple[str, float]]:
        """Get user's top rated models"""
        model_ratings = []
        
        for model_id, scores in user_profile.feedback_scores.items():
            if scores:
                avg_score = np.mean(scores)
                model_ratings.append((model_id, avg_score))
        
        return sorted(model_ratings, key=lambda x: x[1], reverse=True)[:5]
    
    def _calculate_model_loyalty(self, user_profile: UserProfile) -> float:
        """Calculate how loyal user is to specific models"""
        if not user_profile.preferred_models:
            return 0.0
        
        # Check if user heavily prefers a few models
        preferences = list(user_profile.preferred_models.values())
        if len(preferences) < 2:
            return 1.0
        
        # Calculate coefficient of variation
        mean_pref = np.mean(preferences)
        if mean_pref == 0:
            return 0.0
        
        std_pref = np.std(preferences)
        cv = std_pref / mean_pref
        
        # Higher CV means less loyalty (more diverse preferences)
        return max(0.0, 1.0 - cv)
    
    def _suggest_profile_improvements(self, user_profile: UserProfile) -> List[str]:
        """Suggest ways to improve user profile"""
        suggestions = []
        
        if user_profile.total_requests < 10:
            suggestions.append("Use the system more to get better personalized recommendations")
        
        if len(user_profile.feedback_scores) < 3:
            suggestions.append("Rate more models to help us understand your preferences")
        
        if user_profile.vision_usage_frequency == 0 and user_profile.function_calling_frequency == 0:
            suggestions.append("Try advanced features like vision or function calling")
        
        if user_profile.cost_sensitivity == 0.5:  # Default value
            suggestions.append("Set your cost preferences to get better budget-aligned recommendations")
        
        return suggestions
    
    def _analyze_cost_optimization_potential(self, user_profile: UserProfile) -> Dict[str, Any]:
        """Analyze potential for cost optimization"""
        # This would analyze user's model choices vs. cheaper alternatives
        return {
            "potential_monthly_savings": 15.50,
            "cheaper_alternatives_available": True,
            "optimization_suggestions": [
                "Consider GPT-4o Mini for routine tasks",
                "Use free models for simple queries"
            ]
        }
    
    def _suggest_new_features(self, user_profile: UserProfile) -> List[str]:
        """Suggest new features for user to try"""
        suggestions = []
        
        if user_profile.vision_usage_frequency < 0.1:
            suggestions.append("Try vision capabilities for image analysis")
        
        if user_profile.function_calling_frequency < 0.1:
            suggestions.append("Experiment with function calling for tool integration")
        
        if not any(length > 50000 for length in user_profile.context_length_needs):
            suggestions.append("Try models with larger context for document analysis")
        
        return suggestions
    
    def load_global_statistics(self) -> None:
        """Load global statistics from disk"""
        stats_file = self.analytics_dir / "global_stats.json"
        
        if stats_file.exists():
            try:
                with open(stats_file, 'r') as f:
                    data = json.load(f)
                    
                    # Convert defaultdicts back from regular dicts
                    self.global_stats["model_popularity"] = defaultdict(int, data.get("model_popularity", {}))
                    self.global_stats["model_satisfaction"] = defaultdict(list, data.get("model_satisfaction", {}))
                    self.global_stats["use_case_model_success"] = defaultdict(
                        lambda: defaultdict(list), 
                        {k: defaultdict(list, v) for k, v in data.get("use_case_model_success", {}).items()}
                    )
                    self.global_stats["provider_reliability"] = defaultdict(list, data.get("provider_reliability", {}))
                    
                    PrintStyle(color="green").print("✅ Loaded global statistics")
            except Exception as e:
                PrintStyle(color="yellow").print(f"⚠️ Could not load global statistics: {str(e)}")
    
    def save_global_statistics(self) -> None:
        """Save global statistics to disk"""
        stats_file = self.analytics_dir / "global_stats.json"
        
        try:
            # Convert defaultdicts to regular dicts for JSON serialization
            data = {
                "model_popularity": dict(self.global_stats["model_popularity"]),
                "model_satisfaction": dict(self.global_stats["model_satisfaction"]),
                "use_case_model_success": {
                    k: dict(v) for k, v in self.global_stats["use_case_model_success"].items()
                },
                "provider_reliability": dict(self.global_stats["provider_reliability"]),
                "last_updated": datetime.now().isoformat()
            }
            
            with open(stats_file, 'w') as f:
                json.dump(data, f, indent=2)
                
            PrintStyle(color="green").print("✅ Saved global statistics")
        except Exception as e:
            PrintStyle(color="red").print(f"❌ Could not save global statistics: {str(e)}")


# Global recommendation engine instance
recommendation_engine = IntelligentRecommendationEngine()


async def get_personalized_recommendations(user_id: str, 
                                         use_case: str,
                                         available_models: List[ModelInfo],
                                         **kwargs) -> List[Tuple[ModelRecommendation, RecommendationExplanation]]:
    """Get personalized model recommendations for a user"""
    
    context = RecommendationContext(
        use_case=use_case,
        budget_constraint=kwargs.get('budget_constraint'),
        performance_requirement=kwargs.get('performance_requirement', 'balanced'),
        required_features=kwargs.get('required_features', []),
        context_length_needed=kwargs.get('context_length_needed', 4000),
        real_time_requirement=kwargs.get('real_time_requirement', False),
        previous_models_tried=kwargs.get('previous_models_tried', [])
    )
    
    return await recommendation_engine.get_intelligent_recommendations(
        user_id, context, available_models, kwargs.get('max_recommendations', 5)
    )


async def record_model_feedback(user_id: str, model_id: str, 
                              satisfaction_score: float, feedback: Dict[str, Any]) -> None:
    """Record user feedback for model recommendations"""
    await recommendation_engine.record_user_feedback(user_id, model_id, satisfaction_score, feedback)


async def get_user_insights(user_id: str) -> Dict[str, Any]:
    """Get insights about user patterns and preferences"""
    return await recommendation_engine.analyze_user_patterns(user_id)