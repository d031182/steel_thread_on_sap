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
        import os
        logger.info(f"GraphCacheService initialized with db_path: {self.db_path}")
        logger.info(f"Absolute path resolved to: {os.path.abspath(self.db_path)}")
        logger.info(f"File exists: {os.path.exists(self.db_path)}")
        
        # Initialize schema if needed
        self._ensure_schema()
    
    def _ensure_schema(self):
        """Create cache schema if it doesn't exist"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # graph_ontology (parent table - stores graph metadata)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS graph_ontology (
                    ontology_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    graph_type TEXT NOT NULL CHECK(graph_type IN ('schema', 'data', 'csn')),
                    description TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(graph_type)
                )
            """)
            
            # graph_nodes (stores cached nodes)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS graph_nodes (
                    node_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    ontology_id INTEGER NOT NULL,
                    node_key TEXT NOT NULL,
                    node_label TEXT NOT NULL,
                    node_type TEXT,
                    properties_json TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (ontology_id) REFERENCES graph_ontology(ontology_id) ON DELETE CASCADE,
                    UNIQUE(ontology_id, node_key)
                )
            """)
            
            # graph_edges (stores cached edges)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS graph_edges (
                    edge_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    ontology_id INTEGER NOT NULL,
                    from_node_key TEXT NOT NULL,
                    to_node_key TEXT NOT NULL,
                    edge_type TEXT,
                    edge_label TEXT,
                    properties_json TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (ontology_id) REFERENCES graph_ontology(ontology_id) ON DELETE CASCADE
                )
            """)
            
            # Indexes for performance
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_nodes_ontology ON graph_nodes(ontology_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_nodes_key ON graph_nodes(ontology_id, node_key)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_edges_ontology ON graph_edges(ontology_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_edges_from ON graph_edges(ontology_id, from_node_key)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_edges_to ON graph_edges(ontology_id, to_node_key)")
            
            conn.commit()
            logger.info("Cache schema initialized successfully")
            
        except Exception as e:
            conn.rollback()
            logger.error(f"Error initializing cache schema: {e}")
            raise
        finally:
            conn.close()
    
    def load_graph(self, graph_type: str) -> Dict[str, Any]:
        """
        Load graph from cache
        
        Args:
            graph_type: Type of graph to load ('schema', 'data', 'csn')
            
        Returns:
            Dict with 'nodes', 'edges', 'cached_at' keys, or None if not found
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Get ontology
            cursor.execute("""
                SELECT ontology_id, created_at FROM graph_ontology 
                WHERE graph_type = ?
                ORDER BY created_at DESC LIMIT 1
            """, (graph_type,))
            
            row = cursor.fetchone()
            if not row:
                logger.info(f"No cached {graph_type} graph found")
                return None
            
            ontology_id, cached_at = row
            
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
                    'group': node_type
                }
                
                # Merge properties
                if properties_json:
                    properties = json.loads(properties_json)
                    node.update(properties)
                
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
                    'to': to_key
                }
                
                if edge_type:
                    edge['type'] = edge_type
                if edge_label:
                    edge['label'] = edge_label
                
                # Merge properties
                if properties_json:
                    properties = json.loads(properties_json)
                    edge.update(properties)
                
                edges.append(edge)
            
            conn.close()
            
            logger.info(f"Loaded {len(nodes)} nodes, {len(edges)} edges from {graph_type} cache")
            
            return {
                'nodes': nodes,
                'edges': edges,
                'cached_at': cached_at
            }
            
        except Exception as e:
            logger.error(f"Error loading graph cache: {e}", exc_info=True)
            return None
    
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
