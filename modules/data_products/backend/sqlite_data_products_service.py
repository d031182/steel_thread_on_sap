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
                'p2p_data.db'
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
        
        Dynamically discovers data products based on table naming patterns.
        Groups tables by entity prefix (e.g., PurchaseOrder*, SupplierInvoice*).
        
        Returns:
            List of data product metadata dictionaries
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # Get all tables
            cursor.execute("""
                SELECT name
                FROM sqlite_master
                WHERE type='table' AND name NOT LIKE 'sqlite_%'
                ORDER BY name
            """)
            
            table_names = [row[0] for row in cursor.fetchall()]
            
            # Group tables by data product (base entity name)
            data_products = {}
            
            for table_name in table_names:
                # Determine base product using comprehensive logic
                base = None
                
                # Special cases first
                if table_name == 'PurOrdSupplierConfirmation':
                    base = 'PurchaseOrder'
                elif table_name == 'JournalEntryItemBillOfExchange':
                    base = 'JournalEntry'
                elif table_name == 'PaymentTermsConditionsText':
                    base = 'PaymentTerms'
                # Company Code group
                elif table_name.startswith('CompanyCode') or table_name == 'CurrencyRole' or table_name == 'CurrencyRoleText':
                    base = 'CompanyCode'
                # Cost Center group
                elif table_name.startswith('CostCenter'):
                    base = 'CostCenter'
                # Product group (includes Prod* prefix tables)
                elif table_name.startswith('Product') or table_name.startswith('Prod'):
                    base = 'Product'
                # Payment Terms group
                elif table_name.startswith('PaymentTerms'):
                    base = 'PaymentTerms'
                # Purchase Order group
                elif table_name.startswith('PurchaseOrder'):
                    base = 'PurchaseOrder'
                # Supplier Invoice group (check BEFORE Supplier!)
                elif table_name.startswith('SupplierInvoice'):
                    base = 'SupplierInvoice'
                # Supplier group
                elif table_name.startswith('Supplier'):
                    base = 'Supplier'
                # Service Entry Sheet group
                elif table_name.startswith('ServiceEntrySheet'):
                    base = 'ServiceEntrySheet'
                # Journal Entry group
                elif table_name.startswith('JournalEntry'):
                    base = 'JournalEntry'
                else:
                    # Fallback: use table name itself
                    base = table_name
                
                if base not in data_products:
                    data_products[base] = []
                data_products[base].append(table_name)
            
            # Build data product list
            products = []
            for product_name, tables in data_products.items():
                # Get total column count across all tables
                total_columns = 0
                for table in tables:
                    cursor.execute(f"PRAGMA table_info({table})")
                    total_columns += len(cursor.fetchall())
                
                # Get friendly display name to match HANA Cloud
                display_names = {
                    'CompanyCode': 'Company Code',
                    'CostCenter': 'Cost Center',
                    'Product': 'Product',
                    'PurchaseOrder': 'Purchase Order',
                    'SupplierInvoice': 'Supplier Invoice',
                    'Supplier': 'Supplier',
                    'PaymentTerms': 'Payment Terms',
                    'ServiceEntrySheet': 'Service Entry Sheet',
                    'JournalEntry': 'Journal Entry Header'
                }
                
                products.append({
                    'productName': product_name,
                    'displayName': f"{display_names.get(product_name, product_name)} (Local)",
                    'namespace': 'sap.s4.com',
                    'version': '1.0',
                    'schemaName': f'SQLITE_{product_name.upper()}',
                    'source': 'sqlite',
                    'description': f'{product_name} data with {len(tables)} table(s) and {total_columns} columns',
                    'owner': 'Local Database',
                    'createTime': 'N/A (Local)',
                    'tableCount': len(tables)
                })
            
            return products
        
        finally:
            conn.close()
    
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
            # Extract product name from schema (e.g., 'SQLITE_PURCHASEORDER' -> 'PurchaseOrder')
            product_name = schema.replace('SQLITE_', '').lower()
            
            # Get all tables
            cursor.execute("""
                SELECT name, type
                FROM sqlite_master
                WHERE type='table' AND name NOT LIKE 'sqlite_%'
                ORDER BY name
            """)
            
            all_tables = [(row[0], row[1]) for row in cursor.fetchall()]
            
            # Group tables by product using EXACT SAME logic as get_data_products()
            product_tables = {}
            for table_name, table_type in all_tables:
                # Determine base product using comprehensive logic
                base = None
                
                # Special cases first
                if table_name == 'PurOrdSupplierConfirmation':
                    base = 'PurchaseOrder'
                elif table_name == 'JournalEntryItemBillOfExchange':
                    base = 'JournalEntry'
                elif table_name == 'PaymentTermsConditionsText':
                    base = 'PaymentTerms'
                # Company Code group
                elif table_name.startswith('CompanyCode') or table_name == 'CurrencyRole' or table_name == 'CurrencyRoleText':
                    base = 'CompanyCode'
                # Cost Center group
                elif table_name.startswith('CostCenter'):
                    base = 'CostCenter'
                # Product group (includes Prod* prefix tables)
                elif table_name.startswith('Product') or table_name.startswith('Prod'):
                    base = 'Product'
                # Payment Terms group
                elif table_name.startswith('PaymentTerms'):
                    base = 'PaymentTerms'
                # Purchase Order group
                elif table_name.startswith('PurchaseOrder'):
                    base = 'PurchaseOrder'
                # Supplier Invoice group (check BEFORE Supplier!)
                elif table_name.startswith('SupplierInvoice'):
                    base = 'SupplierInvoice'
                # Supplier group
                elif table_name.startswith('Supplier'):
                    base = 'Supplier'
                # Service Entry Sheet group
                elif table_name.startswith('ServiceEntrySheet'):
                    base = 'ServiceEntrySheet'
                # Journal Entry group
                elif table_name.startswith('JournalEntry'):
                    base = 'JournalEntry'
                else:
                    # Fallback: use table name itself
                    base = table_name
                
                if base.lower() not in product_tables:
                    product_tables[base.lower()] = []
                product_tables[base.lower()].append(table_name)
            
            # Get tables for this specific product
            tables = []
            if product_name in product_tables:
                for table_name in product_tables[product_name]:
                    # Get row count
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
        Get column structure for a table including foreign key constraints.
        
        Args:
            schema: Schema name
            table: Table name
        
        Returns:
            List of column metadata dictionaries with FK information
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # Get table info using PRAGMA
            cursor.execute(f"PRAGMA table_info({table})")
            table_info = cursor.fetchall()
            
            # Get foreign key info using PRAGMA
            cursor.execute(f"PRAGMA foreign_key_list({table})")
            fk_info = cursor.fetchall()
            
            # Build FK map: {column_name: "referenced_table(referenced_column)"}
            fk_map = {}
            for fk_row in fk_info:
                # PRAGMA foreign_key_list returns: (id, seq, table, from, to, on_update, on_delete, match)
                from_col = fk_row[3]  # from column
                to_table = fk_row[2]  # referenced table
                to_col = fk_row[4]    # referenced column
                fk_map[from_col] = f"{to_table}({to_col})"
            
            # Build column list with FK information
            columns = []
            for row in table_info:
                # PRAGMA table_info returns: (cid, name, type, notnull, dflt_value, pk)
                column_name = row[1]
                fk_constraint = fk_map.get(column_name, None)
                
                columns.append({
                    'COLUMN_NAME': column_name,
                    'name': column_name,
                    'DATA_TYPE_NAME': row[2],
                    'dataType': row[2],
                    'LENGTH': None,  # SQLite doesn't store length
                    'length': None,
                    'IS_NULLABLE': row[3] == 0,  # notnull=0 means nullable
                    'nullable': row[3] == 0,
                    'IS_PRIMARY_KEY': row[5] > 0,  # pk>0 means primary key
                    'isPrimaryKey': row[5] > 0,
                    'FOREIGN_KEY': fk_constraint,  # e.g., "Supplier(SupplierID)"
                    'foreignKey': fk_constraint
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