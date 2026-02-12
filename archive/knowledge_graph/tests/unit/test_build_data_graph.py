"""
Unit tests for DataGraphBuilder.build_data_graph() method

Tests the most complex function in the codebase (complexity 43).
Covers data-level graph construction with FK relationships.

@author P2P Development Team  
@version 1.0.0
@date 2026-02-05
"""

import pytest
from unittest.mock import Mock, MagicMock, patch
from modules.knowledge_graph.backend.data_graph_builder import DataGraphBuilder


@pytest.mark.unit
@pytest.mark.fast
class TestBuildDataGraph:
    """Test suite for build_data_graph() method"""
    
    def test_build_data_graph_success_simple_keys(self):
        """Test successful data graph building with simple primary keys
        
        ARRANGE: Mock data source with simple PK tables (Supplier, Product)
        ACT: Call build_data_graph()
        ASSERT: Returns nodes, edges, and correct statistics
        """
        # ARRANGE
        mock_data_source = Mock()
        
        # Mock get_data_products() -> returns 2 products
        mock_data_source.get_data_products.return_value = [
            {'productName': 'Supplier', 'schemaName': 'Supplier', 'displayName': 'Supplier Master'},
            {'productName': 'Product', 'schemaName': 'Product', 'displayName': 'Product Catalog'}
        ]
        
        # Mock get_tables() -> returns tables for each product
        def mock_get_tables(schema):
            if schema == 'Supplier':
                return [{'TABLE_NAME': 'Supplier'}]
            elif schema == 'Product':
                return [{'TABLE_NAME': 'Product'}]
            return []
        mock_data_source.get_tables.side_effect = mock_get_tables
        
        # Mock get_table_structure() -> returns PK column
        def mock_get_structure(schema, table):
            if table == 'Supplier':
                return [{'COLUMN_NAME': 'Supplier'}]
            elif table == 'Product':
                return [{'COLUMN_NAME': 'Product'}]
            return []
        mock_data_source.get_table_structure.side_effect = mock_get_structure
        
        # Mock execute_query() -> returns sample records
        def mock_execute_query(query):
            if 'Supplier' in query:
                return {
                    'success': True,
                    'rows': [
                        {'Supplier': '1000', 'Name': 'ACME Corp'},
                        {'Supplier': '2000', 'Name': 'Global Inc'}
                    ]
                }
            elif 'Product' in query:
                return {
                    'success': True,
                    'rows': [
                        {'Product': 'P-100', 'Description': 'Widget'},
                        {'Product': 'P-200', 'Description': 'Gadget'}
                    ]
                }
            return {'success': False}
        mock_data_source.execute_query.side_effect = mock_execute_query
        
        builder = DataGraphBuilder(mock_data_source)
        
        # ACT
        result = builder.build_data_graph(max_records_per_table=20, filter_orphans=False)
        
        # ASSERT
        assert result['success'] is True
        assert len(result['nodes']) == 4  # 2 Supplier + 2 Product records
        assert 'stats' in result
        assert result['stats']['node_count'] == 4
        assert result['stats']['table_count'] == 2
        
        # Verify node structure
        node_ids = [n['id'] for n in result['nodes']]
        assert any('Supplier-1000' in nid for nid in node_ids)
        assert any('Product-P-100' in nid for nid in node_ids)
    
    def test_build_data_graph_compound_primary_keys(self):
        """Test data graph with compound primary keys (SAP pattern)
        
        ARRANGE: Mock JournalEntry table with compound PK (CompanyCode, FiscalYear, AccountingDocument)
        ACT: Call build_data_graph()
        ASSERT: Nodes use compound key format "1010-2024-100001"
        """
        # ARRANGE
        mock_data_source = Mock()
        
        mock_data_source.get_data_products.return_value = [
            {'productName': 'JournalEntry', 'schemaName': 'JournalEntry', 'displayName': 'Journal Entries'}
        ]
        
        mock_data_source.get_tables.return_value = [{'TABLE_NAME': 'JournalEntry'}]
        
        # Compound PK structure
        mock_data_source.get_table_structure.return_value = [
            {'COLUMN_NAME': 'CompanyCode'},
            {'COLUMN_NAME': 'FiscalYear'},
            {'COLUMN_NAME': 'AccountingDocument'},
            {'COLUMN_NAME': 'Amount'}
        ]
        
        # Sample record with compound key
        mock_data_source.execute_query.return_value = {
            'success': True,
            'rows': [
                {'CompanyCode': '1010', 'FiscalYear': '2024', 'AccountingDocument': '100001', 'Amount': 1000.00}
            ]
        }
        
        builder = DataGraphBuilder(mock_data_source)
        
        # ACT
        result = builder.build_data_graph(max_records_per_table=20, filter_orphans=False)
        
        # ASSERT
        assert result['success'] is True
        assert len(result['nodes']) == 1
        
        # Verify compound key format
        node = result['nodes'][0]
        assert '1010-2024-100001' in node['id']  # Compound key format
        assert 'CompanyCode' in node['label']
        assert '1010' in node['label']  # Shows first PK component
    
    def test_build_data_graph_orphan_filtering(self):
        """Test orphan node filtering (nodes with zero connections)
        
        ARRANGE: Mock 3 tables, only 2 have FK relationships
        ACT: Call build_data_graph(filter_orphans=True)
        ASSERT: Orphan nodes filtered out, stats show filtered count
        """
        # ARRANGE
        mock_data_source = Mock()
        
        mock_data_source.get_data_products.return_value = [
            {'productName': 'Supplier', 'schemaName': 'Supplier'},
            {'productName': 'PurchaseOrder', 'schemaName': 'PurchaseOrder'},
            {'productName': 'Orphan', 'schemaName': 'Orphan'}
        ]
        
        def mock_get_tables(schema):
            return [{'TABLE_NAME': schema}]  # Table name = schema name
        mock_data_source.get_tables.side_effect = mock_get_tables
        
        def mock_get_structure(schema, table):
            return [{'COLUMN_NAME': table}]  # PK = table name
        mock_data_source.get_table_structure.side_effect = mock_get_structure
        
        def mock_execute_query(query):
            if 'Supplier' in query:
                return {'success': True, 'rows': [{'Supplier': '1000'}]}
            elif 'PurchaseOrder' in query:
                return {'success': True, 'rows': [{'PurchaseOrder': 'PO-001', 'Supplier': '1000'}]}
            elif 'Orphan' in query:
                return {'success': True, 'rows': [{'Orphan': 'O-001'}]}
            return {'success': False}
        mock_data_source.execute_query.side_effect = mock_execute_query
        
        builder = DataGraphBuilder(mock_data_source)
        
        # Mock FK discovery to create edge between Supplier and PurchaseOrder
        builder._fk_cache = {
            'PurchaseOrder': [('Supplier', 'Supplier')],
            'Orphan': []  # No FKs
        }
        
        # ACT
        result = builder.build_data_graph(max_records_per_table=20, filter_orphans=True)
        
        # ASSERT
        assert result['success'] is True
        assert result['stats']['orphans_filtered'] == 1  # 1 orphan node removed
        assert result['stats']['total_nodes_before_filter'] == 3
        assert result['stats']['node_count'] == 2  # Only connected nodes remain
    
    def test_build_data_graph_no_data_products(self):
        """Test graceful handling when no data products exist
        
        ARRANGE: Mock data source returns empty product list
        ACT: Call build_data_graph()
        ASSERT: Returns success with empty nodes/edges and helpful message
        """
        # ARRANGE
        mock_data_source = Mock()
        mock_data_source.get_data_products.return_value = []
        
        builder = DataGraphBuilder(mock_data_source)
        
        # ACT
        result = builder.build_data_graph()
        
        # ASSERT
        assert result['success'] is True
        assert len(result['nodes']) == 0
        assert len(result['edges']) == 0
        assert result['stats']['node_count'] == 0
        assert 'message' in result
    
    def test_build_data_graph_no_records(self):
        """Test graceful handling when tables exist but have no data
        
        ARRANGE: Mock tables return empty result sets
        ACT: Call build_data_graph()
        ASSERT: Returns success with empty graph and appropriate message
        """
        # ARRANGE
        mock_data_source = Mock()
        
        mock_data_source.get_data_products.return_value = [
            {'productName': 'Supplier', 'schemaName': 'Supplier'}
        ]
        
        mock_data_source.get_tables.return_value = [{'TABLE_NAME': 'Supplier'}]
        mock_data_source.get_table_structure.return_value = [{'COLUMN_NAME': 'Supplier'}]
        
        # Empty result set
        mock_data_source.execute_query.return_value = {
            'success': True,
            'rows': []
        }
        
        builder = DataGraphBuilder(mock_data_source)
        
        # ACT
        result = builder.build_data_graph()
        
        # ASSERT
        assert result['success'] is True
        assert len(result['nodes']) == 0
        assert 'Data-level view requires tables with actual data' in result.get('message', '')
    
    def test_build_data_graph_fk_relationships(self):
        """Test FK relationship edge creation between records
        
        ARRANGE: Mock PurchaseOrder with FK to Supplier
        ACT: Call build_data_graph()
        ASSERT: Edge created from PO record to Supplier record
        """
        # ARRANGE
        mock_data_source = Mock()
        
        mock_data_source.get_data_products.return_value = [
            {'productName': 'Supplier', 'schemaName': 'Supplier'},
            {'productName': 'PurchaseOrder', 'schemaName': 'PurchaseOrder'}
        ]
        
        def mock_get_tables(schema):
            return [{'TABLE_NAME': schema}]
        mock_data_source.get_tables.side_effect = mock_get_tables
        
        def mock_get_structure(schema, table):
            if table == 'Supplier':
                return [{'COLUMN_NAME': 'Supplier'}]
            elif table == 'PurchaseOrder':
                return [{'COLUMN_NAME': 'PurchaseOrder'}, {'COLUMN_NAME': 'Supplier'}]
            return []
        mock_data_source.get_table_structure.side_effect = mock_get_structure
        
        def mock_execute_query(query):
            if 'Supplier' in query:
                return {'success': True, 'rows': [{'Supplier': '1000'}]}
            elif 'PurchaseOrder' in query:
                return {'success': True, 'rows': [{'PurchaseOrder': 'PO-001', 'Supplier': '1000'}]}
            return {'success': False}
        mock_data_source.execute_query.side_effect = mock_execute_query
        
        builder = DataGraphBuilder(mock_data_source)
        
        # Mock FK cache
        builder._fk_cache = {
            'PurchaseOrder': [('Supplier', 'Supplier')]
        }
        
        # ACT
        result = builder.build_data_graph(max_records_per_table=20, filter_orphans=False)
        
        # ASSERT
        assert result['success'] is True
        assert len(result['edges']) == 1
        
        edge = result['edges'][0]
        assert 'PurchaseOrder' in edge['from']
        assert 'Supplier' in edge['to']
        assert edge['label'] == 'Supplier'  # FK column name
    
    def test_build_data_graph_max_records_limit(self):
        """Test max_records_per_table parameter limits result set
        
        ARRANGE: Mock table with 100 records
        ACT: Call build_data_graph(max_records_per_table=5)
        ASSERT: Query uses LIMIT 5
        """
        # ARRANGE
        mock_data_source = Mock()
        
        mock_data_source.get_data_products.return_value = [
            {'productName': 'Supplier', 'schemaName': 'Supplier'}
        ]
        
        mock_data_source.get_tables.return_value = [{'TABLE_NAME': 'Supplier'}]
        mock_data_source.get_table_structure.return_value = [{'COLUMN_NAME': 'Supplier'}]
        
        # Mock execute_query to track LIMIT clause
        def mock_execute_query(query):
            assert 'LIMIT 5' in query  # Verify LIMIT is applied
            return {'success': True, 'rows': [{'Supplier': str(i)} for i in range(5)]}
        mock_data_source.execute_query.side_effect = mock_execute_query
        
        builder = DataGraphBuilder(mock_data_source)
        
        # ACT
        result = builder.build_data_graph(max_records_per_table=5, filter_orphans=False)
        
        # ASSERT
        assert result['success'] is True
        assert len(result['nodes']) <= 5  # Respects limit
    
    def test_build_data_graph_error_handling(self):
        """Test error handling when data source throws exception
        
        ARRANGE: Mock data source that raises exception
        ACT: Call build_data_graph()
        ASSERT: Returns success=False with error message
        """
        # ARRANGE
        mock_data_source = Mock()
        mock_data_source.get_data_products.side_effect = Exception("Database connection failed")
        
        builder = DataGraphBuilder(mock_data_source)
        
        # ACT
        result = builder.build_data_graph()
        
        # ASSERT
        assert result['success'] is False
        assert 'error' in result
        assert 'Database connection failed' in result['error']
        assert len(result['nodes']) == 0
        assert len(result['edges']) == 0
    
    def test_build_data_graph_cache_disabled(self):
        """Test that cache is currently disabled for data mode
        
        ARRANGE: Mock data source with db_path set
        ACT: Call build_data_graph(use_cache=True)
        ASSERT: Cache not used (rebuilds from source)
        """
        # ARRANGE
        mock_data_source = Mock()
        mock_data_source.get_data_products.return_value = [
            {'productName': 'Supplier', 'schemaName': 'Supplier'}
        ]
        mock_data_source.get_tables.return_value = [{'TABLE_NAME': 'Supplier'}]
        mock_data_source.get_table_structure.return_value = [{'COLUMN_NAME': 'Supplier'}]
        mock_data_source.execute_query.return_value = {
            'success': True,
            'rows': [{'Supplier': '1000'}]
        }
        
        builder = DataGraphBuilder(mock_data_source, db_path='test.db')
        
        # ACT
        result = builder.build_data_graph(use_cache=True, filter_orphans=False)
        
        # ASSERT
        assert result['success'] is True
        assert result['stats']['cache_used'] is False  # Cache disabled
        assert 'load_time_ms' in result['stats']
    
    def test_build_data_graph_color_assignment(self):
        """Test color assignment based on data product grouping
        
        ARRANGE: Mock multiple products with known color palette
        ACT: Call build_data_graph()
        ASSERT: Nodes colored by product (Supplier=blue, PurchaseOrder=orange)
        """
        # ARRANGE
        mock_data_source = Mock()
        
        mock_data_source.get_data_products.return_value = [
            {'productName': 'Supplier', 'schemaName': 'Supplier'},
            {'productName': 'PurchaseOrder', 'schemaName': 'PurchaseOrder'}
        ]
        
        def mock_get_tables(schema):
            return [{'TABLE_NAME': schema}]
        mock_data_source.get_tables.side_effect = mock_get_tables
        
        def mock_get_structure(schema, table):
            return [{'COLUMN_NAME': table}]
        mock_data_source.get_table_structure.side_effect = mock_get_structure
        
        def mock_execute_query(query):
            if 'Supplier' in query:
                return {'success': True, 'rows': [{'Supplier': '1000'}]}
            elif 'PurchaseOrder' in query:
                return {'success': True, 'rows': [{'PurchaseOrder': 'PO-001'}]}
            return {'success': False}
        mock_data_source.execute_query.side_effect = mock_execute_query
        
        builder = DataGraphBuilder(mock_data_source)
        
        # ACT
        result = builder.build_data_graph(max_records_per_table=20, filter_orphans=False)
        
        # ASSERT
        assert result['success'] is True
        
        # Find nodes by table
        supplier_node = next(n for n in result['nodes'] if 'Supplier' in n['id'])
        po_node = next(n for n in result['nodes'] if 'PurchaseOrder' in n['id'])
        
        # Verify colors are product-specific (not default gray)
        assert supplier_node['color']['background'] != '#90a4ae'  # Not default
        assert po_node['color']['background'] != '#90a4ae'  # Not default
        # Colors should be different products
        assert supplier_node['color']['background'] != po_node['color']['background']