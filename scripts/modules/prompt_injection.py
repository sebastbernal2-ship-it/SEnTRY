"""
Prompt Injection & Text Manipulation Detection Module
Uses NLP-based scoring for manipulative language in agent communications.
"""
import random
import re
from datetime import datetime, timezone
from typing import Dict, Any, List

from ..utils.scoring import score_to_label, score_to_severity
from ..utils.io import get_utc_now


# Keyword patterns for manipulation detection
MANIPULATION_KEYWORDS = {
    "urgency": ["NOW", "IMMEDIATELY", "URGENT", "ASAP", "tonight", "expires in"],
    "guaranteed": ["GUARANTEED", "guaranteed", "PROMISE", "100% profit", "risk-free"],
    "fomo": ["act NOW before", "last chance", "limited time", "only for you"],
    "pressure": ["Don't miss", "Better act fast", "Everyone is doing it", "Your friends already"],
}

CLEAN_KEYWORDS = [
    "swap",
    "rebalance",
    "market rate",
    "per your strategy",
    "defined strategy",
]


class PromptInjectionDetector:
    """Detects manipulative language and prompt injection attempts in text."""

    def __init__(self):
        """Initialize detector."""
        pass

    def _count_keyword_matches(self, text: str, keywords: List[str]) -> int:
        """Count how many keywords appear in text."""
        count = 0
        text_lower = text.lower()
        for keyword in keywords:
            if keyword.lower() in text_lower:
                count += 1
        return count

    def _check_for_manipulation_patterns(self, text: str) -> float:
        """
        Analyze text for manipulation patterns.
        Returns a partial score based on keyword presence.
        
        Args:
            text: Message text to analyze
        
        Returns:
            Partial score (0-80) based on manipulation patterns
        """
        text_lower = text.lower()
        score = 0.0
        
        # Check urgency patterns (up to 20 points)
        urgency_matches = self._count_keyword_matches(text, MANIPULATION_KEYWORDS["urgency"])
        score += min(urgency_matches * 10, 20)
        
        # Check guaranteed claims (up to 25 points)
        guarantee_matches = self._count_keyword_matches(text, MANIPULATION_KEYWORDS["guaranteed"])
        score += min(guarantee_matches * 15, 25)
        
        # Check FOMO patterns (up to 20 points)
        fomo_matches = self._count_keyword_matches(text, MANIPULATION_KEYWORDS["fomo"])
        score += min(fomo_matches * 12, 20)
        
        # Check pressure tactics (up to 15 points)
        pressure_matches = self._count_keyword_matches(text, MANIPULATION_KEYWORDS["pressure"])
        score += min(pressure_matches * 8, 15)
        
        return min(score, 80.0)

    def _check_for_clean_patterns(self, text: str) -> float:
        """
        Check if text contains clean/legitimate patterns.
        Returns a reduction to score if found.
        
        Args:
            text: Message text to analyze
        
        Returns:
            Reduction to apply (0-30)
        """
        clean_matches = self._count_keyword_matches(text, CLEAN_KEYWORDS)
        return min(clean_matches * 10, 30)

    def score_message(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """
        Score a message for manipulation risk.
        
        Args:
            message: Message dict with 'id' and 'preview' or 'text' fields
        
        Returns:
            Scoring result with score, label, etc.
        """
        text = message.get("text") or message.get("preview") or ""
        
        # Base scoring on manipulation patterns
        manipulation_score = self._check_for_manipulation_patterns(text)
        clean_reduction = self._check_for_clean_patterns(text)
        
        risk_score = max(0, manipulation_score - clean_reduction)
        
        # Additional penalties for suspicious patterns
        if len(text) > 200:
            risk_score += 5  # Long manipulative messages
        
        if text.count("!") > 3:
            risk_score += 10  # Excessive exclamation marks
        
        # Clamp to 0-100
        risk_score = float(min(max(risk_score, 0.0), 100.0))
        
        label = score_to_label(risk_score)
        severity = score_to_severity(risk_score)
        
        return {
            "risk_score": round(risk_score, 2),
            "label": label,
            "severity": severity,
            "text_preview": text[:100] if len(text) > 100 else text,
        }

    def score_batch(self, messages: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Score multiple messages."""
        return [self.score_message(msg) for msg in messages]

    def generate_demo_messages(self, count: int = 10) -> List[Dict[str, Any]]:
        """
        Generate demo message data for testing.
        
        Args:
            count: Number of demo messages
        
        Returns:
            List of demo message dicts
        """
        samples = [
            {"preview": "Swap 0.5 ETH to USDC at market rate."},
            {"preview": "GUARANTEED 900% APY — act NOW before it's gone!"},
            {"preview": "Rebalance portfolio per your defined strategy."},
            {"preview": "Last chance — high-yield opportunity expires in 60 seconds."},
            {"preview": "Deposit USDC into verified pool with 8% APY."},
            {"preview": "WARNING: Your account at RISK! Click here NOW!!"},
            {"preview": "Execute swap with 0.2% slippage tolerance."},
            {"preview": "Don't miss out — everyone is making 500% returns TODAY!"},
            {"preview": "Set new take-profit at $2500 per unit sold."},
            {"preview": "IMMEDIATE ACTION REQUIRED — Limited spots available!!!"},
        ]
        
        messages = []
        for i in range(count):
            sample = random.choice(samples)
            msg = {
                "id": f"msg-{i:04d}",
                "preview": sample["preview"],
            }
            messages.append(msg)
        return messages
