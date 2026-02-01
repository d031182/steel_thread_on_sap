#!/usr/bin/env python3
"""Comprehensive validation of all data products, tables, APIs, and data integrity"""

import sqlite3
import json
from pathlib import Path
from datetime import datetime

# Connect to database
db_path = 'app/database/p2p_data_products.db'
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

print("=" * 80)
print("COMPREHENSIVE DATA PRODUCTS VALIDATION")
print("=" * 80)
print(f"Database: {db_path}")
print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print()

# Load CSN files to get expected schema
csn_dir = Path('data-products')
csn_files = list(csn_dir.glob('*.json'))

print(f"Found {len(csn_files)} CSN files")
print()

# Track validation results
validation_results = {
    'total_products': 0,
    'products_with_data': 0,
    'products_empty': 0,
    'total_tables': 0,
    'tables_with_data': 0,
    'tables_empty': 0,
    'schema_issues': [],
    'data_issues': [],
    'warnings': []
}

# Get all tables in database
cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
all_tables = [row[0] for row in cursor.fetchall()]

print(f"Total tables in database: {len(all_tables)}")
print()

# Map of data products to their tables (EXACT names from CSN and database)
data_product_tables = {
    'SQLITE_PURCHASEORDER': [
        'PurchaseOrder',
        'PurchaseOrderItem', 
        'PurchaseOrderScheduleLine'
    ],
    'SQLITE_SUPPLIER': [
        'Supplier',
        'SupplierCompanyCode',
        'SupplierPurchasingOrganization',
        'SupplierWithHoldingTax'
    ],
    'SQLITE_SUPPLIERINVOICE': [
        'SupplierInvoice',
        'SupplierInvoiceItem'
    ],
    'SQLITE_SERVICEENTRYSHEET': [
        'ServiceEntrySheet',
        'ServiceEntrySheetItem'
    ],
    'SQLITE_PAYMENTTERMS': [
        'PaymentTerms',
        'PaymentTermsText'
    ],
    'SQLITE_JOURNALENTRYHEADER': [
        'JournalEntry',
        'JournalEntryItemBillOfExchange'
    ]
}

print("=" * 80)
print("DATA PRODUCT VALIDATION")
print("=" * 80)
print()

for product_name, tables in data_product_tables.items():
    validation_results['total_products'] += 1
    print(f"[PRODUCT] {product_name}")
    print(f"   Expected tables: {len(tables)}")
    
    product_has_data = False
    product_tables_found = 0
    product_tables_with_data = 0
    
    for table_name in tables:
        validation_results['total_tables'] += 1
        
        # Check if table exists
        if table_name not in all_tables:
            validation_results['schema_issues'].append(f"{product_name}: Table {table_name} missing")
            print(f"   [X] {table_name} - TABLE MISSING")
            continue
        
        product_tables_found += 1
        
        # Check row count
        cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
        row_count = cursor.fetchone()[0]
        
        if row_count > 0:
            validation_results['tables_with_data'] += 1
            product_tables_with_data += 1
            product_has_data = True
            print(f"   [OK] {table_name} - {row_count:,} records")
        else:
            validation_results['tables_empty'] += 1
            print(f"   [EMPTY] {table_name} - 0 records")
            validation_results['warnings'].append(f"{product_name}.{table_name} is empty")
    
    if product_has_data:
        validation_results['products_with_data'] += 1
    else:
        validation_results['products_empty'] += 1
    
    print(f"   Status: {product_tables_found}/{len(tables)} tables found, {product_tables_with_data} with data")
    print()

print("=" * 80)
print("SCHEMA VALIDATION (Key Columns)")
print("=" * 80)
print()

# Critical schema checks for key tables
schema_checks = {
    'PurchaseOrderScheduleLine': [
        ('PurchaseOrder', 'Key column 1'),
        ('PurchaseOrderItem', 'Key column 2'),
        ('PurchaseOrderScheduleLine', 'Key column 3 - EXACT HANA NAME'),
        ('ScheduleLineDeliveryDate', 'Delivery date'),
        ('ScheduleLineOrderQuantity', 'Order quantity')
    ],
    'PurchaseOrderItem': [
        ('PurchaseOrder', 'Key column 1'),
        ('PurchaseOrderItem', 'Key column 2'),
        ('Material', 'Material reference'),
        ('Plant', 'Plant reference')
    ],
    'SupplierInvoice': [
        ('SupplierInvoice', 'Key column'),
        ('FiscalYear', 'Fiscal year'),
        ('CompanyCode', 'Company code')
    ]
}

for table_name, expected_columns in schema_checks.items():
    if table_name not in all_tables:
        print(f"[X] {table_name} - TABLE MISSING")
        continue
    
    print(f"[CHECK] {table_name}")
    cursor.execute(f"PRAGMA table_info({table_name})")
    actual_columns = {row[1] for row in cursor.fetchall()}
    
    all_found = True
    for col_name, description in expected_columns:
        if col_name in actual_columns:
            print(f"   [OK] {col_name} - {description}")
        else:
            print(f"   [X] {col_name} - MISSING - {description}")
            validation_results['schema_issues'].append(f"{table_name}: Missing column {col_name}")
            all_found = False
    
    if all_found:
        print(f"   Schema: VALID [OK]")
    else:
        print(f"   Schema: ISSUES FOUND [X]")
    print()

