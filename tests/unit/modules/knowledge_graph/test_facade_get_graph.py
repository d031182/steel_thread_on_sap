"""
Unit Tests for KnowledgeGraphFacade.get_graph()

Tests the facade's main graph visualization method using Gu Wu standards.
Covers cache hit/miss, Strategy pattern, and error handling.

@author P2P Development Team  
@version 1.0.0
@since v3.24
"""

import pytest
from unittest.mock import Mock, MagicMock, patch
from modules.knowledge_graph.backend.knowledge_graph_facade import KnowledgeGraphFacade


@pytest.mark.unit
@pytest.mark.fast
class TestFacadeGetGraph:
    """Test suite for KnowledgeGraphFacade.get_graph()"""
    
    @pytest.fixture
    def mock_data_source(self):
        """Create mock SQLite data source"""
        # ARRANGE
        data_source = Mock()
        data_source.get_connection_info.return_value = {
            'type': 'sqlite',
            'db_path': 'test.db'
        }
        return data_source
    
    @pytest.fixture
    def mock_hana_data_source(self):
        """Create mock HANA data source"""
        # ARRANGE
        data_source = Mock()
        data_source.get_connection_info.return_value = {
            'type': 'hana',
            'host': 'test.hana.ondemand.com'
        }
        return data_source
    
    @pytest.fixture
    def facade(self, mock_data_source):
        """Create facade instance with mocked data source"""
        # ARRANGE
        return KnowledgeGraphFacade(mock_data_source)
    
    def test_get_graph_cache_hit(self, facade):
        """Test cache hit scenario - should load from cache without building"""
        # ARRANGE
        cached_data = {
            'nodes': [{'id': '1', 'label': 'Test'}],
            'edges': [{'from': '1', 'to': '2'}],
            'stats': {
                'node_count': 1,
                'edge_count': 1,
                'cache_used': True  # Facade preserves this from cache
            }
        }
        
        # Mock the underlying _cache_service attribute (property can't be mocked directly)
        mock_strategy = Mock()
        mock_strategy.load_graph.return_value = cached_data
        facade._cache_service = mock_strategy
        
        # ACT
        result = facade.get_graph(mode='schema', use_cache=True)
        
        # ASSERT
        assert result['success'] is True
        assert result['nodes'] == cached_data['nodes']
        assert result['edges'] == cached_data['edges']
        # Verify cache was used (cache_used flag preserved from cached data)
        assert result['stats']['cache_used'] is True
        assert result['stats']['node_count'] == 1
        assert result['stats']['edge_count'] == 1
        mock_strategy.load_graph.assert_called_once_with('schema')
    
    def test_get_graph_cache_miss_builds_graph(self, facade):
        """Test cache miss - should build graph from source"""
        # ARRANGE
        built_graph = {
            'success': True,
            'nodes': [{'id': 'n1'}],
            'edges': [{'from': 'n1', 'to': 'n2'}],
            'stats': {'node_count': 1, 'edge_count': 1}
        }
        
        # Mock the underlying _cache_service attribute
        mock_strategy = Mock()
        mock_strategy.load_graph.return_value = None  # Cache miss
        facade._cache_service = mock_strategy
        
        with patch('modules.knowledge_graph.backend.knowledge_graph_facade.GraphBuilderFactory') as mock_factory:
            mock_builder = Mock()
            mock_builder.build_schema_graph.return_value = built_graph
            mock_factory.create_builder.return_value = mock_builder
            
            # ACT
            result = facade.get_graph(mode='schema', use_cache=True)
        
        # ASSERT
        assert result['success'] is True
        assert result['nodes'] == built_graph['nodes']
        mock_builder.build_schema_graph.assert_called_once()
        mock_strategy.save_graph.assert_called_once()
    
    def test_get_graph_cache_disabled(self, facade):
        """Test with cache disabled - should build directly"""
        # ARRANGE
        built_graph = {
            'success': True,
            'nodes': [],
            'edges': [],
            'stats': {'node_count': 0, 'edge_count': 0}
        }
        
        with patch('modules.knowledge_graph.backend.knowledge_graph_facade.GraphBuilderFactory') as mock_factory:
            mock_builder = Mock()
            mock_builder.build_schema_graph.return_value = built_graph
            mock_factory.create_builder.return_value = mock_builder
            
            # ACT
            result = facade.get_graph(mode='schema', use_cache=False)
        
        # ASSERT
        assert result['success'] is True
        mock_builder.build_schema_graph.assert_called_once()
    
    def test_get_graph_data_mode_calls_build_data_graph(self, facade):
        """Test data mode uses correct builder method"""
        # ARRANGE
        built_graph = {
            'success': True,
            'nodes': [],
            'edges': [],
            'stats': {'node_count': 0, 'edge_count': 0}
        }
        
        with patch('modules.knowledge_graph.backend.knowledge_graph_facade.GraphBuilderFactory') as mock_factory:
            mock_builder = Mock()
            mock_builder.build_data_graph.return_value = built_graph
            mock_factory.create_builder.return_value = mock_builder
            
            # ACT
            result = facade.get_graph(
                mode='data',
                use_cache=False,
                max_records=10,
                filter_orphans=True
            )
        
        # ASSERT
        assert result['success'] is True
        mock_builder.build_data_graph.assert_called_once_with(
            max_records_per_table=10,
            filter_orphans=True,
            use_cache=False
        )
    
    def test_get_graph_hana_skips_cache(self, mock_hana_data_source):
        """Test HANA data source skips cache (SQLite only)"""
        # ARRANGE
        facade = KnowledgeGraphFacade(mock_hana_data_source)
        built_graph = {
            'success': True,
            'nodes': [],
            'edges': [],
            'stats': {'node_count': 0, 'edge_count': 0}
        }
        
        with patch('modules.knowledge_graph.backend.knowledge_graph_facade.GraphBuilderFactory') as mock_factory:
            mock_builder = Mock()
            mock_builder.build_schema_graph.return_value = built_graph
            mock_factory.create_builder.return_value = mock_builder
            
            # ACT
            result = facade.get_graph(mode='schema', use_cache=True)
        
        # ASSERT
        assert result['success'] is True
        # Should build directly without attempting cache
        mock_builder.build_schema_graph.assert_called_once()
    
    def test_get_graph_invalid_mode_raises_error(self, facade):
        """Test invalid mode raises ValueError"""
        # ARRANGE
        with patch('modules.knowledge_graph.backend.knowledge_graph_facade.GraphBuilderFactory') as mock_factory:
            mock_factory.create_builder.side_effect = ValueError("Invalid mode")
            
            # ACT
            result = facade.get_graph(mode='invalid')
        
        # ASSERT
        assert result['success'] is False
        assert result['error']['code'] == 'BUILD_ERROR'
        assert 'Invalid mode' in result['error']['message']
    
    def test_get_graph_saves_to_cache_after_build(self, facade):
        """Test successful build saves result to cache"""
        # ARRANGE
        built_graph = {
            'success': True,
            'nodes': [{'id': '1'}],
            'edges': [{'from': '1', 'to': '2'}],
            'stats': {'node_count': 1, 'edge_count': 1}
        }
        
        # Mock the underlying _cache_service attribute
        mock_strategy = Mock()
        mock_strategy.load_graph.return_value = None  # Cache miss
        mock_strategy.save_graph.return_value = True
        facade._cache_service = mock_strategy
        
        with patch('modules.knowledge_graph.backend.knowledge_graph_facade.GraphBuilderFactory') as mock_factory:
            mock_builder = Mock()
            mock_builder.build_schema_graph.return_value = built_graph
            mock_factory.create_builder.return_value = mock_builder
            
            # ACT
            result = facade.get_graph(mode='schema', use_cache=True)
        
        # ASSERT
        assert result['success'] is True
        mock_strategy.save_graph.assert_called_once_with(
            nodes=built_graph['nodes'],
            edges=built_graph['edges'],
            graph_type='schema',
            description='Schema graph'
        )
    
    def test_get_graph_handles_cache_save_failure_gracefully(self, facade):
        """Test cache save failure doesn't break graph retrieval"""
        # ARRANGE
        built_graph = {
            'success': True,
            'nodes': [{'id': '1'}],
            'edges': [{'from': '1', 'to': '2'}],
            'stats': {'node_count': 1, 'edge_count': 1}
        }
        
        # Mock the underlying _cache_service attribute
        mock_strategy = Mock()
        mock_strategy.load_graph.return_value = None
        mock_strategy.save_graph.side_effect = Exception("Cache write error")
        facade._cache_service = mock_strategy
        
        with patch('modules.knowledge_graph.backend.knowledge_graph_facade.GraphBuilderFactory') as mock_factory:
            mock_builder = Mock()
            mock_builder.build_schema_graph.return_value = built_graph
            mock_factory.create_builder.return_value = mock_builder
            
            # ACT
            result = facade.get_graph(mode='schema', use_cache=True)
        
        # ASSERT
        # Should still succeed despite cache save failure
        assert result['success'] is True
        assert result['nodes'] == built_graph['nodes']
    
    def test_get_graph_skips_cache_save_for_empty_graph(self, facade):
        """Test empty graph doesn't get saved to cache"""
        # ARRANGE
        empty_graph = {
            'success': True,
            'nodes': [],
            'edges': [],
            'stats': {'node_count': 0, 'edge_count': 0}
        }
        
        # Mock the underlying _cache_service attribute
        mock_strategy = Mock()
        mock_strategy.load_graph.return_value = None
        facade._cache_service = mock_strategy
        
        with patch('modules.knowledge_graph.backend.knowledge_graph_facade.GraphBuilderFactory') as mock_factory:
            mock_builder = Mock()
            mock_builder.build_schema_graph.return_value = empty_graph
            mock_factory.create_builder.return_value = mock_builder
            
            # ACT
            result = facade.get_graph(mode='schema', use_cache=True)
        
        # ASSERT
        assert result['success'] is True
        # Should NOT save empty graph to cache
        mock_strategy.save_graph.assert_not_called()
    
    def test_get_graph_strategy_pattern_polymorphism(self, facade):
        """Test Strategy pattern allows runtime cache selection"""
        # ARRANGE
        # This test verifies the Strategy pattern works correctly
        # by ensuring the facade uses the strategy interface, not concrete implementation
        
        # Mock the underlying _cache_service attribute
        mock_strategy = Mock()
        mock_strategy.load_graph.return_value = {
            'nodes': [],
            'edges': [],
            'stats': {}
        }
        facade._cache_service = mock_strategy
        
        # ACT
        result = facade.get_graph(mode='schema', use_cache=True)
        
        # ASSERT
        # Facade should call strategy methods, demonstrating polymorphism
        assert mock_strategy.load_graph.called
        assert result['success'] is True


