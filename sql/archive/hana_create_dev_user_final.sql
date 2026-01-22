-- ============================================
-- SAP HANA Cloud Development User Setup (Final Working Version)
-- ============================================
-- Execute this script as DBADMIN user
-- Created: 2026-01-21
-- Project: P2P Procure-to-Pay System
-- ============================================

-- Step 1: Create Development User with forced password change
-- Replace the password with your own secure password
-- Per official SAP documentation: FORCE_FIRST_PASSWORD_CHANGE can be included in CREATE USER
CREATE USER DEV_USER PASSWORD "ChangeMeNow123!" FORCE_FIRST_PASSWORD_CHANGE;

-- Step 2: Set User Description
ALTER USER DEV_USER COMMENT 'Development User - P2P Procure-to-Pay Project';

-- Step 4: Grant System Privileges Directly to User
GRANT CREATE SCHEMA TO DEV_USER;
GRANT IMPORT TO DEV_USER;
GRANT EXPORT TO DEV_USER;
GRANT CATALOG READ TO DEV_USER;

-- Step 5: Create Development Schema
CREATE SCHEMA DEV_SCHEMA OWNED BY DEV_USER;

-- Step 6: Grant Full Schema Privileges to User
GRANT ALL PRIVILEGES ON SCHEMA DEV_SCHEMA TO DEV_USER WITH GRANT OPTION;

-- Step 7: Configure Password Policy
ALTER USER DEV_USER PASSWORD LIFETIME 180;
ALTER USER DEV_USER FAILED LOGIN ATTEMPTS LIMIT 5;
ALTER USER DEV_USER PASSWORD LOCK TIME 1440;

-- Step 8: Set Default Schema
ALTER USER DEV_USER SET PARAMETER SCHEMA = 'DEV_SCHEMA';

-- Step 9: Verify User Creation
SELECT 
    USER_NAME,
    CREATOR,
    CREATE_TIME,
    USER_DEACTIVATED
FROM SYS.USERS 
WHERE USER_NAME = 'DEV_USER';

-- Step 10: Verify Granted Privileges
SELECT 
    GRANTEE,
    PRIVILEGE,
    GRANTOR,
    IS_GRANTABLE,
    OBJECT_TYPE,
    SCHEMA_NAME
FROM SYS.GRANTED_PRIVILEGES
WHERE GRANTEE = 'DEV_USER'
ORDER BY PRIVILEGE;

-- ============================================
-- Setup Complete!
-- ============================================
-- Next Steps:
-- 1. Note down the initial password: ChangeMeNow123!
-- 2. Disconnect from DBADMIN
-- 3. Connect as DEV_USER
-- 4. You will be prompted to change password on first login
-- 5. Test by creating a table: CREATE TABLE DEV_SCHEMA.TEST_TABLE (ID INT);
-- ============================================
