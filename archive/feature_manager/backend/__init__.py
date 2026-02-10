"""
Feature Manager Backend
=======================
Backend services for the Feature Manager module.

Exports:
    - FeatureFlags: Feature toggle service
    - feature_manager_api: Flask Blueprint with REST API
"""

from .feature_flags import FeatureFlags
from .api import feature_manager_api

__all__ = ['FeatureFlags', 'feature_manager_api']