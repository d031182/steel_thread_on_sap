-- ============================================================================
-- Grant CSN Table Access to P2P_DP_USER (Run as SYSTEM user)
-- ============================================================================
-- Purpose: Grant privileges that DBADMIN cannot grant (system schema access)
-- User: SYSTEM (only SYSTEM can grant on _SAP_* schemas)
-- Date: 2026-01-24
-- 
-- IMPORTANT: These grants must be run as SYSTEM user because they involve
-- system schemas that DBADMIN doesn't own.
-- ============================================================================

-- ⭐ THE KEY GRANT - CSN Table Access for CSN Viewer Feature
GRANT SELECT ON "_SAP_DB_ACCESS_DATA_PRODUCT_GATEWAY"."_SAP_DATAPRODUCT_DELTA_CSN" 
TO P2P_DP_USER;

-- Gateway Schema Access
GRANT SELECT ON SCHEMA "_SAP_DB_ACCESS_DATA_PRODUCT_GATEWAY" TO P2P_DP_USER;

-- Gateway Metadata Tables
GRANT SELECT ON "_SAP_DB_ACCESS_DATA_PRODUCT_GATEWAY"."_SAP_DATAPRODUCT_DATA_PRODUCT_REMOTE_SOURCES" 
TO P2P_DP_USER;

GRANT SELECT ON "_SAP_DB_ACCESS_DATA_PRODUCT_GATEWAY"."_SAP_DATAPRODUCT_DATA_PRODUCT_VERSIONS" 
TO P2P_DP_USER;

-- Data Product Schemas (PurchaseOrder)
GRANT SELECT ON SCHEMA "_SAP_DATAPRODUCT_sap_s4com_dataProduct_PurchaseOrder_v1_uuid" 
TO P2P_DP_USER;

-- Data Product Schemas (SalesOrder)
GRANT SELECT ON SCHEMA "_SAP_DATAPRODUCT_sap_s4com_dataProduct_SalesOrder_v1_uuid" 
TO P2P_DP_USER;

-- User's Own Schema (P2P_DATA_PRODUCTS)
GRANT SELECT ON SCHEMA P2P_DATA_PRODUCTS TO P2P_DP_USER;
GRANT CREATE ANY ON SCHEMA P2P_DATA_PRODUCTS TO P2P_DP_USER;
GRANT INSERT ON SCHEMA P2P_DATA_PRODUCTS TO P2P_DP_USER;
GRANT UPDATE ON SCHEMA P2P_DATA_PRODUCTS TO P2P_DP_USER;
GRANT DELETE ON SCHEMA P2P_DATA_PRODUCTS TO P2P_DP_USER;
GRANT DROP ON SCHEMA P2P_DATA_PRODUCTS TO P2P_DP_USER;

-- ============================================================================
-- VERIFICATION QUERIES (Run these to test)
-- ============================================================================

-- Query 1: Verify privileges granted
SELECT GRANTEE, PRIVILEGE, SCHEMA_NAME, OBJECT_NAME
FROM SYS.GRANTED_PRIVILEGES
WHERE GRANTEE = 'P2P_DP_USER'
AND OBJECT_TYPE IN ('TABLE', 'SCHEMA')
ORDER BY SCHEMA_NAME, OBJECT_NAME, PRIVILEGE;

-- Query 2: Test CSN table access ⭐
SELECT REMOTE_SOURCE_NAME, 
       LEFT(CSN_JSON, 100) as CSN_PREVIEW
FROM "_SAP_DB_ACCESS_DATA_PRODUCT_GATEWAY"."_SAP_DATAPRODUCT_DELTA_CSN";

-- Expected: Should return CSN data without Error 258!

-- ============================================================================
-- SCRIPT END
-- ============================================================================
-- Run this script in HANA Database Explorer as SYSTEM user
-- Total: 12 GRANT statements + 2 verification queries
-- ============================================================================