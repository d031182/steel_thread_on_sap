"""
Clean up database/p2p_data.db - remove graph tables that don't belong

This script drops graph-related tables from database/p2p_data.db:
- graph_edges
- graph_nodes
- graph_ontology

These tables should only exist in database/p2p_graph.db for the Knowledge Graph module.
All P2P business data (PurchaseOrder, Supplier, Product, etc.) stays in p2p_data.db.
"""

import sqlite3
from pathlib import Path

# Tables to DROP (graph tables don't belong here)
DROP_TABLES = {
    'graph_edges',
    'graph_nodes',
    'graph_ontology'
}

def cleanup_p2p_data_database():
    """Remove graph tables from p2p_data.db"""
    
    db_path = Path('database/p2p_data.db')
    
    if not db_path.exists():
        print(f"❌ Database not found: {db_path}")
        return
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Get all tables
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    all_tables = [row[0] for row in cursor.fetchall()]
    
    print(f"📊 Found {len(all_tables)} tables in {db_path}")
    
    # Identify graph tables that need to be dropped
    tables_to_drop = [t for t in all_tables if t in DROP_TABLES]
    
    if not tables_to_drop:
        print("✅ No graph tables found - database is already clean!")
        conn.close()
        return
    
    print(f"\n🗑️  Dropping {len(tables_to_drop)} graph tables (they belong in p2p_graph.db):")
    
    # Drop each graph table
    for table in sorted(tables_to_drop):
        try:
            cursor.execute(f"DROP TABLE IF EXISTS {table}")
            print(f"  ✓ Dropped: {table}")
        except Exception as e:
            print(f"  ✗ Error dropping {table}: {e}")
    
    conn.commit()
    
    # Verify final state
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    remaining_tables = [row[0] for row in cursor.fetchall()]
    
    print(f"\n✅ Cleanup complete!")
    print(f"📊 Remaining tables: {len(remaining_tables)} (all P2P business data)")
    
    # Verify no graph tables remain
    remaining_graph = set(remaining_tables) & DROP_TABLES
    if remaining_graph:
        print(f"⚠️  Warning: Graph tables still present: {remaining_graph}")
    else:
        print(f"✓ Confirmed: No graph tables remain (correct!)")
    
    conn.close()

if __name__ == '__main__':
    cleanup_p2p_data_database()