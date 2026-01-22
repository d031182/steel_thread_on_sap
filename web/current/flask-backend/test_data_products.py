"""
Quick test to verify data products can be loaded from HANA
"""
import os
from dotenv import load_dotenv
from hdbcli import dbapi

# Load environment
load_dotenv()

HANA_HOST = os.getenv('HANA_HOST')
HANA_PORT = int(os.getenv('HANA_PORT', '443'))
HANA_USER = os.getenv('HANA_USER')
HANA_PASSWORD = os.getenv('HANA_PASSWORD')

print("=" * 60)
print("Testing HANA Data Products Connection")
print("=" * 60)

try:
    # Connect to HANA
    print(f"\n1. Connecting to HANA...")
    print(f"   Host: {HANA_HOST}")
    print(f"   Port: {HANA_PORT}")
    print(f"   User: {HANA_USER}")
    
    connection = dbapi.connect(
        address=HANA_HOST,
        port=HANA_PORT,
        user=HANA_USER,
        password=HANA_PASSWORD,
        encrypt=True,
        sslValidateCertificate=False
    )
    print("   ✅ Connected successfully!")
    
    # Query data products
    print(f"\n2. Querying data product schemas...")
    cursor = connection.cursor()
    
    sql = """
    SELECT 
        SCHEMA_NAME,
        SCHEMA_OWNER,
        CREATE_TIME
    FROM SYS.SCHEMAS
    WHERE SCHEMA_NAME LIKE ?
    ORDER BY SCHEMA_NAME
    """
    
    cursor.execute(sql, ('_SAP_DATAPRODUCT%',))
    rows = cursor.fetchall()
    
    print(f"   ✅ Found {len(rows)} data product schemas")
    
    # Display results
    if rows:
        print(f"\n3. Data Products Found:")
        print("-" * 60)
        for i, row in enumerate(rows[:5], 1):  # Show first 5
            schema_name = row[0]
            # Extract product name
            parts = schema_name.split('_')
            product_name = 'Unknown'
            if 'dataProduct' in parts:
                dp_index = parts.index('dataProduct')
                if dp_index + 1 < len(parts):
                    product_name = parts[dp_index + 1]
            
            print(f"   {i}. {product_name}")
            print(f"      Schema: {schema_name}")
        
        if len(rows) > 5:
            print(f"   ... and {len(rows) - 5} more")
    else:
        print("   ⚠️  No data products found!")
        print("   This might indicate:")
        print("   - No data products installed in HANA")
        print("   - User doesn't have permission to see schemas")
    
    # Test getting tables from first schema
    if rows:
        print(f"\n4. Testing table query for first data product...")
        first_schema = rows[0][0]
        
        sql = """
        SELECT 
            TABLE_NAME,
            TABLE_TYPE,
            RECORD_COUNT
        FROM SYS.TABLES
        WHERE SCHEMA_NAME = ?
        ORDER BY TABLE_NAME
        """
        
        cursor.execute(sql, (first_schema,))
        tables = cursor.fetchall()
        
        print(f"   ✅ Found {len(tables)} tables in {first_schema}")
        
        if tables:
            print(f"\n   Sample tables:")
            for table in tables[:3]:
                print(f"   - {table[0]} ({table[1]}, {table[2]} records)")
    
    cursor.close()
    connection.close()
    
    print("\n" + "=" * 60)
    print("✅ TEST PASSED - Data products loading successfully!")
    print("=" * 60)
    
except Exception as e:
    print("\n" + "=" * 60)
    print("❌ TEST FAILED")
    print("=" * 60)
    print(f"Error: {str(e)}")
    import traceback
    print(traceback.format_exc())
