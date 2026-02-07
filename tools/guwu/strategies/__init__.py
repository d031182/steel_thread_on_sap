"""
Gu Wu Strategy Pattern Components

Provides pluggable test analysis strategies following the Strategy design pattern.
This allows swapping analysis algorithms at runtime without modifying core code.

Components:
- base.py: TestAnalysisStrategy interface + AnalysisResult
- flakiness.py: Transition-based flaky test detection
- performance.py: Threshold-based performance analysis
- coverage.py: Coverage gap analysis

Usage:
    from tools.guwu.strategies import (
        GuWuAnalyzer,
        FlakynessAnalysisStrategy,
        PerformanceAnalysisStrategy
    )
    
    # Single strategy
    analyzer = GuWuAnalyzer(FlakynessAnalysisStrategy())
    result = analyzer.analyze(test_data)
    
    # Swap strategies
    analyzer.set_strategy(PerformanceAnalysisStrategy(threshold=3.0))
    result = analyzer.analyze(test_data)
    
    # Multiple strategies
    results = analyzer.analyze_with_multiple_strategies(
        test_data,
        strategies=[
            FlakynessAnalysisStrategy(),
            PerformanceAnalysisStrategy(),
            CoverageAnalysisStrategy()
        ]
    )
"""

from .base import (
    TestAnalysisStrategy,
    AnalysisResult,
    GuWuAnalyzer
)

from .flakiness import FlakynessAnalysisStrategy
from .performance import PerformanceAnalysisStrategy
from .coverage import CoverageAnalysisStrategy

__all__ = [
    'TestAnalysisStrategy',
    'AnalysisResult',
    'GuWuAnalyzer',
    'FlakynessAnalysisStrategy',
    'PerformanceAnalysisStrategy',
    'CoverageAnalysisStrategy'
]