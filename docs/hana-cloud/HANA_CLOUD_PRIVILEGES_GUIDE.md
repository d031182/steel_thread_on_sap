# SAP HANA Cloud Privileges Guide

## Overview
This guide explains how privileges work in SAP HANA Cloud and addresses the common issue with `CREATE TABLE` and similar privileges.

---

## Important: Schema-Level vs System-Level Privileges

### ❌ Common Mistake
```sql
-- This does NOT work in HANA Cloud:
GRANT CREATE TABLE TO DEV_ROLE;
GRANT CREATE VIEW TO DEV_ROLE;
GRANT CREATE PROCEDURE TO DEV_ROLE;
GRANT CREATE FUNCTION TO DEV_ROLE;
```

**Error:** `invalid privilege name: CREATE TABLE`

### ✅ Correct Approach

In SAP HANA Cloud, object creation privileges are **schema-specific**, not system-wide.

**Option 1: Grant ALL PRIVILEGES on Schema (Recommended)**
```sql
-- Create the schema first
CREATE SCHEMA DEV_SCHEMA;

-- Grant all privileges including CREATE TABLE, VIEW, PROCEDURE, etc.
GRANT ALL PRIVILEGES ON SCHEMA DEV_SCHEMA TO DEV_USER WITH GRANT OPTION;
```

**Option 2: Grant Specific Schema Privileges**
```sql
-- If you need fine-grained control:
GRANT SELECT, INSERT, UPDATE, DELETE ON SCHEMA DEV_SCHEMA TO DEV_USER;
GRANT EXECUTE ON SCHEMA DEV_SCHEMA TO DEV_USER;
GRANT CREATE ANY ON SCHEMA DEV_SCHEMA TO DEV_USER;
```

---

## System-Level Privileges (Valid in HANA Cloud)

These can be granted at the system level:

```sql
-- Connection and Schema Management
GRANT CONNECT TO DEV_USER;
GRANT CREATE SCHEMA TO DEV_USER;

-- Data Import/Export
GRANT IMPORT TO DEV_USER;
GRANT EXPORT TO DEV_USER;

-- Catalog Access
GRANT CATALOG READ TO DEV_USER;

-- Monitoring
GRANT MONITORING TO DEV_USER;

-- Advanced (use with caution)
GRANT BACKUP ADMIN TO DEV_USER;
GRANT USER ADMIN TO DEV_USER;
```

---

## Schema-Level Privileges

Once you have a schema, grant privileges ON that schema:

```sql
-- Full access (recommended for development)
GRANT ALL PRIVILEGES ON SCHEMA MY_SCHEMA TO DEV_USER;

-- Or specific privileges:
GRANT SELECT ON SCHEMA MY_SCHEMA TO DEV_USER;
GRANT INSERT ON SCHEMA MY_SCHEMA TO DEV_USER;
GRANT UPDATE ON SCHEMA MY_SCHEMA TO DEV_USER;
GRANT DELETE ON SCHEMA MY_SCHEMA TO DEV_USER;
GRANT EXECUTE ON SCHEMA MY_SCHEMA TO DEV_USER;
GRANT CREATE ANY ON SCHEMA MY_SCHEMA TO DEV_USER;
GRANT ALTER ON SCHEMA MY_SCHEMA TO DEV_USER;
GRANT DROP ON SCHEMA MY_SCHEMA TO DEV_USER;
```

---

## Understanding "ALL PRIVILEGES ON SCHEMA"

When you grant `ALL PRIVILEGES ON SCHEMA`, it includes:

- ✅ CREATE TABLE
- ✅ CREATE VIEW
- ✅ CREATE PROCEDURE
- ✅ CREATE FUNCTION
- ✅ CREATE SEQUENCE
- ✅ SELECT, INSERT, UPDATE, DELETE
- ✅ EXECUTE
- ✅ ALTER
- ✅ DROP
- ✅ INDEX
- ✅ TRIGGER
- ✅ And more...

---

## Common Privilege Scenarios

