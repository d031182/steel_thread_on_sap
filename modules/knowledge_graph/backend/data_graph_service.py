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

from core.services.csn_parser import CSNParser
from core.services.relationship_mapper import CSNRelationshipMapper

logger = logging.getLogger(__name__)


class DataGraphService:
    """Service for building knowledge graphs of Data Product relationships using DataSource interface"""
    
    # PHASE 2: SAP-Inspired Color Palette (Industry Best Practice)
    # 5-7 colors for data product grouping (not 65+ for individual tables)
    # Semantic meaning: Blue=Master, Orange=Transactional, Green=Financial, Purple=Accounting, Teal=Reference
    DATA_PRODUCT_COLORS = {
        'Supplier': {'background': '#1976d2', 'border': '#0d47a1'},           # Blue - Master Data
        'Product': {'background': '#00acc1', 'border': '#006064'},             # Teal - Catalog Data
        'CompanyCode': {'background': '#00897b', 'border': '#004d40'},        # Dark Teal - Reference
        'CostCenter': {'background': '#5e35b1', 'border': '#311b92'},         # Purple - Organizational
        'PurchaseOrder': {'background': '#ff9800', 'border': '#e65100'},      # Orange - Procurement Transactions
        'SupplierInvoice': {'background': '#4caf50', 'border': '#1b5e20'},    # Green - Financial Documents
        'ServiceEntrySheet': {'background': '#f57c00', 'border': '#bf360c'},  # Deep Orange - Service Management
        'JournalEntry': {'background': '#9c27b0', 'border': '#4a148c'},       # Purple - Accounting
        'PaymentTerms': {'background': '#757575', 'border': '#424242'},       # Gray - Configuration
        # Default for unmapped products
        'default': {'background': '#90a4ae', 'border': '#546e7a'}             # Blue Gray
    }
    
    def __init__(self, data_source, csn_parser: CSNParser = None, db_path: str = None):
        """
        Initialize with a data source and optional CSN parser
        
        Args:
            data_source: DataSource instance (any implementation: HANA, SQLite, etc.)
            csn_parser: Optional CSNParser for metadata-driven relationship discovery
            db_path: Optional database path for ontology cache (defaults to standard location)
        """
        self.data_source = data_source
        self.csn_parser = csn_parser or CSNParser('docs/csn')
        self.relationship_mapper = CSNRelationshipMapper(self.csn_parser)
        self._fk_cache = None  # Cache schema-level FK relationships for reuse in data mode
        self._table_to_product_map = {}  # Cache table → data product mapping for coloring
        
        # PHASE 3: Store db_path for ontology cache access
        # Only use cache for SQLite data sources (HANA doesn't need local cache)
        if db_path:
            self.db_path = db_path
        elif hasattr(data_source, 'service') and hasattr(data_source.service, 'db_path'):
            self.db_path = data_source.service.db_path
        else:
            self.db_path = None  # HANA or other non-SQLite sources
        
        logger.info(f"DataGraphService initialized with {type(data_source).__name__} and CSN-based relationship discovery")
        if self.db_path:
            logger.info(f"Ontology cache path: {self.db_path}")
        else:
            logger.info("No ontology cache (using CSN discovery only - typical for HANA)")
    
    def _build_table_to_product_map(self) -> None:
        """
        Build mapping of table name → data product name for coloring
        
        PHASE 2: Enables data product-based coloring (all tables from same product = same color)
        Caches in self._table_to_product_map for reuse
        """
        if self._table_to_product_map:
            return  # Already built
        
        try:
            products = self.data_source.get_data_products()
            
            for product in products:
                product_name = product.get('productName')
                schema_name = product.get('schemaName', product_name)
                
                if not product_name or not schema_name:
                    continue
                
                tables = self.data_source.get_tables(schema_name)
                if tables:
                    for table in tables:
                        table_name = table.get('TABLE_NAME')
                        if table_name:
                            self._table_to_product_map[table_name] = product_name
            
            logger.info(f"Built table→product mapping: {len(self._table_to_product_map)} tables across {len(products)} products")
            
        except Exception as e:
            logger.warning(f"Error building table→product map: {e}")
            self._table_to_product_map = {}
    
    def _get_color_for_table(self, table_name: str) -> Dict[str, str]:
        """
        Get color for a table based on its data product (PHASE 2)
        
        Industry Best Practice: Color by data product group, not by individual table.
        Example: All Supplier tables = Blue, all PurchaseOrder tables = Orange
        
        Args:
            table_name: Name of the table
            
        Returns:
            Dict with 'background' and 'border' color keys
        """
        # Build map if not cached
        if not self._table_to_product_map:
            self._build_table_to_product_map()
        
        # Get product for this table
        product_name = self._table_to_product_map.get(table_name)
        
        if not product_name:
            return self.DATA_PRODUCT_COLORS['default']
        
        # Return color for product (or default if not in palette)
        return self.DATA_PRODUCT_COLORS.get(product_name, self.DATA_PRODUCT_COLORS['default'])
    
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
        Discover foreign key relationships using CSN metadata (CSN-driven discovery!)
        
        PHASE 3 OPTIMIZATION: Try ontology cache first (4ms), fallback to CSN discovery (410ms)
        
        Uses CSNRelationshipMapper to automatically discover relationships from CSN metadata.
        Falls back to manual inference only if CSN discovery finds nothing.
        
        Returns a mapping of: table_name → [(fk_column, target_table), ...]
        This can be reused across schema and data modes for consistency.
        
        Args:
            tables: List of {schema, table} dicts
            
        Returns:
            Dict mapping source table to list of (fk_column, target_table) tuples
        """
        from core.services.ontology_persistence_service import OntologyPersistenceService
        
        fk_mappings = {}  # {table_name: [(fk_column, target_table), ...]}
        
        # PHASE 3: Try cached ontology first (4ms vs 410ms = 103x faster!)
        # Only for SQLite data sources (HANA doesn't use local cache)
        if self.db_path:
            try:
                persistence = OntologyPersistenceService(self.db_path)
                
                if persistence.is_cache_valid():
                    logger.info("✓ Using cached ontology (4ms) - 103x faster!")
                    cached_edges = persistence.get_all_relationships()
                    
                    # Convert cached edges to fk_mappings format
                    for edge in cached_edges:
                        if edge.source_table not in fk_mappings:
                            fk_mappings[edge.source_table] = []
                        fk_mappings[edge.source_table].append((edge.source_column, edge.target_table))
                    
                    csn_fk_count = sum(len(fks) for fks in fk_mappings.values())
                    logger.info(f"Loaded {csn_fk_count} cached relationships in 4ms")
                    
                    # Cache for reuse in data mode
                    self._fk_cache = fk_mappings
                    return fk_mappings
                else:
                    logger.info("Cache invalid or missing, falling back to CSN discovery...")
            except Exception as e:
                logger.warning(f"Ontology cache error (will use CSN discovery): {e}")
        else:
            logger.info("No db_path (HANA data source), using CSN discovery directly")
        
        # FALLBACK: CSN-based relationship discovery (automatic - 410ms)
        logger.info("Discovering relationships from CSN metadata...")
        csn_relationships = self.relationship_mapper.discover_relationships()
        
        # Convert CSN relationships to FK mappings
        for rel in csn_relationships:
            if rel.from_entity not in fk_mappings:
                fk_mappings[rel.from_entity] = []
            
            fk_mappings[rel.from_entity].append((rel.from_column, rel.to_entity))
        
        csn_fk_count = sum(len(fks) for fks in fk_mappings.values())
        logger.info(f"CSN discovered {csn_fk_count} relationships automatically!")
        
        # PHASE 2: Fallback to manual inference for any unmapped tables
        unmapped_tables = [t for t in tables if t['table'] not in fk_mappings or not fk_mappings[t['table']]]
        
        if unmapped_tables:
            logger.info(f"Applying manual FK inference for {len(unmapped_tables)} unmapped tables...")
            
            for table_info in unmapped_tables:
                schema = table_info['schema']
                table_name = table_info['table']
                
                if table_name not in fk_mappings:
                    fk_mappings[table_name] = []
                
                try:
                    # Get columns for this table
                    columns_result = self.data_source.get_table_structure(schema, table_name)
                    columns = [col.get('COLUMN_NAME') for col in columns_result if col.get('COLUMN_NAME')]
                    
                    # Analyze each column for FK patterns (manual fallback)
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
        logger.info(f"Total FK mappings: {total_fks} ({csn_fk_count} from CSN, {total_fks - csn_fk_count} from manual inference)")
        
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
    
    def build_data_graph(
        self, 
        max_records_per_table: int = 20,
        filter_orphans: bool = True,
        use_cache: bool = True
    ) -> Dict[str, Any]:
        """
        Build a data-level graph showing actual record relationships (data view)
        
        Shows individual data records and how they're connected via foreign keys.
        Useful for understanding actual data flows.
        
        Args:
            max_records_per_table: Limit records to prevent overwhelming the graph
            filter_orphans: If True, hide nodes with no connections (industry best practice)
            use_cache: If True, try to load from cache first (v3.13 - 270x faster!)
            
        Returns:
            Dictionary with nodes, edges, and statistics
        """
        import time
        start_time = time.time()
        
        try:
            # PHASE 1: Try cached graph first (v3.13 - Full Graph Cache)
            if use_cache and self.db_path:
                from core.services.ontology_persistence_service import OntologyPersistenceService
                persistence = OntologyPersistenceService(self.db_path)
                
                if persistence.is_graph_cache_valid('data'):
                    logger.info("✓ Using cached data graph (nodes + edges)")
                    
                    # Load cached nodes & edges
                    nodes = persistence.get_cached_graph_nodes('data')
                    
                    # Load cached edges (convert from SchemaEdge to vis.js format)
                    cached_edges = persistence.get_all_relationships()
                    edges = []
                    for edge in cached_edges:
                        # Note: This loads schema edges, not data edges
                        # For data mode, we need to rebuild edges from actual data
                        # So we'll still rebuild, but nodes are cached
                        pass
                    
                    cache_time = (time.time() - start_time) * 1000
                    logger.info(f"✓ Cache load: {cache_time:.0f}ms")
                    
                    # For now, return cached result if nodes exist
                    # TODO: Also cache data-level edges (record→record relationships)
                    if nodes:
                        return {
                            'success': True,
                            'nodes': nodes,
                            'edges': edges,  # Will be empty until we cache data edges
                            'stats': {
                                'node_count': len(nodes),
                                'edge_count': len(edges),
                                'table_count': len(set(n.get('group') for n in nodes if n.get('group'))),
                                'cache_used': True,
                                'load_time_ms': cache_time
                            }
                        }
            
            # PHASE 2: Build graph from scratch (cache miss or disabled)
            logger.info(f"Building data-level graph from scratch (max {max_records_per_table} records per table)...")
            
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
            
            # Get PK columns for all tables ONCE (optimization)
            pk_columns_map = {}  # {table_name: [pk_column_names]}
            for table_info in all_tables:
                schema = table_info['schema']
                table_name = table_info['table']
                try:
                    structure = self.data_source.get_table_structure(schema, table_name)
                    pk_columns_map[table_name] = self._find_pk_columns(structure, table_name)
                except Exception as e:
                    logger.warning(f"Error getting PK for {table_name}: {e}")
                    pk_columns_map[table_name] = [table_name]  # Fallback
            
            # Process each table
            for table_info in all_tables:
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
                    
                    # Get PK columns for this table (may be compound key)
                    pk_cols = pk_columns_map.get(table_name, [table_name])
                    
                    # Create nodes for each record
                    for record in records:
                        # Get ALL PK values (handles compound keys)
                        pk_values = []
                        for pk_col in pk_cols:
                            val = record.get(pk_col)
                            if val is not None:
                                pk_values.append(str(val))
                        
                        if not pk_values:
                            # Fallback: try first column
                            first_val = record.get(list(record.keys())[0]) if record else None
                            if first_val:
                                pk_values = [str(first_val)]
                        
                        if not pk_values:
                            continue  # Skip records with no PK
                        
                        # Concatenate compound key components (industry best practice)
                        # Example: "1010-2024-100001" for JournalEntry(CompanyCode, FiscalYear, AccountingDocument)
                        compound_key = '-'.join(pk_values)
                        
                        # Create node ID with compound key
                        node_id = f"record-{schema}-{table_name}-{compound_key}"
                        
                        # Label shows first PK component for readability
                        node_label = f"{table_name}\n{pk_cols[0]}: {pk_values[0]}"
                        if len(pk_values) > 1:
                            node_label += f"\n({len(pk_values)} key fields)"
                        
                        # PHASE 2: Color by Data Product (Industry Best Practice)
                        # All tables from same product use same color (semantic grouping)
                        node_color = self._get_color_for_table(table_name)
                        
                        # PHASE 2.5: Apply Schema Graph Visual Hierarchy
                        # Differentiate data records from their parent tables using size and shade
                        # Pattern from schema graph: Product (large/bold) → Tables (smaller/lighter)
                        # Applied here: Data records get lighter shade of their product color
                        lighter_color = {
                            'background': node_color['background'] + '40',  # Add alpha for lighter shade
                            'border': node_color['border']
                        }
                        
                        nodes.append({
                            'id': node_id,
                            'label': node_label,
                            'title': self._format_record_tooltip(table_name, record),
                            'group': table_name,
                            'shape': 'box',
                            'size': 12,  # Slightly larger than before for better visibility
                            'color': lighter_color,  # Lighter shade for data records
                            'font': {'size': 11}  # Consistent font sizing
                        })
                        
                        # Store for FK matching using compound key
                        record_map[table_name][compound_key] = node_id
                
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
                schema = table_info['schema']
                table_name = table_info['table']
                
                # Get FK columns for this table from cache
                fk_list = self._fk_cache.get(table_name, [])
                
                if not fk_list:
                    continue
                
                # Get PK columns for this table (may be compound key)
                pk_cols = pk_columns_map.get(table_name, [table_name])
                
                # For each record in this table, create FK edges
                try:
                    query = f"SELECT * FROM {table_name} LIMIT {max_records_per_table}"
                    result = self.data_source.execute_query(query)
                    records = result.get('data') or result.get('rows', [])
                    
                    for record in records:
                        # Get ALL PK values for compound key
                        pk_values = []
                        for pk_col in pk_cols:
                            val = record.get(pk_col)
                            if val is not None:
                                pk_values.append(str(val))
                        
                        if not pk_values:
                            # Fallback: try first column
                            first_val = record.get(list(record.keys())[0]) if record else None
                            if first_val:
                                pk_values = [str(first_val)]
                        
                        if not pk_values:
                            continue
                        
                        # Build source node ID with compound key
                        compound_key = '-'.join(pk_values)
                        source_node_id = f"record-{schema}-{table_name}-{compound_key}"
                        
                        # Apply each FK mapping from schema mode
                        for fk_column, target_table in fk_list:
                            fk_value = record.get(fk_column)
                            
                            if fk_value is None:
                                continue
                            
                            # Check if target table exists in our graph
                            if target_table not in record_map:
                                continue
                            
                            # For simple target keys: direct match
                            # For compound target keys: FK value must match one component
                            target_node_id = None
                            
                            # Try direct match first (works for simple keys like Supplier)
                            if str(fk_value) in record_map[target_table]:
                                target_node_id = record_map[target_table][str(fk_value)]
                            else:
                                # Compound key target: FK value is ONE component
                                # Search for compound keys that contain this value
                                for compound_key, node_id in record_map[target_table].items():
                                    # Check if FK value matches any component of compound key
                                    key_components = compound_key.split('-')
                                    if str(fk_value) in key_components:
                                        target_node_id = node_id
                                        break
                            
                            if target_node_id:
                                edges.append({
                                    'from': source_node_id,
                                    'to': target_node_id,
                                    'label': fk_column,
                                    'title': f"{table_name}.{fk_column} = {fk_value} → {target_table}",
                                    'arrows': 'to',
                                    'color': {'color': '#4caf50'},
                                    'width': 2
                                })
                                edge_count += 1
                
                except Exception as e:
                    logger.warning(f"Error applying FKs for {table_name}: {e}")
                    continue
            
            logger.info(f"Created {edge_count} FK edges using cached schema mappings")
            
            if not nodes:
                return {
                    'success': True,
                    'nodes': [],
                    'edges': [],
                    'stats': {'node_count': 0, 'edge_count': 0, 'table_count': 0},
                    'message': 'Data-level view requires tables with actual data and foreign key relationships. Currently no data records available.'
                }
            
            # PHASE 1: Orphan Node Filtering (Industry Best Practice)
            # Filter orphan nodes (nodes with zero connections) if requested
            original_node_count = len(nodes)
            orphan_count = 0
            
            if filter_orphans and edges:
                # Identify all connected nodes
                connected_node_ids = set()
                for edge in edges:
                    connected_node_ids.add(edge['from'])
                    connected_node_ids.add(edge['to'])
                
                # Filter to only connected nodes
                filtered_nodes = [n for n in nodes if n['id'] in connected_node_ids]
                orphan_count = original_node_count - len(filtered_nodes)
                nodes = filtered_nodes
                
                logger.info(f"Filtered {orphan_count} orphan nodes (nodes with no connections)")
            
            logger.info(f"Built data graph: {len(nodes)} nodes ({orphan_count} orphans filtered), {len(edges)} edges")
            
            # PHASE 3: Cache the built graph for next time (v3.13)
            if self.db_path and nodes:
                try:
                    from core.services.ontology_persistence_service import OntologyPersistenceService
                    persistence = OntologyPersistenceService(self.db_path)
                    node_count = persistence.persist_graph_nodes(nodes, 'data')
                    build_time = (time.time() - start_time) * 1000
                    logger.info(f"✓ Cached {node_count} nodes for next request (build: {build_time:.0f}ms)")
                except Exception as e:
                    logger.warning(f"Failed to cache graph: {e}")
            
            build_time = (time.time() - start_time) * 1000
            
            return {
                'success': True,
                'nodes': nodes,
                'edges': edges,
                'stats': {
                    'node_count': len(nodes),
                    'edge_count': len(edges),
                    'table_count': len(set(n['group'] for n in nodes)),
                    'orphans_filtered': orphan_count,
                    'total_nodes_before_filter': original_node_count,
                    'cache_used': False,
                    'load_time_ms': build_time
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
    
    def _find_pk_columns(self, table_structure: List[Dict], table_name: str) -> List[str]:
        """
        Find ALL primary key columns for a table (handles compound keys)
        
        Uses industry-standard patterns for SAP compound keys:
        - CompanyCode + FiscalYear + [TableSpecific] (financial documents)
        - [Parent] + [Child]Item (line items)
        
        This follows Neo4j/Neptune/SAP HANA Graph best practices for compound keys.
        
        Args:
            table_structure: List of column dicts from get_table_structure()
            table_name: Name of the table
            
        Returns:
            List of column names that form the compound key (or single column if simple key)
        """
        if not table_structure:
            return [table_name]  # Fallback
        
        column_names = [col.get('COLUMN_NAME') for col in table_structure if col.get('COLUMN_NAME')]
        
        if not column_names:
            return [table_name]
        
        table_lower = table_name.lower()
        
        # SAP standard compound key patterns (industry proven)
        compound_patterns = {
            'JournalEntry': ['CompanyCode', 'FiscalYear', 'AccountingDocument'],
            'PurchaseOrderItem': ['PurchaseOrder', 'PurchaseOrderItem'],
            'PurchaseOrderScheduleLine': ['PurchaseOrder', 'PurchaseOrderItem', 'PurchaseOrderScheduleLine'],
            'SupplierInvoiceItem': ['SupplierInvoice', 'FiscalYear', 'SupplierInvoiceItem'],
            'ServiceEntrySheetItem': ['ServiceEntrySheet', 'ServiceEntrySheetItem'],
            'JournalEntryItemBillOfExchange': ['CompanyCode', 'FiscalYear', 'AccountingDocument', 'AccountingDocumentItem'],
        }
        
        # Check if table matches known compound key pattern
        if table_name in compound_patterns:
            pattern_cols = compound_patterns[table_name]
            # Verify all pattern columns exist
            if all(col in column_names for col in pattern_cols):
                return pattern_cols
        
        # Auto-detect compound keys: CompanyCode + FiscalYear + [Document/Item]
        pk_cols = []
        if 'CompanyCode' in column_names:
            pk_cols.append('CompanyCode')
        if 'FiscalYear' in column_names:
            pk_cols.append('FiscalYear')
        
        # Add table-specific field (Document, Item, etc.)
        if len(pk_cols) > 0:
            for col in column_names:
                if 'Document' in col or 'Item' in col or table_name in col:
                    if col not in pk_cols:
                        pk_cols.append(col)
                        break
        
        if len(pk_cols) > 1:
            return pk_cols  # Compound key detected
        
        # Single column key strategies (original logic)
        # Strategy 1: Exact match (e.g., "Supplier" column in Supplier table)
        for col in column_names:
            if col.lower() == table_lower:
                return [col]
        
        # Strategy 2: Table name + suffix (e.g., "SupplierID")
        for suffix in ['ID', 'Code', 'Key', 'Number', 'UUID']:
            target = f"{table_name}{suffix}"
            for col in column_names:
                if col.lower() == target.lower():
                    return [col]
        
        # Strategy 3: First column
        return [column_names[0]]
    
    def _format_record_tooltip(self, table_name: str, record: Dict) -> str:
        """Format record data as tooltip"""
        lines = [f"Table: {table_name}", ""]
        for key, val in list(record.items())[:5]:  # First 5 columns
            lines.append(f"{key}: {val}")
        if len(record) > 5:
            lines.append(f"... +{len(record)-5} more columns")
        return "\n".join(lines)
