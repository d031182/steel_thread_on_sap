#!/usr/bin/env python3
"""
Rebuild SQLite Database from HANA Cloud Structure

This script rebuilds the SQLite databases (p2p_data.db and p2p_graph.db) by:
1. Reading CSN files from HANA Cloud source
2. Extracting data products and their table structures
3. Creating the same structure in SQLite databases

Purpose: Create a fallback SQLite database with identical structure to HANA Cloud,
         allowing seamless switching when HANA Cloud is unavailable.

Usage:
    # Rebuild from single CSN file
    python scripts/python/rebuild_sqlite_from_hana_structure.py \\
        --csn docs/csn/P2P_COMBINED.csn

    # Rebuild from multiple CSN files
    python scripts/python/rebuild_sqlite_from_hana_structure.py \\
        --csn-dir docs/csn

    # Specify custom output paths
    python scripts/python/rebuild_sqlite_from_hana_structure.py \\
        --csn docs/csn/P2P_COMBINED.csn \\
        --data-db database/p2p_data.db \\
        --graph-db database/p2p_graph.db

    # Dry run (show what would be created without creating)
    python scripts/python/rebuild_sqlite_from_hana_structure.py \\
        --csn docs/csn/P2P_COMBINED.csn \\
        --dry-run

@author P2P Development Team
@version 1.0.0
@date 2026-02-23
"""

import argparse
import json
import logging
import sqlite3
import sys
from pathlib import Path
from typing import Dict, List, Set, Tuple, Optional
from datetime import datetime

