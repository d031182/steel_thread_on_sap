#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Rebuild SQLite Database from CSN Files Only

Creates SQLite database structure using CSN metadata files, without requiring
HANA Cloud connection. Perfect for creating test databases or offline development.

Usage: python scripts/python/rebuild_sqlite_from_csn.py

Author: P2P Development Team
Version: 2.0.0
"""

import sqlite3
import sys
import os
from pathlib import Path
from typing import List, Dict, Optional

# Add project root to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

from core.services.csn_parser import CSNParser

# Fix Windows encoding
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Configuration
SQLITE_DB = "../../modules/data_products_v2/database/p2p_data.db"
CSN_DIR = "../../docs/csn"


def csn_type_to_sqlite(csn_type: str, length: Optional[int] = None) -> str:
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
    
    return 'TEXT'


def create_table_sql_from_csn(table_name: str, entity_metadata) -> Optional[str]:
    """Generate CREATE TABLE SQL from CSN entity metadata"""
    if not entity_metadata or not entity_metadata.columns:
        return None
    
    col_defs = []
    primary_keys = entity_metadata.primary_keys or []
    
    # Build column definitions
    for col in entity_metadata.columns:
        col_name = col.name
        sql_type = csn_type_to_sqlite(col.type, col.length)
        
        col_def = f'"{col_name}" {sql_type}'
        
        # Add NOT NULL for non-nullable non-PK columns
        if not col.is_nullable and col_name not in primary_keys:
            col_def += " NOT NULL"
        
        col_defs.append(col_def)
    
    # Add PRIMARY KEY constraint if any
    if primary_keys:
        pk_cols = ', '.join(f'"{pk}"' for pk in primary_keys)
        col_defs.append(f"PRIMARY KEY ({pk_cols})")
    
    # Generate CREATE TABLE statement
    create_sql = f'CREATE TABLE IF NOT EXISTS "{table_name}" (\n  ' + \
                 ',\n  '.join(col_defs) + '\n)'
    
    return create_sql


def rebuild_table_from_csn(
    conn: sqlite3.Connection,
    entity_name: str,
    parser: CSNParser
) -> bool:
    """Rebuild a single table from CSN metadata"""
    print(f"\n  [{entity_name}]")
    
    # Get entity metadata from CSN
    print(f"    Getting metadata from CSN...")
    entity_metadata = parser.get_entity_metadata(entity_name)
    
    if not entity_metadata:
        print(f"      ⚠️  Entity '{entity_name}' not found in CSN files")
        print(f"      Skipping...")
        return False
    
    print(f"      ✅ Found: {len(entity_metadata.columns)} columns")
    
    if entity_metadata.primary_keys:
        print(f"      🔑 Primary Keys: {', '.join(entity_metadata.primary_keys)}")
    else:
        print(f"      ⚠️  No primary keys defined")
    
    # Generate CREATE TABLE SQL
    create_sql = create_table_sql_from_csn(entity_name, entity_metadata)
    
    if not create_sql:
        print(f"      ❌ Failed to generate SQL")
        return False
    
    try:
        cursor = conn.cursor()
        
        # Drop existing table
        cursor.execute(f'DROP TABLE IF EXISTS "{entity_name}"')
        
        # Create new table with proper schema
        cursor.execute(create_sql)
        print(f"      ✅ Created table: {entity_name}")
        
        conn.commit()
        return True
        
    except sqlite3.Error as e:
        print(f"      ❌ SQLite Error: {e}")
        conn.rollback()
        return False


def main():
    """Main process"""
    print("=" * 80)
    print("REBUILD SQLITE FROM CSN FILES")
    print("=" * 80)
    print("\nStrategy: Use CSN metadata → Create SQLite tables (no HANA required)")
    print(f"\nTarget SQLite: {SQLITE_DB}")
    print(f"Source CSN: {CSN_DIR}/")
    print()
    
    # Check CSN directory exists
    if not os.path.exists(CSN_DIR):
        print(f"❌ CSN directory not found: {CSN_DIR}")
        return 1
    
    csn_files = [f for f in os.listdir(CSN_DIR) if f.endswith('.json')]
    print(f"✅ Found {len(csn_files)} CSN files")
    
    # Initialize CSN parser (memory-efficient)
    print(f"\n📋 Initializing CSN parser...")
    parser = CSNParser(CSN_DIR)
    entities = parser.list_entities()
    print(f"   ✅ Parser ready - {len(entities)} entities available")
    
    # Use ALL entities from CSN files (comprehensive approach)
    entities_to_create = sorted(entities)
    
    print(f"\n   Will create {len(entities_to_create)} tables from CSN:")
    print(f"   (Showing first 20...)")
    for entity in entities_to_create[:20]:
        print(f"     - {entity}")
    if len(entities_to_create) > 20:
        print(f"     ... and {len(entities_to_create) - 20} more")
    
    # Connect to SQLite
    print(f"\n💾 Connecting to SQLite...")
    try:
        # Ensure directory exists
        db_path = Path(SQLITE_DB)
        db_path.parent.mkdir(parents=True, exist_ok=True)
        
        conn = sqlite3.connect(SQLITE_DB)
        print(f"   ✅ Connected: {SQLITE_DB}")
        
    except Exception as e:
        print(f"   ❌ SQLite connection failed: {e}")
        return 1
    
    # Rebuild tables
    print("\n" + "=" * 80)
    print("REBUILDING TABLES FROM CSN")
    print("=" * 80)
    
    tables_rebuilt = 0
    tables_skipped = 0
    
    for entity_name in entities_to_create:
        if rebuild_table_from_csn(conn, entity_name, parser):
            tables_rebuilt += 1
        else:
            tables_skipped += 1
    
    # Summary
    print("\n" + "=" * 80)
    print("REBUILD SUMMARY")
    print("=" * 80)
    
    cursor = conn.cursor()
    cursor.execute("""
        SELECT name FROM sqlite_master 
        WHERE type='table' AND name NOT LIKE 'sqlite_%'
        ORDER BY name
    """)
    
    all_tables = [row[0] for row in cursor.fetchall()]
    
    print(f"\n📊 Results:")
    print(f"   Entities processed: {len(entities_to_create)}")
    print(f"   SQLite tables created: {tables_rebuilt}")
    print(f"   Tables skipped: {tables_skipped}")
    print(f"   Total SQLite tables: {len(all_tables)}")
    
    # Verify PRIMARY KEY constraints
    print(f"\n🔑 Verifying PRIMARY KEY constraints...")
    tables_with_pk = 0
    tables_with_pk_list = []
    tables_without_pk = []
    
    for table in all_tables:
        cursor.execute(f'PRAGMA table_info("{table}")')
        columns = cursor.fetchall()
        has_pk = any(col[5] > 0 for col in columns)  # col[5] is pk flag
        
        if has_pk:
            tables_with_pk += 1
            pk_cols = [col[1] for col in columns if col[5] > 0]
            tables_with_pk_list.append((table, pk_cols))
        else:
            tables_without_pk.append(table)
    
    print(f"   ✅ Tables with PRIMARY KEY: {tables_with_pk}/{len(all_tables)}")
    
    if tables_with_pk_list:
        print(f"\n   Tables with PRIMARY KEYS:")
        for table, pk_cols in tables_with_pk_list:
            print(f"     🔑 {table}: {', '.join(pk_cols)}")
    
    if tables_without_pk:
        print(f"\n   ⚠️  Tables without PRIMARY KEY: {len(tables_without_pk)}")
        for table in tables_without_pk:
            print(f"       - {table}")
    
    conn.close()
    
    print("\n" + "=" * 80)
    print("✅ REBUILD COMPLETE")
    print("=" * 80)
    print(f"\nSQLite database ready:")
    print(f"  Location: {SQLITE_DB}")
    print(f"  Tables: {len(all_tables)}")
    print(f"  With PKs: {tables_with_pk}")
    print("\nNext steps:")
    print("  1. Populate data: python scripts/python/populate_p2p_comprehensive.py")
    print("  2. Test via API: Start server and use API Playground")
    print("  3. Verify data integrity")
    
    return 0


if __name__ == '__main__':
    sys.exit(main())