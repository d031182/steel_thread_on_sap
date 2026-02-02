"""Check schema graph relationships in database."""
import sqlite3

conn = sqlite3.connect('app/p2p_data.db')
cursor = conn.cursor()

# Count relationships
cursor.execute('SELECT COUNT(*) FROM graph_schema_relationships')
count = cursor.fetchone()[0]
print(f'\n✅ Total Relationships: {count}')

# Show sample relationships
cursor.execute('''
    SELECT source_entity, target_entity, relationship_type, relationship_label
    FROM graph_schema_relationships 
    LIMIT 10
''')
print('\n📊 Sample Relationships:')
for row in cursor.fetchall():
    source, target, rel_type, label = row
    print(f'  {source} --[{rel_type}: {label}]--> {target}')

# Check if we have CSN-derived relationships
cursor.execute('''
    SELECT COUNT(*) 
    FROM graph_schema_relationships 
    WHERE source_table LIKE 'C_%'
''')
csn_count = cursor.fetchone()[0]
print(f'\n📋 CSN-derived relationships: {csn_count}')

conn.close()