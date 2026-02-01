"""
Clear Graph Cache Script

Clears the graph cache after backend refactoring.
The old cache has styling embedded (colors, shapes, fonts).
The new cache will have pure data (semantic types only).

This is a one-time migration script for the v2.0 architecture refactoring.

Usage:
    python scripts/python/clear_graph_cache.py
"""

import sqlite3
import sys
from pathlib import Path

# Windows encoding fix (per docs/knowledge/guidelines/windows-encoding-standard.md)
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

def clear_graph_cache(db_path: str = "app/database/p2p_data_products.db"):
    """
    Clear graph cache tables
    
    Tables to clear:
    - graph_nodes: Contains styled nodes (old format)
    - graph_edges: Contains styled edges (old format)
    - graph_cache_metadata: Cache validity timestamps
    """
    db_full_path = project_root / db_path
    
    if not db_full_path.exists():
        print(f"❌ Database not found: {db_full_path}")
        return False
    
    try:
        conn = sqlite3.connect(str(db_full_path))
        cursor = conn.cursor()
        
        # Clear graph cache tables
        tables_to_clear = ['graph_nodes', 'graph_edges', 'graph_cache_metadata']
        
        for table in tables_to_clear:
            # Check if table exists
            cursor.execute("""
                SELECT name FROM sqlite_master 
                WHERE type='table' AND name=?
            """, (table,))
            
            if cursor.fetchone():
                cursor.execute(f"DELETE FROM {table}")
                rows_deleted = cursor.rowcount
                print(f"✓ Cleared {table}: {rows_deleted} rows deleted")
            else:
                print(f"  {table}: table doesn't exist (skipped)")
        
        conn.commit()
        conn.close()
        
        print("\n✅ Graph cache cleared successfully!")
        print("   Next graph load will rebuild cache with pure data structure.")
        return True
        
    except Exception as e:
        print(f"❌ Error clearing cache: {e}")
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("GRAPH CACHE CLEAR - v2.0 Architecture Refactoring")
    print("=" * 60)
    print("\nClearing cached graph data...")
    print("Reason: Backend now returns pure data (no styling)")
    print()
    
    success = clear_graph_cache()
    
    if success:
        print("\n" + "=" * 60)
        print("NEXT STEPS:")
        print("=" * 60)
        print("1. Start the application: python server.py")
        print("2. Navigate to Knowledge Graph page")
        print("3. Click 'Refresh Cache' button")
        print("4. Verify graph loads with new pure data structure")
        print()
    
    sys.exit(0 if success else 1)