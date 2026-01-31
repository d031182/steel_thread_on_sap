"""
Test CSN Parser Service

Validates CSN parsing functionality with downloaded CSN files.
"""

from core.services.csn_parser import CSNParser, get_parser, list_entities
import json


def test_csn_parser():
    """Test CSN parser with Purchase Order"""
    print("=" * 80)
    print("CSN Parser Test")
    print("=" * 80)
    print()
    
    # Test 1: List all entities
    print("[Test 1] List all entities in CSN files")
    entities = list_entities()
    print(f"Found {len(entities)} entities:")
    for entity in entities:
        print(f"  - {entity}")
    print()
    
    # Test 2: Get PurchaseOrder metadata
    print("[Test 2] Get PurchaseOrder metadata")
    parser = get_parser()
    
    # Primary keys
    pks = parser.get_primary_keys('PurchaseOrder')
    print(f"Primary Keys: {pks}")
    print()
    
    # Full metadata
    metadata = parser.get_entity_metadata('PurchaseOrder')
    if metadata:
        print(f"Entity: {metadata.name}")
        print(f"Original Name: {metadata.original_name}")
        print(f"Label: {metadata.label}")
        print(f"Columns: {len(metadata.columns)}")
        print(f"Primary Keys: {metadata.primary_keys}")
        print(f"Associations: {len(metadata.associations)}")
        print()
        
        # Show first 10 columns
        print("First 10 columns:")
        for col in metadata.columns[:10]:
            key_marker = "🔑" if col.is_key else "  "
            print(f"  {key_marker} {col.name}: {col.type}({col.length})")
        print()
        
        # Show associations
        if metadata.associations:
            print(f"Associations ({len(metadata.associations)}):")
            for assoc in metadata.associations[:5]:
                print(f"  - {assoc.name} -> {assoc.target} ({assoc.cardinality})")
        print()
    
    # Test 3: Foreign keys
    print("[Test 3] Get foreign keys")
    fks = parser.get_foreign_keys('PurchaseOrder')
    if fks:
        print(f"Foreign Keys: {len(fks)}")
        for fk in fks[:5]:
            print(f"  - {fk['name']} -> {fk['references_table']}.{fk['references_column']}")
    else:
        print("No foreign keys found")
    print()
    
    # Test 4: Test other entities
    print("[Test 4] Test other entities")
    test_entities = ['Supplier', 'SupplierInvoice', 'JournalEntryHeader']
    for entity_name in test_entities:
        pks = parser.get_primary_keys(entity_name)
        print(f"{entity_name}: PKs = {pks}")
    print()
    
    # Test 5: Performance check
    print("[Test 5] Performance check (cache)")
    import time
    
    # First call (cold cache)
    start = time.time()
    parser.get_entity_metadata('PurchaseOrder')
    cold_time = time.time() - start
    
    # Second call (warm cache)
    start = time.time()
    parser.get_entity_metadata('PurchaseOrder')
    warm_time = time.time() - start
    
    print(f"Cold cache: {cold_time*1000:.2f}ms")
    print(f"Warm cache: {warm_time*1000:.2f}ms")
    print(f"Speedup: {cold_time/warm_time:.1f}x")
    print()
    
    print("=" * 80)
    print("All tests completed!")
    print("=" * 80)


if __name__ == '__main__':
    test_csn_parser()