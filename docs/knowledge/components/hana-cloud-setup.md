# HANA Cloud Setup Guide

**Type**: Component  
**Category**: Infrastructure Setup  
**Created**: 2026-01-25  
**Status**: Active  

## Overview

Comprehensive guide for setting up and configuring SAP HANA Cloud for the P2P Data Products project. Covers initial setup, user creation, privilege grants, and BDC integration.

## Related Documentation

- [[HANA Connection Module]] - Backend service for HANA connectivity
- [[Data Products in HANA Cloud]] - Consuming data products
- [[CSN HANA Cloud Solution]] - CSN data access approach

## Prerequisites

### Required Components
- SAP Business Technology Platform (BTP) account
- SAP HANA Cloud instance provisioned
- SAP Business Data Cloud (BDC) tenant (optional)
- HANA client tools installed

### Required Tools
- **hana-cli**: Command-line tool for HANA operations
- **Database Explorer**: Web-based SQL tool
- **BTP CLI**: Cloud Foundry command-line interface

## Phase 1: Initial Setup

### 1.1 Access HANA Cloud Central

**URL**: https://hana-cockpit.cfapps.{region}.hana.ondemand.com

**Steps**:
1. Log in with SAP BTP credentials
2. Navigate to your HANA Cloud instance
3. Note instance details:
   - Host: `{instance-id}.hana.{region}.hanacloud.ondemand.com`
   - Port: `443` (default)
   - Admin user: `DBADMIN`

### 1.2 Reset DBADMIN Password (If Needed)

**When**: First-time setup or password forgotten

**Steps**:
1. SAP HANA Cloud Central → Actions → Reset DBADMIN Password
2. Enter new password (min 8 chars, uppercase, lowercase, number, special)
3. Confirm and save
4. **Important**: No forced password change on first login

**Password Requirements**:
- Minimum 8 characters
- At least one uppercase letter
- At least one lowercase letter
- At least one number
- At least one special character

### 1.3 Add IP to Allowlist

**Problem**: Connection refused from local machine

**Solution**: Add your IP address to HANA Cloud allowlist

**Steps**:
1. SAP HANA Cloud Central → Security → IP Allowlist
2. Click "Add IP Address"
3. Get your current IP:
   ```powershell
   (Invoke-WebRequest -Uri "https://api.ipify.org").Content
   ```
4. Add IP with description (e.g., "Home Office")
5. Save changes
6. **Note**: IP changes require re-adding

**Alternative**: Enable "Allow all IP addresses" (development only)

## Phase 2: User Creation

### 2.1 Create P2P Data Product User

**Purpose**: Dedicated user for P2P application with minimal privileges

**User Details**:
```
Username: P2P_DP_USER
Password: P2P_DataProd123!  (changeable)
Schema: P2P_DATA_PRODUCTS
```

**SQL Script**:
```sql
-- Create user (as DBADMIN)
CREATE USER P2P_DP_USER PASSWORD "P2P_DataProd123!" NO FORCE_FIRST_PASSWORD_CHANGE;

-- Create schema
CREATE SCHEMA P2P_DATA_PRODUCTS OWNED BY P2P_DP_USER;

-- Grant basic privileges
GRANT SELECT ON SCHEMA P2P_DATA_PRODUCTS TO P2P_DP_USER;
GRANT INSERT ON SCHEMA P2P_DATA_PRODUCTS TO P2P_DP_USER;
GRANT UPDATE ON SCHEMA P2P_DATA_PRODUCTS TO P2P_DP_USER;
GRANT DELETE ON SCHEMA P2P_DATA_PRODUCTS TO P2P_DP_USER;

-- Grant catalog read (for metadata)
GRANT CATALOG READ TO P2P_DP_USER;

-- Verification
SELECT USER_NAME, SCHEMA_NAME, IS_VALID 
FROM SYS.USERS 
WHERE USER_NAME = 'P2P_DP_USER';
```

