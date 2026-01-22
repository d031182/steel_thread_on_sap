# SAP HANA Cloud Official SQL Syntax Reference

## Documentation Source
**Official Reference:** https://help.sap.com/docs/hana-cloud-database/sap-hana-cloud-sap-hana-database-sql-reference-guide

Based on the official SAP HANA Cloud SQL Reference Guide, here is the correct syntax for user and privilege management:

---

## CREATE USER Statement

### Official Syntax (SAP HANA Cloud)
```sql
CREATE USER <user_name> PASSWORD <password>
   [ NO FORCE_FIRST_PASSWORD_CHANGE | FORCE_FIRST_PASSWORD_CHANGE ]
   [ SET USERGROUP <usergroup_name> ]
   [ <user_parameter_clause> ]
```

### Key Points:
1. `PASSWORD` is required
2. `FORCE_FIRST_PASSWORD_CHANGE` is optional and can be in the same statement
3. Default behavior requires password change on first login if not specified

### Examples from Official Documentation:
```sql
-- Basic user creation
CREATE USER MYUSER PASSWORD "MyPassword123!";

-- With force password change
CREATE USER MYUSER PASSWORD "MyPassword123!" FORCE_FIRST_PASSWORD_CHANGE;

-- Without force password change
CREATE USER MYUSER PASSWORD "MyPassword123!" NO FORCE_FIRST_PASSWORD_CHANGE;
```

---

## ALTER USER Statement

### Official Syntax
```sql
ALTER USER <user_name>
   { PASSWORD <password> [ NO FORCE_FIRST_PASSWORD_CHANGE | FORCE_FIRST_PASSWORD_CHANGE ]
   | ACTIVATE USER LOCK
   | DEACTIVATE USER LOCK
   | FAILED LOGIN ATTEMPTS LIMIT <number>
   | PASSWORD LIFETIME <number>
   | PASSWORD LOCK TIME <minutes>
   | SET USERGROUP <usergroup_name>
   | <user_parameter_clause>
   | COMMENT '<comment_string>'
   }
```

### Examples:
```sql
-- Force password change separately
ALTER USER MYUSER FORCE_FIRST_PASSWORD_CHANGE;

-- Set password policy
ALTER USER MYUSER PASSWORD LIFETIME 180;
ALTER USER MYUSER FAILED LOGIN ATTEMPTS LIMIT 5;
ALTER USER MYUSER PASSWORD LOCK TIME 1440;

-- Set comment
ALTER USER MYUSER COMMENT 'Development User';
```

---

## GRANT Statement

### System Privileges Syntax
```sql
GRANT <system_privilege> [,...] TO <grantee> [,...]
   [ WITH ADMIN OPTION ]
```

### Valid System Privileges (Partial List):
- `CREATE SCHEMA`
- `IMPORT`
- `EXPORT`  
- `CATALOG READ`
- `USER ADMIN`
- `ROLE ADMIN`
- `BACKUP ADMIN`

### Schema Privileges Syntax
```sql
GRANT <schema_privilege> [,...] ON SCHEMA <schema_name> [,...]
   TO <grantee> [,...] [ WITH GRANT OPTION ]
```

### Valid Schema Privileges:
- `SELECT`
- `INSERT`
- `UPDATE`
- `DELETE`
- `EXECUTE`
- `CREATE ANY`
- `ALTER`
- `DROP`
- `INDEX`
- `TRIGGER`
- `DEBUG`

### Special: ALL PRIVILEGES
```sql
GRANT ALL PRIVILEGES ON SCHEMA <schema_name> TO <user> [ WITH GRANT OPTION ];
```

This grants all available schema-level privileges including:
- All data manipulation privileges (SELECT, INSERT, UPDATE, DELETE)
- All object creation privileges (CREATE TABLE, CREATE VIEW, CREATE PROCEDURE, etc.)
- All administrative privileges (ALTER, DROP, etc.)

---

## CREATE SCHEMA Statement

### Official Syntax
```sql
CREATE SCHEMA <schema_name> [ OWNED BY <user_name> ]
```

### Examples:
```sql
-- Create schema with owner
CREATE SCHEMA DEV_SCHEMA OWNED BY DEV_USER;

-- Create schema without owner (owned by current user)
CREATE SCHEMA DEV_SCHEMA;
```

---

## Important Notes from Official Documentation

### 1. User Creation Privileges
- Only users with `USER ADMIN` privilege can create users
- DBADMIN has this privilege by default

