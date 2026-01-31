"""
Property Graph Interface

Defines the contract for Property Graph operations.
Enables swappable implementations: NetworkX (SQLite) → HANA Property Graph

@author P2P Development Team
@version 1.0.0
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional


class PropertyGraphInterface(ABC):
    """
    Interface for Property Graph operations
    
    Provides graph algorithms for network analysis:
    - Shortest path finding
    - Centrality analysis (identify critical nodes)
    - Community detection (find clusters)
    - Graph statistics
    
    Implementations:
    - NetworkXPropertyGraph: SQLite + NetworkX (development/offline)
    - HANAPropertyGraph: HANA Property Graph Engine (production/scale)
    """
    
    @abstractmethod
    def shortest_path(self, start: str, end: str) -> List[str]:
        """
        Find shortest path between two nodes
        
        Args:
            start: Starting node ID
            end: Ending node ID
            
        Returns:
            List of node IDs representing the path (empty if no path exists)
            
        Example:
            >>> path = graph.shortest_path('product-Supplier', 'table-Invoices-InvoiceHeader')
            >>> print(path)  # ['product-Supplier', 'table-Supplier-Suppliers', ...]
        """
        pass
    
    @abstractmethod
    def centrality(self, algorithm: str = 'betweenness') -> Dict[str, float]:
        """
        Calculate node centrality (importance/criticality)
        
        Args:
            algorithm: Centrality algorithm to use
                - 'betweenness': How often node appears on shortest paths (bottleneck detection)
                - 'pagerank': Importance based on connections (like Google PageRank)
                - 'degree': Simple count of connections
                - 'closeness': Average distance to all other nodes
                
        Returns:
            Dictionary mapping node_id → centrality_score (higher = more critical)
            
        Example:
            >>> scores = graph.centrality('betweenness')
            >>> top_node = max(scores.items(), key=lambda x: x[1])
            >>> print(f"Most critical: {top_node[0]} (score: {top_node[1]:.4f})")
        """
        pass
    
    @abstractmethod
    def community_detection(self, algorithm: str = 'louvain') -> Dict[str, str]:
        """
        Detect communities/clusters in the graph
        
        Args:
            algorithm: Community detection algorithm
                - 'louvain': Fast, hierarchical community detection
                - 'label_propagation': Simple, fast propagation method
                - 'greedy_modularity': Optimization-based approach
                
        Returns:
            Dictionary mapping node_id → community_id (e.g., 'cluster_0', 'cluster_1')
            
        Example:
            >>> communities = graph.community_detection('louvain')
            >>> cluster_sizes = {}
            >>> for node, cluster in communities.items():
            >>>     cluster_sizes[cluster] = cluster_sizes.get(cluster, 0) + 1
            >>> print(f"Found {len(cluster_sizes)} clusters")
        """
        pass
    
    @abstractmethod
    def get_graph_stats(self) -> Dict[str, Any]:
        """
        Get graph statistics and metrics
        
        Returns:
            Dictionary with graph statistics:
                - node_count: Total number of nodes
                - edge_count: Total number of edges
                - density: How interconnected the graph is (0.0 to 1.0)
                - avg_degree: Average number of connections per node
                - is_connected: Whether all nodes are reachable from each other
                - num_components: Number of disconnected subgraphs
                - diameter: Maximum shortest path length (if connected)
                
        Example:
            >>> stats = graph.get_graph_stats()
            >>> print(f"Graph has {stats['node_count']} nodes and density {stats['density']:.2%}")
        """
        pass
    
    @abstractmethod
    def get_neighbors(self, node_id: str, max_distance: int = 1) -> List[str]:
        """
        Get neighbors of a node within specified distance
        
        Args:
            node_id: Node to find neighbors for
            max_distance: Maximum path length (1 = direct neighbors, 2 = neighbors of neighbors, etc.)
            
        Returns:
            List of node IDs reachable within max_distance
            
        Example:
            >>> neighbors = graph.get_neighbors('product-Supplier', max_distance=2)
            >>> print(f"Found {len(neighbors)} nodes within 2 steps")
        """
        pass
    
    @abstractmethod
    def load_from_dict(self, graph_dict: Dict[str, Any]) -> None:
        """
        Load graph from dictionary representation
        
        Args:
            graph_dict: Dictionary with 'nodes' and 'edges' lists
                nodes: List of {'id': str, 'label': str, ...}
                edges: List of {'from': str, 'to': str, 'label': str, ...}
                
        Example:
            >>> graph.load_from_dict({
            >>>     'nodes': [{'id': 'A', 'label': 'Node A'}, ...],
            >>>     'edges': [{'from': 'A', 'to': 'B', 'label': 'connects'}, ...]
            >>> })
        """
        pass
    
    @abstractmethod
    def get_subgraph(self, node_ids: List[str]) -> Dict[str, Any]:
        """
        Extract subgraph containing only specified nodes
        
        Args:
            node_ids: List of node IDs to include
            
        Returns:
            Dictionary with 'nodes' and 'edges' for the subgraph
            
        Example:
            >>> cluster_nodes = [n for n, c in communities.items() if c == 'cluster_0']
            >>> subgraph = graph.get_subgraph(cluster_nodes)
            >>> print(f"Cluster 0 has {len(subgraph['nodes'])} nodes")
        """
        pass


class KnowledgeGraphInterface(ABC):
    """
    Interface for Knowledge Graph (RDF/SPARQL) operations
    
    Provides semantic reasoning capabilities:
    - SPARQL queries
    - Triple manipulation
    - Inference
    
    Implementations:
    - RDFLibKnowledgeGraph: SQLite + RDFLib (development/offline)
    - HANAKnowledgeGraph: HANA Knowledge Graph Engine (production/scale)
    
    NOTE: This interface is for future Phase 2 implementation (RDFLib/SPARQL)
    """
    
    @abstractmethod
    def sparql_query(self, query: str) -> List[Dict[str, Any]]:
        """Execute SPARQL query and return results"""
        pass
    
    @abstractmethod
    def add_triple(self, subject: str, predicate: str, obj: str) -> None:
        """Add RDF triple to knowledge graph"""
        pass
    
    @abstractmethod
    def get_triples(self, subject: Optional[str] = None, 
                   predicate: Optional[str] = None, 
                   obj: Optional[str] = None) -> List[tuple]:
        """Query triples matching pattern (None = wildcard)"""
        pass