print("=" * 80)
print("DATA INTEGRITY VALIDATION")
print("=" * 80)
print()

# Check referential integrity for Purchase Orders
if 'PurchaseOrder' in all_tables and 'PurchaseOrderItem' in all_tables:
    print("[RELATIONSHIP] Purchase Order -> Items")
    
    cursor.execute("SELECT COUNT(DISTINCT PurchaseOrder) FROM PurchaseOrder")
    po_count = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(DISTINCT PurchaseOrder) FROM PurchaseOrderItem")
    po_in_items = cursor.fetchone()[0]
    
    cursor.execute("""
        SELECT COUNT(*) FROM PurchaseOrderItem poi
        WHERE NOT EXISTS (
            SELECT 1 FROM PurchaseOrder po 
            WHERE po.PurchaseOrder = poi.PurchaseOrder
        )
    """)
    orphaned_items = cursor.fetchone()[0]
    
    print(f"   Purchase Orders: {po_count}")
    print(f"   POs with items: {po_in_items}")
    print(f"   Orphaned items: {orphaned_items}")
    
    if orphaned_items > 0:
        validation_results['data_issues'].append(f"Found {orphaned_items} orphaned PurchaseOrderItems")
        print(f"   Status: [X] Data integrity issue")
    else:
        print(f"   Status: [OK] Valid")
    print()

# Check Schedule Lines
if 'PurchaseOrderItem' in all_tables and 'PurchaseOrderScheduleLine' in all_tables:
    print("[RELATIONSHIP] Purchase Order Items -> Schedule Lines")
    
    cursor.execute("SELECT COUNT(*) FROM PurchaseOrderItem")
    item_count = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(DISTINCT PurchaseOrder || '-' || PurchaseOrderItem) FROM PurchaseOrderScheduleLine")
    items_with_schedule = cursor.fetchone()[0]
    
    cursor.execute("""
        SELECT COUNT(*) FROM PurchaseOrderScheduleLine psl
        WHERE NOT EXISTS (
            SELECT 1 FROM PurchaseOrderItem poi 
            WHERE poi.PurchaseOrder = psl.PurchaseOrder 
            AND poi.PurchaseOrderItem = psl.PurchaseOrderItem
        )
    """)
    orphaned_schedules = cursor.fetchone()[0]
    
    print(f"   Purchase Order Items: {item_count}")
    print(f"   Items with schedule lines: {items_with_schedule}")
    print(f"   Orphaned schedule lines: {orphaned_schedules}")
    
    if orphaned_schedules > 0:
        validation_results['data_issues'].append(f"Found {orphaned_schedules} orphaned PurchaseOrderScheduleLines")
        print(f"   Status: [X] Data integrity issue")
    else:
        print(f"   Status: [OK] Valid")
    print()

# Check Supplier Invoice relationships
if 'SupplierInvoice' in all_tables and 'SuplrInvcItemPurOrdRef' in all_tables:
    print("[RELATIONSHIP] Supplier Invoice -> Items")
    
    cursor.execute("SELECT COUNT(*) FROM SupplierInvoice")
    invoice_count = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM SuplrInvcItemPurOrdRef")
    invoice_items = cursor.fetchone()[0]
    
    print(f"   Supplier Invoices: {invoice_count}")
    print(f"   Invoice Items: {invoice_items}")
    
    if invoice_count > 0 and invoice_items == 0:
        validation_results['warnings'].append("Supplier Invoices exist but no items found")
        print(f"   Status: [WARN] Invoices without items")
    else:
        print(f"   Status: [OK] Valid")
    print()

print("=" * 80)
print("SUMMARY")
print("=" * 80)
print()

print(f"Data Products:")
print(f"  Total: {validation_results['total_products']}")
print(f"  With data: {validation_results['products_with_data']} [OK]")
print(f"  Empty: {validation_results['products_empty']} [WARN]")
print()

print(f"Tables:")
print(f"  Total: {validation_results['total_tables']}")
print(f"  With data: {validation_results['tables_with_data']} [OK]")
print(f"  Empty: {validation_results['tables_empty']} [WARN]")
print()

if validation_results['schema_issues']:
    print(f"Schema Issues: {len(validation_results['schema_issues'])} [X]")
    for issue in validation_results['schema_issues']:
        print(f"  - {issue}")
    print()

if validation_results['data_issues']:
    print(f"Data Integrity Issues: {len(validation_results['data_issues'])} [X]")
    for issue in validation_results['data_issues']:
        print(f"  - {issue}")
    print()

if validation_results['warnings']:
    print(f"Warnings: {len(validation_results['warnings'])} [WARN]")
    for warning in validation_results['warnings']:
        print(f"  - {warning}")
    print()

# Overall status
issues_count = len(validation_results['schema_issues']) + len(validation_results['data_issues'])
if issues_count == 0:
    print("Overall Status: [PASS] No critical issues")
else:
    print(f"Overall Status: [FAIL] {issues_count} critical issues found")

conn.close()

print()
print("=" * 80)
print("Validation complete!")
print("=" * 80)