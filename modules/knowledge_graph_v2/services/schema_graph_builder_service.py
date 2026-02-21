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
        1. Use known P2P product mappings for core entities
        2. Group remaining entities by namespace prefix (e.g., "product.Product" → "product")
        3. Single entities without prefix become their own product
        4. Each entity must belong to exactly one product
        
        FIXED (HIGH-29): Handle both normalized ("PurchaseOrder") and prefixed 
        ("purchaseorder.PurchaseOrder") entity names from CSN.
        
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
        
        # Reverse mapping: normalized_entity → product
        entity_to_product = {}
        for product, entities in known_products.items():
            for entity in entities:
                entity_to_product[entity] = product
        
        # Group entities by product
        products = {}
        for entity_name in entity_names:
            # Normalize entity name (remove namespace prefix if present)
            # Example: "purchaseorder.PurchaseOrder" → "PurchaseOrder"
            normalized_name = entity_name.split('.')[-1] if '.' in entity_name else entity_name
            
            # Check if normalized entity is in known products
            if normalized_name in entity_to_product:
                product_name = entity_to_product[normalized_name]
            else:
                # For unknown entities, use namespace prefix as product
                # Example: "product.ProductPlant" → "product"
                # Example: "companycode.CompanyCode" → "companycode"  
                # Example: "SingleEntity" → "SingleEntity"
                if '.' in entity_name:
                    product_name = entity_name.split('.')[0]
                else:
                    product_name = entity_name
            
            if product_name not in products:
                products[product_name] = []
            
            products[product_name].append(entity_name)
        
        logger.info(f"Inferred {len(products)} products from {len(entity_names)} entities")
        return products
    
    def _add_fk_edges(self, graph: Graph, table_to_product: Dict[str, Dict]) -> None:
        """
        Add foreign key edges to graph from CSN associations
        
        Enhanced with semantic metadata (HIGH-29 Phase 2):
        - ON conditions (explicit JOIN clauses from CSN)
        - Cardinality (1:1, 1:*, *:*)
        - Composition detection
        - Many-to-many relationship tracking
        
        Uses CSN metadata to discover relationships.
        Creates generic EdgeType.FOREIGN_KEY edges (NOT vis.js format).
        
        Args:
            graph: Graph to add edges to (modified in place)
            table_to_product: Map of table_name to product info
        """
        # Discover relationships from CSN (now includes ON conditions!)
        relationships = self.relationship_mapper.discover_relationships()
        
        logger.info(f"[DEBUG] _add_fk_edges: Processing {len(relationships)} relationships")
        logger.info(f"[DEBUG] table_to_product keys (first 5): {list(table_to_product.keys())[:5]}")
        
        explicit_count = 0  # Track explicit vs inferred
        edges_created = 0
        
        for idx, rel in enumerate(relationships):
            if idx < 3:  # Log first 3
                logger.info(f"[DEBUG] Relationship {idx + 1}: {rel.from_entity} -> {rel.to_entity}")
            # Relationship mapper returns normalized names (without prefix)
            # But table_to_product is keyed by original CSN names (with prefix)
            # So we need to find the matching entry by comparing normalized names
            source_table_normalized = rel.from_entity
            target_table_normalized = rel.to_entity
            fk_column = rel.from_column
            
            # Find matching entries in table_to_product
            # Compare normalized names (strip prefix from both sides)
            source_info = None
            target_info = None
            
            for table_name, info in table_to_product.items():
                table_normalized = table_name.split('.')[-1] if '.' in table_name else table_name
                if table_normalized == source_table_normalized:
                    source_info = info
                if table_normalized == target_table_normalized:
                    target_info = info
                if source_info and target_info:
                    break
            
            if idx < 3:  # Log first 3
                logger.info(f"[DEBUG] source_info: {source_info}")
                logger.info(f"[DEBUG] target_info: {target_info}")
            
            if not source_info or not target_info:
                if idx < 3:
                    logger.warning(f"[DEBUG] Skipping - missing source or target")
                continue
            
            source_node_id = source_info['node_id']
            target_node_id = target_info['node_id']
            
            # Skip self-referential edges
            if source_node_id == target_node_id:
                continue
            
            # Build edge properties with semantic enhancement (HIGH-29)
            properties = {
                'source_table': source_table_normalized,
                'target_table': target_table_normalized,
                'fk_column': fk_column,
                'confidence': rel.confidence,
                'inferred': rel.inferred
            }
            
            # Add semantic metadata if available (HIGH-29 Phase 2)
            if rel.cardinality:
                properties['cardinality'] = rel.cardinality
            
            if rel.on_conditions:
                properties['on_conditions'] = rel.on_conditions
                properties['join_clause'] = ' AND '.join(rel.on_conditions)
                explicit_count += 1
            
            if rel.is_composition:
                properties['is_composition'] = True
            
            if rel.is_many_to_many:
                properties['is_many_to_many'] = True
            
            # Create FK edge (generic format with semantic metadata)
            fk_edge = GraphEdge(
                source_id=source_node_id,
                target_id=target_node_id,
                type=EdgeType.FOREIGN_KEY,
                label=fk_column,
                properties=properties
            )
            graph.add_edge(fk_edge)
            edges_created += 1
            
            if idx < 3:
                logger.info(f"[DEBUG] Created FK edge: {source_node_id} -> {target_node_id}")
        
        logger.info(
            f"Added {edges_created} foreign key edges from {len(relationships)} relationships "
            f"({explicit_count} explicit with ON conditions, "
            f"{len(relationships) - explicit_count} inferred)"
        )
