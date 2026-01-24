#!/usr/bin/env python3
"""
Grant CSN Access to P2P_DP_USER (requires SYSTEM user)
Run as SYSTEM to grant privileges on system schemas
"""

import os
import sys
from hdbcli import dbapi

# HANA connection details
HANA_HOST = os.getenv('HANA_HOST', 'e7decab9-3e98-41cf-bbf7-d0a8c13d7fb9.hana.prod-eu10.hanacloud.ondemand.com')
HANA_PORT = int(os.getenv('HANA_PORT', '443'))
HANA_USER = os.getenv('HANA_USER', 'SYSTEM')  # Must be SYSTEM user
HANA_PASSWORD = os.getenv('HANA_PASSWORD', '')

def grant_system_privileges():
    """Grant system schema privileges to P2P_DP_USER"""
    
    if not HANA_PASSWORD:
        print("❌ ERROR: HANA_PASSWORD environment variable not set")
        print("Please set SYSTEM user password:")
        print("   PowerShell: $env:HANA_PASSWORD='system-password'")
        return False
    
    print(f"🔌 Connecting to HANA Cloud as SYSTEM...")
    print(f"   Host: {HANA_HOST}")
    print(f"   Port: {HANA_PORT}")
    print(f"   User: {HANA_USER}")
    
    try:
        # Connect to HANA
        conn = dbapi.connect(
            address=HANA_HOST,
            port=HANA_PORT,
            user=HANA_USER,
            password=HANA_PASSWORD,
            encrypt=True,
            sslValidateCertificate=False
        )
        
        print("✅ Connected successfully as SYSTEM!")
        
        cursor = conn.cursor()
        
        # Read SQL script
        print("\n📄 Reading grant script...")
        with open('grant_csn_access_system.sql', 'r', encoding='utf-8') as f:
            sql_script = f.read()
        
        # Split by SQL statements
        statements = sql_script.split(';')
        
        sql_statements = []
        for stmt in statements:
            lines = []
            for line in stmt.split('\n'):
                stripped = line.strip()
                if not stripped.startswith('--') and stripped:
                    lines.append(line)
            
            clean_stmt = '\n'.join(lines).strip()
            
            # Only skip SELECT statements (verification queries)
            if clean_stmt and not clean_stmt.upper().startswith('SELECT'):
                sql_statements.append(clean_stmt)
        
        print(f"📝 Found {len(sql_statements)} GRANT statements to execute\n")
        
        # Execute each grant
        success_count = 0
        error_count = 0
        
        for i, stmt in enumerate(sql_statements, 1):
            preview = stmt[:80].replace('\n', ' ') + '...' if len(stmt) > 80 else stmt
            print(f"[{i}/{len(sql_statements)}] Executing: {preview}")
            
            try:
                cursor.execute(stmt)
                conn.commit()
                print(f"    ✅ Success")
                success_count += 1
            except dbapi.Error as e:
                error_code = getattr(e, 'errorcode', 'UNKNOWN')
                error_msg = str(e)
                
                # Check if already granted
                if 'already granted' in error_msg.lower() or error_code == 377:
                    print(f"    ⚠️  Already granted (skipping)")
                    success_count += 1
                else:
                    print(f"    ❌ Error {error_code}: {error_msg}")
                    error_count += 1
        
        print(f"\n{'='*60}")
        print(f"📊 Results:")
        print(f"   ✅ Successful: {success_count}")
        print(f"   ❌ Errors: {error_count}")
        print(f"{'='*60}\n")
        
        # Verification queries
        print("🔍 Running verification queries...\n")
        
        # Query 1: Count all privileges
        print("[1] Checking total privileges...")
        cursor.execute("SELECT COUNT(*) FROM SYS.GRANTED_PRIVILEGES WHERE GRANTEE = 'P2P_DP_USER'")
        total_privs = cursor.fetchone()[0]
        print(f"    ✅ Total privileges: {total_privs}")
        
        # Query 2: Check table-level grants
        print("\n[2] Checking table-level grants...")
        cursor.execute("""
            SELECT SCHEMA_NAME, OBJECT_NAME, PRIVILEGE
            FROM SYS.GRANTED_PRIVILEGES
            WHERE GRANTEE = 'P2P_DP_USER'
            AND OBJECT_TYPE = 'TABLE'
            ORDER BY SCHEMA_NAME, OBJECT_NAME
        """)
        table_grants = cursor.fetchall()
        print(f"    ✅ Table grants: {len(table_grants)}")
        for grant in table_grants:
            print(f"       - {grant[0]}.{grant[1]}: {grant[2]}")
        
        # Query 3: THE BIG TEST - CSN Table Access ⭐⭐⭐
        print("\n[3] 🎯 TESTING CSN TABLE ACCESS...")
        try:
            cursor.execute('''
                SELECT REMOTE_SOURCE_NAME, 
                       LEFT(CSN_JSON, 100) as CSN_PREVIEW
                FROM "_SAP_DB_ACCESS_DATA_PRODUCT_GATEWAY"."_SAP_DATAPRODUCT_DELTA_CSN"
            ''')
            csn_rows = cursor.fetchall()
            
            print(f"\n{'='*60}")
            print(f"🎉🎉🎉 SUCCESS! CSN TABLE ACCESS WORKS! 🎉🎉🎉")
            print(f"{'='*60}")
            print(f"    ✅ Found {len(csn_rows)} CSN records:")
            for row in csn_rows:
                print(f"       - {row[0]}")
                print(f"         Preview: {row[1][:50]}...")
            print(f"{'='*60}\n")
            
        except dbapi.Error as e:
            error_code = getattr(e, 'errorcode', 'UNKNOWN')
            print(f"\n❌❌❌ CSN ACCESS FAILED ❌❌❌")
            print(f"    Error {error_code}: {str(e)}")
            print(f"    This should not happen if grants succeeded!\n")
        
        cursor.close()
        conn.close()
        
        print(f"{'='*60}")
        print(f"✅ SYSTEM GRANTS COMPLETE!")
        print(f"{'='*60}\n")
        print(f"📝 Next steps:")
        print(f"   1. Update backend config to use P2P_DP_USER")
        print(f"   2. Implement CSN viewer endpoint")
        print(f"   3. Deploy and test!")
        print(f"\n")
        
        return True
        
    except dbapi.Error as e:
        error_code = getattr(e, 'errorcode', 'UNKNOWN')
        print(f"\n❌ HANA Error {error_code}: {str(e)}")
        return False
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    print("="*60)
    print("Grant System Privileges to P2P_DP_USER")
    print("="*60)
    print("⚠️  Must run as SYSTEM user!")
    print("="*60)
    print()
    
    success = grant_system_privileges()
    sys.exit(0 if success else 1)