"""
CSN Validation Module
====================
Provides CSN (Core Schema Notation) validation and retrieval from SAP Discovery API.

Exports:
- csn_validation_api: Flask blueprint for CSN routes
"""

from .api import csn_validation_api

__all__ = ['csn_validation_api']