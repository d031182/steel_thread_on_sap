#!/usr/bin/env python3
"""
Automated API Endpoint Testing
================================
Tests all module API endpoints to catch 404s and route issues BEFORE user testing.

Usage:
    python test_api_endpoints.py
"""

import requests
import sys
import time
from typing import Dict, List, Tuple

# Base URL
BASE_URL = "http://localhost:5000"

def test_endpoint(method: str, path: str, expected_status: int = 200, data: dict = None) -> Tuple[bool, str]:
    """
    Test an API endpoint
    
    Returns:
        (success: bool, message: str)
    """
    url = f"{BASE_URL}{path}"
    
    try:
        if method == "GET":
            response = requests.get(url, timeout=5)
        elif method == "POST":
            response = requests.post(url, json=data or {}, timeout=5)
        else:
            return False, f"Unsupported method: {method}"
        
        if response.status_code == expected_status:
            return True, f"{response.status_code}"
        elif response.status_code == 308:
            # Redirect detected - might need trailing slash
            return False, f"{response.status_code} REDIRECT (needs trailing slash?)"
        else:
            return False, f"{response.status_code} (expected {expected_status})"
            
    except requests.exceptions.ConnectionError:
        return False, "CONNECTION REFUSED (server not running?)"
    except requests.exceptions.Timeout:
        return False, "TIMEOUT"
    except Exception as e:
        return False, f"ERROR: {str(e)}"

def main():
    """Run all endpoint tests"""
    
    print("\n" + "="*70)
    print("AUTOMATED API ENDPOINT TESTING")
    print("="*70)
    print(f"Testing server at: {BASE_URL}")
    print()
    
    # Define tests: (method, path, expected_status, description)
    tests = [
        # Health check
        ("GET", "/api/health", 200, "Health Check"),
        
        # Data Products API
        ("GET", "/api/data-products/?source=sqlite", 200, "Data Products List (SQLite)"),
        ("GET", "/api/data-products/?source=hana", 200, "Data Products List (HANA)"),
        
        # Feature Manager API
        ("GET", "/api/features", 200, "Feature Flags List"),
        
        # SQL Execution API  
        ("GET", "/api/sql/connections", 200, "SQL Connections"),
        
        # Knowledge Graph API
        ("GET", "/api/knowledge-graph/health", 200, "Knowledge Graph Health"),
        
        # API Playground API
        ("GET", "/api/playground/modules", 200, "Playground Modules"),
        
        # Logs API
        ("GET", "/api/logs?limit=10", 200, "Logs List"),
        
        # Modules API
        ("GET", "/api/modules", 200, "Modules List"),
    ]
    
    passed = 0
    failed = 0
    warnings = 0
    
    print(f"{'METHOD':<6} {'STATUS':<25} {'ENDPOINT':<45}")
    print("-" * 76)
    
    for method, path, expected_status, description in tests:
        success, message = test_endpoint(method, path, expected_status)
        
        # Format output
        status_text = f"{message}"
        if success:
            status_icon = "[PASS]"
            passed += 1
        elif "REDIRECT" in message:
            status_icon = "[WARN]"
            warnings += 1
        else:
            status_icon = "[FAIL]"
            failed += 1
        
        print(f"{status_icon} {method:<5} {status_text:<24} {path}")
    
    # Summary
    print("-" * 76)
    print(f"\nRESULTS: {passed} passed, {failed} failed, {warnings} warnings")
    
    if warnings > 0:
        print(f"\n[WARN] Warnings detected:")
        print("  - 308 REDIRECT means endpoint needs trailing slash in URL")
        print("  - Update frontend code to add trailing slash: /api/endpoint/ not /api/endpoint")
    
    if failed > 0:
        print(f"\n[FAIL] Tests FAILED")
        print("  Fix endpoints before deploying!")
        sys.exit(1)
    elif warnings > 0:
        print(f"\n[WARN] Tests PASSED with warnings")
        print("  Review warnings above")
        sys.exit(0)
    else:
        print(f"\n[PASS] All tests PASSED")
        sys.exit(0)

if __name__ == '__main__':
    # Check if server is reachable first
    try:
        response = requests.get(f"{BASE_URL}/api/health", timeout=2)
        print(f"[OK] Server is running\n")
    except:
        print(f"[FAIL] Server is not running at {BASE_URL}")
        print("\nPlease start the server first:")
        print("  python server.py")
        sys.exit(1)
    
    main()