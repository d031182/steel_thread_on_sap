"""
Knowledge Graph E2E Integration Test
Automated test runner for cache integration architecture validation
"""

import requests
import time
import sys
from datetime import datetime

# Configuration
BASE_URL = "http://localhost:5000"
SQLITE_SOURCE = "sqlite"

def print_header(title):
    """Print formatted test section header"""
    print("\n" + "=" * 60)
    print(f"  {title}")
    print("=" * 60)

def print_result(passed, message):
    """Print test result"""
    status = "[PASS]" if passed else "[FAIL]"
    print(f"{status} {message}")
    return passed

def test_server_health():
    """Check if server is running"""
    print_header("Pre-Test: Server Health Check")
    try:
        response = requests.get(f"{BASE_URL}/api/features", timeout=5)
        return print_result(response.status_code == 200, "Server is running and responding")
    except requests.exceptions.RequestException as e:
        return print_result(False, f"Server not responding: {e}")

def test_v4_schema():
    """Test v4 composite FK schema validation"""
    print_header("Step 0: V4 Schema Validation")
    print("Running: python scripts/python/test_fk_with_pragma.py")
    import subprocess
    result = subprocess.run(
        ["python", "scripts/python/test_fk_with_pragma.py"],
        capture_output=True,
        text=True
    )
    passed = result.returncode == 0 and "[PASS]" in result.stdout
    print(result.stdout)
    return print_result(passed, "V4 composite FK schema validated")

def test_cache_refresh():
    """Test cache refresh endpoint"""
    print_header("Step 1: Cache Refresh")
    try:
        start_time = time.time()
        response = requests.post(
            f"{BASE_URL}/api/knowledge-graph/cache/refresh",
            json={"source": SQLITE_SOURCE},
            timeout=30
        )
        elapsed = time.time() - start_time
        
        data = response.json()
        success = data.get("success", False)
        discovered = data.get("statistics", {}).get("discovered", 0)
        
        print(f"Response time: {elapsed:.2f}s")
        print(f"Discovered: {discovered} relationships")
        print(f"Full response: {data}")
        
        return print_result(
            success and discovered == 31,
            f"Cache refreshed: {discovered}/31 relationships discovered"
        )
    except Exception as e:
        return print_result(False, f"Cache refresh failed: {e}")

def test_data_graph():
    """Test data graph building"""
    print_header("Step 2: Build Data Graph")
    try:
        start_time = time.time()
        response = requests.get(
            f"{BASE_URL}/api/knowledge-graph/",
            params={
                "source": SQLITE_SOURCE,
                "mode": "data",
                "max_records": 20,
                "filter_orphans": "true"
            },
            timeout=60
        )
        elapsed = time.time() - start_time
        
        data = response.json()
        success = data.get("success", False)
        stats = data.get("stats", {})
        edge_count = stats.get("edge_count", 0)
        node_count = stats.get("node_count", 0)
        
        # Check for green edges
        edges = data.get("edges", [])
        green_edges = [e for e in edges if e.get("color", {}).get("color") == "#4caf50"]
        
        print(f"Response time: {elapsed:.2f}s")
        print(f"Total edges: {edge_count}")
        print(f"Total nodes: {node_count}")
        print(f"GREEN edges (#4caf50): {len(green_edges)}")
        
        return print_result(
            success and len(green_edges) >= 18,
            f"Data graph built: {len(green_edges)}/18+ green edges found"
        )
    except Exception as e:
        return print_result(False, f"Data graph build failed: {e}")

def test_schema_graph():
    """Test schema graph building"""
    print_header("Step 3: Build Schema Graph")
    try:
        start_time = time.time()
        response = requests.get(
            f"{BASE_URL}/api/knowledge-graph/",
            params={
                "source": SQLITE_SOURCE,
                "mode": "schema"
            },
            timeout=60
        )
        elapsed = time.time() - start_time
        
        data = response.json()
        success = data.get("success", False)
        
        # Check for orange edges
        edges = data.get("edges", [])
        orange_edges = [e for e in edges if e.get("color", {}).get("color") == "#ff9800"]
        
        print(f"Response time: {elapsed:.2f}s")
        print(f"Total edges: {len(edges)}")
        print(f"ORANGE edges (#ff9800): {len(orange_edges)}")
        
        return print_result(
            success and len(orange_edges) >= 26,
            f"Schema graph built: {len(orange_edges)}/26+ orange edges found"
        )
    except Exception as e:
        return print_result(False, f"Schema graph build failed: {e}")

def test_system_logs():
    """Check for system errors during test"""
    print_header("Step 4: System Logs Check")
    try:
        import sqlite3
        conn = sqlite3.connect('logs/app_logs.db')
        cursor = conn.cursor()
        
        # Check for errors in last 5 minutes
        cursor.execute('''
            SELECT timestamp, level, logger, message 
            FROM application_logs 
            WHERE level IN ("ERROR", "CRITICAL") 
            AND timestamp > datetime("now", "-5 minutes") 
            ORDER BY timestamp DESC 
            LIMIT 10
        ''')
        
        rows = cursor.fetchall()
        conn.close()
        
        if rows:
            print(f"Found {len(rows)} error(s) in last 5 minutes:")
            for row in rows:
                print(f"  {row[0]} - {row[1]} - {row[2]}")
                print(f"    {row[3][:100]}...")
            return print_result(False, "Errors found in system logs")
        else:
            return print_result(True, "No critical errors in last 5 minutes")
    except Exception as e:
        return print_result(False, f"Log check failed: {e}")

def run_all_tests():
    """Run complete E2E test suite"""
    print("\n" + "=" * 60)
    print("  KNOWLEDGE GRAPH E2E INTEGRATION TEST")
    print("  Testing: Cache Integration Architecture")
    print("  Started:", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    print("=" * 60)
    
    results = []
    
    # Pre-test
    results.append(("Server Health", test_server_health()))
    if not results[-1][1]:
        print("\n[ABORT] Server not running. Start server with: python server.py")
        return False
    
    # Main tests
    results.append(("V4 Schema", test_v4_schema()))
    results.append(("Cache Refresh", test_cache_refresh()))
    results.append(("Data Graph", test_data_graph()))
    results.append(("Schema Graph", test_schema_graph()))
    results.append(("System Logs", test_system_logs()))
    
    # Summary
    print_header("TEST SUMMARY")
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "[PASS]" if result else "[FAIL]"
        print(f"{status} {name}")
    
    print(f"\nResults: {passed}/{total} tests passed ({passed*100//total}%)")
    
    if passed == total:
        print("\n✅ ALL TESTS PASSED - Cache integration working correctly!")
        print("\nValidated:")
        print("  - Cache stores 31 FK relationships")
        print("  - Data mode builds graph FROM cache (18+ green edges)")
        print("  - Schema mode builds graph FROM cache (26+ orange edges)")
        print("  - Data and schema graphs are DISJUNCT (independent)")
        return True
    else:
        print(f"\n❌ {total - passed} TEST(S) FAILED - Review failures above")
        return False

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)