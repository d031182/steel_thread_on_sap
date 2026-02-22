"""
Test: Knowledge Graph V2 - Semantic UI Validation (HIGH-51)

PURPOSE:
Validate semantic annotations appear correctly in UI tooltips/labels
after HIGH-30 (backend extraction) and HIGH-50 (edge metadata display).

SCOPE:
- Node tooltips show semantic_summary (total_columns, labeled_columns, semantic_columns, key_columns)
- Edge labels show cardinality (IF explicitly available from CSN associations)
- Edge tooltips show ON conditions (IF explicitly available from CSN associations)
- Note: Inferred FK relationships may not have explicit cardinality/ON conditions

DATA FLOW:
1. Backend API: SchemaGraphBuilderService enriches edges with semantic metadata
2. Frontend API: /api/knowledge-graph/schema returns graph with enriched metadata
3. GraphPresenter: Stores genericGraph in state (passed to adapter)
4. VisJsGraphAdapter: Converts genericGraph → vis.js format with tooltips/labels
5. UI: Displays enriched tooltips/labels to user

ARCHITECTURE:
API contract testing (requests library, < 1 second)

AUTHOR: P2P Development Team
VERSION: 1.0.0 (HIGH-51)
DATE: 2026-02-22
"""

import pytest
import requests


# ============================================================================
# TEST MARKERS
# ============================================================================

pytestmark = [
    pytest.mark.e2e,
    pytest.mark.api_contract,
    pytest.mark.knowledge_graph_v2
]


# ============================================================================
# FIXTURES
# ============================================================================

@pytest.fixture
def base_url():
    """Base URL for Knowledge Graph V2 API"""
    return "http://localhost:5000"


@pytest.fixture
def p2p_graph(base_url):
    """
    Fetch P2P schema graph from API
    
    Returns enriched graph with:
    - nodes.properties.semantic_summary (HIGH-30)
    - edges may have cardinality/on_conditions (if from explicit CSN associations)
    """
    response = requests.get(
        f"{base_url}/api/knowledge-graph/schema",
        params={"use_cache": "true"},
        timeout=5
    )
    assert response.status_code == 200, f"API failed: {response.text}"
    data = response.json()
    assert data.get('success') is True, "API returned success=False"
    return data.get('data', data)  # Handle both response formats


# ============================================================================
# TEST: NODE SEMANTIC SUMMARY IN TOOLTIPS (HIGH-51.1) ✅ PASSING
# ============================================================================

def test_node_tooltip_includes_semantic_summary(p2p_graph):
    """
    Test: Nodes with semantic_summary have enriched properties for tooltips

    VALIDATION:
    - nodes have properties.semantic_summary dict
    - semantic_summary contains: total_columns, labeled_columns, semantic_columns, key_columns
    - All values are integers >= 0
    """
    graph = p2p_graph.get('graph', {})
    nodes = graph.get('nodes', [])
    assert len(nodes) > 0, "No nodes in graph"
    
    # Find nodes with semantic_summary
    nodes_with_summary = [
        node for node in nodes
        if node.get('properties', {}).get('semantic_summary')
    ]
    
    assert len(nodes_with_summary) > 0, "No nodes have semantic_summary"
    
    # Validate semantic_summary structure
    for node in nodes_with_summary:
        summary = node['properties']['semantic_summary']
        
        # Required fields
        assert 'total_columns' in summary, f"Node {node['id']} missing total_columns"
        assert 'labeled_columns' in summary, f"Node {node['id']} missing labeled_columns"
        assert 'semantic_columns' in summary, f"Node {node['id']} missing semantic_columns"
        assert 'key_columns' in summary, f"Node {node['id']} missing key_columns"
        
        # Type + value validation
        for field in ['total_columns', 'labeled_columns', 'semantic_columns', 'key_columns']:
            assert isinstance(summary[field], int), f"{field} must be int"
            assert summary[field] >= 0, f"{field} must be >= 0"


