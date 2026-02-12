"""
Knowledge Graph Facade

Provides a simplified, unified interface to the knowledge graph subsystem.
Orchestrates multiple services (builders, query engines, cache, ontology).

Design Pattern: FACADE (GoF Structural Pattern)
Purpose: Hide complexity of graph operations behind simple interface
Benefits: 
  - API layer shrinks from 700 LOC → 200 LOC
  - Single point of testing
  - Easy to add cross-cutting concerns (logging, caching, auth)
  - Hides implementation details from API consumers

@author P2P Development Team
@version 1.0.0
@since v3.24
"""

from typing import Dict, Any, Optional, List
import logging
import time

from core.interfaces.data_source import DataSource
from core.interfaces.graph_query import TraversalDirection
from core.interfaces.graph_cache import GraphCacheStrategy
from core.services.graph_query_service import GraphQueryService
from modules.knowledge_graph.backend.graph_cache_strategy_adapter import CacheStrategyFactory
from core.services.csn_parser import CSNParser
from core.services.relationship_mapper import CSNRelationshipMapper

logger = logging.getLogger(__name__)


class GraphBuilderFactory:
    """
    Factory for creating graph builders based on mode
    
    Design Pattern: FACTORY METHOD (GoF Creational Pattern)
    Purpose: Encapsulate builder selection logic
    """
    
    @staticmethod
    def create_builder(mode: str, data_source: DataSource, **kwargs):
        """
        Create appropriate graph builder for the specified mode
        
        Args:
            mode: 'schema', 'data', or 'csn'
            data_source: DataSource implementation (SQLite or HANA)
            **kwargs: Additional arguments for specific builders
                - csn_path: Path to CSN files (for csn mode)
                - db_path: Database path for caching (for csn mode)
                - max_records: Max records per table (for data mode)
                - filter_orphans: Hide unconnected nodes (for data mode)
        
        Returns:
            GraphBuilder instance
        
        Raises:
            ValueError: If mode is invalid
        """
        mode = mode.lower()
        
        if mode == 'schema':
            from modules.knowledge_graph.backend.schema_graph_builder import SchemaGraphBuilder
            return SchemaGraphBuilder(data_source)
        
        elif mode == 'csn':
            from modules.knowledge_graph.backend.csn_schema_graph_builder_v2 import CSNSchemaGraphBuilderV2
            csn_path = kwargs.get('csn_path', 'docs/csn')
            db_path = kwargs.get('db_path')
            return CSNSchemaGraphBuilderV2(csn_path, db_path)
        
        elif mode == 'data':
            from modules.knowledge_graph.backend.data_graph_builder import DataGraphBuilder
            return DataGraphBuilder(data_source)
        
        else:
            raise ValueError(f"Invalid mode '{mode}'. Must be 'schema', 'data', or 'csn'")


