# SAP HANA Cloud SQL Scripts - Quick Reference

## Overview
This directory contains SQL scripts for setting up and managing development users in SAP HANA Cloud.

## Available Scripts

### 1. `hana_create_dev_user.sql`
**Purpose:** Create a generic development user with basic privileges

**What it creates:**
- User: `DEV_USER`
- Role: `DEV_ROLE`
- Schema: `DEV_SCHEMA`

**Initial Password:** `ChangeMeNow123!`

**Usage:**
1. Open SAP HANA Database Explorer
2. Connect as DBADMIN
3. Open SQL Console
4. Load and execute this script
5. Change password on first login

---

### 2. `hana_create_p2p_user.sql`
**Purpose:** Create a P2P project-specific development user

**What it creates:**
- User: `P2P_DEV_USER`
- Role: `P2P_DEV_ROLE`
- Schema: `P2P_SCHEMA`

**Initial Password:** `P2P_Dev123!`

**Additional Features:**
- Optimized for P2P project
- Includes CREATE SEQUENCE privilege
- Option to create multiple schemas

**Usage:**
1. Open SAP HANA Database Explorer
2. Connect as DBADMIN
3. Open SQL Console
4. Load and execute this script
5. Change password on first login

---

### 3. `hana_verify_user_setup.sql`
**Purpose:** Verify that user setup was successful

**What it checks:**
- User existence and status
- Granted privileges
- Granted roles
- Schema ownership
- Password policies
- User parameters

**Usage:**
1. Execute after running setup scripts
2. Review output to confirm all objects created correctly
3. Check for any missing privileges

**Expected Results:**
- Users should exist and not be deactivated
- Roles should be granted to users
- Schemas should be owned by users
- Password policies should be configured

---

### 4. `hana_cleanup_user.sql`
**Purpose:** Remove or deactivate development users

**⚠️ WARNING:** This script can delete users and all their data!

**Options Available:**
- Remove generic development user
- Remove P2P development user
- Deactivate users (without deletion)
- Reactivate locked users
- Reset user passwords
- Complete cleanup (remove everything)

**Usage:**
1. **READ THE SCRIPT CAREFULLY**
2. Uncomment only the sections you want to execute
3. Execute selectively

---

## Quick Start Guide

### For First-Time Setup:

1. **Choose your script:**
   - Use `hana_create_dev_user.sql` for general development
   - Use `hana_create_p2p_user.sql` for P2P project

2. **Execute the script:**
   ```sql
   -- Open SAP HANA Database Explorer
   -- Connect as DBADMIN
   -- Load the chosen script
   -- Execute (press F8 or click Execute)
   ```

3. **Verify the setup:**
   ```sql
   -- Load hana_verify_user_setup.sql
   -- Execute to verify all objects created
   ```

4. **Test the connection:**
   - Disconnect from DBADMIN
   - Connect as new user (DEV_USER or P2P_DEV_USER)
   - Change password when prompted

---

## Execution Flow

```
┌─────────────────────────────┐
│  1. Connect as DBADMIN      │
└──────────┬──────────────────┘
           │
           ▼
┌─────────────────────────────┐
│  2. Choose & Execute:       │
│     - hana_create_dev_user  │
│       OR                    │
│     - hana_create_p2p_user  │
└──────────┬──────────────────┘
           │
           ▼
┌─────────────────────────────┐
│  3. Execute:                │
│     - hana_verify_user      │
└──────────┬──────────────────┘
           │
           ▼
┌─────────────────────────────┐
│  4. Test Connection as      │
│     New Dev User            │
└──────────┬──────────────────┘
           │
           ▼
┌─────────────────────────────┐
│  5. Change Password         │
└─────────────────────────────┘
```

---

## Password Requirements

