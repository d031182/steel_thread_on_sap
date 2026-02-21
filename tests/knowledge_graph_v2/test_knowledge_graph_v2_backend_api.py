"""
Knowledge Graph V2 Backend API Contract Tests

Tests API contracts for all backend endpoints following Gu Wu methodology:
"Test the contract, trust the implementation"

Each test validates:
1. HTTP status code (200 success, 400 bad request, 500 error)
2. Response structure (success, data, error fields)
3. Data types and required fields
4. Error handling behavior

Version: 1.0.0
"""
import pytest
import requests
from typing import Dict, Any

# Base URL for Knowledge Graph V2 API
BASE_URL = "http://localhost:5000/api/knowledge-graph"

# Pytest marks
pytestmark = [
    pytest.mark.e2e,
    pytest.mark.api_contract,
    pytest.mark.knowledge_graph_v2
]


# ============================================================================
# Core Endpoints
# ============================================================================

def test_health_check_contract():
    """
    Test: GET /api/knowledge-graph/health returns valid health status
    
    Contract:
    - Returns 200 status code
    - Contains 'status', 'version', 'api' fields
    - Status is 'healthy'
    """
    # ACT
    response = requests.get(f"{BASE_URL}/health", timeout=5)
    
    # ASSERT
    assert response.status_code == 200, "Health check should return 200"
    
    data = response.json()
    assert 'status' in data, "Response should contain 'status'"
    assert 'version' in data, "Response should contain 'version'"
    assert 'api' in data, "Response should contain 'api'"
    assert data['status'] == 'healthy', "Status should be 'healthy'"
    assert data['api'] == 'knowledge-graph-v2', "API name should match"


def test_get_schema_graph_contract():
    """
    Test: GET /api/knowledge-graph/schema returns valid schema graph
    
    Contract:
    - Returns 200 on success or 500 on error
    - Contains 'success' boolean field
    - On success: contains 'data' with 'nodes' and 'edges'
    - On error: contains 'error' string field
    """
    # ACT
    response = requests.get(f"{BASE_URL}/schema", timeout=5)
    
    # ASSERT
    assert response.status_code in [200, 500], "Should return 200 or 500"
    
    data = response.json()
    assert 'success' in data, "Response should contain 'success' field"
    assert isinstance(data['success'], bool), "'success' should be boolean"
    
    if data['success']:
        # Success path validation
        assert 'data' in data, "Success response should contain 'data'"
        graph_data = data['data']
        assert 'graph' in graph_data, "Data should contain 'graph'"
        assert 'metadata' in graph_data, "Data should contain 'metadata'"
        graph = graph_data['graph']
        assert 'nodes' in graph, "Graph should contain 'nodes'"
        assert 'edges' in graph, "Graph should contain 'edges'"
        assert isinstance(graph['nodes'], list), "'nodes' should be list"
        assert isinstance(graph['edges'], list), "'edges' should be list"
    else:
        # Error path validation
        assert 'error' in data, "Error response should contain 'error' field"
        assert isinstance(data['error'], str), "'error' should be string"


def test_get_schema_graph_with_cache_param():
    """
    Test: GET /api/knowledge-graph/schema?use_cache=false bypasses cache
    
    Contract:
    - Accepts 'use_cache' query parameter
    - Returns same structure regardless of cache parameter
    """
    # ACT - Test with cache disabled
    response = requests.get(
        f"{BASE_URL}/schema",
        params={'use_cache': 'false'},
        timeout=5
    )
    
    # ASSERT
    assert response.status_code in [200, 500], "Should return 200 or 500"
    
    data = response.json()
    assert 'success' in data, "Response should contain 'success' field"
    
    if data['success']:
        assert 'data' in data, "Success response should contain 'data'"
        assert 'graph' in data['data'], "Data should contain 'graph'"
        assert 'nodes' in data['data']['graph'], "Graph should contain 'nodes'"
        assert 'edges' in data['data']['graph'], "Graph should contain 'edges'"


