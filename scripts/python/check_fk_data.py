import sqlite3
import json

conn = sqlite3.connect('app/p2p_data.db')
cursor = conn.cursor()

# Check PurchaseOrder
print("=== PurchaseOrder ===")
cursor.execute('SELECT * FROM PurchaseOrder LIMIT 2')
rows = cursor.fetchall()
cols = [d[0] for d in cursor.description]
print(f"Columns ({len(cols)}): {cols[:15]}...")
if rows:
    for row in rows[:1]:
        data = dict(zip(cols, row))
        # Show only non-NULL fields
        non_null = {k: v for k, v in data.items() if v is not None}
        print(f"Non-NULL fields: {list(non_null.keys())}")
        print(f"Sample values: {dict(list(non_null.items())[:10])}")

# Check SupplierInvoice
print("\n=== SupplierInvoice ===")
cursor.execute('SELECT * FROM SupplierInvoice LIMIT 2')
rows = cursor.fetchall()
cols = [d[0] for d in cursor.description]
print(f"Columns ({len(cols)}): {cols[:15]}...")
if rows:
    for row in rows[:1]:
        data = dict(zip(cols, row))
        non_null = {k: v for k, v in data.items() if v is not None}
        print(f"Non-NULL fields: {list(non_null.keys())}")
        print(f"Sample values: {dict(list(non_null.items())[:10])}")

conn.close()