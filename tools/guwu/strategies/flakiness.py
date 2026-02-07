"""
Flakiness Analysis Strategy

Transition-based flaky test detection following the Strategy pattern.
Detects tests with unstable pass/fail patterns.
"""

from typing import Dict, List
from datetime import datetime
import statistics
import logging

from .base import TestAnalysisStrategy, AnalysisResult

logger = logging.getLogger(__name__)


class FlakynessAnalysisStrategy(TestAnalysisStrategy):
    """
    Detect flaky tests using transition analysis
    
    Algorithm:
    - Count state transitions (pass→fail, fail→pass)
    - Calculate transition rate
    - Apply severity multiplier
    - Score: (transitions / total_runs) * sensitivity
    
    Thresholds:
    - Score > 0.3: High flakiness
    - Score > 0.15: Medium flakiness
    - Score <= 0.15: Low flakiness
    
    Usage:
        strategy = FlakynessAnalysisStrategy(sensitivity=1.0)
        result = strategy.analyze({
            'test_id': 'test_api::test_endpoint',
            'history': [
                {'outcome': 'passed'},
                {'outcome': 'failed'},
                {'outcome': 'passed'},
                {'outcome': 'failed'}
            ]
        })
    """
    
    def __init__(self, sensitivity: float = 1.0):
        """
        Initialize flakiness strategy
        
        Args:
            sensitivity: Multiplier for transition score (default 1.0)
                        Higher = more sensitive to transitions
                        Range: 0.5-2.0 typical
        """
        self.sensitivity = sensitivity
        logger.info(f"[Flakiness Strategy] Initialized with sensitivity={sensitivity}")
    
    def get_strategy_name(self) -> str:
        return 'flakiness_transition_based'
    
    def analyze(self, test_data: Dict) -> AnalysisResult:
        """
        Analyze test for flakiness
        
        Args:
            test_data: Must contain:
                - test_id: str
                - history: List[Dict] with 'outcome' keys
        
        Returns:
            AnalysisResult with flakiness score and severity
        """
        # Validate required data
        self.validate_test_data(test_data, ['test_id', 'history'])
        
        test_id = test_data['test_id']
        history = test_data['history']
        
        if len(history) < 3:
            # Not enough data for reliable analysis
            return AnalysisResult(
                strategy=self.get_strategy_name(),
                timestamp=datetime.now(),
                data={
                    'test_id': test_id,
                    'score': 0.0,
                    'severity': 'insufficient_data',
                    'transitions': 0,
                    'total_runs': len(history)
                },
                confidence=0.3,  # Low confidence
                recommendations=['Need at least 3 test runs for flakiness analysis']
            )
        
        # Count transitions
        transitions = self._count_transitions(history)
        total_runs = len(history)
        
        # Calculate score
        score = (transitions / total_runs) * self.sensitivity
        
        # Determine severity
        if score > 0.3:
            severity = 'high'
            confidence = 0.9
        elif score > 0.15:
            severity = 'medium'
            confidence = 0.8
        else:
            severity = 'low'
            confidence = 0.7
        
        # Generate recommendations
        recommendations = self._generate_recommendations(score, severity, test_id)
        
        logger.info(
            f"[Flakiness Strategy] {test_id}: "
            f"score={score:.3f}, severity={severity}, "
            f"transitions={transitions}/{total_runs}"
        )
        
        return AnalysisResult(
            strategy=self.get_strategy_name(),
            timestamp=datetime.now(),
            data={
                'test_id': test_id,
                'score': score,
                'severity': severity,
                'transitions': transitions,
                'total_runs': total_runs,
                'sensitivity_used': self.sensitivity,
                'recent_outcomes': [h.get('outcome') for h in history[-5:]]
            },
            confidence=confidence,
            recommendations=recommendations
        )
    
    def _count_transitions(self, history: List[Dict]) -> int:
        """Count pass↔fail transitions"""
        transitions = 0
        for i in range(len(history) - 1):
            current = history[i].get('outcome', 'unknown')
            next_outcome = history[i + 1].get('outcome', 'unknown')
            
            if current != next_outcome and current in ['passed', 'failed'] and next_outcome in ['passed', 'failed']:
                transitions += 1
        
        return transitions
    
    def _generate_recommendations(self, score: float, severity: str, test_id: str) -> List[str]:
        """Generate action recommendations based on flakiness"""
        recommendations = []
        
        if severity == 'high':
            recommendations.append(f"⚠️ HIGH FLAKINESS: Test '{test_id}' is highly unstable")
            recommendations.append("Action: Quarantine this test immediately")
            recommendations.append("Action: Investigate root cause (timing issues, race conditions, external dependencies)")
            recommendations.append("Action: Consider rewriting test for stability")
        elif severity == 'medium':
            recommendations.append(f"⚠️ MEDIUM FLAKINESS: Test '{test_id}' shows instability")
            recommendations.append("Action: Monitor closely for pattern changes")
            recommendations.append("Action: Review test for potential timing issues")
            recommendations.append("Action: Add retries or increase timeouts if appropriate")
        elif severity == 'low':
            recommendations.append(f"✓ LOW FLAKINESS: Test '{test_id}' is relatively stable")
            recommendations.append("Action: Continue normal monitoring")
        
        return recommendations