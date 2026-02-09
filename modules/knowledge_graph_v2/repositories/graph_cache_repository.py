"""
Graph Cache Repository Interface

Abstract base class for graph caching implementations.
Follows Repository Pattern (Cosmic Python Ch 2).
"""
from abc import ABC, abstractmethod
from typing import Optional
from ..domain import Graph, GraphType


class AbstractGraphCacheRepository(ABC):
    """
    Repository interface for graph caching
    
    Provides abstraction over persistence layer.
    Implementations: SqliteGraphCacheRepository, InMemoryGraphCacheRepository (for testing)
    """
    
    @abstractmethod
    def save(self, graph: Graph) -> None:
        """
        Save graph to cache
        
        Args:
            graph: Graph to save
            
        Raises:
            RepositoryError: If save fails
        """
        pass
    
    @abstractmethod
    def get(self, graph_id: str, graph_type: GraphType) -> Optional[Graph]:
        """
        Retrieve graph from cache
        
        Args:
            graph_id: Identifier of graph (e.g., schema name, product name)
            graph_type: Type of graph (SCHEMA, DATA, CSN)
            
        Returns:
            Graph if found, None otherwise
        """
        pass
    
    @abstractmethod
    def exists(self, graph_id: str, graph_type: GraphType) -> bool:
        """
        Check if graph exists in cache
        
        Args:
            graph_id: Identifier of graph
            graph_type: Type of graph
            
        Returns:
            True if cached, False otherwise
        """
        pass
    
    @abstractmethod
    def delete(self, graph_id: str, graph_type: GraphType) -> bool:
        """
        Delete graph from cache
        
        Args:
            graph_id: Identifier of graph
            graph_type: Type of graph
            
        Returns:
            True if deleted, False if not found
        """
        pass
    
    @abstractmethod
    def clear_all(self) -> int:
        """
        Clear all cached graphs
        
        Returns:
            Number of graphs deleted
        """
        pass


class RepositoryError(Exception):
    """Raised when repository operations fail"""
    pass