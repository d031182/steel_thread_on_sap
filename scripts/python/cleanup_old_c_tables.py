#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Cleanup Old C_ Tables from SQLite

Removes legacy C_ prefixed tables after CSN rebuild.
"""

import sqlite3
import sys

if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

SQLITE_DB = "app/database/p2p_data_products.db"

def main():
    print("="*80)
    print("Cleanup Old C_ Tables")
    print("="*80)
    print(f"\nDatabase: {SQLITE_DB}\n")
    
    conn = sqlite3.connect(SQLITE_DB)
    cursor = conn.cursor()
    
    # Find all C_ tables
    cursor.execute("""
        SELECT name FROM sqlite_master 
        WHERE type='table' AND name LIKE 'C_%'
        ORDER BY name
    """)
    
    c_tables = [row[0] for row in cursor.fetchall()]
    
    if not c_tables:
        print("✅ No C_ tables found - database is clean!")
        return 0
    
    print(f"Found {len(c_tables)} C_ tables to remove:")
    for table in c_tables:
        print(f"  - {table}")
    
    print(f"\nRemoving {len(c_tables)} tables...")
    
    for table in c_tables:
        cursor.execute(f"DROP TABLE IF EXISTS {table}")
        print(f"  ✅ Dropped {table}")
    
    conn.commit()
    
    # Verify
    cursor.execute("""
        SELECT name FROM sqlite_master 
        WHERE type='table' AND name NOT LIKE 'sqlite_%'
        ORDER BY name
    """)
    
    remaining = [row[0] for row in cursor.fetchall()]
    
    print("\n" + "="*80)
    print("CLEANUP COMPLETE")
    print("="*80)
    print(f"\nRemaining tables: {len(remaining)}")
    for table in remaining[:20]:
        print(f"  - {table}")
    if len(remaining) > 20:
        print(f"  ... and {len(remaining) - 20} more")
    
    conn.close()
    print("\n✅ Cleanup complete!")
    
    return 0

if __name__ == '__main__':
    sys.exit(main())