"""
Data Products V2 Backend Module

Exports the Flask blueprint for registration with the main app.
Follows modular blueprint architecture.

Author: P2P Development Team
Version: 2.0.0
Date: 2026-02-08
"""

from modules.data_products_v2.backend.api import data_products_v2_api

__all__ = ['data_products_v2_api']