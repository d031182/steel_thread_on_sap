"""
Data Graph Service

Analyzes actual data in tables to build a knowledge graph of entity relationships.
Shows how data records are connected via foreign keys.

Uses the existing DataSource interface to work with any configured source (SQLite/HANA).

@author P2P Development Team
@version 1.0.0
"""

from typing import Dict, List, Any, Tuple
import logging

logger = logging.getLogger(__name__)


class DataGraphService:
    """Service for building knowledge graphs from actual table data"""
    
    def __init__(self, data_source):
        """
        Initialize with a data source
        
        Args:
            data_source: DataSource instance (HANADataSource or SQLiteDataSource)
        """
        self.data_source = data_source
    
    def _get_all_tables(self) -> List[str]:
        """Get list of all tables in the database"""
        try:
            # For SQLite, query sqlite_master
            query = "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' ORDER BY name"
            results = self.data_source.execute_query(query)
            return [row['name'] for row in results] if results else []
        except Exception as e:
            logger.error(f"Error getting table list: {e}")
            return []
    
    def build_data_graph(self, max_records_per_table: int = 20) -> Dict[str, Any]:
        """
        Build a graph of actual data relationships
        
        Args:
            max_records_per_table: Limit records to prevent overwhelming the graph
            
        Returns:
            Dictionary with nodes and edges representing actual data relationships
        """
        try:
            logger.info(f"Building data graph (max {max_records_per_table} records per table)...")
            
            # Get list of all tables directly from database
            tables = self._get_all_tables()
            
            if not tables:
                logger.warning("No tables found in database")
                return {
                    'success': True,
                    'nodes': [],
                    'edges': [],
                    'stats': {
                        'node_count': 0,
                        'edge_count': 0,
                        'table_count': 0
                    }
                }
            
            logger.info(f"Found {len(tables)} tables to process")
            
            nodes = []
            edges = []
            node_id_counter = 1
            record_to_node = {}  # Map (table, record_key) to node_id
            
            # First pass: Create nodes for each record in each table
            for table_name in tables:
                try:
                    query = f"SELECT * FROM {table_name} LIMIT {max_records_per_table}"
                    records = self.data_source.execute_query(query)
                    
                    if not records:
                        continue
                    
                    logger.info(f"Table {table_name}: {len(records)} records")
                    
                    # Get column names from first record
                    columns = list(records[0].keys())
                    pk_column = self._find_primary_key(table_name, columns)
                    
                    # Create nodes for each record
                    for record in records:
                        node_id = f"node-{node_id_counter}"
                        node_id_counter += 1
                        
                        # Get display label
                        label = self._get_record_label(table_name, record, pk_column)
                        
                        # Store mapping for FK resolution
                        if pk_column and pk_column in record and record[pk_column]:
                            record_key = record[pk_column]
                            record_to_node[(table_name, record_key)] = node_id
                        
                        # Create node
                        nodes.append({
                            'id': node_id,
                            'label': label,
                            'title': self._get_record_tooltip(table_name, record),
                            'group': table_name,
                            'table': table_name
                        })
                    
                except Exception as e:
                    logger.warning(f"Skipping table {table_name}: {e}")
                    continue
            
            # Second pass: Create edges based on FK relationships
            logger.info("Building FK relationships...")
            
            for table_name in tables:
                try:
                    query = f"SELECT * FROM {table_name} LIMIT {max_records_per_table}"
                    records = self.data_source.execute_query(query)
                    
                    if not records:
                        continue
                    
                    columns = list(records[0].keys())
                    source_pk = self._find_primary_key(table_name, columns)
                    
                    for record in records:
                        if not source_pk or source_pk not in record:
                            continue
                        
                        source_key = record[source_pk]
                        source_node = record_to_node.get((table_name, source_key))
                        
                        if not source_node:
                            continue
                        
                        # Look for FK fields
                        for field_name, field_value in record.items():
                            if field_value is None or field_name == source_pk:
                                continue
                            
                            # Check if this might be a FK
                            target_table, _ = self._infer_fk_target(field_name, field_value, tables)
                            
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
                                        'width': 2,
                                        'dashes': True
                                    })
                
                except Exception as e:
                    logger.warning(f"Error processing {table_name} for FK relationships: {e}")
                    continue
            
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
            "Code",
            f"{table_name}Number",
            "Number"
        ]
        
        for candidate in pk_candidates:
            if candidate in columns:
                return candidate
        
        # Return first column as fallback
        return columns[0] if columns else None
    
    def _get_record_label(self, table_name: str, record: Dict, pk_column: str) -> str:
        """Get a short display label for a record"""
        # Try to find a name field
        name_fields = ['Name', 'Description', 'Title', 'Text', 'SupplierName', 'CompanyCodeName']
        
        for field in name_fields:
            if field in record and record[field]:
                value = str(record[field])
                return value[:25] + ('...' if len(value) > 25 else '')
        
        # Use PK value
        if pk_column and pk_column in record and record[pk_column]:
            return f"{table_name[:15]}-{record[pk_column]}"
        
        # Use first non-null value
        for key, value in record.items():
            if value:
                s = str(value)
                return s[:20] + ('...' if len(s) > 20 else '')
        
        return table_name
    
    def _get_record_tooltip(self, table_name: str, record: Dict) -> str:
        """Get detailed tooltip for a record"""
        lines = [f"📋 {table_name}", ""]
        
        # Show up to 5 most important fields
        count = 0
        for key, value in record.items():
            if count >= 5:
                lines.append(f"... +{len(record) - 5} more fields")
                break
            if value is not None:
                value_str = str(value)
                if len(value_str) > 35:
                    value_str = value_str[:35] + '...'
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
        elif field_name.endswith('Number'):
            base_name = field_name[:-6]  # Remove 'Number'
        else:
            return None, None
        
        # Look for matching table
        for table in tables:
            if not table:
                continue
            if table.lower() == base_name.lower() or \
               base_name.lower() in table.lower():
                return table, field_name
        
        return None, None