"""
Unit tests for Gu Wu Decorator Pattern implementation

Tests the GoF Decorator pattern for composable test runner capabilities.
Validates that decorators can be stacked and work independently.
"""

import sys
import io
import time
import pytest
import logging
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path

# Add project root to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from tools.guwu.decorators.base import (
    TestRunner,
    BasicTestRunner,
    TestRunnerDecorator,
    TestResults
)
from tools.guwu.decorators.timing import TimingDecorator
from tools.guwu.decorators.logging import LoggingDecorator
from tools.guwu.decorators.retry import RetryDecorator
from tools.guwu.decorators.metrics import MetricsDecorator


# ============================================================================
# Test Fixtures
# ============================================================================

@pytest.fixture
def mock_runner():
    """Create a mock test runner"""
    runner = Mock(spec=TestRunner)
    runner.run.return_value = TestResults(
        total=5,
        passed=5,
        failed=0,
        duration=2.5
    )
    runner.get_runner_name.return_value = "MockRunner"
    return runner


@pytest.fixture
def basic_runner():
    """Create a basic test runner"""
    return BasicTestRunner(verbose=False)


@pytest.fixture
def failing_runner():
    """Create a runner that always fails"""
    runner = Mock(spec=TestRunner)
    runner.run.return_value = TestResults(
        total=3,
        passed=0,
        failed=3,
        failed_tests=['test_1', 'test_2', 'test_3'],
        duration=1.5
    )
    runner.get_runner_name.return_value = "FailingMockRunner"
    return runner


# ============================================================================
# TestResults Tests
# ============================================================================

@pytest.mark.unit
@pytest.mark.fast
class TestTestResults:
    """Test TestResults dataclass"""
    
    def test_pass_rate_calculation(self):
        """Test pass rate calculation"""
        # ARRANGE
        results = TestResults(total=10, passed=8, failed=2)
        
        # ACT & ASSERT
        assert results.pass_rate == 80.0
    
    def test_pass_rate_zero_tests(self):
        """Test pass rate with zero tests"""
        # ARRANGE
        results = TestResults(total=0, passed=0, failed=0)
        
        # ACT & ASSERT
        assert results.pass_rate == 0.0
    
    def test_success_property_all_passed(self):
        """Test success property when all tests passed"""
        # ARRANGE
        results = TestResults(total=5, passed=5, failed=0)
        
        # ACT & ASSERT
        assert results.success is True
    
    def test_success_property_some_failed(self):
        """Test success property when some tests failed"""
        # ARRANGE
        results = TestResults(total=5, passed=3, failed=2)
        
        # ACT & ASSERT
        assert results.success is False
    
    def test_success_property_no_tests(self):
        """Test success property with no tests"""
        # ARRANGE
        results = TestResults(total=0, passed=0, failed=0)
        
        # ACT & ASSERT
        assert results.success is False
    
    def test_str_representation(self):
        """Test string representation"""
        # ARRANGE
        results = TestResults(total=10, passed=8, failed=2, skipped=0, duration=5.5)
        
        # ACT
        result_str = str(results)
        
        # ASSERT
        assert 'total=10' in result_str
        assert 'passed=8' in result_str
        assert 'failed=2' in result_str
        assert 'pass_rate=80.0%' in result_str
        assert 'duration=5.50s' in result_str


# ============================================================================
# BasicTestRunner Tests
# ============================================================================

@pytest.mark.unit
@pytest.mark.fast
class TestBasicTestRunner:
    """Test BasicTestRunner (ConcreteComponent)"""
    
    def test_empty_test_list(self):
        """Test running with empty test list"""
        # ARRANGE
        runner = BasicTestRunner()
        
        # ACT
        results = runner.run([])
        
        # ASSERT
        assert results.total == 0
        assert results.passed == 0
        assert results.failed == 0
        assert results.duration == 0.0
    
    def test_get_runner_name(self):
        """Test runner name"""
        # ARRANGE
        runner = BasicTestRunner()
        
        # ACT & ASSERT
        assert runner.get_runner_name() == "BasicTestRunner"
    
    def test_verbose_mode(self):
        """Test verbose mode initialization"""
        # ARRANGE & ACT
        runner = BasicTestRunner(verbose=True)
        
        # ASSERT
        assert runner.verbose is True


