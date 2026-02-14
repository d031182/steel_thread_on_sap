"""
Data Products V2 API Contract Tests
====================================

Tests the API contracts that DataProductsV2Adapter depends on.

Following HIGH-16 breakthrough: Test frontend APIs FIRST (< 1s) before testing UI.

Test Coverage:
- List Data Products → GET /api/data-products/
- Get Tables → GET /api/data-products/<product_name>/tables
- Get Table Structure → GET /api/data-products/<product_name>/<table_name>/structure
- Query Table → POST /api/data-products/<product_name>/<table_name>/query
- Error handling scenarios

@pytest.mark.e2e
@pytest.mark.app_v2
@pytest.mark.api_contract
"""

import pytest
import requests
from typing import Dict, Any


class TestDataProductsV2APIContracts:
    """
    Test API contracts for Data Products V2 module.
    
    Philosophy: "Test the API before testing the UI" (HIGH-16)
    Speed: < 1 second per test (60-300x faster than browser)
    """
    
    @pytest.fixture
    def base_url(self) -> str:
        """Base URL for Data Products V2 API"""
        return "http://localhost:5000/api/data-products"
    
    # ========================================
    # GET / - List Data Products
    # ========================================
    
    @pytest.mark.e2e
    @pytest.mark.app_v2
    @pytest.mark.api_contract
    def test_get_data_products_returns_valid_structure(self, base_url: str):
        """
        Test: GET / returns list of data products
        
        Frontend Dependency: DataProductsV2Adapter.getDataProducts()
        
        ARRANGE
        """
        url = base_url
        
        # ACT
        response = requests.get(url, timeout=5)
        
        # ASSERT
        assert response.status_code == 200, \
            f"List data products should return 200, got {response.status_code}"
        
        data = response.json()
        
        # Contract: Must have 'success' field
        assert 'success' in data, "Response must include 'success' field"
        assert data['success'] is True, "'success' must be true"
        
        # Contract: Must have 'data_products' array
        assert 'data_products' in data, "Response must include 'data_products' array"
        assert isinstance(data['data_products'], list), "'data_products' must be array"
        
        # Contract: If products exist, check structure
        if len(data['data_products']) > 0:
            product = data['data_products'][0]
            
            # Each product must have 'product_name' (ACTUAL API CONTRACT)
            assert 'product_name' in product, "Product must have 'product_name' field"
            assert isinstance(product['product_name'], str), "'product_name' must be string"
            
            # Each product should have 'description' (optional but expected)
            if 'description' in product:
                assert isinstance(product['description'], str), "'description' must be string"
    
    # ========================================
    # GET /<product_name>/tables - Get Tables
    # ========================================
    
    @pytest.mark.e2e
    @pytest.mark.app_v2
    @pytest.mark.api_contract
    def test_get_tables_returns_valid_structure(self, base_url: str):
        """
        Test: GET /<product_name>/tables returns table list
        
        Frontend Dependency: DataProductsV2Adapter.getTables()
        
        ARRANGE
        """
        # First get available data products
        products_response = requests.get(base_url, timeout=5)
        products = products_response.json()['data_products']
        
        if len(products) == 0:
            pytest.skip("No data products available for testing")
        
        product_name = products[0]['product_name']
        url = f"{base_url}/{product_name}/tables"
        
        # ACT
        response = requests.get(url, timeout=5)
        
        # ASSERT
        assert response.status_code == 200, \
            f"Get tables should return 200, got {response.status_code}"
        
        data = response.json()
        
        # Contract: Must have 'success' field
        assert 'success' in data, "Response must include 'success' field"
        assert data['success'] is True, "'success' must be true"
        
        # Contract: Must have 'tables' array
        assert 'tables' in data, "Response must include 'tables' array"
        assert isinstance(data['tables'], list), "'tables' must be array"
        
        # Contract: If tables exist, check structure
        if len(data['tables']) > 0:
            table = data['tables'][0]
            
            # Each table must have 'table_name' (ACTUAL API CONTRACT)
            assert 'table_name' in table, "Table must have 'table_name' field"
            assert isinstance(table['table_name'], str), "'table_name' must be string"
    
    @pytest.mark.e2e
    @pytest.mark.app_v2
    @pytest.mark.api_contract
    def test_get_tables_nonexistent_product_returns_gracefully(self, base_url: str):
        """
        Test: GET /<nonexistent_product>/tables returns gracefully
        
        Frontend Dependency: DataProductsV2Adapter error handling
        
        NOTE: API returns 200 with empty tables array (graceful handling)
        
        ARRANGE
        """
        url = f"{base_url}/nonexistent_product_12345/tables"
        
        # ACT
        response = requests.get(url, timeout=5)
        
        # ASSERT (API design: graceful handling, not 404)
        assert response.status_code == 200, \
            f"Nonexistent product returns gracefully, got {response.status_code}"
        
        data = response.json()
        assert 'tables' in data, "Response must include 'tables' array"
        assert len(data['tables']) == 0, "Nonexistent product should return empty tables"
    
    # ========================================
    # GET /<product>/<table>/structure - Get Table Structure
    # ========================================
    
    @pytest.mark.e2e
    @pytest.mark.app_v2
    @pytest.mark.api_contract
    def test_get_table_structure_returns_valid_structure(self, base_url: str):
        """
        Test: GET /<product>/<table>/structure returns column info
        
        Frontend Dependency: DataProductsV2Adapter.getTableStructure()
        
        ARRANGE
        """
        # Get first available product and table
        products_response = requests.get(base_url, timeout=5)
        products = products_response.json()['data_products']
        
        if len(products) == 0:
            pytest.skip("No data products available")
        
        product_name = products[0]['product_name']
        tables_response = requests.get(f"{base_url}/{product_name}/tables", timeout=5)
        tables = tables_response.json()['tables']
        
        if len(tables) == 0:
            pytest.skip("No tables available in product")
        
        table_name = tables[0]['table_name']
        url = f"{base_url}/{product_name}/{table_name}/structure"
        
        # ACT
        response = requests.get(url, timeout=5)
        
        # ASSERT
        assert response.status_code == 200, \
            f"Get structure should return 200, got {response.status_code}"
        
        data = response.json()
        
        # Contract: Must have 'success' field
        assert 'success' in data, "Response must include 'success' field"
        assert data['success'] is True, "'success' must be true"
        
        # Contract: Must have 'columns' array (ACTUAL API CONTRACT)
        assert 'columns' in data, "Response must include 'columns' array"
        assert isinstance(data['columns'], list), "'columns' must be array"
        
        # Contract: If columns exist, check structure
        if len(data['columns']) > 0:
            column = data['columns'][0]
            
            # Each column must have 'column_name' (ACTUAL API CONTRACT)
            assert 'column_name' in column, "Column must have 'column_name' field"
            
            # Each column must have 'data_type' (ACTUAL API CONTRACT)
            assert 'data_type' in column, "Column must have 'data_type' field"
    
    # ========================================
    # POST /<product>/<table>/query - Query Table
    # ========================================
    
    @pytest.mark.e2e
    @pytest.mark.app_v2
    @pytest.mark.api_contract
    def test_post_query_table_returns_valid_structure(self, base_url: str):
        """
        Test: POST /<product>/<table>/query executes query
        
        Frontend Dependency: DataProductsV2Adapter.queryTable()
        
        ARRANGE
        """
        # Get first available product and table
        products_response = requests.get(base_url, timeout=5)
        products = products_response.json()['data_products']
        
        if len(products) == 0:
            pytest.skip("No data products available")
        
        product_name = products[0]['product_name']
        tables_response = requests.get(f"{base_url}/{product_name}/tables", timeout=5)
        tables = tables_response.json()['tables']
        
        if len(tables) == 0:
            pytest.skip("No tables available in product")
        
        table_name = tables[0]['table_name']
        url = f"{base_url}/{product_name}/{table_name}/query"
        
        # Simple SELECT query
        payload = {
            "limit": 10
        }
        
        # ACT
        response = requests.post(url, json=payload, timeout=10)
        
        # ASSERT
        assert response.status_code == 200, \
            f"Query table should return 200, got {response.status_code}"
        
        data = response.json()
        
        # Contract: Must have 'success' field
        assert 'success' in data, "Response must include 'success' field"
        assert data['success'] is True, "'success' must be true"
        
        # Contract: Must have 'rows' array (query results - ACTUAL API CONTRACT)
        assert 'rows' in data, "Response must include 'rows' array"
        assert isinstance(data['rows'], list), "'rows' must be array"
        
        # Contract: Must have 'totalCount' field (ACTUAL API CONTRACT)
        assert 'totalCount' in data, "Response must include 'totalCount' field"
        assert isinstance(data['totalCount'], int), "'totalCount' must be integer"
    
    @pytest.mark.e2e
    @pytest.mark.app_v2
    @pytest.mark.api_contract
    def test_post_query_accepts_optional_params(self, base_url: str):
        """
        Test: POST /<product>/<table>/query accepts optional parameters
        
        Frontend Dependency: DataProductsV2Adapter query flexibility
        
        NOTE: API design allows optional fields (graceful handling)
        
        ARRANGE
        """
        # Use any product/table combination
        url = f"{base_url}/PurchaseOrder/PurchaseOrder/query"
        
        # Optional params (API handles gracefully)
        payload = {
            "limit": 5
        }
        
        # ACT
        response = requests.post(url, json=payload, timeout=5)
        
        # ASSERT (API design: accept optional params gracefully)
        assert response.status_code == 200, \
            f"Query with optional params should succeed, got {response.status_code}"


