#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Generate Complete Sample Data for ALL Data Products

This script generates realistic sample data for all 9 data products in SQLite,
WITHOUT requiring HANA connection. Perfect for:
- Local development and testing
- UI demonstrations
- Automated test data
- Offline work

Master data generated matches realistic SAP patterns for easy HANA substitution.

Usage: python scripts/python/generate_all_sample_data.py
"""

import sqlite3
import sys
from datetime import datetime, timedelta
from random import randint, choice, uniform
from faker import Faker

# Fix Windows encoding
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Configuration
SQLITE_DB = "app/database/p2p_data_products.db"
fake = Faker()

def generate_cost_center_data(conn):
    """Generate Cost Center master data (20 cost centers)"""
    print("\n[1/9] Generating Cost Center data...")
    cursor = conn.cursor()
    
    # Cost centers with realistic SAP hierarchy
    cost_centers = [
        {'id': 'CC1000', 'name': 'Production Planning', 'category': 'PRODUCTION', 'company': '1000'},
        {'id': 'CC1010', 'name': 'Manufacturing', 'category': 'PRODUCTION', 'company': '1000'},
        {'id': 'CC1020', 'name': 'Quality Control', 'category': 'PRODUCTION', 'company': '1000'},
        {'id': 'CC2000', 'name': 'Sales Management', 'category': 'SALES', 'company': '1000'},
        {'id': 'CC2010', 'name': 'Customer Service', 'category': 'SALES', 'company': '1000'},
        {'id': 'CC3000', 'name': 'IT Services', 'category': 'IT', 'company': '1000'},
        {'id': 'CC3010', 'name': 'IT Infrastructure', 'category': 'IT', 'company': '1000'},
        {'id': 'CC4000', 'name': 'Human Resources', 'category': 'HR', 'company': '1000'},
        {'id': 'CC4010', 'name': 'Training & Development', 'category': 'HR', 'company': '1000'},
        {'id': 'CC5000', 'name': 'Finance & Accounting', 'category': 'FINANCE', 'company': '1000'},
        {'id': 'CC5010', 'name': 'Controlling', 'category': 'FINANCE', 'company': '1000'},
        {'id': 'CC6000', 'name': 'Procurement', 'category': 'PROCUREMENT', 'company': '1000'},
        {'id': 'CC6010', 'name': 'Supplier Management', 'category': 'PROCUREMENT', 'company': '1000'},
        {'id': 'CC7000', 'name': 'Logistics', 'category': 'LOGISTICS', 'company': '1000'},
        {'id': 'CC7010', 'name': 'Warehouse Management', 'category': 'LOGISTICS', 'company': '1000'},
        {'id': 'CC8000', 'name': 'Research & Development', 'category': 'RD', 'company': '1000'},
        {'id': 'CC8010', 'name': 'Innovation Lab', 'category': 'RD', 'company': '1000'},
        {'id': 'CC9000', 'name': 'Marketing', 'category': 'MARKETING', 'company': '1000'},
        {'id': 'CC9010', 'name': 'Brand Management', 'category': 'MARKETING', 'company': '1000'},
        {'id': 'CC9020', 'name': 'Digital Marketing', 'category': 'MARKETING', 'company': '1000'}
    ]
    
    # Insert Cost Centers
    for cc in cost_centers:
        cursor.execute("""
            INSERT OR REPLACE INTO CostCenter 
            (CostCenter, CostCenterName, ControllingArea, CompanyCode, ValidityStartDate, ValidityEndDate)
            VALUES (?, ?, '1000', ?, '2024-01-01', '9999-12-31')
        """, (cc['id'], cc['name'], cc['company']))
    
    print(f"  ✓ Created {len(cost_centers)} cost centers")
    
    # Cost Center Text (descriptions in English)
    for cc in cost_centers:
        cursor.execute("""
            INSERT OR REPLACE INTO CostCenterText
            (CostCenter, Language, CostCenterName, CostCenterDescription)
            VALUES (?, 'EN', ?, ?)
        """, (cc['id'], cc['name'], f"Description for {cc['name']}"))
    
    print(f"  ✓ Created {len(cost_centers)} cost center texts")
    
    conn.commit()
    print("  [OK] Cost Center data complete")

def generate_company_code_data(conn):
    """Generate Company Code master data (5 companies)"""
    print("\n[2/9] Generating Company Code data...")
    cursor = conn.cursor()
    
    companies = [
        {'code': '1000', 'name': 'SAP AG', 'city': 'Walldorf', 'country': 'DE', 'currency': 'EUR'},
        {'code': '1010', 'name': 'SAP America', 'city': 'Newtown Square', 'country': 'US', 'currency': 'USD'},
        {'code': '1020', 'name': 'SAP UK', 'city': 'London', 'country': 'GB', 'currency': 'GBP'},
        {'code': '1030', 'name': 'SAP France', 'city': 'Paris', 'country': 'FR', 'currency': 'EUR'},
        {'code': '1040', 'name': 'SAP Asia Pacific', 'city': 'Singapore', 'country': 'SG', 'currency': 'SGD'}
    ]
    
    for co in companies:
        cursor.execute("""
            INSERT OR REPLACE INTO CompanyCode
            (CompanyCode, CompanyCodeName, CityName, Country, Currency)
            VALUES (?, ?, ?, ?, ?)
        """, (co['code'], co['name'], co['city'], co['country'], co['currency']))
    
    print(f"  ✓ Created {len(companies)} company codes")
    
    # Company Code Text
    for co in companies:
        cursor.execute("""
            INSERT OR REPLACE INTO CompanyCodeText
            (CompanyCode, Language, CompanyCodeName)
            VALUES (?, 'EN', ?)
        """, (co['code'], co['name']))
    
    print(f"  ✓ Created {len(companies)} company code texts")
    
    conn.commit()
    print("  [OK] Company Code data complete")

def generate_product_data(conn):
    """Generate Product master data (50 products)"""
    print("\n[3/9] Generating Product data...")
    cursor = conn.cursor()
    
    # Product categories
    categories = [
        ('RAW', 'Raw Materials'),
        ('FERT', 'Finished Goods'),
        ('HALB', 'Semi-Finished'),
        ('HAWA', 'Trading Goods'),
        ('DIEN', 'Services')
    ]
    
    products = []
    for i in range(1, 51):
        cat = choice(categories)
        products.append({
            'id': f"P{1000 + i}",
            'name': f"{cat[1]} Product {i}",
            'type': cat[0],
            'unit': choice(['PC', 'KG', 'L', 'M', 'EA']),
            'price': round(uniform(10.0, 500.0), 2)
        })
    
    for prod in products:
        cursor.execute("""
            INSERT OR REPLACE INTO Product
            (Product, ProductName, ProductType, BaseUnit, NetWeight, GrossWeight)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (prod['id'], prod['name'], prod['type'], prod['unit'], 
              round(uniform(1.0, 50.0), 2), round(uniform(1.5, 60.0), 2)))
    
    print(f"  ✓ Created {len(products)} products")
    
    conn.commit()
    print("  [OK] Product data complete")

