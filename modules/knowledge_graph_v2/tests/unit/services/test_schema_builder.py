"""
Unit Tests for SchemaGraphBuilderService

Tests schema graph building with mocked CSN parser.
"""
import pytest
from unittest.mock import Mock, MagicMock
from modules.knowledge_graph_v2.services.schema_graph_builder_service import SchemaGraphBuilderService
from modules.knowledge_graph_v2.domain import Graph, GraphType, NodeType, EdgeType


class MockEntityMetadata:
    """Mock CSN entity metadata"""
    def __init__(self, label=None):
        self.label = label


class MockRelationship:
    """Mock CSN relationship"""
    def __init__(self, from_entity, to_entity, from_column):
        self.from_entity = from_entity
        self.to_entity = to_entity
        self.from_column = from_column


@pytest.fixture
def mock_csn_parser():
    """Create mock CSN parser"""
    parser = Mock()
    parser.list_entities = Mock(return_value=[])
    parser.get_entity_metadata = Mock(return_value=None)
    return parser


@pytest.fixture
def mock_relationship_mapper(monkeypatch):
    """Mock RelationshipMapper globally"""
    mock_mapper = Mock()
    mock_mapper.discover_relationships = Mock(return_value=[])
    
    # Patch the import in schema_graph_builder_service
    monkeypatch.setattr(
        'modules.knowledge_graph_v2.services.schema_graph_builder_service.CSNRelationshipMapper',
        lambda csn_parser: mock_mapper
    )
    return mock_mapper


@pytest.mark.unit
@pytest.mark.fast
class TestSchemaBuilderInitialization:
    """Test service initialization"""
    
    def test_init_succeeds(self, mock_csn_parser, mock_relationship_mapper):
        """Test service initializes with CSN parser"""
        # ACT
        service = SchemaGraphBuilderService(mock_csn_parser)
        
        # ASSERT
        assert service.csn_parser == mock_csn_parser
        assert service.relationship_mapper is not None


@pytest.mark.unit
@pytest.mark.fast
class TestSchemaBuilderEmptyCSN:
    """Test handling of empty CSN files"""
    
    def test_build_with_no_entities_returns_empty_graph(
        self, mock_csn_parser, mock_relationship_mapper
    ):
        """Test building with no CSN entities returns empty graph"""
        # ARRANGE
        mock_csn_parser.list_entities.return_value = []
        service = SchemaGraphBuilderService(mock_csn_parser)
        
        # ACT
        graph = service.build_from_csn()
        
        # ASSERT
        assert isinstance(graph, Graph)
        assert graph.type == GraphType.SCHEMA
        assert len(graph.nodes) == 0
        assert len(graph.edges) == 0


@pytest.mark.unit
@pytest.mark.fast
class TestSchemaBuilderSingleProduct:
    """Test building graph with single product"""
    
    def test_build_single_product_with_one_table(
        self, mock_csn_parser, mock_relationship_mapper
    ):
        """Test building graph with one product and one table"""
        # ARRANGE
        mock_csn_parser.list_entities.return_value = ['CompanyCode']
        mock_csn_parser.get_entity_metadata.return_value = MockEntityMetadata('Company Code')
        
        service = SchemaGraphBuilderService(mock_csn_parser)
        
        # ACT
        graph = service.build_from_csn()
        
        # ASSERT
        assert len(graph.nodes) == 2  # 1 product + 1 table
        assert len(graph.edges) == 1  # 1 containment edge
        
        # Verify product node
        product_node = graph.get_node('product-Company_Code')
        assert product_node is not None
        assert product_node.type == NodeType.PRODUCT
        assert product_node.label == 'Company_Code'
        
        # Verify table node
        table_node = graph.get_node('table-Company_Code-CompanyCode')
        assert table_node is not None
        assert table_node.type == NodeType.TABLE
        assert table_node.label == 'CompanyCode'
        
        # Verify containment edge
        edges = graph.edges
        assert edges[0].source_id == 'product-Company_Code'
        assert edges[0].target_id == 'table-Company_Code-CompanyCode'
        assert edges[0].type == EdgeType.CONTAINS


@pytest.mark.unit
@pytest.mark.fast
class TestSchemaBuilderMultipleProducts:
    """Test building graph with multiple products"""
    
    def test_build_multiple_products_with_tables(
        self, mock_csn_parser, mock_relationship_mapper
    ):
        """Test building graph with multiple products"""
        # ARRANGE
        mock_csn_parser.list_entities.return_value = [
            'PurchaseOrder', 'PurchaseOrderItem',
            'Supplier'
        ]
        mock_csn_parser.get_entity_metadata.return_value = MockEntityMetadata()
        
        service = SchemaGraphBuilderService(mock_csn_parser)
        
        # ACT
        graph = service.build_from_csn()
        
        # ASSERT
        # 2 products (Purchase_Order, Supplier) + 3 tables = 5 nodes
        assert len(graph.nodes) == 5
        
        # 3 containment edges (product → table)
        assert len(graph.edges) == 3
        
        # Verify products created
        assert graph.has_node('product-Purchase_Order')
        assert graph.has_node('product-Supplier')
        
        # Verify tables created
        assert graph.has_node('table-Purchase_Order-PurchaseOrder')
        assert graph.has_node('table-Purchase_Order-PurchaseOrderItem')
        assert graph.has_node('table-Supplier-Supplier')


