-- ============================================================================
-- SAP HANA Cloud User Creation for Data Product Consumption
-- ============================================================================
-- Purpose: Create P2P_DP_USER with privileges to install and consume data products
-- Created: 2026-01-22
-- Environment: SAP HANA Cloud in BDC Formation (SAP4ME)
-- 
-- IMPORTANT: This script creates a user specifically for data product operations
-- including installing data products, creating virtual tables, and querying them.
-- ============================================================================

-- Step 1: Create the user with fixed password (no forced change)
CREATE USER P2P_DP_USER PASSWORD "P2P_DataProd123!";

-- Step 2: Add user description
COMMENT ON USER P2P_DP_USER IS 'P2P Data Product Consumer - Can install and query BDC data products';

-- ============================================================================
-- SYSTEM PRIVILEGES - Required for Data Product Operations
-- ============================================================================

-- Step 4: Grant CREATE REMOTE SOURCE (required to create remote sources to BDC)
GRANT CREATE REMOTE SOURCE TO P2P_DP_USER;

-- Step 5: Grant CREATE SCHEMA (required if creating schemas for virtual tables)
GRANT CREATE SCHEMA TO P2P_DP_USER;

-- Step 6: Grant CATALOG READ (required to browse metadata and system views)
GRANT CATALOG READ TO P2P_DP_USER;

-- Step 7: Grant IMPORT/EXPORT (useful for data loading operations)
GRANT IMPORT TO P2P_DP_USER;
GRANT EXPORT TO P2P_DP_USER;

-- ============================================================================
-- SCHEMA CREATION - Create dedicated schema for data product virtual tables
-- ============================================================================

-- Step 8: Create schema owned by the user
CREATE SCHEMA P2P_DATA_PRODUCTS OWNED BY P2P_DP_USER;

-- ============================================================================
-- SCHEMA PRIVILEGES - Grant full access to owned schema
-- ============================================================================
-- Note: Using individual grants for BDC compatibility (Error 258 workaround)

-- Step 9-19: Grant all schema privileges individually
GRANT ALTER ON SCHEMA P2P_DATA_PRODUCTS TO P2P_DP_USER WITH GRANT OPTION;
GRANT CREATE ANY ON SCHEMA P2P_DATA_PRODUCTS TO P2P_DP_USER WITH GRANT OPTION;
GRANT DELETE ON SCHEMA P2P_DATA_PRODUCTS TO P2P_DP_USER WITH GRANT OPTION;
GRANT DROP ON SCHEMA P2P_DATA_PRODUCTS TO P2P_DP_USER WITH GRANT OPTION;
GRANT EXECUTE ON SCHEMA P2P_DATA_PRODUCTS TO P2P_DP_USER WITH GRANT OPTION;
GRANT INDEX ON SCHEMA P2P_DATA_PRODUCTS TO P2P_DP_USER WITH GRANT OPTION;
GRANT INSERT ON SCHEMA P2P_DATA_PRODUCTS TO P2P_DP_USER WITH GRANT OPTION;
GRANT REFERENCES ON SCHEMA P2P_DATA_PRODUCTS TO P2P_DP_USER WITH GRANT OPTION;
GRANT SELECT ON SCHEMA P2P_DATA_PRODUCTS TO P2P_DP_USER WITH GRANT OPTION;
GRANT TRUNCATE ON SCHEMA P2P_DATA_PRODUCTS TO P2P_DP_USER WITH GRANT OPTION;
GRANT UPDATE ON SCHEMA P2P_DATA_PRODUCTS TO P2P_DP_USER WITH GRANT OPTION;

-- Step 20: Set default schema
ALTER USER P2P_DP_USER SET PARAMETER SCHEMA = 'P2P_DATA_PRODUCTS';

-- ============================================================================
-- VERIFICATION QUERIES
-- ============================================================================
-- Run these queries to verify successful user creation and privilege grants

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

-- Query 3: Verify schema privileges
SELECT GRANTEE, PRIVILEGE, SCHEMA_NAME, IS_GRANTABLE
FROM SYS.GRANTED_PRIVILEGES
WHERE GRANTEE = 'P2P_DP_USER'
AND SCHEMA_NAME = 'P2P_DATA_PRODUCTS'
ORDER BY PRIVILEGE;

-- Query 4: Verify schema ownership
SELECT SCHEMA_NAME, SCHEMA_OWNER, CREATE_TIME
FROM SYS.SCHEMAS
WHERE SCHEMA_NAME = 'P2P_DATA_PRODUCTS';