@pytest.mark.unit
@pytest.mark.fast
class TestFacadeGetGraphEdgeCases:
    """Test edge cases and error scenarios"""
    
    @pytest.fixture
    def facade(self):
        """Create facade with minimal mock"""
        data_source = Mock()
        data_source.get_connection_info.return_value = {
            'type': 'sqlite',
            'db_path': 'test.db'
        }
        return KnowledgeGraphFacade(data_source)
    
    def test_get_graph_builder_exception(self, facade):
        """Test builder exception is caught and returned as error"""
        # ARRANGE
        with patch('modules.knowledge_graph.backend.knowledge_graph_facade.GraphBuilderFactory') as mock_factory:
            mock_factory.create_builder.side_effect = RuntimeError("Builder failed")
            
            # ACT
            result = facade.get_graph(mode='schema', use_cache=False)
        
        # ASSERT
        assert result['success'] is False
        assert result['error']['code'] == 'BUILD_ERROR'
        assert 'Builder failed' in result['error']['message']
    
    def test_get_graph_csn_mode_passes_db_path(self, facade):
        """Test CSN mode receives db_path for caching"""
        # ARRANGE
        built_graph = {
            'success': True,
            'nodes': [],
            'edges': [],
            'stats': {'node_count': 0, 'edge_count': 0}
        }
        
        with patch('modules.knowledge_graph.backend.knowledge_graph_facade.GraphBuilderFactory') as mock_factory:
            mock_builder = Mock()
            mock_builder.build_schema_graph.return_value = built_graph
            mock_factory.create_builder.return_value = mock_builder
            
            # ACT
            facade.get_graph(mode='csn', use_cache=False)
        
        # ASSERT
        # Verify factory was called with db_path for CSN caching
        call_kwargs = mock_factory.create_builder.call_args[1]
        assert 'db_path' in call_kwargs
        assert call_kwargs['db_path'] == 'test.db'