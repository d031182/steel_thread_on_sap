# How to Access SAP HANA Database Explorer

## Overview
SAP HANA Database Explorer (DBX) is the web-based tool for managing and executing SQL on your SAP HANA Cloud database. This guide shows you how to access it and execute the setup scripts.

---

## Method 1: Access via SAP BTP Cockpit (Recommended)

### Step 1: Log in to SAP BTP Cockpit
1. Go to: **https://cockpit.hanatrial.ondemand.com** (for trial accounts)
   - OR your organization's BTP URL (for production)
2. Enter your SAP credentials
3. Click **Log On**

### Step 2: Navigate to Your Subaccount
1. Click on your **Global Account**
2. Select your **Subaccount**
3. Look for the navigation menu on the left

### Step 3: Open SAP HANA Cloud Central
1. In the left menu, click **SAP HANA Cloud**
2. You'll see your HANA Cloud instance listed
3. Click on the **three dots (...)** next to your instance
4. Select **Open in SAP HANA Database Explorer**

### Step 4: Connect as DBADMIN
1. Database Explorer opens in a new tab
2. You may see a connection dialog
3. Enter:
   - **User:** `DBADMIN`
   - **Password:** Your DBADMIN password
4. Click **Connect** or **OK**

---

## Method 2: Direct URL Access

### Step 1: Get Your Database Explorer URL
The URL format is typically:
```
https://hana-cockpit-<region>.hanacloud.ondemand.com/
```

Common regions:
- **US East:** `us10`
- **Europe (Frankfurt):** `eu10`
- **Europe (Netherlands):** `eu20`
- **Asia Pacific (Sydney):** `ap10`

Example: `https://hana-cockpit-eu10.hanacloud.ondemand.com/`

### Step 2: Log In
1. Open the URL in your browser
2. Enter your SAP credentials
3. Select your HANA Cloud instance
4. Connect using DBADMIN credentials

---

## Method 3: Via SAP Business Application Studio

### If you're using SAP BAS:
1. Open SAP Business Application Studio
2. Open the Command Palette (Ctrl+Shift+P / Cmd+Shift+P)
3. Type: **SAP HANA: Open Database Explorer**
4. Select your HANA Cloud instance
5. Enter DBADMIN credentials

---

## Executing the Setup Scripts

### Once You're Connected to Database Explorer:

#### Step 1: Open SQL Console
1. In Database Explorer, locate your database connection on the left
2. Right-click on the database name
3. Select **Open SQL Console**
   - OR click the **SQL** button in the toolbar

#### Step 2: Load the Script
**Option A - Copy & Paste:**
1. Open `hana_create_dev_user.sql` (or `hana_create_p2p_user.sql`) in a text editor
2. Copy ALL the content (Ctrl+A, Ctrl+C)
3. Paste into the SQL Console (Ctrl+V)

**Option B - Open File:**
1. Click **File** → **Open**
2. Navigate to your script location
3. Select `hana_create_dev_user.sql`
4. Click **Open**

#### Step 3: Execute the Script
1. Click the **Execute** button (▶️ Play icon)
   - OR press **F8**
   - OR press **Ctrl+Enter** (Windows/Linux) / **Cmd+Return** (Mac)
2. Wait for execution to complete
3. Review the results in the Results tab

#### Step 4: Verify the Results
Look for:
- ✅ "Statement executed successfully" messages
- ✅ Result sets showing user information
- ❌ Any error messages (red text)

---

## Visual Guide: Where to Find Things

```
SAP BTP Cockpit
├── Your Subaccount
│   └── SAP HANA Cloud
│       └── Your Instance
│           └── [...] → "Open in SAP HANA Database Explorer"
│
SAP HANA Database Explorer
├── Left Panel: Database Connections
│   └── Your HANA DB
│       ├── Right-click → "Open SQL Console"
│       ├── Catalog (Tables, Views, etc.)
│       └── Users, Roles, Schemas
│
├── Top Toolbar
│   ├── SQL Console button
│   ├── Execute button (▶️)
│   └── File operations
│
└── Main Area
    ├── SQL Console (where you write/paste SQL)
    └── Results Panel (shows execution results)
```

---

## Complete Workflow: From Login to First User

### 🎯 Step-by-Step Complete Process:

1. **Access BTP Cockpit**
   ```
   https://cockpit.hanatrial.ondemand.com
   → Log in with your credentials
   ```

2. **Navigate to HANA Cloud**
   ```
   Subaccount → SAP HANA Cloud → Your Instance → [...] → Open DBX
   ```

3. **Connect as DBADMIN**
   ```
   User: DBADMIN
   Password: [Your DBADMIN password]
   ```

4. **Open SQL Console**
   ```
   Right-click database → Open SQL Console
   ```

5. **Load Script**
   ```
   Copy content from hana_create_dev_user.sql
   Paste into SQL Console
   ```

