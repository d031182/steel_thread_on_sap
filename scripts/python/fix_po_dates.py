#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Fix PO Dates to be within Last 30 Days
Updates PurchaseOrder and PurchaseOrderItem dates to match invoice timeframe
"""

import sqlite3
from datetime import datetime, timedelta
import sys
import os

# Fix Windows encoding
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

DB_PATH = "modules/sqlite_connection/database/p2p_test_data.db"

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

print("Updating PO dates to last 30 days...")

# Calculate new dates (within last 30 days)
base_date = datetime.now() - timedelta(days=25)

# Update PurchaseOrder
cursor.execute("SELECT PurchaseOrder FROM PurchaseOrder ORDER BY PurchaseOrder")
pos = cursor.fetchall()

for i, (po_id,) in enumerate(pos):
    new_date = base_date + timedelta(days=i*2)
    
    cursor.execute("""
        UPDATE PurchaseOrder 
        SET PurchaseOrderDate = ?,
            CreationDate = ?,
            LastChangeDateTime = ?
        WHERE PurchaseOrder = ?
    """, (
        new_date.strftime('%Y-%m-%d'),
        new_date.strftime('%Y-%m-%d'),
        new_date.strftime('%Y-%m-%dT%H:%M:%S'),
        po_id
    ))
    
    # Update PurchaseOrderItem
    cursor.execute("""
        UPDATE PurchaseOrderItem
        SET CreationDate = ?,
            LastChangeDateTime = ?
        WHERE PurchaseOrder = ?
    """, (
        new_date.strftime('%Y-%m-%d'),
        new_date.strftime('%Y-%m-%dT%H:%M:%S'),
        po_id
    ))
    
    print(f"  Updated {po_id}: {new_date.strftime('%Y-%m-%d')}")

conn.commit()
conn.close()

print(f"\n✅ Updated {len(pos)} POs to last 30 days")
print("\nNew date range:")
print(f"  First PO: {base_date.strftime('%Y-%m-%d')}")
print(f"  Last PO: {(base_date + timedelta(days=(len(pos)-1)*2)).strftime('%Y-%m-%d')}")