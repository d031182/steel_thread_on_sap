"""
SQLite Graph Cache Repository

Production implementation using SQLite for persistence.
Uses same schema as v1 for backward compatibility.
"""
import sqlite3
import json
import logging
from typing import Optional
from datetime import datetime

from .graph_cache_repository import AbstractGraphCacheRepository, RepositoryError
from ..domain import Graph, GraphNode, GraphEdge, GraphType, NodeType, EdgeType

logger = logging.getLogger(__name__)


class SqliteGraphCacheRepository(AbstractGraphCacheRepository):
    """
    SQLite implementation of graph cache repository
    
    Schema:
    - graph_ontology: Stores graph metadata
    - graph_nodes: Stores cached nodes
    - graph_edges: Stores cached edges
    
    Same schema as v1 for backward compatibility.
    """
    
    def __init__(self, db_path: str):
        """
        Initialize with database path (injected via DI)
        
        Args:
            db_path: Path to SQLite database
                    Example: 'modules/knowledge_graph_v2/database/graph_cache.db'
        """
        self.db_path = db_path
        logger.info(f"SqliteGraphCacheRepository initialized: {db_path}")
        self._ensure_schema()
    
    def _ensure_schema(self) -> None:
        """Create cache schema if it doesn't exist"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # Enable foreign keys (required for CASCADE)
            cursor.execute("PRAGMA foreign_keys = ON")
            
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
            raise RepositoryError(f"Failed to initialize schema: {e}")
        finally:
            conn.close()
    
    def save(self, graph: Graph) -> None:
        """
        Save graph to SQLite cache
        
        Args:
            graph: Graph to save
            
        Raises:
            RepositoryError: If save fails
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # 1. Delete old ontology (CASCADE deletes nodes/edges)
            cursor.execute("""
                DELETE FROM graph_ontology WHERE graph_type = ?
            """, (graph.type.value,))
            
            # 2. Create new ontology
            cursor.execute("""
                INSERT INTO graph_ontology (graph_type, description, created_at, updated_at)
                VALUES (?, ?, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
            """, (graph.type.value, f"{graph.type.value.capitalize()} graph"))
            
            ontology_id = cursor.lastrowid
            
            # 3. Insert nodes
            for node in graph.nodes:
                # Separate core fields from properties
                properties = dict(node.properties)  # Copy
                
                cursor.execute("""
                    INSERT INTO graph_nodes (
                        ontology_id, node_key, node_label, node_type, properties_json
                    ) VALUES (?, ?, ?, ?, ?)
                """, (
                    ontology_id,
                    node.id,
                    node.label,
                    node.type.value,
                    json.dumps(properties) if properties else None
                ))
            
            # 4. Insert edges
            for edge in graph.edges:
                # Separate core fields from properties
                properties = dict(edge.properties)  # Copy
                
                cursor.execute("""
                    INSERT INTO graph_edges (
                        ontology_id, from_node_key, to_node_key,
                        edge_type, edge_label, properties_json
                    ) VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    ontology_id,
                    edge.source_id,
                    edge.target_id,
                    edge.type.value,
                    edge.label,
                    json.dumps(properties) if properties else None
                ))
            
            conn.commit()
            logger.info(f"Saved graph '{graph.id}' ({graph.type.value}): {len(graph.nodes)} nodes, {len(graph.edges)} edges")
            
        except Exception as e:
            conn.rollback()
            logger.error(f"Error saving graph: {e}")
            raise RepositoryError(f"Failed to save graph: {e}")
        finally:
            conn.close()
    
    def get(self, graph_id: str, graph_type: GraphType) -> Optional[Graph]:
        """
        Retrieve graph from SQLite cache
        
        Args:
            graph_id: Identifier of graph (not used in v1 schema, but kept for interface)
            graph_type: Type of graph
            
        Returns:
            Graph if found, None otherwise
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # Get ontology
            cursor.execute("""
                SELECT ontology_id FROM graph_ontology
                WHERE graph_type = ?
                ORDER BY created_at DESC LIMIT 1
            """, (graph_type.value,))
            
            row = cursor.fetchone()
            if not row:
                logger.info(f"No cached {graph_type.value} graph found")
                return None
            
            ontology_id = row[0]
            
            # Create graph (use graph_id from parameter, not graph_type)
            graph = Graph(graph_id, graph_type)
            
            # Load nodes
            cursor.execute("""
                SELECT node_key, node_label, node_type, properties_json
                FROM graph_nodes
                WHERE ontology_id = ?
            """, (ontology_id,))
            
            for node_key, node_label, node_type, properties_json in cursor.fetchall():
                # Parse properties
                properties = json.loads(properties_json) if properties_json else {}
                
                # Map node_type string to enum
                node_type_enum = self._parse_node_type(node_type)
                
                # Create and add node
                node = GraphNode(node_key, node_label, node_type_enum, properties)
                graph.add_node(node)
            
            # Load edges
            cursor.execute("""
                SELECT from_node_key, to_node_key, edge_type, edge_label, properties_json
                FROM graph_edges
                WHERE ontology_id = ?
            """, (ontology_id,))
            
            for from_key, to_key, edge_type, edge_label, properties_json in cursor.fetchall():
                # Parse properties
                properties = json.loads(properties_json) if properties_json else {}
                
                # Map edge_type string to enum
                edge_type_enum = self._parse_edge_type(edge_type)
                
                # Create and add edge
                edge = GraphEdge(from_key, to_key, edge_type_enum, edge_label, properties)
                graph.add_edge(edge)
            
            logger.info(f"Loaded graph '{graph_type.value}': {len(graph.nodes)} nodes, {len(graph.edges)} edges")
            return graph
            
        except Exception as e:
            logger.error(f"Error loading graph: {e}")
            return None
        finally:
            conn.close()
    
    def exists(self, graph_id: str, graph_type: GraphType) -> bool:
        """
        Check if graph exists in cache
        
        Args:
            graph_id: Identifier of graph (not used in v1 schema)
            graph_type: Type of graph
            
        Returns:
            True if cached, False otherwise
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                SELECT COUNT(*) FROM graph_ontology WHERE graph_type = ?
            """, (graph_type.value,))
            
            count = cursor.fetchone()[0]
            return count > 0
            
        finally:
            conn.close()
    
    def delete(self, graph_id: str, graph_type: GraphType) -> bool:
        """
        Delete graph from cache
        
        Args:
            graph_id: Identifier of graph (not used in v1 schema)
            graph_type: Type of graph
            
        Returns:
            True if deleted, False if not found
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # Enable foreign keys for CASCADE
            cursor.execute("PRAGMA foreign_keys = ON")
            
            cursor.execute("""
                DELETE FROM graph_ontology WHERE graph_type = ?
            """, (graph_type.value,))
            
            deleted = cursor.rowcount > 0
            conn.commit()
            
            if deleted:
                logger.info(f"Deleted {graph_type.value} cache")
            
            return deleted
            
        except Exception as e:
            conn.rollback()
            logger.error(f"Error deleting graph: {e}")
            raise RepositoryError(f"Failed to delete graph: {e}")
        finally:
            conn.close()
    
    def clear_all(self) -> int:
        """
        Clear all cached graphs
        
        Returns:
            Number of graphs deleted
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # Enable foreign keys for CASCADE
            cursor.execute("PRAGMA foreign_keys = ON")
            
            cursor.execute("SELECT COUNT(*) FROM graph_ontology")
            count = cursor.fetchone()[0]
            
            cursor.execute("DELETE FROM graph_ontology")
            conn.commit()
            
            logger.info(f"Cleared all caches ({count} graphs)")
            return count
            
        except Exception as e:
            conn.rollback()
            logger.error(f"Error clearing cache: {e}")
            raise RepositoryError(f"Failed to clear cache: {e}")
        finally:
            conn.close()
    
    def _parse_node_type(self, node_type_str: Optional[str]) -> NodeType:
        """Parse node type string to enum"""
        if not node_type_str:
            return NodeType.TABLE  # Default
        
        type_map = {
            'table': NodeType.TABLE,
            'record': NodeType.RECORD,
            'product': NodeType.PRODUCT,
            'column': NodeType.COLUMN
        }
        
        return type_map.get(node_type_str.lower(), NodeType.TABLE)
    
    def _parse_edge_type(self, edge_type_str: Optional[str]) -> EdgeType:
        """Parse edge type string to enum"""
        if not edge_type_str:
            return EdgeType.REFERENCES  # Default
        
        type_map = {
            'fk': EdgeType.FOREIGN_KEY,
            'foreign_key': EdgeType.FOREIGN_KEY,
            'contains': EdgeType.CONTAINS,
            'references': EdgeType.REFERENCES
        }
        
        return type_map.get(edge_type_str.lower(), EdgeType.REFERENCES)