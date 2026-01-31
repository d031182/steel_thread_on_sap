#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Rebuild SQLite Database with Primary Keys from HANA

Now that HANA data source correctly detects primary keys via SYS.INDEX_COLUMNS,
this script rebuilds all SQLite tables with proper PRIMARY KEY constraints
matching the HANA structure.

Usage: python scripts/python/rebuild_sqlite_with_pk.py
"""

import requests
import sqlite3
import sys
from typing import List, Dict

# Fix Windows encoding
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

BASE_URL = "http://localhost:5000/api"
SQLITE_DB = "app/database/p2p_data_products.db"

def get_table_structure_with_pk(schema: str, table: str) -> List[Dict]:
    """Get column structure from HANA with PRIMARY KEY flags"""
    print(f"    Getting structure for {table}...")
    url = f"{BASE_URL}/data-products/{schema}/{table}/structure?source=hana"
    
    try:
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            columns = data.get('columns', [])
            
            # Count primary keys
            pk_count = sum(1 for col in columns if col.get('isPrimaryKey') or col.get('IS_PRIMARY_KEY'))
            print(f"      ✅ {len(columns)} columns ({pk_count} PKs)")
            return columns
        else:
            print(f"      ❌ Failed: HTTP {response.status_code}")
            return []
    except Exception as e:
        print(f"      ❌ Error: {e}")
        return []

def sql_type_from_hana(hana_type: str, length: int = None) -> str:
    """Convert HANA type to SQLite type"""
    if not hana_type:
        return 'TEXT'
    
    hana_type_upper = hana_type.upper()
    
    if hana_type_upper in ['NVARCHAR', 'VARCHAR', 'CHAR', 'NCHAR', 'CLOB', 'NCLOB']:
        return 'TEXT'
    elif hana_type_upper in ['INTEGER', 'INT', 'BIGINT', 'SMALLINT', 'TINYINT']:
        return 'INTEGER'
    elif hana_type_upper in ['DECIMAL', 'NUMERIC', 'DOUBLE', 'REAL', 'FLOAT']:
        return 'REAL'
    elif hana_type_upper in ['DATE', 'TIME', 'TIMESTAMP', 'SECONDDATE']:
        return 'TEXT'
    elif hana_type_upper == 'BOOLEAN':
        return 'INTEGER'
    else:
        return 'TEXT'

def create_table_sql_with_pk(table_name: str, columns: List[Dict]) -> str:
    """Generate CREATE TABLE SQL with PRIMARY KEY constraints"""
    if not columns:
        return None
    
    col_defs = []
    primary_keys = []
    
    for col in columns:
        col_name = col.get('COLUMN_NAME') or col.get('name')
        data_type = col.get('DATA_TYPE_NAME') or col.get('dataType') or col.get('data_type') or 'TEXT'
        length = col.get('LENGTH') or col.get('length')
        is_nullable = col.get('IS_NULLABLE', True)
        if isinstance(is_nullable, str):
            is_nullable = is_nullable.upper() not in ['FALSE', 'NO', '0']
        
        # Check both possible PK flag names
        is_primary = col.get('isPrimaryKey', False) or col.get('IS_PRIMARY_KEY', False)
        
        if is_primary:
            primary_keys.append(col_name)
        
        sql_type = sql_type_from_hana(data_type, length)
        
        col_def = f"{col_name} {sql_type}"
        if not is_nullable and not is_primary:
            col_def += " NOT NULL"
        
        col_defs.append(col_def)
    
    # Add PRIMARY KEY constraint if any
    if primary_keys:
        col_defs.append(f"PRIMARY KEY ({', '.join(primary_keys)})")
    
    create_sql = f"CREATE TABLE IF NOT EXISTS {table_name} (\n  " + ",\n  ".join(col_defs) + "\n)"
    
    return create_sql

def rebuild_data_product(conn, product_name: str, schema: str):
    """Rebuild all tables for a data product"""
    print(f"\n  [{product_name}]")
    
    cursor = conn.cursor()
    
    # Get tables from HANA
    print(f"    Getting tables from HANA...")
    url = f"{BASE_URL}/data-products/{schema}/tables?source=hana"
    
    try:
        response = requests.get(url, timeout=10)
        
        if response.status_code != 200:
            print(f"      ❌ Failed: HTTP {response.status_code}")
            return 0
        
        tables_data = response.json().get('tables', [])
        print(f"      ✅ Found {len(tables_data)} tables")
        
        tables_created = 0
        
        # Rebuild each table
        for table_info in tables_data:
            table_full_name = table_info['name']
            table_short_name = table_full_name.split('.')[-1]
            
            # Get structure with PK info
            columns = get_table_structure_with_pk(schema, table_full_name)
            
            if columns:
                create_sql = create_table_sql_with_pk(table_short_name, columns)
                
                if create_sql:
                    try:
                        # Drop existing table
                        cursor.execute(f"DROP TABLE IF EXISTS {table_short_name}")
                        
                        # Create new table with PK constraints
                        cursor.execute(create_sql)
                        tables_created += 1
                        print(f"      ✅ Recreated {table_short_name}")
                    except Exception as e:
                        print(f"      ❌ Failed to create {table_short_name}: {e}")
        
        conn.commit()
        return tables_created
        
    except Exception as e:
        print(f"      ❌ Error: {e}")
        return 0

def main():
    """Main process"""
    print("="*80)
    print("Rebuild SQLite Database with Primary Keys from HANA")
    print("="*80)
    print(f"\nTarget Database: {SQLITE_DB}")
    print(f"Source: HANA Cloud via {BASE_URL}")
    print(f"\nNOTE: Server must be running (python server.py)")
    print()
    
    # Test connection
    print("Testing server connection...")
    try:
        response = requests.get(f"{BASE_URL}/data-products?source=hana", timeout=5)
        if response.status_code != 200:
            print(f"❌ Server not responding: HTTP {response.status_code}")
            print("\nPlease start server: python server.py")
            return 1
        
        products_data = response.json()
        data_products = products_data.get('data_products', [])
        print(f"✅ Server OK - Found {len(data_products)} data products in HANA")
    except Exception as e:
        print(f"❌ Cannot connect to server: {e}")
        print("\nPlease start server: python server.py")
        return 1
    
    try:
        conn = sqlite3.connect(SQLITE_DB)
        print(f"\n✅ Connected to SQLite: {SQLITE_DB}")
        
        print("\n" + "="*80)
        print("REBUILDING TABLES WITH PRIMARY KEYS")
        print("="*80)
        
        total_tables = 0
        
        # Rebuild each data product
        for product in data_products:
            schema = product['name']
            display_name = product['display_name']
            
            tables_created = rebuild_data_product(conn, display_name, schema)
            total_tables += tables_created
        
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
        print(f"Tables rebuilt with PKs: {total_tables}")
        
        # Verify PRIMARY KEY constraints
        print("\nVerifying PRIMARY KEY constraints...")
        tables_with_pk = 0
        tables_without_pk = []
        
        for table in all_tables:
            cursor.execute(f"PRAGMA table_info({table})")
            columns = cursor.fetchall()
            has_pk = any(col[5] > 0 for col in columns)  # col[5] is pk flag
            
            if has_pk:
                tables_with_pk += 1
            else:
                tables_without_pk.append(table)
        
        print(f"  ✅ Tables with PRIMARY KEY: {tables_with_pk}/{len(all_tables)}")
        
        if tables_without_pk:
            print(f"  ⚠️  Tables without PRIMARY KEY: {len(tables_without_pk)}")
            for table in tables_without_pk[:5]:  # Show first 5
                print(f"      - {table}")
            if len(tables_without_pk) > 5:
                print(f"      ... and {len(tables_without_pk) - 5} more")
        
        conn.close()
        
        print("\n✅ Rebuild complete!")
        print("\nNext steps:")
        print("  1. Verify in UI: Data Products → View table structures")
        print("  2. Check 🔑 icon appears for primary key columns")
        print("  3. Run validation: python scripts/python/validate_all_data_products.py")
        
    except Exception as e:
        print(f"\n❌ Rebuild failed: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0

if __name__ == '__main__':
    sys.exit(main())