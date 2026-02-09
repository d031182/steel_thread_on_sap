"""
Core API Package
================

Provides core API endpoints that are not module-specific.

Currently includes:
- Frontend Module Registry API: Auto-discovery for frontend modules

@author P2P Development Team
@version 1.0.0
"""

from core.api.frontend_registry import frontend_registry_bp

__all__ = ['frontend_registry_bp']