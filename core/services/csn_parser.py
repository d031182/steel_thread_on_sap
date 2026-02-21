"""
CSN (Core Data Services Notation) Parser Service

Efficiently extracts metadata from SAP CSN JSON files:
- Primary Keys
- Foreign Keys
- Associations
- Relationships
- Data Types
- Semantic Annotations (@Semantics.amount, @Common.Label, etc.)
- Display Labels and Descriptions

Performance optimized for large CSN files with lazy loading and caching.
"""

import json
import os
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from functools import lru_cache


@dataclass
class ColumnMetadata:
    """Column metadata extracted from CSN with semantic annotations"""
    name: str
    type: str
    length: Optional[int] = None
    is_key: bool = False
    is_nullable: bool = True
    
    # ⭐ Semantic Annotation Metadata (HIGH-30)
    display_label: Optional[str] = None  # @title, @Common.Label, @EndUserText.label
    description: Optional[str] = None    # @EndUserText.quickInfo, @Common.QuickInfo
    semantic_type: Optional[str] = None  # @Semantics.amount, @Semantics.currencyCode
    semantic_properties: Dict[str, Any] = field(default_factory=dict)
    all_annotations: Dict[str, Any] = field(default_factory=dict)


@dataclass
class AssociationMetadata:
    """Association/relationship metadata from CSN"""
    name: str
    target: str  # Target entity name
    cardinality: str  # "one", "many", etc.
    keys: List[Dict[str, str]]  # Foreign key mappings
    on_conditions: List[Dict[str, str]] = field(default_factory=list)  # JOIN ON conditions


@dataclass
class EntityMetadata:
    """Complete entity metadata from CSN"""
    name: str
    original_name: str  # ABAP original name
    label: Optional[str]
    columns: List[ColumnMetadata]
    primary_keys: List[str]
    associations: List[AssociationMetadata]
    kind: str  # "entity", "context", etc.


