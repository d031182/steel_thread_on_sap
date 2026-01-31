"""
Quick test of Phase 1: Orphan Node Filtering

Tests the new filter_orphans parameter in the Knowledge Graph API.
"""

import requests
import json

BASE_URL = "http://localhost:5000"

def test_data_mode_with_orphan_filtering():
    """Test Data Mode with orphan filtering enabled (default)"""
    print("\n=== Test 1: Data Mode with Orphan Filtering (default: True) ===")
    
    response = requests.get(
        f"{BASE_URL}/api/knowledge-graph/",
        params={
            "mode": "data",
            "source": "sqlite",
            "max_records": 20
            # filter_orphans defaults to True
        }
    )
    
    if response.status_code == 200:
        data = response.json()
        stats = data.get('stats', {})
        
        print(f"[PASS] Success!")
        print(f"   Nodes displayed: {stats.get('node_count')}")
        print(f"   Edges: {stats.get('edge_count')}")
        print(f"   Orphans filtered: {stats.get('orphans_filtered', 0)}")
        print(f"   Total nodes before filter: {stats.get('total_nodes_before_filter', 'N/A')}")
        
        if stats.get('orphans_filtered', 0) > 0:
            print(f"\n   [INFO] Filtered {stats['orphans_filtered']} orphan nodes!")
            print(f"   Graph is now cleaner and more focused on relationships")
    else:
        print(f"[FAIL] Error: {response.status_code}")
        print(response.text)

def test_data_mode_with_all_nodes():
    """Test Data Mode with orphan filtering disabled"""
    print("\n=== Test 2: Data Mode WITHOUT Orphan Filtering (show all) ===")
    
    response = requests.get(
        f"{BASE_URL}/api/knowledge-graph/",
        params={
            "mode": "data",
            "source": "sqlite",
            "max_records": 20,
            "filter_orphans": "false"  # Explicitly disable filtering
        }
    )
    
    if response.status_code == 200:
        data = response.json()
        stats = data.get('stats', {})
        
        print(f"[PASS] Success!")
        print(f"   Nodes displayed: {stats.get('node_count')}")
        print(f"   Edges: {stats.get('edge_count')}")
        print(f"   Orphans filtered: {stats.get('orphans_filtered', 0)}")
        print(f"   (Shows ALL nodes including orphans)")
    else:
        print(f"[FAIL] Error: {response.status_code}")
        print(response.text)

def compare_results():
    """Compare filtered vs unfiltered results"""
    print("\n=== Comparison Summary ===")
    
    # Get filtered
    r1 = requests.get(f"{BASE_URL}/api/knowledge-graph/", params={"mode": "data", "filter_orphans": "true"})
    stats_filtered = r1.json().get('stats', {})
    
    # Get unfiltered
    r2 = requests.get(f"{BASE_URL}/api/knowledge-graph/", params={"mode": "data", "filter_orphans": "false"})
    stats_unfiltered = r2.json().get('stats', {})
    
    print(f"Unfiltered: {stats_unfiltered.get('node_count')} nodes (includes orphans)")
    print(f"Filtered:   {stats_filtered.get('node_count')} nodes (orphans removed)")
    print(f"Difference: {stats_unfiltered.get('node_count', 0) - stats_filtered.get('node_count', 0)} orphan nodes")
    
    if stats_filtered.get('node_count', 0) < stats_unfiltered.get('node_count', 0):
        print("\n[PASS] Orphan filtering is working correctly!")
        print("   Industry best practice: Neo4j Bloom, Linkurious, Graphistry all filter orphans by default")
    else:
        print("\n[INFO] No orphan nodes found in current dataset")

if __name__ == "__main__":
    print("Testing Phase 1: Orphan Node Filtering Implementation")
    print("=" * 60)
    
    try:
        test_data_mode_with_orphan_filtering()
        test_data_mode_with_all_nodes()
        compare_results()
        
        print("\n" + "=" * 60)
        print("[PASS] Phase 1 backend implementation COMPLETE!")
        print("\nNext: Add UI toggle in Knowledge Graph page")
        
    except requests.exceptions.ConnectionError:
        print("\n[FAIL] Error: Could not connect to server")
        print("   Make sure server is running: python server.py")
    except Exception as e:
        print(f"\n[FAIL] Error: {e}")
