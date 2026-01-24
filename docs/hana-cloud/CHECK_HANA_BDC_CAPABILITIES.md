# How to Check if HANA Cloud Has BDC Service

**Purpose**: Verify if your HANA Cloud instance supports Business Data Cloud (BDC) features  
**Date**: 2026-01-23  
**Status**: Investigation Guide

---

## What is BDC in HANA Cloud?

**Business Data Cloud (BDC)** in HANA Cloud would provide:
- Native data product catalog
- CSN schema definitions
- Metadata management
- Data lineage tracking

**Note**: This is different from the local BDC MCP prototype tool!

---

## Method 1: Check for BDC Schemas (SQL)

### Step 1: Connect to HANA Cloud

Use any SQL client (DBeaver, SAP HANA Database Explorer, etc.) with your credentials:
- Host: `e7decab9-3e98-41cf-bbf7-d0a8c13d7fb9.hana.prod-eu10.hanacloud.ondemand.com`
- Port: `443`
- User: `DBADMIN`

### Step 2: Query for BDC-Related Schemas

```sql
-- Check for schemas with 'BDC' in name
SELECT SCHEMA_NAME, SCHEMA_OWNER, CREATE_TIME
FROM SYS.SCHEMAS
WHERE SCHEMA_NAME LIKE '%BDC%'
   OR SCHEMA_NAME LIKE '%BUSINESS%DATA%'
   OR SCHEMA_NAME LIKE '%DATA%CLOUD%'
ORDER BY SCHEMA_NAME;
```

**Expected Results**:
- ✅ **If BDC is available**: You'll see schemas like `BDC_METADATA`, `BDC_CATALOG`, etc.
- ❌ **If BDC not available**: Empty result set or only your application schemas

### Step 3: Check for Data Product Related Tables

```sql
-- Look for data product tables/views
SELECT TABLE_NAME, TABLE_TYPE, SCHEMA_NAME
FROM SYS.TABLES
WHERE TABLE_NAME LIKE '%DATA%PRODUCT%'
   OR TABLE_NAME LIKE '%BDC%'
   OR COMMENTS LIKE '%data product%'
ORDER BY SCHEMA_NAME, TABLE_NAME;
```

### Step 4: Check for CSN/Schema Tables

```sql
-- Look for CSN or schema definition tables
SELECT TABLE_NAME, TABLE_TYPE, SCHEMA_NAME
FROM SYS.TABLES
WHERE TABLE_NAME LIKE '%CSN%'
   OR TABLE_NAME LIKE '%SCHEMA%'
   OR COMMENTS LIKE '%core schema notation%'
ORDER BY SCHEMA_NAME, TABLE_NAME;
```

---

## Method 2: Check HANA Cloud Configuration (BTP Cockpit)

### Step 1: Access SAP BTP Cockpit

1. Go to: https://cockpit.eu10.hana.ondemand.com/
2. Navigate to your subaccount
3. Go to **SAP HANA Cloud** section

### Step 2: Check Instance Details

1. Find your HANA Cloud instance
2. Click on instance name
3. Look for **Enabled Services** or **Features**

**What to look for**:
- Data services enabled
- Business Data Cloud listed
- Data product support mentioned
- Advanced features section

### Step 3: Check Service Bindings

In your Cloud Foundry space:
```bash
cf services
```

Look for services related to:
- `business-data-cloud`
- `data-product`
- `bdc-api`

---

## Method 3: Check HANA System Views

### System Information Query

```sql
-- Check HANA version and features
SELECT * FROM SYS.M_FEATURES
WHERE FEATURE_NAME LIKE '%DATA%'
   OR FEATURE_NAME LIKE '%BDC%'
   OR FEATURE_NAME LIKE '%PRODUCT%';
```

### Check Available System Views

```sql
-- List all system views (might show BDC-related views)
SELECT VIEW_NAME, SCHEMA_NAME, COMMENTS
FROM SYS.VIEWS
WHERE SCHEMA_NAME = 'SYS'
  AND (VIEW_NAME LIKE '%BDC%'
    OR VIEW_NAME LIKE '%DATA_PRODUCT%'
    OR COMMENTS LIKE '%data product%')
ORDER BY VIEW_NAME;
```

---

## Method 4: Check Documentation Access

### SAP HANA Cloud Documentation

1. Go to: https://help.sap.com/docs/hana-cloud
2. Search for: "Business Data Cloud" or "Data Products"
3. Check if your HANA Cloud version supports these features

