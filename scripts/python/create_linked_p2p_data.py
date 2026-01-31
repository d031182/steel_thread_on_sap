#!/usr/bin/env python3
"""
Create Realistic Linked P2P Data

Creates end-to-end consistent P2P process:
1. Suppliers (already exist)
2. Purchase Orders → Suppliers
3. Supplier Invoices → Purchase Orders & Suppliers (LINKED!)
4. Invoice Items → PO Items (LINKED!)

Includes blocked invoice scenarios for reporting.

@author P2P Development Team
@version 1.0.0
"""

import sys
import os
import sqlite3
from datetime import datetime, timedelta

# Fix Windows encoding
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Add project root to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

DB_PATH = 'app/database/p2p_data_products.db'

print("="*80)
print("Linked P2P Data Creation (End-to-End Consistency)")
print("="*80)
print(f"\nDatabase: {DB_PATH}")
print(f"Timestamp: {datetime.now()}\n")

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

# Clear existing invoices to rebuild with correct links
print("Clearing old invoice data...")
cursor.execute("DELETE FROM SupplierInvoiceItem")
cursor.execute("DELETE FROM SupplierInvoice")
conn.commit()
print("[OK] Old invoices cleared\n")

# Get existing POs and Suppliers
cursor.execute("SELECT PurchaseOrder, Supplier FROM PurchaseOrder ORDER BY PurchaseOrder")
pos = cursor.fetchall()

if not pos:
    print("[ERROR] No purchase orders found! Run create_realistic_p2p_data.py first.")
    conn.close()
    sys.exit(1)

print(f"Found {len(pos)} purchase orders to invoice\n")

# Scenario 1: Normal Invoices (First 6 POs) - Match PO amounts
print("SCENARIO 1: Normal Invoices (Matching PO)")
print("-" * 80)

base_date = datetime.now() - timedelta(days=60)
normal_count = 0

for i, (po_number, supplier) in enumerate(pos[:6], start=1):
    invoice_number = f"5100{i:06d}"
    invoice_date = base_date + timedelta(days=i*5)
    
    # Insert invoice header
    cursor.execute("""
        INSERT INTO SupplierInvoice (
            SupplierInvoice, FiscalYear, CompanyCode,
            DocumentDate, PostingDate,
            InvoicingParty, IsInvoice,
            DocumentCurrency, InvoiceGrossAmount,
            SupplierInvoiceStatus, SupplierInvoiceOrigin
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        invoice_number,
        invoice_date.year,
        '1010',
        invoice_date.strftime('%Y-%m-%d'),
        invoice_date.strftime('%Y-%m-%d'),
        supplier,
        1,
        'USD',
        5000.00,  # Standard amount
        '5',  # Posted
        '1'   # Online
    ))
    
    # Insert invoice item linking to PO
    cursor.execute("""
        INSERT INTO SupplierInvoiceItem (
            SupplierInvoice, FiscalYear, SupplierInvoiceItem,
            PurchaseOrder, PurchaseOrderItem,
            QtyInPurchaseOrderPriceUnit, PurchaseOrderPriceUnit,
            SupplierInvoiceItemAmount, DocumentCurrency,
            CompanyCode, InvoicingParty,
            DocumentDate, PostingDate,
            SuplrInvcItemHasPriceVariance, SuplrInvcItemHasQtyVariance,
            SupplierInvoiceStatus, IsInvoice
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        invoice_number,
        invoice_date.year,
        '000001',
        po_number,
        '00010',
        100.0,
        'EA',
        5000.00,
        'USD',
        '1010',
        supplier,
        invoice_date.strftime('%Y-%m-%d'),
        invoice_date.strftime('%Y-%m-%d'),
        0,  # No price variance
        0,  # No qty variance
        '5',  # Posted
        1
    ))
    
    normal_count += 1
    print(f"  [OK] Invoice {invoice_number} -> PO {po_number} (Supplier: {supplier})")

print(f"\nCreated {normal_count} normal invoices\n")

# Scenario 2: Blocked Invoices (Next 2 POs) - Price variance
print("SCENARIO 2: Blocked Invoices (Price Variance)")
print("-" * 80)

