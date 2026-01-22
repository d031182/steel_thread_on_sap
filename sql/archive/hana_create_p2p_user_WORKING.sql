-- ============================================
-- SAP HANA Cloud P2P Development User Setup
-- VERIFIED WORKING VERSION for SAP Business Data Cloud
-- ============================================
-- Execute this script as DBADMIN user
-- Created: 2026-01-21, 9:24 PM
-- Tested: SAP HANA Cloud in BDC formation
-- ============================================

-- Step 1: Create User (WITHOUT FORCE_FIRST_PASSWORD_CHANGE in same statement)
CREATE USER P2P_DEV_USER PASSWORD "P2P_Dev123!";

-- Step 2: Force password change on first login (SEPARATE statement)
ALTER USER P2P_DEV_USER FORCE FIRST PASSWORD CHANGE;

-- Step 3: Set User Description
ALTER USER P2P_DEV_USER COMMENT 'P2P Development User - Procure-to-Pay Project';

-- Step 4: Grant System Privileges Directly to User
GRANT CREATE SCHEMA TO P2P_DEV_USER;
GRANT IMPORT TO P2P_DEV_USER;
GRANT EXPORT TO P2P_DEV_USER;
GRANT CATALOG READ TO P2P_DEV_USER;

-- Step 5: Create P2P Development Schema
CREATE SCHEMA P2P_SCHEMA OWNED BY P2P_DEV_USER;

-- Step 6: Grant Full Schema Privileges to User
GRANT ALL PRIVILEGES ON SCHEMA P2P_SCHEMA TO P2P_DEV_USER WITH GRANT OPTION;

-- Step 7: Configure Password Policy (Optional but Recommended)
ALTER USER P2P_DEV_USER PASSWORD LIFETIME 180;
ALTER USER P2P_DEV_USER FAILED LOGIN ATTEMPTS LIMIT 5;
ALTER USER P2P_DEV_USER PASSWORD LOCK TIME 1440;

-- Step 8: Set Default Schema
ALTER USER P2P_DEV_USER SET PARAMETER SCHEMA = 'P2P_SCHEMA';

-- ============================================
-- VERIFICATION QUERIES
-- ============================================

-- Verify User Creation
SELECT 
    USER_NAME,
    CREATOR,
    CREATE_TIME,
    USER_DEACTIVATED,
    PASSWORD_CHANGE_TIME_REQUIRED
FROM SYS.USERS 
WHERE USER_NAME = 'P2P_DEV_USER';

-- Verify Granted System Privileges
SELECT 
    GRANTEE,
    PRIVILEGE,
    GRANTOR,
    IS_GRANTABLE
FROM SYS.GRANTED_PRIVILEGES
WHERE GRANTEE = 'P2P_DEV_USER'
AND OBJECT_TYPE IS NULL
ORDER BY PRIVILEGE;

-- Verify Schema Privileges
SELECT 
    GRANTEE,
    PRIVILEGE,
    SCHEMA_NAME,
    IS_GRANTABLE
FROM SYS.GRANTED_PRIVILEGES
WHERE GRANTEE = 'P2P_DEV_USER'
AND SCHEMA_NAME = 'P2P_SCHEMA'
ORDER BY PRIVILEGE;

-- Verify Schema Ownership
SELECT 
    SCHEMA_NAME,
    SCHEMA_OWNER,
    CREATE_TIME
FROM SYS.SCHEMAS
WHERE SCHEMA_NAME = 'P2P_SCHEMA';

-- ============================================
-- Setup Complete!
-- ============================================
-- Expected Results:
-- 1. User P2P_DEV_USER created with PASSWORD_CHANGE_TIME_REQUIRED = TRUE
-- 2. 4 system privileges granted (CREATE SCHEMA, IMPORT, EXPORT, CATALOG READ)
-- 3. 11+ schema privileges granted on P2P_SCHEMA (ALL PRIVILEGES)
-- 4. Schema P2P_SCHEMA owned by P2P_DEV_USER
--
-- Next Steps:
-- 1. Note the password: P2P_Dev123!
-- 2. Disconnect from DBADMIN
-- 3. Connect as P2P_DEV_USER
-- 4. You will be prompted to change password
-- 5. Test: CREATE TABLE P2P_SCHEMA.TEST_TABLE (ID INT);
-- ============================================
