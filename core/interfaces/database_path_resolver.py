"""
Database Path Resolver Interface

Strategy pattern for resolving module database paths.
Enables different path resolution strategies for different environments.

@author P2P Development Team
@version 1.0.0 (v3.25 - Database Path Strategy Pattern)
@date 2026-02-05
"""

from abc import ABC, abstractmethod


class IDatabasePathResolver(ABC):
    """
    Strategy interface for resolving database paths for modules.
    
    Different implementations can provide:
    - Module-owned paths (production)
    - Shared paths (legacy/testing)
    - Configurable paths (development)
    - Cloud storage paths (enterprise)
    
    Benefits:
    - Testability: Inject mock resolvers in tests
    - Flexibility: Swap strategies without code changes
    - SoC: Each strategy has single responsibility
    """
    
    @abstractmethod
    def resolve_path(self, module_name: str) -> str:
        """
        Resolve database path for given module.
        
        Args:
            module_name: Name of module (e.g., "knowledge_graph", "data_products")
            
        Returns:
            Absolute or relative path to database file
            
        Example:
            resolver = ModuleOwnedPathResolver()
            path = resolver.resolve_path("knowledge_graph")
            # Returns: "modules/knowledge_graph/database/graph_cache.db"
        """
        pass