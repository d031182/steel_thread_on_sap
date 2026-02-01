#!/usr/bin/env python3
"""
Migrate to Clean Graph Cache Schema

Replaces old tables with new clean design:
- Deletes: graph_schema_nodes, graph_schema_edges, graph_ontology_metadata
- Creates: graph_ontology, graph_nodes, graph_edges

WARNING: This will delete existing graph data!
"""

import sys
import sqlite3
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))


def migrate_database(db_path: str):
    """Replace old schema with clean design"""
    
    print("=" * 70)
    print("GRAPH CACHE CLEAN MIGRATION")
    print("=" * 70)
    print(f"\nDatabase: {db_path}")
    print("\nWARNING: This will delete existing graph tables!")
    print("=" * 70)
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Step 1: Drop old tables
        print("\n1. Dropping old tables...")
        
        old_tables = [
            'graph_schema_nodes',
            'graph_schema_edges', 
            'graph_ontology_metadata'
        ]
        
        for table in old_tables:
            cursor.execute(f"DROP TABLE IF EXISTS {table}")
            print(f"   - Dropped {table}")
        
        # Step 2: Drop old views/triggers
        print("\n2. Cleaning up old objects...")
        cursor.execute("DROP VIEW IF EXISTS v_graph_schema_edges_confident")
        cursor.execute("DROP VIEW IF EXISTS v_graph_schema_edges_verified")
        cursor.execute("DROP VIEW IF EXISTS v_graph_schema_summary")
        cursor.execute("DROP TRIGGER IF EXISTS update_schema_nodes_timestamp")
        cursor.execute("DROP TRIGGER IF EXISTS update_schema_edges_timestamp")
        print("   - Dropped old views and triggers")
        
        # Step 3: Create new clean schema
        print("\n3. Creating new graph cache tables...")
        
        # Read and execute SQL script
        sql_file = project_root / 'sql' / 'sqlite' / 'create_graph_cache_tables.sql'
        with open(sql_file, 'r') as f:
            sql_script = f.read()
        
        cursor.executescript(sql_script)
        print("   - Created graph_ontology")
        print("   - Created graph_nodes")
        print("   - Created graph_edges")
        print("   - Created indexes")
        
        conn.commit()
        
        # Step 4: Verify new schema
        print("\n4. Verifying new schema...")
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name LIKE 'graph_%'
        """)
        tables = cursor.fetchall()
        
        expected = ['graph_ontology', 'graph_nodes', 'graph_edges']
        found = [t[0] for t in tables]
        
        if all(t in found for t in expected):
            print(f"   OK All 3 tables created: {', '.join(found)}")
        else:
            print(f"   ERROR Missing tables: {set(expected) - set(found)}")
            return 1
        
        print("\n" + "=" * 70)
        print("MIGRATION SUCCESSFUL")
        print("=" * 70)
        print("\nNew clean schema ready!")
        print("Next steps:")
        print("  1. Implement CacheBuilder service")
        print("  2. Implement VisJsTranslator service")
        print("  3. Test graph visualization")
        
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
    force = False
    
    # Parse arguments
    for arg in sys.argv[1:]:
        if arg == '--force':
            force = True
        else:
            db_path = arg
    
    if not force:
        print("\nThis will DELETE existing graph tables and create new ones.")
        response = input("Continue? (yes/no): ")
        
        if response.lower() != 'yes':
            print("Migration cancelled.")
            sys.exit(0)
    
    exit_code = migrate_database(db_path)
    sys.exit(exit_code)
