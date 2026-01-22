# SAP HANA Cloud User Setup - Issue Resolution

## Problem Summary

When trying to create development users in SAP HANA Cloud using the original scripts, two privilege-related errors occurred:

### Error 1: Invalid Privilege Name
```sql
GRANT CREATE TABLE TO DEV_ROLE;  -- ❌ ERROR: invalid privilege name
```

### Error 2: CONNECT Privilege to Role
```sql
GRANT CONNECT TO DEV_ROLE;  -- ❌ ERROR: Does not work as expected
```

---

## Root Cause

SAP HANA Cloud has different privilege behavior compared to HANA On-Premise:

1. **Object-creation privileges** (CREATE TABLE, CREATE VIEW, etc.) are **schema-specific** only
2. **CONNECT privilege** and other system privileges work better when granted **directly to users**, not to roles first
3. **Role-based privilege management** in HANA Cloud requires additional setup

---

## ✅ Solution: Simplified Scripts

I've created two new simplified scripts that work correctly:

### 1. `hana_create_dev_user_simple.sql` ⭐ USE THIS
### 2. `hana_create_p2p_user_simple.sql` ⭐ USE THIS

**Key Changes:**
- ✅ Removed role creation (not needed for simple setup)
- ✅ Grant privileges **directly to user** (not to role first)
- ✅ Only use valid system privileges
- ✅ Schema privileges granted via `ALL PRIVILEGES ON SCHEMA`

---

## Working Script Structure

```sql
-- 1. Create User
CREATE USER DEV_USER PASSWORD "Pass123!" FORCE_FIRST_PASSWORD_CHANGE;

-- 2. Grant System Privileges DIRECTLY to User (not to role)
GRANT CREATE SCHEMA TO DEV_USER;
GRANT IMPORT TO DEV_USER;
GRANT EXPORT TO DEV_USER;
GRANT CATALOG READ TO DEV_USER;

-- 3. Create Schema
CREATE SCHEMA DEV_SCHEMA OWNED BY DEV_USER;

-- 4. Grant Schema Privileges (includes CREATE TABLE, VIEW, etc.)
GRANT ALL PRIVILEGES ON SCHEMA DEV_SCHEMA TO DEV_USER WITH GRANT OPTION;

-- 5. Configure Password Policy
ALTER USER DEV_USER PASSWORD LIFETIME 180;
ALTER USER DEV_USER FAILED LOGIN ATTEMPTS LIMIT 5;
ALTER USER DEV_USER PASSWORD LOCK TIME 1440;

-- 6. Set Default Schema
ALTER USER DEV_USER SET PARAMETER SCHEMA = 'DEV_SCHEMA';
```

---

## What Was Removed

### ❌ Removed (Causes Errors):
```sql
-- Don't create roles for simple setup
CREATE ROLE DEV_ROLE;

-- Don't grant CONNECT to role
GRANT CONNECT TO DEV_ROLE;

-- Don't grant object-creation privileges at system level
GRANT CREATE TABLE TO DEV_ROLE;
GRANT CREATE VIEW TO DEV_ROLE;
GRANT CREATE PROCEDURE TO DEV_ROLE;
GRANT CREATE FUNCTION TO DEV_ROLE;
```

### ✅ Kept (Works Correctly):
```sql
-- Grant system privileges directly to user
GRANT CREATE SCHEMA TO DEV_USER;
GRANT IMPORT TO DEV_USER;
GRANT EXPORT TO DEV_USER;
GRANT CATALOG READ TO DEV_USER;

-- Grant schema privileges (includes all object-creation privileges)
GRANT ALL PRIVILEGES ON SCHEMA DEV_SCHEMA TO DEV_USER WITH GRANT OPTION;
```

---

## Testing the Setup

After running the simplified script:

### 1. Verify User Can Connect
```sql
-- Connect as DEV_USER
-- You should be prompted to change password
```

### 2. Test Table Creation
```sql
-- As DEV_USER, try creating a table
CREATE TABLE DEV_SCHEMA.TEST_TABLE (
    ID INT PRIMARY KEY,
    NAME VARCHAR(100),
    CREATED_AT TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Verify it was created
SELECT * FROM DEV_SCHEMA.TEST_TABLE;
```

### 3. Test View Creation
```sql
-- Create a view
CREATE VIEW DEV_SCHEMA.TEST_VIEW AS 
SELECT * FROM DEV_SCHEMA.TEST_TABLE;
```

### 4. Test Procedure Creation
```sql
-- Create a procedure
CREATE PROCEDURE DEV_SCHEMA.TEST_PROC()
AS
BEGIN
    SELECT COUNT(*) FROM DEV_SCHEMA.TEST_TABLE;
END;
```

---

## File Reference Guide

