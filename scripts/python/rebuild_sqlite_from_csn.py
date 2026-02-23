"""
Rebuild SQLite database from CSN JSON files.

This script reads CSN JSON files from docs/csn/ and rebuilds the SQLite database structure
to match HANA Cloud's hierarchical organization:
- Data Products (from filenames)
  - Tables (entities within each product's namespace)
    - Columns (elements of each entity)

Key features:
- Extracts data product names from CSN filenames
- Groups tables by namespace (e.g., 'purchaseorder', 'supplier')
- Creates proper hierarchical relationships
- Matches HANA Cloud's data product organization
"""

import json
import sqlite3
import sys
from pathlib import Path
from typing import Dict, List, Set
import re

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))


def extract_product_name_from_filename(filename: str) -> str:
    """
    Extract data product name from CSN filename.
    
    Examples:
        'Purchase_Order_CSN.json' -> 'Purchase Order'
        'Supplier_Invoice_CSN.json' -> 'Supplier Invoice'
        'Cost_Center_CSN.json' -> 'Cost Center'
    
    Args:
        filename: CSN filename (e.g., 'Purchase_Order_CSN.json')
        
    Returns:
        Human-readable data product name
    """
    # Remove '_CSN.json' suffix
    name = filename.replace('_CSN.json', '')
    
    # Replace underscores with spaces
    name = name.replace('_', ' ')
    
    return name


def extract_namespace(entity_name: str) -> str:
    """
    Extract namespace from entity name.
    
    Examples:
        'purchaseorder.PurchaseOrder' -> 'purchaseorder'
        'supplier.Supplier' -> 'supplier'
        'costcenter.CostCenter' -> 'costcenter'
    
    Args:
        entity_name: Full entity name with namespace
        
    Returns:
        Namespace portion
    """
    if '.' in entity_name:
        return entity_name.split('.')[0]
    return entity_name


def create_tables(cursor: sqlite3.Cursor):
    """Create the data products, tables, and columns tables."""
    
    # Data products table (top-level grouping)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS data_products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            description TEXT,
            namespace TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Tables (entities within data products)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tables (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            data_product_id INTEGER,
            description TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (data_product_id) REFERENCES data_products(id),
            UNIQUE (name, data_product_id)
        )
    """)
    
    # Columns (fields within tables)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS columns (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            table_id INTEGER,
            name TEXT NOT NULL,
            type TEXT,
            is_key BOOLEAN DEFAULT 0,
            is_nullable BOOLEAN DEFAULT 1,
            description TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (table_id) REFERENCES tables(id),
            UNIQUE (table_id, name)
        )
    """)
    
    print("✓ Created tables: data_products, tables, columns")


def process_csn_file(filepath: Path, cursor: sqlite3.Cursor, conn: sqlite3.Connection):
    """
    Process a single CSN file and insert data into SQLite.
    
    Args:
        filepath: Path to CSN JSON file
        cursor: SQLite cursor
        conn: SQLite connection
    """
    print(f"\nProcessing: {filepath.name}")
    
    # Extract data product name from filename
    product_name = extract_product_name_from_filename(filepath.name)
    
    with open(filepath, 'r', encoding='utf-8') as f:
        csn_data = json.load(f)
    
    # CSN files are arrays with single object
    if isinstance(csn_data, list) and len(csn_data) > 0:
        csn_data = csn_data[0]
    
    definitions = csn_data.get('definitions', {})
    
    if not definitions:
        print(f"  ⚠ No definitions found in {filepath.name}")
        return
    
    # Find the namespace from entity definitions
    namespace = None
    entity_count = 0
    
    for entity_name, entity_def in definitions.items():
        if entity_def.get('kind') == 'entity':
            if namespace is None:
                namespace = extract_namespace(entity_name)
            entity_count += 1
    
    if not namespace:
        print(f"  ⚠ No namespace found in {filepath.name}")
        return
    
    print(f"  Data Product: {product_name}")
    print(f"  Namespace: {namespace}")
    print(f"  Entities: {entity_count}")
    
    # Insert or update data product
    cursor.execute("""
        INSERT INTO data_products (name, namespace, description)
        VALUES (?, ?, ?)
        ON CONFLICT(name) DO UPDATE SET
            namespace = excluded.namespace,
            description = excluded.description
    """, (product_name, namespace, f"Data product from {filepath.name}"))
    
    product_id = cursor.lastrowid
    if product_id == 0:
        # Get existing product ID
        cursor.execute("SELECT id FROM data_products WHERE name = ?", (product_name,))
        product_id = cursor.fetchone()[0]
    
    # Process entities (tables)
    tables_added = 0
    columns_added = 0
    
    for entity_name, entity_def in definitions.items():
        # Skip context definitions, only process entities
        if entity_def.get('kind') != 'entity':
            continue
        
        # Extract table name (without namespace)
        table_name = entity_name.split('.')[-1] if '.' in entity_name else entity_name
        
        # Get description from annotations
        description = entity_def.get('@EndUserText.label', '')
        
        # Insert table
        cursor.execute("""
            INSERT INTO tables (name, data_product_id, description)
            VALUES (?, ?, ?)
            ON CONFLICT(name, data_product_id) DO UPDATE SET
                description = excluded.description
        """, (table_name, product_id, description))
        
        table_id = cursor.lastrowid
        if table_id == 0:
            cursor.execute("""
                SELECT id FROM tables 
                WHERE name = ? AND data_product_id = ?
            """, (table_name, product_id))
            table_id = cursor.fetchone()[0]
        
        tables_added += 1
        
        # Process elements (columns)
        elements = entity_def.get('elements', {})
        
        for col_name, col_def in elements.items():
            col_type = col_def.get('type', 'String')
            is_key = col_def.get('key', False)
            is_nullable = not col_def.get('notNull', False)
            col_description = col_def.get('@EndUserText.label', '')
            
            cursor.execute("""
                INSERT INTO columns (table_id, name, type, is_key, is_nullable, description)
                VALUES (?, ?, ?, ?, ?, ?)
                ON CONFLICT(table_id, name) DO UPDATE SET
                    type = excluded.type,
                    is_key = excluded.is_key,
                    is_nullable = excluded.is_nullable,
                    description = excluded.description
            """, (table_id, col_name, col_type, is_key, is_nullable, col_description))
            
            columns_added += 1
    
    conn.commit()
    print(f"  ✓ Added {tables_added} tables, {columns_added} columns")


