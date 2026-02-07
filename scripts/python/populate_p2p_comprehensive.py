#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Populate P2P Database with Comprehensive Test Data
===================================================
Creates HANA-compatible test data for P2P Dashboard testing:
- 10 Suppliers
- 20 Purchase Orders  
- 30 Invoices (10+ as requested)
- 5 Service Entry Sheets
- Supporting data (PaymentTerms, CompanyCode)

Uses actual HANA Cloud CSN schema field names.
No HANA connection required - pure synthetic data.

Author: P2P Development Team
Date: 2026-02-07
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

def populate_comprehensive_data():
    """Create comprehensive P2P test dataset"""
    
    print("="*80)
    print("POPULATE P2P COMPREHENSIVE TEST DATA")
    print("="*80)
    print(f"\nDatabase: {DB_PATH}")
    print(f"Timestamp: {datetime.now()}\n")
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Clear existing data
    print("Clearing existing data...")
    cursor.execute("DELETE FROM SupplierInvoiceItem")
    cursor.execute("DELETE FROM SupplierInvoice")
    cursor.execute("DELETE FROM PurchaseOrderItem")
    cursor.execute("DELETE FROM PurchaseOrder")
    cursor.execute("DELETE FROM ServiceEntrySheet")
    cursor.execute("DELETE FROM Supplier")
    cursor.execute("DELETE FROM PaymentTerms")
    cursor.execute("DELETE FROM CompanyCode")
    print("  Done\n")
    
    # ==================================================
    # 1. Company Codes
    # ==================================================
    print("[1/7] Creating Company Codes...")
    cursor.execute("""
        INSERT INTO CompanyCode (
            CompanyCode, CompanyCodeName, Country, CityName, Currency, Language
        ) VALUES (?, ?, ?, ?, ?, ?)
    """, ('1010', 'SAP SE', 'DE', 'Walldorf', 'EUR', 'EN'))
    
    cursor.execute("""
        INSERT INTO CompanyCode (
            CompanyCode, CompanyCodeName, Country, CityName, Currency, Language
        ) VALUES (?, ?, ?, ?, ?, ?)
    """, ('2000', 'SAP US', 'US', 'Palo Alto', 'USD', 'EN'))
    
    conn.commit()
    print("  Created 2 company codes\n")
    
    # ==================================================
    # 2. Payment Terms
    # ==================================================
    print("[2/7] Creating Payment Terms...")
    payment_terms = [
        ('Z001', 'Net 30 Days'),
        ('Z002', 'Net 60 Days'),
        ('Z003', '2/10 Net 30'),
        ('Z004', 'Due on Receipt'),
        ('Z005', 'Net 45 Days')
    ]
    
    for pt_id, pt_name in payment_terms:
        cursor.execute("""
            INSERT INTO PaymentTerms (PaymentTerms, _Text)
            VALUES (?, ?)
        """, (pt_id, pt_name))
    
    conn.commit()
    print(f"  Created {len(payment_terms)} payment terms\n")
    
    # ==================================================
    # 3. Suppliers (10 total)
    # ==================================================
    print("[3/7] Creating Suppliers (10)...")
    suppliers = [
        ('0000100001', 'Global Tech Solutions GmbH', 'DE', 'Munich'),
        ('0000100002', 'Enterprise Software AG', 'DE', 'Berlin'),
        ('0000100003', 'Cloud Services Ltd', 'GB', 'London'),
        ('0000100004', 'Data Systems Corp', 'US', 'New York'),
        ('0000100005', 'Innovation Partners SAS', 'FR', 'Paris'),
        ('0000100006', 'Quality Goods BV', 'NL', 'Amsterdam'),
        ('0000100007', 'Precision Mfg SpA', 'IT', 'Milan'),
        ('0000100008', 'Digital Solutions AB', 'SE', 'Stockholm'),
        ('0000100009', 'Smart Logistics SA', 'ES', 'Madrid'),
        ('0000100010', 'Future Tech KK', 'JP', 'Tokyo')
    ]
    
    for supplier_id, name, country, city in suppliers:
        cursor.execute("""
            INSERT INTO Supplier (
                Supplier, SupplierName, SupplierFullName,
                Country, CityName, SupplierAccountGroup,
                PurchasingIsBlocked, CreationDate
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (supplier_id, name, f"{name} Corp", country, city, 'CRED', 0, '2025-01-01'))
    
    conn.commit()
    print(f"  Created {len(suppliers)} suppliers\n")
    
    # ==================================================
    # 4. Purchase Orders (20 total)
    # ==================================================
    print("[4/7] Creating Purchase Orders (20)...")
    base_date = datetime.now() - timedelta(days=60)
    po_count = 0
    
    for i in range(1, 21):
        po_id = f"4500{i:06d}"
        supplier_id = suppliers[(i-1) % 10][0]  # Cycle through suppliers
        payment_term = payment_terms[(i-1) % 5][0]
        po_date = base_date + timedelta(days=i*3)
        
        cursor.execute("""
            INSERT INTO PurchaseOrder (
                PurchaseOrder, Supplier, CompanyCode,
                PurchasingOrganization, PurchasingGroup,
                PurchaseOrderType, PurchaseOrderDate,
                DocumentCurrency, PaymentTerms,
                CreationDate, LastChangeDateTime,
                PurchasingDocumentDeletionCode, CreatedByUser
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            po_id, supplier_id, '1010',
            'P001', 'G01',
            'NB', po_date.strftime('%Y-%m-%d'),
            'EUR', payment_term,
            po_date.strftime('%Y-%m-%d'), po_date.strftime('%Y-%m-%dT%H:%M:%S'),
            None if i <= 15 else 'L',  # Last 5 POs cancelled
            'BUYER01'
        ))
        
        # Add PO items (2 per PO)
        for item_num in [10, 20]:
            cursor.execute("""
                INSERT INTO PurchaseOrderItem (
                    PurchaseOrder, PurchaseOrderItem,
                    Supplier, CompanyCode,
                    MaterialGroup, Material,
                    OrderQuantity, PurchaseOrderQuantityUnit,
                    NetPriceAmount, NetAmount,
                    DocumentCurrency, Plant,
                    CreationDate, LastChangeDateTime,
                    IsCompletelyDelivered, IsFinallyInvoiced,
                    PurgDocumentItemDeletionCode
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                po_id, f"{item_num:05d}",
                supplier_id, '1010',
                'MATGRP001', f'MAT{item_num:05d}',
                100.0, 'EA',
                50.00, 5000.00,
                'EUR', 'P001',
                po_date.strftime('%Y-%m-%d'), po_date.strftime('%Y-%m-%dT%H:%M:%S'),
                1 if i <= 8 else 0,  # First 8 POs completed
                1 if i <= 8 else 0,  # First 8 POs invoiced
                'L' if i > 15 else None  # Last 5 cancelled
            ))
        
        po_count += 1
    
    conn.commit()
    print(f"  Created {po_count} purchase orders with {po_count*2} items\n")
    
    # ==================================================
    # 5. Supplier Invoices (30 total) ← 10+ requested
    # ==================================================
    print("[5/7] Creating Supplier Invoices (30)...")
    invoice_count = 0
    
    # Get first 15 POs (the completed ones)
    cursor.execute("SELECT PurchaseOrder, Supplier FROM PurchaseOrder ORDER BY PurchaseOrder LIMIT 15")
    completed_pos = cursor.fetchall()
    
    for i, (po_id, supplier_id) in enumerate(completed_pos):
        # Create 2 invoices per PO (30 total)
        for inv_seq in [1, 2]:
            invoice_id = f"5100{i*2 + inv_seq:06d}"
            fiscal_year = str(datetime.now().year)
            invoice_date = base_date + timedelta(days=(i*3)+14+(inv_seq*7))
            
            # Some invoices pending, most posted
            status = 'PENDING' if invoice_count >= 26 else 'POSTED'
            
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
            
            # Add invoice item (linked to PO)
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
                    SuplrInvcItemHasAmountVariance, SuplrInvcItemHasOtherVariance,
                    IsInvoice, SupplierInvoiceStatus
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                invoice_id, fiscal_year, '000001',
                po_id, '00010',
                100.0, 'EA',
                5000.00, 'EUR',
                '1010', supplier_id,
                invoice_date.strftime('%Y-%m-%d'), invoice_date.strftime('%Y-%m-%d'),
                0, 0, 0, 0, 0, 0,  # No variances
                1, status
            ))
            
            invoice_count += 1
    
    conn.commit()
    print(f"  Created {invoice_count} invoices with {invoice_count} items\n")
    
    # ==================================================
    # 6. Service Entry Sheets (5 total)
    # ==================================================
    print("[6/7] Creating Service Entry Sheets (5)...")
    cursor.execute("SELECT PurchaseOrder, Supplier FROM PurchaseOrder ORDER BY PurchaseOrder LIMIT 5")
    pos_for_ses = cursor.fetchall()
    
    ses_count = 0
    for po_id, supplier_id in pos_for_ses:
        ses_id = f"0100{ses_count+1:06d}"
        ses_date = base_date + timedelta(days=ses_count*14+7)
        
        cursor.execute("""
            INSERT INTO ServiceEntrySheet (
                ServiceEntrySheet, ServiceEntrySheetName,
                PurchaseOrder, Supplier,
                ServiceEntrySheetDate, CreationDate,
                DocumentDate, CompanyCode,
                ApprovalStatus, ApprovalDateTime,
                ServicePerformer
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            ses_id, f"Service Confirmation {ses_id}",
            po_id, supplier_id,
            ses_date.strftime('%Y-%m-%d'), ses_date.strftime('%Y-%m-%dT%H:%M:%S'),
            ses_date.strftime('%Y-%m-%d'), '1010',
            'APPROVED' if ses_count < 4 else 'PENDING',
            (ses_date + timedelta(days=1)).strftime('%Y-%m-%dT%H:%M:%S') if ses_count < 4 else None,
            supplier_id
        ))
        
        ses_count += 1
    
    conn.commit()
    print(f"  Created {ses_count} service entry sheets\n")
    
    # ==================================================
    # 7. Schedule Lines (for delivery tracking)
    # ==================================================
    print("[7/7] Creating PO Schedule Lines (20)...")
    cursor.execute("SELECT PurchaseOrder, PurchaseOrderItem FROM PurchaseOrderItem ORDER BY PurchaseOrder, PurchaseOrderItem LIMIT 20")
    po_items = cursor.fetchall()
    
    schedule_count = 0
    for po_id, item_id in po_items:
        cursor.execute("""
            INSERT INTO PurchaseOrderScheduleLine (
                PurchaseOrder, PurchaseOrderItem, ScheduleLine,
                ScheduleLineDeliveryDate, ScheduleLineOrderQuantity,
                IsCompletelyDelivered, DelivDateCategory,
                ConfirmedDeliveryDate
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            po_id, item_id, '0001',
            (base_date + timedelta(days=schedule_count*3+14)).strftime('%Y-%m-%d'),
            100.0,
            1 if schedule_count < 16 else 0,
            'ON_TIME' if schedule_count < 14 else ('DELAYED' if schedule_count < 16 else 'PENDING'),
            (base_date + timedelta(days=schedule_count*3+14+(1 if schedule_count >= 14 else 0))).strftime('%Y-%m-%d') if schedule_count < 16 else None
        ))
        
        schedule_count += 1
    
    conn.commit()
    print(f"  Created {schedule_count} schedule lines\n")
    
    # ==================================================
    # SUMMARY
    # ==================================================
    print("\n" + "="*80)
    print("DATA POPULATION COMPLETE")
    print("="*80)
    
    summary = {}
    for table in ['Supplier', 'CompanyCode', 'PaymentTerms', 'PurchaseOrder', 
                  'PurchaseOrderItem', 'PurchaseOrderScheduleLine',
                  'SupplierInvoice', 'SupplierInvoiceItem', 'ServiceEntrySheet']:
        cursor.execute(f"SELECT COUNT(*) FROM {table}")
        count = cursor.fetchone()[0]
        summary[table] = count
    
    print("\nFinal Record Counts:")
    print(f"  Suppliers: {summary['Supplier']}")
    print(f"  Company Codes: {summary['CompanyCode']}")
    print(f"  Payment Terms: {summary['PaymentTerms']}")
    print(f"  Purchase Orders: {summary['PurchaseOrder']}")
    print(f"  PO Items: {summary['PurchaseOrderItem']}")
    print(f"  PO Schedule Lines: {summary['PurchaseOrderScheduleLine']}")
    print(f"  Invoices: {summary['SupplierInvoice']} (10+ as requested)")
    print(f"  Invoice Items: {summary['SupplierInvoiceItem']}")
    print(f"  Service Sheets: {summary['ServiceEntrySheet']}")
    
    # Calculate totals
    cursor.execute("SELECT SUM(InvoiceGrossAmount) FROM SupplierInvoice WHERE DocumentCurrency='EUR'")
    total_invoice = cursor.fetchone()[0] or 0
    
    cursor.execute("SELECT SUM(NetAmount) FROM PurchaseOrderItem WHERE DocumentCurrency='EUR'")
    total_po = cursor.fetchone()[0] or 0
    
    print(f"\nFinancial Summary:")
    print(f"  Total PO Value (EUR): {total_po:,.2f}")
    print(f"  Total Invoice Value (EUR): {total_invoice:,.2f}")
    
    conn.close()
    
    print("\n[OK] Population complete!")
    print("\nNext steps:")
    print("  1. Copy database to: modules/sqlite_connection/database/")
    print("  2. Update app.py path if needed")
    print("  3. Test P2P Dashboard at http://localhost:5000")
    
    return summary

if __name__ == '__main__':
    populate_comprehensive_data()