# ============================================================================
# TestRunnerDecorator Tests
# ============================================================================

@pytest.mark.unit
@pytest.mark.fast
class TestTestRunnerDecorator:
    """Test TestRunnerDecorator base class"""
    
    def test_delegates_to_wrapped_runner(self, mock_runner):
        """Test that decorator delegates to wrapped runner"""
        # ARRANGE
        decorator = TestRunnerDecorator(mock_runner)
        tests = ['test_1.py', 'test_2.py']
        
        # ACT
        results = decorator.run(tests)
        
        # ASSERT
        mock_runner.run.assert_called_once_with(tests)
        assert results.total == 5
        assert results.passed == 5
    
    def test_get_runner_name_shows_chain(self, mock_runner):
        """Test that get_runner_name shows decorator chain"""
        # ARRANGE
        decorator = TestRunnerDecorator(mock_runner)
        
        # ACT
        name = decorator.get_runner_name()
        
        # ASSERT
        assert 'TestRunnerDecorator' in name
        assert 'MockRunner' in name
    
    def test_wrapped_runner_property(self, mock_runner):
        """Test access to wrapped runner"""
        # ARRANGE
        decorator = TestRunnerDecorator(mock_runner)
        
        # ACT
        wrapped = decorator.wrapped_runner
        
        # ASSERT
        assert wrapped is mock_runner


# ============================================================================
# TimingDecorator Tests
# ============================================================================

@pytest.mark.unit
@pytest.mark.fast
class TestTimingDecorator:
    """Test TimingDecorator"""
    
    def test_adds_timing_metadata(self, mock_runner):
        """Test that timing decorator adds timing metadata"""
        # ARRANGE
        decorator = TimingDecorator(mock_runner)
        tests = ['test_1.py']
        
        # ACT
        results = decorator.run(tests)
        
        # ASSERT
        assert 'timing' in results.metadata
        assert 'total_time' in results.metadata['timing']
        assert 'execution_time' in results.metadata['timing']
        assert 'avg_time_per_test' in results.metadata['timing']
    
    def test_timing_accuracy(self, mock_runner):
        """Test timing measurements are accurate"""
        # ARRANGE
        decorator = TimingDecorator(mock_runner)
        tests = ['test_1.py']
        
        # ACT
        start = time.time()
        results = decorator.run(tests)
        actual_duration = time.time() - start
        
        # ASSERT
        timing = results.metadata['timing']
        assert timing['total_time'] <= actual_duration + 0.1  # Allow 100ms tolerance
        assert timing['total_time'] >= 0  # May be 0 on fast systems
    
    def test_avg_time_per_test(self, mock_runner):
        """Test average time per test calculation"""
        # ARRANGE
        mock_runner.run.return_value = TestResults(
            total=10,
            passed=10,
            failed=0,
            duration=5.0
        )
        decorator = TimingDecorator(mock_runner)
        tests = ['test_' + str(i) for i in range(10)]
        
        # ACT
        results = decorator.run(tests)
        
        # ASSERT
        avg_time = results.metadata['timing']['avg_time_per_test']
        assert avg_time >= 0  # May be 0 on fast systems
        assert 'tests_per_second' in results.metadata['timing']


# ============================================================================
# LoggingDecorator Tests
# ============================================================================

