# Grant Data Product Roles to P2P User

**Date**: January 24, 2026  
**Purpose**: Enable P2P_DEV_USER to view and access data products in BDC  
**Based on**: Screenshot showing available role collections

---

## 🎯 Objective

Grant the P2P_DEV_USER the necessary roles to:
- ✅ View available data products
- ✅ Access data product catalog
- ✅ Query data product tables
- ✅ Develop P2P applications

---

## 📋 Available Role Collections (From Your Screenshot)

Your BTP user currently has these role collections:

1. ✅ **SAP HANA Cloud Administrator**
2. ✅ **SAP HANA Cloud Data Publisher Administrator**
3. ✅ **SAP HANA Cloud Data Publisher Viewer** ⭐ KEY FOR DATA PRODUCTS
4. ✅ **SAP HANA Cloud Security Administrator**
5. ✅ **SAP HANA Cloud Viewer** ⭐ KEY FOR VIEWING
6. ✅ **Subaccount Service Administrator**

---

## 🔑 Recommended Roles for P2P_DEV_USER

### **Option 1: Data Publisher Viewer** ⭐ RECOMMENDED

**Role**: `SAP HANA Cloud Data Publisher Viewer`

**What it provides**:
- ✅ View data products in catalog
- ✅ See data product metadata
- ✅ Access to data product schemas (read-only)
- ✅ Query data product tables

**How to grant** (via SQL as DBADMIN):
```sql
-- Check if role exists in HANA
SELECT ROLE_NAME FROM SYS.ROLES 
WHERE ROLE_NAME LIKE '%DATA%PUBLISHER%VIEWER%';

-- If role exists, grant it
GRANT "SAP HANA Cloud Data Publisher Viewer" TO P2P_DEV_USER;

-- Verify grant
SELECT * FROM SYS.GRANTED_ROLES 
WHERE GRANTEE = 'P2P_DEV_USER';
```

### **Option 2: HANA Cloud Viewer** ⭐ ALSO USEFUL

**Role**: `SAP HANA Cloud Viewer`

**What it provides**:
- ✅ Read-only access to database objects
- ✅ View schemas and tables
- ✅ Execute SELECT queries
- ✅ View system information

**How to grant** (via SQL as DBADMIN):
```sql
-- Check if role exists
SELECT ROLE_NAME FROM SYS.ROLES 
WHERE ROLE_NAME LIKE '%CLOUD%VIEWER%';

-- Grant role
GRANT "SAP HANA Cloud Viewer" TO P2P_DEV_USER;
```

---

## 📝 Step-by-Step Instructions

### **Step 1: Connect as DBADMIN**

Open HANA Database Explorer and connect with DBADMIN credentials.

### **Step 2: Check Available Roles**

```sql
-- See all available roles related to data products
SELECT ROLE_NAME, ROLE_SCHEMA_NAME 
FROM SYS.ROLES 
WHERE ROLE_NAME LIKE '%DATA%' 
   OR ROLE_NAME LIKE '%PUBLISHER%'
   OR ROLE_NAME LIKE '%VIEWER%'
ORDER BY ROLE_NAME;
```

### **Step 3: Grant Data Publisher Viewer Role**

```sql
-- Grant the data publisher viewer role
GRANT "SAP HANA Cloud Data Publisher Viewer" TO P2P_DEV_USER;

-- Also grant cloud viewer for general access
GRANT "SAP HANA Cloud Viewer" TO P2P_DEV_USER;
```

### **Step 4: Verify Grants**

```sql
-- Check what roles P2P_DEV_USER has
SELECT 
    GRANTEE,
    ROLE_NAME,
    GRANTOR,
    IS_GRANTABLE
FROM SYS.GRANTED_ROLES 
WHERE GRANTEE = 'P2P_DEV_USER'
ORDER BY ROLE_NAME;
```

### **Step 5: Test as P2P_DEV_USER**

**Connect as P2P_DEV_USER** and try:

