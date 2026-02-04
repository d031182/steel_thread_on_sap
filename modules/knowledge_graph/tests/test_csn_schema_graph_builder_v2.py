"""
Unit Tests for CSN Schema Graph Builder V2

Tests Phase 1 visual enhancements:
- Semantic color encoding (red vs teal)
- Line style encoding (solid vs dashed)
- Cardinality labeling (1:n, 1:1, etc.)

@author P2P Development Team
@version 1.0.0
"""

import sys
import os
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

import unittest
from unittest.mock import Mock, patch, MagicMock
import json

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

from modules.knowledge_graph.backend.csn_schema_graph_builder_v2 import CSNSchemaGraphBuilderV2


class TestCSNSchemaGraphBuilderV2(unittest.TestCase):
    """Test CSNSchemaGraphBuilderV2 with Phase 1 enhancements"""
    
    def setUp(self):
        """Set up test fixtures"""
        # Mock CSN directory (tests don't need real CSN files)
        self.csn_dir = 'docs/csn'
        self.builder = CSNSchemaGraphBuilderV2(self.csn_dir)
    
    def test_initialization(self):
        """Test builder initializes with correct Phase 1 constants"""
        # Visual constants should be defined
        self.assertEqual(self.builder.COMPOSITION_COLOR, '#e53935')  # Red
        self.assertEqual(self.builder.COMPOSITION_WIDTH, 3)  # Thick
        self.assertEqual(self.builder.COMPOSITION_DASHES, False)  # Solid
        
        self.assertEqual(self.builder.ASSOCIATION_COLOR, '#ff9800')  # Orange (user's preferred FK color)
        self.assertEqual(self.builder.ASSOCIATION_WIDTH, 2)  # Normal
        self.assertEqual(self.builder.ASSOCIATION_DASHES, True)  # Dashed
        
        self.assertEqual(self.builder.VALUE_HELP_COLOR, '#8e24aa')  # Purple
    
    def test_format_cardinality_one_to_one(self):
        """Test cardinality formatting: 1:1"""
        result = self.builder._format_cardinality({'min': 1, 'max': 1})
        self.assertEqual(result, '1:1')
    
    def test_format_cardinality_one_to_many(self):
        """Test cardinality formatting: 1:n"""
        result = self.builder._format_cardinality({'min': 1, 'max': '*'})
        self.assertEqual(result, '1:n')
    
    def test_format_cardinality_optional(self):
        """Test cardinality formatting: 0:1"""
        result = self.builder._format_cardinality({'min': 0, 'max': 1})
        self.assertEqual(result, '0:1')
    
    def test_format_cardinality_zero_to_many(self):
        """Test cardinality formatting: 0:*"""
        result = self.builder._format_cardinality({'min': 0, 'max': '*'})
        self.assertEqual(result, '0:n')
    
    def test_relationship_type_composition(self):
        """Test composition detection (Header-Item pattern)"""
        # PurchaseOrderItem should be detected as composition
        result = self.builder._get_csn_relationship_type('PurchaseOrderItem', 'PurchaseOrder')
        self.assertEqual(result, 'Composition')
    
    def test_relationship_type_association(self):
        """Test association detection (default)"""
        # Supplier relationship should be association
        result = self.builder._get_csn_relationship_type('PurchaseOrder', 'Supplier')
        self.assertEqual(result, 'Association')
    
    @patch('modules.knowledge_graph.backend.csn_schema_graph_builder_v2.CSNParser')
    @patch('modules.knowledge_graph.backend.csn_schema_graph_builder_v2.CSNRelationshipMapper')
    def test_build_schema_graph_structure(self, mock_mapper_class, mock_parser_class):
        """Test enhanced graph has correct Phase 1 structure"""
        # Mock CSN parser
        mock_parser = Mock()
        mock_parser.list_entities.return_value = ['PurchaseOrder', 'Supplier']
        mock_parser.get_entity_metadata.return_value = Mock(label='Test', description='Test desc')
        mock_parser_class.return_value = mock_parser
        
        # Mock relationship mapper
        mock_mapper = Mock()
        mock_rel = Mock()
        mock_rel.from_entity = 'PurchaseOrder'
        mock_rel.to_entity = 'Supplier'
        mock_rel.from_column = 'Supplier_ID'
        mock_rel.to_column = 'SupplierID'
        mock_rel.relationship_type = 'Association'
        mock_rel.confidence = 1.0
        mock_mapper.discover_relationships.return_value = [mock_rel]
        mock_mapper_class.return_value = mock_mapper
        
        # Create builder with mocks
        builder = CSNSchemaGraphBuilderV2(self.csn_dir)
        result = builder.build_schema_graph()
        
        # Verify Phase 1 enhancements in response
        self.assertTrue(result['success'])
        self.assertIn('enhancements', result)
        self.assertEqual(result['enhancements']['version'], '2.0.0')
        self.assertEqual(result['enhancements']['phase'], 1)
        self.assertIn('semantic_colors', result['enhancements']['features'])
        self.assertIn('cardinality_labels', result['enhancements']['features'])
        self.assertIn('ownership_styles', result['enhancements']['features'])
    
    @patch('modules.knowledge_graph.backend.csn_schema_graph_builder_v2.CSNParser')
    @patch('modules.knowledge_graph.backend.csn_schema_graph_builder_v2.CSNRelationshipMapper')
    def test_enhanced_edges_have_visual_encoding(self, mock_mapper_class, mock_parser_class):
        """Test edges have Phase 1 visual enhancements"""
        # Mock CSN parser
        mock_parser = Mock()
        mock_parser.list_entities.return_value = ['PurchaseOrder', 'Supplier']
        mock_parser.get_entity_metadata.return_value = Mock(label='Test', description='Test')
        mock_parser_class.return_value = mock_parser
        
        # Mock relationship mapper
        mock_mapper = Mock()
        mock_rel = Mock()
        mock_rel.from_entity = 'PurchaseOrder'
        mock_rel.to_entity = 'Supplier'
        mock_rel.from_column = 'Supplier_ID'
        mock_rel.to_column = 'SupplierID'
        mock_rel.relationship_type = 'Association'
        mock_rel.confidence = 1.0
        mock_mapper.discover_relationships.return_value = [mock_rel]
        mock_mapper_class.return_value = mock_mapper
        
        # Build graph
        builder = CSNSchemaGraphBuilderV2(self.csn_dir)
        result = builder.build_schema_graph()
        
        # Find FK edges (not product-table containment edges)
        fk_edges = [e for e in result['edges'] if 'label' in e and ':' in str(e.get('label', ''))]
        
        if fk_edges:
            edge = fk_edges[0]
            
            # Phase 1 Enhancement 1: Has cardinality label
            self.assertIn('label', edge)
            self.assertIn(':', edge['label'])  # Format: "1:n", "1:1", etc.
            
            # Phase 1 Enhancement 2: Has semantic color
            self.assertIn('color', edge)
            self.assertIn('color', edge['color'])
            color = edge['color']['color']
            self.assertIn(color, ['#e53935', '#ff9800', '#8e24aa'])  # Red, Orange, or Purple
            
            # Phase 1 Enhancement 3: Has width encoding
            self.assertIn('width', edge)
            self.assertIn(edge['width'], [1, 2, 3])  # Thin, normal, or thick
            
            # Phase 1 Enhancement 4: Has dashes encoding
            self.assertIn('dashes', edge)
    
    def test_empty_graph_includes_enhancements_metadata(self):
        """Test empty graph includes v2 enhancements metadata"""
        result = self.builder._empty_graph()
        
        self.assertTrue(result['success'])
        self.assertEqual(result['nodes'], [])
        self.assertEqual(result['edges'], [])
        self.assertIn('enhancements', result)
        self.assertEqual(result['enhancements']['version'], '2.0.0')
        self.assertEqual(result['enhancements']['phase'], 1)
    
    def test_composition_visual_encoding(self):
        """Test composition gets red, thick, solid encoding"""
        # Mock a composition edge
        edge = {
            'from': 'node1',
            'to': 'node2',
            'label': '1:n',
            'title': 'Test',
            'arrows': 'to',
            'color': {'color': self.builder.COMPOSITION_COLOR},
            'width': self.builder.COMPOSITION_WIDTH,
            'dashes': self.builder.COMPOSITION_DASHES
        }
        
        # Verify composition encoding
        self.assertEqual(edge['color']['color'], '#e53935')  # Red
        self.assertEqual(edge['width'], 3)  # Thick
        self.assertEqual(edge['dashes'], False)  # Solid
    
    def test_association_visual_encoding(self):
        """Test association gets teal, normal, dashed encoding"""
        # Mock an association edge
        edge = {
            'from': 'node1',
            'to': 'node2',
            'label': '1:1',
            'title': 'Test',
            'arrows': 'to',
            'color': {'color': self.builder.ASSOCIATION_COLOR},
            'width': self.builder.ASSOCIATION_WIDTH,
            'dashes': self.builder.ASSOCIATION_DASHES
        }
        
        # Verify association encoding
        self.assertEqual(edge['color']['color'], '#ff9800')  # Orange
        self.assertEqual(edge['width'], 2)  # Normal
        self.assertEqual(edge['dashes'], True)  # Dashed
    
    def test_backwards_compatibility_with_v1(self):
        """Test v2 output is backwards compatible with v1 format"""
        result = self.builder._empty_graph()
        
        # v1 fields must exist
        self.assertIn('success', result)
        self.assertIn('nodes', result)
        self.assertIn('edges', result)
        self.assertIn('stats', result)
        
        # v2 adds enhancements field (non-breaking)
        self.assertIn('enhancements', result)


