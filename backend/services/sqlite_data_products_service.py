"""
SQLite Data Products Service

Provides access to local SQLite database containing PurchaseOrder sample data.
This service enables offline development and testing without requiring HANA Cloud connection.

Data Source: backend/database/schema/purchaseorder.sql
Tables: 5 (PurchaseOrder, PurchaseOrderItem, PurchaseOrderScheduleLine, 
         PurchaseOrderAccountAssignment, PurOrdSupplierConfirmation)
Columns: 321 total across all tables
"""

import sqlite3
import os
from typing import List, Dict, Optional


class SQLiteDataProductsService:
    """
    Service for accessing data products from local SQLite database.
    
    Currently supports:
    - PurchaseOrder data product with 5 tables
    - Structure information (columns, types, etc.)
    - Sample data queries
    
    Future: Can be extended to include other P2P data products
    """
    
    def __init__(self, db_path: str = None):
        """
        Initialize SQLite service.
        
        Args:
            db_path: Path to SQLite database file. 
                    Defaults to 'backend/database/p2p_sample.db'
        """
        if db_path is None:
            # Default to sample database location
            db_path = os.path.join(
                os.path.dirname(__file__),
                '..',
                'database',
                'p2p_sample.db'
            )
        
        self.db_path = db_path
        self._ensure_database()
    
    def _ensure_database(self):
        """
        Ensure database exists. If not, create it from schema.
        """
        if not os.path.exists(self.db_path):
            # Create database directory if needed
            os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
            
            # Create database from schema
            schema_path = os.path.join(
                os.path.dirname(__file__),
                '..',
                'database',
                'schema',
                'purchaseorder.sql'
            )
            
            if os.path.exists(schema_path):
                with open(schema_path, 'r') as f:
                    schema_sql = f.read()
                
                conn = sqlite3.connect(self.db_path)
                try:
                    conn.executescript(schema_sql)
                    conn.commit()
                except Exception as e:
                    print(f"Error creating database: {e}")
                finally:
                    conn.close()
    
    def get_data_products(self) -> List[Dict]:
        """
        Get list of available data products in SQLite.
        
        Currently returns only PurchaseOrder data product.
        
        Returns:
            List of data product metadata dictionaries
        """
        return [{
            'productName': 'PurchaseOrder',
            'displayName': 'Purchase Order (Local)',
            'namespace': 'sap.s4.com',
            'version': '1.0',
            'schemaName': 'SQLITE_PURCHASEORDER',
            'source': 'sqlite',
            'description': 'Purchase order data with 5 tables and 321 columns',
            'owner': 'Local Database',
            'createTime': 'N/A (Local)',
            'tableCount': 5
        }]
    
    def get_tables(self, schema: str) -> List[Dict]:
        """
        Get list of tables for a data product.
        
        Args:
            schema: Schema name (e.g., 'SQLITE_PURCHASEORDER')
        
        Returns:
            List of table metadata dictionaries
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # Get all tables from sqlite_master
            cursor.execute("""
                SELECT name, type
                FROM sqlite_master
                WHERE type='table' AND name NOT LIKE 'sqlite_%'
                ORDER BY name
            """)
            
            tables = []
            for row in cursor.fetchall():
                table_name = row[0]
                
                # Get row count for each table
                try:
                    cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
                    count = cursor.fetchone()[0]
                except:
                    count = 0
                
                tables.append({
                    'TABLE_NAME': table_name,
                    'TABLE_TYPE': 'TABLE',
                    'RECORD_COUNT': count
                })
            
            return tables
        
        finally:
            conn.close()
    
    def get_table_structure(self, schema: str, table: str) -> List[Dict]:
        """
        Get column structure for a table.
        
        Args:
            schema: Schema name
            table: Table name
        
        Returns:
            List of column metadata dictionaries
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # Get table info using PRAGMA
            cursor.execute(f"PRAGMA table_info({table})")
            
            columns = []
            for row in cursor.fetchall():
                # PRAGMA returns: (cid, name, type, notnull, dflt_value, pk)
                columns.append({
                    'COLUMN_NAME': row[1],
                    'name': row[1],
                    'DATA_TYPE_NAME': row[2],
                    'dataType': row[2],
                    'LENGTH': None,  # SQLite doesn't store length
                    'length': None,
                    'IS_NULLABLE': row[3] == 0,  # notnull=0 means nullable
                    'nullable': row[3] == 0,
                    'IS_PRIMARY_KEY': row[5] > 0,  # pk>0 means primary key
                    'isPrimaryKey': row[5] > 0
                })
            
            return columns
        
        finally:
            conn.close()
    
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
            schema: Schema name
            table: Table name
            limit: Maximum rows to return
            offset: Number of rows to skip
        
        Returns:
            Dictionary with rows, columns, totalCount, executionTime
        """
        import time
        start_time = time.time()
        
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # Enable column access by name
        cursor = conn.cursor()
        
        try:
            # Get total count
            cursor.execute(f"SELECT COUNT(*) FROM {table}")
            total_count = cursor.fetchone()[0]
            
            # Get data with limit/offset
            cursor.execute(
                f"SELECT * FROM {table} LIMIT ? OFFSET ?",
                (limit, offset)
            )
            
            rows = []
            columns_info = []
            
            for row in cursor.fetchall():
                # Convert Row to dict
                row_dict = dict(row)
                rows.append(row_dict)
                
                # Build columns info on first row
                if not columns_info:
                    columns_info = [
                        {'name': col, 'type': type(row_dict[col]).__name__}
                        for col in row.keys()
                    ]
            
            execution_time = (time.time() - start_time) * 1000  # Convert to ms
            
            return {
                'rows': rows,
                'columns': columns_info,
                'totalCount': total_count,
                'executionTime': round(execution_time, 2)
            }
        
        finally:
            conn.close()
    
    def get_csn_definition(self, schema: str) -> Optional[Dict]:
        """
        Get CSN definition for a data product.
        
        Note: CSN is not stored in SQLite. This returns None.
        For CSN access, use HANA Cloud source.
        
        Args:
            schema: Schema name
        
        Returns:
            None (CSN not available in SQLite)
        """
        return None