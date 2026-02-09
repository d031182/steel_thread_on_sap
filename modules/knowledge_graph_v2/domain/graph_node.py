"""
GraphNode Entity for Knowledge Graph v2

Represents a node in the knowledge graph with immutable properties.
"""
from dataclasses import dataclass, field
from typing import Dict, Any
from .enums import NodeType


@dataclass
class GraphNode:
    """
    Graph node entity
    
    Represents a node in the knowledge graph (table, record, product, column).
    Immutable after creation (value object semantics for thread safety).
    """
    id: str
    label: str
    type: NodeType
    properties: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        """Validate node after initialization"""
        if not self.id:
            raise ValueError("Node id cannot be empty")
        if not self.label:
            raise ValueError("Node label cannot be empty")
        if not isinstance(self.type, NodeType):
            raise ValueError(f"Node type must be NodeType enum, got {type(self.type)}")
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert to generic dictionary format
        
        Returns generic format (NOT vis.js specific!):
        - 'type' (generic) not 'group' (vis.js specific)
        - Frontend adapters convert this to library-specific format
        
        Returns:
            Dict with id, label, type, and properties
        """
        return {
            'id': self.id,
            'label': self.label,
            'type': self.type.value,  # Generic 'type', not 'group'
            **self.properties
        }