#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test HANA Cloud Central API for CSN Download

HANA Central UI uses REST APIs to download CSN files.
This script investigates the API endpoints used by the UI.

Based on: HANA Cloud Central UI "Download CSN File" button
"""
import os
import sys
import json
import requests
from dotenv import load_dotenv

# Fix Windows encoding
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

# Load environment
load_dotenv('app/.env')

def test_hana_cloud_api():
    """Test HANA Cloud Central REST API for CSN download"""
    
    host = os.getenv('HANA_HOST')
    admin_user = os.getenv('HANA_ADMIN_USER')
    admin_password = os.getenv('HANA_ADMIN_PASSWORD')
    
    print("="*80)
    print("HANA Cloud Central API - CSN Download Investigation")
    print("="*80)
    print(f"\nTarget: {host}")
    print(f"User: {admin_user}")
    print()
    
    # Extract instance GUID from host
    # Format: {guid}.hana.prod-eu10.hanacloud.ondemand.com
    instance_guid = host.split('.')[0]
    print(f"Instance GUID: {instance_guid}")
    
    # HANA Cloud Central API endpoints (educated guesses based on SAP BTP patterns)
    api_bases = [
        f"https://{host}",  # Direct HANA instance
        f"https://hanacloud.ondemand.com/api/v1/instances/{instance_guid}",  # Cloud Central API
        f"https://api.cf.eu10.hana.ondemand.com/v1/dataproducts",  # Cloud Foundry API
    ]
    
    print("\nTesting potential API endpoints...")
    print("="*80)
    
    for i, base_url in enumerate(api_bases, 1):
        print(f"\n{i}. Testing: {base_url}")
        
        # Test endpoints that might provide CSN
        endpoints = [
            "/dataproducts",
            "/csn",
            "/schema",
            "/api/dataproducts",
            "/api/csn",
        ]
        
        for endpoint in endpoints:
            url = f"{base_url}{endpoint}"
            print(f"   Trying: {url}")
            
            try:
                # Try with basic auth
                response = requests.get(
                    url,
                    auth=(admin_user, admin_password),
                    timeout=5,
                    verify=True
                )
                
                if response.status_code == 200:
                    print(f"      ✅ SUCCESS! Status 200")
                    print(f"         Content-Type: {response.headers.get('Content-Type')}")
                    print(f"         Size: {len(response.content)} bytes")
                    
                    # Try to parse as JSON
                    try:
                        data = response.json()
                        print(f"         JSON keys: {list(data.keys())[:5]}")
                    except:
                        print(f"         Content preview: {response.text[:100]}...")
                        
                elif response.status_code == 401:
                    print(f"      ❌ 401 Unauthorized - auth method wrong")
                elif response.status_code == 403:
                    print(f"      ❌ 403 Forbidden - no access")
                elif response.status_code == 404:
                    print(f"      ❌ 404 Not Found")
                else:
                    print(f"      ❌ {response.status_code}")
                    
            except requests.exceptions.ConnectionError:
                print(f"      ❌ Connection failed")
            except requests.exceptions.Timeout:
                print(f"      ❌ Timeout")
            except Exception as e:
                print(f"      ❌ Error: {e}")
    
    print("\n" + "="*80)
    print("HANA Cloud API Documentation Pointers")
    print("="*80)
    print("""
The HANA Central UI "Download CSN File" button likely uses:

1. **BTP Cloud Foundry API**:
   - Authentication via OAuth2 token (not basic auth)
   - Endpoint: SAP BTP Cockpit API
   - Requires: CF CLI authentication

2. **HANA Cloud Management API**:
   - Part of SAP Cloud Platform
   - URL pattern: https://api.cf.{region}.hana.ondemand.com
   - Requires: OAuth2 token from BTP

3. **Possible Workaround**:
   - Use browser dev tools (F12) when clicking "Download CSN"
   - Inspect Network tab to see actual API call
   - Copy the API endpoint and auth headers
   - Reproduce in Python script

4. **Alternative: Direct File Access**:
   - CSN files might be stored in BTP storage
   - Accessible via Cloud Foundry CLI
   - Command: `cf download-dataproduct-csn [product-id]`

**Recommendation**:
Since programmatic access is complex, the simplest approach is:
1. Manual download via HANA Central UI (you already have access)
2. Store CSN files in data-products/ directory
3. Use existing CSN parsing logic (already implemented)
""")

if __name__ == '__main__':
    test_hana_cloud_api()