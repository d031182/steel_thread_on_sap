#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Rebuild SQLite Database from HANA + CSN (Backup Repository Strategy)

Creates SQLite backup of HANA Cloud P2P tables using:
1. HANA Cloud - Get list of actual P2P tables (dynamic discovery)
2. CSN metadata - Get table schemas (memory-efficient, no HANA load)
3. SQLite - Create backup repository with same structure

This ensures SQLite mirrors HANA Cloud exactly, serving as backup repository.

Usage: python scripts/python/rebuild_sqlite_from_hana_csn.py

Author: P2P Development Team
Version: 1.0.0
"""

import sqlite3
import sys
import os
from pathlib import Path
from typing import List, Dict, Optional

# Add project root to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

from core.services.csn_parser import CSNParser
from core.repositories import create_repository
from core.repositories.base import AbstractRepository

# Fix Windows encoding
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Configuration
SQLITE_DB = "core/databases/sqlite/p2p_test_data.db"
CSN_DIR = "docs/csn"
HANA_SCHEMA_PATTERN = "C_%"  # P2P tables start with C_


def csn_type_to_sqlite(csn_type: str, length: Optional[int] = None) -> str:
    """
    Convert CSN/CDS type to SQLite type
    
    Args:
        csn_type: CSN type string
        length: Optional length constraint
        
    Returns:
        SQLite type string
    """
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
        return 'TEXT'  # SQLite stores dates as TEXT
    
    # Boolean
    if 'boolean' in csn_type_lower:
        return 'INTEGER'
    
    # Default fallback
    return 'TEXT'


def create_table_sql_from_csn(table_name: str, entity_metadata) -> Optional[str]:
    """
    Generate CREATE TABLE SQL from CSN entity metadata
    
    Args:
        table_name: SQLite table name
        entity_metadata: EntityMetadata from CSN parser
        
    Returns:
        CREATE TABLE SQL string or None if error
    """
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


def get_hana_p2p_tables(hana_repo: AbstractRepository) -> List[str]:
    """
    Query HANA to get list of P2P tables (C_* pattern)
    
    Args:
        hana_repo: HANA repository instance
        
    Returns:
        List of table names (e.g., ["C_PURCHASEORDER", "C_SUPPLIER", ...])
    """
    print("\n  Querying HANA for P2P tables (C_* pattern)...")
    
    try:
        # Query HANA system tables for C_* tables
        query = """
            SELECT DISTINCT TABLE_NAME
            FROM SYS.TABLES
            WHERE TABLE_NAME LIKE ?
            ORDER BY TABLE_NAME
        """
        
        result = hana_repo.execute_query(query, params=(HANA_SCHEMA_PATTERN,))
        
        if result and 'rows' in result:
            tables = [row[0] for row in result['rows']]
            print(f"    ✅ Found {len(tables)} P2P tables in HANA")
            return tables
        else:
            print(f"    ⚠️  No P2P tables found")
            return []
            
    except Exception as e:
        print(f"    ❌ HANA query failed: {e}")
        return []


def map_hana_table_to_entity(hana_table_name: str) -> str:
    """
    Map HANA table name to CSN entity name
    
    Examples:
        C_PURCHASEORDER → PurchaseOrder
        C_SUPPLIER → Supplier
        C_PURCHASEORDERITEM → PurchaseOrderItem
    
    Args:
        hana_table_name: HANA table name (e.g., "C_PURCHASEORDER")
        
    Returns:
        CSN entity name (e.g., "PurchaseOrder")
    """
    if not hana_table_name.startswith('C_'):
        return hana_table_name
    
    # Remove C_ prefix
    name_without_prefix = hana_table_name[2:]
    
    # Convert to PascalCase
    # C_PURCHASEORDER → PurchaseOrder
    # C_PURCHASEORDERITEM → PurchaseOrderItem
    parts = name_without_prefix.split('_')
    entity_name = ''.join(word.capitalize() for word in parts)
    
    return entity_name


def rebuild_table_from_csn(
    conn: sqlite3.Connection,
    hana_table_name: str,
    parser: CSNParser
) -> bool:
    """
    Rebuild a single table from CSN metadata
    
    Args:
        conn: SQLite connection
        hana_table_name: Original HANA table name (e.g., "C_PURCHASEORDER")
        parser: CSN parser instance
        
    Returns:
        True if successful, False otherwise
    """
    # Map HANA table to entity name
    entity_name = map_hana_table_to_entity(hana_table_name)
    
    print(f"\n  [{hana_table_name}] → SQLite table: {entity_name}")
    
    # Get entity metadata from CSN
    print(f"    Getting metadata from CSN...")
    entity_metadata = parser.get_entity_metadata(entity_name)
    
    if not entity_metadata:
        print(f"      ⚠️  Entity '{entity_name}' not found in CSN files")
        print(f"      Skipping (CSN file may not exist for this table)")
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
    print("REBUILD SQLITE FROM HANA + CSN")
    print("=" * 80)
    print("\nStrategy: Query HANA for P2P tables → Create SQLite mirror from CSN")
    print(f"\nTarget SQLite: {SQLITE_DB}")
    print(f"Source CSN: {CSN_DIR}/")
    print(f"HANA Pattern: {HANA_SCHEMA_PATTERN}")
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
    print(f"   Entities: {', '.join(entities)}")
    
    # Initialize HANA repository via factory pattern
    print(f"\n🔌 Connecting to HANA Cloud...")
    try:
        # Load HANA credentials from environment
        # Check both root .env and app/.env
        from dotenv import load_dotenv
        
        # Try app/.env first (where HANA credentials are stored)
        if os.path.exists('app/.env'):
            load_dotenv('app/.env')
        else:
            load_dotenv()  # Fall back to root .env
        
        hana_config = {
            'host': os.getenv('HANA_HOST'),
            'port': int(os.getenv('HANA_PORT', 443)),
            'user': os.getenv('HANA_USER'),
            'password': os.getenv('HANA_PASSWORD')
        }
        
        # Validate config
        if not all([hana_config['host'], hana_config['user'], hana_config['password']]):
            print(f"   ❌ Missing HANA credentials in .env file")
            print(f"   Required: HANA_HOST, HANA_USER, HANA_PASSWORD")
            return 1
        
        hana_repo = create_repository('hana', **hana_config)
        print(f"   ✅ HANA connection ready ({hana_config['host']})")
    except Exception as e:
        print(f"   ❌ HANA connection failed: {e}")
        print(f"   Cannot proceed without HANA (needed for table discovery)")
        return 1
    
    # Get P2P tables from HANA
    print(f"\n🔍 Discovering P2P tables in HANA...")
    hana_tables = get_hana_p2p_tables(hana_repo)
    
    if not hana_tables:
        print(f"\n❌ No P2P tables found in HANA. Cannot proceed.")
        return 1
    
    print(f"\n   P2P Tables found:")
    for table in hana_tables[:10]:
        entity = map_hana_table_to_entity(table)
        print(f"     - {table} → {entity}")
    if len(hana_tables) > 10:
        print(f"     ... and {len(hana_tables) - 10} more")
    
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
    
    for hana_table in hana_tables:
        if rebuild_table_from_csn(conn, hana_table, parser):
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
    print(f"   HANA P2P tables discovered: {len(hana_tables)}")
    print(f"   SQLite tables created: {tables_rebuilt}")
    print(f"   Tables skipped (no CSN): {tables_skipped}")
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
        for table, pk_cols in tables_with_pk_list[:10]:
            print(f"     🔑 {table}: {', '.join(pk_cols)}")
        if len(tables_with_pk_list) > 10:
            print(f"     ... and {len(tables_with_pk_list) - 10} more")
    
    if tables_without_pk:
        print(f"\n   ⚠️  Tables without PRIMARY KEY: {len(tables_without_pk)}")
        for table in tables_without_pk[:5]:
            print(f"       - {table}")
        if len(tables_without_pk) > 5:
            print(f"       ... and {len(tables_without_pk) - 5} more")
    
    conn.close()
    
    print("\n" + "=" * 80)
    print("✅ REBUILD COMPLETE")
    print("=" * 80)
    print(f"\nSQLite database ready as HANA backup:")
    print(f"  Location: {SQLITE_DB}")
    print(f"  Tables: {len(all_tables)}")
    print(f"  With PKs: {tables_with_pk}")
    print("\nNext steps:")
    print("  1. Populate data: python scripts/python/populate_p2p_comprehensive.py")
    print("  2. Test backup repository via API")
    print("  3. Verify data consistency with HANA")
    
    return 0


if __name__ == '__main__':
    sys.exit(main())