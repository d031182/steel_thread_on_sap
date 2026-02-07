"""
Shi Fu Pattern Library
======================

Known correlation patterns between code quality (Feng Shui) and test quality (Gu Wu).

Each pattern detector:
1. Analyzes data from both disciples
2. Identifies specific correlation
3. Calculates confidence score
4. Provides actionable recommendation
"""

from .base_pattern import BasePattern
from .di_flakiness import DIFlakinessPattern
from .complexity_coverage import ComplexityCoveragePattern
from .security_gaps import SecurityGapsPattern
from .performance_timing import PerformanceTimingPattern
from .module_health import ModuleHealthPattern

__all__ = [
    'BasePattern',
    'DIFlakinessPattern',
    'ComplexityCoveragePattern',
    'SecurityGapsPattern',
    'PerformanceTimingPattern',
    'ModuleHealthPattern',
]