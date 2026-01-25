"""
Core Interfaces

Shared abstract base classes for modular architecture.
All modules implement these interfaces for interoperability.
"""

from .data_source import DataSource
from .logger import ApplicationLogger

__all__ = ['DataSource', 'ApplicationLogger']