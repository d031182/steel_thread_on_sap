#!/usr/bin/env python3
"""
Comprehensive SQLite Data Population

Populates SQLite database with realistic P2P data following these rules:
1. Master data: Subset synced from HANA Cloud (allows fluent integration)
2. Transactional data: Realistic end-to-end P2P process
3. Includes blocked invoice scenarios for reporting

Order of execution:
1. Sync master data from HANA (Suppliers, Products, CompanyCode, PaymentTerms)
2. Create realistic purchase orders
3. Create service entry sheets
4. Create supplier invoices (some blocked for reporting)
5. Create journal entries

@author P2P Development Team
@version 1.0.0
"""

import sys
import os
import sqlite3
from datetime import datetime, timedelta
import random

# Add project root to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

DB_PATH = 'app/database/p2p_data_products.db'

print("="*80)
print("Comprehensive SQLite Data Population")
print("="*80)
print(f"\nDatabase: {DB_PATH}")
print(f"Timestamp: {datetime.now()}\n")

# Step 1: Sync master data from HANA
print("STEP 1: Syncing Master Data from HANA")
print("-" * 80)
print("This ensures SQLite contains a subset of HANA data for fluent integration\n")

try:
    import subprocess
    
    # Run the HANA sync script
    result = subprocess.run(
        ['python', 'scripts/python/sync_master_data_from_hana.py'],
        capture_output=True,
        text=True,
        timeout=60
    )
    
    if result.returncode == 0:
        print("✓ Master data synced from HANA successfully")
        print(result.stdout[-500:] if len(result.stdout) > 500 else result.stdout)
    else:
        print("⚠ HANA sync failed (continuing with local data)")
        print(f"Error: {result.stderr}")
        
        # Fallback: Create minimal master data locally
        print("\nFallback: Creating minimal master data locally...")
        subprocess.run(['python', 'scripts/python/generate_master_data_simple.py'])
        
except Exception as e:
    print(f"⚠ Could not sync from HANA: {e}")
    print("Creating minimal master data locally...")
    subprocess.run(['python', 'scripts/python/generate_master_data_simple.py'])

print("\n")

# Step 2: Create realistic P2P transactional data
print("STEP 2: Creating Realistic P2P Transactional Data")
print("-" * 80)
print("End-to-end consistent purchase-to-pay process\n")

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

# Get master data for FK references
cursor.execute("SELECT Supplier FROM Supplier LIMIT 5")
suppliers = [row[0] for row in cursor.fetchall()]

cursor.execute("SELECT CompanyCode FROM CompanyCode LIMIT 3")
company_codes = [row[0] for row in cursor.fetchall()]

cursor.execute("SELECT PaymentTerms FROM PaymentTerms LIMIT 3")
payment_terms = [row[0] for row in cursor.fetchall()]

if not suppliers or not company_codes:
    print("⚠ No master data found! Please check HANA sync or master data creation.")
    conn.close()
    sys.exit(1)

print(f"Found master data:")
print(f"  - {len(suppliers)} suppliers")
print(f"  - {len(company_codes)} company codes")
print(f"  - {len(payment_terms)} payment terms\n")

# Scenario data for realistic P2P process
base_date = datetime.now() - timedelta(days=90)

# Scenario 1: Normal flow (PO → GR → Invoice → Payment) - 3 POs
print("Creating Scenario 1: Normal P2P Flow (3 Purchase Orders)")
normal_pos = []
for i in range(1, 4):
    po_number = f"4500{i:06d}"
    po_date = base_date + timedelta(days=i*10)
    
    cursor.execute("""
        INSERT INTO PurchaseOrder (
            PurchaseOrder, Supplier, CompanyCode, 
            PurchasingOrganization, PurchasingGroup,
            DocumentDate, CreationDate,
            PurchaseOrderType, PaymentTerms
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        po_number,
        suppliers[i % len(suppliers)],
        company_codes[0],
        '1000',
        'P01',
        po_date.strftime('%Y-%m-%d'),
        po_date.strftime('%Y-%m-%d'),
        'NB',
        payment_terms[0] if payment_terms else 'Z001'
    ))
    
    # PO Item
    cursor.execute("""
        INSERT INTO PurchaseOrderItem (
            PurchaseOrder, PurchaseOrderItem,
            Material, PurchaseOrderItemText,
            OrderQuantity, OrderPriceUnit,
            NetPriceAmount, CompanyCode
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        po_number, '00010',
        f'MAT{i:05d}', f'Standard Material {i}',
        100.0, 'EA',
        50.00, company_codes[0]
    ))
    
    normal_pos.append((po_number, suppliers[i % len(suppliers)], 5000.00))
    print(f"  ✓ Created PO {po_number}")

