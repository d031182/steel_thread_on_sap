"""
Fix missing graph_ontology table in database
This table is required for cache save operations
"""
import sqlite3
import sys

def create_ontology_table(db_path: str):
    """Create graph_ontology table if missing"""
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Create graph_ontology table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS graph_ontology (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                source_table TEXT NOT NULL,
                source_column TEXT,
                target_table TEXT NOT NULL,
                target_column TEXT,
                relationship_type TEXT NOT NULL,
                confidence REAL DEFAULT 1.0,
                discovery_method TEXT,
                discovered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_validated TIMESTAMP,
                metadata TEXT
            )
        """)
        
        # Create indexes
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_ontology_source 
            ON graph_ontology(source_table)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_ontology_target 
            ON graph_ontology(target_table)
        """)
        
        conn.commit()
        conn.close()
        
        print(f"SUCCESS: graph_ontology table created in {db_path}")
        return True
        
    except Exception as e:
        print(f"ERROR: Failed to create table: {e}")
        return False

if __name__ == "__main__":
    db_path = "modules/knowledge_graph/database/graph_cache.db"
    success = create_ontology_table(db_path)
    sys.exit(0 if success else 1)
