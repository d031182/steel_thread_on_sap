-- ============================================
-- SAP HANA Cloud Connection Checker
-- Run this FIRST to verify you're connected as DBADMIN
-- ============================================

-- Check who you are currently connected as
SELECT CURRENT_USER AS "Current User",
       SESSION_CONTEXT('APPLICATIONUSER') AS "Application User",
       CURRENT_SCHEMA AS "Current Schema"
FROM DUMMY;

-- Check if you have necessary privileges
SELECT PRIVILEGE, IS_GRANTABLE
FROM SYS.GRANTED_PRIVILEGES
WHERE GRANTEE = CURRENT_USER
AND PRIVILEGE IN ('CREATE SCHEMA', 'USER ADMIN', 'CATALOG READ')
ORDER BY PRIVILEGE;

-- ============================================
-- EXPECTED RESULT if connected as DBADMIN:
-- Current User: DBADMIN
-- 
-- You should see privileges like:
-- - CATALOG READ
-- - CREATE SCHEMA  
-- - USER ADMIN
-- - Many more...
--
-- IF YOU DON'T SEE "DBADMIN", YOU MUST:
-- 1. Disconnect current connection
-- 2. Reconnect as DBADMIN
-- 3. Re-run the user creation script
-- ============================================
