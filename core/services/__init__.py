"""
Core Services
=============
Core infrastructure services for the application.

Exports:
    - ModuleRegistry: Module discovery and management
    - ModuleLoader: Blueprint loading with error handling
    - PathResolver: Configuration-driven path resolution
    - GraphQueryService: Unified graph query facade (HANA + NetworkX)
    - NetworkXGraphQueryEngine: SQLite-based graph engine (deprecated)
    - HANAGraphQueryEngine: HANA Property Graph engine
    - GraphCacheService: Unified graph caching (replaces OntologyPersistenceService)
"""

from .module_registry import ModuleRegistry
from .module_loader import ModuleLoader
from .path_resolver import PathResolver
from .graph_query_service import GraphQueryService
from .networkx_graph_query_engine import NetworkXGraphQueryEngine
from .hana_graph_query_engine import HANAGraphQueryEngine
from .graph_cache_service import GraphCacheService

__all__ = [
    'ModuleRegistry',
    'ModuleLoader',
    'PathResolver',
    'GraphQueryService',
    'NetworkXGraphQueryEngine',
    'HANAGraphQueryEngine',
    'GraphCacheService'
]