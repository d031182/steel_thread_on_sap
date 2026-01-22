# SAP HANA Cloud - First Development User Setup Guide

## Overview
When you have a DBADMIN user in SAP HANA Cloud, the first critical step is to create a dedicated development user. This follows security best practices by:
- Separating administrative and development activities
- Implementing principle of least privilege
- Enabling proper audit trails
- Preventing accidental administrative operations

## Prerequisites
- Access to SAP HANA Cloud instance
- DBADMIN user credentials
- SAP HANA Database Explorer or SQL Console access

## Step-by-Step Guide

### Step 1: Connect as DBADMIN
1. Open SAP HANA Database Explorer (DBX) or SAP HANA Cockpit
2. Connect to your HANA Cloud database using DBADMIN credentials
3. Open SQL Console

### Step 2: Create the Development User

```sql
-- Create a new development user
CREATE USER DEV_USER PASSWORD "InitialPassword123!" NO FORCE_FIRST_PASSWORD_CHANGE;

-- Alternative: Force password change on first login (recommended)
CREATE USER DEV_USER PASSWORD "InitialPassword123!" FORCE_FIRST_PASSWORD_CHANGE;
```

**Password Requirements:**
- Minimum 8 characters
- At least one uppercase letter
- At least one lowercase letter  
- At least one number
- At least one special character

### Step 3: Grant Essential System Privileges

```sql
-- Grant basic connection and development privileges
GRANT CONNECT TO DEV_USER;
GRANT CREATE SCHEMA TO DEV_USER;
GRANT IMPORT TO DEV_USER;
GRANT EXPORT TO DEV_USER;

-- Grant catalog read privileges for development
GRANT CATALOG READ TO DEV_USER;

-- Optional: Grant monitoring privileges (useful for debugging)
GRANT MONITORING TO DEV_USER;
```

### Step 4: Create a Development Schema

```sql
-- Create a dedicated schema for the development user
CREATE SCHEMA DEV_SCHEMA OWNED BY DEV_USER;

-- Grant necessary privileges on the schema
GRANT ALL PRIVILEGES ON SCHEMA DEV_SCHEMA TO DEV_USER WITH GRANT OPTION;
```

### Step 5: Grant Object-Level Privileges (if needed)

```sql
-- If the user needs to access existing schemas/tables
-- Example: Grant SELECT on specific schema
GRANT SELECT ON SCHEMA EXISTING_SCHEMA TO DEV_USER;

-- Grant specific privileges on tables
GRANT SELECT, INSERT, UPDATE, DELETE ON EXISTING_SCHEMA.TABLE_NAME TO DEV_USER;
```

### Step 6: Configure Development Roles (Recommended Approach)

```sql
-- Create a development role with standard privileges
CREATE ROLE DEV_ROLE;

-- Grant privileges to the role
GRANT CREATE SCHEMA TO DEV_ROLE;
GRANT IMPORT TO DEV_ROLE;
GRANT EXPORT TO DEV_ROLE;
GRANT CATALOG READ TO DEV_ROLE;
GRANT MONITORING TO DEV_ROLE;

-- Assign the role to the user
GRANT DEV_ROLE TO DEV_USER;
```

### Step 7: Set User Parameters (Optional)

```sql
-- Set session timeout (in seconds, e.g., 3600 = 1 hour)
ALTER USER DEV_USER SET PARAMETER CLIENT = '100';

-- Set default schema
ALTER USER DEV_USER SET PARAMETER SCHEMA = 'DEV_SCHEMA';

-- Set user description
ALTER USER DEV_USER COMMENT 'Development User for P2P Project';
```

### Step 8: Configure Password Policy

```sql
-- Set password lifetime (days)
ALTER USER DEV_USER PASSWORD LIFETIME 180;

-- Set minimum password length
ALTER USER DEV_USER PASSWORD LOCK TIME 1440; -- Lock for 24 hours after failed attempts

-- Configure failed login attempts
ALTER USER DEV_USER FAILED LOGIN ATTEMPTS LIMIT 5;
```

## Complete Setup Script

Here's a complete script you can execute:

