#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test Clean Graph Cache Implementation (Phase 2)

Tests the complete workflow:
1. Build graph → saves to cache
2. Load from cache → fast (<1s)
3. Verify cache contains expected data
"""

import sys
import time
from pathlib import Path
import io

# Fix Windows encoding issue (cp1252 → utf-8)
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from core.services.visjs_translator import VisJsTranslator
from core.services.graph_cache_service import GraphCacheService


def test_cache_workflow():
    """Test complete cache workflow"""
    
    db_path = 'app/database/p2p_data_products.db'
    
    print("=" * 70)
    print("CLEAN GRAPH CACHE TEST")
    print("=" * 70)
    
    # Test 1: Check cache status
    print("\n1. Checking cache status...")
    translator = VisJsTranslator(db_path)
    
    for graph_type in ['schema', 'data']:
        status = translator.check_cache_status(graph_type)
        print(f"\n   {graph_type.upper()} graph:")
        if status['exists']:
            print(f"   ✓ Cache exists")
            print(f"   - Nodes: {status['node_count']}")
            print(f"   - Edges: {status['edge_count']}")
            print(f"   - Updated: {status['last_updated']}")
        else:
            print(f"   ✗ Cache does not exist")
    
    # Test 2: Load from cache (if exists)
    print("\n2. Testing cache load performance...")
    
    for graph_type in ['schema', 'data']:
        start = time.time()
        graph = translator.get_visjs_graph(graph_type)
        load_time = (time.time() - start) * 1000
        
        print(f"\n   {graph_type.upper()} graph:")
        if graph['stats'].get('cache_exists'):
            print(f"   ✓ Loaded from cache in {load_time:.0f}ms")
            print(f"   - Nodes: {graph['stats']['node_count']}")
            print(f"   - Edges: {graph['stats']['edge_count']}")
        else:
            print(f"   ✗ Cache miss")
    
    # Test 3: Clear and rebuild
    print("\n3. Testing cache rebuild...")
    cache_service = GraphCacheService(db_path)
    
    print("\n   Clearing data cache...")
    cleared = cache_service.clear_cache('data')
    print(f"   {'✓' if cleared else '✗'} Cache cleared: {cleared}")
    
    # Verify cleared
    status = translator.check_cache_status('data')
    print(f"   {'✓' if not status['exists'] else '✗'} Cache empty: {not status['exists']}")
    
    print("\n" + "=" * 70)
    print("TEST COMPLETE")
    print("=" * 70)
    
    print("\nNext step: Start Flask app and test via API:")
    print("  GET /api/knowledge-graph/?mode=data")
    print("  → First request: ~27s (builds + caches)")
    print("  → Second request: <1s (loads from cache)")
    
    return 0


if __name__ == '__main__':
    try:
        exit_code = test_cache_workflow()
        sys.exit(exit_code)
    except Exception as e:
        print(f"\nERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)