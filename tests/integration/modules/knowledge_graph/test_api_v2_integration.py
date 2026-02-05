"""
Integration Tests for Knowledge Graph API v2

Tests the complete flow of layout endpoint integration with the application.

@author P2P Development Team
@version 1.0.0
"""

import pytest
import json
from unittest.mock import Mock, patch, MagicMock
from modules.knowledge_graph.backend.api_v2 import knowledge_graph_api
from modules.knowledge_graph.backend.knowledge_graph_facade import KnowledgeGraphFacade


@pytest.fixture
def client():
    """Create test client for Flask blueprint"""
    from flask import Flask
    app = Flask(__name__)
    app.register_blueprint(knowledge_graph_api)
    app.config['TESTING'] = True
    
    with app.test_client() as client:
        yield client


@pytest.fixture
def mock_facade():
    """Mock KnowledgeGraphFacade for testing"""
    with patch('modules.knowledge_graph.backend.api_v2.KnowledgeGraphFacade') as mock:
        facade = MagicMock()
        mock.return_value = facade
        yield facade


class TestLayoutEndpointIntegration:
    """Test full layout workflow integration"""
    
    @pytest.mark.integration
    @pytest.mark.fast
    def test_layouts_endpoint_accessible(self, client):
        """Layouts endpoint is accessible via HTTP GET"""
        response = client.get('/api/knowledge-graph/layouts')
        assert response.status_code == 200
        assert response.content_type == 'application/json'
    
    @pytest.mark.integration
    @pytest.mark.fast
    def test_presets_endpoint_accessible(self, client):
        """Presets endpoint is accessible via HTTP GET"""
        response = client.get('/api/knowledge-graph/layouts/presets')
        assert response.status_code == 200
        assert response.content_type == 'application/json'
    
    @pytest.mark.integration
    @pytest.mark.fast
    def test_endpoints_return_valid_json(self, client):
        """Both endpoints return valid JSON"""
        # Test layouts
        response = client.get('/api/knowledge-graph/layouts')
        data = json.loads(response.data)
        assert isinstance(data, dict)
        
        # Test presets
        response = client.get('/api/knowledge-graph/layouts/presets')
        data = json.loads(response.data)
        assert isinstance(data, dict)
    
    @pytest.mark.integration
    @pytest.mark.fast
    def test_layout_configs_are_complete(self, client):
        """Layout configurations are complete and usable"""
        response = client.get('/api/knowledge-graph/layouts')
        data = json.loads(response.data)
        
        # Can extract a config
        config = data['layouts']['hierarchical']['directions']['UD']['config']
        
        # Config has all required vis.js fields
        required_fields = ['layout', 'physics', 'edges', 'interaction']
        for field in required_fields:
            assert field in config, f"Missing required field: {field}"
    
    @pytest.mark.integration
    @pytest.mark.fast
    def test_preset_configs_are_complete(self, client):
        """Preset configurations are complete and usable"""
        response = client.get('/api/knowledge-graph/layouts/presets')
        data = json.loads(response.data)
        
        # Can extract a preset config
        config = data['presets']['schema']['config']
        
        # Config has all required vis.js fields
        required_fields = ['layout', 'physics', 'edges', 'interaction']
        for field in required_fields:
            assert field in config, f"Missing required field: {field}"


class TestLayoutEndpointErrorHandling:
    """Test error handling in layout endpoints"""
    
    @pytest.mark.integration
    @pytest.mark.fast
    def test_invalid_endpoint_returns_404(self, client):
        """Invalid layout endpoint returns 404"""
        response = client.get('/api/knowledge-graph/layouts/invalid')
        assert response.status_code == 404
    
    @pytest.mark.integration
    @pytest.mark.fast
    def test_layouts_endpoint_handles_exceptions_gracefully(self, client):
        """Layouts endpoint handles internal errors gracefully"""
        # Even if something goes wrong, endpoint should return valid response
        response = client.get('/api/knowledge-graph/layouts')
        
        # Should get a response (even if error)
        assert response.status_code in [200, 500]
        
        # Should be valid JSON
        data = json.loads(response.data)
        assert isinstance(data, dict)


class TestLayoutPresetWorkflow:
    """Test the complete workflow of using layout presets"""
    
    @pytest.mark.integration
    @pytest.mark.fast
    def test_get_presets_then_apply_schema(self, client):
        """Workflow: Get presets → Select 'schema' → Apply config"""
        # Step 1: Get available presets
        response = client.get('/api/knowledge-graph/layouts/presets')
        data = json.loads(response.data)
        
        # Step 2: Extract schema preset
        schema_preset = data['presets']['schema']
        assert 'config' in schema_preset
        
        # Step 3: Verify config is ready to apply
        config = schema_preset['config']
        assert config['layout']['hierarchical']['enabled'] is True
        
        # This config could now be passed to vis.js network.setOptions()
    
    @pytest.mark.integration
    @pytest.mark.fast
    def test_get_layouts_then_build_custom(self, client):
        """Workflow: Get layouts → Select hierarchical LR → Apply config"""
        # Step 1: Get available layouts
        response = client.get('/api/knowledge-graph/layouts')
        data = json.loads(response.data)
        
        # Step 2: User selects hierarchical Left-Right
        lr_layout = data['layouts']['hierarchical']['directions']['LR']
        assert 'config' in lr_layout
        
        # Step 3: Verify config is ready to apply
        config = lr_layout['config']
        assert config['layout']['hierarchical']['direction'] == 'LR'
        
        # This config could now be passed to vis.js network.setOptions()
    
    @pytest.mark.integration
    @pytest.mark.fast
    def test_switch_between_presets(self, client):
        """Workflow: Apply preset 1 → Switch to preset 2"""
        response = client.get('/api/knowledge-graph/layouts/presets')
        data = json.loads(response.data)
        
        # Apply schema preset (hierarchical)
        schema_config = data['presets']['schema']['config']
        assert schema_config['physics']['enabled'] is False
        
        # Switch to cluster preset (force-directed)
        cluster_config = data['presets']['cluster']['config']
        assert cluster_config['physics']['enabled'] is True
        
        # Configs are independent - can switch anytime


