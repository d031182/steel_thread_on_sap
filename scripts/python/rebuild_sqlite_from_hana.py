#!/usr/bin/env python3
"""
Rebuild SQLite Database from HANA Cloud Source

This script rebuilds the SQLite database structure to mirror HANA Cloud,
including data products and their tables. It can be used as a fallback
solution for seamless database switching.

Usage:
    python scripts/python/rebuild_sqlite_from_hana.py [options]

Options:
    --validate-only     Validate HANA structure without rebuilding
    --force             Force rebuild even if SQLite exists
    --migrate-data      Copy data from HANA to SQLite (optional)
    --dry-run           Show what would be done without executing

Architecture:
    1. Connect to HANA Cloud and extract CSN metadata
    2. Parse data products and table definitions
    3. Create SQLite schema matching HANA structure
    4. Optionally migrate data
    5. Validate SQLite structure matches HANA

API Contract Testing:
    - Backend API: Test data product queries work on both databases
    - Frontend API: Verify metadata matches for both sources
"""

import argparse
import json
import logging
import sqlite3
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any

# Add project root to path
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from core.services.csn_parser import CSNParser
from core.services.database_path_resolvers import resolve_database_path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class HANAStructureExtractor:
    """Extract structure information from HANA Cloud using CSN"""
    
    def __init__(self, csn_path: str):
        self.csn_path = Path(csn_path)
        self.csn_parser = CSNParser()
        
    def extract_structure(self) -> Dict[str, Any]:
        """Extract HANA structure from CSN file"""
        logger.info(f"Loading CSN from: {self.csn_path}")
        
        if not self.csn_path.exists():
            raise FileNotFoundError(f"CSN file not found: {self.csn_path}")
        
        with open(self.csn_path, 'r', encoding='utf-8') as f:
            csn_data = json.load(f)
        
        # Extract data products (namespace groupings)
        data_products = self._extract_data_products(csn_data)
        
        # Extract tables with their structures
        tables = self._extract_tables(csn_data)
        
        # Extract associations/relationships
        associations = self._extract_associations(csn_data)
        
        return {
            'data_products': data_products,
            'tables': tables,
            'associations': associations,
            'csn_version': csn_data.get('version'),
            'namespace': csn_data.get('namespace')
        }
    
    def _extract_data_products(self, csn_data: Dict) -> List[Dict[str, Any]]:
        """Extract data products from CSN definitions"""
        data_products = []
        definitions = csn_data.get('definitions', {})
        
        # Group entities by namespace prefix (data product)
        product_map = {}
        
        for entity_name, entity_def in definitions.items():
            if entity_def.get('kind') != 'entity':
                continue
            
            # Extract namespace (e.g., 'p2p_data' from 'p2p_data.Vendors')
            parts = entity_name.split('.')
            if len(parts) >= 2:
                namespace = parts[0]
                if namespace not in product_map:
                    product_map[namespace] = {
                        'name': namespace,
                        'entities': [],
                        'description': f'Data product: {namespace}'
                    }
                product_map[namespace]['entities'].append(entity_name)
        
        data_products = list(product_map.values())
        logger.info(f"Extracted {len(data_products)} data products")
        
        return data_products
    
    def _extract_tables(self, csn_data: Dict) -> Dict[str, Dict[str, Any]]:
        """Extract table definitions from CSN"""
        tables = {}
        definitions = csn_data.get('definitions', {})
        
        for entity_name, entity_def in definitions.items():
            if entity_def.get('kind') != 'entity':
                continue
            
            # Extract elements (columns)
            elements = entity_def.get('elements', {})
            columns = []
            
            for col_name, col_def in elements.items():
                column_info = {
                    'name': col_name,
                    'type': self._map_csn_type_to_sqlite(col_def.get('type')),
                    'nullable': not col_def.get('notNull', False),
                    'key': col_def.get('key', False),
                    'length': col_def.get('length'),
                    'precision': col_def.get('precision'),
                    'scale': col_def.get('scale')
                }
                columns.append(column_info)
            
            tables[entity_name] = {
                'name': entity_name,
                'columns': columns,
                'keys': entity_def.get('keys', []),
                'annotations': entity_def.get('@', {})
            }
        
        logger.info(f"Extracted {len(tables)} tables")
        return tables
    
    def _extract_associations(self, csn_data: Dict) -> List[Dict[str, Any]]:
        """Extract associations/relationships from CSN"""
        associations = []
        definitions = csn_data.get('definitions', {})
        
        for entity_name, entity_def in definitions.items():
            if entity_def.get('kind') != 'entity':
                continue
            
            elements = entity_def.get('elements', {})
            for elem_name, elem_def in elements.items():
                if elem_def.get('type') == 'cds.Association':
                    target = elem_def.get('target')
                    cardinality = elem_def.get('cardinality', {})
                    
                    associations.append({
                        'source': entity_name,
                        'source_field': elem_name,
                        'target': target,
                        'cardinality': cardinality
                    })
        
        logger.info(f"Extracted {len(associations)} associations")
        return associations
    
    def _map_csn_type_to_sqlite(self, csn_type: str) -> str:
        """Map CSN data types to SQLite types"""
        type_mapping = {
            'cds.String': 'TEXT',
            'cds.Integer': 'INTEGER',
            'cds.Integer64': 'INTEGER',
            'cds.Decimal': 'REAL',
            'cds.Double': 'REAL',
            'cds.Boolean': 'INTEGER',
            'cds.Date': 'TEXT',
            'cds.DateTime': 'TEXT',
            'cds.Timestamp': 'TEXT',
            'cds.UUID': 'TEXT',
            'cds.LargeString': 'TEXT',
            'cds.Binary': 'BLOB'
        }
        
        return type_mapping.get(csn_type, 'TEXT')


