"""
Base Pattern Interface
======================

Abstract base class for all Shi Fu correlation patterns.

Each pattern detector must implement:
1. detect() - Find correlation in data
2. calculate_confidence() - Measure correlation strength
3. generate_recommendation() - Provide actionable advice
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Dict, Optional, List


@dataclass
class PatternMatch:
    """Result of pattern detection"""
    pattern_name: str
    confidence: float  # 0.0-1.0
    severity: str  # URGENT, HIGH, MEDIUM, LOW
    fengshui_evidence: Dict
    guwu_evidence: Dict
    root_cause: str
    recommendation: str
    estimated_effort: str  # e.g., "2-4 hours", "1-2 days"
    combined_value: str  # e.g., "High - fixes code + tests"
    affected_modules: List[str]


class BasePattern(ABC):
    """
    Abstract base class for correlation pattern detectors
    
    Philosophy: Each pattern represents a teaching from Shi Fu's experience.
    """
    
    @property
    @abstractmethod
    def pattern_name(self) -> str:
        """Unique identifier for this pattern"""
        pass
    
    @property
    @abstractmethod
    def pattern_description(self) -> str:
        """Human-readable description of what this pattern detects"""
        pass
    
    @abstractmethod
    def detect(
        self,
        fengshui_data: Dict,
        guwu_data: Dict
    ) -> Optional[PatternMatch]:
        """
        Analyze data from both disciples to find correlation
        
        Args:
            fengshui_data: Code quality metrics from Feng Shui
            guwu_data: Test quality metrics from Gu Wu
        
        Returns:
            PatternMatch if correlation found, None otherwise
        """
        pass
    
    def calculate_confidence(
        self,
        fengshui_metrics: Dict,
        guwu_metrics: Dict
    ) -> float:
        """
        Calculate confidence score (0.0-1.0) for correlation
        
        Higher confidence = stronger evidence of correlation
        
        Args:
            fengshui_metrics: Relevant metrics from code analysis
            guwu_metrics: Relevant metrics from test analysis
        
        Returns:
            Confidence score (0.0 = no correlation, 1.0 = certain correlation)
        """
        # Default implementation: simple heuristic
        # Subclasses can override for more sophisticated scoring
        
        if not fengshui_metrics or not guwu_metrics:
            return 0.0
        
        # Example: If both metrics are above threshold, confidence is high
        # This is a placeholder - each pattern should implement its own logic
        return 0.5
    
    def determine_severity(
        self,
        impact_score: float,
        affected_modules_count: int
    ) -> str:
        """
        Determine severity based on impact and scope
        
        Args:
            impact_score: How severe is the issue (0.0-1.0)
            affected_modules_count: Number of modules affected
        
        Returns:
            Severity level: URGENT, HIGH, MEDIUM, or LOW
        """
        if impact_score >= 0.8 or affected_modules_count >= 5:
            return "URGENT"
        elif impact_score >= 0.6 or affected_modules_count >= 3:
            return "HIGH"
        elif impact_score >= 0.4 or affected_modules_count >= 2:
            return "MEDIUM"
        else:
            return "LOW"
    
    def estimate_effort(self, affected_modules_count: int) -> str:
        """
        Estimate effort to fix based on scope
        
        Args:
            affected_modules_count: Number of modules affected
        
        Returns:
            Effort estimate string
        """
        if affected_modules_count <= 1:
            return "1-2 hours"
        elif affected_modules_count <= 3:
            return "2-4 hours"
        elif affected_modules_count <= 5:
            return "4-8 hours (half day)"
        else:
            return "1-2 days (full refactor)"
    
    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}: {self.pattern_name}>"