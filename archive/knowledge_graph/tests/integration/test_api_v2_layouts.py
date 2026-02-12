"""
Unit Tests for Knowledge Graph API v2 - Layout Endpoints

Tests the /layouts and /layouts/presets endpoints that provide
vis.js configuration objects for graph visualization.

@author P2P Development Team
@version 1.0.0
"""

import pytest
import json
from unittest.mock import Mock, patch
from modules.knowledge_graph.backend.api_v2 import knowledge_graph_api


@pytest.fixture
def client():
    """Create test client for Flask blueprint"""
    from flask import Flask
    app = Flask(__name__)
    app.register_blueprint(knowledge_graph_api)
    app.config['TESTING'] = True
    
    with app.test_client() as client:
        yield client


class TestLayoutsEndpoint:
    """Test /api/knowledge-graph/layouts endpoint"""
    
    @pytest.mark.integration
    @pytest.mark.fast
    def test_layouts_returns_success(self, client):
        """Layouts endpoint returns success response"""
        response = client.get('/api/knowledge-graph/layouts')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['success'] is True
    
    @pytest.mark.integration
    @pytest.mark.fast
    def test_layouts_contains_hierarchical(self, client):
        """Layouts response includes hierarchical configurations"""
        response = client.get('/api/knowledge-graph/layouts')
        data = json.loads(response.data)
        
        assert 'layouts' in data
        assert 'hierarchical' in data['layouts']
        
        hierarchical = data['layouts']['hierarchical']
        assert 'directions' in hierarchical
        assert 'description' in hierarchical
    
    @pytest.mark.integration
    @pytest.mark.fast
    def test_layouts_hierarchical_has_four_directions(self, client):
        """Hierarchical layout has all 4 directions"""
        response = client.get('/api/knowledge-graph/layouts')
        data = json.loads(response.data)
        
        directions = data['layouts']['hierarchical']['directions']
        assert 'UD' in directions  # Top-Down
        assert 'LR' in directions  # Left-Right
        assert 'DU' in directions  # Bottom-Up
        assert 'RL' in directions  # Right-Left
        
        # Each direction has config
        for direction in ['UD', 'LR', 'DU', 'RL']:
            assert 'config' in directions[direction]
            assert 'label' in directions[direction]
            assert 'description' in directions[direction]
    
    @pytest.mark.integration
    @pytest.mark.fast
    def test_layouts_hierarchical_config_structure(self, client):
        """Hierarchical config has correct vis.js structure"""
        response = client.get('/api/knowledge-graph/layouts')
        data = json.loads(response.data)
        
        config = data['layouts']['hierarchical']['directions']['UD']['config']
        
        # Required vis.js options
        assert 'layout' in config
        assert 'hierarchical' in config['layout']
        assert 'physics' in config
        assert 'edges' in config
        
        # Hierarchical settings
        hierarchical = config['layout']['hierarchical']
        assert hierarchical['enabled'] is True
        assert hierarchical['direction'] == 'UD'
        assert hierarchical['sortMethod'] == 'directed'
    
    @pytest.mark.integration
    @pytest.mark.fast
    def test_layouts_contains_force_directed(self, client):
        """Layouts response includes force-directed configurations"""
        response = client.get('/api/knowledge-graph/layouts')
        data = json.loads(response.data)
        
        assert 'force' in data['layouts']
        
        force = data['layouts']['force']
        assert 'solvers' in force
        assert 'description' in force
    
    @pytest.mark.integration
    @pytest.mark.fast
    def test_layouts_force_has_three_solvers(self, client):
        """Force-directed layout has all 3 physics solvers"""
        response = client.get('/api/knowledge-graph/layouts')
        data = json.loads(response.data)
        
        solvers = data['layouts']['force']['solvers']
        assert 'barnesHut' in solvers
        assert 'forceAtlas2Based' in solvers
        assert 'repulsion' in solvers
        
        # Each solver has config
        for solver in ['barnesHut', 'forceAtlas2Based', 'repulsion']:
            assert 'config' in solvers[solver]
            assert 'label' in solvers[solver]
            assert 'performance' in solvers[solver]
    
    @pytest.mark.integration
    @pytest.mark.fast
    def test_layouts_force_config_structure(self, client):
        """Force-directed config has correct vis.js structure"""
        response = client.get('/api/knowledge-graph/layouts')
        data = json.loads(response.data)
        
        config = data['layouts']['force']['solvers']['barnesHut']['config']
        
        # Required vis.js options
        assert 'layout' in config
        assert 'physics' in config
        
        # Physics enabled for force-directed
        assert config['physics']['enabled'] is True
        
        # Barnes-Hut specific settings
        assert 'barnesHut' in config['physics']
        barnes_hut = config['physics']['barnesHut']
        assert 'gravitationalConstant' in barnes_hut
        assert 'springLength' in barnes_hut


