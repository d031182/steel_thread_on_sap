"""
Graph Cache Service

Saves/loads pre-computed graph structures to/from cache tables.
Enables instant graph visualization (<1s vs 27s).
"""

import json
import sqlite3
import logging
from typing import List, Dict, Any
from datetime import datetime

logger = logging.getLogger(__name__)


class GraphCacheService:
    """Service for saving and clearing graph cache"""
    
    def __init__(self, db_path: str):
        """Initialize with database path"""
        self.db_path = db_path
    
    def save_graph(
        self, 
        nodes: List[Dict[str, Any]], 
        edges: List[Dict[str, Any]], 
        graph_type: str = 'data',
        description: str = None
    ) -> int:
        """
        Save graph to cache (creates ontology + nodes + edges)
        
        Args:
            nodes: List of vis.js node dicts
            edges: List of vis.js edge dicts
            graph_type: 'schema' or 'data'
            description: Optional description
            
        Returns:
            Number of nodes saved
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # 1. Delete old ontology (CASCADE deletes nodes/edges automatically)
            cursor.execute("""
                DELETE FROM graph_ontology WHERE graph_type = ?
            """, (graph_type,))
            
            # 2. Create new ontology
            cursor.execute("""
                INSERT INTO graph_ontology (graph_type, description, created_at, updated_at)
                VALUES (?, ?, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
            """, (graph_type, description or f"{graph_type.capitalize()} graph"))
            
            ontology_id = cursor.lastrowid
            
            # 3. Insert nodes
            for node in nodes:
                # Extract core fields
                node_key = node.get('id')
                node_label = node.get('label')
                node_type = node.get('group') or node.get('type')
                
                # Everything else goes into properties_json
                properties = {
                    k: v for k, v in node.items()
                    if k not in ['id', 'label', 'group', 'type']
                }
                
                cursor.execute("""
                    INSERT INTO graph_nodes (
                        ontology_id, node_key, node_label, node_type, properties_json
                    ) VALUES (?, ?, ?, ?, ?)
                """, (
                    ontology_id,
                    node_key,
                    node_label,
                    node_type,
                    json.dumps(properties) if properties else None
                ))
            
            # 4. Insert edges
            for edge in edges:
                # Extract core fields
                from_key = edge.get('from')
                to_key = edge.get('to')
                edge_type = edge.get('type')
                edge_label = edge.get('label')
                
                # Everything else goes into properties_json
                properties = {
                    k: v for k, v in edge.items()
                    if k not in ['from', 'to', 'type', 'label']
                }
                
                cursor.execute("""
                    INSERT INTO graph_edges (
                        ontology_id, from_node_key, to_node_key, 
                        edge_type, edge_label, properties_json
                    ) VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    ontology_id,
                    from_key,
                    to_key,
                    edge_type,
                    edge_label,
                    json.dumps(properties) if properties else None
                ))
            
            conn.commit()
            
            logger.info(
                f"Saved {len(nodes)} nodes, {len(edges)} edges to {graph_type} cache"
            )
            
            return len(nodes)
            
        except Exception as e:
            conn.rollback()
            logger.error(f"Error saving graph cache: {e}")
            raise
        finally:
            conn.close()
    
    def clear_cache(self, graph_type: str = None) -> int:
        """
        Delete cache for graph type (CASCADE deletes nodes/edges)
        
        Args:
            graph_type: Specific graph type to clear ('schema', 'data', 'csn'),
                       or None to clear all graph types
            
        Returns:
            Number of records deleted (ontology rows)
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            if graph_type:
                # Clear specific graph type
                cursor.execute("""
                    DELETE FROM graph_ontology WHERE graph_type = ?
                """, (graph_type,))
            else:
                # Clear all graph types
                cursor.execute("""
                    DELETE FROM graph_ontology
                """)
            
            deleted_count = cursor.rowcount
            conn.commit()
            
            if deleted_count > 0:
                if graph_type:
                    logger.info(f"Cleared {graph_type} cache ({deleted_count} records)")
                else:
                    logger.info(f"Cleared all graph caches ({deleted_count} records)")
            
            return deleted_count
            
        finally:
            conn.close()
