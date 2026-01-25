"""
Data Products Module - Backend Package

Provides SQLite-based data products storage and retrieval services.

Exports:
    - SQLiteDataProductsService: Low-level SQLite service
    - SQLiteDataSource: DataSource interface implementation
"""

from .sqlite_data_products_service import SQLiteDataProductsService
from .sqlite_data_source import SQLiteDataSource

__all__ = ['SQLiteDataProductsService', 'SQLiteDataSource']