class TestPresetsEndpoint:
    """Test /api/knowledge-graph/layouts/presets endpoint"""
    
    @pytest.mark.integration
    @pytest.mark.fast
    def test_presets_returns_success(self, client):
        """Presets endpoint returns success response"""
        response = client.get('/api/knowledge-graph/layouts/presets')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['success'] is True
    
    @pytest.mark.integration
    @pytest.mark.fast
    def test_presets_contains_four_presets(self, client):
        """Presets response includes all 4 presets"""
        response = client.get('/api/knowledge-graph/layouts/presets')
        data = json.loads(response.data)
        
        assert 'presets' in data
        presets = data['presets']
        
        assert 'schema' in presets
        assert 'cluster' in presets
        assert 'compact' in presets
        assert 'explore' in presets
    
    @pytest.mark.integration
    @pytest.mark.fast
    def test_preset_schema_structure(self, client):
        """Schema preset has correct structure"""
        response = client.get('/api/knowledge-graph/layouts/presets')
        data = json.loads(response.data)
        
        schema = data['presets']['schema']
        assert 'name' in schema
        assert 'description' in schema
        assert 'use_case' in schema
        assert 'config' in schema
        
        # Schema uses hierarchical top-down
        config = schema['config']
        assert config['layout']['hierarchical']['enabled'] is True
        assert config['layout']['hierarchical']['direction'] == 'UD'
    
    @pytest.mark.integration
    @pytest.mark.fast
    def test_preset_cluster_structure(self, client):
        """Cluster preset has correct structure"""
        response = client.get('/api/knowledge-graph/layouts/presets')
        data = json.loads(response.data)
        
        cluster = data['presets']['cluster']
        assert 'name' in cluster
        assert 'description' in cluster
        assert 'use_case' in cluster
        assert 'config' in cluster
        
        # Cluster uses force-directed with Barnes-Hut
        config = cluster['config']
        assert config['physics']['enabled'] is True
        assert 'barnesHut' in config['physics']
    
    @pytest.mark.integration
    @pytest.mark.fast
    def test_preset_compact_for_small_screens(self, client):
        """Compact preset optimized for small screens"""
        response = client.get('/api/knowledge-graph/layouts/presets')
        data = json.loads(response.data)
        
        compact = data['presets']['compact']
        
        # Compact uses left-right orientation
        config = compact['config']
        assert config['layout']['hierarchical']['direction'] == 'LR'
        
        # Tighter spacing for small screens
        assert config['layout']['hierarchical']['levelSeparation'] == 100
    
    @pytest.mark.integration
    @pytest.mark.fast
    def test_preset_explore_interactive(self, client):
        """Explore preset allows manual repositioning"""
        response = client.get('/api/knowledge-graph/layouts/presets')
        data = json.loads(response.data)
        
        explore = data['presets']['explore']
        config = explore['config']
        
        # Physics enabled for dragging
        assert config['physics']['enabled'] is True
        
        # Interaction allowed
        assert config['interaction']['dragNodes'] is True


class TestLayoutConfigValidation:
    """Test that configs match vis.js API requirements"""
    
    @pytest.mark.integration
    @pytest.mark.fast
    def test_all_configs_have_required_fields(self, client):
        """Every layout config has required vis.js fields"""
        response = client.get('/api/knowledge-graph/layouts')
        data = json.loads(response.data)
        
        # Check all hierarchical configs
        for direction_key, direction_data in data['layouts']['hierarchical']['directions'].items():
            config = direction_data['config']
            assert 'layout' in config
            assert 'physics' in config
            assert 'edges' in config
            assert 'interaction' in config
        
        # Check all force configs
        for solver_key, solver_data in data['layouts']['force']['solvers'].items():
            config = solver_data['config']
            assert 'layout' in config
            assert 'physics' in config
            assert 'edges' in config
            assert 'interaction' in config
    
    @pytest.mark.integration
    @pytest.mark.fast
    def test_hierarchical_physics_disabled(self, client):
        """Hierarchical layouts have physics disabled"""
        response = client.get('/api/knowledge-graph/layouts')
        data = json.loads(response.data)
        
        for direction_key, direction_data in data['layouts']['hierarchical']['directions'].items():
            config = direction_data['config']
            assert config['physics']['enabled'] is False
    
    @pytest.mark.integration
    @pytest.mark.fast
    def test_force_physics_enabled(self, client):
        """Force-directed layouts have physics enabled"""
        response = client.get('/api/knowledge-graph/layouts')
        data = json.loads(response.data)
        
        for solver_key, solver_data in data['layouts']['force']['solvers'].items():
            config = solver_data['config']
            assert config['physics']['enabled'] is True
    
    @pytest.mark.integration
    @pytest.mark.fast
    def test_configs_serializable_to_json(self, client):
        """All configs can be serialized to JSON"""
        response = client.get('/api/knowledge-graph/layouts')
        data = json.loads(response.data)
        
        # Try to re-serialize all configs
        for direction_key, direction_data in data['layouts']['hierarchical']['directions'].items():
            json.dumps(direction_data['config'])  # Should not raise
        
        for solver_key, solver_data in data['layouts']['force']['solvers'].items():
            json.dumps(solver_data['config'])  # Should not raise


class TestPerformanceMetadata:
    """Test performance metadata for layout selection"""
    
    @pytest.mark.integration
    @pytest.mark.fast
    def test_force_solvers_have_performance_info(self, client):
        """Force-directed solvers include performance characteristics"""
        response = client.get('/api/knowledge-graph/layouts')
        data = json.loads(response.data)
        
        solvers = data['layouts']['force']['solvers']
        
        # Barnes-Hut: Fast O(n log n)
        assert 'performance' in solvers['barnesHut']
        assert 'best_for' in solvers['barnesHut']
        
        # Force Atlas 2: Quality clustering
        assert 'performance' in solvers['forceAtlas2Based']
        assert 'best_for' in solvers['forceAtlas2Based']
        
        # Repulsion: Clean O(n²)
        assert 'performance' in solvers['repulsion']
        assert 'best_for' in solvers['repulsion']
    
    @pytest.mark.integration
    @pytest.mark.fast
    def test_presets_include_use_cases(self, client):
        """Presets include use case descriptions"""
        response = client.get('/api/knowledge-graph/layouts/presets')
        data = json.loads(response.data)
        
        for preset_key, preset_data in data['presets'].items():
            assert 'use_case' in preset_data
            assert len(preset_data['use_case']) > 0


if __name__ == '__main__':
    pytest.main([__file__, '-v'])