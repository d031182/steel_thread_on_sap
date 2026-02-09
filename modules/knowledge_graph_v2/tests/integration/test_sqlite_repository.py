"""
Integration Tests for SqliteGraphCacheRepository

Tests repository with real SQLite database.
"""
import pytest
import os
import tempfile
from modules.knowledge_graph_v2.domain import Graph, GraphNode, GraphEdge, GraphType, NodeType, EdgeType
from modules.knowledge_graph_v2.repositories.sqlite_graph_cache_repository import (
    SqliteGraphCacheRepository,
    RepositoryError
)


@pytest.fixture
def temp_db_path():
    """Create temporary database file for testing"""
    fd, path = tempfile.mkstemp(suffix='.db')
    os.close(fd)
    yield path
    # Cleanup
    if os.path.exists(path):
        os.remove(path)


@pytest.fixture
def repository(temp_db_path):
    """Create repository with temp database"""
    return SqliteGraphCacheRepository(temp_db_path)


@pytest.fixture
def sample_graph():
    """Create sample graph for testing"""
    graph = Graph("test-schema", GraphType.SCHEMA)
    
    # Add nodes
    node1 = GraphNode("n1", "Node 1", NodeType.TABLE, {'color': 'blue'})
    node2 = GraphNode("n2", "Node 2", NodeType.TABLE, {'color': 'red'})
    graph.add_node(node1)
    graph.add_node(node2)
    
    # Add edge
    edge = GraphEdge("n1", "n2", EdgeType.FOREIGN_KEY, "fk_relationship", {'weight': 5})
    graph.add_edge(edge)
    
    return graph


@pytest.mark.integration
class TestSqliteRepositorySaveAndGet:
    """Test save and retrieve with real database"""
    
    def test_save_and_get_succeeds(self, repository, sample_graph):
        """Test saving and retrieving graph from SQLite"""
        # ACT
        repository.save(sample_graph)
        result = repository.get("test-schema", GraphType.SCHEMA)
        
        # ASSERT
        assert result is not None
        assert result.id == "test-schema"
        assert result.type == GraphType.SCHEMA
        assert len(result.nodes) == 2
        assert len(result.edges) == 1
        
        # Verify node details
        node1 = next(n for n in result.nodes if n.id == "n1")
        assert node1.label == "Node 1"
        assert node1.type == NodeType.TABLE
        assert node1.properties['color'] == 'blue'
        
        # Verify edge details
        edge = result.edges[0]
        assert edge.source_id == "n1"
        assert edge.target_id == "n2"
        assert edge.type == EdgeType.FOREIGN_KEY
        assert edge.label == "fk_relationship"
        assert edge.properties['weight'] == 5
    
    def test_get_nonexistent_returns_none(self, repository):
        """Test retrieving non-existent graph returns None"""
        # ACT
        result = repository.get("missing", GraphType.SCHEMA)
        
        # ASSERT
        assert result is None
    
    def test_save_overwrites_existing(self, repository, sample_graph):
        """Test saving same graph type overwrites"""
        # ARRANGE
        repository.save(sample_graph)
        
        # Create modified graph
        modified_graph = Graph("modified", GraphType.SCHEMA)
        node1 = GraphNode("n1", "Modified Node", NodeType.TABLE)
        node2 = GraphNode("n2", "Another Node", NodeType.TABLE)
        node3 = GraphNode("n3", "Third Node", NodeType.TABLE)
        modified_graph.add_node(node1)
        modified_graph.add_node(node2)
        modified_graph.add_node(node3)
        
        # ACT
        repository.save(modified_graph)
        result = repository.get("modified", GraphType.SCHEMA)
        
        # ASSERT
        assert len(result.nodes) == 3  # Overwritten


@pytest.mark.integration
class TestSqliteRepositoryPersistence:
    """Test data persists across repository instances"""
    
    def test_data_persists_across_instances(self, temp_db_path, sample_graph):
        """Test saved data survives repository close/reopen"""
        # ARRANGE - Save with first instance
        repo1 = SqliteGraphCacheRepository(temp_db_path)
        repo1.save(sample_graph)
        del repo1  # Close connection
        
        # ACT - Load with new instance
        repo2 = SqliteGraphCacheRepository(temp_db_path)
        result = repo2.get("test-schema", GraphType.SCHEMA)
        
        # ASSERT
        assert result is not None
        assert len(result.nodes) == 2
        assert len(result.edges) == 1


@pytest.mark.integration
class TestSqliteRepositoryExists:
    """Test existence checking with database"""
    
    def test_exists_returns_true_when_cached(self, repository, sample_graph):
        """Test exists returns True for saved graph"""
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


@pytest.mark.integration
class TestSqliteRepositoryDelete:
    """Test deletion with database"""
    
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
    
    def test_delete_cascade_removes_nodes_and_edges(self, repository, sample_graph, temp_db_path):
        """Test delete removes nodes and edges via CASCADE"""
        # ARRANGE
        repository.save(sample_graph)
        
        # ACT
        repository.delete("test-schema", GraphType.SCHEMA)
        
        # ASSERT - Verify data actually deleted from database
        import sqlite3
        conn = sqlite3.connect(temp_db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM graph_nodes")
        node_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM graph_edges")
        edge_count = cursor.fetchone()[0]
        
        conn.close()
        
        assert node_count == 0
        assert edge_count == 0


@pytest.mark.integration
class TestSqliteRepositoryClearAll:
    """Test clearing all cached graphs"""
    
    def test_clear_all_returns_count(self, repository):
        """Test clear_all returns number of graphs deleted"""
        # ARRANGE
        graph1 = Graph("graph1", GraphType.SCHEMA)
        graph2 = Graph("graph2", GraphType.DATA)
        node = GraphNode("n1", "Node", NodeType.TABLE)
        graph1.add_node(node)
        graph2.add_node(node)
        
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


@pytest.mark.integration
class TestSqliteRepositoryMultipleGraphTypes:
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