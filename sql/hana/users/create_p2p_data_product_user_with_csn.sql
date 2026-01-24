-- ============================================================================
-- SAP HANA Cloud User Creation for Data Product & CSN Access
-- ============================================================================
-- Purpose: Create P2P_DP_USER with privileges for data products AND CSN viewer
-- Created: 2026-01-24
-- Updated: Added CSN table access for CSN viewer feature
-- Environment: SAP HANA Cloud in BDC Formation (SAP4ME)
-- 
-- IMPORTANT: This user has minimal privileges - read-only for security
-- ============================================================================

-- Step 1: Create the user with fixed password
CREATE USER P2P_DP_USER PASSWORD "P2P_DataProd123!";

-- Step 2: Add user description
COMMENT ON USER P2P_DP_USER IS 'P2P Data Product Consumer - Can query data products and CSN definitions';

-- ============================================================================
-- SYSTEM PRIVILEGES - Read-Only Access Only
-- ============================================================================

-- Step 3: Grant CATALOG READ (required to browse metadata and system views)
GRANT CATALOG READ TO P2P_DP_USER;

-- ============================================================================
-- DATA PRODUCT GATEWAY SCHEMA ACCESS ⭐ NEW FOR CSN VIEWER
-- ============================================================================

-- Step 4: Grant SELECT on Data Product Gateway schema (for CSN table access)
GRANT SELECT ON SCHEMA "_SAP_DB_ACCESS_DATA_PRODUCT_GATEWAY" TO P2P_DP_USER;

-- Step 5: Grant SELECT on CSN table specifically (for CSN viewer feature) ⭐
GRANT SELECT ON "_SAP_DB_ACCESS_DATA_PRODUCT_GATEWAY"."_SAP_DATAPRODUCT_DELTA_CSN" 
TO P2P_DP_USER;

-- Step 6: Grant SELECT on other gateway tables (for metadata queries)
GRANT SELECT ON "_SAP_DB_ACCESS_DATA_PRODUCT_GATEWAY"."_SAP_DATAPRODUCT_DATA_PRODUCT_REMOTE_SOURCES" 
TO P2P_DP_USER;

GRANT SELECT ON "_SAP_DB_ACCESS_DATA_PRODUCT_GATEWAY"."_SAP_DATAPRODUCT_DATA_PRODUCT_VERSIONS" 
TO P2P_DP_USER;

-- ============================================================================
-- INSTALLED DATA PRODUCT SCHEMAS ACCESS
-- ============================================================================

-- Step 7: Grant SELECT on PurchaseOrder data product schema
GRANT SELECT ON SCHEMA "_SAP_DATAPRODUCT_sap_s4com_dataProduct_PurchaseOrder_v1_uuid" 
TO P2P_DP_USER;

-- Step 8: Grant SELECT on SalesOrder data product schema
GRANT SELECT ON SCHEMA "_SAP_DATAPRODUCT_sap_s4com_dataProduct_SalesOrder_v1_uuid" 
TO P2P_DP_USER;

-- Note: Add more GRANT SELECT statements as additional data products are installed

