"""
Data Products Module - Backend Package

Provides SQLite-based data products storage and retrieval services.

Exports:
    - SQLiteDataProductsService: Low-level SQLite service
    - SQLiteDataSource: DataSource interface implementation
    - data_products_api: Flask blueprint for REST API endpoints
"""

from .sqlite_data_products_service import SQLiteDataProductsService
from .sqlite_data_source import SQLiteDataSource
from .api import data_products_api

__all__ = ['SQLiteDataProductsService', 'SQLiteDataSource', 'data_products_api']