### Check Your HANA Version

```sql
-- Get HANA version
SELECT * FROM SYS.M_DATABASE;
```

Then check if BDC is available in your version:
- HANA Cloud 2023+ typically has data product features
- Earlier versions may not have BDC

---

## Method 5: Try Sample Data Product Query

### Attempt to Query Data Products

```sql
-- Try common data product view names
-- (These are hypothetical - actual names may differ)

-- Option 1: BDC Catalog
SELECT * FROM BDC_CATALOG.DATA_PRODUCTS;

-- Option 2: Data Product Metadata
SELECT * FROM SYS.DATA_PRODUCTS;

-- Option 3: Schema definitions
SELECT * FROM SYS.SCHEMA_DEFINITIONS;
```

**Expected Outcomes**:
- ✅ **Success**: View exists and returns data → BDC available!
- ❌ **Error "table not found"**: BDC not available or different names
- ❌ **Error "insufficient privileges"**: BDC exists but access denied

---

## Interpreting Results

### Scenario A: BDC Service Found ✅

**What you'll see**:
- BDC-related schemas exist
- Data product tables/views present
- CSN definition tables available

**Next Steps**:
1. Document exact schema and table names
2. Test querying for Supplier data product
3. Retrieve CSN definition
4. Update backend to use HANA SQL queries

### Scenario B: No BDC Service ❌

**What you'll see**:
- No BDC schemas
- No data product tables
- Empty results from all queries

**Next Steps**:
1. **Contact SAP Support**: Ask if BDC can be enabled
2. **Check Alternative Options**: 
   - SAP API Business Hub
   - Discovery API from BTP
   - External link approach
3. **Review HANA License**: BDC might require specific license

### Scenario C: Access Denied ⚠️

**What you'll see**:
- Tables exist but insufficient privileges error

**Next Steps**:
1. Request access from HANA administrator
2. Grant necessary privileges to DBADMIN user
3. Retry queries

---

## Quick Test Script

Run this complete test in one go:

```sql
-- === HANA BDC Capability Check ===

-- 1. Check BDC Schemas
SELECT 'BDC_SCHEMAS' as CHECK_TYPE, COUNT(*) as COUNT
FROM SYS.SCHEMAS
WHERE SCHEMA_NAME LIKE '%BDC%';

-- 2. Check Data Product Tables
SELECT 'DATA_PRODUCT_TABLES' as CHECK_TYPE, COUNT(*) as COUNT
FROM SYS.TABLES
WHERE TABLE_NAME LIKE '%DATA%PRODUCT%';

-- 3. Check CSN Tables
SELECT 'CSN_TABLES' as CHECK_TYPE, COUNT(*) as COUNT
FROM SYS.TABLES
WHERE TABLE_NAME LIKE '%CSN%';

-- 4. Check System Features
SELECT 'BDC_FEATURES' as CHECK_TYPE, COUNT(*) as COUNT
FROM SYS.M_FEATURES
WHERE FEATURE_NAME LIKE '%BDC%';

-- Summary: If all counts are 0, BDC is likely not available
```

**Interpretation**:
- All counts = 0 → ❌ BDC not available
- Any count > 0 → ✅ Investigate further (BDC might be available)

---

## Expected Timeline

- **Method 1 (SQL)**: 5-10 minutes
- **Method 2 (BTP Cockpit)**: 10-15 minutes
- **Method 3 (System Views)**: 5 minutes
- **Method 4 (Documentation)**: 15-30 minutes
- **Method 5 (Sample Queries)**: 5 minutes

**Total**: ~30-60 minutes for thorough investigation

---

## What to Do With Results

### If BDC is Available:
1. Document exact schema names and table structures
2. Create SQL queries to fetch CSN
3. Update `backend/app.py` to use HANA queries instead of HTTP
4. Test with Supplier data product
5. Implement frontend to display results

### If BDC is NOT Available:
1. Explore Option 2: SAP API Business Hub
2. Or Option 3: Test Discovery API from BTP deployment
3. Or Option 4: Provide external links to users
4. Document findings and decision

---

## Questions to Answer

After running these checks, you should know:

1. ✅/❌ Does my HANA Cloud instance have BDC?
2. If yes, what are the exact schema/table names?
3. If no, is it possible to enable it?
4. What alternative options should I pursue?

---

**Next Step**: Run the Quick Test Script above in your HANA Cloud SQL client and share the results!