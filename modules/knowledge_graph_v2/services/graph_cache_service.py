"""
Graph Cache Service

Orchestrates graph caching with automatic rebuild capability.
This is the KEY service that provides cache resilience.

Key Features:
- Automatic rebuild if cache missing/corrupted
- Force rebuild capability (manual refresh)
- Orchestrates builders + repository
- Returns generic Graph domain objects
"""
import logging
from typing import Optional

from ..domain import Graph, GraphType
from ..repositories import AbstractGraphCacheRepository
from .schema_graph_builder_service import SchemaGraphBuilderService

logger = logging.getLogger(__name__)


class GraphCacheService:
    """
    Service for caching graphs with automatic rebuild capability
    
    This service solves the problem: "What if cache is deleted/corrupted?"
    Answer: Automatically rebuild from source!
    
    Responsibilities:
    - Check cache first (fast path)
    - Rebuild if cache miss (slow path)
    - Force rebuild on demand
    - Orchestrate builder + repository
    
    Does NOT:
    - Build graphs directly (delegates to builders)
    - Format for vis.js (returns generic domain objects)
    """
    
    def __init__(
        self,
        cache_repository: AbstractGraphCacheRepository,
        schema_builder: SchemaGraphBuilderService,
        data_builder=None  # Optional: DataGraphBuilderService (Phase 2B)
    ):
        """
        Initialize with injected dependencies
        
        Args:
            cache_repository: Repository for graph persistence
            schema_builder: Builder for schema graphs
            data_builder: Builder for data graphs (optional, future)
        """
        self.cache_repo = cache_repository
        self.schema_builder = schema_builder
        self.data_builder = data_builder
        logger.info("GraphCacheService initialized")
    
    def get_or_rebuild_schema_graph(self) -> Graph:
        """
        Get schema graph from cache, rebuild if missing/corrupted
        
        This is the PRIMARY method for your use case!
        
        Flow:
        1. Try to load from cache (fast: ~60ms)
        2. If found → return cached graph
        3. If not found → rebuild from CSN → save to cache → return
        4. If corrupted → rebuild from CSN → save to cache → return
        
        Returns:
            Graph: Schema graph (either cached or freshly built)
        
        Raises:
            Exception: If rebuild fails (CSN issues, etc.)
        """
        graph_id = 'schema'
        graph_type = GraphType.SCHEMA
        
        try:
            logger.info("Attempting to load schema graph from cache...")
            
            # Try cache first (fast path)
            cached_graph = self.cache_repo.get(graph_id, graph_type)
            
            if cached_graph:
                logger.info(f"✓ Cache HIT: Loaded schema graph from cache ({len(cached_graph.nodes)} nodes)")
                return cached_graph
            
            # Cache miss - rebuild (slow path)
            logger.info("Cache MISS: Schema graph not in cache, rebuilding from CSN...")
            return self._rebuild_and_cache_schema()
            
        except Exception as e:
            # Cache corrupted - rebuild (recovery path)
            logger.warning(f"Cache READ failed ({e}), rebuilding from CSN...")
            return self._rebuild_and_cache_schema()
    
    def force_rebuild_schema(self) -> Graph:
        """
        Force rebuild schema graph (ignore cache)
        
        Use cases:
        - CSN files updated (schema changed)
        - Manual refresh requested by user
        - Cache suspected to be stale
        
        Flow:
        1. Delete old cache (if exists)
        2. Rebuild from CSN
        3. Save to cache
        4. Return fresh graph
        
        Returns:
            Graph: Freshly built schema graph
        
        Raises:
            Exception: If rebuild fails
        """
        logger.info("Force rebuild: Deleting old cache and rebuilding from CSN...")
        
        # Delete old cache
        graph_id = 'schema'
        graph_type = GraphType.SCHEMA
        
        if self.cache_repo.exists(graph_id, graph_type):
            deleted = self.cache_repo.delete(graph_id, graph_type)
            if deleted:
                logger.info("✓ Deleted old schema cache")
        
        # Rebuild and cache
        return self._rebuild_and_cache_schema()
    
    def _rebuild_and_cache_schema(self) -> Graph:
        """
        Internal: Rebuild schema graph from CSN and save to cache
        
        Returns:
            Graph: Freshly built and cached schema graph
        
        Raises:
            Exception: If build or save fails
        """
        try:
            # Build from CSN (slow: ~200-300ms)
            logger.info("Building schema graph from CSN...")
            fresh_graph = self.schema_builder.build_from_csn()
            
            stats = fresh_graph.get_statistics()
            logger.info(
                f"✓ Built schema graph: {stats['node_count']} nodes, "
                f"{stats['edge_count']} edges"
            )
            
            # Save to cache for next time
            logger.info("Saving schema graph to cache...")
            self.cache_repo.save(fresh_graph)
            logger.info("✓ Saved to cache")
            
            return fresh_graph
            
        except Exception as e:
            logger.error(f"Failed to rebuild schema graph: {e}", exc_info=True)
            raise
    
    def exists_in_cache(self, graph_id: str, graph_type: GraphType) -> bool:
        """
        Check if graph exists in cache (without loading it)
        
        Useful for cache status checks.
        
        Args:
            graph_id: ID of graph to check
            graph_type: Type of graph to check
            
        Returns:
            bool: True if cached, False otherwise
        """
        return self.cache_repo.exists(graph_id, graph_type)
    
    def clear_cache(self, graph_type: GraphType) -> bool:
        """
        Clear cache for specific graph type
        
        Administrative operation. Use with caution!
        
        Args:
            graph_type: Type of graphs to clear (SCHEMA or DATA)
            
        Returns:
            bool: True if cleared, False if nothing to clear
        """
        logger.warning(f"Clearing cache for graph type: {graph_type}")
        
        if graph_type == GraphType.SCHEMA:
            return self.cache_repo.delete('schema', graph_type)
        elif graph_type == GraphType.DATA:
            return self.cache_repo.delete('data', graph_type)
        else:
            logger.error(f"Unknown graph type: {graph_type}")
            return False
    
    # Future methods (Phase 2B - Data graphs)
    # def get_or_rebuild_data_graph(self) -> Graph:
    #     """Get data graph from cache, rebuild if missing"""
    #     pass
    # 
    # def force_rebuild_data(self) -> Graph:
    #     """Force rebuild data graph"""
    #     pass