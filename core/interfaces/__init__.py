"""
Core Interfaces

Shared abstract base classes for modular architecture.
All modules implement these interfaces for interoperability.
"""

from .i_logger import ILogger, LogLevel, NoOpLogger
from .database_path_resolver import IDatabasePathResolver
from .data_product_repository import IDataProductRepository, DataProduct, Table, Column

__all__ = [
    'ILogger', 
    'LogLevel', 
    'NoOpLogger',
    'IDatabasePathResolver',
    'IDataProductRepository',
    'DataProduct',
    'Table',
    'Column'
]
