"""
NetworkX Graph Query Engine

SQLite + NetworkX fallback implementation of IGraphQueryEngine.
Provides graph query operations using in-memory NetworkX graphs.

Features:
- Loads graph from SQLite + ontology cache
- In-memory processing (fast for < 100K nodes)
- Full NetworkX algorithm support
- Zero HANA dependency

@author P2P Development Team
@version 1.0.0
"""

import sqlite3
import json
from typing import List, Dict, Optional, Set, Any
import networkx as nx
from datetime import datetime

from core.interfaces.graph_query import (
    IGraphQueryEngine,
    GraphNode,
    GraphEdge,
    GraphPath,
    Subgraph,
    TraversalDirection
)


class NetworkXGraphQueryEngine(IGraphQueryEngine):
    """
    NetworkX-based graph query engine for SQLite.
    
    Architecture:
    1. Load ontology from graph_edges (cached relationships)
    2. Load data from actual tables using ontology
    3. Build NetworkX DiGraph in memory
    4. Execute queries using NetworkX algorithms
    
    Performance:
    - Load time: ~100-200ms for 1000 nodes
    - Query time: <1ms for most operations
    - Best for: < 100K nodes
    
    Example:
        engine = NetworkXGraphQueryEngine('app/database/p2p_data_products.db')
        
        # Find path
        path = engine.shortest_path('Supplier:SUP001', 'Invoice:5100000001')
        print(f"Path length: {path.length}")
    """
    
    def __init__(self, db_path: str, auto_load: bool = True):
        """
        Initialize engine.
        
        Args:
            db_path: Path to SQLite database
            auto_load: If True, load graph immediately
        """
        self.db_path = db_path
        self._graph: Optional[nx.DiGraph] = None
        self._load_time: Optional[float] = None
        
        if auto_load:
            self._load_graph()
    
    # ========================================================================
    # GRAPH LOADING (Internal)
    # ========================================================================
    
    def _load_graph(self) -> nx.DiGraph:
        """
        Load graph from SQLite into NetworkX.
        
        Process:
        1. Load ontology (relationships) from graph_edges
        2. For each relationship, query actual data
        3. Build NetworkX graph with nodes & edges
        
        Returns:
            NetworkX DiGraph
        """
        if self._graph is not None:
            return self._graph
        
        start_time = datetime.now()
        
        G = nx.DiGraph()
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Step 1: Load edges from graph (simplified - just load edges)
        cursor.execute("""
            SELECT from_node_key, to_node_key, edge_type, edge_label, properties_json
            FROM graph_edges
            ORDER BY edge_id
        """)
        
        edges = cursor.fetchall()
        nodes_added = set()
        edges_added = 0
        
        # Step 2: For each edge, add nodes and edges to NetworkX graph
        for from_node, to_node, edge_type, edge_label, props_json in edges:
            try:
                # Parse properties if present
                properties = {}
                if props_json:
                    try:
                        properties = json.loads(props_json)
                    except:
                        pass
                
                # Extract table and ID from node keys (format: "TableName:ID")
                if ':' in from_node:
                    from_table, from_id = from_node.split(':', 1)
                else:
                    from_table, from_id = from_node, from_node
                
                if ':' in to_node:
                    to_table, to_id = to_node.split(':', 1)
                else:
                    to_table, to_id = to_node, to_node
                
                # Add nodes if not exists
                if from_node not in nodes_added:
                    G.add_node(from_node, label=from_table, table=from_table, record_id=from_id)
                    nodes_added.add(from_node)
                
                if to_node not in nodes_added:
                    G.add_node(to_node, label=to_table, table=to_table, record_id=to_id)
                    nodes_added.add(to_node)
                
                # Remove conflicting properties that we're setting explicitly
                # NetworkX warns if attributes are passed both as kwargs and in **kwargs dict
                # Filter out: label, type, source_table, target_table (all set as explicit kwargs below)
                safe_properties = {k: v for k, v in properties.items() 
                                  if k not in ('source_table', 'target_table', 'label', 'type')}
                
                # Add edge with explicit properties and safe additional properties
                G.add_edge(
                    from_node,
                    to_node,
                    label=edge_label or edge_type,
                    type=edge_type,
                    source_table=from_table,
                    target_table=to_table,
                    **safe_properties
                )
                edges_added += 1
            
            except Exception as e:
                # Skip edges that fail
                print(f"[WARN] Skipped edge {from_node}->{to_node}: {e}")
                continue
        
        conn.close()
        
        # Cache the graph
        self._graph = G
        self._load_time = (datetime.now() - start_time).total_seconds()
        
        print(f"[NetworkX] Loaded {len(nodes_added)} nodes, {edges_added} edges in {self._load_time*1000:.0f}ms")
        
        return G
    
    def _ensure_graph_loaded(self) -> nx.DiGraph:
        """Ensure graph is loaded, load if needed"""
        if self._graph is None:
            return self._load_graph()
        return self._graph
    
    def _get_node_properties(self, node_id: str) -> Dict:
        """
        Load full node properties from database.
        
        Args:
            node_id: Node ID (e.g., 'PurchaseOrder:PO000001')
            
        Returns:
            Dictionary of properties
        """
        table, record_id = node_id.split(':', 1)
        
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        try:
            cursor.execute(f"SELECT * FROM {table} WHERE {table} = ? LIMIT 1", (record_id,))
            row = cursor.fetchone()
            
            if row:
                return dict(row)
            return {}
        except sqlite3.Error:
            return {}
        finally:
            conn.close()
    
    # ========================================================================
    # IGraphQueryEngine Implementation
    # ========================================================================
    
    def get_neighbors(
        self,
        node_id: str,
        direction: TraversalDirection = TraversalDirection.OUTGOING,
        edge_types: Optional[List[str]] = None,
        limit: Optional[int] = None
    ) -> List[GraphNode]:
        """Get adjacent nodes using NetworkX"""
        G = self._ensure_graph_loaded()
        
        if not G.has_node(node_id):
            return []
        
        # Get neighbors based on direction
        if direction == TraversalDirection.OUTGOING:
            neighbors = list(G.successors(node_id))
        elif direction == TraversalDirection.INCOMING:
            neighbors = list(G.predecessors(node_id))
        else:  # BOTH
            neighbors = list(set(G.successors(node_id)) | set(G.predecessors(node_id)))
        
        # Filter by edge type if specified
        if edge_types:
            filtered = []
            for neighbor in neighbors:
                if direction == TraversalDirection.INCOMING:
                    edge_data = G.get_edge_data(neighbor, node_id)
                else:
                    edge_data = G.get_edge_data(node_id, neighbor)
                
                if edge_data and edge_data.get('type') in edge_types:
                    filtered.append(neighbor)
            neighbors = filtered
        
        # Apply limit
        if limit:
            neighbors = neighbors[:limit]
        
        # Convert to GraphNode objects
        return [
            GraphNode(
                id=n,
                label=G.nodes[n].get('label', ''),
                properties=G.nodes[n]
            )
            for n in neighbors
        ]
    
    def shortest_path(
        self,
        start_id: str,
        end_id: str,
        max_hops: int = 10
    ) -> Optional[GraphPath]:
        """Find shortest path using NetworkX"""
        G = self._ensure_graph_loaded()
        
        if not G.has_node(start_id) or not G.has_node(end_id):
            return None
        
        try:
            # Use NetworkX shortest_path algorithm
            path_nodes = nx.shortest_path(G, start_id, end_id)
            
            # Check max hops
            if len(path_nodes) - 1 > max_hops:
                return None
            
            # Build GraphNode objects
            nodes = [
                GraphNode(
                    id=n,
                    label=G.nodes[n].get('label', ''),
                    properties=G.nodes[n]
                )
                for n in path_nodes
            ]
            
            # Build GraphEdge objects
            edges = []
            for i in range(len(path_nodes) - 1):
                src = path_nodes[i]
                tgt = path_nodes[i + 1]
                edge_data = G.get_edge_data(src, tgt)
                
                edges.append(GraphEdge(
                    id=f"{src}->{tgt}",
                    source_id=src,
                    target_id=tgt,
                    label=edge_data.get('label', 'related') if edge_data else 'related',
                    properties=edge_data or {}
                ))
            
            return GraphPath(
                nodes=nodes,
                edges=edges,
                length=len(edges)
            )
        
        except nx.NetworkXNoPath:
            return None
        except Exception as e:
            print(f"[ERROR] shortest_path failed: {e}")
            return None
    
    def traverse(
        self,
        start_id: str,
        depth: int = 2,
        direction: TraversalDirection = TraversalDirection.OUTGOING,
        edge_types: Optional[List[str]] = None
    ) -> List[GraphNode]:
        """Breadth-first traversal using NetworkX"""
        G = self._ensure_graph_loaded()
        
        if not G.has_node(start_id):
            return []
        
        visited = set()
        queue = [(start_id, 0)]
        result_nodes = []
        
        while queue:
            node, current_depth = queue.pop(0)
            
            if node in visited or current_depth > depth:
                continue
            
            visited.add(node)
            result_nodes.append(node)
            
            # Get neighbors for next level
            if current_depth < depth:
                if direction == TraversalDirection.OUTGOING:
                    neighbors = G.successors(node)
                elif direction == TraversalDirection.INCOMING:
                    neighbors = G.predecessors(node)
                else:  # BOTH
                    neighbors = set(G.successors(node)) | set(G.predecessors(node))
                
                # Filter by edge type if specified
                if edge_types:
                    filtered = []
                    for neighbor in neighbors:
                        edge_data = G.get_edge_data(node, neighbor) or G.get_edge_data(neighbor, node)
                        if edge_data and edge_data.get('type') in edge_types:
                            filtered.append(neighbor)
                    neighbors = filtered
                
                for neighbor in neighbors:
                    if neighbor not in visited:
                        queue.append((neighbor, current_depth + 1))
        
        # Convert to GraphNode objects
        return [
            GraphNode(
                id=n,
                label=G.nodes[n].get('label', ''),
                properties=G.nodes[n]
            )
            for n in result_nodes
        ]
    
    def subgraph(
        self,
        node_ids: List[str],
        include_edges: bool = True
    ) -> Subgraph:
        """Extract subgraph using NetworkX"""
        G = self._ensure_graph_loaded()
        
        # Filter to existing nodes
        existing_nodes = [n for n in node_ids if G.has_node(n)]
        
        if not existing_nodes:
            return Subgraph()
        
        # Create subgraph
        if include_edges:
            sg = G.subgraph(existing_nodes)
        else:
            sg = nx.DiGraph()
            for node in existing_nodes:
                sg.add_node(node, **G.nodes[node])
        
        # Convert to Subgraph object
        nodes = {
            GraphNode(
                id=n,
                label=G.nodes[n].get('label', ''),
                properties=G.nodes[n]
            )
            for n in sg.nodes()
        }
        
        edges = set()
        if include_edges:
            for src, tgt in sg.edges():
                edge_data = sg.get_edge_data(src, tgt)
                edges.add(GraphEdge(
                    id=f"{src}->{tgt}",
                    source_id=src,
                    target_id=tgt,
                    label=edge_data.get('label', 'related') if edge_data else 'related',
                    properties=edge_data or {}
                ))
        
        return Subgraph(nodes=nodes, edges=edges)
    
    def get_node(self, node_id: str) -> Optional[GraphNode]:
        """Get single node"""
        G = self._ensure_graph_loaded()
        
        if not G.has_node(node_id):
            return None
        
        return GraphNode(
            id=node_id,
            label=G.nodes[node_id].get('label', ''),
            properties=G.nodes[node_id]
        )
    
    def node_exists(self, node_id: str) -> bool:
        """Check if node exists"""
        G = self._ensure_graph_loaded()
        return G.has_node(node_id)
    
    def get_node_count(self) -> int:
        """Get total node count"""
        G = self._ensure_graph_loaded()
        return G.number_of_nodes()
    
    def get_edge_count(self) -> int:
        """Get total edge count"""
        G = self._ensure_graph_loaded()
        return G.number_of_edges()
    
    def clear_cache(self) -> None:
        """Clear cached graph"""
        self._graph = None
        self._load_time = None
    
    # ========================================================================
    # ADVANCED QUERIES (NetworkX-Specific)
    # ========================================================================
    
    def get_connected_components(self) -> List[Set[str]]:
        """
        Find connected components (groups of connected nodes).
        
        Returns:
            List of sets, each set is a connected component
        """
        G = self._ensure_graph_loaded()
        
        # NetworkX requires undirected graph for connected components
        G_undirected = G.to_undirected()
        return list(nx.connected_components(G_undirected))
    
    def get_pagerank(self, top_k: int = 10, damping_factor: float = 0.85, 
                     max_iter: int = 200, tol: float = 1e-06) -> List[Dict[str, Any]]:
        """
        Calculate PageRank for all nodes, return top_k.
        
        Args:
            top_k: Number of top nodes to return
            damping_factor: Damping parameter (0.85 is Google's original value)
            max_iter: Maximum iterations (increased from NetworkX default of 100)
            tol: Convergence tolerance
            
        Returns:
            List of dicts with node_id and score, sorted by score (descending)
        """
        G = self._ensure_graph_loaded()
        
        # Handle empty graph
        if G.number_of_nodes() == 0:
            return []
        
        try:
            scores = nx.pagerank(G, alpha=damping_factor, max_iter=max_iter, tol=tol)
        except nx.PowerIterationFailedConvergence:
            # If convergence fails, try with looser tolerance
            print(f"[WARN] PageRank failed to converge after {max_iter} iterations, retrying with looser tolerance")
            try:
                scores = nx.pagerank(G, alpha=damping_factor, max_iter=max_iter, tol=1e-3)
            except:
                # Last resort: return uniform distribution
                print(f"[ERROR] PageRank still failed, returning uniform distribution")
                scores = {node: 1.0 / G.number_of_nodes() for node in G.nodes()}
        
        # Sort by score and return top_k as list of dicts
        sorted_scores = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        return [
            {'node_id': node_id, 'score': score}
            for node_id, score in sorted_scores[:top_k]
        ]
    
    def get_betweenness_centrality(self, top_k: int = 10, vertex_table: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Calculate betweenness centrality (how often node is on shortest paths).
        
        Args:
            top_k: Number of top nodes to return
            vertex_table: Optional filter by table name (e.g., 'Supplier')
            
        Returns:
            List of dicts with node_id and score, sorted by score (descending)
        """
        G = self._ensure_graph_loaded()
        
        if G.number_of_nodes() == 0:
            return []
        
        scores = nx.betweenness_centrality(G)
        
        # Filter by vertex_table if specified
        if vertex_table:
            scores = {
                node_id: score 
                for node_id, score in scores.items()
                if node_id.startswith(f"{vertex_table}:")
            }
        
        # Sort and return top_k
        sorted_scores = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        return [
            {'node_id': node_id, 'score': score}
            for node_id, score in sorted_scores[:top_k]
        ]
    
    def get_degree_centrality(self, top_k: int = 10, vertex_table: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Calculate degree centrality (number of connections).
        
        Args:
            top_k: Number of top nodes to return
            vertex_table: Optional filter by table name (e.g., 'Supplier')
            
        Returns:
            List of dicts with node_id and score, sorted by score (descending)
        """
        G = self._ensure_graph_loaded()
        
        if G.number_of_nodes() == 0:
            return []
        
        scores = nx.degree_centrality(G)
        
        # Filter by vertex_table if specified
        if vertex_table:
            scores = {
                node_id: score 
                for node_id, score in scores.items()
                if node_id.startswith(f"{vertex_table}:")
            }
        
        # Sort and return top_k
        sorted_scores = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        return [
            {'node_id': node_id, 'score': score}
            for node_id, score in sorted_scores[:top_k]
        ]
    
    def find_cycles(self) -> List[List[str]]:
        """
        Find all cycles in graph.
        
        Returns:
            List of cycles, each cycle is a list of node IDs
        """
        G = self._ensure_graph_loaded()
        try:
            return list(nx.simple_cycles(G))
        except:
            return []
    
    def get_statistics(self) -> Dict:
        """
        Get comprehensive graph statistics.
        
        Returns:
            Dictionary with various graph metrics
        """
        G = self._ensure_graph_loaded()
        
        return {
            'nodes': G.number_of_nodes(),
            'edges': G.number_of_edges(),
            'density': nx.density(G),
            'is_directed': G.is_directed(),
            'load_time_ms': self._load_time * 1000 if self._load_time else None,
            'avg_degree': sum(dict(G.degree()).values()) / G.number_of_nodes() if G.number_of_nodes() > 0 else 0
        }
    
    def export_to_json(self) -> Dict:
        """
        Export entire graph to JSON (for visualization).
        
        Returns:
            Dictionary with nodes and edges arrays
        """
        G = self._ensure_graph_loaded()
        
        nodes = [
            {
                'id': node_id,
                'label': data.get('label', ''),
                'properties': data
            }
            for node_id, data in G.nodes(data=True)
        ]
        
        edges = [
            {
                'id': f"{src}->{tgt}",
                'source': src,
                'target': tgt,
                'label': data.get('label', 'related'),
                'properties': data
            }
            for src, tgt, data in G.edges(data=True)
        ]
        
        return {
            'nodes': nodes,
            'edges': edges,
            'statistics': self.get_statistics()
        }


# Convenience function
def create_engine(db_path: str) -> NetworkXGraphQueryEngine:
    """
    Factory function to create NetworkX engine.
    
    Args:
        db_path: Path to SQLite database
        
    Returns:
        Initialized NetworkXGraphQueryEngine
    """
    return NetworkXGraphQueryEngine(db_path, auto_load=True)