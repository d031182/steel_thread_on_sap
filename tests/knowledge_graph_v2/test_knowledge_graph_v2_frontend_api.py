"""
Knowledge Graph V2 Frontend API Contract Tests

Tests Frontend API metadata contracts following Gu Wu methodology:
"Test the contract, trust the implementation"

Frontend APIs provide metadata for module registration, routing, and UX configuration.
These tests validate the module's registration in the frontend module registry.

Version: 1.0.0
"""
import pytest
import requests
from typing import Dict, Any

# Base URL for Frontend Registry API
BASE_URL = "http://localhost:5000/api/modules/frontend-registry"

# Pytest marks
pytestmark = [
    pytest.mark.e2e,
    pytest.mark.api_contract,
    pytest.mark.knowledge_graph_v2,
    pytest.mark.frontend_api
]


# ============================================================================
# Frontend Module Registry Tests
# ============================================================================

def test_frontend_registry_contains_knowledge_graph_v2():
    """
    Test: Frontend registry includes knowledge_graph_v2 module
    
    Contract:
    - GET /api/modules/frontend-registry returns 200
    - Response contains 'modules' array
    - Array includes module with id='knowledge_graph_v2'
    - Module entry contains required metadata fields
    """
    # ACT
    response = requests.get(BASE_URL, timeout=5)
    
    # ASSERT
    assert response.status_code == 200, "Frontend registry should return 200"
    
    data = response.json()
    assert 'modules' in data, "Response should contain 'modules' array"
    assert isinstance(data['modules'], list), "'modules' should be list"
    assert len(data['modules']) > 0, "Should have at least one module"
    
    # Find knowledge_graph_v2 module
    kg_module = next(
        (m for m in data['modules'] if m.get('id') == 'knowledge_graph_v2'),
        None
    )
    
    assert kg_module is not None, "Should contain knowledge_graph_v2 module"


def test_knowledge_graph_v2_module_structure():
    """
    Test: knowledge_graph_v2 module has required metadata structure
    
    Contract (from Module Federation Standard):
    - id: string (snake_case)
    - name: string (human-readable)
    - category: string (analytics|data|system)
    - version: string
    - enabled: boolean
    - routes: array of route objects
    - factory: string (factory function name)
    """
    # ACT
    response = requests.get(BASE_URL, timeout=5)
    data = response.json()
    
    # Find knowledge_graph_v2 module
    kg_module = next(
        (m for m in data['modules'] if m.get('id') == 'knowledge_graph_v2'),
        None
    )
    
    assert kg_module is not None, "Module should exist in registry"
    
    # ASSERT - Required fields
    assert 'id' in kg_module, "Module should have 'id'"
    assert kg_module['id'] == 'knowledge_graph_v2', "ID should be 'knowledge_graph_v2'"
    
    assert 'name' in kg_module, "Module should have 'name'"
    assert isinstance(kg_module['name'], str), "'name' should be string"
    
    assert 'category' in kg_module, "Module should have 'category'"
    assert kg_module['category'] in ['analytics', 'data', 'system'], \
        "Category should be analytics, data, or system"
    
    assert 'version' in kg_module, "Module should have 'version'"
    assert isinstance(kg_module['version'], str), "'version' should be string"
    
    assert 'enabled' in kg_module, "Module should have 'enabled'"
    assert isinstance(kg_module['enabled'], bool), "'enabled' should be boolean"
    
    assert 'routes' in kg_module, "Module should have 'routes'"
    assert isinstance(kg_module['routes'], list), "'routes' should be list"
    
    assert 'factory' in kg_module, "Module should have 'factory'"
    assert isinstance(kg_module['factory'], str), "'factory' should be string"


def test_knowledge_graph_v2_routes_structure():
    """
    Test: Module routes follow required structure
    
    Contract:
    - Each route has 'path' (string starting with /)
    - Each route has 'title' (string)
    - Optional: 'icon', 'description'
    """
    # ACT
    response = requests.get(BASE_URL, timeout=5)
    data = response.json()
    
    kg_module = next(
        (m for m in data['modules'] if m.get('id') == 'knowledge_graph_v2'),
        None
    )
    
    assert kg_module is not None, "Module should exist"
    assert 'routes' in kg_module, "Module should have routes"
    
    routes = kg_module['routes']
    assert len(routes) > 0, "Module should have at least one route"
    
    # ASSERT - Each route structure
    for route in routes:
        assert 'path' in route, "Route should have 'path'"
        assert isinstance(route['path'], str), "'path' should be string"
        assert route['path'].startswith('/'), "'path' should start with /"
        
        assert 'title' in route, "Route should have 'title'"
        assert isinstance(route['title'], str), "'title' should be string"


