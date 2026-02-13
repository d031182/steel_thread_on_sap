"""
Clean up p2p_graph.db - remove P2P data tables that don't belong

This script drops all tables from database/p2p_graph.db except:
- graph_edges
- graph_nodes  
- graph_ontology
- sqlite_sequence

All P2P business data (PurchaseOrder, Supplier, etc.) should be in
modules/sqlite_connection/database/p2p_data.db instead.
"""

import sqlite3
from pathlib import Path

# Tables to KEEP (knowledge graph only)
KEEP_TABLES = {
    'graph_edges',
    'graph_nodes',
    'graph_ontology',
    'sqlite_sequence'
}

def cleanup_graph_database():
    """Remove all non-graph tables from p2p_graph.db"""
    
    db_path = Path('database/p2p_graph.db')
    
    if not db_path.exists():
        print(f"❌ Database not found: {db_path}")
        return
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Get all tables
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    all_tables = [row[0] for row in cursor.fetchall()]
    
    print(f"📊 Found {len(all_tables)} tables in {db_path}")
    print(f"✅ Keeping: {', '.join(sorted(KEEP_TABLES))}")
    
    # Identify tables to drop
    tables_to_drop = [t for t in all_tables if t not in KEEP_TABLES]
    
    if not tables_to_drop:
        print("✅ No tables to drop - database is already clean!")
        conn.close()
        return
    
    print(f"\n🗑️  Dropping {len(tables_to_drop)} unnecessary tables:")
    
    # Drop each table
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
    print(f"📊 Remaining tables ({len(remaining_tables)}): {', '.join(sorted(remaining_tables))}")
    
    # Verify we only have graph tables
    unexpected = set(remaining_tables) - KEEP_TABLES
    if unexpected:
        print(f"⚠️  Warning: Unexpected tables remain: {unexpected}")
    
    conn.close()

if __name__ == '__main__':
    cleanup_graph_database()