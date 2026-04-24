from abc import ABC, abstractmethod
import random
from .models import MatchMetadata, EnforcementCategory

class AIRatingAdapter(ABC):
    @abstractmethod
    def analyze_context(self, match: MatchMetadata) -> dict:
        pass

class MockGeminiAdapter(AIRatingAdapter):
    """
    High-fidelity mock for Gemini AI. 
    Simulates deep analysis of content context, parody detection, and commercial intent.
    """
    def analyze_context(self, match: MatchMetadata) -> dict:
        # Simulate AI "thinking"
        is_parody = match.transformation_index < 0.4
        is_news = "news" in match.match_id.lower()
        
        # High-fidelity mock logic
        ai_recommendation = "MONETIZE"
        if match.match_confidence > 0.9 and match.transformation_index > 0.8:
            ai_recommendation = "TAKEDOWN"
        elif is_parody or is_news:
            ai_recommendation = "MONITOR"
            
        return {
            "model": "gemini-1.5-pro-mock",
            "reasoning": f"Analyzed match {match.match_id}. Transformation index {match.match_index if hasattr(match, 'match_index') else match.transformation_index} suggests {'high' if not is_parody else 'low'} risk.",
            "parody_probability": 0.8 if is_parody else 0.1,
            "commercial_intent": "high" if match.is_commercial else "low",
            "suggested_action": ai_recommendation
        }

class DecisionEngine:
    def __init__(self, ai_adapter: AIRatingAdapter):
        self.ai_adapter = ai_adapter

    def calculate_severity_score(self, match: MatchMetadata) -> float:
        """
        ASS = (MatchConfidence * 0.4) + (VelocityNorm * 0.25) + (ReputationInv * 0.2) + (Transformation * 0.15)
        """
        # Simple velocity normalization (e.g., 1000 views/hr is 1.0)
        velocity_norm = min(match.view_velocity / 1000.0, 1.0)
        reputation_inv = 1.0 - match.uploader_reputation
        
        score = (match.match_confidence * 0.4) + \
                (velocity_norm * 0.25) + \
                (reputation_inv * 0.2) + \
                (match.transformation_index * 0.15)
        
        return round(score, 4)

    def classify(self, match: MatchMetadata) -> tuple[EnforcementCategory, float, dict]:
        score = self.calculate_severity_score(match)
        ai_analysis = self.ai_adapter.analyze_context(match)
        
        # Merge ASS score with AI recommendation
        if score > 0.85:
            category = EnforcementCategory.TAKEDOWN
        elif score > 0.60:
            category = EnforcementCategory.MONETIZE
        elif score > 0.40:
            category = EnforcementCategory.LICENSE
        else:
            category = EnforcementCategory.MONITOR
            
        # AI Override for Safe Harbor / Fair Use
        if ai_analysis["suggested_action"] == "MONITOR" and score < 0.70:
            category = EnforcementCategory.MONITOR
            
        return category, score, ai_analysis
