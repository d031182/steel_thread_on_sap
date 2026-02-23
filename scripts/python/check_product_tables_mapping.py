"""
Check the data_product_tables mapping table
"""
import sqlite3

db_path = 'modules/data_products_v2/database/p2p_data.db'

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Check if data_product_tables exists
cursor.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name='data_product_tables'")
schema = cursor.fetchone()
if schema:
    print("data_product_tables schema:")
    print(schema[0])
    print("\n" + "="*80 + "\n")
    
    # Get some sample mappings
    cursor.execute("""
        SELECT dpt.data_product_id, dp.name as product_name, dpt.table_name 
        FROM data_product_tables dpt
        JOIN data_products dp ON dp.id = dpt.data_product_id
        LIMIT 10
    """)
    rows = cursor.fetchall()
    
    if rows:
        print(f"Sample mappings (showing first 10):")
        for row in rows:
            print(f"  Product ID {row[0]} ({row[1]}) -> Table: {row[2]}")
    else:
        print("No mappings found!")
    
    # Count total mappings
    cursor.execute("SELECT COUNT(*) FROM data_product_tables")
    total = cursor.fetchone()[0]
    print(f"\nTotal mappings: {total}")
else:
    print("ERROR: data_product_tables table does not exist!")

conn.close()