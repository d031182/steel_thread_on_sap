"""
Knowledge Graph Facade v2

Simplified interface for knowledge graph operations with cache rebuild capability.
This is the main entry point for consumers (API, tests, other modules).
"""
from typing import Dict, Any, Optional
from pathlib import Path

from ..domain import Graph, GraphType
from ..repositories import AbstractGraphCacheRepository
from ..services import GraphCacheService, SchemaGraphBuilderService
from core.services.csn_parser import CSNParser


class KnowledgeGraphFacadeV2:
    """
    Unified interface for knowledge graph operations
    
    Provides simplified API wrapping cache service with:
    - Automatic cache rebuild on miss/corruption
    - Force rebuild capability
    - Cache status checks
    - Generic graph format (NOT vis.js)
    
    Usage:
        facade = KnowledgeGraphFacadeV2(cache_repo, csn_dir)
        result = facade.get_schema_graph()  # Auto-rebuilds if needed
        graph_dict = result['graph']  # Generic format
    """
    
    def __init__(
        self,
        cache_repository: AbstractGraphCacheRepository,
        csn_directory: Path,
        graph_query_service=None
    ):
        """
        Initialize facade with dependencies
        
        Args:
            cache_repository: Repository for graph caching
            csn_directory: Directory containing CSN files
            graph_query_service: NetworkXGraphQueryEngine instance for advanced queries
        """
        # Initialize CSN parser
        self.csn_parser = CSNParser(csn_directory)
        
        # Initialize schema builder
        self.schema_builder = SchemaGraphBuilderService(self.csn_parser)
        
        # Initialize cache service (orchestrator)
        self.cache_service = GraphCacheService(
            cache_repository=cache_repository,
            schema_builder=self.schema_builder
        )
        
        # Store graph query engine directly (HIGH-31)
        self.graph_query_service = graph_query_service
    
    def get_schema_graph(self, use_cache: bool = True) -> Dict[str, Any]:
        """
        Get schema graph (auto-rebuilds if cache miss/corrupted)
        
        Args:
            use_cache: If True, uses cache (auto-rebuild on miss).
                      If False, forces rebuild (ignores cache).
        
        Returns:
            Dictionary with:
            - success: bool
            - graph: Generic graph dict (nodes, edges)
            - cache_used: bool
            - metadata: Dict with stats
        
        Example:
            result = facade.get_schema_graph()
            if result['success']:
                graph_dict = result['graph']  # Generic format
                print(f"Nodes: {result['metadata']['node_count']}")
        """
        try:
            # Get or rebuild graph
            if use_cache:
                graph = self.cache_service.get_or_rebuild_schema_graph()
                cache_used = True
            else:
                graph = self.cache_service.force_rebuild_schema()
                cache_used = False
            
            # Convert to generic dict format
            stats = graph.get_statistics()
            
            return {
                'success': True,
                'graph': graph.to_dict(),  # Generic format (NOT vis.js!)
                'cache_used': cache_used,
                'metadata': {
                    'graph_id': graph.id,
                    'graph_type': graph.type.value,
                    'node_count': stats['node_count'],
                    'edge_count': stats['edge_count'],
                    'nodes_by_type': stats['nodes_by_type'],
                    'edges_by_type': stats['edges_by_type']
                }
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'error_type': type(e).__name__
            }
    
    # ========================================================================
    # Advanced Query Methods (HIGH-31: Phase 3)
    # ========================================================================
    
    def get_pagerank(self, top_k: int = 10, damping_factor: float = 0.85) -> Dict[str, Any]:
        """
        Calculate PageRank centrality scores
        
        Args:
            top_k: Number of top nodes to return
            damping_factor: PageRank damping factor (default: 0.85)
        
        Returns:
            Dictionary with:
            - success: bool
            - data: Dict with scores, top_k, total_nodes
            - error: str (if failed)
        
        Example:
            result = facade.get_pagerank(top_k=10)
            if result['success']:
                scores = result['data']['scores']
        """
        if not self.graph_query_service:
            return {
                'success': False,
                'error': 'GraphQueryService not initialized'
            }
        
        try:
            scores = self.graph_query_service.get_pagerank(top_k=top_k, damping_factor=damping_factor)
            
            return {
                'success': True,
                'data': {
                    'scores': scores,
                    'top_k': top_k,
                    'total_nodes': self.graph_query_service.get_node_count(),
                    'algorithm': 'PageRank',
                    'damping_factor': damping_factor
                }
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'error_type': type(e).__name__
            }
    
    def get_centrality(
        self,
        metric: str = 'betweenness',
        top_k: int = 10
    ) -> Dict[str, Any]:
        """
        Calculate centrality metrics
        
        Args:
            metric: Centrality type ('betweenness', 'degree')
            top_k: Number of top nodes to return
        
        Returns:
            Dictionary with:
            - success: bool
            - data: Dict with metric, scores, top_k
            - error: str (if failed)
        
        Example:
            result = facade.get_centrality(metric='betweenness', top_k=10)
            if result['success']:
                scores = result['data']['scores']
        """
        if not self.graph_query_service:
            return {
                'success': False,
                'error': 'GraphQueryService not initialized'
            }
        
        try:
            # Delegate to engine based on metric type
            if metric == 'betweenness':
                scores = self.graph_query_service.get_betweenness_centrality(top_k=top_k)
            elif metric == 'degree':
                scores = self.graph_query_service.get_degree_centrality(top_k=top_k)
            else:
                return {
                    'success': False,
                    'error': f'Centrality metric "{metric}" not supported. Supported: betweenness, degree'
                }
            
            return {
                'success': True,
                'data': {
                    'metric': metric,
                    'scores': scores,
                    'top_k': top_k
                }
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'error_type': type(e).__name__
            }
    
    def detect_communities(self, algorithm: str = 'louvain') -> Dict[str, Any]:
        """
        Detect communities in graph
        
        Args:
            algorithm: Detection algorithm (not yet implemented)
        
        Returns:
            Dictionary with error (placeholder)
        """
        return {
            'success': False,
            'error': 'Community detection not yet implemented'
        }
    
    def find_cycles(self) -> Dict[str, Any]:
        """
        Find all cycles in graph
        
        Returns:
            Dictionary with:
            - success: bool
            - data: Dict with cycles, cycle_count
            - error: str (if failed)
        """
        if not self.graph_query_service:
            return {
                'success': False,
                'error': 'GraphQueryService not initialized'
            }
        
        try:
            cycles = self.graph_query_service.find_cycles()
            
            return {
                'success': True,
                'data': {
                    'cycles': cycles,
                    'cycle_count': len(cycles)
                }
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'error_type': type(e).__name__
            }
    
    def get_connected_components(self) -> Dict[str, Any]:
        """
        Find connected components in graph
        
        Returns:
            Dictionary with:
            - success: bool
            - data: Dict with components, component_count
            - error: str (if failed)
        """
        if not self.graph_query_service:
            return {
                'success': False,
                'error': 'GraphQueryService not initialized'
            }
        
        try:
            components_sets = self.graph_query_service.get_connected_components()
            
            # Convert sets to lists for JSON serialization
            components = [list(comp) for comp in components_sets]
            
            return {
                'success': True,
                'data': {
                    'components': components,
                    'component_count': len(components)
                }
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'error_type': type(e).__name__
            }
    
    def get_graph_statistics(self) -> Dict[str, Any]:
        """
        Get comprehensive graph statistics
        
        Returns:
            Dictionary with:
            - success: bool
            - data: Dict with nodes, edges, density, avg_degree, etc.
            - error: str (if failed)
        """
        if not self.graph_query_service:
            return {
                'success': False,
                'error': 'GraphQueryService not initialized'
            }
        
        try:
            # Use engine's built-in statistics method
            stats = self.graph_query_service.get_statistics()
            
            return {
                'success': True,
                'data': stats
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'error_type': type(e).__name__
            }
    
    def rebuild_schema_graph(self) -> Dict[str, Any]:
        """
        Force rebuild of schema graph (ignores cache)
        
        Use this when:
        - CSN files have been updated
        - Cache is known to be stale
        - Manual refresh requested by admin
        
        Returns:
            Same format as get_schema_graph()
        
        Example:
            result = facade.rebuild_schema_graph()
            if result['success']:
                print("Schema rebuilt successfully")
        """
        return self.get_schema_graph(use_cache=False)
    
    def get_schema_status(self) -> Dict[str, Any]:
        """
        Get schema graph cache status
        
        Returns:
            Dictionary with:
            - cached: bool (is schema cached?)
            - csn_files_count: int
            - csn_directory: str
        
        Example:
            status = facade.get_schema_status()
            if status['cached']:
                print("Schema graph is cached")
        """
        try:
            cached = self.cache_service.exists_in_cache('schema', GraphType.SCHEMA)
            
            # Count CSN files
            csn_files = list(self.csn_parser.csn_dir.glob("*_CSN.json"))
            
            return {
                'success': True,
                'cached': cached,
                'csn_files_count': len(csn_files),
                'csn_directory': str(self.csn_parser.csn_dir)
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'error_type': type(e).__name__
            }
    
    def clear_schema_cache(self) -> Dict[str, Any]:
        """
        Clear schema graph cache (admin operation)
        
        Returns:
            Dictionary with:
            - success: bool
            - cleared: bool (was cache actually cleared?)
        
        Example:
            result = facade.clear_schema_cache()
            if result['cleared']:
                print("Cache cleared successfully")
        """
        try:
            cleared = self.cache_service.clear_cache(GraphType.SCHEMA)
            
            return {
                'success': True,
                'cleared': cleared
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'error_type': type(e).__name__
            }