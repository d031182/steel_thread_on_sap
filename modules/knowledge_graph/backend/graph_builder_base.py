"""
Graph Builder Base Class

Shared utilities for building knowledge graphs.
Contains FK discovery logic reused by SchemaGraphService and DataGraphService.

PRESERVES YOUR SEMANTICS: All FK discovery patterns that work with database metadata.

@author P2P Development Team
@version 1.0.0 (WP-KG-002 Phase 2 - Extract Shared Utilities)
"""

from typing import Dict, List, Tuple
import logging

from core.services.relationship_mapper import CSNRelationshipMapper
from core.services.csn_parser import CSNParser

logger = logging.getLogger(__name__)


class GraphBuilderBase:
    """
    Base class for graph builders with shared FK discovery logic
    
    Provides:
    - FK relationship discovery (CSN + cache + manual inference)
    - SAP naming convention patterns
    - Your proven semantic inference rules
    """
    
    def __init__(self, data_source, csn_parser: CSNParser = None, db_path: str = None):
        """
        Initialize with data source and optional CSN parser
        
        Args:
            data_source: DataSource instance
            csn_parser: Optional CSNParser for FK discovery
            db_path: Optional database path for graph cache (defaults to KG module database)
        """
        import os
        
        self.data_source = data_source
        self.csn_parser = csn_parser or CSNParser('docs/csn')
        self.relationship_mapper = CSNRelationshipMapper(self.csn_parser)
        self._fk_cache = None
        
        # Get db_path for graph cache
        # CRITICAL: After database separation (2026-02-05), graph cache is in KG module
        # NOT in data_products database!
        if db_path:
            self.db_path = db_path
        else:
            # Default to Knowledge Graph module's graph_cache.db
            self.db_path = os.path.join(
                os.path.dirname(__file__),  # modules/knowledge_graph/backend/
                '..',                        # modules/knowledge_graph/
                'database',
                'graph_cache.db'
            )
    
    def _discover_fk_mappings(self, tables: List[Dict[str, str]]) -> Dict[str, List[Tuple[str, str]]]:
        """
        Discover foreign key relationships using CSN metadata + ontology cache
        
        PRESERVES YOUR RICH SEMANTICS: FK relations, parent-child, associations, cardinality
        
        Strategy:
        1. Try ontology cache first (4ms) - 103x faster!
        2. Fallback to CSN metadata discovery (410ms)
        3. Manual inference for unmapped tables (SAP naming conventions)
        
        Returns mapping: table_name → [(fk_column, target_table), ...]
        This is cached for reuse across schema and data modes.
        
        Args:
            tables: List of {schema, table} dicts
            
        Returns:
            Dict mapping source table to list of (fk_column, target_table) tuples
        """
        from core.services.ontology_persistence_service import OntologyPersistenceService
        
        fk_mappings = {}
        
        # STEP 1: Try cached ontology first (SQLite only)
        if self.db_path:
            try:
                persistence = OntologyPersistenceService(self.db_path)
                
                if persistence.is_cache_valid():
                    logger.info("✓ Using cached ontology (4ms) - 103x faster!")
                    cached_edges = persistence.get_all_relationships()
                    
                    # Convert to fk_mappings format
                    for edge in cached_edges:
                        if edge.source_table not in fk_mappings:
                            fk_mappings[edge.source_table] = []
                        fk_mappings[edge.source_table].append((edge.source_column, edge.target_table))
                    
                    csn_fk_count = sum(len(fks) for fks in fk_mappings.values())
                    logger.info(f"Loaded {csn_fk_count} cached relationships")
                    
                    self._fk_cache = fk_mappings
                    return fk_mappings
            except Exception as e:
                logger.warning(f"Ontology cache error: {e}")
        
        # STEP 2: Fallback to CSN-based discovery
        logger.info("Discovering relationships from CSN metadata...")
        csn_relationships = self.relationship_mapper.discover_relationships()
        
        for rel in csn_relationships:
            if rel.from_entity not in fk_mappings:
                fk_mappings[rel.from_entity] = []
            fk_mappings[rel.from_entity].append((rel.from_column, rel.to_entity))
        
        csn_fk_count = sum(len(fks) for fks in fk_mappings.values())
        logger.info(f"CSN discovered {csn_fk_count} relationships automatically!")
        
        # STEP 3: Manual inference for unmapped tables
        unmapped_tables = [t for t in tables if t['table'] not in fk_mappings or not fk_mappings[t['table']]]
        
        if unmapped_tables:
            logger.info(f"Applying manual FK inference for {len(unmapped_tables)} tables...")
            
            for table_info in unmapped_tables:
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
        logger.info(f"Total FK mappings: {total} ({csn_fk_count} from CSN, {total - csn_fk_count} from manual inference)")
        
        return fk_mappings
    
    def _infer_fk_target_table(self, column_name: str, source_table: str) -> str:
        """
        Infer target table from column name using SAP naming conventions
        
        PRESERVES YOUR SEMANTICS: Proven patterns that work with database metadata
        
        Strategy:
        1. Check for exact table name match (e.g., "Supplier" column → Supplier table)
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
        known_tables = [
            'Supplier', 'Product', 'CompanyCode', 'CostCenter',
            'PurchaseOrder', 'ServiceEntrySheet', 'JournalEntry',
            'PaymentTerms', 'Plant', 'Material'
        ]
        
        for table in known_tables:
            if table.lower() in col_lower and table.lower() != source_lower:
                return table
        
        return None