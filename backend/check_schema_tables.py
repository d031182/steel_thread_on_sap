"""
Quick script to check what tables exist in a HANA schema
"""
import os
import sys
from hdbcli import dbapi

# HANA connection details
HANA_HOST = os.getenv('HANA_HOST', '')
HANA_PORT = int(os.getenv('HANA_PORT', '443'))
HANA_USER = os.getenv('HANA_USER', '')
HANA_PASSWORD = os.getenv('HANA_PASSWORD', '')

schema_name = sys.argv[1] if len(sys.argv) > 1 else '_SAP_DATAPRODUCT_sap_s4com_dataProduct_PurchaseOrder_v1_7fb1fb77-5355-4c54-99aa-51127bb5e625'

print(f"Checking schema: {schema_name}\n")

# Connect
conn = dbapi.connect(
    address=HANA_HOST,
    port=HANA_PORT,
    user=HANA_USER,
    password=HANA_PASSWORD,
    encrypt=True,
    sslValidateCertificate=False
)

cursor = conn.cursor()

# Get all tables in schema
cursor.execute("""
    SELECT TABLE_NAME, TABLE_TYPE
    FROM SYS.TABLES
    WHERE SCHEMA_NAME = ?
    ORDER BY TABLE_NAME
""", (schema_name,))

tables = cursor.fetchall()

if tables:
    print(f"Found {len(tables)} tables:\n")
    for table_name, table_type in tables:
        print(f"  - {table_name} ({table_type})")
else:
    print("No tables found in this schema")
    print("\nLet me check all data product schemas...")
    
    cursor.execute("""
        SELECT SCHEMA_NAME
        FROM SYS.SCHEMAS
        WHERE SCHEMA_NAME LIKE '_SAP_DATAPRODUCT%'
        ORDER BY SCHEMA_NAME
    """)
    
    schemas = cursor.fetchall()
    print(f"\nFound {len(schemas)} data product schemas:")
    for (schema,) in schemas:
        print(f"  - {schema}")

cursor.close()
conn.close()