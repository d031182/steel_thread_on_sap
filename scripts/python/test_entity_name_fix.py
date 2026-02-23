"""
Test script to verify entity_name parameter is working correctly

This tests the full call chain to ensure product names with spaces
(like "Purchase Order") are correctly looked up in metadata tables.
"""

import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from core.services.sqlite_data_products_service import SQLiteDataProductsService

def test_entity_name_parameter():
    """Test that entity_name parameter correctly looks up metadata"""
    
    # Get default database path
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    db_path = os.path.join(project_root, 'core', 'databases', 'sqlite', 'p2p_test_data.db')
    
    print(f"Testing with database: {db_path}")
    print(f"Database exists: {os.path.exists(db_path)}\n")
    
    service = SQLiteDataProductsService(db_path)
    
    # Test Case 1: Product with space in name
    print("="*80)
    print("Test Case 1: Purchase Order (has space)")
    print("="*80)
    
    schema_name = "SQLITE_PURCHASEORDER"
    entity_name = "Purchase Order"  # With space (as in metadata table)
    
    print(f"Calling get_tables(schema='{schema_name}', entity_name='{entity_name}')")
    
    tables = service.get_tables(schema_name, entity_name=entity_name)
    
    print(f"\nFound {len(tables)} tables:")
    for table in tables[:3]:  # Show first 3
        print(f"  - {table['TABLE_NAME']}: {table.get('SEMANTIC_LABEL', 'No label')}")
    
    # Test Case 2: Product without space
    print("\n" + "="*80)
    print("Test Case 2: Invoice (no space)")
    print("="*80)
    
    schema_name = "SQLITE_INVOICE"
    entity_name = "Invoice"  # No space
    
    print(f"Calling get_tables(schema='{schema_name}', entity_name='{entity_name}')")
    
    tables = service.get_tables(schema_name, entity_name=entity_name)
    
    print(f"\nFound {len(tables)} tables:")
    for table in tables[:3]:
        print(f"  - {table['TABLE_NAME']}: {table.get('SEMANTIC_LABEL', 'No label')}")
    
    # Test Case 3: Without entity_name (fallback behavior)
    print("\n" + "="*80)
    print("Test Case 3: Purchase Order WITHOUT entity_name (fallback)")
    print("="*80)
    
    schema_name = "SQLITE_PURCHASEORDER"
    
    print(f"Calling get_tables(schema='{schema_name}', entity_name=None)")
    
    tables = service.get_tables(schema_name, entity_name=None)
    
    print(f"\nFound {len(tables)} tables:")
    for table in tables[:3]:
        print(f"  - {table['TABLE_NAME']}: {table.get('SEMANTIC_LABEL', 'No label')}")

if __name__ == '__main__':
    test_entity_name_parameter()