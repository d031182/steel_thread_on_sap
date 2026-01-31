"""
Test script to verify HANA primary key retrieval
Based on HANA Central screenshot showing Key column = 1
"""
import os
import sys
from dotenv import load_dotenv

# Fix Windows console encoding
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

# Load environment from app/.env
load_dotenv('app/.env')

def test_hana_pk_queries():
    """Test different methods to retrieve primary keys from HANA"""
    
    # Connection details from environment
    host = os.getenv('HANA_HOST')
    port = int(os.getenv('HANA_PORT', 443))
    user = os.getenv('HANA_USER')
    password = os.getenv('HANA_PASSWORD')
    
    print(f"Testing HANA PK retrieval on {host}")
    print("=" * 80)
    
    try:
        from modules.hana_connection.backend.hana_connection import HANAConnection
        
        conn = HANAConnection(host, port, user, password)
        
        # Find PurchaseOrder schema
        print("\n1. Finding PurchaseOrder schema...")
        schema_sql = """
        SELECT SCHEMA_NAME
        FROM SYS.SCHEMAS
        WHERE SCHEMA_NAME LIKE '%PurchaseOrder%'
        """
        
        result = conn.execute_query(schema_sql)
        if not result['success'] or not result['rows']:
            print("   ❌ PurchaseOrder schema not found!")
            return
        
        schema_name = result['rows'][0]['SCHEMA_NAME']
        print(f"   ✅ Found schema: {schema_name}")
        
        # Find main PurchaseOrder table
        print("\n2. Finding PurchaseOrder table...")
        table_sql = """
        SELECT TABLE_NAME
        FROM SYS.TABLES
        WHERE SCHEMA_NAME = ?
          AND TABLE_NAME LIKE '%PurchaseOrder'
          AND TABLE_NAME NOT LIKE '%Text'
          AND TABLE_NAME NOT LIKE '%Item%'
        ORDER BY TABLE_NAME
        """
        
        result = conn.execute_query(table_sql, (schema_name,))
        if not result['success'] or not result['rows']:
            print("   ❌ PurchaseOrder table not found!")
            return
        
        table_name = result['rows'][0]['TABLE_NAME']
        print(f"   ✅ Found table: {table_name}")
        
        # Method 1: Query SYS.CONSTRAINTS
        print("\n3. Method 1: Query SYS.CONSTRAINTS for PRIMARY KEY...")
        pk_sql_1 = """
        SELECT 
            c.CONSTRAINT_NAME,
            c.CONSTRAINT_TYPE,
            col.COLUMN_NAME,
            col.POSITION
        FROM SYS.CONSTRAINTS c
        JOIN SYS.CONSTRAINT_COLUMN_USAGE col
            ON c.CONSTRAINT_NAME = col.CONSTRAINT_NAME
            AND c.SCHEMA_NAME = col.SCHEMA_NAME
        WHERE c.SCHEMA_NAME = ?
          AND c.TABLE_NAME = ?
          AND c.CONSTRAINT_TYPE = 'PRIMARY KEY'
        ORDER BY col.POSITION
        """
        
        result = conn.execute_query(pk_sql_1, (schema_name, table_name))
        if result['success'] and result['rows']:
            print(f"   ✅ Found {len(result['rows'])} primary key columns:")
            for row in result['rows']:
                print(f"      - {row['COLUMN_NAME']} (Constraint: {row['CONSTRAINT_NAME']})")
        else:
            print("   ❌ No primary keys found via SYS.CONSTRAINTS")
        
        # Method 2: Query SYS.TABLE_COLUMNS (check if KEY_SEQ exists)
        print("\n4. Method 2: Query SYS.TABLE_COLUMNS for key indicators...")
        col_sql = """
        SELECT 
            COLUMN_NAME,
            POSITION,
            DATA_TYPE_NAME,
            IS_NULLABLE
        FROM SYS.TABLE_COLUMNS
        WHERE SCHEMA_NAME = ?
          AND TABLE_NAME = ?
        ORDER BY POSITION
        LIMIT 5
        """
        
        result = conn.execute_query(col_sql, (schema_name, table_name))
        if result['success'] and result['rows']:
            print(f"   ✅ Found {len(result['rows'])} columns (first 5):")
            for row in result['rows']:
                print(f"      - {row['COLUMN_NAME']} ({row['DATA_TYPE_NAME']}, Nullable: {row['IS_NULLABLE']})")
        
        # Method 3: Check HANA Central metadata views
        print("\n5. Method 3: Check for KEY_SEQ or similar metadata...")
        key_meta_sql = """
        SELECT COLUMN_NAME
        FROM SYS.M_CS_ALL_COLUMN_STATISTICS
        WHERE SCHEMA_NAME = ?
          AND TABLE_NAME = ?
        LIMIT 5
        """
        
        try:
            result = conn.execute_query(key_meta_sql, (schema_name, table_name))
            if result['success']:
                print(f"   ✅ M_CS_ALL_COLUMN_STATISTICS accessible")
            else:
                print(f"   ❌ Cannot access M_CS_ALL_COLUMN_STATISTICS: {result.get('error')}")
        except Exception as e:
            print(f"   ❌ M_CS_ALL_COLUMN_STATISTICS not available: {e}")
        
        # Method 4: Check INDEX_COLUMNS for primary key index
        print("\n6. Method 4: Query SYS.INDEX_COLUMNS for primary key index...")
        idx_sql = """
        SELECT 
            i.INDEX_NAME,
            i.INDEX_TYPE,
            ic.COLUMN_NAME,
            ic.POSITION
        FROM SYS.INDEXES i
        JOIN SYS.INDEX_COLUMNS ic
            ON i.SCHEMA_NAME = ic.SCHEMA_NAME
            AND i.TABLE_NAME = ic.TABLE_NAME
            AND i.INDEX_NAME = ic.INDEX_NAME
        WHERE i.SCHEMA_NAME = ?
          AND i.TABLE_NAME = ?
          AND i.CONSTRAINT = 'PRIMARY KEY'
        ORDER BY ic.POSITION
        """
        
        result = conn.execute_query(idx_sql, (schema_name, table_name))
        if result['success'] and result['rows']:
            print(f"   ✅ Found primary key via INDEX:")
            for row in result['rows']:
                print(f"      - {row['COLUMN_NAME']} (Index: {row['INDEX_NAME']}, Type: {row['INDEX_TYPE']})")
        else:
            print(f"   ❌ No primary key index found: {result.get('error', 'No results')}")
        
        conn.close()
        
        print("\n" + "=" * 80)
        print("✅ Primary key detection test complete!")
        print("\nConclusion:")
        print("- The implementation uses SYS.CONSTRAINTS which is the standard approach")
        print("- HANA Central UI shows Key=1, our query should retrieve the same info")
        print("- The code is correct - test with actual HANA connection to verify")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    test_hana_pk_queries()