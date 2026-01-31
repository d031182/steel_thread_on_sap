"""
Property Graph Service (NetworkX Implementation)

Implements Property Graph algorithms using NetworkX library.
Provides network analysis capabilities for Data Product relationships.

Uses NetworkX for offline/development mode. Future: Can swap to HANA Property Graph.

@author P2P Development Team
@version 1.0.0
"""

import networkx as nx
from typing import List, Dict, Any, Optional
import logging
from core.interfaces.graph import PropertyGraphInterface

logger = logging.getLogger(__name__)


class NetworkXPropertyGraph(PropertyGraphInterface):
    """
    NetworkX implementation of Property Graph interface
    
    Loads graph from DataGraphService output and provides algorithms:
    - Shortest path finding
    - Centrality analysis (betweenness, pagerank, degree, closeness)
    - Community detection (louvain, label propagation, greedy modularity)
    - Graph statistics
    
    Works offline with SQLite data. Future: Swap to HANA Property Graph for scale.
    """
    
    def __init__(self):
        """Initialize empty NetworkX graph"""
        self.graph = nx.DiGraph()  # Directed graph (edges have direction)
        logger.info("NetworkXPropertyGraph initialized")
    
    def load_from_dict(self, graph_dict: Dict[str, Any]) -> None:
        """
        Load graph from dictionary (DataGraphService output)
        
        Args:
            graph_dict: Dictionary with 'nodes' and 'edges' lists
                nodes: [{'id': str, 'label': str, 'group': str, ...}, ...]
                edges: [{'from': str, 'to': str, 'label': str, ...}, ...]
        """
        try:
            nodes = graph_dict.get('nodes', [])
            edges = graph_dict.get('edges', [])
            
            # Clear existing graph
            self.graph.clear()
            
            # Add nodes with attributes
            for node in nodes:
                node_id = node.get('id')
                if node_id:
                    # Store all node attributes
                    self.graph.add_node(node_id, **{k: v for k, v in node.items() if k != 'id'})
            
            # Add edges with attributes
            for edge in edges:
                from_node = edge.get('from')
                to_node = edge.get('to')
                if from_node and to_node:
                    # Store all edge attributes
                    self.graph.add_edge(from_node, to_node, **{k: v for k, v in edge.items() if k not in ['from', 'to']})
            
            logger.info(f"Loaded graph: {len(nodes)} nodes, {len(edges)} edges")
            
        except Exception as e:
            logger.error(f"Error loading graph: {e}", exc_info=True)
            raise
    
    def shortest_path(self, start: str, end: str) -> List[str]:
        """
        Find shortest path between two nodes
        
        Args:
            start: Starting node ID
            end: Ending node ID
            
        Returns:
            List of node IDs representing path, or empty list if no path exists
        """
        try:
            # NetworkX handles directed graphs - finds shortest directed path
            path = nx.shortest_path(self.graph, start, end)
            logger.info(f"Shortest path from {start} to {end}: {len(path)} nodes")
            return path
            
        except nx.NetworkXNoPath:
            logger.warning(f"No path exists between {start} and {end}")
            return []
            
        except nx.NodeNotFound as e:
            logger.warning(f"Node not found: {e}")
            return []
            
        except Exception as e:
            logger.error(f"Error finding shortest path: {e}", exc_info=True)
            return []
    
    def centrality(self, algorithm: str = 'betweenness') -> Dict[str, float]:
        """
        Calculate node centrality (importance/criticality)
        
        Args:
            algorithm: 'betweenness', 'pagerank', 'degree', or 'closeness'
            
        Returns:
            Dictionary mapping node_id → centrality_score
        """
        try:
            if algorithm == 'betweenness':
                # How often node appears on shortest paths (bottleneck detection)
                scores = nx.betweenness_centrality(self.graph)
                
            elif algorithm == 'pagerank':
                # Importance based on connections (like Google PageRank)
                scores = nx.pagerank(self.graph)
                
            elif algorithm == 'degree':
                # Simple count of connections
                degree_dict = dict(self.graph.degree())
                # Normalize by max possible degree
                max_degree = max(degree_dict.values()) if degree_dict else 1
                scores = {node: degree / max_degree for node, degree in degree_dict.items()}
                
            elif algorithm == 'closeness':
                # Average distance to all other nodes
                scores = nx.closeness_centrality(self.graph)
                
            else:
                raise ValueError(f"Unknown centrality algorithm: {algorithm}")
            
            logger.info(f"Calculated {algorithm} centrality for {len(scores)} nodes")
            return scores
            
        except Exception as e:
            logger.error(f"Error calculating centrality: {e}", exc_info=True)
            return {}
    
    def community_detection(self, algorithm: str = 'louvain') -> Dict[str, str]:
        """
        Detect communities/clusters in graph
        
        Args:
            algorithm: 'louvain', 'label_propagation', or 'greedy_modularity'
            
        Returns:
            Dictionary mapping node_id → community_id (e.g., 'cluster_0')
        """
        try:
            # Convert to undirected for community detection
            undirected = self.graph.to_undirected()
            
            if algorithm == 'louvain':
                # Louvain method (fast, hierarchical)
                communities = nx.community.louvain_communities(undirected)
                
            elif algorithm == 'label_propagation':
                # Label propagation (simple, fast)
                communities = list(nx.community.label_propagation_communities(undirected))
                
            elif algorithm == 'greedy_modularity':
                # Greedy modularity optimization
                communities = nx.community.greedy_modularity_communities(undirected)
                
            else:
                raise ValueError(f"Unknown community detection algorithm: {algorithm}")
            
            # Convert to dict mapping node → cluster_id
            result = {}
            for i, community in enumerate(communities):
                for node in community:
                    result[node] = f"cluster_{i}"
            
            logger.info(f"Detected {len(communities)} communities using {algorithm}")
            return result
            
        except Exception as e:
            logger.error(f"Error detecting communities: {e}", exc_info=True)
            return {}
    
    def get_graph_stats(self) -> Dict[str, Any]:
        """
        Get graph statistics and metrics
        
        Returns:
            Dictionary with graph statistics
        """
        try:
            stats = {
                'node_count': self.graph.number_of_nodes(),
                'edge_count': self.graph.number_of_edges(),
                'density': nx.density(self.graph),
                'is_directed': self.graph.is_directed()
            }
            
            # Average degree
            if stats['node_count'] > 0:
                degrees = [d for n, d in self.graph.degree()]
                stats['avg_degree'] = sum(degrees) / len(degrees)
            else:
                stats['avg_degree'] = 0
            
            # Check connectivity (use undirected version)
            undirected = self.graph.to_undirected()
            stats['is_connected'] = nx.is_connected(undirected)
            stats['num_components'] = nx.number_connected_components(undirected)
            
            # Diameter (only if connected)
            if stats['is_connected'] and stats['node_count'] > 1:
                try:
                    stats['diameter'] = nx.diameter(undirected)
                except:
                    stats['diameter'] = None
            else:
                stats['diameter'] = None
            
            logger.info(f"Graph stats: {stats['node_count']} nodes, {stats['edge_count']} edges, "
                       f"{stats['density']:.3f} density")
            return stats
            
        except Exception as e:
            logger.error(f"Error calculating graph stats: {e}", exc_info=True)
            return {
                'node_count': 0,
                'edge_count': 0,
                'density': 0.0,
                'avg_degree': 0.0,
                'is_connected': False,
                'num_components': 0,
                'diameter': None
            }
    
    def get_neighbors(self, node_id: str, max_distance: int = 1) -> List[str]:
        """
        Get neighbors within specified distance
        
        Args:
            node_id: Node to find neighbors for
            max_distance: Maximum path length (1 = direct neighbors)
            
        Returns:
            List of node IDs reachable within max_distance
        """
        try:
            if node_id not in self.graph:
                logger.warning(f"Node {node_id} not found in graph")
                return []
            
            neighbors = set()
            
            # Use shortest path lengths to find nodes within distance
            lengths = nx.single_source_shortest_path_length(self.graph, node_id, cutoff=max_distance)
            
            # Exclude the source node itself
            neighbors = [node for node, dist in lengths.items() if node != node_id]
            
            logger.info(f"Found {len(neighbors)} neighbors within distance {max_distance} of {node_id}")
            return neighbors
            
        except Exception as e:
            logger.error(f"Error getting neighbors: {e}", exc_info=True)
            return []
    
    def get_subgraph(self, node_ids: List[str]) -> Dict[str, Any]:
        """
        Extract subgraph containing only specified nodes
        
        Args:
            node_ids: List of node IDs to include
            
        Returns:
            Dictionary with 'nodes' and 'edges' for subgraph
        """
        try:
            # Get subgraph
            subgraph = self.graph.subgraph(node_ids)
            
            # Convert to dict format
            nodes = []
            for node in subgraph.nodes():
                node_data = {'id': node}
                node_data.update(subgraph.nodes[node])
                nodes.append(node_data)
            
            edges = []
            for from_node, to_node, edge_data in subgraph.edges(data=True):
                edge = {'from': from_node, 'to': to_node}
                edge.update(edge_data)
                edges.append(edge)
            
            logger.info(f"Extracted subgraph: {len(nodes)} nodes, {len(edges)} edges")
            
            return {
                'nodes': nodes,
                'edges': edges,
                'stats': {
                    'node_count': len(nodes),
                    'edge_count': len(edges)
                }
            }
            
        except Exception as e:
            logger.error(f"Error extracting subgraph: {e}", exc_info=True)
            return {'nodes': [], 'edges': [], 'stats': {'node_count': 0, 'edge_count': 0}}