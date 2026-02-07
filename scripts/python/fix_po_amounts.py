#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Fix PO Item NetAmount Values
Adds realistic monetary values to PurchaseOrderItem.NetAmount
"""

import sqlite3
import sys
import os

# Fix Windows encoding
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

DB_PATH = "modules/sqlite_connection/database/p2p_test_data.db"

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

print("Adding NetAmount values to PO items...")

# Get all PO items
cursor.execute("SELECT PurchaseOrder, PurchaseOrderItem FROM PurchaseOrderItem ORDER BY PurchaseOrder, PurchaseOrderItem")
items = cursor.fetchall()

for i, (po_id, item_id) in enumerate(items):
    # Generate realistic amounts: 2,500 - 12,500 USD
    net_amount = 2500.00 + (i * 500)
    
    cursor.execute("""
        UPDATE PurchaseOrderItem
        SET NetAmount = ?,
            DocumentCurrency = 'EUR'
        WHERE PurchaseOrder = ? AND PurchaseOrderItem = ?
    """, (net_amount, po_id, item_id))
    
    print(f"  {po_id}-{item_id}: €{net_amount:,.2f}")

conn.commit()

# Verify total
cursor.execute("SELECT SUM(NetAmount) FROM PurchaseOrderItem")
total = cursor.fetchone()[0]

conn.close()

print(f"\n✅ Updated {len(items)} PO items")
print(f"Total PO Value: €{total:,.2f}")