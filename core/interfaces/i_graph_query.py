"""
Graph Query Engine Interface

Provides a unified interface for graph query operations that works with:
- HANA Property Graph (production)
- NetworkX + SQLite (development fallback)

@author P2P Development Team
@version 1.0.0
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Optional, Any
from dataclasses import dataclass, field
from enum import Enum


class TraversalDirection(Enum):
    """Direction for graph traversal"""
    OUTGOING = "outgoing"
    INCOMING = "incoming"
    BOTH = "both"


@dataclass
class GraphNode:
    """
    Standard node representation across all graph backends.
    
    Examples:
        GraphNode(
            id="PurchaseOrder:PO000001",
            label="PurchaseOrder",
            properties={"amount": 5000.0, "status": "Approved"}
        )
    """
    id: str
    label: str
    properties: Dict[str, Any] = field(default_factory=dict)
    
    def __hash__(self):
        return hash(self.id)
    
    def __eq__(self, other):
        return isinstance(other, GraphNode) and self.id == other.id


@dataclass
class GraphEdge:
    """
    Standard edge representation across all graph backends.
    
    Examples:
        GraphEdge(
            id="PO000001->5100000001",
            source_id="PurchaseOrder:PO000001",
            target_id="SupplierInvoice:5100000001",
            label="has_invoice",
            properties={"created_at": "2026-01-31"}
        )
    """
    id: str
    source_id: str
    target_id: str
    label: str
    properties: Dict[str, Any] = field(default_factory=dict)
    
    def __hash__(self):
        return hash(self.id)
    
    def __eq__(self, other):
        return isinstance(other, GraphEdge) and self.id == other.id


@dataclass
class GraphPath:
    """
    Represents a path through the graph.
    
    Examples:
        GraphPath(
            nodes=[supplier_node, po_node, invoice_node],
            edges=[supplier_po_edge, po_invoice_edge],
            length=2
        )
    """
    nodes: List[GraphNode]
    edges: List[GraphEdge]
    length: int
    
    @property
    def start_node(self) -> Optional[GraphNode]:
        """First node in path"""
        return self.nodes[0] if self.nodes else None
    
    @property
    def end_node(self) -> Optional[GraphNode]:
        """Last node in path"""
        return self.nodes[-1] if self.nodes else None
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON serialization"""
        return {
            'nodes': [{'id': n.id, 'label': n.label, 'properties': n.properties} for n in self.nodes],
            'edges': [{'id': e.id, 'source': e.source_id, 'target': e.target_id, 'label': e.label} for e in self.edges],
            'length': self.length
        }


