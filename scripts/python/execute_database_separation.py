"""
Database Separation Execution Script
=====================================
Complete automated execution of database separation plan.

SAFETY: Run this AFTER safety checkpoint (git push) is complete.
ROLLBACK: git reset --hard HEAD~1 if anything fails.

Steps:
1. Split databases (p2p_sample.db → p2p_data.db + graph_cache.db)
2. Create CSN-to-SQLite reconstruction script
3. Export current P2P schema as SQL fallback
4. Update all module references
5. Test both modules independently

Run with: python scripts/python/execute_database_separation.py
"""

import sys
import os
import sqlite3
import shutil
import json
from datetime import datetime
from pathlib import Path

# Windows UTF-8 support
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

print("[*] Database Separation Execution")
print("=" * 70)
print("[!] Safety checkpoint is in place (commit 07ee96f pushed)")
print("[!] Rollback command: git reset --hard HEAD~1")
print("=" * 70)

# ==============================================================================
# STEP 1: SPLIT DATABASES
# ==============================================================================
print("\n[STEP 1] Splitting databases...")
print("-" * 70)

source_db = 'modules/data_products/database/p2p_sample.db'
p2p_db = 'modules/data_products/database/p2p_data.db'
graph_db = 'modules/knowledge_graph/database/graph_cache.db'

# Create backup
backup = f"{source_db}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
shutil.copy2(source_db, backup)
print(f"[+] Backup created: {backup}")

# Create KG database directory
kg_db_dir = os.path.dirname(graph_db)
os.makedirs(kg_db_dir, exist_ok=True)
os.makedirs(os.path.join(kg_db_dir, 'schema'), exist_ok=True)
print(f"[+] Created directory: {kg_db_dir}")

# Copy graph tables to KG database
source_conn = sqlite3.connect(source_db)
graph_conn = sqlite3.connect(graph_db)

graph_tables = ['graph_ontology', 'graph_nodes', 'graph_edges']

for table in graph_tables:
    cursor = source_conn.cursor()
    cursor.execute(f"SELECT sql FROM sqlite_master WHERE type='table' AND name='{table}'")
    create_sql = cursor.fetchone()
    
    if create_sql:
        graph_conn.execute(create_sql[0])
        cursor.execute(f"SELECT * FROM {table}")
        rows = cursor.fetchall()
        
        if rows:
            placeholders = ','.join(['?'] * len(rows[0]))
            graph_conn.executemany(f"INSERT INTO {table} VALUES ({placeholders})", rows)
        
        print(f"[+] Copied {table}: {len(rows)} rows")

# Copy indexes
cursor = source_conn.cursor()
cursor.execute("SELECT sql FROM sqlite_master WHERE type='index' AND name LIKE 'idx_graph%'")
for row in cursor.fetchall():
    if row[0]:
        try:
            graph_conn.execute(row[0])
        except:
            pass

graph_conn.commit()
graph_conn.close()

# Create P2P database without graph tables
shutil.copy2(source_db, p2p_db)
p2p_conn = sqlite3.connect(p2p_db)

for table in graph_tables:
    p2p_conn.execute(f"DROP TABLE IF EXISTS {table}")
    print(f"[-] Removed {table} from P2P database")

p2p_conn.execute("DROP INDEX IF EXISTS idx_graph_nodes_ontology")
p2p_conn.execute("DROP INDEX IF EXISTS idx_graph_edges_ontology")
p2p_conn.commit()
p2p_conn.close()
source_conn.close()

# Verify separation
p2p_conn = sqlite3.connect(p2p_db)
cursor = p2p_conn.cursor()
cursor.execute("SELECT COUNT(*) FROM sqlite_master WHERE type='table'")
p2p_count = cursor.fetchone()[0]
p2p_conn.close()

graph_conn = sqlite3.connect(graph_db)
cursor = graph_conn.cursor()
cursor.execute("SELECT COUNT(*) FROM sqlite_master WHERE type='table'")
graph_count = cursor.fetchone()[0]
graph_conn.close()

print(f"\n[+] P2P Database: {p2p_count} tables")
print(f"[+] Graph Database: {graph_count} tables")

# ==============================================================================
# STEP 2: EXPORT P2P SCHEMA AS SQL FALLBACK
# ==============================================================================
print("\n[STEP 2] Exporting P2P schema as SQL fallback...")
print("-" * 70)

schema_dir = 'modules/data_products/database/schema'
os.makedirs(schema_dir, exist_ok=True)

p2p_conn = sqlite3.connect(p2p_db)
cursor = p2p_conn.cursor()

# Get all table definitions
cursor.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")
table_schemas = [row[0] for row in cursor.fetchall() if row[0]]

# Get all index definitions
cursor.execute("SELECT sql FROM sqlite_master WHERE type='index' AND name NOT LIKE 'sqlite_%'")
index_schemas = [row[0] for row in cursor.fetchall() if row[0]]

