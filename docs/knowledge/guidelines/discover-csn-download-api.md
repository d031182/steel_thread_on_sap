# How to Discover CSN Download API from HANA Central

**Created**: 2026-01-31  
**Purpose**: Guide to find the actual API endpoint used by HANA Central's "Download CSN File" button

---

## Background

The HANA Central UI has a "Download CSN File" button that works, but the API endpoint it uses is not documented publicly. We can discover it using browser developer tools.

## Investigation Results

### ❌ What Doesn't Work (Tested)

**SQL Access**:
- `_SAP_DB_ACCESS_DATA_PRODUCT_GATEWAY._SAP_DATAPRODUCT_DELTA_CSN` table exists
- Both HANA_DP_USER and DBADMIN: Error 258 (insufficient privilege)
- CSN gateway requires special system-level privileges

**HTTP REST APIs**:
- `https://{instance}.hana.prod-eu10.hanacloud.ondemand.com/...` - Connection failed
- `https://hanacloud.ondemand.com/api/v1/instances/{guid}/...` - Connection failed
- `https://api.cf.eu10.hana.ondemand.com/v1/dataproducts/...` - 404 Not Found

**Conclusion**: HANA Central UI uses OAuth2 authentication via SAP BTP, not basic auth.

---

## ✅ How to Find the Real API Endpoint

### Step-by-Step Guide

**1. Open HANA Central in Browser**
- URL: https://hanacloud.ondemand.com
- Login with your SAP credentials
- Navigate to your HANA instance

**2. Open Browser Developer Tools**
- Press `F12` (Windows/Linux) or `Cmd+Option+I` (Mac)
- Go to **Network** tab
- Enable "Preserve log" checkbox (important!)
- Clear existing logs (trash icon)

**3. Trigger CSN Download**
- Navigate to **Data Products** tab
- Select a data product (e.g., Purchase Order)
- Click **Actions menu** (three dots)
- Click **"Download CSN File"**

**4. Capture the API Call**
In the Network tab, you should see a new request. Look for:
- Request URL (e.g., `https://...`)
- Request Method (likely `GET` or `POST`)
- Request Headers:
  - `Authorization: Bearer ...` (OAuth2 token)
  - `X-CSRF-Token: ...` (if POST)
- Response: Should be JSON CSN file

**5. Document the Findings**
Record these details:
```
URL: https://[discovered-endpoint]
Method: GET/POST
Headers:
  - Authorization: Bearer [token]
  - Accept: application/json
  - [Other headers...]
Query Parameters:
  - productId: ...
  - schemaName: ...
  - [Other params...]
```

---

## Expected API Pattern (Educated Guess)

Based on SAP BTP patterns, the API likely follows this structure:

```
Base URL: https://api.cf.eu10.hana.ondemand.com/dataproduct/v1
Endpoint: /instances/{instance-guid}/dataproducts/{product-id}/csn

Example:
GET https://api.cf.eu10.hana.ondemand.com/dataproduct/v1/instances/20bb37c7-0dd0-4369-82bf-5366b234c948/dataproducts/3b5b49db-c1fe-4a16-8188-cb84544f5dbb/csn

Headers:
Authorization: Bearer {oauth2_token}
Accept: application/json
```

---

## How to Get OAuth2 Token

The HANA Central UI gets its token from SAP BTP. To replicate:

### Option 1: Extract from Browser
1. Open dev tools while logged into HANA Central
2. Go to **Application** tab → **Storage** → **Local Storage**
3. Look for keys like:
   - `access_token`
   - `id_token`
   - `cf_token`
4. Copy the token value

### Option 2: Use SAP BTP CLI
```bash
# Install CF CLI
# https://docs.cloudfoundry.org/cf-cli/install-go-cli.html

# Login to BTP
cf login -a https://api.cf.eu10.hana.ondemand.com

# Get OAuth token
cf oauth-token

# Token will be in format: "bearer {token}"
# Use this token in Authorization header
```

### Option 3: Use BTP API
```bash
# Get token via SAP Cloud Platform API
curl -X POST 'https://[your-subdomain].authentication.eu10.hana.ondemand.com/oauth/token' \
  -H 'Content-Type: application/x-www-form-urlencoded' \
  -d 'grant_type=password' \
  -d 'username=your-email@sap.com' \
  -d 'password=your-password' \
  -d 'client_id=[client-id]' \
  -d 'client_secret=[client-secret]'
```

