"""
Quick script to check database schema - identify graph cache tables
"""
import sqlite3
import sys
import io

# Fix Windows encoding issue
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

db_path = 'app/p2p_data.db'

try:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Get all tables
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
    all_tables = [row[0] for row in cursor.fetchall()]
    
    print(f"\nDatabase: {db_path}")
    print(f"Total tables: {len(all_tables)}")
    print("\n" + "="*60)
    
    # Show all tables
    print("\nALL TABLES:")
    for table in all_tables:
        print(f"  - {table}")
    
    # Focus on graph tables
    graph_tables = [t for t in all_tables if 'graph' in t.lower()]
    
    print("\n" + "="*60)
    print(f"\nGRAPH-RELATED TABLES ({len(graph_tables)}):")
    
    if graph_tables:
        for table in graph_tables:
            print(f"\n  Table: {table}")
            
            # Get column info
            cursor.execute(f"PRAGMA table_info({table})")
            columns = cursor.fetchall()
            for col in columns:
                col_id, col_name, col_type, not_null, default, pk = col
                pk_marker = " [PK]" if pk else ""
                print(f"      - {col_name}: {col_type}{pk_marker}")
            
            # Get row count
            cursor.execute(f"SELECT COUNT(*) FROM {table}")
            count = cursor.fetchone()[0]
            print(f"      Rows: {count}")
    else:
        print("  WARNING: No graph tables found!")
    
    conn.close()
    print("\n" + "="*60)
    
except Exception as e:
    print(f"ERROR: {e}")
    sys.exit(1)