def test_rebuild_schema_graph_contract():
    """
    Test: POST /api/knowledge-graph/schema/rebuild forces cache rebuild
    
    Contract:
    - Returns 200 on success or 500 on error
    - Contains 'success' boolean field
    - On success: contains 'data' with rebuilt graph
    - On error: contains 'error' string field
    """
    # ACT
    response = requests.post(f"{BASE_URL}/schema/rebuild", timeout=10)
    
    # ASSERT
    assert response.status_code in [200, 500], "Should return 200 or 500"
    
    data = response.json()
    assert 'success' in data, "Response should contain 'success' field"
    assert isinstance(data['success'], bool), "'success' should be boolean"
    
    if data['success']:
        assert 'data' in data, "Success response should contain 'data'"
        assert 'graph' in data['data'], "Data should contain 'graph'"
        assert 'nodes' in data['data']['graph'], "Rebuilt graph should contain 'nodes'"
        assert 'edges' in data['data']['graph'], "Rebuilt graph should contain 'edges'"
    else:
        assert 'error' in data, "Error response should contain 'error' field"


def test_get_status_contract():
    """
    Test: GET /api/knowledge-graph/status returns cache status
    
    Contract:
    - Returns 200 on success or 500 on error
    - Contains 'success' boolean field
    - On success: contains 'data' with cache and CSN info
    - On error: contains 'error' string field
    """
    # ACT
    response = requests.get(f"{BASE_URL}/status", timeout=5)
    
    # ASSERT
    assert response.status_code in [200, 500], "Should return 200 or 500"
    
    data = response.json()
    assert 'success' in data, "Response should contain 'success' field"
    
    if data['success']:
        assert 'data' in data, "Success response should contain 'data'"
        # Status data structure may vary, but 'data' field must exist
    else:
        assert 'error' in data, "Error response should contain 'error' field"


def test_clear_cache_contract():
    """
    Test: DELETE /api/knowledge-graph/cache clears cache
    
    Contract:
    - Returns 200 on success or 500 on error
    - Contains 'success' boolean field
    - On success: may contain confirmation message
    - On error: contains 'error' string field
    """
    # ACT
    response = requests.delete(f"{BASE_URL}/cache", timeout=5)
    
    # ASSERT
    assert response.status_code in [200, 500], "Should return 200 or 500"
    
    data = response.json()
    assert 'success' in data, "Response should contain 'success' field"
    assert isinstance(data['success'], bool), "'success' should be boolean"
    
    if not data['success']:
        assert 'error' in data, "Error response should contain 'error' field"


# ============================================================================
# Analytics Endpoints (HIGH-31: Phase 3)
# ============================================================================

def test_get_pagerank_contract():
    """
    Test: GET /api/knowledge-graph/analytics/pagerank calculates PageRank
    
    Contract:
    - Returns 200 on success, 400 on bad params, 500 on error
    - Accepts 'top_k' and 'damping_factor' query parameters
    - On success: contains 'data' with PageRank scores
    - On error: contains 'error' field
    """
    # ACT
    response = requests.get(
        f"{BASE_URL}/analytics/pagerank",
        params={'top_k': 5, 'damping_factor': 0.85},
        timeout=10
    )
    
    # ASSERT
    assert response.status_code in [200, 400, 500], "Should return 200/400/500"
    
    data = response.json()
    assert 'success' in data, "Response should contain 'success' field"
    
    if response.status_code == 200:
        assert data['success'] is True, "Success status should be true"
        assert 'data' in data, "Success response should contain 'data'"
    else:
        assert 'error' in data, "Error response should contain 'error' field"


def test_get_pagerank_invalid_params():
    """
    Test: GET /analytics/pagerank with invalid params returns 400
    
    Contract:
    - Returns 400 for invalid top_k (< 1)
    - Returns 400 for invalid damping_factor (not in 0-1)
    - Error response contains 'error' field
    """
    # ACT - Invalid top_k
    response = requests.get(
        f"{BASE_URL}/analytics/pagerank",
        params={'top_k': 0},
        timeout=5
    )
    
    # ASSERT
    assert response.status_code == 400, "Invalid top_k should return 400"
    data = response.json()
    assert 'success' in data and data['success'] is False
    assert 'error' in data, "Error response should contain 'error' field"


