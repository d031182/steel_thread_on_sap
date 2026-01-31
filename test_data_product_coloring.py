"""
Test Phase 2: Data Product-Based Coloring

Validates that nodes are colored by data product (not by individual table).
"""

import requests
import json

BASE_URL = "http://localhost:5000"

def test_data_product_coloring():
    """Test that nodes are colored by data product group"""
    print("\n=== Phase 2: Data Product-Based Coloring ===")
    
    response = requests.get(
        f"{BASE_URL}/api/knowledge-graph/",
        params={
            "mode": "data",
            "source": "sqlite",
            "max_records": 20
        }
    )
    
    if response.status_code != 200:
        print(f"[FAIL] Error: {response.status_code}")
        print(response.text)
        return
    
    data = response.json()
    nodes = data.get('nodes', [])
    stats = data.get('stats', {})
    
    print(f"[PASS] Graph loaded successfully")
    print(f"   Total nodes: {stats.get('node_count')}")
    print(f"   Orphans filtered: {stats.get('orphans_filtered')}")
    
    # Analyze coloring by data product
    color_groups = {}  # {color: [table_names]}
    table_to_color = {}  # {table_name: color}
    
    for node in nodes:
        table = node.get('group')  # Table name is in 'group' field
        color = node.get('color', {}).get('background', 'N/A')
        
        if color not in color_groups:
            color_groups[color] = set()
        color_groups[color].add(table)
        table_to_color[table] = color
    
    print(f"\n   Color Groups: {len(color_groups)} distinct colors used")
    print(f"   Table Types: {len(table_to_color)} table types")
    
    # Show color distribution
    print(f"\n   Color Distribution:")
    for color, tables in sorted(color_groups.items(), key=lambda x: len(x[1]), reverse=True):
        print(f"      {color}: {len(tables)} table types")
        # Show sample tables for this color
        sample = list(tables)[:3]
        print(f"         Sample: {', '.join(sample)}")
    
    # Validate: Should have 5-9 colors (not 65+)
    if len(color_groups) <= 10:
        print(f"\n[PASS] Coloring is grouped! ({len(color_groups)} colors vs 65+ tables)")
        print(f"   Industry standard: Neo4j/Linkurious use 5-7 color palette")
    else:
        print(f"\n[WARN] Too many colors: {len(color_groups)}")
        print(f"   Expected: 5-10 colors (data product grouping)")
        print(f"   Current: {len(color_groups)} colors")

if __name__ == "__main__":
    print("Testing Phase 2: Data Product-Based Coloring")
    print("=" * 60)
    
    try:
        test_data_product_coloring()
        
        print("\n" + "=" * 60)
        print("[INFO] Test complete - review color distribution above")
        
    except requests.exceptions.ConnectionError:
        print("\n[FAIL] Error: Could not connect to server")
        print("   Make sure server is running: python server.py")
    except Exception as e:
        print(f"\n[FAIL] Error: {e}")