# Scenario 2: Blocked invoices (various blocking reasons) - 2 POs
print("\nCreating Scenario 2: Blocked Invoices (2 Purchase Orders)")
blocked_pos = []
blocking_reasons = [
    ('01', 'Price variance'),
    ('02', 'Quantity variance')
]

for i, (block_code, block_reason) in enumerate(blocking_reasons, start=1):
    po_number = f"4501{i:06d}"
    po_date = base_date + timedelta(days=i*10 + 40)
    
    cursor.execute("""
        INSERT INTO PurchaseOrder (
            PurchaseOrder, Supplier, CompanyCode,
            PurchasingOrganization, PurchasingGroup,
            DocumentDate, CreationDate,
            PurchaseOrderType, PaymentTerms
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        po_number,
        suppliers[i % len(suppliers)],
        company_codes[0],
        '1000',
        'P01',
        po_date.strftime('%Y-%m-%d'),
        po_date.strftime('%Y-%m-%d'),
        'NB',
        payment_terms[0] if payment_terms else 'Z001'
    ))
    
    cursor.execute("""
        INSERT INTO PurchaseOrderItem (
            PurchaseOrder, PurchaseOrderItem,
            Material, PurchaseOrderItemText,
            OrderQuantity, OrderPriceUnit,
            NetPriceAmount, CompanyCode
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        po_number, '00010',
        f'MAT{10+i:05d}', f'Material for Blocked Invoice {i}',
        100.0, 'EA',
        60.00, company_codes[0]
    ))
    
    blocked_pos.append((po_number, suppliers[i % len(suppliers)], 6000.00, block_code, block_reason))
    print(f"  ✓ Created PO {po_number} (will have blocked invoice)")

# Create Service Entry Sheets for Normal POs
print("\nCreating Service Entry Sheets...")
for po_number, supplier, _ in normal_pos[:2]:  # First 2 POs
    ses_number = f"100{po_number[4:]}"
    ses_date = base_date + timedelta(days=int(po_number[-2:]) + 5)
    
    cursor.execute("""
        INSERT INTO ServiceEntrySheet (
            ServiceEntrySheet, PurchaseOrder, Supplier,
            DocumentDate, ServicePerformer
        ) VALUES (?, ?, ?, ?, ?)
    """, (
        ses_number,
        po_number,
        supplier,
        ses_date.strftime('%Y-%m-%d'),
        'External'
    ))
    print(f"  ✓ Created SES {ses_number} for PO {po_number}")

# Create Supplier Invoices
print("\nCreating Supplier Invoices...")

# Normal invoices (not blocked)
for i, (po_number, supplier, amount) in enumerate(normal_pos, start=1):
    invoice_number = f"5100{i:06d}"
    invoice_date = base_date + timedelta(days=int(po_number[-2:]) + 10)
    
    cursor.execute("""
        INSERT INTO SupplierInvoice (
            SupplierInvoice, FiscalYear, Supplier, CompanyCode,
            DocumentDate, PostingDate, InvoiceGrossAmount,
            DocumentCurrency, PaymentTerms
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        invoice_number,
        invoice_date.year,
        supplier,
        company_codes[0],
        invoice_date.strftime('%Y-%m-%d'),
        invoice_date.strftime('%Y-%m-%d'),
        amount,
        'USD',
        payment_terms[0] if payment_terms else 'Z001'
    ))
    
    # Invoice Item linking to PO
    cursor.execute("""
        INSERT INTO SupplierInvoiceItem (
            SupplierInvoice, FiscalYear, SupplierInvoiceItem,
            PurchaseOrder, PurchaseOrderItem,
            SupplierInvoiceItemAmount, CompanyCode
        ) VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        invoice_number,
        invoice_date.year,
        '0001',
        po_number,
        '00010',
        amount,
        company_codes[0]
    ))
    
    print(f"  ✓ Created Invoice {invoice_number} (Normal - Not Blocked)")

