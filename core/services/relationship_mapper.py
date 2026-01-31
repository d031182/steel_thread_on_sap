"""
CSN Relationship Mapper

Automatically discovers relationships between entities using CSN metadata.
Uses column naming conventions to infer foreign key relationships.
"""

from typing import List, Dict, Set, Optional
from dataclasses import dataclass
from functools import lru_cache

from .csn_parser import CSNParser


@dataclass
class Relationship:
    """
    Represents a relationship between two entities
    """
    from_entity: str          # Source entity name
    from_column: str          # Source column name
    to_entity: str            # Target entity name
    to_column: str            # Target column name (usually PK)
    relationship_type: str    # 'many-to-one', 'one-to-many', etc.
    confidence: float = 1.0   # Confidence score (0.0 to 1.0)
    inferred: bool = True     # True if inferred, False if manually defined
    
    def __hash__(self):
        """Allow relationships to be used in sets"""
        return hash((self.from_entity, self.from_column, self.to_entity, self.to_column))
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON serialization"""
        return {
            'from_entity': self.from_entity,
            'from_column': self.from_column,
            'to_entity': self.to_entity,
            'to_column': self.to_column,
            'relationship_type': self.relationship_type,
            'confidence': self.confidence,
            'inferred': self.inferred
        }


class CSNRelationshipMapper:
    """
    Automatically discover relationships from CSN metadata
    
    Uses column naming conventions to infer FK relationships:
    - If a non-PK column name matches another entity name → likely FK
    - Target column is usually the entity's PK
    - Validates data types for compatibility
    
    Example:
        mapper = CSNRelationshipMapper(csn_parser)
        relationships = mapper.discover_relationships()
        # Returns 100+ relationships automatically!
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
    
    @lru_cache(maxsize=1)
    def _get_entity_set(self) -> Set[str]:
        """Get set of all entity names (cached)"""
        return set(self.csn_parser.list_entities())
    
    def discover_relationships(self, confidence_threshold: float = 0.5) -> List[Relationship]:
        """
        Discover all relationships between entities
        
        Args:
            confidence_threshold: Minimum confidence score (0.0 to 1.0)
        
        Returns:
            List of discovered relationships
        """
        if self._cache is not None:
            return self._cache
        
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
                        inferred=True
                    )
                    
                    # Only include if confidence is above threshold
                    if rel.confidence >= confidence_threshold:
                        relationships.add(rel)
        
        # Add manual relationships
        relationships.update(self._manual_relationships)
        
        # Sort by confidence (highest first)
        result = sorted(relationships, key=lambda r: r.confidence, reverse=True)
        
        # Cache result
        self._cache = result
        return result
    
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