"""
Data Graph Service

Analyzes actual data in tables to build a knowledge graph of entity relationships.
Shows how data records are connected via foreign keys.

Uses ONLY the DataSource interface methods - works with any data source (SQLite, HANA, etc.)
through proper dependency injection.

@author P2P Development Team
@version 2.0.0 - Pure DI implementation
"""

from typing import Dict, List, Any, Tuple
import logging

logger = logging.getLogger(__name__)


class DataGraphService:
    """Service for building knowledge graphs from actual table data using DataSource interface"""
    
    def __init__(self, data_source):
        """
        Initialize with a data source
        
        Args:
            data_source: DataSource instance (any implementation: HANA, SQLite, etc.)
        """
        self.data_source = data_source
        logger.info(f"DataGraphService initialized with {type(data_source).__name__}")
    
    def _get_all_tables(self) -> List[Dict[str, str]]:
        """
        Get list of all tables from all data products using DataSource interface
        
        Returns:
            List of dicts with 'schema' and 'table' keys
        """
        all_tables = []
        
        try:
            # Get all data products
            products = self.data_source.get_data_products()
            logger.info(f"Found {len(products)} data products")
            
            # Get tables from each product
            for product in products:
                schema = product.get('schemaName', product.get('productName'))
                if not schema:
                    continue
                
                tables = self.data_source.get_tables(schema)
                if tables:
                    for table in tables:
                        table_name = table.get('TABLE_NAME')
                        if table_name:
                            all_tables.append({
                                'schema': schema,
                                'table': table_name
                            })
            
            logger.info(f"Found {len(all_tables)} tables total")
            return all_tables
            
        except Exception as e:
            logger.error(f"Error getting table list: {type(e).__name__}: {e}", exc_info=True)
            raise
    
    def build_data_graph(self, max_records_per_table: int = 20) -> Dict[str, Any]:
        """
        Build a graph of actual data relationships using DataSource interface
        
        Args:
            max_records_per_table: Limit records to prevent overwhelming the graph
            
        Returns:
            Dictionary with nodes, edges, and statistics
        """
        try:
            logger.info(f"Building data graph (max {max_records_per_table} records per table)...")
            
            # Get all tables using interface
            tables = self._get_all_tables()
            
            if not tables:
                logger.warning("No tables found")
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
            
            nodes = []
            edges = []
            node_id_counter = 1
            record_to_node = {}  # Map (schema, table, record_key) to node_id
            
            # First pass: Create nodes for each record using query_table()
            for table_info in tables:
                schema = table_info['schema']
                table_name = table_info['table']
                
                try:
                    # Use DataSource interface to query table
                    result = self.data_source.query_table(
                        schema=schema,
                        table=table_name,
                        limit=max_records_per_table,
                        offset=0
                    )
                    
                    records = result.get('rows', [])
                    if not records:
                        continue
                    
                    logger.info(f"Table {schema}.{table_name}: {len(records)} records")
                    
                    # Find primary key column
                    columns = [col['COLUMN_NAME'] for col in result.get('columns', [])]
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
                            record_to_node[(schema, table_name, record_key)] = node_id
                        
                        # Create node
                        nodes.append({
                            'id': node_id,
                            'label': label,
                            'title': self._get_record_tooltip(table_name, record),
                            'group': f"{schema}.{table_name}",
                            'table': table_name,
                            'schema': schema
                        })
                    
                except Exception as e:
                    logger.warning(f"Skipping table {schema}.{table_name}: {e}")
                    continue
            
            # Second pass: Create edges based on FK relationships
            logger.info("Building FK relationships...")
            
            for table_info in tables:
                schema = table_info['schema']
                table_name = table_info['table']
                
                try:
                    result = self.data_source.query_table(
                        schema=schema,
                        table=table_name,
                        limit=max_records_per_table,
                        offset=0
                    )
                    
                    records = result.get('rows', [])
                    if not records:
                        continue
                    
                    columns = [col['COLUMN_NAME'] for col in result.get('columns', [])]
                    source_pk = self._find_primary_key(table_name, columns)
                    
                    for record in records:
                        if not source_pk or source_pk not in record:
                            continue
                        
                        source_key = record[source_pk]
                        source_node = record_to_node.get((schema, table_name, source_key))
                        
                        if not source_node:
                            continue
                        
                        # Look for FK fields
                        for field_name, field_value in record.items():
                            if field_value is None or field_name == source_pk:
                                continue
                            
                            # Check if this might be a FK
                            target_info = self._infer_fk_target(field_name, field_value, tables)
                            
                            if target_info:
                                target_schema, target_table = target_info
                                target_node = record_to_node.get((target_schema, target_table, field_value))
                                
                                if target_node and target_node != source_node:
                                    edges.append({
                                        'from': source_node,
                                        'to': target_node,
                                        'label': field_name,
                                        'title': f"{schema}.{table_name}.{field_name} → {target_schema}.{target_table}",
                                        'arrows': 'to',
                                        'color': {'color': '#ff9800'},
                                        'width': 2,
                                        'dashes': True
                                    })
                
                except Exception as e:
                    logger.warning(f"Error processing {schema}.{table_name} for FK relationships: {e}")
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
        self, field_name: str, field_value: Any, tables: List[Dict]
    ) -> Tuple[str, str]:
        """
        Infer which table a FK field points to
        
        Args:
            field_name: Field name (e.g., 'SupplierID')
            field_value: Field value
            tables: List of table info dicts with 'schema' and 'table' keys
        
        Returns:
            (schema, table) tuple or None
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
            return None
        
        # Look for matching table
        for table_info in tables:
            table_name = table_info['table']
            schema = table_info['schema']
            
            if table_name.lower() == base_name.lower() or \
               base_name.lower() in table_name.lower():
                return (schema, table_name)
        
        return None