"""
Graph Cache Loader

Loads cached graph data from SQLite for fast repeated access.
Module-specific service (not shared infrastructure).

Previously: core/services/visjs_translator.py
Moved to module: Better encapsulation, only Knowledge Graph uses this

@author P2P Development Team
@version 1.0.0
"""

import json
import sqlite3
from typing import Dict, Any


class GraphCacheLoader:
    """
    Loads graph from persistent cache
    
    Fast path for repeated graph requests (<1s vs ~700ms rebuild).
    Returns pure data (semantic types), no styling.
    """
    
    def __init__(self, db_path: str):
        """Initialize with database path"""
        self.db_path = db_path
    
    def load_graph(self, graph_type: str = 'schema') -> Dict[str, Any]:
        """
        Load graph from cache in vis.js-compatible format
        
        Args:
            graph_type: 'schema' or 'data'
            
        Returns:
            {
                'nodes': [...],  # Nodes with semantic types (no styling)
                'edges': [...],  # Edges with semantic relationships (no styling)
                'stats': {...}   # Cache metadata
            }
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        try:
            # 1. Get ontology (determines which cache to load)
            cursor.execute("""
                SELECT ontology_id, graph_type, updated_at
                FROM graph_ontology
                WHERE graph_type = ?
            """, (graph_type,))
            
            ontology_row = cursor.fetchone()
            
            if not ontology_row:
                # No cache found - caller should rebuild
                return {
                    'nodes': [],
                    'edges': [],
                    'stats': {
                        'cache_exists': False,
                        'message': f'No cache found for graph_type={graph_type}'
                    }
                }
            
            ontology_id = ontology_row['ontology_id']
            
            # 2. Load nodes from cache
            cursor.execute("""
                SELECT node_key, node_label, node_type, properties_json
                FROM graph_nodes
                WHERE ontology_id = ?
            """, (ontology_id,))
            
            nodes_rows = cursor.fetchall()
            
            # 3. Transform to vis.js-compatible format (pure data)
            nodes = []
            for row in nodes_rows:
                # Base node structure
                node = {
                    'id': row['node_key'],
                    'label': row['node_label'] or row['node_key']
                }
                
                # Add properties from JSON (type, metadata, title - NO styling)
                if row['properties_json']:
                    props = json.loads(row['properties_json'])
                    node.update(props)
                
                nodes.append(node)
            
            # 4. Load edges from cache
            cursor.execute("""
                SELECT from_node_key, to_node_key, edge_type, edge_label, properties_json
                FROM graph_edges
                WHERE ontology_id = ?
            """, (ontology_id,))
            
            edges_rows = cursor.fetchall()
            
            # 5. Transform to vis.js-compatible format (pure data)
            edges = []
            for row in edges_rows:
                # Base edge structure
                edge = {
                    'from': row['from_node_key'],
                    'to': row['to_node_key']
                }
                
                # Add label if present
                if row['edge_label']:
                    edge['label'] = row['edge_label']
                
                # Add properties from JSON (relationship, metadata - NO styling)
                if row['properties_json']:
                    props = json.loads(row['properties_json'])
                    edge.update(props)
                
                edges.append(edge)
            
            # 6. Return with cache metadata
            return {
                'nodes': nodes,
                'edges': edges,
                'stats': {
                    'node_count': len(nodes),
                    'edge_count': len(edges),
                    'graph_type': graph_type,
                    'cache_exists': True,
                    'last_updated': ontology_row['updated_at']
                }
            }
            
        finally:
            conn.close()
    
    def check_cache_status(self, graph_type: str = 'schema') -> Dict[str, Any]:
        """
        Check if cache exists for graph type
        
        Args:
            graph_type: 'schema' or 'data'
            
        Returns:
            {
                'exists': bool,
                'node_count': int,
                'edge_count': int,
                'last_updated': str
            }
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                SELECT 
                    o.ontology_id,
                    o.updated_at,
                    (SELECT COUNT(*) FROM graph_nodes WHERE ontology_id = o.ontology_id) as node_count,
                    (SELECT COUNT(*) FROM graph_edges WHERE ontology_id = o.ontology_id) as edge_count
                FROM graph_ontology o
                WHERE o.graph_type = ?
            """, (graph_type,))
            
            row = cursor.fetchone()
            
            if not row:
                return {'exists': False}
            
            return {
                'exists': True,
                'node_count': row['node_count'],
                'edge_count': row['edge_count'],
                'last_updated': row['updated_at']
            }
            
        finally:
            conn.close()