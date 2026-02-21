"""
CSN Relationship Mapper

Automatically discovers relationships between entities using CSN metadata.
Uses two strategies:
1. Explicit associations from CSN (with ON conditions) - Phase 1 integration (HIGH-29)
2. Inferred relationships from column naming conventions - Legacy fallback

Integration with CSNAssociationParser enables semantic enhancement:
- Explicit join conditions (ON clauses)
- Cardinality metadata (1:1, 1:*, *:*)
- Composition detection
- Many-to-many relationship tracking
"""

from typing import List, Dict, Set, Optional
from dataclasses import dataclass
from functools import lru_cache
import logging

from .csn_parser import CSNParser

logger = logging.getLogger(__name__)


@dataclass
class Relationship:
    """
    Represents a relationship between two entities
    
    Enhanced with ON condition support from CSNAssociationParser (HIGH-29 Phase 2)
    """
    from_entity: str          # Source entity name
    from_column: str          # Source column name
    to_entity: str            # Target entity name
    to_column: str            # Target column name (usually PK)
    relationship_type: str    # 'many-to-one', 'one-to-many', etc.
    confidence: float = 1.0   # Confidence score (0.0 to 1.0)
    inferred: bool = True     # True if inferred, False if from explicit CSN
    
    # NEW: Semantic enhancement fields (HIGH-29 Phase 2)
    cardinality: Optional[str] = None     # e.g., "1:*", "1:1", "*:*"
    on_conditions: Optional[List[str]] = None  # JOIN ON conditions from CSN
    is_composition: bool = False          # True if CSN composition
    is_many_to_many: bool = False         # True if M:N relationship
    
    def __hash__(self):
        """Allow relationships to be used in sets"""
        return hash((self.from_entity, self.from_column, self.to_entity, self.to_column))
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON serialization"""
        result = {
            'from_entity': self.from_entity,
            'from_column': self.from_column,
            'to_entity': self.to_entity,
            'to_column': self.to_column,
            'relationship_type': self.relationship_type,
            'confidence': self.confidence,
            'inferred': self.inferred
        }
        
        # Add semantic enhancement fields if present (HIGH-29)
        if self.cardinality:
            result['cardinality'] = self.cardinality
        if self.on_conditions:
            result['on_conditions'] = self.on_conditions
        if self.is_composition:
            result['is_composition'] = self.is_composition
        if self.is_many_to_many:
            result['is_many_to_many'] = self.is_many_to_many
        
        return result


class CSNRelationshipMapper:
    """
    Automatically discover relationships from CSN metadata
    
    Two-tier discovery strategy (HIGH-29 Phase 2 integration):
    
    1. **Explicit CSN Associations** (97 associations):
       - Parse CSN associations with ON conditions
       - Extract cardinality (1:1, 1:*, *:*)
       - Detect compositions and many-to-many
       - Confidence: 1.0 (explicit from CSN)
    
    2. **Inferred from Column Names** (legacy fallback):
       - If non-PK column name matches entity name → likely FK
       - Target column is usually entity's PK
       - Validates data type compatibility
       - Confidence: 0.5-0.9 (heuristic-based)
    
    Example:
        mapper = CSNRelationshipMapper(csn_parser)
        relationships = mapper.discover_relationships()
        # Returns 100+ relationships (97 explicit + inferred)
        
        # Access semantic metadata
        for rel in relationships:
            if rel.on_conditions:
                print(f"JOIN ON: {', '.join(rel.on_conditions)}")
            print(f"Cardinality: {rel.cardinality}")
    """
    
    def __init__(self, csn_parser: CSNParser):
        """
        Initialize relationship mapper
        
        Args:
            csn_parser: CSN parser instance for metadata access
        """
        self.csn_parser = csn_parser
        self._manual_relationships: Set[Relationship] = set()
        self._cache: Optional[List[Relationship]] = None
        
        # NEW: Lazy-load CSNAssociationParser (HIGH-29 Phase 2)
        self._association_parser = None
        logger.info("CSNRelationshipMapper initialized with CSNAssociationParser integration")
    
    @lru_cache(maxsize=1)
    def _get_entity_set(self) -> Set[str]:
        """Get set of all entity names (cached)"""
        return set(self.csn_parser.list_entities())
    
    def discover_relationships(self, confidence_threshold: float = 0.5) -> List[Relationship]:
        """
        Discover all relationships between entities
        
        Two-tier discovery (HIGH-29 Phase 2):
        1. Explicit CSN associations (with ON conditions)
        2. Inferred from column naming patterns
        
        Args:
            confidence_threshold: Minimum confidence score (0.0 to 1.0)
        
        Returns:
            List of discovered relationships (explicit + inferred)
        """
        if self._cache is not None:
            return self._cache
        
        relationships = set()
        
        # TIER 1: Discover explicit CSN associations (HIGH-29 Phase 2)
        explicit_rels = self._discover_explicit_associations()
        relationships.update(explicit_rels)
        logger.info(f"Discovered {len(explicit_rels)} explicit relationships from CSN associations")
        
        # TIER 2: Discover inferred relationships (legacy fallback)
        inferred_rels = self._discover_inferred_relationships()
        
        # Remove inferred relationships that conflict with explicit ones
        explicit_keys = {(r.from_entity, r.from_column, r.to_entity) for r in explicit_rels}
        for rel in inferred_rels:
            key = (rel.from_entity, rel.from_column, rel.to_entity)
            if key not in explicit_keys:
                relationships.add(rel)
        
        logger.info(f"Discovered {len(inferred_rels)} inferred relationships (after deduplication)")
        
        # Add manual relationships
        relationships.update(self._manual_relationships)
        
        # Filter by confidence threshold
        filtered = [r for r in relationships if r.confidence >= confidence_threshold]
        
        # Sort by confidence (highest first)
        result = sorted(filtered, key=lambda r: r.confidence, reverse=True)
        
        # Cache result
        self._cache = result
        logger.info(f"Total relationships discovered: {len(result)} (threshold: {confidence_threshold})")
        return result
    
    def _get_association_parser(self):
        """Lazy-load CSNAssociationParser"""
        if self._association_parser is None:
            from .csn_association_parser import CSNAssociationParser
            self._association_parser = CSNAssociationParser(self.csn_parser)
        return self._association_parser
    
    def _discover_explicit_associations(self) -> Set[Relationship]:
        """
        Discover explicit relationships from CSN associations (HIGH-29 Phase 2)
        
        Returns:
            Set of relationships from CSN associations (with ON conditions)
        """
        relationships = set()
        
        try:
            parser = self._get_association_parser()
            associations = parser.parse_all_associations()
            
            for assoc in associations:
                # Strip namespace prefix from target entity (HIGH-29 fix)
                # CSN: "companycode.CompanyCode" -> "CompanyCode"
                # CSN: "product.Product" -> "Product"
                target_entity = self._normalize_entity_name(assoc.target_entity)
                
                # Convert CSNAssociation to Relationship
                rel = Relationship(
                    from_entity=assoc.source_entity,
                    from_column=assoc.field_name,
                    to_entity=target_entity,
                    to_column='',  # Target column in ON conditions
                    relationship_type=assoc.cardinality_type.value,
                    confidence=assoc.confidence,  # 1.0 for explicit
                    inferred=False,  # Explicit from CSN
                    # Semantic enhancement fields (HIGH-29)
                    cardinality=assoc.cardinality_type.value,
                    on_conditions=[str(cond) for cond in assoc.conditions] if assoc.conditions else None,
                    is_composition=assoc.is_composition,
                    is_many_to_many=assoc.is_many_to_many
                )
                relationships.add(rel)
        
        except Exception as e:
            logger.warning(f"Failed to discover explicit associations: {e}", exc_info=True)
        
        return relationships
    
    def _normalize_entity_name(self, entity_name: str) -> str:
        """
        Normalize entity name by stripping namespace prefix
        
        CSN associations use format: "namespace.EntityName"
        But CSN entity list uses format: "EntityName"
        
        Args:
            entity_name: Entity name (possibly with namespace)
        
        Returns:
            Entity name without namespace prefix
        
        Examples:
            "companycode.CompanyCode" -> "CompanyCode"
            "product.Product" -> "Product"
            "CompanyCode" -> "CompanyCode"
        """
        if '.' in entity_name:
            # Strip namespace prefix
            return entity_name.split('.')[-1]
        return entity_name
    
    def _discover_inferred_relationships(self) -> Set[Relationship]:
        """
        Discover inferred relationships from column naming conventions (legacy)
        
        Returns:
            Set of inferred relationships
        """
        relationships = set()
        entities = self._get_entity_set()
        
        # Scan all entities for potential relationships
        for entity_name in entities:
            entity = self.csn_parser.get_entity_metadata(entity_name)
            if not entity:
                continue
            
            # Check each column for FK patterns
            for column in entity.columns:
                # Skip primary key columns
                if column.is_key:
                    continue
                
                # Check if column name matches another entity
                if column.name in entities:
                    # Found a potential FK relationship!
                    target_entity = self.csn_parser.get_entity_metadata(column.name)
                    if not target_entity:
                        continue
                    
                    # Get target PK (usually same name as entity)
                    target_pk = target_entity.primary_keys[0] if target_entity.primary_keys else column.name
                    
                    # Create relationship
                    rel = Relationship(
                        from_entity=entity_name,
                        from_column=column.name,
                        to_entity=column.name,
                        to_column=target_pk,
                        relationship_type='many-to-one',
                        confidence=self._calculate_confidence(column, target_entity),
                        inferred=True  # Inferred from naming
                    )
                    
                    relationships.add(rel)
        
        return relationships
    
    def _calculate_confidence(self, column, target_entity) -> float:
        """
        Calculate confidence score for a potential relationship
        
        Args:
            column: Source column metadata
            target_entity: Target entity metadata
        
        Returns:
            Confidence score (0.0 to 1.0)
        """
        score = 0.0
        
        # Exact name match is strong signal
        if column.name == target_entity.name:
            score += 0.7
        
        # Column matches target's primary key
        if target_entity.primary_keys and column.name in target_entity.primary_keys:
            score += 0.2
        
        # Data type compatibility
        if target_entity.primary_keys:
            pk_column = next((c for c in target_entity.columns if c.name in target_entity.primary_keys), None)
            if pk_column and column.type == pk_column.type:
                score += 0.1
        
        return min(score, 1.0)
    
    def add_manual_relationship(
        self,
        from_entity: str,
        from_column: str,
        to_entity: str,
        to_column: str,
        relationship_type: str = 'many-to-one'
    ) -> None:
        """
        Manually add a relationship that doesn't follow naming conventions
        
        Args:
            from_entity: Source entity name
            from_column: Source column name
            to_entity: Target entity name
            to_column: Target column name
            relationship_type: Type of relationship
        """
        rel = Relationship(
            from_entity=from_entity,
            from_column=from_column,
            to_entity=to_entity,
            to_column=to_column,
            relationship_type=relationship_type,
            confidence=1.0,  # Manual relationships have 100% confidence
            inferred=False
        )
        self._manual_relationships.add(rel)
        self._cache = None  # Clear cache
    
    def get_relationships_for_entity(self, entity_name: str) -> List[Relationship]:
        """
        Get all relationships involving a specific entity
        
        Args:
            entity_name: Entity name
        
        Returns:
            List of relationships where entity is source or target
        """
        all_rels = self.discover_relationships()
        return [
            rel for rel in all_rels
            if rel.from_entity == entity_name or rel.to_entity == entity_name
        ]
    
    def get_outgoing_relationships(self, entity_name: str) -> List[Relationship]:
        """
        Get outgoing relationships (where entity is the source)
        
        Args:
            entity_name: Entity name
        
        Returns:
            List of relationships where entity is source
        """
        all_rels = self.discover_relationships()
        return [rel for rel in all_rels if rel.from_entity == entity_name]
    
    def get_incoming_relationships(self, entity_name: str) -> List[Relationship]:
        """
        Get incoming relationships (where entity is the target)
        
        Args:
            entity_name: Entity name
        
        Returns:
            List of relationships where entity is target
        """
        all_rels = self.discover_relationships()
        return [rel for rel in all_rels if rel.to_entity == entity_name]
    
    def clear_cache(self) -> None:
        """Clear cached relationships"""
        self._cache = None
        self._get_entity_set.cache_clear()
    
    def export_relationships(self) -> List[Dict]:
        """
        Export all relationships as list of dictionaries
        
        Returns:
            List of relationship dictionaries
        """
        return [rel.to_dict() for rel in self.discover_relationships()]


# Convenience function
def discover_relationships(csn_directory: str = 'docs/csn') -> List[Relationship]:
    """
    Convenience function to discover relationships
    
    Args:
        csn_directory: Path to CSN files
    
    Returns:
        List of discovered relationships
    """
    from .csn_parser import CSNParser
    parser = CSNParser(csn_directory)
    mapper = CSNRelationshipMapper(parser)
    return mapper.discover_relationships()