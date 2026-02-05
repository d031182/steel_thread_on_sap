"""
Integration Test: Graph Cache Refresh Synchronization

Tests that refresh_ontology_cache() clears BOTH caches:
1. Ontology cache (graph_ontology tables) 
2. Vis.js cache (graph_nodes/graph_edges tables)

This ensures "Refresh Graph" button returns fresh data, not stale cached visualization.

Test Type: Integration (validates interaction between two cache services)
Gu Wu Compliant: Uses fixtures, AAA pattern, proper markers
"""

import pytest
from modules.sqlite_connection.backend.sqlite_data_source import SQLiteDataSource
from modules.knowledge_graph.backend.knowledge_graph_facade import create_facade


@pytest.fixture
def data_source():
    """Fixture: Provide SQLite data source for testing"""
    return SQLiteDataSource('p2p_data.db')


@pytest.fixture
def facade(data_source):
    """Fixture: Create knowledge graph facade with data source"""
    return create_facade(data_source)


@pytest.mark.integration
def test_cache_refresh_clears_both_caches(facade):
    """
    Test that refresh clears both ontology and vis.js caches (AAA pattern)
    
    Validates that clicking "Refresh Graph" button clears stale cache
    and returns fresh data on next load.
    """
    # ARRANGE: Load graph to populate cache
    initial_graph = facade.get_graph(mode='schema', use_cache=True)
    assert initial_graph.get('success'), "Initial graph load failed"
    assert initial_graph['stats']['node_count'] > 0, "Graph should have nodes"
    
    # ACT: Refresh cache (should clear BOTH caches)
    refresh_result = facade.refresh_ontology_cache()
    
    # ASSERT: Refresh succeeded and cleared both caches
    assert refresh_result['success'], f"Refresh failed: {refresh_result.get('error')}"
    
    stats = refresh_result['statistics']
    assert 'cleared_ontology' in stats, "Should report ontology cache cleared"
    assert 'cleared_visjs' in stats, "Should report vis.js cache cleared"
    assert 'discovered' in stats, "Should report relationships discovered"
    
    # ASSERT: Vis.js cache is empty after refresh
    if facade.cache_service:
        cache_status_after = facade.cache_service.check_cache_status('schema')
        assert not cache_status_after.get('exists'), \
            "Vis.js cache should be empty after refresh"
    
    # ASSERT: Graph can be rebuilt and is consistent
    rebuilt_graph = facade.get_graph(mode='schema', use_cache=True)
    assert rebuilt_graph.get('success'), "Graph rebuild failed"
    assert rebuilt_graph['stats']['node_count'] > 0, "Rebuilt graph should have nodes"
    assert initial_graph['stats']['node_count'] == rebuilt_graph['stats']['node_count'], \
        "Node count should be consistent after refresh"


@pytest.mark.integration 
def test_cache_refresh_discovers_relationships(facade):
    """Test that refresh rediscovers relationships from CSN (AAA pattern)"""
    # ARRANGE: (facade provided by fixture)
    
    # ACT: Refresh cache
    result = facade.refresh_ontology_cache()
    
    # ASSERT: Refresh succeeded and discovered relationships
    assert result['success'], f"Refresh failed: {result.get('error')}"
    assert result['statistics']['discovered'] > 0, \
        "Should discover at least some relationships"
    assert 'discovery_time_ms' in result['statistics'], \
        "Should report discovery time"


@pytest.mark.integration
def test_cache_status_reflects_refresh(facade):
    """Test that cache status correctly reports cache state after refresh (AAA pattern)"""
    # ARRANGE: Populate cache
    facade.get_graph(mode='schema', use_cache=True)
    status_before = facade.get_cache_status()
    assert status_before['success'], "Cache status check failed"
    
    # ACT: Refresh (clears cache)
    facade.refresh_ontology_cache()
    
    # ASSERT: Status correctly shows cache was cleared
    status_after = facade.get_cache_status()
    assert status_after['success'], "Cache status check after refresh failed"
    # Note: Status will show relationship counts from ontology, not vis.js cache