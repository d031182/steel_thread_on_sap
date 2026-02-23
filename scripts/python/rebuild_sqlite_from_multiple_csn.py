#!/usr/bin/env python3
"""
Rebuild SQLite Database from Multiple HANA Cloud CSN Files

This script processes multiple CSN (Core Schema Notation) files from SAP Data Exchange Layer
and rebuilds a SQLite database with the same structure as HANA Cloud source.

Usage:
    python scripts/python/rebuild_sqlite_from_multiple_csn.py [--csn-dir DIR] [--output DB] [--dry-run]

Examples:
    # Dry run - show what would be created without making changes
    python scripts/python/rebuild_sqlite_from_multiple_csn.py --dry-run

    # Process all CSN files and create SQLite database
    python scripts/python/rebuild_sqlite_from_multiple_csn.py

    # Specify custom paths
    python scripts/python/rebuild_sqlite_from_multiple_csn.py --csn-dir docs/csn --output database/p2p_data.db
"""

import argparse
import json
import logging
import sqlite3
import sys
from pathlib import Path
from typing import Dict, List, Tuple, Any, Optional
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class CSNTypeMapper:
    """Maps CSN/CDS types to SQLite types"""
    
    TYPE_MAPPING = {
        'cds.String': 'TEXT',
        'cds.Date': 'TEXT',  # ISO 8601 format: YYYY-MM-DD
        'cds.Time': 'TEXT',  # ISO 8601 format: HH:MM:SS
        'cds.DateTime': 'TEXT',  # ISO 8601 format: YYYY-MM-DDTHH:MM:SS
        'cds.Timestamp': 'TEXT',  # ISO 8601 format with microseconds
        'cds.Boolean': 'INTEGER',  # 0 or 1
        'cds.Integer': 'INTEGER',
        'cds.Integer64': 'INTEGER',
        'cds.Decimal': 'REAL',
        'cds.Double': 'REAL',
        'cds.Binary': 'BLOB',
        'cds.LargeBinary': 'BLOB',
        'cds.LargeString': 'TEXT',
        'cds.Association': None,  # Skip associations
        'cds.Composition': None,  # Skip compositions
    }
    
    @classmethod
    def map_type(cls, csn_type: str, length: Optional[int] = None, 
                 precision: Optional[int] = None, scale: Optional[int] = None) -> Optional[str]:
        """
        Map CSN type to SQLite type
        
        Args:
            csn_type: The CSN type (e.g., 'cds.String')
            length: String length
            precision: Decimal precision
            scale: Decimal scale
            
        Returns:
            SQLite type or None if type should be skipped
        """
        sqlite_type = cls.TYPE_MAPPING.get(csn_type)
        
        if sqlite_type is None:
            return None
            
        # Add constraints for specific types
        if csn_type == 'cds.String' and length:
            return f"{sqlite_type}({length})"
        elif csn_type == 'cds.Decimal' and precision and scale:
            # SQLite doesn't have true DECIMAL, but we can add check constraint
            return f"REAL"  # Store as REAL, add check constraint separately
            
        return sqlite_type


class CSNParser:
    """Parse CSN files and extract entity definitions"""
    
    def __init__(self, csn_file_path: Path):
        self.csn_file_path = csn_file_path
        self.csn_data = None
        
    def load(self) -> Dict[str, Any]:
        """Load and parse CSN file"""
        try:
            with open(self.csn_file_path, 'r', encoding='utf-8') as f:
                self.csn_data = json.load(f)
            logger.info(f"Loaded CSN file: {self.csn_file_path}")
            return self.csn_data
        except Exception as e:
            logger.error(f"Failed to load CSN file {self.csn_file_path}: {e}")
            raise
            
    def extract_entities(self) -> List[Tuple[str, Dict[str, Any]]]:
        """
        Extract entity definitions from CSN
        
        Returns:
            List of (entity_name, entity_definition) tuples
        """
        if not self.csn_data:
            self.load()
            
        entities = []
        
        # CSN files are arrays with single element containing definitions
        if isinstance(self.csn_data, list) and len(self.csn_data) > 0:
            definitions = self.csn_data[0].get('definitions', {})
            
            for entity_name, entity_def in definitions.items():
                if entity_def.get('kind') == 'entity':
                    entities.append((entity_name, entity_def))
                    logger.debug(f"Found entity: {entity_name}")
                    
        return entities


