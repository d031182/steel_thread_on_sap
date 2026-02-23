"""
Quick script to inspect SQLite database structure
"""
import sqlite3

db_path = 'modules/data_products_v2/database/p2p_data.db'

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Get all tables
cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
tables = [row[0] for row in cursor.fetchall()]

print(f"Total tables: {len(tables)}")
print("\nFirst 20 tables:")
for t in tables[:20]:
    print(f"  {t}")

# Check for metadata tables
metadata_tables = [t for t in tables if 'metadata' in t.lower()]
print(f"\nMetadata tables: {metadata_tables}")

# Check for any catalog/schema tracking tables
catalog_tables = [t for t in tables if any(keyword in t.lower() for keyword in ['catalog', 'schema', 'product'])]
print(f"\nCatalog/Schema/Product tracking tables: {catalog_tables}")

conn.close()