@dataclass
class Subgraph:
    """
    Represents a subgraph (subset of nodes and edges).
    
    Examples:
        Subgraph(
            nodes={node1, node2, node3},
            edges={edge1, edge2}
        )
    """
    nodes: set[GraphNode] = field(default_factory=set)
    edges: set[GraphEdge] = field(default_factory=set)
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON serialization"""
        return {
            'nodes': [{'id': n.id, 'label': n.label, 'properties': n.properties} for n in self.nodes],
            'edges': [
                {'id': e.id, 'source': e.source_id, 'target': e.target_id, 'label': e.label, 'properties': e.properties}
                for e in self.edges
            ],
            'node_count': len(self.nodes),
            'edge_count': len(self.edges)
        }


class IGraphQueryEngine(ABC):
    """
    Interface for graph query engines.
    
    Implementations:
    - HANAGraphQueryEngine: Uses HANA Property Graph SQL
    - NetworkXGraphQueryEngine: Uses SQLite + NetworkX in-memory
    
    Design Pattern: Strategy Pattern
    - Define interface for graph operations
    - Concrete implementations for different backends
    - GraphQueryService uses factory to select engine
    
    Example Usage:
        engine = NetworkXGraphQueryEngine(db_path)
        
        # Find neighbors
        neighbors = engine.get_neighbors('PurchaseOrder:PO000001')
        
        # Find path
        path = engine.shortest_path(
            'Supplier:SUP001',
            'SupplierInvoice:5100000001'
        )
    """
    
    @abstractmethod
    def get_neighbors(
        self,
        node_id: str,
        direction: TraversalDirection = TraversalDirection.OUTGOING,
        edge_types: Optional[List[str]] = None,
        limit: Optional[int] = None
    ) -> List[GraphNode]:
        """
        Get adjacent nodes (direct neighbors).
        
        Args:
            node_id: ID of the source node
            direction: Direction to traverse (outgoing, incoming, both)
            edge_types: Filter by edge types (e.g., ['has_invoice', 'has_po'])
            limit: Maximum number of neighbors to return
            
        Returns:
            List of adjacent GraphNode objects
            
        Examples:
            # Get all invoices for a PO
            invoices = engine.get_neighbors(
                'PurchaseOrder:PO000001',
                direction=TraversalDirection.OUTGOING,
                edge_types=['has_invoice']
            )
        """
        pass
    
    @abstractmethod
    def shortest_path(
        self,
        start_id: str,
        end_id: str,
        max_hops: int = 10
    ) -> Optional[GraphPath]:
        """
        Find shortest path between two nodes.
        
        Args:
            start_id: Starting node ID
            end_id: Target node ID
            max_hops: Maximum path length (default 10)
            
        Returns:
            GraphPath object if path exists, None otherwise
            
        Examples:
            # Find path: Supplier -> PO -> Invoice
            path = engine.shortest_path(
                'Supplier:SUP001',
                'SupplierInvoice:5100000001',
                max_hops=5
            )
            
            if path:
                print(f"Path length: {path.length}")
                for node in path.nodes:
                    print(f"  {node.label}: {node.id}")
        """
        pass
    
    @abstractmethod
    def traverse(
        self,
        start_id: str,
        depth: int = 2,
        direction: TraversalDirection = TraversalDirection.OUTGOING,
        edge_types: Optional[List[str]] = None
    ) -> List[GraphNode]:
        """
        Breadth-first traversal from a starting node.
        
        Args:
            start_id: Starting node ID
            depth: Maximum depth to traverse
            direction: Direction to traverse
            edge_types: Filter by edge types
            
        Returns:
            List of reachable GraphNode objects
            
        Examples:
            # Get all nodes within 2 hops of a supplier
            related = engine.traverse(
                'Supplier:SUP001',
                depth=2,
                direction=TraversalDirection.OUTGOING
            )
            # Returns: Supplier, POs, Invoices
        """
        pass
    
    @abstractmethod
    def subgraph(
        self,
        node_ids: List[str],
        include_edges: bool = True
    ) -> Subgraph:
        """
        Extract a subgraph containing specified nodes.
        
        Args:
            node_ids: List of node IDs to include
            include_edges: If True, include edges between nodes
            
        Returns:
            Subgraph object
            
        Examples:
            # Extract subgraph for specific POs
            sg = engine.subgraph(
                ['PurchaseOrder:PO000001', 'PurchaseOrder:PO000002'],
                include_edges=True
            )
        """
        pass
    
    @abstractmethod
    def get_node(self, node_id: str) -> Optional[GraphNode]:
        """
        Get a single node by ID.
        
        Args:
            node_id: Node ID
            
        Returns:
            GraphNode if exists, None otherwise
        """
        pass
    
    @abstractmethod
    def node_exists(self, node_id: str) -> bool:
        """
        Check if a node exists in the graph.
        
        Args:
            node_id: Node ID to check
            
        Returns:
            True if node exists
        """
        pass
    
    @abstractmethod
    def get_node_count(self) -> int:
        """
        Get total number of nodes in graph.
        
        Returns:
            Node count
        """
        pass
    
    @abstractmethod
    def get_edge_count(self) -> int:
        """
        Get total number of edges in graph.
        
        Returns:
            Edge count
        """
        pass
    
    @abstractmethod
    def clear_cache(self) -> None:
        """
        Clear any cached graph data.
        
        Used to force reload from database after schema changes.
        """
        pass


# Type aliases for convenience
Node = GraphNode
Edge = GraphEdge
Path = GraphPath