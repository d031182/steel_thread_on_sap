"""
Performance Analysis Strategy

Threshold-based performance analysis following the Strategy pattern.
Detects slow tests that exceed duration thresholds.
"""

from typing import Dict, List
from datetime import datetime
import statistics
import logging

from .base import TestAnalysisStrategy, AnalysisResult

logger = logging.getLogger(__name__)


class PerformanceAnalysisStrategy(TestAnalysisStrategy):
    """
    Detect slow tests using threshold analysis
    
    Algorithm:
    - Calculate average duration from history
    - Compare to threshold
    - Determine severity based on how much threshold is exceeded
    
    Severity Levels:
    - Critical: > 2x threshold
    - High: > threshold but <= 2x
    - Medium: > 80% threshold
    - Low: <= 80% threshold
    
    Usage:
        strategy = PerformanceAnalysisStrategy(threshold=5.0)
        result = strategy.analyze({
            'test_id': 'test_api::test_slow_endpoint',
            'durations': [6.2, 5.8, 7.1, 6.5]
        })
    """
    
    def __init__(self, threshold: float = 5.0):
        """
        Initialize performance strategy
        
        Args:
            threshold: Maximum acceptable duration in seconds (default 5.0)
        """
        self.threshold = threshold
        logger.info(f"[Performance Strategy] Initialized with threshold={threshold}s")
    
    def get_strategy_name(self) -> str:
        return 'performance_threshold_based'
    
    def analyze(self, test_data: Dict) -> AnalysisResult:
        """
        Analyze test performance
        
        Args:
            test_data: Must contain:
                - test_id: str
                - durations: List[float] (in seconds)
        
        Returns:
            AnalysisResult with performance metrics
        """
        # Validate required data
        self.validate_test_data(test_data, ['test_id', 'durations'])
        
        test_id = test_data['test_id']
        durations = test_data['durations']
        
        if not durations:
            return AnalysisResult(
                strategy=self.get_strategy_name(),
                timestamp=datetime.now(),
                data={
                    'test_id': test_id,
                    'avg_duration': 0.0,
                    'severity': 'no_data'
                },
                confidence=0.0,
                recommendations=['No duration data available']
            )
        
        # Calculate statistics
        avg_duration = statistics.mean(durations)
        max_duration = max(durations)
        min_duration = min(durations)
        std_dev = statistics.stdev(durations) if len(durations) > 1 else 0.0
        
        # Determine severity
        severity, confidence = self._determine_severity(avg_duration)
        
        # Generate recommendations
        recommendations = self._generate_recommendations(
            test_id, avg_duration, max_duration, severity
        )
        
        logger.info(
            f"[Performance Strategy] {test_id}: "
            f"avg={avg_duration:.2f}s, max={max_duration:.2f}s, "
            f"severity={severity}, threshold={self.threshold}s"
        )
        
        return AnalysisResult(
            strategy=self.get_strategy_name(),
            timestamp=datetime.now(),
            data={
                'test_id': test_id,
                'avg_duration': avg_duration,
                'max_duration': max_duration,
                'min_duration': min_duration,
                'std_dev': std_dev,
                'severity': severity,
                'threshold': self.threshold,
                'threshold_exceeded_by': avg_duration - self.threshold,
                'slowdown_factor': avg_duration / self.threshold if self.threshold > 0 else 0
            },
            confidence=confidence,
            recommendations=recommendations
        )
    
    def _determine_severity(self, avg_duration: float) -> tuple:
        """Determine severity level and confidence"""
        if avg_duration > self.threshold * 2:
            return 'critical', 1.0
        elif avg_duration > self.threshold:
            return 'high', 0.9
        elif avg_duration > self.threshold * 0.8:
            return 'medium', 0.7
        else:
            return 'low', 0.6
    
    def _generate_recommendations(
        self,
        test_id: str,
        avg_duration: float,
        max_duration: float,
        severity: str
    ) -> List[str]:
        """Generate optimization recommendations"""
        recommendations = []
        
        if severity == 'critical':
            recommendations.append(f"🔴 CRITICAL: Test '{test_id}' is extremely slow ({avg_duration:.2f}s)")
            recommendations.append(f"Action: IMMEDIATE optimization required (>{self.threshold * 2}s threshold)")
            recommendations.append("Action: Profile test to identify bottlenecks")
            recommendations.append("Action: Consider breaking into smaller tests")
            recommendations.append("Action: Check for N+1 queries, unnecessary API calls")
        elif severity == 'high':
            recommendations.append(f"⚠️ HIGH: Test '{test_id}' exceeds threshold ({avg_duration:.2f}s > {self.threshold}s)")
            recommendations.append("Action: Optimize within 1 week")
            recommendations.append("Action: Review database queries and API calls")
            recommendations.append("Action: Add test-specific timeouts if appropriate")
        elif severity == 'medium':
            recommendations.append(f"⚠️ MEDIUM: Test '{test_id}' approaching threshold ({avg_duration:.2f}s)")
            recommendations.append("Action: Monitor for further slowdown")
            recommendations.append("Action: Review for optimization opportunities")
        else:
            recommendations.append(f"✓ LOW: Test '{test_id}' performs well ({avg_duration:.2f}s)")
            recommendations.append("Action: Continue monitoring")
        
        # Add max duration warning if significantly higher than average
        if max_duration > avg_duration * 1.5:
            recommendations.append(
                f"⚠️ High variance detected: max={max_duration:.2f}s vs avg={avg_duration:.2f}s"
            )
            recommendations.append("Action: Investigate inconsistent performance")
        
        return recommendations