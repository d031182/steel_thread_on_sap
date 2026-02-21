"""
Test CSN Association Parser

Validates that the new CSNAssociationParser can successfully:
1. Parse all 97 associations from CSN files
2. Extract ON conditions correctly
3. Detect many-to-many relationships
4. Calculate relationship metrics

This is a quick validation script before writing full API contract tests.
"""

import sys
import os

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from core.services.csn_parser import CSNParser
from core.services.csn_association_parser import CSNAssociationParser


def main():
    """Test the CSN association parser"""
    print("=" * 80)
    print("CSN Association Parser Test")
    print("=" * 80)
    
    # Initialize parser
    print("\n1. Initializing CSN parser...")
    csn_parser = CSNParser('docs/csn')
    assoc_parser = CSNAssociationParser(csn_parser)
    
    # Parse all associations
    print("\n2. Parsing all associations...")
    associations = assoc_parser.parse_all_associations()
    print(f"   ✓ Found {len(associations)} associations")
    
    if len(associations) == 0:
        print("   ✗ ERROR: Expected ~97 associations, found 0")
        return False
    
    # Show sample associations
    print("\n3. Sample associations:")
    for i, assoc in enumerate(associations[:5]):
        print(f"\n   Association #{i+1}:")
        print(f"   - Source: {assoc.source_entity}")
        print(f"   - Field: {assoc.field_name}")
        print(f"   - Target: {assoc.target_entity}")
        print(f"   - Cardinality: {assoc.cardinality_type.value}")
        print(f"   - Conditions: {len(assoc.conditions)}")
        if assoc.conditions:
            for cond in assoc.conditions:
                print(f"     • {cond}")
        print(f"   - Is Composition: {assoc.is_composition}")
    
    # Get cardinality statistics
    print("\n4. Cardinality Statistics:")
    stats = assoc_parser.get_cardinality_statistics()
    for cardinality, count in stats.items():
        print(f"   - {cardinality}: {count}")
    
    # Find many-to-many relationships
    print("\n5. Detecting many-to-many relationships...")
    m2m = assoc_parser.find_many_to_many_relationships()
    print(f"   ✓ Found {len(m2m)} many-to-many relationships")
    
    if m2m:
        print("\n   Sample M:N relationships:")
        for i, (assoc1, assoc2) in enumerate(m2m[:3]):
            print(f"\n   M:N #{i+1}:")
            print(f"   - {assoc1.target_entity} ←→ {assoc2.target_entity}")
            print(f"   - Via: {assoc1.source_entity}")
    
    # Get complexity metrics
    print("\n6. Relationship Complexity Metrics:")
    metrics = assoc_parser.get_relationship_complexity_metrics()
    print(f"   - Total associations: {metrics['total_associations']}")
    print(f"   - Avg conditions per assoc: {metrics['avg_conditions_per_assoc']}")
    print(f"   - Many-to-many count: {metrics['many_to_many_count']}")
    print(f"   - Composition count: {metrics['composition_count']}")
    
    print("\n   Most connected entities:")
    for entity, count in metrics['most_connected_entities'][:5]:
        print(f"   - {entity}: {count} associations")
    
    # Validate specific known associations
    print("\n7. Validating known associations...")
    
    # Check for CompanyCode associations
    cc_assocs = [a for a in associations if 'CompanyCode' in a.source_entity]
    print(f"   - CompanyCode-related: {len(cc_assocs)}")
    
    # Check for associations with ON conditions
    with_conditions = [a for a in associations if len(a.conditions) > 0]
    print(f"   - With ON conditions: {len(with_conditions)}")
    
    # Check for compositions
    compositions = [a for a in associations if a.is_composition]
    print(f"   - Compositions: {len(compositions)}")
    
    print("\n" + "=" * 80)
    print("✓ Test Complete!")
    print(f"✓ Successfully parsed {len(associations)} associations")
    print("=" * 80)
    
    return True


if __name__ == '__main__':
    try:
        success = main()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n✗ ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)