# ========================================
# Integration Test: Full Workflow
# ========================================

class TestDataProductsV2Workflow:
    """
    Test complete workflow that DataProductsV2Adapter orchestrates.
    
    Validates: List → GetTables → GetStructure → Query sequence
    """
    
    @pytest.mark.e2e
    @pytest.mark.app_v2
    @pytest.mark.api_contract
    def test_complete_data_products_workflow(self):
        """
        Test: Complete data products workflow
        
        Simulates: User navigating data products module
        
        ARRANGE
        """
        base_url = "http://localhost:5000/api/data-products"
        
        # ACT & ASSERT: Step 1 - List products
        products_response = requests.get(base_url, timeout=5)
        assert products_response.status_code == 200
        products_data = products_response.json()
        assert products_data['success'] is True
        assert len(products_data['data_products']) > 0, "Should have at least one product"
        
        # Get first product
        product_name = products_data['data_products'][0]['product_name']
        
        # ACT & ASSERT: Step 2 - Get tables
        tables_response = requests.get(f"{base_url}/{product_name}/tables", timeout=5)
        assert tables_response.status_code == 200
        tables_data = tables_response.json()
        assert tables_data['success'] is True
        assert len(tables_data['tables']) > 0, "Product should have at least one table"
        
        # Get first table
        table_name = tables_data['tables'][0]['table_name']
        
        # ACT & ASSERT: Step 3 - Get table structure
        structure_response = requests.get(
            f"{base_url}/{product_name}/{table_name}/structure",
            timeout=5
        )
        assert structure_response.status_code == 200
        structure_data = structure_response.json()
        assert structure_data['success'] is True
        assert len(structure_data['columns']) > 0, "Table should have columns"
        
        # ACT & ASSERT: Step 4 - Query table (limit 5 rows)
        query_response = requests.post(
            f"{base_url}/{product_name}/{table_name}/query",
            json={"limit": 5},
            timeout=10
        )
        assert query_response.status_code == 200
        query_data = query_response.json()
        assert query_data['success'] is True
        assert 'rows' in query_data, "Response should have 'rows'"
        assert query_data['totalCount'] >= 0, "totalCount should be non-negative"
