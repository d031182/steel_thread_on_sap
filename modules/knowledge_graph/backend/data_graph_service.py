"""
Data Graph Service

Builds a knowledge graph showing how Data Products relate to each other.
Schema-level visualization of the data architecture.

Uses ONLY the DataSource interface methods - works with any data source (SQLite, HANA, etc.)
through proper dependency injection.

@author P2P Development Team
@version 3.0.0 - Schema-level visualization (Data Product relationships)
"""

from typing import Dict, List, Any, Set, Tuple
import logging
import re

logger = logging.getLogger(__name__)


class DataGraphService:
    """Service for building knowledge graphs of Data Product relationships using DataSource interface"""
    
    def __init__(self, data_source):
        """
        Initialize with a data source
        
        Args:
            data_source: DataSource instance (any implementation: HANA, SQLite, etc.)
        """
        self.data_source = data_source
        self._fk_cache = None  # Cache schema-level FK relationships for reuse in data mode
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
    
    def build_schema_graph(self) -> Dict[str, Any]:
        """
        Build a schema-level graph showing Data Product relationships (architecture view)
        
        Shows:
        - Data Products as nodes
        - Tables within products as sub-nodes
        - Foreign key relationships between tables as edges
        
        Args:
            None
            
        Returns:
            Dictionary with nodes, edges, and statistics
        """
        try:
            logger.info("Building schema-level data product graph...")
            
            # Get all data products using interface
            products = self.data_source.get_data_products()
            
            if not products:
                logger.warning("No data products found")
                return {
                    'success': True,
                    'nodes': [],
                    'edges': [],
                    'stats': {
                        'node_count': 0,
                        'edge_count': 0,
                        'product_count': 0,
                        'table_count': 0
                    }
                }
            
            logger.info(f"Found {len(products)} data products")
            
            nodes = []
            edges = []
            table_to_product = {}  # Map table name to product
            all_tables = []
            
            # Create nodes for products and tables
            for product in products:
                product_name = product.get('productName')
                schema_name = product.get('schemaName', product_name)
                display_name = product.get('displayName', product_name)
                
                if not product_name:
                    continue
                
                # Create product node
                product_node_id = f"product-{product_name}"
                nodes.append({
                    'id': product_node_id,
                    'label': display_name or product_name,
                    'title': f"Data Product: {product_name}\n{product.get('description', '')}",
                    'group': 'product',
                    'shape': 'box',
                    'color': {
                        'background': '#1976d2',
                        'border': '#0d47a1'
                    },
                    'font': {
                        'color': 'white',
                        'size': 16,
                        'bold': True
                    },
                    'size': 30
                })
                
                # Get tables for this product
                try:
                    tables = self.data_source.get_tables(schema_name)
                    
                    for table in tables:
                        table_name = table.get('TABLE_NAME')
                        if not table_name:
                            continue
                        
                        # Create table node
                        table_node_id = f"table-{schema_name}-{table_name}"
                        nodes.append({
                            'id': table_node_id,
                            'label': table_name,
                            'title': f"Table: {table_name}\nProduct: {product_name}",
                            'group': 'table',
                            'shape': 'ellipse',
                            'color': {
                                'background': '#e3f2fd',
                                'border': '#1976d2'
                            },
                            'size': 15
                        })
                        
                        # Edge from product to table (contains relationship)
                        edges.append({
                            'from': product_node_id,
                            'to': table_node_id,
                            'arrows': 'to',
                            'color': {'color': '#666'},
                            'width': 1,
                            'dashes': False
                        })
                        
                        # Track table→product mapping for FK analysis
                        table_to_product[table_name] = {
                            'product': product_name,
                            'schema': schema_name,
                            'node_id': table_node_id
                        }
                        all_tables.append({'schema': schema_name, 'table': table_name})
                        
                except Exception as e:
                    logger.warning(f"Error getting tables for product {product_name}: {e}")
                    continue
            
            # Analyze foreign key relationships between tables
            logger.info("Analyzing foreign key relationships...")
            fk_edges = self._find_fk_relationships(all_tables, table_to_product)
            edges.extend(fk_edges)
            
            logger.info(f"Built graph: {len(nodes)} nodes, {len(edges)} edges")
            
            return {
                'success': True,
                'nodes': nodes,
                'edges': edges,
                'stats': {
                    'node_count': len(nodes),
                    'edge_count': len(edges),
                    'product_count': len(products),
                    'table_count': len(all_tables)
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
    
    def _discover_fk_mappings(self, tables: List[Dict[str, str]]) -> Dict[str, List[Tuple[str, str]]]:
        """
        Discover foreign key relationships between tables (schema analysis)
        
        Returns a mapping of: table_name → [(fk_column, target_table), ...]
        This can be reused across schema and data modes for consistency.
        
        Args:
            tables: List of {schema, table} dicts
            
        Returns:
            Dict mapping source table to list of (fk_column, target_table) tuples
        """
        fk_mappings = {}  # {table_name: [(fk_column, target_table), ...]}
        
        for table_info in tables:
            schema = table_info['schema']
            table_name = table_info['table']
            
            if table_name not in fk_mappings:
                fk_mappings[table_name] = []
            
            try:
                # Get columns for this table
                columns_result = self.data_source.get_table_structure(schema, table_name)
                columns = [col.get('COLUMN_NAME') for col in columns_result if col.get('COLUMN_NAME')]
                
                # Analyze each column for FK patterns
                for column in columns:
                    target_table = self._infer_fk_target_table(column, table_name)
                    
                    if target_table:
                        fk_mappings[table_name].append((column, target_table))
                
            except Exception as e:
                logger.warning(f"Error analyzing FKs for {schema}.{table_name}: {e}")
                continue
        
        # Cache for reuse in data mode
        self._fk_cache = fk_mappings
        
        total_fks = sum(len(fks) for fks in fk_mappings.values())
        logger.info(f"Discovered {total_fks} FK mappings across {len(fk_mappings)} tables")
        
        return fk_mappings
    
    def _find_fk_relationships(
        self, 
        tables: List[Dict[str, str]], 
        table_to_product: Dict[str, Dict]
    ) -> List[Dict]:
        """
        Find foreign key relationships between tables for schema mode visualization
        
        Uses _discover_fk_mappings() to get FK mappings, then creates edges.
        
        Args:
            tables: List of {schema, table} dicts
            table_to_product: Map of table_name to product info
            
        Returns:
            List of edge dicts for schema-level visualization
        """
        # Discover FK mappings (cached for reuse in data mode)
        fk_mappings = self._discover_fk_mappings(tables)
        
        edges = []
        
        # Create edges from FK mappings
        for source_table, fk_list in fk_mappings.items():
            source_node = table_to_product.get(source_table, {}).get('node_id')
            
            if not source_node:
                continue
            
            for fk_column, target_table in fk_list:
                if target_table in table_to_product:
                    target_node = table_to_product[target_table]['node_id']
                    
                    # Don't create self-referential edges
                    if target_node != source_node:
                        edges.append({
                            'from': source_node,
                            'to': target_node,
                            'label': fk_column,
                            'title': f"{source_table}.{fk_column} → {target_table}",
                            'arrows': 'to',
                            'color': {'color': '#ff9800'},
                            'width': 2,
                            'dashes': True
                        })
        
        logger.info(f"Found {len(edges)} foreign key relationships")
        return edges
    
    def _infer_fk_target_table(self, column_name: str, source_table: str) -> str:
        """
        Infer which table a FK column points to based on SAP naming conventions
        
        Strategy:
        1. Check for exact table name match in column (e.g., "Supplier" column → Supplier table)
        2. Check for common SAP FK patterns (e.g., "SupplierID", "CompanyCode")
        3. Check for role-based names (e.g., "InvoicingParty" → Supplier)
        
        Args:
            column_name: Column name (e.g., 'Supplier', 'CompanyCode', 'InvoicingParty')
            source_table: Source table name (to avoid self-references)
            
        Returns:
            Target table name or None
        """
        col_lower = column_name.lower()
        source_lower = source_table.lower()
        
        # Don't self-reference
        if col_lower == source_lower:
            return None
        
        # Strategy 1: Common SAP role-based columns
        role_mappings = {
            'invoicingparty': 'Supplier',
            'supplier': 'Supplier',
            'vendor': 'Supplier',
            'companycode': 'CompanyCode',
            'company': 'CompanyCode',
            'purchaseorder': 'PurchaseOrder',
            'po': 'PurchaseOrder',
            'product': 'Product',
            'material': 'Product',
            'costcenter': 'CostCenter',
            'plant': 'Plant'
        }
        
        if col_lower in role_mappings:
            target = role_mappings[col_lower]
            if target.lower() != source_lower:
                return target
        
        # Strategy 2: Check for ID/Code/Key/Number suffixes
        for suffix in ['ID', 'Code', 'Key', 'Number']:
            if column_name.endswith(suffix):
                base_name = column_name[:-len(suffix)]
                if base_name and base_name.lower() != source_lower:
                    return base_name
        
        # Strategy 3: Check if column name contains a known table name
        # Common SAP tables to look for
        known_tables = [
            'Supplier', 'Product', 'CompanyCode', 'CostCenter', 
            'PurchaseOrder', 'ServiceEntrySheet', 'JournalEntry',
            'PaymentTerms', 'Plant', 'Material'
        ]
        
        for table in known_tables:
            if table.lower() in col_lower and table.lower() != source_lower:
                return table
        
        return None
    
    def build_data_graph(self, max_records_per_table: int = 20) -> Dict[str, Any]:
        """
        Build a data-level graph showing actual record relationships (data view)
        
        Shows individual data records and how they're connected via foreign keys.
        Useful for understanding actual data flows.
        
        Args:
            max_records_per_table: Limit records to prevent overwhelming the graph
            
        Returns:
            Dictionary with nodes, edges, and statistics
        """
        try:
            logger.info(f"Building data-level graph (max {max_records_per_table} records per table)...")
            
            nodes = []
            edges = []
            
            # Get all tables with data
            all_tables = self._get_all_tables()
            
            if not all_tables:
                return {
                    'success': True,
                    'nodes': [],
                    'edges': [],
                    'stats': {'node_count': 0, 'edge_count': 0, 'table_count': 0},
                    'message': 'No tables found'
                }
            
            # Track record IDs for FK matching
            record_map = {}  # {table_name: {record_id: node_id}}
            
            # Process each table
            for table_info in all_tables:  # Process all tables with data
                schema = table_info['schema']
                table_name = table_info['table']
                
                try:
                    # Get sample records (SQLite doesn't use schema prefix)
                    query = f'SELECT * FROM {table_name} LIMIT {max_records_per_table}'
                    result = self.data_source.execute_query(query)
                    
                    if not result.get('success'):
                        continue
                    
                    # Handle both 'data' (HANA) and 'rows' (SQLite) keys
                    records = result.get('data') or result.get('rows')
                    if not records:
                        continue
                    
                    # Initialize record map for this table
                    if table_name not in record_map:
                        record_map[table_name] = {}
                    
                    # Create nodes for each record
                    for row_num, record in enumerate(records, start=1):
                        # Find primary key column
                        # First try: column name matches table name (e.g., Supplier table → Supplier column)
                        pk_value = None
                        pk_column = None
                        
                        if table_name in record:
                            pk_column = table_name
                            pk_value = record[pk_column]
                        else:
                            # Second try: column ends with ID, Code, Number, Key
                            for col in record.keys():
                                if any(col.endswith(suffix) for suffix in ['ID', 'Code', 'Number', 'Key']):
                                    if table_name.replace('_', '').lower() in col.lower():
                                        pk_value = record[col]
                                        pk_column = col
                                        break
                        
                        if not pk_value:
                            # Fallback: use first column
                            pk_column = list(record.keys())[0]
                            pk_value = record[pk_column]
                        
                        # Create node (include schema, table, pk_value AND row number for true uniqueness)
                        # Row number ensures uniqueness even when pk_value is not actually a primary key
                        node_id = f"record-{schema}-{table_name}-{pk_value}-row{row_num}"
                        node_label = f"{table_name}\n{pk_column}: {pk_value}"
                        
                        nodes.append({
                            'id': node_id,
                            'label': node_label,
                            'title': self._format_record_tooltip(table_name, record),
                            'group': table_name,
                            'shape': 'box',
                            'size': 10
                        })
                        
                        # Store for FK matching
                        record_map[table_name][str(pk_value)] = node_id
                
                except Exception as e:
                    logger.warning(f"Error processing {schema}.{table_name}: {e}")
                    continue
            
            # OPTIMIZATION: Reuse schema-level FK mappings discovered during schema mode
            # If no cache, discover FKs now (lazy initialization)
            if self._fk_cache is None:
                logger.info("Discovering FK mappings for data mode...")
                self._discover_fk_mappings(all_tables)
            else:
                logger.info("Reusing cached FK mappings from schema mode")
            
            # Apply FK mappings to create edges between actual records
            logger.info("Applying FK mappings to data records...")
            edge_count = 0
            
            for table_info in all_tables:
                table_name = table_info['table']
                
                # Get FK columns for this table from cache
                fk_list = self._fk_cache.get(table_name, [])
                
                if not fk_list or table_name not in record_map:
                    continue
                
                # For each record in this table
                try:
                    query = f"SELECT * FROM {table_name} LIMIT {max_records_per_table}"
                    result = self.data_source.execute_query(query)
                    records = result.get('data') or result.get('rows', [])
                    
                    for record in records:
                        # Match this record by PK
                        record_pk = str(record.get(table_name) or record.get(list(record.keys())[0]))
                        
                        # Find the matching node
                        for stored_pk, node_id in record_map[table_name].items():
                            if stored_pk == record_pk:
                                # Apply each FK mapping
                                for fk_column, target_table in fk_list:
                                    fk_value = record.get(fk_column)
                                    
                                    if fk_value is not None and target_table in record_map:
                                        # Find target record with matching PK value
                                        target_node = record_map[target_table].get(str(fk_value))
                                        
                                        if target_node:
                                            edges.append({
                                                'from': node_id,
                                                'to': target_node,
                                                'label': fk_column,
                                                'title': f"{fk_column}: {fk_value}",
                                                'arrows': 'to',
                                                'color': {'color': '#4caf50'},
                                                'width': 2
                                            })
                                            edge_count += 1
                                break
                
                except Exception as e:
                    logger.warning(f"Error applying FKs for {table_name}: {e}")
                    continue
            
            logger.info(f"Created {edge_count} FK edges using cached mappings")
            
            if not nodes:
                return {
                    'success': True,
                    'nodes': [],
                    'edges': [],
                    'stats': {'node_count': 0, 'edge_count': 0, 'table_count': 0},
                    'message': 'Data-level view requires tables with actual data and foreign key relationships. Currently no data records available.'
                }
            
            logger.info(f"Built data graph: {len(nodes)} nodes, {len(edges)} edges")
            
            return {
                'success': True,
                'nodes': nodes,
                'edges': edges,
                'stats': {
                    'node_count': len(nodes),
                    'edge_count': len(edges),
                    'table_count': len(set(n['group'] for n in nodes))
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
    
    def _format_record_tooltip(self, table_name: str, record: Dict) -> str:
        """Format record data as tooltip"""
        lines = [f"Table: {table_name}", ""]
        for key, val in list(record.items())[:5]:  # First 5 columns
            lines.append(f"{key}: {val}")
        if len(record) > 5:
            lines.append(f"... +{len(record)-5} more columns")
        return "\n".join(lines)
