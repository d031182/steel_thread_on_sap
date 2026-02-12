"""
CSN to HANA Validation Tool
============================
Validates CSN field definitions against actual HANA table structures.
This ensures SQLite schema matches HANA reality, not just CSN theory.

Usage:
    python backend/validate_csn_against_hana.py PurchaseOrder

Author: P2P Development Team
Date: 2026-01-24
"""

import json
import os
import sys
from typing import Dict, List, Tuple
from hdbcli import dbapi

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# HANA connection details (from environment)
HANA_HOST = os.getenv('HANA_HOST', '')
HANA_PORT = int(os.getenv('HANA_PORT', '443'))
HANA_USER = os.getenv('HANA_USER', '')
HANA_PASSWORD = os.getenv('HANA_PASSWORD', '')


class CSNValidator:
    """Validates CSN definitions against actual HANA tables"""
    
    def __init__(self, hana_host, hana_port, hana_user, hana_password):
        self.host = hana_host
        self.port = hana_port
        self.user = hana_user
        self.password = hana_password
        self.connection = None
    
    def connect(self) -> bool:
        """Connect to HANA Cloud"""
        try:
            print(f"🔌 Connecting to HANA: {self.user}@{self.host}:{self.port}")
            self.connection = dbapi.connect(
                address=self.host,
                port=self.port,
                user=self.user,
                password=self.password,
                encrypt=True,
                sslValidateCertificate=False
            )
            print("✅ Connected to HANA successfully")
            return True
        except Exception as e:
            print(f"❌ Connection failed: {str(e)}")
            return False
    
    def find_data_product_schema(self, product_name: str) -> str:
        """Find the actual schema name for a data product in HANA"""
        sql = """
        SELECT SCHEMA_NAME
        FROM SYS.SCHEMAS
        WHERE SCHEMA_NAME LIKE '%' || ? || '%'
        ORDER BY CREATE_TIME DESC
        LIMIT 1
        """
        
        cursor = self.connection.cursor()
        cursor.execute(sql, (product_name,))
        result = cursor.fetchone()
        cursor.close()
        
        if result:
            schema_name = result[0]
            print(f"📦 Found schema: {schema_name}")
            return schema_name
        else:
            print(f"❌ No schema found containing: {product_name}")
            return None
    
    def get_hana_table_structure(self, schema_name: str, table_name: str) -> List[Dict]:
        """Get actual table structure from HANA"""
        print(f"\n🔍 Querying HANA for table structure: {schema_name}.{table_name}")
        
        # First, try to find the actual table name (may have schema prefix)
        find_table_sql = """
        SELECT TABLE_NAME
        FROM SYS.TABLES
        WHERE SCHEMA_NAME = ? AND TABLE_NAME LIKE ?
        LIMIT 1
        """
        
        cursor = self.connection.cursor()
        # Try exact match first
        cursor.execute(find_table_sql, (schema_name, table_name))
        result = cursor.fetchone()
        
        if not result:
            # Try with wildcard (table name might have schema prefix)
            cursor.execute(find_table_sql, (schema_name, f'%.{table_name}'))
            result = cursor.fetchone()
        
        if not result:
            cursor.close()
            return []
        
        actual_table_name = result[0]
        print(f"✓ Found table: {actual_table_name}")
        
        sql = """
        SELECT 
            COLUMN_NAME,
            POSITION,
            DATA_TYPE_NAME,
            LENGTH,
            SCALE,
            IS_NULLABLE,
            DEFAULT_VALUE
        FROM SYS.TABLE_COLUMNS
        WHERE SCHEMA_NAME = ? AND TABLE_NAME = ?
        ORDER BY POSITION
        """
        
        cursor.execute(sql, (schema_name, actual_table_name))
        
        columns = []
        for row in cursor.fetchall():
            columns.append({
                'name': row[0],
                'position': row[1],
                'dataType': row[2],
                'length': row[3],
                'scale': row[4],
                'nullable': row[5] == 'TRUE',
                'defaultValue': row[6]
            })
        
        cursor.close()
        
        print(f"✅ Found {len(columns)} columns in HANA table")
        return columns
    
    def load_csn_file(self, product_name: str) -> Dict:
        """Load CSN file from data-products directory"""
        # Try different naming patterns
        possible_files = [
            f'data-products/sap-s4com-{product_name}-v1.en.json',
            f'data-products/sap-s4com-{product_name}-v1.json',
            f'data-products/{product_name}.json'
        ]
        
        for filepath in possible_files:
            if os.path.exists(filepath):
                print(f"📄 Loading CSN from: {filepath}")
                with open(filepath, 'r', encoding='utf-8') as f:
                    csn = json.load(f)
                print(f"✅ CSN loaded successfully")
                return csn
        
        print(f"❌ CSN file not found. Tried: {possible_files}")
        return None
    
    def extract_csn_entity_fields(self, csn: Dict, entity_name: str) -> List[Dict]:
        """Extract field definitions from CSN for a specific entity"""
        if 'definitions' not in csn:
            print("❌ No 'definitions' section in CSN")
            return []
        
        if entity_name not in csn['definitions']:
            print(f"❌ Entity '{entity_name}' not found in CSN")
            print(f"Available entities: {list(csn['definitions'].keys())}")
            return []
        
        entity = csn['definitions'][entity_name]
        elements = entity.get('elements', {})
        
        fields = []
        for field_name, field_def in elements.items():
            # Skip associations (relationships to other tables)
            if field_def.get('type') == 'cds.Association':
                continue
            
            fields.append({
                'name': field_name,
                'cdsType': field_def.get('type', 'unknown'),
                'length': field_def.get('length'),
                'precision': field_def.get('precision'),
                'scale': field_def.get('scale'),
                'key': field_def.get('key', False)
            })
        
        print(f"✅ Extracted {len(fields)} fields from CSN entity '{entity_name}'")
        return fields
    
    def map_cds_to_hana_type(self, cds_type: str, length=None, precision=None, scale=None) -> str:
        """Map CDS type to HANA SQL type"""
        mapping = {
            'cds.String': 'NVARCHAR' if length else 'NVARCHAR',
            'cds.Decimal': 'DECIMAL',
            'cds.Integer': 'INTEGER',
            'cds.Date': 'DATE',
            'cds.DateTime': 'TIMESTAMP',
            'cds.Timestamp': 'TIMESTAMP',
            'cds.Boolean': 'BOOLEAN',
            'cds.Double': 'DOUBLE',
            'cds.Binary': 'VARBINARY'
        }
        
        hana_type = mapping.get(cds_type, 'NVARCHAR')
        
        # Add length/precision/scale
        if hana_type == 'NVARCHAR' and length:
            return f'{hana_type}({length})'
        elif hana_type == 'DECIMAL' and precision:
            if scale:
                return f'{hana_type}({precision},{scale})'
            else:
                return f'{hana_type}({precision})'
        
        return hana_type
    
    def validate_entity(self, csn: Dict, entity_name: str, schema_name: str) -> Dict:
        """
        Validate CSN entity against actual HANA table
        
        Returns:
            Dictionary with validation results
        """
        print(f"\n{'='*80}")
        print(f"VALIDATING: {entity_name}")
        print(f"{'='*80}")
        
        # Get CSN fields
        csn_fields = self.extract_csn_entity_fields(csn, entity_name)
        if not csn_fields:
            return {
                'success': False,
                'error': 'Failed to extract CSN fields'
            }
        
        # Find actual table name in HANA
        # CSN entity name should match HANA table name
        table_name = entity_name
        
        # Get HANA columns
        try:
            hana_columns = self.get_hana_table_structure(schema_name, table_name)
        except Exception as e:
            print(f"❌ Failed to query HANA: {str(e)}")
            return {
                'success': False,
                'error': f'Failed to query HANA table: {str(e)}'
            }
        
        if not hana_columns:
            print(f"❌ Table '{table_name}' not found in HANA schema '{schema_name}'")
            return {
                'success': False,
                'error': 'Table not found in HANA'
            }
        
        # Compare CSN vs HANA
        print(f"\n📊 Comparison Results:")
        print(f"{'─'*80}")
        print(f"CSN Fields: {len(csn_fields)}")
        print(f"HANA Columns: {len(hana_columns)}")
        print(f"{'─'*80}\n")
        
        # Create lookups
        csn_by_name = {f['name']: f for f in csn_fields}
        hana_by_name = {c['name']: c for c in hana_columns}
        
        # Track discrepancies
        matches = []
        missing_in_hana = []
        missing_in_csn = []
        type_mismatches = []
        
        # Check CSN fields against HANA
        for csn_field in csn_fields:
            field_name = csn_field['name']
            
            if field_name not in hana_by_name:
                missing_in_hana.append(field_name)
                print(f"⚠️  '{field_name}' - In CSN but NOT in HANA")
            else:
                hana_col = hana_by_name[field_name]
                expected_type = self.map_cds_to_hana_type(
                    csn_field['cdsType'],
                    csn_field.get('length'),
                    csn_field.get('precision'),
                    csn_field.get('scale')
                )
                
                # Check type match (case insensitive, ignoring length for now)
                hana_type_base = hana_col['dataType'].split('(')[0].upper()
                expected_type_base = expected_type.split('(')[0].upper()
                
                if hana_type_base == expected_type_base or \
                   (hana_type_base in ['NVARCHAR', 'VARCHAR'] and expected_type_base in ['NVARCHAR', 'VARCHAR']):
                    matches.append(field_name)
                    print(f"✅ '{field_name}' - Match: {hana_col['dataType']}")
                else:
                    type_mismatches.append({
                        'field': field_name,
                        'csn': expected_type,
                        'hana': hana_col['dataType']
                    })
                    print(f"⚠️  '{field_name}' - Type mismatch: CSN={expected_type}, HANA={hana_col['dataType']}")
        
        # Check for columns in HANA not in CSN
        for hana_col in hana_columns:
            if hana_col['name'] not in csn_by_name:
                missing_in_csn.append(hana_col['name'])
                print(f"⚠️  '{hana_col['name']}' - In HANA but NOT in CSN")
        
        # Summary
        print(f"\n{'─'*80}")
        print(f"📊 Validation Summary:")
        print(f"{'─'*80}")
        print(f"✅ Matching fields: {len(matches)}/{len(csn_fields)}")
        print(f"⚠️  Missing in HANA: {len(missing_in_hana)}")
        print(f"⚠️  Missing in CSN: {len(missing_in_csn)}")
        print(f"⚠️  Type mismatches: {len(type_mismatches)}")
        
        validation_success = (len(missing_in_hana) == 0 and 
                             len(type_mismatches) == 0)
        
        if validation_success:
            print(f"\n✅ VALIDATION PASSED - CSN matches HANA structure")
        else:
            print(f"\n⚠️  VALIDATION WARNINGS - Some discrepancies found")
        
        print(f"{'='*80}\n")
        
        return {
            'success': True,
            'entity': entity_name,
            'schemaName': schema_name,
            'tableName': table_name,
            'validationPassed': validation_success,
            'csnFields': len(csn_fields),
            'hanaColumns': len(hana_columns),
            'matches': matches,
            'missingInHana': missing_in_hana,
            'missingInCsn': missing_in_csn,
            'typeMismatches': type_mismatches,
            'hanaColumns': hana_columns  # Include for SQLite schema generation
        }
    
    def generate_sqlite_schema(self, validation_result: Dict) -> str:
        """Generate SQLite CREATE TABLE statement from HANA columns"""
        if not validation_result.get('hanaColumns'):
            return None
        
        entity = validation_result['entity']
        columns = validation_result['hanaColumns']
        
        print(f"\n📝 Generating SQLite schema for: {entity}")
        print(f"{'─'*80}")
        
        # Start CREATE TABLE
        sql_lines = [f"CREATE TABLE {entity} ("]
        
        # Add columns
        for i, col in enumerate(columns):
            # Map HANA type to SQLite type
            hana_type = col['dataType'].upper()
            
            if hana_type.startswith('NVARCHAR') or hana_type.startswith('VARCHAR'):
                sqlite_type = 'TEXT'
            elif 'DECIMAL' in hana_type or 'NUMBER' in hana_type:
                sqlite_type = 'REAL'
            elif 'INT' in hana_type or 'TINYINT' in hana_type or 'SMALLINT' in hana_type:
                sqlite_type = 'INTEGER'
            elif hana_type == 'DATE' or hana_type == 'TIMESTAMP':
                sqlite_type = 'TEXT'  # Store as ISO string
            elif hana_type == 'BOOLEAN':
                sqlite_type = 'INTEGER'  # 0/1
            elif 'DOUBLE' in hana_type or 'REAL' in hana_type:
                sqlite_type = 'REAL'
            elif 'BINARY' in hana_type or 'BLOB' in hana_type:
                sqlite_type = 'BLOB'
            else:
                sqlite_type = 'TEXT'  # Default
            
            # Build column definition
            nullable = 'NULL' if col['nullable'] else 'NOT NULL'
            
            col_def = f"    {col['name']} {sqlite_type}"
            
            # Add NOT NULL if needed
            if not col['nullable']:
                col_def += f" {nullable}"
            
            # Add comma except for last column
            if i < len(columns) - 1:
                col_def += ","
            
            sql_lines.append(col_def)
        
        sql_lines.append(");")
        
        schema_sql = '\n'.join(sql_lines)
        
        print(f"✅ Generated SQLite schema ({len(columns)} columns)")
        print(f"{'─'*80}\n")
        
        return schema_sql
    
    def save_validation_report(self, product_name: str, results: List[Dict]):
        """Save validation report to file"""
        output_dir = 'backend/database/validation'
        os.makedirs(output_dir, exist_ok=True)
        
        output_file = f"{output_dir}/{product_name}_validation_report.json"
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump({
                'product': product_name,
                'timestamp': datetime.now().isoformat(),
                'entities': results
            }, f, indent=2)
        
        print(f"💾 Validation report saved: {output_file}")
    
    def save_sqlite_schemas(self, product_name: str, schemas: Dict[str, str]):
        """Save generated SQLite schemas to files"""
        output_dir = 'backend/database/schema'
        os.makedirs(output_dir, exist_ok=True)
        
        output_file = f"{output_dir}/{product_name.lower()}.sql"
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(f"-- SQLite Schema for {product_name}\n")
            f.write(f"-- Generated from HANA Cloud table structures\n")
            f.write(f"-- Date: {datetime.now().isoformat()}\n")
            f.write(f"-- DO NOT EDIT MANUALLY - Generated by validate_csn_against_hana.py\n\n")
            
            for entity_name, schema_sql in schemas.items():
                f.write(f"-- {entity_name}\n")
                f.write(schema_sql)
                f.write("\n\n")
        
        print(f"💾 SQLite schemas saved: {output_file}")
    
    def close(self):
        """Close connection"""
        if self.connection:
            self.connection.close()
            print("🔌 Connection closed")


