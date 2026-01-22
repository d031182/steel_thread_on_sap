# Data Product Authorization Guide for SAP HANA Cloud

**Complete Guide to User Privileges for Data Product Installation and Consumption**

**Date**: January 22, 2026, 12:10 AM  
**Environment**: SAP HANA Cloud in BDC Formation  
**Purpose**: Enable users to install and consume SAP Business Data Cloud data products

---

## Overview

This guide explains the **complete authorization model** for installing and consuming data products from SAP Business Data Cloud in SAP HANA Cloud, including required privileges, user setup, and step-by-step procedures.

---

## Authorization Levels

### Level 1: BDC Administration (Platform Level)

**Location**: SAP Datasphere / SAP Business Data Cloud

**Required Role**: Administrator with **Data Warehouse General** privilege

**Privileges**:
- Data Warehouse General (-R------) - Read access to SAP Datasphere
- Space authorization capabilities
- Data product sharing permissions

**Responsibilities**:
- Authorize spaces for data product installation
- Share data products to target HANA Cloud instances
- Manage formations in SAP for Me

**How to Check**:
1. Login to SAP Datasphere
2. Navigate to Space Management
3. Verify you can see "Authorize Spaces" option
4. Check user roles and privileges

### Level 2: HANA Cloud Database (Database Level)

**Location**: SAP HANA Cloud Database

**Required Privileges**: See detailed list below

**Responsibilities**:
- Create remote sources
- Create virtual tables
- Query data products
- Manage schemas and objects

---

## Required HANA Cloud Privileges

### System Privileges

**1. CREATE REMOTE SOURCE** ⭐ **CRITICAL**
- **Purpose**: Create named connections to SAP BDC
- **When Used**: During data product installation (automatic) or manual remote source creation
- **Granted By**: DBADMIN
- **Syntax**:
  ```sql
  GRANT CREATE REMOTE SOURCE TO <username>;
  ```

**2. CREATE VIRTUAL TABLE (Object Privilege)** ⭐ **CRITICAL**
- **Purpose**: Create virtual table pointers to remote data
- **When Used**: When installing data products or manually creating virtual tables
- **Granted By**: Remote source owner or DBADMIN
- **Syntax**:
  ```sql
  GRANT CREATE VIRTUAL TABLE ON REMOTE SOURCE <remote_source_name> TO <username>;
  ```
- **Important**: Automatically granted if user creates the remote source themselves

**3. CREATE SCHEMA**
- **Purpose**: Create schemas for organizing virtual tables
- **When Used**: If creating dedicated schemas for data products
- **Syntax**:
  ```sql
  GRANT CREATE SCHEMA TO <username>;
  ```

**4. CATALOG READ**
- **Purpose**: Browse metadata, system views, and database objects
- **When Used**: Exploring available data products and virtual tables
- **Syntax**:
  ```sql
  GRANT CATALOG READ TO <username>;
  ```

**5. IMPORT / EXPORT** (Optional but Recommended)
- **Purpose**: Data loading and unloading operations
- **When Used**: If materializing data from virtual tables
- **Syntax**:
  ```sql
  GRANT IMPORT TO <username>;
  GRANT EXPORT TO <username>;
  ```

### Schema Privileges

**Required on Target Schema** (where virtual tables will be created):

1. **CREATE ANY** - Create objects in schema
2. **SELECT** - Query virtual tables
3. **INSERT** (if materializing data)
4. **UPDATE** (if updating local copies)
5. **DELETE** (if managing local copies)
6. **DROP** - Remove virtual tables
7. **ALTER** - Modify objects
8. **EXECUTE** - Run procedures/functions
9. **INDEX** - Create indexes
10. **REFERENCES** - Create foreign keys
11. **TRUNCATE** - Clear tables

**Syntax for all schema privileges**:
```sql
GRANT ALTER ON SCHEMA <schema_name> TO <username>;
GRANT CREATE ANY ON SCHEMA <schema_name> TO <username>;
GRANT DELETE ON SCHEMA <schema_name> TO <username>;
GRANT DROP ON SCHEMA <schema_name> TO <username>;
GRANT EXECUTE ON SCHEMA <schema_name> TO <username>;
GRANT INDEX ON SCHEMA <schema_name> TO <username>;
GRANT INSERT ON SCHEMA <schema_name> TO <username>;
GRANT REFERENCES ON SCHEMA <schema_name> TO <username>;
GRANT SELECT ON SCHEMA <schema_name> TO <username>;
GRANT TRUNCATE ON SCHEMA <schema_name> TO <username>;
GRANT UPDATE ON SCHEMA <schema_name> TO <username>;
```

