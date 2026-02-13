"""
Integration Tests for Knowledge Graph v2 API

Tests Flask endpoints with real Flask test client.
"""
import pytest
from flask import Flask
from pathlib import Path
from unittest.mock import Mock, patch

from modules.knowledge_graph_v2.backend import blueprint
from modules.knowledge_graph_v2.domain import Graph, GraphType, GraphNode, NodeType


@pytest.fixture
def app():
    """Create Flask app for testing"""
    app = Flask(__name__)
    app.register_blueprint(blueprint)
    app.config['TESTING'] = True
    return app


@pytest.fixture
def client(app):
    """Create Flask test client"""
    return app.test_client()


@pytest.fixture
def mock_facade():
    """Create mock facade for testing"""
    with patch('modules.knowledge_graph_v2.backend.api.get_facade') as mock_get_facade:
        mock_facade_instance = Mock()
        mock_get_facade.return_value = mock_facade_instance
        yield mock_facade_instance


@pytest.mark.integration
class TestHealthEndpoint:
    """Test health check endpoint"""
    
    def test_health_returns_200(self, client):
        """Test health endpoint returns 200"""
        # ACT
        response = client.get('/api/knowledge-graph/health')
        
        # ASSERT
        assert response.status_code == 200
        data = response.get_json()
        assert data['status'] == 'healthy'
        assert data['version'] == '2.0'
        assert data['api'] == 'knowledge-graph-v2'


@pytest.mark.integration
class TestGetSchemaGraphEndpoint:
    """Test GET /schema endpoint"""
    
    def test_get_with_cache_success(self, client, mock_facade):
        """Test GET /schema with cache returns 200"""
        # ARRANGE
        mock_graph = Graph('schema', GraphType.SCHEMA)
        mock_graph.add_node(GraphNode('n1', 'Product', NodeType.TABLE))
        
        mock_facade.get_schema_graph.return_value = {
            'success': True,
            'graph': mock_graph.to_dict(),
            'cache_used': True,
            'metadata': {
                'node_count': 1,
                'edge_count': 0
            }
        }
        
        # ACT
        response = client.get('/api/knowledge-graph/schema')
        
        # ASSERT
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
        assert data['cache_used'] is True
        assert 'graph' in data
        mock_facade.get_schema_graph.assert_called_once_with(use_cache=True)
    
    def test_get_without_cache_forces_rebuild(self, client, mock_facade):
        """Test GET /schema?use_cache=false forces rebuild"""
        # ARRANGE
        mock_graph = Graph('schema', GraphType.SCHEMA)
        mock_facade.get_schema_graph.return_value = {
            'success': True,
            'graph': mock_graph.to_dict(),
            'cache_used': False,
            'metadata': {'node_count': 0, 'edge_count': 0}
        }
        
        # ACT
        response = client.get('/api/knowledge-graph/schema?use_cache=false')
        
        # ASSERT
        assert response.status_code == 200
        data = response.get_json()
        assert data['cache_used'] is False
        mock_facade.get_schema_graph.assert_called_once_with(use_cache=False)
    
    def test_get_handles_facade_errors(self, client, mock_facade):
        """Test GET /schema handles facade errors with 500"""
        # ARRANGE
        mock_facade.get_schema_graph.return_value = {
            'success': False,
            'error': 'Build failed',
            'error_type': 'Exception'
        }
        
        # ACT
        response = client.get('/api/knowledge-graph/schema')
        
        # ASSERT
        assert response.status_code == 500
        data = response.get_json()
        assert data['success'] is False
        assert 'error' in data
    
    def test_get_returns_generic_format(self, client, mock_facade):
        """Test GET /schema returns generic format (NOT vis.js)"""
        # ARRANGE
        mock_graph = Graph('schema', GraphType.SCHEMA)
        node = GraphNode('n1', 'Product', NodeType.TABLE)
        mock_graph.add_node(node)
        
        mock_facade.get_schema_graph.return_value = {
            'success': True,
            'graph': mock_graph.to_dict(),
            'cache_used': True,
            'metadata': {'node_count': 1, 'edge_count': 0}
        }
        
        # ACT
        response = client.get('/api/knowledge-graph/schema')
        
        # ASSERT
        assert response.status_code == 200
        data = response.get_json()
        graph = data['graph']
        
        # Verify GENERIC format (NOT vis.js)
        assert 'nodes' in graph
        assert 'edges' in graph
        if graph['nodes']:
            # Has 'type' field (generic), NOT 'group' (vis.js)
            assert 'type' in graph['nodes'][0]
            assert 'group' not in graph['nodes'][0]


@pytest.mark.integration
class TestRebuildSchemaEndpoint:
    """Test POST /schema/rebuild endpoint"""
    
    def test_rebuild_returns_200(self, client, mock_facade):
        """Test POST /schema/rebuild returns 200"""
        # ARRANGE
        mock_graph = Graph('schema', GraphType.SCHEMA)
        mock_facade.rebuild_schema_graph.return_value = {
            'success': True,
            'graph': mock_graph.to_dict(),
            'cache_used': False,
            'metadata': {'node_count': 0, 'edge_count': 0}
        }
        
        # ACT
        response = client.post('/api/knowledge-graph/schema/rebuild')
        
        # ASSERT
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
        assert data['cache_used'] is False
        mock_facade.rebuild_schema_graph.assert_called_once()
    
    def test_rebuild_handles_errors(self, client, mock_facade):
        """Test POST /schema/rebuild handles errors with 500"""
        # ARRANGE
        mock_facade.rebuild_schema_graph.return_value = {
            'success': False,
            'error': 'Rebuild failed',
            'error_type': 'Exception'
        }
        
        # ACT
        response = client.post('/api/knowledge-graph/schema/rebuild')
        
        # ASSERT
        assert response.status_code == 500
        data = response.get_json()
        assert data['success'] is False


