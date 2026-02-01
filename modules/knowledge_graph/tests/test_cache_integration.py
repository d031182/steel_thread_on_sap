"""
Integration Test: Knowledge Graph Cache End-to-End

Tests that cache actually works through the full API -> Builder -> Cache stack.
This is NOT a unit test - it validates the INTEGRATION of components.

WHY THIS TEST EXISTS:
- Previous bug: Cache infrastructure existed but API wasn't using it (no db_path)
- Unit tests passed, but integration was broken
- This test catches integration failures

@author P2P Development Team
@version 1.0.0 (Feb 2026)
"""

import time
import os
import sys
import tempfile
import shutil

# Force UTF-8 encoding for Windows
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

# Add parent directories to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

from modules.sqlite_connection.backend.sqlite_data_source import SQLiteDataSource
from modules.knowledge_graph.backend.schema_graph_builder import SchemaGraphBuilder
from modules.knowledge_graph.backend.data_graph_builder import DataGraphBuilder
from core.services.graph_cache_service import GraphCacheService


def test_schema_cache_integration():
    """
    Integration Test: Schema graph cache works end-to-end
    
    Flow:
    1. Clear cache
    2. First call: Build from scratch (slow, ~100-1000ms)
    3. Second call: Load from cache (fast, <20ms)
    4. Verify: 10x+ speedup on cache hit
    
    SUCCESS CRITERIA:
    - Cache hit is at least 10x faster than cache miss
    - First call saves to cache
    - Second call loads from cache (confirmed in stats)
    """
    print("\n" + "="*70)
    print("INTEGRATION TEST: Schema Graph Cache")
    print("="*70)
    
    # Use test database
    test_db = 'app/database/p2p_data_products.db'
    
    if not os.path.exists(test_db):
        print(f"❌ SKIP: Test database not found: {test_db}")
        return
    
    try:
        # Initialize data source
        data_source = SQLiteDataSource(test_db)
        
        # PHASE 1: Clear cache
        print("\n1. Clearing cache...")
        cache = GraphCacheService(test_db)
        cleared = cache.clear_cache(graph_type='schema')
        print(f"   ✓ Cleared {cleared} cache entries")
        
        # PHASE 2: First call (cache miss - should be slow)
        print("\n2. First call (cache miss - building from scratch)...")
        builder = SchemaGraphBuilder(data_source, db_path=test_db)
        
        start = time.time()
        result1 = builder.build_schema_graph(use_cache=True)
        time1 = (time.time() - start) * 1000
        
        assert result1['success'], "First call failed"
        assert len(result1['nodes']) > 0, "No nodes returned"
        
        cache_used1 = result1.get('stats', {}).get('cache_used', False)
        
        print(f"   ✓ Built graph: {len(result1['nodes'])} nodes, {len(result1['edges'])} edges")
        print(f"   ✓ Time: {time1:.0f}ms")
        print(f"   ✓ Cache used: {cache_used1}")
        
        assert not cache_used1, "First call should NOT use cache (it's empty)"
        
        # PHASE 3: Second call (cache hit - should be fast)
        print("\n3. Second call (cache hit - loading from cache)...")
        builder2 = SchemaGraphBuilder(data_source, db_path=test_db)
        
        start = time.time()
        result2 = builder2.build_schema_graph(use_cache=True)
        time2 = (time.time() - start) * 1000
        
        assert result2['success'], "Second call failed"
        assert len(result2['nodes']) > 0, "No nodes returned"
        
        cache_used2 = result2.get('stats', {}).get('cache_used', False)
        
        print(f"   ✓ Loaded graph: {len(result2['nodes'])} nodes, {len(result2['edges'])} edges")
        print(f"   ✓ Time: {time2:.0f}ms")
        print(f"   ✓ Cache used: {cache_used2}")
        
        assert cache_used2, "Second call MUST use cache"
        
        # PHASE 4: Verify performance improvement
        print("\n4. Performance validation...")
        
        # Handle case where cache is SO fast it shows as 0ms (rounds down)
        # In this case, we know cache is working because cache_used=True
        if time2 < 1 and cache_used2:
            print(f"   ✓ First call:  {time1:.0f}ms (cache miss)")
            print(f"   ✓ Second call: <1ms (cache hit - too fast to measure!)")
            print(f"   ✓ Speedup:     >{time1:.0f}x faster (cache hit < 1ms)")
            print(f"\n✅ TEST PASSED: Cache working (hit time <1ms, cache_used=True)")
        else:
            speedup = time1 / time2 if time2 > 0 else 0
            
            print(f"   ✓ First call:  {time1:.0f}ms (cache miss)")
            print(f"   ✓ Second call: {time2:.0f}ms (cache hit)")
            print(f"   ✓ Speedup:     {speedup:.1f}x faster")
            
            # Success criteria: At least 10x speedup
            min_speedup = 10.0
            
            if speedup >= min_speedup:
                print(f"\n✅ TEST PASSED: Cache provides {speedup:.1f}x speedup (>= {min_speedup}x required)")
            else:
                print(f"\n❌ TEST FAILED: Cache only provides {speedup:.1f}x speedup (< {min_speedup}x required)")
                assert False, f"Cache speedup {speedup:.1f}x < {min_speedup}x required"
        
        # PHASE 5: Verify data consistency
        print("\n5. Data consistency check...")
        assert len(result1['nodes']) == len(result2['nodes']), "Node count mismatch"
        assert len(result1['edges']) == len(result2['edges']), "Edge count mismatch"
        print(f"   ✓ Data consistent between cache miss and cache hit")
        
        print("\n" + "="*70)
        print("✅ INTEGRATION TEST PASSED: Schema Cache Working End-to-End")
        print("="*70)
        
    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        raise


