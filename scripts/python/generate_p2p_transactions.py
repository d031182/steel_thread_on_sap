#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Generate Realistic P2P Transactional Data

Generates end-to-end Procure-to-Pay transactional data that reuses
the master data already populated in SQLite.

P2P Process Flow:
1. Purchase Order (PO) created for Supplier
2. PO Items reference Products
3. Goods Receipt / Service Entry Sheet confirms delivery
4. Supplier Invoice received
5. Invoice Items link to PO Items
6. Journal Entry records financial impact

Usage: python scripts/python/generate_p2p_transactions.py

Author: P2P Development Team
Version: 1.0.0
Date: 2026-02-08
"""

import sqlite3
import sys
import os
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Dict, Any
import random

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# Fix Windows encoding
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Configuration
SQLITE_DB = "core/databases/sqlite/p2p_data.db"
NUM_POS = 20  # Number of Purchase Orders to generate
BASE_DATE = datetime.now() - timedelta(days=90)


def get_master_data(conn: sqlite3.Connection) -> Dict[str, List[Dict]]:
    """Load master data from SQLite"""
    cursor = conn.cursor()
    master_data = {}
    
    # Suppliers
    cursor.execute('SELECT Supplier, SupplierName, Country FROM Supplier LIMIT 10')
    master_data['suppliers'] = [
        {'Supplier': row[0], 'SupplierName': row[1], 'Country': row[2]}
        for row in cursor.fetchall()
    ]
    
    # Products
    cursor.execute('SELECT Product, ProductType, BaseUnit FROM Product LIMIT 10')
    master_data['products'] = [
        {'Product': row[0], 'ProductType': row[1], 'BaseUnit': row[2]}
        for row in cursor.fetchall()
    ]
    
    # Company Codes
    cursor.execute('SELECT CompanyCode, Currency FROM CompanyCode LIMIT 5')
    master_data['company_codes'] = [
        {'CompanyCode': row[0], 'Currency': row[1]}
        for row in cursor.fetchall()
    ]
    
    # Payment Terms
    cursor.execute('SELECT PaymentTerms FROM PaymentTerms LIMIT 5')
    master_data['payment_terms'] = [
        {'PaymentTerms': row[0]}
        for row in cursor.fetchall()
    ]
    
    return master_data


def clear_transactional_data(conn: sqlite3.Connection):
    """Clear existing transactional data"""
    cursor = conn.cursor()
    
    tables = [
        'JournalEntry', 'JournalEntryItemBillOfExchange',
        'ServiceEntrySheetItem', 'ServiceEntrySheet',
        'SupplierInvoiceItem', 'SupplierInvoice',
        'PurOrdSupplierConfirmation',
        'PurchaseOrderScheduleLine',
        'PurchaseOrderAccountAssignment',
        'PurchaseOrderItem',
        'PurchaseOrder'
    ]
    
    for table in tables:
        try:
            cursor.execute(f'DELETE FROM "{table}"')
            print(f"   ✅ Cleared {table}")
        except sqlite3.Error as e:
            print(f"   ⚠️  Could not clear {table}: {e}")
    
    conn.commit()


def generate_purchase_orders(conn: sqlite3.Connection, master_data: Dict, num_pos: int) -> List[Dict]:
    """Generate Purchase Orders"""
    cursor = conn.cursor()
    pos = []
    
    for i in range(1, num_pos + 1):
        po_id = f"4500{i:06d}"
        supplier = random.choice(master_data['suppliers'])
        company_code = random.choice(master_data['company_codes'])
        payment_term = random.choice(master_data['payment_terms'])
        po_date = BASE_DATE + timedelta(days=i*4)
        
        cursor.execute("""
            INSERT INTO PurchaseOrder (
                PurchaseOrder, Supplier, CompanyCode,
                PurchasingOrganization, PurchasingGroup,
                PurchaseOrderType, PurchaseOrderDate,
                DocumentCurrency, PaymentTerms,
                CreationDate, LastChangeDateTime,
                CreatedByUser
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            po_id, supplier['Supplier'], company_code['CompanyCode'],
            'P001', 'G01',
            'NB', po_date.strftime('%Y-%m-%d'),
            company_code['Currency'], payment_term['PaymentTerms'],
            po_date.strftime('%Y-%m-%d'), po_date.strftime('%Y-%m-%dT%H:%M:%S'),
            'BUYER01'
        ))
        
        pos.append({
            'PurchaseOrder': po_id,
            'Supplier': supplier['Supplier'],
            'CompanyCode': company_code['CompanyCode'],
            'Currency': company_code['Currency'],
            'Date': po_date
        })
    
    conn.commit()
    return pos


