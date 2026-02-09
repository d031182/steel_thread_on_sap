#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Populate SQLite from HANA Master Data + Generate Transactions

Phase 1: Extract 10 master data records from HANA Cloud
  - 10 Suppliers
  - 10 Products  
  - CompanyCode records
  - PaymentTerms records

Phase 2: Generate realistic end-to-end transactional data
  - Purchase Orders (linked to Suppliers)
  - Purchase Order Items (linked to Products)
  - Supplier Invoices (linked to POs)
  - Service Entry Sheets (linked to POs)
  - Journal Entries (financial records)

All transactions reuse extracted master data for consistency.

Usage: python scripts/python/populate_from_hana_master_data.py

Author: P2P Development Team
Version: 1.0.0
"""

import sqlite3
import sys
import os
from datetime import datetime, timedelta
from typing import List, Dict, Any
from pathlib import Path
from dotenv import load_dotenv

# Add project root to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

from modules.hana_connection.backend import HANAConnection

# Fix Windows encoding
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Configuration
SQLITE_DB = "core/databases/sqlite/p2p_data.db"
MASTER_DATA_LIMIT = 10  # Extract 10 records of each master data type

# Master data tables (vs transactional tables)
MASTER_DATA_TABLES = [
    'CompanyCode', 'CompanyCodeCurrencyRole', 'CompanyCodeCurrencyTranslation',
    'CompanyCodeHierarchy', 'CompanyCodeHierarchyNode', 'CompanyCodeHierarchyNodeText',
    'CompanyCodeHierarchyText',
    'CostCenter', 'CostCenterCategory', 'CostCenterCategoryText',
    'CostCenterHierarchy', 'CostCenterHierarchyNode', 'CostCenterHierarchyNodeText',
    'CostCenterHierarchyText', 'CostCenterText',
    'CurrencyRole', 'CurrencyRoleText',
    'PaymentTerms', 'PaymentTermsConditions', 'PaymentTermsConditionsText', 'PaymentTermsText',
    'Product', 'ProductGroup', 'ProductGroupText', 'ProductDescription',
    'ProductConsumption', 'ProductProcurement', 'ProductQualityManagement',
    'ProductSales', 'ProductSalesDelivery', 'ProductStorage',
    'ProductUnitOfMeasure', 'ProductUnitOfMeasureEAN',
    'ProductValuation', 'ProductValuationAccounting', 'ProductValuationCosting',
    'ProductWarehouseManagement',
    'ProductPlant', 'ProductPlantCosting', 'ProductPlantForecast',
    'ProductPlantInternationalTrade', 'ProductPlantProcurement',
    'ProductPlantPurchaseTax', 'ProductPlantQualityManagement',
    'ProductPlantStorage', 'ProductPlantSupplyPlanning', 'ProductPlantWorkScheduling',
    'ProductMRPArea',
    'ProdIntlTradeClassification', 'ProdWhseManagementStorageType',
    'Supplier', 'SupplierCompanyCode', 'SupplierPurchasingOrganization',
    'SupplierWithHoldingTax'
]


def extract_master_data_from_hana(cursor) -> Dict[str, List[Dict[str, Any]]]:
    """Extract 10 master data records from HANA Cloud"""
    print("\n" + "="*80)
    print("PHASE 1: EXTRACT MASTER DATA FROM HANA CLOUD")
    print("="*80)
    
    master_data = {}
    
    # 1. Extract Suppliers
    print(f"\n[1/4] Extracting {MASTER_DATA_LIMIT} Suppliers from HANA...")
    try:
        cursor.execute(f"""
            SELECT TOP {MASTER_DATA_LIMIT}
                "Supplier",
                "SupplierName",
                "SupplierFullName",
                "Country",
                "CityName",
                "SupplierAccountGroup",
                "PurchasingIsBlocked",
                "CreationDate"
            FROM "Supplier"
            WHERE "SupplierName" IS NOT NULL
            ORDER BY "Supplier"
        """)
        
        suppliers = []
        for row in cursor.fetchall():
            suppliers.append({
                'Supplier': row[0],
                'SupplierName': row[1],
                'SupplierFullName': row[2],
                'Country': row[3],
                'CityName': row[4],
                'SupplierAccountGroup': row[5],
                'PurchasingIsBlocked': row[6],
                'CreationDate': row[7]
            })
        
        master_data['suppliers'] = suppliers
        print(f"   ✅ Extracted {len(suppliers)} suppliers")
        
    except Exception as e:
        print(f"   ⚠️  HANA query failed: {e}")
        print(f"   Using fallback synthetic suppliers...")
        master_data['suppliers'] = generate_synthetic_suppliers()
    
    # 2. Extract Products
    print(f"\n[2/4] Extracting {MASTER_DATA_LIMIT} Products from HANA...")
    try:
        cursor.execute(f"""
            SELECT TOP {MASTER_DATA_LIMIT}
                "Product",
                "ProductType",
                "ProductGroup",
                "BaseUnit",
                "WeightUnit",
                "CreationDate"
            FROM "Product"
            WHERE "Product" IS NOT NULL
            ORDER BY "Product"
        """)
        
        products = []
        for row in cursor.fetchall():
            products.append({
                'Product': row[0],
                'ProductType': row[1],
                'ProductGroup': row[2],
                'BaseUnit': row[3],
                'WeightUnit': row[4],
                'CreationDate': row[5]
            })
        
        master_data['products'] = products
        print(f"   ✅ Extracted {len(products)} products")
        
    except Exception as e:
        print(f"   ⚠️  HANA query failed: {e}")
        print(f"   Using fallback synthetic products...")
        master_data['products'] = generate_synthetic_products()
    
    # 3. Extract CompanyCodes
    print(f"\n[3/4] Extracting CompanyCodes from HANA...")
    try:
        cursor.execute(f"""
            SELECT TOP {MASTER_DATA_LIMIT}
                "CompanyCode",
                "CompanyCodeName",
                "Country",
                "CityName",
                "Currency",
                "Language"
            FROM "CompanyCode"
            WHERE "CompanyCode" IS NOT NULL
            ORDER BY "CompanyCode"
        """)
        
        company_codes = []
        for row in cursor.fetchall():
            company_codes.append({
                'CompanyCode': row[0],
                'CompanyCodeName': row[1],
                'Country': row[2],
                'CityName': row[3],
                'Currency': row[4],
                'Language': row[5]
            })
        
        master_data['company_codes'] = company_codes
        print(f"   ✅ Extracted {len(company_codes)} company codes")
        
    except Exception as e:
        print(f"   ⚠️  HANA query failed: {e}")
        print(f"   Using fallback synthetic company codes...")
        master_data['company_codes'] = generate_synthetic_company_codes()
    
    # 4. Extract PaymentTerms
    print(f"\n[4/4] Extracting PaymentTerms from HANA...")
    try:
        cursor.execute(f"""
            SELECT TOP {MASTER_DATA_LIMIT}
                "PaymentTerms"
            FROM "PaymentTerms"
            WHERE "PaymentTerms" IS NOT NULL
            ORDER BY "PaymentTerms"
        """)
        
        payment_terms = []
        for row in cursor.fetchall():
            payment_terms.append({
                'PaymentTerms': row[0]
            })
        
        master_data['payment_terms'] = payment_terms
        print(f"   ✅ Extracted {len(payment_terms)} payment terms")
        
    except Exception as e:
        print(f"   ⚠️  HANA query failed: {e}")
        print(f"   Using fallback synthetic payment terms...")
        master_data['payment_terms'] = generate_synthetic_payment_terms()
    
    return master_data


def generate_synthetic_suppliers() -> List[Dict[str, Any]]:
    """Fallback: Generate synthetic suppliers if HANA extraction fails"""
    return [
        {'Supplier': '0000100001', 'SupplierName': 'Global Tech Solutions GmbH', 'SupplierFullName': 'Global Tech Solutions GmbH Corp', 'Country': 'DE', 'CityName': 'Munich', 'SupplierAccountGroup': 'CRED', 'PurchasingIsBlocked': 0, 'CreationDate': '2025-01-01'},
        {'Supplier': '0000100002', 'SupplierName': 'Enterprise Software AG', 'SupplierFullName': 'Enterprise Software AG Corp', 'Country': 'DE', 'CityName': 'Berlin', 'SupplierAccountGroup': 'CRED', 'PurchasingIsBlocked': 0, 'CreationDate': '2025-01-01'},
        {'Supplier': '0000100003', 'SupplierName': 'Cloud Services Ltd', 'SupplierFullName': 'Cloud Services Ltd Corp', 'Country': 'GB', 'CityName': 'London', 'SupplierAccountGroup': 'CRED', 'PurchasingIsBlocked': 0, 'CreationDate': '2025-01-01'},
        {'Supplier': '0000100004', 'SupplierName': 'Data Systems Corp', 'SupplierFullName': 'Data Systems Corp', 'Country': 'US', 'CityName': 'New York', 'SupplierAccountGroup': 'CRED', 'PurchasingIsBlocked': 0, 'CreationDate': '2025-01-01'},
        {'Supplier': '0000100005', 'SupplierName': 'Innovation Partners SAS', 'SupplierFullName': 'Innovation Partners SAS Corp', 'Country': 'FR', 'CityName': 'Paris', 'SupplierAccountGroup': 'CRED', 'PurchasingIsBlocked': 0, 'CreationDate': '2025-01-01'},
        {'Supplier': '0000100006', 'SupplierName': 'Quality Goods BV', 'SupplierFullName': 'Quality Goods BV Corp', 'Country': 'NL', 'CityName': 'Amsterdam', 'SupplierAccountGroup': 'CRED', 'PurchasingIsBlocked': 0, 'CreationDate': '2025-01-01'},
        {'Supplier': '0000100007', 'SupplierName': 'Precision Mfg SpA', 'SupplierFullName': 'Precision Mfg SpA Corp', 'Country': 'IT', 'CityName': 'Milan', 'SupplierAccountGroup': 'CRED', 'PurchasingIsBlocked': 0, 'CreationDate': '2025-01-01'},
        {'Supplier': '0000100008', 'SupplierName': 'Digital Solutions AB', 'SupplierFullName': 'Digital Solutions AB Corp', 'Country': 'SE', 'CityName': 'Stockholm', 'SupplierAccountGroup': 'CRED', 'PurchasingIsBlocked': 0, 'CreationDate': '2025-01-01'},
        {'Supplier': '0000100009', 'SupplierName': 'Smart Logistics SA', 'SupplierFullName': 'Smart Logistics SA Corp', 'Country': 'ES', 'CityName': 'Madrid', 'SupplierAccountGroup': 'CRED', 'PurchasingIsBlocked': 0, 'CreationDate': '2025-01-01'},
        {'Supplier': '0000100010', 'SupplierName': 'Future Tech KK', 'SupplierFullName': 'Future Tech KK Corp', 'Country': 'JP', 'CityName': 'Tokyo', 'SupplierAccountGroup': 'CRED', 'PurchasingIsBlocked': 0, 'CreationDate': '2025-01-01'}
    ]


def generate_synthetic_products() -> List[Dict[str, Any]]:
    """Fallback: Generate synthetic products if HANA extraction fails"""
    return [
        {'Product': 'PROD000001', 'ProductType': 'FERT', 'ProductGroup': 'MATGRP001', 'BaseUnit': 'EA', 'WeightUnit': 'KG', 'CreationDate': '2025-01-01'},
        {'Product': 'PROD000002', 'ProductType': 'FERT', 'ProductGroup': 'MATGRP001', 'BaseUnit': 'EA', 'WeightUnit': 'KG', 'CreationDate': '2025-01-01'},
        {'Product': 'PROD000003', 'ProductType': 'FERT', 'ProductGroup': 'MATGRP002', 'BaseUnit': 'EA', 'WeightUnit': 'KG', 'CreationDate': '2025-01-01'},
        {'Product': 'PROD000004', 'ProductType': 'FERT', 'ProductGroup': 'MATGRP002', 'BaseUnit': 'EA', 'WeightUnit': 'KG', 'CreationDate': '2025-01-01'},
        {'Product': 'PROD000005', 'ProductType': 'FERT', 'ProductGroup': 'MATGRP003', 'BaseUnit': 'EA', 'WeightUnit': 'KG', 'CreationDate': '2025-01-01'},
        {'Product': 'PROD000006', 'ProductType': 'FERT', 'ProductGroup': 'MATGRP003', 'BaseUnit': 'EA', 'WeightUnit': 'KG', 'CreationDate': '2025-01-01'},
        {'Product': 'PROD000007', 'ProductType': 'FERT', 'ProductGroup': 'MATGRP004', 'BaseUnit': 'EA', 'WeightUnit': 'KG', 'CreationDate': '2025-01-01'},
        {'Product': 'PROD000008', 'ProductType': 'FERT', 'ProductGroup': 'MATGRP004', 'BaseUnit': 'EA', 'WeightUnit': 'KG', 'CreationDate': '2025-01-01'},
        {'Product': 'PROD000009', 'ProductType': 'FERT', 'ProductGroup': 'MATGRP005', 'BaseUnit': 'EA', 'WeightUnit': 'KG', 'CreationDate': '2025-01-01'},
        {'Product': 'PROD000010', 'ProductType': 'FERT', 'ProductGroup': 'MATGRP005', 'BaseUnit': 'EA', 'WeightUnit': 'KG', 'CreationDate': '2025-01-01'}
    ]


def generate_synthetic_company_codes() -> List[Dict[str, Any]]:
    """Fallback: Generate synthetic company codes if HANA extraction fails"""
    return [
        {'CompanyCode': '1010', 'CompanyCodeName': 'SAP SE', 'Country': 'DE', 'CityName': 'Walldorf', 'Currency': 'EUR', 'Language': 'EN'},
        {'CompanyCode': '2000', 'CompanyCodeName': 'SAP Labs US', 'Country': 'US', 'CityName': 'Palo Alto', 'Currency': 'USD', 'Language': 'EN'}
    ]


def generate_synthetic_payment_terms() -> List[Dict[str, Any]]:
    """Fallback: Generate synthetic payment terms if HANA extraction fails"""
    return [
        {'PaymentTerms': 'Z001'},
        {'PaymentTerms': 'Z002'},
        {'PaymentTerms': 'Z003'},
        {'PaymentTerms': 'Z004'},
        {'PaymentTerms': 'Z005'}
    ]


def insert_master_data(sqlite_conn: sqlite3.Connection, master_data: Dict[str, List[Dict[str, Any]]]) -> None:
    """Insert extracted master data into SQLite"""
    print("\n" + "="*80)
    print("INSERTING MASTER DATA INTO SQLITE")
    print("="*80)
    
    cursor = sqlite_conn.cursor()
    
    # 1. Suppliers
    print(f"\n[1/4] Inserting {len(master_data['suppliers'])} Suppliers...")
    for supplier in master_data['suppliers']:
        cursor.execute("""
            INSERT OR REPLACE INTO Supplier (
                Supplier, SupplierName, SupplierFullName,
                Country, CityName, SupplierAccountGroup,
                PurchasingIsBlocked, CreationDate
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            supplier['Supplier'],
            supplier['SupplierName'],
            supplier['SupplierFullName'],
            supplier['Country'],
            supplier['CityName'],
            supplier['SupplierAccountGroup'],
            supplier['PurchasingIsBlocked'],
            supplier['CreationDate']
        ))
    print(f"   ✅ Inserted {len(master_data['suppliers'])} suppliers")
    
    # 2. Products
    print(f"\n[2/4] Inserting {len(master_data['products'])} Products...")
    for product in master_data['products']:
        cursor.execute("""
            INSERT OR REPLACE INTO Product (
                Product, ProductType, ProductGroup,
                BaseUnit, WeightUnit, CreationDate
            ) VALUES (?, ?, ?, ?, ?, ?)
        """, (
            product['Product'],
            product['ProductType'],
            product['ProductGroup'],
            product['BaseUnit'],
            product['WeightUnit'],
            product['CreationDate']
        ))
    print(f"   ✅ Inserted {len(master_data['products'])} products")
    
    # 3. CompanyCodes
    print(f"\n[3/4] Inserting {len(master_data['company_codes'])} CompanyCodes...")
    for cc in master_data['company_codes']:
        cursor.execute("""
            INSERT OR REPLACE INTO CompanyCode (
                CompanyCode, CompanyCodeName, Country,
                CityName, Currency, Language
            ) VALUES (?, ?, ?, ?, ?, ?)
        """, (
            cc['CompanyCode'],
            cc['CompanyCodeName'],
            cc['Country'],
            cc['CityName'],
            cc['Currency'],
            cc['Language']
        ))
    print(f"   ✅ Inserted {len(master_data['company_codes'])} company codes")
    
    # 4. PaymentTerms
    print(f"\n[4/4] Inserting {len(master_data['payment_terms'])} PaymentTerms...")
    for pt in master_data['payment_terms']:
        cursor.execute("""
            INSERT OR REPLACE INTO PaymentTerms (PaymentTerms)
            VALUES (?)
        """, (pt['PaymentTerms'],))
    print(f"   ✅ Inserted {len(master_data['payment_terms'])} payment terms")
    
    sqlite_conn.commit()


