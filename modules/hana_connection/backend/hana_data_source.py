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
            
            data_products.append({
                'name': schema_name,
                'display_name': product_name.replace('_', ' ').title(),
                'version': version,
                'namespace': namespace,
                'owner': row.get('SCHEMA_OWNER', ''),
                'created_at': row.get('CREATE_TIME', '')
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
        Get detailed table structure (columns, types, constraints)
        
        Args:
            schema: Schema name
            table: Table name
        
        Returns:
            List of column definitions
        """
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
        
        # Format columns
        columns = []
        for row in result['rows']:
            col_info = {
                'name': row['COLUMN_NAME'],
                'position': row['POSITION'],
                'data_type': row['DATA_TYPE_NAME'],
                'length': row.get('LENGTH'),
                'scale': row.get('SCALE'),
                'nullable': row['IS_NULLABLE'] == 'TRUE',
                'default_value': row.get('DEFAULT_VALUE'),
                'comment': row.get('COMMENTS')
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
    
    def close(self):
        """Close underlying connection"""
        self.connection.close()