class CSNParser:
    """
    Efficient CSN parser with caching and lazy loading
    
    Usage:
        parser = CSNParser('docs/csn')
        entity = parser.get_entity_metadata('PurchaseOrder')
        pks = parser.get_primary_keys('PurchaseOrder')
        fks = parser.get_foreign_keys('PurchaseOrder')
    """
    
    def __init__(self, csn_directory: str = 'docs/csn'):
        """
        Initialize CSN parser
        
        Args:
            csn_directory: Path to directory containing CSN JSON files
        """
        self.csn_directory = csn_directory
        self._file_cache: Dict[str, Any] = {}
        self._entity_index: Optional[Dict[str, str]] = None  # entity_name -> file_path
    
    def _build_entity_index(self) -> Dict[str, str]:
        """
        Build index of entity names to CSN files (lazy)
        
        Returns:
            Dictionary mapping entity names to file paths
        """
        if self._entity_index is not None:
            return self._entity_index
        
        index = {}
        
        if not os.path.exists(self.csn_directory):
            return index
        
        # Scan all CSN files
        for filename in os.listdir(self.csn_directory):
            if not filename.endswith('.json'):
                continue
            
            filepath = os.path.join(self.csn_directory, filename)
            
            # Quick scan for entity names (avoid full parse)
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    
                # CSN format: array with definitions
                if isinstance(data, list) and len(data) > 0:
                    definitions = data[0].get('definitions', {})
                    
                    for entity_name, entity_def in definitions.items():
                        if entity_def.get('kind') == 'entity':
                            # Store simple entity name (e.g., "PurchaseOrder" not "purchaseorder.PurchaseOrder")
                            simple_name = entity_name.split('.')[-1]
                            index[simple_name] = filepath
                            
            except (json.JSONDecodeError, IOError):
                continue
        
        self._entity_index = index
        return index
    
    @lru_cache(maxsize=32)
    def _load_csn_file(self, filepath: str) -> Optional[Dict]:
        """
        Load and cache CSN file (with LRU eviction)
        
        Args:
            filepath: Path to CSN JSON file
            
        Returns:
            Parsed CSN data or None if error
        """
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
                # Return first element if array
                return data[0] if isinstance(data, list) and len(data) > 0 else data
        except (json.JSONDecodeError, IOError) as e:
            print(f"Error loading CSN file {filepath}: {e}")
            return None
    
    def _find_entity_definition(self, entity_name: str) -> Optional[tuple[Dict, str]]:
        """
        Find entity definition in CSN files
        
        Args:
            entity_name: Simple entity name (e.g., "PurchaseOrder")
            
        Returns:
            Tuple of (entity_definition, full_entity_name) or None
        """
        index = self._build_entity_index()
        
        filepath = index.get(entity_name)
        if not filepath:
            return None
        
        csn_data = self._load_csn_file(filepath)
        if not csn_data:
            return None
        
        definitions = csn_data.get('definitions', {})
        
        # Find entity (match on simple name)
        for full_name, entity_def in definitions.items():
            if entity_def.get('kind') == 'entity' and full_name.endswith(entity_name):
                return entity_def, full_name
        
        return None
    
    def _extract_column_metadata(self, col_name: str, col_def: Dict) -> ColumnMetadata:
        """
        Extract column metadata with complete semantic annotations (HIGH-30)
        
        Args:
            col_name: Column name
            col_def: Column definition from CSN
            
        Returns:
            ColumnMetadata with all annotations
        """
        # Extract display label (prioritize @title > @Common.Label > @EndUserText.label)
        display_label = (
            col_def.get('@title') or 
            col_def.get('@Common.Label') or 
            col_def.get('@EndUserText.label')
        )
        
        # Extract description
        description = (
            col_def.get('@EndUserText.quickInfo') or
            col_def.get('@Common.QuickInfo')
        )
        
        # Extract semantic type and properties
        semantic_type = None
        semantic_properties = {}
        
        for key, value in col_def.items():
            if key.startswith('@Semantics.'):
                semantic_key = key.replace('@Semantics.', '')
                
                if '.' not in semantic_key:
                    # Primary semantic type (e.g., @Semantics.amount)
                    semantic_type = semantic_key
                else:
                    # Semantic property (e.g., @Semantics.amount.currencyCode)
                    parts = semantic_key.split('.', 1)
                    semantic_properties[parts[1]] = value
        
        # Extract all annotations for complete metadata
        all_annotations = {
            k: v for k, v in col_def.items() 
            if k.startswith('@')
        }
        
        return ColumnMetadata(
            name=col_name,
            type=col_def.get('type', 'unknown'),
            length=col_def.get('length'),
            is_key=col_def.get('key', False),
            is_nullable=not col_def.get('notNull', False),
            display_label=display_label,
            description=description,
            semantic_type=semantic_type,
            semantic_properties=semantic_properties,
            all_annotations=all_annotations
        )
    
    def _parse_on_conditions(self, on_clause: List) -> List[Dict]:
        """
        Parse ON condition into structured join information
        
        Example ON clause:
        [
            { "ref": ["SupplierID"] },
            "=",
            { "ref": ["to_Supplier", "SupplierID"] }
        ]
        
        Returns:
        [
            {
                "left_field": "SupplierID",
                "operator": "=",
                "right_entity": "to_Supplier",
                "right_field": "SupplierID"
            }
        ]
        """
        join_conditions = []
        
        # Parse ON clause (simplified for basic = comparisons)
        i = 0
        while i < len(on_clause):
            if isinstance(on_clause[i], dict) and 'ref' in on_clause[i]:
                left_ref = on_clause[i]['ref']
                left_field = left_ref[0] if isinstance(left_ref, list) else left_ref
                
                # Next should be operator
                if i + 1 < len(on_clause) and isinstance(on_clause[i + 1], str):
                    operator = on_clause[i + 1]
                    
                    # Next should be right side
                    if i + 2 < len(on_clause) and isinstance(on_clause[i + 2], dict):
                        right_ref = on_clause[i + 2]['ref']
                        
                        if isinstance(right_ref, list) and len(right_ref) >= 2:
                            join_conditions.append({
                                'left_field': left_field,
                                'operator': operator,
                                'right_entity': right_ref[0],
                                'right_field': right_ref[1]
                            })
                        
                        i += 3
                        continue
            
            i += 1
        
        return join_conditions
    
    def _parse_association(self, element_name: str, element_def: Dict) -> AssociationMetadata:
        """
        Extract complete association metadata including ON conditions
        
        Args:
            element_name: Association name
            element_def: Association definition from CSN
            
        Returns:
            AssociationMetadata with ON conditions
        """
        # Extract target entity
        col_type = element_def.get('type', {})
        if isinstance(col_type, dict) and 'ref' in col_type:
            target = col_type['ref'][0] if isinstance(col_type['ref'], list) else col_type['ref']
        else:
            target = element_def.get('target', '')
        
        # Determine cardinality
        cardinality = "one"
        if element_def.get('cardinality', {}).get('max') == '*':
            cardinality = "many"
        
        # Extract foreign key mappings
        keys = []
        foreign_keys_def = element_def.get('keys', [])
        for key in foreign_keys_def:
            if 'ref' in key:
                keys.append({
                    'local': key['ref'][0] if isinstance(key['ref'], list) else key['ref']
                })
        
        # Extract ON conditions
        on_conditions = element_def.get('on', [])
        join_conditions = self._parse_on_conditions(on_conditions)
        
        return AssociationMetadata(
            name=element_name,
            target=target,
            cardinality=cardinality,
            keys=keys,
            on_conditions=join_conditions
        )
    
    def get_entity_metadata(self, entity_name: str) -> Optional[EntityMetadata]:
        """
        Get complete metadata for an entity
        
        Args:
            entity_name: Simple entity name (e.g., "PurchaseOrder")
            
        Returns:
            EntityMetadata object or None if not found
        """
        result = self._find_entity_definition(entity_name)
        if not result:
            return None
        
        entity_def, full_name = result
        
        # Extract columns with semantic annotations
        columns = []
        primary_keys = []
        elements = entity_def.get('elements', {})
        
        for col_name, col_def in elements.items():
            # Skip associations (they have "type" as object with "ref")
            if isinstance(col_def.get('type'), dict):
                continue
            
            is_key = col_def.get('key', False)
            if is_key:
                primary_keys.append(col_name)
            
            # Use enhanced metadata extraction
            column = self._extract_column_metadata(col_name, col_def)
            columns.append(column)
        
        # Extract associations with ON conditions
        associations = []
        for col_name, col_def in elements.items():
            col_type = col_def.get('type')
            
            # Association has type as object with "ref"
            if isinstance(col_type, dict) and 'ref' in col_type:
                association = self._parse_association(col_name, col_def)
                associations.append(association)
        
        return EntityMetadata(
            name=entity_name,
            original_name=entity_def.get('__abapOriginalName', entity_name),
            label=entity_def.get('@EndUserText.label'),
            columns=columns,
            primary_keys=primary_keys,
            associations=associations,
            kind=entity_def.get('kind', 'entity')
        )
    
    def get_primary_keys(self, entity_name: str) -> List[str]:
        """
        Get primary key column names for an entity
        
        Args:
            entity_name: Simple entity name
            
        Returns:
            List of primary key column names
        """
        metadata = self.get_entity_metadata(entity_name)
        return metadata.primary_keys if metadata else []
    
    def get_foreign_keys(self, entity_name: str) -> List[Dict[str, Any]]:
        """
        Get foreign key relationships for an entity
        
        Args:
            entity_name: Simple entity name
            
        Returns:
            List of foreign key dictionaries with:
            - name: FK column name
            - references_table: Target table name
            - references_column: Target column name
        """
        metadata = self.get_entity_metadata(entity_name)
        if not metadata:
            return []
        
        foreign_keys = []
        for assoc in metadata.associations:
            if assoc.cardinality == "one":  # FK is many-to-one
                for key_map in assoc.keys:
                    foreign_keys.append({
                        'name': key_map.get('local', assoc.name),
                        'references_table': assoc.target,
                        'references_column': key_map.get('foreign', 'id')
                    })
        
        return foreign_keys
    
    def get_associations(self, entity_name: str) -> List[Dict[str, Any]]:
        """
        Get all associations (relationships) for an entity
        
        Args:
            entity_name: Simple entity name
            
        Returns:
            List of association dictionaries
        """
        metadata = self.get_entity_metadata(entity_name)
        if not metadata:
            return []
        
        return [
            {
                'name': assoc.name,
                'target': assoc.target,
                'cardinality': assoc.cardinality,
                'type': 'foreign_key' if assoc.cardinality == 'one' else 'navigation',
                'on_conditions': assoc.on_conditions
            }
            for assoc in metadata.associations
        ]
    
    def get_column_metadata(self, entity_name: str, column_name: str) -> Optional[ColumnMetadata]:
        """
        Get metadata for a specific column
        
        Args:
            entity_name: Simple entity name
            column_name: Column name
            
        Returns:
            ColumnMetadata object or None if not found
        """
        metadata = self.get_entity_metadata(entity_name)
        if not metadata:
            return None
        
        for column in metadata.columns:
            if column.name == column_name:
                return column
        
        return None
    
    def list_entities(self) -> List[str]:
        """
        List all available entities in CSN files
        
        Returns:
            List of entity names
        """
        index = self._build_entity_index()
        return sorted(index.keys())
    
    def clear_cache(self):
        """Clear all caches (useful for testing or reloading)"""
        self._file_cache.clear()
        self._entity_index = None
        self._load_csn_file.cache_clear()


# Singleton instance for convenience
_default_parser: Optional[CSNParser] = None


def get_parser(csn_directory: str = 'docs/csn') -> CSNParser:
    """
    Get or create default CSN parser instance
    
    Args:
        csn_directory: Path to CSN files (default: 'docs/csn')
        
    Returns:
        CSNParser instance
    """
    global _default_parser
    if _default_parser is None:
        _default_parser = CSNParser(csn_directory)
    return _default_parser


# Convenience functions using default parser
def get_primary_keys(entity_name: str) -> List[str]:
    """Convenience function: Get primary keys using default parser"""
    return get_parser().get_primary_keys(entity_name)


def get_foreign_keys(entity_name: str) -> List[Dict[str, Any]]:
    """Convenience function: Get foreign keys using default parser"""
    return get_parser().get_foreign_keys(entity_name)


def get_associations(entity_name: str) -> List[Dict[str, Any]]:
    """Convenience function: Get associations using default parser"""
    return get_parser().get_associations(entity_name)


def list_entities() -> List[str]:
    """Convenience function: List all entities using default parser"""
    return get_parser().list_entities()