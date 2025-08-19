"""
Pareng Boyong Capability Advisor
Intelligent tool recommendation system with cost optimization
"""

import re
import os
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
import json

class CapabilityAdvisor:
    """
    Intelligent advisor for Pareng Boyong tool selection
    Always prioritizes FREE and lowest-cost options
    """
    
    def __init__(self):
        self.tool_catalog = self._initialize_tool_catalog()
        self.cost_tracking = {"daily_total": 0.0, "monthly_total": 0.0}
        self.quality_keywords = self._initialize_quality_keywords()
        self.use_case_patterns = self._initialize_use_case_patterns()
        
    def _initialize_tool_catalog(self) -> Dict[str, Any]:
        """Initialize the complete tool catalog with priorities and capabilities"""
        return {
            "video_generation": {
                "primary": {
                    "tool": "cost_optimized_video_generator",
                    "file": "python/tools/cost_optimized_video_generator.py",
                    "priority": 1,
                    "cost_range": [0.00, 0.01],
                    "capabilities": [
                        "FREE local ComfyUI (AnimateDiff)",
                        "FREE HuggingFace Spaces", 
                        "FREE fal.ai tier",
                        "Low-cost Replicate fallback"
                    ],
                    "when_to_use": "ALWAYS use first for ANY video request",
                    "quality": "medium-high",
                    "speed": "fast-medium"
                },
                "secondary": {
                    "tool": "trending_video_generator", 
                    "file": "python/tools/trending_video_generator.py",
                    "priority": 2,
                    "cost_range": [0.01, 0.05],
                    "capabilities": [
                        "CogVideoX-2B (VPS-friendly)",
                        "Stable Video Diffusion (image-to-video)",
                        "Open-Sora 1.3 (highest quality)",
                        "AnimateDiff integration"
                    ],
                    "when_to_use": "When cost-optimized unavailable or specific models needed",
                    "quality": "high",
                    "speed": "medium"
                },
                "tertiary": {
                    "tool": "advanced_video_generator",
                    "file": "python/tools/advanced_video_generator.py", 
                    "priority": 3,
                    "cost_range": [0.02, 0.10],
                    "capabilities": [
                        "Wan2.1-VACE-14B (14B parameters)",
                        "FusioniX (50% faster, cinematic)",
                        "MultiTalk (conversational, lip-sync)",
                        "Wan2GP (low-VRAM optimization)"
                    ],
                    "when_to_use": "Professional quality or specialized models only",
                    "quality": "very_high",
                    "speed": "slow-medium"
                },
                "fallback": {
                    "tool": "simple_video_generator",
                    "file": "python/tools/simple_video_generator.py",
                    "priority": 4,
                    "cost_range": [0.01, 0.03],
                    "capabilities": ["ZeroScope V2", "Basic cloud APIs"],
                    "when_to_use": "Backup when other services fail",
                    "quality": "medium",
                    "speed": "fast"
                }
            },
            "image_generation": {
                "primary": {
                    "tool": "imagen4_generator",
                    "file": "python/tools/imagen4_generator.py",
                    "priority": 1,
                    "cost_range": [0.002, 0.01],
                    "capabilities": [
                        "Google Imagen 4 Fast (10x faster)",
                        "Up to 2K resolution", 
                        "Multiple aspect ratios",
                        "Enhanced text rendering",
                        "Professional quality"
                    ],
                    "when_to_use": "ALWAYS use first for ANY image request",
                    "quality": "very_high",
                    "speed": "very_fast"
                },
                "fallback": {
                    "tool": "multimedia_generator",
                    "file": "python/tools/multimedia_generator.py",
                    "priority": 2,
                    "cost_range": [0.00, 0.02],
                    "capabilities": ["ComfyUI FLUX.1", "SVG placeholders"],
                    "when_to_use": "When Imagen 4 fails or unavailable",
                    "quality": "medium-high",
                    "speed": "medium"
                }
            },
            "audio_generation": {
                "primary": {
                    "tool": "multimedia_generator",
                    "file": "python/tools/multimedia_generator.py", 
                    "priority": 1,
                    "cost_range": [0.00, 0.05],
                    "capabilities": [
                        "Filipino TTS (Toucan TTS)",
                        "Music generation (Bark, AudioCraft)",
                        "Voiceovers (multiple languages)",
                        "HTML audio placeholders"
                    ],
                    "when_to_use": "All audio generation requests",
                    "quality": "medium-high", 
                    "speed": "medium"
                }
            },
            "system_tools": {
                "system_self_awareness": {
                    "tool": "system_self_awareness",
                    "file": "python/tools/system_self_awareness.py",
                    "priority": 0,  # Critical - check before major operations
                    "cost_range": [0.00, 0.00],
                    "capabilities": [
                        "Risk assessment",
                        "System health monitoring", 
                        "Resource usage tracking",
                        "Recovery recommendations"
                    ],
                    "when_to_use": "CRITICAL - Before any major system operations",
                    "quality": "essential",
                    "speed": "instant"
                },
                "enhanced_ui_renderer": {
                    "tool": "enhanced_ui_renderer",
                    "file": "python/tools/enhanced_ui_renderer.py",
                    "priority": 1,
                    "cost_range": [0.00, 0.00],
                    "capabilities": [
                        "React-style components",
                        "Shadcn UI elements", 
                        "Interactive dashboards",
                        "Professional HTML/CSS/JS"
                    ],
                    "when_to_use": "Rich responses and dashboard creation",
                    "quality": "high",
                    "speed": "fast"
                },
                "env_loader": {
                    "tool": "env_loader",
                    "file": "python/tools/env_loader.py",
                    "priority": 0,  # Foundational
                    "cost_range": [0.00, 0.00],
                    "capabilities": [
                        "Centralized .env management",
                        "API key validation",
                        "Service configuration"
                    ],
                    "when_to_use": "FOUNDATIONAL - Required by all tools",
                    "quality": "essential",
                    "speed": "instant"
                }
            }
        }
    
    def _initialize_quality_keywords(self) -> Dict[str, List[str]]:
        """Initialize quality requirement detection keywords"""
        return {
            "free_preferred": [
                "quick", "test", "draft", "concept", "try", "experiment",
                "sample", "demo", "prototype", "rough", "basic"
            ],
            "standard": [
                "social media", "instagram", "facebook", "twitter", "presentation", 
                "blog", "post", "story", "content", "share"
            ],
            "high_quality": [
                "professional", "client", "commercial", "marketing", "business",
                "portfolio", "showcase", "premium", "quality", "polished"
            ],
            "premium": [
                "broadcast", "film", "cinema", "enterprise", "corporate",
                "high-end", "luxury", "flagship", "signature", "masterpiece"
            ]
        }
    
    def _initialize_use_case_patterns(self) -> Dict[str, Dict[str, Any]]:
        """Initialize use case pattern matching"""
        return {
            "video": {
                "conversational": {
                    "patterns": ["conversation", "dialogue", "talk", "speak", "chat", "interview", "discussion"],
                    "recommended_tool": "advanced_video_generator",
                    "model_preference": "multitalk",
                    "reason": "Requires specialized lip-sync and multi-character support"
                },
                "cinematic": {
                    "patterns": ["cinematic", "film", "movie", "dramatic", "epic", "professional", "commercial"],
                    "recommended_tool": "cost_optimized_video_generator",  # Try FREE first
                    "escalation": "advanced_video_generator",
                    "model_preference": "fusionix",
                    "reason": "Cinematic quality can often be achieved with FREE services first"
                },
                "image_animation": {
                    "patterns": ["animate", "image to video", "bring to life", "movement", "motion"],
                    "recommended_tool": "cost_optimized_video_generator",
                    "model_preference": "stable-video-diffusion",
                    "reason": "Image-to-video is well supported by FREE services"
                },
                "quick_content": {
                    "patterns": ["quick", "fast", "simple", "basic", "social media"],
                    "recommended_tool": "cost_optimized_video_generator",
                    "force_free": True,
                    "reason": "Basic content should always use FREE services"
                }
            },
            "image": {
                "social_media": {
                    "patterns": ["instagram", "facebook", "twitter", "linkedin", "social", "post"],
                    "recommended_tool": "imagen4_generator",
                    "aspect_ratio": "1:1",
                    "reason": "Social media optimized aspect ratio"
                },
                "professional": {
                    "patterns": ["professional", "business", "corporate", "presentation", "marketing"],
                    "recommended_tool": "imagen4_generator", 
                    "aspect_ratio": "16:9",
                    "style": "professional",
                    "reason": "Professional contexts benefit from high-quality generation"
                },
                "portrait": {
                    "patterns": ["portrait", "person", "face", "character", "headshot", "profile"],
                    "recommended_tool": "imagen4_generator",
                    "aspect_ratio": "3:4",
                    "category": "portraits",
                    "reason": "Portrait aspect ratio and specialized handling"
                }
            }
        }
    
    def analyze_request(self, request: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Analyze user request and provide intelligent tool recommendations
        
        Args:
            request: User's request text
            context: Additional context (budget, quality requirements, etc.)
            
        Returns:
            Dict containing recommendations, cost analysis, and reasoning
        """
        if context is None:
            context = {}
            
        request_lower = request.lower()
        
        # Detect content type
        content_type = self._detect_content_type(request_lower)
        
        # Detect quality requirements  
        quality_level = self._detect_quality_level(request_lower, context)
        
        # Detect use case patterns
        use_case = self._detect_use_case_patterns(request_lower, content_type)
        
        # Get tool recommendations
        recommendations = self._get_tool_recommendations(
            content_type, quality_level, use_case, context
        )
        
        # Cost analysis
        cost_analysis = self._analyze_costs(recommendations, context)
        
        # Generate reasoning
        reasoning = self._generate_reasoning(
            content_type, quality_level, use_case, recommendations
        )
        
        return {
            "content_type": content_type,
            "quality_level": quality_level,
            "use_case": use_case,
            "recommendations": recommendations,
            "cost_analysis": cost_analysis,
            "reasoning": reasoning,
            "timestamp": datetime.now().isoformat()
        }
    
    def _detect_content_type(self, request: str) -> str:
        """Detect the type of content being requested"""
        
        video_keywords = [
            "video", "animation", "movie", "clip", "footage", "cinematic",
            "animate", "motion", "movement", "film", "scene"
        ]
        
        image_keywords = [
            "image", "picture", "photo", "drawing", "artwork", "illustration",
            "portrait", "landscape", "design", "graphic", "visual"
        ]
        
        audio_keywords = [
            "audio", "voice", "sound", "music", "speech", "talk", "voiceover",
            "narration", "tts", "text to speech", "filipino", "tagalog"
        ]
        
        # Count keyword matches
        video_score = sum(1 for keyword in video_keywords if keyword in request)
        image_score = sum(1 for keyword in image_keywords if keyword in request)
        audio_score = sum(1 for keyword in audio_keywords if keyword in request)
        
        # Determine type based on highest score
        if video_score > image_score and video_score > audio_score:
            return "video"
        elif image_score > audio_score:
            return "image" 
        elif audio_score > 0:
            return "audio"
        else:
            # Default heuristics
            if any(word in request for word in ["generate", "create", "make"]):
                if any(word in request for word in ["moving", "sequence", "story"]):
                    return "video"
                else:
                    return "image"
            return "image"  # Default fallback
    
    def _detect_quality_level(self, request: str, context: Dict[str, Any]) -> str:
        """Detect quality requirements from request and context"""
        
        # Check context first
        if context.get("quality"):
            return context["quality"]
        
        if context.get("budget"):
            budget = context["budget"]
            if budget == 0:
                return "free_preferred"
            elif budget < 0.02:
                return "standard"
            elif budget < 0.05:
                return "high_quality"
            else:
                return "premium"
        
        # Analyze request text
        for quality, keywords in self.quality_keywords.items():
            if any(keyword in request for keyword in keywords):
                return quality
        
        return "standard"  # Default
    
    def _detect_use_case_patterns(self, request: str, content_type: str) -> Optional[str]:
        """Detect specific use case patterns"""
        
        if content_type in self.use_case_patterns:
            for use_case, config in self.use_case_patterns[content_type].items():
                if any(pattern in request for pattern in config["patterns"]):
                    return use_case
        
        return None
    
    def _get_tool_recommendations(
        self, 
        content_type: str, 
        quality_level: str, 
        use_case: Optional[str],
        context: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Get prioritized tool recommendations"""
        
        recommendations = []
        
        if content_type in self.tool_catalog:
            tools = self.tool_catalog[content_type]
            
            # Special handling for use case patterns
            if use_case and use_case in self.use_case_patterns.get(content_type, {}):
                pattern_config = self.use_case_patterns[content_type][use_case]
                
                # Check if we should force FREE for certain use cases
                if pattern_config.get("force_free"):
                    primary_tool = tools["primary"].copy()
                    primary_tool["force_free"] = True
                    primary_tool["reason"] = pattern_config["reason"]
                    recommendations.append(primary_tool)
                    return recommendations
                
                # Check if pattern recommends specific tool
                recommended_tool = pattern_config.get("recommended_tool", "").replace("_generator", "")
                escalation_tool = pattern_config.get("escalation", "").replace("_generator", "")
                
                # For cost optimization, always try primary first
                if content_type == "video":
                    primary_tool = tools["primary"].copy()
                    primary_tool["reason"] = "Always try FREE options first, even for specialized requests"
                    if "model_preference" in pattern_config:
                        primary_tool["model_preference"] = pattern_config["model_preference"]
                    recommendations.append(primary_tool)
                    
                    # Add escalation if different from primary
                    if escalation_tool and escalation_tool not in ["cost_optimized"]:
                        for tier_name, tier_config in tools.items():
                            if escalation_tool in tier_config["tool"]:
                                escalation = tier_config.copy()
                                escalation["reason"] = f"Escalation for {use_case}: {pattern_config['reason']}"
                                if "model_preference" in pattern_config:
                                    escalation["model_preference"] = pattern_config["model_preference"]
                                recommendations.append(escalation)
                                break
                else:
                    # For images and audio, use primary recommendation
                    primary_tool = tools["primary"].copy()
                    primary_tool["reason"] = pattern_config["reason"]
                    recommendations.append(primary_tool)
            else:
                # Standard priority-based recommendations
                sorted_tools = sorted(
                    tools.items(), 
                    key=lambda x: x[1]["priority"]
                )
                
                for tier_name, tool_config in sorted_tools:
                    tool_rec = tool_config.copy()
                    tool_rec["tier"] = tier_name
                    
                    # Quality-based filtering
                    if quality_level == "free_preferred":
                        if tool_config["cost_range"][0] == 0.00:
                            tool_rec["reason"] = "FREE service preferred by user"
                            recommendations.append(tool_rec)
                    elif quality_level == "premium":
                        if tier_name in ["tertiary", "primary"]:
                            tool_rec["reason"] = f"Premium quality requirement - {tier_name} tier"
                            recommendations.append(tool_rec)
                    else:
                        tool_rec["reason"] = f"Standard recommendation - {tier_name} tier"
                        recommendations.append(tool_rec)
                
                # Ensure we always have at least the primary recommendation
                if not recommendations and "primary" in tools:
                    primary = tools["primary"].copy()
                    primary["tier"] = "primary" 
                    primary["reason"] = "Default primary recommendation"
                    recommendations.append(primary)
        
        return recommendations
    
    def _analyze_costs(
        self, 
        recommendations: List[Dict[str, Any]], 
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Analyze costs for recommendations"""
        
        total_estimated_cost = 0.0
        cost_breakdown = []
        savings_analysis = {}
        
        for rec in recommendations:
            cost_range = rec["cost_range"]
            estimated_cost = (cost_range[0] + cost_range[1]) / 2
            
            cost_breakdown.append({
                "tool": rec["tool"],
                "estimated_cost": estimated_cost,
                "cost_range": cost_range,
                "priority": rec["priority"]
            })
            
            if rec["priority"] == 1:  # Primary recommendation
                total_estimated_cost = estimated_cost
        
        # Calculate potential savings
        if recommendations:
            primary_cost = cost_breakdown[0]["estimated_cost"]
            premium_baseline = 0.05  # Typical premium service cost
            
            savings_analysis = {
                "estimated_primary_cost": primary_cost,
                "premium_baseline": premium_baseline,
                "estimated_savings": max(0, premium_baseline - primary_cost),
                "savings_percentage": max(0, (premium_baseline - primary_cost) / premium_baseline * 100)
            }
        
        return {
            "total_estimated_cost": total_estimated_cost,
            "cost_breakdown": cost_breakdown,
            "savings_analysis": savings_analysis,
            "budget_status": self._check_budget_status(total_estimated_cost, context)
        }
    
    def _check_budget_status(self, estimated_cost: float, context: Dict[str, Any]) -> str:
        """Check if estimated cost fits within budget constraints"""
        
        budget = context.get("budget")
        if budget is None:
            if estimated_cost == 0.0:
                return "FREE - No budget concerns"
            elif estimated_cost < 0.01:
                return "Very low cost - Acceptable"
            elif estimated_cost < 0.05:
                return "Low cost - Should be acceptable"
            else:
                return "Higher cost - Consider alternatives"
        
        if estimated_cost <= budget:
            return f"Within budget (${budget:.3f})"
        else:
            return f"Exceeds budget by ${estimated_cost - budget:.3f}"
    
    def _generate_reasoning(
        self,
        content_type: str,
        quality_level: str, 
        use_case: Optional[str],
        recommendations: List[Dict[str, Any]]
    ) -> str:
        """Generate human-readable reasoning for recommendations"""
        
        reasoning_parts = []
        
        # Content type reasoning
        reasoning_parts.append(f"Detected content type: {content_type}")
        
        # Quality level reasoning
        quality_explanations = {
            "free_preferred": "User prefers FREE options - prioritizing zero-cost services",
            "standard": "Standard quality requirements - balancing cost and quality",
            "high_quality": "High quality requirements - willing to use paid services for better results",
            "premium": "Premium quality requirements - cost less important than quality"
        }
        reasoning_parts.append(quality_explanations.get(quality_level, f"Quality level: {quality_level}"))
        
        # Use case reasoning
        if use_case:
            reasoning_parts.append(f"Specialized use case detected: {use_case}")
        
        # Primary recommendation reasoning
        if recommendations:
            primary = recommendations[0]
            reasoning_parts.append(f"Primary recommendation: {primary['tool']} - {primary.get('reason', 'Best fit for requirements')}")
            
            # Cost optimization note
            if primary["cost_range"][0] == 0.00:
                reasoning_parts.append("🆓 FREE service available - maximum cost savings!")
            elif primary["cost_range"][1] < 0.02:
                reasoning_parts.append("💸 Low-cost option - good balance of cost and quality")
        
        return " | ".join(reasoning_parts)
    
    def get_tool_parameters(
        self, 
        tool_name: str, 
        request: str, 
        recommendations: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate optimal parameters for the selected tool"""
        
        params = {}
        request_lower = request.lower()
        content_type = recommendations.get("content_type", "")
        use_case = recommendations.get("use_case")
        
        if "video" in tool_name:
            params.update({
                "prompt": request,
                "duration": 3,  # Conservative default for cost
                "fps": 8,       # Conservative default for cost
                "resolution": "720p",
                "style": "cinematic"
            })
            
            # Use case specific parameters
            if use_case == "conversational":
                params.update({
                    "video_type": "conversational",
                    "audio_sync": True,
                    "characters": ["Speaker 1", "Speaker 2"]
                })
            elif use_case == "cinematic":
                params.update({
                    "style": "cinematic",
                    "quality": "high"
                })
            
            # Quality-based adjustments
            quality_level = recommendations.get("quality_level", "standard")
            if quality_level == "free_preferred":
                params["force_free"] = True
                params["max_cost"] = 0.00
            elif quality_level == "premium":
                params["duration"] = 5
                params["fps"] = 24
                params["resolution"] = "1080p"
                params["max_cost"] = 0.10
            else:
                params["max_cost"] = 0.02
            
            # Model preference from recommendations
            for rec in recommendations.get("recommendations", []):
                if "model_preference" in rec:
                    params["model"] = rec["model_preference"]
                    break
        
        elif "image" in tool_name or tool_name == "imagen4_generator":
            params.update({
                "prompt": request,
                "output_format": "jpg",
                "safety_filter_level": "block_medium_and_above"
            })
            
            # Aspect ratio detection
            if any(word in request_lower for word in ["social media", "instagram", "square"]):
                params["aspect_ratio"] = "1:1"
            elif any(word in request_lower for word in ["widescreen", "landscape", "banner"]):
                params["aspect_ratio"] = "16:9"
            elif any(word in request_lower for word in ["portrait", "vertical", "story"]):
                params["aspect_ratio"] = "3:4"
            else:
                params["aspect_ratio"] = "1:1"  # Default
            
            # Style detection
            if any(word in request_lower for word in ["professional", "business"]):
                params["style"] = "professional"
            elif any(word in request_lower for word in ["artistic", "creative", "art"]):
                params["style"] = "artistic"
            else:
                params["style"] = "realistic"
        
        elif "audio" in tool_name or "multimedia" in tool_name:
            params.update({
                "text": request,
                "voice_type": "filipino" if any(word in request_lower for word in ["filipino", "tagalog"]) else "english",
                "audio_type": "music" if any(word in request_lower for word in ["music", "song"]) else "voiceover"
            })
        
        return params
    
    def suggest_cost_optimization(self, analysis: Dict[str, Any]) -> List[str]:
        """Suggest ways to optimize costs based on the analysis"""
        
        suggestions = []
        cost_analysis = analysis.get("cost_analysis", {})
        estimated_cost = cost_analysis.get("total_estimated_cost", 0)
        
        if estimated_cost == 0.0:
            suggestions.append("🆓 Excellent! This will use FREE services with no cost.")
        elif estimated_cost < 0.01:
            suggestions.append("💰 Very cost-effective option - minimal spending required.")
        else:
            suggestions.extend([
                "💡 To reduce costs, consider:",
                "  • Shorter video duration (3 seconds vs 5+)",
                "  • Lower resolution (720p vs 1080p)", 
                "  • Simpler prompts for better FREE service compatibility",
                "  • Try FREE services first before paid alternatives"
            ])
        
        # Quality-based suggestions
        quality_level = analysis.get("quality_level", "")
        if quality_level == "premium" and estimated_cost > 0.05:
            suggestions.append("⚠️ Premium quality will incur higher costs - consider if necessary for your use case.")
        
        return suggestions
    
    def format_recommendation_response(self, analysis: Dict[str, Any]) -> str:
        """Format the analysis into a user-friendly response"""
        
        recommendations = analysis.get("recommendations", [])
        if not recommendations:
            return "❌ No recommendations available for this request."
        
        primary = recommendations[0]
        cost_analysis = analysis.get("cost_analysis", {})
        
        response = f"""
# 🧠 **Pareng Boyong Intelligence Recommendation**

## 🎯 **Optimal Tool Selection**
**Primary Tool**: `{primary['tool']}`
**Reasoning**: {primary.get('reason', 'Best fit for your requirements')}

## 💰 **Cost Analysis**
**Estimated Cost**: ${cost_analysis.get('total_estimated_cost', 0):.3f}
**Cost Range**: ${primary['cost_range'][0]:.3f} - ${primary['cost_range'][1]:.3f}
**Budget Status**: {cost_analysis.get('budget_status', 'No budget specified')}

## 🎨 **Capabilities**
{chr(10).join(f'• {cap}' for cap in primary.get('capabilities', []))}

## 📊 **Quality vs Cost**
**Quality Level**: {analysis.get('quality_level', 'standard').replace('_', ' ').title()}
**Speed**: {primary.get('speed', 'medium').title()}
**Quality**: {primary.get('quality', 'high').replace('_', ' ').title()}

## 💡 **Cost Optimization Tips**
{chr(10).join(self.suggest_cost_optimization(analysis))}

## 🔄 **Fallback Options**
{chr(10).join(f'• {rec["tool"]} (${rec["cost_range"][0]:.3f}-${rec["cost_range"][1]:.3f})' for rec in recommendations[1:3]) if len(recommendations) > 1 else '• No fallback needed - primary option is reliable'}

**Analysis Generated**: {analysis.get('timestamp', datetime.now().isoformat())}
"""
        
        return response.strip()


# Convenience functions for easy importing
_advisor = None

def get_advisor() -> CapabilityAdvisor:
    """Get global advisor instance"""
    global _advisor
    if _advisor is None:
        _advisor = CapabilityAdvisor()
    return _advisor

def analyze_request(request: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
    """Quick analysis function"""
    return get_advisor().analyze_request(request, context)

def recommend_tool(request: str, context: Dict[str, Any] = None) -> str:
    """Get formatted recommendation for a request"""
    analysis = analyze_request(request, context)
    return get_advisor().format_recommendation_response(analysis)

def get_tool_parameters(tool_name: str, request: str, analysis: Dict[str, Any]) -> Dict[str, Any]:
    """Get optimal parameters for a tool"""
    return get_advisor().get_tool_parameters(tool_name, request, analysis)


if __name__ == "__main__":
    # Test the capability advisor
    advisor = CapabilityAdvisor()
    
    test_requests = [
        "Create a video of a cat walking in a garden",
        "Generate a professional product showcase video", 
        "I need an image for my Instagram post",
        "Create a conversation between two characters",
        "Quick test video of a landscape"
    ]
    
    print("🧠 **Pareng Boyong Capability Advisor Test**\n")
    
    for i, request in enumerate(test_requests, 1):
        print(f"## Test {i}: \"{request}\"")
        analysis = advisor.analyze_request(request)
        response = advisor.format_recommendation_response(analysis)
        print(response)
        print("\n" + "="*50 + "\n")