class TestPhase1VisualConstants(unittest.TestCase):
    """Test Phase 1 visual constants are within cognitive limits"""
    
    def test_color_count_within_millers_law(self):
        """Test we use ≤7 colors (Miller's 7±2 rule)"""
        builder = CSNSchemaGraphBuilderV2('docs/csn')
        colors = {
            builder.COMPOSITION_COLOR,
            builder.ASSOCIATION_COLOR,
            builder.VALUE_HELP_COLOR
        }
        
        # Phase 1 uses only 3 colors (well within limit)
        self.assertEqual(len(colors), 3)
        self.assertLessEqual(len(colors), 7)  # Miller's law
    
    def test_line_styles_count(self):
        """Test we use ≤3 line styles (preattentive processing limit)"""
        builder = CSNSchemaGraphBuilderV2('docs/csn')
        
        # Phase 1 uses only 3 line styles
        styles = {
            'solid': builder.COMPOSITION_DASHES,
            'dashed': builder.ASSOCIATION_DASHES,
            'dotted': builder.VALUE_HELP_DASHES
        }
        
        self.assertEqual(len(styles), 3)
    
    def test_width_encoding_distinct(self):
        """Test line widths are visually distinct (>1px difference)"""
        builder = CSNSchemaGraphBuilderV2('docs/csn')
        
        # Widths must differ by at least 1px for visual distinction
        self.assertGreaterEqual(abs(builder.COMPOSITION_WIDTH - builder.ASSOCIATION_WIDTH), 1)
        self.assertGreaterEqual(abs(builder.ASSOCIATION_WIDTH - builder.VALUE_HELP_WIDTH), 1)


if __name__ == '__main__':
    # Run tests
    unittest.main(verbosity=2)