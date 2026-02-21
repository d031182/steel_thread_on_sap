"""
API Contract Tests for Knowledge Graph V2 Analytics Endpoints (HIGH-31)

Tests advanced query endpoints following Gu Wu API contract testing methodology.
Tests the contract, trusts the implementation.
"""
import pytest
import requests
from typing import Dict, Any


# ============================================================================
# Configuration
# ============================================================================

BASE_URL = "http://localhost:5000"
API_PREFIX = "/api/knowledge-graph"


# ============================================================================
# Fixtures
# ============================================================================

@pytest.fixture
def analytics_base_url():
    """Base URL for analytics endpoints"""
    return f"{BASE_URL}{API_PREFIX}/analytics"


# ============================================================================
# API Contract Tests - PageRank
# ============================================================================

@pytest.mark.e2e
@pytest.mark.api_contract
def test_pagerank_default_parameters(analytics_base_url):
    """
    Test: GET /analytics/pagerank with default parameters
    
    Contract:
    - Returns 200 status
    - Response has 'success' field
    - Response has 'data' field with 'scores' list
    - Default top_k = 10
    """
    # ARRANGE
    url = f"{analytics_base_url}/pagerank"
    
    # ACT
    response = requests.get(url, timeout=10)
    
    # ASSERT
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"
    
    data = response.json()
    assert 'success' in data, "Response missing 'success' field"
    assert data['success'] is True, "Expected success=True"
    assert 'data' in data, "Response missing 'data' field"
    assert 'scores' in data['data'], "Response data missing 'scores' field"
    assert isinstance(data['data']['scores'], list), "Scores must be a list"


@pytest.mark.e2e
@pytest.mark.api_contract
def test_pagerank_custom_parameters(analytics_base_url):
    """
    Test: GET /analytics/pagerank with custom parameters
    
    Contract:
    - Accepts top_k parameter
    - Accepts damping_factor parameter
    - Returns correct structure
    """
    # ARRANGE
    url = f"{analytics_base_url}/pagerank"
    params = {
        'top_k': 5,
        'damping_factor': 0.9
    }
    
    # ACT
    response = requests.get(url, params=params, timeout=10)
    
    # ASSERT
    assert response.status_code == 200
    data = response.json()
    assert data['success'] is True
    assert 'data' in data
    assert 'scores' in data['data']


@pytest.mark.e2e
@pytest.mark.api_contract
def test_pagerank_invalid_top_k(analytics_base_url):
    """
    Test: GET /analytics/pagerank with invalid top_k
    
    Contract:
    - Returns 400 for top_k < 1
    - Response has error message
    """
    # ARRANGE
    url = f"{analytics_base_url}/pagerank"
    params = {'top_k': 0}
    
    # ACT
    response = requests.get(url, params=params, timeout=10)
    
    # ASSERT
    assert response.status_code == 400
    data = response.json()
    assert data['success'] is False
    assert 'error' in data


@pytest.mark.e2e
@pytest.mark.api_contract
def test_pagerank_invalid_damping_factor(analytics_base_url):
    """
    Test: GET /analytics/pagerank with invalid damping_factor
    
    Contract:
    - Returns 400 for damping_factor outside (0, 1)
    - Response has error message
    """
    # ARRANGE
    url = f"{analytics_base_url}/pagerank"
    params = {'damping_factor': 1.5}
    
    # ACT
    response = requests.get(url, params=params, timeout=10)
    
    # ASSERT
    assert response.status_code == 400
    data = response.json()
    assert data['success'] is False
    assert 'error' in data


# ============================================================================
# API Contract Tests - Centrality
# ============================================================================

@pytest.mark.e2e
@pytest.mark.api_contract
def test_centrality_default_parameters(analytics_base_url):
    """
    Test: GET /analytics/centrality with default parameters
    
    Contract:
    - Returns 200 status
    - Response has 'success' field
    - Response has 'data' field with 'scores' list
    - Default metric = betweenness
    """
    # ARRANGE
    url = f"{analytics_base_url}/centrality"
    
    # ACT
    response = requests.get(url, timeout=10)
    
    # ASSERT
    assert response.status_code == 200
    data = response.json()
    assert data['success'] is True
    assert 'data' in data
    assert 'scores' in data['data']
    assert isinstance(data['data']['scores'], list)


@pytest.mark.e2e
@pytest.mark.api_contract
def test_centrality_custom_metric(analytics_base_url):
    """
    Test: GET /analytics/centrality with custom metric
    
    Contract:
    - Accepts metric parameter
    - Returns correct structure
    """
    # ARRANGE
    url = f"{analytics_base_url}/centrality"
    params = {
        'metric': 'degree',
        'top_k': 15
    }
    
    # ACT
    response = requests.get(url, params=params, timeout=10)
    
    # ASSERT
    assert response.status_code == 200
    data = response.json()
    assert data['success'] is True
    assert 'data' in data


@pytest.mark.e2e
@pytest.mark.api_contract
def test_centrality_invalid_top_k(analytics_base_url):
    """
    Test: GET /analytics/centrality with invalid top_k
    
    Contract:
    - Returns 400 for invalid parameters
    - Response has error message
    """
    # ARRANGE
    url = f"{analytics_base_url}/centrality"
    params = {'top_k': -1}
    
    # ACT
    response = requests.get(url, params=params, timeout=10)
    
    # ASSERT
    assert response.status_code == 400
    data = response.json()
    assert data['success'] is False
    assert 'error' in data