class SQLiteSchemaBuilder:
    """Build SQLite schema from CSN entities"""
    
    def __init__(self, db_path: Path, dry_run: bool = False):
        self.db_path = db_path
        self.dry_run = dry_run
        self.type_mapper = CSNTypeMapper()
        self.statements = []
        
    def build_create_table_statement(self, entity_name: str, entity_def: Dict[str, Any]) -> Optional[str]:
        """
        Build CREATE TABLE statement from entity definition
        
        Args:
            entity_name: Full entity name (e.g., 'purchaseorder.PurchaseOrder')
            entity_def: Entity definition from CSN
            
        Returns:
            CREATE TABLE SQL statement or None if entity should be skipped
        """
        # Extract table name from entity name (last part)
        parts = entity_name.split('.')
        table_name = parts[-1] if len(parts) > 1 else entity_name
        
        # Skip context definitions
        if entity_def.get('kind') == 'context':
            return None
            
        elements = entity_def.get('elements', {})
        if not elements:
            logger.warning(f"Entity {entity_name} has no elements, skipping")
            return None
            
        # Build column definitions
        columns = []
        primary_keys = []
        
        for elem_name, elem_def in elements.items():
            elem_type = elem_def.get('type')
            
            # Skip associations and compositions
            if elem_type in ['cds.Association', 'cds.Composition']:
                continue
                
            # Map type
            sqlite_type = self.type_mapper.map_type(
                elem_type,
                elem_def.get('length'),
                elem_def.get('precision'),
                elem_def.get('scale')
            )
            
            if sqlite_type is None:
                continue
                
            # Build column definition
            col_def = f'"{elem_name}" {sqlite_type}'
            
            # Add NOT NULL if required
            if elem_def.get('notNull'):
                col_def += ' NOT NULL'
                
            # Track primary keys
            if elem_def.get('key'):
                primary_keys.append(elem_name)
                
            columns.append(col_def)
            
        if not columns:
            logger.warning(f"No columns generated for entity {entity_name}, skipping")
            return None
            
        # Add primary key constraint
        if primary_keys:
            pk_cols = ', '.join(f'"{pk}"' for pk in primary_keys)
            columns.append(f'PRIMARY KEY ({pk_cols})')
            
        # Build CREATE TABLE statement
        columns_sql = ',\n    '.join(columns)
        create_stmt = f'CREATE TABLE IF NOT EXISTS "{table_name}" (\n    {columns_sql}\n);'
        
        return create_stmt
        
    def process_entities(self, entities: List[Tuple[str, Dict[str, Any]]]):
        """Process all entities and generate CREATE TABLE statements"""
        for entity_name, entity_def in entities:
            create_stmt = self.build_create_table_statement(entity_name, entity_def)
            if create_stmt:
                self.statements.append(create_stmt)
                logger.info(f"Generated CREATE TABLE for: {entity_name}")
                
    def execute(self):
        """Execute all CREATE TABLE statements"""
        if self.dry_run:
            logger.info("=" * 60)
            logger.info("DRY RUN - SQL statements that would be executed:")
            logger.info("=" * 60)
            for stmt in self.statements:
                print(stmt)
                print()
            logger.info(f"Total tables to create: {len(self.statements)}")
            return
            
        # Create database connection
        try:
            # Ensure directory exists
            self.db_path.parent.mkdir(parents=True, exist_ok=True)
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Execute statements
            for stmt in self.statements:
                cursor.execute(stmt)
                
            conn.commit()
            conn.close()
            
            logger.info(f"✅ Successfully created {len(self.statements)} tables in {self.db_path}")
            
        except Exception as e:
            logger.error(f"❌ Failed to execute SQL statements: {e}")
            raise


def main():
    parser = argparse.ArgumentParser(
        description='Rebuild SQLite database from multiple HANA Cloud CSN files',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument(
        '--csn-dir',
        type=Path,
        default=Path('docs/csn'),
        help='Directory containing CSN files (default: docs/csn)'
    )
    parser.add_argument(
        '--output',
        type=Path,
        default=Path('database/p2p_data.db'),
        help='Output SQLite database path (default: database/p2p_data.db)'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Show what would be created without making changes'
    )
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Enable verbose logging'
    )
    
    args = parser.parse_args()
    
    if args.verbose:
        logger.setLevel(logging.DEBUG)
        
    logger.info("=" * 60)
    logger.info("SQLite Database Rebuilder from Multiple CSN Files")
    logger.info("=" * 60)
    logger.info(f"CSN Directory: {args.csn_dir}")
    logger.info(f"Output Database: {args.output}")
    logger.info(f"Dry Run: {args.dry_run}")
    logger.info("")
    
    # Check if CSN directory exists
    if not args.csn_dir.exists():
        logger.error(f"❌ CSN directory not found: {args.csn_dir}")
        return 1
        
    # Find all CSN files
    csn_files = list(args.csn_dir.glob('*.json'))
    if not csn_files:
        logger.error(f"❌ No CSN files found in {args.csn_dir}")
        return 1
        
    logger.info(f"Found {len(csn_files)} CSN files")
    logger.info("")
    
    # Initialize schema builder
    schema_builder = SQLiteSchemaBuilder(args.output, args.dry_run)
    
    # Process each CSN file
    total_entities = 0
    for csn_file in csn_files:
        logger.info(f"Processing: {csn_file.name}")
        try:
            parser = CSNParser(csn_file)
            entities = parser.extract_entities()
            total_entities += len(entities)
            logger.info(f"  Found {len(entities)} entities")
            schema_builder.process_entities(entities)
        except Exception as e:
            logger.error(f"  ❌ Error processing {csn_file.name}: {e}")
            continue
            
    logger.info("")
    logger.info(f"Total entities processed: {total_entities}")
    logger.info(f"Total tables to create: {len(schema_builder.statements)}")
    logger.info("")
    
    # Execute CREATE TABLE statements
    try:
        schema_builder.execute()
        logger.info("")
        logger.info("✅ Database rebuild completed successfully!")
        return 0
    except Exception as e:
        logger.error(f"❌ Database rebuild failed: {e}")
        return 1


if __name__ == '__main__':
    sys.exit(main())