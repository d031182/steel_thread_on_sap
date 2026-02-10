"""
Core Interfaces

Shared abstract base classes for modular architecture.
All modules implement these interfaces for interoperability.

Naming Convention:
- Python interfaces use 'i_' prefix (i_logger.py, i_data_source.py)
- JavaScript interfaces use 'I' prefix (ILogger.js, IDataSource.js)
- Ensures cross-language consistency and clear identification
"""

from .i_data_source import DataSource
from .i_logger import ApplicationLogger
from .i_database_path_resolver import IDatabasePathResolver
from .i_data_product_repository import IDataProductRepository
from .i_graph import Graph
from .i_graph_query import GraphQuery
from .i_graph_cache import GraphCache
from .i_log_intelligence import LogIntelligence
from .i_relationship_discovery import RelationshipDiscovery

__all__ = [
    'DataSource',
    'ApplicationLogger', 
    'IDatabasePathResolver',
    'IDataProductRepository',
    'Graph',
    'GraphQuery',
    'GraphCache',
    'LogIntelligence',
    'RelationshipDiscovery'
]