"""
Data Products Module - Backend Package

Provides data products viewing and management services.

Exports:
    - SQLiteDataProductsService: Low-level SQLite service for data products
    - data_products_api: Flask blueprint for REST API endpoints

Note: SQLiteDataSource moved to sqlite_connection module (infrastructure layer)
"""

from .sqlite_data_products_service import SQLiteDataProductsService
from .api import data_products_api

__all__ = ['SQLiteDataProductsService', 'data_products_api']
