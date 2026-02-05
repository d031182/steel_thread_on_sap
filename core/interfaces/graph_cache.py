"""
Graph Cache Interface

Strategy pattern for different graph cache implementations.
Enables runtime selection of cache backend (v5, Redis, Memcached, etc.)

Design Pattern: STRATEGY (GoF Behavioral Pattern)
Purpose: Define family of cache algorithms, make them interchangeable

@author P2P Development Team
@version 1.0.0
@since v3.24
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional, Tuple


class GraphCacheStrategy(ABC):
    """
    Abstract interface for graph cache operations
    
    Current Implementation:
    - GraphCacheServiceAdapter: Wraps GraphCacheService (v5 schema)
    
    Future Implementations:
    - RedisCacheAdapter: Distributed caching via Redis
    - MemcachedCacheAdapter: High-performance memory cache
    """
    
    @abstractmethod
    def save_graph(
        self, 
        nodes: List[Dict], 
        edges: List[Dict],
        graph_type: str,
        description: Optional[str] = None
    ) -> bool:
        """
        Save complete graph to cache
        
        Args:
            nodes: List of vis.js node objects
            edges: List of vis.js edge objects
            graph_type: 'schema', 'data', or 'csn'
            description: Optional description
        
        Returns:
            True if successful
        """
        pass
    
    @abstractmethod
    def load_graph(self, graph_type: str) -> Optional[Dict[str, Any]]:
        """
        Load graph from cache
        
        Args:
            graph_type: 'schema', 'data', or 'csn'
        
        Returns:
            Dict with 'nodes' and 'edges' keys, or None if cache miss
        """
        pass
    
    @abstractmethod
    def is_cache_valid(self, graph_type: str) -> bool:
        """
        Check if cache exists for graph type
        
        Args:
            graph_type: 'schema', 'data', or 'csn'
        
        Returns:
            True if cache exists
        """
        pass
    
    @abstractmethod
    def clear_cache(self, graph_type: Optional[str] = None) -> int:
        """
        Clear cache for graph type (or all)
        
        Args:
            graph_type: Specific type to clear, or None for all
        
        Returns:
            Number of records deleted
        """
        pass
    
    @abstractmethod
    def get_statistics(self) -> Dict[str, Any]:
        """
        Get cache statistics
        
        Returns:
            Dict with cache stats
        """
        pass