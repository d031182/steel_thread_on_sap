-- ============================================
-- Find All Installed Data Products
-- Purpose: Discover data product schemas for grant script customization
-- Execute as: DBADMIN
-- ============================================

-- ============================================
-- STEP 1: LIST ALL DATA PRODUCT SCHEMAS
-- ============================================

SELECT 
    '=== INSTALLED DATA PRODUCTS ===' AS INFO,
    SCHEMA_NAME,
    SCHEMA_OWNER,
    CREATE_TIME
FROM SYS.SCHEMAS
WHERE SCHEMA_NAME LIKE '_SAP_DATAPRODUCT%'
ORDER BY CREATE_TIME DESC;

-- ============================================
-- STEP 2: EXTRACT SCHEMA NAMES FOR GRANT SCRIPT
-- ============================================

-- Copy these schema names and paste into create_hana_dp_user_for_team.sql
SELECT 
    '=== COPY THESE FOR GRANT SCRIPT ===' AS INFO,
    'GRANT SELECT ON SCHEMA "' || SCHEMA_NAME || '" TO HANA_DP_USER;' AS GRANT_STATEMENT
FROM SYS.SCHEMAS
WHERE SCHEMA_NAME LIKE '_SAP_DATAPRODUCT%'
ORDER BY SCHEMA_NAME;

-- ============================================
-- STEP 3: IDENTIFY DATA PRODUCTS BY NAME
-- ============================================

SELECT 
    '=== DATA PRODUCT DETAILS ===' AS INFO,
    SCHEMA_NAME,
    CASE 
        WHEN SCHEMA_NAME LIKE '%Supplier%' THEN 'Supplier'
        WHEN SCHEMA_NAME LIKE '%PurchaseOrder%' THEN 'Purchase Order'
        WHEN SCHEMA_NAME LIKE '%SupplierInvoice%' THEN 'Supplier Invoice'
        WHEN SCHEMA_NAME LIKE '%ServiceEntrySheet%' THEN 'Service Entry Sheet'
        WHEN SCHEMA_NAME LIKE '%PaymentTerms%' THEN 'Payment Terms'
        WHEN SCHEMA_NAME LIKE '%JournalEntry%' THEN 'Journal Entry'
        WHEN SCHEMA_NAME LIKE '%Customer%' THEN 'Customer'
        WHEN SCHEMA_NAME LIKE '%SalesOrder%' THEN 'Sales Order'
        WHEN SCHEMA_NAME LIKE '%CostCenter%' THEN 'Cost Center'
        WHEN SCHEMA_NAME LIKE '%GLAccount%' THEN 'GL Account'
        ELSE 'Unknown'
    END AS PRODUCT_NAME,
    SCHEMA_OWNER,
    CREATE_TIME
FROM SYS.SCHEMAS
WHERE SCHEMA_NAME LIKE '_SAP_DATAPRODUCT%'
ORDER BY PRODUCT_NAME, CREATE_TIME DESC;

-- ============================================
-- STEP 4: COUNT TABLES PER DATA PRODUCT
-- ============================================

SELECT 
    '=== TABLES PER DATA PRODUCT ===' AS INFO,
    SCHEMA_NAME,
    COUNT(*) AS TABLE_COUNT
FROM SYS.TABLES
WHERE SCHEMA_NAME LIKE '_SAP_DATAPRODUCT%'
GROUP BY SCHEMA_NAME
ORDER BY TABLE_COUNT DESC, SCHEMA_NAME;

-- ============================================
-- STEP 5: SAMPLE TABLE NAMES
-- ============================================

-- See what tables exist in each data product
SELECT 
    '=== SAMPLE TABLES IN EACH DATA PRODUCT ===' AS INFO,
    SCHEMA_NAME,
    TABLE_NAME,
    RECORD_COUNT
FROM SYS.TABLES
WHERE SCHEMA_NAME LIKE '_SAP_DATAPRODUCT%'
ORDER BY SCHEMA_NAME, TABLE_NAME
LIMIT 50;

-- ============================================
-- INSTRUCTIONS
-- ============================================

SELECT '
NEXT STEPS:
1. Copy GRANT statements from STEP 2 output
2. Paste into create_hana_dp_user_for_team.sql (replace placeholders)
3. Update password in create_hana_dp_user_for_team.sql
4. Execute create_hana_dp_user_for_team.sql as DBADMIN
5. Test connection as HANA_DP_USER
' AS INSTRUCTIONS FROM DUMMY;