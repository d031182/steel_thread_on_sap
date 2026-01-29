#!/usr/bin/env python3
"""
Create All P2P Data Products in SQLite
Generates schemas and sample data from CSN definitions

Usage: python scripts/python/create_all_data_products.py
"""

import sqlite3
import json
import random
from datetime import datetime, timedelta
from pathlib import Path

# Paths
DB_PATH = Path("app/database/p2p_data_products.db")
CSN_DIR = Path("data-products")

# Ensure database directory exists
DB_PATH.parent.mkdir(parents=True, exist_ok=True)

# Data products to generate (excluding PurchaseOrder - already imported)
DATA_PRODUCTS = [
    {
        'name': 'Supplier',
        'csn_file': 'sap-s4com-Supplier-v1.en.json',
        'sample_count': 50
    },
    {
        'name': 'PaymentTerms',
        'csn_file': 'sap-s4com-PaymentTerms-v1.en.json',
        'sample_count': 20
    },
    {
        'name': 'ServiceEntrySheet',
        'csn_file': 'sap-s4com-ServiceEntrySheet-v1.en.json',
        'sample_count': 30
    },
    {
        'name': 'JournalEntryHeader',
        'csn_file': 'sap-s4com-JournalEntryHeader-v1.en.json',
        'sample_count': 40
    }
]

def map_cds_to_sqlite(cds_type):
    """Map CDS type to SQLite type"""
    if cds_type == 'cds.String':
        return 'TEXT'
    elif cds_type == 'cds.Decimal':
        return 'REAL'
    elif cds_type == 'cds.Integer':
        return 'INTEGER'
    elif cds_type in ['cds.Date', 'cds.DateTime', 'cds.Timestamp']:
        return 'TEXT'
    elif cds_type == 'cds.Boolean':
        return 'INTEGER'
    elif cds_type == 'cds.Double':
        return 'REAL'
    else:
        return 'TEXT'

def generate_create_table_sql(entity_name, elements):
    """Generate CREATE TABLE statement"""
    lines = [f"CREATE TABLE IF NOT EXISTS {entity_name} ("]
    columns = []
    
    for field_name, field_def in elements.items():
        if field_def.get('type') == 'cds.Association':
            continue
        
        sqlite_type = map_cds_to_sqlite(field_def.get('type', 'cds.String'))
        not_null = ' NOT NULL' if field_def.get('key') else ''
        columns.append(f"    {field_name} {sqlite_type}{not_null}")
    
    lines.append(',\n'.join(columns))
    lines.append(");")
    return '\n'.join(lines)

def generate_sample_value(field_name, field_type, index):
    """Generate realistic sample value based on field name and type"""
    field_lower = field_name.lower()
    
    # Date fields
    if 'date' in field_lower:
        base_date = datetime.now() - timedelta(days=random.randint(0, 365))
        return base_date.strftime('%Y-%m-%d')
    
    # ID fields
    if field_name.endswith('ID') or field_name == 'Supplier' or field_name == 'PaymentTerms':
        return f"{random.randint(100000, 999999)}"
    
    # Code fields
    if 'code' in field_lower or 'type' in field_lower:
        return random.choice(['A', 'B', 'C', 'X', 'Y', 'Z'])
    
    # Name fields
    if 'name' in field_lower:
        names = ['Acme Corp', 'Global Solutions', 'Tech Industries', 'Prime Vendors', 'Quality Supplies']
        return random.choice(names)
    
    # Country
    if 'country' in field_lower:
        return random.choice(['US', 'DE', 'UK', 'FR', 'JP'])
    
    # Currency
    if 'currency' in field_lower:
        return random.choice(['USD', 'EUR', 'GBP'])
    
    # Amount fields
    if 'amount' in field_lower or 'value' in field_lower:
        return round(random.uniform(100, 50000), 2)
    
    # Percentage
    if 'percent' in field_lower or 'rate' in field_lower:
        return round(random.uniform(0, 100), 2)
    
    # Boolean
    if field_type == 'cds.Boolean':
        return random.choice([0, 1])
    
    # Integer
    if field_type == 'cds.Integer':
        return random.randint(1, 1000)
    
    # Decimal
    if field_type == 'cds.Decimal':
        return round(random.uniform(0, 10000), 2)
    
    # Default text
    return f"Value_{index}"