def generate_transactional_data(
    sqlite_conn: sqlite3.Connection,
    master_data: Dict[str, List[Dict[str, Any]]]
) -> None:
    """Generate realistic end-to-end transactional data using master data"""
    print("\n" + "="*80)
    print("PHASE 2: GENERATE TRANSACTIONAL DATA")
    print("="*80)
    
    cursor = sqlite_conn.cursor()
    base_date = datetime.now() - timedelta(days=90)
    
    suppliers = master_data['suppliers']
    products = master_data['products']
    company_code = master_data['company_codes'][0]['CompanyCode']
    currency = master_data['company_codes'][0]['Currency']
    
    # 1. Purchase Orders (20 POs)
    print(f"\n[1/4] Generating 20 Purchase Orders...")
    po_ids = []
    
    for i in range(1, 21):
        po_id = f"4500{i:06d}"
        supplier = suppliers[(i-1) % len(suppliers)]
        payment_term = master_data['payment_terms'][(i-1) % len(master_data['payment_terms'])]
        po_date = base_date + timedelta(days=i*4)
        
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
            po_id, supplier['Supplier'], company_code,
            'P001', 'G01',
            'NB', po_date.strftime('%Y-%m-%d'),
            currency, payment_term['PaymentTerms'],
            po_date.strftime('%Y-%m-%d'), po_date.strftime('%Y-%m-%dT%H:%M:%S'),
            'BUYER01'
        ))
        
        po_ids.append((po_id, supplier['Supplier']))
        
        # Add 2 PO items per PO (using extracted products)
        for item_seq, product in enumerate(products[:2], start=1):
            item_num = item_seq * 10
            qty = 100.0 * item_seq
            price = 50.00 + (item_seq * 10)
            
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
                po_id, f"{item_num:05d}",
                supplier['Supplier'], company_code,
                product['Product'], product['ProductGroup'],
                qty, product['BaseUnit'],
                price, qty * price,
                currency, 'P001',
                po_date.strftime('%Y-%m-%d'), po_date.strftime('%Y-%m-%dT%H:%M:%S'),
                1 if i <= 12 else 0,
                1 if i <= 10 else 0
            ))
    
    sqlite_conn.commit()
    print(f"   ✅ Created 20 POs with 40 items")
    
    # 2. Supplier Invoices (30 invoices for first 15 POs)
    print(f"\n[2/4] Generating 30 Supplier Invoices...")
    invoice_count = 0
    
    for i, (po_id, supplier_id) in enumerate(po_ids[:15]):
        for inv_seq in [1, 2]:
            invoice_id = f"5100{invoice_count+1:06d}"
            fiscal_year = str(datetime.now().year)
            invoice_date = base_date + timedelta(days=(i*4)+20+(inv_seq*10))
            
            cursor.execute("""
                INSERT INTO SupplierInvoice (
                    SupplierInvoice, FiscalYear, CompanyCode,
                    DocumentDate, PostingDate,
                    InvoicingParty, IsInvoice,
                    DocumentCurrency, InvoiceGrossAmount
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                invoice_id, fiscal_year, company_code,
                invoice_date.strftime('%Y-%m-%d'), invoice_date.strftime('%Y-%m-%d'),
                supplier_id, 1,
                currency, 5000.00 + (i * 100)
            ))
            
            # Invoice item
            cursor.execute("""
                INSERT INTO SupplierInvoiceItem (
                    SupplierInvoice, FiscalYear, SupplierInvoiceItem,
                    PurchaseOrder, PurchaseOrderItem,
                    SupplierInvoiceItemAmount, DocumentCurrency,
                    CompanyCode, InvoicingParty,
                    DocumentDate, PostingDate
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                invoice_id, fiscal_year, '000001',
                po_id, '00010',
                5000.00 + (i * 100), currency,
                company_code, supplier_id,
                invoice_date.strftime('%Y-%m-%d'), invoice_date.strftime('%Y-%m-%d')
            ))
            
            invoice_count += 1
    
    sqlite_conn.commit()
    print(f"   ✅ Created {invoice_count} invoices with {invoice_count} items")
    
    # 3. Service Entry Sheets (10 SES for first 10 POs)
    print(f"\n[3/4] Generating 10 Service Entry Sheets...")
    ses_count = 0
    
    for i, (po_id, supplier_id) in enumerate(po_ids[:10]):
        ses_id = f"0100{i+1:06d}"
        ses_date = base_date + timedelta(days=i*4+10)
        
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
            po_id, supplier_id,
            ses_date.strftime('%Y-%m-%d'), ses_date.strftime('%Y-%m-%dT%H:%M:%S'),
            'APPROVED', (ses_date + timedelta(days=1)).strftime('%Y-%m-%dT%H:%M:%S'),
            'BUYER01'
        ))
        
        # SES Item
        cursor.execute("""
            INSERT INTO ServiceEntrySheetItem (
                ServiceEntrySheet, ServiceEntrySheetItem,
                PurchaseOrder, PurchaseOrderItem,
                QuantityUnit, ConfirmedQuantity
            ) VALUES (?, ?, ?, ?, ?, ?)
        """, (
            ses_id, '000001',
            po_id, '00010',
            'EA', 100.0
        ))
        
        ses_count += 1
    
    sqlite_conn.commit()
    print(f"   ✅ Created {ses_count} service entry sheets with {ses_count} items")
    
    # 4. Journal Entries (Financial records for first 10 invoices)
    print(f"\n[4/4] Generating 10 Journal Entries...")
    cursor.execute("""
        SELECT SupplierInvoice, FiscalYear, InvoiceGrossAmount, DocumentDate
        FROM SupplierInvoice
        ORDER BY SupplierInvoice
        LIMIT 10
    """)
    
    invoices_for_je = cursor.fetchall()
    je_count = 0
    
    for inv_id, fiscal_year, amount, doc_date in invoices_for_je:
        je_id = f"0190{je_count+1:06d}"
        
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
    
    sqlite_conn.commit()
    print(f"   ✅ Created {je_count} journal entries")