### Scenario 1: Full Development Access
```sql
-- User can do everything in their schema
CREATE USER DEV_USER PASSWORD "Pass123!";
CREATE SCHEMA DEV_SCHEMA OWNED BY DEV_USER;
GRANT CONNECT TO DEV_USER;
GRANT ALL PRIVILEGES ON SCHEMA DEV_SCHEMA TO DEV_USER WITH GRANT OPTION;
```

### Scenario 2: Read-Only Access
```sql
-- User can only read data
CREATE USER VIEWER_USER PASSWORD "Pass123!";
GRANT CONNECT TO VIEWER_USER;
GRANT SELECT ON SCHEMA DATA_SCHEMA TO VIEWER_USER;
GRANT EXECUTE ON SCHEMA DATA_SCHEMA TO VIEWER_USER;
```

### Scenario 3: Application User
```sql
-- User can read/write data but not create objects
CREATE USER APP_USER PASSWORD "Pass123!";
GRANT CONNECT TO APP_USER;
GRANT SELECT, INSERT, UPDATE, DELETE ON SCHEMA APP_SCHEMA TO APP_USER;
GRANT EXECUTE ON SCHEMA APP_SCHEMA TO APP_USER;
```

### Scenario 4: Multi-Schema Access
```sql
-- User needs access to multiple schemas
CREATE USER MULTI_USER PASSWORD "Pass123!";
GRANT CONNECT TO MULTI_USER;
GRANT ALL PRIVILEGES ON SCHEMA SCHEMA1 TO MULTI_USER;
GRANT ALL PRIVILEGES ON SCHEMA SCHEMA2 TO MULTI_USER;
GRANT SELECT ON SCHEMA SCHEMA3 TO MULTI_USER;
```

---

## Checking Current Privileges

### Check User's System Privileges
```sql
SELECT PRIVILEGE, IS_GRANTABLE
FROM SYS.GRANTED_PRIVILEGES
WHERE GRANTEE = 'DEV_USER'
  AND OBJECT_TYPE IS NULL
ORDER BY PRIVILEGE;
```

### Check User's Schema Privileges
```sql
SELECT SCHEMA_NAME, PRIVILEGE, IS_GRANTABLE
FROM SYS.GRANTED_PRIVILEGES
WHERE GRANTEE = 'DEV_USER'
  AND OBJECT_TYPE = 'SCHEMA'
ORDER BY SCHEMA_NAME, PRIVILEGE;
```

### Check All Privileges (Including via Roles)
```sql
SELECT PRIVILEGE, OBJECT_TYPE, SCHEMA_NAME, IS_GRANTABLE
FROM SYS.EFFECTIVE_PRIVILEGES
WHERE USER_NAME = 'DEV_USER'
ORDER BY OBJECT_TYPE, SCHEMA_NAME, PRIVILEGE;
```

---

## Role-Based Privilege Management

### Best Practice: Use Roles
```sql
-- Create role
CREATE ROLE DEV_ROLE;

-- Grant system privileges to role
GRANT CONNECT TO DEV_ROLE;
GRANT CREATE SCHEMA TO DEV_ROLE;

-- Create schema and grant privileges to role
CREATE SCHEMA DEV_SCHEMA;
GRANT ALL PRIVILEGES ON SCHEMA DEV_SCHEMA TO DEV_ROLE WITH GRANT OPTION;

-- Assign role to user
CREATE USER DEV_USER PASSWORD "Pass123!";
GRANT DEV_ROLE TO DEV_USER;
```

### Advantages of Roles:
- ✅ Easier to manage multiple users
- ✅ Consistent privilege sets
- ✅ Simpler to audit
- ✅ Can grant/revoke for groups

---

## Troubleshooting Privilege Issues

### Issue 1: "Invalid privilege name: CREATE TABLE"
**Cause:** Trying to grant object-creation privilege at system level

**Solution:** Grant on specific schema
```sql
-- Wrong:
GRANT CREATE TABLE TO DEV_USER;

-- Right:
GRANT ALL PRIVILEGES ON SCHEMA DEV_SCHEMA TO DEV_USER;
```

