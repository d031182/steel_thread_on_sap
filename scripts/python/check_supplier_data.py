import sqlite3
conn = sqlite3.connect('app/database/p2p_data_products.db')
cursor = conn.cursor()
cursor.execute('SELECT * FROM Supplier LIMIT 3')
rows = cursor.fetchall()
print(f'Rows: {len(rows)}')
for r in rows:
    print(r)
conn.close()