def test_knowledge_graph_v2_factory_naming():
    """
    Test: Module factory follows naming convention
    
    Contract:
    - Factory name is PascalCase + 'Module'
    - Example: 'KnowledgeGraphV2Module' or 'KnowledgeGraphModule'
    """
    # ACT
    response = requests.get(BASE_URL, timeout=5)
    data = response.json()
    
    kg_module = next(
        (m for m in data['modules'] if m.get('id') == 'knowledge_graph_v2'),
        None
    )
    
    assert kg_module is not None, "Module should exist"
    assert 'factory' in kg_module, "Module should have factory"
    
    factory = kg_module['factory']
    
    # ASSERT - Factory naming
    assert factory.endswith('Module'), "Factory should end with 'Module'"
    assert factory[0].isupper(), "Factory should start with uppercase (PascalCase)"
    assert 'KnowledgeGraph' in factory, "Factory should contain 'KnowledgeGraph'"


def test_knowledge_graph_v2_route_paths():
    """
    Test: Route paths follow kebab-case convention
    
    Contract:
    - Paths use kebab-case: /knowledge-graph (not /knowledge_graph)
    - Consistent with backend API paths
    """
    # ACT
    response = requests.get(BASE_URL, timeout=5)
    data = response.json()
    
    kg_module = next(
        (m for m in data['modules'] if m.get('id') == 'knowledge_graph_v2'),
        None
    )
    
    assert kg_module is not None, "Module should exist"
    routes = kg_module['routes']
    
    # ASSERT - Each route path
    for route in routes:
        path = route['path']
        # Should not contain underscores (kebab-case not snake_case)
        assert '_' not in path, f"Path '{path}' should use kebab-case (no underscores)"
        # Should contain hyphens if multi-word
        if 'knowledge' in path.lower() and 'graph' in path.lower():
            assert 'knowledge-graph' in path.lower(), \
                f"Path '{path}' should use 'knowledge-graph' (kebab-case)"


def test_knowledge_graph_v2_metadata_consistency():
    """
    Test: Module metadata is consistent across fields
    
    Contract:
    - module.json id matches registry id
    - Version format is semantic (X.Y.Z)
    - Category is appropriate for module type
    """
    # ACT
    response = requests.get(BASE_URL, timeout=5)
    data = response.json()
    
    kg_module = next(
        (m for m in data['modules'] if m.get('id') == 'knowledge_graph_v2'),
        None
    )
    
    assert kg_module is not None, "Module should exist"
    
    # ASSERT - ID consistency
    assert kg_module['id'] == 'knowledge_graph_v2', \
        "Registry ID should match module.json id"
    
    # ASSERT - Version format (X.Y.Z or X.Y)
    version = kg_module['version']
    version_parts = version.split('.')
    assert len(version_parts) >= 2, "Version should be semantic (X.Y or X.Y.Z)"
    assert all(part.isdigit() for part in version_parts), \
        "Version parts should be numeric"
    
    # ASSERT - Category is appropriate for analytics/data module
    assert kg_module['category'] in ['analytics', 'data'], \
        "Knowledge graph should be 'analytics' or 'data' category"


def test_multiple_modules_registered():
    """
    Test: Frontend registry contains multiple modules
    
    Contract:
    - Registry should contain at least 2 modules (knowledge_graph_v2 + others)
    - This validates registry is properly aggregating modules
    """
    # ACT
    response = requests.get(BASE_URL, timeout=5)
    data = response.json()
    
    # ASSERT
    assert 'modules' in data, "Response should contain modules"
    modules = data['modules']
    
    assert len(modules) >= 2, \
        "Registry should contain multiple modules (not just knowledge_graph_v2)"
    
    # Verify knowledge_graph_v2 is one of them
    module_ids = [m.get('id') for m in modules]
    assert 'knowledge_graph_v2' in module_ids, \
        "knowledge_graph_v2 should be in registry"


def test_frontend_registry_response_structure():
    """
    Test: Frontend registry response follows consistent structure
    
    Contract:
    - Response is valid JSON
    - Top-level 'modules' array exists
    - Each module follows consistent schema
    - No duplicate module IDs
    """
    # ACT
    response = requests.get(BASE_URL, timeout=5)
    
    # ASSERT - Response structure
    assert response.status_code == 200, "Should return 200"
    assert response.headers['Content-Type'] == 'application/json', \
        "Should return JSON"
    
    data = response.json()
    assert isinstance(data, dict), "Response should be JSON object"
    assert 'modules' in data, "Should contain 'modules' key"
    assert isinstance(data['modules'], list), "'modules' should be array"
    
    # ASSERT - No duplicate IDs
    module_ids = [m.get('id') for m in data['modules']]
    unique_ids = set(module_ids)
    assert len(module_ids) == len(unique_ids), \
        "Module IDs should be unique (no duplicates)"


