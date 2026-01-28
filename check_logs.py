import sqlite3

conn = sqlite3.connect('app/logs/app_logs.db')
cursor = conn.cursor()

cursor.execute('SELECT COUNT(*) FROM application_logs')
total = cursor.fetchone()[0]
print(f'Total logs in database: {total}')

cursor.execute('SELECT level, COUNT(*) FROM application_logs GROUP BY level')
print('By level:')
for row in cursor.fetchall():
    print(f'  {row[0]}: {row[1]}')

if total > 0:
    cursor.execute('SELECT timestamp, level, message FROM application_logs ORDER BY id DESC LIMIT 5')
    print('\nLast 5 logs:')
    for row in cursor.fetchall():
        print(f'  [{row[1]}] {row[0]}: {row[2][:80]}...')

conn.close()