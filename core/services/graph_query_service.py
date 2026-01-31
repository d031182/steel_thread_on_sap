"""
Graph Query Service - Unified Facade for Graph Operations

Provides a single entry point for all graph query operations,
automatically selecting the appropriate backend (HANA or NetworkX)
based on the data source type.

This is the integration layer (Phase 4C) that completes the hybrid
graph system architecture.

@author P2P Development Team
@version 1.0.0
"""

import logging
from typing import List, Dict, Optional

from core.interfaces.graph_query import (
    IGraphQueryEngine,
    GraphNode,
    GraphPath,
    Subgraph,
    TraversalDirection
)
from core.interfaces.data_source import DataSource
from core.services.networkx_graph_query_engine import NetworkXGraphQueryEngine
from core.services.hana_graph_query_engine import HANAGraphQueryEngine

logger = logging.getLogger(__name__)


class GraphQueryService:
    """
    Unified graph query service with automatic backend selection.
    
    Architecture Pattern: Facade + Strategy
    - Facade: Single interface for all graph operations
    - Strategy: Selects appropriate engine based on data source
    
    Supported Backends:
    - HANAGraphQueryEngine: For HANA Cloud (10-100x faster)
    - NetworkXGraphQueryEngine: For SQLite (local development)
    
    Example:
        # Service auto-detects backend
        service = GraphQueryService(data_source, db_path='app/database/p2p.db')
        
        # Same API works with any backend
        neighbors = service.get_neighbors('PurchaseOrder:PO000001')
        path = service.shortest_path('Supplier:SUP001', 'Invoice:INV001')
        
        # Check which backend is being used
        print(service.get_backend_info())
    """
    
    def __init__(
        self,
        data_source: DataSource,
        db_path: Optional[str] = None,
        hana_workspace: str = 'P2P_GRAPH'
    ):
        """
        Initialize graph query service with automatic backend selection.
        
        Args:
            data_source: DataSource instance (HANADataSource or SQLiteDataSource)
            db_path: Path to SQLite database (for NetworkX backend)
            hana_workspace: HANA graph workspace name (default: P2P_GRAPH)
        """
        self.data_source = data_source
        self.db_path = db_path or 'app/database/p2p_data_products.db'
        self.hana_workspace = hana_workspace
        
        # Auto-select engine based on data source type
        self.engine = self._select_engine()
        
        # Log selection
        backend_name = type(self.engine).__name__
        logger.info(f"GraphQueryService initialized with {backend_name}")
        logger.info(f"  Data source: {type(data_source).__name__}")
        if 'HANA' in backend_name:
            logger.info(f"  HANA workspace: {hana_workspace}")
        else:
            logger.info(f"  SQLite database: {db_path}")
    
    def _select_engine(self) -> IGraphQueryEngine:
        """
        Auto-select graph query engine based on data source type.
        
        Selection Logic:
        - HANADataSource → HANAGraphQueryEngine (native HANA Property Graph)
        - SQLiteDataSource → NetworkXGraphQueryEngine (in-memory graph)
        - Other → NetworkXGraphQueryEngine (safe fallback)
        
        Returns:
            IGraphQueryEngine implementation
        """
        data_source_type = type(self.data_source).__name__
        
        # Check if HANA data source
        if 'HANA' in data_source_type or 'Hana' in data_source_type:
            logger.info("✓ Detected HANA data source → Using HANAGraphQueryEngine")
            try:
                return HANAGraphQueryEngine(
                    self.data_source,
                    self.hana_workspace
                )
            except Exception as e:
                logger.warning(f"Failed to create HANAGraphQueryEngine: {e}")
                logger.info("Falling back to NetworkXGraphQueryEngine")
                return NetworkXGraphQueryEngine(self.db_path)
        
        # Default: NetworkX (SQLite or unknown data source)
        logger.info("✓ Detected SQLite/local data source → Using NetworkXGraphQueryEngine")
        return NetworkXGraphQueryEngine(self.db_path)
    
    def get_backend_info(self) -> Dict[str, str]:
        """
        Get information about the active backend.
        
        Returns:
            Dict with backend name, type, and configuration
        """
        engine_type = type(self.engine).__name__
        
        info = {
            'backend': engine_type,
            'data_source': type(self.data_source).__name__,
        }
        
        if 'HANA' in engine_type:
            info['workspace'] = self.hana_workspace
            info['performance'] = '10-100x faster than NetworkX'
            info['platform'] = 'HANA Cloud Property Graph'
        else:
            info['database'] = self.db_path
            info['performance'] = 'Optimized for local development'
            info['platform'] = 'NetworkX + SQLite'
        
        return info
    
    # ========================================================================
    # IGraphQueryEngine Interface Methods (Delegate to selected engine)
    # ========================================================================
    
    def get_neighbors(
        self,
        node_id: str,
        direction: TraversalDirection = TraversalDirection.OUTGOING,
        edge_types: Optional[List[str]] = None,
        limit: Optional[int] = None
    ) -> List[GraphNode]:
        """Get adjacent nodes (delegates to selected engine)"""
        return self.engine.get_neighbors(node_id, direction, edge_types, limit)
    
    def shortest_path(
        self,
        start_id: str,
        end_id: str,
        max_hops: int = 10
    ) -> Optional[GraphPath]:
        """Find shortest path (delegates to selected engine)"""
        return self.engine.shortest_path(start_id, end_id, max_hops)
    
    def traverse(
        self,
        start_id: str,
        depth: int = 2,
        direction: TraversalDirection = TraversalDirection.OUTGOING,
        edge_types: Optional[List[str]] = None
    ) -> List[GraphNode]:
        """Breadth-first traversal (delegates to selected engine)"""
        return self.engine.traverse(start_id, depth, direction, edge_types)
    
    def subgraph(
        self,
        node_ids: List[str],
        include_edges: bool = True
    ) -> Subgraph:
        """Extract subgraph (delegates to selected engine)"""
        return self.engine.subgraph(node_ids, include_edges)
    
    def get_node(self, node_id: str) -> Optional[GraphNode]:
        """Get single node (delegates to selected engine)"""
        return self.engine.get_node(node_id)
    
    def node_exists(self, node_id: str) -> bool:
        """Check if node exists (delegates to selected engine)"""
        return self.engine.node_exists(node_id)
    
    def get_node_count(self) -> int:
        """Get total node count (delegates to selected engine)"""
        return self.engine.get_node_count()
    
    def get_edge_count(self) -> int:
        """Get total edge count (delegates to selected engine)"""
        return self.engine.get_edge_count()
    
    def clear_cache(self) -> None:
        """Clear engine cache (delegates to selected engine)"""
        self.engine.clear_cache()
    
    # ========================================================================
    # Advanced Methods (HANA-specific, graceful degradation for NetworkX)
    # ========================================================================
    
    def get_pagerank(self, top_k: int = 10) -> Dict[str, float]:
        """
        Calculate PageRank centrality.
        
        HANA: Uses native GRAPH_PAGERANK()
        NetworkX: Uses networkx.pagerank()
        
        Args:
            top_k: Return top K nodes
            
        Returns:
            Dict mapping node_id → pagerank score
        """
        if hasattr(self.engine, 'get_pagerank'):
            return self.engine.get_pagerank(top_k)
        
        logger.warning("PageRank not supported by current backend")
        return {}
    
    def get_betweenness_centrality(
        self,
        vertex_table: Optional[str] = None,
        top_k: int = 10
    ) -> Dict[str, float]:
        """
        Calculate betweenness centrality.
        
        HANA: Uses native GRAPH_BETWEENNESS_CENTRALITY()
        NetworkX: Uses networkx.betweenness_centrality()
        
        Args:
            vertex_table: Filter to specific table (HANA only)
            top_k: Return top K nodes
            
        Returns:
            Dict mapping node_id → centrality score
        """
        if hasattr(self.engine, 'get_betweenness_centrality'):
            return self.engine.get_betweenness_centrality(vertex_table, top_k)
        
        logger.warning("Betweenness centrality not supported by current backend")
        return {}
    
    def detect_communities(self, algorithm: str = 'louvain') -> Dict[str, int]:
        """
        Community detection.
        
        HANA: Uses native GRAPH_LOUVAIN_COMMUNITY_DETECTION()
        NetworkX: Uses community detection algorithms
        
        Args:
            algorithm: 'louvain' or 'label_propagation'
            
        Returns:
            Dict mapping node_id → community_id
        """
        if hasattr(self.engine, 'detect_communities'):
            return self.engine.detect_communities(algorithm)
        
        logger.warning("Community detection not supported by current backend")
        return {}