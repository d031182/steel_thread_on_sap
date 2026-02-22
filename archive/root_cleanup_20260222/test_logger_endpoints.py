#!/usr/bin/env python3
"""
Quick test script to verify logger API endpoints are accessible
"""
import requests
import json

BASE_URL = "http://localhost:5000"

def test_endpoint(method, path, data=None):
    """Test an endpoint and print result"""
    url = f"{BASE_URL}{path}"
    print(f"\n{'='*60}")
    print(f"{method} {path}")
    print(f"{'='*60}")
    
    try:
        if method == "GET":
            response = requests.get(url, timeout=5)
        elif method == "POST":
            response = requests.post(url, json=data, timeout=5)
        else:
            print(f"❌ Unsupported method: {method}")
            return
        
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        
        if response.status_code == 200:
            print("✅ SUCCESS")
        else:
            print(f"⚠️  Non-200 status: {response.status_code}")
            
    except requests.exceptions.ConnectionError:
        print("❌ ERROR: Server not running at http://localhost:5000")
        print("   Please start the server first: python server.py")
    except Exception as e:
        print(f"❌ ERROR: {e}")

if __name__ == "__main__":
    print("Testing Logger Module API Endpoints")
    print("="*60)
    
    # Test 1: Health check
    test_endpoint("GET", "/api/logger/health")
    
    # Test 2: Get logging mode
    test_endpoint("GET", "/api/logger/mode")
    
    # Test 3: Set logging mode
    test_endpoint("POST", "/api/logger/mode", {"mode": "flight_recorder"})
    
    # Test 4: Get logs
    test_endpoint("GET", "/api/logger/logs")
    
    # Test 5: Submit client log
    test_endpoint("POST", "/api/logger/client", {
        "level": "INFO",
        "category": "API",
        "message": "Test log from endpoint test script"
    })
    
    print("\n" + "="*60)
    print("All tests completed!")
    print("="*60)