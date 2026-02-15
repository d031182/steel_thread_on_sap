"""
Data Products V2 Backend API Contract Tests

Tests API contracts for data_products_v2 module via HTTP.
Following Gu Wu methodology: Test API contracts, trust implementation.

Test Strategy:
- Test backend API endpoints via requests (< 1 second)
- Validate response structure (contract compliance)
- One API test validates entire call chain implicitly
- Mark with @pytest.mark.api_contract

Endpoints Tested:
- GET  /api/data-products      - List data products
- GET  /api/data-products/{product}/tables  - Get tables
- GET  /api/data-products/{product}/{table}/structure - Get structure
- POST /api/data-products/{product}/{table}/query - Query data

Author: P2P Development Team
Date: 2026-02-15
Version: 1.0.0
"""

import pytest
import requests
import time


# Test Configuration
API_PREFIX = "/api/data-products"


@pytest.mark.e2e
@pytest.mark.api_contract
def test_list_data_products_contract(flask_server, test_timeout):
    """
    Test: GET /api/data-products returns valid contract
    
    Validates:
    - HTTP 200 response
    - success field present
    - data_products array present
    - count field present
    - source field present
    
    Implicitly Tests:
    - DataProductsV2API blueprint
    - DataProductsFacade.get_data_products()
    - SqliteDataProductRepository (via facade)
    - Database query execution
    """
    # ARRANGE
    url = f"{flask_server}{API_PREFIX}/"
    params = {"source": "sqlite"}
    
    # ACT
    response = requests.get(url, params=params, timeout=test_timeout)
    
    # ASSERT - Contract structure
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"
    
    data = response.json()
    assert 'success' in data, "Response missing 'success' field"
    assert data['success'] is True, "API should return success=true"
    
    assert 'data_products' in data, "Response missing 'data_products' field"
    assert isinstance(data['data_products'], list), "data_products should be array"
    
    assert 'count' in data, "Response missing 'count' field"
    assert isinstance(data['count'], int), "count should be integer"
    
    assert 'source' in data, "Response missing 'source' field"
    assert data['source'] == 'sqlite', "source should match request"
    
    # If data exists, validate product structure
    if data['count'] > 0:
        product = data['data_products'][0]
        required_fields = [
            'product_name', 'display_name', 'namespace',
            'version', 'schema_name', 'source', 'table_count'
        ]
        for field in required_fields:
            assert field in product, f"Product missing '{field}' field"


@pytest.mark.e2e
@pytest.mark.api_contract
def test_list_data_products_invalid_source(flask_server, test_timeout):
    """
    Test: Invalid source parameter returns 400
    
    Validates:
    - HTTP 400 for invalid source
    - Error message present
    - success=false
    """
    # ARRANGE
    url = f"{flask_server}{API_PREFIX}/"
    params = {"source": "invalid"}
    
    # ACT
    response = requests.get(url, params=params, timeout=test_timeout)
    
    # ASSERT
    assert response.status_code == 400, "Invalid source should return 400"
    
    data = response.json()
    assert data['success'] is False, "Error response should have success=false"
    assert 'error' in data, "Error response should have 'error' field"


@pytest.mark.e2e
@pytest.mark.api_contract
def test_get_tables_contract(flask_server, test_timeout):
    """
    Test: GET /api/data-products/{product}/tables returns valid contract
    
    Validates:
    - HTTP 200 response
    - success field present
    - tables array present
    - count field present
    
    Implicitly Tests:
    - DataProductsFacade.get_tables()
    - SqliteDataProductRepository.get_tables_in_product()
    """
    # ARRANGE
    # First get a valid product name
    list_url = f"{flask_server}{API_PREFIX}/"
    list_response = requests.get(list_url, params={"source": "sqlite"}, timeout=test_timeout)
    
    # Skip if no products
    if list_response.json().get('count', 0) == 0:
        pytest.skip("No products available to test")
    
    product_name = list_response.json()['data_products'][0]['product_name']
    
    # ACT
    tables_url = f"{flask_server}{API_PREFIX}/{product_name}/tables"
    response = requests.get(tables_url, params={"source": "sqlite"}, timeout=test_timeout)
    
    # ASSERT - Contract structure
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"
    
    data = response.json()
    assert 'success' in data, "Response missing 'success' field"
    assert data['success'] is True, "API should return success=true"
    
    assert 'tables' in data, "Response missing 'tables' field"
    assert isinstance(data['tables'], list), "tables should be array"
    
    assert 'count' in data, "Response missing 'count' field"
    assert isinstance(data['count'], int), "count should be integer"
    
    # If tables exist, validate structure
    if data['count'] > 0:
        table = data['tables'][0]
        required_fields = ['table_name', 'table_type', 'schema_name']
        for field in required_fields:
            assert field in table, f"Table missing '{field}' field"


