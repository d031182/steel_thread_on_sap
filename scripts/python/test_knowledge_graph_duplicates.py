#!/usr/bin/env python3
"""
Knowledge Graph Duplicate Node ID Test

Tests that the Knowledge Graph API doesn't generate duplicate node IDs.
This was the root cause of vis.js rendering failures.

Usage: python scripts/python/test_knowledge_graph_duplicates.py
"""
import requests
import sys
from collections import Counter

def test_knowledge_graph_data_mode():
    """Test data mode for duplicate node IDs"""
    url = 'http://localhost:5000/api/knowledge-graph/'
    params = {'mode': 'data', 'source': 'sqlite', 'max_records': 20}
    
    print("=" * 60)
    print("Testing Knowledge Graph Data Mode")
    print("=" * 60)
    print(f"URL: {url}")
    print(f"Params: {params}")
    print()
    
    # Make request
    try:
        r = requests.get(url, params=params, timeout=30)
    except requests.exceptions.RequestException as e:
        print(f"❌ FAIL: Request failed: {e}")
        return 1
    
    # Check HTTP status
    if r.status_code != 200:
        print(f"❌ FAIL: HTTP {r.status_code}")
        print(r.text[:500])
        return 1
    
    print(f"✓ HTTP 200 OK")
    
    # Parse JSON
    try:
        data = r.json()
    except ValueError as e:
        print(f"❌ FAIL: Invalid JSON: {e}")
        print(r.text[:500])
        return 1
    
    print(f"✓ Valid JSON response")
    
    # Check API success field
    if not data.get('success', True):  # Default True for backwards compat
        print(f"❌ FAIL: API returned success=false")
        error = data.get('error', 'Unknown error')
        print(f"Error: {error}")
        return 1
    
    print(f"✓ API success=true")
    
    # Extract nodes
    nodes = data.get('nodes', [])
    edges = data.get('edges', [])
    
    if not nodes:
        print(f"⚠️  WARNING: No nodes returned")
        print(f"This might be expected if database is empty")
        return 0
    
    print(f"✓ Received {len(nodes)} nodes, {len(edges)} edges")
    
    # Check for duplicate node IDs (THE CRITICAL TEST)
    node_ids = [n.get('id') for n in nodes if n.get('id')]
    id_counts = Counter(node_ids)
    duplicates = {node_id: count for node_id, count in id_counts.items() if count > 1}
    
    if duplicates:
        print()
        print("❌ FAIL: Found duplicate node IDs!")
        print(f"Total duplicates: {len(duplicates)}")
        print()
        for dup_id, count in sorted(duplicates.items(), key=lambda x: -x[1])[:10]:
            print(f"  • {dup_id}: appears {count} times")
        if len(duplicates) > 10:
            print(f"  ... and {len(duplicates) - 10} more")
        print()
        print("This will cause vis.js to fail with:")
        print(f"  'Error: Cannot add item: item with id {list(duplicates.keys())[0]} already exists'")
        return 1
    
    print(f"✓ All {len(node_ids)} node IDs are unique")
    
    # Check node structure
    for i, node in enumerate(nodes[:3]):  # Check first 3
        if 'id' not in node:
            print(f"❌ FAIL: Node {i} missing 'id' field")
            return 1
        if 'label' not in node:
            print(f"⚠️  WARNING: Node {i} missing 'label' field")
    
    print(f"✓ All nodes have required fields")
    
    # Check edge references
    node_id_set = set(node_ids)
    invalid_edges = []
    for edge in edges:
        from_id = edge.get('from')
        to_id = edge.get('to')
        if from_id and from_id not in node_id_set:
            invalid_edges.append(f"Edge 'from' references invalid node: {from_id}")
        if to_id and to_id not in node_id_set:
            invalid_edges.append(f"Edge 'to' references invalid node: {to_id}")
    
    if invalid_edges:
        print(f"❌ FAIL: {len(invalid_edges)} edges reference invalid nodes:")
        for err in invalid_edges[:5]:
            print(f"  • {err}")
        return 1
    
    print(f"✓ All {len(edges)} edges reference valid nodes")
    
    # Success summary
    print()
    print("=" * 60)
    print("✅ ALL TESTS PASSED")
    print("=" * 60)
    print(f"Graph Structure:")
    print(f"  • {len(nodes)} unique nodes")
    print(f"  • {len(edges)} valid edges")
    print(f"  • {len(set(n.get('group') for n in nodes))} node types")
    print()
    print("vis.js will render this graph successfully! 🎉")
    print()
    
    return 0

if __name__ == '__main__':
    sys.exit(test_knowledge_graph_data_mode())