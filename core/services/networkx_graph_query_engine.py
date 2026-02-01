"""
NetworkX Graph Query Engine

DEPRECATED: This engine loads from old graph_schema_edges tables which are being removed.

STATUS: Deprecated in v3.19 (Cache Consolidation)
REPLACEMENT: Use GraphCacheService + DataGraphBuilder for visualization
FUTURE: Will be rewritten to load from graph_ontology/nodes/edges tables

SQLite + NetworkX fallback implementation of IGraphQueryEngine.
Provides graph query operations using in-memory NetworkX graphs.

Features:
- Loads graph from SQLite + ontology cache
- In-memory processing (fast for < 100K nodes)
- Full NetworkX algorithm support
- Zero HANA dependency

@author P2P Development Team
@version 1.0.0 - DEPRECATED
"""

import sqlite3
import json
from typing import List, Dict, Optional, Set
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
    1. Load ontology from graph_schema_edges (cached relationships)
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
        
        DEPRECATED: This loads from graph_schema_edges which is being removed.
        
        Process:
        1. Load ontology (relationships) from graph_schema_edges (OLD - DEPRECATED)
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
        
        # Step 1: Load ontology (relationships) from OLD tables (DEPRECATED)
        # Check if old tables exist (graceful degradation during migration)
        try:
            cursor.execute("""
                SELECT name FROM sqlite_master 
                WHERE type='table' AND name='graph_schema_edges'
            """)
            if not cursor.fetchone():
                print("[WARN] NetworkXGraphQueryEngine: graph_schema_edges table not found")
                print("[WARN] This engine is deprecated - use DataGraphBuilder instead")
                conn.close()
                self._graph = G  # Empty graph
                return G
        except sqlite3.Error:
            conn.close()
            self._graph = G
            return G
        
        cursor.execute("""
            SELECT source_table, source_column, target_table, target_column, relationship_type
            FROM graph_schema_edges
            WHERE is_active = 1 AND confidence >= 0.7
            ORDER BY confidence DESC
        """)
        
        relationships = cursor.fetchall()
        nodes_added = set()
        edges_added = 0
        
        # Step 2: For each relationship, load actual data
        for src_table, src_col, tgt_table, tgt_col, rel_type in relationships:
            try:
                # Get primary key columns for both tables
                cursor.execute(f"PRAGMA table_info({src_table})")
                src_pk = next((row[1] for row in cursor.fetchall() if row[5] > 0), src_table)
                
                cursor.execute(f"PRAGMA table_info({tgt_table})")
                tgt_pk = next((row[1] for row in cursor.fetchall() if row[5] > 0), tgt_table)
                
                # Query relationships from data
                query = f"""
                    SELECT DISTINCT 
                        src.{src_pk} as src_id,
                        tgt.{tgt_pk} as tgt_id
                    FROM {src_table} src
                    INNER JOIN {tgt_table} tgt ON src.{src_col} = tgt.{tgt_col or tgt_pk}
                """
                
                cursor.execute(query)
                
                for src_id, tgt_id in cursor.fetchall():
                    src_node_id = f"{src_table}:{src_id}"
                    tgt_node_id = f"{tgt_table}:{tgt_id}"
                    
                    # Add nodes if not exists
                    if src_node_id not in nodes_added:
                        G.add_node(src_node_id, label=src_table, table=src_table, record_id=src_id)
                        nodes_added.add(src_node_id)
                    
                    if tgt_node_id not in nodes_added:
                        G.add_node(tgt_node_id, label=tgt_table, table=tgt_table, record_id=tgt_id)
                        nodes_added.add(tgt_node_id)
                    
                    # Add edge
                    G.add_edge(
                        src_node_id,
                        tgt_node_id,
                        label=rel_type,
                        type=rel_type,
                        source_table=src_table,
                        target_table=tgt_table
                    )
                    edges_added += 1
            
            except sqlite3.Error as e:
                # Skip relationships that fail (table doesn't exist, etc.)
                print(f"[WARN] Skipped {src_table}->{tgt_table}: {e}")
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
    
    def get_pagerank(self, alpha: float = 0.85) -> Dict[str, float]:
        """
        Calculate PageRank for all nodes.
        
        Args:
            alpha: Damping parameter (0.85 is Google's original value)
            
        Returns:
            Dict mapping node_id to PageRank score
        """
        G = self._ensure_graph_loaded()
        return nx.pagerank(G, alpha=alpha)
    
    def get_betweenness_centrality(self) -> Dict[str, float]:
        """
        Calculate betweenness centrality (how often node is on shortest paths).
        
        Returns:
            Dict mapping node_id to centrality score
        """
        G = self._ensure_graph_loaded()
        return nx.betweenness_centrality(G)
    
    def get_degree_centrality(self) -> Dict[str, float]:
        """
        Calculate degree centrality (number of connections).
        
        Returns:
            Dict mapping node_id to degree centrality
        """
        G = self._ensure_graph_loaded()
        return nx.degree_centrality(G)
    
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