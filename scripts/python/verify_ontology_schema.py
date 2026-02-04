#!/usr/bin/env python3
"""Verify new versioned ontology schema with FK constraints"""
import sqlite3

conn = sqlite3.connect('app/p2p_data.db')
cursor = conn.cursor()

print("=== GRAPH_ONTOLOGY Schema ===")
cursor.execute("PRAGMA table_info(graph_ontology)")
for row in cursor.fetchall():
    print(f"{row[1]}: {row[2]}")

print("\n=== GRAPH_NODES Schema (with FK) ===")
cursor.execute("PRAGMA table_info(graph_nodes)")
for row in cursor.fetchall():
    print(f"{row[1]}: {row[2]}")
    
cursor.execute("PRAGMA foreign_key_list(graph_nodes)")
fks = cursor.fetchall()
print(f"Foreign Keys: {fks}")

print("\n=== GRAPH_EDGES Schema (with FK) ===")
cursor.execute("PRAGMA table_info(graph_edges)")
for row in cursor.fetchall():
    print(f"{row[1]}: {row[2]}")
    
cursor.execute("PRAGMA foreign_key_list(graph_edges)")
fks = cursor.fetchall()
print(f"Foreign Keys: {fks}")

print("\n=== Initial Data ===")
cursor.execute("SELECT ontology_id, version, mode, source, is_active FROM graph_ontology")
for row in cursor.fetchall():
    print(f"ID={row[0]}, version={row[1]}, mode={row[2]}, source={row[3]}, active={row[4]}")

conn.close()
print("\n✓ Schema verification complete!")