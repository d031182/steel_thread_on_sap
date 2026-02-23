"""Comprehensive diagnostic for data products tables API issue"""
import requests
import sqlite3
import os
from urllib.parse import quote

# Configuration
BASE_URL = "http://localhost:5000"
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
db_path = os.path.join(project_root, 'modules', 'data_products_v2', 'database', 'p2p_data.db')

print("=" * 80)
print("DIAGNOSTIC: Data Products Tables API")
print("=" * 80)
print()

# Step 1: Check database
print("STEP 1: Database Check")
print("-" * 80)
print(f"Database path: {db_path}")
print(f"Database exists: {os.path.exists(db_path)}")
print()

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Get sample data products with namespace
cursor.execute('SELECT id, name, namespace FROM data_products LIMIT 5')
products = cursor.fetchall()

print("Sample data products:")
for product_id, name, namespace in products:
    cursor.execute('SELECT COUNT(*) FROM tables WHERE data_product_id = ?', (product_id,))
    table_count = cursor.fetchone()[0]
    print(f"  ID={product_id}, namespace=\"{namespace}\", name=\"{name}\", tables={table_count}")
print()

# Step 2: Test /api/data-products endpoint
print("STEP 2: Test /api/data-products Endpoint")
print("-" * 80)
try:
    response = requests.get(f"{BASE_URL}/api/data-products", timeout=5)
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"Success: {data.get('success', 'N/A')}")
        products_list = data.get('data', {}).get('products', [])
        print(f"Products count: {len(products_list)}")
        if products_list:
            print(f"Sample product: {products_list[0]}")
    else:
        print(f"Error: {response.text}")
except Exception as e:
    print(f"Exception: {e}")
print()

# Step 3: Test /api/data-products/{namespace}/tables with NAMESPACE
print("STEP 3: Test /api/data-products/{namespace}/tables (Using Namespace)")
print("-" * 80)

# Test with a known namespace from database
test_namespace = "purchaseorder"  # Known to have data
print(f"Testing with namespace: \"{test_namespace}\"")
print()

try:
    url = f"{BASE_URL}/api/data-products/{test_namespace}/tables"
    print(f"URL: {url}")
    response = requests.get(url, timeout=5)
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"Success: {data.get('success', 'N/A')}")
        tables_list = data.get('data', {}).get('tables', [])
        print(f"Tables count: {len(tables_list)}")
        if tables_list:
            print(f"Sample table: {tables_list[0]}")
    else:
        print(f"Error response: {response.text}")
except Exception as e:
    print(f"Exception: {e}")
print()

# Step 4: Check what backend expects
print("STEP 4: Backend API Analysis")
print("-" * 80)
print("The API route is: /api/data-products/<product_identifier>/tables")
print()
print("Key Question: Does the backend expect:")
print("  A) namespace (clean identifier without spaces)")
print("  B) URL-encoded name (with %20 for spaces)")
print("  C) numeric ID")
print()
print("RECOMMENDATION: Backend should use namespace for URL-friendly routing")
print("  Example: /api/data-products/purchaseorder/tables")
print("  NOT: /api/data-products/Purchase%20Order/tables")
print()

# Step 5: Test all identification methods
print("STEP 5: Test All Identification Methods")
print("-" * 80)

# Get a product with tables
cursor.execute('''
    SELECT dp.id, dp.name, dp.namespace, COUNT(t.id) as table_count
    FROM data_products dp
    LEFT JOIN tables t ON t.data_product_id = dp.id
    WHERE dp.namespace = ?
    GROUP BY dp.id
''', (test_namespace,))

result = cursor.fetchone()
if result:
    product_id, product_name, product_namespace, table_count = result
    print(f"Test Product:")
    print(f"  ID: {product_id}")
    print(f"  Name: {product_name}")
    print(f"  Namespace: {product_namespace}")
    print(f"  Table Count (DB): {table_count}")
    print()
    
    # Test with namespace (RECOMMENDED)
    print(f"Test A: Using namespace \"{product_namespace}\"")
    try:
        url = f"{BASE_URL}/api/data-products/{product_namespace}/tables"
        response = requests.get(url, timeout=5)
        print(f"  URL: {url}")
        print(f"  Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            tables_count = len(data.get('data', {}).get('tables', []))
            print(f"  ✓ SUCCESS - Tables returned: {tables_count}")
        else:
            print(f"  ✗ FAILED - {response.text[:100]}")
    except Exception as e:
        print(f"  ✗ EXCEPTION: {e}")
    print()
    
    # Test with URL-encoded name (OLD WAY)
    print(f"Test B: Using URL-encoded name \"{product_name}\"")
    try:
        encoded_name = quote(product_name)
        url = f"{BASE_URL}/api/data-products/{encoded_name}/tables"
        response = requests.get(url, timeout=5)
        print(f"  URL: {url}")
        print(f"  Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            tables_count = len(data.get('data', {}).get('tables', []))
            print(f"  ✓ SUCCESS - Tables returned: {tables_count}")
        else:
            print(f"  ✗ FAILED - {response.text[:100]}")
    except Exception as e:
        print(f"  ✗ EXCEPTION: {e}")
    print()
    
    # Test with ID
    print(f"Test C: Using numeric ID {product_id}")
    try:
        url = f"{BASE_URL}/api/data-products/{product_id}/tables"
        response = requests.get(url, timeout=5)
        print(f"  URL: {url}")
        print(f"  Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            tables_count = len(data.get('data', {}).get('tables', []))
            print(f"  ✓ SUCCESS - Tables returned: {tables_count}")
        else:
            print(f"  ✗ FAILED - {response.text[:100]}")
    except Exception as e:
        print(f"  ✗ EXCEPTION: {e}")
    print()

conn.close()

print("=" * 80)
print("DIAGNOSIS COMPLETE")
print("=" * 80)
print()
print("NEXT STEPS:")
print("1. Verify which identification method works (namespace recommended)")
print("2. Update backend API to use namespace as route parameter")
print("3. Update frontend adapter to use namespace in URLs")
print("4. Ensure consistency: always use namespace, never URL-encoded names")