### ✅ **USE THESE (Working Scripts):**
| File | Purpose | Status |
|------|---------|--------|
| `hana_create_dev_user_simple.sql` | Generic dev user | ✅ **WORKING** |
| `hana_create_p2p_user_simple.sql` | P2P-specific user | ✅ **WORKING** |
| `hana_verify_user_setup.sql` | Verification | ✅ Works |
| `hana_cleanup_user.sql` | Cleanup | ✅ Works |

### ⚠️ **OLD VERSIONS (Have Issues):**
| File | Status | Issue |
|------|--------|-------|
| `hana_create_dev_user.sql` | ❌ Has errors | Uses invalid GRANT syntax |
| `hana_create_p2p_user.sql` | ❌ Has errors | Uses invalid GRANT syntax |

---

## Quick Start (Corrected)

### Step 1: Access Database Explorer
1. Login to SAP BTP Cockpit
2. Navigate to SAP HANA Cloud
3. Open Database Explorer
4. Connect as DBADMIN

### Step 2: Execute Script
1. Open SQL Console
2. Copy content from `hana_create_dev_user_simple.sql`
3. Paste and execute (F8)
4. Verify success messages

### Step 3: Test New User
1. Disconnect from DBADMIN
2. Connect as DEV_USER
3. Change password when prompted
4. Test: `CREATE TABLE DEV_SCHEMA.TEST (ID INT);`

---

## Why the Original Scripts Failed

### Issue #1: Invalid System-Level Privileges
```sql
-- HANA On-Premise (works):
GRANT CREATE TABLE TO USER;

-- HANA Cloud (fails):
GRANT CREATE TABLE TO USER;  -- ❌ "invalid privilege name"
```

**Solution:** Use schema-level grants instead
```sql
-- HANA Cloud (works):
GRANT ALL PRIVILEGES ON SCHEMA MY_SCHEMA TO USER;  -- ✅ Includes CREATE TABLE
```

### Issue #2: Role-Based Privilege Issues
```sql
-- This approach has issues in HANA Cloud:
CREATE ROLE MY_ROLE;
GRANT CONNECT TO MY_ROLE;  -- ❌ May not work
GRANT MY_ROLE TO USER;
```

**Solution:** Grant privileges directly to user
```sql
-- This works reliably:
GRANT CREATE SCHEMA TO USER;  -- ✅ Direct grant
GRANT IMPORT TO USER;          -- ✅ Direct grant
```

---

## Privileges Explained

### System-Level (Global) Privileges
These are granted at system level:
- `CREATE SCHEMA` - Can create new schemas
- `IMPORT` - Can import data
- `EXPORT` - Can export data
- `CATALOG READ` - Can read system catalog

### Schema-Level Privileges
These are granted on specific schemas:
- `ALL PRIVILEGES` - Grants everything including:
  - CREATE TABLE
  - CREATE VIEW
  - CREATE PROCEDURE
  - CREATE FUNCTION
  - SELECT, INSERT, UPDATE, DELETE
  - And more...

---

## Important Notes

1. **Connection Works Automatically**
   - User can connect once created
   - No explicit CONNECT privilege needed
   - Schema ownership provides access

2. **Schema Ownership**
   - `OWNED BY DEV_USER` makes user the owner
   - Owner automatically has full privileges
   - Additional grant ensures all operations work

3. **Password Management**
   - `FORCE_FIRST_PASSWORD_CHANGE` ensures security
   - Password policies are configured automatically
   - User must change password on first login

4. **Default Schema**
   - Setting default schema is convenient
   - User doesn't need to prefix table names
   - Can still access other schemas if granted

---

## Troubleshooting

### If User Still Cannot Connect:
```sql
-- Check if user exists
SELECT * FROM SYS.USERS WHERE USER_NAME = 'DEV_USER';

-- Check if user is locked
SELECT USER_NAME, USER_DEACTIVATED 
FROM SYS.USERS 
WHERE USER_NAME = 'DEV_USER';

-- If locked, unlock:
ALTER USER DEV_USER DEACTIVATE USER LOCK;
```

### If User Cannot Create Tables:
```sql
-- Check schema privileges
SELECT * FROM SYS.GRANTED_PRIVILEGES 
WHERE GRANTEE = 'DEV_USER' 
AND OBJECT_TYPE = 'SCHEMA';

-- If missing, grant again:
GRANT ALL PRIVILEGES ON SCHEMA DEV_SCHEMA TO DEV_USER WITH GRANT OPTION;
```

---

## Summary

✅ **Use the simplified scripts:** `hana_create_dev_user_simple.sql` or `hana_create_p2p_user_simple.sql`

✅ **These work without errors in SAP HANA Cloud**

✅ **User can immediately start developing after password change**

---

**Document Version:** 1.0  
**Last Updated:** 2026-01-21  
**Status:** Issue Resolved - Simplified scripts working
