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
                INSERT INTO graph_ontology (graph_type, description)
                VALUES (?, ?)
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
    
    def load_graph(self, graph_type: str = 'data') -> Dict[str, Any]:
        """
        Load graph from cache
        
        Args:
            graph_type: 'schema' or 'data'
            
        Returns:
            Dictionary with 'nodes' and 'edges' lists, or None if not cached
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # Get ontology ID for this graph type
            cursor.execute("""
                SELECT ontology_id FROM graph_ontology WHERE graph_type = ?
            """, (graph_type,))
            
            row = cursor.fetchone()
            if not row:
                return None  # Cache miss
            
            ontology_id = row[0]
            
            # Load nodes
            cursor.execute("""
                SELECT node_key, node_label, node_type, properties_json
                FROM graph_nodes
                WHERE ontology_id = ?
            """, (ontology_id,))
            
            nodes = []
            for node_key, node_label, node_type, properties_json in cursor.fetchall():
                node = {
                    'id': node_key,
                    'label': node_label,
                    'type': node_type
                }
                
                # Merge properties back into node
                if properties_json:
                    try:
                        properties = json.loads(properties_json)
                        node.update(properties)
                    except:
                        pass
                
                nodes.append(node)
            
            # Load edges
            cursor.execute("""
                SELECT from_node_key, to_node_key, edge_type, edge_label, properties_json
                FROM graph_edges
                WHERE ontology_id = ?
            """, (ontology_id,))
            
            edges = []
            for from_key, to_key, edge_type, edge_label, properties_json in cursor.fetchall():
                edge = {
                    'from': from_key,
                    'to': to_key,
                    'relationship': edge_type,  # Builders use 'relationship'
                    'label': edge_label
                }
                
                # Merge properties back into edge
                if properties_json:
                    try:
                        properties = json.loads(properties_json)
                        edge.update(properties)
                    except:
                        pass
                
                edges.append(edge)
            
            logger.info(f"Loaded {len(nodes)} nodes, {len(edges)} edges from {graph_type} cache")
            
            return {
                'nodes': nodes,
                'edges': edges
            }
            
        except Exception as e:
            logger.error(f"Error loading graph cache: {e}")
            return None
        finally:
            conn.close()
    
    def clear_cache(self, graph_type: str = 'data') -> bool:
        """
        Delete cache for graph type (CASCADE deletes nodes/edges)
        
        Args:
            graph_type: 'schema' or 'data'
            
        Returns:
            True if deleted, False if not found
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                DELETE FROM graph_ontology WHERE graph_type = ?
            """, (graph_type,))
            
            deleted = cursor.rowcount > 0
            conn.commit()
            
            if deleted:
                logger.info(f"Cleared {graph_type} cache")
            
            return deleted
            
        finally:
            conn.close()
