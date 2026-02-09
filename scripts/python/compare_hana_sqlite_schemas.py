#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Compare HANA Cloud Tables vs SQLite Schema
===========================================
Validates that SQLite schema matches actual HANA Cloud tables.

This script:
1. Queries HANA Cloud for all existing tables
2. Queries SQLite for all tables
3. Compares schemas and reports differences

Author: P2P Development Team
Version: 1.0.0
Date: 2026-02-08
"""

import sqlite3
import sys
import os
from pathlib import Path
from typing import List, Dict, Optional, Set
from dataclasses import dataclass

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from modules.hana_connection.backend.hana_connection import HANAConnection
from dotenv import load_dotenv

# Fix Windows encoding
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Configuration
SQLITE_DB = "core/databases/sqlite/p2p_data.db"


@dataclass
class ColumnInfo:
    """Column information for comparison"""
    name: str
    data_type: str
    nullable: bool
    is_pk: bool


@dataclass
class ComparisonResult:
    """Result of schema comparison"""
    table_name: str
    status: str  # MATCH, HANA_ONLY, SQLITE_ONLY, SCHEMA_DIFF
    hana_columns: Optional[List[ColumnInfo]] = None
    sqlite_columns: Optional[List[ColumnInfo]] = None
    differences: Optional[List[str]] = None


def get_hana_tables(connection) -> Set[str]:
    """Get list of tables in HANA Cloud Data Product schemas"""
    cursor = connection.cursor()
    
    # Query tables from Data Product schemas
    query = """
        SELECT TABLE_NAME
        FROM TABLES
        WHERE SCHEMA_NAME LIKE '_SAP_DATAPRODUCT%'
        ORDER BY TABLE_NAME
    """
    cursor.execute(query)
    
    # Extract base table names (strip schema prefix)
    # Example: "_SAP_DATAPRODUCT_xxx_companycode.CompanyCode" -> "CompanyCode"
    tables = set()
    for row in cursor.fetchall():
        full_name = row[0]
        # Get part after last dot
        if '.' in full_name:
            base_name = full_name.split('.')[-1]
            tables.add(base_name)
    
    cursor.close()
    
    return tables


def get_hana_table_schema(connection, table_name: str) -> List[ColumnInfo]:
    """Get table schema from HANA Cloud Data Product schemas"""
    cursor = connection.cursor()
    
    # First, find the full table name in Data Product schemas
    find_query = """
        SELECT SCHEMA_NAME, TABLE_NAME
        FROM TABLES
        WHERE SCHEMA_NAME LIKE '_SAP_DATAPRODUCT%'
        AND TABLE_NAME LIKE ?
    """
    cursor.execute(find_query, (f'%.{table_name}',))
    result = cursor.fetchone()
    
    if not result:
        cursor.close()
        return []
    
    schema_name, full_table_name = result
    
    # Get column information
    query = """
        SELECT 
            COLUMN_NAME,
            DATA_TYPE_NAME,
            IS_NULLABLE,
            POSITION
        FROM TABLE_COLUMNS
        WHERE SCHEMA_NAME = ?
        AND TABLE_NAME = ?
        ORDER BY POSITION
    """
    cursor.execute(query, (schema_name, full_table_name))
    
    columns = []
    for row in cursor.fetchall():
        columns.append(ColumnInfo(
            name=row[0],
            data_type=row[1],
            nullable=(row[2] == 'TRUE'),
            is_pk=False  # Will check separately
        ))
    
    # Get primary key info
    pk_query = """
        SELECT COLUMN_NAME
        FROM CONSTRAINTS
        WHERE SCHEMA_NAME = ?
        AND TABLE_NAME = ?
        AND IS_PRIMARY_KEY = 'TRUE'
    """
    cursor.execute(pk_query, (schema_name, full_table_name))
    pk_columns = {row[0] for row in cursor.fetchall()}
    
    # Mark primary keys
    for col in columns:
        if col.name in pk_columns:
            col.is_pk = True
    
    cursor.close()
    return columns


def get_sqlite_tables(db_path: str) -> Set[str]:
    """Get list of tables in SQLite"""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT name FROM sqlite_master 
        WHERE type='table' 
        AND name NOT LIKE 'sqlite_%'
        ORDER BY name
    """)
    
    tables = {row[0] for row in cursor.fetchall()}
    conn.close()
    
    return tables


def get_sqlite_table_schema(db_path: str, table_name: str) -> List[ColumnInfo]:
    """Get table schema from SQLite"""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute(f"PRAGMA table_info({table_name})")
    table_info = cursor.fetchall()
    
    columns = []
    for row in table_info:
        # PRAGMA table_info returns: (cid, name, type, notnull, dflt_value, pk)
        columns.append(ColumnInfo(
            name=row[1],
            data_type=row[2],
            nullable=(row[3] == 0),  # notnull=0 means nullable
            is_pk=(row[5] > 0)  # pk>0 means primary key
        ))
    
    conn.close()
    return columns