@pytest.mark.integration
class TestStatusEndpoint:
    """Test GET /status endpoint"""
    
    def test_status_returns_200(self, client, mock_facade):
        """Test GET /status returns 200"""
        # ARRANGE
        mock_facade.get_schema_status.return_value = {
            'success': True,
            'cached': True,
            'csn_files_count': 8,
            'csn_directory': 'docs/csn'
        }
        
        # ACT
        response = client.get('/api/knowledge-graph/status')
        
        # ASSERT
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
        assert 'cached' in data
        assert 'csn_files_count' in data
        mock_facade.get_schema_status.assert_called_once()
    
    def test_status_handles_errors(self, client, mock_facade):
        """Test GET /status handles errors with 500"""
        # ARRANGE
        mock_facade.get_schema_status.return_value = {
            'success': False,
            'error': 'Database error',
            'error_type': 'Exception'
        }
        
        # ACT
        response = client.get('/api/knowledge-graph/status')
        
        # ASSERT
        assert response.status_code == 500
        data = response.get_json()
        assert data['success'] is False


@pytest.mark.integration
class TestClearCacheEndpoint:
    """Test DELETE /cache endpoint"""
    
    def test_clear_returns_200(self, client, mock_facade):
        """Test DELETE /cache returns 200"""
        # ARRANGE
        mock_facade.clear_schema_cache.return_value = {
            'success': True,
            'cleared': True
        }
        
        # ACT
        response = client.delete('/api/knowledge-graph/cache')
        
        # ASSERT
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
        assert data['cleared'] is True
        mock_facade.clear_schema_cache.assert_called_once()
    
    def test_clear_when_no_cache(self, client, mock_facade):
        """Test DELETE /cache when no cache exists"""
        # ARRANGE
        mock_facade.clear_schema_cache.return_value = {
            'success': True,
            'cleared': False
        }
        
        # ACT
        response = client.delete('/api/knowledge-graph/cache')
        
        # ASSERT
        assert response.status_code == 200
        data = response.get_json()
        assert data['cleared'] is False
    
    def test_clear_handles_errors(self, client, mock_facade):
        """Test DELETE /cache handles errors with 500"""
        # ARRANGE
        mock_facade.clear_schema_cache.return_value = {
            'success': False,
            'error': 'Delete failed',
            'error_type': 'Exception'
        }
        
        # ACT
        response = client.delete('/api/knowledge-graph/cache')
        
        # ASSERT
        assert response.status_code == 500
        data = response.get_json()
        assert data['success'] is False


@pytest.mark.integration
class TestErrorHandling:
    """Test error handling decorator"""
    
    def test_value_error_returns_400(self, client, mock_facade):
        """Test ValueError in endpoint returns 400"""
        # ARRANGE
        mock_facade.get_schema_graph.side_effect = ValueError("Invalid input")
        
        # ACT
        response = client.get('/api/knowledge-graph/schema')
        
        # ASSERT
        assert response.status_code == 400
        data = response.get_json()
        assert data['success'] is False
        assert data['error_type'] == 'ValueError'
    
    def test_generic_exception_returns_500(self, client, mock_facade):
        """Test generic Exception in endpoint returns 500"""
        # ARRANGE
        mock_facade.get_schema_graph.side_effect = RuntimeError("Unexpected error")
        
        # ACT
        response = client.get('/api/knowledge-graph/schema')
        
        # ASSERT
        assert response.status_code == 500
        data = response.get_json()
        assert data['success'] is False
        assert data['error_type'] == 'RuntimeError'


@pytest.mark.integration
class TestResponseFormat:
    """Test API response format consistency"""
    
    def test_all_success_responses_have_success_field(self, client, mock_facade):
        """Test all successful responses include 'success' field"""
        # ARRANGE
        mock_graph = Graph('schema', GraphType.SCHEMA)
        
        mock_facade.get_schema_graph.return_value = {
            'success': True,
            'graph': mock_graph.to_dict(),
            'cache_used': True,
            'metadata': {}
        }
        mock_facade.get_schema_status.return_value = {
            'success': True,
            'cached': True,
            'csn_files_count': 0,
            'csn_directory': 'docs/csn'
        }
        mock_facade.clear_schema_cache.return_value = {
            'success': True,
            'cleared': True
        }
        
        # ACT & ASSERT
        r1 = client.get('/api/knowledge-graph/schema')
        assert r1.get_json()['success'] is True
        
        r2 = client.get('/api/knowledge-graph/status')
        assert r2.get_json()['success'] is True
        
        r3 = client.delete('/api/knowledge-graph/cache')
        assert r3.get_json()['success'] is True
    
    def test_all_error_responses_have_error_fields(self, client, mock_facade):
        """Test all error responses include 'success', 'error', 'error_type'"""
        # ARRANGE
        mock_facade.get_schema_graph.return_value = {
            'success': False,
            'error': 'Test error',
            'error_type': 'Exception'
        }
        
        # ACT
        response = client.get('/api/knowledge-graph/schema')
        
        # ASSERT
        data = response.get_json()
        assert 'success' in data
        assert data['success'] is False
        assert 'error' in data
        assert 'error_type' in data