# Add project root to Python path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from core.services.csn_parser import CSNParser
from core.services.database_path_resolvers import resolve_database_path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class SQLiteSchemaBuilder:
    """
    Build SQLite schema from HANA Cloud CSN structure.
    
    Handles:
    - Data type mapping (HANA → SQLite)
    - Primary keys, foreign keys, indexes
    - Data products grouping
    - Table dependencies
    """
    
    # HANA to SQLite type mapping
    TYPE_MAPPING = {
        # String types
        'cds.String': 'TEXT',
        'cds.LargeString': 'TEXT',
        'String': 'TEXT',
        
        # Numeric types
        'cds.Integer': 'INTEGER',
        'cds.Integer64': 'INTEGER',
        'cds.Decimal': 'REAL',
        'cds.Double': 'REAL',
        'Integer': 'INTEGER',
        'Decimal': 'REAL',
        
        # Date/Time types
        'cds.Date': 'TEXT',
        'cds.DateTime': 'TEXT',
        'cds.Timestamp': 'TEXT',
        'Date': 'TEXT',
        'DateTime': 'TEXT',
        'Timestamp': 'TEXT',
        
        # Boolean
        'cds.Boolean': 'INTEGER',
        'Boolean': 'INTEGER',
        
        # UUID
        'cds.UUID': 'TEXT',
        'UUID': 'TEXT',
    }
    
    def __init__(self, dry_run: bool = False):
        """
        Initialize schema builder.
        
        Args:
            dry_run: If True, only show what would be created without creating
        """
        self.dry_run = dry_run
        self.data_products: Dict[str, List[str]] = {}
        self.table_schemas: Dict[str, Dict] = {}
        
    def map_hana_type(self, hana_type: str, length: Optional[int] = None) -> str:
        """
        Map HANA data type to SQLite type.
        
        Args:
            hana_type: HANA/CDS data type
            length: Optional length for string types
            
        Returns:
            SQLite data type
        """
        sqlite_type = self.TYPE_MAPPING.get(hana_type, 'TEXT')
        
        # Add length for TEXT types if specified
        if sqlite_type == 'TEXT' and length and length < 1000:
            sqlite_type = f'TEXT({length})'
            
        return sqlite_type
    
    def parse_csn_file(self, csn_path: Path) -> Dict:
        """
        Parse CSN file and extract structure.
        
        Args:
            csn_path: Path to CSN file
            
        Returns:
            Parsed CSN structure
        """
        logger.info(f"📖 Parsing CSN file: {csn_path}")
        
        try:
            with open(csn_path, 'r', encoding='utf-8') as f:
                csn_data = json.load(f)
            
            return csn_data
            
        except FileNotFoundError:
            logger.error(f"❌ CSN file not found: {csn_path}")
            raise
        except json.JSONDecodeError as e:
            logger.error(f"❌ Invalid JSON in CSN file: {e}")
            raise
    
    def extract_data_products(self, csn_data: Dict) -> Dict[str, List[str]]:
        """
        Extract data products and their tables from CSN.
        
        Args:
            csn_data: Parsed CSN structure
            
        Returns:
            Dict mapping data product names to table lists
        """
        logger.info("🔍 Extracting data products...")
        
        data_products = {}
        
        # Handle CSN wrapped in array (SAP BDS format)
        if isinstance(csn_data, list) and len(csn_data) > 0:
            csn_data = csn_data[0]
        
        definitions = csn_data.get('definitions', {})
        
        for entity_name, entity_def in definitions.items():
            # Skip non-entities
            if entity_def.get('kind') != 'entity':
                continue
            
            # Extract data product from namespace
            # Example: "P2P.PurchaseOrder" → data product "P2P"
            parts = entity_name.split('.')
            if len(parts) >= 2:
                data_product = parts[0]
                table_name = parts[-1]
                
                if data_product not in data_products:
                    data_products[data_product] = []
                
                data_products[data_product].append(table_name)
                
                # Store schema for later table creation
                self.table_schemas[table_name] = {
                    'full_name': entity_name,
                    'elements': entity_def.get('elements', {}),
                    'keys': entity_def.get('keys', []),
                    'data_product': data_product
                }
        
        # Log summary
        logger.info(f"✅ Found {len(data_products)} data products:")
        for product, tables in data_products.items():
            logger.info(f"   📦 {product}: {len(tables)} tables")
        
        return data_products
    
    def generate_create_table_sql(self, table_name: str) -> str:
        """
        Generate CREATE TABLE SQL for a table.
        
        Args:
            table_name: Name of the table
            
        Returns:
            CREATE TABLE SQL statement
        """
        schema = self.table_schemas.get(table_name)
        if not schema:
            raise ValueError(f"No schema found for table: {table_name}")
        
        elements = schema['elements']
        keys = schema.get('keys', [])
        
        # SQLite reserved keywords that need quoting
        RESERVED_KEYWORDS = {
            'default', 'order', 'group', 'values', 'index', 'table',
            'select', 'from', 'where', 'join', 'union', 'all', 'distinct',
            'case', 'when', 'then', 'else', 'end', 'primary', 'foreign',
            'key', 'constraint', 'check', 'unique', 'not', 'null', 'as',
            'on', 'using', 'into', 'insert', 'update', 'delete', 'create',
            'drop', 'alter', 'transaction', 'commit', 'rollback'
        }
        
        # Build column definitions
        columns = []
        primary_keys = []
        
        for col_name, col_def in elements.items():
            # Get data type
            col_type = col_def.get('type', 'cds.String')
            col_length = col_def.get('length')
            sqlite_type = self.map_hana_type(col_type, col_length)
            
            # Check if key
            is_key = col_name in keys or col_def.get('key', False)
            
            # Quote column name if it's a reserved keyword OR contains special characters (hyphen, etc.)
            needs_quoting = (
                col_name.lower() in RESERVED_KEYWORDS or
                '-' in col_name or  # Contains hyphen
                ' ' in col_name or  # Contains space
                not col_name.replace('_', '').isalnum()  # Contains other special chars
            )
            quoted_col_name = f'"{col_name}"' if needs_quoting else col_name
            
            # Build column definition
            col_sql = f"{quoted_col_name} {sqlite_type}"
            
            if is_key:
                # Use quoted name for primary key constraint if needed
                pk_col_name = f'"{col_name}"' if needs_quoting else col_name
                primary_keys.append(pk_col_name)
            
            # Add NOT NULL for keys
            if is_key:
                col_sql += " NOT NULL"
            
            columns.append(col_sql)
        
        # Add primary key constraint
        if primary_keys:
            pk_constraint = f"PRIMARY KEY ({', '.join(primary_keys)})"
            columns.append(pk_constraint)
        
        # Always quote table name to handle special characters and reserved keywords
        quoted_table_name = f'"{table_name}"'
        
        # Build CREATE TABLE statement
        sql = f"CREATE TABLE IF NOT EXISTS {quoted_table_name} (\n"
        sql += ",\n".join(f"  {col}" for col in columns)
        sql += "\n)"
        
        return sql
    
    def create_database_structure(
        self,
        db_path: Path,
        tables: List[str],
        data_product: str
    ) -> None:
        """
        Create database structure for a data product.
        
        Args:
            db_path: Path to SQLite database
            tables: List of table names to create
            data_product: Name of data product (for logging)
        """
        if self.dry_run:
            logger.info(f"🔍 DRY RUN - Would create {db_path}")
            logger.info(f"   Tables: {', '.join(tables)}")
            for table in tables:
                sql = self.generate_create_table_sql(table)
                logger.info(f"\n   SQL for {table}:\n{sql}\n")
            return
        
        # Ensure directory exists
        db_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Connect to database
        logger.info(f"📝 Creating database: {db_path}")
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        
        try:
            # Create each table
            for table_name in tables:
                logger.info(f"   ✅ Creating table: {table_name}")
                sql = self.generate_create_table_sql(table_name)
                try:
                    cursor.execute(sql)
                except sqlite3.OperationalError as e:
                    logger.error(f"❌ SQL Error for table {table_name}: {e}")
                    logger.error(f"SQL: {sql}")
                    raise
            
            # Create metadata table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS _rebuild_metadata (
                    rebuild_date TEXT NOT NULL,
                    source_type TEXT NOT NULL,
                    data_product TEXT NOT NULL,
                    table_count INTEGER NOT NULL,
                    csn_source TEXT
                )
            """)
            
            # Insert metadata
            cursor.execute("""
                INSERT INTO _rebuild_metadata
                (rebuild_date, source_type, data_product, table_count, csn_source)
                VALUES (?, ?, ?, ?, ?)
            """, (
                datetime.now().isoformat(),
                'HANA_CSN',
                data_product,
                len(tables),
                'CSN files from docs/csn'
            ))
            
            conn.commit()
            logger.info(f"✅ Created {len(tables)} tables in {db_path}")
            
        except Exception as e:
            conn.rollback()
            logger.error(f"❌ Error creating tables: {e}")
            raise
        finally:
            conn.close()
    
    def rebuild_from_csn(
        self,
        csn_path: Path,
        data_db_path: Path,
        graph_db_path: Path
    ) -> None:
        """
        Rebuild SQLite databases from CSN file.
        
        Args:
            csn_path: Path to CSN file
            data_db_path: Path to p2p_data.db
            graph_db_path: Path to p2p_graph.db
        """
        logger.info("🚀 Starting SQLite rebuild from HANA structure...")
        
        # Parse CSN
        csn_data = self.parse_csn_file(csn_path)
        
        # Extract data products and tables
        self.data_products = self.extract_data_products(csn_data)
        
        # Separate business data tables from graph tables
        business_tables = []
        graph_tables = []
        
        for product, tables in self.data_products.items():
            for table in tables:
                # Graph tables typically contain 'graph', 'edge', 'node' in name
                if any(keyword in table.lower() for keyword in ['graph', 'edge', 'node']):
                    graph_tables.append(table)
                else:
                    business_tables.append(table)
        
        # Create p2p_data.db (business data)
        if business_tables:
            logger.info(f"\n📦 Creating p2p_data.db with {len(business_tables)} tables")
            self.create_database_structure(
                data_db_path,
                business_tables,
                'P2P_DATA'
            )
        
        # Create p2p_graph.db (graph data)
        if graph_tables:
            logger.info(f"\n🕸️  Creating p2p_graph.db with {len(graph_tables)} tables")
            self.create_database_structure(
                graph_db_path,
                graph_tables,
                'GRAPH'
            )
        
        # Summary
        logger.info("\n" + "=" * 60)
        logger.info("✅ SQLite Rebuild Complete!")
        logger.info("=" * 60)
        logger.info(f"📊 Statistics:")
        logger.info(f"   • Data Products: {len(self.data_products)}")
        logger.info(f"   • Business Tables: {len(business_tables)}")
        logger.info(f"   • Graph Tables: {len(graph_tables)}")
        logger.info(f"   • Total Tables: {len(business_tables) + len(graph_tables)}")
        logger.info(f"\n📂 Databases created:")
        logger.info(f"   • {data_db_path}")
        logger.info(f"   • {graph_db_path}")
        logger.info("=" * 60)
    
    def rebuild_from_multiple_csn(
        self,
        csn_dir: Path,
        data_db_path: Path,
        graph_db_path: Path
    ) -> None:
        """
        Rebuild SQLite databases from multiple CSN files.
        
        Args:
            csn_dir: Directory containing CSN files
            data_db_path: Path to p2p_data.db
            graph_db_path: Path to p2p_graph.db
        """
        logger.info(f"🔍 Scanning directory for CSN files: {csn_dir}")
        
        # Find all CSN files (both .csn and .json extensions)
        csn_files = list(csn_dir.glob('*.csn')) + list(csn_dir.glob('*.json'))
        if not csn_files:
            logger.error(f"❌ No CSN files found in {csn_dir}")
            return
        
        logger.info(f"📚 Found {len(csn_files)} CSN files")
        
        # Merge data from all CSN files
        all_data_products = {}
        
        for csn_file in csn_files:
            logger.info(f"\n📖 Processing: {csn_file.name}")
            csn_data = self.parse_csn_file(csn_file)
            products = self.extract_data_products(csn_data)
            
            # Merge products
            for product, tables in products.items():
                if product not in all_data_products:
                    all_data_products[product] = []
                all_data_products[product].extend(tables)
        
        # Remove duplicates
        for product in all_data_products:
            all_data_products[product] = list(set(all_data_products[product]))
        
        # Use merged data
        self.data_products = all_data_products
        
        # Continue with standard rebuild process
        business_tables = []
        graph_tables = []
        
        for product, tables in self.data_products.items():
            for table in tables:
                if any(keyword in table.lower() for keyword in ['graph', 'edge', 'node']):
                    graph_tables.append(table)
                else:
                    business_tables.append(table)
        
        # Create databases
        if business_tables:
            logger.info(f"\n📦 Creating p2p_data.db with {len(business_tables)} tables")
            self.create_database_structure(
                data_db_path,
                business_tables,
                'P2P_DATA'
            )
        
        if graph_tables:
            logger.info(f"\n🕸️  Creating p2p_graph.db with {len(graph_tables)} tables")
            self.create_database_structure(
                graph_db_path,
                graph_tables,
                'GRAPH'
            )
        
        # Summary
        logger.info("\n" + "=" * 60)
        logger.info("✅ SQLite Rebuild Complete!")
        logger.info("=" * 60)
        logger.info(f"📊 Statistics:")
        logger.info(f"   • CSN Files Processed: {len(csn_files)}")
        logger.info(f"   • Data Products: {len(self.data_products)}")
        logger.info(f"   • Business Tables: {len(business_tables)}")
        logger.info(f"   • Graph Tables: {len(graph_tables)}")
        logger.info(f"   • Total Tables: {len(business_tables) + len(graph_tables)}")
        logger.info(f"\n📂 Databases created:")
        logger.info(f"   • {data_db_path}")
        logger.info(f"   • {graph_db_path}")
        logger.info("=" * 60)


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description='Rebuild SQLite databases from HANA Cloud CSN structure',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Rebuild from single CSN file
  python scripts/python/rebuild_sqlite_from_hana_structure.py \\
      --csn docs/csn/P2P_COMBINED.csn

  # Rebuild from multiple CSN files
  python scripts/python/rebuild_sqlite_from_hana_structure.py \\
      --csn-dir docs/csn

  # Custom output paths
  python scripts/python/rebuild_sqlite_from_hana_structure.py \\
      --csn docs/csn/P2P_COMBINED.csn \\
      --data-db database/p2p_data.db \\
      --graph-db database/p2p_graph.db

  # Dry run (show what would be created)
  python scripts/python/rebuild_sqlite_from_hana_structure.py \\
      --csn docs/csn/P2P_COMBINED.csn \\
      --dry-run
        """
    )
    
    # Input options (mutually exclusive)
    input_group = parser.add_mutually_exclusive_group(required=True)
    input_group.add_argument(
        '--csn',
        type=Path,
        help='Path to single CSN file'
    )
    input_group.add_argument(
        '--csn-dir',
        type=Path,
        help='Directory containing multiple CSN files'
    )
    
    # Output options
    parser.add_argument(
        '--data-db',
        type=Path,
        help='Path to p2p_data.db (default: database/p2p_data.db)'
    )
    parser.add_argument(
        '--graph-db',
        type=Path,
        help='Path to p2p_graph.db (default: database/p2p_graph.db)'
    )
    
    # Options
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Show what would be created without creating'
    )
    
    args = parser.parse_args()
    
    # Resolve database paths
    data_db_path = args.data_db or Path(resolve_database_path('p2p_data'))
    graph_db_path = args.graph_db or Path(resolve_database_path('p2p_graph'))
    
    # Create builder
    builder = SQLiteSchemaBuilder(dry_run=args.dry_run)
    
    try:
        # Rebuild from CSN
        if args.csn:
            builder.rebuild_from_csn(args.csn, data_db_path, graph_db_path)
        else:
            builder.rebuild_from_multiple_csn(args.csn_dir, data_db_path, graph_db_path)
        
        if not args.dry_run:
            logger.info("\n💡 Next steps:")
            logger.info("   1. Verify structure: python scripts/python/compare_hana_sqlite_schemas.py")
            logger.info("   2. Test fallback: python -m pytest tests/data_products_v2/test_database_fallback.py")
            logger.info("   3. Populate data if needed: python scripts/python/populate_p2p_comprehensive.py")
        
    except Exception as e:
        logger.error(f"\n❌ Rebuild failed: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()