def check_and_generate_journal_entry(conn):
    """Check and generate Journal Entry data if needed"""
    print("\n[4/9] Checking Journal Entry data...")
    cursor = conn.cursor()
    
    cursor.execute("SELECT COUNT(*) FROM JournalEntry")
    count = cursor.fetchone()[0]
    
    if count > 0:
        print(f"  ✓ Already has {count} records - SKIPPING")
        return
    
    print("  Generating Journal Entry sample data...")
    
    # Generate 50 journal entries
    for i in range(1, 51):
        entry_id = f"JE{2024}{i:05d}"
        cursor.execute("""
            INSERT OR REPLACE INTO JournalEntry
            (AccountingDocument, CompanyCode, FiscalYear, AccountingDocumentType, 
             DocumentDate, PostingDate, AccountingDocumentHeaderText)
            VALUES (?, '1000', '2024', 'SA', ?, ?, ?)
        """, (entry_id, datetime(2024, randint(1, 12), randint(1, 28)).strftime('%Y-%m-%d'),
              datetime(2024, randint(1, 12), randint(1, 28)).strftime('%Y-%m-%d'),
              f"Journal Entry {i}"))
    
    print(f"  ✓ Created 50 journal entries")
    conn.commit()

def check_and_generate_payment_terms(conn):
    """Check and generate Payment Terms data if needed"""
    print("\n[5/9] Checking Payment Terms data...")
    cursor = conn.cursor()
    
    cursor.execute("SELECT COUNT(*) FROM PaymentTerms")
    count = cursor.fetchone()[0]
    
    if count > 0:
        print(f"  ✓ Already has {count} records - SKIPPING")
        return
    
    print("  Generating Payment Terms sample data...")
    
    terms = [
        ('Z001', 'Net 30 Days', 30),
        ('Z002', 'Net 60 Days', 60),
        ('Z003', 'Net 90 Days', 90),
        ('Z010', 'Immediate Payment', 0),
        ('Z020', 'Net 45 Days with 2% Discount', 45)
    ]
    
    for term in terms:
        cursor.execute("""
            INSERT OR REPLACE INTO PaymentTerms
            (PaymentTerms, CashDiscount1Days, CashDiscount1Percent, CashDiscount2Days, CashDiscount2Percent, NetPaymentDays)
            VALUES (?, 10, 2.0, 30, 1.0, ?)
        """, (term[0], term[2]))
        
        cursor.execute("""
            INSERT OR REPLACE INTO PaymentTermsText
            (PaymentTerms, Language, PaymentTermsName, PaymentTermsDescription)
            VALUES (?, 'EN', ?, ?)
        """, (term[0], term[1], f"Description for {term[1]}"))
    
    print(f"  ✓ Created {len(terms)} payment terms")
    conn.commit()

