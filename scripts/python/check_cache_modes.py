import sqlite3

conn = sqlite3.connect('app/p2p_data.db')
cursor = conn.cursor()

cursor.execute('SELECT mode, source, COUNT(*) as count FROM graph_cache_ontology GROUP BY mode, source')
print('Cache Contents:')
for row in cursor.fetchall():
    print(f'  mode={row[0]}, source={row[1]}, count={row[2]}')

conn.close()