### Issue 2: "Insufficient privilege"
**Cause:** User doesn't have required privilege

**Solution:** Check and grant missing privilege
```sql
-- Check what user has
SELECT * FROM SYS.GRANTED_PRIVILEGES WHERE GRANTEE = 'DEV_USER';

-- Grant missing privilege
GRANT <PRIVILEGE_NAME> ON SCHEMA <SCHEMA_NAME> TO DEV_USER;
```

### Issue 3: "User cannot create tables"
**Cause:** User has CONNECT but no schema privileges

**Solution:** Grant schema privileges
```sql
GRANT ALL PRIVILEGES ON SCHEMA DEV_SCHEMA TO DEV_USER;
```

### Issue 4: "Cannot access tables in schema"
**Cause:** User needs explicit schema access

**Solution:** Grant SELECT or ALL PRIVILEGES
```sql
GRANT SELECT ON SCHEMA OTHER_SCHEMA TO DEV_USER;
```

---

## HANA Cloud vs HANA On-Premise Differences

| Privilege | HANA On-Premise | HANA Cloud |
|-----------|-----------------|------------|
| CREATE TABLE | System-level | Schema-level only |
| CREATE VIEW | System-level | Schema-level only |
| CREATE PROCEDURE | System-level | Schema-level only |
| CREATE SCHEMA | System-level | System-level |
| CONNECT | System-level | System-level |

**Key Difference:** In HANA Cloud, most object-creation privileges are schema-specific.

---

## Updated Setup Scripts

Both `hana_create_dev_user.sql` and `hana_create_p2p_user.sql` have been corrected to use the proper privilege syntax:

```sql
-- System privileges only
GRANT CONNECT TO DEV_ROLE;
GRANT CREATE SCHEMA TO DEV_ROLE;
GRANT IMPORT TO DEV_ROLE;
GRANT EXPORT TO DEV_ROLE;
GRANT CATALOG READ TO DEV_ROLE;
GRANT MONITORING TO DEV_ROLE;

-- Schema privileges (includes CREATE TABLE, VIEW, etc.)
GRANT ALL PRIVILEGES ON SCHEMA DEV_SCHEMA TO DEV_USER WITH GRANT OPTION;
```

---

## Quick Reference

### Valid System Privileges
```
CONNECT
CREATE SCHEMA
IMPORT
EXPORT
CATALOG READ
MONITORING
BACKUP ADMIN
USER ADMIN
ROLE ADMIN
```

### Schema Privilege Keywords
```
ALL PRIVILEGES
SELECT
INSERT
UPDATE
DELETE
EXECUTE
CREATE ANY
ALTER
DROP
INDEX
TRIGGER
DEBUG
```

### Privilege Syntax
```sql
-- System privilege
GRANT <PRIVILEGE_NAME> TO <USER_OR_ROLE>;

-- Schema privilege
GRANT <PRIVILEGE_NAME> ON SCHEMA <SCHEMA_NAME> TO <USER_OR_ROLE>;

-- With grant option
GRANT <PRIVILEGE_NAME> ON SCHEMA <SCHEMA_NAME> TO <USER_OR_ROLE> WITH GRANT OPTION;
```

---

## Additional Resources

- [SAP HANA Cloud SQL Privileges](https://help.sap.com/docs/HANA_CLOUD_DATABASE/c1d3f60099654ecfb3fe36ac93c121bb/20a3d5d175191014b5a8c01e25f6cc0d.html)
- [Managing Users and Roles](https://help.sap.com/docs/HANA_CLOUD/c1d3f60099654ecfb3fe36ac93c121bb/c511c28a6c6b4d58a5cdaf37eb5b1f3a.html)
- [SQL Privilege Types](https://help.sap.com/docs/HANA_CLOUD_DATABASE/c1d3f60099654ecfb3fe36ac93c121bb/fb0f9b103d6940f28f3479ab7e0e618a.html)

---

**Document Version:** 1.0  
**Last Updated:** 2026-01-21  
**Status:** Scripts corrected for HANA Cloud privilege model