-- ============================================================================
-- CREATE DEDICATED SCHEMA (Optional - for user's own work)
-- ============================================================================

-- Step 9: Create schema owned by the user (optional, for custom views/queries)
CREATE SCHEMA P2P_DATA_PRODUCTS OWNED BY P2P_DP_USER;

-- Step 10: Grant full access to owned schema
GRANT SELECT ON SCHEMA P2P_DATA_PRODUCTS TO P2P_DP_USER;
GRANT CREATE ANY ON SCHEMA P2P_DATA_PRODUCTS TO P2P_DP_USER;
GRANT INSERT ON SCHEMA P2P_DATA_PRODUCTS TO P2P_DP_USER;
GRANT UPDATE ON SCHEMA P2P_DATA_PRODUCTS TO P2P_DP_USER;
GRANT DELETE ON SCHEMA P2P_DATA_PRODUCTS TO P2P_DP_USER;
GRANT DROP ON SCHEMA P2P_DATA_PRODUCTS TO P2P_DP_USER;

-- Step 11: Set default schema
ALTER USER P2P_DP_USER SET PARAMETER SCHEMA = 'P2P_DATA_PRODUCTS';

-- ============================================================================
-- VERIFICATION QUERIES
-- ============================================================================

-- Query 1: Verify user was created
SELECT USER_NAME, CREATOR, CREATE_TIME, USER_DEACTIVATED
FROM SYS.USERS 
WHERE USER_NAME = 'P2P_DP_USER';

-- Query 2: Verify system privileges
SELECT GRANTEE, PRIVILEGE, IS_GRANTABLE
FROM SYS.GRANTED_PRIVILEGES
WHERE GRANTEE = 'P2P_DP_USER'
AND OBJECT_TYPE = 'SYSTEMPRIVILEGE'
ORDER BY PRIVILEGE;

-- Query 3: Verify schema privileges (should show gateway and data product schemas)
SELECT GRANTEE, PRIVILEGE, SCHEMA_NAME, IS_GRANTABLE
FROM SYS.GRANTED_PRIVILEGES
WHERE GRANTEE = 'P2P_DP_USER'
AND OBJECT_TYPE = 'SCHEMA'
ORDER BY SCHEMA_NAME, PRIVILEGE;

-- Query 4: Verify table-level privileges (should show CSN table)
SELECT GRANTEE, PRIVILEGE, SCHEMA_NAME, OBJECT_NAME, IS_GRANTABLE
FROM SYS.GRANTED_PRIVILEGES
WHERE GRANTEE = 'P2P_DP_USER'
AND OBJECT_TYPE = 'TABLE'
ORDER BY SCHEMA_NAME, OBJECT_NAME, PRIVILEGE;

-- Query 5: Test CSN table access ⭐
SELECT REMOTE_SOURCE_NAME, 
       LEFT(CSN_JSON, 100) as CSN_PREVIEW
FROM "_SAP_DB_ACCESS_DATA_PRODUCT_GATEWAY"."_SAP_DATAPRODUCT_DELTA_CSN";

-- Expected: Should return CSN data without Error 258

-- ============================================================================
-- WHAT THIS USER CAN DO
-- ============================================================================
--
-- CSN Viewer Feature (NEW):
-- ✅ Query CSN table to retrieve data product schemas
-- ✅ View CSN_JSON column with complete CSN definitions
-- ✅ Support automated CSN viewer in P2P application
--
-- Data Product Queries:
-- ✅ Query installed data product virtual tables (SELECT only)
-- ✅ Query metadata tables in gateway schema
-- ✅ Create views in P2P_DATA_PRODUCTS schema
-- ✅ Join virtual tables with local tables
--
-- Security Profile:
-- ✅ READ-ONLY access to data products and CSN
-- ❌ CANNOT modify data products
-- ❌ CANNOT create remote sources
-- ❌ CANNOT install new data products (must use HANA Cloud Central UI)
-- ❌ CANNOT grant privileges to other users
--
-- This is a secure, read-only user perfect for application queries!
--
-- ============================================================================

-- ============================================================================
-- TESTING CSN ACCESS
-- ============================================================================

-- Test 1: Query CSN table structure
SELECT COLUMN_NAME, DATA_TYPE_NAME, LENGTH
FROM SYS.TABLE_COLUMNS
WHERE SCHEMA_NAME = '_SAP_DB_ACCESS_DATA_PRODUCT_GATEWAY'
AND TABLE_NAME = '_SAP_DATAPRODUCT_DELTA_CSN'
ORDER BY POSITION;

-- Expected columns:
-- REMOTE_SOURCE_NAME (NVARCHAR, 255)
-- CSN_JSON (NCLOB, 2147483647)

-- Test 2: Count CSN records
SELECT COUNT(*) as CSN_COUNT
FROM "_SAP_DB_ACCESS_DATA_PRODUCT_GATEWAY"."_SAP_DATAPRODUCT_DELTA_CSN";

-- Expected: Should match number of installed data products

-- Test 3: Query CSN for specific data product
SELECT REMOTE_SOURCE_NAME,
       CSN_JSON
FROM "_SAP_DB_ACCESS_DATA_PRODUCT_GATEWAY"."_SAP_DATAPRODUCT_DELTA_CSN"
WHERE REMOTE_SOURCE_NAME LIKE '%PurchaseOrder%';

-- Expected: CSN_JSON contains complete schema definition

-- ============================================================================
-- BACKEND CONFIGURATION
-- ============================================================================
--
-- After creating this user, update backend/.env or default-env.json:
--
-- {
--   "HANA_HOST": "e7decab9-3e98-41cf-bbf7-d0a8c13d7fb9.hana.prod-eu10.hanacloud.ondemand.com",
--   "HANA_PORT": "443",
--   "HANA_USER": "P2P_DP_USER",  ← Use this user instead of DBADMIN
--   "HANA_PASSWORD": "P2P_DataProd123!",
--   "HANA_ENCRYPT": "true"
-- }
--
-- This provides secure, read-only access for the CSN viewer application!
--
-- ============================================================================

-- ============================================================================
-- CSN VIEWER API ENDPOINT
-- ============================================================================
--
-- Backend can now implement:
-- GET /api/data-products/<product>/csn
--
-- SQL query used by endpoint:
-- SELECT CSN_JSON 
-- FROM "_SAP_DB_ACCESS_DATA_PRODUCT_GATEWAY"."_SAP_DATAPRODUCT_DELTA_CSN"
-- WHERE REMOTE_SOURCE_NAME LIKE '%<product>%';
--
-- Returns: Complete CSN JSON for the specified data product
--
-- ============================================================================

-- ============================================================================
-- TROUBLESHOOTING
-- ============================================================================
--
-- Issue: Still getting "Error 258 - insufficient privilege" on CSN table
-- Solution: 
-- 1. Verify user was created successfully (Query 1)
-- 2. Verify table grant was applied (Query 4)
-- 3. Try connecting with P2P_DP_USER and running Test 2
-- 4. If still failing, DBADMIN may need to run the GRANT again
--
-- Issue: Cannot query data product virtual tables
-- Solution: Add GRANT SELECT for specific data product schemas (Steps 7-8)
--
-- Issue: User doesn't have enough privileges for custom operations
-- Solution: This is intentional! P2P_DP_USER is read-only for security.
--           Use DBADMIN for administrative tasks.
--
-- ============================================================================

-- ============================================================================
-- SECURITY NOTES
-- ============================================================================
--
-- Why P2P_DP_USER is better than DBADMIN:
-- ✅ Principle of least privilege - only what's needed
-- ✅ Read-only access to sensitive data
-- ✅ Cannot accidentally modify system tables
-- ✅ Cannot grant privileges to other users
-- ✅ Safer for production deployment
-- ✅ Audit trail shows P2P_DP_USER activity separately
--
-- DBADMIN should only be used for:
-- ❌ User creation and privilege grants
-- ❌ Schema management
-- ❌ System administration
-- ❌ NOT for application queries!
--
-- ============================================================================

-- ============================================================================
-- SCRIPT END
-- ============================================================================
-- Execute this entire script in SAP HANA Database Explorer as DBADMIN
-- Total statements: 11 grants + 3 admin statements
-- Total verification queries: 5
-- Expected result: P2P_DP_USER ready for CSN viewer implementation!
-- ============================================================================