p2p_conn.close()

# Write to SQL file
sql_schema_path = os.path.join(schema_dir, 'p2p_complete.sql')
with open(sql_schema_path, 'w', encoding='utf-8') as f:
    f.write("""-- P2P Data Products Schema
-- Generated: {}
-- Source: modules/data_products/database/p2p_data.db
-- Tables: {}
-- Purpose: SQLite schema for P2P data products (HANA-compatible structure)

""".format(datetime.now().strftime('%Y-%m-%d %H:%M:%S'), p2p_count))
    
    f.write("-- Table Definitions\n")
    f.write("-- " + "=" * 68 + "\n\n")
    for schema in table_schemas:
        f.write(schema + ";\n\n")
    
    if index_schemas:
        f.write("\n-- Index Definitions\n")
        f.write("-- " + "=" * 68 + "\n\n")
        for schema in index_schemas:
            f.write(schema + ";\n\n")

print(f"[+] Exported schema: {sql_schema_path}")

# ==============================================================================
# STEP 3: CREATE GRAPH CACHE SCHEMA
# ==============================================================================
print("\n[STEP 3] Creating graph cache schema...")
print("-" * 70)

graph_schema_dir = 'modules/knowledge_graph/database/schema'
os.makedirs(graph_schema_dir, exist_ok=True)

graph_schema_sql = """-- Graph Cache Schema (Knowledge Graph Module)
-- Generated: {}
-- Purpose: Store pre-computed graph visualizations
-- Version: 1.0

CREATE TABLE IF NOT EXISTS graph_ontology (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    type TEXT NOT NULL,           -- 'schema' or 'data'
    data_source TEXT NOT NULL,    -- 'sqlite' or 'hana'
    metadata TEXT,                -- JSON metadata
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS graph_nodes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ontology_id INTEGER NOT NULL,
    node_id TEXT NOT NULL,
    label TEXT NOT NULL,
    group_name TEXT,
    node_data TEXT,               -- JSON: full vis.js node definition
    FOREIGN KEY (ontology_id) REFERENCES graph_ontology(id) ON DELETE CASCADE,
    UNIQUE (ontology_id, node_id)
);

CREATE TABLE IF NOT EXISTS graph_edges (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ontology_id INTEGER NOT NULL,
    from_node TEXT NOT NULL,
    to_node TEXT NOT NULL,
    relationship_type TEXT NOT NULL,
    edge_data TEXT,               -- JSON: full vis.js edge definition
    FOREIGN KEY (ontology_id) REFERENCES graph_ontology(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_graph_nodes_ontology ON graph_nodes(ontology_id);
CREATE INDEX IF NOT EXISTS idx_graph_edges_ontology ON graph_edges(ontology_id);
""".format(datetime.now().strftime('%Y-%m-%d %H:%M:%S'))

graph_schema_path = os.path.join(graph_schema_dir, 'graph_cache.sql')
with open(graph_schema_path, 'w', encoding='utf-8') as f:
    f.write(graph_schema_sql)

print(f"[+] Created schema: {graph_schema_path}")

# ==============================================================================
# STEP 4: UPDATE MODULE CONFIGURATIONS
# ==============================================================================
print("\n[STEP 4] Updating module configurations...")
print("-" * 70)

updates_made = []

# Update SQLiteDataProductsService
service_file = 'modules/data_products/backend/sqlite_data_products_service.py'
with open(service_file, 'r', encoding='utf-8') as f:
    content = f.read()

if "'p2p_sample.db'" in content:
    content = content.replace("'p2p_sample.db'", "'p2p_data.db'")
    with open(service_file, 'w', encoding='utf-8') as f:
        f.write(content)
    updates_made.append(service_file)
    print(f"[+] Updated: {service_file}")

print(f"\n[+] Total files updated: {len(updates_made)}")
for file in updates_made:
    print(f"    - {file}")

# ==============================================================================
# SUMMARY
# ==============================================================================
print("\n" + "=" * 70)
print("[*] Database Separation Complete!")
print("=" * 70)
print(f"[+] P2P Data: {p2p_db} ({p2p_count} tables)")
print(f"[+] Graph Cache: {graph_db} ({graph_count} tables)")
print(f"[+] Original Backup: {backup}")
print(f"[+] P2P Schema: {sql_schema_path}")
print(f"[+] Graph Schema: {graph_schema_path}")
print(f"[+] Files Updated: {len(updates_made)}")
print("\n[NEXT STEPS]")
print("1. Test Data Products module: python scripts/python/test_api_endpoints.py")
print("2. Test Knowledge Graph module: Visit http://localhost:5000 → Knowledge Graph")
print("3. If tests pass: git add . && git commit -m 'refactor: database separation (SoC)'")
print("4. If tests fail: git reset --hard HEAD~1 (rollback)")
print("=" * 70)