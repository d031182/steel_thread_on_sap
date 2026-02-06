"""
Metrics Decorator - Integrates with Gu Wu metrics collection system
"""

import logging
from typing import List
from datetime import datetime
from .base import TestRunnerDecorator, TestResults


class MetricsDecorator(TestRunnerDecorator):
    """
    Integrates with Gu Wu metrics system (ConcreteDecorator)
    
    Automatically collects and persists:
    - Test execution metrics
    - Pass/fail rates
    - Duration trends
    - Integration with existing Gu Wu metrics.db
    
    Example:
        from tests.guwu.metrics import GuWuMetrics
        
        runner = BasicTestRunner()
        metrics = GuWuMetrics('tests/guwu/metrics.db')
        runner = MetricsDecorator(runner, metrics)
        results = runner.run(tests)
    """
    
    def __init__(self, runner, metrics_collector=None, db_path: str = None):
        """
        Initialize metrics decorator
        
        Args:
            runner: Wrapped test runner
            metrics_collector: GuWuMetrics instance (optional)
            db_path: Path to metrics database (used if metrics_collector not provided)
        """
        super().__init__(runner)
        self.metrics_collector = metrics_collector
        self.db_path = db_path or 'tests/guwu/metrics.db'
        self.logger = logging.getLogger(__name__)
        
        # Lazy load metrics collector if not provided
        if self.metrics_collector is None:
            self._init_metrics_collector()
    
    def _init_metrics_collector(self):
        """Initialize metrics collector on first use"""
        try:
            from tests.guwu.metrics import GuWuMetrics
            self.metrics_collector = GuWuMetrics(self.db_path)
            self.logger.debug(f"[Metrics] Initialized GuWuMetrics with {self.db_path}")
        except Exception as e:
            self.logger.warning(f"[Metrics] Could not initialize metrics collector: {e}")
            self.metrics_collector = None
    
    def run(self, tests: List[str]) -> TestResults:
        """
        Run tests and collect metrics
        
        Args:
            tests: List of test identifiers
            
        Returns:
            TestResults with metrics metadata
        """
        if self.metrics_collector is None:
            self.logger.warning("[Metrics] Metrics collector not available, skipping collection")
            return self._runner.run(tests)
        
        self.logger.info(f"[Metrics] Collecting metrics for {len(tests)} tests")
        
        # BEFORE: Record session start
        session_id = self._generate_session_id()
        start_time = datetime.now()
        
        # DELEGATE: Run wrapped runner
        results = self._runner.run(tests)
        
        # AFTER: Record metrics
        try:
            self._record_session_metrics(
                session_id=session_id,
                results=results,
                start_time=start_time
            )
            
            # Add metrics metadata to results
            results.metadata['metrics'] = {
                'session_id': session_id,
                'db_path': self.db_path,
                'collected': True
            }
            
            self.logger.info(
                f"[Metrics] Session {session_id} recorded: "
                f"{results.passed}/{results.total} passed"
            )
            
        except Exception as e:
            self.logger.error(f"[Metrics] Failed to record metrics: {e}")
            results.metadata['metrics'] = {
                'collected': False,
                'error': str(e)
            }
        
        return results
    
    def _generate_session_id(self) -> str:
        """Generate unique session identifier"""
        import uuid
        return str(uuid.uuid4())[:8]
    
    def _record_session_metrics(self, session_id: str, results: TestResults, start_time: datetime):
        """Record session metrics to database"""
        # Record each test execution
        for i, test in enumerate(range(results.total)):
            # Determine outcome
            if i < results.passed:
                outcome = 'passed'
            elif i < (results.passed + results.failed):
                outcome = 'failed'
            else:
                outcome = 'skipped'
            
            # Record to metrics database
            # Note: This is a simplified version - real implementation would
            # need to track individual test IDs and outcomes from pytest
            try:
                self.metrics_collector.record_test_run(
                    test_id=f"test_{i}",  # Placeholder
                    outcome=outcome,
                    duration=results.duration / results.total if results.total > 0 else 0
                )
            except Exception as e:
                self.logger.debug(f"[Metrics] Could not record test {i}: {e}")
        
        # Record session summary
        self.logger.debug(
            f"[Metrics] Recorded {results.total} test executions to {self.db_path}"
        )