def generate_po_items(conn: sqlite3.Connection, pos: List[Dict], master_data: Dict) -> List[Dict]:
    """Generate PO Items"""
    cursor = conn.cursor()
    po_items = []
    
    for po in pos:
        # 2-3 items per PO
        num_items = random.randint(2, 3)
        products = random.sample(master_data['products'], min(num_items, len(master_data['products'])))
        
        for idx, product in enumerate(products, start=1):
            item_num = f"{idx*10:05d}"
            qty = float(random.randint(10, 500))
            price = float(random.randint(10, 500))
            net_amount = qty * price
            
            cursor.execute("""
                INSERT INTO PurchaseOrderItem (
                    PurchaseOrder, PurchaseOrderItem,
                    Supplier, CompanyCode,
                    Material, MaterialGroup,
                    OrderQuantity, PurchaseOrderQuantityUnit,
                    NetPriceAmount, NetAmount,
                    DocumentCurrency, Plant,
                    CreationDate, LastChangeDateTime,
                    IsCompletelyDelivered, IsFinallyInvoiced
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                po['PurchaseOrder'], item_num,
                po['Supplier'], po['CompanyCode'],
                product['Product'], 'MATGRP001',
                qty, product['BaseUnit'],
                price, net_amount,
                po['Currency'], 'P001',
                po['Date'].strftime('%Y-%m-%d'), po['Date'].strftime('%Y-%m-%dT%H:%M:%S'),
                1,  # IsCompletelyDelivered
                0   # IsFinallyInvoiced (will be updated later)
            ))
            
            po_items.append({
                'PurchaseOrder': po['PurchaseOrder'],
                'PurchaseOrderItem': item_num,
                'Supplier': po['Supplier'],
                'CompanyCode': po['CompanyCode'],
                'Currency': po['Currency'],
                'NetAmount': net_amount,
                'Date': po['Date']
            })
    
    conn.commit()
    return po_items


def generate_service_entry_sheets(conn: sqlite3.Connection, po_items: List[Dict]) -> int:
    """Generate Service Entry Sheets for 50% of POs"""
    cursor = conn.cursor()
    
    # Get unique POs
    pos_with_items = {}
    for item in po_items:
        po_id = item['PurchaseOrder']
        if po_id not in pos_with_items:
            pos_with_items[po_id] = []
        pos_with_items[po_id].append(item)
    
    # Create SES for half of the POs
    po_list = list(pos_with_items.keys())
    selected_pos = random.sample(po_list, len(po_list) // 2)
    
    ses_count = 0
    for i, po_id in enumerate(selected_pos, start=1):
        items = pos_with_items[po_id]
        first_item = items[0]
        
        ses_id = f"0100{i:06d}"
        ses_date = first_item['Date'] + timedelta(days=random.randint(5, 15))
        
        cursor.execute("""
            INSERT INTO ServiceEntrySheet (
                ServiceEntrySheet, ServiceEntrySheetName,
                PurchaseOrder, Supplier,
                PostingDate, CreationDateTime,
                ApprovalStatus, ApprovalDateTime,
                CreatedByUser
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            ses_id, f"Service Confirmation {ses_id}",
            po_id, first_item['Supplier'],
            ses_date.strftime('%Y-%m-%d'), ses_date.strftime('%Y-%m-%dT%H:%M:%S'),
            'APPROVED', (ses_date + timedelta(days=1)).strftime('%Y-%m-%dT%H:%M:%S'),
            'RECEIVER01'
        ))
        
        # Create SES items for each PO item
        for item in items:
            cursor.execute("""
                INSERT INTO ServiceEntrySheetItem (
                    ServiceEntrySheet, ServiceEntrySheetItem,
                    PurchaseOrder, PurchaseOrderItem,
                    QuantityUnit, ConfirmedQuantity
                ) VALUES (?, ?, ?, ?, ?, ?)
            """, (
                ses_id, item['PurchaseOrderItem'],
                po_id, item['PurchaseOrderItem'],
                'EA', 100.0
            ))
        
        ses_count += 1
    
    conn.commit()
    return ses_count


