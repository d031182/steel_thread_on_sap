from hdbcli import dbapi

# Connect
conn = dbapi.connect(
    address='20bb37c7-0dd0-4369-82bf-5366b234c948.hna1.prod-eu10.hanacloud.ondemand.com',
    port=443,
    user='HANA_DP_USER',
    password='YourSecurePassword123!',
    encrypt=True,
    sslValidateCertificate=False
)

cursor = conn.cursor()

# List all data product tables
cursor.execute("""
    SELECT SCHEMA_NAME, TABLE_NAME 
    FROM SYS.TABLES 
    WHERE SCHEMA_NAME LIKE '_SAP_DATAPRODUCT%'
    ORDER BY SCHEMA_NAME, TABLE_NAME
""")

print("Available Data Product Tables:")
print(f"{'SCHEMA':<70} {'TABLE':<50}")
print("-" * 120)

for row in cursor.fetchall():
    print(f"{row[0]:<70} {row[1]:<50}")

cursor.close()
conn.close()