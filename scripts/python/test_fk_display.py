"""
Quick test to verify FK information is returned by API
"""
import requests
import json

# Test structure endpoint for PurchaseOrderItem (has FK to PurchaseOrder)
response = requests.get(
    'http://localhost:5000/api/data-products/SQLITE_PURCHASEORDER/PurchaseOrderItem/structure?source=sqlite'
)

data = response.json()

if data['success']:
    print(f"OK Found {len(data['columns'])} columns")
    print("\nColumns with Foreign Keys:")
    print("-" * 80)
    
    for col in data['columns']:
        fk = col.get('foreignKey') or col.get('FOREIGN_KEY')
        if fk:
            print(f"  {col['name']:30s} -> {fk}")
    
    # Show first few columns with all details
    print("\nFirst 3 Columns (Full Details):")
    print("-" * 80)
    for col in data['columns'][:3]:
        print(f"  Name: {col['name']}")
        print(f"  Type: {col['dataType']}")
        print(f"  Nullable: {col['nullable']}")
        print(f"  FK: {col.get('foreignKey') or '-'}")
        print()
else:
    print(f"ERROR: {data.get('error')}")
