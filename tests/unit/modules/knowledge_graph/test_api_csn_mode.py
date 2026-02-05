"""
API Integration Tests for CSN Mode

Tests the Knowledge Graph API with CSN mode parameter.

@author P2P Development Team
@version 1.0.0
"""

import unittest
import sys
from pathlib import Path
import pytest

# Add project root to path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))


class TestKnowledgeGraphAPICSNMode(unittest.TestCase):
    """Test suite for Knowledge Graph API CSN mode"""
    
    def setUp(self):
        """Set up test Flask app"""
        from app.app import create_app
        
        self.app = create_app()
        self.client = self.app.test_client()
        self.app.testing = True
    
    @pytest.mark.unit
    @pytest.mark.fast
    def test_csn_mode_endpoint_exists(self):
        """Test that API accepts mode=csn parameter"""
        response = self.client.get('/api/knowledge-graph/?mode=csn')
        
        # Should return 200 or valid JSON error (not 404)
        self.assertIn(response.status_code, [200, 400, 500])
        
        data = response.get_json()
        self.assertIsInstance(data, dict)
        self.assertIn('success', data)
    
    @pytest.mark.unit
    @pytest.mark.fast
    def test_csn_mode_returns_graph_data(self):
        """Test that CSN mode returns valid graph data"""
        response = self.client.get('/api/knowledge-graph/?mode=csn&source=sqlite')
        
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        
        # Check structure
        self.assertIn('success', data)
        self.assertIn('nodes', data)
        self.assertIn('edges', data)
        self.assertIn('stats', data)
        
        # Check data types
        self.assertIsInstance(data['nodes'], list)
        self.assertIsInstance(data['edges'], list)
        self.assertIsInstance(data['stats'], dict)
    
    @pytest.mark.unit
    @pytest.mark.fast
    def test_csn_mode_has_nodes(self):
        """Test that CSN mode returns non-empty graph"""
        response = self.client.get('/api/knowledge-graph/?mode=csn')
        
        data = response.get_json()
        
        if data.get('success'):
            # Should have nodes from CSN files
            self.assertGreater(len(data['nodes']), 0, 
                             "CSN mode should return nodes from docs/csn/")
    
    @pytest.mark.unit
    @pytest.mark.fast
    def test_csn_mode_statistics(self):
        """Test that CSN mode returns proper statistics"""
        response = self.client.get('/api/knowledge-graph/?mode=csn')
        
        data = response.get_json()
        
        if data.get('success'):
            stats = data['stats']
            
            # Check required fields
            self.assertIn('node_count', stats)
            self.assertIn('edge_count', stats)
            self.assertIn('product_count', stats)
            self.assertIn('table_count', stats)
            
            # Values should match
            self.assertEqual(stats['node_count'], len(data['nodes']))
            self.assertEqual(stats['edge_count'], len(data['edges']))
    
    @pytest.mark.unit
    @pytest.mark.fast
    def test_csn_mode_vs_schema_mode(self):
        """Test that CSN mode differs from schema mode (shows more data)"""
        # Get schema mode data
        schema_response = self.client.get('/api/knowledge-graph/?mode=schema')
        schema_data = schema_response.get_json()
        
        # Get CSN mode data
        csn_response = self.client.get('/api/knowledge-graph/?mode=csn')
        csn_data = csn_response.get_json()
        
        if schema_data.get('success') and csn_data.get('success'):
            # CSN should have more nodes (full metadata catalog)
            self.assertGreaterEqual(len(csn_data['nodes']), len(schema_data['nodes']),
                                   "CSN mode should show full catalog (more nodes than deployed schema)")
    
    @pytest.mark.unit
    @pytest.mark.fast
    def test_invalid_mode_parameter(self):
        """Test that invalid mode returns error"""
        response = self.client.get('/api/knowledge-graph/?mode=invalid')
        
        self.assertEqual(response.status_code, 400)
        data = response.get_json()
        
        self.assertFalse(data['success'])
        self.assertIn('error', data)
        self.assertEqual(data['error']['code'], 'INVALID_MODE')
    
    @pytest.mark.unit
    @pytest.mark.fast
    def test_csn_mode_with_different_sources(self):
        """Test CSN mode with both sqlite and hana sources"""
        # SQLite source
        response_sqlite = self.client.get('/api/knowledge-graph/?mode=csn&source=sqlite')
        self.assertEqual(response_sqlite.status_code, 200)
        
        # HANA source (may not be configured, but shouldn't crash)
        response_hana = self.client.get('/api/knowledge-graph/?mode=csn&source=hana')
        # Should return 200 (success) or 503 (not configured), not 500 (crash)
        self.assertIn(response_hana.status_code, [200, 503])
    
    @pytest.mark.unit
    @pytest.mark.fast
    def test_csn_mode_node_format(self):
        """Test that CSN mode returns vis.js compatible node format"""
        response = self.client.get('/api/knowledge-graph/?mode=csn')
        data = response.get_json()
        
        if data.get('success') and len(data['nodes']) > 0:
            node = data['nodes'][0]
            
            # Check required vis.js fields
            required_fields = ['id', 'label', 'title', 'group', 'shape', 'color']
            for field in required_fields:
                self.assertIn(field, node, f"Node missing required field: {field}")
            
            # Check color format
            color = node['color']
            self.assertIsInstance(color, dict)
            self.assertIn('background', color)
            self.assertIn('border', color)
    
    @pytest.mark.unit
    @pytest.mark.fast
    def test_csn_mode_edge_format(self):
        """Test that CSN mode returns vis.js compatible edge format"""
        response = self.client.get('/api/knowledge-graph/?mode=csn')
        data = response.get_json()
        
        if data.get('success') and len(data['edges']) > 0:
            edge = data['edges'][0]
            
            # Check required vis.js fields
            required_fields = ['from', 'to', 'arrows', 'color']
            for field in required_fields:
                self.assertIn(field, edge, f"Edge missing required field: {field}")
            
            # Check color format
            self.assertIn('color', edge)
            self.assertIsInstance(edge['color'], dict)
    
    @pytest.mark.unit
    @pytest.mark.fast
    def test_csn_mode_response_time(self):
        """Test that CSN mode responds within acceptable time"""
        import time
        
        start = time.time()
        response = self.client.get('/api/knowledge-graph/?mode=csn')
        duration = time.time() - start
        
        # Should respond within 5 seconds
        self.assertLess(duration, 5.0, 
                       f"CSN mode took {duration:.2f}s (should be < 5s)")
    
    @pytest.mark.unit
    @pytest.mark.fast
    def test_csn_mode_with_cache_parameter(self):
        """Test CSN mode with use_cache parameter"""
        # Test with cache enabled
        response1 = self.client.get('/api/knowledge-graph/?mode=csn&use_cache=true')
        self.assertEqual(response1.status_code, 200)
        
        # Test with cache disabled
        response2 = self.client.get('/api/knowledge-graph/?mode=csn&use_cache=false')
        self.assertEqual(response2.status_code, 200)


