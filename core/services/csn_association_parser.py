"""
CSN Association Parser

Parses CSN association metadata including ON conditions, cardinality, and targets.
This is Phase 1 of the Knowledge Graph Semantic Enhancement (HIGH-29).

Key Features:
- Parse CSN associations with ON conditions
- Extract cardinality information (1:1, 1:*, *:*)
- Detect many-to-many relationships
- Calculate relationship complexity metrics
- Support for join tables and bridge entities

Based on analysis of 97 associations found in CSN files.
"""

from typing import List, Dict, Optional, Set, Tuple
from dataclasses import dataclass
from enum import Enum
import logging

from .csn_parser import CSNParser

logger = logging.getLogger(__name__)


class CardinalityType(Enum):
    """Relationship cardinality types"""
    ONE_TO_ONE = "1:1"
    ONE_TO_MANY = "1:*"
    MANY_TO_ONE = "*:1"
    MANY_TO_MANY = "*:*"


@dataclass
class AssociationCondition:
    """
    Represents a single condition in an association's ON clause
    
    Example from CSN:
    {
      "ref": ["CompanyCode"]
    },
    "=",
    {
      "ref": ["_CompanyCodeHierNode", "CompanyCode"]
    }
    """
    source_field: str           # Local field (e.g., "CompanyCode")
    operator: str               # Usually "="
    target_field: str           # Target field path (e.g., "_CompanyCodeHierNode.CompanyCode")
    target_entity: Optional[str] = None  # Resolved target entity name
    
    def __str__(self):
        return f"{self.source_field} {self.operator} {self.target_field}"


