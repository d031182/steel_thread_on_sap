"""
Unit Tests for KnowledgeGraphFacade Cache Integration

Tests the complete cache workflow:
- Facade → GraphCacheService → SQLite Database
- Cache save and load operations
- Cache persistence across facade instances

@author P2P Development Team
@version 1.0.0
"""

import pytest
import os
import tempfile
from unittest.mock import Mock, MagicMock
from modules.knowledge_graph.backend.knowledge_graph_facade import KnowledgeGraphFacade


@pytest.fixture
def temp_cache_db():
    """Create temporary cache database for testing"""
    # Create temp file
    fd, path = tempfile.mkstemp(suffix='.db')
    os.close(fd)
    
    yield path
    
    # Cleanup
    if os.path.exists(path):
        os.remove(path)


@pytest.fixture
def mock_data_source(temp_cache_db):
    """Mock data source with SQLite connection info"""
    data_source = Mock()
    data_source.get_connection_info.return_value = {
        'type': 'sqlite',
        'db_path': temp_cache_db  # This is the DATA db path (not used for cache)
    }
    data_source.get_data_products.return_value = [
        {'schemaName': 'TestSchema', 'dataProductName': 'TestProduct'}
    ]
    return data_source


class TestFacadeCacheIntegration:
    """Test cache integration with facade"""
    
    def test_facade_uses_separate_cache_database(self, mock_data_source, temp_cache_db):
        """
        CRITICAL TEST: Verify facade uses separate cache database
        
        This test catches the bug we just fixed:
        - Data DB: database/p2p_data.db (or temp file)
        - Cache DB: modules/knowledge_graph/database/graph_cache.db (SEPARATE)
        """
        facade = KnowledgeGraphFacade(mock_data_source)
        
        # Facade should create cache with ABSOLUTE path to graph_cache.db
        assert facade.graph_cache_strategy is not None
        
        # Cache should NOT be using the data database path
        cache_db_path = facade.graph_cache_strategy.db_path
        assert 'graph_cache.db' in cache_db_path
        assert cache_db_path != temp_cache_db  # Different from data DB!
    
    def test_cache_save_and_load_workflow(self, mock_data_source):
        """Test complete save → load workflow"""
        facade = KnowledgeGraphFacade(mock_data_source)
        
        # Sample graph data
        test_nodes = [
            {'id': 'node1', 'label': 'Test Node 1', 'group': 'TestType'},
            {'id': 'node2', 'label': 'Test Node 2', 'group': 'TestType'}
        ]
        test_edges = [
            {'from': 'node1', 'to': 'node2', 'label': 'connects'}
        ]
        
        # Save to cache (use valid graph_type)
        cache = facade.graph_cache_strategy
        success = cache.save_graph(
            nodes=test_nodes,
            edges=test_edges,
            graph_type='schema',  # Must be 'schema', 'data', or 'csn'
            description='Test graph'
        )
        
        assert success is True
        
        # Load from cache
        result = cache.load_graph('schema')
        
        assert result is not None
        assert len(result['nodes']) == 2
        assert len(result['edges']) == 1
        assert result['nodes'][0]['id'] == 'node1'
        assert result['edges'][0]['from'] == 'node1'
    
    def test_cache_persists_across_facade_instances(self, mock_data_source):
        """
        CRITICAL TEST: Cache should survive facade recreation
        
        This catches the bug where cache was being wiped between requests.
        """
        # Create facade and save data
        facade1 = KnowledgeGraphFacade(mock_data_source)
        test_nodes = [{'id': 'persistent', 'label': 'Test', 'group': 'Type'}]
        test_edges = []
        
        facade1.graph_cache_strategy.save_graph(
            nodes=test_nodes,
            edges=test_edges,
            graph_type='data'  # Use valid graph_type
        )
        
        # Destroy facade1 (simulate end of request)
        del facade1
        
        # Create NEW facade instance (simulate new request)
        facade2 = KnowledgeGraphFacade(mock_data_source)
        
        # Load should still work!
        result = facade2.graph_cache_strategy.load_graph('data')
        
        assert result is not None
        assert len(result['nodes']) == 1
        assert result['nodes'][0]['id'] == 'persistent'
    
    def test_cache_handles_empty_graph(self, mock_data_source):
        """Test cache handles empty graphs gracefully"""
        facade = KnowledgeGraphFacade(mock_data_source)
        cache = facade.graph_cache_strategy
        
        # Save empty graph
        success = cache.save_graph(
            nodes=[],
            edges=[],
            graph_type='csn'  # Use valid graph_type
        )
        
        assert success is True
        
        # Load should return empty lists
        result = cache.load_graph('csn')
        assert result is not None
        assert result['nodes'] == []
        assert result['edges'] == []
    
    def test_cache_overwrites_existing_graph_type(self, mock_data_source):
        """
        CRITICAL TEST: Verify cache overwrites old data for same graph_type
        
        This is the "delete old ontology" logic we fixed.
        """
        facade = KnowledgeGraphFacade(mock_data_source)
        cache = facade.graph_cache_strategy
        
        # Save initial data
        cache.save_graph(
            nodes=[{'id': 'old', 'label': 'Old Node', 'group': 'Type'}],
            edges=[],
            graph_type='schema'
        )
        
        # Save NEW data with SAME graph_type
        cache.save_graph(
            nodes=[{'id': 'new', 'label': 'New Node', 'group': 'Type'}],
            edges=[],
            graph_type='schema'
        )
        
        # Load should return NEW data only (old deleted)
        result = cache.load_graph('schema')
        assert len(result['nodes']) == 1
        assert result['nodes'][0]['id'] == 'new'
    
    def test_cache_isolates_different_graph_types(self, mock_data_source):
        """Test different graph_types don't interfere"""
        facade = KnowledgeGraphFacade(mock_data_source)
        cache = facade.graph_cache_strategy
        
        # Save schema graph
        cache.save_graph(
            nodes=[{'id': 'schema1', 'label': 'Schema', 'group': 'Table'}],
            edges=[],
            graph_type='schema'
        )
        
        # Save data graph
        cache.save_graph(
            nodes=[{'id': 'data1', 'label': 'Data', 'group': 'Record'}],
            edges=[],
            graph_type='data'
        )
        
        # Load schema - should get ONLY schema nodes
        schema_result = cache.load_graph('schema')
        assert len(schema_result['nodes']) == 1
        assert schema_result['nodes'][0]['id'] == 'schema1'
        
        # Load data - should get ONLY data nodes
        data_result = cache.load_graph('data')
        assert len(data_result['nodes']) == 1
        assert data_result['nodes'][0]['id'] == 'data1'
    
    def test_cache_returns_none_for_missing_graph_type(self, mock_data_source):
        """Test cache returns None for non-existent graph"""
        facade = KnowledgeGraphFacade(mock_data_source)
        cache = facade.graph_cache_strategy
        
        result = cache.load_graph('nonexistent_type')
        assert result is None
    
    def test_hana_data_source_has_no_cache(self):
        """Test HANA data source doesn't get cache (SQLite only)"""
        hana_source = Mock()
        hana_source.get_connection_info.return_value = {
            'type': 'hana',
            'host': 'hana.example.com'
        }
        
        facade = KnowledgeGraphFacade(hana_source)
        
        # Cache should be None for HANA
        assert facade.graph_cache_strategy is None


