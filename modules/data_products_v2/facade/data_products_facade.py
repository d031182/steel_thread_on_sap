"""
Data Products Facade

Business logic layer that orchestrates data product operations
with source switching capability.

Follows Facade Pattern to provide simple interface over complex subsystem.

Author: P2P Development Team  
Version: 2.0.0
Date: 2026-02-08
"""

from typing import List, Dict, Optional
from core.interfaces.data_product_repository import IDataProductRepository, DataProduct, Table, Column
from modules.data_products_v2.repositories import DataProductRepositoryFactory


class DataProductsFacade:
    """
    Facade for data products business logic
    
    Provides:
    - Runtime source switching (HANA/SQLite)
    - Unified API regardless of source
    - Error handling and validation
    
    Usage:
        facade = DataProductsFacade('hana', host, port, user, password)
        products = facade.get_data_products()
        # Switch to SQLite
        facade.switch_source('sqlite', db_path='/path/to/db')
    """
    
    def __init__(
        self,
        source_type: str,
        host: Optional[str] = None,
        port: Optional[int] = None,
        user: Optional[str] = None,
        password: Optional[str] = None,
        database: Optional[str] = None,
        schema: Optional[str] = None,
        db_path: Optional[str] = None
    ):
        """Initialize facade with data source"""
        self._repository = DataProductRepositoryFactory.create(
            source_type=source_type,
            host=host,
            port=port,
            user=user,
            password=password,
            database=database,
            schema=schema,
            db_path=db_path
        )
    
    def get_data_products(self) -> List[DataProduct]:
        """Get all data products from current source"""
        return self._repository.get_data_products()
    
    def get_tables(self, product_name: str) -> List[Table]:
        """Get tables within a data product"""
        return self._repository.get_tables_in_product(product_name)
    
    def get_table_structure(self, product_name: str, table_name: str) -> List[Column]:
        """Get table structure (columns)"""
        return self._repository.get_table_structure(product_name, table_name)
    
    def query_table(
        self,
        product_name: str,
        table_name: str,
        limit: int = 100,
        offset: int = 0,
        filters: Optional[Dict] = None
    ) -> Dict:
        """Query table data"""
        return self._repository.query_table_data(
            product_name,
            table_name,
            limit,
            offset,
            filters
        )
    
    def get_current_source(self) -> str:
        """Get current data source type"""
        return self._repository.get_source_type()
    
    def test_connection(self) -> bool:
        """Test connection to current data source"""
        return self._repository.test_connection()
    
    def switch_source(
        self,
        source_type: str,
        host: Optional[str] = None,
        port: Optional[int] = None,
        user: Optional[str] = None,
        password: Optional[str] = None,
        database: Optional[str] = None,
        schema: Optional[str] = None,
        db_path: Optional[str] = None
    ):
        """
        Switch to different data source at runtime
        
        Args:
            source_type: 'hana' or 'sqlite'
            (other params as needed for connection)
        """
        self._repository = DataProductRepositoryFactory.create(
            source_type=source_type,
            host=host,
            port=port,
            user=user,
            password=password,
            database=database,
            schema=schema,
            db_path=db_path
        )