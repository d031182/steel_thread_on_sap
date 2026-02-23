"""Check actual product names in data_products table"""
import sqlite3
import os

# Get correct database path - it's in modules/data_products_v2/database/
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
db_path = os.path.join(project_root, 'modules', 'data_products_v2', 'database', 'p2p_data.db')

print(f"Database: {db_path}")
print(f"Exists: {os.path.exists(db_path)}")
print()

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Get all product names
cursor.execute('SELECT id, name FROM data_products ORDER BY name')
products = cursor.fetchall()

print(f"Found {len(products)} data products:")
print()

for product_id, name in products:
    # Get table count
    cursor.execute('SELECT COUNT(*) FROM tables WHERE data_product_id = ?', (product_id,))
    table_count = cursor.fetchone()[0]
    
    print(f"{product_id:3d}. \"{name}\" ({table_count} tables)")

conn.close()