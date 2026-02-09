"""
Unit tests for GraphCacheService

Tests cache save/load/clear operations to prevent basic errors like:
- Wrong column names in SQL queries
- Missing methods
- Path resolution issues
- Schema mismatches
"""

import pytest
import sqlite3
import tempfile
import os
from pathlib import Path

from modules.knowledge_graph.backend.graph_cache_service import GraphCacheService


@pytest.fixture
def temp_db():
    """Create temporary test database with schema"""
    fd, path = tempfile.mkstemp(suffix='.db')
    os.close(fd)
    
    # Create schema
    conn = sqlite3.connect(path)
    cursor = conn.cursor()
    
    cursor.execute("""
        CREATE TABLE graph_ontology (
            ontology_id INTEGER PRIMARY KEY AUTOINCREMENT,
            graph_type TEXT NOT NULL,
            description TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    cursor.execute("""
        CREATE TABLE graph_nodes (
            node_id INTEGER PRIMARY KEY AUTOINCREMENT,
            ontology_id INTEGER NOT NULL,
            node_key TEXT NOT NULL,
            node_label TEXT,
            node_type TEXT,
            properties_json TEXT,
            FOREIGN KEY (ontology_id) REFERENCES graph_ontology(ontology_id) ON DELETE CASCADE
        )
    """)
    
    cursor.execute("""
        CREATE TABLE graph_edges (
            edge_id INTEGER PRIMARY KEY AUTOINCREMENT,
            ontology_id INTEGER NOT NULL,
            from_node_key TEXT NOT NULL,
            to_node_key TEXT NOT NULL,
            edge_type TEXT,
            edge_label TEXT,
            properties_json TEXT,
            FOREIGN KEY (ontology_id) REFERENCES graph_ontology(ontology_id) ON DELETE CASCADE
        )
    """)
    
    conn.commit()
    conn.close()
    
    yield path
    
    # Cleanup
    if os.path.exists(path):
        os.unlink(path)


@pytest.fixture
def cache_service(temp_db):
    """Create GraphCacheService instance"""
    return GraphCacheService(temp_db)


@pytest.fixture
def sample_graph():
    """Sample graph data"""
    return {
        'nodes': [
            {'id': 'node1', 'label': 'Node 1', 'group': 'type1', 'size': 10},
            {'id': 'node2', 'label': 'Node 2', 'group': 'type2', 'color': 'red'}
        ],
        'edges': [
            {'from': 'node1', 'to': 'node2', 'label': 'connects', 'arrows': 'to'}
        ]
    }


class TestGraphCacheService:
    """Test GraphCacheService functionality"""
    
    def test_initialization(self, temp_db):
        """Test service initializes with database path"""
        service = GraphCacheService(temp_db)
        assert service.db_path == temp_db
    
    def test_save_graph_creates_ontology(self, cache_service, sample_graph):
        """Test saving graph creates ontology record"""
        count = cache_service.save_graph(
            nodes=sample_graph['nodes'],
            edges=sample_graph['edges'],
            graph_type='test'
        )
        
        assert count == 2  # 2 nodes saved
        
        # Verify ontology created
        conn = sqlite3.connect(cache_service.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM graph_ontology WHERE graph_type = 'test'")
        assert cursor.fetchone()[0] == 1
        conn.close()
    
    def test_save_graph_creates_nodes(self, cache_service, sample_graph):
        """Test saving graph creates node records"""
        cache_service.save_graph(
            nodes=sample_graph['nodes'],
            edges=sample_graph['edges'],
            graph_type='test'
        )
        
        # Verify nodes created
        conn = sqlite3.connect(cache_service.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM graph_nodes")
        assert cursor.fetchone()[0] == 2
        
        # Verify node data
        cursor.execute("SELECT node_key, node_label, node_type FROM graph_nodes ORDER BY node_key")
        rows = cursor.fetchall()
        assert rows[0] == ('node1', 'Node 1', 'type1')
        assert rows[1] == ('node2', 'Node 2', 'type2')
        conn.close()
    
    def test_save_graph_creates_edges(self, cache_service, sample_graph):
        """Test saving graph creates edge records"""
        cache_service.save_graph(
            nodes=sample_graph['nodes'],
            edges=sample_graph['edges'],
            graph_type='test'
        )
        
        # Verify edges created
        conn = sqlite3.connect(cache_service.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM graph_edges")
        assert cursor.fetchone()[0] == 1
        
        # Verify edge data
        cursor.execute("SELECT from_node_key, to_node_key, edge_label FROM graph_edges")
        row = cursor.fetchone()
        assert row == ('node1', 'node2', 'connects')
        conn.close()
    
    def test_save_graph_stores_properties_json(self, cache_service, sample_graph):
        """Test node/edge properties stored as JSON"""
        cache_service.save_graph(
            nodes=sample_graph['nodes'],
            edges=sample_graph['edges'],
            graph_type='test'
        )
        
        conn = sqlite3.connect(cache_service.db_path)
        cursor = conn.cursor()
        
        # Check node properties
        cursor.execute("SELECT properties_json FROM graph_nodes WHERE node_key = 'node1'")
        import json
        props = json.loads(cursor.fetchone()[0])
        assert props['size'] == 10
        
        # Check edge properties
        cursor.execute("SELECT properties_json FROM graph_edges")
        props = json.loads(cursor.fetchone()[0])
        assert props['arrows'] == 'to'
        conn.close()
    
    def test_save_graph_replaces_existing(self, cache_service, sample_graph):
        """Test saving same graph_type replaces old data"""
        # Save first time
        cache_service.save_graph(
            nodes=sample_graph['nodes'],
            edges=sample_graph['edges'],
            graph_type='test'
        )
        
        # Save again with different data
        new_nodes = [{'id': 'node3', 'label': 'Node 3', 'group': 'type3'}]
        cache_service.save_graph(
            nodes=new_nodes,
            edges=[],
            graph_type='test'
        )
        
        # Verify only new data exists
        conn = sqlite3.connect(cache_service.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM graph_nodes")
        assert cursor.fetchone()[0] == 1
        cursor.execute("SELECT node_key FROM graph_nodes")
        assert cursor.fetchone()[0] == 'node3'
        conn.close()
    
    def test_load_graph_returns_none_when_empty(self, cache_service):
        """Test load_graph returns None when no cache exists"""
        result = cache_service.load_graph('nonexistent')
        assert result is None
    
    def test_load_graph_retrieves_saved_data(self, cache_service, sample_graph):
        """Test load_graph retrieves previously saved data"""
        # Save
        cache_service.save_graph(
            nodes=sample_graph['nodes'],
            edges=sample_graph['edges'],
            graph_type='test'
        )
        
        # Load
        result = cache_service.load_graph('test')
        
        assert result is not None
        assert 'nodes' in result
        assert 'edges' in result
        assert 'cached_at' in result
        assert len(result['nodes']) == 2
        assert len(result['edges']) == 1
    
    def test_load_graph_reconstructs_node_structure(self, cache_service, sample_graph):
        """Test load_graph reconstructs vis.js node format"""
        cache_service.save_graph(
            nodes=sample_graph['nodes'],
            edges=sample_graph['edges'],
            graph_type='test'
        )
        
        result = cache_service.load_graph('test')
        node1 = [n for n in result['nodes'] if n['id'] == 'node1'][0]
        
        assert node1['id'] == 'node1'
        assert node1['label'] == 'Node 1'
        assert node1['group'] == 'type1'
        assert node1['size'] == 10  # Property restored from JSON
    
    def test_load_graph_reconstructs_edge_structure(self, cache_service, sample_graph):
        """Test load_graph reconstructs vis.js edge format"""
        cache_service.save_graph(
            nodes=sample_graph['nodes'],
            edges=sample_graph['edges'],
            graph_type='test'
        )
        
        result = cache_service.load_graph('test')
        edge = result['edges'][0]
        
        assert edge['from'] == 'node1'
        assert edge['to'] == 'node2'
        assert edge['label'] == 'connects'
        assert edge['arrows'] == 'to'  # Property restored from JSON
    
    def test_load_graph_uses_correct_column_names(self, cache_service, sample_graph):
        """
        CRITICAL TEST: Verify SQL uses 'ontology_id' not 'id'
        
        This test would have caught the "no such column: id" bug immediately.
        """
        cache_service.save_graph(
            nodes=sample_graph['nodes'],
            edges=sample_graph['edges'],
            graph_type='test'
        )
        
        # This should not raise "no such column" error
        result = cache_service.load_graph('test')
        assert result is not None
        
        # Verify the ontology_id was actually used
        conn = sqlite3.connect(cache_service.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT ontology_id FROM graph_ontology WHERE graph_type = 'test'")
        ontology_id = cursor.fetchone()[0]
        assert ontology_id is not None
        conn.close()
    
    def test_clear_cache_deletes_specific_type(self, cache_service, sample_graph):
        """Test clear_cache removes specific graph type"""
        # Save two different types
        cache_service.save_graph(
            nodes=sample_graph['nodes'],
            edges=sample_graph['edges'],
            graph_type='type1'
        )
        cache_service.save_graph(
            nodes=sample_graph['nodes'],
            edges=sample_graph['edges'],
            graph_type='type2'
        )
        
        # Clear only type1
        deleted = cache_service.clear_cache('type1')
        assert deleted == 1
        
        # Verify type1 gone, type2 remains
        assert cache_service.load_graph('type1') is None
        assert cache_service.load_graph('type2') is not None
    
    def test_clear_cache_deletes_all_types(self, cache_service, sample_graph):
        """Test clear_cache with no parameter clears all"""
        # Save two types
        cache_service.save_graph(
            nodes=sample_graph['nodes'],
            edges=sample_graph['edges'],
            graph_type='type1'
        )
        cache_service.save_graph(
            nodes=sample_graph['nodes'],
            edges=sample_graph['edges'],
            graph_type='type2'
        )
        
        # Clear all
        deleted = cache_service.clear_cache()
        assert deleted == 2
        
        # Verify both gone
        assert cache_service.load_graph('type1') is None
        assert cache_service.load_graph('type2') is None
    
    def test_cascade_delete_removes_nodes_and_edges(self, cache_service, sample_graph):
        """Test deleting ontology cascades to nodes and edges"""
        cache_service.save_graph(
            nodes=sample_graph['nodes'],
            edges=sample_graph['edges'],
            graph_type='test'
        )
        
        # Clear cache
        cache_service.clear_cache('test')
        
        # Verify CASCADE deleted nodes and edges
        conn = sqlite3.connect(cache_service.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM graph_nodes")
        assert cursor.fetchone()[0] == 0
        cursor.execute("SELECT COUNT(*) FROM graph_edges")
        assert cursor.fetchone()[0] == 0
        conn.close()
    
    def test_save_empty_graph(self, cache_service):
        """Test saving graph with no nodes/edges"""
        count = cache_service.save_graph(nodes=[], edges=[], graph_type='empty')
        assert count == 0
        
        # Should still create ontology
        result = cache_service.load_graph('empty')
        assert result is not None
        assert len(result['nodes']) == 0
        assert len(result['edges']) == 0
    
    def test_absolute_path_resolution(self):
        """Test service works with absolute paths"""
        fd, path = tempfile.mkstemp(suffix='.db')
        os.close(fd)
        
        try:
            # Use absolute path
            abs_path = os.path.abspath(path)
            service = GraphCacheService(abs_path)
            assert service.db_path == abs_path
            assert os.path.isabs(service.db_path)
        finally:
            if os.path.exists(path):
                os.unlink(path)


if __name__ == '__main__':
    pytest.main([__file__, '-v'])