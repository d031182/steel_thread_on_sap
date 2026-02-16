"""
SQLite Data Product Repository

Adapter that wraps the V1 SQLiteDataProductsService to implement
the IDataProductRepository interface.

This follows the Adapter Pattern - taking existing V1 functionality
and adapting it to the new V2 interface contract.

Author: P2P Development Team
Version: 2.0.0
Date: 2026-02-08
"""

from typing import List, Dict, Optional
from core.interfaces.data_product_repository import (
    IDataProductRepository,
    DataProduct,
    Table,
    Column,
    DataAccessError
)
from core.repositories import create_repository, AbstractRepository


class SQLiteDataProductRepository(IDataProductRepository):
    """
    SQLite implementation of data product repository
    
    Uses core _SqliteRepository for database access.
    
    Benefits:
    - Direct database access via core repository
    - Provides clean V2 interface
    - Enables source switching via interface
    
    Usage:
        repo = SQLiteDataProductRepository(db_path)
        products = repo.get_data_products()
    """
    
    def __init__(self, db_path: str = None):
        """
        Initialize SQLite repository using factory pattern
        
        Args:
            db_path: Path to SQLite database (optional, uses default if None)
        """
        # Use core repository factory (proper DI)
        self._repo: AbstractRepository = create_repository(
            backend='sqlite',
            db_path=db_path
        )
        self._db_path = db_path or getattr(self._repo, '_db_path', None)
    
    def get_data_products(self) -> List[DataProduct]:
        """
        Get all data products from SQLite
        
        Returns:
            List of DataProduct domain models
        
        Raises:
            DataAccessError: If query fails
        """
        try:
            # Call core repository service (returns List[Dict])
            products_dict = self._repo.get_data_products()
            
            # Adapt to V2 domain models
            products = []
            for p in products_dict:
                products.append(DataProduct(
                    product_name=p['productName'],
                    display_name=p['displayName'],
                    namespace=p['namespace'],
                    version=p['version'],
                    schema_name=p['schemaName'],
                    source='sqlite',
                    description=p['description'],
                    owner=p['owner'],
                    create_time=p['createTime'],
                    table_count=p['tableCount']
                ))
            
            return products
            
        except Exception as e:
            raise DataAccessError(f"Failed to get data products from SQLite: {e}")
    
    def get_tables_in_product(self, product_name: str) -> List[Table]:
        """
        Get tables within a data product
        
        Args:
            product_name: Product name (e.g., 'PurchaseOrder')
        
        Returns:
            List of Table domain models
        
        Raises:
            ValueError: If product not found
            DataAccessError: If query fails
        """
        try:
            # Build schema name
            schema_name = f'SQLITE_{product_name.upper()}'
            
            # Call core repository service (returns List[Dict])
            tables_dict = self._repo.get_tables(schema_name)
            
            # Adapt to V2 domain models
            tables = []
            for t in tables_dict:
                tables.append(Table(
                    table_name=t['TABLE_NAME'],
                    table_type=t['TABLE_TYPE'],
                    record_count=t['RECORD_COUNT'],
                    schema_name=schema_name
                ))
            
            return tables
            
        except Exception as e:
            raise DataAccessError(f"Failed to get tables for product {product_name}: {e}")
    
    def get_table_structure(self, product_name: str, table_name: str) -> List[Column]:
        """
        Get column structure for a table
        
        Args:
            product_name: Product name
            table_name: Table name
        
        Returns:
            List of Column domain models
        
        Raises:
            ValueError: If table not found
            DataAccessError: If query fails
        """
        try:
            # Build schema name
            schema_name = f'SQLITE_{product_name.upper()}'
            
            # Call core repository service (returns List[Dict])
            columns_dict = self._repo.get_table_structure(schema_name, table_name)
            
            # Adapt to V2 domain models
            columns = []
            for c in columns_dict:
                columns.append(Column(
                    column_name=c['COLUMN_NAME'],
                    data_type=c['DATA_TYPE_NAME'],
                    length=c.get('LENGTH'),
                    is_nullable=c['IS_NULLABLE'],
                    is_primary_key=c['IS_PRIMARY_KEY'],
                    foreign_key=c.get('FOREIGN_KEY')
                ))
            
            return columns
            
        except Exception as e:
            raise DataAccessError(f"Failed to get structure for {table_name}: {e}")
    
    def query_table_data(
        self,
        product_name: str,
        table_name: str,
        limit: int = 100,
        offset: int = 0,
        filters: Optional[Dict] = None
    ) -> Dict:
        """
        Query data from a table
        
        Args:
            product_name: Product name
            table_name: Table name
            limit: Max rows
            offset: Skip rows
            filters: Filter conditions (future)
        
        Returns:
            Dict with rows, columns, totalCount, executionTime
        
        Raises:
            ValueError: If table not found
            DataAccessError: If query fails
        """
        try:
            # Build schema name
            schema_name = f'SQLITE_{product_name.upper()}'
            
            # Call core repository service (already returns correct format)
            result = self._repo.query_table(
                schema=schema_name,
                table=table_name,
                limit=limit,
                offset=offset
            )
            
            # V1 service already returns the correct format!
            # {rows, columns, totalCount, executionTime}
            return result
            
        except Exception as e:
            raise DataAccessError(f"Failed to query {table_name}: {e}")
    
    def get_source_type(self) -> str:
        """Get source type"""
        return 'sqlite'
    
    def test_connection(self) -> bool:
        """
        Test SQLite database connection
        
        Returns:
            True if database accessible, False otherwise
        """
        try:
            # Try to get data products (quick query)
            self.get_data_products()
            return True
        except:
            return False
    
    def execute_sql(self, sql: str) -> Dict:
        """
        Execute raw SQL query against SQLite database
        
        Args:
            sql: SQL SELECT statement
        
        Returns:
            Dict with success, rows, columns, row_count, execution_time_ms
        
        Raises:
            ValueError: If non-SELECT query attempted
            DataAccessError: If query execution fails
        """
        import sqlite3
        import time
        
        # Validate SELECT only (security)
        sql_upper = sql.strip().upper()
        if not sql_upper.startswith('SELECT'):
            return {
                'success': False,
                'error': 'Only SELECT queries allowed',
                'rows': [],
                'columns': [],
                'row_count': 0,
                'execution_time_ms': 0,
                'warnings': []
            }
        
        try:
            start_time = time.time()
            
            # Connect to SQLite database
            conn = sqlite3.connect(self._db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(sql)
            
            # Fetch results
            rows = [dict(row) for row in cursor.fetchall()]
            columns = [desc[0] for desc in cursor.description] if cursor.description else []
            
            execution_time_ms = (time.time() - start_time) * 1000
            
            conn.close()
            
            return {
                'success': True,
                'rows': rows,
                'columns': columns,
                'row_count': len(rows),
                'execution_time_ms': execution_time_ms,
                'warnings': []
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'rows': [],
                'columns': [],
                'row_count': 0,
                'execution_time_ms': 0,
                'warnings': []
            }
