"""
Timing Decorator - Adds detailed timing measurements to test execution
"""

import time
import logging
from typing import List
from .base import TestRunnerDecorator, TestResults


class TimingDecorator(TestRunnerDecorator):
    """
    Adds detailed timing measurements (ConcreteDecorator)
    
    Tracks:
    - Overall execution time
    - Per-test timing (if available)
    - Timing breakdown by phase
    
    Example:
        runner = BasicTestRunner()
        runner = TimingDecorator(runner)
        results = runner.run(tests)
        print(results.metadata['timing'])
    """
    
    def __init__(self, runner, track_individual_tests: bool = False):
        """
        Initialize timing decorator
        
        Args:
            runner: Wrapped test runner
            track_individual_tests: Track timing per test (slower but detailed)
        """
        super().__init__(runner)
        self.track_individual_tests = track_individual_tests
        self.logger = logging.getLogger(__name__)
    
    def run(self, tests: List[str]) -> TestResults:
        """
        Run tests with detailed timing
        
        Args:
            tests: List of test identifiers
            
        Returns:
            TestResults with timing metadata
        """
        self.logger.info(f"[Timing] Starting timer for {len(tests)} tests")
        
        # BEFORE: Start timing
        start_time = time.time()
        setup_time = time.time() - start_time  # Setup overhead
        
        # DELEGATE: Run wrapped runner
        exec_start = time.time()
        results = self._runner.run(tests)
        exec_time = time.time() - exec_start
        
        # AFTER: Calculate timing breakdown
        teardown_start = time.time()
        # Teardown operations (if any)
        teardown_time = time.time() - teardown_start
        
        total_time = time.time() - start_time
        
        # Add timing metadata
        timing_data = {
            'total_time': total_time,
            'execution_time': exec_time,
            'setup_time': setup_time,
            'teardown_time': teardown_time,
            'avg_time_per_test': exec_time / len(tests) if tests else 0,
            'tests_per_second': len(tests) / exec_time if exec_time > 0 else 0
        }
        
        results.metadata['timing'] = timing_data
        results.duration = total_time  # Update overall duration
        
        self.logger.info(
            f"[Timing] Completed in {total_time:.2f}s "
            f"(avg: {timing_data['avg_time_per_test']:.2f}s/test, "
            f"rate: {timing_data['tests_per_second']:.1f} tests/s)"
        )
        
        return results