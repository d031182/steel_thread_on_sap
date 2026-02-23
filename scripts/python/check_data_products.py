import sqlite3

conn = sqlite3.connect('database/p2p_data.db')
cursor = conn.cursor()

# Check data_products table
cursor.execute('SELECT id, name, display_name, description FROM data_products LIMIT 5')
rows = cursor.fetchall()

print('Data products in database:')
for row in rows:
    desc = row[3][:50] if row[3] else None
    print(f'  ID: {row[0]}, Name: {row[1]}, Display: {row[2]}, Desc: {desc}')

conn.close()