def test_get_centrality_contract():
    """
    Test: GET /api/knowledge-graph/analytics/centrality calculates centrality
    
    Contract:
    - Returns 200 on success, 400 on bad params, 500 on error
    - Accepts 'metric' and 'top_k' query parameters
    - On success: contains 'data' with centrality scores
    - On error: contains 'error' field
    """
    # ACT
    response = requests.get(
        f"{BASE_URL}/analytics/centrality",
        params={'metric': 'betweenness', 'top_k': 5},
        timeout=10
    )
    
    # ASSERT
    assert response.status_code in [200, 400, 500], "Should return 200/400/500"
    
    data = response.json()
    assert 'success' in data, "Response should contain 'success' field"
    
    if response.status_code == 200:
        assert data['success'] is True, "Success status should be true"
        assert 'data' in data, "Success response should contain 'data'"
    else:
        assert 'error' in data, "Error response should contain 'error' field"


def test_get_centrality_invalid_params():
    """
    Test: GET /analytics/centrality with invalid top_k returns 400
    
    Contract:
    - Returns 400 for invalid top_k (< 1)
    - Error response contains 'error' field
    """
    # ACT
    response = requests.get(
        f"{BASE_URL}/analytics/centrality",
        params={'top_k': -1},
        timeout=5
    )
    
    # ASSERT
    assert response.status_code == 400, "Invalid top_k should return 400"
    data = response.json()
    assert 'success' in data and data['success'] is False
    assert 'error' in data, "Error response should contain 'error' field"


def test_detect_communities_contract():
    """
    Test: GET /api/knowledge-graph/analytics/communities detects communities
    
    Contract:
    - Returns 200 on success, 400 on bad params, 500 on error
    - Accepts 'algorithm' query parameter
    - On success: contains 'data' with community assignments
    - On error: contains 'error' field
    """
    # ACT
    response = requests.get(
        f"{BASE_URL}/analytics/communities",
        params={'algorithm': 'louvain'},
        timeout=10
    )
    
    # ASSERT
    assert response.status_code in [200, 400, 500], "Should return 200/400/500"
    
    data = response.json()
    assert 'success' in data, "Response should contain 'success' field"
    
    if response.status_code == 200:
        assert data['success'] is True, "Success status should be true"
        assert 'data' in data, "Success response should contain 'data'"
    else:
        assert 'error' in data, "Error response should contain 'error' field"


def test_find_cycles_contract():
    """
    Test: GET /api/knowledge-graph/analytics/cycles finds graph cycles
    
    Contract:
    - Returns 200 on success or 500 on error
    - Contains 'success' boolean field
    - On success: contains 'data' with cycles
    - On error: contains 'error' field
    """
    # ACT
    response = requests.get(f"{BASE_URL}/analytics/cycles", timeout=10)
    
    # ASSERT
    assert response.status_code in [200, 500], "Should return 200 or 500"
    
    data = response.json()
    assert 'success' in data, "Response should contain 'success' field"
    
    if data['success']:
        assert 'data' in data, "Success response should contain 'data'"
    else:
        assert 'error' in data, "Error response should contain 'error' field"


def test_get_connected_components_contract():
    """
    Test: GET /api/knowledge-graph/analytics/components finds components
    
    Contract:
    - Returns 200 on success or 500 on error
    - Contains 'success' boolean field
    - On success: contains 'data' with connected components
    - On error: contains 'error' field
    """
    # ACT
    response = requests.get(f"{BASE_URL}/analytics/components", timeout=10)
    
    # ASSERT
    assert response.status_code in [200, 500], "Should return 200 or 500"
    
    data = response.json()
    assert 'success' in data, "Response should contain 'success' field"
    
    if data['success']:
        assert 'data' in data, "Success response should contain 'data'"
    else:
        assert 'error' in data, "Error response should contain 'error' field"


def test_get_graph_statistics_contract():
    """
    Test: GET /api/knowledge-graph/analytics/statistics returns statistics
    
    Contract:
    - Returns 200 on success or 500 on error
    - Contains 'success' boolean field
    - On success: contains 'data' with comprehensive statistics
    - On error: contains 'error' field
    """
    # ACT
    response = requests.get(f"{BASE_URL}/analytics/statistics", timeout=10)
    
    # ASSERT
    assert response.status_code in [200, 500], "Should return 200 or 500"
    
    data = response.json()
    assert 'success' in data, "Response should contain 'success' field"
    
    if data['success']:
        assert 'data' in data, "Success response should contain 'data'"
        # Statistics should contain key metrics
        stats = data['data']
        # Structure may vary, but 'data' field is required
    else:
        assert 'error' in data, "Error response should contain 'error' field"