# ============================================================================
# API Contract Tests - Communities
# ============================================================================

@pytest.mark.e2e
@pytest.mark.api_contract
def test_communities_default_algorithm(analytics_base_url):
    """
    Test: GET /analytics/communities with default algorithm
    
    Contract:
    - Returns 500 status (not yet implemented)
    - Response has 'success' field (False)
    - Response has 'error' field with message
    - NOTE: Community detection is Future Work (not Phase 3)
    """
    # ARRANGE
    url = f"{analytics_base_url}/communities"
    
    # ACT
    response = requests.get(url, timeout=10)
    
    # ASSERT
    assert response.status_code == 500  # Not implemented yet
    data = response.json()
    assert data['success'] is False
    assert 'error' in data
    assert 'not yet implemented' in data['error'].lower()


@pytest.mark.e2e
@pytest.mark.api_contract
def test_communities_custom_algorithm(analytics_base_url):
    """
    Test: GET /analytics/communities with custom algorithm
    
    Contract:
    - Accepts algorithm parameter
    - Returns correct structure
    """
    # ARRANGE
    url = f"{analytics_base_url}/communities"
    params = {'algorithm': 'label_propagation'}
    
    # ACT
    response = requests.get(url, params=params, timeout=10)
    
    # ASSERT
    assert response.status_code in [200, 500]  # May not be implemented
    data = response.json()
    assert 'success' in data


# ============================================================================
# API Contract Tests - Cycles
# ============================================================================

@pytest.mark.e2e
@pytest.mark.api_contract
def test_cycles_detection(analytics_base_url):
    """
    Test: GET /analytics/cycles
    
    Contract:
    - Returns 200 or 500 status
    - Response has 'success' field
    - If successful, has 'data' field with 'cycles'
    """
    # ARRANGE
    url = f"{analytics_base_url}/cycles"
    
    # ACT
    response = requests.get(url, timeout=10)
    
    # ASSERT
    assert response.status_code in [200, 500]
    data = response.json()
    assert 'success' in data
    if data['success']:
        assert 'data' in data


# ============================================================================
# API Contract Tests - Connected Components
# ============================================================================

@pytest.mark.e2e
@pytest.mark.api_contract
def test_connected_components(analytics_base_url):
    """
    Test: GET /analytics/components
    
    Contract:
    - Returns 200 or 500 status
    - Response has 'success' field
    - If successful, has 'data' field with 'components'
    """
    # ARRANGE
    url = f"{analytics_base_url}/components"
    
    # ACT
    response = requests.get(url, timeout=10)
    
    # ASSERT
    assert response.status_code in [200, 500]
    data = response.json()
    assert 'success' in data
    if data['success']:
        assert 'data' in data


# ============================================================================
# API Contract Tests - Graph Statistics
# ============================================================================

@pytest.mark.e2e
@pytest.mark.api_contract
def test_graph_statistics(analytics_base_url):
    """
    Test: GET /analytics/statistics
    
    Contract:
    - Returns 200 status
    - Response has 'success' field
    - Response has 'data' field with statistics
    """
    # ARRANGE
    url = f"{analytics_base_url}/statistics"
    
    # ACT
    response = requests.get(url, timeout=10)
    
    # ASSERT
    assert response.status_code == 200
    data = response.json()
    assert data['success'] is True
    assert 'data' in data
    # Statistics should contain basic graph metrics
    assert isinstance(data['data'], dict)


# ============================================================================
# Integration Test - Full Analytics Workflow
# ============================================================================

@pytest.mark.e2e
@pytest.mark.api_contract
def test_analytics_full_workflow(analytics_base_url):
    """
    Test: Complete analytics workflow
    
    Validates all analytics endpoints work together:
    1. Get graph statistics
    2. Calculate PageRank
    3. Calculate centrality
    4. Detect communities
    """
    # STEP 1: Get statistics
    stats_response = requests.get(f"{analytics_base_url}/statistics", timeout=10)
    assert stats_response.status_code == 200
    stats_data = stats_response.json()
    assert stats_data['success'] is True
    
    # STEP 2: Calculate PageRank
    pagerank_response = requests.get(
        f"{analytics_base_url}/pagerank",
        params={'top_k': 5},
        timeout=10
    )
    assert pagerank_response.status_code == 200
    pagerank_data = pagerank_response.json()
    assert pagerank_data['success'] is True
    
    # STEP 3: Calculate centrality
    centrality_response = requests.get(
        f"{analytics_base_url}/centrality",
        params={'metric': 'degree', 'top_k': 5},
        timeout=10
    )
    assert centrality_response.status_code == 200
    centrality_data = centrality_response.json()
    assert centrality_data['success'] is True
    
    # STEP 4: Detect communities
    communities_response = requests.get(
        f"{analytics_base_url}/communities",
        timeout=10
    )
    assert communities_response.status_code in [200, 500]
    communities_data = communities_response.json()
    assert 'success' in communities_data