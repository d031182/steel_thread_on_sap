#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test CSN (Core Schema Notation) Access from HANA

Tests if we can retrieve CSN definitions from HANA Cloud,
which contain complete data product schemas including primary keys.

Usage: python test_csn_access.py
"""
import os
import sys
import json
from dotenv import load_dotenv

# Fix Windows encoding
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

# Load environment from app/.env
load_dotenv('app/.env')

def test_csn_access():
    """Test different methods to access CSN from HANA"""
    
    # Connection details from environment
    host = os.getenv('HANA_HOST')
    port = int(os.getenv('HANA_PORT', 443))
    user = os.getenv('HANA_USER')
    password = os.getenv('HANA_PASSWORD')
    
    print(f"Testing CSN access on {host}")
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
        
        # Method 1: Try _SAP_DB_ACCESS_DATA_PRODUCT_GATEWAY._SAP_DATAPRODUCT_DELTA_CSN
        print("\n2. Method 1: Query _SAP_DATAPRODUCT_DELTA_CSN...")
        csn_sql_1 = """
        SELECT CSN_JSON, REMOTE_SOURCE_NAME
        FROM _SAP_DB_ACCESS_DATA_PRODUCT_GATEWAY._SAP_DATAPRODUCT_DELTA_CSN
        WHERE REMOTE_SOURCE_NAME LIKE '%PurchaseOrder%'
        """
        
        try:
            result = conn.execute_query(csn_sql_1)
            if result['success'] and result['rows']:
                print(f"   ✅ Found {len(result['rows'])} CSN entries")
                for row in result['rows']:
                    source_name = row['REMOTE_SOURCE_NAME']
                    csn_json = row.get('CSN_JSON')
                    if csn_json:
                        csn_data = json.loads(csn_json)
                        print(f"      - {source_name}")
                        print(f"        CSN version: {csn_data.get('$version', 'unknown')}")
                        entities = csn_data.get('definitions', {})
                        print(f"        Entities: {len(entities)}")
            else:
                print(f"   ❌ No CSN found: {result.get('error', 'No results')}")
        except Exception as e:
            print(f"   ❌ Error: {e}")
        
        # Method 2: Try listing all available CSN entries
        print("\n3. Method 2: List ALL CSN entries available...")
        list_csn_sql = """
        SELECT REMOTE_SOURCE_NAME, COUNT(*) as COUNT
        FROM _SAP_DB_ACCESS_DATA_PRODUCT_GATEWAY._SAP_DATAPRODUCT_DELTA_CSN
        GROUP BY REMOTE_SOURCE_NAME
        ORDER BY REMOTE_SOURCE_NAME
        """
        
        try:
            result = conn.execute_query(list_csn_sql)
            if result['success'] and result['rows']:
                print(f"   ✅ Found {len(result['rows'])} data products with CSN")
                for row in result['rows'][:5]:  # Show first 5
                    print(f"      - {row['REMOTE_SOURCE_NAME']} ({row['COUNT']} entries)")
                if len(result['rows']) > 5:
                    print(f"      ... and {len(result['rows']) - 5} more")
            else:
                print(f"   ❌ Cannot list CSN: {result.get('error')}")
        except Exception as e:
            print(f"   ❌ Error: {e}")
        
        # Method 3: Check if CSN gateway schema exists
        print("\n4. Method 3: Check CSN gateway schema existence...")
        gateway_sql = """
        SELECT SCHEMA_NAME
        FROM SYS.SCHEMAS
        WHERE SCHEMA_NAME LIKE '%GATEWAY%'
           OR SCHEMA_NAME LIKE '%CSN%'
           OR SCHEMA_NAME LIKE '%DATAPRODUCT%'
        """
        
        result = conn.execute_query(gateway_sql)
        if result['success'] and result['rows']:
            print(f"   ✅ Found {len(result['rows'])} related schemas:")
            for row in result['rows']:
                print(f"      - {row['SCHEMA_NAME']}")
        
        # Method 4: Check what tables exist in gateway schema
        print("\n5. Method 4: List tables in gateway schema...")
        tables_sql = """
        SELECT TABLE_NAME
        FROM SYS.TABLES
        WHERE SCHEMA_NAME = '_SAP_DB_ACCESS_DATA_PRODUCT_GATEWAY'
        ORDER BY TABLE_NAME
        """
        
        try:
            result = conn.execute_query(tables_sql)
            if result['success'] and result['rows']:
                print(f"   ✅ Found {len(result['rows'])} tables in gateway:")
                for row in result['rows']:
                    print(f"      - {row['TABLE_NAME']}")
            else:
                print(f"   ❌ Cannot access gateway schema: {result.get('error')}")
        except Exception as e:
            print(f"   ❌ Error: {e}")
        
        conn.close()
        
        print("\n" + "=" * 80)
        print("CSN Access Test Complete!")
        print("\nConclusions:")
        print("- If CSN found: Can use it to get complete schema definitions")
        print("- If CSN not found: May need different approach or privileges")
        print("- CSN contains: entities, keys, associations, annotations")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    test_csn_access()