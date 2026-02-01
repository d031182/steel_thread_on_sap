"""
VisJs Translator Service

Translates graph cache (graph_nodes/graph_edges) to vis.js format.
Fast, simple transformation (<1s).
"""

import json
import sqlite3
from typing import Dict, List, Any


class VisJsTranslator:
    """Translates graph cache to vis.js format"""
    
    def __init__(self, db_path: str):
        """Initialize with database path"""
        self.db_path = db_path
    
    def get_visjs_graph(self, graph_type: str = 'schema') -> Dict[str, Any]:
        """
        Get graph in vis.js format from cache
        
        Args:
            graph_type: 'schema' or 'data'
            
        Returns:
            {
                'nodes': [...],  # vis.js nodes
                'edges': [...],  # vis.js edges
                'stats': {...}   # Metadata
            }
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        try:
            # 1. Get ontology
            cursor.execute("""
                SELECT ontology_id, graph_type, updated_at
                FROM graph_ontology
                WHERE graph_type = ?
            """, (graph_type,))
            
            ontology_row = cursor.fetchone()
            
            if not ontology_row:
                return {
                    'nodes': [],
                    'edges': [],
                    'stats': {
                        'error': f'No cache found for graph_type={graph_type}',
                        'cache_exists': False
                    }
                }
            
            ontology_id = ontology_row['ontology_id']
            
            # 2. Load nodes
            cursor.execute("""
                SELECT node_key, node_label, node_type, properties_json
                FROM graph_nodes
                WHERE ontology_id = ?
            """, (ontology_id,))
            
            nodes_rows = cursor.fetchall()
            
            # 3. Transform to vis.js format
            visjs_nodes = []
            for row in nodes_rows:
                # Base node
                node = {
                    'id': row['node_key'],
                    'label': row['node_label'] or row['node_key']
                }
                
                # Add properties from JSON
                if row['properties_json']:
                    props = json.loads(row['properties_json'])
                    node.update(props)  # color, shape, etc.
                
                visjs_nodes.append(node)
            
            # 4. Load edges
            cursor.execute("""
                SELECT from_node_key, to_node_key, edge_type, edge_label, properties_json
                FROM graph_edges
                WHERE ontology_id = ?
            """, (ontology_id,))
            
            edges_rows = cursor.fetchall()
            
            # 5. Transform to vis.js format
            visjs_edges = []
            for row in edges_rows:
                # Base edge
                edge = {
                    'from': row['from_node_key'],
                    'to': row['to_node_key']
                }
                
                # Add label if present
                if row['edge_label']:
                    edge['label'] = row['edge_label']
                
                # Add properties from JSON
                if row['properties_json']:
                    props = json.loads(row['properties_json'])
                    edge.update(props)  # color, arrows, etc.
                
                visjs_edges.append(edge)
            
            # 6. Return with stats
            return {
                'nodes': visjs_nodes,
                'edges': visjs_edges,
                'stats': {
                    'node_count': len(visjs_nodes),
                    'edge_count': len(visjs_edges),
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