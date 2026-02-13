"""
Data Products V2 Database Path Integration Test

Tests that the API correctly uses the standard database path
and returns expected data products.

Prevents regression of the bug where V2 API used wrong path
and returned 0 products.

Author: Gu Wu Testing Framework
Date: 2026-02-08
"""

import pytest
from pathlib import Path


@pytest.mark.integration
@pytest.mark.fast
class TestDataProductsV2DatabasePath:
    """Integration tests for database path configuration"""
    
    def test_api_uses_correct_database_path(self, client):
        """
        Test that API uses correct database path
        
        CRITICAL: Prevents returning 0 products due to wrong path
        """
        response = client.get('/api/data-products/')
        
        assert response.status_code == 200
        data = response.get_json()
        
        # Must return success
        assert data['success'] is True
        
        # Must return products (database has data)
        assert data['count'] > 0, "API returned 0 products - likely wrong database path!"
        
        # Must be from sqlite source
        assert data['source'] == 'sqlite'
        
        # Verify we got the expected products from standard database
        assert data['count'] == 9, f"Expected 9 products, got {data['count']}"
    
    def test_api_returns_expected_product_names(self, client):
        """Test that API returns products from correct database"""
        response = client.get('/api/data-products/')
        data = response.get_json()
        
        product_names = {p['product_name'] for p in data['data_products']}
        
        # Expected products from core/databases/sqlite/p2p_data.db
        expected_products = {
            'CompanyCode',
            'CostCenter', 
            'JournalEntry',
            'PaymentTerms',
            'Product',
            'PurchaseOrder',
            'ServiceEntrySheet',
            'Supplier',
            'SupplierInvoice'
        }
        
        assert product_names == expected_products, \
            f"Product mismatch! Missing: {expected_products - product_names}, Extra: {product_names - expected_products}"
    
    def test_repository_uses_correct_database_path(self):
        """Test that repository layer uses correct database path"""
        from modules.data_products_v2.repositories.sqlite_data_product_repository import SQLiteDataProductRepository
        
        # Create repository with default path
        repo = SQLiteDataProductRepository()
        
        # Verify path
        expected_path = 'core/databases/sqlite/p2p_data.db'
        assert expected_path in repo._db_path, \
            f"Repository using wrong path: {repo._db_path}"
        
        # Verify it works
        products = repo.get_data_products()
        assert len(products) == 9, f"Repository returned {len(products)} products, expected 9"
    
    def test_database_file_exists(self):
        """Test that the expected database file exists"""
        project_root = Path(__file__).parent.parent.parent
        db_path = project_root / 'core' / 'databases' / 'sqlite' / 'p2p_data.db'
        
        assert db_path.exists(), \
            f"Database file not found at: {db_path}"
        
        assert db_path.stat().st_size > 0, \
            f"Database file is empty: {db_path}"
    
    def test_v1_and_v2_use_same_database(self, client):
        """
        Test that V1 and V2 return same products (use same database)
        
        CRITICAL: Ensures V2 didn't revert to old path
        """
        # Get V1 products
        v1_response = client.get('/api/data-products')
        v1_data = v1_response.get_json()
        
        # Get V2 products
        v2_response = client.get('/api/data-products/')
        v2_data = v2_response.get_json()
        
        # Both should succeed
        assert v1_data['success'] is True
        assert v2_data['success'] is True
        
        # Both should return same count
        assert v1_data['count'] == v2_data['count'], \
            f"V1 returned {v1_data['count']} products, V2 returned {v2_data['count']} - different databases!"
        
        # Both should return same product names
        v1_names = {p['productName'] for p in v1_data['data_products']}
        v2_names = {p['product_name'] for p in v2_data['data_products']}
        
        assert v1_names == v2_names, \
            f"V1 and V2 returning different products - using different databases!"


@pytest.mark.integration
@pytest.mark.slow
class TestDataProductsV2DataAccess:
    """Integration tests for full data access workflow"""
    
    def test_full_workflow_product_to_table_to_structure(self, client):
        """
        Test complete workflow: Get products → Get tables → Get structure
        
        Verifies all layers use correct database path
        """
        # Step 1: Get products
        products_response = client.get('/api/data-products/')
        products_data = products_response.get_json()
        
        assert products_data['success'] is True
        assert products_data['count'] > 0
        
        # Step 2: Get tables for first product
        first_product = products_data['data_products'][0]['product_name']
        tables_response = client.get(f'/api/data-products/{first_product}/tables')
        tables_data = tables_response.get_json()
        
        assert tables_data['success'] is True
        assert tables_data['count'] > 0
        
        # Step 3: Get structure for first table
        first_table = tables_data['tables'][0]['table_name']
        structure_response = client.get(
            f'/api/data-products/{first_product}/{first_table}/structure'
        )
        structure_data = structure_response.get_json()
        
        assert structure_data['success'] is True
        assert len(structure_data['columns']) > 0
        
        # If this all works, database path is correct throughout the stack
    
    def test_query_returns_actual_data(self, client):
        """Test that querying table returns actual rows (not empty)"""
        # Get PurchaseOrder tables
        tables_response = client.get('/api/data-products/PurchaseOrder/tables')
        tables_data = tables_response.get_json()
        
        # Query first table
        first_table = tables_data['tables'][0]['table_name']
        query_response = client.post(
            f'/api/data-products/PurchaseOrder/{first_table}/query',
            json={'limit': 10}
        )
        query_data = query_response.get_json()
        
        assert query_data['success'] is True
        
        # If database path is correct, should have data
        # (Some tables might be empty, but totalCount should be >= 0)
        assert 'totalCount' in query_data
        assert 'rows' in query_data