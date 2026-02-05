"""
Unit tests for KnowledgeGraphFacade.get_graph() method
Testing graph retrieval functionality with Gu Wu framework standards
"""
# Fix pytest import on Windows - add project root to sys.path BEFORE imports
import sys
from pathlib import Path
project_root = Path(__file__).parent.parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

import pytest
from unittest.mock import Mock, patch
from modules.knowledge_graph.backend.knowledge_graph_facade import KnowledgeGraphFacade


@pytest.fixture
def mock_data_source():
    """Create mock data source for KnowledgeGraphFacade"""
    data_source = Mock()
    data_source.get_connection_info.return_value = {
        'type': 'sqlite',
        'db_path': 'test.db'
    }
    return data_source


@pytest.fixture
def facade(mock_data_source):
    """Create KnowledgeGraphFacade instance with mocked data source"""
    return KnowledgeGraphFacade(mock_data_source)


@pytest.fixture
def sample_graph_data():
    """Sample graph data structure for testing"""
    return {
        'success': True,
        'nodes': [
            {'id': 'node1', 'label': 'Customer'},
            {'id': 'node2', 'label': 'PurchaseOrder'}
        ],
        'edges': [
            {'from': 'node1', 'to': 'node2', 'label': 'PLACED'}
        ],
        'stats': {'node_count': 2, 'edge_count': 1}
    }


# ============================================================================
# BASIC FUNCTIONALITY TESTS
# ============================================================================

@pytest.mark.unit
@pytest.mark.fast
def test_get_graph_csn_mode_success(facade, sample_graph_data):
    """Test get_graph() successfully retrieves CSN schema graph"""
    # ARRANGE
    mode = 'csn'
    mock_builder = Mock()
    mock_builder.build_schema_graph.return_value = sample_graph_data
    
    with patch('modules.knowledge_graph.backend.knowledge_graph_facade.GraphBuilderFactory.create_builder', return_value=mock_builder):
        # ACT
        result = facade.get_graph(mode=mode, use_cache=False)
        
        # ASSERT
        assert result == sample_graph_data
        mock_builder.build_schema_graph.assert_called_once()


@pytest.mark.unit
@pytest.mark.fast
def test_get_graph_data_mode_success(facade, sample_graph_data):
    """Test get_graph() successfully retrieves data graph"""
    # ARRANGE
    mode = 'data'
    mock_builder = Mock()
    mock_builder.build_data_graph.return_value = sample_graph_data
    
    with patch('modules.knowledge_graph.backend.knowledge_graph_facade.GraphBuilderFactory.create_builder', return_value=mock_builder):
        # ACT
        result = facade.get_graph(mode=mode, use_cache=False)
        
        # ASSERT
        assert result == sample_graph_data
        mock_builder.build_data_graph.assert_called_once()


@pytest.mark.unit
@pytest.mark.fast
def test_get_graph_schema_mode_success(facade, sample_graph_data):
    """Test get_graph() successfully retrieves schema graph"""
    # ARRANGE
    mode = 'schema'
    mock_builder = Mock()
    mock_builder.build_schema_graph.return_value = sample_graph_data
    
    with patch('modules.knowledge_graph.backend.knowledge_graph_facade.GraphBuilderFactory.create_builder', return_value=mock_builder):
        # ACT
        result = facade.get_graph(mode=mode, use_cache=False)
        
        # ASSERT
        assert result == sample_graph_data
        mock_builder.build_schema_graph.assert_called_once()


# ============================================================================
# ERROR HANDLING TESTS
# ============================================================================

@pytest.mark.unit
@pytest.mark.fast
def test_get_graph_handles_builder_exception(facade):
    """Test get_graph() gracefully handles exceptions from builder"""
    # ARRANGE
    mode = 'csn'
    error_message = "Database connection failed"
    mock_builder = Mock()
    mock_builder.build_schema_graph.side_effect = Exception(error_message)
    
    with patch('modules.knowledge_graph.backend.knowledge_graph_facade.GraphBuilderFactory.create_builder', return_value=mock_builder):
        # ACT
        result = facade.get_graph(mode=mode, use_cache=False)
        
        # ASSERT
        assert result['success'] is False
        assert 'error' in result
        assert error_message in result['error']['message']


@pytest.mark.unit
@pytest.mark.fast
def test_get_graph_handles_empty_result(facade):
    """Test get_graph() handles empty graph response"""
    # ARRANGE
    mode = 'data'
    empty_graph = {
        'success': True,
        'nodes': [],
        'edges': [],
        'stats': {'node_count': 0, 'edge_count': 0}
    }
    mock_builder = Mock()
    mock_builder.build_data_graph.return_value = empty_graph
    
    with patch('modules.knowledge_graph.backend.knowledge_graph_facade.GraphBuilderFactory.create_builder', return_value=mock_builder):
        # ACT
        result = facade.get_graph(mode=mode, use_cache=False)
        
        # ASSERT
        assert result == empty_graph
        assert len(result['nodes']) == 0
        assert len(result['edges']) == 0


