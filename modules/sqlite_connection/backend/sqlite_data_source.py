"""
SQLite Data Source
==================
DataSource interface implementation for SQLite database.

This wrapper provides a standard interface for accessing SQLite data products,
making it easy to swap between different data sources (HANA, SQLite, etc.).

Part of: SQLite Connection Module
Version: 1.0
"""

import sys
import os
from typing import List, Dict, Optional

# Add project root to path for interface imports
backend_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(os.path.dirname(backend_dir)))
sys.path.insert(0, project_root)

from core.interfaces.data_source import DataSource

# Import the SQLiteDataProductsService from data_products module
sys.path.insert(0, os.path.join(project_root, 'modules'))
from data_products.backend.sqlite_data_products_service import SQLiteDataProductsService


class SQLiteDataSource(DataSource):
    """
    SQLite implementation of DataSource interface
    
    Provides access to SQLite data products through a standard interface,
    compatible with the HANA DataSource for easy swapping.
    """
    
    def __init__(self, db_path: Optional[str] = None):
        """
        Initialize SQLite data source
        
        Args:
            db_path: Path to SQLite database (optional, uses default if not provided)
        """
        self.service = SQLiteDataProductsService(db_path)
    
    def get_data_products(self) -> List[Dict]:
        """
        Get list of available data products
        
        Returns:
            List of data products with metadata
        """
        return self.service.get_data_products()
    
    def get_tables(self, schema: str) -> List[Dict]:
        """
        Get list of tables in a schema
        
        Args:
            schema: Schema name (for SQLite, this is ignored as there's one schema)
        
        Returns:
            List of tables with metadata
        """
        return self.service.get_tables(schema)
    
    def get_table_structure(self, schema: str, table: str) -> List[Dict]:
        """
        Get detailed table structure (columns, types, constraints)
        
        Args:
            schema: Schema name (ignored for SQLite)
            table: Table name
        
        Returns:
            List of column definitions
        """
        return self.service.get_table_structure(schema, table)
    
    def query_table(self, schema: str, table: str, limit: int = 100, offset: int = 0) -> Dict:
        """
        Query data from a table
        
        Args:
            schema: Schema name (ignored for SQLite)
            table: Table name
            limit: Maximum number of rows to return
            offset: Number of rows to skip
        
        Returns:
            Query results with rows, columns, and metadata
        """
        return self.service.query_table(schema, table, limit, offset)
    
    def get_csn_definition(self, schema: str) -> Optional[Dict]:
        """
        Get CSN (Core Schema Notation) definition for a data product
        
        Args:
            schema: Schema name or product identifier
        
        Returns:
            CSN definition as dict, or None if not available
        
        Note:
            SQLite does not store CSN definitions. This method
            returns None to maintain interface compatibility.
        """
        return self.service.get_csn_definition(schema)
    
    def execute_query(self, sql: str, params: tuple = None) -> Dict:
        """
        Execute arbitrary SQL query on SQLite database
        
        Args:
            sql: SQL query string
            params: Optional tuple of query parameters
        
        Returns:
            Dictionary with query results
        """
        import sqlite3
        from datetime import datetime
        
        try:
            start_time = datetime.now()
            
            # Use get_connection_info() instead of direct attribute access
            conn_info = self.get_connection_info()
            db_path = conn_info.get('db_path')
            
            conn = sqlite3.connect(db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            if params:
                cursor.execute(sql, params)
            else:
                cursor.execute(sql)
            
            # Check if this is a SELECT query
            if sql.strip().upper().startswith('SELECT'):
                rows = cursor.fetchall()
                columns = [desc[0] for desc in cursor.description] if cursor.description else []
                
                # Convert Row objects to dicts
                result_rows = [dict(row) for row in rows]
                
                execution_time = (datetime.now() - start_time).total_seconds() * 1000
                
                conn.close()
                
                return {
                    'success': True,
                    'rows': result_rows,
                    'columns': columns,
                    'rowCount': len(result_rows),
                    'executionTime': execution_time
                }
            else:
                # DML statement (INSERT, UPDATE, DELETE, etc.)
                conn.commit()
                row_count = cursor.rowcount
                
                execution_time = (datetime.now() - start_time).total_seconds() * 1000
                
                conn.close()
                
                return {
                    'success': True,
                    'rows': [],
                    'columns': [],
                    'rowCount': row_count,
                    'executionTime': execution_time,
                    'message': f'{row_count} row(s) affected'
                }
                
        except Exception as e:
            return {
                'success': False,
                'rows': [],
                'columns': [],
                'rowCount': 0,
                'executionTime': 0,
                'error': {
                    'message': str(e),
                    'code': 'SQLITE_ERROR'
                }
            }
    
    def get_connection_info(self) -> Dict[str, any]:
        """
        Get connection information for this SQLite data source.
        
        Returns:
            Dictionary with SQLite-specific connection details:
            - type: 'sqlite'
            - db_path: Path to SQLite database file
            - in_memory: Whether database is in-memory (False for file-based)
        """
        # Delegate to service's get_db_path() if available, else direct access
        # This is acceptable since get_connection_info() IS the abstraction layer
        db_path = getattr(self.service, 'db_path', None)
        
        return {
            'type': 'sqlite',
            'db_path': db_path,
            'in_memory': False  # Our SQLite databases are file-based
        }
    
    def close(self):
        """Close any open connections (no-op for SQLite)"""
        pass  # SQLite connections are per-query, no persistent connection
