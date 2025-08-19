"""
Docker Multimedia Detector - Enhanced detection system for multimedia requests
Integrates Docker services with Pareng Boyong's automatic detection system
"""

import re
import logging
from typing import Dict, List, Tuple, Optional, Any
from .docker_multimedia_generator import docker_multimedia_generator

class DockerMultimediaDetector:
    """Advanced multimedia request detection with Docker service integration"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Enhanced detection patterns for multimedia requests
        self.image_patterns = [
            # English patterns
            r'\b(?:create|generate|make|draw|design|produce|render)\s+(?:an?|some?)\s+image\b',
            r'\b(?:create|generate|make|draw|design|produce|render)\s+(?:an?|some?)\s+(?:picture|photo|artwork|illustration)\b',
            r'\b(?:show me|give me|I need|I want)\s+(?:an?|some?)\s+(?:image|picture|photo|illustration)\b',
            r'\bgenerate.*?(?:image|picture|photo|visual|artwork)\b',
            r'\b(?:artistic|creative)\s+(?:image|picture|artwork|visual)\b',
            r'\bphotorealistic\s+(?:image|picture|render)\b',
            
            # Filipino patterns
            r'\b(?:gumawa|lumikha|mag-?generate)\s+ng\s+(?:larawan|litrato|artwork)\b',
            r'\b(?:gusto ko|kailangan ko)\s+ng\s+(?:larawan|litrato|picture)\b',
            r'\bmagandang\s+(?:larawan|tanawin|picture)\b'
        ]
        
        self.video_patterns = [
            # English patterns - Basic video
            r'\b(?:create|generate|make|produce|render)\s+(?:an?|some?)\s+video\b',
            r'\b(?:animate|animation)\b',
            r'\bmake.*?(?:video|animation|clip)\b',
            r'\bgenerate.*?(?:video|animation|clip)\b',
            
            # English patterns - Advanced video (trigger advanced_video_generator)
            r'\b(?:cinematic|film-?quality|professional|high-?quality)\s+video\b',
            r'\b(?:conversation|dialogue|characters?\s+(?:talking|discussing))\b',
            r'\bmulti-?character\s+(?:video|conversation|dialogue)\b',
            r'\b(?:dramatic|artistic|movie-?style)\s+video\b',
            r'\bcharacters?\s+(?:having\s+)?(?:conversation|dialogue|discussion)\b',
            
            # Filipino patterns
            r'\b(?:gumawa|lumikha)\s+ng\s+video\b',
            r'\b(?:mag-?animate|animation)\b',
            r'\bmagandang\s+video\b'
        ]
        
        self.audio_patterns = [
            # Music generation
            r'\b(?:create|generate|compose|make|produce)\s+(?:some?|an?)\s+(?:music|song|audio|soundtrack)\b',
            r'\b(?:musical|melodic|harmonic)\s+(?:composition|piece|track)\b',
            r'\bambient\s+(?:music|audio|sound)\b',
            r'\bupbeat\s+(?:music|song|track)\b',
            
            # Voiceover generation
            r'\b(?:voice-?over|voiceover|speak\s+this|say\s+this)\b',
            r'\b(?:filipino|tagalog)\s+(?:voice|pronunciation|speech)\b',
            r'\btext-?to-?speech\b',
            
            # Filipino patterns
            r'\b(?:gumawa|lumikha)\s+ng\s+(?:musika|kanta|tunog)\b',
            r'\bmagandang\s+(?:musika|kanta)\b',
            r'\b(?:kumanta|mag-?speak)\b'
        ]
        
        # Quality and model hints
        self.quality_indicators = {
            'high_quality': [
                r'\b(?:high-?quality|professional|studio-?quality|premium|best\s+quality)\b',
                r'\b(?:cinematic|film-?quality|movie-?style|professional)\b',
                r'\b(?:detailed|realistic|photorealistic)\b'
            ],
            'conversational': [
                r'\b(?:conversation|dialogue|characters?\s+talking|discussion)\b',
                r'\bmulti-?character\s+(?:conversation|dialogue)\b',
                r'\b(?:people|characters?)\s+(?:discussing|talking\s+about)\b'
            ],
            'fast_generation': [
                r'\b(?:quick|fast|rapid|speedy|50%\s+faster)\b',
                r'\b(?:low-?vram|6gb|older\s+gpu|accessible)\b'
            ]
        }
    
    def analyze_request(self, message: str) -> Dict[str, Any]:
        """Analyze message for multimedia content requests"""
        
        message_lower = message.lower()
        detected_types = []
        confidence_scores = {}
        suggestions = []
        
        # Check for image requests
        image_matches = self._check_patterns(message_lower, self.image_patterns)
        if image_matches:
            detected_types.append("image")
            confidence_scores["image"] = min(0.8 + len(image_matches) * 0.1, 0.95)
            suggestions.append({
                "type": "image",
                "tool": "generate_image_docker_tool",
                "confidence": confidence_scores["image"],
                "matches": image_matches
            })
        
        # Check for video requests
        video_matches = self._check_patterns(message_lower, self.video_patterns)
        if video_matches:
            detected_types.append("video")
            confidence_scores["video"] = min(0.8 + len(video_matches) * 0.1, 0.95)
            
            # Determine if advanced video generation is needed
            advanced_needed = self._check_advanced_video_requirements(message_lower)
            tool_name = "generate_video_docker_tool" if not advanced_needed else "advanced_video_generator"
            
            suggestions.append({
                "type": "video",
                "tool": tool_name,
                "confidence": confidence_scores["video"],
                "matches": video_matches,
                "advanced": advanced_needed
            })
        
        # Check for audio requests
        audio_matches = self._check_patterns(message_lower, self.audio_patterns)
        if audio_matches:
            detected_types.append("audio")
            confidence_scores["audio"] = min(0.8 + len(audio_matches) * 0.1, 0.95)
            
            # Determine if music or voiceover
            audio_type = "voiceover" if any("voice" in match or "speak" in match or "say" in match for match in audio_matches) else "music"
            
            suggestions.append({
                "type": "audio",
                "subtype": audio_type,
                "tool": "audio_voiceover" if audio_type == "voiceover" else "music_generator",
                "confidence": confidence_scores["audio"],
                "matches": audio_matches
            })
        
        # Calculate overall confidence
        overall_confidence = max(confidence_scores.values()) if confidence_scores else 0.0
        
        return {
            "detected": len(detected_types) > 0,
            "types": detected_types,
            "confidence_scores": confidence_scores,
            "overall_confidence": overall_confidence,
            "suggestions": suggestions,
            "should_activate": overall_confidence >= 0.6,  # Activation threshold
            "message_analysis": {
                "length": len(message),
                "has_multimedia_keywords": len(detected_types) > 0,
                "quality_hints": self._extract_quality_hints(message_lower)
            }
        }
    
    def _check_patterns(self, text: str, patterns: List[str]) -> List[str]:
        """Check text against list of regex patterns"""
        matches = []
        for pattern in patterns:
            if re.search(pattern, text, re.IGNORECASE):
                matches.append(pattern)
        return matches
    
    def _check_advanced_video_requirements(self, message_lower: str) -> bool:
        """Determine if advanced video generation is needed"""
        
        # Check for quality indicators
        quality_matches = self._check_patterns(message_lower, self.quality_indicators['high_quality'])
        conversation_matches = self._check_patterns(message_lower, self.quality_indicators['conversational'])
        
        return len(quality_matches) > 0 or len(conversation_matches) > 0
    
    def _extract_quality_hints(self, message_lower: str) -> Dict[str, List[str]]:
        """Extract quality and model hints from message"""
        hints = {}
        
        for hint_type, patterns in self.quality_indicators.items():
            matches = self._check_patterns(message_lower, patterns)
            if matches:
                hints[hint_type] = matches
        
        return hints
    
    async def auto_generate_if_detected(self, message: str, threshold: float = 0.7) -> Optional[Dict[str, Any]]:
        """Automatically generate content if high confidence detection"""
        
        analysis = self.analyze_request(message)
        
        if not analysis["should_activate"] or analysis["overall_confidence"] < threshold:
            return None
        
        # Get highest confidence suggestion
        best_suggestion = max(analysis["suggestions"], key=lambda x: x["confidence"])
        content_type = best_suggestion["type"]
        
        try:
            if content_type == "image":
                result = await docker_multimedia_generator.generate_multimedia_content(
                    prompt=message,
                    content_type="image"
                )
                
            elif content_type == "video":
                # Extract video-specific parameters
                quality_hints = analysis["message_analysis"]["quality_hints"]
                model = None
                
                if "conversational" in quality_hints:
                    model = "multitalk"
                elif "high_quality" in quality_hints:
                    model = "wan_vace_14b"  
                elif "fast_generation" in quality_hints:
                    model = "fusionix"
                
                result = await docker_multimedia_generator.generate_multimedia_content(
                    prompt=message,
                    content_type="video",
                    model=model
                )
            
            else:
                return None
            
            # Add detection metadata
            result["detection_info"] = {
                "auto_generated": True,
                "confidence": analysis["overall_confidence"],
                "detected_type": content_type,
                "suggestion_used": best_suggestion
            }
            
            return result
            
        except Exception as e:
            self.logger.error(f"Auto-generation error: {e}")
            return {
                "status": "error",
                "message": f"Auto-generation failed: {str(e)}",
                "detection_info": analysis
            }
    
    def generate_suggestions_text(self, analysis: Dict[str, Any]) -> str:
        """Generate human-readable suggestions based on detection analysis"""
        
        if not analysis["detected"]:
            return ""
        
        suggestions_text = "🎨 **Multimedia Content Detected!**\n\n"
        
        for suggestion in analysis["suggestions"]:
            content_type = suggestion["type"]
            confidence = suggestion["confidence"]
            tool = suggestion["tool"]
            
            suggestions_text += f"• **{content_type.title()}** (Confidence: {confidence:.1%})\n"
            suggestions_text += f"  - Tool: `{tool}`\n"
            
            if content_type == "video" and suggestion.get("advanced"):
                suggestions_text += f"  - ⭐ Advanced generation recommended for high-quality output\n"
            
            suggestions_text += "\n"
        
        if analysis["overall_confidence"] >= 0.7:
            suggestions_text += "💡 **High confidence detected - content can be auto-generated!**\n"
        elif analysis["overall_confidence"] >= 0.6:
            suggestions_text += "🤔 **Moderate confidence - consider using suggested tools**\n"
        
        return suggestions_text

# Global detector instance
docker_multimedia_detector = DockerMultimediaDetector()

def detect_multimedia_request(message: str) -> Dict[str, Any]:
    """
    Agent Zero tool for detecting multimedia requests in messages
    
    Args:
        message: User message to analyze
    
    Returns:
        Dict with detection results, confidence scores, and suggestions
    """
    return docker_multimedia_detector.analyze_request(message)

def auto_generate_multimedia(message: str, threshold: float = 0.7) -> Optional[Dict[str, Any]]:
    """
    Agent Zero tool for automatically generating multimedia content based on detection
    
    Args:
        message: User message to analyze and potentially generate content for
        threshold: Confidence threshold for auto-generation (default: 0.7)
    
    Returns:
        Generation result if auto-generated, None otherwise
    """
    import asyncio
    return asyncio.run(
        docker_multimedia_detector.auto_generate_if_detected(message, threshold)
    )

# Export tools
__all__ = [
    'detect_multimedia_request',
    'auto_generate_multimedia', 
    'docker_multimedia_detector'
]