def generate_supplier_invoices(conn: sqlite3.Connection, po_items: List[Dict]) -> int:
    """Generate Supplier Invoices for 70% of PO items"""
    cursor = conn.cursor()
    
    # Get unique POs
    pos_with_items = {}
    for item in po_items:
        po_id = item['PurchaseOrder']
        if po_id not in pos_with_items:
            pos_with_items[po_id] = []
        pos_with_items[po_id].append(item)
    
    # Create invoices for 70% of POs
    po_list = list(pos_with_items.keys())
    selected_pos = random.sample(po_list, int(len(po_list) * 0.7))
    
    invoice_count = 0
    fiscal_year = str(datetime.now().year)
    
    for i, po_id in enumerate(selected_pos, start=1):
        items = pos_with_items[po_id]
        first_item = items[0]
        
        invoice_id = f"5100{i:06d}"
        invoice_date = first_item['Date'] + timedelta(days=random.randint(20, 40))
        
        # Calculate total amount
        total_amount = sum(item['NetAmount'] for item in items)
        
        cursor.execute("""
            INSERT INTO SupplierInvoice (
                SupplierInvoice, FiscalYear, CompanyCode,
                DocumentDate, PostingDate,
                InvoicingParty, IsInvoice,
                DocumentCurrency, InvoiceGrossAmount
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            invoice_id, fiscal_year, first_item['CompanyCode'],
            invoice_date.strftime('%Y-%m-%d'), invoice_date.strftime('%Y-%m-%d'),
            first_item['Supplier'], 1,
            first_item['Currency'], total_amount
        ))
        
        # Create invoice items
        for item in items:
            cursor.execute("""
                INSERT INTO SupplierInvoiceItem (
                    SupplierInvoice, FiscalYear, SupplierInvoiceItem,
                    PurchaseOrder, PurchaseOrderItem,
                    SupplierInvoiceItemAmount, DocumentCurrency,
                    CompanyCode, InvoicingParty,
                    DocumentDate, PostingDate
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                invoice_id, fiscal_year, item['PurchaseOrderItem'],
                po_id, item['PurchaseOrderItem'],
                item['NetAmount'], item['Currency'],
                item['CompanyCode'], item['Supplier'],
                invoice_date.strftime('%Y-%m-%d'), invoice_date.strftime('%Y-%m-%d')
            ))
            
            # Mark PO item as invoiced
            cursor.execute("""
                UPDATE PurchaseOrderItem
                SET IsFinallyInvoiced = 1
                WHERE PurchaseOrder = ? AND PurchaseOrderItem = ?
            """, (po_id, item['PurchaseOrderItem']))
        
        invoice_count += 1
    
    conn.commit()
    return invoice_count


