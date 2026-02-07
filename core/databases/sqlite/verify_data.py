#!/usr/bin/env python3
"""Verify test data in P2P database"""
import sqlite3

conn = sqlite3.connect('modules/sqlite_connection/database/p2p_test_data.db')
cursor = conn.cursor()

print('Tables:')
for t in cursor.execute('SELECT name FROM sqlite_master WHERE type="table" ORDER BY name').fetchall():
    print(f'  - {t[0]}')

print('\nData counts:')
print(f'  Suppliers: {cursor.execute("SELECT COUNT(*) FROM Supplier").fetchone()[0]}')
print(f'  Purchase Orders: {cursor.execute("SELECT COUNT(*) FROM PurchaseOrder").fetchone()[0]}')
print(f'  Invoices: {cursor.execute("SELECT COUNT(*) FROM SupplierInvoice").fetchone()[0]}')
print(f'  Service Sheets: {cursor.execute("SELECT COUNT(*) FROM ServiceEntrySheet").fetchone()[0]}')

total = cursor.execute("SELECT SUM(InvoiceGrossAmount) FROM SupplierInvoice WHERE Currency='EUR'").fetchone()[0]
print(f'\nTotal Invoice Value (EUR): {total:,.2f}')

conn.close()
print('\nDatabase verification complete!')