def check_and_generate_service_entry(conn):
    """Check and generate Service Entry Sheet data if needed"""
    print("\n[6/9] Checking Service Entry Sheet data...")
    cursor = conn.cursor()
    
    cursor.execute("SELECT COUNT(*) FROM ServiceEntrySheet")
    count = cursor.fetchone()[0]
    
    if count > 0:
        print(f"  ✓ Already has {count} records - SKIPPING")
        return
    
    print("  Generating Service Entry Sheet sample data...")
    
    # Generate 30 service entry sheets
    for i in range(1, 31):
        ses_id = f"SES{2024}{i:05d}"
        cursor.execute("""
            INSERT OR REPLACE INTO ServiceEntrySheet
            (ServiceEntrySheet, PurchaseOrder, PurchaseOrderItem, ServiceEntrySheetStatus)
            VALUES (?, ?, ?, ?)
        """, (ses_id, f"PO{4500000000 + i}", '10', choice(['APPROVED', 'PENDING', 'COMPLETED'])))
    
    print(f"  ✓ Created 30 service entry sheets")
    conn.commit()

def check_and_generate_supplier(conn):
    """Check and generate Supplier data if needed"""
    print("\n[7/9] Checking Supplier data...")
    cursor = conn.cursor()
    
    cursor.execute("SELECT COUNT(*) FROM Supplier")
    count = cursor.fetchone()[0]
    
    if count > 0:
        print(f"  ✓ Already has {count} records - SKIPPING")
        return
    
    print("  Generating Supplier sample data...")
    
    # Generate 50 suppliers
    for i in range(1, 51):
        supplier_id = f"SUP{10000 + i}"
        cursor.execute("""
            INSERT OR REPLACE INTO Supplier
            (Supplier, SupplierName, SupplierFullName, CreationDate, OrganizationBPName1, 
             OrganizationBPName2, CityName, PostalCode, StreetName, Country, Region, PhoneNumber1, FaxNumber)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (supplier_id, f"Supplier {i}", f"Supplier Company {i} GmbH",
              (datetime.now() - timedelta(days=randint(30, 365))).strftime('%Y-%m-%d'),
              f"Supplier {i}", "GmbH", fake.city(), fake.postcode(), 
              fake.street_address(), choice(['DE', 'US', 'GB', 'FR', 'CN']),
              fake.state_abbr() if i % 2 == 0 else None, 
              fake.phone_number(), fake.phone_number()))
    
    print(f"  ✓ Created 50 suppliers")
    conn.commit()

def check_and_generate_purchase_order(conn):
    """Check and generate Purchase Order data if needed"""
    print("\n[8/9] Checking Purchase Order data...")
    cursor = conn.cursor()
    
    cursor.execute("SELECT COUNT(*) FROM PurchaseOrder")
    count = cursor.fetchone()[0]
    
    if count > 0:
        print(f"  ✓ Already has {count} records - SKIPPING")
        return
    
    print("  Generating Purchase Order sample data...")
    
    # Generate 30 purchase orders
    for i in range(1, 31):
        po_number = f"PO{4500000000 + i}"
        supplier_id = f"SUP{10000 + randint(1, 50)}"
        
        cursor.execute("""
            INSERT OR REPLACE INTO PurchaseOrder
            (PurchaseOrder, PurchaseOrderType, Supplier, CompanyCode, PurchasingOrganization,
             PurchasingGroup, CreationDate, CreatedByUser, DocumentCurrency, PaymentTerms)
            VALUES (?, 'NB', ?, '1000', '1000', '001', ?, 'BUYER01', 'EUR', 'Z001')
        """, (po_number, supplier_id, 
              (datetime.now() - timedelta(days=randint(1, 90))).strftime('%Y-%m-%d')))
    
    print(f"  ✓ Created 30 purchase orders")
    conn.commit()

def check_and_generate_supplier_invoice(conn):
    """Check and generate Supplier Invoice data if needed"""
    print("\n[9/9] Checking Supplier Invoice data...")
    cursor = conn.cursor()
    
    cursor.execute("SELECT COUNT(*) FROM SupplierInvoice")
    count = cursor.fetchone()[0]
    
    if count > 0:
        print(f"  ✓ Already has {count} records - SKIPPING")
        return
    
    print("  Generating Supplier Invoice sample data...")
    
    # Generate 25 supplier invoices
    for i in range(1, 26):
        invoice_id = f"INV{2024}{i:05d}"
        supplier_id = f"SUP{10000 + randint(1, 50)}"
        po_number = f"PO{4500000000 + randint(1, 30)}"
        
        cursor.execute("""
            INSERT OR REPLACE INTO SupplierInvoice
            (SupplierInvoice, FiscalYear, CompanyCode, DocumentDate, PostingDate,
             SupplierInvoiceIDByInvcgParty, InvoicingParty, DocumentCurrency, InvoiceGrossAmount)
            VALUES (?, '2024', '1000', ?, ?, ?, ?, 'EUR', ?)
        """, (invoice_id,
              (datetime.now() - timedelta(days=randint(1, 60))).strftime('%Y-%m-%d'),
              (datetime.now() - timedelta(days=randint(1, 60))).strftime('%Y-%m-%d'),
              f"SI-{i:05d}", supplier_id, round(uniform(1000.0, 50000.0), 2)))
    
    print(f"  ✓ Created 25 supplier invoices")
    conn.commit()

def verify_all_data(conn):
    """Verify all data products have data"""
    print("\n" + "="*80)
    print("DATA VERIFICATION")
    print("="*80)
    
    cursor = conn.cursor()
    
    # All main tables across 9 data products
    tables_to_check = [
        ('CostCenter', 'Cost Center'),
        ('CostCenterText', 'Cost Center'),
        ('CompanyCode', 'Company Code'),
        ('CompanyCodeText', 'Company Code'),
        ('Product', 'Product'),
        ('JournalEntry', 'Journal Entry'),
        ('PaymentTerms', 'Payment Terms'),
        ('PaymentTermsText', 'Payment Terms'),
        ('ServiceEntrySheet', 'Service Entry Sheet'),
        ('Supplier', 'Supplier'),
        ('PurchaseOrder', 'Purchase Order'),
        ('SupplierInvoice', 'Supplier Invoice')
    ]
    
    print("\nRecord Counts by Data Product:")
    current_product = None
    total_records = 0
    
    for table, product in tables_to_check:
        if product != current_product:
            if current_product:
                print()  # Blank line between products
            print(f"\n{product}:")
            current_product = product
        
        try:
            cursor.execute(f"SELECT COUNT(*) FROM {table}")
            count = cursor.fetchone()[0]
            status = "✓" if count > 0 else "✗"
            print(f"  {status} {table}: {count} records")
            total_records += count
        except Exception as e:
            print(f"  ✗ {table}: [ERROR] {e}")
    
    print("\n" + "="*80)
    print(f"TOTAL RECORDS: {total_records}")
    print("="*80)
    
    # Check for empty tables
    empty_count = 0
    for table, _ in tables_to_check:
        try:
            cursor.execute(f"SELECT COUNT(*) FROM {table}")
            if cursor.fetchone()[0] == 0:
                empty_count += 1
        except:
            pass
    
    if empty_count == 0:
        print("\n✓ SUCCESS: All main tables have data!")
    else:
        print(f"\n⚠ WARNING: {empty_count} tables still empty")
    
    return empty_count == 0

def main():
    """Main data generation process"""
    print("="*80)
    print("Generate Complete Sample Data for ALL Data Products")
    print("="*80)
    print(f"\nTarget Database: {SQLITE_DB}")
    print("Strategy: Generate realistic SAP sample data WITHOUT HANA")
    print()
    
    try:
        # Install faker if not available
        try:
            import faker
        except ImportError:
            print("Installing faker library...")
            import subprocess
            subprocess.check_call([sys.executable, "-m", "pip", "install", "faker", "-q"])
            print("  ✓ faker installed\n")
        
        conn = sqlite3.connect(SQLITE_DB)
        
        # Generate all data products
        generate_cost_center_data(conn)
        generate_company_code_data(conn)
        generate_product_data(conn)
        check_and_generate_journal_entry(conn)
        check_and_generate_payment_terms(conn)
        check_and_generate_service_entry(conn)
        check_and_generate_supplier(conn)
        check_and_generate_purchase_order(conn)
        check_and_generate_supplier_invoice(conn)
        
        # Verify
        success = verify_all_data(conn)
        
        conn.close()
        
        if success:
            print("\n✓ ALL DATA GENERATION COMPLETE!")
            print("\nNext steps:")
            print("  1. Refresh UI: Click 'Load Data' button")
            print("  2. All 9 data products should now show data")
            print("  3. Cost Center, Company Code, Product now populated!")
            return 0
        else:
            print("\n⚠ Some tables still empty - check errors above")
            return 1
        
    except Exception as e:
        print(f"\n[ERROR] Data generation failed: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == '__main__':
    sys.exit(main())