#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Populate SQLite Master Data from HANA Cloud

Extracts 10 records from each master data table in HANA Cloud
and inserts them into the corresponding SQLite tables.

Master data tables: 47 tables (excluding transactional tables like
PurchaseOrder, SupplierInvoice, ServiceEntrySheet, JournalEntry, etc.)

Usage: python scripts/python/populate_master_data_from_hana.py

Author: P2P Development Team
Version: 1.0.0
Date: 2026-02-08
"""

import sqlite3
import sys
import os
from pathlib import Path
from typing import List, Dict, Any, Tuple
from dotenv import load_dotenv

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from modules.hana_connection.backend.hana_connection import HANAConnection

# Fix Windows encoding
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Configuration
SQLITE_DB = "core/databases/sqlite/p2p_data.db"
RECORDS_PER_TABLE = 10

# Master data tables (47 tables - no transactional data)
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


def get_table_columns(sqlite_cursor, table_name: str) -> List[str]:
    """Get column names for a SQLite table"""
    sqlite_cursor.execute(f'PRAGMA table_info("{table_name}")')
    return [row[1] for row in sqlite_cursor.fetchall()]


def find_hana_table(hana_cursor, table_name: str) -> Tuple[str, str]:
    """Find the full HANA table name in Data Product schemas"""
    query = """
        SELECT SCHEMA_NAME, TABLE_NAME
        FROM TABLES
        WHERE SCHEMA_NAME LIKE '_SAP_DATAPRODUCT%'
        AND TABLE_NAME LIKE ?
    """
    hana_cursor.execute(query, (f'%.{table_name}',))
    result = hana_cursor.fetchone()
    
    if result:
        return result[0], result[1]
    return None, None


def extract_from_hana(hana_cursor, schema_name: str, table_name: str, columns: List[str], limit: int = 10) -> List[Tuple]:
    """Extract records from HANA table"""
    # Build column list
    col_list = ', '.join(f'"{col}"' for col in columns)
    
    # Query HANA
    query = f"""
        SELECT TOP {limit} {col_list}
        FROM "{schema_name}"."{table_name}"
    """
    
    try:
        hana_cursor.execute(query)
        return hana_cursor.fetchall()
    except Exception as e:
        print(f"         ⚠️  Query failed: {e}")
        return []


def insert_into_sqlite(sqlite_cursor, table_name: str, columns: List[str], records: List[Tuple]) -> int:
    """Insert records into SQLite table"""
    if not records:
        return 0
    
    # Build INSERT statement
    col_list = ', '.join(f'"{col}"' for col in columns)
    placeholders = ', '.join('?' * len(columns))
    
    insert_sql = f'INSERT OR REPLACE INTO "{table_name}" ({col_list}) VALUES ({placeholders})'
    
    # Insert all records
    inserted = 0
    for record in records:
        try:
            sqlite_cursor.execute(insert_sql, record)
            inserted += 1
        except sqlite3.Error as e:
            print(f"         ⚠️  Insert error: {e}")
    
    return inserted


def populate_table(
    hana_cursor,
    sqlite_cursor,
    table_name: str,
    limit: int = 10
) -> Tuple[bool, int]:
    """Populate a single table from HANA to SQLite"""
    
    # Get SQLite columns
    sqlite_cols = get_table_columns(sqlite_cursor, table_name)
    
    if not sqlite_cols:
        return False, 0
    
    # Find HANA table
    schema_name, hana_table_name = find_hana_table(hana_cursor, table_name)
    
    if not schema_name:
        print(f"      ⚠️  Table not found in HANA")
        return False, 0
    
    print(f"      Found: {schema_name}.{hana_table_name}")
    
    # Extract from HANA
    print(f"      Extracting {limit} records...")
    records = extract_from_hana(hana_cursor, schema_name, hana_table_name, sqlite_cols, limit)
    
    if not records:
        print(f"      ⚠️  No records extracted")
        return False, 0
    
    print(f"      ✅ Extracted {len(records)} records")
    
    # Insert into SQLite
    print(f"      Inserting into SQLite...")
    inserted = insert_into_sqlite(sqlite_cursor, table_name, sqlite_cols, records)
    
    print(f"      ✅ Inserted {inserted}/{len(records)} records")
    
    return True, inserted


def main():
    """Main execution"""
    print("=" * 80)
    print("POPULATE SQLITE MASTER DATA FROM HANA CLOUD")
    print("=" * 80)
    print(f"\nStrategy:")
    print(f"  - Extract {RECORDS_PER_TABLE} records per table from HANA")
    print(f"  - Master data tables: {len(MASTER_DATA_TABLES)} tables")
    print(f"  - Target: {SQLITE_DB}")
    print()
    
    # Connect to HANA
    print("🔌 Connecting to HANA Cloud...")
    try:
        load_dotenv('app/.env')
        
        hana_host = os.getenv('HANA_HOST')
        hana_port = int(os.getenv('HANA_PORT', 443))
        hana_user = os.getenv('HANA_USER')
        hana_password = os.getenv('HANA_PASSWORD')
        
        if not all([hana_host, hana_user, hana_password]):
            print("   ❌ HANA credentials not configured")
            return 1
        
        hana_manager = HANAConnection(hana_host, hana_port, hana_user, hana_password)
        if not hana_manager.connect():
            print("   ❌ Failed to connect to HANA")
            return 1
        
        hana_conn = hana_manager.connection
        print(f"   ✅ Connected to HANA Cloud")
        
    except Exception as e:
        print(f"   ❌ HANA connection error: {e}")
        return 1
    
    # Connect to SQLite
    print(f"\n💾 Connecting to SQLite...")
    try:
        sqlite_conn = sqlite3.connect(SQLITE_DB)
        print(f"   ✅ Connected: {SQLITE_DB}")
    except Exception as e:
        print(f"   ❌ SQLite connection failed: {e}")
        return 1
    
    # Populate tables
    print("\n" + "=" * 80)
    print(f"POPULATING {len(MASTER_DATA_TABLES)} MASTER DATA TABLES")
    print("=" * 80)
    
    hana_cursor = hana_conn.cursor()
    sqlite_cursor = sqlite_conn.cursor()
    
    tables_success = 0
    tables_failed = 0
    total_records = 0
    
    for i, table_name in enumerate(MASTER_DATA_TABLES, 1):
        print(f"\n  [{i}/{len(MASTER_DATA_TABLES)}] {table_name}")
        
        success, count = populate_table(hana_cursor, sqlite_cursor, table_name, RECORDS_PER_TABLE)
        
        if success:
            tables_success += 1
            total_records += count
            sqlite_conn.commit()
        else:
            tables_failed += 1
    
    # Summary
    print("\n" + "=" * 80)
    print("POPULATION SUMMARY")
    print("=" * 80)
    
    print(f"\n📊 Results:")
    print(f"   Tables processed: {len(MASTER_DATA_TABLES)}")
    print(f"   ✅ Success: {tables_success}")
    print(f"   ❌ Failed: {tables_failed}")
    print(f"   📈 Total records: {total_records}")
    
    # Close connections
    hana_manager.close()
    sqlite_conn.close()
    
    print("\n" + "=" * 80)
    if tables_failed == 0:
        print("✅ ALL TABLES POPULATED SUCCESSFULLY")
    else:
        print(f"⚠️  {tables_failed} TABLES FAILED")
    print("=" * 80)
    
    print(f"\nSQLite database ready:")
    print(f"  Location: {SQLITE_DB}")
    print(f"  Master data records: {total_records}")
    print(f"\nNext steps:")
    print(f"  1. Start server: python server.py")
    print(f"  2. Test via API Playground")
    
    return 0 if tables_failed == 0 else 1


if __name__ == '__main__':
    sys.exit(main())