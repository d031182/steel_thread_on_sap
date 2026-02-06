"""
Logging Decorator - Adds comprehensive logging to test execution
"""

import logging
from typing import List
from datetime import datetime
from .base import TestRunnerDecorator, TestResults


class LoggingDecorator(TestRunnerDecorator):
    """
    Adds comprehensive logging (ConcreteDecorator)
    
    Logs:
    - Test execution start/end
    - Test results summary
    - Failure details
    - Performance warnings
    
    Example:
        runner = BasicTestRunner()
        runner = LoggingDecorator(runner, log_level=logging.INFO)
        results = runner.run(tests)
    """
    
    def __init__(self, runner, log_level: int = logging.INFO, log_failures_only: bool = False):
        """
        Initialize logging decorator
        
        Args:
            runner: Wrapped test runner
            log_level: Logging level (DEBUG, INFO, WARNING, ERROR)
            log_failures_only: Only log when tests fail
        """
        super().__init__(runner)
        self.log_level = log_level
        self.log_failures_only = log_failures_only
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(log_level)
    
    def run(self, tests: List[str]) -> TestResults:
        """
        Run tests with comprehensive logging
        
        Args:
            tests: List of test identifiers
            
        Returns:
            TestResults from wrapped runner
        """
        # BEFORE: Log test execution start
        self.logger.info("=" * 70)
        self.logger.info(f"[Gu Wu] Test Execution Started")
        self.logger.info(f"[Gu Wu] Timestamp: {datetime.now().isoformat()}")
        self.logger.info(f"[Gu Wu] Total Tests: {len(tests)}")
        self.logger.info("=" * 70)
        
        if self.logger.level <= logging.DEBUG:
            self.logger.debug(f"[Gu Wu] Test List: {tests}")
        
        # DELEGATE: Run wrapped runner
        try:
            results = self._runner.run(tests)
            
            # AFTER: Log results
            if not self.log_failures_only or results.failed > 0:
                self._log_results(results)
            
            return results
            
        except Exception as e:
            self.logger.error(f"[Gu Wu] Test execution failed with exception: {e}")
            self.logger.exception(e)
            raise
    
    def _log_results(self, results: TestResults):
        """Log test results summary"""
        self.logger.info("=" * 70)
        self.logger.info(f"[Gu Wu] Test Execution Completed")
        self.logger.info(f"[Gu Wu] {results}")
        self.logger.info("=" * 70)
        
        # Log success/failure status
        if results.success:
            self.logger.info(f"[Gu Wu] ✓ ALL TESTS PASSED")
        else:
            self.logger.warning(f"[Gu Wu] ✗ {results.failed} TESTS FAILED")
        
        # Log failed tests
        if results.failed_tests:
            self.logger.warning(f"[Gu Wu] Failed Tests:")
            for test in results.failed_tests:
                self.logger.warning(f"[Gu Wu]   - {test}")
        
        # Log skipped tests
        if results.skipped_tests:
            self.logger.info(f"[Gu Wu] Skipped Tests ({len(results.skipped_tests)}):")
            for test in results.skipped_tests:
                self.logger.info(f"[Gu Wu]   - {test}")
        
        # Log performance warnings
        if results.duration > 60:  # More than 1 minute
            self.logger.warning(
                f"[Gu Wu] ⚠ Test suite took {results.duration:.1f}s (consider optimization)"
            )
        
        self.logger.info("=" * 70)