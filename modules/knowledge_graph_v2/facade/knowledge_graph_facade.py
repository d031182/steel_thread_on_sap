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
        csn_directory: Path
    ):
        """
        Initialize facade with dependencies
        
        Args:
            cache_repository: Repository for graph caching
            csn_directory: Directory containing CSN files
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