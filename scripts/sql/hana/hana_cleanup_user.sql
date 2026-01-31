-- ============================================
-- SAP HANA Cloud User Cleanup/Rollback Script
-- ============================================
-- Execute this script as DBADMIN user
-- WARNING: This will remove the development users and all their data!
-- Created: 2026-01-21
-- ============================================

-- IMPORTANT: Uncomment the sections you want to execute
-- Do NOT run this entire script blindly!

-- ============================================
-- Option 1: Remove Generic Development User
-- ============================================

-- Step 1: Revoke all privileges from DEV_USER (optional, CASCADE will handle this)
-- REVOKE ALL PRIVILEGES FROM DEV_USER;

-- Step 2: Drop the user (CASCADE removes all dependent objects)
-- DROP USER DEV_USER CASCADE;

-- Step 3: Drop the development schema
-- DROP SCHEMA DEV_SCHEMA CASCADE;

-- Step 4: Drop the development role
-- DROP ROLE DEV_ROLE;

-- ============================================
-- Option 2: Remove P2P Development User
-- ============================================

-- Step 1: Drop the P2P user (CASCADE removes all dependent objects)
-- DROP USER P2P_DEV_USER CASCADE;

-- Step 2: Drop the P2P schema
-- DROP SCHEMA P2P_SCHEMA CASCADE;

-- Step 3: Drop additional P2P schemas if created
-- DROP SCHEMA P2P_DATA_SCHEMA CASCADE;
-- DROP SCHEMA P2P_VIEW_SCHEMA CASCADE;

-- Step 4: Drop the P2P role
-- DROP ROLE P2P_DEV_ROLE;

-- ============================================
-- Option 3: Safe Deactivation (without deletion)
-- ============================================

-- Deactivate DEV_USER without deleting
-- ALTER USER DEV_USER ACTIVATE USER LOCK;

-- Deactivate P2P_DEV_USER without deleting
-- ALTER USER P2P_DEV_USER ACTIVATE USER LOCK;

-- ============================================
-- Option 4: Reactivate Locked Users
-- ============================================

-- Reactivate DEV_USER
-- ALTER USER DEV_USER DEACTIVATE USER LOCK;

-- Reactivate P2P_DEV_USER
-- ALTER USER P2P_DEV_USER DEACTIVATE USER LOCK;

-- ============================================
-- Option 5: Reset User Password
-- ============================================

-- Reset DEV_USER password
-- ALTER USER DEV_USER PASSWORD "NewPassword123!" FORCE_FIRST_PASSWORD_CHANGE;

-- Reset P2P_DEV_USER password
-- ALTER USER P2P_DEV_USER PASSWORD "NewPassword123!" FORCE_FIRST_PASSWORD_CHANGE;

-- ============================================
-- Option 6: Remove All (Complete Cleanup)
-- ============================================
-- Uncomment ALL lines below to remove everything

-- DROP USER DEV_USER CASCADE;
-- DROP USER P2P_DEV_USER CASCADE;
-- DROP SCHEMA DEV_SCHEMA CASCADE;
-- DROP SCHEMA P2P_SCHEMA CASCADE;
-- DROP ROLE DEV_ROLE;
-- DROP ROLE P2P_DEV_ROLE;

-- ============================================
-- Verification After Cleanup
-- ============================================

-- Check if users still exist
SELECT USER_NAME FROM SYS.USERS 
WHERE USER_NAME IN ('DEV_USER', 'P2P_DEV_USER');

-- Check if schemas still exist
SELECT SCHEMA_NAME FROM SYS.SCHEMAS 
WHERE SCHEMA_NAME IN ('DEV_SCHEMA', 'P2P_SCHEMA');

-- Check if roles still exist
SELECT ROLE_NAME FROM SYS.ROLES 
WHERE ROLE_NAME IN ('DEV_ROLE', 'P2P_DEV_ROLE');

-- ============================================
-- Cleanup Complete!
-- ============================================
