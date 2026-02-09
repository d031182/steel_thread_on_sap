#!/usr/bin/env python3
"""
HANA Cloud CSN Compliance Validator

Uses the CSN parser to validate that HANA Cloud table schemas comply with
CSN file specifications.

Usage:
    python scripts/python/validate_hana_csn_compliance.py
"""

import os
import sys
import json
from pathlib import Path
from typing import Dict, List, Set, Tuple
from dataclasses import dataclass

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from core.services.csn_parser import CSNParser
from modules.hana_connection.backend.hana_connection import HANAConnection
from dotenv import load_dotenv


@dataclass
class ValidationIssue:
    """Represents a schema validation issue"""
    severity: str  # ERROR, WARNING, INFO
    entity: str
    issue_type: str
    message: str
    csn_value: str = None
    hana_value: str = None


class HANACSNValidator:
    """Validates HANA Cloud schema against CSN specifications"""
    
    def __init__(self):
        self.csn_parser = CSNParser()
        self.issues: List[ValidationIssue] = []
        self.csn_dir = project_root / "docs" / "csn"
        
    def load_csn_files(self) -> Dict[str, dict]:
        """Load all CSN files from docs/csn directory"""
        csn_files = {}
        
        if not self.csn_dir.exists():
            print(f"❌ CSN directory not found: {self.csn_dir}")
            return csn_files
            
        for csn_file in self.csn_dir.glob("*.json"):
            try:
                with open(csn_file, 'r', encoding='utf-8') as f:
                    csn_data = json.load(f)
                    entity_name = csn_file.stem.replace('_CSN', '')
                    csn_files[entity_name] = csn_data
                    print(f"✅ Loaded CSN: {entity_name}")
            except Exception as e:
                print(f"⚠️  Error loading {csn_file.name}: {e}")
                
        return csn_files
    
    def get_hana_table_schema(self, connection, table_name: str) -> Dict:
        """Get table schema from HANA Cloud"""
        schema_info = {
            'columns': {},
            'primary_keys': [],
            'foreign_keys': []
        }
        
        try:
            cursor = connection.cursor()
            
            # Get column information
            query = """
                SELECT 
                    COLUMN_NAME,
                    DATA_TYPE_NAME,
                    LENGTH,
                    SCALE,
                    IS_NULLABLE,
                    DEFAULT_VALUE,
                    COMMENTS
                FROM TABLE_COLUMNS
                WHERE SCHEMA_NAME = CURRENT_SCHEMA
                AND TABLE_NAME = ?
                ORDER BY POSITION
            """
            cursor.execute(query, (table_name,))
            
            for row in cursor.fetchall():
                col_name = row[0]
                schema_info['columns'][col_name] = {
                    'type': row[1],
                    'length': row[2],
                    'scale': row[3],
                    'nullable': row[4] == 'TRUE',
                    'default': row[5],
                    'comment': row[6]
                }
            
            # Get primary key information
            pk_query = """
                SELECT COLUMN_NAME
                FROM CONSTRAINTS
                WHERE SCHEMA_NAME = CURRENT_SCHEMA
                AND TABLE_NAME = ?
                AND IS_PRIMARY_KEY = 'TRUE'
                ORDER BY POSITION
            """
            cursor.execute(pk_query, (table_name,))
            schema_info['primary_keys'] = [row[0] for row in cursor.fetchall()]
            
            # Get foreign key information
            fk_query = """
                SELECT 
                    COLUMN_NAME,
                    REFERENCED_SCHEMA_NAME,
                    REFERENCED_TABLE_NAME,
                    REFERENCED_COLUMN_NAME
                FROM REFERENTIAL_CONSTRAINTS
                WHERE SCHEMA_NAME = CURRENT_SCHEMA
                AND TABLE_NAME = ?
            """
            cursor.execute(fk_query, (table_name,))
            
            for row in cursor.fetchall():
                schema_info['foreign_keys'].append({
                    'column': row[0],
                    'ref_schema': row[1],
                    'ref_table': row[2],
                    'ref_column': row[3]
                })
            
            cursor.close()
            
        except Exception as e:
            print(f"⚠️  Error getting HANA schema for {table_name}: {e}")
            
        return schema_info
    
    def map_csn_to_hana_type(self, csn_type: str, csn_length: int = None) -> str:
        """Map CSN type to HANA type"""
        type_mapping = {
            'cds.String': 'NVARCHAR',
            'cds.Integer': 'INTEGER',
            'cds.Integer64': 'BIGINT',
            'cds.Decimal': 'DECIMAL',
            'cds.Double': 'DOUBLE',
            'cds.Boolean': 'BOOLEAN',
            'cds.Date': 'DATE',
            'cds.Time': 'TIME',
            'cds.DateTime': 'TIMESTAMP',
            'cds.Timestamp': 'TIMESTAMP',
            'cds.UUID': 'NVARCHAR',  # UUID stored as string
            'cds.Binary': 'VARBINARY',
            'cds.LargeBinary': 'BLOB',
            'cds.LargeString': 'NCLOB'
        }
        
        return type_mapping.get(csn_type, csn_type)
    
    def validate_column(self, entity_name: str, col_name: str, 
                       csn_col: dict, hana_col: dict) -> None:
        """Validate a single column definition"""
        
        # Check data type
        csn_type = csn_col.get('type', '')
        expected_hana_type = self.map_csn_to_hana_type(csn_type, csn_col.get('length'))
        actual_hana_type = hana_col.get('type', '')
        
        if expected_hana_type != actual_hana_type:
            self.issues.append(ValidationIssue(
                severity='ERROR',
                entity=entity_name,
                issue_type='DATA_TYPE_MISMATCH',
                message=f"Column '{col_name}' type mismatch",
                csn_value=f"{csn_type} (maps to {expected_hana_type})",
                hana_value=actual_hana_type
            ))
        
        # Check length for string types
        if 'length' in csn_col and actual_hana_type in ('NVARCHAR', 'VARCHAR'):
            csn_length = csn_col['length']
            hana_length = hana_col.get('length')
            
            if csn_length != hana_length:
                self.issues.append(ValidationIssue(
                    severity='WARNING',
                    entity=entity_name,
                    issue_type='LENGTH_MISMATCH',
                    message=f"Column '{col_name}' length mismatch",
                    csn_value=str(csn_length),
                    hana_value=str(hana_length)
                ))
        
        # Check nullable
        csn_nullable = not csn_col.get('notNull', False)
        hana_nullable = hana_col.get('nullable', True)
        
        if csn_nullable != hana_nullable:
            self.issues.append(ValidationIssue(
                severity='WARNING',
                entity=entity_name,
                issue_type='NULLABLE_MISMATCH',
                message=f"Column '{col_name}' nullable constraint mismatch",
                csn_value=str(csn_nullable),
                hana_value=str(hana_nullable)
            ))
    
    def validate_entity(self, entity_name: str, csn_data: dict, 
                       hana_schema: Dict) -> None:
        """Validate an entire entity (table) schema"""
        
        # Parse CSN to get entity definition
        entities = self.csn_parser.parse_csn(csn_data)
        
        if not entities:
            self.issues.append(ValidationIssue(
                severity='ERROR',
                entity=entity_name,
                issue_type='CSN_PARSE_ERROR',
                message='Failed to parse CSN file'
            ))
            return
        
        # Get the main entity (usually the first one)
        csn_entity = entities[0] if entities else None
        
        if not csn_entity:
            self.issues.append(ValidationIssue(
                severity='ERROR',
                entity=entity_name,
                issue_type='NO_ENTITY_FOUND',
                message='No entity definition found in CSN'
            ))
            return
        
        csn_columns = {col['name']: col for col in csn_entity.get('elements', [])}
        hana_columns = hana_schema.get('columns', {})
        
        # Check for missing columns in HANA
        for col_name in csn_columns:
            if col_name not in hana_columns:
                self.issues.append(ValidationIssue(
                    severity='ERROR',
                    entity=entity_name,
                    issue_type='MISSING_COLUMN',
                    message=f"Column '{col_name}' defined in CSN but missing in HANA"
                ))
        
        # Check for extra columns in HANA
        for col_name in hana_columns:
            if col_name not in csn_columns:
                self.issues.append(ValidationIssue(
                    severity='INFO',
                    entity=entity_name,
                    issue_type='EXTRA_COLUMN',
                    message=f"Column '{col_name}' exists in HANA but not defined in CSN"
                ))
        
        # Validate matching columns
        for col_name in csn_columns:
            if col_name in hana_columns:
                self.validate_column(
                    entity_name, 
                    col_name, 
                    csn_columns[col_name], 
                    hana_columns[col_name]
                )
        
        # Validate primary keys
        csn_keys = csn_entity.get('keys', [])
        hana_keys = hana_schema.get('primary_keys', [])
        
        if set(csn_keys) != set(hana_keys):
            self.issues.append(ValidationIssue(
                severity='WARNING',
                entity=entity_name,
                issue_type='PRIMARY_KEY_MISMATCH',
                message='Primary key definition mismatch',
                csn_value=', '.join(csn_keys),
                hana_value=', '.join(hana_keys)
            ))
    
    def generate_report(self) -> str:
        """Generate validation report"""
        report = []
        report.append("=" * 80)
        report.append("HANA CLOUD CSN COMPLIANCE VALIDATION REPORT")
        report.append("=" * 80)
        report.append("")
        
        # Count issues by severity
        errors = [i for i in self.issues if i.severity == 'ERROR']
        warnings = [i for i in self.issues if i.severity == 'WARNING']
        info = [i for i in self.issues if i.severity == 'INFO']
        
        report.append(f"Total Issues Found: {len(self.issues)}")
        report.append(f"  - Errors:   {len(errors)}")
        report.append(f"  - Warnings: {len(warnings)}")
        report.append(f"  - Info:     {len(info)}")
        report.append("")
        
        if not self.issues:
            report.append("✅ ALL VALIDATIONS PASSED - HANA schema fully complies with CSN specifications!")
            report.append("")
            return "\n".join(report)
        
        # Group issues by entity
        issues_by_entity = {}
        for issue in self.issues:
            if issue.entity not in issues_by_entity:
                issues_by_entity[issue.entity] = []
            issues_by_entity[issue.entity].append(issue)
        
        # Report issues by entity
        for entity_name in sorted(issues_by_entity.keys()):
            entity_issues = issues_by_entity[entity_name]
            report.append(f"\n{'=' * 80}")
            report.append(f"Entity: {entity_name}")
            report.append(f"{'=' * 80}")
            
            for issue in entity_issues:
                severity_icon = {
                    'ERROR': '❌',
                    'WARNING': '⚠️',
                    'INFO': 'ℹ️'
                }.get(issue.severity, '•')
                
                report.append(f"\n{severity_icon} [{issue.severity}] {issue.issue_type}")
                report.append(f"   {issue.message}")
                
                if issue.csn_value or issue.hana_value:
                    report.append(f"   CSN:  {issue.csn_value or 'N/A'}")
                    report.append(f"   HANA: {issue.hana_value or 'N/A'}")
        
        report.append("\n" + "=" * 80)
        report.append("RECOMMENDATIONS")
        report.append("=" * 80)
        
        if errors:
            report.append("\n❌ CRITICAL: Schema compliance errors found!")
            report.append("   Action: Review and fix mismatches between CSN and HANA schema")
            report.append("   Impact: Data integrity and application functionality may be affected")
        
        if warnings:
            report.append("\n⚠️  WARNING: Schema differences detected")
            report.append("   Action: Review warnings and update CSN or HANA schema as needed")
            report.append("   Impact: May cause unexpected behavior or performance issues")
        
        if info:
            report.append("\nℹ️  INFO: Additional columns found in HANA")
            report.append("   Action: Consider documenting extra columns in CSN if they are intentional")
            report.append("   Impact: Minimal, but may indicate schema drift")
        
        report.append("")
        return "\n".join(report)
    
    def validate(self) -> bool:
        """
        Main validation method
        
        Returns:
            bool: True if validation passes (no errors), False otherwise
        """
        print("\n🔍 Starting HANA Cloud CSN Compliance Validation...")
        print("=" * 80)
        
        # Load CSN files
        print("\n📖 Loading CSN specifications...")
        csn_files = self.load_csn_files()
        
        if not csn_files:
            print("❌ No CSN files found. Please ensure CSN files exist in docs/csn/")
            return False
        
        print(f"✅ Loaded {len(csn_files)} CSN specifications")
        
        # Connect to HANA
        print("\n🔌 Connecting to HANA Cloud...")
        try:
            # Load environment variables
            load_dotenv('app/.env')
            
            hana_host = os.getenv('HANA_HOST')
            hana_port = int(os.getenv('HANA_PORT', 443))
            hana_user = os.getenv('HANA_USER')
            hana_password = os.getenv('HANA_PASSWORD')
            
            if not all([hana_host, hana_user, hana_password]):
                print("❌ Missing HANA credentials in environment variables")
                print("   Required: HANA_HOST, HANA_USER, HANA_PASSWORD in app/.env")
                return False
            
            hana_manager = HANAConnection(hana_host, hana_port, hana_user, hana_password)
            if not hana_manager.connect():
                print("❌ HANA connection failed")
                return False
            
            connection = hana_manager.connection
            print("✅ Connected to HANA Cloud")
        except Exception as e:
            print(f"❌ Failed to connect to HANA Cloud: {e}")
            return False
        
        # Validate each entity
        print("\n✨ Validating entities...")
        for entity_name, csn_data in csn_files.items():
            print(f"\n  Validating: {entity_name}")
            
            # Convert entity name to table name (e.g., "Purchase_Order" -> "PURCHASE_ORDER")
            table_name = entity_name.upper().replace(' ', '_')
            
            try:
                hana_schema = self.get_hana_table_schema(connection, table_name)
                
                if not hana_schema['columns']:
                    self.issues.append(ValidationIssue(
                        severity='ERROR',
                        entity=entity_name,
                        issue_type='TABLE_NOT_FOUND',
                        message=f"Table '{table_name}' not found in HANA Cloud"
                    ))
                else:
                    self.validate_entity(entity_name, csn_data, hana_schema)
                    
            except Exception as e:
                self.issues.append(ValidationIssue(
                    severity='ERROR',
                    entity=entity_name,
                    issue_type='VALIDATION_ERROR',
                    message=f"Error during validation: {str(e)}"
                ))
        
        # Close connection
        hana_manager.close()
        print("\n✅ Validation complete")
        
        # Generate and print report
        report = self.generate_report()
        print("\n" + report)
        
        # Save report to file
        report_file = project_root / "docs" / "HANA_CSN_COMPLIANCE_REPORT.md"
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report)
        print(f"\n📄 Full report saved to: {report_file}")
        
        # Return True if no errors
        errors = [i for i in self.issues if i.severity == 'ERROR']
        return len(errors) == 0


def main():
    """Main entry point"""
    validator = HANACSNValidator()
    
    try:
        success = validator.validate()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ Validation failed with error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()