---

## User Setup Options

### Option 1: Data Product Consumer (Recommended)

**User**: P2P_DP_USER  
**Script**: `create_p2p_data_product_user.sql`  
**Purpose**: Dedicated user for data product operations

**Capabilities**:
- ✅ Install data products via HANA Cloud Central
- ✅ Create remote sources
- ✅ Create virtual tables
- ✅ Query all virtual tables
- ✅ Create views and calculation views
- ✅ Join virtual tables with local tables
- ✅ Export/Import data

**Privileges Granted**:
- System: CREATE REMOTE SOURCE, CREATE SCHEMA, CATALOG READ, IMPORT, EXPORT
- Schema: All 11 privileges on P2P_DATA_PRODUCTS schema
- Ownership: Owns P2P_DATA_PRODUCTS schema

**Setup Command**:
```sql
-- Execute entire script: create_p2p_data_product_user.sql
-- Run as DBADMIN in Database Explorer
```

### Option 2: Development User (Alternative)

**User**: P2P_DEV_USER  
**Script**: `create_p2p_user.sql`  
**Purpose**: General development user

**To Add Data Product Capabilities**:
```sql
-- Additional grants needed for P2P_DEV_USER:
GRANT CREATE REMOTE SOURCE TO P2P_DEV_USER;

-- If user will create virtual tables in P2P_SCHEMA:
GRANT CREATE ANY ON SCHEMA P2P_SCHEMA TO P2P_DEV_USER;
```

### Option 3: Use DBADMIN (Not Recommended)

**User**: DBADMIN  
**Purpose**: Administrative tasks only

**Why Not Recommended**:
- ❌ Too many privileges (security risk)
- ❌ No separation of duties
- ❌ Difficult to audit user-specific activities
- ❌ Best practice: Use DBADMIN only for user creation and administration

**When to Use**: Initial setup and troubleshooting only

---

## Data Product Installation Workflow

### Phase 1: Formation Setup (One-Time)

