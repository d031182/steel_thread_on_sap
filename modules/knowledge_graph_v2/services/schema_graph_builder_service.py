"""
Schema Graph Builder Service

Builds schema-level knowledge graphs from CSN files.
Returns generic Graph domain objects (NOT vis.js format).

Key Differences from v1:
- Returns Graph domain objects (generic format)
- No vis.js formatting (that's frontend's job)
- Clean separation: business logic only
- Dependency injection (CSNParser injected)
"""
import logging
from typing import Dict, List

from core.services.csn_parser import CSNParser
from core.services.relationship_mapper import CSNRelationshipMapper
from ..domain import Graph, GraphNode, GraphEdge, GraphType, NodeType, EdgeType

logger = logging.getLogger(__name__)


class SchemaGraphBuilderService:
    """
    Service for building schema graphs from CSN metadata
    
    Responsibilities:
    - Parse CSN files
    - Build graph structure (products → tables → relationships)
    - Return generic domain objects
    
    Does NOT:
    - Format for vis.js (frontend's job)
    - Access cache directly (GraphCacheService's job)
    - Query databases (DataGraphBuilderService's job)
    """
    
    def __init__(self, csn_parser: CSNParser):
        """
        Initialize with CSN parser (injected via DI)
        
        Args:
            csn_parser: Parser for CSN files
        """
        self.csn_parser = csn_parser
        self.relationship_mapper = CSNRelationshipMapper(csn_parser)
        logger.info("SchemaGraphBuilderService initialized")
    
    def build_from_csn(self) -> Graph:
        """
        Build schema graph from CSN files
        
        Returns generic Graph domain object (NOT vis.js format).
        Frontend will convert to vis.js format later.
        
        Returns:
            Graph: Domain object with:
                - Product nodes (NodeType.PRODUCT)
                - Table nodes (NodeType.TABLE)
                - Containment edges (product → table)
                - FK edges (table → table)
        
        Raises:
            Exception: If CSN parsing fails
        """
        try:
            logger.info("Building schema graph from CSN files...")
            
            # Create graph
            graph = Graph('schema', GraphType.SCHEMA)
            
            # Get all entities from CSN
            entity_names = self.csn_parser.list_entities()
            
            if not entity_names:
                logger.warning("No entities found in CSN files")
                return graph  # Empty graph
            
            logger.info(f"Found {len(entity_names)} entities in CSN files")
            
            # Phase 1: Infer products and group entities
            products_map = self._infer_products_from_entities(entity_names)
            table_to_product = {}  # Track for FK edges
            
            # Phase 2: Create product and table nodes
            for product_name, table_names in products_map.items():
                # Create product node (generic format)
                product_node = GraphNode(
                    id=f"product-{product_name}",
                    label=product_name,
                    type=NodeType.PRODUCT,
                    properties={'description': f'Data Product: {product_name}'}
                )
                graph.add_node(product_node)
                
                # Create table nodes for this product
                for table_name in table_names:
                    metadata = self.csn_parser.get_entity_metadata(table_name)
                    
                    # Create table node (generic format)
                    table_node_id = f"table-{product_name}-{table_name}"
                    table_node = GraphNode(
                        id=table_node_id,
                        label=table_name,
                        type=NodeType.TABLE,
                        properties={
                            'product': product_name,
                            'entity_label': metadata.label if metadata else None
                        }
                    )
                    graph.add_node(table_node)
                    
                    # Add containment edge: product contains table (generic format)
                    containment_edge = GraphEdge(
                        source_id=product_node.id,
                        target_id=table_node_id,
                        type=EdgeType.CONTAINS,
                        label='contains',
                        properties={}
                    )
                    graph.add_edge(containment_edge)
                    
                    # Track for FK analysis
                    table_to_product[table_name] = {
                        'product': product_name,
                        'node_id': table_node_id
                    }
            
            # Phase 3: Discover FK relationships from CSN
            logger.info("Analyzing foreign key relationships from CSN...")
            self._add_fk_edges(graph, table_to_product)
            
            stats = graph.get_statistics()
            logger.info(
                f"Built schema graph: {stats['node_count']} nodes "
                f"({stats['nodes_by_type'].get('product', 0)} products, "
                f"{stats['nodes_by_type'].get('table', 0)} tables), "
                f"{stats['edge_count']} edges"
            )
            
            return graph
            
        except Exception as e:
            logger.error(f"Error building schema graph from CSN: {e}", exc_info=True)
            raise
    
    def _infer_products_from_entities(self, entity_names: List[str]) -> Dict[str, List[str]]:
        """
        Infer data products from CSN entity names
        
        Strategy:
        1. Use known P2P product mappings
        2. Group by entity name prefixes as fallback
        3. Each entity must belong to exactly one product
        
        Args:
            entity_names: List of entity names from CSN
            
        Returns:
            Dict mapping product_name to list of table names
        """
        # Known P2P products and their entities (from CSN files)
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
        products = {}
        for entity_name in entity_names:
            product_name = entity_to_product.get(entity_name, entity_name)
            
            if product_name not in products:
                products[product_name] = []
            
            products[product_name].append(entity_name)
        
        logger.info(f"Inferred {len(products)} products from {len(entity_names)} entities")
        return products
    
    def _add_fk_edges(self, graph: Graph, table_to_product: Dict[str, Dict]) -> None:
        """
        Add foreign key edges to graph from CSN associations
        
        Uses CSN metadata to discover relationships.
        Creates generic EdgeType.FOREIGN_KEY edges (NOT vis.js format).
        
        Args:
            graph: Graph to add edges to (modified in place)
            table_to_product: Map of table_name to product info
        """
        # Discover relationships from CSN
        relationships = self.relationship_mapper.discover_relationships()
        
        for rel in relationships:
            source_table = rel.from_entity
            target_table = rel.to_entity
            fk_column = rel.from_column
            
            # Get node IDs
            source_info = table_to_product.get(source_table)
            target_info = table_to_product.get(target_table)
            
            if not source_info or not target_info:
                continue
            
            source_node_id = source_info['node_id']
            target_node_id = target_info['node_id']
            
            # Skip self-referential edges
            if source_node_id == target_node_id:
                continue
            
            # Create FK edge (generic format)
            fk_edge = GraphEdge(
                source_id=source_node_id,
                target_id=target_node_id,
                type=EdgeType.FOREIGN_KEY,
                label=fk_column,
                properties={
                    'source_table': source_table,
                    'target_table': target_table,
                    'fk_column': fk_column
                }
            )
            graph.add_edge(fk_edge)
        
        logger.info(f"Added {len(relationships)} foreign key relationships")