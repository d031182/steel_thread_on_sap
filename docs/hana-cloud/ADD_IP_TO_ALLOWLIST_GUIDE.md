# Add IP to HANA Cloud Allowlist - Step-by-Step Guide

## Your Information
- **Your IP**: 10.50.122.213
- **HANA Instance**: e7decab9-3e98-41cf-bbf7-d0a8c13d7fb9.hana.prod-eu10.hanacloud.ondemand.com
- **Region**: eu10 (Europe Frankfurt)

---

## Method 1: Via SAP HANA Cloud Central (Recommended - GUI) 🖱️

### Step 1: Access HANA Cloud Central

1. **Open browser** and go to: https://hanacloud.ondemand.com

2. **Login** with your SAP BTP credentials (S-user or P-user)

3. You should see the **HANA Cloud Central** dashboard

### Step 2: Locate Your Instance

1. In the left sidebar, click **"SAP HANA Database"**

2. You should see your instance listed:
   - Name: (your instance name)
   - ID: `e7decab9-3e98-41cf-bbf7-d0a8c13d7fb9`
   - Status: Should be **"RUNNING"** (if stopped, start it first)

### Step 3: Manage Configuration

1. **Click on your instance** to select it

2. Click the **"Actions"** button (top right or in the row)

3. Select **"Manage Configuration"** from the dropdown menu

4. A new panel opens with configuration options

### Step 4: Add IP to Allowlist

1. Scroll down to the **"Connections"** section

2. Find **"Allowed connections"** or **"IP Allowlist"**

3. You'll see a list of currently allowed IPs (might be empty or have some entries)

4. Click **"Add"** or **"+"** button

5. **Enter your IP**: `10.50.122.213`

6. **Optional**: Add a description like "Development Laptop"

7. Click **"Save"** or **"Apply"**

### Step 5: Verify

1. The configuration change takes effect **immediately** (no restart needed)

2. You should see your IP in the allowlist:
   ```
   10.50.122.213  |  Development Laptop  |  Active
   ```

### Step 6: Test Connection

Open PowerShell and test:
```powershell
cd C:\Users\D031182\gitrepo\p2p_mcp\web\current\backend
node test-connection.js
```

**Expected output**:
```
✅ Connected to HANA Cloud!
✅ Query executed successfully!
Results: {
  "CURRENT_USER": "DBADMIN",
  "CURRENT_SCHEMA": "P2P_SCHEMA",
  "CURRENT_TIMESTAMP": "2026-01-22 02:23:30.000"
}
🎉 Connection test PASSED!
```

---

## Method 2: Via BTP Cockpit (Alternative - GUI) 🖱️

### Step 1: Access BTP Cockpit

1. **Open browser**: https://cockpit.eu10.hana.ondemand.com

2. **Login** with your credentials

3. Navigate to your **subaccount**

### Step 2: Open SAP HANA Cloud

1. In the left menu, click **"SAP HANA Cloud"**

2. Click **"Manage SAP HANA Cloud"** button

3. This opens HANA Cloud Central (same as Method 1)

4. Continue with **Method 1, Step 2** above

---

## Method 3: Via BTP CLI (For Automation) 💻

### Prerequisites
```bash
# Check if BTP CLI is installed
btp --version

# Login
btp login
```

### Get Instance Details
```bash
# List HANA Cloud instances
btp list services/instance --subaccount YOUR-SUBACCOUNT-ID

# Get specific instance details
btp get services/instance e7decab9-3e98-41cf-bbf7-d0a8c13d7fb9 \
    --subaccount YOUR-SUBACCOUNT-ID
```

### Update IP Allowlist
```bash
# Update instance configuration with IP allowlist
btp update services/instance e7decab9-3e98-41cf-bbf7-d0a8c13d7fb9 \
    --subaccount YOUR-SUBACCOUNT-ID \
    --parameters '{
        "data": {
            "whitelistIPs": ["10.50.122.213/32"]
        }
    }'
```

**Note**: This might require HANA Cloud admin privileges