**Location**: SAP for Me (https://me.sap.com)

**Steps**:
1. Login to SAP for Me
2. Navigate to **Formations**
3. Verify formation exists or create new:
   - Name: e.g., "P2P Analytics Formation"
   - Components: SAP BDC + Your HANA Cloud instance
   - Users: Assign with appropriate roles
4. Establish trust between systems
5. Verify formation status: Active

**Required By**: BDC Administrator

### Phase 2: User Setup (One-Time)

**Location**: SAP HANA Database Explorer

**Steps**:
1. Login as **DBADMIN**
2. Open SQL Console
3. Execute **`create_p2p_data_product_user.sql`**
4. Verify successful creation (4 verification queries)
5. Note initial password: `P2P_DataProd123!`
6. User will be forced to change on first login

**Result**: P2P_DP_USER created with all required privileges

### Phase 3: Browse Data Products

**Location**: SAP Business Data Cloud Catalog & Marketplace

**Steps**:
1. Login to SAP BDC
2. Navigate to **Catalog & Marketplace**
3. Search for data products:
   - Filter by domain: Sales, Procurement, Finance
   - Search by keyword: e.g., "Supplier", "Invoice"
4. Review data product details:
   - Description and use cases
   - Available APIs and objects
   - Column definitions
   - Sample data
   - Quality metrics
5. Note data product names for sharing

**Data Products for P2P**:
- ✅ Supplier
- ✅ Purchase Order
- ✅ Purchase Requisition
- ✅ Supplier Invoice
- ✅ Service Entry Sheet
- ✅ Payment Terms
- ✅ Journal Entry Header

### Phase 4: Share Data Products

**Location**: SAP BDC Catalog

**Steps**:
1. Select data product
2. Click **"Share"** or **"Add Target"**
3. Select target: Your HANA Cloud instance (from formation)
4. Confirm sharing
5. Data product appears in HANA Cloud Central

**Required By**: BDC Administrator (Data Warehouse General privilege)

**What Happens**:
- Metadata shared to target HANA Cloud
- No data replication occurs
- Virtual table definitions prepared
- Ready for installation

### Phase 5: Install Data Products

**Location**: SAP HANA Cloud Central

**Steps**:
1. Login to HANA Cloud Central
2. Navigate to **Data Products** tab
3. View shared data products from BDC
4. Select data product to install
5. Click **"Install"**
6. Monitor installation progress
7. Verify completion status

**What Gets Created Automatically**:
```
Installation creates:
  ├─ Remote Source (connection to BDC)
  │   └─ Name: e.g., "BDC_REMOTE_SOURCE"
  ├─ Virtual Tables (one per business object)
  │   ├─ SUPPLIER
  │   ├─ PURCHASE_ORDER
  │   ├─ PURCHASE_ORDER_ITEM
  │   ├─ SUPPLIER_INVOICE
  │   └─ ...
  └─ Metadata (columns, types, descriptions)
```

**User Requirements**:
- Must have CREATE REMOTE SOURCE privilege ✅
- Must have CREATE ANY on target schema ✅
- CREATE VIRTUAL TABLE privilege granted automatically

### Phase 6: Query Virtual Tables

**Location**: SAP HANA Database Explorer

**Steps**:
1. Login as **P2P_DP_USER**
2. Navigate to **P2P_DATA_PRODUCTS** schema
3. View virtual tables
4. Execute SQL queries

**Example Queries**:

```sql
-- Query 1: View all suppliers
SELECT * FROM P2P_DATA_PRODUCTS.SUPPLIER
LIMIT 100;

-- Query 2: Find recent invoices
SELECT 
    SupplierInvoiceID,
    SupplierName,
    InvoiceDate,
    GrossAmount
FROM P2P_DATA_PRODUCTS.SUPPLIER_INVOICE
WHERE InvoiceDate >= '2026-01-01'
ORDER BY InvoiceDate DESC;

-- Query 3: Join virtual tables
SELECT 
    po.PurchaseOrderID,
    po.SupplierID,
    s.SupplierName,
    poi.MaterialID,
    poi.OrderQuantity
FROM P2P_DATA_PRODUCTS.PURCHASE_ORDER po
JOIN P2P_DATA_PRODUCTS.SUPPLIER s
    ON po.SupplierID = s.SupplierID
JOIN P2P_DATA_PRODUCTS.PURCHASE_ORDER_ITEM poi
    ON po.PurchaseOrderID = poi.PurchaseOrderID
WHERE po.CreatedDate >= '2026-01-01';

-- Query 4: Join virtual table with local table
-- (Assumes you have local P2P_SCHEMA with custom logic)
SELECT 
    vt.SupplierInvoiceID,
    vt.InvoiceAmount,
    lt.MatchingStatus,
    lt.VarianceAmount
FROM P2P_DATA_PRODUCTS.SUPPLIER_INVOICE vt
LEFT JOIN P2P_SCHEMA.INVOICE_MATCHING_STATUS lt
    ON vt.SupplierInvoiceID = lt.InvoiceID;
```

---

## Privilege Verification

### Check System Privileges

```sql
-- View all system privileges for user
SELECT GRANTEE, PRIVILEGE, IS_GRANTABLE
FROM SYS.GRANTED_PRIVILEGES
WHERE GRANTEE = 'P2P_DP_USER'
AND OBJECT_TYPE = 'SYSTEMPRIVILEGE'
ORDER BY PRIVILEGE;

-- Expected results:
-- CATALOG READ
-- CREATE REMOTE SOURCE ⭐
-- CREATE SCHEMA
-- EXPORT
-- IMPORT
```

### Check Schema Privileges

```sql
-- View all schema privileges
SELECT GRANTEE, PRIVILEGE, SCHEMA_NAME, IS_GRANTABLE
FROM SYS.GRANTED_PRIVILEGES
WHERE GRANTEE = 'P2P_DP_USER'
AND SCHEMA_NAME = 'P2P_DATA_PRODUCTS'
ORDER BY PRIVILEGE;

-- Expected: 11 privileges (ALTER, CREATE ANY, DELETE, DROP, EXECUTE, INDEX, INSERT, REFERENCES, SELECT, TRUNCATE, UPDATE)
```

### Check Remote Source Privileges

```sql
-- View remote source privileges
SELECT GRANTEE, PRIVILEGE, OBJECT_NAME
FROM SYS.GRANTED_PRIVILEGES
WHERE GRANTEE = 'P2P_DP_USER'
AND OBJECT_TYPE = 'REMOTESOURCE';

-- Expected after data product installation:
-- CREATE VIRTUAL TABLE privilege on BDC remote source
```

### Check Virtual Tables

```sql
-- List all virtual tables in schema
SELECT SCHEMA_NAME, TABLE_NAME, TABLE_TYPE, IS_VIRTUAL
FROM SYS.TABLES
WHERE SCHEMA_NAME = 'P2P_DATA_PRODUCTS'
AND IS_VIRTUAL = 'TRUE'
ORDER BY TABLE_NAME;
```

---

## Troubleshooting

### Issue 1: Cannot Install Data Product

**Symptom**: Installation fails with privilege error

**Possible Causes**:
- Missing CREATE REMOTE SOURCE privilege
- Missing CREATE ANY on target schema
- Formation not properly configured

**Solution**:
```sql
-- Verify user has required privileges:
SELECT PRIVILEGE FROM SYS.GRANTED_PRIVILEGES
WHERE GRANTEE = 'P2P_DP_USER'
AND PRIVILEGE IN ('CREATE REMOTE SOURCE', 'CREATE SCHEMA');

-- If missing, grant as DBADMIN:
GRANT CREATE REMOTE SOURCE TO P2P_DP_USER;
GRANT CREATE ANY ON SCHEMA P2P_DATA_PRODUCTS TO P2P_DP_USER;
```

### Issue 2: Error 258 - Insufficient Privilege

**Symptom**: "Error 258 - insufficient privilege" when granting

**Cause**: DBADMIN in BDC may have custom restrictions

**Solution**: Use individual GRANT statements (not GRANT ALL)
- Script `create_p2p_data_product_user.sql` already uses this approach
- See `HANA_CLOUD_BDC_RESEARCH_FINDINGS.md` for details

### Issue 3: Cannot See Virtual Tables

**Symptom**: Virtual tables not visible after installation

**Possible Causes**:
- Looking in wrong schema
- Installation not complete
- Database Explorer cache

**Solution**:
1. Verify installation status in HANA Cloud Central
2. Check P2P_DATA_PRODUCTS schema specifically
3. Refresh Database Explorer (F5)
4. Query system view:
   ```sql
   SELECT * FROM SYS.TABLES 
   WHERE IS_VIRTUAL = 'TRUE';
   ```

### Issue 4: Virtual Table Query Slow

**Symptom**: Queries taking too long

**Causes**:
- Network latency to BDC
- No filtering at source
- Selecting all columns

**Solution**:
```sql
-- Bad: Retrieve everything
SELECT * FROM P2P_DATA_PRODUCTS.SUPPLIER_INVOICE;

-- Good: Filter at source
SELECT SupplierInvoiceID, InvoiceAmount
FROM P2P_DATA_PRODUCTS.SUPPLIER_INVOICE
WHERE InvoiceDate >= '2026-01-01'
AND CompanyCode = '1000'
LIMIT 1000;
```

### Issue 5: Cannot Create Remote Source Manually

**Symptom**: CREATE REMOTE SOURCE fails

**Cause**: Missing privilege or incorrect syntax

**Solution**:
```sql
-- Verify privilege:
SELECT PRIVILEGE FROM SYS.GRANTED_PRIVILEGES
WHERE GRANTEE = 'P2P_DP_USER'
AND PRIVILEGE = 'CREATE REMOTE SOURCE';

-- Correct syntax:
CREATE REMOTE SOURCE BDC_MANUAL_SOURCE
ADAPTER "hanaodbc"
CONFIGURATION 'ServerNode=<bdc_host>:443;encrypt=true;sslValidateCertificate=false'
WITH CREDENTIAL TYPE 'PASSWORD' USING 'user=<user>;password=<password>';
```

---

## Best Practices

### Security

1. **Use Dedicated Users**
   - Create P2P_DP_USER for data products
   - Don't use DBADMIN for queries
   - Separate dev/test/prod users

2. **Minimal Privileges**
   - Grant only required privileges
   - Use schema-level grants, not system-wide
   - Review privileges regularly

3. **Password Management**
   - Force password change on first login ✅
   - Use strong passwords
   - Rotate credentials regularly

4. **Formation Security**
   - Limit formation membership
   - Separate formations for environments
   - Review trust relationships

### Performance

1. **Selective Queries**
   - Always use WHERE clauses
   - Filter at source, not in application
   - Select only needed columns

2. **Consider Materialization**
   - For frequently accessed data
   - Create local copies with scheduled refresh
   - Use calculation views for complex logic

3. **Monitor Usage**
   - Track virtual table queries
   - Identify slow queries
   - Optimize or materialize as needed

### Governance

1. **Documentation**
   - Document data product usage
   - Track dependencies
   - Maintain data lineage

2. **Change Management**
   - Test in dev before prod
   - Monitor data product updates
   - Communicate changes to users

3. **Audit Trail**
   - Log virtual table access
   - Monitor privilege grants
   - Review user activities

---

## Reference Scripts

### Script 1: create_p2p_data_product_user.sql ⭐ RECOMMENDED

**Purpose**: Create dedicated user for data product operations

**What It Creates**:
- User: P2P_DP_USER
- Password: P2P_DataProd123! (must change)
- Schema: P2P_DATA_PRODUCTS
- Privileges: All required for data products

**Usage**:
```sql
-- Execute in Database Explorer as DBADMIN
-- Run entire script (20 statements)
```

### Script 2: create_p2p_user.sql

**Purpose**: Create general development user

**To Add Data Product Capabilities**:
```sql
GRANT CREATE REMOTE SOURCE TO P2P_DEV_USER;
```

### Verification Queries

```sql
-- 1. Check user exists
SELECT * FROM SYS.USERS WHERE USER_NAME = 'P2P_DP_USER';

-- 2. Check system privileges
SELECT * FROM SYS.GRANTED_PRIVILEGES
WHERE GRANTEE = 'P2P_DP_USER'
AND OBJECT_TYPE = 'SYSTEMPRIVILEGE';

-- 3. Check schema privileges
SELECT * FROM SYS.GRANTED_PRIVILEGES
WHERE GRANTEE = 'P2P_DP_USER'
AND SCHEMA_NAME = 'P2P_DATA_PRODUCTS';

-- 4. Check remote sources
SELECT * FROM SYS.REMOTE_SOURCES;

-- 5. Check virtual tables
SELECT * FROM SYS.TABLES
WHERE IS_VIRTUAL = 'TRUE'
AND SCHEMA_NAME = 'P2P_DATA_PRODUCTS';
```

---

## Summary

### Key Privileges Required

**CRITICAL (Must Have)**:
1. ⭐ CREATE REMOTE SOURCE (system privilege)
2. ⭐ CREATE VIRTUAL TABLE (object privilege on remote source)
3. ⭐ CREATE ANY (schema privilege)

**Recommended**:
4. CREATE SCHEMA (system privilege)
5. CATALOG READ (system privilege)
6. SELECT (schema privilege)

**Optional**:
7. IMPORT/EXPORT (for materialization)
8. Other schema privileges (for advanced operations)

### Quick Setup Checklist

- [ ] Verify formation exists in SAP for Me
- [ ] Execute `create_p2p_data_product_user.sql` as DBADMIN
- [ ] Verify user creation (4 verification queries)
- [ ] Login as P2P_DP_USER and change password
- [ ] Browse data products in BDC Catalog
- [ ] Share data products to HANA Cloud instance
- [ ] Install data products in HANA Cloud Central
- [ ] Query virtual tables in Database Explorer

### Next Steps

1. 📋 Execute user creation script
2. 📋 Verify formation configuration
3. 📋 Install first data product (Supplier)
4. 📋 Test virtual table queries
5. 📋 Expand to other P2P data products
6. 📋 Build analytics and reports

---

## References

### Official Documentation

1. **Data Product Support in SAP HANA Cloud**
   - https://help.sap.com/docs/hana-cloud/sap-hana-cloud-administration-guide/data-product-support-in-sap-hana-cloud-internal

2. **Managing User Privileges**
   - https://help.sap.com/docs/hana-cloud-database/sap-hana-cloud-sap-hana-database-data-access-guide/managing-user-privileges

3. **Create Virtual Table**
   - https://help.sap.com/docs/hana-cloud-database/sap-hana-cloud-sap-hana-database-data-access-guide/create-virtual-table

4. **Source Privileges Reference**
   - https://help.sap.com/docs/hana-cloud-database/sap-hana-cloud-sap-hana-database-security-guide/source-privileges-reference

5. **Authorize Spaces (SAP Datasphere)**
   - https://help.sap.com/docs/SAP_DATASPHERE/9f804b8efa8043539289f42f372c4862/67ec785b5de842488781f20c4ab52a9f.html

### Related Documentation

- `DATA_PRODUCT_SUPPORT_IN_HANA_CLOUD.md` - Complete guide to data products
- `HANA_CLOUD_PRIVILEGES_GUIDE.md` - General HANA Cloud privilege model
- `HANA_CLOUD_BDC_RESEARCH_FINDINGS.md` - BDC-specific findings

---

**Document Version**: 1.0  
**Status**: Production-ready  
**Last Updated**: January 22, 2026, 12:10 AM  
**Next Review**: After first data product installation
