# HANA_DP_USER Setup Guide - Team Generic User

**Created**: January 26, 2026  
**Purpose**: Create team-shared user for viewing and consuming data products  
**User Name**: `HANA_DP_USER`  
**Use Case**: Team members can use this generic account to access data products

---

## 🎯 Quick Start

### Option 1: Use Database Explorer (Recommended)

1. Open HANA Database Explorer
2. Connect as **DBADMIN**
3. Open SQL Console
4. Copy & paste: `sql/hana/create_hana_dp_user_for_team.sql`
5. Execute script
6. Review output for success messages

### Option 2: Use PowerShell Helper

```powershell
# Execute from project root
powershell -ExecutionPolicy Bypass -File sql/hana/run_create_hana_dp_user.ps1
```

---

## 📋 What This User Can Do

### ✅ Access Capabilities

**View Data Products**:
- List all available data products
- See data product metadata (versions, entities)
- Browse data product catalog

**Query Data Products**:
- Execute SELECT queries on all data product tables
- Read Supplier, Purchase Order, Invoice data
- Create JOINs across data products
- Aggregate data for reporting

**Development Work**:
- Test data product queries
- Develop P2P application features
- Create views combining data products
- Build analytical reports

### ❌ Cannot Do

**Restricted Operations**:
- ❌ Install new data products (admin only)
- ❌ Modify data product data (read-only)
- ❌ Delete or alter data products
- ❌ Grant privileges to other users
- ❌ Access SYSTEM-level operations

---

## 🔐 Security & Password

**Initial Password**: `YourSecurePassword123!`

**⚠️ IMPORTANT**: Change the password before executing the script!

**To change password in script**:
```sql
-- Edit line 12 in create_hana_dp_user_for_team.sql:
CREATE USER HANA_DP_USER PASSWORD "YOUR_STRONG_PASSWORD_HERE!" NO FORCE_FIRST_PASSWORD_CHANGE;
```

**Password Requirements**:
- Minimum 8 characters
- At least 1 uppercase letter
- At least 1 lowercase letter
- At least 1 number
- At least 1 special character

---

## 🧪 Testing Access

### After User Creation, Test with These Queries

**Connect as**: `HANA_DP_USER`

**Test 1: List Available Data Products**
```sql
SELECT SCHEMA_NAME, SCHEMA_OWNER, CREATE_TIME
FROM SYS.SCHEMAS
WHERE SCHEMA_NAME LIKE '_SAP_DATAPRODUCT%'
ORDER BY CREATE_TIME DESC;
```

**Expected**: Should see list of installed data products

---

**Test 2: Query Supplier Data Product**
```sql
-- Replace schema name with actual from Test 1
SELECT TOP 10 
    Supplier,
    SupplierName,
    Country,
    City
FROM "_SAP_DATAPRODUCT_sap_s4com_dataProduct_Supplier_v1_..."."supplier.Supplier";
```

**Expected**: Should see supplier data (or error if not installed)

---

**Test 3: Check My Privileges**
```sql
-- See what roles I have
SELECT ROLE_NAME 
FROM SYS.GRANTED_ROLES 
WHERE GRANTEE = CURRENT_USER
ORDER BY ROLE_NAME;

-- See what schemas I can access
SELECT SCHEMA_NAME, PRIVILEGE
FROM SYS.GRANTED_PRIVILEGES 
WHERE GRANTEE = CURRENT_USER
  AND OBJECT_TYPE = 'SCHEMA'
  AND SCHEMA_NAME LIKE '_SAP_DATAPRODUCT%'
ORDER BY SCHEMA_NAME;
```

**Expected**: Should show granted roles and schema access

---

**Test 4: Sample P2P Query**
```sql
-- Example: Join Supplier with Purchase Order
SELECT 
    s.SupplierName,
    po.PurchaseOrder,
    po.PurchaseOrderDate,
    po.PurchasingOrganization
FROM "_SAP_DATAPRODUCT_..._Supplier"."supplier.Supplier" s
INNER JOIN "_SAP_DATAPRODUCT_..._PurchaseOrder"."purchaseorder.PurchaseOrder" po
    ON s.Supplier = po.Supplier
ORDER BY po.PurchaseOrderDate DESC
LIMIT 10;
```

**Expected**: Should see joined data from both data products

---

## 📝 Customization Required

### Before Executing Script

**1. Set Password** (Line 12):
```sql
CREATE USER HANA_DP_USER PASSWORD "YOUR_TEAM_PASSWORD!" NO FORCE_FIRST_PASSWORD_CHANGE;
```

**2. Get Actual Data Product Schema Names**:

Run this query as DBADMIN to find installed data products:
```sql
SELECT SCHEMA_NAME FROM SYS.SCHEMAS 
WHERE SCHEMA_NAME LIKE '_SAP_DATAPRODUCT%';
```

**3. Update Schema Names in Script** (Lines 60-110):