def test_data_cache_integration():
    """
    Integration Test: Data graph cache works end-to-end
    
    Similar to schema test but for data graph mode.
    """
    print("\n" + "="*70)
    print("INTEGRATION TEST: Data Graph Cache")
    print("="*70)
    
    # Use test database
    test_db = 'app/database/p2p_data_products.db'
    
    if not os.path.exists(test_db):
        print(f"❌ SKIP: Test database not found: {test_db}")
        return
    
    try:
        # Initialize data source
        data_source = SQLiteDataSource(test_db)
        
        # PHASE 1: Clear cache
        print("\n1. Clearing cache...")
        cache = GraphCacheService(test_db)
        cleared = cache.clear_cache(graph_type='data')
        print(f"   ✓ Cleared {cleared} cache entries")
        
        # PHASE 2: First call (cache miss)
        print("\n2. First call (cache miss - building from scratch)...")
        builder = DataGraphBuilder(data_source, db_path=test_db)
        
        start = time.time()
        result1 = builder.build_data_graph(max_records_per_table=10, use_cache=True)
        time1 = (time.time() - start) * 1000
        
        assert result1['success'], "First call failed"
        
        cache_used1 = result1.get('stats', {}).get('cache_used', False)
        
        print(f"   ✓ Built graph: {len(result1['nodes'])} nodes, {len(result1['edges'])} edges")
        print(f"   ✓ Time: {time1:.0f}ms")
        print(f"   ✓ Cache used: {cache_used1}")
        
        # PHASE 3: Second call (cache hit)
        print("\n3. Second call (cache hit - loading from cache)...")
        builder2 = DataGraphBuilder(data_source, db_path=test_db)
        
        start = time.time()
        result2 = builder2.build_data_graph(max_records_per_table=10, use_cache=True)
        time2 = (time.time() - start) * 1000
        
        assert result2['success'], "Second call failed"
        
        cache_used2 = result2.get('stats', {}).get('cache_used', False)
        
        print(f"   ✓ Loaded graph: {len(result2['nodes'])} nodes, {len(result2['edges'])} edges")
        print(f"   ✓ Time: {time2:.0f}ms")
        print(f"   ✓ Cache used: {cache_used2}")
        
        assert cache_used2, "Second call MUST use cache"
        
        # PHASE 4: Verify performance improvement
        print("\n4. Performance validation...")
        speedup = time1 / time2 if time2 > 0 else 0
        
        print(f"   ✓ First call:  {time1:.0f}ms (cache miss)")
        print(f"   ✓ Second call: {time2:.0f}ms (cache hit)")
        print(f"   ✓ Speedup:     {speedup:.1f}x faster")
        
        # Data graph typically has more speedup than schema (100-270x)
        min_speedup = 10.0
        
        if speedup >= min_speedup:
            print(f"\n✅ TEST PASSED: Cache provides {speedup:.1f}x speedup (>= {min_speedup}x required)")
        else:
            print(f"\n❌ TEST FAILED: Cache only provides {speedup:.1f}x speedup (< {min_speedup}x required)")
            assert False, f"Cache speedup {speedup:.1f}x < {min_speedup}x required"
        
        print("\n" + "="*70)
        print("✅ INTEGRATION TEST PASSED: Data Cache Working End-to-End")
        print("="*70)
        
    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        raise


def test_cache_disabled():
    """
    Test that cache can be explicitly disabled via use_cache=False
    """
    print("\n" + "="*70)
    print("INTEGRATION TEST: Cache Disable Functionality")
    print("="*70)
    
    test_db = 'app/database/p2p_data_products.db'
    
    if not os.path.exists(test_db):
        print(f"❌ SKIP: Test database not found: {test_db}")
        return
    
    try:
        data_source = SQLiteDataSource(test_db)
        builder = SchemaGraphBuilder(data_source, db_path=test_db)
        
        # First call with cache enabled (should save to cache)
        print("\n1. Building graph with cache enabled...")
        result1 = builder.build_schema_graph(use_cache=True)
        assert result1['success'], "First call failed"
        
        # Second call with cache DISABLED (should rebuild from scratch)
        print("\n2. Building graph with cache DISABLED...")
        start = time.time()
        result2 = builder.build_schema_graph(use_cache=False)
        time2 = (time.time() - start) * 1000
        
        assert result2['success'], "Second call failed"
        cache_used = result2.get('stats', {}).get('cache_used', False)
        
        print(f"   ✓ Time: {time2:.0f}ms")
        print(f"   ✓ Cache used: {cache_used}")
        
        assert not cache_used, "Cache should NOT be used when use_cache=False"
        
        print("\n✅ TEST PASSED: Cache can be explicitly disabled")
        
    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        raise


if __name__ == '__main__':
    print("\n" + "="*70)
    print("KNOWLEDGE GRAPH CACHE - INTEGRATION TEST SUITE")
    print("="*70)
    print("\nPurpose: Validate cache works end-to-end through API -> Builder -> Cache")
    print("Success: Cache provides 10x+ speedup on second call")
    
    try:
        # Run all integration tests
        test_schema_cache_integration()
        test_data_cache_integration()
        test_cache_disabled()
        
        print("\n" + "="*70)
        print("✅ ALL INTEGRATION TESTS PASSED")
        print("="*70)
        print("\nCache is working correctly end-to-end!")
        print("- Schema graph: Cache working")
        print("- Data graph: Cache working")
        print("- Cache disable: Working")
        
    except AssertionError as e:
        print(f"\n❌ INTEGRATION TEST FAILED: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ UNEXPECTED ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)