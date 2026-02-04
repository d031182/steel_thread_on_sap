"""Check if schema graph is using cache"""
import sqlite3

conn = sqlite3.connect('logs/app_logs.db')
cursor = conn.cursor()

# Get recent logs related to relationship discovery
cursor.execute('''
    SELECT timestamp, level, message 
    FROM application_logs 
    WHERE (logger LIKE "%relationship%" OR logger LIKE "%schema%" OR message LIKE "%cache%")
    AND timestamp > datetime("now", "-5 minutes")
    ORDER BY timestamp DESC 
    LIMIT 20
''')

rows = cursor.fetchall()

if rows:
    print("Recent cache/relationship logs:")
    print("=" * 80)
    for row in rows:
        # Remove unicode characters
        msg = row[2].replace('\u2713', '[OK]').replace('\u2717', '[X]')
        print(f"{row[0]} | {row[1]} | {msg[:100]}")
else:
    print("No recent logs found")

conn.close()