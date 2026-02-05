import sqlite3
import os

backup_dir = 'database_cleanup_backup_20260205'
dbs = [f for f in os.listdir(backup_dir) if f.endswith('.db')]

print('Checking backup databases:\n')
for db in dbs:
    db_path = os.path.join(backup_dir, db)
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")
    tables = [row[0] for row in cursor.fetchall()]
    
    supplier_count = 'N/A'
    if 'Supplier' in tables:
        cursor.execute("SELECT COUNT(*) FROM Supplier")
        supplier_count = cursor.fetchone()[0]
    
    print(f'\n{db}:')
    print(f'  Tables: {len(tables)}')
    print(f'  Supplier rows: {supplier_count}')
    if len(tables) > 0:
        print(f'  Table names: {", ".join(tables[:5])}{"..." if len(tables) > 5 else ""}')
    
    conn.close()