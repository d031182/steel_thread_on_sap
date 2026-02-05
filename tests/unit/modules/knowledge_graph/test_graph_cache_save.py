"""
Unit tests for graph cache saving functionality

Tests that KnowledgeGraphFacade.get_graph() correctly saves cache
to graph_nodes and graph_edges tables after building graph.

@marks: unit, fast
"""

import pytest
import sqlite3
from pathlib import Path
from modules.sqlite_connection.backend.sqlite_data_source import SQLiteDataSource
from modules.knowledge_graph.backend.knowledge_graph_facade import KnowledgeGraphFacade
from core.services.graph_cache_service import GraphCacheService


@pytest.fixture
def db_path():
    """Get path to graph cache database"""
    project_root = Path(__file__).parent.parent.parent.parent.parent
    return project_root / 'modules' / 'knowledge_graph' / 'database' / 'graph_cache.db'


@pytest.fixture
def cache_service(db_path):
    """Create GraphCacheService instance"""
    return GraphCacheService(str(db_path))


@pytest.fixture
def facade():
    """Create KnowledgeGraphFacade with SQLite data source"""
    data_source = SQLiteDataSource()
    return KnowledgeGraphFacade(data_source)


@pytest.mark.unit
@pytest.mark.fast
def test_graph_cache_save_on_build(facade, cache_service, db_path):
    """
    Test that get_graph() saves cache after building graph
    
    AAA Pattern:
    - Arrange: Clear cache, verify empty
    - Act: Build graph with use_cache=False
    - Assert: Cache populated with nodes/edges
    """
    # ARRANGE - Clear cache and verify empty
    cache_service.clear_cache()
    
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()
    
    cursor.execute("SELECT COUNT(*) FROM graph_nodes")
    nodes_before = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM graph_edges")
    edges_before = cursor.fetchone()[0]
    
    assert nodes_before == 0, "Cache should be empty after clear"
    assert edges_before == 0, "Cache should be empty after clear"
    
    # ACT - Build graph (should trigger cache save)
    result = facade.get_graph(mode='schema', use_cache=False)
    
    # ASSERT - Graph built successfully
    assert result.get('success') is True, f"Graph build failed: {result.get('error')}"
    assert result['stats']['node_count'] > 0, "Graph should have nodes"
    assert result['stats']['edge_count'] > 0, "Graph should have edges"
    
    # ASSERT - Cache is now populated
    cursor.execute("SELECT COUNT(*) FROM graph_nodes")
    nodes_after = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM graph_edges")
    edges_after = cursor.fetchone()[0]
    
    conn.close()
    
    assert nodes_after > 0, "graph_nodes should be populated after build"
    assert edges_after > 0, "graph_edges should be populated after build"
    
    # ASSERT - Cache matches result
    assert nodes_after == result['stats']['node_count'], \
        f"Node count mismatch (cache={nodes_after}, result={result['stats']['node_count']})"
    assert edges_after == result['stats']['edge_count'], \
        f"Edge count mismatch (cache={edges_after}, result={result['stats']['edge_count']})"


@pytest.mark.unit
@pytest.mark.fast
def test_graph_cache_hit_after_save(facade, cache_service):
    """
    Test that get_graph() returns cached data on second call
    
    AAA Pattern:
    - Arrange: Build graph once (saves to cache)
    - Act: Request graph again with use_cache=True
    - Assert: Returns instantly from cache
    """
    # ARRANGE - Build and cache
    result1 = facade.get_graph(mode='schema', use_cache=False)
    assert result1.get('success') is True
    
    # ACT - Request again with cache enabled
    result2 = facade.get_graph(mode='schema', use_cache=True)
    
    # ASSERT - Got same data from cache
    assert result2.get('success') is True
    assert result2['stats'].get('cache_exists') is True, "Should indicate cache hit"
    assert result2['stats']['node_count'] == result1['stats']['node_count']
    assert result2['stats']['edge_count'] == result1['stats']['edge_count']


@pytest.mark.unit
def test_graph_cache_metadata_saved(facade, cache_service, db_path):
    """
    Test that metadata is saved with cache
    
    AAA Pattern:
    - Arrange: Clear cache
    - Act: Build graph
    - Assert: Metadata table populated correctly
    """
    # ARRANGE
    cache_service.clear_cache()
    
    # ACT
    result = facade.get_graph(mode='schema', use_cache=False)
    assert result.get('success') is True
    
    # ASSERT - Check metadata
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT graph_type, node_count, edge_count, created_at 
        FROM graph_cache_metadata 
        ORDER BY created_at DESC 
        LIMIT 1
    """)
    metadata = cursor.fetchone()
    conn.close()
    
    assert metadata is not None, "Metadata should be saved"
    assert metadata[0] == 'schema', "Graph type should be 'schema'"
    assert metadata[1] == result['stats']['node_count'], "Node count should match"
    assert metadata[2] == result['stats']['edge_count'], "Edge count should match"
    assert metadata[3] is not None, "Created timestamp should exist"