"""
Test new Knowledge Graph query endpoints (v3.15 Phase 1)

Tests the fast GraphQueryService integration:
- /query/neighbors
- /query/path
- /query/traverse

Run: python scripts/python/test_kg_query_endpoints.py
"""

import requests
import json

BASE_URL = "http://localhost:5001/api/knowledge-graph"

def test_query_neighbors():
    """Test /query/neighbors endpoint"""
    print("\n=== Testing /query/neighbors ===")
    
    payload = {
        "source": "sqlite",
        "node_id": "Supplier",
        "direction": "outgoing",
        "limit": 5
    }
    
    try:
        response = requests.post(f"{BASE_URL}/query/neighbors", json=payload)
        result = response.json()
        
        print(f"Status: {response.status_code}")
        print(f"Success: {result.get('success')}")
        print(f"Backend: {result.get('backend', {}).get('backend')}")
        print(f"Neighbors found: {result.get('count')}")
        
        if result.get('success'):
            print("✓ /query/neighbors working!")
            return True
        else:
            print(f"✗ Error: {result.get('error')}")
            return False
            
    except Exception as e:
        print(f"✗ Exception: {e}")
        return False


def test_query_path():
    """Test /query/path endpoint"""
    print("\n=== Testing /query/path ===")
    
    payload = {
        "source": "sqlite",
        "start_id": "Supplier",
        "end_id": "PurchaseOrder",
        "max_hops": 10
    }
    
    try:
        response = requests.post(f"{BASE_URL}/query/path", json=payload)
        result = response.json()
        
        print(f"Status: {response.status_code}")
        print(f"Success: {result.get('success')}")
        
        if result.get('success'):
            path = result.get('path', {})
            print(f"Backend: {result.get('backend', {}).get('backend')}")
            print(f"Path length: {path.get('length')} hops")
            print(f"Nodes in path: {len(path.get('nodes', []))}")
            print("✓ /query/path working!")
            return True
        elif result.get('error', {}).get('code') == 'NO_PATH':
            print("No path exists (expected for empty DB)")
            print("✓ /query/path working (no path is valid response)!")
            return True
        else:
            print(f"✗ Error: {result.get('error')}")
            return False
            
    except Exception as e:
        print(f"✗ Exception: {e}")
        return False


def test_query_traverse():
    """Test /query/traverse endpoint"""
    print("\n=== Testing /query/traverse ===")
    
    payload = {
        "source": "sqlite",
        "start_id": "Supplier",
        "depth": 2,
        "direction": "outgoing"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/query/traverse", json=payload)
        result = response.json()
        
        print(f"Status: {response.status_code}")
        print(f"Success: {result.get('success')}")
        print(f"Backend: {result.get('backend', {}).get('backend')}")
        print(f"Nodes reached: {result.get('count')}")
        
        if result.get('success'):
            print("✓ /query/traverse working!")
            return True
        else:
            print(f"✗ Error: {result.get('error')}")
            return False
            
    except Exception as e:
        print(f"✗ Exception: {e}")
        return False


def main():
    """Run all tests"""
    print("="*60)
    print("Knowledge Graph Query Endpoints Test (v3.15 Phase 1)")
    print("="*60)
    
    print("\nMake sure server is running: python server.py")
    input("Press Enter to start tests...")
    
    results = []
    results.append(("query_neighbors", test_query_neighbors()))
    results.append(("query_path", test_query_path()))
    results.append(("query_traverse", test_query_traverse()))
    
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    
    for name, passed in results:
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"{status}: {name}")
    
    all_passed = all(r[1] for r in results)
    
    if all_passed:
        print("\n🎉 All tests passed! v3.15 Phase 1 ready to commit!")
    else:
        print("\n❌ Some tests failed. Check server logs.")
    
    return all_passed


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)