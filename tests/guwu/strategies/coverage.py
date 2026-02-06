"""
Coverage Analysis Strategy

Coverage gap detection following the Strategy pattern.
Identifies areas with insufficient test coverage.
"""

from typing import Dict, List
from datetime import datetime
import logging

from .base import TestAnalysisStrategy, AnalysisResult

logger = logging.getLogger(__name__)


class CoverageAnalysisStrategy(TestAnalysisStrategy):
    """
    Detect coverage gaps using coverage data
    
    Algorithm:
    - Calculate coverage percentage
    - Determine priority based on coverage level
    - Identify critical gaps (< 50% coverage)
    
    Priority Levels:
    - Critical: < 50% coverage
    - High: 50-70% coverage
    - Medium: 70-85% coverage
    - Low: > 85% coverage
    
    Usage:
        strategy = CoverageAnalysisStrategy(target_coverage=70.0)
        result = strategy.analyze({
            'test_id': 'module::my_module',
            'coverage': {
                'lines_covered': 120,
                'total_lines': 200,
                'uncovered_lines': [45, 46, 78, 79, 80]
            }
        })
    """
    
    def __init__(self, target_coverage: float = 70.0):
        """
        Initialize coverage strategy
        
        Args:
            target_coverage: Target coverage percentage (default 70.0)
        """
        self.target_coverage = target_coverage
        logger.info(f"[Coverage Strategy] Initialized with target={target_coverage}%")
    
    def get_strategy_name(self) -> str:
        return 'coverage_gap_analysis'
    
    def analyze(self, test_data: Dict) -> AnalysisResult:
        """
        Analyze test coverage
        
        Args:
            test_data: Must contain:
                - test_id: str (or module name)
                - coverage: Dict with lines_covered, total_lines
        
        Returns:
            AnalysisResult with coverage metrics and gap analysis
        """
        # Validate required data
        self.validate_test_data(test_data, ['test_id', 'coverage'])
        
        test_id = test_data['test_id']
        coverage = test_data['coverage']
        
        lines_covered = coverage.get('lines_covered', 0)
        total_lines = coverage.get('total_lines', 0)
        
        if total_lines == 0:
            return AnalysisResult(
                strategy=self.get_strategy_name(),
                timestamp=datetime.now(),
                data={
                    'test_id': test_id,
                    'coverage_pct': 0.0,
                    'priority': 'no_code'
                },
                confidence=0.0,
                recommendations=['No code to analyze']
            )
        
        # Calculate coverage percentage
        coverage_pct = (lines_covered / total_lines) * 100
        gap_lines = total_lines - lines_covered
        
        # Determine priority
        priority, confidence = self._determine_priority(coverage_pct)
        
        # Generate recommendations
        recommendations = self._generate_recommendations(
            test_id, coverage_pct, gap_lines, priority
        )
        
        logger.info(
            f"[Coverage Strategy] {test_id}: "
            f"coverage={coverage_pct:.1f}%, gap={gap_lines} lines, "
            f"priority={priority}"
        )
        
        return AnalysisResult(
            strategy=self.get_strategy_name(),
            timestamp=datetime.now(),
            data={
                'test_id': test_id,
                'coverage_pct': coverage_pct,
                'lines_covered': lines_covered,
                'total_lines': total_lines,
                'gap_lines': gap_lines,
                'priority': priority,
                'target_coverage': self.target_coverage,
                'coverage_deficit': max(0, self.target_coverage - coverage_pct),
                'uncovered_lines': coverage.get('uncovered_lines', [])[:10]  # First 10
            },
            confidence=confidence,
            recommendations=recommendations
        )
    
    def _determine_priority(self, coverage_pct: float) -> tuple:
        """Determine priority level and confidence"""
        if coverage_pct < 50:
            return 'critical', 1.0
        elif coverage_pct < 70:
            return 'high', 0.9
        elif coverage_pct < 85:
            return 'medium', 0.8
        else:
            return 'low', 0.7
    
    def _generate_recommendations(
        self,
        test_id: str,
        coverage_pct: float,
        gap_lines: int,
        priority: str
    ) -> List[str]:
        """Generate coverage improvement recommendations"""
        recommendations = []
        
        if priority == 'critical':
            recommendations.append(f"🔴 CRITICAL: '{test_id}' has very low coverage ({coverage_pct:.1f}%)")
            recommendations.append(f"Action: IMMEDIATE test creation required ({gap_lines} uncovered lines)")
            recommendations.append("Action: Prioritize critical business logic paths")
            recommendations.append("Action: Add unit tests for all public methods")
            recommendations.append("Action: Review why coverage is so low")
        elif priority == 'high':
            recommendations.append(f"⚠️ HIGH: '{test_id}' below target coverage ({coverage_pct:.1f}% < {self.target_coverage}%)")
            recommendations.append(f"Action: Add tests for {gap_lines} uncovered lines")
            recommendations.append("Action: Focus on edge cases and error paths")
            recommendations.append("Action: Aim to reach 70% minimum")
        elif priority == 'medium':
            recommendations.append(f"⚠️ MEDIUM: '{test_id}' approaching target ({coverage_pct:.1f}%)")
            recommendations.append("Action: Fill remaining coverage gaps when convenient")
            recommendations.append("Action: Review uncovered lines for necessity")
        else:
            recommendations.append(f"✓ LOW: '{test_id}' has good coverage ({coverage_pct:.1f}%)")
            recommendations.append("Action: Maintain current coverage level")
        
        return recommendations