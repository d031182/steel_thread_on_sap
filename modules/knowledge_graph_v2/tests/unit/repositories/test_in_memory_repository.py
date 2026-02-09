"""
Unit Tests for InMemoryGraphCacheRepository

Tests repository operations without database (fast unit tests).
"""
import pytest
from modules.knowledge_graph_v2.domain import Graph, GraphNode, GraphType, NodeType
from modules.knowledge_graph_v2.repositories.in_memory_graph_cache_repository import (
    InMemoryGraphCacheRepository
)


@pytest.fixture
def repository():
    """Create fresh in-memory repository for each test"""
    return InMemoryGraphCacheRepository()


@pytest.fixture
def sample_graph():
    """Create sample graph for testing"""
    graph = Graph("test-schema", GraphType.SCHEMA)
    node = GraphNode("n1", "Test Node", NodeType.TABLE)
    graph.add_node(node)
    return graph


@pytest.mark.unit
@pytest.mark.fast
class TestRepositorySaveAndGet:
    """Test save and retrieve operations"""
    
    def test_save_and_get_succeeds(self, repository, sample_graph):
        """Test saving and retrieving graph"""
        # ACT
        repository.save(sample_graph)
        result = repository.get("test-schema", GraphType.SCHEMA)
        
        # ASSERT
        assert result is not None
        assert result.id == "test-schema"
        assert result.type == GraphType.SCHEMA
        assert len(result.nodes) == 1
    
    def test_get_nonexistent_returns_none(self, repository):
        """Test retrieving non-existent graph returns None"""
        # ACT
        result = repository.get("missing", GraphType.SCHEMA)
        
        # ASSERT
        assert result is None
    
    def test_save_overwrites_existing(self, repository, sample_graph):
        """Test saving same graph ID overwrites"""
        # ARRANGE
        repository.save(sample_graph)
        
        # Create modified graph with same ID
        modified_graph = Graph("test-schema", GraphType.SCHEMA)
        node1 = GraphNode("n1", "Node 1", NodeType.TABLE)
        node2 = GraphNode("n2", "Node 2", NodeType.TABLE)
        modified_graph.add_node(node1)
        modified_graph.add_node(node2)
        
        # ACT
        repository.save(modified_graph)
        result = repository.get("test-schema", GraphType.SCHEMA)
        
        # ASSERT
        assert len(result.nodes) == 2  # Overwritten with 2 nodes


@pytest.mark.unit
@pytest.mark.fast
class TestRepositoryExists:
    """Test existence checking"""
    
    def test_exists_returns_true_when_cached(self, repository, sample_graph):
        """Test exists returns True for cached graph"""
        # ARRANGE
        repository.save(sample_graph)
        
        # ACT
        result = repository.exists("test-schema", GraphType.SCHEMA)
        
        # ASSERT
        assert result is True
    
    def test_exists_returns_false_when_not_cached(self, repository):
        """Test exists returns False for non-existent graph"""
        # ACT
        result = repository.exists("missing", GraphType.SCHEMA)
        
        # ASSERT
        assert result is False
    
    def test_exists_distinguishes_graph_types(self, repository, sample_graph):
        """Test exists distinguishes between graph types"""
        # ARRANGE
        repository.save(sample_graph)  # SCHEMA type
        
        # ACT & ASSERT
        assert repository.exists("test-schema", GraphType.SCHEMA) is True
        assert repository.exists("test-schema", GraphType.DATA) is False  # Different type


@pytest.mark.unit
@pytest.mark.fast
class TestRepositoryDelete:
    """Test deletion operations"""
    
    def test_delete_existing_returns_true(self, repository, sample_graph):
        """Test deleting existing graph returns True"""
        # ARRANGE
        repository.save(sample_graph)
        
        # ACT
        result = repository.delete("test-schema", GraphType.SCHEMA)
        
        # ASSERT
        assert result is True
        assert repository.exists("test-schema", GraphType.SCHEMA) is False
    
    def test_delete_nonexistent_returns_false(self, repository):
        """Test deleting non-existent graph returns False"""
        # ACT
        result = repository.delete("missing", GraphType.SCHEMA)
        
        # ASSERT
        assert result is False
    
    def test_delete_removes_from_cache(self, repository, sample_graph):
        """Test delete removes graph from cache"""
        # ARRANGE
        repository.save(sample_graph)
        
        # ACT
        repository.delete("test-schema", GraphType.SCHEMA)
        result = repository.get("test-schema", GraphType.SCHEMA)
        
        # ASSERT
        assert result is None


@pytest.mark.unit
@pytest.mark.fast
class TestRepositoryClearAll:
    """Test clearing all cached graphs"""
    
    def test_clear_all_returns_count(self, repository):
        """Test clear_all returns number of graphs deleted"""
        # ARRANGE
        graph1 = Graph("graph1", GraphType.SCHEMA)
        graph2 = Graph("graph2", GraphType.DATA)
        repository.save(graph1)
        repository.save(graph2)
        
        # ACT
        count = repository.clear_all()
        
        # ASSERT
        assert count == 2
    
    def test_clear_all_removes_all_graphs(self, repository, sample_graph):
        """Test clear_all removes all cached graphs"""
        # ARRANGE
        repository.save(sample_graph)
        
        # ACT
        repository.clear_all()
        
        # ASSERT
        assert repository.exists("test-schema", GraphType.SCHEMA) is False
        assert repository.get("test-schema", GraphType.SCHEMA) is None
    
    def test_clear_all_on_empty_returns_zero(self, repository):
        """Test clear_all on empty repository returns 0"""
        # ACT
        count = repository.clear_all()
        
        # ASSERT
        assert count == 0


@pytest.mark.unit
@pytest.mark.fast
class TestRepositoryMultipleGraphTypes:
    """Test repository with multiple graph types"""
    
    def test_stores_different_graph_types_separately(self, repository):
        """Test different graph types stored separately"""
        # ARRANGE
        schema_graph = Graph("test", GraphType.SCHEMA)
        data_graph = Graph("test", GraphType.DATA)
        
        node1 = GraphNode("n1", "Schema Node", NodeType.TABLE)
        node2 = GraphNode("n2", "Data Node", NodeType.RECORD)
        
        schema_graph.add_node(node1)
        data_graph.add_node(node2)
        
        # ACT
        repository.save(schema_graph)
        repository.save(data_graph)
        
        # ASSERT
        schema_result = repository.get("test", GraphType.SCHEMA)
        data_result = repository.get("test", GraphType.DATA)
        
        assert schema_result.nodes[0].type == NodeType.TABLE
        assert data_result.nodes[0].type == NodeType.RECORD