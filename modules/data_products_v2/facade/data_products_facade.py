"""
Data Products Facade

Business logic layer that orchestrates data product operations.

Follows Facade Pattern to provide simple interface over complex subsystem.
Uses Dependency Injection - repository is injected via constructor.

Author: P2P Development Team  
Version: 3.0.0 (DI Refactoring)
Date: 2026-02-15
"""

from typing import List, Dict, Optional
from core.interfaces.data_product_repository import IDataProductRepository, DataProduct, Table, Column


class DataProductsFacade:
    """
    Facade for data products business logic
    
    Uses Constructor Injection for repository dependency.
    
    Benefits:
    - Easy to test (inject mock repositories)
    - Loosely coupled (no dependency on factory)
    - Single Responsibility (uses repository, doesn't create it)
    
    Usage:
        # Create repository
        repo = SQLiteDataProductRepository(db_path='/path/to/db')
        
        # Inject into facade
        facade = DataProductsFacade(repository=repo)
        
        # Use facade
        products = facade.get_data_products()
    """
    
    def __init__(self, repository: IDataProductRepository):
        """
        Initialize facade with injected repository
        
        Args:
            repository: Pre-configured repository instance (SQLite or HANA)
        
        Raises:
            TypeError: If repository doesn't implement IDataProductRepository
        """
        if not isinstance(repository, IDataProductRepository):
            raise TypeError(
                f"Repository must implement IDataProductRepository, "
                f"got {type(repository).__name__}"
            )
        
        self._repository = repository
    
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
