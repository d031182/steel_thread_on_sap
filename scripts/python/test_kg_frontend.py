
#!/usr/bin/env python3
"""
Knowledge Graph Frontend Integration Test

Tests the frontend JavaScript error handling by simulating
API calls and checking for JavaScript errors.

@author P2P Development Team
@version 1.0.0
"""

import requests
import time
import sys

def test_kg_apis():
    """Test Knowledge Graph APIs that frontend uses"""
    
    print("=" * 60)
    print("  KNOWLEDGE GRAPH FRONTEND API TEST")
    print("=" * 60)
    print()
    
    base_url = "http://localhost:5000"
    tests_passed = 0
    tests_failed = 0
    
    # Test 1: Health check
    print("[TEST 1] Server health check...")
    try:
        response = requests.get(f"{base_url}/api/knowledge-graph/health", timeout=5)
        data = response.json()
        if data.get('success'):
            print("[PASS] Server is healthy")
            tests_passed += 1
        else:
            print(f"[FAIL] Server unhealthy - {data}")
            tests_failed += 1
    except Exception as e:
        print(f"[FAIL] {e}")
        tests_failed += 1
    
    print()
    
    # Test 2: Cache refresh (the problematic endpoint)
    print("[TEST 2] Cache refresh endpoint...")
    try:
        response = requests.post(
            f"{base_url}/api/knowledge-graph/cache/refresh",
            json={"source": "sqlite"},
            timeout=10
        )
        data = response.json()
        
        # Validate response structure
        if data.get('success'):
            print(f"[PASS] Cache refreshed - {data.get('message', 'OK')}")
            
            # Check for statistics
            stats = data.get('statistics', {})
            print(f"   - Discovered: {stats.get('discovered', 0)} relationships")
            print(f"   - Time: {stats.get('discovery_time_ms', 0):.0f}ms")
            tests_passed += 1
        else:
            # Test error response structure
            error = data.get('error', {})
            if isinstance(error, dict):
                error_msg = error.get('message', str(error))
            else:
                error_msg = str(error)
            print(f"[FAIL] (expected): {error_msg}")
            tests_failed += 1
            
    except Exception as e:
        print(f"[FAIL] {e}")
        tests_failed += 1
    
    print()
    
    # Test 3: Load knowledge graph
    print("[TEST 3] Load knowledge graph...")
    try:
        response = requests.get(
            f"{base_url}/api/knowledge-graph/",
            params={"source": "sqlite", "mode": "schema"},
            timeout=10
        )
        data = response.json()
        
        # Check for success OR proper error format
        if 'nodes' in data and 'edges' in data:
            node_count = len(data['nodes'])
            edge_count = len(data['edges'])
            print(f"[PASS] Graph loaded - {node_count} nodes, {edge_count} edges")
            tests_passed += 1
        elif data.get('success') == False:
            error_msg = "Unknown error"
            if 'error' in data:
                if isinstance(data['error'], dict) and 'message' in data['error']:
                    error_msg = data['error']['message']
                elif isinstance(data['error'], str):
                    error_msg = data['error']
            print(f"[FAIL] (expected error): {error_msg}")
            tests_failed += 1
        else:
            print(f"[FAIL] Invalid response structure - {data}")
            tests_failed += 1
            
    except Exception as e:
        print(f"[FAIL] {e}")
        tests_failed += 1
    
    print()
    
    # Test 4: Data mode graph
    print("[TEST 4] Load data mode graph...")
    try:
        response = requests.get(
            f"{base_url}/api/knowledge-graph/",
            params={"source": "sqlite", "mode": "data", "max_records": 10},
            timeout=10
        )
        data = response.json()
        
        if 'nodes' in data and 'edges' in data:
            node_count = len(data['nodes'])
            edge_count = len(data['edges'])
            print(f"[PASS] Data graph loaded - {node_count} nodes, {edge_count} edges")
            tests_passed += 1
        elif data.get('success') == False:
            error_msg = "Unknown error"
            if 'error' in data:
                if isinstance(data['error'], dict) and 'message' in data['error']:
                    error_msg = data['error']['message']
            print(f"[FAIL] (expected error): {error_msg}")
            tests_failed += 1
        else:
            print(f"[FAIL] Invalid response - {data}")
            tests_failed += 1
            
    except Exception as e:
        print(f"[FAIL] {e}")
        tests_failed += 1
    
    print()
    
    # Summary
    print("=" * 60)
    print("  TEST SUMMARY")
    print("=" * 60)
    total_tests = tests_passed + tests_failed
    print(f"Total: {total_tests} tests")
    print(f"[+] Passed: {tests_passed}")
    print(f"[-] Failed: {tests_failed}")
    print(f"Success Rate: {(tests_passed/total_tests*100):.0f}%")
    print()
    
    if tests_failed == 0:
        print("[SUCCESS] ALL TESTS PASSED! Frontend should work correctly.")
        return True
    else:
        print(f"[WARNING] {tests_failed} test(s) failed. Check errors above.")
        return False

if __name__ == "__main__":
    print()
    print("Testing Knowledge Graph Frontend APIs...")
    print("Make sure server is running: python server.py")
    print()
    time.sleep(1)
    
    success = test_kg_apis()
    sys.exit(0 if success else 1)