@pytest.mark.unit
@pytest.mark.fast
class TestLoggingDecorator:
    """Test LoggingDecorator"""
    
    def test_logs_execution_start_and_end(self, mock_runner, caplog):
        """Test that logging decorator logs start and end"""
        # ARRANGE
        caplog.set_level(logging.INFO)
        decorator = LoggingDecorator(mock_runner, log_level=logging.INFO)
        tests = ['test_1.py']
        
        # ACT
        results = decorator.run(tests)
        
        # ASSERT
        log_messages = [record.message for record in caplog.records]
        assert any('Test Execution Started' in msg for msg in log_messages)
        assert any('Test Execution Completed' in msg for msg in log_messages)
    
    def test_logs_failures(self, failing_runner, caplog):
        """Test that failures are logged"""
        # ARRANGE
        caplog.set_level(logging.INFO)
        decorator = LoggingDecorator(failing_runner, log_level=logging.INFO)
        tests = ['test_1.py']
        
        # ACT
        results = decorator.run(tests)
        
        # ASSERT
        log_messages = [record.message for record in caplog.records]
        assert any('TESTS FAILED' in msg for msg in log_messages)
    
    def test_log_failures_only_mode(self, mock_runner, caplog):
        """Test log_failures_only mode"""
        # ARRANGE
        caplog.set_level(logging.INFO)
        decorator = LoggingDecorator(
            mock_runner,
            log_level=logging.INFO,
            log_failures_only=True
        )
        tests = ['test_1.py']
        
        # ACT
        results = decorator.run(tests)
        
        # ASSERT - Should not log completion for passing tests
        log_messages = [record.message for record in caplog.records]
        completion_logs = [msg for msg in log_messages if 'Test Execution Completed' in msg]
        assert len(completion_logs) == 0
    
    def test_exception_handling(self, caplog):
        """Test that exceptions are logged"""
        # ARRANGE
        caplog.set_level(logging.ERROR)
        failing_mock = Mock(spec=TestRunner)
        failing_mock.run.side_effect = RuntimeError("Test execution failed")
        decorator = LoggingDecorator(failing_mock)
        
        # ACT & ASSERT
        with pytest.raises(RuntimeError):
            decorator.run(['test_1.py'])
        
        # Check error was logged
        assert any('Test execution failed' in record.message for record in caplog.records)


# ============================================================================
# RetryDecorator Tests
# ============================================================================

@pytest.mark.unit
@pytest.mark.fast
class TestRetryDecorator:
    """Test RetryDecorator"""
    
    def test_no_retry_when_all_pass(self, mock_runner):
        """Test no retries when all tests pass"""
        # ARRANGE
        decorator = RetryDecorator(mock_runner, max_retries=2, delay=0)
        tests = ['test_1.py']
        
        # ACT
        results = decorator.run(tests)
        
        # ASSERT
        assert results.metadata['retries']['attempted'] == 0
        assert results.metadata['retries']['recovered'] == 0
        assert mock_runner.run.call_count == 1  # Only called once
    
    def test_retries_on_failure(self, failing_runner):
        """Test retries when tests fail"""
        # ARRANGE
        decorator = RetryDecorator(failing_runner, max_retries=2, delay=0)
        tests = ['test_1.py']
        
        # ACT
        results = decorator.run(tests)
        
        # ASSERT
        assert results.metadata['retries']['attempted'] == 2
        assert failing_runner.run.call_count == 3  # 1 initial + 2 retries
    
    def test_stops_retry_on_success(self):
        """Test that retry stops when tests pass"""
        # ARRANGE
        mock = Mock(spec=TestRunner)
        # First call fails, second call passes
        mock.run.side_effect = [
            TestResults(total=3, passed=0, failed=3, duration=1.0),
            TestResults(total=3, passed=3, failed=0, duration=1.0)
        ]
        mock.get_runner_name.return_value = "MockRunner"
        
        decorator = RetryDecorator(mock, max_retries=5, delay=0)
        tests = ['test_1.py']
        
        # ACT
        results = decorator.run(tests)
        
        # ASSERT
        assert results.passed == 3
        assert results.failed == 0
        assert mock.run.call_count == 2  # Stopped after success
        assert results.metadata['retries']['attempted'] == 1
        assert results.metadata['retries']['recovered'] == 3
    
    def test_delay_between_retries(self, failing_runner):
        """Test delay between retry attempts"""
        # ARRANGE
        decorator = RetryDecorator(failing_runner, max_retries=2, delay=0.1)
        tests = ['test_1.py']
        
        # ACT
        start = time.time()
        results = decorator.run(tests)
        duration = time.time() - start
        
        # ASSERT
        # Should have 2 delays of 0.1s each
        assert duration >= 0.2  # At least 200ms for delays


