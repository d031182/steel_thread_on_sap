"""
CSN Schema Graph Builder

Builds schema-level knowledge graphs from CSN files (metadata-driven approach).
Achieves feature parity with SchemaGraphBuilder but uses CSN files instead of database queries.

FEATURE PARITY GOALS:
- Same output format (vis.js compatible)
- Same graph structure (products → tables → FK relationships)
- Same semantics and visual styling
- Same performance characteristics

KEY DIFFERENCES:
- Data source: CSN files (metadata) vs Database queries (runtime schema)
- Discovery: CSN associations vs Database FK inspection
- Use case: Design-time analysis vs Runtime verification

@author P2P Development Team
@version 1.0.0 (CSN-Driven Alternative)
"""

from typing import Dict, List, Any
import logging
import os

from core.services.csn_parser import CSNParser
from core.services.relationship_mapper import CSNRelationshipMapper

logger = logging.getLogger(__name__)


class CSNSchemaGraphBuilder:
    """
    CSN-based schema graph builder
    
    Single Responsibility: Convert CSN metadata → graph data structure
    Same semantics as SchemaGraphBuilder but driven by CSN files
    
    Input: CSN files from docs/csn directory
    Output: Graph data with vis.js formatting (backwards compatible)
    
    Does NOT:
    - Query actual databases (that's SchemaGraphBuilder's approach)
    - Query actual data records (that's DataGraphService's job)
    """
    
    def __init__(self, csn_directory: str = 'docs/csn', db_path: str = None):
        """
        Initialize with CSN directory
        
        Args:
            csn_directory: Path to directory containing CSN JSON files
            db_path: Optional database path for ontology cache (for consistency)
        """
        self.csn_parser = CSNParser(csn_directory)
        self.relationship_mapper = CSNRelationshipMapper(self.csn_parser)
        self.csn_directory = csn_directory
        self.db_path = db_path
        logger.info(f"CSNSchemaGraphBuilder initialized with CSN directory: {csn_directory}")
    
    def build_schema_graph(self) -> Dict[str, Any]:
        """
        Build schema-level graph from CSN files
        
        Uses CSN metadata approach: Reads entity definitions from CSN files.
        
        Shows:
        - Data Products as nodes (inferred from CSN file grouping)
        - Tables (entities) within products as sub-nodes
        - Foreign key relationships (associations) between tables as edges
        
        Returns:
            Dictionary with vis.js formatted data (same format as SchemaGraphBuilder):
            {
                'success': bool,
                'nodes': [
                    {
                        'id': str,
                        'label': str,
                        'title': str,  # Tooltip
                        'group': 'product' | 'table',
                        'shape': 'box' | 'ellipse',
                        'color': {'background': str, 'border': str},
                        'size': int,
                        'font': {...}
                    }
                ],
                'edges': [
                    {
                        'from': str,
                        'to': str,
                        'label': str,
                        'title': str,
                        'arrows': str,
                        'color': {'color': str},
                        'width': int,
                        'dashes': bool
                    }
                ],
                'stats': {
                    'node_count': int,
                    'edge_count': int,
                    'product_count': int,
                    'table_count': int
                }
            }
        """
        try:
            logger.info("Building schema-level graph from CSN files...")
            
            # Check if CSN directory exists
            if not os.path.exists(self.csn_directory):
                logger.warning(f"CSN directory not found: {self.csn_directory}")
                return self._empty_graph()
            
            # Get all entities from CSN files
            entity_names = self.csn_parser.list_entities()
            
            if not entity_names:
                logger.warning("No entities found in CSN files")
                return self._empty_graph()
            
            logger.info(f"Found {len(entity_names)} entities in CSN files")
            
            nodes = []
            edges = []
            table_to_product = {}  # Map table → product info for FK analysis
            products_map = {}  # Group entities by product
            
            # Phase 1: Group entities into products (infer from CSN file structure)
            products_map = self._infer_products_from_csn(entity_names)
            
            # Phase 2: Create product and table nodes
            for product_name, tables in products_map.items():
                # Create product node (same vis.js format as SchemaGraphBuilder)
                product_node_id = f"product-{product_name}"
                nodes.append({
                    'id': product_node_id,
                    'label': product_name,
                    'title': f"Data Product: {product_name}\n(from CSN metadata)",
                    'group': 'product',
                    'shape': 'box',
                    'color': {
                        'background': '#1976d2',  # Same blue as SchemaGraphBuilder
                        'border': '#0d47a1'
                    },
                    'font': {
                        'color': 'white',
                        'size': 16,
                        'bold': True
                    },
                    'size': 30
                })
                
                # Create table nodes for this product
                for table_name in tables:
                    metadata = self.csn_parser.get_entity_metadata(table_name)
                    if not metadata:
                        continue
                    
                    # Create table node (same vis.js format as SchemaGraphBuilder)
                    table_node_id = f"table-{product_name}-{table_name}"
                    nodes.append({
                        'id': table_node_id,
                        'label': table_name,
                        'title': f"Table: {table_name}\nProduct: {product_name}\n{metadata.label or ''}",
                        'group': 'table',
                        'shape': 'ellipse',  # Same shape as SchemaGraphBuilder
                        'color': {
                            'background': '#e3f2fd',  # Same light blue
                            'border': '#1976d2'
                        },
                        'size': 15
                    })
                    
                    # Edge: product contains table (same format as SchemaGraphBuilder)
                    edges.append({
                        'from': product_node_id,
                        'to': table_node_id,
                        'arrows': 'to',
                        'color': {'color': '#666'},  # Same gray
                        'width': 1,
                        'dashes': False
                    })
                    
                    # Track for FK analysis
                    table_to_product[table_name] = {
                        'product': product_name,
                        'node_id': table_node_id
                    }
            
            # Phase 3: Discover FK relationships from CSN associations
            logger.info("Analyzing foreign key relationships from CSN...")
            fk_edges = self._find_fk_relationships_from_csn(table_to_product)
            edges.extend(fk_edges)
            
            logger.info(f"Built CSN schema graph: {len(nodes)} nodes, {len(edges)} edges")
            
            # Save to cache if available (same as SchemaGraphBuilder)
            if self.db_path and nodes:
                try:
                    from core.services.graph_cache_service import GraphCacheService
                    cache = GraphCacheService(self.db_path)
                    cache.save_graph(nodes, edges, graph_type='schema_csn')
                    logger.info(f"✓ Saved CSN schema graph to cache ({len(nodes)} nodes)")
                except Exception as e:
                    logger.warning(f"Cache save failed: {e}")
            
            return {
                'success': True,
                'nodes': nodes,
                'edges': edges,
                'stats': {
                    'node_count': len(nodes),
                    'edge_count': len(edges),
                    'product_count': len(products_map),
                    'table_count': len(table_to_product)
                }
            }
            
        except Exception as e:
            logger.error(f"Error building CSN schema graph: {e}", exc_info=True)
            return {
                'success': False,
                'error': str(e),
                'nodes': [],
                'edges': []
            }
    
    def _infer_products_from_csn(self, entity_names: List[str]) -> Dict[str, List[str]]:
        """
        Infer data products from CSN entity names and grouping
        
        Strategy:
        1. Group by CSN file (each file = one product)
        2. Use entity name prefixes as fallback
        3. Map to known P2P products
        
        Args:
            entity_names: List of entity names from CSN
            
        Returns:
            Dict mapping product_name to list of table names
        """
        products = {}
        
        # Known P2P products and their entities (from our CSN files)
        known_products = {
            'Purchase_Order': ['PurchaseOrder', 'PurchaseOrderItem'],
            'Supplier_Invoice': ['SupplierInvoice', 'SupplierInvoiceItem'],
            'Service_Entry_Sheet': ['ServiceEntrySheet', 'ServiceEntrySheetItem'],
            'Journal_Entry': ['JournalEntryHeader', 'JournalEntryItem'],
            'Supplier': ['Supplier', 'SupplierCompanyCode'],
            'Product': ['Product', 'ProductPlant'],
            'Company_Code': ['CompanyCode'],
            'Cost_Center': ['CostCenter'],
            'Payment_Terms': ['PaymentTerms']
        }
        
        # Reverse mapping: entity → product
        entity_to_product = {}
        for product, entities in known_products.items():
            for entity in entities:
                entity_to_product[entity] = product
        
        # Group entities by product
        for entity_name in entity_names:
            product_name = entity_to_product.get(entity_name)
            
            # Fallback: use entity name as product name
            if not product_name:
                product_name = entity_name
            
            if product_name not in products:
                products[product_name] = []
            
            products[product_name].append(entity_name)
        
        logger.info(f"Inferred {len(products)} products from CSN entities")
        return products
    
    def _find_fk_relationships_from_csn(
        self,
        table_to_product: Dict[str, Dict]
    ) -> List[Dict]:
        """
        Find foreign key relationships from CSN associations
        
        Uses CSN metadata (associations) instead of database FK inspection.
        Same output format as SchemaGraphBuilder._find_fk_relationships()
        
        Args:
            table_to_product: Map of table_name to product info
            
        Returns:
            List of edge dicts (vis.js format)
        """
        edges = []
        
        # Use relationship mapper to discover relationships from CSN
        relationships = self.relationship_mapper.discover_relationships()
        
        for rel in relationships:
            source_table = rel.from_entity
            target_table = rel.to_entity
            fk_column = rel.from_column
            
            # Get node IDs
            source_node = table_to_product.get(source_table, {}).get('node_id')
            target_node = table_to_product.get(target_table, {}).get('node_id')
            
            if not source_node or not target_node:
                continue
            
            # No self-referential edges (same as SchemaGraphBuilder)
            if target_node == source_node:
                continue
            
            # Create edge (same format as SchemaGraphBuilder)
            edges.append({
                'from': source_node,
                'to': target_node,
                'label': fk_column,
                'title': f"{source_table}.{fk_column} → {target_table}",
                'arrows': 'to',
                'color': {'color': '#ff9800'},  # Same orange
                'width': 2,
                'dashes': True  # Same dashed style
            })
        
        logger.info(f"Found {len(edges)} foreign key relationships from CSN")
        return edges
    
    def _empty_graph(self) -> Dict[str, Any]:
        """Return empty graph structure (same format as SchemaGraphBuilder)"""
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