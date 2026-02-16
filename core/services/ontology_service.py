"""
Ontology Service - Query p2p_graph.db for table name mappings

Provides a clean interface to the ontology database, which stores
mappings between logical entity names and physical table names across
different data sources (HANA, SQLite).

Usage:
    ontology = OntologyService()
    hana_table = ontology.get_table_name('SupplierInvoice', 'hana')
    # Returns: 'P2P_DATAPRODUCT_sap_bdc_SupplierInvoice_V1'
"""

import sqlite3
from typing import Optional, Dict, List
from pathlib import Path


class OntologyService:
    """
    Service for querying ontology metadata from p2p_graph.db
    
    The ontology database stores:
    - Entity definitions (logical names)
    - Properties (including physical table names per datasource)
    - Relationships between entities
    """
    
    def __init__(self, db_path: str = 'database/p2p_graph.db'):
        """
        Initialize ontology service
        
        Args:
            db_path: Path to p2p_graph.db (relative to project root)
        """
        self.db_path = db_path
        self._connection = None
    
    def _get_connection(self) -> sqlite3.Connection:
        """Get or create database connection"""
        if self._connection is None:
            self._connection = sqlite3.connect(self.db_path)
            self._connection.row_factory = sqlite3.Row
        return self._connection
    
    def get_table_name(self, entity_name: str, datasource: str) -> Optional[str]:
        """
        Get physical table name for an entity in a specific datasource
        
        Args:
            entity_name: Logical entity name (e.g., 'SupplierInvoice')
            datasource: Data source identifier ('hana', 'sqlite', 'p2p_data')
        
        Returns:
            Physical table name or None if not found
            
        Examples:
            get_table_name('SupplierInvoice', 'hana')
            # Returns: 'P2P_DATAPRODUCT_sap_bdc_SupplierInvoice_V1'
            
            get_table_name('SupplierInvoice', 'sqlite')
            # Returns: 'SupplierInvoice'
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        
        # Normalize datasource name
        datasource_key = self._normalize_datasource(datasource)
        
        # Query ontology for table name property
        # Property key format: 'table_name_{datasource}' or 'physical_table_{datasource}'
        query = """
        SELECT p.value
        FROM entities e
        JOIN properties p ON e.entity_id = p.entity_id
        WHERE e.name = ?
        AND (p.key = ? OR p.key = ? OR p.key LIKE ?)
        LIMIT 1
        """
        
        result = cursor.execute(
            query,
            (
                entity_name,
                f'table_name_{datasource_key}',
                f'physical_table_{datasource_key}',
                f'%{datasource_key}%table%'
            )
        ).fetchone()
        
        if result:
            return result['value']
        
        # Fallback: if datasource is sqlite/p2p_data, just use entity name
        if datasource_key in ['sqlite', 'p2p_data']:
            return entity_name
        
        return None
    
    def get_all_table_mappings(self, datasource: str) -> Dict[str, str]:
        """
        Get all entity-to-table mappings for a datasource
        
        Args:
            datasource: Data source identifier ('hana', 'sqlite', 'p2p_data')
        
        Returns:
            Dict mapping entity names to physical table names
            
        Example:
            mappings = ontology.get_all_table_mappings('hana')
            # Returns: {
            #     'SupplierInvoice': 'P2P_DATAPRODUCT_sap_bdc_SupplierInvoice_V1',
            #     'PurchaseOrder': 'P2P_DATAPRODUCT_sap_bdc_PurchaseOrder_V1',
            #     ...
            # }
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        
        datasource_key = self._normalize_datasource(datasource)
        
        # Query all entities and their table names
        query = """
        SELECT DISTINCT e.name, p.value
        FROM entities e
        JOIN properties p ON e.entity_id = p.entity_id
        WHERE (p.key = ? OR p.key = ? OR p.key LIKE ?)
        """
        
        results = cursor.execute(
            query,
            (
                f'table_name_{datasource_key}',
                f'physical_table_{datasource_key}',
                f'%{datasource_key}%table%'
            )
        ).fetchall()
        
        mappings = {}
        for row in results:
            mappings[row['name']] = row['value']
        
        # Fallback for SQLite: entity name = table name
        if datasource_key in ['sqlite', 'p2p_data'] and not mappings:
            # Get all entities
            cursor.execute("SELECT name FROM entities WHERE type='entity'")
            for row in cursor.fetchall():
                entity_name = row['name']
                mappings[entity_name] = entity_name
        
        return mappings
    
    def _normalize_datasource(self, datasource: str) -> str:
        """Normalize datasource name for property key lookup"""
        # Map variations to standard keys
        datasource_map = {
            'hana': 'hana',
            'hana_cloud': 'hana',
            'sqlite': 'sqlite',
            'p2p_data': 'sqlite',  # p2p_data uses SQLite backend
        }
        return datasource_map.get(datasource.lower(), datasource.lower())
    
    def close(self):
        """Close database connection"""
        if self._connection:
            self._connection.close()
            self._connection = None
    
    def __enter__(self):
        """Context manager support"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager support"""
        self.close()


# Singleton instance
_ontology_service = None


def get_ontology_service() -> OntologyService:
    """Get singleton ontology service instance"""
    global _ontology_service
    if _ontology_service is None:
        _ontology_service = OntologyService()
    return _ontology_service