#!/usr/bin/env python3
"""
Migrate Knowledge Graph Cache to Separate Database

PROBLEM:
- KG cache tables (graph_edges, graph_nodes, graph_ontology) in p2p_data.db
- Violates module separation (v3.28 Strategy Pattern)
- Shows in Data Products UI incorrectly

SOLUTION:
- Copy cache tables from p2p_data.db to modules/knowledge_graph/database/graph_cache.db
- Drop cache tables from p2p_data.db
- Clean separation achieved

SAFE:
- Creates backup before migration
- Rollback available if needed

@author P2P Development Team
@version 1.0.0 (2026-02-05 - Database Separation)
"""

import sys
import os
import shutil
import sqlite3
from datetime import datetime
from pathlib import Path

# Windows encoding fix (MANDATORY for all Python scripts)
if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except AttributeError:
        import io
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

def main():
    """Execute KG cache migration to separate database"""
    
    # Paths
    source_db = project_root / 'database' / 'p2p_data.db'
    target_db = project_root / 'modules' / 'knowledge_graph' / 'database' / 'graph_cache.db'
    backup_db = project_root / 'database' / f'p2p_data_backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}.db'
    
    print("="*70)
    print("KNOWLEDGE GRAPH CACHE MIGRATION")
    print("="*70)
    print(f"Source: {source_db}")
    print(f"Target: {target_db}")
    print(f"Backup: {backup_db}")
    print()
    
    # Check source exists
    if not source_db.exists():
        print(f"[!] ERROR: Source database not found: {source_db}")
        return 1
    
    # Create backup
    print("[*] Creating backup...")
    shutil.copy2(source_db, backup_db)
    print(f"[+] Backup created: {backup_db}")
    print()
    
    # Create target directory
    target_db.parent.mkdir(parents=True, exist_ok=True)
    
    # Connect to databases
    source_conn = sqlite3.connect(source_db)
    target_conn = sqlite3.connect(target_db)
    
    try:
        # Get list of cache tables in source
        cursor = source_conn.cursor()
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name LIKE 'graph_%'
            ORDER BY name
        """)
        cache_tables = [row[0] for row in cursor.fetchall()]
        
        if not cache_tables:
            print("[i] No cache tables found in source database (already migrated?)")
            return 0
        
        print(f"[*] Found {len(cache_tables)} cache tables to migrate:")
        for table in cache_tables:
            print(f"   - {table}")
        print()
        
        # Migrate each table
        for table_name in cache_tables:
            print(f"[>] Migrating {table_name}...")
            
            # Get table schema
            cursor.execute(f"SELECT sql FROM sqlite_master WHERE type='table' AND name='{table_name}'")
            create_sql = cursor.fetchone()[0]
            
            # Create table in target
            target_conn.execute(create_sql)
            
            # Copy data
            cursor.execute(f"SELECT * FROM {table_name}")
            rows = cursor.fetchall()
            
            if rows:
                # Get column count
                placeholders = ','.join(['?' for _ in range(len(rows[0]))])
                target_conn.executemany(
                    f"INSERT INTO {table_name} VALUES ({placeholders})",
                    rows
                )
                print(f"   [+] Copied {len(rows)} rows")
            else:
                print(f"   [i] Table is empty")
        
        # Commit target
        target_conn.commit()
        print()
        
        # Drop tables from source
        print("[!] Removing cache tables from source database...")
        for table_name in cache_tables:
            source_conn.execute(f"DROP TABLE {table_name}")
            print(f"   [+] Dropped {table_name}")
        
        source_conn.commit()
        print()
        
        # Verify migration
        print("[?] Verifying migration...")
        cursor = target_conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
        target_tables = [row[0] for row in cursor.fetchall()]
        
        missing = set(cache_tables) - set(target_tables)
        if missing:
            print(f"[!] ERROR: Tables missing in target: {missing}")
            return 1
        
        print(f"[+] All {len(cache_tables)} tables verified in target database")
        print()
        
        # Final status
        print("="*70)
        print("[SUCCESS] MIGRATION COMPLETE!")
        print("="*70)
        print()
        print("Results:")
        print(f"  • Cache tables moved: {len(cache_tables)}")
        print(f"  • Target database: {target_db}")
        print(f"  • Backup available: {backup_db}")
        print()
        print("Next steps:")
        print("  1. Refresh Data Products page - cache tables should be gone")
        print("  2. Test Knowledge Graph - should still work")
        print("  3. If issues occur, restore from backup")
        print()
        
        return 0
        
    except Exception as e:
        print(f"[!] ERROR during migration: {e}")
        print(f"Backup available at: {backup_db}")
        return 1
        
    finally:
        source_conn.close()
        target_conn.close()


if __name__ == '__main__':
    sys.exit(main())