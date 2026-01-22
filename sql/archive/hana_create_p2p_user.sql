-- ============================================
-- SAP HANA Cloud P2P Development User Setup
-- ============================================
-- Execute this script as DBADMIN user
-- This creates a P2P-specific development environment
-- Created: 2026-01-21
-- Project: P2P Procure-to-Pay System
-- ============================================

-- Step 1: Create P2P Development Role
CREATE ROLE P2P_DEV_ROLE;

-- Step 2: Grant System Privileges to P2P Role
GRANT CONNECT TO P2P_DEV_ROLE;
GRANT CREATE SCHEMA TO P2P_DEV_ROLE;
GRANT IMPORT TO P2P_DEV_ROLE;
GRANT EXPORT TO P2P_DEV_ROLE;
GRANT CATALOG READ TO P2P_DEV_ROLE;
GRANT MONITORING TO P2P_DEV_ROLE;

-- Step 3: Create P2P Schema
CREATE SCHEMA P2P_SCHEMA;

-- Step 4: Grant Full Privileges on P2P Schema to Role
-- This grants CREATE TABLE, CREATE VIEW, CREATE PROCEDURE, CREATE FUNCTION, etc.
GRANT ALL PRIVILEGES ON SCHEMA P2P_SCHEMA TO P2P_DEV_ROLE WITH GRANT OPTION;

-- Step 5: Create P2P Development User
-- Replace the password with your own secure password
CREATE USER P2P_DEV_USER 
    PASSWORD "P2P_Dev123!" 
    FORCE_FIRST_PASSWORD_CHANGE;

-- Step 6: Set User Description
ALTER USER P2P_DEV_USER COMMENT 'P2P Development User - Procure-to-Pay Project';

-- Step 7: Assign P2P Role to User
GRANT P2P_DEV_ROLE TO P2P_DEV_USER;

-- Step 8: Configure Password Policy
ALTER USER P2P_DEV_USER PASSWORD LIFETIME 180;
ALTER USER P2P_DEV_USER FAILED LOGIN ATTEMPTS LIMIT 5;
ALTER USER P2P_DEV_USER PASSWORD LOCK TIME 1440;

-- Step 9: Set Default Schema
ALTER USER P2P_DEV_USER SET PARAMETER SCHEMA = 'P2P_SCHEMA';

-- Step 10: Create Additional P2P Schemas (Optional)
-- Uncomment if you need separate schemas for different data layers
-- CREATE SCHEMA P2P_DATA_SCHEMA;
-- CREATE SCHEMA P2P_VIEW_SCHEMA;
-- GRANT ALL PRIVILEGES ON SCHEMA P2P_DATA_SCHEMA TO P2P_DEV_ROLE WITH GRANT OPTION;
-- GRANT ALL PRIVILEGES ON SCHEMA P2P_VIEW_SCHEMA TO P2P_DEV_ROLE WITH GRANT OPTION;

-- Step 11: Verify User Creation
SELECT 
    USER_NAME,
    CREATOR,
    CREATE_TIME,
    USER_DEACTIVATED
FROM SYS.USERS 
WHERE USER_NAME = 'P2P_DEV_USER';

-- Step 12: Verify Granted Privileges
SELECT 
    GRANTEE,
    PRIVILEGE,
    GRANTOR,
    IS_GRANTABLE
FROM SYS.GRANTED_PRIVILEGES
WHERE GRANTEE = 'P2P_DEV_USER'
ORDER BY PRIVILEGE;

-- Step 13: Verify Granted Roles
SELECT 
    GRANTEE,
    ROLE_NAME,
    GRANTOR
FROM SYS.GRANTED_ROLES
WHERE GRANTEE = 'P2P_DEV_USER';

-- Step 14: Verify Schema Ownership
SELECT 
    SCHEMA_NAME,
    SCHEMA_OWNER,
    CREATE_TIME
FROM SYS.SCHEMAS
WHERE SCHEMA_NAME LIKE 'P2P%';

-- Step 15: Verify Role Privileges
SELECT 
    ROLE_NAME,
    PRIVILEGE,
    IS_GRANTABLE
FROM SYS.GRANTED_PRIVILEGES
WHERE GRANTEE = 'P2P_DEV_ROLE'
ORDER BY PRIVILEGE;

-- ============================================
-- Setup Complete!
-- ============================================
-- Next Steps:
-- 1. Note down the initial password: P2P_Dev123!
-- 2. Disconnect from DBADMIN
-- 3. Connect as P2P_DEV_USER
-- 4. You will be prompted to change password on first login
-- 5. Start creating P2P database objects in P2P_SCHEMA
-- ============================================