class TestFacadeGetGraph:
    """Test facade's get_graph() method with caching"""
    
    def test_get_graph_saves_to_cache_after_build(self, mock_data_source, monkeypatch):
        """Test get_graph() saves result to cache"""
        facade = KnowledgeGraphFacade(mock_data_source)
        
        # Mock the builder to return test data
        def mock_build_schema_graph(self):
            return {
                'success': True,
                'nodes': [{'id': 'test', 'label': 'Test', 'group': 'Type'}],
                'edges': [],
                'stats': {'node_count': 1, 'edge_count': 0}
            }
        
        from modules.knowledge_graph.backend import schema_graph_builder
        monkeypatch.setattr(
            schema_graph_builder.SchemaGraphBuilder,
            'build_schema_graph',
            mock_build_schema_graph
        )
        
        # Build graph (should save to cache)
        result = facade.get_graph(mode='schema', use_cache=True)
        
        assert result['success'] is True
        
        # Verify it was saved to cache
        cached = facade.graph_cache_strategy.load_graph('schema')
        assert cached is not None
        assert len(cached['nodes']) == 1
    
    def test_get_graph_loads_from_cache_on_second_call(self, mock_data_source, monkeypatch):
        """
        CRITICAL TEST: Second call should load from cache, not rebuild
        
        This is the main performance benefit we're testing.
        """
        facade = KnowledgeGraphFacade(mock_data_source)
        
        # Track how many times builder is called
        build_count = {'count': 0}
        
        def mock_build_schema_graph(self):
            build_count['count'] += 1
            return {
                'success': True,
                'nodes': [{'id': f'node{build_count["count"]}', 'label': 'Test', 'group': 'Type'}],
                'edges': [],
                'stats': {'node_count': 1, 'edge_count': 0}
            }
        
        from modules.knowledge_graph.backend import schema_graph_builder
        monkeypatch.setattr(
            schema_graph_builder.SchemaGraphBuilder,
            'build_schema_graph',
            mock_build_schema_graph
        )
        
        # First call - builds and caches
        result1 = facade.get_graph(mode='schema', use_cache=True)
        assert build_count['count'] == 1
        assert result1['nodes'][0]['id'] == 'node1'
        
        # Second call - should load from cache (no rebuild!)
        result2 = facade.get_graph(mode='schema', use_cache=True)
        assert build_count['count'] == 1  # Still 1! No second build!
        assert result2['nodes'][0]['id'] == 'node1'  # Same data


@pytest.mark.fast
class TestCacheServiceDirectly:
    """Direct tests of GraphCacheService (no facade)"""
    
    def test_cache_service_initializes_schema(self, temp_cache_db):
        """Test cache service creates tables on first use"""
        from modules.knowledge_graph.backend.graph_cache_service import GraphCacheService
        
        cache = GraphCacheService(temp_cache_db)
        
        # Save should work (creates tables automatically)
        success = cache.save_graph(
            nodes=[{'id': 'test', 'label': 'Test', 'group': 'Type'}],
            edges=[],
            graph_type='schema'
        )
        
        assert success is True
        
        # Verify tables were created
        import sqlite3
        conn = sqlite3.connect(temp_cache_db)
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]
        conn.close()
        
        assert 'graph_ontology' in tables
        assert 'graph_nodes' in tables
        assert 'graph_edges' in tables
    
    def test_cache_service_handles_properties_json(self, temp_cache_db):
        """Test cache correctly stores/loads properties as JSON"""
        from modules.knowledge_graph.backend.graph_cache_service import GraphCacheService
        
        cache = GraphCacheService(temp_cache_db)
        
        # Save node with custom properties
        nodes = [{
            'id': 'complex',
            'label': 'Complex Node',
            'group': 'Type',
            'custom_prop': 'value',
            'nested': {'key': 'value'}
        }]
        
        cache.save_graph(nodes=nodes, edges=[], graph_type='data')
        
        # Load and verify properties preserved
        result = cache.load_graph('data')
        assert result['nodes'][0]['custom_prop'] == 'value'
        assert result['nodes'][0]['nested'] == {'key': 'value'}


if __name__ == '__main__':
    pytest.main([__file__, '-v'])