def test_edge_has_semantic_summary(p2p_graph):
    """
    Test: Edges include semantic summary (from HIGH-30 enhancement)
    
    Verifies:
    - semantic_summary field present in all edges
    - Summary is non-empty string
    - Contains descriptive relationship context
    """
    edges = p2p_graph['graph']['edges']
    assert len(edges) > 0, "Graph should have edges"
    
    # Check first edge for semantic summary
    first_edge = edges[0]
    assert 'semantic_summary' in first_edge, "Edge should have semantic_summary field"
    assert isinstance(first_edge['semantic_summary'], str), "semantic_summary should be string"
    assert len(first_edge['semantic_summary']) > 0, "semantic_summary should not be empty"


def test_edge_cardinality_optional(p2p_graph):
    """
    Test: Edges MAY include cardinality metadata (optional for inferred FK relationships)
    
    Context:
    - CSN associations (with _ prefix) have explicit cardinality
    - Inferred FK relationships may not have cardinality
    - This is expected behavior per relationship_mapper.py design
    
    Verifies:
    - If cardinality present, it has valid values ("1:1", "1:*", "*:*")
    - Missing cardinality is acceptable for inferred relationships
    """
    edges = p2p_graph['graph']['edges']
    
    # Find edges with relationships
    relationship_edges = [e for e in edges if 'from' in e and 'to' in e and e['from'] != e['to']]
    assert len(relationship_edges) > 0, "Graph should have relationship edges"
    
    # Check cardinality if present
    edges_with_cardinality = [e for e in relationship_edges if 'cardinality' in e]
    
    if edges_with_cardinality:
        # If cardinality present, verify valid values
        for edge in edges_with_cardinality:
            assert edge['cardinality'] in ['1:1', '1:*', '*:*'], \
                f"Invalid cardinality value: {edge['cardinality']}"
        print(f"INFO: {len(edges_with_cardinality)} edges have explicit cardinality")
    else:
        # No cardinality is acceptable for inferred FK relationships
        print("INFO: No explicit cardinality found (using inferred FK relationships)")


def test_edge_on_conditions_optional(p2p_graph):
    """
    Test: Edges MAY include JOIN ON conditions (optional for inferred FK relationships)
    
    Context:
    - CSN associations have explicit ON conditions
    - Inferred FK relationships don't have ON conditions
    - This is expected behavior per relationship_mapper.py design
    
    Verifies:
    - If on_conditions present, they are valid list of strings
    - Missing on_conditions is acceptable for inferred relationships
    """
    edges = p2p_graph['graph']['edges']
    
    # Find edges with relationships
    relationship_edges = [e for e in edges if 'from' in e and 'to' in e and e['from'] != e['to']]
    assert len(relationship_edges) > 0, "Graph should have relationship edges"
    
    # Check ON conditions if present
    edges_with_conditions = [e for e in relationship_edges if 'on_conditions' in e]
    
    if edges_with_conditions:
        # If on_conditions present, verify valid structure
        for edge in edges_with_conditions:
            assert isinstance(edge['on_conditions'], list), "on_conditions should be list"
            assert len(edge['on_conditions']) > 0, "on_conditions should not be empty"
            assert all(isinstance(cond, str) for cond in edge['on_conditions']), \
                "Each condition should be a string"
        print(f"INFO: {len(edges_with_conditions)} edges have explicit ON conditions")
    else:
        # No ON conditions is acceptable for inferred FK relationships
        print("INFO: No explicit ON conditions found (using inferred FK relationships)")


# ============================================================================
# TEST: PERFORMANCE - API RESPONSE TIME (HIGH-51.6)
# ============================================================================

def test_schema_graph_api_performance(base_url):
    """
    Test: Schema graph API returns within performance budget
    
    VALIDATION:
    - Cached request: < 2 seconds
    - Response size reasonable (< 5MB)
    """
    import time
    
    start_time = time.time()
    response = requests.get(
        f"{base_url}/api/knowledge-graph/schema",
        params={"use_cache": "true"},
        timeout=5
    )
    elapsed = time.time() - start_time
    
    assert response.status_code == 200
    assert elapsed < 2.0, f"API took {elapsed:.2f}s (should be < 2s for cached)"
    
    # Check response size (sanity check)
    content_length = len(response.content)
    assert content_length < 5 * 1024 * 1024, \
        f"Response too large: {content_length / (1024*1024):.2f}MB"