class KnowledgeGraphFacade:
    """
    Simplified interface to knowledge graph operations
    
    Design Pattern: FACADE (GoF Structural Pattern)
    
    Orchestrates:
    - Graph builders (schema, CSN, data)
    - Query service (neighbors, paths, traversal)
    - Cache service (vis.js visualization)
    - Ontology service (relationship persistence)
    
    Usage:
        facade = KnowledgeGraphFacade(data_source)
        
        # Get graph visualization
        graph = facade.get_graph(mode='schema', use_cache=True)
        
        # Query operations
        neighbors = facade.get_neighbors('PurchaseOrder:12345')
        path = facade.find_shortest_path('Supplier:S001', 'Invoice:INV123')
        nodes = facade.traverse_from('Product:P001', depth=2)
        
        # Cache operations
        facade.refresh_ontology_cache()
        stats = facade.get_cache_status()
    """
    
    def __init__(self, data_source: DataSource):
        """
        Initialize facade with data source
        
        Args:
            data_source: DataSource implementation (SQLite or HANA)
        """
        self.data_source = data_source
        
        # Get connection info for cache/ontology services
        conn_info = data_source.get_connection_info()
        self.db_path = conn_info.get('db_path') if conn_info.get('type') == 'sqlite' else None
        self.source_type = conn_info.get('type', 'sqlite')
        
        # Initialize services (lazy - only when needed)
        self._query_service = None
        self._cache_service = None
        self._graph_cache_service = None
        self._ontology_service = None
        self._csn_parser = None
        self._relationship_mapper = None
    
    @property
    def query_service(self) -> GraphQueryService:
        """Lazy initialization of query service"""
        if self._query_service is None:
            self._query_service = GraphQueryService(self.data_source)
        return self._query_service
    
    @property
    def graph_cache_strategy(self) -> Optional[GraphCacheStrategy]:
        """
        Lazy initialization of graph cache strategy (SQLite only)
        
        Uses Strategy + Factory patterns to select appropriate cache implementation.
        Currently always uses GraphCacheService v5.
        
        Note: Cache database is separate from data database
        - Data DB: database/p2p_data.db (or HANA)
        - Cache DB: modules/knowledge_graph/database/graph_cache.db
        """
        if self._cache_service is None and self.source_type == 'sqlite':
            # Cache is in a separate database (not p2p_data.db)
            # Use absolute path to ensure it works regardless of working directory
            import os
            cache_db_path = os.path.abspath('modules/knowledge_graph/database/graph_cache.db')
            logger.info(f"Initializing cache service with absolute path: {cache_db_path}")
            
            # Use CacheStrategyFactory (Factory pattern)
            self._cache_service = CacheStrategyFactory.create(cache_db_path, prefer_v5=True)
        return self._cache_service
    
    @property
    def csn_parser(self) -> CSNParser:
        """Lazy initialization of CSN parser"""
        if self._csn_parser is None:
            self._csn_parser = CSNParser('docs/csn')
        return self._csn_parser
    
    @property
    def relationship_mapper(self) -> CSNRelationshipMapper:
        """Lazy initialization of relationship mapper"""
        if self._relationship_mapper is None:
            self._relationship_mapper = CSNRelationshipMapper(self.csn_parser)
        return self._relationship_mapper
    
    # ========================================
    # Graph Building Operations
    # ========================================
    
    def get_graph(
        self,
        mode: str = 'schema',
        use_cache: bool = True,
        max_records: int = 20,
        filter_orphans: bool = True
    ) -> Dict[str, Any]:
        """
        Get knowledge graph visualization
        
        This is the main entry point for graph visualization.
        Handles cache lookup, builder selection, and graph construction.
        
        Args:
            mode: Visualization mode ('schema', 'data', or 'csn')
            use_cache: Whether to try cache first (SQLite only)
            max_records: Maximum records per table (data mode only)
            filter_orphans: Hide nodes with no connections (data mode only)
        
        Returns:
            Dict with 'nodes', 'edges', 'stats', 'success' keys
        
        Raises:
            ValueError: If mode is invalid
        """
        try:
            # Try cache first (SQLite only, not HANA) using Strategy pattern
            if use_cache and self.graph_cache_strategy and self.source_type == 'sqlite':
                logger.info(f"Attempting to load {mode} graph from cache...")
                try:
                    cached_graph = self.graph_cache_strategy.load_graph(mode)
                    
                    if cached_graph:
                        logger.info(f"✓ Loaded {mode} graph from cache: {len(cached_graph.get('nodes', []))} nodes, {len(cached_graph.get('edges', []))} edges")
                        return {
                            'success': True,
                            'nodes': cached_graph['nodes'],
                            'edges': cached_graph['edges'],
                            'stats': cached_graph.get('stats', {
                                'node_count': len(cached_graph['nodes']),
                                'edge_count': len(cached_graph['edges']),
                                'cache_used': True
                            })
                        }
                    else:
                        logger.info(f"Cache miss for {mode} graph (returned None)")
                except Exception as cache_err:
                    logger.error(f"Cache load exception: {cache_err}", exc_info=True)
                
                logger.info(f"Building {mode} graph from scratch after cache miss...")
            else:
                logger.info(f"Cache not available (use_cache={use_cache}, strategy={self.graph_cache_strategy is not None}, source={self.source_type})")
            
            # Build graph (cache miss or disabled)
            start_time = time.time()
            logger.info(f"Building {mode} knowledge graph from {self.source_type}")
            
            builder = GraphBuilderFactory.create_builder(
                mode=mode,
                data_source=self.data_source,
                csn_path='docs/csn',
                db_path=self.db_path
            )
            
            # Build based on mode
            if mode == 'data':
                result = builder.build_data_graph(
                    max_records_per_table=max_records,
                    filter_orphans=filter_orphans,
                    use_cache=False  # Already tried cache above
                )
            else:
                result = builder.build_schema_graph()
            
            elapsed = (time.time() - start_time) * 1000
            logger.info(f"Graph built in {elapsed:.0f}ms: {result['stats']['node_count']} nodes, {result['stats']['edge_count']} edges")
            
            # Save to cache (SQLite only) using Strategy pattern
            if result.get('success') and self.graph_cache_strategy and self.source_type == 'sqlite':
                try:
                    nodes = result.get('nodes', [])
                    edges = result.get('edges', [])
                    
                    if nodes and edges:
                        success = self.graph_cache_strategy.save_graph(
                            nodes=nodes,
                            edges=edges,
                            graph_type=mode,
                            description=f"{mode.capitalize()} graph"
                        )
                        if success:
                            logger.info(f"✓ Saved {len(nodes)} nodes, {len(edges)} edges to {mode} cache")
                        else:
                            logger.warning(f"Cache save returned False")
                    else:
                        logger.warning(f"Skipping cache save - empty graph (nodes={len(nodes)}, edges={len(edges)})")
                        
                except Exception as cache_error:
                    # Log but don't fail the request if cache save fails
                    logger.error(f"Failed to save graph cache: {cache_error}", exc_info=True)
            
            return result
            
        except Exception as e:
            logger.error(f"Error building graph: {e}", exc_info=True)
            return {
                'success': False,
                'error': {
                    'code': 'BUILD_ERROR',
                    'message': str(e)
                }
            }
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Get statistics about available data for graphing
        
        Returns:
            Dict with product_count, table_count
        """
        try:
            products = self.data_source.get_data_products()
            
            total_tables = 0
            for product in products:
                tables = self.data_source.get_tables(product['schemaName'])
                total_tables += len(tables) if tables else 0
            
            return {
                'success': True,
                'stats': {
                    'source': self.source_type,
                    'product_count': len(products),
                    'table_count': total_tables
                }
            }
            
        except Exception as e:
            logger.error(f"Error getting statistics: {e}", exc_info=True)
            return {
                'success': False,
                'error': {
                    'code': 'STATS_ERROR',
                    'message': str(e)
                }
            }
    
    # ========================================
    # Graph Query Operations (NEW in v3.15)
    # ========================================
    
    def get_neighbors(
        self,
        node_id: str,
        direction: str = 'outgoing',
        edge_types: Optional[List[str]] = None,
        limit: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Get neighbors of a node (10-100x faster for HANA)
        
        Uses GraphQueryService with automatic backend selection:
        - HANA → HANAGraphQueryEngine (native Property Graph)
        - SQLite → NetworkXGraphQueryEngine (optimized local)
        
        Args:
            node_id: Node identifier (e.g., 'PurchaseOrder:12345')
            direction: 'outgoing', 'incoming', or 'both'
            edge_types: Optional list of edge types to filter by
            limit: Optional maximum number of neighbors to return
        
        Returns:
            Dict with 'neighbors', 'count', 'backend' keys
        """
        try:
            # Map direction string to enum
            direction_map = {
                'outgoing': TraversalDirection.OUTGOING,
                'incoming': TraversalDirection.INCOMING,
                'both': TraversalDirection.BOTH
            }
            direction_enum = direction_map.get(direction.lower(), TraversalDirection.OUTGOING)
            
            # Execute query
            neighbors = self.query_service.get_neighbors(node_id, direction_enum, edge_types, limit)
            backend_info = self.query_service.get_backend_info()
            
            # Convert GraphNode objects to dicts
            neighbors_data = [
                {
                    'id': n.id,
                    'label': n.label,
                    'properties': n.properties
                }
                for n in neighbors
            ]
            
            logger.info(f"Found {len(neighbors_data)} neighbors for {node_id} using {backend_info['backend']}")
            
            return {
                'success': True,
                'node_id': node_id,
                'direction': direction,
                'neighbors': neighbors_data,
                'count': len(neighbors_data),
                'backend': backend_info
            }
            
        except Exception as e:
            logger.error(f"Error getting neighbors: {e}", exc_info=True)
            return {
                'success': False,
                'error': {
                    'code': 'QUERY_ERROR',
                    'message': str(e)
                }
            }
    
    def find_shortest_path(
        self,
        start_id: str,
        end_id: str,
        max_hops: int = 10
    ) -> Dict[str, Any]:
        """
        Find shortest path between two nodes
        
        Args:
            start_id: Starting node identifier
            end_id: Ending node identifier
            max_hops: Maximum path length to search
        
        Returns:
            Dict with 'path' (nodes + edges), 'length', 'backend' keys
        """
        try:
            path = self.query_service.shortest_path(start_id, end_id, max_hops)
            backend_info = self.query_service.get_backend_info()
            
            if path:
                # Convert GraphPath to dict
                path_data = {
                    'nodes': [
                        {
                            'id': n.id,
                            'label': n.label,
                            'properties': n.properties
                        }
                        for n in path.nodes
                    ],
                    'edges': [
                        {
                            'from': e.source_id,
                            'to': e.target_id,
                            'type': e.edge_type,
                            'properties': e.properties
                        }
                        for e in path.edges
                    ],
                    'length': path.length,
                    'total_cost': path.total_cost
                }
                
                logger.info(f"Found path from {start_id} to {end_id}: {path.length} hops using {backend_info['backend']}")
                
                return {
                    'success': True,
                    'start_id': start_id,
                    'end_id': end_id,
                    'path': path_data,
                    'backend': backend_info
                }
            else:
                return {
                    'success': False,
                    'error': {
                        'code': 'NO_PATH',
                        'message': f'No path exists between {start_id} and {end_id} within {max_hops} hops'
                    }
                }
                
        except Exception as e:
            logger.error(f"Error finding path: {e}", exc_info=True)
            return {
                'success': False,
                'error': {
                    'code': 'PATH_ERROR',
                    'message': str(e)
                }
            }
    
    def traverse_from(
        self,
        start_id: str,
        depth: int = 2,
        direction: str = 'outgoing',
        edge_types: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Breadth-first traversal from starting node
        
        Args:
            start_id: Starting node identifier
            depth: Traversal depth (1-10)
            direction: 'outgoing', 'incoming', or 'both'
            edge_types: Optional list of edge types to follow
        
        Returns:
            Dict with 'nodes', 'count', 'backend' keys
        """
        try:
            # Map direction
            direction_map = {
                'outgoing': TraversalDirection.OUTGOING,
                'incoming': TraversalDirection.INCOMING,
                'both': TraversalDirection.BOTH
            }
            direction_enum = direction_map.get(direction.lower(), TraversalDirection.OUTGOING)
            
            # Execute traversal
            nodes = self.query_service.traverse(start_id, depth, direction_enum, edge_types)
            backend_info = self.query_service.get_backend_info()
            
            # Convert to dicts
            nodes_data = [
                {
                    'id': n.id,
                    'label': n.label,
                    'properties': n.properties
                }
                for n in nodes
            ]
            
            logger.info(f"Traversed from {start_id} depth {depth}: {len(nodes_data)} nodes using {backend_info['backend']}")
            
            return {
                'success': True,
                'start_id': start_id,
                'depth': depth,
                'direction': direction,
                'nodes': nodes_data,
                'count': len(nodes_data),
                'backend': backend_info
            }
            
        except Exception as e:
            logger.error(f"Error traversing graph: {e}", exc_info=True)
            return {
                'success': False,
                'error': {
                    'code': 'TRAVERSAL_ERROR',
                    'message': str(e)
                }
            }
    
    # ========================================
    # Graph Algorithm Operations (NetworkX)
    # ========================================
    
    def calculate_centrality(self, algorithm: str = 'betweenness') -> Dict[str, Any]:
        """
        Calculate node centrality (importance/criticality)
        
        Args:
            algorithm: 'betweenness', 'pagerank', 'degree', or 'closeness'
        
        Returns:
            Dict with 'scores', 'top_10' keys
        """
        try:
            from modules.knowledge_graph.backend.data_graph_builder import DataGraphBuilder
            from modules.knowledge_graph.backend.property_graph_service import NetworkXPropertyGraph
            
            valid_algorithms = ['betweenness', 'pagerank', 'degree', 'closeness']
            if algorithm not in valid_algorithms:
                raise ValueError(f"Invalid algorithm '{algorithm}'. Must be one of: {', '.join(valid_algorithms)}")
            
            # Build schema graph
            builder = DataGraphBuilder(self.data_source)
            graph_dict = builder.build_schema_graph()
            
            if not graph_dict.get('success'):
                return graph_dict
            
            # Load into NetworkX and calculate
            property_graph = NetworkXPropertyGraph()
            property_graph.load_from_dict(graph_dict)
            scores = property_graph.centrality(algorithm)
            
            # Sort by score (highest first)
            sorted_scores = sorted(scores.items(), key=lambda x: x[1], reverse=True)
            
            logger.info(f"Calculated {algorithm} centrality: {len(scores)} nodes")
            
            return {
                'success': True,
                'algorithm': algorithm,
                'scores': dict(sorted_scores),
                'top_10': [{'node': node, 'score': score} for node, score in sorted_scores[:10]]
            }
            
        except Exception as e:
            logger.error(f"Error calculating centrality: {e}", exc_info=True)
            return {
                'success': False,
                'error': {
                    'code': 'CENTRALITY_ERROR',
                    'message': str(e)
                }
            }
    
    def detect_communities(self, algorithm: str = 'louvain') -> Dict[str, Any]:
        """
        Detect communities/clusters in graph
        
        Args:
            algorithm: 'louvain', 'label_propagation', or 'greedy_modularity'
        
        Returns:
            Dict with 'communities', 'cluster_stats', 'num_clusters' keys
        """
        try:
            from modules.knowledge_graph.backend.data_graph_builder import DataGraphBuilder
            from modules.knowledge_graph.backend.property_graph_service import NetworkXPropertyGraph
            
            valid_algorithms = ['louvain', 'label_propagation', 'greedy_modularity']
            if algorithm not in valid_algorithms:
                raise ValueError(f"Invalid algorithm '{algorithm}'. Must be one of: {', '.join(valid_algorithms)}")
            
            # Build schema graph
            builder = DataGraphBuilder(self.data_source)
            graph_dict = builder.build_schema_graph()
            
            if not graph_dict.get('success'):
                return graph_dict
            
            # Load into NetworkX and detect communities
            property_graph = NetworkXPropertyGraph()
            property_graph.load_from_dict(graph_dict)
            communities = property_graph.community_detection(algorithm)
            
            # Calculate cluster statistics
            cluster_stats = {}
            for node, cluster in communities.items():
                if cluster not in cluster_stats:
                    cluster_stats[cluster] = {'count': 0, 'nodes': []}
                cluster_stats[cluster]['count'] += 1
                cluster_stats[cluster]['nodes'].append(node)
            
            logger.info(f"Detected {len(cluster_stats)} communities using {algorithm}")
            
            return {
                'success': True,
                'algorithm': algorithm,
                'communities': communities,
                'cluster_stats': cluster_stats,
                'num_clusters': len(cluster_stats)
            }
            
        except Exception as e:
            logger.error(f"Error detecting communities: {e}", exc_info=True)
            return {
                'success': False,
                'error': {
                    'code': 'COMMUNITY_ERROR',
                    'message': str(e)
                }
            }
    
    # ========================================
    # Cache & Ontology Operations
    # ========================================
    
    def refresh_ontology_cache(self) -> Dict[str, Any]:
        """
        Refresh graph cache by rebuilding and saving
        
        This triggers a complete rebuild of the graph from source data,
        then saves it to cache for fast subsequent loads.
        
        Use this when:
        - Data has changed (new records added)
        - Schema has changed (new tables added)
        - Want to force cache rebuild
        
        Returns:
            Dict with statistics about the refresh
        """
        try:
            logger.info("Starting graph cache refresh...")
            start_time = time.time()
            
            # Build graph fresh from data (no cache)
            result = self.get_graph(
                mode='data',
                use_cache=False,  # Force rebuild
                max_records=20,
                filter_orphans=True
            )
            
            if not result.get('success'):
                return result
            
            # Graph was already saved to cache by get_graph()
            # (see graph_cache_service.save_graph() call in get_graph())
            
            elapsed = (time.time() - start_time) * 1000
            node_count = result.get('stats', {}).get('node_count', 0)
            edge_count = result.get('stats', {}).get('edge_count', 0)
            
            logger.info(f"Cache refresh complete: {node_count} nodes, {edge_count} edges in {elapsed:.0f}ms")
            
            return {
                'success': True,
                'statistics': {
                    'nodes_cached': node_count,
                    'edges_cached': edge_count,
                    'refresh_time_ms': round(elapsed, 2)
                },
                'message': f'Graph cache refreshed successfully. Cached {node_count} nodes and {edge_count} edges in {elapsed:.0f}ms'
            }
            
        except Exception as e:
            logger.error(f"Error refreshing cache: {e}", exc_info=True)
            return {
                'success': False,
                'error': {
                    'code': 'REFRESH_ERROR',
                    'message': str(e)
                }
            }
    
    def get_cache_status(self) -> Dict[str, Any]:
        """
        Get current status of the graph cache
        
        Returns:
            Dict with cache statistics
        """
        try:
            if not self.graph_cache_strategy:
                return {
                    'success': True,
                    'source': self.source_type,
                    'cache': {
                        'available': False,
                        'reason': 'Cache only available for SQLite'
                    }
                }
            
            stats = self.graph_cache_strategy.get_statistics()
            
            return {
                'success': True,
                'source': self.source_type,
                'cache': stats
            }
            
        except Exception as e:
            logger.error(f"Error getting cache status: {e}", exc_info=True)
            return {
                'success': False,
                'error': {
                    'code': 'STATUS_ERROR',
                    'message': str(e)
                }
            }
    
    # ========================================
    # Legacy Operations (DEPRECATED)
    # ========================================
    
    def get_neighbors_legacy(self, node_id: str, max_distance: int = 1) -> Dict[str, Any]:
        """
        DEPRECATED: Use get_neighbors() for better performance (10-100x faster)
        
        Get neighbors using NetworkX (builds entire graph first)
        """
        try:
            from modules.knowledge_graph.backend.data_graph_builder import DataGraphBuilder
            from modules.knowledge_graph.backend.property_graph_service import NetworkXPropertyGraph
            
            logger.warning("Using legacy get_neighbors_legacy - consider migrating to get_neighbors()")
            
            # Build schema graph
            builder = DataGraphBuilder(self.data_source)
            graph_dict = builder.build_schema_graph()
            
            if not graph_dict.get('success'):
                return graph_dict
            
            # Load into NetworkX and get neighbors
            property_graph = NetworkXPropertyGraph()
            property_graph.load_from_dict(graph_dict)
            neighbors = property_graph.get_neighbors(node_id, max_distance)
            
            logger.info(f"Found {len(neighbors)} neighbors within distance {max_distance} of {node_id}")
            
            return {
                'success': True,
                'node_id': node_id,
                'max_distance': max_distance,
                'neighbors': neighbors,
                'count': len(neighbors)
            }
            
        except Exception as e:
            logger.error(f"Error in legacy get_neighbors: {e}", exc_info=True)
            return {
                'success': False,
                'error': {
                    'code': 'LEGACY_ERROR',
                    'message': str(e)
                }
            }


# ========================================
# Convenience Functions for API Layer
# ========================================

def create_facade(data_source: DataSource) -> KnowledgeGraphFacade:
    """
    Factory function to create facade instance
    
    Args:
        data_source: DataSource implementation
    
    Returns:
        KnowledgeGraphFacade instance
    """
    return KnowledgeGraphFacade(data_source)


def validate_graph_mode(mode: str) -> None:
    """
    Validate graph visualization mode
    
    Args:
        mode: Mode string to validate
    
    Raises:
        ValueError: If mode is invalid
    """
    valid_modes = ['schema', 'data', 'csn']
    if mode.lower() not in valid_modes:
        raise ValueError(f"Invalid mode '{mode}'. Must be one of: {', '.join(valid_modes)}")


def validate_algorithm(algorithm: str, valid_algorithms: List[str]) -> None:
    """
    Validate algorithm name
    
    Args:
        algorithm: Algorithm string to validate
        valid_algorithms: List of valid algorithm names
    
    Raises:
        ValueError: If algorithm is invalid
    """
    if algorithm.lower() not in valid_algorithms:
        raise ValueError(f"Invalid algorithm '{algorithm}'. Must be one of: {', '.join(valid_algorithms)}")