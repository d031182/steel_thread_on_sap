"""
Data Products V2 Frontend API Contract Tests

Tests frontend metadata API contract for data_products_v2 module.
Following Gu Wu methodology: Test API contracts, trust implementation.

Test Strategy:
- Test frontend registry API via HTTP requests
- Validate module metadata structure
- Ensure data_products_v2 properly registered
- Mark with @pytest.mark.api_contract

Frontend API tested:
- GET /api/modules/frontend-registry - Should include data_products_v2

Author: P2P Development Team
Date: 2026-02-15
Version: 1.0.0
"""

import pytest
import requests


# Test Configuration
BASE_URL = "http://localhost:5000"
FRONTEND_API = "/api/modules/frontend-registry"
TIMEOUT = 5  # seconds


@pytest.mark.e2e
@pytest.mark.api_contract
def test_frontend_registry_includes_data_products_v2():
    """
    Test: Frontend registry includes data_products_v2 module metadata
    
    Validates:
    - HTTP 200 response
    - success field present
    - modules array contains data_products_v2
    - Module has required frontend metadata fields
    
    Implicitly Tests:
    - FrontendModuleRegistry service
    - Module.json parsing
    - Module discovery mechanism
    """
    # ARRANGE
    url = f"{BASE_URL}{FRONTEND_API}"
    
    # ACT
    response = requests.get(url, timeout=TIMEOUT)
    
    # ASSERT - Contract structure
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"
    
    data = response.json()
    assert 'success' in data, "Response missing 'success' field"
    assert data['success'] is True, "API should return success=true"
    
    assert 'modules' in data, "Response missing 'modules' array"
    assert isinstance(data['modules'], list), "modules should be array"
    
    # Find data_products_v2 module
    dp_module = None
    for module in data['modules']:
        if module.get('id') == 'data_products_v2':
            dp_module = module
            break
    
    assert dp_module is not None, "data_products_v2 module not found in registry"
    
    # Validate module metadata structure
    required_fields = ['id', 'name', 'version', 'frontend', 'backend']
    for field in required_fields:
        assert field in dp_module, f"Module missing '{field}' field"
    
    # Validate frontend metadata
    frontend = dp_module['frontend']
    assert 'scripts' in frontend, "Frontend missing 'scripts' field"
    assert isinstance(frontend['scripts'], list), "scripts should be array"
    assert len(frontend['scripts']) > 0, "scripts array should not be empty"


@pytest.mark.e2e
@pytest.mark.api_contract
def test_get_specific_module_data_products_v2():
    """
    Test: GET /api/modules/frontend-registry/data_products_v2 returns module
    
    Validates:
    - HTTP 200 response
    - Module metadata returned
    - success field present
    
    Implicitly Tests:
    - FrontendModuleRegistry.get_module_by_id()
    """
    # ARRANGE
    url = f"{BASE_URL}{FRONTEND_API}/data_products_v2"
    
    # ACT
    response = requests.get(url, timeout=TIMEOUT)
    
    # ASSERT
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"
    
    data = response.json()
    assert 'success' in data, "Response missing 'success' field"
    assert data['success'] is True, "API should return success=true"
    
    assert 'module' in data, "Response missing 'module' field"
    
    module = data['module']
    assert module['id'] == 'data_products_v2', "Module ID should match request"


@pytest.mark.e2e
@pytest.mark.api_contract
def test_frontend_registry_stats_includes_data_products_v2():
    """
    Test: Registry stats accounts for data_products_v2 module
    
    Validates:
    - HTTP 200 response
    - Stats include total_modules count
    - data_products_v2 contributes to count
    
    Implicitly Tests:
    - FrontendModuleRegistry.get_registry_stats()
    """
    # ARRANGE
    stats_url = f"{BASE_URL}{FRONTEND_API}/stats"
    list_url = f"{BASE_URL}{FRONTEND_API}"
    
    # ACT
    stats_response = requests.get(stats_url, timeout=TIMEOUT)
    list_response = requests.get(list_url, timeout=TIMEOUT)
    
    # ASSERT
    assert stats_response.status_code == 200, "Stats endpoint should respond"
    assert list_response.status_code == 200, "List endpoint should respond"
    
    stats_data = stats_response.json()
    list_data = list_response.json()
    
    assert 'stats' in stats_data, "Response missing 'stats' field"
    assert 'total_modules' in stats_data['stats'], "Stats missing 'total_modules'"
    
    # Stats count should match actual module count
    expected_count = len(list_data['modules'])
    actual_count = stats_data['stats']['total_modules']
    
    assert actual_count == expected_count, \
        f"Stats count mismatch: {actual_count} vs {expected_count}"


@pytest.mark.e2e
@pytest.mark.api_contract
def test_frontend_api_performance():
    """
    Test: Frontend registry responds quickly (< 500ms)
    
    Validates:
    - Response time < 500ms (metadata only, no heavy queries)
    - Fast enough for navigation generation
    """
    # ARRANGE
    url = f"{BASE_URL}{FRONTEND_API}"
    
    # ACT
    import time
    start_time = time.time()
    response = requests.get(url, timeout=TIMEOUT)
    elapsed_ms = (time.time() - start_time) * 1000
    
    # ASSERT
    assert response.status_code == 200, "API should respond successfully"
    assert elapsed_ms < 500, \
        f"Frontend API too slow: {elapsed_ms:.0f}ms (should be < 500ms for metadata)"


@pytest.mark.e2e
@pytest.mark.api_contract
def test_data_products_v2_module_structure():
    """
    Test: data_products_v2 module has valid structure in registry
    
    Validates complete module metadata structure for proper frontend loading
    """
    # ARRANGE
    url = f"{BASE_URL}{FRONTEND_API}/data_products_v2"
    
    # ACT
    response = requests.get(url, timeout=TIMEOUT)
    
    # ASSERT
    assert response.status_code == 200, "Module should be found"
    
    module = response.json()['module']
    
    # Validate frontend config
    assert 'frontend' in module, "Module missing 'frontend' config"
    frontend = module['frontend']
    
    assert 'scripts' in frontend, "Frontend missing 'scripts'"
    assert 'route' in frontend, "Frontend missing 'route'"
    
    # Validate backend config
    assert 'backend' in module, "Module missing 'backend' config"
    backend = module['backend']
    
    assert 'base_url' in backend, "Backend missing 'base_url'"
    assert backend['base_url'] == '/api/data-products', \
        f"Backend base_url should be '/api/data-products', got {backend['base_url']}"


# Smoke Test
@pytest.mark.smoke
def test_frontend_registry_health():
    """
    Smoke test: Frontend registry is responsive
    
    Quick check that frontend metadata API is available.
    """
    # ARRANGE
    url = f"{BASE_URL}{FRONTEND_API}"
    
    # ACT
    try:
        response = requests.get(url, timeout=TIMEOUT)
        
        # ASSERT
        assert response.status_code == 200, \
            f"Registry should be accessible (got {response.status_code})"
    
    except requests.exceptions.ConnectionError:
        pytest.fail("Server not running. Start with: python server.py")