"""
Create Graph Cache Tables v5
Executes the v5 schema to create the new 3-table architecture
"""
import sqlite3
import sys
from pathlib import Path

def create_tables():
    """Create graph cache tables v5"""
    try:
        # Get project root
        script_dir = Path(__file__).parent
        project_root = script_dir.parent.parent
        
        # Paths
        db_path = project_root / "p2p_data.db"
        sql_path = project_root / "sql" / "sqlite" / "create_graph_cache_tables_v5.sql"
        
        print(f"Database: {db_path}")
        print(f"SQL File: {sql_path}")
        
        # Read SQL
        with open(sql_path, 'r', encoding='utf-8') as f:
            sql_script = f.read()
        
        # Execute
        conn = sqlite3.connect(str(db_path))
        conn.executescript(sql_script)
        conn.commit()
        
        # Verify tables created
        cursor = conn.cursor()
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name LIKE 'graph_%'
            ORDER BY name
        """)
        tables = cursor.fetchall()
        
        print("\nTables created:")
        for table in tables:
            print(f"  - {table[0]}")
        
        # Verify foreign keys enabled
        cursor.execute("PRAGMA foreign_keys")
        fk_status = cursor.fetchone()[0]
        print(f"\nForeign keys: {'ENABLED' if fk_status else 'DISABLED'}")
        
        conn.close()
        
        print("\nSUCCESS: Graph cache tables v5 created")
        return 0
        
    except Exception as e:
        print(f"\nERROR: {e}", file=sys.stderr)
        return 1

if __name__ == "__main__":
    sys.exit(create_tables())