```sql
-- List all data product schemas
SELECT SCHEMA_NAME, SCHEMA_OWNER, CREATE_TIME
FROM SYS.SCHEMAS
WHERE SCHEMA_NAME LIKE '_SAP_DATAPRODUCT%'
ORDER BY CREATE_TIME DESC;

-- Query a data product (example: Supplier)
SELECT TOP 10 *
FROM "_SAP_DATAPRODUCT_sap_s4com_dataProduct_Supplier_v1_c8f5c255-6ddd-444a-8f90-01baa10b87d3"."_SAP_DATAPRODUCT_b6d7050b-8c9a-4c4d-9689-346e4ab14855_supplier.Supplier";
```

---

## 🔍 Additional Privileges You May Need

### **For Data Product Schema Access**

If the roles don't provide enough access, grant SELECT on specific schemas:

```sql
-- Grant SELECT on all data product schemas
-- (Execute as DBADMIN)

-- Example for Supplier data product
GRANT SELECT ON SCHEMA "_SAP_DATAPRODUCT_sap_s4com_dataProduct_Supplier_v1_c8f5c255-6ddd-444a-8f90-01baa10b87d3" 
TO P2P_DEV_USER;

-- You may need to repeat for each data product schema
```

### **For Catalog Access**

```sql
-- Grant catalog read privilege
GRANT CATALOG READ TO P2P_DEV_USER;
```

---

## 📊 Role Collection Mapping

| BTP Role Collection | HANA Database Role | Purpose |
|-------------------|-------------------|----------|
| SAP HANA Cloud Data Publisher Viewer | (BTP-managed) | View data products in catalog |
| SAP HANA Cloud Viewer | (BTP-managed) | Read-only database access |
| SAP HANA Cloud Administrator | (BTP-managed) | Full admin access (DBADMIN has this) |

**Note**: BTP role collections may automatically grant corresponding HANA database roles.

---

## 🎯 What P2P_DEV_USER Can Do After This

### **✅ Can Do:**
1. View available data products in catalog
2. List data product schemas
3. Query data product tables (SELECT)
4. View data product metadata
5. Use data products in P2P application
6. Create views joining data products with custom tables

