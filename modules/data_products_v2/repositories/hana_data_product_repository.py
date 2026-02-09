"""
HANA Data Product Repository

Adapter that wraps the core/_hana_repository.py to implement
the IDataProductRepository interface.

This follows the Adapter Pattern - taking existing HANA functionality
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
from core.repositories._hana_repository import _HanaRepository


class HANADataProductRepository(IDataProductRepository):
    """
    HANA Cloud implementation of data product repository
    
    Wraps the existing _HanaRepository and adapts it to the new
    IDataProductRepository interface (V2).
    
    Benefits:
    - Reuses tested HANA connection logic
    - Provides clean V2 interface
    - Enables source switching via interface
    
    Usage:
        repo = HANADataProductRepository(host, port, user, password)
        products = repo.get_data_products()
    """
    
    def __init__(self, host: str, port: int, user: str, password: str, 
                 database: Optional[str] = None, schema: Optional[str] = None):
        """
        Initialize HANA repository
        
        Args:
            host: HANA Cloud hostname
            port: HANA Cloud port (typically 443)
            user: Database user
            password: Database password
            database: Optional database name
            schema: Optional default schema
        """
        self._repository = _HanaRepository(host, port, user, password, database, schema)
    
    def get_data_products(self) -> List[DataProduct]:
        """
        Get all data products from HANA Cloud
        
        Returns:
            List of DataProduct domain models
        
        Raises:
            DataAccessError: If query fails or connection unavailable
        """
        try:
            # Call V1 HANA repository (returns List[Dict])
            products_dict = self._repository.get_data_products()
            
            # Adapt to V2 domain models
            products = []
            for p in products_dict:
                products.append(DataProduct(
                    product_name=p.get('name', 'Unknown'),
                    display_name=p.get('display_name', 'Unknown'),
                    namespace=p.get('namespace', 'sap.s4com'),
                    version=p.get('version', 'v1'),
                    schema_name=p.get('name', ''),  # Use 'name' as schema_name
                    source='hana',
                    description=f"HANA Cloud data product with {p.get('entity_count', 0)} entities",
                    owner=p.get('owner', 'SAP'),
                    create_time=p.get('created_at', 'N/A'),
                    table_count=p.get('entity_count', 0)
                ))
            
            return products
            
        except Exception as e:
            raise DataAccessError(f"Failed to get data products from HANA: {e}")
    
    def get_tables_in_product(self, product_name: str) -> List[Table]:
        """
        Get tables within a data product
        
        Args:
            product_name: Product name or schema name
        
        Returns:
            List of Table domain models
        
        Raises:
            ValueError: If product not found
            DataAccessError: If query fails
        """
        try:
            # V1 HANA repository expects schema name
            # For HANA, product_name IS the schema name
            schema_name = product_name
            
            # Call V1 repository (returns List[Dict])
            tables_dict = self._repository.get_tables(schema_name)
            
            # Adapt to V2 domain models
            tables = []
            for t in tables_dict:
                tables.append(Table(
                    table_name=t.get('name', t.get('TABLE_NAME', 'Unknown')),
                    table_type=t.get('type', t.get('TABLE_TYPE', 'TABLE')),
                    record_count=t.get('record_count', 0),
                    schema_name=schema_name
                ))
            
            return tables
            
        except Exception as e:
            raise DataAccessError(f"Failed to get tables for product {product_name}: {e}")
    
    def get_table_structure(self, product_name: str, table_name: str) -> List[Column]:
        """
        Get column structure for a table
        
        Args:
            product_name: Product name or schema name
            table_name: Table name
        
        Returns:
            List of Column domain models
        
        Raises:
            ValueError: If table not found
            DataAccessError: If query fails
        """
        try:
            # V1 HANA repository expects schema name
            schema_name = product_name
            
            # Call V1 repository (returns List[Dict])
            columns_dict = self._repository.get_table_structure(schema_name, table_name)
            
            # Adapt to V2 domain models
            columns = []
            for c in columns_dict:
                columns.append(Column(
                    column_name=c.get('name', c.get('COLUMN_NAME', 'Unknown')),
                    data_type=c.get('data_type', c.get('DATA_TYPE_NAME', 'VARCHAR')),
                    length=c.get('length', c.get('LENGTH')),
                    is_nullable=c.get('nullable', c.get('IS_NULLABLE', True)),
                    is_primary_key=c.get('isPrimaryKey', c.get('IS_PRIMARY_KEY', False)),
                    foreign_key=c.get('foreignKey', c.get('FOREIGN_KEY'))
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
            product_name: Product name or schema name
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
            # V1 HANA repository expects schema name
            schema_name = product_name
            
            # Call V1 repository (returns correct format)
            result = self._repository.query_table(
                schema=schema_name,
                table=table_name,
                limit=limit,
                offset=offset
            )
            
            # V1 repository already returns correct format!
            # {rows, columns, totalCount, executionTime}
            return result
            
        except Exception as e:
            raise DataAccessError(f"Failed to query {table_name}: {e}")
    
    def get_source_type(self) -> str:
        """Get source type"""
        return 'hana'
    
    def test_connection(self) -> bool:
        """
        Test HANA Cloud connection
        
        Returns:
            True if connection successful, False otherwise
        """
        try:
            # Try to get data products (quick query to SYS.SCHEMAS)
            self.get_data_products()
            return True
        except:
            return False