6. **Execute**
   ```
   Press F8 or click Execute button (▶️)
   ```

7. **Verify**
   ```
   Run hana_verify_user_setup.sql
   Check results
   ```

8. **Test New User**
   ```
   Disconnect from DBADMIN
   Connect as DEV_USER
   Change password when prompted
   ```

---

## Troubleshooting Access Issues

### Issue: Cannot Find SAP HANA Cloud in BTP Cockpit
**Solution:**
- Make sure you're in the correct subaccount
- Check if HANA Cloud instance is running (not stopped)
- Verify you have the necessary permissions

### Issue: "Database Explorer" Option Not Available
**Solution:**
- Try accessing directly via URL
- Check if your role includes database access permissions
- Contact your administrator

### Issue: DBADMIN Password Not Working
**Solution:**
- Verify caps lock is off
- Check if you're using the correct password
- Password may have been reset - check with administrator
- Try "Forgot Password" if available

### Issue: Connection Times Out
**Solution:**
- Check your internet connection
- Verify HANA Cloud instance is running
- Check if IP whitelist is configured (for restricted instances)
- Try again after a few minutes

### Issue: "Insufficient Privileges" Error
**Solution:**
- Make sure you're connected as DBADMIN (not another user)
- DBADMIN should have all privileges by default
- Contact administrator if problem persists

---

## Alternative Tools (If Database Explorer Not Available)

### 1. SAP HANA Studio (Desktop Client)
- Download from SAP Software Center
- Install on your local machine
- Connect to HANA Cloud instance
- Execute SQL scripts

### 2. SAP HANA Command Line (hdbsql)
```bash
# Install HANA client
# Connect using command line
hdbsql -n your-host:443 -u DBADMIN -p YourPassword

# Execute script
\i hana_create_dev_user.sql
```

### 3. DBeaver (Third-Party Tool)
- Free database tool
- Supports SAP HANA
- Download from dbeaver.io
- Connect using JDBC driver

---

## Security Reminders

⚠️ **Important Security Notes:**

1. **Always use HTTPS**
   - Never connect over unsecured connections
   - Verify SSL certificate

2. **Protect Credentials**
   - Don't share DBADMIN password
   - Use password manager
   - Change password regularly

3. **Log Out After Use**
   - Close Database Explorer when done
   - Don't leave sessions open
   - Clear browser cache if using shared computer

4. **Monitor Access**
   - Review audit logs regularly
   - Check for unauthorized access
   - Report suspicious activity

---

## Quick Reference Card

### Access URLs
| Environment | URL Pattern |
|-------------|-------------|
| Trial | `https://cockpit.hanatrial.ondemand.com` |
| Production | `https://cockpit.<region>.ondemand.com` |
| DBX | `https://hana-cockpit-<region>.hanacloud.ondemand.com` |

### Keyboard Shortcuts (in SQL Console)
| Action | Windows/Linux | Mac |
|--------|---------------|-----|
| Execute | F8 or Ctrl+Enter | F8 or Cmd+Return |
| New Console | Ctrl+N | Cmd+N |
| Save | Ctrl+S | Cmd+S |
| Format SQL | Ctrl+Shift+F | Cmd+Shift+F |
| Comment Line | Ctrl+/ | Cmd+/ |

### Common SQL Commands
```sql
-- Check current user
SELECT CURRENT_USER FROM DUMMY;

-- List all users
SELECT USER_NAME FROM SYS.USERS;

-- Check user privileges
SELECT * FROM SYS.GRANTED_PRIVILEGES 
WHERE GRANTEE = 'DEV_USER';
```

---

## Next Steps After Accessing Database Explorer

✅ **Checklist:**
- [ ] Successfully logged into Database Explorer
- [ ] Connected as DBADMIN
- [ ] Opened SQL Console
- [ ] Executed hana_create_dev_user.sql (or hana_create_p2p_user.sql)
- [ ] Verified with hana_verify_user_setup.sql
- [ ] Disconnected from DBADMIN
- [ ] Connected as new DEV_USER
- [ ] Changed password on first login
- [ ] Ready to start development!

---

## Additional Resources

- [SAP HANA Database Explorer Documentation](https://help.sap.com/docs/HANA_CLOUD_DATABASE/e2d2b48377c14490b55466b5f1872640/7fa981c8f1b44196b243faeb4afb5793.html)
- [SAP BTP Cockpit Guide](https://help.sap.com/docs/BTP/65de2977205c403bbc107264b8eccf4b/19d7119265564c0e937719b7c920a8b0.html)
- [SAP HANA Cloud Getting Started](https://help.sap.com/docs/HANA_CLOUD)

---

**Document Version:** 1.0  
**Last Updated:** 2026-01-21  
**For:** P2P Procure-to-Pay Project