@pytest.mark.unit
@pytest.mark.fast
class TestSchemaBuilderForeignKeys:
    """Test FK relationship discovery"""
    
    def test_build_with_foreign_keys_creates_edges(
        self, mock_csn_parser, mock_relationship_mapper
    ):
        """Test FK relationships create edges between tables"""
        # ARRANGE
        mock_csn_parser.list_entities.return_value = [
            'PurchaseOrder', 'Supplier'
        ]
        mock_csn_parser.get_entity_metadata.return_value = MockEntityMetadata()
        
        # Mock FK relationship: PurchaseOrder → Supplier
        mock_relationship_mapper.discover_relationships.return_value = [
            MockRelationship('PurchaseOrder', 'Supplier', 'SupplierID')
        ]
        
        service = SchemaGraphBuilderService(mock_csn_parser)
        
        # ACT
        graph = service.build_from_csn()
        
        # ASSERT
        # 2 products + 2 tables = 4 nodes
        assert len(graph.nodes) == 4
        
        # 2 containment + 1 FK = 3 edges
        assert len(graph.edges) == 3
        
        # Find FK edge
        fk_edges = [e for e in graph.edges if e.type == EdgeType.FOREIGN_KEY]
        assert len(fk_edges) == 1
        
        fk_edge = fk_edges[0]
        assert fk_edge.source_id == 'table-Purchase_Order-PurchaseOrder'
        assert fk_edge.target_id == 'table-Supplier-Supplier'
        assert fk_edge.label == 'SupplierID'
        assert fk_edge.properties['fk_column'] == 'SupplierID'
    
    def test_build_skips_self_referential_fks(
        self, mock_csn_parser, mock_relationship_mapper
    ):
        """Test self-referential FKs are skipped"""
        # ARRANGE
        mock_csn_parser.list_entities.return_value = ['CompanyCode']
        mock_csn_parser.get_entity_metadata.return_value = MockEntityMetadata()
        
        # Mock self-referential FK (should be skipped)
        mock_relationship_mapper.discover_relationships.return_value = [
            MockRelationship('CompanyCode', 'CompanyCode', 'ParentID')
        ]
        
        service = SchemaGraphBuilderService(mock_csn_parser)
        
        # ACT
        graph = service.build_from_csn()
        
        # ASSERT
        # Only containment edge, NO FK edge
        assert len(graph.edges) == 1
        assert graph.edges[0].type == EdgeType.CONTAINS


@pytest.mark.unit
@pytest.mark.fast
class TestSchemaBuilderGenericFormat:
    """Test service returns generic format (NOT vis.js)"""
    
    def test_nodes_use_generic_types(
        self, mock_csn_parser, mock_relationship_mapper
    ):
        """Test nodes use NodeType enum (not vis.js properties)"""
        # ARRANGE
        mock_csn_parser.list_entities.return_value = ['CompanyCode']
        mock_csn_parser.get_entity_metadata.return_value = MockEntityMetadata()
        
        service = SchemaGraphBuilderService(mock_csn_parser)
        
        # ACT
        graph = service.build_from_csn()
        
        # ASSERT
        product_node = graph.get_node('product-Company_Code')
        table_node = graph.get_node('table-Company_Code-CompanyCode')
        
        # Generic types (NOT vis.js properties like 'shape', 'color')
        assert product_node.type == NodeType.PRODUCT
        assert table_node.type == NodeType.TABLE
        
        # No vis.js properties
        assert 'shape' not in product_node.properties
        assert 'color' not in product_node.properties
        assert 'size' not in product_node.properties
    
    def test_edges_use_source_target_not_from_to(
        self, mock_csn_parser, mock_relationship_mapper
    ):
        """Test edges use generic 'source_id'/'target_id' (not vis.js 'from'/'to')"""
        # ARRANGE
        mock_csn_parser.list_entities.return_value = ['CompanyCode']
        mock_csn_parser.get_entity_metadata.return_value = MockEntityMetadata()
        
        service = SchemaGraphBuilderService(mock_csn_parser)
        
        # ACT
        graph = service.build_from_csn()
        
        # ASSERT
        edge = graph.edges[0]
        
        # Generic attributes (source_id, target_id)
        assert hasattr(edge, 'source_id')
        assert hasattr(edge, 'target_id')
        
        # NOT vis.js attributes (from, to)
        assert not hasattr(edge, 'from')
        assert not hasattr(edge, 'to')
        
        # No vis.js properties
        assert 'arrows' not in edge.properties
        assert 'dashes' not in edge.properties
        assert 'width' not in edge.properties


@pytest.mark.unit
@pytest.mark.fast
class TestSchemaBuilderStatistics:
    """Test graph statistics"""
    
    def test_statistics_reflect_correct_counts(
        self, mock_csn_parser, mock_relationship_mapper
    ):
        """Test graph statistics match actual structure"""
        # ARRANGE
        mock_csn_parser.list_entities.return_value = [
            'PurchaseOrder', 'PurchaseOrderItem', 'Supplier'
        ]
        mock_csn_parser.get_entity_metadata.return_value = MockEntityMetadata()
        
        service = SchemaGraphBuilderService(mock_csn_parser)
        
        # ACT
        graph = service.build_from_csn()
        stats = graph.get_statistics()
        
        # ASSERT
        assert stats['node_count'] == 5  # 2 products + 3 tables
        assert stats['edge_count'] == 3  # 3 containment edges
        assert stats['nodes_by_type']['product'] == 2
        assert stats['nodes_by_type']['table'] == 3