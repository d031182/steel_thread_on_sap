#!/usr/bin/env python3
"""
Test Data Products V2 Tables API
=================================

Test the /api/data-products/{productName}/tables endpoint
to see why no tables are returned.
"""

import requests
import json

def test_tables_api():
    """Test the tables API endpoint"""
    
    base_url = "http://localhost:5000"
    
    # First, get the list of data products
    print("=" * 60)
    print("1. Fetching data products...")
    print("=" * 60)
    
    response = requests.get(f"{base_url}/api/data-products/?source=sqlite")
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        print(f"Success: {result.get('success')}")
        products = result.get('data_products', [])
        print(f"Found {len(products)} data products")
        
        # Show first product details
        if products:
            product = products[0]
            print(f"\nFirst product:")
            print(f"  - product_name: {product.get('product_name')}")
            print(f"  - display_name: {product.get('display_name')}")
            print(f"  - table_count: {product.get('table_count')}")
            
            # Now test getting tables for this product
            product_name = product.get('product_name')
            
            print("\n" + "=" * 60)
            print(f"2. Fetching tables for '{product_name}'...")
            print("=" * 60)
            
            tables_response = requests.get(
                f"{base_url}/api/data-products/{product_name}/tables?source=sqlite"
            )
            print(f"Status: {tables_response.status_code}")
            print(f"Response: {tables_response.text}")
            
            if tables_response.status_code == 200:
                tables_result = tables_response.json()
                print(f"\nSuccess: {tables_result.get('success')}")
                tables = tables_result.get('tables', [])
                print(f"Found {len(tables)} tables")
                
                if tables:
                    print("\nTables:")
                    for table in tables[:5]:  # Show first 5
                        print(f"  - {table.get('table_name')} ({table.get('TABLE_TYPE', 'UNKNOWN')})")
                else:
                    print("\nWARNING: No tables returned!")
                    print("This explains why the UI shows 'No tables found'")
            else:
                print(f"ERROR: {tables_response.text}")
    else:
        print(f"ERROR: {response.text}")

if __name__ == "__main__":
    test_tables_api()