def main():
    """Main validation workflow"""
    if len(sys.argv) < 2:
        print("Usage: python backend/validate_csn_against_hana.py <ProductName>")
        print("Example: python backend/validate_csn_against_hana.py PurchaseOrder")
        sys.exit(1)
    
    product_name = sys.argv[1]
    
    print(f"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                    CSN to HANA Validation Tool                               ║
║                                                                              ║
║  This tool validates CSN field definitions against actual HANA tables       ║
║  and generates SQLite schemas based on HANA reality.                        ║
╚══════════════════════════════════════════════════════════════════════════════╝

📦 Data Product: {product_name}
🕐 Timestamp: {datetime.now().isoformat()}

""")
    
    # Check credentials
    if not all([HANA_HOST, HANA_USER, HANA_PASSWORD]):
        print("❌ HANA credentials not configured")
        print("Set environment variables: HANA_HOST, HANA_USER, HANA_PASSWORD")
        sys.exit(1)
    
    # Initialize validator
    validator = CSNValidator(HANA_HOST, HANA_PORT, HANA_USER, HANA_PASSWORD)
    
    # Connect to HANA
    if not validator.connect():
        sys.exit(1)
    
    try:
        # Find schema in HANA
        schema_name = validator.find_data_product_schema(product_name)
        if not schema_name:
            print(f"\n❌ Could not find data product schema for: {product_name}")
            print("Available schemas:")
            # List available schemas
            cursor = validator.connection.cursor()
            cursor.execute("SELECT SCHEMA_NAME FROM SYS.SCHEMAS WHERE SCHEMA_NAME LIKE '_SAP_DATAPRODUCT%' ORDER BY SCHEMA_NAME")
            for row in cursor.fetchall():
                print(f"  - {row[0]}")
            cursor.close()
            sys.exit(1)
        
        # Load CSN file
        csn = validator.load_csn_file(product_name)
        if not csn:
            sys.exit(1)
        
        # Get entities from CSN
        entities = list(csn.get('definitions', {}).keys())
        print(f"\n📋 Found {len(entities)} entities in CSN:")
        for entity in entities:
            print(f"  - {entity}")
        
        # Validate each entity
        validation_results = []
        sqlite_schemas = {}
        
        for entity_name in entities:
            result = validator.validate_entity(csn, entity_name, schema_name)
            validation_results.append(result)
            
            # Generate SQLite schema from HANA columns
            if result.get('success') and result.get('hanaColumns'):
                sqlite_schema = validator.generate_sqlite_schema(result)
                if sqlite_schema:
                    sqlite_schemas[entity_name] = sqlite_schema
        
        # Save reports
        validator.save_validation_report(product_name, validation_results)
        
        if sqlite_schemas:
            validator.save_sqlite_schemas(product_name, sqlite_schemas)
        
        # Final summary
        print(f"\n{'═'*80}")
        print(f"✅ VALIDATION COMPLETE")
        print(f"{'═'*80}")
        print(f"📊 Entities validated: {len(validation_results)}")
        print(f"✅ Passed: {sum(1 for r in validation_results if r.get('validationPassed'))}")
        print(f"⚠️  Warnings: {sum(1 for r in validation_results if not r.get('validationPassed'))}")
        print(f"📝 SQLite schemas generated: {len(sqlite_schemas)}")
        print(f"{'═'*80}\n")
        
        # Return success if all entities validated
        all_passed = all(r.get('validationPassed', False) for r in validation_results)
        return 0 if all_passed else 1
        
    finally:
        validator.close()


if __name__ == '__main__':
    from datetime import datetime
    sys.exit(main())