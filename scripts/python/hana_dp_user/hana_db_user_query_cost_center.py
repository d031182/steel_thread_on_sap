from hdbcli import dbapi

conn = dbapi.connect(
    address='20bb37c7-0dd0-4369-82bf-5366b234c948.hna1.prod-eu10.hanacloud.ondemand.com',
    port=443,
    user='HANA_DP_USER',
    password='YourSecurePassword123!',
    encrypt=True,
    sslValidateCertificate=False
)

cursor = conn.cursor()

print("=== Discovering Available Data Product Tables ===\n")

# First, discover what tables exist
cursor.execute("""
    SELECT SCHEMA_NAME, TABLE_NAME 
    FROM SYS.TABLES 
    WHERE SCHEMA_NAME LIKE '_SAP_DATAPRODUCT%'
    ORDER BY SCHEMA_NAME, TABLE_NAME
""")

print(f"{'SCHEMA':<80} {'TABLE':<50}")
print("-" * 130)

tables = []
for row in cursor.fetchall():
    schema = row[0]
    table = row[1]
    print(f"{schema:<80} {table:<50}")
    tables.append((schema, table))

print(f"\n=== Found {len(tables)} tables ===\n")

# Query first table if any exist
if tables:
    schema, table = tables[0]
    print(f"=== Querying: {table} ===\n")
    
    try:
        query = f'SELECT * FROM "{schema}"."{table}" LIMIT 5'
        cursor.execute(query)
        
        # Get column names
        columns = [desc[0] for desc in cursor.description]
        print("Columns:", ", ".join(columns))
        print()
        
        # Print rows
        rows = cursor.fetchall()
        for i, row in enumerate(rows, 1):
            print(f"Row {i}:", row)
        
        print(f"\n[OK] Successfully queried {len(rows)} rows")
        
    except Exception as e:
        print(f"[ERROR] Failed to query: {e}")
else:
    print("[WARNING] No data product tables found!")

cursor.close()
conn.close()
