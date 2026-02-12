"""
Graph Cache Strategy Adapters

Adapters that wrap concrete cache implementations to the GraphCacheStrategy interface.

Design Patterns:
- ADAPTER (GoF Structural Pattern): Makes GraphCacheService compatible with GraphCacheStrategy
- STRATEGY (GoF Behavioral Pattern): Allows runtime selection of cache implementation

@author P2P Development Team
@version 1.0.0
@since v3.24
"""

from typing import List, Dict, Any, Optional
import logging
import json

from core.interfaces.graph_cache import GraphCacheStrategy
from modules.knowledge_graph.backend.graph_cache_service import GraphCacheService

logger = logging.getLogger(__name__)


class GraphCacheServiceAdapter(GraphCacheStrategy):
    """
    Adapter for GraphCacheService (v5 implementation)
    
    Wraps the new clean GraphCacheService to implement GraphCacheStrategy interface.
    """
    
    def __init__(self, db_path: str):
        """
        Initialize adapter
        
        Args:
            db_path: Path to database file
        """
        self.cache_service = GraphCacheService(db_path)
        self.db_path = db_path
    
    def save_graph(
        self, 
        nodes: List[Dict], 
        edges: List[Dict],
        graph_type: str,
        description: Optional[str] = None
    ) -> bool:
        """Save graph to v5 cache"""
        try:
            self.cache_service.save_graph(
                nodes=nodes,
                edges=edges,
                graph_type=graph_type,
                description=description
            )
            return True
        except Exception as e:
            logger.error(f"Error saving graph to cache: {e}")
            return False
    
    def load_graph(self, graph_type: str) -> Optional[Dict[str, Any]]:
        """Load graph from v5 cache"""
        try:
            result = self.cache_service.load_graph(graph_type)
            
            if result and result.get('nodes'):
                return {
                    'nodes': result['nodes'],
                    'edges': result['edges'],
                    'stats': {
                        'cache_exists': True,
                        'node_count': len(result['nodes']),
                        'edge_count': len(result['edges']),
                        'cached_at': result.get('cached_at')
                    }
                }
            
            return None
            
        except Exception as e:
            logger.error(f"Error loading graph from cache: {e}")
            return None
    
    def is_cache_valid(self, graph_type: str) -> bool:
        """Check if cache exists for graph type"""
        try:
            result = self.cache_service.load_graph(graph_type)
            return result is not None and len(result.get('nodes', [])) > 0
        except Exception as e:
            logger.error(f"Error checking cache validity: {e}")
            return False
    
    def clear_cache(self, graph_type: Optional[str] = None) -> int:
        """Clear cache"""
        try:
            if graph_type:
                return self.cache_service.clear_cache(graph_type)
            else:
                # Clear all graph types
                total = 0
                for gt in ['schema', 'data', 'csn']:
                    total += self.cache_service.clear_cache(gt)
                return total
        except Exception as e:
            logger.error(f"Error clearing cache: {e}")
            return 0
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get cache statistics"""
        try:
            import sqlite3
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Count cached graphs by type
            cursor.execute("""
                SELECT graph_type, COUNT(*), SUM(node_count), SUM(edge_count)
                FROM graph_metadata
                GROUP BY graph_type
            """)
            
            stats = {}
            for row in cursor.fetchall():
                graph_type, count, nodes, edges = row
                stats[graph_type] = {
                    'cached': count > 0,
                    'node_count': nodes or 0,
                    'edge_count': edges or 0
                }
            
            conn.close()
            
            return {
                'cache_available': True,
                'implementation': 'GraphCacheService v5',
                'graphs': stats
            }
            
        except Exception as e:
            logger.error(f"Error getting cache statistics: {e}")
            return {
                'cache_available': False,
                'error': str(e)
            }


class CacheStrategyFactory:
    """
    Factory for creating appropriate cache strategy
    
    Design Pattern: FACTORY METHOD (GoF Creational Pattern)
    Purpose: Encapsulate cache implementation selection
    
    Selection Logic:
    - Always use GraphCacheServiceAdapter (v5) for new deployments
    - Legacy adapter available if needed for migration
    """
    
    @staticmethod
    def create(db_path: str, prefer_v5: bool = True) -> GraphCacheStrategy:
        """
        Create appropriate cache strategy
        
        Args:
            db_path: Path to database
            prefer_v5: If True, use new v5 cache (recommended)
        
        Returns:
            GraphCacheStrategy implementation
        """
        if prefer_v5:
            logger.info("Using GraphCacheService v5 (recommended)")
            return GraphCacheServiceAdapter(db_path)
        else:
            # Future: Legacy adapter if needed
            logger.warning("Legacy cache not yet implemented, falling back to v5")
            return GraphCacheServiceAdapter(db_path)