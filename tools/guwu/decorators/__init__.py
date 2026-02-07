"""
Decorator Pattern Components for Gu Wu

Provides composable test runner capabilities following the GoF Decorator pattern.
Decorators can be stacked to add timing, logging, retry logic, etc. without
modifying the core test runner.
"""

from .base import (
    TestRunner,
    BasicTestRunner,
    TestRunnerDecorator,
    TestResults
)
from .timing import TimingDecorator
from .logging import LoggingDecorator
from .retry import RetryDecorator
from .metrics import MetricsDecorator

__all__ = [
    'TestRunner',
    'BasicTestRunner',
    'TestRunnerDecorator',
    'TestResults',
    'TimingDecorator',
    'LoggingDecorator',
    'RetryDecorator',
    'MetricsDecorator'
]