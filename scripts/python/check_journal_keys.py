import sqlite3

conn = sqlite3.connect('app/database/p2p_data_products.db')
cursor = conn.cursor()

# Check JournalEntry data
cursor.execute('SELECT CompanyCode, FiscalYear, AccountingDocument FROM JournalEntry LIMIT 5')
print("JournalEntry sample data:")
for row in cursor.fetchall():
    print(f"  {row[0]} + {row[1]} + {row[2]}")

# Check for duplicates on single column
cursor.execute('SELECT AccountingDocument, COUNT(*) as cnt FROM JournalEntry GROUP BY AccountingDocument HAVING cnt > 1 LIMIT 3')
print("\nDuplicate AccountingDocument values:")
for row in cursor.fetchall():
    print(f"  {row[0]}: {row[1]} times")

conn.close()