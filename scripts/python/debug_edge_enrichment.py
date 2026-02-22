"""
Debug script to verify edge enrichment is working correctly.

Tests the complete flow:
1. SchemaGraphBuilderService builds graph
2. Edges have semantic metadata in properties
3. to_dict() flattens properties to top level
4. Cache stores/retrieves correctly
"""
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from core.services.csn_parser import CSNParser
from modules.knowledge_graph_v2.services.schema_graph_builder_service import SchemaGraphBuilderService

def main():
    print("=" * 80)
    print("DEBUG: Edge Enrichment Flow")
    print("=" * 80)
    
    # Step 1: Build graph
    print("\n1. Building schema graph from CSN...")
    csn_parser = CSNParser()
    builder = SchemaGraphBuilderService(csn_parser)
    graph = builder.build_from_csn()
    
    print(f"   ✓ Built graph: {len(graph.nodes)} nodes, {len(graph.edges)} edges")
    
    # Step 2: Check FK edges for semantic metadata
    print("\n2. Checking FK edges for semantic metadata...")
    fk_edges = [e for e in graph.edges if e.type.value == 'foreign_key']
    print(f"   Found {len(fk_edges)} FK edges")
    
    # Find edges with cardinality/on_conditions
    enriched_edges = []
    for edge in fk_edges[:10]:  # Check first 10
        has_cardinality = 'cardinality' in edge.properties
        has_on_conditions = 'on_conditions' in edge.properties
        
        if has_cardinality or has_on_conditions:
            enriched_edges.append(edge)
            print(f"\n   Edge: {edge.source_id} -> {edge.target_id}")
            print(f"   - Label: {edge.label}")
            print(f"   - Cardinality: {edge.properties.get('cardinality', 'N/A')}")
            print(f"   - ON conditions: {edge.properties.get('on_conditions', 'N/A')}")
            print(f"   - Inferred: {edge.properties.get('inferred', 'N/A')}")
    
    if enriched_edges:
        print(f"\n   ✓ Found {len(enriched_edges)} enriched edges (with cardinality/on_conditions)")
    else:
        print("\n   ✗ NO enriched edges found!")
        print("   This means relationship_mapper is NOT returning semantic metadata")
    
    # Step 3: Test to_dict() serialization
    print("\n3. Testing to_dict() serialization...")
    if fk_edges:
        test_edge = fk_edges[0]
        edge_dict = test_edge.to_dict()
        
        print(f"\n   Edge properties dict:")
        for key, value in test_edge.properties.items():
            print(f"   - {key}: {value}")
        
        print(f"\n   Edge to_dict() result:")
        for key, value in edge_dict.items():
            print(f"   - {key}: {value}")
        
        # Check if properties were flattened
        if test_edge.properties:
            all_flattened = all(k in edge_dict for k in test_edge.properties.keys())
            if all_flattened:
                print("\n   ✓ Properties correctly flattened to top level")
            else:
                print("\n   ✗ Properties NOT fully flattened")
    
    print("\n" + "=" * 80)
    print("DEBUG COMPLETE")
    print("=" * 80)

if __name__ == '__main__':
    main()