def create_tables_and_data(product_config):
    """Create tables and generate sample data for a product"""
    csn_path = CSN_DIR / product_config['csn_file']
    
    if not csn_path.exists():
        print(f"[SKIP] CSN file not found: {csn_path}")
        return
    
    print(f"\n{'='*60}")
    print(f"Processing: {product_config['name']}")
    print(f"{'='*60}")
    
    # Load CSN
    with open(csn_path, 'r', encoding='utf-8') as f:
        csn = json.load(f)
    
    definitions = csn.get('definitions', {})
    if not definitions:
        print(f"[SKIP] No definitions found in {csn_path}")
        return
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        tables_created = 0
        rows_inserted = 0
        
        # Create tables and generate data for each entity
        for entity_name, entity_def in definitions.items():
            elements = entity_def.get('elements', {})
            if not elements:
                continue
            
            # Create table
            sql = generate_create_table_sql(entity_name, elements)
            cursor.execute(sql)
            print(f"  [OK] Created table: {entity_name}")
            tables_created += 1
            
            # Generate sample data
            sample_count = product_config['sample_count']
            
            # Get column names (excluding associations)
            columns = [name for name, def_ in elements.items() 
                      if def_.get('type') != 'cds.Association']
            
            if not columns:
                continue
            
            # Generate rows
            rows = []
            for i in range(1, sample_count + 1):
                row_values = []
                for col_name in columns:
                    field_def = elements[col_name]
                    field_type = field_def.get('type', 'cds.String')
                    
                    # Generate value
                    value = generate_sample_value(col_name, field_type, i)
                    row_values.append(value)
                
                rows.append(tuple(row_values))
            
            # Insert data
            placeholders = ','.join(['?' for _ in columns])
            insert_sql = f"INSERT INTO {entity_name} ({','.join(columns)}) VALUES ({placeholders})"
            
            try:
                cursor.executemany(insert_sql, rows)
                rows_inserted += len(rows)
                print(f"  [OK] Inserted {len(rows)} rows into {entity_name}")
            except Exception as e:
                print(f"  [WARN] Could not insert data into {entity_name}: {e}")
        
        conn.commit()
        print(f"\n[SUCCESS] {product_config['name']}")
        print(f"  Tables created: {tables_created}")
        print(f"  Rows inserted: {rows_inserted}")
        
    except Exception as e:
        print(f"[ERROR] {e}")
        conn.rollback()
    finally:
        conn.close()

def main():
    """Main execution"""
    print("="*60)
    print("P2P Data Products - SQLite Generator")
    print("="*60)
    print(f"Database: {DB_PATH}")
    print(f"Products to generate: {len(DATA_PRODUCTS)}")
    print()
    
    for product in DATA_PRODUCTS:
        create_tables_and_data(product)
    
    # Final summary
    print("\n" + "="*60)
    print("FINAL SUMMARY")
    print("="*60)
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
    tables = [r[0] for r in cursor.fetchall()]
    
    print(f"Total tables in database: {len(tables)}")
    print("\nTables with data:")
    
    for table in tables:
        cursor.execute(f"SELECT COUNT(*) FROM {table}")
        count = cursor.fetchone()[0]
        if count > 0:
            print(f"  - {table}: {count} records")
    
    conn.close()
    
    print("\n" + "="*60)
    print("Next steps:")
    print("1. Restart application (if running)")
    print("2. Navigate to Data Products page")
    print("3. Select 'SQLite (Local)' as data source")
    print("4. All P2P data products should now be available!")
    print("="*60)

if __name__ == '__main__':
    main()