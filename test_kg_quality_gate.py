"""
Knowledge Graph Quality Gate

Validates that Data Mode graph generation will succeed without duplicate node errors.
Similar to module_quality_gate.py but for graph data quality.

Tests:
1. PK detection works for all tables
2. No duplicate node IDs generated
3. Compound keys properly handled
"""

import sqlite3
from collections import defaultdict
from modules.knowledge_graph.backend.data_graph_service import DataGraphService
from modules.sqlite_connection.backend.sqlite_data_source import SQLiteDataSource

def test_kg_quality():
    """Test knowledge graph quality"""
    
    print("=" * 80)
    print("KNOWLEDGE GRAPH QUALITY GATE")
    print("=" * 80)
    
    # Initialize service
    data_source = SQLiteDataSource(db_path='app/database/p2p_data_products.db')
    kg_service = DataGraphService(data_source)
    
    # Get all tables
    products = data_source.get_data_products()
    all_tables = []
    
    for product in products:
        schema = product.get('schemaName', product.get('productName'))
        tables = data_source.get_tables(schema)
        for table in tables:
            table_name = table.get('TABLE_NAME')
            if table_name:
                all_tables.append({'schema': schema, 'table': table_name})
    
    print(f"\nFound {len(all_tables)} tables to validate\n")
    
    failures = []
    warnings = []
    
    # Test 1: PK Detection
    print("TEST 1: Primary Key Detection")
    print("-" * 80)
    
    pk_map = {}
    for table_info in all_tables:
        schema = table_info['schema']
        table_name = table_info['table']
        
        try:
            structure = data_source.get_table_structure(schema, table_name)
            pk_cols = kg_service._find_pk_columns(structure, table_name)
            pk_map[table_name] = pk_cols
            
            if len(pk_cols) > 1:
                print(f"[OK] {table_name}: COMPOUND KEY {pk_cols}")
            else:
                print(f"  {table_name}: {pk_cols[0]}")
                
        except Exception as e:
            failures.append(f"PK detection failed for {table_name}: {e}")
            print(f"[ERR] {table_name}: ERROR - {e}")
    
    # Test 2: Duplicate Node ID Detection
    print("\n\nTEST 2: Duplicate Node ID Detection")
    print("-" * 80)
    
    node_id_tracker = defaultdict(list)  # {node_id: [table_names]}
    
    for table_info in all_tables:
        schema = table_info['schema']
        table_name = table_info['table']
        pk_cols = pk_map.get(table_name, [table_name])
        
        try:
            # Get sample data
            query = f"SELECT * FROM {table_name} LIMIT 20"
            result = data_source.execute_query(query)
            records = result.get('data') or result.get('rows', [])
            
            if not records:
                continue
            
            # Generate node IDs using same logic as service
            for record in records:
                pk_values = []
                for pk_col in pk_cols:
                    val = record.get(pk_col)
                    if val is not None:
                        pk_values.append(str(val))
                
                if not pk_values:
                    warnings.append(f"{table_name}: Record with no PK value")
                    continue
                
                compound_key = '-'.join(pk_values)
                node_id = f"record-{schema}-{table_name}-{compound_key}"
                
                # Track node ID
                node_id_tracker[node_id].append(table_name)
        
        except Exception as e:
            warnings.append(f"Could not test {table_name}: {e}")
    
    # Check for duplicates
    duplicates_found = False
    for node_id, tables in node_id_tracker.items():
        if len(tables) > 1:
            duplicates_found = True
            failures.append(f"DUPLICATE NODE ID: {node_id} appears in {tables}")
            print(f"[ERR] DUPLICATE: {node_id}")
            print(f"  Tables: {tables}")
    
    if not duplicates_found:
        print("[OK] No duplicate node IDs detected")
    
    # Test 3: Compound Key Coverage
    print("\n\nTEST 3: Compound Key Pattern Coverage")
    print("-" * 80)
    
    compound_tables = {name: cols for name, cols in pk_map.items() if len(cols) > 1}
    
    if compound_tables:
        print(f"Found {len(compound_tables)} tables with compound keys:")
        for table, cols in compound_tables.items():
            print(f"  - {table}: {' + '.join(cols)}")
    else:
        warnings.append("No compound keys detected - may need more pattern definitions")
    
    # Summary
    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    
    print(f"\nTables tested: {len(all_tables)}")
    print(f"Compound keys: {len(compound_tables)}")
    print(f"Total node IDs: {len(node_id_tracker)}")
    print(f"Warnings: {len(warnings)}")
    print(f"Failures: {len(failures)}")
    
    if warnings:
        print("\nWARNINGS:")
        for w in warnings:
            print(f"  [!] {w}")
    
    if failures:
        print("\nFAILURES:")
        for f in failures:
            print(f"  [X] {f}")
        print("\n[FAIL] QUALITY GATE: FAILED")
        return False
    else:
        print("\n[PASS] QUALITY GATE: PASSED")
        return True

if __name__ == '__main__':
    success = test_kg_quality()
    exit(0 if success else 1)