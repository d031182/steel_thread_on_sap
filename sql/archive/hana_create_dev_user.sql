-- ============================================
-- SAP HANA Cloud Development User Setup
-- ============================================
-- Execute this script as DBADMIN user
-- Created: 2026-01-21
-- Project: P2P Procure-to-Pay System
-- ============================================

-- Step 1: Create Development User
-- Replace the password with your own secure password
CREATE USER DEV_USER 
    PASSWORD "ChangeMeNow123!" 
    FORCE_FIRST_PASSWORD_CHANGE;

-- Step 2: Set User Description
ALTER USER DEV_USER COMMENT 'Development User - P2P Procure-to-Pay Project';

-- Step 3: Create Development Role
CREATE ROLE DEV_ROLE;

-- Step 4: Grant System Privileges to Role
GRANT CONNECT TO DEV_ROLE;
GRANT CREATE SCHEMA TO DEV_ROLE;
GRANT IMPORT TO DEV_ROLE;
GRANT EXPORT TO DEV_ROLE;
GRANT CATALOG READ TO DEV_ROLE;
GRANT MONITORING TO DEV_ROLE;

-- Step 5: Assign Role to User
GRANT DEV_ROLE TO DEV_USER;

-- Step 6: Create Development Schema
CREATE SCHEMA DEV_SCHEMA OWNED BY DEV_USER;

-- Step 7: Grant Schema Privileges
-- This grants CREATE TABLE, CREATE VIEW, CREATE PROCEDURE, CREATE FUNCTION, etc.
GRANT ALL PRIVILEGES ON SCHEMA DEV_SCHEMA TO DEV_USER WITH GRANT OPTION;

-- Step 8: Configure Password Policy
ALTER USER DEV_USER PASSWORD LIFETIME 180;
ALTER USER DEV_USER FAILED LOGIN ATTEMPTS LIMIT 5;
ALTER USER DEV_USER PASSWORD LOCK TIME 1440;

-- Step 9: Set Default Schema
ALTER USER DEV_USER SET PARAMETER SCHEMA = 'DEV_SCHEMA';

-- Step 10: Verify User Creation
SELECT 
    USER_NAME,
    CREATOR,
    CREATE_TIME,
    USER_DEACTIVATED,
    PASSWORD_LOCK_TIME
FROM SYS.USERS 
WHERE USER_NAME = 'DEV_USER';

-- Step 11: Verify Granted Privileges
SELECT 
    GRANTEE,
    PRIVILEGE,
    GRANTOR,
    IS_GRANTABLE
FROM SYS.GRANTED_PRIVILEGES
WHERE GRANTEE = 'DEV_USER'
ORDER BY PRIVILEGE;

-- Step 12: Verify Granted Roles
SELECT 
    GRANTEE,
    ROLE_NAME,
    GRANTOR
FROM SYS.GRANTED_ROLES
WHERE GRANTEE = 'DEV_USER';

-- Step 13: Verify Schema Ownership
SELECT 
    SCHEMA_NAME,
    SCHEMA_OWNER,
    CREATE_TIME
FROM SYS.SCHEMAS
WHERE SCHEMA_OWNER = 'DEV_USER';

-- ============================================
-- Setup Complete!
-- ============================================
-- Next Steps:
-- 1. Note down the initial password: ChangeMeNow123!
-- 2. Disconnect from DBADMIN
-- 3. Connect as DEV_USER
-- 4. You will be prompted to change password on first login
-- ============================================
