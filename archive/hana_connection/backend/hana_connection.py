"""
HANA Connection Manager
=======================
Manages connections to SAP HANA Cloud with error handling and query execution.

This class handles:
- Connection establishment with proper error handling
- SQL query execution with detailed logging
- Parameter binding for SQL injection prevention
- Connection lifecycle management
"""

import logging
from datetime import datetime
from hdbcli import dbapi
import traceback

logger = logging.getLogger(__name__)


class HANAConnection:
    """HANA Cloud connection manager"""
    
    def __init__(self, host, port, user, password):
        """
        Initialize HANA connection manager
        
        Args:
            host: HANA Cloud hostname
            port: HANA Cloud port (typically 443)
            user: Database user
            password: Database password
        """
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.connection = None
    
    def connect(self):
        """
        Establish connection to HANA Cloud
        
        Returns:
            bool: True if connection successful, False otherwise
        """
        if self.connection is None:
            try:
                logger.info(f"[HANA] Attempting connection to {self.host}:{self.port} as user '{self.user}'")
                self.connection = dbapi.connect(
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
    
    def execute_query(self, sql, params=None):
        """
        Execute SQL query with optional parameters and return results
        
        Args:
            sql: SQL query string
            params: Optional tuple/list of parameters for parameterized queries
        
        Returns:
            dict: Query results with structure:
                {
                    'success': bool,
                    'rows': list of dicts (on success),
                    'rowCount': int,
                    'columnCount': int,
                    'columns': list of column names,
                    'executionTime': float (milliseconds),
                    'error': dict (on failure)
                }
        """
        if not self.connect():
            logger.error("[HANA] Cannot execute query - connection failed")
            raise Exception("Failed to connect to HANA")
        
        cursor = self.connection.cursor()
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
    
    def close(self):
        """Close connection"""
        if self.connection:
            self.connection.close()
            self.connection = None
            logger.info("HANA connection closed")