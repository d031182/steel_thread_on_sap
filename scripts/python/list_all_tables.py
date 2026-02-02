"""List all tables in the database."""
import sqlite3

conn = sqlite3.connect('app/p2p_data.db')
cursor = conn.cursor()

cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
tables = cursor.fetchall()

print(f'\nTotal Tables: {len(tables)}\n')
print('All Tables:')
for table in tables:
    print(f'  - {table[0]}')

# Check specifically for graph tables
print('\nGraph-related tables:')
graph_tables = [t[0] for t in tables if 'graph' in t[0].lower()]
for table in graph_tables:
    cursor.execute(f'SELECT COUNT(*) FROM {table}')
    count = cursor.fetchone()[0]
    print(f'  - {table}: {count} rows')

conn.close()
