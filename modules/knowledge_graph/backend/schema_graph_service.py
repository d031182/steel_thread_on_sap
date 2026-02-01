"""
Schema Graph Service

Builds schema-level knowledge graphs showing Data Product architecture.
Uses database-driven approach (queries actual tables) - not CSN-based.

SEPARATION OF CONCERNS:
- This service: Schema structure (products + tables + FK relationships)
- DataGraphService: Actual data records (individual rows)
- Frontend: Visual formatting (colors, shapes, styles)

@author P2P Development Team
@version 1.0.0 (SoC Refactoring - Database-Driven)
"""

from typing import Dict, List, Any, Tuple
import logging

from core.services.relationship_mapper import CSNRelationshipMapper
from core.services.csn_parser import CSNParser

logger = logging.getLogger(__name__)


class SchemaGraphService:
    """
    Schema-level graph builder (database-driven approach)
    
    Single Responsibility: Convert database schema → graph data structure
    
    Input: DataSource instance (queries actual tables)
    Output: Pure data (nodes/edges arrays with properties)
    
    Does NOT:
    - Format for visualization (that's frontend's job)
    - Query actual data records (that's DataGraphService's job)
    """
    
    def __init__(self, data_source, csn_parser: CSNParser = None, db_path: str = None):
        """
        Initialize with data source for querying schema
        
        Args:
            data_source: DataSource instance (any implementation: HANA, SQLite, etc.)
            csn_parser: Optional CSNParser for FK relationship discovery
            db_path: Optional database path for ontology cache
        """
        self.data_source = data_source
        self.csn_parser = csn_parser or CSNParser('docs/csn')
        self.relationship_mapper = CSNRelationshipMapper(self.csn_parser)
        self._fk_cache = None  # Cache FK relationships
        
        # Get db_path for ontology cache (SQLite only)
        if db_path:
            self.db_path = db_path
        else:
            conn_info = data_source.get_connection_info()
            self.db_path = conn_info.get('db_path') if conn_info.get('type') == 'sqlite' else None
        
        logger.info(f"SchemaGraphService initialized with {type(data_source).__name__}")
    
    def build_schema_graph(self) -> Dict[str, Any]:
        """
        Build schema-level graph showing Data Product architecture
        
        Uses database-driven approach: Queries actual tables from data source.
        
        Shows:
        - Data Products as nodes
        - Tables within products as sub-nodes  
        - Foreign key relationships between tables as edges
        
        Returns:
            Dictionary with pure data structure:
            {
                'nodes': [
                    {
                        'id': str,
                        'label': str,
                        'type': 'product' | 'table',
                        'properties': {...}  # All metadata, no styling
                    }
                ],
                'edges': [
                    {
                        'from': str,
                        'to': str,
                        'label': str,
                        'type': 'contains' | 'foreign_key',
                        'properties': {...}  # FK metadata, no styling
                    }
                ],
                'stats': {
                    'node_count': int,
                    'edge_count': int,
                    'product_count': int,
                    'table_count': int
                }
            }
        
        Note: Returns PURE DATA STRUCTURE. Frontend applies vis.js formatting.
        """
        try:
            logger.info("Building schema-level graph from database...")
            
            # Get all data products from data source
            products = self.data_source.get_data_products()
            
            if not products:
                logger.warning("No data products found")
                return self._empty_graph()
            
            logger.info(f"Found {len(products)} data products")
            
            nodes = []
            edges = []
            table_to_product = {}  # Map table → product info for FK analysis
            all_tables = []
            
            # Phase 1: Create product and table nodes
            for product in products:
                product_name = product.get('productName')
                schema_name = product.get('schemaName', product_name)
                display_name = product.get('displayName', product_name)
                
                if not product_name:
                    continue
                
                # Create product node (pure data)
                product_node_id = f"product-{product_name}"
                nodes.append({
                    'id': product_node_id,
                    'label': display_name or product_name,
                    'type': 'product',
                    'properties': {
                        'productName': product_name,
                        'schemaName': schema_name,
                        'description': product.get('description', ''),
                        'namespace': product.get('namespace', ''),
                        'version': product.get('version', 'v1')
                    }
                })
                
                # Get tables for this product from database
                try:
                    tables = self.data_source.get_tables(schema_name)
                    
                    for table in tables:
                        table_name = table.get('TABLE_NAME')
                        if not table_name:
                            continue
                        
                        # Create table node (pure data)
                        table_node_id = f"table-{schema_name}-{table_name}"
                        nodes.append({
                            'id': table_node_id,
                            'label': table_name,
                            'type': 'table',
                            'properties': {
                                'tableName': table_name,
                                'productName': product_name,
                                'schemaName': schema_name
                            }
                        })
                        
                        # Edge: product contains table
                        edges.append({
                            'from': product_node_id,
                            'to': table_node_id,
                            'label': 'contains',
                            'type': 'containment',
                            'properties': {}
                        })
                        
                        # Track for FK analysis
                        table_to_product[table_name] = {
                            'product': product_name,
                            'schema': schema_name,
                            'node_id': table_node_id
                        }
                        all_tables.append({'schema': schema_name, 'table': table_name})
                
                except Exception as e:
                    logger.warning(f"Error getting tables for product {product_name}: {e}")
                    continue
            
            # Phase 2: Discover FK relationships
            logger.info("Analyzing foreign key relationships...")
            fk_edges = self._find_fk_relationships(all_tables, table_to_product)
            edges.extend(fk_edges)
            
            logger.info(f"Built schema graph: {len(nodes)} nodes, {len(edges)} edges")
            
            # Save to cache if available
            if self.db_path and nodes:
                try:
                    from core.services.graph_cache_service import GraphCacheService
                    cache = GraphCacheService(self.db_path)
                    cache.save_graph(nodes, edges, graph_type='schema')
                    logger.info(f"✓ Saved schema graph to cache ({len(nodes)} nodes)")
                except Exception as e:
                    logger.warning(f"Cache save failed: {e}")
            
            return {
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
            logger.error(f"Error building schema graph: {e}", exc_info=True)
            return {
                'nodes': [],
                'edges': [],
                'stats': {'node_count': 0, 'edge_count': 0},
                'error': str(e)
            }
    
    def _discover_fk_mappings(self, tables: List[Dict[str, str]]) -> Dict[str, List[Tuple[str, str]]]:
        """
        Discover foreign key relationships using CSN metadata + ontology cache
        
        Try ontology cache first (4ms), fallback to CSN discovery (410ms).
        Returns mapping: table_name → [(fk_column, target_table), ...]
        
        Args:
            tables: List of {schema, table} dicts
            
        Returns:
            Dict mapping source table to list of (fk_column, target_table) tuples
        """
        from core.services.ontology_persistence_service import OntologyPersistenceService
        
        fk_mappings = {}
        
        # Try cached ontology first (SQLite only)
        if self.db_path:
            try:
                persistence = OntologyPersistenceService(self.db_path)
                
                if persistence.is_cache_valid():
                    logger.info("✓ Using cached ontology (4ms)")
                    cached_edges = persistence.get_all_relationships()
                    
                    # Convert to fk_mappings format
                    for edge in cached_edges:
                        if edge.source_table not in fk_mappings:
                            fk_mappings[edge.source_table] = []
                        fk_mappings[edge.source_table].append((edge.source_column, edge.target_table))
                    
                    logger.info(f"Loaded {sum(len(fks) for fks in fk_mappings.values())} cached relationships")
                    self._fk_cache = fk_mappings
                    return fk_mappings
            except Exception as e:
                logger.warning(f"Ontology cache error: {e}")
        
        # Fallback: CSN-based discovery
        logger.info("Discovering relationships from CSN metadata...")
        csn_relationships = self.relationship_mapper.discover_relationships()
        
        for rel in csn_relationships:
            if rel.from_entity not in fk_mappings:
                fk_mappings[rel.from_entity] = []
            fk_mappings[rel.from_entity].append((rel.from_column, rel.to_entity))
        
        csn_count = sum(len(fks) for fks in fk_mappings.values())
        logger.info(f"CSN discovered {csn_count} relationships")
        
        # Manual inference for unmapped tables
        unmapped = [t for t in tables if t['table'] not in fk_mappings or not fk_mappings[t['table']]]
        
        if unmapped:
            logger.info(f"Applying manual FK inference for {len(unmapped)} tables...")
            
            for table_info in unmapped:
                schema = table_info['schema']
                table_name = table_info['table']
                
                if table_name not in fk_mappings:
                    fk_mappings[table_name] = []
                
                try:
                    columns_result = self.data_source.get_table_structure(schema, table_name)
                    columns = [col.get('COLUMN_NAME') for col in columns_result if col.get('COLUMN_NAME')]
                    
                    for column in columns:
                        target_table = self._infer_fk_target_table(column, table_name)
                        if target_table:
                            fk_mappings[table_name].append((column, target_table))
                
                except Exception as e:
                    logger.warning(f"Error analyzing FKs for {table_name}: {e}")
        
        self._fk_cache = fk_mappings
        total = sum(len(fks) for fks in fk_mappings.values())
        logger.info(f"Total FK mappings: {total}")
        
        return fk_mappings
    
    def _find_fk_relationships(
        self,
        tables: List[Dict[str, str]],
        table_to_product: Dict[str, Dict]
    ) -> List[Dict]:
        """
        Find foreign key relationships for schema visualization
        
        Args:
            tables: List of {schema, table} dicts
            table_to_product: Map of table_name to product info
            
        Returns:
            List of edge dicts (pure data, no styling)
        """
        fk_mappings = self._discover_fk_mappings(tables)
        edges = []
        
        for source_table, fk_list in fk_mappings.items():
            source_node = table_to_product.get(source_table, {}).get('node_id')
            
            if not source_node:
                continue
            
            for fk_column, target_table in fk_list:
                if target_table in table_to_product:
                    target_node = table_to_product[target_table]['node_id']
                    
                    # No self-referential edges
                    if target_node != source_node:
                        edges.append({
                            'from': source_node,
                            'to': target_node,
                            'label': fk_column,
                            'type': 'foreign_key',
                            'properties': {
                                'sourceTable': source_table,
                                'targetTable': target_table,
                                'sourceColumn': fk_column
                            }
                        })
        
        logger.info(f"Found {len(edges)} foreign key relationships")
        return edges
    
    def _infer_fk_target_table(self, column_name: str, source_table: str) -> str:
        """
        Infer target table from column name using SAP naming conventions
        
        Args:
            column_name: Column name (e.g., 'Supplier', 'CompanyCode')
            source_table: Source table name (to avoid self-references)
            
        Returns:
            Target table name or None
        """
        col_lower = column_name.lower()
        source_lower = source_table.lower()
        
        if col_lower == source_lower:
            return None
        
        # Role-based mappings
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
        
        # Check for ID/Code/Key/Number suffixes
        for suffix in ['ID', 'Code', 'Key', 'Number']:
            if column_name.endswith(suffix):
                base_name = column_name[:-len(suffix)]
                if base_name and base_name.lower() != source_lower:
                    return base_name
        
        # Check for known table names in column
        known_tables = [
            'Supplier', 'Product', 'CompanyCode', 'CostCenter',
            'PurchaseOrder', 'ServiceEntrySheet', 'JournalEntry',
            'PaymentTerms', 'Plant', 'Material'
        ]
        
        for table in known_tables:
            if table.lower() in col_lower and table.lower() != source_lower:
                return table
        
        return None
    
    def _empty_graph(self) -> Dict[str, Any]:
        """Return empty graph structure"""
        return {
            'nodes': [],
            'edges': [],
            'stats': {
                'node_count': 0,
                'edge_count': 0,
                'product_count': 0,
                'table_count': 0
            }
        }