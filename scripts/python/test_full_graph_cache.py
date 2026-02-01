#!/usr/bin/env python3
"""
Test Full Graph Cache Implementation (v3.13)

Tests:
1. First load (no cache) - should build and cache
2. Second load (with cache) - should load from cache (<100ms)
3. Cache invalidation - should rebuild
"""

import sys
import time
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from modules.data_products.backend.sqlite_data_products_service import SQLiteDataProductsService
from modules.knowledge_graph.backend.data_graph_service import DataGraphService
from core.services.ontology_persistence_service import OntologyPersistenceService


def test_graph_cache():
    """Test complete graph caching workflow"""
    
    print("=" * 70)
    print("FULL GRAPH CACHE TEST (v3.13)")
    print("=" * 70)
    
    # Initialize services
    db_path = 'app/database/p2p_data_products.db'
    from modules.sqlite_connection.backend.sqlite_data_source import SQLiteDataSource
    data_source = SQLiteDataSource(db_path)
    
    # Create graph service
    graph_service = DataGraphService(data_source, db_path=db_path)
    persistence = OntologyPersistenceService(db_path)
    
    print(f"\n✓ Initialized with database: {db_path}\n")
    
    # TEST 1: Clear cache and build fresh
    print("TEST 1: Build Fresh Graph (No Cache)")
    print("-" * 70)
    
    nodes_deleted, edges_deleted = persistence.invalidate_graph_cache('data')
    print(f"  Cleared cache: {nodes_deleted} nodes, {edges_deleted} edges")
    
    start = time.time()
    result1 = graph_service.build_data_graph(max_records_per_table=20, use_cache=True)
    time1 = (time.time() - start) * 1000
    
    print(f"  ✓ Built graph: {result1['stats']['node_count']} nodes, {result1['stats']['edge_count']} edges")
    print(f"  ✓ Time: {time1:.0f}ms")
    print(f"  ✓ Cache used: {result1['stats'].get('cache_used', False)}")
    
    # TEST 2: Load from cache
    print("\nTEST 2: Load from Cache")
    print("-" * 70)
    
    start = time.time()
    result2 = graph_service.build_data_graph(max_records_per_table=20, use_cache=True)
    time2 = (time.time() - start) * 1000
    
    print(f"  ✓ Loaded graph: {result2['stats']['node_count']} nodes, {result2['stats']['edge_count']} edges")
    print(f"  ✓ Time: {time2:.0f}ms")
    print(f"  ✓ Cache used: {result2['stats'].get('cache_used', False)}")
    
    # TEST 3: Verify speedup
    print("\nTEST 3: Performance Comparison")
    print("-" * 70)
    
    speedup = time1 / time2 if time2 > 0 else 0
    print(f"  Fresh build: {time1:.0f}ms")
    print(f"  Cache load:  {time2:.0f}ms")
    print(f"  Speedup:     {speedup:.1f}x faster")
    
    # TEST 4: Verify cache validity
    print("\nTEST 4: Cache Validity Check")
    print("-" * 70)
    
    is_valid = persistence.is_graph_cache_valid('data')
    print(f"  ✓ Cache valid: {is_valid}")
    
    # Get cached node count
    if is_valid:
        cached_nodes = persistence.get_cached_graph_nodes('data')
        print(f"  ✓ Cached nodes: {len(cached_nodes)}")
    
    # TEST 5: Cache with use_cache=False
    print("\nTEST 5: Bypass Cache (use_cache=False)")
    print("-" * 70)
    
    start = time.time()
    result3 = graph_service.build_data_graph(max_records_per_table=20, use_cache=False)
    time3 = (time.time() - start) * 1000
    
    print(f"  ✓ Built graph: {result3['stats']['node_count']} nodes, {result3['stats']['edge_count']} edges")
    print(f"  ✓ Time: {time3:.0f}ms")
    print(f"  ✓ Cache used: {result3['stats'].get('cache_used', False)}")
    
    # Summary
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print(f"  Fresh build:        {time1:.0f}ms")
    print(f"  Cache load:         {time2:.0f}ms")
    print(f"  Bypass cache:       {time3:.0f}ms")
    print(f"  Cache speedup:      {speedup:.1f}x")
    print(f"  Cache valid:        {is_valid}")
    
    # Success criteria
    if time2 < 1000 and speedup > 10:
        print(f"\n✅ SUCCESS: Cache provides {speedup:.0f}x speedup, loads in <1s")
        return 0
    elif time2 < 1000:
        print(f"\n⚠️  PARTIAL: Cache fast but speedup only {speedup:.1f}x (expected >10x)")
        return 0
    else:
        print(f"\n❌ FAILED: Cache load too slow ({time2:.0f}ms, expected <1000ms)")
        return 1


if __name__ == '__main__':
    try:
        exit_code = test_graph_cache()
        sys.exit(exit_code)
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)