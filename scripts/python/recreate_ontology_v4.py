#!/usr/bin/env python3
"""Recreate ontology schema with composite primary key"""
import sqlite3

conn = sqlite3.connect('app/p2p_data.db')
cursor = conn.cursor()

# Drop old tables
cursor.execute('DROP TABLE IF EXISTS graph_edges')
cursor.execute('DROP TABLE IF EXISTS graph_nodes')
cursor.execute('DROP TABLE IF EXISTS graph_ontology')
cursor.execute('DROP VIEW IF EXISTS v_ontology_summary')
conn.commit()
print('Old tables dropped')

# Create new schema
script = open('scripts/sql/sqlite_old/create_graph_ontology_tables_v4.sql', 'r', encoding='utf-8').read()
cursor.executescript(script)
conn.commit()
print('New composite PK schema created')

# Verify
cursor.execute('SELECT data_source, mode, description FROM graph_ontology')
rows = cursor.fetchall()
print('\nData combinations:')
for row in rows:
    print(f'  {row[0]} + {row[1]}: {row[2]}')

conn.close()
print('\nSchema v4.0 created successfully!')