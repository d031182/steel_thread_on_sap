"""
Feng Shui Preview Mode - Proactive Architecture Validation

Validates architecture DURING planning phase, before implementation starts.
Catches 80%+ violations before coding begins.

Usage:
    python -m tools.fengshui preview --module [name]
    python -m tools.fengshui preview --design-doc path/to/design.md
"""

from .engine import PreviewEngine
from .validators import (
    NamingValidator,
    StructureValidator,
    IsolationValidator,
    DependencyValidator,
    PatternValidator
)

__all__ = [
    'PreviewEngine',
    'NamingValidator',
    'StructureValidator',
    'IsolationValidator',
    'DependencyValidator',
    'PatternValidator'
]