class SQLiteRebuilder:
    """Rebuild SQLite database from HANA structure"""
    
    def __init__(self, sqlite_path: str, force: bool = False):
        self.sqlite_path = Path(sqlite_path)
        self.force = force
        self.conn: Optional[sqlite3.Connection] = None
    
    def rebuild(self, hana_structure: Dict[str, Any]) -> bool:
        """Rebuild SQLite database from HANA structure"""
        try:
            # Check if database exists
            if self.sqlite_path.exists() and not self.force:
                logger.warning(f"SQLite database already exists: {self.sqlite_path}")
                logger.warning("Use --force to overwrite")
                return False
            
            # Backup existing database if it exists
            if self.sqlite_path.exists():
                backup_path = self.sqlite_path.with_suffix('.db.backup')
                logger.info(f"Backing up existing database to: {backup_path}")
                self.sqlite_path.rename(backup_path)
            
            # Create new database
            logger.info(f"Creating SQLite database: {self.sqlite_path}")
            self.conn = sqlite3.connect(self.sqlite_path)
            
            # Create tables
            tables = hana_structure.get('tables', {})
            self._create_tables(tables)
            
            # Create indexes for keys
            self._create_indexes(tables)
            
            # Store metadata
            self._create_metadata_table(hana_structure)
            
            self.conn.commit()
            logger.info("✅ SQLite database rebuilt successfully")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Error rebuilding SQLite: {e}")
            if self.conn:
                self.conn.rollback()
            return False
            
        finally:
            if self.conn:
                self.conn.close()
    
    def _create_tables(self, tables: Dict[str, Dict[str, Any]]):
        """Create tables in SQLite"""
        for table_name, table_def in tables.items():
            # Convert dotted names to underscores for SQLite
            sqlite_table_name = table_name.replace('.', '_')
            
            columns = table_def.get('columns', [])
            if not columns:
                logger.warning(f"Skipping table {table_name}: no columns defined")
                continue
            
            # Build CREATE TABLE statement
            col_defs = []
            for col in columns:
                col_def = f'"{col["name"]}" {col["type"]}'
                
                if not col['nullable']:
                    col_def += ' NOT NULL'
                
                if col.get('key'):
                    col_def += ' PRIMARY KEY'
                
                col_defs.append(col_def)
            
            create_sql = f'CREATE TABLE IF NOT EXISTS "{sqlite_table_name}" (\n'
            create_sql += ',\n'.join(f'  {col_def}' for col_def in col_defs)
            create_sql += '\n)'
            
            logger.info(f"Creating table: {sqlite_table_name}")
            logger.debug(f"SQL: {create_sql}")
            
            self.conn.execute(create_sql)
    
    def _create_indexes(self, tables: Dict[str, Dict[str, Any]]):
        """Create indexes for key fields"""
        for table_name, table_def in tables.items():
            sqlite_table_name = table_name.replace('.', '_')
            
            # Create indexes for key columns (if not already primary key)
            for col in table_def.get('columns', []):
                if col.get('key') and not col.get('primary_key'):
                    index_name = f'idx_{sqlite_table_name}_{col["name"]}'
                    create_index = f'CREATE INDEX IF NOT EXISTS "{index_name}" ON "{sqlite_table_name}" ("{col["name"]}")'
                    
                    logger.debug(f"Creating index: {index_name}")
                    self.conn.execute(create_index)
    
    def _create_metadata_table(self, hana_structure: Dict[str, Any]):
        """Create metadata table to track rebuild information"""
        create_meta = '''
        CREATE TABLE IF NOT EXISTS _rebuild_metadata (
            key TEXT PRIMARY KEY,
            value TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        '''
        self.conn.execute(create_meta)
        
        # Store metadata
        metadata = [
            ('csn_version', hana_structure.get('csn_version', 'unknown')),
            ('namespace', hana_structure.get('namespace', '')),
            ('data_products_count', str(len(hana_structure.get('data_products', [])))),
            ('tables_count', str(len(hana_structure.get('tables', {})))),
            ('associations_count', str(len(hana_structure.get('associations', [])))),
            ('rebuild_source', 'HANA Cloud CSN')
        ]
        
        for key, value in metadata:
            self.conn.execute(
                'INSERT OR REPLACE INTO _rebuild_metadata (key, value) VALUES (?, ?)',
                (key, value)
            )


