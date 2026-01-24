# SYSTEM Password Reset Guide for BDC-Provisioned HANA Cloud

**Created**: 2026-01-24
**Purpose**: Document how to reset SYSTEM user password in BDC-provisioned HANA Cloud instances

---

## 🎯 The Challenge

BDC-provisioned HANA Cloud instances are managed differently than BTP-deployed instances:
- No direct access via BTP Cockpit
- No Cloud Foundry CLI commands work
- DBADMIN cannot reset SYSTEM password (Error 258)

---

## 🔍 Methods to Reset SYSTEM Password

### **Method 1: SAP for Me Portal**

**For BDC Customers (Most Common):**

1. Go to https://me.sap.com
2. Login with your S-user credentials
3. Navigate to **Installations & Monitoring**
4. Find your **BDC Formation** (e.g., "VP_BDC_FORMATION")
5. Click on formation → **HANA Cloud** section
6. Find your HANA instance
7. Click on **instance name** or **three dots (•••)**
8. Look for:
   - **"Database Settings"** or
   - **"User Management"** or
   - **"Security"** or
   - **"Manage Configuration"**
9. Find **SYSTEM user** section
10. Click **"Reset Password"** or **"Change Password"**
11. Enter new password (must meet requirements)
12. Save

**Password Requirements:**
- At least 8 characters
- At least 1 uppercase letter
- At least 1 lowercase letter  
- At least 1 number
- At least 1 special character

---

### **Method 2: Contact SAP Support**

**If UI method doesn't work:**

1. Open SAP Support ticket via https://launchpad.support.sap.com
2. Component: **HAN-DB-HDB** (HANA Database)
3. Subject: "Reset SYSTEM password for BDC HANA Cloud instance"
4. Include:
   - Instance ID or hostname
   - BDC Formation name
   - Your S-user ID
   - Business justification
5. SAP will reset password and provide temporary password
6. Change password after first login

**Expected Response Time**: 1-2 business days

---

### **Method 3: Check Formation Owner**

**If this is a shared BDC formation:**

1. Identify the **Formation Owner** (the person who provisioned BDC)
2. They might have the SYSTEM password documented
3. They can reset it via SAP for Me
4. Request password from them

---

### **Method 4: Database Recovery Console (Advanced)**

**For on-premise or special access:**

If you have OS-level access to HANA server (unlikely for BDC):

```bash
# Stop HANA instance
HDB stop

# Start in maintenance mode
HDB start --maintenance

# Connect to maintenance console
hdbsql -u SYSTEM -n localhost:30013

# Reset password
ALTER USER SYSTEM PASSWORD "NewPassword123!";

# Restart normally
HDB stop
HDB start
```

**Note**: This likely won't work for BDC Cloud instances (no OS access).

---

## 🎯 Recommended Approach for Your Situation

**Based on your BDC-provisioned HANA:**

### **Step 1**: Try SAP for Me (15 minutes)
1. Login to https://me.sap.com
2. Navigate through: Installations → Your Formation → HANA Instance
3. Look for password reset option

### **Step 2**: If not found, open SAP ticket (same day)
1. Go to https://launchpad.support.sap.com
2. Create incident with priority P2 (High)
3. Request SYSTEM password reset
4. Include all instance details

### **Step 3**: While waiting, use alternative (works now!)
1. Implement CSN viewer with api.sap.com (already done!)
2. Feature works without SYSTEM access
3. Switch to HANA CSN table later when SYSTEM is available

---

## 📝 After Getting SYSTEM Password

Once you have SYSTEM password:

1. **Connect as SYSTEM** in Database Explorer
2. **Run grant script**:
   ```bash
   $env:HANA_PASSWORD="system-password"
   $env:HANA_USER="SYSTEM"
   python grant_system_privileges.py
   ```
3. **Verify CSN access**:
   ```sql
   SELECT * FROM "_SAP_DB_ACCESS_DATA_PRODUCT_GATEWAY"."_SAP_DATAPRODUCT_DELTA_CSN"
   ```
4. **Switch backend to use P2P_DP_USER** (optional, for security)

---

## 🔐 Security Best Practices

After resetting SYSTEM password:

1. ✅ Use strong password (16+ characters)
2. ✅ Document password securely (password manager)
3. ✅ Don't share SYSTEM password widely
4. ✅ Create dedicated users for applications (like P2P_DP_USER)
5. ✅ Use DBADMIN for daily admin tasks
6. ✅ Reserve SYSTEM for system-level operations only

---

## 🎯 Current Status: Blocked but Alternatives Work

**What's Blocked:**
- Cannot query CSN data from HANA table (Error 258)
- Cannot reset SYSTEM password from Database Explorer
- Need SAP assistance

**What Works:**
- ✅ CSN data available via api.sap.com (Discovery API)
- ✅ Backend endpoint already implemented
- ✅ Just need UI implementation
- ✅ Feature can be delivered today!

**Decision**: Implement with api.sap.com now, switch to HANA table later if needed.

---

## 📞 SAP Support Contact Info

**For BDC HANA Cloud:**
- Support Portal: https://launchpad.support.sap.com
- Component: **HAN-DB-HDB**
- Priority: P2 (High) or P3 (Medium)
- Expected Response: 4-24 hours

**For BDC Formation:**
- Support Portal: Same
- Component: **BDC-XXX** (formation-specific)
- Include formation name and instance details

---

**Last Updated**: 2026-01-24 09:57 AM
**Status**: SYSTEM password reset methods documented
**Next Action**: Try SAP for Me or open support ticket