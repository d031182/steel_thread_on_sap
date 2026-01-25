"""
SQLite Connection Module
========================
SQLite database connection and data source management.

Provides a DataSource interface implementation for SQLite,
mirroring the HANA Connection module pattern.

Exports:
    - SQLiteDataSource: DataSource interface implementation
"""

from .sqlite_data_source import SQLiteDataSource

__all__ = ['SQLiteDataSource']