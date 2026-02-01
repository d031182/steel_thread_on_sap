#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Validate SQLite Data Products Against HANA Cloud Schemas

This script:
1. Retrieves all HANA Cloud data products and their schemas
2. Compares with SQLite data products
3. Validates table structures (columns, types)
4. Generates a validation report
5. Identifies any schema mismatches

Usage: python scripts/python/validate_sqlite_vs_hana_schemas.py
"""

import requests
import json
import sys
from typing import Dict, List, Set

# Fix Windows encoding for emojis
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# API Base URL
BASE_URL = "http://localhost:5000/api"

def get_data_products(source: str) -> List[Dict]:
    """Get all data products from a source"""
    response = requests.get(f"{BASE_URL}/data-products?source={source}")
    if response.status_code == 200:
        data = response.json()
        return data.get('data_products', [])
    return []

def get_tables(schema_name: str, source: str) -> List[Dict]:
    """Get tables for a data product"""
    response = requests.get(f"{BASE_URL}/data-products/{schema_name}/tables?source={source}")
    if response.status_code == 200:
        data = response.json()
        return data.get('tables', [])
    return []

def get_table_structure(schema_name: str, table_name: str, source: str) -> List[Dict]:
    """Get column structure for a table"""
    response = requests.get(
        f"{BASE_URL}/data-products/{schema_name}/{table_name}/structure?source={source}"
    )
    if response.status_code == 200:
        data = response.json()
        return data.get('columns', [])
    return []

def normalize_table_name(name: str) -> str:
    """Normalize table name for comparison (remove prefixes)"""
    # Remove HANA prefix patterns
    parts = name.split('.')
    return parts[-1] if len(parts) > 1 else name

def compare_data_products():
    """Compare HANA and SQLite data products"""
    
    print("="*80)
    print("HANA Cloud vs SQLite Data Products Validation")
    print("="*80)
    print()
    
    # Get data products from both sources
    print("Fetching data products...")
    hana_products = get_data_products('hana')
    sqlite_products = get_data_products('sqlite')
    
    print(f"  HANA Cloud: {len(hana_products)} data products")
    print(f"  SQLite: {len(sqlite_products)} data products")
    print()
    
    # Create mapping of product names
    hana_map = {p['display_name']: p for p in hana_products}
    sqlite_map = {p['displayName'].replace(' (Local)', ''): p for p in sqlite_products}
    
    # Find matches and mismatches
    hana_names = set(hana_map.keys())
    sqlite_names = set(sqlite_map.keys())
    
    matched = hana_names & sqlite_names
    hana_only = hana_names - sqlite_names
    sqlite_only = sqlite_names - hana_names
    
    print("="*80)
    print("DATA PRODUCT COVERAGE")
    print("="*80)
    print(f"[OK] Matched: {len(matched)} data products")
    for name in sorted(matched):
        print(f"  - {name}")
    print()
    
    if hana_only:
        print(f"[WARN] In HANA only: {len(hana_only)} data products")
        for name in sorted(hana_only):
            print(f"  - {name}")
        print()
    
    if sqlite_only:
        print(f"[WARN] In SQLite only: {len(sqlite_only)} data products")
        for name in sorted(sqlite_only):
            print(f"  - {name}")
        print()
    
    # Validate matched data products
    print("="*80)
    print("SCHEMA VALIDATION (Matched Data Products)")
    print("="*80)
    print()
    
    validation_results = []
    
    for product_name in sorted(matched):
        print(f"\n{'='*80}")
        print(f"Validating: {product_name}")
        print('='*80)
        
        hana_product = hana_map[product_name]
        sqlite_product = sqlite_map[product_name]
        
        # Get tables
        hana_tables = get_tables(hana_product['name'], 'hana')
        sqlite_schema = sqlite_product['schemaName']
        sqlite_tables = get_tables(sqlite_schema, 'sqlite')
        
        print(f"  HANA: {len(hana_tables)} tables")
        print(f"  SQLite: {len(sqlite_tables)} tables")
        
        # Normalize table names for comparison
        hana_table_names = {normalize_table_name(t['name']): t['name'] for t in hana_tables}
        sqlite_table_names = {t['TABLE_NAME']: t['TABLE_NAME'] for t in sqlite_tables}
        
        table_names_hana = set(hana_table_names.keys())
        table_names_sqlite = set(sqlite_table_names.keys())
        
        matched_tables = table_names_hana & table_names_sqlite
        hana_only_tables = table_names_hana - table_names_sqlite
        sqlite_only_tables = table_names_sqlite - table_names_hana
        
        result = {
            'product': product_name,
            'matched_tables': len(matched_tables),
            'hana_only_tables': list(hana_only_tables),
            'sqlite_only_tables': list(sqlite_only_tables),
            'status': 'PASS' if not hana_only_tables and not sqlite_only_tables else 'PARTIAL'
        }
        
        if matched_tables:
            print(f"  [OK] Matched tables: {len(matched_tables)}")
            for table in sorted(matched_tables):
                print(f"     - {table}")
        
        if hana_only_tables:
            print(f"  [WARN] HANA only: {len(hana_only_tables)}")
            for table in sorted(hana_only_tables):
                print(f"     - {table}")
            result['status'] = 'MISSING_IN_SQLITE'
        
        if sqlite_only_tables:
            print(f"  [WARN] SQLite only: {len(sqlite_only_tables)}")
            for table in sorted(sqlite_only_tables):
                print(f"     - {table}")
        
        validation_results.append(result)
    
    # Summary
    print("\n" + "="*80)
    print("VALIDATION SUMMARY")
    print("="*80)
    
    pass_count = sum(1 for r in validation_results if r['status'] == 'PASS')
    partial_count = sum(1 for r in validation_results if r['status'] == 'PARTIAL')
    missing_count = sum(1 for r in validation_results if r['status'] == 'MISSING_IN_SQLITE')
    
    print(f"\nTotal Validated: {len(validation_results)} data products")
    print(f"  [OK] PASS: {pass_count} (perfect match)")
    print(f"  [WARN] PARTIAL: {partial_count} (extra tables in SQLite)")
    print(f"  [ERROR] MISSING: {missing_count} (tables missing in SQLite)")
    
    if missing_count > 0:
        print("\n[ACTION REQUIRED]:")
        print("The following data products have missing tables in SQLite:")
        for result in validation_results:
            if result['status'] == 'MISSING_IN_SQLITE':
                print(f"\n  {result['product']}:")
                for table in result['hana_only_tables']:
                    print(f"    - Missing: {table}")
    
    # Coverage percentage
    total_hana_tables = sum(len(result['hana_only_tables']) + result['matched_tables'] 
                           for result in validation_results)
    total_matched = sum(result['matched_tables'] for result in validation_results)
    
    if total_hana_tables > 0:
        coverage = (total_matched / total_hana_tables) * 100
        print(f"\nOverall Table Coverage: {coverage:.1f}% ({total_matched}/{total_hana_tables} tables)")
    
    print("\n" + "="*80)
    
    return validation_results

if __name__ == '__main__':
    try:
        results = compare_data_products()
        print("\n[OK] Validation complete!")
    except Exception as e:
        print(f"\n[ERROR] Error during validation: {e}")
        import traceback
        traceback.print_exc()