"""
Private HANA Repository Implementation

DO NOT IMPORT THIS MODULE DIRECTLY!
Use: from core.repositories import create_repository

This is a private implementation (underscore prefix) that should only
be accessed via the factory pattern in core.repositories.__init__.py

Repository Pattern: Provides collection-like interface for HANA data access,
hiding HANA-specific implementation details from business logic.
"""

import sys
import os
import logging
import traceback
from typing import List, Dict, Optional
from datetime import datetime
from hdbcli import dbapi

# Add project root to path for imports
backend_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(backend_dir))
sys.path.insert(0, project_root)

from core.repositories.base import AbstractRepository

logger = logging.getLogger(__name__)


class _HanaRepository(AbstractRepository):
    """
    Private HANA repository implementation.
    
    This class merges:
    - HANADataSource (interface adapter)
    - HANAConnection (connection management)
    
    Benefits of merging:
    - Single responsibility: All HANA logic in one place
    - No exposed connection module
    - Cleaner encapsulation
    - Industry standard (Repository Pattern)
    
    Note: Underscore prefix (_HanaRepository) indicates this is private.
    Access ONLY via: create_repository('hana')
    """
    
    def __init__(
        self, 
        host: str, 
        port: int, 
        user: str, 
        password: str,
        database: Optional[str] = None,
        schema: Optional[str] = None
    ):
        """
        Initialize HANA repository.
        
        Args:
            host: HANA Cloud hostname
            port: HANA Cloud port (typically 443)
            user: Database user
            password: Database password
            database: Optional database name
            schema: Optional default schema
        """
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.database = database
        self.schema = schema
        self._connection = None
    
    def _connect(self) -> bool:
        """
        Establish connection to HANA Cloud (private method).
        
        Returns:
            True if connection successful, False otherwise
        """
        if self._connection is None:
            try:
                logger.info(f"[HANA] Attempting connection to {self.host}:{self.port} as user '{self.user}'")
                self._connection = dbapi.connect(
                    address=self.host,
                    port=self.port,
                    user=self.user,
                    password=self.password,
                    encrypt=True,
                    sslValidateCertificate=False
                )
                logger.info(f"[HANA] ✓ Connection established successfully to {self.host}:{self.port}")
                return True
            except dbapi.Error as e:
                # Log HANA-specific errors with detailed context
                error_code = getattr(e, 'errorcode', 'UNKNOWN')
                error_text = str(e)
                logger.error(f"[HANA] ✗ Connection failed to {self.host}:{self.port}")
                logger.error(f"[HANA] Error code: {error_code}")
                logger.error(f"[HANA] Error message: {error_text}")
                logger.error(f"[HANA] User: {self.user}")
                logger.error(f"[HANA] Possible causes:")
                logger.error(f"[HANA]   - IP not in HANA Cloud allowlist (most common)")
                logger.error(f"[HANA]   - Invalid credentials")
                logger.error(f"[HANA]   - HANA instance not running")
                logger.error(f"[HANA]   - Network connectivity issues")
                return False
            except Exception as e:
                # Log non-HANA errors
                logger.error(f"[HANA] ✗ Unexpected connection error: {type(e).__name__}")
                logger.error(f"[HANA] Error details: {str(e)}")
                logger.error(f"[HANA] Traceback:\n{traceback.format_exc()}")
                return False
        return True
    
    def execute_query(self, sql: str, params: tuple = None) -> Dict:
        """
        Execute SQL query with optional parameters.
        
        Args:
            sql: SQL query string
            params: Optional tuple/list of parameters for parameterized queries
        
        Returns:
            Dictionary with:
            - success: bool
            - rows: List[Dict]
            - rowCount: int
            - columnCount: int
            - columns: List[str]
            - executionTime: float (milliseconds)
            - error: Dict (if failed)
        """
        if not self._connect():
            logger.error("[HANA] Cannot execute query - connection failed")
            raise Exception("Failed to connect to HANA")
        
        cursor = self._connection.cursor()
        start_time = datetime.now()
        
        # Log query execution start
        sql_preview = sql[:200] + '...' if len(sql) > 200 else sql
        if params:
            logger.info(f"[HANA] Executing query with {len(params)} parameters")
        logger.info(f"[HANA] SQL: {sql_preview}")
        
        try:
            # Execute with or without parameters
            if params:
                cursor.execute(sql, params)
            else:
                cursor.execute(sql)
            
            # Get column names
            columns = [desc[0] for desc in cursor.description] if cursor.description else []
            
            # Fetch all rows
            rows = cursor.fetchall()
            
            # Convert to list of dicts
            result = []
            for row in rows:
                row_dict = {}
                for i, col in enumerate(columns):
                    value = row[i]
                    # Convert datetime to string
                    if isinstance(value, datetime):
                        value = value.isoformat()
                    row_dict[col] = value
                result.append(row_dict)
            
            execution_time = (datetime.now() - start_time).total_seconds() * 1000
            
            logger.info(f"[HANA] ✓ Query executed successfully: {len(result)} rows, {len(columns)} columns, {execution_time:.2f}ms")
            
            return {
                'success': True,
                'rows': result,
                'rowCount': len(result),
                'columnCount': len(columns),
                'columns': columns,
                'executionTime': round(execution_time, 2)
            }
            
        except dbapi.Error as e:
            # Log HANA SQL errors with detailed context
            execution_time = (datetime.now() - start_time).total_seconds() * 1000
            error_code = getattr(e, 'errorcode', 'UNKNOWN')
            error_text = str(e)
            
            logger.error(f"[HANA] ✗ SQL execution failed after {execution_time:.2f}ms")
            logger.error(f"[HANA] Error code: {error_code}")
            logger.error(f"[HANA] Error message: {error_text}")
            logger.error(f"[HANA] SQL: {sql_preview}")
            if params:
                logger.error(f"[HANA] Parameters: {params}")
            logger.error(f"[HANA] Possible causes:")
            logger.error(f"[HANA]   - Invalid SQL syntax")
            logger.error(f"[HANA]   - Table/column does not exist")
            logger.error(f"[HANA]   - Insufficient privileges")
            logger.error(f"[HANA]   - Invalid parameter values")
            
            return {
                'success': False,
                'error': {
                    'message': error_text,
                    'code': 'SQL_ERROR',
                    'errorCode': error_code
                }
            }
        except Exception as e:
            # Log unexpected errors
            execution_time = (datetime.now() - start_time).total_seconds() * 1000
            logger.error(f"[HANA] ✗ Unexpected query error after {execution_time:.2f}ms: {type(e).__name__}")
            logger.error(f"[HANA] Error details: {str(e)}")
            logger.error(f"[HANA] SQL: {sql_preview}")
            logger.error(f"[HANA] Traceback:\n{traceback.format_exc()}")
            
            return {
                'success': False,
                'error': {
                    'message': str(e),
                    'code': 'SQL_ERROR'
                }
            }
        finally:
            cursor.close()
    
    def get_data_products(self) -> List[Dict]:
        """
        Get list of installed data products.
        
        Returns:
            List of data products with metadata
        
        Raises:
            Exception: If query fails (connection, SQL error, etc.)
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
        
        result = self.execute_query(sql, ('_SAP_DATAPRODUCT%',))
        
        if not result['success']:
            error_msg = result.get('error', {}).get('message', 'Unknown error')
            logger.error(f"[HANA] Failed to get data products: {error_msg}")
            raise Exception(f"Failed to query HANA data products: {error_msg}")
        
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
            
            # Get table count for this schema
            table_count = 0
            try:
                count_sql = """
                SELECT COUNT(*) as TABLE_COUNT
                FROM SYS.TABLES
                WHERE SCHEMA_NAME = ?
                """
                count_result = self.execute_query(count_sql, (schema_name,))
                if count_result['success'] and count_result['rows']:
                    table_count = count_result['rows'][0]['TABLE_COUNT']
            except Exception:
                table_count = 0
            
            # Format display name
            import re
            formatted_name = product_name.replace('_', ' ')
            formatted_name = re.sub(r'([a-z])([A-Z])', r'\1 \2', formatted_name)
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
                'source_system': 'S/4HANA Cloud Private Edition'
            })
        
        return data_products
    
    def get_tables(self, schema: str) -> List[Dict]:
        """
        Get list of tables in a schema.
        
        Args:
            schema: Schema name
        
        Returns:
            List of tables with metadata
        
        Raises:
            Exception: If query fails
        """
        sql = """
        SELECT 
            TABLE_NAME,
            TABLE_TYPE
        FROM SYS.TABLES
        WHERE SCHEMA_NAME = ?
        ORDER BY TABLE_NAME
        """
        
        result = self.execute_query(sql, (schema,))
        
        if not result['success']:
            error_msg = result.get('error', {}).get('message', 'Unknown error')
            logger.error(f"[HANA] Failed to get tables for schema '{schema}': {error_msg}")
            raise Exception(f"Failed to query HANA tables in schema '{schema}': {error_msg}")
        
        tables = []
        for table in result['rows']:
            tables.append({
                'name': table['TABLE_NAME'],
                'type': table['TABLE_TYPE'],
                'record_count': None  # Fetched when viewing table data
            })
        
        return tables
    
    def get_table_structure(self, schema: str, table: str) -> List[Dict]:
        """
        Get detailed table structure (columns, types, constraints).
        
        Args:
            schema: Schema name
            table: Table name
        
        Returns:
            List of column definitions with FK information
        
        Raises:
            Exception: If query fails
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
        
        result = self.execute_query(sql, (schema, table))
        
        if not result['success']:
            error_msg = result.get('error', {}).get('message', 'Unknown error')
            logger.error(f"[HANA] Failed to get structure for table '{schema}'.'{table}': {error_msg}")
            raise Exception(f"Failed to query HANA table structure for '{schema}'.'{table}': {error_msg}")
        
        # Get primary key constraints
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
        
        pk_result = self.execute_query(pk_sql, (schema, table))
        
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
        
        fk_result = self.execute_query(fk_sql, (schema, table))
        
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
                'isPrimaryKey': is_pk,
                'IS_PRIMARY_KEY': is_pk,
                'foreignKey': fk_map.get(col_name),
                'FOREIGN_KEY': fk_map.get(col_name)
            }
            columns.append(col_info)
        
        return columns
    
    def query_table(self, schema: str, table: str, limit: int = 100, offset: int = 0) -> Dict:
        """
        Query data from a table.
        
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
        
        struct_result = self.execute_query(struct_sql, (schema, table))
        
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
        
        result = self.execute_query(sql, (limit, offset))
        
        if not result['success']:
            return {
                'rows': [],
                'columns': [],
                'totalCount': 0,
                'executionTime': 0
            }
        
        # Get total count for pagination
        count_sql = f'SELECT COUNT(*) as TOTAL FROM "{schema}"."{table}"'
        count_result = self.execute_query(count_sql)
        total_count = count_result['rows'][0]['TOTAL'] if count_result['success'] and count_result['rows'] else result['rowCount']
        
        return {
            'rows': result['rows'],
            'columns': [{'name': col} for col in result['columns']],
            'totalCount': total_count,
            'executionTime': result['executionTime']
        }
    
    def get_csn_definition(self, schema: str) -> Optional[Dict]:
        """
        Get CSN (Core Schema Notation) definition for a data product.
        
        Args:
            schema: Schema name or product identifier
        
        Returns:
            CSN definition as dict, or None if not available
        """
        try:
            sql = """
            SELECT CSN_JSON
            FROM _SAP_DB_ACCESS_DATA_PRODUCT_GATEWAY._SAP_DATAPRODUCT_DELTA_CSN
            WHERE REMOTE_SOURCE_NAME = ?
            """
            
            result = self.execute_query(sql, (schema,))
            
            if result['success'] and result['rows']:
                import json
                csn_json = result['rows'][0]['CSN_JSON']
                return json.loads(csn_json) if csn_json else None
            
            return None
            
        except Exception:
            # CSN access may fail due to privileges or missing data
            return None
    
    def get_connection_info(self) -> Dict[str, any]:
        """
        Get connection information for this HANA repository.
        
        Returns:
            Dictionary with HANA-specific connection details:
            - type: 'hana'
            - host: HANA server hostname
            - port: HANA server port
            - database: Database name (if configured)
            - schema: Default schema (if configured)
        """
        return {
            'type': 'hana',
            'host': self.host,
            'port': self.port,
            'database': self.database,
            'schema': self.schema
        }
    
    def close(self):
        """Close HANA connection."""
        if self._connection:
            self._connection.close()
            self._connection = None
            logger.info("[HANA] Connection closed")