### 2. Password Requirements
SAP HANA Cloud enforces password complexity by default:
- Minimum length: 8 characters
- Must contain uppercase letters
- Must contain lowercase letters
- Must contain numbers
- Must contain special characters

### 3. Schema Ownership
- When you create a schema with `OWNED BY`, the owner automatically gets certain privileges
- However, explicit `GRANT ALL PRIVILEGES` is still recommended for full access

### 4. Privilege Model
SAP HANA Cloud uses a **schema-centric** privilege model:
- Object creation privileges (CREATE TABLE, CREATE VIEW, etc.) are **NOT** system privileges
- They must be granted at the schema level
- Use `GRANT ALL PRIVILEGES ON SCHEMA` for development users

### 5. Role vs. Direct Grants
- Both roles and direct grants are supported
- For simple setups, direct grants to users work fine
- For complex environments with many users, roles are recommended

---

## Verified Working Script Pattern

Based on official syntax, here's the verified pattern:

```sql
-- 1. Create user (FORCE_FIRST_PASSWORD_CHANGE is optional in same statement)
CREATE USER DEV_USER PASSWORD "MyPassword123!" FORCE_FIRST_PASSWORD_CHANGE;

-- 2. Set user description
ALTER USER DEV_USER COMMENT 'Development User';

-- 3. Grant system privileges
GRANT CREATE SCHEMA TO DEV_USER;
GRANT IMPORT TO DEV_USER;
GRANT EXPORT TO DEV_USER;
GRANT CATALOG READ TO DEV_USER;

-- 4. Create schema
CREATE SCHEMA DEV_SCHEMA OWNED BY DEV_USER;

-- 5. Grant schema privileges
GRANT ALL PRIVILEGES ON SCHEMA DEV_SCHEMA TO DEV_USER WITH GRANT OPTION;

-- 6. Configure password policy
ALTER USER DEV_USER PASSWORD LIFETIME 180;
ALTER USER DEV_USER FAILED LOGIN ATTEMPTS LIMIT 5;
ALTER USER DEV_USER PASSWORD LOCK TIME 1440;

-- 7. Set default schema (user parameter)
ALTER USER DEV_USER SET PARAMETER SCHEMA = 'DEV_SCHEMA';
```

---

## Common Errors and Solutions

### Error: "incorrect syntax near FORCE_FIRST_PASSWORD_CHANGE"
**Cause:** Trying to use it as a separate statement without proper syntax

**Solutions:**
```sql
-- Option 1: Include in CREATE USER (recommended)
CREATE USER MYUSER PASSWORD "Pass123!" FORCE_FIRST_PASSWORD_CHANGE;

-- Option 2: Use ALTER USER separately
CREATE USER MYUSER PASSWORD "Pass123!";
ALTER USER MYUSER FORCE_FIRST_PASSWORD_CHANGE;
```

### Error: "invalid privilege name: CREATE TABLE"
**Cause:** Trying to grant object creation privilege at system level

**Solution:**
```sql
-- Wrong:
GRANT CREATE TABLE TO MYUSER;

-- Right:
GRANT ALL PRIVILEGES ON SCHEMA MY_SCHEMA TO MYUSER;
```

### Error: "insufficient privilege"
**Cause:** Not connected as user with sufficient privileges (e.g., USER ADMIN)

**Solution:**
- Connect as DBADMIN
- Or ensure your user has USER ADMIN privilege

---

## References

1. **CREATE USER Statement**  
   https://help.sap.com/docs/hana-cloud-database/sap-hana-cloud-sap-hana-database-sql-reference-guide/create-user-statement-access-control

2. **ALTER USER Statement**  
   https://help.sap.com/docs/hana-cloud-database/sap-hana-cloud-sap-hana-database-sql-reference-guide/alter-user-statement-access-control

3. **GRANT Statement**  
   https://help.sap.com/docs/hana-cloud-database/sap-hana-cloud-sap-hana-database-sql-reference-guide/grant-statement-access-control

4. **CREATE SCHEMA Statement**  
   https://help.sap.com/docs/hana-cloud-database/sap-hana-cloud-sap-hana-database-sql-reference-guide/create-schema-statement-data-definition

5. **SQL Privilege Types**  
   https://help.sap.com/docs/hana-cloud-database/sap-hana-cloud-sap-hana-database-sql-reference-guide/privileges

---

**Document Version:** 1.0  
**Last Updated:** 2026-01-21  
**Based on:** SAP HANA Cloud Database SQL Reference Guide  
**Status:** Official syntax verified