**Execution Options**:

**Option 1: Database Explorer**
```bash
# Open Database Explorer
hana-cli opendbx

# Paste SQL script
# Execute (F8)
```

**Option 2: hana-cli**
```bash
hana-cli sql -u DBADMIN -p "your-password" \
  -f sql/hana/users/create_p2p_data_product_user.sql
```

### 2.2 Grant Data Product Access

**Purpose**: Allow P2P_DP_USER to access SAP BDC data products

**Prerequisites**:
- Formation created (SAP for Me)
- Data products shared to HANA Cloud
- Data products installed

**Grant Privileges**:
```sql
-- Grant access to data product schema
GRANT SELECT ON SCHEMA "_SAP_DB_ACCESS_DATA_PRODUCT_GATEWAY" TO P2P_DP_USER;

-- Grant access to specific data products (example)
GRANT SELECT ON "_SAP_DB_ACCESS_DATA_PRODUCT_GATEWAY"."SUPPLIER" TO P2P_DP_USER;
GRANT SELECT ON "_SAP_DB_ACCESS_DATA_PRODUCT_GATEWAY"."PURCHASE_ORDER" TO P2P_DP_USER;
GRANT SELECT ON "_SAP_DB_ACCESS_DATA_PRODUCT_GATEWAY"."SUPPLIER_INVOICE" TO P2P_DP_USER;

-- Grant CSN access
GRANT SELECT ON "_SAP_DB_ACCESS_DATA_PRODUCT_GATEWAY"."_SAP_DATAPRODUCT_DELTA_CSN" TO P2P_DP_USER;
```

**Verification**:
```sql
-- Verify user can access data products
SELECT * FROM "_SAP_DB_ACCESS_DATA_PRODUCT_GATEWAY"."SUPPLIER" LIMIT 10;

-- Verify CSN access
SELECT REMOTE_SOURCE_NAME 
FROM "_SAP_DB_ACCESS_DATA_PRODUCT_GATEWAY"."_SAP_DATAPRODUCT_DELTA_CSN"
WHERE REMOTE_SOURCE_NAME LIKE '%Supplier%';
```

## Phase 3: HANA Client Setup

### 3.1 Install HANA Client

**Windows**:
```powershell
# Download from SAP Software Center or SAP Support Portal
# Run installer: HANA_CLIENT_WINDOWS_X86_64.EXE
# Follow installation wizard
```

**Verify Installation**:
```powershell
hdbsql -v
# Should show version info
```

### 3.2 Install hana-cli

**Prerequisites**: Node.js installed

```bash
npm install -g hana-cli
```

**Verify**:
```bash
hana-cli --version
```

**Initial Configuration**:
```bash
# Add connection
hana-cli addConnection \
  -n "BDC Production" \
  -h "e7decab9-3e98-41cf-bbf7-d0a8c13d7fb9.hana.prod-eu10.hanacloud.ondemand.com" \
  -p 443 \
  -u P2P_DP_USER \
  -s \
  -encrypt

# Test connection
hana-cli status
```

### 3.3 Configure Database Explorer

**Access**:
```bash
hana-cli opendbx
```

**Or via URL**:
```
https://hana-cockpit.cfapps.{region}.hana.ondemand.com/
```

**Features**:
- SQL Console
- Schema browser
- Table viewer
- Query history
- Performance monitoring

## Phase 4: BDC Integration

### 4.1 Create Formation