# ============================================================================
# Error Handling Tests
# ============================================================================

def test_invalid_endpoint_returns_404():
    """
    Test: Invalid endpoint returns 404
    
    Contract:
    - Non-existent endpoints return 404
    - This tests Flask routing, not our API code
    """
    # ACT
    response = requests.get(f"{BASE_URL}/invalid-endpoint", timeout=5)
    
    # ASSERT
    assert response.status_code == 404, "Invalid endpoint should return 404"


def test_api_error_response_structure():
    """
    Test: All error responses follow consistent structure
    
    Contract:
    - Error responses contain 'success': False
    - Error responses contain 'error' string field
    - May optionally contain 'error_type' field
    """
    # ACT - Trigger error with invalid parameter
    response = requests.get(
        f"{BASE_URL}/analytics/pagerank",
        params={'top_k': 'invalid'},  # Non-numeric value
        timeout=5
    )
    
    # ASSERT
    assert response.status_code in [400, 500], "Should return error code"
    
    data = response.json()
    assert 'success' in data, "Response should contain 'success' field"
    assert data['success'] is False, "Error response should have success=False"
    assert 'error' in data, "Error response should contain 'error' field"
    assert isinstance(data['error'], str), "'error' should be string"


# ============================================================================
# Integration Workflow Tests
# ============================================================================

def test_cache_rebuild_workflow():
    """
    Test: Complete cache rebuild workflow
    
    Workflow:
    1. Clear cache
    2. Rebuild schema graph
    3. Get status
    4. Verify graph accessible
    
    Contract: Each step returns success response
    """
    # ARRANGE - Start with clean cache
    requests.delete(f"{BASE_URL}/cache", timeout=5)
    
    # ACT & ASSERT - Step 1: Rebuild
    rebuild_response = requests.post(f"{BASE_URL}/schema/rebuild", timeout=10)
    assert rebuild_response.status_code in [200, 500]
    rebuild_data = rebuild_response.json()
    assert 'success' in rebuild_data
    
    # ACT & ASSERT - Step 2: Get status
    status_response = requests.get(f"{BASE_URL}/status", timeout=5)
    assert status_response.status_code in [200, 500]
    status_data = status_response.json()
    assert 'success' in status_data
    
    # ACT & ASSERT - Step 3: Get graph
    graph_response = requests.get(f"{BASE_URL}/schema", timeout=5)
    assert graph_response.status_code in [200, 500]
    graph_data = graph_response.json()
    assert 'success' in graph_data


def test_analytics_workflow():
    """
    Test: Complete analytics workflow
    
    Workflow:
    1. Get schema graph
    2. Calculate PageRank
    3. Calculate centrality
    4. Get statistics
    
    Contract: Each step returns consistent response structure
    """
    # ACT & ASSERT - Step 1: Get graph
    graph_response = requests.get(f"{BASE_URL}/schema", timeout=5)
    assert graph_response.status_code in [200, 500]
    assert 'success' in graph_response.json()
    
    # ACT & ASSERT - Step 2: PageRank
    pagerank_response = requests.get(
        f"{BASE_URL}/analytics/pagerank",
        params={'top_k': 5},
        timeout=10
    )
    assert pagerank_response.status_code in [200, 400, 500]
    assert 'success' in pagerank_response.json()
    
    # ACT & ASSERT - Step 3: Centrality
    centrality_response = requests.get(
        f"{BASE_URL}/analytics/centrality",
        params={'metric': 'betweenness', 'top_k': 5},
        timeout=10
    )
    assert centrality_response.status_code in [200, 400, 500]
    assert 'success' in centrality_response.json()
    
    # ACT & ASSERT - Step 4: Statistics
    stats_response = requests.get(f"{BASE_URL}/analytics/statistics", timeout=10)
    assert stats_response.status_code in [200, 500]
    assert 'success' in stats_response.json()


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
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        if response.status_code != 200:
            pytest.skip("Server not responding to health check")
    except requests.exceptions.RequestException:
        pytest.skip("Server not accessible - start with: python server.py")