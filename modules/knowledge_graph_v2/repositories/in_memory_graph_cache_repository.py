"""
In-Memory Graph Cache Repository

Fake implementation for testing (no database required).
Follows Repository Pattern - enables fast unit tests.
"""
from typing import Dict, Tuple, Optional
from .graph_cache_repository import AbstractGraphCacheRepository, RepositoryError
from ..domain import Graph, GraphType


class InMemoryGraphCacheRepository(AbstractGraphCacheRepository):
    """
    In-memory graph cache repository for testing
    
    No database required - perfect for unit tests (0.001s execution).
    Stores graphs in memory dictionary.
    """
    
    def __init__(self):
        """Initialize in-memory storage"""
        self._storage: Dict[Tuple[str, str], Graph] = {}
    
    def save(self, graph: Graph) -> None:
        """
        Save graph to memory
        
        Args:
            graph: Graph to save
            
        Raises:
            RepositoryError: If save fails
        """
        try:
            key = self._make_key(graph.id, graph.type)
            self._storage[key] = graph
        except Exception as e:
            raise RepositoryError(f"Failed to save graph: {e}")
    
    def get(self, graph_id: str, graph_type: GraphType) -> Optional[Graph]:
        """
        Retrieve graph from memory
        
        Args:
            graph_id: Identifier of graph
            graph_type: Type of graph
            
        Returns:
            Graph if found, None otherwise
        """
        key = self._make_key(graph_id, graph_type)
        return self._storage.get(key)
    
    def exists(self, graph_id: str, graph_type: GraphType) -> bool:
        """
        Check if graph exists in memory
        
        Args:
            graph_id: Identifier of graph
            graph_type: Type of graph
            
        Returns:
            True if cached, False otherwise
        """
        key = self._make_key(graph_id, graph_type)
        return key in self._storage
    
    def delete(self, graph_id: str, graph_type: GraphType) -> bool:
        """
        Delete graph from memory
        
        Args:
            graph_id: Identifier of graph
            graph_type: Type of graph
            
        Returns:
            True if deleted, False if not found
        """
        key = self._make_key(graph_id, graph_type)
        if key in self._storage:
            del self._storage[key]
            return True
        return False
    
    def clear_all(self) -> int:
        """
        Clear all cached graphs
        
        Returns:
            Number of graphs deleted
        """
        count = len(self._storage)
        self._storage.clear()
        return count
    
    def _make_key(self, graph_id: str, graph_type: GraphType) -> Tuple[str, str]:
        """
        Create storage key from graph_id and graph_type
        
        Args:
            graph_id: Graph identifier
            graph_type: Graph type enum
            
        Returns:
            Tuple key for storage dict
        """
        return (graph_id, graph_type.value)