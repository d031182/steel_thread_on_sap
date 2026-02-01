#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test Clean Graph Cache via Flask API

Tests the complete end-to-end workflow:
1. First request: Build graph + save to cache (~27s)
2. Second request: Load from cache (<1s)
3. Verify performance improvement
"""

import sys
import io
import time
import requests

# Fix Windows encoding issue (cp1252 → utf-8)
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')


def test_api_cache():
    """Test graph cache via API"""
    
    base_url = 'http://localhost:5000'
    
    print("=" * 70)
    print("API CACHE TEST")
    print("=" * 70)
    
    # Test 1: First request (build + cache)
    print("\n1. First request (should build + cache)...")
    print("   URL: GET /api/knowledge-graph/?mode=data&use_cache=false")
    
    start = time.time()
    try:
        response = requests.get(f'{base_url}/api/knowledge-graph/', params={
            'mode': 'data',
            'use_cache': 'false'  # Force build
        }, timeout=60)
        
        build_time = (time.time() - start) * 1000
        
        if response.status_code == 200:
            data = response.json()
            print(f"   ✓ Success ({build_time:.0f}ms)")
            print(f"   - Nodes: {data.get('stats', {}).get('node_count', 0)}")
            print(f"   - Edges: {data.get('stats', {}).get('edge_count', 0)}")
            
            if build_time < 5000:  # Should be ~27s, if <5s something's wrong
                print(f"   ⚠️  Warning: Build suspiciously fast ({build_time:.0f}ms)")
        else:
            print(f"   ✗ Failed: {response.status_code}")
            print(f"   Response: {response.text[:200]}")
            return 1
            
    except requests.exceptions.ConnectionError:
        print("   ✗ Connection failed - is Flask running?")
        print("\n   Start server first: python server.py")
        return 1
    except Exception as e:
        print(f"   ✗ Error: {e}")
        return 1
    
    # Test 2: Second request (should use cache)
    print("\n2. Second request (should load from cache)...")
    print("   URL: GET /api/knowledge-graph/?mode=data&use_cache=true")
    
    start = time.time()
    try:
        response = requests.get(f'{base_url}/api/knowledge-graph/', params={
            'mode': 'data',
            'use_cache': 'true'
        }, timeout=10)
        
        cache_time = (time.time() - start) * 1000
        
        if response.status_code == 200:
            data = response.json()
            print(f"   ✓ Success ({cache_time:.0f}ms)")
            print(f"   - Nodes: {data.get('stats', {}).get('node_count', 0)}")
            print(f"   - Edges: {data.get('stats', {}).get('edge_count', 0)}")
            
            # Verify it's actually using cache
            if cache_time > 5000:
                print(f"   ⚠️  Warning: Cache load slow ({cache_time:.0f}ms) - may not be cached")
            else:
                speedup = build_time / cache_time if cache_time > 0 else 0
                print(f"\n   🚀 Speedup: {speedup:.1f}x faster!")
        else:
            print(f"   ✗ Failed: {response.status_code}")
            return 1
            
    except Exception as e:
        print(f"   ✗ Error: {e}")
        return 1
    
    print("\n" + "=" * 70)
    print("TEST COMPLETE")
    print("=" * 70)
    
    print(f"\nPerformance:")
    print(f"  First request (build):  {build_time:.0f}ms")
    print(f"  Second request (cache): {cache_time:.0f}ms")
    print(f"  Improvement: {speedup:.1f}x faster")
    
    if speedup > 10:
        print("\n✓ Cache working perfectly!")
        return 0
    else:
        print(f"\n⚠️  Cache may not be working (expected >10x speedup)")
        return 1


if __name__ == '__main__':
    try:
        exit_code = test_api_cache()
        sys.exit(exit_code)
    except Exception as e:
        print(f"\nERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)