Replace placeholder schema names with actual ones from Step 2:
```sql
-- Example: Replace this...
GRANT SELECT ON SCHEMA "_SAP_DATAPRODUCT_sap_s4com_dataProduct_Supplier_v1_..." 

-- With actual schema name...
GRANT SELECT ON SCHEMA "_SAP_DATAPRODUCT_sap_s4com_dataProduct_Supplier_v1_c8f5c255-6ddd-444a-8f90-01baa10b87d3"
```

---

## 🔧 Connection Details

### For Team Members

**Host**: `e7decab9-3e98-41cf-bbf7-d0a8c13d7fb9.hana.prod-eu10.hanacloud.ondemand.com`  
**Port**: `443`  
**User**: `HANA_DP_USER`  
**Password**: (Set by admin - share securely with team)

### Connection String Format

```
hdbcli:
-h e7decab9-3e98-41cf-bbf7-d0a8c13d7fb9.hana.prod-eu10.hanacloud.ondemand.com
-p 443
-u HANA_DP_USER
-pw <password>
-e
```

### In Application (Python)

```python
from hdbcli import dbapi

conn = dbapi.connect(
    address='e7decab9-3e98-41cf-bbf7-d0a8c13d7fb9.hana.prod-eu10.hanacloud.ondemand.com',
    port=443,
    user='HANA_DP_USER',
    password='your_password',
    encrypt=True,
    sslValidateCertificate=False
)
```

---

## 🚨 Troubleshooting

### Problem: "invalid user name: HANA_DP_USER"

**Cause**: User already exists

**Solution**:
```sql
-- Drop and recreate
DROP USER HANA_DP_USER CASCADE;
-- Then run script again
```

---

### Problem: "insufficient privilege" when granting

**Cause**: DBADMIN doesn't have privilege to grant certain roles in BDC

**Solution**:
- Skip role grants (they're optional)
- Focus on schema-level grants (these work in BDC)
- The script handles this with BEGIN/EXCEPTION blocks

---

### Problem: "Schema not found" errors

**Cause**: Data product not installed in HANA Cloud

**Solution**:
1. Check installed products: `SELECT SCHEMA_NAME FROM SYS.SCHEMAS WHERE SCHEMA_NAME LIKE '_SAP_DATAPRODUCT%'`
2. Update script with actual schema names
3. Comment out grants for non-installed products

---

### Problem: "Error 258" when querying

**Cause**: Schema grants not applied

**Solution**:
```sql
-- Grant SELECT explicitly on the schema
GRANT SELECT ON SCHEMA "_SAP_DATAPRODUCT_..." TO HANA_DP_USER;
```

---

## 📊 What Gets Granted

### Minimum Required (Always Granted)
- ✅ `CATALOG READ` - Browse database catalog
- ✅ `CONNECT` - Login capability
- ✅ `CREATE SCHEMA` - Create own working schemas (optional)

### Roles (Attempted - May Not Exist in BDC)
- ⚠️ `SAP HANA Cloud Data Publisher Viewer` - View data products
- ⚠️ `SAP HANA Cloud Viewer` - Read-only database access

### Schema Access (Customizable)
- ✅ `SELECT` on each `_SAP_DATAPRODUCT_...` schema
- ✅ Access to all tables within those schemas

---

## 👥 Team Usage Guidelines

### Sharing with Team

**DO**:
- ✅ Share connection details securely (password manager)
- ✅ Document which data products are accessible
- ✅ Provide example queries
- ✅ Set up read-only access only

**DON'T**:
- ❌ Share password in plain text emails
- ❌ Grant write access to data products
- ❌ Use this user for production apps
- ❌ Share DBADMIN credentials

### Use Cases

**Development**:
- Test data product queries during development
- Explore data product schemas
- Build prototype queries

**Analysis**:
- Run ad-hoc data analysis
- Create reports
- Validate data quality

**Demo**:
- Show data products to stakeholders
- Test application features
- Validate integrations

---

## 📚 Related Documentation

- `GRANT_DATA_PRODUCT_ROLES_TO_P2P_USER.md` - Detailed role documentation
- `DATA_PRODUCT_AUTHORIZATION_GUIDE.md` - Authorization concepts
- `HANA_CLOUD_PRIVILEGES_GUIDE.md` - HANA privilege model
- `DATA_PRODUCT_SUPPORT_IN_HANA_CLOUD.md` - Data product architecture

---

## ✅ Success Checklist

After executing script:

- [ ] User created without errors
- [ ] Basic privileges granted (CATALOG READ, CONNECT)
- [ ] Roles attempted (check output messages)
- [ ] Schema grants applied (at least 1 data product)
- [ ] Verification queries show results
- [ ] Test connection as HANA_DP_USER works
- [ ] Test SELECT query returns data
- [ ] Share credentials securely with team
- [ ] Document accessible data products
- [ ] Add connection to team wiki/docs

---

## 🎯 Next Steps

1. **Execute**: Run `create_hana_dp_user_for_team.sql` as DBADMIN
2. **Test**: Connect as HANA_DP_USER and run test queries
3. **Share**: Distribute connection details to team securely
4. **Document**: Update team docs with accessible data products
5. **Use**: Start building P2P applications!

---

**Questions?** See `docs/hana-cloud/` for 29+ HANA Cloud guides.