#!/usr/bin/env python3
"""
Initialize Graph Ontology Schema

Creates tables for persisting graph ontologies in SQLite.
Aligns with HANA Property Graph engine architecture.
"""

import sqlite3
from pathlib import Path

DB_PATH = 'app/database/p2p_data_products.db'
SQL_PATH = 'sql/sqlite/create_graph_ontology_tables.sql'

print("="*80)
print("Initialize Graph Ontology Schema")
print("="*80)
print(f"\nDatabase: {DB_PATH}")
print(f"SQL Script: {SQL_PATH}\n")

# Read SQL script
with open(SQL_PATH, 'r', encoding='utf-8') as f:
    sql_script = f.read()

# Connect and execute
conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

try:
    # Execute the entire script
    cursor.executescript(sql_script)
    conn.commit()
    
    # Verify tables created
    cursor.execute("""
        SELECT name FROM sqlite_master 
        WHERE type='table' AND name LIKE 'graph_%'
        ORDER BY name
    """)
    tables = [row[0] for row in cursor.fetchall()]
    
    cursor.execute("""
        SELECT name FROM sqlite_master 
        WHERE type='view' AND name LIKE 'v_graph_%'
        ORDER BY name
    """)
    views = [row[0] for row in cursor.fetchall()]
    
    print("[OK] Schema created successfully!\n")
    print("Tables created:")
    for table in tables:
        print(f"  - {table}")
    
    print("\nViews created:")
    for view in views:
        print(f"  - {view}")
    
    # Show metadata
    cursor.execute("SELECT key, value FROM graph_ontology_metadata")
    metadata = cursor.fetchall()
    
    print("\nInitial metadata:")
    for key, value in metadata:
        print(f"  - {key}: {value}")
    
    print("\n" + "="*80)
    print("[SUCCESS] Graph ontology schema ready!")
    print("="*80)
    print("\nNext: Run migration script to populate from CSN")
    
except Exception as e:
    print(f"[ERROR] Failed to create schema: {e}")
    conn.rollback()
finally:
    conn.close()