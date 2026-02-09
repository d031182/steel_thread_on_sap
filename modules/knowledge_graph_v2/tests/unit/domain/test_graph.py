"""
Unit Tests for Graph Domain Model

Tests for Graph aggregate root and its invariants.
Following TDD: These tests validate domain logic in 0.001s (no DB needed).
"""
import pytest
from modules.knowledge_graph_v2.domain import (
    Graph, GraphNode, GraphEdge,
    GraphType, NodeType, EdgeType
)


@pytest.mark.unit
@pytest.mark.fast
class TestGraphCreation:
    """Test graph creation and initialization"""
    
    def test_create_graph_succeeds(self):
        """Test graph creation with valid parameters"""
        # ARRANGE & ACT
        graph = Graph("test-graph", GraphType.SCHEMA)
        
        # ASSERT
        assert graph.id == "test-graph"
        assert graph.type == GraphType.SCHEMA
        assert len(graph.nodes) == 0
        assert len(graph.edges) == 0
    
    def test_create_graph_with_empty_id_fails(self):
        """Test graph creation fails with empty ID"""
        # ACT & ASSERT
        with pytest.raises(ValueError, match="id cannot be empty"):
            Graph("", GraphType.SCHEMA)
    
    def test_create_graph_with_invalid_type_fails(self):
        """Test graph creation fails with invalid type"""
        # ACT & ASSERT
        with pytest.raises(ValueError, match="must be GraphType enum"):
            Graph("test", "not_an_enum")


@pytest.mark.unit
@pytest.mark.fast
class TestGraphNodeOperations:
    """Test node addition and retrieval"""
    
    def test_add_node_succeeds(self):
        """Test adding node to graph"""
        # ARRANGE
        graph = Graph("test", GraphType.SCHEMA)
        node = GraphNode("n1", "Test Node", NodeType.TABLE)
        
        # ACT
        graph.add_node(node)
        
        # ASSERT
        assert len(graph.nodes) == 1
        assert graph.has_node("n1")
        assert graph.get_node("n1") == node
    
    def test_add_duplicate_node_fails(self):
        """Test adding duplicate node raises ValueError"""
        # ARRANGE
        graph = Graph("test", GraphType.SCHEMA)
        node1 = GraphNode("n1", "Node 1", NodeType.TABLE)
        node2 = GraphNode("n1", "Node 2", NodeType.TABLE)  # Same ID
        
        graph.add_node(node1)
        
        # ACT & ASSERT
        with pytest.raises(ValueError, match="already exists"):
            graph.add_node(node2)
    
    def test_get_nonexistent_node_returns_none(self):
        """Test retrieving non-existent node returns None"""
        # ARRANGE
        graph = Graph("test", GraphType.SCHEMA)
        
        # ACT
        result = graph.get_node("missing")
        
        # ASSERT
        assert result is None
    
    def test_has_node_returns_false_for_missing(self):
        """Test has_node returns False for missing node"""
        # ARRANGE
        graph = Graph("test", GraphType.SCHEMA)
        
        # ACT & ASSERT
        assert not graph.has_node("missing")


@pytest.mark.unit
@pytest.mark.fast
class TestGraphEdgeOperations:
    """Test edge addition and referential integrity"""
    
    def test_add_edge_succeeds(self):
        """Test adding edge between existing nodes"""
        # ARRANGE
        graph = Graph("test", GraphType.SCHEMA)
        node1 = GraphNode("n1", "Node 1", NodeType.TABLE)
        node2 = GraphNode("n2", "Node 2", NodeType.TABLE)
        
        graph.add_node(node1)
        graph.add_node(node2)
        
        edge = GraphEdge("n1", "n2", EdgeType.FOREIGN_KEY)
        
        # ACT
        graph.add_edge(edge)
        
        # ASSERT
        assert len(graph.edges) == 1
        assert graph.edges[0] == edge
    
    def test_add_edge_with_missing_source_fails(self):
        """Test adding edge fails if source node missing (referential integrity)"""
        # ARRANGE
        graph = Graph("test", GraphType.SCHEMA)
        node2 = GraphNode("n2", "Node 2", NodeType.TABLE)
        graph.add_node(node2)
        
        edge = GraphEdge("missing", "n2", EdgeType.FOREIGN_KEY)
        
        # ACT & ASSERT
        with pytest.raises(ValueError, match="Source node 'missing' not found"):
            graph.add_edge(edge)
    
    def test_add_edge_with_missing_target_fails(self):
        """Test adding edge fails if target node missing (referential integrity)"""
        # ARRANGE
        graph = Graph("test", GraphType.SCHEMA)
        node1 = GraphNode("n1", "Node 1", NodeType.TABLE)
        graph.add_node(node1)
        
        edge = GraphEdge("n1", "missing", EdgeType.FOREIGN_KEY)
        
        # ACT & ASSERT
        with pytest.raises(ValueError, match="Target node 'missing' not found"):
            graph.add_edge(edge)
    
    def test_add_duplicate_edge_is_idempotent(self):
        """Test adding duplicate edge is idempotent (no error, no duplicate)"""
        # ARRANGE
        graph = Graph("test", GraphType.SCHEMA)
        node1 = GraphNode("n1", "Node 1", NodeType.TABLE)
        node2 = GraphNode("n2", "Node 2", NodeType.TABLE)
        
        graph.add_node(node1)
        graph.add_node(node2)
        
        edge1 = GraphEdge("n1", "n2", EdgeType.FOREIGN_KEY)
        edge2 = GraphEdge("n1", "n2", EdgeType.FOREIGN_KEY)  # Duplicate
        
        # ACT
        graph.add_edge(edge1)
        graph.add_edge(edge2)  # Should be ignored
        
        # ASSERT
        assert len(graph.edges) == 1  # No duplicate


