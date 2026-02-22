"""
Test: Knowledge Graph V2 - Complete Frontend API Chain
Tests the entire flow from rebuild to graph rendering
"""
import pytest
import requests
import json

BASE_URL = "http://localhost:5000"

@pytest.mark.e2e
@pytest.mark.api_contract
def test_complete_rebuild_chain():
    """
    Test: Complete rebuild chain from backend to expected frontend format
    
    ARRANGE: None (uses existing backend)
    ACT: Call rebuild endpoint
    ASSERT: Response structure matches what frontend expects
    """
    # ACT: Trigger rebuild
    response = requests.post(
        f"{BASE_URL}/api/knowledge-graph/schema/rebuild",
        timeout=30
    )
    
    # ASSERT: Response structure
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"
    data = response.json()
    
    print("\n=== BACKEND RESPONSE STRUCTURE ===")
    print(f"Top-level keys: {list(data.keys())}")
    
    # Check top-level structure
    assert 'success' in data, "Response should have 'success' field"
    assert data['success'] is True, "Success should be True"
    assert 'data' in data, "Response should have 'data' field (wrapper)"
    
    # Check data wrapper content
    inner_data = data['data']
    print(f"Inner data keys: {list(inner_data.keys())}")
    assert 'graph' in inner_data, "Inner data should have 'graph' field"
    assert 'metadata' in inner_data, "Inner data should have 'metadata' field"
    
    # Check graph structure
    graph = inner_data['graph']
    print(f"Graph keys: {list(graph.keys())}")
    assert 'nodes' in graph, "Graph should have 'nodes' array"
    assert 'edges' in graph, "Graph should have 'edges' array"
    assert isinstance(graph['nodes'], list), "Nodes should be an array"
    assert isinstance(graph['edges'], list), "Edges should be an array"
    
    # Verify we have data
    print(f"\nGraph contains: {len(graph['nodes'])} nodes, {len(graph['edges'])} edges")
    assert len(graph['nodes']) > 0, "Should have at least one node"
    assert len(graph['edges']) > 0, "Should have at least one edge"
    
    # Check node structure (frontend expects 'id', 'label', 'type', 'properties')
    sample_node = graph['nodes'][0]
    print(f"\nSample node structure: {list(sample_node.keys())}")
    assert 'id' in sample_node, "Node should have 'id'"
    assert 'label' in sample_node, "Node should have 'label'"
    assert 'type' in sample_node, "Node should have 'type'"
    
    # Check edge structure (frontend expects 'from', 'to', 'label', 'type')
    if len(graph['edges']) > 0:
        sample_edge = graph['edges'][0]
        print(f"Sample edge structure: {list(sample_edge.keys())}")
        # Backend uses 'source_id' and 'target_id', need to verify
        assert 'from' in sample_edge or 'source_id' in sample_edge, "Edge should have 'from' or 'source_id'"
        assert 'to' in sample_edge or 'target_id' in sample_edge, "Edge should have 'to' or 'target_id'"
    
    print("\n✅ Complete chain test passed")


@pytest.mark.e2e
@pytest.mark.api_contract  
def test_schema_endpoint_structure():
    """
    Test: Schema endpoint returns correct structure
    
    This is the endpoint used by loadGraph() method
    """
    # ACT
    response = requests.get(
        f"{BASE_URL}/api/knowledge-graph/schema",
        timeout=10
    )
    
    # ASSERT
    assert response.status_code == 200
    data = response.json()
    
    print("\n=== SCHEMA ENDPOINT STRUCTURE ===")
    print(f"Top-level keys: {list(data.keys())}")
    
    assert 'success' in data
    assert 'data' in data
    
    inner_data = data['data']
    print(f"Inner data keys: {list(inner_data.keys())}")
    assert 'graph' in inner_data
    assert 'metadata' in inner_data
    
    graph = inner_data['graph']
    assert 'nodes' in graph
    assert 'edges' in graph
    
    print(f"\nSchema endpoint: {len(graph['nodes'])} nodes, {len(graph['edges'])} edges")
    print("✅ Schema endpoint structure correct")


@pytest.mark.e2e
@pytest.mark.api_contract
def test_edge_field_mapping():
    """
    Test: Verify edge field mapping (source_id/target_id vs from/to)
    
    Frontend VisJsAdapter expects 'source_id' and 'target_id'
    but vis.js needs 'from' and 'to'
    """
    # ACT
    response = requests.get(
        f"{BASE_URL}/api/knowledge-graph/schema",
        timeout=10
    )
    
    # ASSERT
    data = response.json()
    graph = data['data']['graph']
    
    if len(graph['edges']) > 0:
        edge = graph['edges'][0]
        print(f"\n=== EDGE FIELD MAPPING ===")
        print(f"Edge fields: {list(edge.keys())}")
        
        # Backend should use source_id/target_id (generic format)
        # Frontend adapter converts to from/to (vis.js format)
        assert 'source_id' in edge, "Backend should use 'source_id'"
        assert 'target_id' in edge, "Backend should use 'target_id'"
        
        print("✅ Edge fields correct (source_id/target_id)")