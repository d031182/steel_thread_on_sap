"""
Unit Tests for KnowledgeGraphFacadeV2

Tests the simplified unified interface with error handling.
"""
import pytest
from unittest.mock import Mock, MagicMock, patch
from pathlib import Path

from modules.knowledge_graph_v2.facade import KnowledgeGraphFacadeV2
from modules.knowledge_graph_v2.domain import Graph, GraphType, GraphNode, NodeType


@pytest.fixture
def mock_cache_repo():
    """Create mock cache repository"""
    return Mock()


@pytest.fixture
def mock_csn_dir(tmp_path):
    """Create mock CSN directory with sample files"""
    csn_dir = tmp_path / "csn"
    csn_dir.mkdir()
    
    # Create sample CSN file
    sample_csn = csn_dir / "Product_CSN.json"
    sample_csn.write_text('{"definitions": {}}')
    
    return csn_dir


@pytest.fixture
def facade(mock_cache_repo, mock_csn_dir):
    """Create facade with mocked dependencies"""
    with patch('modules.knowledge_graph_v2.facade.knowledge_graph_facade.CSNParser'):
        with patch('modules.knowledge_graph_v2.facade.knowledge_graph_facade.SchemaGraphBuilderService'):
            with patch('modules.knowledge_graph_v2.facade.knowledge_graph_facade.GraphCacheService'):
                return KnowledgeGraphFacadeV2(mock_cache_repo, mock_csn_dir)


@pytest.mark.unit
@pytest.mark.fast
class TestFacadeInitialization:
    """Test facade initialization"""
    
    def test_init_succeeds(self, mock_cache_repo, mock_csn_dir):
        """Test facade initializes with dependencies"""
        # ACT
        with patch('modules.knowledge_graph_v2.facade.knowledge_graph_facade.CSNParser'):
            with patch('modules.knowledge_graph_v2.facade.knowledge_graph_facade.SchemaGraphBuilderService'):
                with patch('modules.knowledge_graph_v2.facade.knowledge_graph_facade.GraphCacheService'):
                    facade = KnowledgeGraphFacadeV2(mock_cache_repo, mock_csn_dir)
        
        # ASSERT
        assert facade is not None
        assert hasattr(facade, 'cache_service')
        assert hasattr(facade, 'schema_builder')
        assert hasattr(facade, 'csn_parser')


@pytest.mark.unit
@pytest.mark.fast
class TestGetSchemaGraph:
    """Test get_schema_graph method"""
    
    def test_get_with_cache_returns_success(self, facade):
        """Test get with cache returns successful result"""
        # ARRANGE
        mock_graph = Graph('schema', GraphType.SCHEMA)
        mock_graph.add_node(GraphNode('n1', 'Product', NodeType.TABLE))
        
        facade.cache_service.get_or_rebuild_schema_graph = Mock(return_value=mock_graph)
        
        # ACT
        result = facade.get_schema_graph(use_cache=True)
        
        # ASSERT
        assert result['success'] is True
        assert 'graph' in result
        assert result['cache_used'] is True
        assert result['metadata']['node_count'] == 1
        facade.cache_service.get_or_rebuild_schema_graph.assert_called_once()
    
    def test_get_without_cache_forces_rebuild(self, facade):
        """Test get without cache forces rebuild"""
        # ARRANGE
        mock_graph = Graph('schema', GraphType.SCHEMA)
        facade.cache_service.force_rebuild_schema = Mock(return_value=mock_graph)
        
        # ACT
        result = facade.get_schema_graph(use_cache=False)
        
        # ASSERT
        assert result['success'] is True
        assert result['cache_used'] is False
        facade.cache_service.force_rebuild_schema.assert_called_once()
    
    def test_get_returns_generic_format(self, facade):
        """Test get returns generic format (NOT vis.js)"""
        # ARRANGE
        mock_graph = Graph('schema', GraphType.SCHEMA)
        node = GraphNode('n1', 'Product', NodeType.TABLE)
        mock_graph.add_node(node)
        
        facade.cache_service.get_or_rebuild_schema_graph = Mock(return_value=mock_graph)
        
        # ACT
        result = facade.get_schema_graph()
        
        # ASSERT
        assert result['success'] is True
        graph_dict = result['graph']
        
        # Verify GENERIC format (source/target, NOT from/to)
        assert 'nodes' in graph_dict
        assert 'edges' in graph_dict
        
        # Nodes have generic 'type' field (NOT 'group')
        if graph_dict['nodes']:
            assert 'type' in graph_dict['nodes'][0]
            assert 'group' not in graph_dict['nodes'][0]
    
    def test_get_handles_errors_gracefully(self, facade):
        """Test get handles exceptions and returns error result"""
        # ARRANGE
        facade.cache_service.get_or_rebuild_schema_graph = Mock(
            side_effect=Exception("Build failed!")
        )
        
        # ACT
        result = facade.get_schema_graph()
        
        # ASSERT
        assert result['success'] is False
        assert 'error' in result
        assert result['error'] == "Build failed!"
        assert result['error_type'] == "Exception"


