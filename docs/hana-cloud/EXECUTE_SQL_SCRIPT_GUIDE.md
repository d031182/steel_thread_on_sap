# How to Execute SQL Scripts in SAP HANA Cloud

**Guide to Running create_p2p_data_product_user.sql**

**Date**: January 22, 2026, 12:15 AM

---

## Option 1: Database Explorer (Recommended) ⭐

### Via hana-cli (Easiest)

**Step 1: Open Database Explorer**
```bash
hana-cli opendbx
```

This will:
- Open your browser to HANA Database Explorer
- Use credentials from `default-env.json`
- Connect automatically

**Step 2: Execute SQL Script**
1. Click "SQL Console" button (or press Ctrl+Alt+C)
2. Open file: `create_p2p_data_product_user.sql`
3. Click "Run" button (or press F8)
4. Review results
5. Run verification queries

**Verification**:
```sql
-- Check user created
SELECT * FROM SYS.USERS WHERE USER_NAME = 'P2P_DP_USER';

-- Check privileges
SELECT * FROM SYS.GRANTED_PRIVILEGES 
WHERE GRANTEE = 'P2P_DP_USER'
ORDER BY PRIVILEGE;
```

---

## Option 2: hana-cli querySimple (For Simple Queries)

**Note**: This works for individual SQL statements, not full scripts with multiple statements.

**Example - Check if user exists**:
```bash
hana-cli querySimple -q "SELECT USER_NAME FROM SYS.USERS WHERE USER_NAME = 'P2P_DP_USER'"
```

**Limitation**: Cannot execute multi-statement scripts like `create_p2p_data_product_user.sql`

---

## Option 3: Install hdbsql (SAP HANA Client)

If you want true CLI-based script execution, install SAP HANA Client.

### Installation Steps

**Download**:
1. Go to: https://tools.hana.ondemand.com/#hanatools
2. Download: SAP HANA Client 2.0 for Windows
3. Extract and install

**Execute Script**:
```bash
hdbsql -n <host>:443 -u DBADMIN -p <password> -ssltruststore -I create_p2p_data_product_user.sql
```

**Your Connection Details**:
```
Host: e7decab9-3e98-41cf-bbf7-d0a8c13d7fb9.hana.prod-eu10.hanacloud.ondemand.com
Port: 443
User: DBADMIN
Password: HANA4vpbdc
```

---

## Recommended Approach

**Use Database Explorer via hana-cli** ⭐

**Why**:
- ✅ Already installed
- ✅ Easy to use (one command)
- ✅ Visual feedback
- ✅ Can see all results
- ✅ Can run verification queries immediately
- ✅ No additional installation needed

**Command**:
```bash
hana-cli opendbx
```

Then copy/paste the entire content of `create_p2p_data_product_user.sql` into the SQL Console.

---

## Step-by-Step Execution

### Complete Workflow

**1. Open Database Explorer**
```bash
cd c:\Users\D031182\gitrepo\p2p_mcp
hana-cli opendbx
```

**2. In Database Explorer**:
- Wait for browser to open
- Database Explorer should load automatically
- You should see your HANA Cloud instance connected

**3. Open SQL Console**:
- Click the SQL Console icon (top toolbar)
- Or use menu: View → SQL Console
- Or keyboard shortcut: Ctrl+Alt+C

**4. Load SQL Script**:
- Click "Open" icon
- Navigate to: `c:\Users\D031182\gitrepo\p2p_mcp\create_p2p_data_product_user.sql`
- Or copy/paste entire script content

**5. Execute**:
- Click "Run" button (green play icon)
- Or press F8
- Script will execute all 20 statements

**6. Review Results**:
- Check "Messages" tab for any errors
- All statements should show "Statement executed successfully"

**7. Run Verification Queries**:
The script includes 4 verification queries at the end:
- Query 1: User created
- Query 2: System privileges (should show 5)
- Query 3: Schema privileges (should show 11)
- Query 4: Schema ownership

---

## Troubleshooting

### Issue: hana-cli opendbx fails

**Error**: "Could not open database explorer"

**Solution**:
```bash
# Check connection first
hana-cli status

# If not connected, check default-env.json
type default-env.json

# Manually open Database Explorer
# URL: https://poc-pd-78nb7vx2.hana-tooling.ingress.orchestration.prod-eu10.hanacloud.ondemand.com/
```

### Issue: Authentication Error

**Error**: "Invalid credentials"

**Solution**:
1. Verify DBADMIN password
2. Update `default-env.json` if needed
3. Try connecting again

### Issue: Permission Denied

**Error**: "Error 258 - insufficient privilege"

**Cause**: Running as wrong user

**Solution**: Ensure you're connected as DBADMIN (not P2P_DEV_USER)

---

## Alternative: Manual Execution via Browser

If `hana-cli opendbx` doesn't work, access Database Explorer directly:

**URL**:
```
https://poc-pd-78nb7vx2.hana-tooling.ingress.orchestration.prod-eu10.hanacloud.ondemand.com/
```

**Login**:
- User: DBADMIN
- Password: HANA4vpbdc

Then follow steps 3-7 above.

---

## Script Content Preview

The script creates:
- User: P2P_DP_USER
- Password: P2P_DataProd123! (must change on first login)
- Schema: P2P_DATA_PRODUCTS
- 5 system privileges
- 11 schema privileges

**Total**: 20 SQL statements

---

## After Execution

**Verify Success**:
```sql
-- 1. Check user
SELECT USER_NAME, CREATOR, CREATE_TIME 
FROM SYS.USERS 
WHERE USER_NAME = 'P2P_DP_USER';

-- 2. Check system privileges  
SELECT PRIVILEGE 
FROM SYS.GRANTED_PRIVILEGES
WHERE GRANTEE = 'P2P_DP_USER'
AND OBJECT_TYPE = 'SYSTEMPRIVILEGE';

-- Expected: CREATE REMOTE SOURCE, CREATE SCHEMA, CATALOG READ, IMPORT, EXPORT

-- 3. Check schema
SELECT SCHEMA_NAME, SCHEMA_OWNER 
FROM SYS.SCHEMAS
WHERE SCHEMA_NAME = 'P2P_DATA_PRODUCTS';

-- Expected: SCHEMA_OWNER = 'P2P_DP_USER'
```

**If All Successful**:
✅ User created
✅ Privileges granted  
✅ Schema created
✅ Ready to install data products!

---

## Next Steps

After successful execution:

1. **Login as P2P_DP_USER**
   - Use Database Explorer
   - Password: P2P_DataProd123!
   - Will be forced to change password

2. **Verify Formation**
   - Login to SAP for Me
   - Check formation includes your HANA Cloud instance

3. **Install Data Products**
   - Follow guide in `DATA_PRODUCT_AUTHORIZATION_GUIDE.md`
   - Browse BDC Catalog
   - Share and install data products

---

**Document Version**: 1.0  
**Status**: Ready to execute  
**Last Updated**: January 22, 2026, 12:15 AM
