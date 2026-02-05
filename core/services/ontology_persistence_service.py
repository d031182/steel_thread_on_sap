"""
Graph Ontology Persistence Service

Manages persistent storage of graph schema ontologies.
Provides caching, manual overrides, and incremental updates.

Aligns with HANA Property Graph engine architecture.

@author P2P Development Team
@version 1.0.0
"""

import sqlite3
from datetime import datetime
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass


@dataclass
class SchemaEdge:
    """Represents a schema relationship"""
    source_table: str
    source_column: str
    target_table: str
    target_column: Optional[str]
    relationship_type: str
    confidence: float
    discovery_method: str
    is_active: bool = True
    notes: Optional[str] = None
    edge_id: Optional[int] = None


class OntologyPersistenceService:
    """
    Service for persisting and managing graph ontologies.
    
    Features:
    - Cache discovered relationships in database
    - Support manual overrides and verification
    - Incremental updates (only changed relationships)
    - Query optimization via indexed lookups
    """
    
    def __init__(self, db_path: str):
        """
        Initialize service.
        
        Args:
            db_path: Path to SQLite database
        """
        self.db_path = db_path
    
    # ========================================================================
    # READ Operations (Fast Cached Lookups)
    # ========================================================================
    
    def get_all_relationships(self, active_only: bool = True) -> List[SchemaEdge]:
        """
        Get all cached relationships from database.
        
        Args:
            active_only: If True, only return active relationships
            
        Returns:
            List of SchemaEdge objects
            
        Performance: ~50ms for 100+ relationships (vs. 2-3s discovery)
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        query = """
            SELECT 
                edge_id, source_table, source_column, 
                target_table, target_column, relationship_type,
                confidence, discovery_method, is_active, notes
            FROM graph_edges
        """
        
        if active_only:
            query += " WHERE is_active = 1"
        
        query += " ORDER BY confidence DESC"
        
        cursor.execute(query)
        rows = cursor.fetchall()
        conn.close()
        
        return [
            SchemaEdge(
                edge_id=row[0],
                source_table=row[1],
                source_column=row[2],
                target_table=row[3],
                target_column=row[4],
                relationship_type=row[5],
                confidence=row[6],
                discovery_method=row[7],
                is_active=bool(row[8]),
                notes=row[9]
            )
            for row in rows
        ]
    
    def get_relationships_for_table(self, table_name: str) -> List[SchemaEdge]:
        """Get all relationships where table is source or target"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT 
                edge_id, source_table, source_column, 
                target_table, target_column, relationship_type,
                confidence, discovery_method, is_active, notes
            FROM graph_edges
            WHERE (source_table = ? OR target_table = ?)
            AND is_active = 1
            ORDER BY confidence DESC
        """, (table_name, table_name))
        
        rows = cursor.fetchall()
        conn.close()
        
        return [
            SchemaEdge(
                edge_id=row[0],
                source_table=row[1],
                source_column=row[2],
                target_table=row[3],
                target_column=row[4],
                relationship_type=row[5],
                confidence=row[6],
                discovery_method=row[7],
                is_active=bool(row[8]),
                notes=row[9]
            )
            for row in rows
        ]
    
    def is_cache_valid(self) -> bool:
        """Check if cached relationships exist"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM graph_edges")
        count = cursor.fetchone()[0]
        
        conn.close()
        return count > 0
    
    # ========================================================================
    # WRITE Operations (Persistence & Updates)
    # ========================================================================
    
    def persist_relationships(
        self, 
        relationships: List[Dict],
        discovery_method: str = 'csn_metadata'
    ) -> Tuple[int, int]:
        """
        Persist discovered relationships to database.
        
        Args:
            relationships: List of relationship dicts from RelationshipMapper
            discovery_method: How relationships were discovered
            
        Returns:
            Tuple of (inserted_count, updated_count)
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        inserted = 0
        updated = 0
        
        for rel in relationships:
            source_table = rel['source_table']
            source_column = rel['source_column']
            target_table = rel['target_table']
            target_column = rel.get('target_column')
            relationship_type = rel['type']
            confidence = rel['confidence']
            
            # Check if relationship already exists
            cursor.execute("""
                SELECT edge_id, confidence, discovery_method 
                FROM graph_edges
                WHERE source_table = ?
                AND source_column = ? 
                AND target_table = ?
                AND (target_column = ? OR (target_column IS NULL AND ? IS NULL))
            """, (source_table, source_column, target_table, target_column, target_column))
            
            existing = cursor.fetchone()
            
            if existing:
                edge_id, old_confidence, old_method = existing
                
                # Update only if confidence improved or method changed
                if confidence > old_confidence or discovery_method != old_method:
                    cursor.execute("""
                        UPDATE graph_edges
                        SET confidence = ?,
                            discovery_method = ?,
                            relationship_type = ?,
                            updated_at = CURRENT_TIMESTAMP
                        WHERE edge_id = ?
                    """, (confidence, discovery_method, relationship_type, edge_id))
                    updated += 1
            else:
                # Insert new relationship
                cursor.execute("""
                    INSERT INTO graph_edges (
                        source_table, source_column, target_table, target_column,
                        relationship_type, confidence, discovery_method
                    ) VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    source_table, source_column, target_table, target_column,
                    relationship_type, confidence, discovery_method
                ))
                inserted += 1
        
        # Update metadata
        cursor.execute("""
            UPDATE graph_ontology_metadata 
            SET value = CURRENT_TIMESTAMP
            WHERE key = 'last_discovery'
        """)
        
        cursor.execute("""
            UPDATE graph_ontology_metadata 
            SET value = (SELECT COUNT(*) FROM graph_edges WHERE is_active = 1)
            WHERE key = 'total_relationships'
        """)
        
        conn.commit()
        conn.close()
        
        return (inserted, updated)
    
    # ========================================================================
    # MANUAL OVERRIDE Operations
    # ========================================================================
    
    def add_manual_relationship(
        self,
        source_table: str,
        source_column: str,
        target_table: str,
        target_column: Optional[str],
        relationship_type: str,
        notes: Optional[str] = None
    ) -> int:
        """
        Manually add or override a relationship.
        
        Returns:
            edge_id of created/updated relationship
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO graph_edges (
                source_table, source_column, target_table, target_column,
                relationship_type, confidence, discovery_method, notes
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(source_table, source_column, target_table, target_column)
            DO UPDATE SET
                relationship_type = excluded.relationship_type,
                confidence = 1.0,
                discovery_method = 'manual_override',
                notes = excluded.notes,
                updated_at = CURRENT_TIMESTAMP
        """, (
            source_table, source_column, target_table, target_column,
            relationship_type, 1.0, 'manual_override', notes
        ))
        
        edge_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return edge_id
    
    def verify_relationship(self, edge_id: int, notes: Optional[str] = None) -> bool:
        """
        Mark a relationship as manually verified (high trust).
        
        Args:
            edge_id: ID of relationship to verify
            notes: Optional verification notes
            
        Returns:
            True if successful
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            UPDATE graph_edges
            SET discovery_method = 'manual_verified',
                confidence = 1.0,
                notes = COALESCE(?, notes),
                updated_at = CURRENT_TIMESTAMP
            WHERE edge_id = ?
        """, (notes, edge_id))
        
        success = cursor.rowcount > 0
        conn.commit()
        conn.close()
        
        return success
    
    def disable_relationship(self, edge_id: int) -> bool:
        """
        Disable a relationship without deleting (soft delete).
        
        Args:
            edge_id: ID of relationship to disable
            
        Returns:
            True if successful
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            UPDATE graph_edges
            SET is_active = 0,
                updated_at = CURRENT_TIMESTAMP
            WHERE edge_id = ?
        """, (edge_id,))
        
        success = cursor.rowcount > 0
        conn.commit()
        conn.close()
        
        return success
    
    # ========================================================================
    # UTILITY Operations
    # ========================================================================
    
    def get_statistics(self) -> Dict:
        """Get ontology statistics"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM graph_edges WHERE is_active = 1")
        total = cursor.fetchone()[0]
        
        cursor.execute("""
            SELECT COUNT(*) FROM graph_edges 
            WHERE is_active = 1 AND confidence >= 0.9
        """)
        high_conf = cursor.fetchone()[0]
        
        cursor.execute("""
            SELECT COUNT(*) FROM graph_edges 
            WHERE is_active = 1 AND discovery_method IN ('manual_verified', 'manual_override')
        """)
        manual = cursor.fetchone()[0]
        
        cursor.execute("""
            SELECT value FROM graph_ontology_metadata 
            WHERE key = 'last_discovery'
        """)
        last_discovery = cursor.fetchone()
        
        conn.close()
        
        return {
            'total_relationships': total,
            'high_confidence': high_conf,
            'manually_verified': manual,
            'last_discovery': last_discovery[0] if last_discovery else None,
            'cache_valid': total > 0
        }
    
    def clear_cache(self) -> int:
        """
        Clear all cached relationships (for full refresh).
        
        Returns:
            Number of relationships deleted
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        count = 0
        
        # Clear graph_edges table
        try:
            cursor.execute("DELETE FROM graph_edges")
            count = cursor.rowcount
        except sqlite3.OperationalError:
            # Table doesn't exist, that's OK (empty cache)
            count = 0
        
        # Update metadata if table exists
        try:
            cursor.execute("""
                UPDATE graph_ontology_metadata 
                SET value = '0' 
                WHERE key = 'total_relationships'
            """)
        except sqlite3.OperationalError:
            # Metadata table doesn't exist, that's OK
            pass
        
        conn.commit()
        conn.close()
        
        return count
    
    # ========================================================================
    # GRAPH CACHE Operations (v3.13 - Full Graph Caching)
    # ========================================================================
    
    def persist_graph_nodes(
        self, 
        nodes: List[Dict],
        mode: str  # 'schema' or 'data'
    ) -> int:
        """
        Cache complete graph nodes to database.
        
        Args:
            nodes: List of vis.js node objects (complete with colors, labels, etc.)
            mode: Graph mode ('schema' or 'data')
            
        Returns:
            Number of nodes persisted
            
        Performance: ~50ms for 100 nodes
        """
        import json
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Clear old nodes for this mode
        cursor.execute("""
            DELETE FROM graph_nodes 
            WHERE graph_mode = ?
        """, (mode,))
        
        # Insert new nodes
        for node in nodes:
            cursor.execute("""
                INSERT INTO graph_nodes (
                    node_id, label, node_type, graph_mode,
                    metadata_json, visual_properties_json
                ) VALUES (?, ?, ?, ?, ?, ?)
            """, (
                node['id'],
                node['label'],
                node.get('group', 'unknown'),
                mode,
                json.dumps(node),  # Store complete node for exact reconstruction
                json.dumps({
                    'color': node.get('color'),
                    'shape': node.get('shape'),
                    'size': node.get('size'),
                    'title': node.get('title')
                })
            ))
        
        conn.commit()
        conn.close()
        
        return len(nodes)
    
    def get_cached_graph_nodes(self, mode: str) -> List[Dict]:
        """
        Load cached graph nodes from database.
        
        Args:
            mode: Graph mode ('schema' or 'data')
            
        Returns:
            List of vis.js node objects (ready to render)
            
        Performance: ~50ms for 100 nodes
        """
        import json
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT metadata_json
            FROM graph_nodes
            WHERE graph_mode = ?
            ORDER BY node_id
        """, (mode,))
        
        rows = cursor.fetchall()
        conn.close()
        
        return [json.loads(row[0]) for row in rows]
    
    def is_graph_cache_valid(self, mode: str) -> bool:
        """
        Check if complete graph cache exists for given mode.
        
        Args:
            mode: Graph mode ('schema' or 'data')
            
        Returns:
            True if both nodes and edges are cached
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Check nodes exist for this mode
        cursor.execute("""
            SELECT COUNT(*) 
            FROM graph_nodes 
            WHERE graph_mode = ?
        """, (mode,))
        node_count = cursor.fetchone()[0]
        
        # Check edges exist (shared across modes)
        cursor.execute("SELECT COUNT(*) FROM graph_edges WHERE is_active = 1")
        edge_count = cursor.fetchone()[0]
        
        conn.close()
        
        return node_count > 0 and edge_count > 0
    
    def invalidate_graph_cache(self, mode: str = None) -> Tuple[int, int]:
        """
        Clear cached graph (nodes and optionally edges).
        
        Args:
            mode: Specific mode to clear, or None to clear all
            
        Returns:
            Tuple of (nodes_deleted, edges_deleted)
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Clear nodes
        if mode:
            cursor.execute("""
                DELETE FROM graph_nodes 
                WHERE graph_mode = ?
            """, (mode,))
        else:
            cursor.execute("DELETE FROM graph_nodes")
        
        nodes_deleted = cursor.rowcount
        
        # Clear edges (only if clearing all modes)
        edges_deleted = 0
        if not mode:
            cursor.execute("DELETE FROM graph_edges")
            edges_deleted = cursor.rowcount
        
        conn.commit()
        conn.close()
        
        return (nodes_deleted, edges_deleted)
