"""
Test Health Monitor Observer

Aggregates test health metrics across test suite execution.
Provides holistic view of test quality trends.
"""

from typing import Dict, List
from datetime import datetime, timedelta
from collections import defaultdict
import logging

from .base import TestObserver, TestEvent, TestEventType

logger = logging.getLogger(__name__)


class TestHealthMonitorObserver(TestObserver):
    """
    Monitor overall test suite health
    
    Tracks:
    - Pass/fail rates over time
    - Test duration trends
    - Coverage trends
    - Flakiness trends
    
    Provides:
    - Suite health score (0-100)
    - Trend analysis (improving/degrading)
    - Early warning alerts
    
    Usage:
        monitor = TestHealthMonitorObserver()
        subject.attach(monitor)
        
        # After test suite runs:
        health = monitor.get_health_score()
        # → 85 (good health)
        
        trends = monitor.get_trends()
        # → {'pass_rate': 'improving', 'performance': 'stable'}
    """
    
    def __init__(self, window_size: int = 10):
        """
        Initialize health monitor
        
        Args:
            window_size: Number of test runs to consider for trends
        """
        super().__init__("TestHealthMonitor")
        self.window_size = window_size
        
        # Metrics storage
        self._suite_results: List[Dict] = []
        self._test_outcomes: Dict[str, List[str]] = defaultdict(list)
        self._test_durations: Dict[str, List[float]] = defaultdict(list)
        self._coverage_history: List[float] = []
        
        logger.info(f"[Health Monitor] Initialized (window_size={window_size})")
    
    def update(self, event: TestEvent):
        """
        React to test event
        
        Args:
            event: TestEvent to process
        """
        if event.event_type == TestEventType.SUITE_FINISHED:
            self._handle_suite_finished(event)
        elif event.event_type == TestEventType.TEST_PASSED:
            self._record_test_outcome(event, 'passed')
        elif event.event_type == TestEventType.TEST_FAILED:
            self._record_test_outcome(event, 'failed')
        elif event.event_type == TestEventType.TEST_SKIPPED:
            self._record_test_outcome(event, 'skipped')
        elif event.event_type == TestEventType.COVERAGE_DROPPED:
            self._handle_coverage_change(event)
    
    def _handle_suite_finished(self, event: TestEvent):
        """Process suite completion event"""
        suite_data = event.data
        
        result = {
            'timestamp': event.timestamp,
            'total_tests': suite_data.get('total', 0),
            'passed': suite_data.get('passed', 0),
            'failed': suite_data.get('failed', 0),
            'skipped': suite_data.get('skipped', 0),
            'duration': suite_data.get('duration', 0.0),
            'coverage': suite_data.get('coverage', 0.0)
        }
        
        self._suite_results.append(result)
        
        # Keep only recent results
        if len(self._suite_results) > self.window_size:
            self._suite_results.pop(0)
        
        # Store coverage
        if result['coverage'] > 0:
            self._coverage_history.append(result['coverage'])
            if len(self._coverage_history) > self.window_size:
                self._coverage_history.pop(0)
        
        logger.info(
            f"[Health Monitor] Suite finished: "
            f"{result['passed']}/{result['total_tests']} passed, "
            f"coverage={result['coverage']:.1f}%"
        )
    
    def _record_test_outcome(self, event: TestEvent, outcome: str):
        """Record individual test outcome"""
        test_id = event.data.get('test_id', 'unknown')
        duration = event.data.get('duration', 0.0)
        
        # Store outcome
        self._test_outcomes[test_id].append(outcome)
        if len(self._test_outcomes[test_id]) > self.window_size:
            self._test_outcomes[test_id].pop(0)
        
        # Store duration
        if duration > 0:
            self._test_durations[test_id].append(duration)
            if len(self._test_durations[test_id]) > self.window_size:
                self._test_durations[test_id].pop(0)
    
    def _handle_coverage_change(self, event: TestEvent):
        """Process coverage change event"""
        new_coverage = event.data.get('new_coverage', 0.0)
        old_coverage = event.data.get('old_coverage', 0.0)
        
        if new_coverage < old_coverage:
            logger.warning(
                f"[Health Monitor] Coverage dropped: "
                f"{old_coverage:.1f}% → {new_coverage:.1f}%"
            )
    
    def get_health_score(self) -> float:
        """
        Calculate overall test suite health score (0-100)
        
        Components:
        - Pass rate: 40% weight
        - Coverage: 30% weight
        - Performance: 20% weight
        - Stability: 10% weight
        
        Returns:
            Health score (0-100, higher is better)
        """
        if not self._suite_results:
            return 0.0
        
        # Get recent suite result
        recent = self._suite_results[-1]
        
        # Pass rate score (0-40 points)
        pass_rate = recent['passed'] / recent['total_tests'] if recent['total_tests'] > 0 else 0
        pass_score = pass_rate * 40
        
        # Coverage score (0-30 points)
        coverage = recent['coverage']
        coverage_score = min(coverage / 100 * 30, 30)
        
        # Performance score (0-20 points)
        # Fast suite (< 30s) = 20 points, slow (> 120s) = 0 points
        duration = recent['duration']
        if duration < 30:
            perf_score = 20
        elif duration > 120:
            perf_score = 0
        else:
            perf_score = 20 * (1 - (duration - 30) / 90)
        
        # Stability score (0-10 points)
        # Based on recent pass rate consistency
        if len(self._suite_results) >= 3:
            recent_pass_rates = [
            r['passed'] / r['total_tests'] if r['total_tests'] > 0 else 0
                for r in self._suite_results[-3:]
            ]
            variance = max(recent_pass_rates) - min(recent_pass_rates)
            stability_score = 10 * (1 - min(variance * 2, 1.0))
        else:
            stability_score = 5  # Default for insufficient data
        
        total_score = pass_score + coverage_score + perf_score + stability_score
        
        return round(total_score, 1)
    
    def get_trends(self) -> Dict[str, str]:
        """
        Analyze trends in test health
        
        Returns:
            Dict with trend indicators: 'improving', 'stable', 'degrading'
        """
        if len(self._suite_results) < 3:
            return {
                'pass_rate': 'insufficient_data',
                'coverage': 'insufficient_data',
                'performance': 'insufficient_data'
            }
        
        recent = self._suite_results[-3:]
        
        # Pass rate trend
        pass_rates = [
            r['passed'] / r['total_tests'] if r['total_tests'] > 0 else 0
            for r in recent
        ]
        pass_trend = self._determine_trend(pass_rates)
        
        # Coverage trend
        coverages = [r['coverage'] for r in recent if r['coverage'] > 0]
        cov_trend = self._determine_trend(coverages) if coverages else 'insufficient_data'
        
        # Performance trend (lower is better, so invert)
        durations = [r['duration'] for r in recent]
        perf_trend = self._determine_trend(durations, lower_is_better=True)
        
        return {
            'pass_rate': pass_trend,
            'coverage': cov_trend,
            'performance': perf_trend
        }
    
    def _determine_trend(self, values: List[float], lower_is_better: bool = False) -> str:
        """Determine if values are improving, stable, or degrading"""
        if len(values) < 2:
            return 'insufficient_data'
        
        # Calculate change
        start = values[0]
        end = values[-1]
        
        if start == 0:
            return 'stable'
        
        change_pct = ((end - start) / start) * 100
        
        # Invert for metrics where lower is better (e.g., duration)
        if lower_is_better:
            change_pct = -change_pct
        
        if change_pct > 5:
            return 'improving'
        elif change_pct < -5:
            return 'degrading'
        else:
            return 'stable'
    
    def get_summary(self) -> Dict:
        """
        Get comprehensive test health summary
        
        Returns:
            Dict with health score, trends, and key metrics
        """
        if not self._suite_results:
            return {
                'health_score': 0.0,
                'status': 'no_data',
                'trends': {},
                'latest_results': {}
            }
        
        health_score = self.get_health_score()
        trends = self.get_trends()
        latest = self._suite_results[-1]
        
        # Determine status
        if health_score >= 80:
            status = 'excellent'
        elif health_score >= 60:
            status = 'good'
        elif health_score >= 40:
            status = 'fair'
        else:
            status = 'poor'
        
        return {
            'health_score': health_score,
            'status': status,
            'trends': trends,
            'latest_results': {
                'total_tests': latest['total_tests'],
                'pass_rate': latest['passed'] / latest['total_tests'] if latest['total_tests'] > 0 else 0,
                'coverage': latest['coverage'],
                'duration': latest['duration']
            },
            'recommendations': self._generate_recommendations(health_score, trends)
        }
    
    def _generate_recommendations(self, health_score: float, trends: Dict) -> List[str]:
        """Generate recommendations based on health and trends"""
        recommendations = []
        
        if health_score < 60:
            recommendations.append("⚠️ Test suite health is below acceptable threshold")
        
        if trends.get('pass_rate') == 'degrading':
            recommendations.append("⚠️ Pass rate is declining - investigate recent failures")
        
        if trends.get('coverage') == 'degrading':
            recommendations.append("⚠️ Coverage is dropping - add tests for new code")
        
        if trends.get('performance') == 'degrading':
            recommendations.append("⚠️ Test suite is slowing down - profile slow tests")
        
        if not recommendations:
            recommendations.append("✓ Test suite is healthy")
        
        return recommendations