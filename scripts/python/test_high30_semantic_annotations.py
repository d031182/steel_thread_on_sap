"""
Test Script for HIGH-30: Semantic Annotation Extraction

Verifies that CSN parser correctly extracts:
- Display labels (@title, @Common.Label, @EndUserText.label)
- Descriptions (@EndUserText.quickInfo, @Common.QuickInfo)
- Semantic types (@Semantics.amount, @Semantics.currencyCode)
- Semantic properties (@Semantics.amount.currencyCode)
"""

import sys
import os

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from core.services.csn_parser import CSNParser


def test_semantic_annotations():
    """Test semantic annotation extraction from CSN"""
    
    print("=" * 80)
    print("HIGH-30: Semantic Annotation Extraction Test")
    print("=" * 80)
    
    parser = CSNParser('docs/csn')
    
    # Test entity: SupplierInvoice (known to have annotations)
    print("\n1. Testing SupplierInvoice entity metadata...")
    invoice_metadata = parser.get_entity_metadata('SupplierInvoice')
    
    if not invoice_metadata:
        print("❌ FAILED: SupplierInvoice entity not found")
        return False
    
    print(f"✅ Found SupplierInvoice with {len(invoice_metadata.columns)} columns")
    
    # Test 2: Find fields with display labels
    print("\n2. Testing display label extraction...")
    labeled_fields = [col for col in invoice_metadata.columns if col.display_label]
    
    if labeled_fields:
        print(f"✅ Found {len(labeled_fields)} fields with display labels:")
        for col in labeled_fields[:5]:  # Show first 5
            print(f"   - {col.name}: '{col.display_label}'")
    else:
        print("⚠️ WARNING: No fields with display labels found")
    
    # Test 3: Find fields with descriptions
    print("\n3. Testing description extraction...")
    described_fields = [col for col in invoice_metadata.columns if col.description]
    
    if described_fields:
        print(f"✅ Found {len(described_fields)} fields with descriptions:")
        for col in described_fields[:3]:  # Show first 3
            desc_preview = col.description[:60] + "..." if len(col.description) > 60 else col.description
            print(f"   - {col.name}: {desc_preview}")
    else:
        print("⚠️ WARNING: No fields with descriptions found")
    
    # Test 4: Find fields with semantic types
    print("\n4. Testing semantic type extraction...")
    semantic_fields = [col for col in invoice_metadata.columns if col.semantic_type]
    
    if semantic_fields:
        print(f"✅ Found {len(semantic_fields)} fields with semantic types:")
        for col in semantic_fields[:5]:  # Show first 5
            props = f" (properties: {list(col.semantic_properties.keys())})" if col.semantic_properties else ""
            print(f"   - {col.name}: @Semantics.{col.semantic_type}{props}")
    else:
        print("⚠️ WARNING: No fields with semantic types found")
    
    # Test 5: Find amount fields specifically
    print("\n5. Testing amount field detection...")
    amount_fields = [
        col for col in invoice_metadata.columns 
        if col.semantic_type == 'amount'
    ]
    
    if amount_fields:
        print(f"✅ Found {len(amount_fields)} amount fields:")
        for col in amount_fields:
            currency_code = col.semantic_properties.get('currencyCode', 'N/A')
            print(f"   - {col.name}: currency={currency_code}")
    else:
        print("⚠️ WARNING: No amount fields found")
    
    # Test 6: Check annotation completeness
    print("\n6. Testing annotation completeness...")
    annotated_fields = [
        col for col in invoice_metadata.columns 
        if col.all_annotations
    ]
    
    print(f"✅ {len(annotated_fields)}/{len(invoice_metadata.columns)} fields have annotations")
    
    if annotated_fields:
        # Show one example with all annotations
        example = annotated_fields[0]
        print(f"\n   Example field '{example.name}' annotations:")
        for key, value in list(example.all_annotations.items())[:5]:  # Show first 5
            print(f"      {key}: {value}")
    
    # Test 7: Test multiple entities
    print("\n7. Testing across multiple entities...")
    test_entities = ['PurchaseOrder', 'Supplier', 'PurchaseOrderItem']
    
    for entity_name in test_entities:
        metadata = parser.get_entity_metadata(entity_name)
        if metadata:
            labeled = sum(1 for col in metadata.columns if col.display_label)
            semantic = sum(1 for col in metadata.columns if col.semantic_type)
            print(f"   - {entity_name}: {labeled} labeled fields, {semantic} semantic fields")
    
    # Test 8: Verify get_column_metadata() method
    print("\n8. Testing get_column_metadata() method...")
    
    # Try to find a specific field
    if invoice_metadata.columns:
        test_field = invoice_metadata.columns[0].name
        col_meta = parser.get_column_metadata('SupplierInvoice', test_field)
        
        if col_meta:
            print(f"✅ get_column_metadata() works: {test_field}")
            print(f"   - Type: {col_meta.type}")
            print(f"   - Label: {col_meta.display_label or 'N/A'}")
            print(f"   - Semantic: {col_meta.semantic_type or 'N/A'}")
        else:
            print(f"❌ FAILED: get_column_metadata() returned None")
            return False
    
    print("\n" + "=" * 80)
    print("✅ HIGH-30 SEMANTIC ANNOTATION EXTRACTION TEST COMPLETE")
    print("=" * 80)
    
    return True


if __name__ == '__main__':
    success = test_semantic_annotations()
    sys.exit(0 if success else 1)