class TestLayoutMetadataForUserExperience:
    """Test that metadata helps users make informed choices"""
    
    @pytest.mark.integration
    @pytest.mark.fast
    def test_hierarchical_directions_have_labels(self, client):
        """Hierarchical directions have user-friendly labels"""
        response = client.get('/api/knowledge-graph/layouts')
        data = json.loads(response.data)
        
        directions = data['layouts']['hierarchical']['directions']
        
        # Each direction should have a label
        for direction_key in ['UD', 'LR', 'DU', 'RL']:
            assert 'label' in directions[direction_key]
            label = directions[direction_key]['label']
            assert len(label) > 0
            # Labels should be descriptive (e.g., "Top-Down", not just "UD")
            assert len(label) > 5
    
    @pytest.mark.integration
    @pytest.mark.fast
    def test_force_solvers_have_performance_info(self, client):
        """Force solvers include performance characteristics"""
        response = client.get('/api/knowledge-graph/layouts')
        data = json.loads(response.data)
        
        solvers = data['layouts']['force']['solvers']
        
        for solver_key in ['barnesHut', 'forceAtlas2Based', 'repulsion']:
            solver = solvers[solver_key]
            assert 'performance' in solver
            assert 'best_for' in solver
            
            # Performance info should be useful
            assert len(solver['performance']) > 0
            assert len(solver['best_for']) > 0
    
    @pytest.mark.integration
    @pytest.mark.fast
    def test_presets_describe_use_cases(self, client):
        """Presets describe their ideal use cases"""
        response = client.get('/api/knowledge-graph/layouts/presets')
        data = json.loads(response.data)
        
        for preset_key in ['schema', 'cluster', 'compact', 'explore']:
            preset = data['presets'][preset_key]
            assert 'use_case' in preset
            assert 'description' in preset
            
            # Use case should be descriptive
            use_case = preset['use_case']
            assert len(use_case) > 10  # Not just "Schema"


class TestConfigurationConsistency:
    """Test that configurations are consistent across endpoints"""
    
    @pytest.mark.integration
    @pytest.mark.fast
    def test_schema_preset_matches_hierarchical_ud(self, client):
        """Schema preset config matches hierarchical UD config"""
        # Get preset
        response = client.get('/api/knowledge-graph/layouts/presets')
        preset_data = json.loads(response.data)
        schema_config = preset_data['presets']['schema']['config']
        
        # Get layout
        response = client.get('/api/knowledge-graph/layouts')
        layout_data = json.loads(response.data)
        ud_config = layout_data['layouts']['hierarchical']['directions']['UD']['config']
        
        # Core settings should match
        assert schema_config['layout']['hierarchical']['direction'] == ud_config['layout']['hierarchical']['direction']
        assert schema_config['physics']['enabled'] == ud_config['physics']['enabled']
    
    @pytest.mark.integration
    @pytest.mark.fast
    def test_cluster_preset_matches_force_barnes_hut(self, client):
        """Cluster preset config matches force Barnes-Hut config"""
        # Get preset
        response = client.get('/api/knowledge-graph/layouts/presets')
        preset_data = json.loads(response.data)
        cluster_config = preset_data['presets']['cluster']['config']
        
        # Get layout
        response = client.get('/api/knowledge-graph/layouts')
        layout_data = json.loads(response.data)
        barnes_hut_config = layout_data['layouts']['force']['solvers']['barnesHut']['config']
        
        # Core settings should match
        assert cluster_config['physics']['enabled'] == barnes_hut_config['physics']['enabled']
        assert 'barnesHut' in cluster_config['physics']
        assert 'barnesHut' in barnes_hut_config['physics']


class TestConcurrentRequests:
    """Test that multiple requests work correctly"""
    
    @pytest.mark.integration
    @pytest.mark.fast
    def test_multiple_layout_requests(self, client):
        """Multiple requests to /layouts return consistent results"""
        response1 = client.get('/api/knowledge-graph/layouts')
        response2 = client.get('/api/knowledge-graph/layouts')
        
        data1 = json.loads(response1.data)
        data2 = json.loads(response2.data)
        
        # Results should be identical
        assert data1 == data2
    
    @pytest.mark.integration
    @pytest.mark.fast
    def test_multiple_preset_requests(self, client):
        """Multiple requests to /presets return consistent results"""
        response1 = client.get('/api/knowledge-graph/layouts/presets')
        response2 = client.get('/api/knowledge-graph/layouts/presets')
        
        data1 = json.loads(response1.data)
        data2 = json.loads(response2.data)
        
        # Results should be identical
        assert data1 == data2


if __name__ == '__main__':
    pytest.main([__file__, '-v'])