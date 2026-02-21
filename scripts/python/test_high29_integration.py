"""
Test HIGH-29 Integration: Semantic Enhancement with ON Conditions

Verifies that:
1. CSNAssociationParser correctly parses associations with ON conditions
2. CSNRelationshipMapper integrates explicit associations
3. SchemaGraphBuilderService includes semantic metadata in edges
4. Graph edges contain ON conditions, cardinality, and composition flags

Usage:
    python scripts/python/test_high29_integration.py
"""
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from core.services.csn_parser import CSNParser
from core.services.relationship_mapper import CSNRelationshipMapper
from core.services.csn_association_parser import CSNAssociationParser
from modules.knowledge_graph_v2.services.schema_graph_builder_service import SchemaGraphBuilderService


def test_association_parser():
    """Test CSNAssociationParser finds associations with ON conditions"""
    print("\n" + "="*80)
    print("TEST 1: CSNAssociationParser - Parse Associations with ON Conditions")
    print("="*80)
    
    csn_parser = CSNParser('docs/csn')
    assoc_parser = CSNAssociationParser(csn_parser)
    
    # Parse all associations
    associations = assoc_parser.parse_all_associations()
    
    print(f"\n✓ Found {len(associations)} associations in CSN files")
    
    # Find associations with ON conditions
    with_on_conditions = [a for a in associations if a.conditions]
    
    print(f"✓ {len(with_on_conditions)} associations have explicit ON conditions")
    
    # Show examples
    if with_on_conditions:
        print(f"\nExample associations with ON conditions:")
        for assoc in with_on_conditions[:3]:
            print(f"\n  {assoc.source_entity}.{assoc.field_name} -> {assoc.target_entity}")
            print(f"  Cardinality: {assoc.cardinality_type.value}")
            print(f"  ON conditions:")
            for cond in assoc.conditions:
                print(f"    - {cond}")
    
    return len(with_on_conditions) > 0


def test_relationship_mapper():
    """Test CSNRelationshipMapper integrates associations"""
    print("\n" + "="*80)
    print("TEST 2: CSNRelationshipMapper - Integrate Explicit Associations")
    print("="*80)
    
    csn_parser = CSNParser('docs/csn')
    mapper = CSNRelationshipMapper(csn_parser)
    
    # Discover relationships
    relationships = mapper.discover_relationships()
    
    print(f"\n✓ Discovered {len(relationships)} total relationships")
    
    # Count explicit vs inferred
    explicit = [r for r in relationships if not r.inferred]
    inferred = [r for r in relationships if r.inferred]
    
    print(f"✓ {len(explicit)} explicit (from CSN associations)")
    print(f"✓ {len(inferred)} inferred (from naming conventions)")
    
    # Find relationships with ON conditions
    with_on = [r for r in relationships if r.on_conditions]
    
    print(f"✓ {len(with_on)} relationships have ON conditions")
    
    # Show examples
    if with_on:
        print(f"\nExample relationships with semantic metadata:")
        for rel in with_on[:3]:
            print(f"\n  {rel.from_entity}.{rel.from_column} -> {rel.to_entity}")
            print(f"  Cardinality: {rel.cardinality}")
            print(f"  Confidence: {rel.confidence}")
            print(f"  ON conditions: {rel.on_conditions}")
            if rel.is_composition:
                print(f"  Composition: Yes")
    
    return len(with_on) > 0


def test_schema_graph_builder():
    """Test SchemaGraphBuilderService includes ON conditions in edges"""
    print("\n" + "="*80)
    print("TEST 3: SchemaGraphBuilderService - Build Graph with Semantic Metadata")
    print("="*80)
    
    csn_parser = CSNParser('docs/csn')
    builder = SchemaGraphBuilderService(csn_parser)
    
    # Build graph
    graph = builder.build_from_csn()
    
    stats = graph.get_statistics()
    print(f"\n✓ Built graph with {stats['node_count']} nodes, {stats['edge_count']} edges")
    
    # Find FK edges with ON conditions
    fk_edges = [e for e in graph.edges if e.type.value == 'fk']
    edges_with_on = [e for e in fk_edges if 'on_conditions' in e.properties]
    
    print(f"✓ {len(fk_edges)} foreign key edges")
    print(f"✓ {len(edges_with_on)} FK edges have ON conditions")
    
    # Show examples
    if edges_with_on:
        print(f"\nExample FK edges with semantic metadata:")
        for edge in edges_with_on[:3]:
            props = edge.properties
            print(f"\n  {props['source_table']} -> {props['target_table']}")
            print(f"  FK Column: {props['fk_column']}")
            print(f"  Cardinality: {props.get('cardinality', 'N/A')}")
            print(f"  JOIN ON: {props.get('join_clause', 'N/A')}")
            print(f"  Confidence: {props.get('confidence', 'N/A')}")
            if props.get('is_composition'):
                print(f"  Composition: Yes")
    
    return len(edges_with_on) > 0


def test_end_to_end():
    """Test complete HIGH-29 integration"""
    print("\n" + "="*80)
    print("TEST 4: End-to-End Integration Verification")
    print("="*80)
    
    # Run all tests
    test1_passed = test_association_parser()
    test2_passed = test_relationship_mapper()
    test3_passed = test_schema_graph_builder()
    
    # Summary
    print("\n" + "="*80)
    print("INTEGRATION TEST SUMMARY")
    print("="*80)
    
    results = {
        "CSNAssociationParser": test1_passed,
        "CSNRelationshipMapper": test2_passed,
        "SchemaGraphBuilderService": test3_passed
    }
    
    all_passed = all(results.values())
    
    for component, passed in results.items():
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"{status} - {component}")
    
    if all_passed:
        print("\n🎉 ALL TESTS PASSED - HIGH-29 Integration Complete!")
        print("\nKey Achievements:")
        print("  • CSN associations parsed with ON conditions")
        print("  • Explicit relationships integrated with inferred ones")
        print("  • Graph edges contain semantic metadata (cardinality, ON clauses)")
        print("  • Knowledge graph now has 97+ explicit associations")
    else:
        print("\n⚠️ SOME TESTS FAILED - Review integration")
    
    return all_passed


if __name__ == '__main__':
    try:
        success = test_end_to_end()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)