-- ============================================================================
-- EXPECTED RESULTS
-- ============================================================================
-- 
-- Query 1: Should return 1 row with USER_DEACTIVATED = 'FALSE'
-- Query 2: Should return 5 rows (CREATE REMOTE SOURCE, CREATE SCHEMA, CATALOG READ, IMPORT, EXPORT)
-- Query 3: Should return 11 rows (all schema privileges)
-- Query 4: Should return 1 row with SCHEMA_OWNER = 'P2P_DP_USER'
--
-- Total Statements: 20 creation/grant statements
-- Total Verification Queries: 4
-- 
-- ============================================================================

-- ============================================================================
-- WHAT THIS USER CAN DO
-- ============================================================================
--
-- Data Product Operations:
-- ✅ Install data products from SAP BDC (via HANA Cloud Central UI)
-- ✅ Create remote sources to BDC (CREATE REMOTE SOURCE privilege)
-- ✅ Create virtual tables pointing to BDC data (CREATE VIRTUAL TABLE privilege on remote source)
-- ✅ Query virtual tables (SELECT privilege on schema)
-- ✅ Create additional schemas if needed (CREATE SCHEMA privilege)
-- ✅ Join virtual tables with local tables
-- ✅ Create views on virtual tables
-- ✅ Import/Export data
--
-- What happens during data product installation:
-- 1. HANA Cloud Central creates remote source automatically (user must have CREATE REMOTE SOURCE)
-- 2. Virtual tables created in P2P_DATA_PRODUCTS schema (user is owner)
-- 3. User can query virtual tables immediately
-- 4. No data replication - queries go to BDC via remote source
--
-- ============================================================================

-- ============================================================================
-- ADDITIONAL GRANTS (Optional - if needed for specific scenarios)
-- ============================================================================
--
-- If user needs to grant virtual table access to other users:
-- GRANT CREATE VIRTUAL TABLE ON REMOTE SOURCE <remote_source_name> TO P2P_DP_USER WITH GRANT OPTION;
--
-- If user needs to create calculation views:
-- GRANT CREATE ANY ON SCHEMA P2P_DATA_PRODUCTS TO P2P_DP_USER; (already granted above)
--
-- If user needs to create procedures/functions:
-- GRANT EXECUTE ON SCHEMA P2P_DATA_PRODUCTS TO P2P_DP_USER; (already granted above)
--
-- ============================================================================

-- ============================================================================
-- POST-CREATION WORKFLOW
-- ============================================================================
--
-- After running this script successfully:
--
-- 1. Login as P2P_DP_USER with password "P2P_DataProd123!"
-- 2. Verify formation exists in SAP for Me
-- 3. In SAP BDC Catalog & Marketplace:
--    - Browse for P2P data products:
--      * Supplier
--      * Purchase Order
--      * Supplier Invoice
--      * Service Entry Sheet
--      * Payment Terms
--      * Journal Entry Header
-- 4. Share selected data products to your HANA Cloud instance
-- 5. In SAP HANA Cloud Central:
--    - Navigate to Data Products tab
--    - Install shared data products
--    - Verify virtual tables created in P2P_DATA_PRODUCTS schema
-- 6. Query virtual tables:
--    SELECT * FROM P2P_DATA_PRODUCTS.[VIRTUAL_TABLE_NAME];
--
-- ============================================================================

-- ============================================================================
-- TROUBLESHOOTING
-- ============================================================================
--
-- Issue: "Error 258 - insufficient privilege" when creating remote source
-- Solution: This script grants CREATE REMOTE SOURCE - verify it was successful
--
-- Issue: Cannot see Data Products tab in HANA Cloud Central
-- Solution: Verify formation exists and includes your HANA Cloud instance
--
-- Issue: Virtual tables not appearing after installation
-- Solution: Check P2P_DATA_PRODUCTS schema, refresh Database Explorer
--
-- Issue: "CREATE VIRTUAL TABLE privilege required"
-- Solution: When remote source is created by data product installation,
--           the privilege should be granted automatically. If manual creation
--           needed, have DBADMIN grant it:
--           GRANT CREATE VIRTUAL TABLE ON REMOTE SOURCE <name> TO P2P_DP_USER;
--
-- ============================================================================

-- ============================================================================
-- SCRIPT END
-- ============================================================================
-- Execute this entire script in SAP HANA Database Explorer as DBADMIN user
-- Verify all 20 statements execute successfully before proceeding
-- ============================================================================
