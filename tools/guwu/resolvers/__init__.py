"""
Gu Wu Resolvers - Multi-Capability Issue Resolution

Gu Wu expands beyond test generation to resolve various quality issues
detected by Feng Shui and other agents.

Philosophy: "Attending to Martial Affairs" - Self-healing codebase
"""

from .base_resolver import BaseResolver, ResolutionResult, ResolutionStatus
from .resolver_registry import ResolverRegistry

__all__ = [
    'BaseResolver',
    'ResolutionResult',
    'ResolutionStatus',
    'ResolverRegistry',
]