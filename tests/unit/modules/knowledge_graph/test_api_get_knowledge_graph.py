"""
Unit tests for get_knowledge_graph() API endpoint

Tests the main API endpoint for knowledge graph visualization.
Covers parameter validation, mode switching, error handling, and caching.

Note: Classes are imported inside get_knowledge_graph(), so patches must target
the source modules, not the api module.

@author P2P Development Team
@version 1.0.0
@date 2026-02-05
"""

import pytest
from unittest.mock import Mock, MagicMock, patch
from flask import Flask
import json


@pytest.mark.unit
@pytest.mark.fast
class TestGetKnowledgeGraphAPI:
    """Test suite for get_knowledge_graph() API endpoint"""
    
    @pytest.fixture
    def app(self):
        """Create Flask app with knowledge graph blueprint"""
        # ARRANGE
        from modules.knowledge_graph.backend.api import knowledge_graph_api
        
        app = Flask(__name__)
        app.register_blueprint(knowledge_graph_api, url_prefix='/knowledge-graph')
        
        # Mock data sources
        app.sqlite_data_source = Mock()
        app.hana_data_source = Mock()
        
        app.config['TESTING'] = True
        return app
    
    @pytest.fixture
    def client(self, app):
        """Create test client"""
        return app.test_client()
    
    def test_get_knowledge_graph_default_parameters(self, client):
        """Test API with default parameters (sqlite, schema mode)
        
        ARRANGE: Mock SchemaGraphBuilder to return sample graph
        ACT: GET /knowledge-graph/ with no parameters
        ASSERT: Returns success with default mode=schema, source=sqlite
        """
        # ARRANGE
        mock_graph = {
            'success': True,
            'nodes': [{'id': '1', 'label': 'Test'}],
            'edges': [{'from': '1', 'to': '2'}],
            'stats': {'node_count': 1, 'edge_count': 1}
        }
        
        # Patch at source module (where it's imported from)
        with patch('modules.knowledge_graph.backend.schema_graph_builder.SchemaGraphBuilder') as mock_builder_class:
            mock_builder = Mock()
            mock_builder.build_schema_graph.return_value = mock_graph
            mock_builder_class.return_value = mock_builder
            
            # ACT
            response = client.get('/knowledge-graph/')
        
        # ASSERT
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        assert len(data['nodes']) == 1
        assert len(data['edges']) == 1
    
    def test_get_knowledge_graph_data_mode(self, client):
        """Test data mode calls build_data_graph with correct parameters
        
        ARRANGE: Mock DataGraphBuilder
        ACT: GET with mode=data, max_records=5, filter_orphans=false
        ASSERT: Calls build_data_graph with correct parameters
        """
        # ARRANGE
        mock_graph = {
            'success': True,
            'nodes': [],
            'edges': [],
            'stats': {'node_count': 0, 'edge_count': 0}
        }
        
        # Patch at source module
        with patch('modules.knowledge_graph.backend.data_graph_builder.DataGraphBuilder') as mock_builder_class:
            mock_builder = Mock()
            mock_builder.build_data_graph.return_value = mock_graph
            mock_builder_class.return_value = mock_builder
            
            # ACT
            response = client.get('/knowledge-graph/?mode=data&max_records=5&filter_orphans=false')
        
        # ASSERT
        assert response.status_code == 200
        mock_builder.build_data_graph.assert_called_once_with(
            max_records_per_table=5,
            filter_orphans=False,
            use_cache=True
        )
    
    def test_get_knowledge_graph_csn_mode(self, client):
        """Test CSN mode uses CSNSchemaGraphBuilderV2
        
        ARRANGE: Mock CSNSchemaGraphBuilderV2
        ACT: GET with mode=csn
        ASSERT: Uses CSN builder and calls build_schema_graph
        """
        # ARRANGE
        mock_graph = {
            'success': True,
            'nodes': [{'id': 'csn1'}],
            'edges': [],
            'stats': {'node_count': 1, 'edge_count': 0}
        }
        
        # Patch at source module
        with patch('modules.knowledge_graph.backend.csn_schema_graph_builder_v2.CSNSchemaGraphBuilderV2') as mock_builder_class:
            mock_builder = Mock()
            mock_builder.build_schema_graph.return_value = mock_graph
            mock_builder_class.return_value = mock_builder
            
            # ACT
            response = client.get('/knowledge-graph/?mode=csn')
        
        # ASSERT
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        assert data['nodes'][0]['id'] == 'csn1'
    
    def test_get_knowledge_graph_hana_source(self, client, app):
        """Test HANA data source selection
        
        ARRANGE: Configure HANA data source
        ACT: GET with source=hana
        ASSERT: Uses HANA data source, not SQLite
        """
        # ARRANGE
        mock_graph = {
            'success': True,
            'nodes': [],
            'edges': [],
            'stats': {'node_count': 0, 'edge_count': 0}
        }
        
        # Patch at source module
        with patch('modules.knowledge_graph.backend.schema_graph_builder.SchemaGraphBuilder') as mock_builder_class:
            mock_builder = Mock()
            mock_builder.build_schema_graph.return_value = mock_graph
            mock_builder_class.return_value = mock_builder
            
            # ACT
            response = client.get('/knowledge-graph/?source=hana')
        
        # ASSERT
        assert response.status_code == 200
        # Verify HANA data source was passed to builder
        call_args = mock_builder_class.call_args
        assert call_args[0][0] == app.hana_data_source
    
    def test_get_knowledge_graph_invalid_source(self, client):
        """Test invalid source parameter returns 400 error
        
        ARRANGE: None
        ACT: GET with source=invalid
        ASSERT: Returns 400 with INVALID_SOURCE error
        """
        # ACT
        response = client.get('/knowledge-graph/?source=invalid')
        
        # ASSERT
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['success'] is False
        assert data['error']['code'] == 'INVALID_SOURCE'
        assert 'sqlite' in data['error']['message']
        assert 'hana' in data['error']['message']
    
    def test_get_knowledge_graph_invalid_mode(self, client):
        """Test invalid mode parameter returns 400 error
        
        ARRANGE: None
        ACT: GET with mode=invalid
        ASSERT: Returns 400 with INVALID_MODE error
        """
        # ACT
        response = client.get('/knowledge-graph/?mode=invalid')
        
        # ASSERT
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['success'] is False
        assert data['error']['code'] == 'INVALID_MODE'
        assert 'schema' in data['error']['message']
        assert 'data' in data['error']['message']
    
    def test_get_knowledge_graph_max_records_validation(self, client):
        """Test max_records parameter validation (1-100 range)
        
        ARRANGE: None
        ACT: GET with max_records=0 and max_records=101
        ASSERT: Both return 400 with INVALID_PARAMETER error
        """
        # ACT - Test below minimum
        response1 = client.get('/knowledge-graph/?mode=data&max_records=0')
        
        # ASSERT
        assert response1.status_code == 400
        data1 = json.loads(response1.data)
        assert data1['error']['code'] == 'INVALID_PARAMETER'
        assert 'between 1 and 100' in data1['error']['message']
        
        # ACT - Test above maximum
        response2 = client.get('/knowledge-graph/?mode=data&max_records=101')
        
        # ASSERT
        assert response2.status_code == 400
        data2 = json.loads(response2.data)
        assert data2['error']['code'] == 'INVALID_PARAMETER'
    
    def test_get_knowledge_graph_hana_not_configured(self, client, app):
        """Test error when HANA requested but not configured
        
        ARRANGE: Set HANA data source to None
        ACT: GET with source=hana
        ASSERT: Returns 503 with SOURCE_NOT_CONFIGURED error
        """
        # ARRANGE
        app.hana_data_source = None
        
        # ACT
        response = client.get('/knowledge-graph/?source=hana')
        
        # ASSERT
        assert response.status_code == 503
        data = json.loads(response.data)
        assert data['success'] is False
        assert data['error']['code'] == 'SOURCE_NOT_CONFIGURED'
        assert 'not configured' in data['error']['message']
    
    def test_get_knowledge_graph_builder_exception(self, client):
        """Test exception handling when builder throws error
        
        ARRANGE: Mock builder to raise exception
        ACT: GET /knowledge-graph/
        ASSERT: Returns 500 with SERVER_ERROR
        """
        # ARRANGE
        # Patch at source module
        with patch('modules.knowledge_graph.backend.schema_graph_builder.SchemaGraphBuilder') as mock_builder_class:
            mock_builder_class.side_effect = RuntimeError("Database connection failed")
            
            # ACT
            response = client.get('/knowledge-graph/')
        
        # ASSERT
        assert response.status_code == 500
        data = json.loads(response.data)
        assert data['success'] is False
        assert data['error']['code'] == 'SERVER_ERROR'
        assert 'Database connection failed' in data['error']['message']
    
    def test_get_knowledge_graph_cache_enabled_sqlite(self, client, app):
        """Test cache lookup for SQLite source
        
        ARRANGE: Mock VisJsTranslator to return cached graph
        ACT: GET with use_cache=true (default)
        ASSERT: Returns cached graph without building
        """
        # ARRANGE
        # Configure data_source to return proper connection info
        app.sqlite_data_source.get_connection_info.return_value = {
            'type': 'sqlite',
            'db_path': 'test.db'
        }
        
        cached_graph = {
            'success': True,
            'nodes': [{'id': 'cached'}],
            'edges': [],
            'stats': {'cache_exists': True, 'node_count': 1}
        }
        
        # Patch at source module
        with patch('core.services.visjs_translator.VisJsTranslator') as mock_translator_class:
            mock_translator = Mock()
            mock_translator.get_visjs_graph.return_value = cached_graph
            mock_translator_class.return_value = mock_translator
            
            # ACT
            response = client.get('/knowledge-graph/?use_cache=true')
        
        # ASSERT
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        assert data['nodes'][0]['id'] == 'cached'
        assert data['stats']['cache_exists'] is True
    
    def test_get_knowledge_graph_cache_disabled(self, client):
        """Test cache bypass when use_cache=false
        
        ARRANGE: Mock builder
        ACT: GET with use_cache=false
        ASSERT: Builds graph instead of using cache
        """
        # ARRANGE
        mock_graph = {
            'success': True,
            'nodes': [{'id': 'fresh'}],
            'edges': [],
            'stats': {'node_count': 1, 'edge_count': 0}
        }
        
        # Patch at source module
        with patch('modules.knowledge_graph.backend.schema_graph_builder.SchemaGraphBuilder') as mock_builder_class:
            mock_builder = Mock()
            mock_builder.build_schema_graph.return_value = mock_graph
            mock_builder_class.return_value = mock_builder
            
            # ACT
            response = client.get('/knowledge-graph/?use_cache=false')
        
        # ASSERT
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['nodes'][0]['id'] == 'fresh'
        mock_builder.build_schema_graph.assert_called_once()
    
    def test_get_knowledge_graph_cache_fallback_on_error(self, client):
        """Test graceful fallback when cache load fails
        
        ARRANGE: Mock cache to raise exception, mock builder to succeed
        ACT: GET /knowledge-graph/
        ASSERT: Falls back to building graph (no crash)
        """
        # ARRANGE
        mock_graph = {
            'success': True,
            'nodes': [],
            'edges': [],
            'stats': {'node_count': 0, 'edge_count': 0}
        }
        
        # Patch at source module
        with patch('core.services.visjs_translator.VisJsTranslator') as mock_translator_class:
            mock_translator_class.side_effect = Exception("Cache read error")
            
            with patch('modules.knowledge_graph.backend.schema_graph_builder.SchemaGraphBuilder') as mock_builder_class:
                mock_builder = Mock()
                mock_builder.build_schema_graph.return_value = mock_graph
                mock_builder_class.return_value = mock_builder
                
                # ACT
                response = client.get('/knowledge-graph/')
        
        # ASSERT
        assert response.status_code == 200  # Should succeed despite cache error
        data = json.loads(response.data)
        assert data['success'] is True
    
    def test_get_knowledge_graph_case_insensitive_parameters(self, client):
        """Test parameters are case-insensitive
        
        ARRANGE: Mock builder
        ACT: GET with UPPERCASE parameters
        ASSERT: Handles correctly (lowercase conversion)
        """
        # ARRANGE
        mock_graph = {
            'success': True,
            'nodes': [],
            'edges': [],
            'stats': {'node_count': 0, 'edge_count': 0}
        }
        
        # Patch at source module
        with patch('modules.knowledge_graph.backend.schema_graph_builder.SchemaGraphBuilder') as mock_builder_class:
            mock_builder = Mock()
            mock_builder.build_schema_graph.return_value = mock_graph
            mock_builder_class.return_value = mock_builder
            
            # ACT
            response = client.get('/knowledge-graph/?source=SQLITE&mode=SCHEMA')
        
        # ASSERT
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
    
    def test_get_knowledge_graph_filter_orphans_true_variants(self, client):
        """Test filter_orphans accepts various true values
        
        ARRANGE: Mock DataGraphBuilder
        ACT: Test 'true', '1', 'yes'
        ASSERT: All interpreted as True
        """
        # ARRANGE
        mock_graph = {
            'success': True,
            'nodes': [],
            'edges': [],
            'stats': {'node_count': 0, 'edge_count': 0}
        }
        
        test_values = ['true', '1', 'yes', 'TRUE', 'Yes']
        
        for value in test_values:
            # Patch at source module
            with patch('modules.knowledge_graph.backend.data_graph_builder.DataGraphBuilder') as mock_builder_class:
                mock_builder = Mock()
                mock_builder.build_data_graph.return_value = mock_graph
                mock_builder_class.return_value = mock_builder
                
                # ACT
                response = client.get(f'/knowledge-graph/?mode=data&filter_orphans={value}')
            
            # ASSERT
            assert response.status_code == 200
            # Verify filter_orphans=True was passed
            call_kwargs = mock_builder.build_data_graph.call_args[1]
            assert call_kwargs['filter_orphans'] is True, f"Failed for value: {value}"