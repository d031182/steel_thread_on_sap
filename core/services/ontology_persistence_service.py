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
            FROM graph_schema_edges
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
            FROM graph_schema_edges
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
        
        cursor.execute("SELECT COUNT(*) FROM graph_schema_edges")
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
                FROM graph_schema_edges
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
                        UPDATE graph_schema_edges
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
                    INSERT INTO graph_schema_edges (
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
            SET value = (SELECT COUNT(*) FROM graph_schema_edges WHERE is_active = 1)
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
            INSERT INTO graph_schema_edges (
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
            UPDATE graph_schema_edges
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
            UPDATE graph_schema_edges
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
        
        cursor.execute("SELECT COUNT(*) FROM graph_schema_edges WHERE is_active = 1")
        total = cursor.fetchone()[0]
        
        cursor.execute("""
            SELECT COUNT(*) FROM graph_schema_edges 
            WHERE is_active = 1 AND confidence >= 0.9
        """)
        high_conf = cursor.fetchone()[0]
        
        cursor.execute("""
            SELECT COUNT(*) FROM graph_schema_edges 
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
        
        cursor.execute("DELETE FROM graph_schema_edges")
        count = cursor.rowcount
        
        cursor.execute("""
            UPDATE graph_ontology_metadata 
            SET value = '0' 
            WHERE key = 'total_relationships'
        """)
        
        conn.commit()
        conn.close()
        
        return count