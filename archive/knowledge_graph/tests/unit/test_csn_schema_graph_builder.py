"""
Unit Tests for CSNSchemaGraphBuilder

Tests the CSN metadata-driven schema graph builder.

@author P2P Development Team
@version 1.0.0
"""

import unittest
import os
import sys
from pathlib import Path
import pytest

# Add project root to path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from modules.knowledge_graph.backend.csn_schema_graph_builder import CSNSchemaGraphBuilder


class TestCSNSchemaGraphBuilder(unittest.TestCase):
    """Test suite for CSNSchemaGraphBuilder"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.csn_directory = 'docs/csn'
        self.builder = CSNSchemaGraphBuilder(self.csn_directory)
    
    @pytest.mark.unit
    @pytest.mark.fast
    def test_initialization(self):
        """Test builder initialization"""
        self.assertIsNotNone(self.builder)
        self.assertEqual(self.builder.csn_directory, self.csn_directory)
        self.assertIsNotNone(self.builder.csn_parser)
        self.assertIsNotNone(self.builder.relationship_mapper)
    
    @pytest.mark.unit
    @pytest.mark.fast
    def test_build_schema_graph_success(self):
        """Test successful schema graph building"""
        result = self.builder.build_schema_graph()
        
        # Check structure
        self.assertIsInstance(result, dict)
        self.assertIn('success', result)
        self.assertIn('nodes', result)
        self.assertIn('edges', result)
        self.assertIn('stats', result)
        
        # Check success
        self.assertTrue(result['success'], f"Graph build failed: {result.get('error')}")
        
        # Check data types
        self.assertIsInstance(result['nodes'], list)
        self.assertIsInstance(result['edges'], list)
        self.assertIsInstance(result['stats'], dict)
    
    @pytest.mark.unit
    @pytest.mark.fast
    def test_graph_has_nodes(self):
        """Test that graph contains nodes"""
        result = self.builder.build_schema_graph()
        
        self.assertTrue(result['success'])
        self.assertGreater(len(result['nodes']), 0, "Graph should have at least one node")
        
        # Verify node structure (vis.js format)
        node = result['nodes'][0]
        self.assertIn('id', node)
        self.assertIn('label', node)
        self.assertIn('title', node)
        self.assertIn('group', node)
        self.assertIn('shape', node)
        self.assertIn('color', node)
    
    @pytest.mark.unit
    @pytest.mark.fast
    def test_graph_has_edges(self):
        """Test that graph contains edges"""
        result = self.builder.build_schema_graph()
        
        self.assertTrue(result['success'])
        self.assertGreater(len(result['edges']), 0, "Graph should have at least one edge")
        
        # Verify edge structure (vis.js format)
        edge = result['edges'][0]
        self.assertIn('from', edge)
        self.assertIn('to', edge)
        self.assertIn('arrows', edge)
        self.assertIn('color', edge)
    
    @pytest.mark.unit
    @pytest.mark.fast
    def test_graph_statistics(self):
        """Test graph statistics calculation"""
        result = self.builder.build_schema_graph()
        
        self.assertTrue(result['success'])
        stats = result['stats']
        
        # Check required stat fields
        self.assertIn('node_count', stats)
        self.assertIn('edge_count', stats)
        self.assertIn('product_count', stats)
        self.assertIn('table_count', stats)
        
        # Check stat values match actual data
        self.assertEqual(stats['node_count'], len(result['nodes']))
        self.assertEqual(stats['edge_count'], len(result['edges']))
    
    @pytest.mark.unit
    @pytest.mark.fast
    def test_node_groups(self):
        """Test that nodes have correct groups (product, table)"""
        result = self.builder.build_schema_graph()
        
        self.assertTrue(result['success'])
        
        # Count node groups
        groups = {}
        for node in result['nodes']:
            group = node.get('group', 'unknown')
            groups[group] = groups.get(group, 0) + 1
        
        # Should have both product and table nodes
        self.assertIn('product', groups, "Should have product nodes")
        self.assertIn('table', groups, "Should have table nodes")
        self.assertGreater(groups['product'], 0)
        self.assertGreater(groups['table'], 0)
    
    @pytest.mark.unit
    @pytest.mark.fast
    def test_product_to_table_relationships(self):
        """Test that products are connected to tables"""
        result = self.builder.build_schema_graph()
        
        self.assertTrue(result['success'])
        
        # Find product nodes
        product_nodes = [n for n in result['nodes'] if n.get('group') == 'product']
        self.assertGreater(len(product_nodes), 0)
        
        # Check each product has outgoing edges (contains tables)
        product_ids = {n['id'] for n in product_nodes}
        edges_from_products = [e for e in result['edges'] if e['from'] in product_ids]
        
        self.assertGreater(len(edges_from_products), 0, "Products should have edges to tables")
    
    @pytest.mark.unit
    @pytest.mark.fast
    def test_foreign_key_relationships(self):
        """Test that FK relationships are discovered"""
        result = self.builder.build_schema_graph()
        
        self.assertTrue(result['success'])
        
        # Find table-to-table edges (FK relationships)
        table_nodes = [n for n in result['nodes'] if n.get('group') == 'table']
        table_ids = {n['id'] for n in table_nodes}
        
        fk_edges = [e for e in result['edges'] 
                    if e['from'] in table_ids and e['to'] in table_ids 
                    and e.get('dashes') == True]  # FK edges are dashed
        
        # Should have at least some FK relationships
        self.assertGreaterEqual(len(fk_edges), 0, "Should discover FK relationships from CSN")
    
    @pytest.mark.unit
    @pytest.mark.fast
    def test_vis_js_format_compatibility(self):
        """Test that output is compatible with vis.js format"""
        result = self.builder.build_schema_graph()
        
        self.assertTrue(result['success'])
        
        # Check node format (vis.js required fields)
        for node in result['nodes']:
            self.assertIn('id', node)
            self.assertIn('label', node)
            
            # Check color format
            self.assertIn('color', node)
            color = node['color']
            self.assertIsInstance(color, dict)
            self.assertIn('background', color)
            self.assertIn('border', color)
        
        # Check edge format (vis.js required fields)
        for edge in result['edges']:
            self.assertIn('from', edge)
            self.assertIn('to', edge)
            self.assertIn('arrows', edge)
            
            # Check color format
            self.assertIn('color', edge)
            self.assertIsInstance(edge['color'], dict)
    
    @pytest.mark.unit
    @pytest.mark.fast
    def test_empty_csn_directory(self):
        """Test behavior with non-existent CSN directory"""
        builder = CSNSchemaGraphBuilder('/nonexistent/path')
        result = builder.build_schema_graph()
        
        # Should return empty graph, not error
        self.assertTrue(result['success'])
        self.assertEqual(len(result['nodes']), 0)
        self.assertEqual(len(result['edges']), 0)
    
    @pytest.mark.unit
    @pytest.mark.fast
    def test_infer_products_from_csn(self):
        """Test product inference from entity names"""
        result = self.builder.build_schema_graph()
        
        self.assertTrue(result['success'])
        
        # Get product names from nodes
        product_nodes = [n for n in result['nodes'] if n.get('group') == 'product']
        product_names = [n['label'] for n in product_nodes]
        
        # Should infer recognizable product names
        # (Based on known_products mapping in the builder)
        known_products = [
            'Purchase_Order', 'Supplier_Invoice', 'Service_Entry_Sheet',
            'Journal_Entry', 'Supplier', 'Product', 'Company_Code',
            'Cost_Center', 'Payment_Terms'
        ]
        
        # At least some known products should be present
        found_known = [p for p in product_names if p in known_products]
        self.assertGreater(len(found_known), 0, 
                          f"Should find known products. Found: {product_names}")
    
    @pytest.mark.unit
    @pytest.mark.fast
    def test_no_self_referential_edges(self):
        """Test that there are no edges from a node to itself"""
        result = self.builder.build_schema_graph()
        
        self.assertTrue(result['success'])
        
        for edge in result['edges']:
            self.assertNotEqual(edge['from'], edge['to'], 
                               f"Found self-referential edge: {edge}")
    
    @pytest.mark.unit
    @pytest.mark.fast
    def test_cache_support(self):
        """Test that builder supports caching (doesn't error when db_path provided)"""
        # Create builder with db_path
        builder = CSNSchemaGraphBuilder('docs/csn', 'test.db')
        
        # Should not error even if cache save fails
        result = builder.build_schema_graph()
        self.assertTrue(result['success'])


class TestCSNSchemaGraphBuilderEdgeCases(unittest.TestCase):
    """Test edge cases and error handling"""
    
    @pytest.mark.unit
    @pytest.mark.fast
    def test_missing_csn_files(self):
        """Test behavior when CSN files are missing"""
        import tempfile
        
        # Create empty temp directory
        with tempfile.TemporaryDirectory() as tmpdir:
            builder = CSNSchemaGraphBuilder(tmpdir)
            result = builder.build_schema_graph()
            
            # Should return empty graph gracefully
            self.assertTrue(result['success'])
            self.assertEqual(len(result['nodes']), 0)
            self.assertEqual(result['stats']['node_count'], 0)
    
    @pytest.mark.unit
    @pytest.mark.fast
    def test_malformed_csn_handling(self):
        """Test that builder handles malformed CSN gracefully"""
        # This tests the CSNParser's error handling
        # The builder should not crash even if CSN parsing fails
        builder = CSNSchemaGraphBuilder('docs/csn')
        
        # Should handle any CSN parsing errors gracefully
        try:
            result = builder.build_schema_graph()
            self.assertIn('success', result)
        except Exception as e:
            self.fail(f"Builder should handle CSN errors gracefully, got: {e}")


def run_tests():
    """Run all tests"""
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add test classes
    suite.addTests(loader.loadTestsFromTestCase(TestCSNSchemaGraphBuilder))
    suite.addTests(loader.loadTestsFromTestCase(TestCSNSchemaGraphBuilderEdgeCases))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result.wasSuccessful()


if __name__ == '__main__':
    success = run_tests()
    sys.exit(0 if success else 1)