### **❌ Cannot Do:**
1. Install new data products (requires admin)
2. Modify data products (they're read-only)
3. Delete data products
4. Change data product configurations
5. Access SYSTEM-level operations

---

## 🧪 Testing Script

Save this as `test_p2p_data_product_access.sql`:

```sql
-- ============================================
-- Test Data Product Access for P2P_DEV_USER
-- Run this after granting roles
-- ============================================

-- Connect as: P2P_DEV_USER
-- Expected: All queries should succeed

-- Test 1: List data product schemas
SELECT 'Test 1: List Data Product Schemas' as TEST;
SELECT COUNT(*) as DATA_PRODUCT_COUNT
FROM SYS.SCHEMAS
WHERE SCHEMA_NAME LIKE '_SAP_DATAPRODUCT%';

-- Test 2: Query Supplier data product
SELECT 'Test 2: Query Supplier Data Product' as TEST;
SELECT TOP 5 
    Supplier,
    SupplierName,
    Country
FROM "_SAP_DATAPRODUCT_sap_s4com_dataProduct_Supplier_v1_c8f5c255-6ddd-444a-8f90-01baa10b87d3"."_SAP_DATAPRODUCT_b6d7050b-8c9a-4c4d-9689-346e4ab14855_supplier.Supplier";

-- Test 3: Check granted roles
SELECT 'Test 3: Check My Roles' as TEST;
SELECT ROLE_NAME 
FROM SYS.GRANTED_ROLES 
WHERE GRANTEE = CURRENT_USER
ORDER BY ROLE_NAME;

-- Test 4: Check schema privileges
SELECT 'Test 4: Check My Schema Privileges' as TEST;
SELECT SCHEMA_NAME, PRIVILEGE
FROM SYS.EFFECTIVE_PRIVILEGES
WHERE GRANTEE = CURRENT_USER
  AND SCHEMA_NAME LIKE '_SAP_DATAPRODUCT%'
GROUP BY SCHEMA_NAME, PRIVILEGE;

-- If all tests pass, P2P_DEV_USER has proper data product access! ✅
```

---

## 🚨 Troubleshooting

### **Problem: Roles don't exist in HANA**

**Symptom**:
```
invalid role name: SAP HANA Cloud Data Publisher Viewer
```

**Solution**:
These might be BTP-only roles. Use schema-level grants instead:

```sql
-- Grant SELECT on data product schemas
CALL SYS.GRANT_PRIVILEGE_ON_SCHEMA_TO_USER(
    '_SAP_DATAPRODUCT_sap_s4com_dataProduct_Supplier_v1_c8f5c255-6ddd-444a-8f90-01baa10b87d3',
    'SELECT',
    'P2P_DEV_USER'
);
```

### **Problem: Error 258 (insufficient privilege)**

**Cause**: DBADMIN doesn't have rights to grant these roles in BDC

**Solution**:
1. Grant via SAP BTP Cockpit (as BTP admin)
2. Or use direct schema grants (see above)
3. Or contact SAP Support for role assignment

### **Problem: Can't see data products**

**Cause**: Data products not installed yet

**Solution**:
1. Check HANA Cloud Central
2. Install needed data products (Supplier Invoice, Purchase Order, etc.)
3. Then grant access to P2P_DEV_USER

---

## 📋 Recommended Grant Script

**File**: `grant_p2p_data_product_access.sql`

```sql
-- ============================================
-- Grant Data Product Access to P2P_DEV_USER
-- Execute as: DBADMIN
-- ============================================

-- Try to grant standard roles first
BEGIN
    -- Try Data Publisher Viewer role
    EXEC 'GRANT "SAP HANA Cloud Data Publisher Viewer" TO P2P_DEV_USER';
    SELECT 'Granted: Data Publisher Viewer' as STATUS FROM DUMMY;
EXCEPTION
    WHEN OTHERS THEN
        SELECT 'Role not available: Data Publisher Viewer' as STATUS FROM DUMMY;
END;

BEGIN
    -- Try Cloud Viewer role
    EXEC 'GRANT "SAP HANA Cloud Viewer" TO P2P_DEV_USER';
    SELECT 'Granted: Cloud Viewer' as STATUS FROM DUMMY;
EXCEPTION
    WHEN OTHERS THEN
        SELECT 'Role not available: Cloud Viewer' as STATUS FROM DUMMY;
END;

-- Grant CATALOG READ (essential for browsing)
GRANT CATALOG READ TO P2P_DEV_USER;
SELECT 'Granted: CATALOG READ' as STATUS FROM DUMMY;

-- Grant SELECT on all existing data product schemas
-- (You'll need to customize this based on your data products)

-- Supplier
GRANT SELECT ON SCHEMA "_SAP_DATAPRODUCT_sap_s4com_dataProduct_Supplier_v1_c8f5c255-6ddd-444a-8f90-01baa10b87d3" 
TO P2P_DEV_USER;

-- Customer (if exists)
GRANT SELECT ON SCHEMA "_SAP_DATAPRODUCT_sap_s4com_dataProduct_Customer_v1_..." 
TO P2P_DEV_USER;

-- Add more as needed...

-- Verify grants
SELECT 
    'Final Status: Roles and Privileges for P2P_DEV_USER' as SUMMARY,
    COUNT(*) as GRANTED_ROLES
FROM SYS.GRANTED_ROLES 
WHERE GRANTEE = 'P2P_DEV_USER';

SELECT 
    SCHEMA_NAME,
    PRIVILEGE
FROM SYS.EFFECTIVE_PRIVILEGES
WHERE GRANTEE = 'P2P_DEV_USER'
  AND SCHEMA_NAME LIKE '_SAP_DATAPRODUCT%'
ORDER BY SCHEMA_NAME, PRIVILEGE;
```

---

## ✅ Success Criteria

After granting roles, P2P_DEV_USER should be able to:

1. ✅ Login to Database Explorer
2. ✅ See data product schemas in catalog
3. ✅ Execute SELECT queries on data products
4. ✅ View table metadata and structure
5. ✅ Create views joining data products
6. ✅ Develop P2P application queries

---

## 📚 References

- **BTP Cockpit**: Where role collections are managed
- **HANA Database Explorer**: Where SQL grants are executed
- **Documentation**: `HANA_CLOUD_IN_BDC_CONTEXT.md`
- **Data Products**: `DATA_PRODUCT_SUPPORT_IN_HANA_CLOUD.md`

---

**Document Version**: 1.0  
**Created**: January 24, 2026  
**Status**: Ready to execute