---

## Method 4: Allow All IPs (Development Only - NOT for Production) ⚠️

If you want to allow **all IPs** for development purposes:

### Warning
⚠️ **Security Risk**: This allows connections from ANY IP address  
⚠️ **Use only for development/testing**  
⚠️ **Never use in production**

### Steps (via HANA Cloud Central)

1. Go to **Manage Configuration** (Method 1, Steps 1-3)

2. In **"Allowed connections"** section

3. Add: `0.0.0.0/0` (allows all IPv4 addresses)

4. Or: Check **"Allow all IP addresses"** (if available)

5. Click **"Save"**

### When to Use This
- ✅ Development environment
- ✅ Testing from multiple locations
- ✅ Quick prototyping
- ❌ **NEVER in production**

---

## Troubleshooting

### Issue 1: Cannot Find "Manage Configuration"

**Possible Causes**:
- You don't have HANA Cloud admin role
- Instance is stopped
- Wrong subaccount selected

**Solution**:
1. Verify you have **HANA Cloud Administrator** role
2. Check instance status (must be RUNNING)
3. Contact your BTP administrator for access

### Issue 2: Configuration Changes Not Taking Effect

**Try**:
1. Wait 30 seconds and test again
2. Restart your HANA instance (Actions → Restart)
3. Check if configuration was actually saved
4. Verify the IP address format (should be `10.50.122.213` or `10.50.122.213/32`)

### Issue 3: Still Getting "Socket closed by peer"

**Check**:
1. **Instance Status**: Must be "RUNNING"
   ```bash
   # Via BTP CLI
   btp get services/instance YOUR-INSTANCE-ID
   ```

2. **Firewall**: Corporate firewall might block port 443
   ```bash
   # Test connectivity
   Test-NetConnection -ComputerName e7decab9-3e98-41cf-bbf7-d0a8c13d7fb9.hana.prod-eu10.hanacloud.ondemand.com -Port 443
   ```

3. **Credentials**: Verify password is correct
   ```bash
   # Check .env file
   cat web\current\backend\.env
   ```

---

## Alternative: Use hana-cli to Add IP

If you have `hana-cli` installed with proper credentials:

```bash
# The hana-cli might have a command to manage configurations
# Check documentation:
hana-cli help

# Or manage via Cloud Foundry CLI
cf service YOUR-HANA-INSTANCE
```

**Note**: This depends on your `hana-cli` version and configuration

---

## Quick Reference

### Your Details
```
Instance ID: e7decab9-3e98-41cf-bbf7-d0a8c13d7fb9
Instance Host: e7decab9-3e98-41cf-bbf7-d0a8c13d7fb9.hana.prod-eu10.hanacloud.ondemand.com
Your IP: 10.50.122.213
Region: eu10
```

### Access URLs
- **HANA Cloud Central**: https://hanacloud.ondemand.com
- **BTP Cockpit**: https://cockpit.eu10.hana.ondemand.com
- **Account**: Check your SAP BTP account details

### Testing After Changes
```powershell
# Test connection
cd C:\Users\D031182\gitrepo\p2p_mcp\web\current\backend
node test-connection.js

# If successful, start backend
npm start

# Test API
curl http://localhost:3000/api/health
```

---

## Need Help?

If you encounter issues:

1. **Check SAP Help**: https://help.sap.com/docs/hana-cloud
2. **Check BTP Status**: https://status.sap.com
3. **Contact Support**: Open a ticket with SAP support
4. **Ask Admin**: Your BTP administrator can add the IP for you

---

## Summary

**Recommended Method**: Method 1 (HANA Cloud Central GUI)

**Steps**:
1. Go to https://hanacloud.ondemand.com
2. Select your instance
3. Actions → Manage Configuration
4. Add IP: `10.50.122.213`
5. Save
6. Test connection

**Expected Result**: Connection test passes, backend works!

---

**Last Updated**: January 22, 2026, 2:23 AM  
**Status**: Ready to add IP to allowlist
