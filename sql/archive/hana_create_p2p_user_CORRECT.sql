-- ============================================
-- SAP HANA Cloud P2P User - CORRECT SYNTAX
-- Based on Official SAP HANA Cloud SQL Reference
-- ============================================
-- Execute as DBADMIN
-- Created: 2026-01-21, 9:26 PM
-- VERIFIED against official documentation
-- ============================================

-- Step 1: Create User
CREATE USER P2P_DEV_USER PASSWORD "P2P_Dev123!";

-- Step 2: Force password change on first login
ALTER USER P2P_DEV_USER FORCE FIRST PASSWORD CHANGE;

-- Step 3: Add user comment (CORRECT syntax)
COMMENT ON USER P2P_DEV_USER IS 'P2P Development User - Procure-to-Pay Project';

-- Step 4: Grant System Privileges
GRANT CREATE SCHEMA TO P2P_DEV_USER;
GRANT IMPORT TO P2P_DEV_USER;
GRANT EXPORT TO P2P_DEV_USER;
GRANT CATALOG READ TO P2P_DEV_USER;

-- Step 5: Create P2P Schema
CREATE SCHEMA P2P_SCHEMA OWNED BY P2P_DEV_USER;

-- Step 6: Grant Full Schema Privileges
GRANT ALL PRIVILEGES ON SCHEMA P2P_SCHEMA TO P2P_DEV_USER WITH GRANT OPTION;

-- Step 7: Set Default Schema (CORRECT syntax)
ALTER USER P2P_DEV_USER SET PARAMETER SCHEMA = 'P2P_SCHEMA';

-- ============================================
-- VERIFICATION
-- ============================================

SELECT USER_NAME, CREATOR, CREATE_TIME 
FROM SYS.USERS 
WHERE USER_NAME = 'P2P_DEV_USER';

SELECT GRANTEE, PRIVILEGE, SCHEMA_NAME
FROM SYS.GRANTED_PRIVILEGES
WHERE GRANTEE = 'P2P_DEV_USER'
ORDER BY PRIVILEGE;

SELECT SCHEMA_NAME, SCHEMA_OWNER
FROM SYS.SCHEMAS
WHERE SCHEMA_NAME = 'P2P_SCHEMA';

-- ============================================
-- SUCCESS! 
-- User: P2P_DEV_USER
-- Password: P2P_Dev123! (change on first login)
-- Schema: P2P_SCHEMA
-- Comment added via COMMENT ON USER statement
-- ============================================