def print_summary(sqlite_conn: sqlite3.Connection) -> None:
    """Print population summary"""
    print("\n" + "="*80)
    print("POPULATION SUMMARY")
    print("="*80)
    
    cursor = sqlite_conn.cursor()
    
    tables = [
        'Supplier', 'Product', 'CompanyCode', 'PaymentTerms',
        'PurchaseOrder', 'PurchaseOrderItem',
        'SupplierInvoice', 'SupplierInvoiceItem',
        'ServiceEntrySheet', 'ServiceEntrySheetItem',
        'JournalEntry'
    ]
    
    print("\n📊 Record Counts:")
    total_records = 0
    
    for table in tables:
        try:
            cursor.execute(f'SELECT COUNT(*) FROM "{table}"')
            count = cursor.fetchone()[0]
            total_records += count
            
            status = "✅" if count > 0 else "⚠️"
            print(f"   {status} {table}: {count}")
            
        except sqlite3.Error:
            print(f"   ⚠️  {table}: Table not found")
    
    print(f"\n   📈 Total Records: {total_records}")
    
    # Financial summary
    print(f"\n💰 Financial Summary:")
    try:
        cursor.execute('SELECT SUM("InvoiceGrossAmount") FROM "SupplierInvoice"')
        total_invoice = cursor.fetchone()[0] or 0
        
        cursor.execute('SELECT SUM("NetAmount") FROM "PurchaseOrderItem"')
        total_po = cursor.fetchone()[0] or 0
        
        print(f"   Total PO Value: {total_po:,.2f}")
        print(f"   Total Invoice Value: {total_invoice:,.2f}")
        
    except sqlite3.Error as e:
        print(f"   ⚠️  Could not calculate financials: {e}")