blocked_count = 0
for i, (po_number, supplier) in enumerate(pos[6:8], start=1):
    invoice_number = f"5200{i:06d}"
    invoice_date = base_date + timedelta(days=40 + i*5)
    
    # Higher invoice amount than PO (price variance!)
    variance = 500.00 * i
    invoice_amount = 5000.00 + variance
    
    # Insert invoice header
    cursor.execute("""
        INSERT INTO SupplierInvoice (
            SupplierInvoice, FiscalYear, CompanyCode,
            DocumentDate, PostingDate,
            InvoicingParty, IsInvoice,
            DocumentCurrency, InvoiceGrossAmount,
            SupplierInvoiceStatus, SupplierInvoiceOrigin
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        invoice_number,
        invoice_date.year,
        '1010',
        invoice_date.strftime('%Y-%m-%d'),
        invoice_date.strftime('%Y-%m-%d'),
        supplier,
        1,
        'USD',
        invoice_amount,
        '1',  # Defined (not posted - BLOCKED!)
        '1'   # Online
    ))
    
    # Insert invoice item with price variance flag
    cursor.execute("""
        INSERT INTO SupplierInvoiceItem (
            SupplierInvoice, FiscalYear, SupplierInvoiceItem,
            PurchaseOrder, PurchaseOrderItem,
            QtyInPurchaseOrderPriceUnit, PurchaseOrderPriceUnit,
            SupplierInvoiceItemAmount, DocumentCurrency,
            CompanyCode, InvoicingParty,
            DocumentDate, PostingDate,
            SuplrInvcItemHasPriceVariance, SuplrInvcItemHasQtyVariance,
            SupplierInvoiceStatus, IsInvoice
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        invoice_number,
        invoice_date.year,
        '000001',
        po_number,
        '00010',
        100.0,
        'EA',
        invoice_amount,
        'USD',
        '1010',
        supplier,
        invoice_date.strftime('%Y-%m-%d'),
        invoice_date.strftime('%Y-%m-%d'),
        1,  # HAS PRICE VARIANCE!
        0,
        '1',  # Defined (BLOCKED)
        1
    ))
    
    blocked_count += 1
    variance_pct = (variance / 5000.00) * 100
    print(f"  [BLOCKED] Invoice {invoice_number} -> PO {po_number}")
    print(f"            Variance: ${variance:.2f} ({variance_pct:.1f}% over PO)")
    print(f"            Status: Blocked (not posted)")

print(f"\nCreated {blocked_count} blocked invoices\n")

# Scenario 3: In-Progress (Last 2 POs) - No invoices yet
print("SCENARIO 3: In-Progress Orders (No Invoice Yet)")
print("-" * 80)
for po_number, supplier in pos[8:]:
    print(f"  [PENDING] PO {po_number} -> Supplier {supplier} (Awaiting invoice)")

conn.commit()

# Final Summary
print("\n" + "="*80)
print("LINKED P2P DATA SUMMARY")
print("="*80)

cursor.execute("SELECT COUNT(*) FROM Supplier")
supplier_count = cursor.fetchone()[0]

cursor.execute("SELECT COUNT(*) FROM PurchaseOrder")
po_count = cursor.fetchone()[0]

cursor.execute("SELECT COUNT(*) FROM SupplierInvoice")
invoice_count = cursor.fetchone()[0]

cursor.execute("SELECT COUNT(*) FROM SupplierInvoiceItem")
item_count = cursor.fetchone()[0]

# Verify linking
cursor.execute("""
    SELECT COUNT(*) 
    FROM SupplierInvoiceItem sii
    INNER JOIN PurchaseOrder po ON sii.PurchaseOrder = po.PurchaseOrder
""")
linked_count = cursor.fetchone()[0]

print(f"\nMaster Data:")
print(f"  - Suppliers: {supplier_count}")

print(f"\nTransactional Data:")
print(f"  - Purchase Orders: {po_count}")
print(f"  - Supplier Invoices: {invoice_count}")
print(f"  - Invoice Items: {item_count}")
print(f"  - Linked Items (Invoice->PO): {linked_count} of {item_count}")

print(f"\nEnd-to-End Flow:")
print(f"  - Complete (PO -> Invoice): {normal_count} transactions")
print(f"  - Blocked (Price Variance): {blocked_count} transactions")
print(f"  - In Progress (No Invoice): {po_count - normal_count - blocked_count} transactions")

print("\n" + "="*80)
print("[OK] REALISTIC P2P DATA CREATED")
print("="*80)
print("\nProcess Flow Validation:")
print("  1. Supplier exists")
print("  2. Purchase Order references Supplier")
print("  3. Supplier Invoice references BOTH Supplier AND PO")
print("  4. Invoice Items reference PO Items")
print("  5. Price variance logic applied for blocked scenarios")
print("\nReady for Knowledge Graph visualization!")

conn.close()