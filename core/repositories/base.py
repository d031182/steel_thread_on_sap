"""
Repository Pattern Base Interface

Abstract base class for all repository implementations (SQLite, HANA, etc.).
Following Domain-Driven Design (DDD) principles for data access abstraction.

Industry Standard: Repository Pattern provides collection-like interface,
hiding database specifics from business logic. Enables easy testing via
mock repositories and supports multi-backend architectures.

References:
- Cosmic Python (cosmicpython.com)
- Domain-Driven Design (DDD) by Eric Evans
- Repository Pattern (Martin Fowler)
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Optional


class AbstractRepository(ABC):
    """
    Abstract repository interface for data access.
    
    Consumers should ONLY use this interface, never concrete implementations.
    Implementations are private and accessed via factory pattern.
    
    Benefits:
    - Full decoupling: Business logic sees "in-memory collections"
    - Easy testing: Mock FakeRepository without real database
    - Multi-backend: Swap SQLite/HANA/PostgreSQL without code changes
    - Dependency Injection: Repository injected via app context
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
    
    @abstractmethod
    def execute_query(self, sql: str, params: tuple = None) -> Dict:
        """
        Execute arbitrary SQL query.
        
        This method allows execution of raw SQL for use cases like:
        - SQL Playground / interactive query tool
        - Data exploration
        - Advanced queries not covered by structured methods
        - KPI calculations and aggregations
        
        Args:
            sql: SQL query string
            params: Optional tuple of query parameters for parameterized queries
            
        Returns:
            Dictionary with:
            - success: bool - Whether query executed successfully
            - rows: List[Dict] - Query results (empty list if no results)
            - columns: List[str] - Column names
            - rowCount: int - Number of rows returned
            - executionTime: float - Query execution time in milliseconds
            - error: Dict - Error details if success=False
                - message: str - Error message
                - code: str - Error code
        
        Note:
            - This method should handle both SELECT and DML statements
            - Implementation should provide appropriate error handling
            - Execution time should include query + result fetch time
        """
        pass
    
    @abstractmethod
    def get_connection_info(self) -> Dict[str, any]:
        """
        Get generic connection information for this repository.
        
        Enables modules to access repository-specific metadata without
        breaking abstraction or using hasattr() checks on implementation details.
        
        Use Cases:
        - Cache path resolution (SQLite needs db_path for ontology cache)
        - Connection pooling info (HANA connection details)
        - Logging/monitoring metadata
        - Generic configuration access
        
        Returns:
            Dictionary with repository-specific keys. Common patterns:
            
            SQLite:
                {
                    'type': 'sqlite',
                    'db_path': '/path/to/database.db',
                    'in_memory': False
                }
            
            HANA:
                {
                    'type': 'hana',
                    'host': 'hana.example.com',
                    'port': 443,
                    'database': 'DBNAME',
                    'schema': 'SCHEMA'
                }
            
            Note: Keys are intentionally flexible to accommodate different
            repository types without forcing a rigid structure.
        
        Example Usage:
            ```python
            # Clean DI approach (no hasattr checks!)
            conn_info = repository.get_connection_info()
            
            if conn_info.get('type') == 'sqlite':
                db_path = conn_info.get('db_path')
                # Use for cache or logging
            ```
        
        Benefits:
        - ✅ Preserves abstraction (interface-level, not implementation)
        - ✅ Eliminates hasattr() anti-pattern
        - ✅ Easy to test and mock
        - ✅ Works with any repository type
        """
        pass