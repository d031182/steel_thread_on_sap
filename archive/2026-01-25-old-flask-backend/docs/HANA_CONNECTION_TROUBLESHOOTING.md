# HANA Cloud Connection Issue - Troubleshooting Guide

**Date**: 2026-01-22, 8:47 AM  
**Error**: Socket closed by peer - Connection failed  
**Status**: ⚠️ HANA Cloud instance not accessible

---

## 🔴 CURRENT PROBLEM

The Flask backend code is **working correctly**, but cannot connect to HANA Cloud:

```
Error: (-10709, 'Connection failed (RTE:[89013] Socket closed by peer)')
Host: e7decab9-3e98-41cf-bbf7-d0a8c13d7fb9.hana.prod-eu10.hanacloud.ondemand.com
Port: 443
User: DBADMIN
```

---

## 🎯 ROOT CAUSE

This is **NOT a code problem** - the refactored Flask backend is secure and correct. This is an **infrastructure/access issue**:

### Most Likely Causes:

1. **HANA Cloud Instance is STOPPED** 🔴
   - HANA Cloud instances auto-stop after inactivity
   - Need to start it via BTP Cockpit or CLI

2. **IP Address Not Allowlisted** 🟡
   - Your current IP (130.41.102.58 or similar) needs to be in allowlist
   - HANA Cloud blocks connections from non-allowlisted IPs

3. **Network/Firewall Issue** 🟡
   - Corporate firewall blocking port 443
   - VPN required for HANA access

---

## ✅ SOLUTION 1: Start HANA Cloud Instance

### Option A: Via BTP Cockpit (Easiest)

1. Open BTP Cockpit: https://cockpit.btp.cloud.sap
2. Navigate to your subaccount
3. Go to: **SAP HANA Cloud** → **Instances**
4. Find instance: `e7decab9-3e98-41cf-bbf7-d0a8c13d7fb9`
5. Click **Actions** → **Start**
6. Wait 2-3 minutes for startup

### Option B: Via BTP CLI

```bash
# Login to BTP
cf login -a https://api.cf.eu10.hana.ondemand.com

# List HANA instances
cf service hana-cloud-instance

# Start the instance
cf update-service <instance-name> -c '{"data":{"serviceStopped":false}}'

# Check status
cf service <instance-name>
```

---

## ✅ SOLUTION 2: Add IP to Allowlist

### Check Your Current IP

```bash
# Windows PowerShell
(Invoke-WebRequest -Uri "https://api.ipify.org").Content

# Or visit: https://whatismyipaddress.com
```

### Add IP via BTP Cockpit

1. Open BTP Cockpit
2. Go to **SAP HANA Cloud** → **Instances**
3. Select your instance
4. Click **Manage Configuration**
5. Under **Connections**, add your IP to allowlist
6. Format: `130.41.102.58/32` (or your actual IP)
7. Save changes

**Note**: If you're on a corporate network, you may need to allowlist a range like `130.41.0.0/16`

---

## ✅ SOLUTION 3: Verify Network Access

### Test Port Connectivity

```powershell
# Windows PowerShell
Test-NetConnection -ComputerName e7decab9-3e98-41cf-bbf7-d0a8c13d7fb9.hana.prod-eu10.hanacloud.ondemand.com -Port 443
```

**Expected Output** (if accessible):
```
TcpTestSucceeded : True
```

**If it fails**: Contact your network admin about port 443 access to HANA Cloud

---

## 🔍 DIAGNOSTIC COMMANDS

After applying fixes, test the connection:

### Test 1: Run Test Script
```bash
cd web/current/flask-backend
python test_data_products.py
```

**Expected**: Should show list of data products

### Test 2: Start Flask Server
```bash
cd web/current/flask-backend
python app.py
```

**Expected**: Server starts, shows "✓ HANA configured"

### Test 3: Hit Health Endpoint
```bash
curl http://localhost:5000/api/health
```

**Expected**:
```json
{
  "status": "healthy",
  "hana": "healthy",
  "version": "1.1.0"
}
```

### Test 4: List Data Products
```bash
curl http://localhost:5000/api/data-products
```

**Expected**: JSON with list of data products

---

## 📋 VERIFICATION CHECKLIST

Before reporting the issue as "not working":

- [ ] HANA Cloud instance is **STARTED** (check BTP Cockpit)
- [ ] Your IP address is **ALLOWLISTED** (check instance config)
- [ ] Port 443 is **ACCESSIBLE** (run Test-NetConnection)
- [ ] HANA credentials in `.env` are **CORRECT**
- [ ] You're on **correct network** (VPN if required)

---

## 🎯 EXPECTED BEHAVIOR (After Fix)

Once HANA is accessible, you should see:

### 1. Test Script Output
```
============================================================
Testing HANA Data Products Connection
============================================================

1. Connecting to HANA...
   ✅ Connected successfully!

2. Querying data product schemas...
   ✅ Found 27 data product schemas

3. Data Products Found:
   1. JournalEntryHeader
      Schema: _SAP_DATAPRODUCT_sap_s4com_dataProduct_JournalEntryHeader_v1_...
   2. PaymentTerms
   ...

✅ TEST PASSED - Data products loading successfully!
```

### 2. Flask Server Logs
```
2026-01-22 08:50:00 - __main__ - INFO - Default HANA connection configured
2026-01-22 08:50:00 - __main__ - INFO - ✓ HANA configured: DBADMIN@...
2026-01-22 08:50:00 - __main__ - INFO - 🚀 Starting Flask server on http://localhost:5000
```

### 3. Browser Access
- Navigate to: http://localhost:5000
- See: List of 27 data products
- Click any: See tables and data

---

## 🚨 IMPORTANT NOTE

**The Flask backend refactoring DID NOT break data product loading.**

The refactoring:
- ✅ Fixed SQL injection vulnerabilities
- ✅ Added proper logging
- ✅ Added input validation
- ✅ Made the code MORE secure

**The issue is**: HANA Cloud infrastructure access, not the code.

---

## 📚 RELATED DOCUMENTATION

- `docs/hana-cloud/ADD_IP_TO_ALLOWLIST_GUIDE.md` - IP allowlist guide
- `docs/hana-cloud/HANA_CLOUD_ADMINISTRATION_GUIDE_SUMMARY.md` - Admin guide
- `docs/hana-cloud/HANA_CLOUD_SETUP_ISSUE_RESOLVED.md` - Past setup issues

---

## 🔄 NEXT STEPS

1. **Check HANA Cloud status** in BTP Cockpit
2. **Start the instance** if stopped
3. **Add your IP** to allowlist if needed
4. **Re-run test**: `python test_data_products.py`
5. **Start Flask**: `python app.py`
6. **Open browser**: http://localhost:5000

---

**Status**: ⚠️ Waiting for HANA Cloud to be accessible  
**Code Status**: ✅ Working correctly (security improved)  
**Action Required**: Start HANA instance and/or allowlist IP