@pytest.mark.unit
@pytest.mark.fast
class TestRebuildSchemaGraph:
    """Test rebuild_schema_graph method"""
    
    def test_rebuild_forces_cache_bypass(self, facade):
        """Test rebuild always bypasses cache"""
        # ARRANGE
        mock_graph = Graph('schema', GraphType.SCHEMA)
        facade.cache_service.force_rebuild_schema = Mock(return_value=mock_graph)
        
        # ACT
        result = facade.rebuild_schema_graph()
        
        # ASSERT
        assert result['success'] is True
        assert result['cache_used'] is False
        facade.cache_service.force_rebuild_schema.assert_called_once()
    
    def test_rebuild_returns_metadata(self, facade):
        """Test rebuild includes complete metadata"""
        # ARRANGE
        mock_graph = Graph('schema', GraphType.SCHEMA)
        mock_graph.add_node(GraphNode('n1', 'Product', NodeType.TABLE))
        facade.cache_service.force_rebuild_schema = Mock(return_value=mock_graph)
        
        # ACT
        result = facade.rebuild_schema_graph()
        
        # ASSERT
        assert 'metadata' in result
        metadata = result['metadata']
        assert metadata['graph_id'] == 'schema'
        assert metadata['graph_type'] == 'schema'  # lowercase from enum.value
        assert metadata['node_count'] == 1
        assert 'nodes_by_type' in metadata


@pytest.mark.unit
@pytest.mark.fast
class TestGetSchemaStatus:
    """Test get_schema_status method"""
    
    def test_status_when_cached(self, facade, mock_csn_dir):
        """Test status returns true when schema is cached"""
        # ARRANGE
        facade.cache_service.exists_in_cache = Mock(return_value=True)
        
        # ACT
        result = facade.get_schema_status()
        
        # ASSERT
        assert result['success'] is True
        assert result['cached'] is True
        assert result['csn_files_count'] >= 0
        assert 'csn_directory' in result
    
    def test_status_when_not_cached(self, facade):
        """Test status returns false when schema not cached"""
        # ARRANGE
        facade.cache_service.exists_in_cache = Mock(return_value=False)
        
        # ACT
        result = facade.get_schema_status()
        
        # ASSERT
        assert result['success'] is True
        assert result['cached'] is False
    
    def test_status_handles_errors(self, facade):
        """Test status handles exceptions gracefully"""
        # ARRANGE
        facade.cache_service.exists_in_cache = Mock(
            side_effect=Exception("Database error")
        )
        
        # ACT
        result = facade.get_schema_status()
        
        # ASSERT
        assert result['success'] is False
        assert 'error' in result
        assert result['error'] == "Database error"


@pytest.mark.unit
@pytest.mark.fast
class TestClearSchemaCache:
    """Test clear_schema_cache method"""
    
    def test_clear_when_cache_exists(self, facade):
        """Test clear returns true when cache exists"""
        # ARRANGE
        facade.cache_service.clear_cache = Mock(return_value=True)
        
        # ACT
        result = facade.clear_schema_cache()
        
        # ASSERT
        assert result['success'] is True
        assert result['cleared'] is True
        facade.cache_service.clear_cache.assert_called_once_with(GraphType.SCHEMA)
    
    def test_clear_when_cache_not_exists(self, facade):
        """Test clear returns false when no cache to clear"""
        # ARRANGE
        facade.cache_service.clear_cache = Mock(return_value=False)
        
        # ACT
        result = facade.clear_schema_cache()
        
        # ASSERT
        assert result['success'] is True
        assert result['cleared'] is False
    
    def test_clear_handles_errors(self, facade):
        """Test clear handles exceptions gracefully"""
        # ARRANGE
        facade.cache_service.clear_cache = Mock(
            side_effect=Exception("Delete failed")
        )
        
        # ACT
        result = facade.clear_schema_cache()
        
        # ASSERT
        assert result['success'] is False
        assert 'error' in result


@pytest.mark.unit
@pytest.mark.fast
class TestErrorHandling:
    """Test comprehensive error handling"""
    
    def test_all_methods_have_try_except(self, facade):
        """Test all public methods handle exceptions"""
        # ARRANGE
        facade.cache_service.get_or_rebuild_schema_graph = Mock(
            side_effect=Exception("Test error")
        )
        facade.cache_service.exists_in_cache = Mock(
            side_effect=Exception("Test error")
        )
        facade.cache_service.clear_cache = Mock(
            side_effect=Exception("Test error")
        )
        
        # ACT & ASSERT - None should raise exceptions
        result1 = facade.get_schema_graph()
        assert result1['success'] is False
        
        result2 = facade.get_schema_status()
        assert result2['success'] is False
        
        result3 = facade.clear_schema_cache()
        assert result3['success'] is False


@pytest.mark.unit
@pytest.mark.fast
class TestResponseFormat:
    """Test response format consistency"""
    
    def test_success_response_has_required_fields(self, facade):
        """Test successful responses have expected structure"""
        # ARRANGE
        mock_graph = Graph('schema', GraphType.SCHEMA)
        facade.cache_service.get_or_rebuild_schema_graph = Mock(return_value=mock_graph)
        
        # ACT
        result = facade.get_schema_graph()
        
        # ASSERT
        assert 'success' in result
        assert result['success'] is True
        assert 'graph' in result
        assert 'cache_used' in result
        assert 'metadata' in result
    
    def test_error_response_has_required_fields(self, facade):
        """Test error responses have expected structure"""
        # ARRANGE
        facade.cache_service.get_or_rebuild_schema_graph = Mock(
            side_effect=ValueError("Invalid input")
        )
        
        # ACT
        result = facade.get_schema_graph()
        
        # ASSERT
        assert 'success' in result
        assert result['success'] is False
        assert 'error' in result
        assert 'error_type' in result
        assert result['error_type'] == "ValueError"