"""
HANA Data Source
================
DataSource interface implementation for SAP HANA Cloud.

This wrapper provides a standard interface for accessing HANA data products,
making it easy to swap between different data sources (HANA, SQLite, etc.).
"""

import sys
import os
from typing import List, Dict, Optional

# Add project root to path for interface imports
backend_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(os.path.dirname(backend_dir)))
sys.path.insert(0, project_root)

from core.interfaces.data_source import DataSource
from .hana_connection import HANAConnection


class HANADataSource(DataSource):
    """
    HANA implementation of DataSource interface
    
    Provides access to SAP HANA Cloud data products through a standard interface.
    """
    
    def __init__(self, host: str, port: int, user: str, password: str):
        """
        Initialize HANA data source
        
        Args:
            host: HANA Cloud hostname
            port: HANA Cloud port
            user: Database user
            password: Database password
        """
        self.connection = HANAConnection(host, port, user, password)
    
    def get_data_products(self) -> List[Dict]:
        """
        Get list of installed data products
        
        Returns:
            List of data products with metadata
        """
        sql = """
        SELECT 
            SCHEMA_NAME,
            SCHEMA_OWNER,
            CREATE_TIME
        FROM SYS.SCHEMAS
        WHERE SCHEMA_NAME LIKE ?
        ORDER BY SCHEMA_NAME
        """
        
        result = self.connection.execute_query(sql, ('_SAP_DATAPRODUCT%',))
        
        if not result['success']:
            return []
        
        # Parse schema names to extract metadata
        data_products = []
        for row in result['rows']:
            schema_name = row['SCHEMA_NAME']
            
            # Parse schema name: _SAP_DATAPRODUCT_sap_s4com_dataProduct_ProductName_v1_uuid
            parts = schema_name.split('_')
            
            product_name = 'Unknown'
            version = 'v1'
            namespace = 'sap.s4com'
            
            # Extract namespace
            if len(parts) > 3:
                namespace = parts[3].replace('-', '.')
            
            # Extract product name and version
            if 'dataProduct' in parts:
                dp_index = parts.index('dataProduct')
                if dp_index + 1 < len(parts):
                    product_name = parts[dp_index + 1]
                # Find version
                for part in parts[dp_index+2:]:
                    if part.startswith('v') and part[1:].isdigit():
                        version = part
                        break
            
            # Get table count for this schema (fast query - just count, no data)
            table_count = 0
            try:
                count_sql = """
                SELECT COUNT(*) as TABLE_COUNT
                FROM SYS.TABLES
                WHERE SCHEMA_NAME = ?
                """
                count_result = self.connection.execute_query(count_sql, (schema_name,))
                if count_result['success'] and count_result['rows']:
                    table_count = count_result['rows'][0]['TABLE_COUNT']
            except Exception:
                table_count = 0
            
            # Format display name properly:
            # 1. Replace underscores with spaces
            # 2. Add spaces before capital letters (CamelCase → Title Case)
            # 3. Title case the result
            import re
            formatted_name = product_name.replace('_', ' ')
            # Add space before capitals: "PurchaseOrder" → "Purchase Order"
            formatted_name = re.sub(r'([a-z])([A-Z])', r'\1 \2', formatted_name)
            # Add space for consecutive capitals: "SAP" stays "SAP"
            formatted_name = re.sub(r'([A-Z]+)([A-Z][a-z])', r'\1 \2', formatted_name)
            formatted_name = formatted_name.title()
            
            data_products.append({
                'name': schema_name,
                'display_name': formatted_name,
                'version': version,
                'namespace': namespace,
                'owner': row.get('SCHEMA_OWNER', ''),
                'created_at': row.get('CREATE_TIME', ''),
                'entity_count': table_count,
                'source_system': 'S/4HANA Cloud Private Edition'  # Source system context
            })
        
        return data_products
    
    def get_tables(self, schema: str) -> List[Dict]:
        """
        Get list of tables in a schema
        
        Args:
            schema: Schema name
        
        Returns:
            List of tables with metadata (without record counts for performance)
        
        Note:
            Record counts are expensive (1-2s per table). They are now fetched
            only when querying table data via query_table().
        """
        sql = """
        SELECT 
            TABLE_NAME,
            TABLE_TYPE
        FROM SYS.TABLES
        WHERE SCHEMA_NAME = ?
        ORDER BY TABLE_NAME
        """
        
        result = self.connection.execute_query(sql, (schema,))
        
        if not result['success']:
            return []
        
        # Return tables without record counts (performance optimization)
        tables = []
        for table in result['rows']:
            tables.append({
                'name': table['TABLE_NAME'],
                'type': table['TABLE_TYPE'],
                'record_count': None  # Will be fetched when viewing table data
            })
        
        return tables
    
    def get_table_structure(self, schema: str, table: str) -> List[Dict]:
        """
        Get detailed table structure (columns, types, constraints) including foreign keys
        
        Args:
            schema: Schema name
            table: Table name
        
        Returns:
            List of column definitions with FK information
        """
        # Get column information
        sql = """
        SELECT 
            COLUMN_NAME,
            POSITION,
            DATA_TYPE_NAME,
            LENGTH,
            SCALE,
            IS_NULLABLE,
            DEFAULT_VALUE,
            COMMENTS
        FROM SYS.TABLE_COLUMNS
        WHERE SCHEMA_NAME = ? AND TABLE_NAME = ?
        ORDER BY POSITION
        """
        
        result = self.connection.execute_query(sql, (schema, table))
        
        if not result['success']:
            return []
        
        # Get primary key constraints via INDEX (HANA stores PKs as indexes)
        pk_sql = """
        SELECT ic.COLUMN_NAME
        FROM SYS.INDEXES i
        JOIN SYS.INDEX_COLUMNS ic
            ON i.SCHEMA_NAME = ic.SCHEMA_NAME
            AND i.TABLE_NAME = ic.TABLE_NAME
            AND i.INDEX_NAME = ic.INDEX_NAME
        WHERE i.SCHEMA_NAME = ? 
            AND i.TABLE_NAME = ?
            AND i.CONSTRAINT = 'PRIMARY KEY'
        ORDER BY ic.POSITION
        """
        
        pk_result = self.connection.execute_query(pk_sql, (schema, table))
        
        # Build PK set
        pk_columns = set()
        if pk_result['success']:
            for pk_row in pk_result['rows']:
                pk_columns.add(pk_row['COLUMN_NAME'])
        
        # Get foreign key constraints
        fk_sql = """
        SELECT 
            c.COLUMN_NAME,
            r.REFERENCED_SCHEMA_NAME,
            r.REFERENCED_TABLE_NAME,
            r.REFERENCED_COLUMN_NAME
        FROM SYS.REFERENTIAL_CONSTRAINTS r
        JOIN SYS.CONSTRAINT_COLUMN_USAGE c 
            ON r.CONSTRAINT_NAME = c.CONSTRAINT_NAME 
            AND r.SCHEMA_NAME = c.SCHEMA_NAME
        WHERE r.SCHEMA_NAME = ? AND r.TABLE_NAME = ?
        """
        
        fk_result = self.connection.execute_query(fk_sql, (schema, table))
        
        # Build FK map
        fk_map = {}
        if fk_result['success']:
            for fk_row in fk_result['rows']:
                col_name = fk_row['COLUMN_NAME']
                ref_table = fk_row['REFERENCED_TABLE_NAME']
                ref_col = fk_row['REFERENCED_COLUMN_NAME']
                fk_map[col_name] = f"{ref_table}({ref_col})"
        
        # Format columns with PK and FK information
        columns = []
        for row in result['rows']:
            col_name = row['COLUMN_NAME']
            is_pk = col_name in pk_columns
            col_info = {
                'name': col_name,
                'position': row['POSITION'],
                'data_type': row['DATA_TYPE_NAME'],
                'length': row.get('LENGTH'),
                'scale': row.get('SCALE'),
                'nullable': row['IS_NULLABLE'] == 'TRUE',
                'default_value': row.get('DEFAULT_VALUE'),
                'comment': row.get('COMMENTS'),
                'isPrimaryKey': is_pk,  # Primary key flag
                'IS_PRIMARY_KEY': is_pk,  # Alternate key for compatibility
                'foreignKey': fk_map.get(col_name),  # FK constraint or None
                'FOREIGN_KEY': fk_map.get(col_name)  # Alternate key for compatibility
            }
            columns.append(col_info)
        
        return columns
    
    def query_table(self, schema: str, table: str, limit: int = 100, offset: int = 0) -> Dict:
        """
        Query data from a table
        
        Args:
            schema: Schema name
            table: Table name
            limit: Maximum number of rows to return
            offset: Number of rows to skip
        
        Returns:
            Query results with rows, columns, and metadata
        """
        # Get table structure to limit columns
        struct_sql = """
        SELECT COLUMN_NAME, POSITION
        FROM SYS.TABLE_COLUMNS
        WHERE SCHEMA_NAME = ? AND TABLE_NAME = ?
        ORDER BY POSITION
        """
        
        struct_result = self.connection.execute_query(struct_sql, (schema, table))
        
        if struct_result['success'] and struct_result['rows']:
            # Get first 10 columns for preview
            columns = [row['COLUMN_NAME'] for row in struct_result['rows'][:10]]
            column_list = ', '.join([f'"{col}"' for col in columns])
        else:
            column_list = '*'
        
        # Query data
        sql = f"""
        SELECT {column_list}
        FROM "{schema}"."{table}"
        LIMIT ? OFFSET ?
        """
        
        result = self.connection.execute_query(sql, (limit, offset))
        
        if not result['success']:
            return {
                'rows': [],
                'columns': [],
                'totalCount': 0,
                'executionTime': 0
            }
        
        # Get total count for pagination
        count_sql = f'SELECT COUNT(*) as TOTAL FROM "{schema}"."{table}"'
        count_result = self.connection.execute_query(count_sql)
        total_count = count_result['rows'][0]['TOTAL'] if count_result['success'] and count_result['rows'] else result['rowCount']
        
        return {
            'rows': result['rows'],
            'columns': [{'name': col} for col in result['columns']],
            'totalCount': total_count,
            'executionTime': result['executionTime']
        }
    
    def get_csn_definition(self, schema: str) -> Optional[Dict]:
        """
        Get CSN (Core Schema Notation) definition for a data product
        
        Args:
            schema: Schema name or product identifier
        
        Returns:
            CSN definition as dict, or None if not available
        
        Note:
            CSN definitions in HANA Cloud are stored in the
            _SAP_DB_ACCESS_DATA_PRODUCT_GATEWAY schema.
            This requires specific privileges to access.
        """
        try:
            sql = """
            SELECT CSN_JSON
            FROM _SAP_DB_ACCESS_DATA_PRODUCT_GATEWAY._SAP_DATAPRODUCT_DELTA_CSN
            WHERE REMOTE_SOURCE_NAME = ?
            """
            
            result = self.connection.execute_query(sql, (schema,))
            
            if result['success'] and result['rows']:
                import json
                csn_json = result['rows'][0]['CSN_JSON']
                return json.loads(csn_json) if csn_json else None
            
            return None
            
        except Exception:
            # CSN access may fail due to privileges or missing data
            return None
    
    def execute_query(self, sql: str, params: tuple = None) -> Dict:
        """
        Execute arbitrary SQL query
        
        Args:
            sql: SQL query string
            params: Optional query parameters
        
        Returns:
            Query result with success, rows, columns, etc.
        """
        return self.connection.execute_query(sql, params)
    
    def get_connection_info(self) -> Dict[str, any]:
        """
        Get connection information for this HANA data source.
        
        Returns:
            Dictionary with HANA-specific connection details:
            - type: 'hana'
            - host: HANA server hostname
            - port: HANA server port
        
        Note: HANA data sources don't use local file-based caching,
        so db_path is not included (unlike SQLite).
        """
        return {
            'type': 'hana',
            'host': self.connection.host if hasattr(self.connection, 'host') else 'unknown',
            'port': self.connection.port if hasattr(self.connection, 'port') else 443
        }
    
    def close(self):
        """Close underlying connection"""
        self.connection.close()
