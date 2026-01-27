#!/usr/bin/env python3
"""
Grant HANA_DP_USER Access to Data Products
Using: Python hdbcli
Execute as: DBADMIN
"""

import json
import sys
import os
from pathlib import Path
from hdbcli import dbapi

# Find default-env.json in scripts/python/ directory
script_dir = Path(__file__).resolve().parent
env_file = script_dir.parent / 'default-env.json'

# Load HANA credentials
try:
    with open(env_file, 'r') as f:
        env = json.load(f)
    hana = env['VCAP_SERVICES']['hana'][0]['credentials']
except Exception as e:
    print(f"ERROR: Failed to load {env_file}: {e}")
    print(f"Looking in: {env_file}")
    sys.exit(1)

HANA_HOST = hana['host']
HANA_PORT = hana['port']
HANA_USER = hana['user']
HANA_PASSWORD = hana['password']

print("=== Connecting to HANA Cloud ===")
print(f"Host: {HANA_HOST}")
print(f"Port: {HANA_PORT}")
print(f"User: {HANA_USER}")
print()

# Connect to HANA
try:
    conn = dbapi.connect(
        address=HANA_HOST,
        port=HANA_PORT,
        user=HANA_USER,
        password=HANA_PASSWORD,
        encrypt=True,
        sslValidateCertificate=False
    )
    cursor = conn.cursor()
    print("[OK] Connected successfully")
    print()
except Exception as e:
    print(f"ERROR: Failed to connect: {e}")
    sys.exit(1)

# ============================================
# STEP 1: Find Data Product Schemas
# ============================================

print("=== Step 1: Finding Data Product Schemas ===")

try:
    cursor.execute("""
        SELECT SCHEMA_NAME 
        FROM SYS.SCHEMAS 
        WHERE SCHEMA_NAME LIKE '_SAP_DATAPRODUCT%' 
        ORDER BY SCHEMA_NAME
    """)
    
    schemas = [row[0] for row in cursor.fetchall()]
    
    if not schemas:
        print("WARNING: No data product schemas found!")
        print("Make sure data products are installed in HANA Cloud Central")
        sys.exit(0)
    
    for schema in schemas:
        print(f"  Found: {schema}")
    
    print()
    print(f"Found {len(schemas)} data product schema(s)")
    print()
    
except Exception as e:
    print(f"ERROR: Failed to query schemas: {e}")
    sys.exit(1)

# ============================================
# STEP 2: Grant Basic Privileges
# ============================================

print("=== Step 2: Granting Basic Privileges ===")

try:
    cursor.execute("GRANT CATALOG READ TO HANA_DP_USER")
    print("  [OK] Granted CATALOG READ")
except Exception as e:
    print(f"  [SKIP] CATALOG READ (may already exist): {e}")

try:
    cursor.execute("GRANT CONNECT TO HANA_DP_USER")
    print("  [OK] Granted CONNECT")
except Exception as e:
    print(f"  [SKIP] CONNECT (may already exist): {e}")

print()

# ============================================
# STEP 3: Grant SELECT on Each Data Product Schema
# ============================================

print("=== Step 3: Granting SELECT on Data Product Schemas ===")

success_count = 0
fail_count = 0

for schema in schemas:
    print(f"Granting SELECT on: {schema}")
    try:
        grant_sql = f'GRANT SELECT ON SCHEMA "{schema}" TO HANA_DP_USER'
        cursor.execute(grant_sql)
        print("  [OK] Granted successfully")
        success_count += 1
    except Exception as e:
        print(f"  [SKIP] May already be granted: {e}")
        fail_count += 1

print()
print("=== Grant Summary ===")
print(f"  Success: {success_count}")
print(f"  Skipped: {fail_count} (may already exist)")
print()

# ============================================
# STEP 4: Verify Grants
# ============================================

print("=== Step 4: Verifying Grants ===")

try:
    cursor.execute("""
        SELECT SCHEMA_NAME, PRIVILEGE 
        FROM SYS.GRANTED_PRIVILEGES 
        WHERE GRANTEE = 'HANA_DP_USER' 
        AND SCHEMA_NAME LIKE '_SAP_DATAPRODUCT%' 
        ORDER BY SCHEMA_NAME, PRIVILEGE
    """)
    
    print()
    print("=== Granted Privileges ===")
    print(f"{'SCHEMA_NAME':<60} {'PRIVILEGE':<20}")
    print("-" * 80)
    
    for row in cursor.fetchall():
        print(f"{row[0]:<60} {row[1]:<20}")
    
    print()
    
except Exception as e:
    print(f"ERROR: Failed to verify grants: {e}")

# Close connection
cursor.close()
conn.close()

# ============================================
# STEP 5: Summary
# ============================================

print("=== Next Steps ===")
print()
print("Test access by running:")
print("  python sql/hana/test_hana_dp_user_access.py")
print()
print("[OK] Setup complete!")