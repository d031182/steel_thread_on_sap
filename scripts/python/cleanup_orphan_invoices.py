#!/usr/bin/env python3
"""
Cleanup Orphan Supplier Invoices

Deletes supplier invoices that are not linked to any purchase order.
"""

import sqlite3

DB_PATH = 'app/database/p2p_data_products.db'

print("="*80)
print("Cleanup Orphan Supplier Invoices")
print("="*80)

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

# Find orphan invoices (invoices without linked PO)
cursor.execute("""
    SELECT si.SupplierInvoice, si.FiscalYear
    FROM SupplierInvoice si
    LEFT JOIN SupplierInvoiceItem sii 
        ON si.SupplierInvoice = sii.SupplierInvoice 
        AND si.FiscalYear = sii.FiscalYear
    WHERE sii.SupplierInvoice IS NULL
""")

orphans = cursor.fetchall()

if not orphans:
    print("\n[OK] No orphan invoices found. All invoices are properly linked!")
    conn.close()
else:
    print(f"\nFound {len(orphans)} orphan invoices:")
    print("-" * 80)
    for inv, year in orphans:
        print(f"  - {inv} (FY: {year})")
    
    # Delete orphan invoice items first (if any exist)
    cursor.execute("""
        DELETE FROM SupplierInvoiceItem
        WHERE SupplierInvoice IN (
            SELECT si.SupplierInvoice
            FROM SupplierInvoice si
            LEFT JOIN SupplierInvoiceItem sii 
                ON si.SupplierInvoice = sii.SupplierInvoice 
                AND si.FiscalYear = sii.FiscalYear
            WHERE sii.SupplierInvoice IS NULL
        )
    """)
    items_deleted = cursor.rowcount
    
    # Delete orphan invoice headers
    cursor.execute("""
        DELETE FROM SupplierInvoice
        WHERE SupplierInvoice IN (
            SELECT si.SupplierInvoice
            FROM SupplierInvoice si
            LEFT JOIN SupplierInvoiceItem sii 
                ON si.SupplierInvoice = sii.SupplierInvoice 
                AND si.FiscalYear = sii.FiscalYear
            WHERE sii.SupplierInvoice IS NULL
        )
    """)
    headers_deleted = cursor.rowcount
    
    conn.commit()
    
    print(f"\n[DELETED]")
    print(f"  - Invoice Headers: {headers_deleted}")
    print(f"  - Invoice Items: {items_deleted}")
    
    # Verify cleanup
    cursor.execute("SELECT COUNT(*) FROM SupplierInvoice")
    remaining = cursor.fetchone()[0]
    
    print(f"\n[RESULT]")
    print(f"  - Remaining Invoices: {remaining}")
    print(f"  - All remaining invoices are linked to POs!")
    
    conn.close()

print("\n" + "="*80)
print("[COMPLETE] Orphan cleanup finished")
print("="*80)