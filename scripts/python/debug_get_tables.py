"""
Debug script to test get_tables() logic

This script helps debug why tables are not being returned for Purchase Order.
"""

import os
import sys

# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)

from core.services.sqlite_data_products_service import SQLiteDataProductsService

def main():
    """Test the get_tables() method with different schema formats"""
    
    # Initialize service
    service = SQLiteDataProductsService()
    
    print("=" * 80)
    print("DEBUG: get_tables() method")
    print("=" * 80)
    
    # Test different schema name formats
    test_schemas = [
        'SQLITE_PURCHASEORDER',      # What repository builds (no space/underscore)
        'SQLITE_PURCHASE_ORDER',     # What frontend might send (with underscore)
        'SQLITE_Purchase Order',     # With space (unlikely)
    ]
    
    for schema in test_schemas:
        print(f"\n{'='*80}")
        print(f"Testing schema: '{schema}'")
        print(f"{'='*80}")
        
        # Extract product name as the service does
        product_name = schema.replace('SQLITE_', '').lower()
        print(f"Extracted product_name: '{product_name}'")
        
        # Call get_tables
        try:
            tables = service.get_tables(schema)
            print(f"✓ SUCCESS: Found {len(tables)} tables")
            if tables:
                print(f"  Tables: {[t['TABLE_NAME'] for t in tables[:3]]}...")
            else:
                print(f"  WARNING: No tables found!")
        except Exception as e:
            print(f"✗ ERROR: {e}")
    
    print(f"\n{'='*80}")
    print("Testing get_data_products() to see what schemaName is generated")
    print(f"{'='*80}")
    
    products = service.get_data_products()
    for p in products:
        if 'Purchase' in p['productName']:
            print(f"\nProduct: {p['productName']}")
            print(f"  schemaName: {p['schemaName']}")
            print(f"  tableCount: {p['tableCount']}")

if __name__ == '__main__':
    main()