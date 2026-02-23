"""
Check the data_products table structure and content
"""
import sqlite3
import json

db_path = 'modules/data_products_v2/database/p2p_data.db'

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Check if data_products table exists
cursor.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name='data_products'")
schema = cursor.fetchone()
if schema:
    print("data_products table schema:")
    print(schema[0])
    print("\n" + "="*80 + "\n")
else:
    print("ERROR: data_products table does not exist!")
    conn.close()
    exit(1)

# Get all data products
cursor.execute("SELECT * FROM data_products LIMIT 5")
rows = cursor.fetchall()

# Get column names
column_names = [description[0] for description in cursor.description]

print(f"Found {len(rows)} data products (showing first 5):")
print(f"Columns: {column_names}\n")

for row in rows:
    data = dict(zip(column_names, row))
    print(f"Data Product: {data.get('name', 'N/A')}")
    print(f"  ID: {data.get('id', 'N/A')}")
    print(f"  Namespace: {data.get('namespace', 'N/A')}")
    print(f"  Description: {data.get('description', 'N/A')[:80]}...")
    
    # Try to parse tables JSON if it exists
    if 'tables' in data and data['tables']:
        try:
            tables = json.loads(data['tables'])
            print(f"  Tables count: {len(tables)}")
            if len(tables) > 0:
                print(f"    First table: {tables[0]}")
        except:
            print(f"  Tables (raw): {data['tables'][:100]}...")
    print()

conn.close()