```sql
-- ============================================
-- SAP HANA Cloud Development User Setup
-- ============================================

-- 1. Create Development User
CREATE USER DEV_USER 
    PASSWORD "ChangeMeNow123!" 
    FORCE_FIRST_PASSWORD_CHANGE;

-- 2. Set User Description
ALTER USER DEV_USER COMMENT 'Development User - P2P Procure-to-Pay Project';

-- 3. Create Development Role
CREATE ROLE DEV_ROLE;

-- 4. Grant System Privileges to Role
GRANT CONNECT TO DEV_ROLE;
GRANT CREATE SCHEMA TO DEV_ROLE;
GRANT IMPORT TO DEV_ROLE;
GRANT EXPORT TO DEV_ROLE;
GRANT CATALOG READ TO DEV_ROLE;
GRANT MONITORING TO DEV_ROLE;

-- 5. Assign Role to User
GRANT DEV_ROLE TO DEV_USER;

-- 6. Create Development Schema
CREATE SCHEMA DEV_SCHEMA OWNED BY DEV_USER;

-- 7. Grant Schema Privileges
GRANT ALL PRIVILEGES ON SCHEMA DEV_SCHEMA TO DEV_USER WITH GRANT OPTION;

-- 8. Configure Password Policy
ALTER USER DEV_USER PASSWORD LIFETIME 180;
ALTER USER DEV_USER FAILED LOGIN ATTEMPTS LIMIT 5;
ALTER USER DEV_USER PASSWORD LOCK TIME 1440;

-- 9. Set Default Schema
ALTER USER DEV_USER SET PARAMETER SCHEMA = 'DEV_SCHEMA';

-- 10. Verify User Creation
SELECT USER_NAME, CREATOR, CREATE_TIME, USER_DEACTIVATED 
FROM SYS.USERS 
WHERE USER_NAME = 'DEV_USER';
```

## Verification Steps

### 1. Verify User Creation
```sql
SELECT 
    USER_NAME,
    CREATOR,
    CREATE_TIME,
    USER_DEACTIVATED,
    PASSWORD_LOCK_TIME,
    PASSWORD_CHANGE_TIME
FROM SYS.USERS 
WHERE USER_NAME = 'DEV_USER';
```

### 2. Check Granted Privileges
```sql
SELECT 
    GRANTEE,
    PRIVILEGE,
    GRANTOR,
    IS_GRANTABLE
FROM SYS.GRANTED_PRIVILEGES
WHERE GRANTEE = 'DEV_USER'
ORDER BY PRIVILEGE;
```

### 3. Check Granted Roles
```sql
SELECT 
    GRANTEE,
    ROLE_NAME,
    GRANTOR
FROM SYS.GRANTED_ROLES
WHERE GRANTEE = 'DEV_USER';
```

### 4. Check Schema Ownership
```sql
SELECT 
    SCHEMA_NAME,
    SCHEMA_OWNER,
    CREATE_TIME
FROM SYS.SCHEMAS
WHERE SCHEMA_OWNER = 'DEV_USER';
```

## Best Practices

### 1. **Use Roles Instead of Direct Privileges**
- Create roles for different access levels
- Grant roles to users instead of individual privileges
- Makes privilege management easier

### 2. **Implement Naming Conventions**
- Use prefixes: `DEV_`, `TEST_`, `PROD_`
- Schema naming: `<USER>_SCHEMA` or `<PROJECT>_SCHEMA`
- Role naming: `<PROJECT>_<LEVEL>_ROLE`

### 3. **Separate Development Schemas**
- Each developer should have their own schema
- Project schemas should be separate from user schemas
- Use schema-level security

### 4. **Password Management**
- Force password change on first login
- Set appropriate password lifetime
- Configure failed login attempt limits

### 5. **Audit Configuration**
```sql
-- Enable audit trail for the user
CREATE AUDIT POLICY DEV_USER_AUDIT
    AUDITING SUCCESSFUL DDL, FAILED DDL
    LEVEL CRITICAL;
    
ALTER AUDIT POLICY DEV_USER_AUDIT FOR USER DEV_USER;
```

## Common Development Privileges by Use Case

### Data Modeler
```sql
CREATE ROLE DATA_MODELER_ROLE;
GRANT CREATE SCHEMA TO DATA_MODELER_ROLE;
GRANT CREATE TABLE TO DATA_MODELER_ROLE;
GRANT CREATE VIEW TO DATA_MODELER_ROLE;
GRANT CREATE PROCEDURE TO DATA_MODELER_ROLE;
GRANT CREATE FUNCTION TO DATA_MODELER_ROLE;
```

### Report Developer
```sql
CREATE ROLE REPORT_DEV_ROLE;
GRANT CREATE CALCULATION VIEW TO REPORT_DEV_ROLE;
GRANT CREATE ANALYTIC VIEW TO REPORT_DEV_ROLE;
GRANT SELECT ON SCHEMA DATA_SCHEMA TO REPORT_DEV_ROLE;
```

