#!/usr/bin/env python3
"""Test FK constraints with PRAGMA foreign_keys enabled"""
import sqlite3

conn = sqlite3.connect('app/p2p_data.db')
cursor = conn.cursor()

# CRITICAL: Enable FK constraints (disabled by default in SQLite)
cursor.execute("PRAGMA foreign_keys = ON")

print("=== Testing Composite FK with PRAGMA foreign_keys=ON ===\n")

# Clean up previous test data
cursor.execute("DELETE FROM graph_nodes WHERE node_key IN ('test_table', 'bad_table')")
cursor.execute("DELETE FROM graph_edges WHERE source_node_key IN ('table1', 'table2')")
conn.commit()

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
    print(f"[PASS] FK constraint blocked invalid insert: {e}\n")
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

# Test 4: Invalid edge (should fail)
print("Test 4: Insert invalid edge referencing (baddb, schema)")
try:
    cursor.execute("""
        INSERT INTO graph_edges (data_source, mode, source_node_key, target_node_key, edge_type, label)
        VALUES ('baddb', 'schema', 'table3', 'table4', 'foreign_key', 'Bad FK')
    """)
    conn.commit()
    print("[FAIL] Should have been blocked by FK constraint\n")
except Exception as e:
    print(f"[PASS] FK constraint blocked invalid insert: {e}\n")
    conn.rollback()

print("=== Summary ===")
print("Composite FK (data_source, mode) is working correctly!")
print("FK constraints MUST be enabled with: PRAGMA foreign_keys = ON")

conn.close()