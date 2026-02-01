"""
Drop Old Graph Cache Tables

Removes redundant graph_schema_* tables after cache consolidation.
These tables are no longer used after v3.19.

Tables to drop:
- graph_schema_nodes
- graph_schema_edges  
- graph_schema_node_properties

@author P2P Development Team
@version 1.0.0
"""

import sqlite3
import sys
from pathlib import Path

# Windows encoding fix
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))


def drop_old_tables(db_path: str = 'app/database/p2p_data_products.db'):
    """
    Drop old graph cache tables
    
    Args:
        db_path: Path to SQLite database
    """
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    old_tables = [
        'graph_schema_nodes',
        'graph_schema_edges',
        'graph_schema_node_properties',
        'graph_ontology_metadata'
    ]
    
    print(f"Checking for old graph cache tables in {db_path}...")
    
    # Check which tables exist
    cursor.execute("""
        SELECT name FROM sqlite_master 
        WHERE type='table' AND (name LIKE 'graph_schema_%' OR name = 'graph_ontology_metadata')
        ORDER BY name
    """)
    
    existing_tables = [row[0] for row in cursor.fetchall()]
    
    if not existing_tables:
        print("[OK] No old graph cache tables found - database is clean!")
        conn.close()
        return
    
    print(f"\nFound {len(existing_tables)} old tables:")
    for table in existing_tables:
        # Get row count
        cursor.execute(f"SELECT COUNT(*) FROM {table}")
        count = cursor.fetchone()[0]
        print(f"  - {table}: {count} rows")
    
    # Drop tables
    print("\nDropping old tables...")
    for table in old_tables:
        if table in existing_tables:
            cursor.execute(f"DROP TABLE IF EXISTS {table}")
            print(f"  [OK] Dropped {table}")
    
    conn.commit()
    conn.close()
    
    print("\n[SUCCESS] Old graph cache tables removed successfully!")
    print("Database now uses unified cache (graph_ontology, graph_nodes, graph_edges)")


if __name__ == '__main__':
    drop_old_tables()