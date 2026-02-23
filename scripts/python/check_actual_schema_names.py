"""
Check actual schema names in the database
"""
import sqlite3

db_path = "modules/data_products_v2/database/p2p_data.db"
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# First, check what tables exist
cursor.execute("""
    SELECT name FROM sqlite_master 
    WHERE type='table' 
    ORDER BY name
""")

print("TABLES IN DATABASE:")
print("=" * 80)
for row in cursor.fetchall():
    print(f"  {row[0]}")

print("\n" + "=" * 80)

# Check data_products table
cursor.execute("SELECT id, name, namespace FROM data_products")
print("\nDATA PRODUCTS:")
print("=" * 80)
for row in cursor.fetchall():
    print(f"  ID: {row[0]}, Name: {row[1]}, Namespace: {row[2]}")

conn.close()