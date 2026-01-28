#!/usr/bin/env python3
"""
Create Supplier Invoice Data Product in SQLite
Generates HANA-compatible SQLite schema and sample data

Usage: python scripts/python/create_supplier_invoice_sqlite.py
"""

import sqlite3
import json
import random
from datetime import datetime, timedelta
from pathlib import Path

# Paths
DB_PATH = Path("app/database/p2p_data_products.db")
CSN_PATH = Path("data-products/sap-s4com-SupplierInvoice-v1.en-complete.json")

# Ensure database directory exists
DB_PATH.parent.mkdir(parents=True, exist_ok=True)

def load_csn():
    """Load Supplier Invoice CSN definition"""
    with open(CSN_PATH, 'r', encoding='utf-8') as f:
        return json.load(f)

def map_cds_to_sqlite(cds_type, length=None, precision=None, scale=None):
    """Map CDS type to SQLite type"""
    if cds_type == 'cds.String':
        return 'TEXT'
    elif cds_type == 'cds.Decimal':
        return 'REAL'
    elif cds_type == 'cds.Integer':
        return 'INTEGER'
    elif cds_type in ['cds.Date', 'cds.DateTime', 'cds.Timestamp']:
        return 'TEXT'  # Store as ISO string
    elif cds_type == 'cds.Boolean':
        return 'INTEGER'  # 0/1
    elif cds_type == 'cds.Double':
        return 'REAL'
    else:
        return 'TEXT'  # Default

def generate_create_table_sql(entity_name, elements):
    """Generate CREATE TABLE statement from CSN elements"""
    lines = [f"CREATE TABLE IF NOT EXISTS {entity_name} ("]
    
    columns = []
    for field_name, field_def in elements.items():
        # Skip associations
        if field_def.get('type') == 'cds.Association':
            continue
        
        sqlite_type = map_cds_to_sqlite(
            field_def.get('type', 'cds.String'),
            field_def.get('length'),
            field_def.get('precision'),
            field_def.get('scale')
        )
        
        nullable = '' if field_def.get('key') else 'NULL'
        not_null = ' NOT NULL' if field_def.get('key') else ''
        
        columns.append(f"    {field_name} {sqlite_type}{not_null}")
    
    lines.append(',\n'.join(columns))
    lines.append(");")
    
    return '\n'.join(lines)

def create_tables(conn, csn):
    """Create SupplierInvoice and SupplierInvoiceItem tables"""
    cursor = conn.cursor()
    
    definitions = csn.get('definitions', {})
    
    # Create SupplierInvoice table
    if 'SupplierInvoice' in definitions:
        entity = definitions['SupplierInvoice']
        sql = generate_create_table_sql('SupplierInvoice', entity.get('elements', {}))
        print(f"Creating SupplierInvoice table...")
        cursor.execute(sql)
        print("[OK] SupplierInvoice table created")
    
    # Create SupplierInvoiceItem table
    if 'SupplierInvoiceItem' in definitions:
        entity = definitions['SupplierInvoiceItem']
        sql = generate_create_table_sql('SupplierInvoiceItem', entity.get('elements', {}))
        print(f"Creating SupplierInvoiceItem table...")
        cursor.execute(sql)
        print("[OK] SupplierInvoiceItem table created")
    
    conn.commit()

