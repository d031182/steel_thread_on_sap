#!/usr/bin/env python3
"""
Script to create P2P_DP_USER in HANA Cloud
Uses hdbcli to execute SQL from create_p2p_data_product_user_with_csn.sql
"""

import os
import sys
from hdbcli import dbapi

# HANA connection details from environment
HANA_HOST = os.getenv('HANA_HOST', 'e7decab9-3e98-41cf-bbf7-d0a8c13d7fb9.hana.prod-eu10.hanacloud.ondemand.com')
HANA_PORT = int(os.getenv('HANA_PORT', '443'))
HANA_USER = os.getenv('HANA_USER', 'DBADMIN')
HANA_PASSWORD = os.getenv('HANA_PASSWORD', '')

def create_p2p_user():
    """Create P2P_DP_USER with CSN access privileges"""
    
    if not HANA_PASSWORD:
        print("❌ ERROR: HANA_PASSWORD environment variable not set")
        print("Please set: export HANA_PASSWORD='your-password'")
        return False
    
    print(f"🔌 Connecting to HANA Cloud...")
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
        
        print("✅ Connected successfully!")
        
        cursor = conn.cursor()
        
        # Read SQL script
        print("\n📄 Reading SQL script...")
        with open('create_p2p_data_product_user_with_csn.sql', 'r', encoding='utf-8') as f:
            sql_script = f.read()
        
        # Split by SQL statements and clean
        statements = sql_script.split(';')
        
        sql_statements = []
        for stmt in statements:
            # Remove SQL comments but preserve the statement
            lines = []
            for line in stmt.split('\n'):
                stripped = line.strip()
                # Skip comment-only lines and empty lines
                if not stripped.startswith('--') and stripped:
                    lines.append(line)
            
            clean_stmt = '\n'.join(lines).strip()
            
            # Only skip SELECT statements (verification queries)
            if clean_stmt and not clean_stmt.upper().startswith('SELECT'):
                sql_statements.append(clean_stmt)
        
        print(f"📝 Found {len(sql_statements)} SQL statements to execute\n")
        
        # Execute each statement
        success_count = 0
        error_count = 0
        
        for i, stmt in enumerate(sql_statements, 1):
            # Show preview of statement
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
                
                # Some errors are OK (user already exists, etc.)
                if 'user already exists' in error_msg.lower() or error_code == 362:
                    print(f"    ⚠️  User already exists (skipping)")
                    success_count += 1
                elif 'already granted' in error_msg.lower():
                    print(f"    ⚠️  Privilege already granted (skipping)")
                    success_count += 1
                else:
                    print(f"    ❌ Error: {error_msg}")
                    error_count += 1
        
        print(f"\n{'='*60}")
        print(f"📊 Results:")
        print(f"   ✅ Successful: {success_count}")
        print(f"   ❌ Errors: {error_count}")
        print(f"{'='*60}\n")
        
        # Run verification queries
        print("🔍 Running verification queries...\n")
        
        # Query 1: Verify user created
        print("[1] Checking if user exists...")
        cursor.execute("SELECT USER_NAME, USER_DEACTIVATED FROM SYS.USERS WHERE USER_NAME = 'P2P_DP_USER'")
        user_row = cursor.fetchone()
        if user_row:
            print(f"    ✅ User 'P2P_DP_USER' exists (deactivated: {user_row[1]})")
        else:
            print(f"    ❌ User 'P2P_DP_USER' not found!")
        
        # Query 2: Count privileges
        print("\n[2] Checking privileges...")
        cursor.execute("SELECT COUNT(*) FROM SYS.GRANTED_PRIVILEGES WHERE GRANTEE = 'P2P_DP_USER'")
        priv_count = cursor.fetchone()[0]
        print(f"    ✅ {priv_count} privileges granted")
        
        # Query 3: Test CSN table access ⭐
        print("\n[3] Testing CSN table access...")
        try:
            cursor.execute('''
                SELECT REMOTE_SOURCE_NAME, LEFT(CSN_JSON, 100) as CSN_PREVIEW
                FROM "_SAP_DB_ACCESS_DATA_PRODUCT_GATEWAY"."_SAP_DATAPRODUCT_DELTA_CSN"
            ''')
            csn_rows = cursor.fetchall()
            print(f"    ✅ SUCCESS! Can access CSN table")
            print(f"    ✅ Found {len(csn_rows)} CSN records")
            for row in csn_rows:
                print(f"       - {row[0]}")
        except dbapi.Error as e:
            error_code = getattr(e, 'errorcode', 'UNKNOWN')
            if error_code == 258:
                print(f"    ❌ Error 258: Insufficient privilege")
                print(f"    ⚠️  Need to grant SELECT on CSN table!")
            else:
                print(f"    ❌ Error: {str(e)}")
        
        cursor.close()
        conn.close()
        
        print(f"\n{'='*60}")
        print(f"🎉 P2P_DP_USER setup complete!")
        print(f"{'='*60}\n")
        print(f"📝 Next steps:")
        print(f"   1. Verify CSN access works (see above)")
        print(f"   2. Update backend/.env to use P2P_DP_USER")
        print(f"   3. Implement CSN viewer endpoint")
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
    print("P2P_DP_USER Creation Script")
    print("="*60)
    print()
    
    success = create_p2p_user()
    sys.exit(0 if success else 1)