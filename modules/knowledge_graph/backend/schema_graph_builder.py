"""
Schema Graph Service

Builds schema-level knowledge graphs showing Data Product architecture.
Uses database-driven approach (queries actual tables) - not CSN-based.

SEPARATION OF CONCERNS:
- This service: Schema structure (products + tables + FK relationships)
- DataGraphService: Actual data records (individual rows)
- Frontend: Visual formatting (colors, shapes, styles) - FUTURE in Phase 2

NOTE: Currently returns vis.js format for backwards compatibility with existing API/frontend.
Phase 2 will move formatting to frontend and return pure data.

@author P2P Development Team
@version 1.0.0 (SoC Refactoring - Database-Driven with vis.js format)
"""

from typing import Dict, List, Any
import logging

from modules.knowledge_graph.backend.graph_builder_base import GraphBuilderBase

logger = logging.getLogger(__name__)


class SchemaGraphService(GraphBuilderBase):
    """
    Schema-level graph builder (database-driven approach)
    
    Single Responsibility: Convert database schema → graph data structure
    Inherits: FK discovery logic from GraphBuilderBase
    
    Input: DataSource instance (queries actual tables)
    Output: Graph data with vis.js formatting (backwards compatible)
    
    Does NOT:
    - Query actual data records (that's DataGraphService's job)
    """
    
    def __init__(self, data_source, csn_parser=None, db_path=None):
        """
        Initialize with data source for querying schema
        
        Args:
            data_source: DataSource instance (any implementation: HANA, SQLite, etc.)
            csn_parser: Optional CSNParser for FK relationship discovery
            db_path: Optional database path for ontology cache
        """
        super().__init__(data_source, csn_parser, db_path)
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
            Dictionary with vis.js formatted data (backwards compatible):
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
                
                # Create product node (vis.js format)
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
                
                # Get tables for this product from database
                try:
                    tables = self.data_source.get_tables(schema_name)
                    
                    for table in tables:
                        table_name = table.get('TABLE_NAME')
                        if not table_name:
                            continue
                        
                        # Create table node (vis.js format)
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
                        
                        # Edge: product contains table (vis.js format)
                        edges.append({
                            'from': product_node_id,
                            'to': table_node_id,
                            'arrows': 'to',
                            'color': {'color': '#666'},
                            'width': 1,
                            'dashes': False
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
            logger.error(f"Error building schema graph: {e}", exc_info=True)
            return {
                'success': False,
                'error': str(e),
                'nodes': [],
                'edges': []
            }
    
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
            List of edge dicts (vis.js format)
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
                            'title': f"{source_table}.{fk_column} → {target_table}",
                            'arrows': 'to',
                            'color': {'color': '#ff9800'},
                            'width': 2,
                            'dashes': True
                        })
        
        logger.info(f"Found {len(edges)} foreign key relationships")
        return edges
    
    def _empty_graph(self) -> Dict[str, Any]:
        """Return empty graph structure"""
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