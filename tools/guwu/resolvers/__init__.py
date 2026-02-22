"""
Gu Wu Resolvers - Multi-Capability Issue Resolution

Gu Wu expands beyond test generation to resolve various quality issues
detected by Feng Shui and other agents.

Philosophy: "Attending to Martial Affairs" - Self-healing codebase
"""

from .base_resolver import BaseResolver, ResolutionResult, ResolutionStatus
from .resolver_registry import ResolverRegistry

# Singleton instance
_registry_instance = None


def get_registry() -> ResolverRegistry:
    """
    Get the singleton resolver registry instance.
    
    Returns:
        ResolverRegistry: The global resolver registry
    """
    global _registry_instance
    if _registry_instance is None:
        _registry_instance = ResolverRegistry()
    return _registry_instance


__all__ = [
    'BaseResolver',
    'ResolutionResult',
    'ResolutionStatus',
    'ResolverRegistry',
    'get_registry',
]
