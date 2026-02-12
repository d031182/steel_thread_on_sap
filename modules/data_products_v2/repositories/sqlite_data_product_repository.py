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
from core.repositories._sqlite_repository import _SqliteRepository


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
        Initialize SQLite repository
        
        Args:
            db_path: Path to SQLite database (optional, uses default if None)
        """
        self._repo = _SqliteRepository(db_path)
        self._db_path = db_path or self._repo._db_path
    
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