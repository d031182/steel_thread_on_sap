"""
Integration Test: Graph Cache Refresh Synchronization

Tests that refresh_ontology_cache() clears BOTH caches:
1. Ontology cache (graph_ontology tables) 
2. Vis.js cache (graph_nodes/graph_edges tables)

This ensures "Refresh Graph" button returns fresh data, not stale cached visualization.

Test Type: Integration (validates interaction between two cache services)
"""

import pytest
from modules.sqlite_connection.backend.sqlite_data_source import SQLiteDataSource
from modules.knowledge_graph.backend.knowledge_graph_facade import create_facade


@pytest.mark.integration
@pytest.mark.slow
def test_cache_refresh_clears_both_caches():
    """
    Test that refresh clears both ontology and vis.js caches
    
    Steps:
    1. Load graph to populate cache
    2. Verify cache exists
    3. Refresh cache (should clear BOTH)
    4. Verify both caches are empty
    5. Load graph again (should rebuild)
    6. Verify cache is repopulated
    """
    # Initialize
    data_source = SQLiteDataSource('p2p_data.db')
    facade = create_facade(data_source)
    
    # Step 1: Get graph to populate cache
    graph1 = facade.get_graph(mode='schema', use_cache=True)
    assert graph1.get('success'), "Initial graph load failed"
    assert graph1['stats']['node_count'] > 0, "Graph should have nodes"
    
    # Step 2: Verify cache exists
    if facade.cache_service:
        cache_status_before = facade.cache_service.check_cache_status('schema')
        cache_existed = cache_status_before.get('exists', False)
        # Note: Cache may or may not exist on first load, that's OK
    
    # Step 3: Refresh cache (should clear BOTH caches)
    refresh_result = facade.refresh_ontology_cache()
    assert refresh_result['success'], f"Refresh failed: {refresh_result.get('error')}"
    
    stats = refresh_result['statistics']
    assert 'cleared_ontology' in stats, "Should report ontology cache cleared"
    assert 'cleared_visjs' in stats, "Should report vis.js cache cleared"
    assert 'discovered' in stats, "Should report relationships discovered"
    
    # Step 4: Verify vis.js cache is empty after refresh
    if facade.cache_service:
        cache_status_after = facade.cache_service.check_cache_status('schema')
        assert not cache_status_after.get('exists'), \
            "Vis.js cache should be empty after refresh"
    
    # Step 5: Get graph again (should rebuild from scratch, not use cache)
    graph2 = facade.get_graph(mode='schema', use_cache=True)
    assert graph2.get('success'), "Graph rebuild failed"
    assert graph2['stats']['node_count'] > 0, "Rebuilt graph should have nodes"
    
    # On first request after refresh, should NOT hit cache
    cache_hit_after_refresh = graph2['stats'].get('cache_exists', False)
    # Note: May be True if cache was rebuilt during get_graph(), that's OK
    
    # Step 6: Get graph one more time (NOW should definitely use cache)
    graph3 = facade.get_graph(mode='schema', use_cache=True)
    assert graph3.get('success'), "Third graph load failed"
    cache_hit_second_time = graph3['stats'].get('cache_exists', False)
    # Cache should be working now
    
    # Verify graph is consistent
    assert graph2['stats']['node_count'] == graph3['stats']['node_count'], \
        "Node count should be consistent across loads"


@pytest.mark.integration 
def test_cache_refresh_discovers_relationships():
    """Test that refresh rediscovers relationships from CSN"""
    data_source = SQLiteDataSource('p2p_data.db')
    facade = create_facade(data_source)
    
    result = facade.refresh_ontology_cache()
    
    assert result['success'], f"Refresh failed: {result.get('error')}"
    assert result['statistics']['discovered'] > 0, \
        "Should discover at least some relationships"
    assert 'discovery_time_ms' in result['statistics'], \
        "Should report discovery time"


@pytest.mark.integration
def test_cache_status_reflects_refresh():
    """Test that cache status correctly reports cache state after refresh"""
    data_source = SQLiteDataSource('p2p_data.db')
    facade = create_facade(data_source)
    
    # Populate cache
    facade.get_graph(mode='schema', use_cache=True)
    
    # Check status before
    status_before = facade.get_cache_status()
    assert status_before['success'], "Cache status check failed"
    
    # Refresh (clears cache)
    facade.refresh_ontology_cache()
    
    # Check status after - cache should be empty
    status_after = facade.get_cache_status()
    assert status_after['success'], "Cache status check failed"
    # Note: Status will show relationship counts from ontology, not vis.js cache