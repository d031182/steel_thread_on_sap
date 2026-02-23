"""Direct database verification - test the actual file that should be used."""
import sqlite3
import os

# Use the ACTUAL database location
db_path = 'modules/data_products_v2/database/p2p_data.db'

print(f"Testing database: {db_path}")
print(f"File exists: {os.path.exists(db_path)}")
print(f"File size: {os.path.getsize(db_path) if os.path.exists(db_path) else 'N/A'} bytes")
print()

if os.path.exists(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Get all tables
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
    tables = cursor.fetchall()
    print(f"Found {len(tables)} tables:")
    for table in tables:
        print(f"  - {table[0]}")
    print()
    
    # Check for data_products table specifically
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='data_products'")
    if cursor.fetchone():
        print("✓ data_products table exists")
        cursor.execute("SELECT COUNT(*) FROM data_products")
        count = cursor.fetchone()[0]
        print(f"✓ Contains {count} records")
        
        if count > 0:
            cursor.execute("SELECT id, name, description FROM data_products LIMIT 5")
            print("\nSample records:")
            for row in cursor.fetchall():
                print(f"  {row[0]}: {row[1]} - {row[2][:50] if row[2] else 'No description'}...")
    else:
        print("✗ data_products table NOT found")
    
    conn.close()
else:
    print("✗ Database file does not exist!")