@dataclass
class CSNAssociation:
    """
    Represents a parsed CSN association with full metadata
    
    Example:
        {
          "__abapOriginalName": "_CompanyCodeHierNode",
          "type": "cds.Association",
          "cardinality": {"max": "*"},
          "target": "companycode.CompanyCodeHierarchyNode",
          "on": [...]
        }
    """
    source_entity: str                      # Entity containing the association
    field_name: str                         # Association field name (e.g., "_CompanyCode")
    target_entity: str                      # Target entity name
    cardinality_type: CardinalityType       # Relationship cardinality
    cardinality_max: Optional[str]          # Max cardinality ("1", "*", etc.)
    cardinality_min: Optional[str]          # Min cardinality (optional)
    conditions: List[AssociationCondition]  # ON clause conditions
    is_composition: bool = False            # True if composition
    is_many_to_many: bool = False           # True if many-to-many
    confidence: float = 1.0                 # Confidence score (1.0 for explicit CSN)
    
    def get_join_condition(self) -> str:
        """Get human-readable join condition"""
        if not self.conditions:
            return f"{self.source_entity}.{self.field_name} → {self.target_entity}"
        return " AND ".join(str(cond) for cond in self.conditions)
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON serialization"""
        return {
            'source_entity': self.source_entity,
            'field_name': self.field_name,
            'target_entity': self.target_entity,
            'cardinality': self.cardinality_type.value,
            'cardinality_max': self.cardinality_max,
            'cardinality_min': self.cardinality_min,
            'is_composition': self.is_composition,
            'is_many_to_many': self.is_many_to_many,
            'join_condition': self.get_join_condition(),
            'condition_count': len(self.conditions),
            'confidence': self.confidence
        }


class CSNAssociationParser:
    """
    Parse CSN associations with ON conditions
    
    This parser reads the 97 associations found in CSN files and extracts:
    - Association targets
    - Cardinality information
    - ON clause join conditions
    - Many-to-many relationship detection
    
    Example Usage:
        parser = CSNAssociationParser(csn_parser)
        associations = parser.parse_all_associations()
        print(f"Found {len(associations)} associations")
        
        # Get many-to-many relationships
        m2m = parser.find_many_to_many_relationships()
        print(f"Found {len(m2m)} many-to-many relationships")
    """
    
    def __init__(self, csn_parser: CSNParser):
        """
        Initialize association parser
        
        Args:
            csn_parser: CSN parser instance for metadata access
        """
        self.csn_parser = csn_parser
        self._cache: Optional[List[CSNAssociation]] = None
        logger.info("CSNAssociationParser initialized")
    
    def parse_all_associations(self) -> List[CSNAssociation]:
        """
        Parse all associations from all CSN files
        
        Returns:
            List of parsed associations (97 expected based on analysis)
        """
        if self._cache is not None:
            return self._cache
        
        associations = []
        entities = self.csn_parser.list_entities()
        
        logger.info(f"Parsing associations from {len(entities)} entities...")
        
        for entity_name in entities:
            entity_assocs = self._parse_entity_associations(entity_name)
            associations.extend(entity_assocs)
        
        logger.info(f"Parsed {len(associations)} associations")
        self._cache = associations
        return associations
    
    def _parse_entity_associations(self, entity_name: str) -> List[CSNAssociation]:
        """
        Parse associations for a specific entity
        
        Args:
            entity_name: Entity name
            
        Returns:
            List of associations for this entity
        """
        associations = []
        
        try:
            # Get entity metadata to verify entity exists
            entity_metadata = self.csn_parser.get_entity_metadata(entity_name)
            if not entity_metadata:
                return associations
            
            # Get raw CSN definition using private method
            result = self.csn_parser._find_entity_definition(entity_name)
            if not result:
                return associations
            
            csn_def, full_name = result
            if 'elements' not in csn_def:
                return associations
            
            elements = csn_def.get('elements', {})
            
            # Scan elements for associations
            for field_name, field_def in elements.items():
                if not isinstance(field_def, dict):
                    continue
                
                field_type = field_def.get('type', '')
                
                # Check if this is an association
                if field_type == 'cds.Association' or field_type == 'cds.Composition':
                    assoc = self._parse_association(entity_name, field_name, field_def)
                    if assoc:
                        associations.append(assoc)
        
        except Exception as e:
            logger.warning(f"Error parsing associations for {entity_name}: {e}")
        
        return associations
    
    def _parse_association(
        self, 
        entity_name: str, 
        field_name: str, 
        field_def: Dict
    ) -> Optional[CSNAssociation]:
        """
        Parse a single association field definition
        
        Args:
            entity_name: Source entity name
            field_name: Association field name
            field_def: Field definition from CSN
            
        Returns:
            Parsed association or None if invalid
        """
        try:
            # Get target entity
            target = field_def.get('target')
            if not target:
                logger.warning(f"No target for association {entity_name}.{field_name}")
                return None
            
            # Parse cardinality
            cardinality = field_def.get('cardinality', {})
            cardinality_max = cardinality.get('max', '1')
            cardinality_min = cardinality.get('min')
            
            # Determine cardinality type
            if cardinality_max == '*':
                cardinality_type = CardinalityType.ONE_TO_MANY
            else:
                cardinality_type = CardinalityType.ONE_TO_ONE
            
            # Parse ON conditions
            conditions = self._parse_on_conditions(field_def.get('on', []))
            
            # Check if composition
            is_composition = field_def.get('type') == 'cds.Composition'
            
            # Create association object
            assoc = CSNAssociation(
                source_entity=entity_name,
                field_name=field_name,
                target_entity=target,
                cardinality_type=cardinality_type,
                cardinality_max=cardinality_max,
                cardinality_min=cardinality_min,
                conditions=conditions,
                is_composition=is_composition,
                is_many_to_many=False,  # Will be detected later
                confidence=1.0  # Explicit CSN = 100% confidence
            )
            
            return assoc
        
        except Exception as e:
            logger.warning(f"Error parsing association {entity_name}.{field_name}: {e}")
            return None
    
    def _parse_on_conditions(self, on_clause: List) -> List[AssociationCondition]:
        """
        Parse ON clause conditions
        
        CSN ON clause structure:
        [
            {"ref": ["CompanyCode"]},
            "=",
            {"ref": ["_CompanyCodeHierNode", "CompanyCode"]}
        ]
        
        Args:
            on_clause: ON clause list from CSN
            
        Returns:
            List of parsed conditions
        """
        conditions = []
        
        try:
            # ON clause is a list of [left_operand, operator, right_operand, ...]
            i = 0
            while i < len(on_clause):
                if i + 2 >= len(on_clause):
                    break
                
                left = on_clause[i]
                operator = on_clause[i + 1]
                right = on_clause[i + 2]
                
                # Parse left side (source field)
                if isinstance(left, dict) and 'ref' in left:
                    source_field = '.'.join(left['ref'])
                else:
                    source_field = str(left)
                
                # Parse right side (target field)
                if isinstance(right, dict) and 'ref' in right:
                    target_field = '.'.join(right['ref'])
                else:
                    target_field = str(right)
                
                # Create condition
                condition = AssociationCondition(
                    source_field=source_field,
                    operator=str(operator),
                    target_field=target_field
                )
                conditions.append(condition)
                
                # Move to next condition (skip AND/OR operators)
                i += 3
                if i < len(on_clause) and isinstance(on_clause[i], str):
                    i += 1  # Skip AND/OR
        
        except Exception as e:
            logger.warning(f"Error parsing ON conditions: {e}")
        
        return conditions
    
    def find_many_to_many_relationships(self) -> List[Tuple[CSNAssociation, CSNAssociation]]:
        """
        Detect many-to-many relationships
        
        Strategy:
        1. Find entities with multiple associations (potential join tables)
        2. Check if entity has only associations and keys (bridge entity pattern)
        3. Link both sides to create M:N relationship
        
        Returns:
            List of (assoc1, assoc2) tuples representing M:N relationships
        """
        associations = self.parse_all_associations()
        m2m_relationships = []
        
        # Group associations by source entity
        by_entity: Dict[str, List[CSNAssociation]] = {}
        for assoc in associations:
            if assoc.source_entity not in by_entity:
                by_entity[assoc.source_entity] = []
            by_entity[assoc.source_entity].append(assoc)
        
        # Find potential join tables (entities with 2+ associations)
        for entity_name, entity_assocs in by_entity.items():
            if len(entity_assocs) >= 2:
                # Check if this looks like a join table
                # (has mostly associations, few other fields)
                if self._is_join_table(entity_name, entity_assocs):
                    # Create M:N pairs
                    for i, assoc1 in enumerate(entity_assocs):
                        for assoc2 in entity_assocs[i+1:]:
                            m2m_relationships.append((assoc1, assoc2))
                            # Mark as M:N
                            assoc1.is_many_to_many = True
                            assoc2.is_many_to_many = True
        
        logger.info(f"Detected {len(m2m_relationships)} many-to-many relationships")
        return m2m_relationships
    
    def _is_join_table(self, entity_name: str, associations: List[CSNAssociation]) -> bool:
        """
        Check if entity is a join table
        
        Heuristic: Entity has 2+ associations and most fields are keys/FKs
        
        Args:
            entity_name: Entity name
            associations: Associations for this entity
            
        Returns:
            True if likely a join table
        """
        try:
            entity = self.csn_parser.get_entity_metadata(entity_name)
            if not entity:
                return False
            
            # Count association fields vs total fields
            assoc_count = len(associations)
            total_fields = len(entity.columns)
            
            # Join table if > 50% of fields are associations
            return assoc_count / total_fields > 0.5 if total_fields > 0 else False
        
        except Exception:
            return False
    
    def get_cardinality_statistics(self) -> Dict[str, int]:
        """
        Calculate cardinality statistics
        
        Returns:
            Dictionary with counts for each cardinality type
        """
        associations = self.parse_all_associations()
        
        stats = {
            '1:1': 0,
            '1:*': 0,
            '*:1': 0,
            '*:*': 0
        }
        
        for assoc in associations:
            stats[assoc.cardinality_type.value] += 1
        
        return stats
    
    def get_relationship_complexity_metrics(self) -> Dict[str, any]:
        """
        Calculate relationship complexity metrics
        
        Returns:
            Dictionary with complexity metrics:
            - total_associations: Total count
            - avg_conditions_per_assoc: Average ON conditions
            - many_to_many_count: M:N relationships
            - composition_count: Composition relationships
            - most_connected_entities: Top entities by association count
        """
        associations = self.parse_all_associations()
        m2m = self.find_many_to_many_relationships()
        
        # Calculate average conditions
        total_conditions = sum(len(a.conditions) for a in associations)
        avg_conditions = total_conditions / len(associations) if associations else 0
        
        # Count compositions
        composition_count = sum(1 for a in associations if a.is_composition)
        
        # Find most connected entities
        entity_counts: Dict[str, int] = {}
        for assoc in associations:
            entity_counts[assoc.source_entity] = entity_counts.get(assoc.source_entity, 0) + 1
        
        most_connected = sorted(
            entity_counts.items(), 
            key=lambda x: x[1], 
            reverse=True
        )[:10]
        
        return {
            'total_associations': len(associations),
            'avg_conditions_per_assoc': round(avg_conditions, 2),
            'many_to_many_count': len(m2m),
            'composition_count': composition_count,
            'most_connected_entities': most_connected,
            'cardinality_distribution': self.get_cardinality_statistics()
        }
    
    def export_associations(self) -> List[Dict]:
        """
        Export all associations as list of dictionaries
        
        Returns:
            List of association dictionaries
        """
        return [assoc.to_dict() for assoc in self.parse_all_associations()]
    
    def clear_cache(self) -> None:
        """Clear cached associations"""
        self._cache = None