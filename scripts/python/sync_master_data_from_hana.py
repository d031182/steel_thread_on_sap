#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sync Master Data from HANA Cloud to SQLite

This script:
1. Connects to HANA Cloud to fetch actual master data
2. Extracts key master data (Supplier, Product, Company Code, Cost Center)
3. Populates SQLite with the same master data
4. Ensures referential integrity (matching IDs)

This makes SQLite a true fallback with consistent data for testing.

Usage: python scripts/python/sync_master_data_from_hana.py
"""

import requests
import sqlite3
import json
from typing import List, Dict
import sys

# Fix Windows encoding
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Configuration
BASE_URL = "http://localhost:5000/api"
SQLITE_DB = "app/database/p2p_data_products.db"

def fetch_hana_data(schema: str, table: str, limit: int = 1000) -> List[Dict]:
    """Fetch data from HANA Cloud table"""
    print(f"  Fetching {table} from HANA...")
    
    # Use correct API endpoint with POST and source parameter
    url = f"{BASE_URL}/data-products/{schema}/{table}/query?source=hana"
    
    try:
        response = requests.post(
            url,
            json={"limit": limit, "offset": 0},
            headers={'Content-Type': 'application/json'}
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                rows = data.get('rows', [])
                print(f"    Retrieved {len(rows)} records")
                return rows
            else:
                print(f"    [ERROR] API returned error: {data.get('error')}")
                return []
        else:
            print(f"    [ERROR] Failed to fetch: {response.status_code}")
            return []
    except Exception as e:
        print(f"    [ERROR] Request failed: {e}")
        return []

def get_table_columns(cursor, table_name: str) -> List[str]:
    """Get column names for a table"""
    cursor.execute(f"PRAGMA table_info({table_name})")
    return [row[1] for row in cursor.fetchall()]

def insert_data(cursor, table_name: str, rows: List[Dict]):
    """Insert data into SQLite table"""
    if not rows:
        print(f"    No data to insert")
        return
    
    # Get table columns
    columns = get_table_columns(cursor, table_name)
    
    # Filter row data to only include columns that exist in table
    filtered_rows = []
    for row in rows:
        filtered_row = {k: v for k, v in row.items() if k in columns}
        filtered_rows.append(filtered_row)
    
    if not filtered_rows:
        print(f"    No matching columns found")
        return
    
    # Build insert statement
    first_row = filtered_rows[0]
    cols = list(first_row.keys())
    placeholders = ','.join(['?' for _ in cols])
    col_names = ','.join(cols)
    
    insert_sql = f"INSERT OR REPLACE INTO {table_name} ({col_names}) VALUES ({placeholders})"
    
    # Insert all rows
    inserted = 0
    for row in filtered_rows:
        values = [row.get(col) for col in cols]
        try:
            cursor.execute(insert_sql, values)
            inserted += 1
        except Exception as e:
            print(f"    [WARN] Failed to insert row: {e}")
    
    print(f"    Inserted {inserted}/{len(filtered_rows)} records")

def sync_supplier_data(conn):
    """Sync Supplier master data from HANA"""
    print("\n[1/4] Syncing Supplier Data...")
    
    cursor = conn.cursor()
    
    # Supplier schema name
    schema = "_SAP_DATAPRODUCT_sap_s4com_dataProduct_Supplier_v1_a54ad0f0-63e7-40c0-9aab-3c4bde45caff"
    
    # Fetch and insert Supplier
    table_prefix = "_SAP_DATAPRODUCT_27e9b543-ceae-4e76-8ba0-05c7c4276590_supplier"
    
    supplier_data = fetch_hana_data(schema, f"{table_prefix}.Supplier", limit=500)
    if supplier_data:
        insert_data(cursor, "Supplier", supplier_data)
    
    # Fetch and insert SupplierCompanyCode
    company_data = fetch_hana_data(schema, f"{table_prefix}.SupplierCompanyCode", limit=500)
    if company_data:
        insert_data(cursor, "SupplierCompanyCode", company_data)
    
    # Fetch and insert SupplierPurchasingOrganization
    purch_data = fetch_hana_data(schema, f"{table_prefix}.SupplierPurchasingOrganization", limit=500)
    if purch_data:
        insert_data(cursor, "SupplierPurchasingOrganization", purch_data)
    
    # Fetch and insert SupplierWithHoldingTax
    tax_data = fetch_hana_data(schema, f"{table_prefix}.SupplierWithHoldingTax", limit=500)
    if tax_data:
        insert_data(cursor, "SupplierWithHoldingTax", tax_data)
    
    conn.commit()
    print("  [OK] Supplier data synced")

def sync_product_data(conn):
    """Sync Product master data from HANA (if tables exist in SQLite)"""
    print("\n[2/4] Syncing Product Data...")
    
    # Check if Product tables exist in SQLite
    cursor = conn.cursor()
    cursor.execute("""
        SELECT name FROM sqlite_master 
        WHERE type='table' AND name LIKE 'Product%'
    """)
    
    if not cursor.fetchall():
        print("  [SKIP] Product tables don't exist in SQLite yet")
        print("  [INFO] Run create_all_data_products.py to create Product schema first")
        return
    
    schema = "_SAP_DATAPRODUCT_sap_s4com_dataProduct_Product_v1_7f798906-cc0b-45fb-b138-7bacc1e87969"
    table_prefix = "_SAP_DATAPRODUCT_69fa1e0f-38b7-48db-9ff3-3ee7a1035c3a_product"
    
    # Note: Product has 29 entities - we'll sync the main ones
    product_data = fetch_hana_data(schema, f"{table_prefix}.Product", limit=500)
    if product_data:
        insert_data(cursor, "Product", product_data)
    
    conn.commit()
    print("  [OK] Product data synced")

def sync_company_code_data(conn):
    """Sync Company Code master data from HANA (if tables exist in SQLite)"""
    print("\n[3/4] Syncing Company Code Data...")
    
    # Check if CompanyCode tables exist in SQLite
    cursor = conn.cursor()
    cursor.execute("""
        SELECT name FROM sqlite_master 
        WHERE type='table' AND name LIKE 'CompanyCode%'
    """)
    
    if not cursor.fetchall():
        print("  [SKIP] CompanyCode tables don't exist in SQLite yet")
        print("  [INFO] Run create_all_data_products.py to create CompanyCode schema first")
        return
    
    schema = "_SAP_DATAPRODUCT_sap_s4com_dataProduct_CompanyCode_v1_645851fc-9f81-4bba-b245-65819a82e521"
    table_prefix = "_SAP_DATAPRODUCT_c28ee30d-4fa1-46a0-83cd-b5e4bc1e1f32_companycode"
    
    company_data = fetch_hana_data(schema, f"{table_prefix}.CompanyCode", limit=500)
    if company_data:
        insert_data(cursor, "CompanyCode", company_data)
    
    conn.commit()
    print("  [OK] Company Code data synced")

def sync_cost_center_data(conn):
    """Sync Cost Center master data from HANA (if tables exist in SQLite)"""
    print("\n[4/4] Syncing Cost Center Data...")
    
    # Check if CostCenter tables exist in SQLite
    cursor = conn.cursor()
    cursor.execute("""
        SELECT name FROM sqlite_master 
        WHERE type='table' AND name LIKE 'CostCenter%'
    """)
    
    if not cursor.fetchall():
        print("  [SKIP] CostCenter tables don't exist in SQLite yet")
        print("  [INFO] Run create_all_data_products.py to create CostCenter schema first")
        return
    
    schema = "_SAP_DATAPRODUCT_sap_s4com_dataProduct_CostCenter_v1_5dd836b0-1fc4-428b-b176-2cf8951e932b"
    table_prefix = "_SAP_DATAPRODUCT_9c8ad0d9-b826-4d2a-a735-c66ce36a99c3_costcenter"
    
    cost_center_data = fetch_hana_data(schema, f"{table_prefix}.CostCenter", limit=500)
    if cost_center_data:
        insert_data(cursor, "CostCenter", cost_center_data)
    
    conn.commit()
    print("  [OK] Cost Center data synced")

def main():
    """Main sync process"""
    print("="*80)
    print("Sync Master Data from HANA Cloud to SQLite")
    print("="*80)
    print(f"\nTarget Database: {SQLITE_DB}")
    print(f"Source: HANA Cloud via {BASE_URL}")
    print()
    
    try:
        # Connect to SQLite
        conn = sqlite3.connect(SQLITE_DB)
        
        # Sync master data
        sync_supplier_data(conn)
        sync_product_data(conn)
        sync_company_code_data(conn)
        sync_cost_center_data(conn)
        
        # Summary
        print("\n" + "="*80)
        print("SYNC SUMMARY")
        print("="*80)
        
        cursor = conn.cursor()
        
        # Count records
        tables = ['Supplier', 'SupplierCompanyCode', 'SupplierPurchasingOrganization', 
                 'SupplierWithHoldingTax', 'Product', 'CompanyCode', 'CostCenter']
        
        print("\nRecord Counts:")
        for table in tables:
            try:
                cursor.execute(f"SELECT COUNT(*) FROM {table}")
                count = cursor.fetchone()[0]
                print(f"  {table}: {count} records")
            except:
                print(f"  {table}: [table not found]")
        
        conn.close()
        
        print("\n[OK] Master data sync complete!")
        print("\nNext steps:")
        print("  1. Run validation: python scripts/python/validate_sqlite_vs_hana_schemas.py")
        print("  2. Test in UI: Switch to 'SQLite (Local)' data source")
        print("  3. SQLite is now a true fallback with HANA master data!")
        
    except Exception as e:
        print(f"\n[ERROR] Sync failed: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0

if __name__ == '__main__':
    sys.exit(main())