@pytest.mark.unit
@pytest.mark.fast
def test_get_graph_invalid_mode_handling(facade):
    """Test get_graph() handles invalid mode parameter"""
    # ARRANGE
    invalid_mode = 'invalid_mode'
    
    with patch('modules.knowledge_graph.backend.knowledge_graph_facade.GraphBuilderFactory.create_builder', side_effect=ValueError(f"Invalid mode '{invalid_mode}'")):
        # ACT
        result = facade.get_graph(mode=invalid_mode, use_cache=False)
        
        # ASSERT
        assert result['success'] is False
        assert 'error' in result
        assert 'invalid_mode' in result['error']['message'].lower()


# ============================================================================
# CACHING BEHAVIOR TESTS
# ============================================================================

@pytest.mark.unit
@pytest.mark.fast
def test_get_graph_uses_cache_when_enabled(facade, sample_graph_data):
    """Test get_graph() attempts to use cache when use_cache=True"""
    # ARRANGE
    mode = 'schema'
    facade._cache_service = Mock()
    facade._cache_service.get_visjs_graph.return_value = {
        'stats': {'cache_exists': True},
        'nodes': sample_graph_data['nodes'],
        'edges': sample_graph_data['edges']
    }
    
    # ACT
    result = facade.get_graph(mode=mode, use_cache=True)
    
    # ASSERT
    facade._cache_service.get_visjs_graph.assert_called_once_with(mode)
    assert result['stats']['cache_exists'] is True


@pytest.mark.unit
@pytest.mark.fast
def test_get_graph_builds_when_cache_miss(facade, sample_graph_data):
    """Test get_graph() builds graph when cache miss occurs"""
    # ARRANGE
    mode = 'schema'
    facade._cache_service = Mock()
    facade._cache_service.get_visjs_graph.return_value = {
        'stats': {'cache_exists': False}
    }
    
    mock_builder = Mock()
    mock_builder.build_schema_graph.return_value = sample_graph_data
    
    with patch('modules.knowledge_graph.backend.knowledge_graph_facade.GraphBuilderFactory.create_builder', return_value=mock_builder):
        # ACT
        result = facade.get_graph(mode=mode, use_cache=True)
        
        # ASSERT
        facade._cache_service.get_visjs_graph.assert_called_once()
        mock_builder.build_schema_graph.assert_called_once()
        assert result == sample_graph_data


# ============================================================================
# PARAMETER TESTS
# ============================================================================

@pytest.mark.unit
@pytest.mark.fast
def test_get_graph_with_max_records_parameter(facade, sample_graph_data):
    """Test get_graph() respects max_records parameter for data mode"""
    # ARRANGE
    mode = 'data'
    max_records = 100
    mock_builder = Mock()
    mock_builder.build_data_graph.return_value = sample_graph_data
    
    with patch('modules.knowledge_graph.backend.knowledge_graph_facade.GraphBuilderFactory.create_builder', return_value=mock_builder):
        # ACT
        result = facade.get_graph(mode=mode, use_cache=False, max_records=max_records)
        
        # ASSERT
        assert result == sample_graph_data
        call_args = mock_builder.build_data_graph.call_args
        assert call_args[1]['max_records_per_table'] == max_records


@pytest.mark.unit
@pytest.mark.fast
def test_get_graph_with_filter_orphans_parameter(facade, sample_graph_data):
    """Test get_graph() respects filter_orphans parameter"""
    # ARRANGE
    mode = 'data'
    filter_orphans = False
    mock_builder = Mock()
    mock_builder.build_data_graph.return_value = sample_graph_data
    
    with patch('modules.knowledge_graph.backend.knowledge_graph_facade.GraphBuilderFactory.create_builder', return_value=mock_builder):
        # ACT
        result = facade.get_graph(mode=mode, use_cache=False, filter_orphans=filter_orphans)
        
        # ASSERT
        assert result == sample_graph_data
        call_args = mock_builder.build_data_graph.call_args
        assert call_args[1]['filter_orphans'] == filter_orphans


# ============================================================================
# PERFORMANCE TESTS
# ============================================================================

@pytest.mark.unit
@pytest.mark.fast
def test_get_graph_large_result_set(facade):
    """Test get_graph() handles large graph result sets"""
    # ARRANGE
    mode = 'data'
    large_graph = {
        'success': True,
        'nodes': [{'id': f'node{i}', 'label': 'Customer'} for i in range(1000)],
        'edges': [{'from': f'node{i}', 'to': f'node{i+1}', 'label': 'REL'} for i in range(999)],
        'stats': {'node_count': 1000, 'edge_count': 999}
    }
    mock_builder = Mock()
    mock_builder.build_data_graph.return_value = large_graph
    
    with patch('modules.knowledge_graph.backend.knowledge_graph_facade.GraphBuilderFactory.create_builder', return_value=mock_builder):
        # ACT
        result = facade.get_graph(mode=mode, use_cache=False)
        
        # ASSERT
        assert len(result['nodes']) == 1000
        assert len(result['edges']) == 999