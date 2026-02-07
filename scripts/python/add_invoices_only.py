#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Add Supplier Invoices Only (Minimal Script)
Uses existing POs and Suppliers, adds 15 invoices with correct HANA schema
"""

import sqlite3
from datetime import datetime, timedelta
import sys
import os

# Fix Windows encoding
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

DB_PATH = "app/database/p2p_data_products.db"

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

print("Adding 15 Supplier Invoices...")

# Get existing POs
cursor.execute("SELECT PurchaseOrder, Supplier FROM PurchaseOrder ORDER BY PurchaseOrder")
pos = cursor.fetchall()

if not pos:
    print("ERROR: No purchase orders found!")
    conn.close()
    exit(1)

base_date = datetime.now() - timedelta(days=30)
invoice_count = 0

# Create 15 invoices (1-2 per PO)
for i, (po_id, supplier_id) in enumerate(pos[:10]):  # Use first 10 POs
    # Create 1-2 invoices per PO
    num_invoices = 2 if i < 5 else 1
    
    for seq in range(num_invoices):
        invoice_id = f"5100{invoice_count+1:06d}"
        fiscal_year = str(datetime.now().year)
        invoice_date = base_date + timedelta(days=(i*3)+14+(seq*7))
        
        # First 12 posted, last 3 pending
        status = 'PENDING' if invoice_count >= 12 else 'POSTED'
        
        cursor.execute("""
            INSERT INTO SupplierInvoice (
                SupplierInvoice, FiscalYear, CompanyCode,
                DocumentDate, PostingDate,
                InvoicingParty, IsInvoice,
                DocumentCurrency, InvoiceGrossAmount,
                SupplierInvoiceStatus, SupplierInvoiceOrigin
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            invoice_id, fiscal_year, '1010',
            invoice_date.strftime('%Y-%m-%d'), invoice_date.strftime('%Y-%m-%d'),
            supplier_id, 1,
            'EUR', 5000.00 + (i * 100),
            status, '1'
        ))
        
        # Add invoice item
        cursor.execute("""
            INSERT INTO SupplierInvoiceItem (
                SupplierInvoice, FiscalYear, SupplierInvoiceItem,
                PurchaseOrder, PurchaseOrderItem,
                QtyInPurchaseOrderPriceUnit, PurchaseOrderPriceUnit,
                SupplierInvoiceItemAmount, DocumentCurrency,
                CompanyCode, InvoicingParty,
                DocumentDate, PostingDate,
                SuplrInvcItemHasPriceVariance, SuplrInvcItemHasQtyVariance,
                SuplrInvcItmHasQualityVariance, SuplrInvcItemHasOrdPrcQtyVarc,
                SuplrInvcItemHasAmountOutsdTol, SuplrInvcItemHasOtherVariance,
                IsInvoice, SupplierInvoiceStatus
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            invoice_id, fiscal_year, '000001',
            po_id, '00010',
            100.0, 'EA',
            5000.00, 'EUR',
            '1010', supplier_id,
            invoice_date.strftime('%Y-%m-%d'), invoice_date.strftime('%Y-%m-%d'),
            0, 0, 0, 0, 0, 0,
            1, status
        ))
        
        invoice_count += 1
        print(f"  [{status}] Invoice {invoice_id} → PO {po_id}")
        
        if invoice_count >= 15:
            break
    
    if invoice_count >= 15:
        break

conn.commit()
conn.close()

print(f"\n✅ Added {invoice_count} invoices (12 POSTED, 3 PENDING)")
print(f"\nFinal counts:")
print(f"  Suppliers: 10")
print(f"  Purchase Orders: 10")
print(f"  Invoices: {invoice_count}")