def main():
    """Main execution"""
    print("="*80)
    print("POPULATE SQLITE FROM HANA MASTER DATA")
    print("="*80)
    print("\nStrategy:")
    print("  Phase 1: Extract 10 master data records from HANA")
    print("  Phase 2: Generate realistic transactions using master data")
    print()
    
    # Check .env for HANA credentials
    load_dotenv('app/.env')
    
    # Phase 1: Extract from HANA
    master_data = None
    
    try:
        print("Connecting to HANA Cloud...")
        
        # Get HANA credentials from environment
        hana_host = os.getenv('HANA_HOST')
        hana_port = os.getenv('HANA_PORT', '443')
        hana_user = os.getenv('HANA_USER')
        hana_password = os.getenv('HANA_PASSWORD')
        
        if not all([hana_host, hana_user, hana_password]):
            raise ValueError("Missing HANA credentials in environment variables")
        
        # Create connection
        hana_manager = HANAConnection(hana_host, int(hana_port), hana_user, hana_password)
        if not hana_manager.connect():
            raise Exception("HANA connection failed")
        
        print("   ✅ HANA Connected")
        
        master_data = extract_master_data_from_hana(hana_manager.connection.cursor())
        
        hana_manager.close()
        print("\n   ✅ HANA Extraction Complete")
        
    except Exception as e:
        print(f"\n   ⚠️  HANA connection failed: {e}")
        print(f"   Using synthetic fallback data...")
        
        master_data = {
            'suppliers': generate_synthetic_suppliers(),
            'products': generate_synthetic_products(),
            'company_codes': generate_synthetic_company_codes(),
            'payment_terms': generate_synthetic_payment_terms()
        }
    
    # Phase 2: Insert into SQLite and generate transactions
    print(f"\n💾 Connecting to SQLite: {SQLITE_DB}")
    
    try:
        sqlite_conn = sqlite3.connect(SQLITE_DB)
        print(f"   ✅ SQLite Connected")
        
        # Clear existing transactional data (keep structure)
        print(f"\n🧹 Clearing existing transactional data...")
        cursor = sqlite_conn.cursor()
        tables_to_clear = [
            'JournalEntry', 'ServiceEntrySheetItem', 'ServiceEntrySheet',
            'SupplierInvoiceItem', 'SupplierInvoice',
            'PurchaseOrderItem', 'PurchaseOrder',
            'PaymentTerms', 'CompanyCode', 'Product', 'Supplier'
        ]
        for table in tables_to_clear:
            try:
                cursor.execute(f'DELETE FROM "{table}"')
                print(f"   ✅ Cleared {table}")
            except sqlite3.Error as e:
                print(f"   ⚠️  Could not clear {table}: {e}")
        
        sqlite_conn.commit()
        print(f"   ✅ Database cleared")
        
        # Insert master data
        insert_master_data(sqlite_conn, master_data)
        
        # Generate transactional data
        generate_transactional_data(sqlite_conn, master_data)
        
        # Print summary
        print_summary(sqlite_conn)
        
        sqlite_conn.close()
        
        print("\n" + "="*80)
        print("✅ POPULATION COMPLETE")
        print("="*80)
        print(f"\nDatabase ready: {SQLITE_DB}")
        print("\nNext steps:")
        print("  1. Start server: python server.py")
        print("  2. Test via API Playground")
        print("  3. Verify data integrity")
        
        return 0
        
    except Exception as e:
        print(f"\n❌ SQLite error: {e}")
        return 1


if __name__ == '__main__':
    sys.exit(main())