@pytest.mark.e2e
@pytest.mark.api_contract
def test_get_table_structure_contract(flask_server, test_timeout):
    """
    Test: GET /api/data-products/{product}/{table}/structure returns valid contract
    
    Validates:
    - HTTP 200 response
    - success field present
    - columns array present
    
    Implicitly Tests:
    - DataProductsFacade.get_table_structure()
    - SqliteDataProductRepository.get_table_structure()
    """
    # ARRANGE
    # Get a valid product and table
    list_url = f"{flask_server}{API_PREFIX}/"
    list_response = requests.get(list_url, params={"source": "sqlite"}, timeout=test_timeout)
    
    if list_response.json().get('count', 0) == 0:
        pytest.skip("No products available")
    
    product_name = list_response.json()['data_products'][0]['product_name']
    
    tables_url = f"{flask_server}{API_PREFIX}/{product_name}/tables"
    tables_response = requests.get(tables_url, params={"source": "sqlite"}, timeout=test_timeout)
    
    if tables_response.json().get('count', 0) == 0:
        pytest.skip("No tables available")
    
    table_name = tables_response.json()['tables'][0]['table_name']
    
    # ACT
    structure_url = f"{flask_server}{API_PREFIX}/{product_name}/{table_name}/structure"
    response = requests.get(structure_url, params={"source": "sqlite"}, timeout=test_timeout)
    
    # ASSERT - Contract structure
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"
    
    data = response.json()
    assert 'success' in data, "Response missing 'success' field"
    assert data['success'] is True, "API should return success=true"
    
    assert 'columns' in data, "Response missing 'columns' field"
    assert isinstance(data['columns'], list), "columns should be array"
    
    # Validate column structure
    if len(data['columns']) > 0:
        column = data['columns'][0]
        required_fields = ['column_name', 'data_type']
        for field in required_fields:
            assert field in column, f"Column missing '{field}' field"


@pytest.mark.e2e
@pytest.mark.api_contract
def test_query_table_contract(flask_server, test_timeout):
    """
    Test: POST /api/data-products/{product}/{table}/query returns valid contract
    
    Validates:
    - HTTP 200 response
    - success field present
    - rows array present
    - columns array present
    - executionTime present
    
    Implicitly Tests:
    - DataProductsFacade.query_table()
    - SqliteDataProductRepository.query_table_data()
    """
    # ARRANGE
    # Get valid product and table
    list_url = f"{flask_server}{API_PREFIX}/"
    list_response = requests.get(list_url, params={"source": "sqlite"}, timeout=test_timeout)
    
    if list_response.json().get('count', 0) == 0:
        pytest.skip("No products available")
    
    product_name = list_response.json()['data_products'][0]['product_name']
    
    tables_url = f"{flask_server}{API_PREFIX}/{product_name}/tables"
    tables_response = requests.get(tables_url, params={"source": "sqlite"}, timeout=test_timeout)
    
    if tables_response.json().get('count', 0) == 0:
        pytest.skip("No tables available")
    
    table_name = tables_response.json()['tables'][0]['table_name']
    
    # ACT
    query_url = f"{flask_server}{API_PREFIX}/{product_name}/{table_name}/query"
    payload = {"limit": 10, "offset": 0}
    response = requests.post(query_url, json=payload, params={"source": "sqlite"}, timeout=test_timeout)
    
    # ASSERT - Contract structure
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"
    
    data = response.json()
    assert 'success' in data, "Response missing 'success' field"
    assert data['success'] is True, "API should return success=true"
    
    assert 'rows' in data, "Response missing 'rows' field"
    assert isinstance(data['rows'], list), "rows should be array"
    
    assert 'columns' in data, "Response missing 'columns' field"
    assert isinstance(data['columns'], list), "columns should be array"
    
    assert 'executionTime' in data, "Response missing 'executionTime' field"


@pytest.mark.e2e
@pytest.mark.api_contract
def test_api_performance(flask_server, test_timeout):
    """
    Test: API responds within acceptable time (< 1 second for SQLite)
    
    Validates:
    - Response time < 1000ms for local SQLite
    - Fast enough for good UX
    """
    # ARRANGE
    url = f"{flask_server}{API_PREFIX}/"
    params = {"source": "sqlite"}
    
    # ACT
    start_time = time.time()
    response = requests.get(url, params=params, timeout=test_timeout)
    elapsed_ms = (time.time() - start_time) * 1000
    
    # ASSERT
    assert response.status_code == 200, "API should respond successfully"
    assert elapsed_ms < 1000, f"API too slow: {elapsed_ms:.0f}ms (should be < 1000ms)"


# Module Health Check
@pytest.mark.smoke
def test_module_health(flask_server, test_timeout):
    """
    Smoke test: Verify data_products_v2 module is loaded
    
    Quick check that module is registered and accessible.
    """
    # ARRANGE
    url = f"{flask_server}{API_PREFIX}/"
    
    # ACT
    response = requests.get(url, params={"source": "sqlite"}, timeout=test_timeout)
    
    # ASSERT
    assert response.status_code in [200, 503], \
        f"Module should respond (got {response.status_code})"