def test_knowledge_graph_v2_enabled_status():
    """
    Test: Module enabled status is properly set
    
    Contract:
    - 'enabled' is boolean
    - When true, module should be active and routes accessible
    - Validates feature flag integration
    """
    # ACT
    response = requests.get(BASE_URL, timeout=5)
    data = response.json()
    
    kg_module = next(
        (m for m in data['modules'] if m.get('id') == 'knowledge_graph_v2'),
        None
    )
    
    assert kg_module is not None, "Module should exist"
    
    # ASSERT
    assert 'enabled' in kg_module, "Should have 'enabled' field"
    assert isinstance(kg_module['enabled'], bool), "'enabled' should be boolean"
    
    # If enabled, routes should be accessible
    if kg_module['enabled']:
        assert len(kg_module['routes']) > 0, \
            "Enabled module should have accessible routes"


def test_knowledge_graph_v2_optional_fields():
    """
    Test: Optional metadata fields (if present) are valid
    
    Contract:
    - If 'description' exists, it should be string
    - If 'icon' exists, it should be string
    - If 'dependencies' exists, it should be array
    """
    # ACT
    response = requests.get(BASE_URL, timeout=5)
    data = response.json()
    
    kg_module = next(
        (m for m in data['modules'] if m.get('id') == 'knowledge_graph_v2'),
        None
    )
    
    assert kg_module is not None, "Module should exist"
    
    # ASSERT - Optional fields (if present)
    if 'description' in kg_module:
        assert isinstance(kg_module['description'], str), \
            "'description' should be string"
    
    if 'icon' in kg_module:
        assert isinstance(kg_module['icon'], str), \
            "'icon' should be string"
    
    if 'dependencies' in kg_module:
        assert isinstance(kg_module['dependencies'], list), \
            "'dependencies' should be array"


# ============================================================================
# Error Handling Tests
# ============================================================================

def test_frontend_registry_handles_invalid_requests():
    """
    Test: Frontend registry handles invalid HTTP methods
    
    Contract:
    - GET is allowed (returns 200)
    - POST/PUT/DELETE should return 405 Method Not Allowed
    """
    # ACT - Try POST (should be rejected)
    response = requests.post(BASE_URL, json={}, timeout=5)
    
    # ASSERT
    assert response.status_code == 405, \
        "POST to frontend registry should return 405 Method Not Allowed"


# ============================================================================
# Integration Tests
# ============================================================================

def test_knowledge_graph_v2_backend_frontend_consistency():
    """
    Test: Backend API paths match frontend routes
    
    Contract:
    - Frontend routes should align with backend endpoints
    - Example: Frontend /knowledge-graph → Backend /api/knowledge-graph
    - This validates end-to-end integration
    """
    # ACT - Get frontend routes
    frontend_response = requests.get(BASE_URL, timeout=5)
    frontend_data = frontend_response.json()
    
    kg_module = next(
        (m for m in frontend_data['modules'] if m.get('id') == 'knowledge_graph_v2'),
        None
    )
    
    assert kg_module is not None, "Module should exist"
    frontend_routes = kg_module['routes']
    
    # ACT - Test backend health endpoint
    backend_response = requests.get(
        "http://localhost:5000/api/knowledge-graph/health",
        timeout=5
    )
    
    # ASSERT - Backend is accessible
    assert backend_response.status_code == 200, \
        "Backend API should be accessible"
    
    # ASSERT - Route naming consistency
    for route in frontend_routes:
        path = route['path']
        # Frontend paths should match backend API structure
        if 'knowledge' in path.lower():
            assert 'knowledge-graph' in path.lower() or 'knowledge_graph' in path.lower(), \
                f"Frontend route '{path}' should use consistent naming"


# ============================================================================
# Pytest Fixtures for Server Management
# ============================================================================

@pytest.fixture(scope="module", autouse=True)
def verify_server_running():
    """
    Verify server is running before tests
    
    This fixture runs once per module to confirm server accessibility.
    """
    try:
        response = requests.get(BASE_URL, timeout=5)
        if response.status_code != 200:
            pytest.skip("Server not responding to frontend registry endpoint")
    except requests.exceptions.RequestException:
        pytest.skip("Server not accessible - start with: python server.py")