def main():
    """Main execution function."""
    
    # Paths
    csn_dir = project_root / 'docs' / 'csn'
    db_path = project_root / 'modules' / 'data_products_v2' / 'database' / 'p2p_data.db'
    
    print("=" * 60)
    print("SQLite Database Rebuild from CSN Files")
    print("=" * 60)
    print(f"CSN Directory: {csn_dir}")
    print(f"Database: {db_path}")
    
    # Check if CSN directory exists
    if not csn_dir.exists():
        print(f"\n❌ Error: CSN directory not found: {csn_dir}")
        sys.exit(1)
    
    # Get all CSN files
    csn_files = sorted(csn_dir.glob('*_CSN.json'))
    
    if not csn_files:
        print(f"\n❌ Error: No CSN files found in {csn_dir}")
        sys.exit(1)
    
    print(f"\nFound {len(csn_files)} CSN files")
    
    # Create database directory if needed
    db_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Connect to database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Drop existing tables for clean rebuild
        print("\nDropping existing tables...")
        cursor.execute("DROP TABLE IF EXISTS columns")
        cursor.execute("DROP TABLE IF EXISTS tables")
        cursor.execute("DROP TABLE IF EXISTS data_products")
        cursor.execute("DROP TABLE IF EXISTS data_product_tables")  # Drop legacy table
        cursor.execute("DROP TABLE IF EXISTS relationships")  # Drop legacy table
        conn.commit()
        
        # Create tables
        print("\nCreating database schema...")
        create_tables(cursor)
        
        # Process each CSN file
        print("\n" + "=" * 60)
        print("Processing CSN Files")
        print("=" * 60)
        
        for csn_file in csn_files:
            process_csn_file(csn_file, cursor, conn)
        
        # Print summary
        print("\n" + "=" * 60)
        print("Database Rebuild Summary")
        print("=" * 60)
        
        cursor.execute("SELECT COUNT(*) FROM data_products")
        product_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM tables")
        table_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM columns")
        column_count = cursor.fetchone()[0]
        
        print(f"✓ Data Products: {product_count}")
        print(f"✓ Tables: {table_count}")
        print(f"✓ Columns: {column_count}")
        
        # Show data products with table counts
        print("\nData Products:")
        cursor.execute("""
            SELECT dp.name, dp.namespace, COUNT(t.id) as table_count
            FROM data_products dp
            LEFT JOIN tables t ON dp.id = t.data_product_id
            GROUP BY dp.id, dp.name, dp.namespace
            ORDER BY dp.name
        """)
        
        for row in cursor.fetchall():
            product_name, namespace, table_count = row
            print(f"  • {product_name} ({namespace}): {table_count} tables")
        
        print("\n✅ Database rebuild complete!")
        print(f"📁 Location: {db_path}")
        
    except Exception as e:
        print(f"\n❌ Error during rebuild: {e}")
        import traceback
        traceback.print_exc()
        conn.rollback()
        sys.exit(1)
    
    finally:
        conn.close()


if __name__ == '__main__':
    main()