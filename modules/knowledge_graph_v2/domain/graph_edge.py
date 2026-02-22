"""
GraphEdge Value Object for Knowledge Graph v2

Represents an immutable edge/relationship in the knowledge graph.
"""
from dataclasses import dataclass, field
from typing import Dict, Any, Optional
from .enums import EdgeType


@dataclass(frozen=True)
class GraphEdge:
    """
    Graph edge value object
    
    Represents a directed edge between two nodes.
    Immutable (frozen=True) - value objects cannot change after creation.
    """
    source_id: str
    target_id: str
    type: EdgeType
    label: Optional[str] = None
    properties: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        """Validate edge after initialization"""
        if not self.source_id:
            raise ValueError("Edge source_id cannot be empty")
        if not self.target_id:
            raise ValueError("Edge target_id cannot be empty")
        if not isinstance(self.type, EdgeType):
            raise ValueError(f"Edge type must be EdgeType enum, got {type(self.type)}")
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert to generic dictionary format
        
        Returns generic format with explicit IDs:
        - 'source_id'/'target_id' (explicit field names)
        - Frontend adapters convert this to library-specific format
          (e.g., vis.js uses 'from'/'to')
        
        Returns:
            Dict with source_id, target_id, type, label, and properties
        """
        result = {
            'source_id': self.source_id,
            'target_id': self.target_id,
            'type': self.type.value,
        }
        
        if self.label:
            result['label'] = self.label
        
        if self.properties:
            result.update(self.properties)
        
        return result