class TestKnowledgeGraphAPIModeComparison(unittest.TestCase):
    """Test mode comparison and compatibility"""
    
    def setUp(self):
        """Set up test Flask app"""
        from app.app import create_app
        
        self.app = create_app()
        self.client = self.app.test_client()
        self.app.testing = True
    
    @pytest.mark.unit
    @pytest.mark.fast
    def test_all_modes_return_same_format(self):
        """Test that all modes return compatible vis.js format"""
        modes = ['schema', 'csn', 'data']
        
        for mode in modes:
            with self.subTest(mode=mode):
                response = self.client.get(f'/api/knowledge-graph/?mode={mode}')
                
                # Skip if mode not yet implemented or data source not configured
                if response.status_code not in [200, 503]:
                    continue
                
                if response.status_code == 200:
                    data = response.get_json()
                    
                    # All modes should return same structure
                    self.assertIn('success', data)
                    self.assertIn('nodes', data)
                    self.assertIn('edges', data)
                    self.assertIn('stats', data)
    
    @pytest.mark.unit
    @pytest.mark.fast
    def test_csn_mode_has_more_entities_than_schema(self):
        """Test that CSN shows full catalog (more than deployed schema)"""
        # Get both modes
        schema_resp = self.client.get('/api/knowledge-graph/?mode=schema')
        csn_resp = self.client.get('/api/knowledge-graph/?mode=csn')
        
        schema_data = schema_resp.get_json()
        csn_data = csn_resp.get_json()
        
        # If both succeed, CSN should have more nodes
        if schema_data.get('success') and csn_data.get('success'):
            schema_nodes = len(schema_data['nodes'])
            csn_nodes = len(csn_data['nodes'])
            
            self.assertGreaterEqual(csn_nodes, schema_nodes,
                                   f"CSN mode ({csn_nodes} nodes) should show full catalog "
                                   f"(>= deployed schema {schema_nodes} nodes)")


def run_tests():
    """Run all tests"""
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add test classes
    suite.addTests(loader.loadTestsFromTestCase(TestKnowledgeGraphAPICSNMode))
    suite.addTests(loader.loadTestsFromTestCase(TestKnowledgeGraphAPIModeComparison))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result.wasSuccessful()


if __name__ == '__main__':
    success = run_tests()
    sys.exit(0 if success else 1)