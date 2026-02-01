#!/usr/bin/env python3
"""
Migrate Graph Cache Schema to v3.13 - Metadata Approach

Uses existing graph_ontology_metadata table as key-value store.
No new tables or columns needed!
"""

import sys
import sqlite3
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))


def migrate_database(db_path: str):
    """Apply v3.13 migration using metadata table"""
    
    print("=" * 70)
    print("GRAPH CACHE SCHEMA MIGRATION (v3.13) - Metadata Approach")
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
        
        # Add cache keys to metadata table
        print("\n1. Adding cache keys to graph_ontology_metadata...")
        cursor.execute("""
            INSERT OR REPLACE INTO graph_ontology_metadata (key, value) VALUES
                ('cache_schema_nodes', NULL),
                ('cache_schema_edges', NULL),
                ('cache_data_nodes', NULL),
                ('cache_data_edges', NULL),
                ('cache_schema_updated', NULL),
                ('cache_data_updated', NULL),
                ('cache_version', '3.13'),
                ('cache_enabled', 'true')
        """)
        print("   ✓ Added 8 cache keys")
        
        # Update schema version
        print("\n2. Updating schema version...")
        cursor.execute("""
            UPDATE graph_ontology_metadata 
            SET value = '1.1.0', updated_at = CURRENT_TIMESTAMP
            WHERE key = 'schema_version'
        """)
        print("   ✓ Updated to version 1.1.0")
        
        conn.commit()
        
        # Verify migration
        print("\n3. Verifying migration...")
        cursor.execute("""
            SELECT key FROM graph_ontology_metadata 
            WHERE key LIKE 'cache_%'
        """)
        cache_keys = cursor.fetchall()
        
        expected_keys = [
            'cache_schema_nodes',
            'cache_schema_edges', 
            'cache_data_nodes',
            'cache_data_edges',
            'cache_schema_updated',
            'cache_data_updated',
            'cache_version',
            'cache_enabled'
        ]
        
        found_keys = [row[0] for row in cache_keys]
        missing = [key for key in expected_keys if key not in found_keys]
        
        if missing:
            print(f"   ✗ Missing keys: {missing}")
            return 1
        else:
            print(f"   ✓ All {len(cache_keys)} cache keys present")
        
        print("\n" + "=" * 70)
        print("MIGRATION SUCCESSFUL")
        print("=" * 70)
        print("\nBenefits of metadata approach:")
        print("  ✓ No new tables needed")
        print("  ✓ Simple key-value storage")
        print("  ✓ Entire graph cached as JSON")
        print("  ✓ Single SELECT for instant load")
        print("\nNext: Run app and test graph visualization!")
        
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