@pytest.mark.unit
@pytest.mark.fast
class TestGraphSerialization:
    """Test graph serialization to dict"""
    
    def test_to_dict_returns_generic_format(self):
        """Test to_dict returns generic format (NOT vis.js specific)"""
        # ARRANGE
        graph = Graph("test", GraphType.SCHEMA)
        node = GraphNode("n1", "Test", NodeType.TABLE)
        graph.add_node(node)
        
        # ACT
        result = graph.to_dict()
        
        # ASSERT
        assert 'nodes' in result
        assert 'edges' in result
        assert len(result['nodes']) == 1
        assert result['nodes'][0]['id'] == 'n1'
        assert result['nodes'][0]['type'] == 'table'  # Generic 'type', not 'group'
    
    def test_to_dict_with_edges(self):
        """Test to_dict includes edges in generic format"""
        # ARRANGE
        graph = Graph("test", GraphType.SCHEMA)
        node1 = GraphNode("n1", "Node 1", NodeType.TABLE)
        node2 = GraphNode("n2", "Node 2", NodeType.TABLE)
        
        graph.add_node(node1)
        graph.add_node(node2)
        
        edge = GraphEdge("n1", "n2", EdgeType.FOREIGN_KEY, label="FK_Test")
        graph.add_edge(edge)
        
        # ACT
        result = graph.to_dict()
        
        # ASSERT
        assert len(result['edges']) == 1
        assert result['edges'][0]['source'] == 'n1'  # Generic 'source', not 'from'
        assert result['edges'][0]['target'] == 'n2'  # Generic 'target', not 'to'
        assert result['edges'][0]['type'] == 'fk'
        assert result['edges'][0]['label'] == 'FK_Test'


@pytest.mark.unit
@pytest.mark.fast
class TestGraphStatistics:
    """Test graph statistics generation"""
    
    def test_get_statistics_returns_counts(self):
        """Test get_statistics returns node/edge counts"""
        # ARRANGE
        graph = Graph("test", GraphType.SCHEMA)
        node1 = GraphNode("n1", "Node 1", NodeType.TABLE)
        node2 = GraphNode("n2", "Node 2", NodeType.RECORD)
        
        graph.add_node(node1)
        graph.add_node(node2)
        
        edge = GraphEdge("n1", "n2", EdgeType.CONTAINS)
        graph.add_edge(edge)
        
        # ACT
        stats = graph.get_statistics()
        
        # ASSERT
        assert stats['graph_id'] == 'test'
        assert stats['graph_type'] == 'schema'
        assert stats['node_count'] == 2
        assert stats['edge_count'] == 1
        assert stats['nodes_by_type']['table'] == 1
        assert stats['nodes_by_type']['record'] == 1
        assert stats['edges_by_type']['contains'] == 1


@pytest.mark.unit
@pytest.mark.fast
class TestGraphImmutability:
    """Test graph provides immutable views"""
    
    def test_nodes_property_returns_copy(self):
        """Test nodes property returns copy, not reference"""
        # ARRANGE
        graph = Graph("test", GraphType.SCHEMA)
        node = GraphNode("n1", "Test", NodeType.TABLE)
        graph.add_node(node)
        
        # ACT
        nodes1 = graph.nodes
        nodes2 = graph.nodes
        
        # ASSERT
        assert nodes1 is not nodes2  # Different objects
        assert nodes1 == nodes2  # Same content
    
    def test_edges_property_returns_copy(self):
        """Test edges property returns copy, not reference"""
        # ARRANGE
        graph = Graph("test", GraphType.SCHEMA)
        node1 = GraphNode("n1", "Node 1", NodeType.TABLE)
        node2 = GraphNode("n2", "Node 2", NodeType.TABLE)
        
        graph.add_node(node1)
        graph.add_node(node2)
        
        edge = GraphEdge("n1", "n2", EdgeType.FOREIGN_KEY)
        graph.add_edge(edge)
        
        # ACT
        edges1 = graph.edges
        edges2 = graph.edges
        
        # ASSERT
        assert edges1 is not edges2  # Different objects
        assert edges1 == edges2  # Same content