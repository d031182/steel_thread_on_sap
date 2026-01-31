#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Rebuild SQLite Database with Primary Keys from CSN Files

Uses CSN metadata (docs/csn/*.json) to rebuild SQLite tables with proper
PRIMARY KEY constraints, without requiring HANA Cloud access.

Usage: python scripts/python/rebuild_sqlite_from_csn.py
"""

import sqlite3
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

from core.services.csn_parser import CSNParser

# Fix Windows encoding
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

SQLITE_DB = "app/database/p2p_data_products.db"
CSN_DIR = "docs/csn"

# Entity name to SQLite table name mapping
ENTITY_TO_TABLE = {
    'PurchaseOrder': 'C_PurchaseOrderDEX',
    'PurchaseOrderItem': 'C_PurchaseOrderItemDEX',
    'Supplier': 'C_SupplierDEX',
    'SupplierInvoice': 'C_SupplierInvoiceDEX',
    'SupplierInvoiceItem': 'C_SuplrInvcItemPurOrdRefDEX',
    'JournalEntry': 'C_JournalEntryDEX',
    'PaymentTerms': 'C_PaymentTermsDEX',
    'ServiceEntrySheet': 'C_ServiceEntrySheetDEX',
    'Product': 'C_ProductDEX',
    'CompanyCode': 'C_CompanyCodeDEX',
    'CostCenter': 'C_CostCenterDEX',
}

def csn_type_to_sqlite(csn_type: str, length: int = None) -> str:
    """Convert CSN/CDS type to SQLite type"""
    if not csn_type:
        return 'TEXT'
    
    csn_type_lower = csn_type.lower()
    
    # String types
    if 'string' in csn_type_lower or csn_type_lower in ['cds.string']:
        return 'TEXT'
    
    # Integer types
    if 'int' in csn_type_lower or csn_type_lower in ['cds.integer', 'cds.integer64']:
        return 'INTEGER'
    
    # Decimal types
    if 'decimal' in csn_type_lower or csn_type_lower in ['cds.decimal', 'cds.decimalfloat']:
        return 'REAL'
    
    # Date/time types
    if any(x in csn_type_lower for x in ['date', 'time', 'timestamp']):
        return 'TEXT'
    
    # Boolean
    if 'boolean' in csn_type_lower:
        return 'INTEGER'
    
    # Default
    return 'TEXT'

def create_table_sql_from_csn(table_name: str, entity_metadata) -> str:
    """Generate CREATE TABLE SQL from CSN entity metadata"""
    if not entity_metadata or not entity_metadata.columns:
        return None
    
    col_defs = []
    primary_keys = entity_metadata.primary_keys or []
    
    for col in entity_metadata.columns:
        col_name = col.name
        sql_type = csn_type_to_sqlite(col.type, col.length)
        
        col_def = f"{col_name} {sql_type}"
        
        # Add NOT NULL for non-nullable non-PK columns
        if not col.is_nullable and col_name not in primary_keys:
            col_def += " NOT NULL"
        
        col_defs.append(col_def)
    
    # Add PRIMARY KEY constraint if any
    if primary_keys:
        col_defs.append(f"PRIMARY KEY ({', '.join(primary_keys)})")
    
    create_sql = f"CREATE TABLE IF NOT EXISTS {table_name} (\n  " + ",\n  ".join(col_defs) + "\n)"
    
    return create_sql

def rebuild_table_from_csn(conn, entity_name: str, table_name: str, parser: CSNParser) -> bool:
    """Rebuild a single table from CSN metadata"""
    print(f"\n  [{entity_name}] → {table_name}")
    
    # Get entity metadata from CSN
    print(f"    Getting metadata from CSN...")
    entity_metadata = parser.get_entity_metadata(entity_name)
    
    if not entity_metadata:
        print(f"      ❌ Entity not found in CSN files")
        return False
    
    print(f"      ✅ Found: {len(entity_metadata.columns)} columns, {len(entity_metadata.primary_keys)} PKs")
    print(f"         Primary Keys: {entity_metadata.primary_keys}")
    
    # Generate CREATE TABLE SQL
    create_sql = create_table_sql_from_csn(table_name, entity_metadata)
    
    if not create_sql:
        print(f"      ❌ Failed to generate SQL")
        return False
    
    try:
        cursor = conn.cursor()
        
        # Drop existing table
        cursor.execute(f"DROP TABLE IF EXISTS {table_name}")
        print(f"      ✅ Dropped old table")
        
        # Create new table with PK constraints
        cursor.execute(create_sql)
        print(f"      ✅ Created table with PRIMARY KEY")
        
        conn.commit()
        return True
        
    except Exception as e:
        print(f"      ❌ SQL Error: {e}")
        return False

def main():
    """Main process"""
    print("="*80)
    print("Rebuild SQLite Database from CSN Metadata")
    print("="*80)
    print(f"\nTarget Database: {SQLITE_DB}")
    print(f"Source: CSN files in {CSN_DIR}/")
    print(f"\nNOTE: Uses local CSN files, no server required")
    print()
    
    # Check CSN directory
    if not os.path.exists(CSN_DIR):
        print(f"❌ CSN directory not found: {CSN_DIR}")
        return 1
    
    csn_files = [f for f in os.listdir(CSN_DIR) if f.endswith('.json')]
    print(f"✅ Found {len(csn_files)} CSN files:")
    for f in csn_files:
        print(f"   - {f}")
    
    # Initialize CSN parser
    print(f"\n Initializing CSN parser...")
    parser = CSNParser(CSN_DIR)
    
    # List available entities
    entities = parser.list_entities()
    print(f"✅ Parser ready - {len(entities)} entities available")
    
    # Connect to SQLite
    try:
        conn = sqlite3.connect(SQLITE_DB)
        print(f"\n✅ Connected to SQLite: {SQLITE_DB}")
        
        print("\n" + "="*80)
        print("REBUILDING TABLES FROM CSN")
        print("="*80)
        
        tables_rebuilt = 0
        
        # Rebuild mapped tables
        for entity_name, table_name in ENTITY_TO_TABLE.items():
            if entity_name in entities:
                if rebuild_table_from_csn(conn, entity_name, table_name, parser):
                    tables_rebuilt += 1
            else:
                print(f"\n  [{entity_name}] → {table_name}")
                print(f"    ⚠️  Not found in CSN files")
        
        # Summary
        print("\n" + "="*80)
        print("REBUILD SUMMARY")
        print("="*80)
        
        cursor = conn.cursor()
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name NOT LIKE 'sqlite_%'
            ORDER BY name
        """)
        
        all_tables = [row[0] for row in cursor.fetchall()]
        print(f"\nTotal tables in SQLite: {len(all_tables)}")
        print(f"Tables rebuilt from CSN: {tables_rebuilt}/{len(ENTITY_TO_TABLE)}")
        
        # Verify PRIMARY KEY constraints
        print("\nVerifying PRIMARY KEY constraints...")
        tables_with_pk = 0
        tables_with_pk_list = []
        tables_without_pk = []
        
        for table in all_tables:
            cursor.execute(f"PRAGMA table_info({table})")
            columns = cursor.fetchall()
            has_pk = any(col[5] > 0 for col in columns)  # col[5] is pk flag
            
            if has_pk:
                tables_with_pk += 1
                pk_cols = [col[1] for col in columns if col[5] > 0]
                tables_with_pk_list.append((table, pk_cols))
            else:
                tables_without_pk.append(table)
        
        print(f"  ✅ Tables with PRIMARY KEY: {tables_with_pk}/{len(all_tables)}")
        
        if tables_with_pk_list:
            print(f"\n  Tables with PRIMARY KEYS:")
            for table, pk_cols in tables_with_pk_list[:10]:  # Show first 10
                print(f"    - {table}: {', '.join(pk_cols)}")
            if len(tables_with_pk_list) > 10:
                print(f"    ... and {len(tables_with_pk_list) - 10} more")
        
        if tables_without_pk:
            print(f"\n  ⚠️  Tables without PRIMARY KEY: {len(tables_without_pk)}")
            for table in tables_without_pk[:5]:  # Show first 5
                print(f"      - {table}")
            if len(tables_without_pk) > 5:
                print(f"      ... and {len(tables_without_pk) - 5} more")
        
        conn.close()
        
        print("\n✅ Rebuild complete!")
        print("\nNext steps:")
        print("  1. Start server: python server.py")
        print("  2. Verify in UI: Data Products → View table structures")
        print("  3. Check 🔑 icon appears for primary key columns")
        
    except Exception as e:
        print(f"\n❌ Rebuild failed: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0

if __name__ == '__main__':
    sys.exit(main())