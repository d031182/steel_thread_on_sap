#!/usr/bin/env python3
"""
Migrate Graph Cache Schema to v3.13

Adds columns needed for full graph node caching.
Safe to run multiple times (uses ADD COLUMN IF NOT EXISTS pattern).
"""

import sys
import sqlite3
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))


def migrate_database(db_path: str):
    """Apply v3.13 migration to database"""
    
    print("=" * 70)
    print("GRAPH CACHE SCHEMA MIGRATION (v3.13)")
    print("=" * 70)
    print(f"\nDatabase: {db_path}\n")
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Check current schema version
        cursor.execute("""
            SELECT value FROM graph_ontology_metadata 
            WHERE key = 'schema_version'
        """)
        current_version = cursor.fetchone()
        print(f"Current schema version: {current_version[0] if current_version else 'unknown'}")
        
        # Add graph_mode column
        print("\n1. Adding graph_mode column...")
        try:
            cursor.execute("""
                ALTER TABLE graph_schema_nodes 
                ADD COLUMN graph_mode TEXT CHECK(graph_mode IN ('schema', 'data'))
            """)
            print("   ✓ Added graph_mode column")
        except sqlite3.OperationalError as e:
            if "duplicate column" in str(e).lower():
                print("   → Already exists (skipping)")
            else:
                raise
        
        # Add metadata_json column
        print("\n2. Adding metadata_json column...")
        try:
            cursor.execute("""
                ALTER TABLE graph_schema_nodes 
                ADD COLUMN metadata_json TEXT
            """)
            print("   ✓ Added metadata_json column")
        except sqlite3.OperationalError as e:
            if "duplicate column" in str(e).lower():
                print("   → Already exists (skipping)")
            else:
                raise
        
        # Add visual_properties_json column
        print("\n3. Adding visual_properties_json column...")
        try:
            cursor.execute("""
                ALTER TABLE graph_schema_nodes 
                ADD COLUMN visual_properties_json TEXT
            """)
            print("   ✓ Added visual_properties_json column")
        except sqlite3.OperationalError as e:
            if "duplicate column" in str(e).lower():
                print("   → Already exists (skipping)")
            else:
                raise
        
        # Update schema version
        print("\n4. Updating metadata...")
        cursor.execute("""
            UPDATE graph_ontology_metadata 
            SET value = '1.1.0', updated_at = CURRENT_TIMESTAMP
            WHERE key = 'schema_version'
        """)
        
        cursor.execute("""
            INSERT OR REPLACE INTO graph_ontology_metadata (key, value) 
            VALUES 
                ('cache_version', '3.13'),
                ('cache_enabled', 'true')
        """)
        print("   ✓ Updated metadata")
        
        conn.commit()
        
        # Verify migration
        print("\n5. Verifying migration...")
        cursor.execute("PRAGMA table_info(graph_schema_nodes)")
        columns = cursor.fetchall()
        column_names = [col[1] for col in columns]
        
        required = ['graph_mode', 'metadata_json', 'visual_properties_json']
        missing = [col for col in required if col not in column_names]
        
        if missing:
            print(f"   ✗ Missing columns: {missing}")
            return 1
        else:
            print(f"   ✓ All required columns present")
        
        print("\n" + "=" * 70)
        print("MIGRATION SUCCESSFUL")
        print("=" * 70)
        print("\nGraph cache v3.13 is now ready to use!")
        print("Next: Test with 'python scripts/python/test_full_graph_cache.py'")
        
        return 0
        
    except Exception as e:
        conn.rollback()
        print(f"\nERROR during migration: {e}")
        import traceback
        traceback.print_exc()
        return 1
    finally:
        conn.close()


if __name__ == '__main__':
    db_path = 'app/database/p2p_data_products.db'
    
    if len(sys.argv) > 1:
        db_path = sys.argv[1]
    
    exit_code = migrate_database(db_path)
    sys.exit(exit_code)