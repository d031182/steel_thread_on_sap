"""
Test: Knowledge Graph V2 - Rebuild triggers graph rendering
Validates that rebuild automatically loads and displays the graph
"""
import pytest
import requests
import time

BASE_URL = "http://localhost:5000"

@pytest.mark.e2e
@pytest.mark.api_contract
def test_rebuild_triggers_data_load():
    """
    Test: Rebuild should automatically load graph data
    
    ARRANGE: None (uses existing backend)
    ACT: Trigger rebuild, then fetch graphs
    ASSERT: Graph data is available after rebuild
    """
    # ACT: Trigger rebuild
    rebuild_response = requests.post(
        f"{BASE_URL}/api/knowledge-graph-v2/rebuild",
        timeout=30
    )
    
    # ASSERT: Rebuild succeeded
    assert rebuild_response.status_code == 200
    rebuild_data = rebuild_response.json()
    assert rebuild_data['success'] is True, "Rebuild should succeed"
    
    # Wait briefly for cache to update
    time.sleep(0.5)
    
    # ACT: Fetch graphs (simulating what frontend does after rebuild)
    graphs_response = requests.get(
        f"{BASE_URL}/api/knowledge-graph-v2/graphs",
        timeout=10
    )
    
    # ASSERT: Graphs are available
    assert graphs_response.status_code == 200
    graphs_data = graphs_response.json()
    assert 'graphs' in graphs_data, "Response should contain graphs"
    assert len(graphs_data['graphs']) > 0, "Should have at least one graph"
    
    # Verify schema graph exists and has data
    schema_graph = next(
        (g for g in graphs_data['graphs'] if g['name'] == 'HANA Schema Graph'),
        None
    )
    assert schema_graph is not None, "Schema graph should exist"
    assert schema_graph['node_count'] > 0, "Schema graph should have nodes"
    assert schema_graph['edge_count'] > 0, "Schema graph should have edges"
    
    print(f"✅ Rebuild + Load verified: {schema_graph['node_count']} nodes, {schema_graph['edge_count']} edges")


@pytest.mark.e2e  
@pytest.mark.api_contract
def test_rebuild_cache_info():
    """
    Test: Rebuild returns cache status information
    
    ARRANGE: None
    ACT: Trigger rebuild
    ASSERT: Response includes cache_info
    """
    # ACT
    response = requests.post(
        f"{BASE_URL}/api/knowledge-graph-v2/rebuild",
        timeout=30
    )
    
    # ASSERT
    assert response.status_code == 200
    data = response.json()
    assert 'cache_info' in data, "Response should include cache_info"
    
    cache_info = data['cache_info']
    assert 'total_nodes' in cache_info, "cache_info should include total_nodes"
    assert 'total_edges' in cache_info, "cache_info should include total_edges"
    assert cache_info['total_nodes'] > 0, "Should have nodes in cache"
    
    print(f"✅ Cache info verified: {cache_info['total_nodes']} nodes in cache")