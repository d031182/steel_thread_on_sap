import sqlite3
import os

dbs = ['p2p_data.db', 'p2p_data_legacy.db', 'p2p_data_products.db']

for db in dbs:
    path = f'database/{db}'
    if os.path.exists(path):
        conn = sqlite3.connect(path)
        cursor = conn.cursor()
        tables = cursor.execute('SELECT name FROM sqlite_master WHERE type="table"').fetchall()
        print(f'{db}: {os.path.getsize(path)} bytes - {len(tables)} tables')
        for table in tables:
            if 'Supplier' in table[0] or 'Invoice' in table[0]:
                count = cursor.execute(f'SELECT COUNT(*) FROM "{table[0]}"').fetchone()[0]
                print(f'  -> {table[0]}: {count} rows')
        conn.close()