def generate_sample_data(conn):
    """Generate realistic sample data"""
    cursor = conn.cursor()
    
    # Sample data for SupplierInvoice (Header)
    invoices = []
    base_date = datetime.now() - timedelta(days=90)
    
    for i in range(1, 26):  # 25 invoices
        invoice_num = f"510000{i:04d}"
        fiscal_year = "2025"
        company_code = random.choice(["1010", "1020", "1030"])
        doc_date = (base_date + timedelta(days=random.randint(0, 90))).strftime('%Y-%m-%d')
        post_date = doc_date
        supplier = f"100{random.randint(1000, 9999)}"
        currency = "EUR"
        gross_amount = round(random.uniform(1000, 50000), 2)
        status = random.choice(["1", "2", "5"])  # 1=Defined, 2=Deleted, 5=Posted
        origin = random.choice(["1", "2", "4"])  # 1=Online, 2=ERS, 4=Batch
        
        invoices.append((
            invoice_num,
            fiscal_year,
            company_code,
            doc_date,
            post_date,
            f"INV-{invoice_num}",  # SupplierInvoiceIDByInvcgParty
            supplier,
            1,  # IsInvoice
            currency,
            gross_amount,
            0.0,  # SuplrInvcAutomReducedAmount
            round(random.uniform(0, 500), 2),  # UnplannedDeliveryCost
            f"Invoice for PO {random.randint(4500000000, 4599999999)}",  # DocumentHeaderText
            origin,
            0.0,  # SuplrInvcManuallyReducedAmount
            "V0",  # UnplannedDeliveryCostTaxCode
            status,
            "",  # ReverseDocument
            ""   # ReverseDocumentFiscalYear
        ))
    
    cursor.executemany("""
        INSERT INTO SupplierInvoice (
            SupplierInvoice, FiscalYear, CompanyCode, DocumentDate, PostingDate,
            SupplierInvoiceIDByInvcgParty, InvoicingParty, IsInvoice, DocumentCurrency,
            InvoiceGrossAmount, SuplrInvcAutomReducedAmount, UnplannedDeliveryCost,
            DocumentHeaderText, SupplierInvoiceOrigin, SuplrInvcManuallyReducedAmount,
            UnplannedDeliveryCostTaxCode, SupplierInvoiceStatus, ReverseDocument,
            ReverseDocumentFiscalYear
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, invoices)
    
    print(f"[OK] Inserted {len(invoices)} supplier invoice headers")
    
    # Sample data for SupplierInvoiceItem (Line Items)
    items = []
    for invoice_num, fiscal_year, company_code, doc_date, post_date, _, supplier, _, currency, _, _, _, _, origin, _, _, status, _, _ in invoices:
        num_items = random.randint(1, 5)
        for item_num in range(1, num_items + 1):
            po_num = f"450000{random.randint(1000, 9999)}"
            po_item = f"{random.randint(10, 90):05d}"
            material = f"MAT-{random.randint(1000, 9999)}"
            quantity = round(random.uniform(1, 100), 3)
            unit = "EA"
            amount = round(random.uniform(100, 5000), 2)
            plant = f"P{random.randint(100, 999)}"
            
            items.append((
                invoice_num,
                fiscal_year,
                f"{item_num:06d}",  # SupplierInvoiceItem
                quantity,  # QtyInPurchaseOrderPriceUnit
                unit,  # PurchaseOrderPriceUnit
                unit,  # PurchaseOrderQuantityUnit
                po_num,  # PurchaseOrder
                po_item,  # PurchaseOrderItem
                "",  # PrmtHbReferenceDocument
                "",  # PrmtHbReferenceDocumentFsclYr
                "",  # PrmtHbReferenceDocumentItem
                material,  # PurchaseOrderItemMaterial
                quantity,  # QuantityInPurchaseOrderUnit
                0,  # SuplrInvcItmHasQualityVariance
                0,  # SuplrInvcItemHasOrdPrcQtyVarc
                0,  # SuplrInvcItemHasQtyVariance
                0,  # SuplrInvcItemHasPriceVariance
                0,  # SuplrInvcItemHasOtherVariance
                0,  # SuplrInvcItemHasAmountOutsdTol
                0,  # SuplrInvcItemHasDateVariance
                "",  # IsSubsequentDebitCredit
                plant,  # Plant
                currency,  # DocumentCurrency
                amount,  # SupplierInvoiceItemAmount
                0.0,  # SuplrInvcAutomReducedAmount
                0.0,  # UnplannedDeliveryCost
                f"Item {item_num}",  # DocumentHeaderText
                doc_date,  # DocumentDate
                post_date,  # PostingDate
                company_code,  # CompanyCode
                origin,  # SupplierInvoiceOrigin
                supplier,  # InvoicingParty
                "",  # UnplannedDeliveryCostTaxCode
                "",  # ReverseDocument
                "",  # ReverseDocumentFiscalYear
                f"INV-{invoice_num}",  # SupplierInvoiceIDByInvcgParty
                1,  # IsInvoice
                status  # SupplierInvoiceStatus
            ))
    
    cursor.executemany("""
        INSERT INTO SupplierInvoiceItem (
            SupplierInvoice, FiscalYear, SupplierInvoiceItem,
            QtyInPurchaseOrderPriceUnit, PurchaseOrderPriceUnit, PurchaseOrderQuantityUnit,
            PurchaseOrder, PurchaseOrderItem, PrmtHbReferenceDocument,
            PrmtHbReferenceDocumentFsclYr, PrmtHbReferenceDocumentItem,
            PurchaseOrderItemMaterial, QuantityInPurchaseOrderUnit,
            SuplrInvcItmHasQualityVariance, SuplrInvcItemHasOrdPrcQtyVarc,
            SuplrInvcItemHasQtyVariance, SuplrInvcItemHasPriceVariance,
            SuplrInvcItemHasOtherVariance, SuplrInvcItemHasAmountOutsdTol,
            SuplrInvcItemHasDateVariance, IsSubsequentDebitCredit, Plant,
            DocumentCurrency, SupplierInvoiceItemAmount, SuplrInvcAutomReducedAmount,
            UnplannedDeliveryCost, DocumentHeaderText, DocumentDate, PostingDate,
            CompanyCode, SupplierInvoiceOrigin, InvoicingParty,
            UnplannedDeliveryCostTaxCode, ReverseDocument, ReverseDocumentFiscalYear,
            SupplierInvoiceIDByInvcgParty, IsInvoice, SupplierInvoiceStatus
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, items)
    
    print(f"[OK] Inserted {len(items)} supplier invoice line items")
    
    conn.commit()

def main():
    """Main execution"""
    print("=" * 80)
    print("Supplier Invoice SQLite Data Product Generator")
    print("=" * 80)
    print()
    
    # Load CSN
    print("Loading CSN definition...")
    csn = load_csn()
    print(f"[OK] CSN loaded: {len(csn.get('definitions', {}))} entities found")
    print()
    
    # Connect to SQLite
    print(f"Connecting to SQLite database: {DB_PATH}")
    conn = sqlite3.connect(DB_PATH)
    print("[OK] Connected")
    print()
    
    try:
        # Create tables
        create_tables(conn, csn)
        print()
        
        # Generate sample data
        print("Generating sample data...")
        generate_sample_data(conn)
        print()
        
        # Verify
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM SupplierInvoice")
        invoice_count = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM SupplierInvoiceItem")
        item_count = cursor.fetchone()[0]
        
        print("=" * 80)
        print("[SUCCESS]")
        print("=" * 80)
        print(f"Tables created: SupplierInvoice, SupplierInvoiceItem")
        print(f"Sample data: {invoice_count} invoices, {item_count} line items")
        print(f"Database: {DB_PATH}")
        print()
        print("Next steps:")
        print("1. Start the application: python server.py")
        print("2. Navigate to Data Products page")
        print("3. Select 'SQLite (Local)' as data source")
        print("4. View Supplier Invoice data")
        print("=" * 80)
        
    finally:
        conn.close()
        print("\n[OK] Database connection closed")

if __name__ == '__main__':
    main()