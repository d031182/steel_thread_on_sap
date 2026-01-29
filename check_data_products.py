import sqlite3

# Check the correct database file
db_path = 'app/database/p2p_data_products.db'
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

print(f"Checking database: {db_path}\n")

# Get ALL tables
cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
tables = cursor.fetchall()

print(f"All tables: {len(tables)}")
for table in tables:
    table_name = table[0]
    # Get row count
    cursor.execute(f"SELECT COUNT(*) FROM `{table_name}`")
    count = cursor.fetchone()[0]
    if count > 0:
        print(f"  - {table_name}: {count} rows")

# Check for Purchase Order tables
print("\nPurchase Order tables:")
cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name LIKE '%Purch%' ORDER BY name")
po_tables = cursor.fetchall()
if po_tables:
    for table in po_tables:
        cursor.execute(f"SELECT COUNT(*) FROM `{table[0]}`")
        count = cursor.fetchone()[0]
        print(f"  - {table[0]}: {count} rows")
else:
    print("  No Purchase Order tables found!")

conn.close()