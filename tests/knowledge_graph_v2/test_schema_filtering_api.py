"""
API Contract Tests for Knowledge Graph Schema Filtering

Tests the new filtering, pagination, and summary capabilities.
"""
import pytest
import requests


@pytest.mark.e2e
@pytest.mark.api_contract
def test_schema_summary_endpoint():
    """Test: GET /api/knowledge-graph/schema?summary=true returns summary only"""
    # ARRANGE
    url = "http://localhost:5000/api/knowledge-graph/schema?summary=true"
    
    # ACT
    response = requests.get(url, timeout=10)
    
    # ASSERT
    assert response.status_code == 200
    data = response.json()
    assert data['success'] is True
    assert 'data' in data
    assert 'summary' in data['data']
    
    summary = data['data']['summary']
    assert 'total_nodes' in summary
    assert 'total_edges' in summary
    assert 'entity_types' in summary
    assert 'relationship_types' in summary
    assert isinstance(summary['total_nodes'], int)
    assert isinstance(summary['total_edges'], int)
    assert isinstance(summary['entity_types'], dict)
    assert isinstance(summary['relationship_types'], dict)
    
    # Summary should NOT include graph data
    assert 'graph' not in data['data']


@pytest.mark.e2e
@pytest.mark.api_contract
def test_schema_pagination():
    """Test: GET /api/knowledge-graph/schema?limit=10&offset=0 returns paginated results"""
    # ARRANGE
    url = "http://localhost:5000/api/knowledge-graph/schema?limit=10&offset=0"
    
    # ACT
    response = requests.get(url, timeout=10)
    
    # ASSERT
    assert response.status_code == 200
    data = response.json()
    assert data['success'] is True
    assert 'data' in data
    
    # Check pagination metadata
    assert 'pagination' in data['data']
    pagination = data['data']['pagination']
    assert 'total_nodes' in pagination
    assert 'returned_nodes' in pagination
    assert 'offset' in pagination
    assert 'limit' in pagination
    assert pagination['returned_nodes'] <= 10
    assert pagination['offset'] == 0
    assert pagination['limit'] == 10
    
    # Check graph data
    assert 'graph' in data['data']
    graph = data['data']['graph']
    assert 'nodes' in graph
    assert 'edges' in graph
    assert len(graph['nodes']) <= 10


@pytest.mark.e2e
@pytest.mark.api_contract
def test_schema_entity_type_filtering():
    """Test: Filter by entity types returns only specified types"""
    # ARRANGE
    url = "http://localhost:5000/api/knowledge-graph/schema?entity_types=PurchaseOrder,Invoice"
    
    # ACT
    response = requests.get(url, timeout=10)
    
    # ASSERT
    assert response.status_code == 200
    data = response.json()
    assert data['success'] is True
    
    # Check that only specified entity types are returned
    graph = data['data']['graph']
    nodes = graph['nodes']
    
    for node in nodes:
        entity_type = node.get('type') or node.get('entity_type')
        assert entity_type in ['PurchaseOrder', 'Invoice'], \
            f"Unexpected entity type: {entity_type}"


@pytest.mark.e2e
@pytest.mark.api_contract
def test_schema_without_edges():
    """Test: GET /api/knowledge-graph/schema?include_edges=false returns nodes only"""
    # ARRANGE
    url = "http://localhost:5000/api/knowledge-graph/schema?include_edges=false"
    
    # ACT
    response = requests.get(url, timeout=10)
    
    # ASSERT
    assert response.status_code == 200
    data = response.json()
    assert data['success'] is True
    
    # Check that edges are empty
    graph = data['data']['graph']
    assert 'edges' in graph
    assert len(graph['edges']) == 0
    
    # But nodes should still be present
    assert 'nodes' in graph
    assert len(graph['nodes']) > 0


@pytest.mark.e2e
@pytest.mark.api_contract
def test_schema_combined_filters():
    """Test: Combine multiple filters (entity_types + limit + no edges)"""
    # ARRANGE
    url = "http://localhost:5000/api/knowledge-graph/schema?entity_types=PurchaseOrder&limit=5&include_edges=false"
    
    # ACT
    response = requests.get(url, timeout=10)
    
    # ASSERT
    assert response.status_code == 200
    data = response.json()
    assert data['success'] is True
    
    graph = data['data']['graph']
    nodes = graph['nodes']
    edges = graph['edges']
    
    # Check pagination
    assert len(nodes) <= 5
    
    # Check entity type filtering
    for node in nodes:
        entity_type = node.get('type') or node.get('entity_type')
        assert entity_type == 'PurchaseOrder'
    
    # Check edges excluded
    assert len(edges) == 0


@pytest.mark.e2e
@pytest.mark.api_contract
def test_schema_invalid_limit():
    """Test: Invalid limit parameter returns 400 error"""
    # ARRANGE
    url = "http://localhost:5000/api/knowledge-graph/schema?limit=0"
    
    # ACT
    response = requests.get(url, timeout=10)
    
    # ASSERT
    assert response.status_code == 400
    data = response.json()
    assert data['success'] is False
    assert 'error' in data
    assert 'limit must be >= 1' in data['error']


@pytest.mark.e2e
@pytest.mark.api_contract
def test_schema_invalid_offset():
    """Test: Invalid offset parameter returns 400 error"""
    # ARRANGE
    url = "http://localhost:5000/api/knowledge-graph/schema?offset=-1"
    
    # ACT
    response = requests.get(url, timeout=10)
    
    # ASSERT
    assert response.status_code == 400
    data = response.json()
    assert data['success'] is False
    assert 'error' in data
    assert 'offset must be >= 0' in data['error']


@pytest.mark.e2e
@pytest.mark.api_contract
def test_schema_pagination_second_page():
    """Test: Pagination with offset works correctly"""
    # ARRANGE - Get first page
    url_page1 = "http://localhost:5000/api/knowledge-graph/schema?limit=5&offset=0"
    response_page1 = requests.get(url_page1, timeout=10)
    data_page1 = response_page1.json()
    nodes_page1 = data_page1['data']['graph']['nodes']
    
    # ACT - Get second page
    url_page2 = "http://localhost:5000/api/knowledge-graph/schema?limit=5&offset=5"
    response_page2 = requests.get(url_page2, timeout=10)
    
    # ASSERT
    assert response_page2.status_code == 200
    data_page2 = response_page2.json()
    assert data_page2['success'] is True
    
    nodes_page2 = data_page2['data']['graph']['nodes']
    
    # Verify different nodes returned (if total > 5)
    if data_page1['data']['pagination']['total_nodes'] > 5:
        page1_ids = {n['id'] for n in nodes_page1}
        page2_ids = {n['id'] for n in nodes_page2}
        assert len(page1_ids.intersection(page2_ids)) == 0, \
            "Pages should not contain overlapping nodes"


@pytest.mark.e2e
@pytest.mark.api_contract
def test_schema_summary_performance():
    """Test: Summary endpoint is faster than full graph (< 2 seconds)"""
    import time
    
    # ARRANGE
    url = "http://localhost:5000/api/knowledge-graph/schema?summary=true"
    
    # ACT
    start = time.time()
    response = requests.get(url, timeout=10)
    elapsed = time.time() - start
    
    # ASSERT
    assert response.status_code == 200
    assert elapsed < 2.0, f"Summary endpoint took {elapsed:.2f}s (should be < 2s)"
    
    data = response.json()
    assert data['success'] is True
    assert 'summary' in data['data']