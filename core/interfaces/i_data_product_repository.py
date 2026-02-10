"""
Data Product Repository Interface

Defines the contract for data product data access across different sources
(HANA Cloud, SQLite, future sources like PostgreSQL, etc.)

This interface follows the Repository Pattern, providing a clean abstraction
layer that allows the application to switch between data sources without
changing business logic.

Author: P2P Development Team
Version: 2.0.0
Date: 2026-02-08
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Optional
from dataclasses import dataclass


@dataclass
class DataProduct:
    """
    Data Product domain model
    
    Represents a collection of related tables (e.g., PurchaseOrder, Supplier)
    """
    product_name: str
    display_name: str
    namespace: str
    version: str
    schema_name: str
    source: str  # 'hana' or 'sqlite'
    description: str
    owner: str
    create_time: str
    table_count: int


@dataclass
class Table:
    """
    Table metadata domain model
    """
    table_name: str
    table_type: str
    record_count: int
    schema_name: str


@dataclass
class Column:
    """
    Column metadata domain model
    """
    column_name: str
    data_type: str
    length: Optional[int]
    is_nullable: bool
    is_primary_key: bool
    foreign_key: Optional[str]  # Format: "ReferencedTable(ReferencedColumn)"


class IDataProductRepository(ABC):
    """
    Repository interface for data product operations
    
    Implementations:
    - HANADataProductRepository: Queries HANA Cloud data products
    - SQLiteDataProductRepository: Queries local SQLite database
    
    Usage:
        repo = repository_factory.create('hana', connection)
        products = repo.get_data_products()
        tables = repo.get_tables_in_product('PurchaseOrder')
    """
    
    @abstractmethod
    def get_data_products(self) -> List[DataProduct]:
        """
        Get list of all available data products
        
        Returns:
            List of DataProduct objects
        
        Raises:
            ConnectionError: If data source unavailable
            DataAccessError: If query fails
        """
        pass
    
    @abstractmethod
    def get_tables_in_product(self, product_name: str) -> List[Table]:
        """
        Get list of tables within a data product
        
        Args:
            product_name: Name of the data product (e.g., 'PurchaseOrder')
        
        Returns:
            List of Table objects
        
        Raises:
            ValueError: If product_name not found
            DataAccessError: If query fails
        """
        pass
    
    @abstractmethod
    def get_table_structure(self, product_name: str, table_name: str) -> List[Column]:
        """
        Get column structure for a specific table
        
        Args:
            product_name: Name of the data product
            table_name: Name of the table
        
        Returns:
            List of Column objects
        
        Raises:
            ValueError: If table not found
            DataAccessError: If query fails
        """
        pass
    
    @abstractmethod
    def query_table_data(
        self, 
        product_name: str, 
        table_name: str,
        limit: int = 100,
        offset: int = 0,
        filters: Optional[Dict] = None
    ) -> Dict:
        """
        Query data from a table with pagination
        
        Args:
            product_name: Name of the data product
            table_name: Name of the table
            limit: Maximum rows to return
            offset: Number of rows to skip
            filters: Optional filter conditions (future enhancement)
        
        Returns:
            Dictionary with structure:
            {
                'rows': List[Dict],
                'columns': List[Dict],
                'totalCount': int,
                'executionTime': float
            }
        
        Raises:
            ValueError: If table not found
            DataAccessError: If query fails
        """
        pass
    
    @abstractmethod
    def get_source_type(self) -> str:
        """
        Get the data source type
        
        Returns:
            'hana' or 'sqlite'
        """
        pass
    
    @abstractmethod
    def test_connection(self) -> bool:
        """
        Test if connection to data source is working
        
        Returns:
            True if connection successful, False otherwise
        """
        pass


class DataAccessError(Exception):
    """Raised when data access operation fails"""
    pass