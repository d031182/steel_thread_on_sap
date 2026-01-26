-- ============================================
-- Create Generic Data Product User for Team
-- User: HANA_DP_USER
-- Purpose: Team-shared user for viewing and consuming data products
-- Execute as: DBADMIN in Database Explorer
-- ============================================

-- ============================================
-- STEP 1: CREATE USER
-- ============================================

-- Create user with strong password
CREATE USER HANA_DP_USER PASSWORD "YourSecurePassword123!" NO FORCE_FIRST_PASSWORD_CHANGE;

-- Set password policy
ALTER USER HANA_DP_USER DISABLE PASSWORD LIFETIME;

SELECT 'User HANA_DP_USER created successfully' AS STATUS FROM DUMMY;

-- ============================================
-- STEP 2: GRANT BASIC PRIVILEGES
-- ============================================

-- Essential catalog access
GRANT CATALOG READ TO HANA_DP_USER;

-- Allow user to connect
GRANT CONNECT TO HANA_DP_USER;

-- Allow user to create own schemas (optional - for temporary work)
GRANT CREATE SCHEMA TO HANA_DP_USER;

SELECT 'Basic privileges granted' AS STATUS FROM DUMMY;

-- ============================================
-- STEP 3: GRANT DATA PRODUCT VIEWER ROLES
-- ============================================

-- Try to grant BTP-managed roles (may not exist in pure HANA)
BEGIN
    DECLARE EXIT HANDLER FOR SQLEXCEPTION
        SELECT 'Role not available - will use schema grants instead' AS STATUS FROM DUMMY;
    
    -- Data Publisher Viewer role
    EXEC 'GRANT "SAP HANA Cloud Data Publisher Viewer" TO HANA_DP_USER';
    SELECT 'Granted: Data Publisher Viewer role' AS STATUS FROM DUMMY;
END;

BEGIN
    DECLARE EXIT HANDLER FOR SQLEXCEPTION
        SELECT 'Role not available - will use schema grants instead' AS STATUS FROM DUMMY;
    
    -- Cloud Viewer role
    EXEC 'GRANT "SAP HANA Cloud Viewer" TO HANA_DP_USER';
    SELECT 'Granted: Cloud Viewer role' AS STATUS FROM DUMMY;
END;

-- ============================================
-- STEP 4: GRANT ACCESS TO DATA PRODUCT SCHEMAS
-- ============================================

-- IMPORTANT: You need to customize this section based on
-- which data products are installed in your HANA Cloud instance.
-- 
-- To find installed data products, run:
-- SELECT SCHEMA_NAME FROM SYS.SCHEMAS 
-- WHERE SCHEMA_NAME LIKE '_SAP_DATAPRODUCT%';

-- Example grants for common P2P data products:

-- Supplier Data Product
BEGIN
    DECLARE EXIT HANDLER FOR SQLEXCEPTION
        SELECT 'Supplier data product not installed' AS STATUS FROM DUMMY;
    
    EXEC 'GRANT SELECT ON SCHEMA "_SAP_DATAPRODUCT_sap_s4com_dataProduct_Supplier_v1_c8f5c255-6ddd-444a-8f90-01baa10b87d3" TO HANA_DP_USER';
    SELECT 'Granted: Supplier data product access' AS STATUS FROM DUMMY;
END;

-- Purchase Order Data Product
BEGIN
    DECLARE EXIT HANDLER FOR SQLEXCEPTION
        SELECT 'PurchaseOrder data product not installed' AS STATUS FROM DUMMY;
    
    EXEC 'GRANT SELECT ON SCHEMA "_SAP_DATAPRODUCT_sap_s4com_dataProduct_PurchaseOrder_v1_..." TO HANA_DP_USER';
    SELECT 'Granted: PurchaseOrder data product access' AS STATUS FROM DUMMY;
END;

-- Supplier Invoice Data Product
BEGIN
    DECLARE EXIT HANDLER FOR SQLEXCEPTION
        SELECT 'SupplierInvoice data product not installed' AS STATUS FROM DUMMY;
    
    EXEC 'GRANT SELECT ON SCHEMA "_SAP_DATAPRODUCT_sap_s4com_dataProduct_SupplierInvoice_v1_..." TO HANA_DP_USER';
    SELECT 'Granted: SupplierInvoice data product access' AS STATUS FROM DUMMY;