**Location**: SAP for Me (https://me.sap.com)

**Steps**:
1. Navigate to Formations section
2. Click "Create Formation"
3. Add components:
   - SAP Business Data Cloud tenant
   - SAP HANA Cloud instance
   - (Optional) SAP Datasphere, Databricks
4. Assign users with appropriate roles
5. Save formation

**Formation Benefits**:
- Establishes trust between systems
- Enables data product sharing
- Provides SSO across components
- Simplifies connectivity

### 4.2 Share Data Products

**In SAP BDC**:
1. Navigate to Catalog & Marketplace
2. Browse P2P data products:
   - Supplier
   - Purchase Order
   - Service Entry Sheet
   - Supplier Invoice
   - Payment Terms
   - Journal Entry Header
3. For each product:
   - Click "Share" or "Add Target"
   - Select HANA Cloud instance
   - Confirm sharing

### 4.3 Install Data Products

**In HANA Cloud Central**:
1. Navigate to Data Products tab
2. View shared products from BDC
3. Select product to install
4. Click "Install"
5. Installation automatically creates:
   - Remote source (connection to BDC)
   - Virtual tables (one per business object)
   - Metadata mappings

**Verify Installation**:
```sql
-- Check remote sources
SELECT * FROM SYS.REMOTE_SOURCES;

-- Check virtual tables
SELECT * FROM SYS.VIRTUAL_TABLES 
WHERE SCHEMA_NAME = '_SAP_DB_ACCESS_DATA_PRODUCT_GATEWAY';

-- Query data product
SELECT * FROM "_SAP_DB_ACCESS_DATA_PRODUCT_GATEWAY"."SUPPLIER" LIMIT 10;
```

## Phase 5: Application Configuration

### 5.1 Update Application Config

**File**: `default-env.json` or environment variables

```json
{
  "HANA_HOST": "e7decab9-3e98-41cf-bbf7-d0a8c13d7fb9.hana.prod-eu10.hanacloud.ondemand.com",
  "HANA_PORT": "443",
  "HANA_USER": "P2P_DP_USER",
  "HANA_PASSWORD": "P2P_DataProd123!",
  "HANA_SCHEMA": "P2P_DATA_PRODUCTS",
  "HANA_ENCRYPT": "true"
}
```

**Security Note**: Never commit credentials to Git!

### 5.2 Test Connection

**Python (via HANA Connection Module)**:
```python
from modules.hana_connection.backend import HanaConnectionService

# Initialize connection
conn = HanaConnectionService()

# Test query
result = conn.execute_query("SELECT CURRENT_USER FROM DUMMY")
print(f"Connected as: {result[0]['CURRENT_USER']}")

# Query data product
result = conn.execute_query("""
    SELECT * FROM "_SAP_DB_ACCESS_DATA_PRODUCT_GATEWAY"."SUPPLIER"
    LIMIT 5
""")
print(f"Retrieved {len(result)} suppliers")
```

**JavaScript**:
```javascript
const hana = require('@sap/hana-client');

const conn = hana.createConnection();
conn.connect({
    host: process.env.HANA_HOST,
    port: process.env.HANA_PORT,
    user: process.env.HANA_USER,
    password: process.env.HANA_PASSWORD,
    encrypt: true
});

conn.exec('SELECT CURRENT_USER FROM DUMMY', (err, result) => {
    console.log('Connected as:', result[0].CURRENT_USER);
    conn.disconnect();
});
```

## Common Issues & Solutions

### Issue 1: Connection Refused

**Error**: `Connection failed: [10709] Connection refused`

**Causes**:
- IP not in allowlist
- Wrong host/port
- Firewall blocking

**Solutions**:
1. Add IP to allowlist (see Phase 1.3)
2. Verify host and port
3. Check firewall settings
4. Test with `ping {host}`

### Issue 2: Authentication Failed

**Error**: `Authentication failed` or Error code 258

**Causes**:
- Wrong username/password
- User locked/expired
- Insufficient privileges

**Solutions**:
1. Reset password via HANA Cloud Central
2. Verify username (case-sensitive)
3. Check user status: `SELECT * FROM SYS.USERS WHERE USER_NAME = 'P2P_DP_USER'`
4. Grant required privileges

### Issue 3: Table Not Found

**Error**: `invalid table name` or Error code 259

**Causes**:
- Data product not installed
- Wrong schema name
- Missing privileges

**Solutions**:
1. Verify data product installed
2. Check schema: `SELECT * FROM SYS.SCHEMAS`
3. Grant SELECT privilege on schema
4. Use fully qualified names: `"SCHEMA"."TABLE"`

### Issue 4: Slow Query Performance

**Symptoms**: Queries taking >30 seconds

**Causes**:
- Virtual table (network latency)
- No WHERE clause (fetching all data)
- Large result set

**Solutions**:
1. Add WHERE clauses to filter at source
2. Select only needed columns
3. Consider creating local replica for frequently accessed data
4. Use LIMIT for testing

## Best Practices

### Security
- ✅ Use dedicated application users (not DBADMIN)
- ✅ Grant minimal required privileges
- ✅ Rotate passwords regularly
- ✅ Use encrypted connections (port 443)
- ✅ Never commit credentials to Git
- ✅ Use environment variables or secure vaults

### Performance
- ✅ Add IP allowlist entries for all developers
- ✅ Use connection pooling in applications
- ✅ Filter data at source (WHERE clauses)
- ✅ Select only needed columns (avoid SELECT *)
- ✅ Monitor query execution times

### Maintenance
- ✅ Update data products regularly
- ✅ Monitor disk space usage
- ✅ Review and clean up unused objects
- ✅ Document all schema changes
- ✅ Keep formation membership up-to-date

## Quick Reference

### Connection Details
```
Host: e7decab9-3e98-41cf-bbf7-d0a8c13d7fb9.hana.prod-eu10.hanacloud.ondemand.com
Port: 443
User: P2P_DP_USER
Schema: P2P_DATA_PRODUCTS
Encryption: Required (TLS)
```

### Common Commands
```bash
# Open Database Explorer
hana-cli opendbx

# Check connection status
hana-cli status

# Execute SQL file
hana-cli sql -f script.sql

# Query simple
hana-cli querySimple -q "SELECT * FROM DUMMY"
```

### Essential SQL
```sql
-- Check current user
SELECT CURRENT_USER FROM DUMMY;

-- List schemas
SELECT SCHEMA_NAME FROM SYS.SCHEMAS ORDER BY SCHEMA_NAME;

-- List tables in schema
SELECT TABLE_NAME FROM SYS.TABLES 
WHERE SCHEMA_NAME = 'P2P_DATA_PRODUCTS';

-- Check privileges
SELECT * FROM SYS.GRANTED_PRIVILEGES 
WHERE GRANTEE = 'P2P_DP_USER';
```

## Additional Resources

### Official Documentation
- HANA Cloud Admin Guide: `docs/hana-cloud/HANA_CLOUD_ADMINISTRATION_GUIDE_SUMMARY.md`
- Getting Started: `docs/hana-cloud/HANA_CLOUD_GETTING_STARTED_SUMMARY.md`
- BDC Context: `docs/hana-cloud/HANA_CLOUD_IN_BDC_CONTEXT.md`
- Privileges Guide: `docs/hana-cloud/HANA_CLOUD_PRIVILEGES_GUIDE.md`

### Guides
- BTP CLI: `docs/hana-cloud/BTP_CLI_HANA_CLOUD_GUIDE.md`
- Execute SQL: `docs/hana-cloud/EXECUTE_SQL_SCRIPT_GUIDE.md`
- Data Product Authorization: `docs/hana-cloud/DATA_PRODUCT_AUTHORIZATION_GUIDE.md`

### Troubleshooting
- Setup Issues: `docs/hana-cloud/HANA_CLOUD_SETUP_ISSUE_RESOLVED.md`
- BDC Research: `docs/hana-cloud/HANA_CLOUD_BDC_RESEARCH_FINDINGS.md`

## Status

✅ **ACTIVE GUIDE** - Primary setup reference

**Last Updated**: 2026-01-25  
**Tested With**: HANA Cloud 2024 Q4, BDC 2024  
**Maintenance**: Update when HANA Cloud versions change