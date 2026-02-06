"""
Base Strategy Pattern Components for Gu Wu

Provides the core Strategy pattern interface and analyzer context.
Following GoF Strategy pattern for pluggable test analysis algorithms.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Dict, List, Any, Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


@dataclass
class AnalysisResult:
    """Result of test analysis"""
    strategy: str                    # Which strategy was used
    timestamp: datetime              # When analysis was performed
    data: Dict[str, Any]            # Strategy-specific results
    confidence: float = 1.0          # Confidence in result (0.0-1.0)
    recommendations: List[str] = None  # Action recommendations
    
    def __post_init__(self):
        if self.recommendations is None:
            self.recommendations = []
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for serialization"""
        return {
            'strategy': self.strategy,
            'timestamp': self.timestamp.isoformat(),
            'data': self.data,
            'confidence': self.confidence,
            'recommendations': self.recommendations
        }


class TestAnalysisStrategy(ABC):
    """
    Base strategy for test analysis (Strategy Pattern)
    
    This is the Strategy interface that all concrete strategies implement.
    Allows swapping analysis algorithms at runtime without modifying client code.
    
    Usage:
        strategy = FlakynessAnalysisStrategy(sensitivity=1.2)
        result = strategy.analyze(test_data)
        
        # Swap strategy
        strategy = PerformanceAnalysisStrategy(threshold=3.0)
        result = strategy.analyze(test_data)
    """
    
    @abstractmethod
    def analyze(self, test_data: Dict) -> AnalysisResult:
        """
        Analyze test data and return result
        
        Args:
            test_data: Dictionary containing test information
                Expected keys vary by strategy but commonly include:
                - test_id: str
                - history: List[Dict] (past runs)
                - durations: List[float]
                - outcomes: List[str] ('passed', 'failed', 'skipped')
                - coverage: Dict (coverage data)
        
        Returns:
            AnalysisResult with strategy-specific data
        """
        pass
    
    @abstractmethod
    def get_strategy_name(self) -> str:
        """
        Return unique strategy identifier
        
        Used for tracking which strategy was used for each analysis.
        Should be descriptive and unique.
        
        Returns:
            Strategy name (e.g., 'flakiness_transition_based')
        """
        pass
    
    def validate_test_data(self, test_data: Dict, required_keys: List[str]) -> bool:
        """
        Validate test_data has required keys
        
        Args:
            test_data: Test data dictionary
            required_keys: List of required key names
        
        Returns:
            True if valid, raises ValueError if not
        """
        missing_keys = [key for key in required_keys if key not in test_data]
        if missing_keys:
            raise ValueError(
                f"Test data missing required keys: {missing_keys}. "
                f"Strategy '{self.get_strategy_name()}' requires: {required_keys}"
            )
        return True


class GuWuAnalyzer:
    """
    Context class that uses TestAnalysisStrategy (Strategy Pattern)
    
    This is the Context in the Strategy pattern. It maintains a reference
    to a Strategy object and delegates analysis work to it.
    
    Benefits:
    - Can swap strategies at runtime
    - Strategy changes don't affect client code
    - Easy to add new strategies (just implement interface)
    - Can run multiple strategies and compare results
    
    Usage:
        # Single strategy
        analyzer = GuWuAnalyzer(FlakynessAnalysisStrategy())
        result = analyzer.analyze(test_data)
        
        # Swap strategy
        analyzer.set_strategy(PerformanceAnalysisStrategy())
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
    
    def __init__(self, strategy: TestAnalysisStrategy):
        """
        Initialize analyzer with a strategy
        
        Args:
            strategy: Concrete strategy implementation
        """
        self._strategy = strategy
        self._strategy_history: List[Dict] = []
    
    @property
    def strategy(self) -> TestAnalysisStrategy:
        """Get current strategy"""
        return self._strategy
    
    def set_strategy(self, strategy: TestAnalysisStrategy):
        """
        Change analysis strategy at runtime
        
        This is the key benefit of Strategy pattern - swap algorithms
        without changing client code.
        
        Args:
            strategy: New strategy to use
        """
        logger.info(
            f"[Gu Wu Analyzer] Switching strategy: "
            f"{self._strategy.get_strategy_name()} → {strategy.get_strategy_name()}"
        )
        self._strategy = strategy
    
    def analyze(self, test_data: Dict) -> AnalysisResult:
        """
        Run analysis using current strategy
        
        Args:
            test_data: Test data to analyze
        
        Returns:
            AnalysisResult from current strategy
        """
        logger.info(f"[Gu Wu Analyzer] Running analysis with strategy: {self._strategy.get_strategy_name()}")
        
        # Delegate to strategy
        result = self._strategy.analyze(test_data)
        
        # Track which strategy was used (for audit trail)
        self._strategy_history.append({
            'strategy': self._strategy.get_strategy_name(),
            'timestamp': datetime.now(),
            'test_id': test_data.get('test_id', 'unknown'),
            'confidence': result.confidence
        })
        
        return result
    
    def analyze_with_multiple_strategies(
        self,
        test_data: Dict,
        strategies: List[TestAnalysisStrategy]
    ) -> List[AnalysisResult]:
        """
        Run multiple strategies and aggregate results
        
        Useful for:
        - Comparing different analysis approaches
        - Comprehensive test health assessment
        - Validating strategy accuracy
        
        Args:
            test_data: Test data to analyze
            strategies: List of strategies to run
        
        Returns:
            List of AnalysisResult (one per strategy)
        """
        logger.info(
            f"[Gu Wu Analyzer] Running {len(strategies)} strategies: "
            f"{[s.get_strategy_name() for s in strategies]}"
        )
        
        results = []
        original_strategy = self._strategy
        
        try:
            for strategy in strategies:
                self.set_strategy(strategy)
                result = self.analyze(test_data)
                results.append(result)
        finally:
            # Restore original strategy
            self._strategy = original_strategy
        
        return results
    
    def get_strategy_history(self, limit: int = 10) -> List[Dict]:
        """
        Get history of strategies used
        
        Useful for:
        - Auditing which strategies were applied
        - Analyzing strategy effectiveness
        - Debugging analysis results
        
        Args:
            limit: Maximum number of history entries to return
        
        Returns:
            List of strategy usage records (most recent first)
        """
        return self._strategy_history[-limit:]
    
    def clear_history(self):
        """Clear strategy history (e.g., at session end)"""
        self._strategy_history = []
        logger.info("[Gu Wu Analyzer] Strategy history cleared")