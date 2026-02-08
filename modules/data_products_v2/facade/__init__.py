"""
Data Products V2 - Facade Layer

This module provides the business logic layer for Data Products V2.
Uses the Facade pattern to orchestrate repository operations and
provide a clean API to the REST endpoints.
"""

from modules.data_products_v2.facade.data_products_facade import DataProductsFacade

__all__ = ['DataProductsFacade']