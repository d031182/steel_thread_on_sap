"""
Backend API Contract Tests for Knowledge Graph V2 Module

Tests the backend API endpoints as black boxes using HTTP requests.
Following Gu Wu API Contract Testing methodology - one API test validates entire call chain.

CRITICAL: These tests verify the API contract (request/response structure), not implementation details.
"""

import pytest
import requests
import time


BASE_URL = "http://localhost:5000"


@pytest.mark.api_contract
@pytest.mark.e2e
def test_schema_graph_endpoint_returns_valid_structure():
    """
    Test: GET /api/knowledge-graph/schema/graph returns valid graph structure
    
    Validates entire call chain: API → Facade → Service → Repository → Database
    """
    url = f"{BASE_URL}/api/knowledge-graph/schema/graph"
    
    response = requests.get(url, timeout=10)
    
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"
    
    data = response.json()
    assert "success" in data, "Response missing 'success' field"
    assert data["success"] is True, "API request failed"
    assert "data" in data, "Response missing 'data' field"
    
    graph_data = data["data"]
    assert "nodes" in graph_data, "Graph missing 'nodes' field"
    assert "edges" in graph_data, "Graph missing 'edges' field"
    assert isinstance(graph_data["nodes"], list), "Nodes must be a list"
    assert isinstance(graph_data["edges"], list), "Edges must be a list"


@pytest.mark.api_contract
@pytest.mark.e2e
def test_rebuild_schema_graph_returns_success():
    """
    Test: POST /api/knowledge-graph/schema/rebuild triggers graph rebuild
    
    Validates write operations through entire stack
    """
    url = f"{BASE_URL}/api/knowledge-graph/schema/rebuild"
    
    response = requests.post(url, timeout=30)
    
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"
    
    data = response.json()
    assert "success" in data, "Response missing 'success' field"
    assert data["success"] is True, "Rebuild failed"
    assert "data" in data, "Response missing 'data' field"
    
    rebuild_data = data["data"]
    assert "nodes_count" in rebuild_data, "Missing nodes_count"
    assert "edges_count" in rebuild_data, "Missing edges_count"
    assert isinstance(rebuild_data["nodes_count"], int), "nodes_count must be integer"
    assert isinstance(rebuild_data["edges_count"], int), "edges_count must be integer"


@pytest.mark.api_contract
@pytest.mark.e2e
def test_cache_status_endpoint():
    """
    Test: GET /api/knowledge-graph/schema/status returns cache status
    
    Validates cache layer through API
    """
    url = f"{BASE_URL}/api/knowledge-graph/schema/status"
    
    response = requests.get(url, timeout=5)
    
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"
    
    data = response.json()
    assert "success" in data, "Response missing 'success' field"
    assert data["success"] is True, "Status request failed"
    assert "data" in data, "Response missing 'data' field"
    
    status_data = data["data"]
    assert "cached" in status_data, "Missing 'cached' field"
    assert isinstance(status_data["cached"], bool), "cached must be boolean"


@pytest.mark.api_contract
@pytest.mark.e2e
def test_clear_cache_endpoint():
    """
    Test: POST /api/knowledge-graph/schema/cache/clear clears cache
    
    Validates cache invalidation through API
    """
    url = f"{BASE_URL}/api/knowledge-graph/schema/cache/clear"
    
    response = requests.post(url, timeout=5)
    
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"
    
    data = response.json()
    assert "success" in data, "Response missing 'success' field"
    assert data["success"] is True, "Clear cache failed"


@pytest.mark.api_contract
@pytest.mark.e2e
def test_table_columns_endpoint():
    """
    Test: GET /api/knowledge-graph/tables/{table_name}/columns returns column metadata
    
    Validates metadata retrieval through API
    """
    # Use a known table from the schema (adjust if needed)
    table_name = "PurchaseOrders"
    url = f"{BASE_URL}/api/knowledge-graph/tables/{table_name}/columns"
    
    response = requests.get(url, timeout=5)
    
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"
    
    data = response.json()
    assert "success" in data, "Response missing 'success' field"
    assert data["success"] is True, "Request failed"
    assert "data" in data, "Response missing 'data' field"
    
    columns_data = data["data"]
    assert "table_name" in columns_data, "Missing table_name"
    assert "columns" in columns_data, "Missing columns"
    assert isinstance(columns_data["columns"], list), "Columns must be a list"


@pytest.mark.api_contract
@pytest.mark.e2e
def test_analytics_pagerank_endpoint():
    """
    Test: GET /api/knowledge-graph/analytics/pagerank returns PageRank scores
    
    Validates analytics functionality through API
    """
    url = f"{BASE_URL}/api/knowledge-graph/analytics/pagerank"
    
    response = requests.get(url, timeout=10)
    
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"
    
    data = response.json()
    assert "success" in data, "Response missing 'success' field"
    assert data["success"] is True, "PageRank request failed"
    assert "data" in data, "Response missing 'data' field"
    
    pagerank_data = data["data"]
    assert isinstance(pagerank_data, dict), "PageRank data must be a dictionary"


@pytest.mark.api_contract
@pytest.mark.e2e
def test_analytics_statistics_endpoint():
    """
    Test: GET /api/knowledge-graph/analytics/statistics returns graph statistics
    
    Validates graph metrics through API
    """
    url = f"{BASE_URL}/api/knowledge-graph/analytics/statistics"
    
    response = requests.get(url, timeout=10)
    
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"
    
    data = response.json()
    assert "success" in data, "Response missing 'success' field"
    assert data["success"] is True, "Statistics request failed"
    assert "data" in data, "Response missing 'data' field"
    
    stats_data = data["data"]
    assert "node_count" in stats_data, "Missing node_count"
    assert "edge_count" in stats_data, "Missing edge_count"
    assert isinstance(stats_data["node_count"], int), "node_count must be integer"
    assert isinstance(stats_data["edge_count"], int), "edge_count must be integer"


@pytest.mark.api_contract
@pytest.mark.e2e
def test_error_handling_invalid_table():
    """
    Test: Error handling for non-existent table
    
    Validates proper error responses from API
    """
    table_name = "NonExistentTable123"
    url = f"{BASE_URL}/api/knowledge-graph/tables/{table_name}/columns"
    
    response = requests.get(url, timeout=5)
    
    # Should return error (404 or 200 with success=false)
    assert response.status_code in [200, 404], f"Unexpected status: {response.status_code}"
    
    data = response.json()
    assert "success" in data, "Response missing 'success' field"
    
    if response.status_code == 200:
        assert data["success"] is False, "Should indicate failure for invalid table"
        assert "error" in data or "message" in data, "Missing error message"


@pytest.mark.api_contract
@pytest.mark.e2e
def test_api_response_time_acceptable():
    """
    Test: API response times are within acceptable limits (<1s for cached data)
    
    Performance contract test
    """
    url = f"{BASE_URL}/api/knowledge-graph/schema/graph"
    
    # First call may be slower (cache miss)
    response = requests.get(url, timeout=10)
    assert response.status_code == 200
    
    # Second call should be fast (cached)
    start_time = time.time()
    response = requests.get(url, timeout=10)
    elapsed = time.time() - start_time
    
    assert response.status_code == 200
    assert elapsed < 1.0, f"Cached response too slow: {elapsed:.2f}s (expected <1s)"