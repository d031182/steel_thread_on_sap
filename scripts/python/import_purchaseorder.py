#!/usr/bin/env python3
"""Import Purchase Order schema into SQLite database"""

import sqlite3

# Connect to database
conn = sqlite3.connect('app/database/p2p_data_products.db')

# Read and execute schema
with open('app/database/schema/purchaseorder.sql', 'r') as f:
    schema = f.read()
    conn.executescript(schema)
    conn.commit()

# Verify tables
cursor = conn.cursor()
cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
tables = [r[0] for r in cursor.fetchall()]

print('Tables after import:')
for t in tables:
    cursor.execute(f"SELECT COUNT(*) FROM {t}")
    count = cursor.fetchone()[0]
    print(f'  - {t}: {count} records')

conn.close()
print('\n[OK] Purchase Order schema imported successfully!')