# ============================================================================
# MetricsDecorator Tests
# ============================================================================

@pytest.mark.unit
@pytest.mark.fast
class TestMetricsDecorator:
    """Test MetricsDecorator"""
    
    def test_adds_metrics_metadata(self, mock_runner):
        """Test that metrics decorator adds metadata"""
        # ARRANGE
        mock_metrics = Mock()
        decorator = MetricsDecorator(mock_runner, metrics_collector=mock_metrics)
        tests = ['test_1.py']
        
        # ACT
        results = decorator.run(tests)
        
        # ASSERT
        assert 'metrics' in results.metadata
        assert 'session_id' in results.metadata['metrics']
        assert results.metadata['metrics']['collected'] is True
    
    def test_handles_missing_metrics_collector(self, mock_runner):
        """Test graceful handling when metrics collector unavailable"""
        # ARRANGE
        decorator = MetricsDecorator(mock_runner)
        tests = ['test_1.py']
        
        # ACT
        results = decorator.run(tests)
        
        # ASSERT - Should work gracefully even without metrics
        assert results.total == 5
        # When GuWuMetrics unavailable, metadata won't be added (graceful degradation)
    
    def test_session_id_generation(self, mock_runner):
        """Test session ID generation"""
        # ARRANGE
        mock_metrics = Mock()
        decorator = MetricsDecorator(mock_runner, metrics_collector=mock_metrics)
        
        # ACT
        session_id = decorator._generate_session_id()
        
        # ASSERT
        assert isinstance(session_id, str)
        assert len(session_id) == 8  # UUID first 8 chars


# ============================================================================
# Decorator Stacking Tests
# ============================================================================

