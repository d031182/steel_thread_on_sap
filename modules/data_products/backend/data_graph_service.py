"""
Data Graph Service

Analyzes actual data in tables to build a knowledge graph of entity relationships.
Shows how data records are connected via foreign keys.

@author P2P Development Team
@version 1.0.0
"""

import sqlite3
from typing import Dict, List, Any, Set, Tuple
import logging

logger = logging.getLogger(__name__)


class DataGraphService:
    """Service for building knowledge graphs from actual table data"""
    
    def __init__(self, db_path: str = "data_products.db"):
        self.db_path = db_path
    
    def build_data_graph(self, max_records_per_table: int = 50) -> Dict[str, Any]:
        """
        Build a graph of actual data relationships
        
        Args:
            max_records_per_table: Limit records to prevent overwhelming the graph
            
        Returns:
            Dictionary with nodes and edges representing actual data relationships
        """
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            nodes = []
            edges = []
            node_id_counter = 1
            record_to_node = {}  # Map (table, record_key) to node_id
            
            # Get all tables
            cursor.execute("""
                SELECT name FROM sqlite_master 
                WHERE type='table' AND name NOT LIKE 'sqlite_%'
                ORDER BY name
            """)
            tables = [row['name'] for row in cursor.fetchall()]
            
            logger.info(f"Building data graph for {len(tables)} tables")
            
            # Process each table
            for table_name in tables:
                # Get table info
                cursor.execute(f"PRAGMA table_info({table_name})")
                columns = [row['name'] for row in cursor.fetchall()]
                
                # Find potential primary key
                pk_column = self._find_primary_key(table_name, columns)
                
                # Get sample records
                cursor.execute(f"SELECT * FROM {table_name} LIMIT {max_records_per_table}")
                records = cursor.fetchall()
                
                logger.info(f"Table {table_name}: {len(records)} records, PK: {pk_column}")
                
                # Create nodes for each record
                for record in records:
                    record_dict = dict(record)
                    
                    # Create unique node ID
                    node_id = f"node-{node_id_counter}"
                    node_id_counter += 1
                    
                    # Get display label
                    label = self._get_record_label(table_name, record_dict, pk_column)
                    
                    # Store mapping for FK resolution
                    if pk_column and pk_column in record_dict:
                        record_key = record_dict[pk_column]
                        record_to_node[(table_name, record_key)] = node_id
                    
                    # Create node
                    nodes.append({
                        'id': node_id,
                        'label': label,
                        'title': self._get_record_tooltip(table_name, record_dict),
                        'group': table_name,
                        'table': table_name,
                        'data': record_dict
                    })
            
            # Second pass: Create edges based on FK relationships
            for table_name in tables:
                cursor.execute(f"SELECT * FROM {table_name} LIMIT {max_records_per_table}")
                records = cursor.fetchall()
                columns = [row['name'] for row in cursor.fetchall()]
                
                for record in records:
                    record_dict = dict(record)
                    source_pk = self._find_primary_key(table_name, record_dict.keys())
                    
                    if not source_pk or source_pk not in record_dict:
                        continue
                        
                    source_key = record_dict[source_pk]
                    source_node = record_to_node.get((table_name, source_key))
                    
                    if not source_node:
                        continue
                    
                    # Look for FK fields
                    for field_name, field_value in record_dict.items():
                        if field_value is None:
                            continue
                        
                        # Check if this might be a FK
                        target_table, target_field = self._infer_fk_target(
                            field_name, field_value, tables
                        )
                        
                        if target_table:
                            target_node = record_to_node.get((target_table, field_value))
                            
                            if target_node and target_node != source_node:
                                edges.append({
                                    'from': source_node,
                                    'to': target_node,
                                    'label': field_name,
                                    'title': f"{table_name}.{field_name} → {target_table}",
                                    'arrows': 'to',
                                    'color': {'color': '#ff9800'},
                                    'width': 2
                                })
            
            conn.close()
            
            logger.info(f"Built graph: {len(nodes)} nodes, {len(edges)} edges")
            
            return {
                'success': True,
                'nodes': nodes,
                'edges': edges,
                'stats': {
                    'node_count': len(nodes),
                    'edge_count': len(edges),
                    'table_count': len(tables)
                }
            }
            
        except Exception as e:
            logger.error(f"Error building data graph: {e}", exc_info=True)
            return {
                'success': False,
                'error': str(e),
                'nodes': [],
                'edges': []
            }
    
    def _find_primary_key(self, table_name: str, columns: List[str]) -> str:
        """Find the primary key column for a table"""
        # Common PK patterns
        pk_candidates = [
            f"{table_name}ID",
            "ID",
            f"{table_name}Key",
            "Key",
            f"{table_name}Code",
            "Code"
        ]
        
        for candidate in pk_candidates:
            if candidate in columns:
                return candidate
        
        # Return first column as fallback
        return columns[0] if columns else None
    
    def _get_record_label(self, table_name: str, record: Dict, pk_column: str) -> str:
        """Get a short display label for a record"""
        # Try to find a name field
        name_fields = ['Name', 'Description', 'Title', 'Text']
        
        for field in name_fields:
            if field in record and record[field]:
                value = str(record[field])
                return value[:30] + ('...' if len(value) > 30 else '')
        
        # Use PK value
        if pk_column and pk_column in record:
            return f"{record[pk_column]}"
        
        # Use first non-null value
        for value in record.values():
            if value:
                s = str(value)
                return s[:20] + ('...' if len(s) > 20 else '')
        
        return table_name
    
    def _get_record_tooltip(self, table_name: str, record: Dict) -> str:
        """Get detailed tooltip for a record"""
        lines = [f"Table: {table_name}", ""]
        
        # Show up to 5 fields
        count = 0
        for key, value in record.items():
            if count >= 5:
                lines.append(f"... and {len(record) - 5} more fields")
                break
            if value is not None:
                value_str = str(value)
                if len(value_str) > 40:
                    value_str = value_str[:40] + '...'
                lines.append(f"{key}: {value_str}")
                count += 1
        
        return "\n".join(lines)
    
    def _infer_fk_target(
        self, field_name: str, field_value: Any, tables: List[str]
    ) -> Tuple[str, str]:
        """
        Infer which table a FK field points to
        
        Returns:
            (target_table, target_field) or (None, None)
        """
        # Common FK patterns
        if field_name.endswith('ID'):
            base_name = field_name[:-2]  # Remove 'ID'
        elif field_name.endswith('Code'):
            base_name = field_name[:-4]  # Remove 'Code'
        elif field_name.endswith('Key'):
            base_name = field_name[:-3]  # Remove 'Key'
        else:
            return None, None
        
        # Look for matching table
        for table in tables:
            if table.lower() == base_name.lower() or \
               table.lower().endswith(base_name.lower()):
                # Assume same column name in target table
                return table, field_name
        
        return None, None


# Singleton instance
_service_instance = None


def get_data_graph_service() -> DataGraphService:
    """Get singleton instance of DataGraphService"""
    global _service_instance
    if _service_instance is None:
        _service_instance = DataGraphService()
    return _service_instance