"""
Base classes for Test Runner Decorator Pattern

Implements the GoF Decorator pattern for composable test runner capabilities.
"""

import sys
import io
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from datetime import datetime


@dataclass
class TestResults:
    """Results from test execution"""
    total: int
    passed: int
    failed: int
    skipped: int = 0
    duration: float = 0.0
    timestamp: datetime = field(default_factory=datetime.now)
    failed_tests: List[str] = field(default_factory=list)
    skipped_tests: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    @property
    def pass_rate(self) -> float:
        """Calculate pass rate"""
        if self.total == 0:
            return 0.0
        return (self.passed / self.total) * 100
    
    @property
    def success(self) -> bool:
        """Check if all tests passed"""
        return self.failed == 0 and self.total > 0
    
    def __str__(self) -> str:
        return (
            f"TestResults(total={self.total}, passed={self.passed}, "
            f"failed={self.failed}, skipped={self.skipped}, "
            f"pass_rate={self.pass_rate:.1f}%, duration={self.duration:.2f}s)"
        )


class TestRunner(ABC):
    """Base test runner interface (Component in Decorator pattern)"""
    
    @abstractmethod
    def run(self, tests: List[str]) -> TestResults:
        """
        Run tests and return results
        
        Args:
            tests: List of test identifiers (file paths, test IDs, etc.)
            
        Returns:
            TestResults object with execution details
        """
        pass
    
    def get_runner_name(self) -> str:
        """Return runner identifier"""
        return self.__class__.__name__


class BasicTestRunner(TestRunner):
    """
    Core test execution without enhancements (ConcreteComponent)
    
    This is the basic runner that actually executes tests via pytest.
    All decorators wrap this core runner.
    """
    
    def __init__(self, verbose: bool = False):
        """
        Initialize basic runner
        
        Args:
            verbose: Enable verbose pytest output
        """
        self.verbose = verbose
    
    def run(self, tests: List[str]) -> TestResults:
        """
        Execute tests using pytest
        
        Args:
            tests: List of test file paths or test IDs
            
        Returns:
            TestResults with execution details
        """
        import pytest
        import time
        
        if not tests:
            return TestResults(
                total=0,
                passed=0,
                failed=0,
                skipped=0,
                duration=0.0
            )
        
        # Prepare pytest arguments
        args = tests.copy()
        if self.verbose:
            args.append('-v')
        
        # Capture output
        start_time = time.time()
        
        # Run pytest and capture result
        result_code = pytest.main(args)
        
        duration = time.time() - start_time
        
        # Parse pytest exit code
        # 0: All tests passed
        # 1: Tests failed
        # 2: Test execution interrupted
        # 3: Internal error
        # 4: pytest command line usage error
        # 5: No tests collected
        
        if result_code == 0:
            # All passed
            return TestResults(
                total=len(tests),
                passed=len(tests),
                failed=0,
                duration=duration
            )
        elif result_code == 1:
            # Some failed (we don't know exact count without parsing output)
            # This is a limitation of the basic runner
            return TestResults(
                total=len(tests),
                passed=0,  # Unknown
                failed=len(tests),  # Assume all failed (worst case)
                duration=duration,
                metadata={'result_code': result_code}
            )
        elif result_code == 5:
            # No tests collected
            return TestResults(
                total=0,
                passed=0,
                failed=0,
                duration=duration,
                metadata={'result_code': result_code, 'note': 'No tests collected'}
            )
        else:
            # Error or interrupted
            return TestResults(
                total=len(tests),
                passed=0,
                failed=len(tests),
                duration=duration,
                metadata={'result_code': result_code, 'error': True}
            )
    
    def get_runner_name(self) -> str:
        return "BasicTestRunner"


class TestRunnerDecorator(TestRunner):
    """
    Base decorator for test runner (Decorator base class)
    
    All concrete decorators inherit from this class and override run()
    to add their specific behavior before/after delegating to wrapped runner.
    """
    
    def __init__(self, runner: TestRunner):
        """
        Initialize decorator with wrapped runner
        
        Args:
            runner: The test runner to wrap (can be BasicTestRunner or another decorator)
        """
        self._runner = runner
    
    def run(self, tests: List[str]) -> TestResults:
        """
        Default implementation: delegate to wrapped runner
        
        Subclasses override this to add behavior before/after delegation.
        
        Args:
            tests: List of test identifiers
            
        Returns:
            TestResults from wrapped runner
        """
        return self._runner.run(tests)
    
    def get_runner_name(self) -> str:
        """Return decorator chain names"""
        return f"{self.__class__.__name__}({self._runner.get_runner_name()})"
    
    @property
    def wrapped_runner(self) -> TestRunner:
        """Access to wrapped runner (for inspection/testing)"""
        return self._runner