### Application Developer
```sql
CREATE ROLE APP_DEV_ROLE;
GRANT CREATE SCHEMA TO APP_DEV_ROLE;
GRANT CREATE TABLE TO APP_DEV_ROLE;
GRANT CREATE PROCEDURE TO APP_DEV_ROLE;
GRANT CREATE FUNCTION TO APP_DEV_ROLE;
GRANT IMPORT TO APP_DEV_ROLE;
GRANT EXPORT TO APP_DEV_ROLE;
```

## Project-Specific Setup (P2P Example)

```sql
-- Create P2P Development Role
CREATE ROLE P2P_DEV_ROLE;

-- Grant necessary privileges
GRANT CREATE SCHEMA TO P2P_DEV_ROLE;
GRANT CREATE TABLE TO P2P_DEV_ROLE;
GRANT CREATE VIEW TO P2P_DEV_ROLE;
GRANT CREATE PROCEDURE TO P2P_DEV_ROLE;
GRANT IMPORT TO P2P_DEV_ROLE;
GRANT EXPORT TO P2P_DEV_ROLE;

-- Create P2P Schema
CREATE SCHEMA P2P_SCHEMA;

-- Grant privileges on P2P Schema
GRANT ALL PRIVILEGES ON SCHEMA P2P_SCHEMA TO P2P_DEV_ROLE WITH GRANT OPTION;

-- Create P2P Development User
CREATE USER P2P_DEV_USER PASSWORD "P2P_Dev123!" FORCE_FIRST_PASSWORD_CHANGE;

-- Assign role to user
GRANT P2P_DEV_ROLE TO P2P_DEV_USER;

-- Set default schema
ALTER USER P2P_DEV_USER SET PARAMETER SCHEMA = 'P2P_SCHEMA';
```

## Troubleshooting

### Issue: User Cannot Connect
```sql
-- Check if user is locked
SELECT USER_NAME, USER_DEACTIVATED, PASSWORD_LOCK_TIME
FROM SYS.USERS
WHERE USER_NAME = 'DEV_USER';

-- Unlock user
ALTER USER DEV_USER DEACTIVATE USER LOCK;
```

### Issue: Insufficient Privileges
```sql
-- Check current privileges
SELECT PRIVILEGE FROM SYS.GRANTED_PRIVILEGES WHERE GRANTEE = 'DEV_USER';

-- Grant missing privilege
GRANT <PRIVILEGE_NAME> TO DEV_USER;
```

### Issue: Schema Access Denied
```sql
-- Check schema privileges
SELECT * FROM SYS.GRANTED_PRIVILEGES
WHERE GRANTEE = 'DEV_USER' 
AND OBJECT_TYPE = 'SCHEMA';

-- Grant schema access
GRANT SELECT ON SCHEMA <SCHEMA_NAME> TO DEV_USER;
```

## Security Considerations

1. **Never use DBADMIN for development**
2. **Implement password complexity requirements**
3. **Enable audit logging for sensitive operations**
4. **Regularly review and revoke unused privileges**
5. **Use SSL/TLS for connections**
6. **Implement IP whitelisting if possible**
7. **Set up proper backup and recovery procedures**

## Next Steps

After creating the development user:

1. **Test the Connection**
   - Disconnect from DBADMIN
   - Connect as the new DEV_USER
   - Verify access to assigned schemas

2. **Create Initial Database Objects**
   - Tables
   - Views
   - Procedures
   - Functions

3. **Set Up Development Tools**
   - Configure SAP Business Application Studio
   - Set up SAP HANA Database Explorer
   - Configure VS Code with HANA extensions

4. **Implement Version Control**
   - Use git for database artifacts
   - Implement CI/CD for database deployments

## Additional Resources

- [SAP HANA Cloud Security Guide](https://help.sap.com/docs/hana-cloud/sap-hana-cloud-security-guide)
- [SAP HANA SQL Reference](https://help.sap.com/docs/hana-cloud-database/sap-hana-cloud-sap-hana-database-sql-reference-guide)
- [SAP HANA Cloud Administration Guide](https://help.sap.com/docs/hana-cloud/sap-hana-cloud-administration-guide)

---

**Document Version:** 1.0  
**Last Updated:** 2026-01-21  
**Author:** Development Team  
**Project:** P2P Procure-to-Pay System
