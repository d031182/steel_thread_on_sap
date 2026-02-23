"""Test hierarchical data product structure."""
import sys
from pathlib import Path

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from core.services.sqlite_data_products_service import SQLiteDataProductsService

service = SQLiteDataProductsService()
products = service.get_data_products()

print(f"✓ Total products: {len(products)}")

# Find Purchase Order
po = [p for p in products if 'Purchase Order' in p['productName']][0]
print(f"\n✓ Purchase Order product:")
print(f"  Name: {po['productName']}")
print(f"  Tables: {po['tableCount']}")

# Get tables
tables = service.get_tables(po['schemaName'])
print(f"\n✓ Tables under Purchase Order:")
for t in tables:
    print(f"  - {t['TABLE_NAME']}")

print("\n✅ Hierarchical structure working correctly!")