---

## Once You Have the API

### Create Python Script to Download CSN

```python
import requests
import json

def download_csn(instance_guid, product_id, oauth_token):
    """Download CSN file from HANA Cloud API"""
    
    url = f"https://api.cf.eu10.hana.ondemand.com/dataproduct/v1/instances/{instance_guid}/dataproducts/{product_id}/csn"
    
    headers = {
        'Authorization': f'Bearer {oauth_token}',
        'Accept': 'application/json'
    }
    
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        csn_data = response.json()
        
        # Save to file
        filename = f"data-products/{product_id}.csn.json"
        with open(filename, 'w') as f:
            json.dump(csn_data, f, indent=2)
        
        print(f"✅ Downloaded CSN to {filename}")
        return csn_data
    else:
        print(f"❌ Failed: HTTP {response.status_code}")
        print(response.text)
        return None

# Usage
oauth_token = "your-token-here"
instance_guid = "20bb37c7-0dd0-4369-82bf-5366b234c948"
product_id = "3b5b49db-c1fe-4a16-8188-cb84544f5dbb"  # Purchase Order

csn = download_csn(instance_guid, product_id, oauth_token)
```

---

## Why This Is Complex

**HANA Central UI Authentication Flow**:
1. User logs into SAP BTP Cockpit (OAuth2/SAML)
2. Gets BTP session token
3. BTP token used to call HANA Cloud APIs
4. HANA Cloud APIs have elevated privileges
5. Download CSN file via API

**Your Current Setup**:
- ✅ Direct HANA database connection (username/password)
- ❌ No BTP OAuth2 token
- ❌ No Cloud Foundry CLI session
- ❌ No BTP API access configured

**Gap**: You have database-level access, but not cloud management API access.

---

## Practical Solutions

### Solution 1: Manual Download (Easiest) ⭐

**When**: Occasionally need CSN for reference

**Steps**:
1. Open HANA Central UI
2. Download CSN file manually
3. Save to `data-products/` directory
4. Use in scripts as needed

**Time**: 30 seconds per data product

---

### Solution 2: Browser Dev Tools Discovery (One-time setup)

**When**: Want to automate CSN downloads

**Steps**:
1. Follow "How to Find the Real API Endpoint" section above
2. Copy actual API URL and headers from Network tab
3. Extract OAuth2 token from browser storage
4. Create Python script using discovered endpoint
5. Refresh token periodically (OAuth tokens expire)

**Time**: 30 minutes setup, then automated

---

### Solution 3: Use Current Solution (Recommended) ⭐⭐

**When**: Just need schema information for SQLite rebuild

**Why**: You already have everything via SYS tables:
- ✅ Primary keys via `SYS.INDEX_COLUMNS`
- ✅ Foreign keys via `SYS.REFERENTIAL_CONSTRAINTS`  
- ✅ Column types via `SYS.TABLE_COLUMNS`
- ✅ Complete schema metadata

**No CSN needed** for:
- SQLite schema creation
- Primary key constraints
- Foreign key relationships
- UI display (keys, FKs already shown)

---

## Next Steps

### Option A: Discover Real API (For Learning)
1. Follow browser dev tools guide above
2. Document actual endpoint in this file
3. Create automated download script

### Option B: Use Manual Download (Pragmatic)
1. Download CSN files as needed via UI
2. Store in `data-products/` directory
3. Reference when needed

### Option C: Continue with Current Solution (Recommended)
1. Use existing HANA INDEX/CONSTRAINTS queries
2. Run `rebuild_sqlite_with_pk.py` to sync schemas
3. CSN files are optional documentation only

---

## Summary

**The Reality**:
- HANA Central UI uses BTP OAuth2 APIs (not database authentication)
- Your DBADMIN user has database privileges, not cloud API privileges
- Direct SQL access to CSN tables is blocked (Error 258)

**The Workaround**:
- Manual download via UI (simple, works now)
- Or discover actual API via browser dev tools (one-time effort)

**The Good News**:
- You don't actually need CSN files!
- Everything you need is accessible via SYS tables
- Primary keys, foreign keys, and schemas all working

---

**Last Updated**: 2026-01-31  
**Status**: CSN not programmatically accessible with current credentials