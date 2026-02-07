"""
Private SQLite Repository Implementation

DO NOT IMPORT THIS MODULE DIRECTLY!
Use: from core.repositories import create_repository

This is a private implementation (underscore prefix) that should only
be accessed via the factory pattern in core.repositories.__init__.py

Repository Pattern: Provides collection-like interface for data access,
hiding SQLite-specific implementation details from business logic.
"""

import sys
import os
import sqlite3
from typing import List, Dict, Optional
from datetime import datetime

# Add project root to path for imports
backend_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(backend_dir))
sys.path.insert(0, project_root)

from core.repositories.base import AbstractRepository

# Import the SQLiteDataProductsService for data product operations
sys.path.insert(0, os.path.join(project_root, 'modules'))
from data_products.backend.sqlite_data_products_service import SQLiteDataProductsService


class _SqliteRepository(AbstractRepository):
    """
    Private SQLite repository implementation.
    
    This class merges:
    - SQLiteDataSource (interface adapter)
    - Connection management (formerly in sqlite_connection module)
    
    Benefits of merging:
    - Single responsibility: All SQLite logic in one place
    - No exposed connection module
    - Cleaner encapsulation
    - Industry standard (Repository Pattern)
    
    Note: Underscore prefix (_SqliteRepository) indicates this is private.
    Access ONLY via: create_repository('sqlite')
    """
    
    def __init__(self, db_path: Optional[str] = None):
        """
        Initialize SQLite repository.
        
        Args:
            db_path: Path to SQLite database file (optional, uses default if not provided)
        """
        self.service = SQLiteDataProductsService(db_path)
        self._db_path = db_path or self._get_default_db_path()
    
    def _get_default_db_path(self) -> str:
        """Get default database path if none provided."""
        # Try to get from service first
        if hasattr(self.service, 'db_path') and self.service.db_path:
            return self.service.db_path
        
        # Fallback to module-owned database (modular architecture)
        project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        return os.path.join(project_root, 'modules', 'sqlite_connection', 'database', 'p2p_test_data.db')
    
    def get_data_products(self) -> List[Dict]:
        """
        Get list of available data products.
        
        Returns:
            List of data products with metadata
        """
        return self.service.get_data_products()
    
    def get_tables(self, schema: str) -> List[Dict]:
        """
        Get list of tables in a schema.
        
        Args:
            schema: Schema name (for SQLite, this is ignored as there's one schema)
        
        Returns:
            List of tables with metadata
        """
        return self.service.get_tables(schema)
    
    def get_table_structure(self, schema: str, table: str) -> List[Dict]:
        """
        Get detailed table structure (columns, types, constraints).
        
        Args:
            schema: Schema name (ignored for SQLite)
            table: Table name
        
        Returns:
            List of column definitions
        """
        return self.service.get_table_structure(schema, table)
    
    def query_table(self, schema: str, table: str, limit: int = 100, offset: int = 0) -> Dict:
        """
        Query data from a table.
        
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
        Get CSN (Core Schema Notation) definition for a data product.
        
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
        Execute arbitrary SQL query on SQLite database.
        
        This method supports:
        - SELECT queries (returns rows)
        - DML statements (INSERT, UPDATE, DELETE)
        - Parameterized queries for safety
        
        Args:
            sql: SQL query string
            params: Optional tuple of query parameters
        
        Returns:
            Dictionary with:
            - success: bool
            - rows: List[Dict] (empty for DML)
            - columns: List[str]
            - rowCount: int
            - executionTime: float (milliseconds)
            - error: Dict (if failed)
        """
        try:
            start_time = datetime.now()
            
            # Create connection (managed internally)
            conn = self._create_connection()
            cursor = conn.cursor()
            
            # Execute query with or without parameters
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
    
    def _create_connection(self) -> sqlite3.Connection:
        """
        Create a new SQLite database connection (private method).
        
        Returns:
            sqlite3.Connection with Row factory configured
        
        Note:
            This is a private method (underscore prefix).
            Connection management is encapsulated within the repository.
        """
        if not self._db_path:
            raise ValueError("Database path not configured")
        
        connection = sqlite3.connect(self._db_path)
        connection.row_factory = sqlite3.Row
        return connection
    
    def get_connection_info(self) -> Dict[str, any]:
        """
        Get connection information for this SQLite repository.
        
        Returns:
            Dictionary with SQLite-specific connection details:
            - type: 'sqlite'
            - db_path: Path to SQLite database file
            - in_memory: Whether database is in-memory (False for file-based)
        """
        return {
            'type': 'sqlite',
            'db_path': self._db_path,
            'in_memory': False  # Our SQLite databases are file-based
        }