-- ============================================
-- SAP HANA Cloud P2P Development User Setup (Final Working Version)
-- ============================================
-- Execute this script as DBADMIN user
-- This creates a P2P-specific development environment
-- Created: 2026-01-21
-- Project: P2P Procure-to-Pay System
-- ============================================

-- Step 1: Create P2P Development User with forced password change
-- Replace the password with your own secure password
-- Per official SAP documentation: FORCE_FIRST_PASSWORD_CHANGE can be included in CREATE USER
CREATE USER P2P_DEV_USER PASSWORD "P2P_Dev123!" FORCE_FIRST_PASSWORD_CHANGE;

-- Step 2: Set User Description
ALTER USER P2P_DEV_USER COMMENT 'P2P Development User - Procure-to-Pay Project';

-- Step 4: Grant System Privileges Directly to User
GRANT CREATE SCHEMA TO P2P_DEV_USER;
GRANT IMPORT TO P2P_DEV_USER;
GRANT EXPORT TO P2P_DEV_USER;
GRANT CATALOG READ TO P2P_DEV_USER;

-- Step 5: Create P2P Schema
CREATE SCHEMA P2P_SCHEMA;

-- Step 6: Grant Full Schema Privileges to User
GRANT ALL PRIVILEGES ON SCHEMA P2P_SCHEMA TO P2P_DEV_USER WITH GRANT OPTION;

-- Step 7: Configure Password Policy
ALTER USER P2P_DEV_USER PASSWORD LIFETIME 180;
ALTER USER P2P_DEV_USER FAILED LOGIN ATTEMPTS LIMIT 5;
ALTER USER P2P_DEV_USER PASSWORD LOCK TIME 1440;

-- Step 8: Set Default Schema
ALTER USER P2P_DEV_USER SET PARAMETER SCHEMA = 'P2P_SCHEMA';

-- Step 9: Create Additional P2P Schemas (Optional)
-- Uncomment if you need separate schemas for different data layers
-- CREATE SCHEMA P2P_DATA_SCHEMA;
-- CREATE SCHEMA P2P_VIEW_SCHEMA;
-- GRANT ALL PRIVILEGES ON SCHEMA P2P_DATA_SCHEMA TO P2P_DEV_USER WITH GRANT OPTION;
-- GRANT ALL PRIVILEGES ON SCHEMA P2P_VIEW_SCHEMA TO P2P_DEV_USER WITH GRANT OPTION;

-- Step 10: Verify User Creation
SELECT 
    USER_NAME,
    CREATOR,
    CREATE_TIME,
    USER_DEACTIVATED
FROM SYS.USERS 
WHERE USER_NAME = 'P2P_DEV_USER';

-- Step 11: Verify Granted Privileges
SELECT 
    GRANTEE,
    PRIVILEGE,
    GRANTOR,
    IS_GRANTABLE,
    OBJECT_TYPE,
    SCHEMA_NAME
FROM SYS.GRANTED_PRIVILEGES
WHERE GRANTEE = 'P2P_DEV_USER'
ORDER BY PRIVILEGE;

-- Step 12: Verify Schema Ownership
SELECT 
    SCHEMA_NAME,
    SCHEMA_OWNER,
    CREATE_TIME
FROM SYS.SCHEMAS
WHERE SCHEMA_NAME LIKE 'P2P%';

-- ============================================
-- Setup Complete!
-- ============================================
-- Next Steps:
-- 1. Note down the initial password: P2P_Dev123!
-- 2. Disconnect from DBADMIN
-- 3. Connect as P2P_DEV_USER
-- 4. You will be prompted to change password on first login
-- 5. Test by creating a table: CREATE TABLE P2P_SCHEMA.TEST_TABLE (ID INT);
-- 6. Start creating P2P database objects in P2P_SCHEMA
-- ============================================
