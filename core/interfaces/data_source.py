"""
DataSource Interface

Abstract base class for all data source implementations (HANA, SQLite, etc.).
Ensures consistent API across different data sources.
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Optional


class DataSource(ABC):
    """
    Abstract interface for data sources.
    
    All data source implementations (HANA, SQLite, PostgreSQL, etc.)
    must implement this interface to ensure consistent behavior.
    """
    
    @abstractmethod
    def get_data_products(self) -> List[Dict]:
        """
        Get list of available data products.
        
        Returns:
            List of data product metadata dictionaries with keys:
            - productName: str
            - displayName: str (optional)
            - namespace: str
            - version: str
            - schemaName: str
            - source: str (e.g., 'hana', 'sqlite')
            - tableCount: int
            - createTime: str (optional)
            - owner: str (optional)
        """
        pass
    
    @abstractmethod
    def get_tables(self, schema: str) -> List[Dict]:
        """
        Get list of tables in a schema.
        
        Args:
            schema: Schema/data product name
            
        Returns:
            List of table metadata dictionaries with keys:
            - TABLE_NAME: str
            - TABLE_TYPE: str
            - RECORD_COUNT: int (optional)
        """
        pass
    
    @abstractmethod
    def get_table_structure(self, schema: str, table: str) -> List[Dict]:
        """
        Get column structure for a table.
        
        Args:
            schema: Schema/data product name
            table: Table name
            
        Returns:
            List of column metadata dictionaries with keys:
            - COLUMN_NAME: str
            - DATA_TYPE_NAME: str
            - LENGTH: int (optional)
            - IS_NULLABLE: bool
            - IS_PRIMARY_KEY: bool
        """
        pass
    
    @abstractmethod
    def query_table(
        self, 
        schema: str, 
        table: str, 
        limit: int = 100, 
        offset: int = 0
    ) -> Dict:
        """
        Query data from a table.
        
        Args:
            schema: Schema/data product name
            table: Table name
            limit: Maximum rows to return
            offset: Number of rows to skip
            
        Returns:
            Dictionary with:
            - rows: List[Dict] - Query results
            - columns: List[Dict] - Column information
            - totalCount: int - Total rows in table
            - executionTime: float - Query execution time in ms
        """
        pass
    
    @abstractmethod
    def get_csn_definition(self, schema: str) -> Optional[Dict]:
        """
        Get CSN (Core Schema Notation) definition for a data product.
        
        Args:
            schema: Schema/data product name
            
        Returns:
            CSN definition dictionary or None if not available
        """
        pass