#!/usr/bin/env python3
"""Verify composite FK constraints work correctly"""
import sqlite3

conn = sqlite3.connect('app/p2p_data.db')
cursor = conn.cursor()

print("=== Testing Composite FK Constraints ===\n")

# Test 1: Insert valid node (should succeed)
print("Test 1: Insert valid node referencing (sqlite, schema)")
try:
    cursor.execute("""
        INSERT INTO graph_nodes (data_source, mode, node_type, node_key, label)
        VALUES ('sqlite', 'schema', 'table', 'test_table', 'Test Table')
    """)
    conn.commit()
    print("[PASS] Node inserted\n")
except Exception as e:
    print(f"[FAIL] {e}\n")
    conn.rollback()

# Test 2: Insert invalid node (should fail - FK violation)
print("Test 2: Insert invalid node referencing (invalid_source, schema)")
try:
    cursor.execute("""
        INSERT INTO graph_nodes (data_source, mode, node_type, node_key, label)
        VALUES ('invalid_source', 'schema', 'table', 'bad_table', 'Bad Table')
    """)
    conn.commit()
    print("[FAIL] Should have been blocked by FK constraint\n")
except Exception as e:
    print(f"[PASS] FK constraint worked - {e}\n")
    conn.rollback()

# Test 3: Insert valid edge (should succeed)
print("Test 3: Insert valid edge referencing (sqlite, schema)")
try:
    cursor.execute("""
        INSERT INTO graph_edges (data_source, mode, source_node_key, target_node_key, edge_type, label)
        VALUES ('sqlite', 'schema', 'table1', 'table2', 'foreign_key', 'FK_Relation')
    """)
    conn.commit()
    print("[PASS] Edge inserted\n")
except Exception as e:
    print(f"[FAIL] {e}\n")
    conn.rollback()

# Test 4: Verify CASCADE DELETE
print("Test 4: Delete parent (sqlite, data) - children should CASCADE delete")
cursor.execute("SELECT COUNT(*) FROM graph_nodes WHERE data_source='sqlite' AND mode='data'")
before_count = cursor.fetchone()[0]
print(f"  Nodes before: {before_count}")

cursor.execute("DELETE FROM graph_ontology WHERE data_source='sqlite' AND mode='data'")
conn.commit()

cursor.execute("SELECT COUNT(*) FROM graph_nodes WHERE data_source='sqlite' AND mode='data'")
after_count = cursor.fetchone()[0]
print(f"  Nodes after: {after_count}")

if after_count == 0:
    print("[PASS] CASCADE DELETE worked\n")
else:
    print("[FAIL] CASCADE DELETE did not work\n")

# Restore deleted row
cursor.execute("""
    INSERT INTO graph_ontology (data_source, mode, description)
    VALUES ('sqlite', 'data', 'Data graph for SQLite data source')
""")
conn.commit()

# Final summary
print("=== Schema Structure ===")
cursor.execute("PRAGMA table_info(graph_ontology)")
print("\ngraph_ontology:")
for row in cursor.fetchall():
    print(f"  {row[1]}: {row[2]}")

cursor.execute("PRAGMA foreign_key_list(graph_nodes)")
print("\ngraph_nodes FK:")
for row in cursor.fetchall():
    print(f"  {row}")

cursor.execute("PRAGMA foreign_key_list(graph_edges)")
print("\ngraph_edges FK:")
for row in cursor.fetchall():
    print(f"  {row}")

conn.close()
print("\n[DONE] Composite FK verification complete!")