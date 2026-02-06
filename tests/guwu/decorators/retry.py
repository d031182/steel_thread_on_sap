"""
Retry Decorator - Adds retry logic for flaky tests
"""

import logging
import time
from typing import List
from .base import TestRunnerDecorator, TestResults


class RetryDecorator(TestRunnerDecorator):
    """
    Adds retry logic for flaky tests (ConcreteDecorator)
    
    Retries failed tests automatically to handle flaky failures.
    Useful for tests that occasionally fail due to timing issues.
    
    Example:
        runner = BasicTestRunner()
        runner = RetryDecorator(runner, max_retries=2, delay=1.0)
        results = runner.run(tests)
    """
    
    def __init__(self, runner, max_retries: int = 2, delay: float = 1.0):
        """
        Initialize retry decorator
        
        Args:
            runner: Wrapped test runner
            max_retries: Maximum number of retry attempts per test
            delay: Delay in seconds between retries
        """
        super().__init__(runner)
        self.max_retries = max_retries
        self.delay = delay
        self.logger = logging.getLogger(__name__)
    
    def run(self, tests: List[str]) -> TestResults:
        """
        Run tests with retry logic
        
        Args:
            tests: List of test identifiers
            
        Returns:
            TestResults with retry metadata
        """
        self.logger.info(f"[Retry] Retry decorator enabled (max_retries={self.max_retries})")
        
        # DELEGATE: First attempt
        results = self._runner.run(tests)
        
        # Check if any tests failed
        if results.failed == 0:
            # All passed on first try
            results.metadata['retries'] = {'attempted': 0, 'recovered': 0}
            return results
        
        # RETRY LOGIC: Retry failed tests
        retries_attempted = 0
        tests_recovered = 0
        retry_history = []
        
        for attempt in range(1, self.max_retries + 1):
            if results.failed == 0:
                break  # All tests passed
            
            self.logger.warning(
                f"[Retry] Attempt {attempt}/{self.max_retries}: "
                f"Retrying {results.failed} failed tests"
            )
            
            # Wait before retry
            if self.delay > 0:
                time.sleep(self.delay)
            
            # Retry with same runner
            retry_results = self._runner.run(tests)
            retries_attempted += 1
            
            # Check if any tests recovered
            if retry_results.failed < results.failed:
                recovered = results.failed - retry_results.failed
                tests_recovered += recovered
                self.logger.info(
                    f"[Retry] ✓ {recovered} tests recovered on attempt {attempt}"
                )
            
            retry_history.append({
                'attempt': attempt,
                'failed': retry_results.failed,
                'recovered': results.failed - retry_results.failed
            })
            
            # Update results
            results = retry_results
        
        # Add retry metadata
        results.metadata['retries'] = {
            'attempted': retries_attempted,
            'recovered': tests_recovered,
            'history': retry_history,
            'final_failures': results.failed
        }
        
        if tests_recovered > 0:
            self.logger.info(
                f"[Retry] Successfully recovered {tests_recovered} tests after retries"
            )
        else:
            self.logger.warning(
                f"[Retry] No tests recovered after {retries_attempted} retry attempts"
            )
        
        return results