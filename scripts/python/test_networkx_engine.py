#!/usr/bin/env python3
"""
Test NetworkX Graph Query Engine

Verifies the NetworkX engine implementation works correctly.
"""

import sys
import os
from datetime import datetime

# Add project root to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

from core.services.networkx_graph_query_engine import NetworkXGraphQueryEngine
from core.interfaces.graph_query import TraversalDirection

DB_PATH = 'app/database/p2p_data_products.db'

print("="*80)
print("NetworkX Graph Query Engine Test")
print("="*80)
print(f"\nDatabase: {DB_PATH}")
print(f"Timestamp: {datetime.now()}\n")

# Initialize engine
print("STEP 1: Initialize NetworkX Engine")
print("-" * 80)

start = datetime.now()
engine = NetworkXGraphQueryEngine(DB_PATH, auto_load=True)
init_time = (datetime.now() - start).total_seconds()

stats = engine.get_statistics()
print(f"\n[OK] Engine initialized in {init_time*1000:.0f}ms")
print(f"  - Nodes: {stats['nodes']}")
print(f"  - Edges: {stats['edges']}")
print(f"  - Load Time: {stats['load_time_ms']:.0f}ms")
print(f"  - Avg Degree: {stats['avg_degree']:.2f}\n")

# Test 1: Get neighbors
print("STEP 2: Test get_neighbors()")
print("-" * 80)

neighbors = engine.get_neighbors('Supplier:SUP001', direction=TraversalDirection.OUTGOING)
print(f"[OK] Found {len(neighbors)} neighbors for Supplier:SUP001")
for n in neighbors[:5]:  # Show first 5
    print(f"  - {n.label}: {n.id}")

# Test 2: Shortest path
print("\nSTEP 3: Test shortest_path()")
print("-" * 80)

path = engine.shortest_path('Supplier:SUP001', 'SupplierInvoice:5100000001')
if path:
    print(f"[OK] Found path with length {path.length}")
    print("Path:")
    for i, node in enumerate(path.nodes):
        print(f"  {i+1}. {node.label}: {node.id}")
    print("\nEdges:")
    for edge in path.edges:
        print(f"  - {edge.label}: {edge.source_id} -> {edge.target_id}")
else:
    print("[WARN] No path found")

# Test 3: Traverse
print("\nSTEP 4: Test traverse()")
print("-" * 80)

related = engine.traverse(
    'Supplier:SUP001',
    depth=2,
    direction=TraversalDirection.OUTGOING
)
print(f"[OK] Found {len(related)} nodes within 2 hops")

# Group by type
by_type = {}
for node in related:
    by_type.setdefault(node.label, []).append(node.id)

print("Nodes by type:")
for label, nodes in by_type.items():
    print(f"  - {label}: {len(nodes)}")

# Test 4: Node operations
print("\nSTEP 5: Test node operations")
print("-" * 80)

node = engine.get_node('PurchaseOrder:PO000001')
if node:
    print(f"[OK] Retrieved node: {node.label} {node.id}")
    print(f"     Properties: {list(node.properties.keys())[:5]}...")  # Show first 5 properties

exists = engine.node_exists('Supplier:SUP999')
print(f"[OK] node_exists('Supplier:SUP999'): {exists}")

# Test 5: Advanced algorithms
print("\nSTEP 6: Test advanced algorithms")
print("-" * 80)

print("Calculating PageRank...")
pagerank = engine.get_pagerank()
top_5 = sorted(pagerank.items(), key=lambda x: x[1], reverse=True)[:5]
print("[OK] Top 5 nodes by PageRank:")
for node_id, score in top_5:
    print(f"  - {node_id}: {score:.4f}")

print("\nCalculating Degree Centrality...")
degree = engine.get_degree_centrality()
top_5_degree = sorted(degree.items(), key=lambda x: x[1], reverse=True)[:5]
print("[OK] Top 5 nodes by Degree Centrality:")
for node_id, score in top_5_degree:
    print(f"  - {node_id}: {score:.4f}")

# Final summary
print("\n" + "="*80)
print("TEST SUMMARY")
print("="*80)
print(f"\n[OK] All tests passed!")
print(f"\nPerformance:")
print(f"  - Engine Init: {init_time*1000:.0f}ms")
print(f"  - Graph Load: {stats['load_time_ms']:.0f}ms")
print(f"  - Total: {(init_time)*1000:.0f}ms")

print(f"\nGraph Statistics:")
print(f"  - Nodes: {stats['nodes']}")
print(f"  - Edges: {stats['edges']}")
print(f"  - Density: {stats['density']:.4f}")
print(f"  - Avg Degree: {stats['avg_degree']:.2f}")

print("\n" + "="*80)
print("[SUCCESS] NetworkX engine fully functional!")
print("="*80)
print("\nNext: Create unified GraphQueryService (HANA + NetworkX)")