def generate_journal_entries(conn: sqlite3.Connection) -> int:
    """Generate Journal Entries for invoices"""
    cursor = conn.cursor()
    
    # Get invoices
    cursor.execute("""
        SELECT SupplierInvoice, FiscalYear, CompanyCode, DocumentDate, InvoiceGrossAmount
        FROM SupplierInvoice
        ORDER BY DocumentDate
    """)
    
    invoices = cursor.fetchall()
    je_count = 0
    
    for i, (inv_id, fiscal_year, company_code, doc_date, amount) in enumerate(invoices, start=1):
        je_id = f"0190{i:06d}"
        
        cursor.execute("""
            INSERT INTO JournalEntry (
                CompanyCode, FiscalYear, AccountingDocument,
                AccountingDocumentType, DocumentDate, PostingDate,
                DocumentReferenceID, AccountingDocCreatedByUser,
                AccountingDocumentCreationDate
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            company_code, fiscal_year, je_id,
            'RE', doc_date, doc_date,
            inv_id, 'ACCOUNTANT01',
            doc_date
        ))
        
        je_count += 1
    
    conn.commit()
    return je_count


def print_summary(conn: sqlite3.Connection):
    """Print data summary"""
    cursor = conn.cursor()
    
    print("\n" + "="*80)
    print("DATA SUMMARY")
    print("="*80)
    
    print("\n📊 Master Data:")
    for table in ['Supplier', 'Product', 'CompanyCode', 'PaymentTerms']:
        cursor.execute(f'SELECT COUNT(*) FROM "{table}"')
        count = cursor.fetchone()[0]
        print(f"   {table}: {count} records")
    
    print("\n📦 Transactional Data:")
    trans_tables = [
        'PurchaseOrder', 'PurchaseOrderItem',
        'ServiceEntrySheet', 'ServiceEntrySheetItem',
        'SupplierInvoice', 'SupplierInvoiceItem',
        'JournalEntry'
    ]
    
    total_trans = 0
    for table in trans_tables:
        cursor.execute(f'SELECT COUNT(*) FROM "{table}"')
        count = cursor.fetchone()[0]
        total_trans += count
        status = "✅" if count > 0 else "⚠️"
        print(f"   {status} {table}: {count}")
    
    print(f"\n   📈 Total Transactional Records: {total_trans}")
    
    # Financial summary
    print(f"\n💰 Financial Summary:")
    cursor.execute('SELECT SUM(InvoiceGrossAmount) FROM SupplierInvoice')
    total_invoice = cursor.fetchone()[0] or 0
    
    cursor.execute('SELECT SUM(NetAmount) FROM PurchaseOrderItem')
    total_po = cursor.fetchone()[0] or 0
    
    print(f"   Total PO Value: {total_po:,.2f}")
    print(f"   Total Invoice Value: {total_invoice:,.2f}")
    print(f"   Coverage: {(total_invoice/total_po*100) if total_po > 0 else 0:.1f}%")


def main():
    """Main execution"""
    print("=" * 80)
    print("GENERATE P2P TRANSACTIONAL DATA")
    print("=" * 80)
    print(f"\nStrategy:")
    print(f"  1. Load master data from SQLite")
    print(f"  2. Generate {NUM_POS} Purchase Orders")
    print(f"  3. Generate PO Items (2-3 per PO)")
    print(f"  4. Generate Service Entry Sheets (50% of POs)")
    print(f"  5. Generate Supplier Invoices (70% of POs)")
    print(f"  6. Generate Journal Entries (for all invoices)")
    print()
    
    # Connect to SQLite
    print("💾 Connecting to SQLite...")
    try:
        conn = sqlite3.connect(SQLITE_DB)
        print(f"   ✅ Connected: {SQLITE_DB}")
    except Exception as e:
        print(f"   ❌ Connection failed: {e}")
        return 1
    
    # Load master data
    print("\n📋 Loading master data...")
    master_data = get_master_data(conn)
    print(f"   ✅ Loaded:")
    print(f"      Suppliers: {len(master_data['suppliers'])}")
    print(f"      Products: {len(master_data['products'])}")
    print(f"      Company Codes: {len(master_data['company_codes'])}")
    print(f"      Payment Terms: {len(master_data['payment_terms'])}")
    
    # Use synthetic data if master data is missing
    if not master_data['suppliers']:
        print("\n   ⚠️  No suppliers found, using synthetic data...")
        master_data['suppliers'] = [
            {'Supplier': f'SUP{i:07d}', 'SupplierName': f'Supplier {i}', 'Country': 'DE'}
            for i in range(1, 11)
        ]
        # Insert synthetic suppliers
        cursor = conn.cursor()
        for supplier in master_data['suppliers']:
            cursor.execute("""
                INSERT OR REPLACE INTO Supplier (Supplier, SupplierName, Country)
                VALUES (?, ?, ?)
            """, (supplier['Supplier'], supplier['SupplierName'], supplier['Country']))
        conn.commit()
        print(f"   ✅ Created 10 synthetic suppliers")
    
    if not master_data['products']:
        print("\n   ⚠️  No products found, using synthetic data...")
        master_data['products'] = [
            {'Product': f'PROD{i:06d}', 'ProductType': 'FERT', 'BaseUnit': 'EA'}
            for i in range(1, 11)
        ]
        # Insert synthetic products
        cursor = conn.cursor()
        for product in master_data['products']:
            cursor.execute("""
                INSERT OR REPLACE INTO Product (Product, ProductType, BaseUnit)
                VALUES (?, ?, ?)
            """, (product['Product'], product['ProductType'], product['BaseUnit']))
        conn.commit()
        print(f"   ✅ Created 10 synthetic products")
    
    # Clear existing transactional data
    print("\n🧹 Clearing existing transactional data...")
    clear_transactional_data(conn)
    
    # Generate data
    print("\n" + "="*80)
    print("GENERATING TRANSACTIONAL DATA")
    print("="*80)
    
    print(f"\n[1/5] Generating {NUM_POS} Purchase Orders...")
    pos = generate_purchase_orders(conn, master_data, NUM_POS)
    print(f"   ✅ Created {len(pos)} POs")
    
    print(f"\n[2/5] Generating PO Items...")
    po_items = generate_po_items(conn, pos, master_data)
    print(f"   ✅ Created {len(po_items)} PO items")
    
    print(f"\n[3/5] Generating Service Entry Sheets...")
    ses_count = generate_service_entry_sheets(conn, po_items)
    print(f"   ✅ Created {ses_count} Service Entry Sheets")
    
    print(f"\n[4/5] Generating Supplier Invoices...")
    invoice_count = generate_supplier_invoices(conn, po_items)
    print(f"   ✅ Created {invoice_count} Supplier Invoices")
    
    print(f"\n[5/5] Generating Journal Entries...")
    je_count = generate_journal_entries(conn)
    print(f"   ✅ Created {je_count} Journal Entries")
    
    # Summary
    print_summary(conn)
    
    conn.close()
    
    print("\n" + "="*80)
    print("✅ P2P TRANSACTIONAL DATA GENERATED")
    print("="*80)
    print(f"\nDatabase ready: {SQLITE_DB}")
    print(f"\nNext steps:")
    print(f"  1. Start server: python server.py")
    print(f"  2. Test via API Playground")
    print(f"  3. Verify P2P process flow")
    
    return 0


if __name__ == '__main__':
    sys.exit(main())