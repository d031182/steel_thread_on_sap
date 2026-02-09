"""
Graph Aggregate Root for Knowledge Graph v2

The Graph is the aggregate root that enforces invariants across nodes and edges.
"""
from typing import Dict, List, Any, Optional
from .graph_node import GraphNode
from .graph_edge import GraphEdge
from .enums import GraphType, EdgeType


class Graph:
    """
    Graph aggregate root
    
    Enforces invariants:
    - All edges reference existing nodes (referential integrity)
    - No duplicate nodes (uniqueness by ID)
    - No duplicate edges (idempotent edge addition)
    
    This is the main domain object that ensures graph consistency.
    """
    
    def __init__(self, graph_id: str, graph_type: GraphType):
        """
        Initialize graph
        
        Args:
            graph_id: Unique identifier for this graph
            graph_type: Type of graph (SCHEMA, DATA, CSN)
        """
        if not graph_id:
            raise ValueError("Graph id cannot be empty")
        if not isinstance(graph_type, GraphType):
            raise ValueError(f"Graph type must be GraphType enum, got {type(graph_type)}")
        
        self.id = graph_id
        self.type = graph_type
        self._nodes: Dict[str, GraphNode] = {}
        self._edges: List[GraphEdge] = []
    
    def add_node(self, node: GraphNode) -> None:
        """
        Add node to graph
        
        Enforces uniqueness: raises ValueError if node with same ID already exists
        
        Args:
            node: GraphNode to add
            
        Raises:
            ValueError: If node with same ID already exists
        """
        if node.id in self._nodes:
            raise ValueError(f"Node with id '{node.id}' already exists")
        
        self._nodes[node.id] = node
    
    def add_edge(self, edge: GraphEdge) -> None:
        """
        Add edge to graph
        
        Enforces referential integrity: both source and target nodes must exist
        Enforces uniqueness: duplicate edges are ignored (idempotent)
        
        Args:
            edge: GraphEdge to add
            
        Raises:
            ValueError: If source or target node doesn't exist
        """
        # Enforce referential integrity
        if edge.source_id not in self._nodes:
            raise ValueError(f"Source node '{edge.source_id}' not found in graph")
        if edge.target_id not in self._nodes:
            raise ValueError(f"Target node '{edge.target_id}' not found in graph")
        
        # Check for duplicate (idempotent addition)
        if self._has_edge(edge.source_id, edge.target_id, edge.type):
            return  # Silently ignore duplicate
        
        self._edges.append(edge)
    
    def get_node(self, node_id: str) -> Optional[GraphNode]:
        """
        Retrieve node by ID
        
        Args:
            node_id: ID of node to retrieve
            
        Returns:
            GraphNode if found, None otherwise
        """
        return self._nodes.get(node_id)
    
    def has_node(self, node_id: str) -> bool:
        """
        Check if node exists
        
        Args:
            node_id: ID of node to check
            
        Returns:
            True if node exists, False otherwise
        """
        return node_id in self._nodes
    
    @property
    def nodes(self) -> List[GraphNode]:
        """
        Get all nodes (immutable view)
        
        Returns:
            List of all nodes (copy, not reference)
        """
        return list(self._nodes.values())
    
    @property
    def edges(self) -> List[GraphEdge]:
        """
        Get all edges (immutable view)
        
        Returns:
            List of all edges (copy, not reference)
        """
        return list(self._edges)
    
    def _has_edge(self, source_id: str, target_id: str, edge_type: EdgeType) -> bool:
        """
        Check if edge already exists
        
        Args:
            source_id: Source node ID
            target_id: Target node ID
            edge_type: Type of edge
            
        Returns:
            True if edge exists, False otherwise
        """
        return any(
            e.source_id == source_id 
            and e.target_id == target_id 
            and e.type == edge_type
            for e in self._edges
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert to generic dictionary format
        
        Returns GENERIC graph format (NOT vis.js specific!):
        - nodes: List of node dicts
        - edges: List of edge dicts
        
        Frontend adapters convert this to library-specific format (vis.js, D3, etc.)
        
        Returns:
            Dict with nodes and edges arrays
        """
        return {
            'nodes': [node.to_dict() for node in self._nodes.values()],
            'edges': [edge.to_dict() for edge in self._edges]
        }
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Get graph statistics
        
        Returns:
            Dict with node count, edge count, graph type, etc.
        """
        return {
            'graph_id': self.id,
            'graph_type': self.type.value,
            'node_count': len(self._nodes),
            'edge_count': len(self._edges),
            'nodes_by_type': self._count_nodes_by_type(),
            'edges_by_type': self._count_edges_by_type()
        }
    
    def _count_nodes_by_type(self) -> Dict[str, int]:
        """Count nodes by type"""
        counts = {}
        for node in self._nodes.values():
            type_name = node.type.value
            counts[type_name] = counts.get(type_name, 0) + 1
        return counts
    
    def _count_edges_by_type(self) -> Dict[str, int]:
        """Count edges by type"""
        counts = {}
        for edge in self._edges:
            type_name = edge.type.value
            counts[type_name] = counts.get(type_name, 0) + 1
        return counts