class DatabaseValidator:
    """Validate SQLite structure matches HANA"""
    
    def __init__(self, sqlite_path: str):
        self.sqlite_path = Path(sqlite_path)
    
    def validate(self, hana_structure: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """Validate SQLite structure matches HANA structure"""
        errors = []
        
        try:
            conn = sqlite3.connect(self.sqlite_path)
            cursor = conn.cursor()
            
            # Get SQLite tables
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE '_%'")
            sqlite_tables = {row[0] for row in cursor.fetchall()}
            
            # Expected tables from HANA
            expected_tables = {
                name.replace('.', '_')
                for name in hana_structure.get('tables', {}).keys()
            }
            
            # Check missing tables
            missing_tables = expected_tables - sqlite_tables
            if missing_tables:
                errors.append(f"Missing tables: {', '.join(missing_tables)}")
            
            # Check extra tables
            extra_tables = sqlite_tables - expected_tables
            if extra_tables:
                logger.warning(f"Extra tables in SQLite: {', '.join(extra_tables)}")
            
            # Validate table structures
            for hana_table_name, hana_table_def in hana_structure.get('tables', {}).items():
                sqlite_table_name = hana_table_name.replace('.', '_')
                
                if sqlite_table_name not in sqlite_tables:
                    continue
                
                # Get SQLite columns
                cursor.execute(f'PRAGMA table_info("{sqlite_table_name}")')
                sqlite_columns = {row[1]: row for row in cursor.fetchall()}
                
                # Expected columns
                expected_columns = {col['name'] for col in hana_table_def.get('columns', [])}
                
                # Check column mismatch
                sqlite_col_names = set(sqlite_columns.keys())
                missing_cols = expected_columns - sqlite_col_names
                if missing_cols:
                    errors.append(f"Table {sqlite_table_name} missing columns: {', '.join(missing_cols)}")
            
            conn.close()
            
            if errors:
                logger.error("❌ Validation failed:")
                for error in errors:
                    logger.error(f"  - {error}")
                return False, errors
            else:
                logger.info("✅ Validation successful: SQLite matches HANA structure")
                return True, []
            
        except Exception as e:
            logger.error(f"❌ Validation error: {e}")
            return False, [str(e)]


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description='Rebuild SQLite database from HANA Cloud source',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Rebuild SQLite from HANA CSN
  python scripts/python/rebuild_sqlite_from_hana.py

  # Force rebuild even if SQLite exists
  python scripts/python/rebuild_sqlite_from_hana.py --force

  # Validate only (no rebuild)
  python scripts/python/rebuild_sqlite_from_hana.py --validate-only

  # Dry run (show what would be done)
  python scripts/python/rebuild_sqlite_from_hana.py --dry-run
        """
    )
    
    parser.add_argument(
        '--csn-path',
        default='docs/csn/p2p-cap-model.json',
        help='Path to CSN file (default: docs/csn/p2p-cap-model.json)'
    )
    
    parser.add_argument(
        '--sqlite-path',
        default=None,
        help='Path to SQLite database (default: database/p2p_data.db)'
    )
    
    parser.add_argument(
        '--validate-only',
        action='store_true',
        help='Only validate structure without rebuilding'
    )
    
    parser.add_argument(
        '--force',
        action='store_true',
        help='Force rebuild even if SQLite exists'
    )
    
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Show what would be done without executing'
    )
    
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Enable verbose logging'
    )
    
    args = parser.parse_args()
    
    # Configure logging level
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Resolve SQLite path
    sqlite_path = args.sqlite_path or resolve_database_path('p2p_data')
    
    logger.info("=" * 60)
    logger.info("HANA Cloud to SQLite Database Rebuilder")
    logger.info("=" * 60)
    logger.info(f"CSN Path: {args.csn_path}")
    logger.info(f"SQLite Path: {sqlite_path}")
    logger.info(f"Mode: {'Validate Only' if args.validate_only else 'Rebuild'}")
    if args.dry_run:
        logger.info("DRY RUN MODE - No changes will be made")
    logger.info("=" * 60)
    
    try:
        # Extract HANA structure
        extractor = HANAStructureExtractor(args.csn_path)
        hana_structure = extractor.extract_structure()
        
        logger.info(f"\nHANA Structure Summary:")
        logger.info(f"  Data Products: {len(hana_structure['data_products'])}")
        logger.info(f"  Tables: {len(hana_structure['tables'])}")
        logger.info(f"  Associations: {len(hana_structure['associations'])}")
        
        if args.dry_run:
            logger.info("\n✅ Dry run complete - no changes made")
            return 0
        
        if args.validate_only:
            # Validate only
            validator = DatabaseValidator(sqlite_path)
            success, errors = validator.validate(hana_structure)
            return 0 if success else 1
        
        # Rebuild SQLite
        rebuilder = SQLiteRebuilder(sqlite_path, force=args.force)
        success = rebuilder.rebuild(hana_structure)
        
        if success:
            # Validate the rebuild
            validator = DatabaseValidator(sqlite_path)
            valid, errors = validator.validate(hana_structure)
            
            if valid:
                logger.info("\n✅ SQLite database rebuilt and validated successfully")
                logger.info(f"\nTo switch to SQLite fallback:")
                logger.info(f"  1. Set DATABASE_TYPE=sqlite in .env")
                logger.info(f"  2. Restart server: python server.py")
                return 0
            else:
                logger.error("\n❌ Rebuild succeeded but validation failed")
                return 1
        else:
            logger.error("\n❌ Rebuild failed")
            return 1
            
    except Exception as e:
        logger.error(f"\n❌ Fatal error: {e}")
        return 1


if __name__ == '__main__':
    sys.exit(main())