END;

-- Service Entry Sheet Data Product
BEGIN
    DECLARE EXIT HANDLER FOR SQLEXCEPTION
        SELECT 'ServiceEntrySheet data product not installed' AS STATUS FROM DUMMY;
    
    EXEC 'GRANT SELECT ON SCHEMA "_SAP_DATAPRODUCT_sap_s4com_dataProduct_ServiceEntrySheet_v1_..." TO HANA_DP_USER';
    SELECT 'Granted: ServiceEntrySheet data product access' AS STATUS FROM DUMMY;
END;

-- Payment Terms Data Product
BEGIN
    DECLARE EXIT HANDLER FOR SQLEXCEPTION
        SELECT 'PaymentTerms data product not installed' AS STATUS FROM DUMMY;
    
    EXEC 'GRANT SELECT ON SCHEMA "_SAP_DATAPRODUCT_sap_s4com_dataProduct_PaymentTerms_v1_..." TO HANA_DP_USER';
    SELECT 'Granted: PaymentTerms data product access' AS STATUS FROM DUMMY;
END;

-- Journal Entry Data Product
BEGIN
    DECLARE EXIT HANDLER FOR SQLEXCEPTION
        SELECT 'JournalEntryHeader data product not installed' AS STATUS FROM DUMMY;
    
    EXEC 'GRANT SELECT ON SCHEMA "_SAP_DATAPRODUCT_sap_s4com_dataProduct_JournalEntryHeader_v1_..." TO HANA_DP_USER';
    SELECT 'Granted: JournalEntryHeader data product access' AS STATUS FROM DUMMY;
END;

SELECT 'Schema-level grants attempted (customize based on installed products)' AS STATUS FROM DUMMY;

-- ============================================
-- STEP 5: VERIFY ALL GRANTS
-- ============================================

-- Check roles granted
SELECT 
    'Roles Granted to HANA_DP_USER' AS SECTION,
    ROLE_NAME,
    GRANTOR,
    IS_GRANTABLE
FROM SYS.GRANTED_ROLES 
WHERE GRANTEE = 'HANA_DP_USER'
ORDER BY ROLE_NAME;

-- Check system privileges
SELECT 
    'System Privileges' AS SECTION,
    PRIVILEGE,
    GRANTEE,
    GRANTOR,
    IS_GRANTABLE
FROM SYS.GRANTED_PRIVILEGES 
WHERE GRANTEE = 'HANA_DP_USER'
  AND OBJECT_TYPE = 'SYSTEMPRIVILEGE'
ORDER BY PRIVILEGE;

-- Check schema privileges
SELECT 
    'Schema Privileges' AS SECTION,
    SCHEMA_NAME,
    PRIVILEGE,
    GRANTEE,
    GRANTOR
FROM SYS.GRANTED_PRIVILEGES 
WHERE GRANTEE = 'HANA_DP_USER'
  AND OBJECT_TYPE = 'SCHEMA'
  AND SCHEMA_NAME LIKE '_SAP_DATAPRODUCT%'
ORDER BY SCHEMA_NAME, PRIVILEGE;

-- ============================================
-- STEP 6: CONNECTION INFO
-- ============================================

SELECT 
    'Connection Information for HANA_DP_USER' AS SECTION,
    CURRENT_USER AS USERNAME,
    CURRENT_SCHEMA AS DEFAULT_SCHEMA,
    SESSION_CONTEXT('APPLICATIONUSER') AS APPLICATION_USER
FROM DUMMY;

-- ============================================
-- SUCCESS SUMMARY
-- ============================================

SELECT '✅ HANA_DP_USER setup complete!' AS STATUS FROM DUMMY;
SELECT 'Next: Test access by connecting as HANA_DP_USER' AS NEXT_STEP FROM DUMMY;
SELECT 'Run: SELECT SCHEMA_NAME FROM SYS.SCHEMAS WHERE SCHEMA_NAME LIKE ''_SAP_DATAPRODUCT%'';' AS TEST_QUERY FROM DUMMY;