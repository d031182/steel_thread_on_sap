import sqlite3

conn = sqlite3.connect('database/p2p_data.db')
cursor = conn.cursor()

# Get all tables
cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
tables = cursor.fetchall()

print(f"\n✅ Tables in database: {len(tables)}")
for table in tables:
    table_name = table[0]
    print(f"\n📊 Table: {table_name}")
    
    # Get row count
    cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
    count = cursor.fetchone()[0]
    print(f"   Rows: {count}")
    
    # Get first 2 rows
    cursor.execute(f"SELECT * FROM {table_name} LIMIT 2")
    rows = cursor.fetchall()
    
    # Get column names
    cursor.execute(f"PRAGMA table_info({table_name})")
    columns = [col[1] for col in cursor.fetchall()]
    print(f"   Columns: {', '.join(columns)}")
    
    if rows:
        print(f"   Sample data:")
        for row in rows:
            print(f"     {row}")

conn.close()