@pytest.mark.unit
@pytest.mark.fast
class TestDecoratorStacking:
    """Test that multiple decorators can be stacked"""
    
    def test_stack_timing_and_logging(self, mock_runner, caplog):
        """Test stacking Timing + Logging decorators"""
        # ARRANGE
        caplog.set_level(logging.INFO)
        runner = mock_runner
        runner = TimingDecorator(runner)
        runner = LoggingDecorator(runner)
        tests = ['test_1.py']
        
        # ACT
        results = runner.run(tests)
        
        # ASSERT
        assert 'timing' in results.metadata
        log_messages = [record.message for record in caplog.records]
        assert any('Test Execution Started' in msg for msg in log_messages)
    
    def test_stack_all_four_decorators(self, mock_runner):
        """Test stacking all 4 decorators"""
        # ARRANGE
        mock_metrics = Mock()
        runner = mock_runner
        runner = TimingDecorator(runner)
        runner = LoggingDecorator(runner)
        runner = RetryDecorator(runner, max_retries=1, delay=0)
        runner = MetricsDecorator(runner, metrics_collector=mock_metrics)
        tests = ['test_1.py']
        
        # ACT
        results = runner.run(tests)
        
        # ASSERT
        assert 'timing' in results.metadata
        assert 'retries' in results.metadata
        assert 'metrics' in results.metadata
        assert results.total == 5
    
    def test_decorator_order_matters(self):
        """Test that decorator order affects behavior"""
        # ARRANGE
        mock = Mock(spec=TestRunner)
        mock.run.return_value = TestResults(total=3, passed=0, failed=3, duration=1.0)
        mock.get_runner_name.return_value = "MockRunner"
        
        # Order 1: Retry → Timing
        runner1 = mock
        runner1 = RetryDecorator(runner1, max_retries=1, delay=0)
        runner1 = TimingDecorator(runner1)
        
        # Order 2: Timing → Retry
        mock2 = Mock(spec=TestRunner)
        mock2.run.return_value = TestResults(total=3, passed=0, failed=3, duration=1.0)
        mock2.get_runner_name.return_value = "MockRunner"
        runner2 = mock2
        runner2 = TimingDecorator(runner2)
        runner2 = RetryDecorator(runner2, max_retries=1, delay=0)
        
        # ACT
        results1 = runner1.run(['test_1.py'])
        results2 = runner2.run(['test_1.py'])
        
        # ASSERT
        # Both should have timing and retry metadata
        assert 'timing' in results1.metadata
        assert 'retries' in results1.metadata
        assert 'timing' in results2.metadata
        assert 'retries' in results2.metadata
    
    def test_get_runner_name_chain(self, mock_runner):
        """Test runner name shows full decorator chain"""
        # ARRANGE
        runner = mock_runner
        runner = TimingDecorator(runner)
        runner = LoggingDecorator(runner)
        runner = RetryDecorator(runner, max_retries=1, delay=0)
        
        # ACT
        name = runner.get_runner_name()
        
        # ASSERT
        assert 'RetryDecorator' in name
        assert 'LoggingDecorator' in name
        assert 'TimingDecorator' in name
        assert 'MockRunner' in name


# ============================================================================
# Integration Tests
# ============================================================================

@pytest.mark.unit
@pytest.mark.fast
class TestDecoratorIntegration:
    """Test decorator integration scenarios"""
    
    def test_ci_cd_configuration(self, mock_runner):
        """Test typical CI/CD decorator stack"""
        # ARRANGE - Full CI/CD stack
        mock_metrics = Mock()
        runner = mock_runner
        runner = TimingDecorator(runner)
        runner = LoggingDecorator(runner, log_level=logging.INFO)
        runner = MetricsDecorator(runner, metrics_collector=mock_metrics)
        tests = ['test_1.py', 'test_2.py']
        
        # ACT
        results = runner.run(tests)
        
        # ASSERT
        assert results.success
        assert 'timing' in results.metadata
        assert 'metrics' in results.metadata
    
    def test_development_configuration(self, mock_runner):
        """Test typical development decorator stack (minimal)"""
        # ARRANGE - Just timing for quick feedback
        runner = mock_runner
        runner = TimingDecorator(runner)
        tests = ['test_1.py']
        
        # ACT
        results = runner.run(tests)
        
        # ASSERT
        assert 'timing' in results.metadata
        assert 'retries' not in results.metadata  # No retry in dev
        assert 'metrics' not in results.metadata  # No metrics in dev
    
    def test_flaky_test_configuration(self):
        """Test configuration for handling flaky tests"""
        # ARRANGE - Retry + Logging
        mock = Mock(spec=TestRunner)
        # Simulates flaky test: fail → pass
        mock.run.side_effect = [
            TestResults(total=1, passed=0, failed=1, duration=0.5),
            TestResults(total=1, passed=1, failed=0, duration=0.5)
        ]
        mock.get_runner_name.return_value = "MockRunner"
        
        runner = mock
        runner = RetryDecorator(runner, max_retries=2, delay=0)
        runner = LoggingDecorator(runner, log_level=logging.WARNING, log_failures_only=True)
        
        # ACT
        results = runner.run(['test_flaky.py'])
        
        # ASSERT
        assert results.passed == 1
        assert results.failed == 0
        assert results.metadata['retries']['recovered'] == 1


if __name__ == '__main__':
    pytest.main([__file__, '-v'])