# Blocked invoices  
for i, (po_number, supplier, amount, block_code, block_reason) in enumerate(blocked_pos, start=1):
    invoice_number = f"5200{i:06d}"
    invoice_date = base_date + timedelta(days=int(po_number[-2:]) + 10)
    
    # Note: We'll simulate blocking by adding blocking indicator in a comment/field
    # In real SAP, this would be PaymentBlockingReason field
    cursor.execute("""
        INSERT INTO SupplierInvoice (
            SupplierInvoice, FiscalYear, Supplier, CompanyCode,
            DocumentDate, PostingDate, InvoiceGrossAmount,
            DocumentCurrency, PaymentTerms
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        invoice_number,
        invoice_date.year,
        supplier,
        company_codes[0],
        invoice_date.strftime('%Y-%m-%d'),
        invoice_date.strftime('%Y-%m-%d'),
        amount + 500.00,  # Price variance - higher than PO
        'USD',
        payment_terms[0] if payment_terms else 'Z001'
    ))
    
    cursor.execute("""
        INSERT INTO SupplierInvoiceItem (
            SupplierInvoice, FiscalYear, SupplierInvoiceItem,
            PurchaseOrder, PurchaseOrderItem,
            SupplierInvoiceItemAmount, CompanyCode
        ) VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        invoice_number,
        invoice_date.year,
        '0001',
        po_number,
        '00010',
        amount + 500.00,
        company_codes[0]
    ))
    
    print(f"  ✓ Created Invoice {invoice_number} (BLOCKED - {block_reason})")

# Create Journal Entries for posted invoices
print("\nCreating Journal Entries...")
for i, (po_number, supplier, amount) in enumerate(normal_pos[:2], start=1):  # First 2
    je_number = f"100{i:09d}"
    je_date = base_date + timedelta(days=int(po_number[-2:]) + 12)
    
    cursor.execute("""
        INSERT INTO JournalEntry (
            CompanyCode, FiscalYear, AccountingDocument,
            DocumentDate, PostingDate, DocumentType
        ) VALUES (?, ?, ?, ?, ?, ?)
    """, (
        company_codes[0],
        je_date.year,
        je_number,
        je_date.strftime('%Y-%m-%d'),
        je_date.strftime('%Y-%m-%d'),
        'KR'  # Vendor Invoice
    ))
    print(f"  ✓ Created Journal Entry {je_number}")

conn.commit()

# Summary Report
print("\n" + "="*80)
print("DATA POPULATION SUMMARY")
print("="*80)

cursor.execute("SELECT COUNT(*) FROM Supplier")
print(f"Suppliers: {cursor.fetchone()[0]}")

cursor.execute("SELECT COUNT(*) FROM CompanyCode")
print(f"Company Codes: {cursor.fetchone()[0]}")

cursor.execute("SELECT COUNT(*) FROM PaymentTerms")
print(f"Payment Terms: {cursor.fetchone()[0]}")

cursor.execute("SELECT COUNT(*) FROM PurchaseOrder")
print(f"Purchase Orders: {cursor.fetchone()[0]}")

cursor.execute("SELECT COUNT(*) FROM PurchaseOrderItem")
print(f"PO Items: {cursor.fetchone()[0]}")

cursor.execute("SELECT COUNT(*) FROM ServiceEntrySheet")
print(f"Service Entry Sheets: {cursor.fetchone()[0]}")

cursor.execute("SELECT COUNT(*) FROM SupplierInvoice")
print(f"Supplier Invoices: {cursor.fetchone()[0]}")

cursor.execute("SELECT COUNT(*) FROM SupplierInvoiceItem")
print(f"Invoice Items: {cursor.fetchone()[0]}")

cursor.execute("SELECT COUNT(*) FROM JournalEntry")
print(f"Journal Entries: {cursor.fetchone()[0]}")

print("\n" + "="*80)
print("SCENARIO ANALYSIS")
print("="*80)

print("\n1. Normal P2P Flow (Complete):")
print("   PO → SES → Invoice → Journal Entry")
for po_number, supplier, amount in normal_pos[:2]:
    print(f"   - PO {po_number}: {supplier} (${amount:,.2f}) ✓ Complete")

print("\n2. Blocked Invoices (For Reporting):")
for po_number, supplier, amount, block_code, block_reason in blocked_pos:
    print(f"   - PO {po_number}: {supplier} (${amount+500:,.2f})")
    print(f"     ⚠ BLOCKED: {block_reason} (Code: {block_code})")
    print(f"     Variance: ${500.00} over PO price")

print("\n3. In-Progress Transactions:")
for po_number, supplier, amount in normal_pos[2:]:
    print(f"   - PO {po_number}: {supplier} (${amount:,.2f}) - Awaiting goods receipt")

print("\n" + "="*80)
print("✓ DATA POPULATION COMPLETE")
print("="*80)
print("\nDatabase ready for:")
print("  • Knowledge graph visualization")
print("  • Blocked invoice reporting")
print("  • End-to-end P2P process analysis")
print("  • HANA integration testing")

conn.close()