All passwords must meet these criteria:
- Minimum 8 characters
- At least one uppercase letter (A-Z)
- At least one lowercase letter (a-z)
- At least one number (0-9)
- At least one special character (!@#$%^&*)

**Default Passwords:**
- DEV_USER: `ChangeMeNow123!`
- P2P_DEV_USER: `P2P_Dev123!`

**⚠️ IMPORTANT:** These must be changed on first login!

---

## Common Tasks

### Task 1: Create a New Development User
```sql
-- Run: hana_create_dev_user.sql
-- Or: hana_create_p2p_user.sql
```

### Task 2: Verify Setup
```sql
-- Run: hana_verify_user_setup.sql
```

### Task 3: Check User Privileges
```sql
SELECT PRIVILEGE 
FROM SYS.GRANTED_PRIVILEGES 
WHERE GRANTEE = 'DEV_USER';
```

### Task 4: Grant Additional Privilege
```sql
-- Connect as DBADMIN
GRANT <PRIVILEGE_NAME> TO DEV_USER;
```

### Task 5: Reset Password
```sql
-- Connect as DBADMIN
ALTER USER DEV_USER 
PASSWORD "NewPassword123!" 
FORCE_FIRST_PASSWORD_CHANGE;
```

### Task 6: Lock/Unlock User
```sql
-- Lock user
ALTER USER DEV_USER ACTIVATE USER LOCK;

-- Unlock user
ALTER USER DEV_USER DEACTIVATE USER LOCK;
```

---

## Troubleshooting

### Issue: "User already exists"
**Solution:** User was already created. Options:
1. Drop existing user: `DROP USER DEV_USER CASCADE;`
2. Use a different username in the script

### Issue: "Insufficient privileges"
**Solution:** Make sure you're connected as DBADMIN

### Issue: "Schema already exists"
**Solution:** Drop existing schema: `DROP SCHEMA DEV_SCHEMA CASCADE;`

### Issue: "Cannot connect as new user"
**Possible Causes:**
1. User is locked - run: `ALTER USER DEV_USER DEACTIVATE USER LOCK;`
2. Wrong password - reset password using DBADMIN
3. Connection parameters incorrect - verify host/port

### Issue: "Password does not meet requirements"
**Solution:** Ensure password has:
- 8+ characters
- Upper and lowercase letters
- Numbers
- Special characters

---

## Security Best Practices

1. **Never use DBADMIN for development**
   - Always create dedicated users
   - Separate administrative from development tasks

2. **Use strong passwords**
   - Change default passwords immediately
   - Use password manager
   - Don't share passwords

3. **Implement least privilege**
   - Grant only necessary privileges
   - Use roles instead of direct privileges
   - Review privileges regularly

4. **Enable auditing**
   - Monitor user activities
   - Log sensitive operations
   - Review audit logs regularly

5. **Separate environments**
   - Development schema separate from production
   - Different users for different environments
   - Test changes in dev before production

---

## Script Customization

### To change usernames:
Find and replace throughout the scripts:
- `DEV_USER` → Your desired username
- `DEV_SCHEMA` → Your desired schema name
- `DEV_ROLE` → Your desired role name

### To change passwords:
Locate the CREATE USER statements:
```sql
CREATE USER DEV_USER 
    PASSWORD "YourNewPassword123!" 
    FORCE_FIRST_PASSWORD_CHANGE;
```

### To add more privileges:
Add GRANT statements after role creation:
```sql
GRANT YOUR_PRIVILEGE TO DEV_ROLE;
```

---

## Additional Resources

- [HANA Cloud First User Setup Guide](HANA_CLOUD_FIRST_USER_SETUP.md)
- [SAP HANA Cloud Security Guide](https://help.sap.com/docs/hana-cloud/sap-hana-cloud-security-guide)
- [SAP HANA SQL Reference](https://help.sap.com/docs/hana-cloud-database/sap-hana-cloud-sap-hana-database-sql-reference-guide)

---

## Script Summary Table

| Script | Purpose | Executes As | Creates Objects | Modifies System |
|--------|---------|-------------|-----------------|-----------------|
| hana_create_dev_user.sql | Setup generic dev user | DBADMIN | Yes (3) | Yes |
| hana_create_p2p_user.sql | Setup P2P dev user | DBADMIN | Yes (3) | Yes |
| hana_verify_user_setup.sql | Verify setup | DBADMIN | No | No |
| hana_cleanup_user.sql | Remove users | DBADMIN | No | Yes |

---

**Document Version:** 1.0  
**Last Updated:** 2026-01-21  
**Author:** Development Team  
**Project:** P2P Procure-to-Pay System