def compare_schemas(
    table_name: str,
    hana_cols: Optional[List[ColumnInfo]],
    sqlite_cols: Optional[List[ColumnInfo]]
) -> ComparisonResult:
    """Compare schemas between HANA and SQLite"""
    
    # HANA only
    if hana_cols and not sqlite_cols:
        return ComparisonResult(
            table_name=table_name,
            status='HANA_ONLY',
            hana_columns=hana_cols,
            differences=[f"Table exists in HANA but not in SQLite"]
        )
    
    # SQLite only
    if sqlite_cols and not hana_cols:
        return ComparisonResult(
            table_name=table_name,
            status='SQLITE_ONLY',
            sqlite_columns=sqlite_cols,
            differences=[f"Table exists in SQLite but not in HANA"]
        )
    
    # Both exist - compare columns
    if hana_cols and sqlite_cols:
        differences = []
        
        hana_col_names = {col.name for col in hana_cols}
        sqlite_col_names = {col.name for col in sqlite_cols}
        
        # Check for missing columns
        missing_in_sqlite = hana_col_names - sqlite_col_names
        missing_in_hana = sqlite_col_names - hana_col_names
        
        if missing_in_sqlite:
            differences.append(f"Missing in SQLite: {', '.join(missing_in_sqlite)}")
        
        if missing_in_hana:
            differences.append(f"Missing in HANA: {', '.join(missing_in_hana)}")
        
        # Check common columns for differences
        common_cols = hana_col_names & sqlite_col_names
        for col_name in common_cols:
            hana_col = next(c for c in hana_cols if c.name == col_name)
            sqlite_col = next(c for c in sqlite_cols if c.name == col_name)
            
            # Check primary key mismatch
            if hana_col.is_pk != sqlite_col.is_pk:
                differences.append(
                    f"Column '{col_name}': PK mismatch "
                    f"(HANA: {hana_col.is_pk}, SQLite: {sqlite_col.is_pk})"
                )
        
        status = 'MATCH' if not differences else 'SCHEMA_DIFF'
        
        return ComparisonResult(
            table_name=table_name,
            status=status,
            hana_columns=hana_cols,
            sqlite_columns=sqlite_cols,
            differences=differences if differences else None
        )
    
    return ComparisonResult(
        table_name=table_name,
        status='UNKNOWN',
        differences=["Unable to compare"]
    )


def main():
    """Main comparison process"""
    print("=" * 80)
    print("COMPARE HANA CLOUD VS SQLITE SCHEMAS")
    print("=" * 80)
    print(f"\nSQLite DB: {SQLITE_DB}")
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
    
    # Get tables from both sources
    print("\n📋 Discovering tables...")
    hana_tables = get_hana_tables(hana_conn)
    sqlite_tables = get_sqlite_tables(SQLITE_DB)
    
    print(f"   HANA tables: {len(hana_tables)}")
    print(f"   SQLite tables: {len(sqlite_tables)}")
    
    # Get all unique table names
    all_tables = hana_tables | sqlite_tables
    print(f"   Total unique tables: {len(all_tables)}")
    
    # Compare each table
    print("\n" + "=" * 80)
    print("SCHEMA COMPARISON")
    print("=" * 80)
    
    results = []
    
    for table_name in sorted(all_tables):
        print(f"\n📊 {table_name}")
        
        # Get schemas
        hana_schema = None
        sqlite_schema = None
        
        if table_name in hana_tables:
            hana_schema = get_hana_table_schema(hana_conn, table_name)
            print(f"   HANA: {len(hana_schema)} columns")
        
        if table_name in sqlite_tables:
            sqlite_schema = get_sqlite_table_schema(SQLITE_DB, table_name)
            print(f"   SQLite: {len(sqlite_schema)} columns")
        
        # Compare
        result = compare_schemas(table_name, hana_schema, sqlite_schema)
        results.append(result)
        
        # Display result
        if result.status == 'MATCH':
            print(f"   ✅ MATCH")
        elif result.status == 'HANA_ONLY':
            print(f"   ⚠️  EXISTS ONLY IN HANA")
        elif result.status == 'SQLITE_ONLY':
            print(f"   ⚠️  EXISTS ONLY IN SQLITE")
        elif result.status == 'SCHEMA_DIFF':
            print(f"   ⚠️  SCHEMA DIFFERENCES:")
            for diff in result.differences:
                print(f"      - {diff}")
    
    # Summary
    print("\n" + "=" * 80)
    print("COMPARISON SUMMARY")
    print("=" * 80)
    
    matches = [r for r in results if r.status == 'MATCH']
    hana_only = [r for r in results if r.status == 'HANA_ONLY']
    sqlite_only = [r for r in results if r.status == 'SQLITE_ONLY']
    diffs = [r for r in results if r.status == 'SCHEMA_DIFF']
    
    print(f"\n✅ Matches: {len(matches)}")
    print(f"⚠️  HANA only: {len(hana_only)}")
    print(f"⚠️  SQLite only: {len(sqlite_only)}")
    print(f"⚠️  Schema differences: {len(diffs)}")
    
    if hana_only:
        print(f"\n📊 Tables in HANA but not SQLite:")
        for r in hana_only:
            print(f"   - {r.table_name}")
    
    if sqlite_only:
        print(f"\n📊 Tables in SQLite but not HANA:")
        for r in sqlite_only:
            print(f"   - {r.table_name}")
    
    if diffs:
        print(f"\n⚠️  Tables with schema differences:")
        for r in diffs:
            print(f"   - {r.table_name}")
            for diff in r.differences:
                print(f"      {diff}")
    
    # Close connection
    hana_manager.close()
    
    print("\n" + "=" * 80)
    if len(matches) == len(results):
        print("✅ ALL TABLES MATCH!")
    else:
        print("⚠️  SCHEMAS HAVE DIFFERENCES")
    print("=" * 80)
    
    return 0 if len(diffs) == 0 else 1


if __name__ == '__main__':
    sys.exit(main())