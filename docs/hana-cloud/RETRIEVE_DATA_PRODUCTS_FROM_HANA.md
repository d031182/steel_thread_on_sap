# Retrieve Data Products from HANA Cloud Instance

## Understanding the Setup

### What is the BDC MCP Server?

The **BDC MCP Server** is NOT a separate database - it's simply a **tool that connects to YOUR HANA Cloud instance** and allows me to query it remotely. Think of it as a remote SQL client.

```
You (Local) ← → BDC MCP Server ← → YOUR HANA Cloud Instance
                 (Just a connector)    (The actual database)
```

### Your HANA Instance Details

- **Host**: e7decab9-3e98-41cf-bbf7-d0a8c13d7fb9.hana.prod-eu10.hanacloud.ondemand.com
- **Port**: 443
- **User**: P2P_DEV_USER (password: `P2P_Dev123!`)
- **User Schema**: P2P_SCHEMA (empty, ready for your custom tables)

---

## Understanding "Available" vs "Installed"

### Important Distinction

The HANA Cloud Central UI shows:
- **"Available Data Products (2)"** = Products you CAN install from the catalog (not yet installed)
  - Sales Order - **Not Installed** ❌
  - Delivery Management Configuration Data - **Not Installed** ❌

BUT your HANA instance ALREADY HAS:
- **27 Data Product Schemas** = Already installed from other sources (S/4HANA systems shared via BDC)

### Why This Confusion?

The UI shows "Available = 2" because:
1. It only displays NEW products you can add from the current catalog view
2. The 27 existing schemas were shared/installed from OTHER S/4HANA systems in your BDC formation
3. These 27 are NOT shown in "Available" because they're already installed

### Summary

✅ **27 SAP Data Products ALREADY INSTALLED** in your HANA Cloud instance  
❌ **Sales Order NOT INSTALLED** (shows as "Available" = you can install it)  
✅ **2 Products Available to Install** (Sales Order + Delivery Management)

### Complete List of Installed Data Products

| # | Data Product | Schema Name | Install Date |
|---|--------------|-------------|--------------|
| 1 | **Supplier** | `_SAP_DATAPRODUCT_sap_s4com_dataProduct_Supplier_v1_...` | 2025-11-04 |
| 2 | **Customer** | `_SAP_DATAPRODUCT_sap_s4com_dataProduct_Customer_v1_...` | 2025-11-04 |
| 3 | **Product** | `_SAP_DATAPRODUCT_sap_s4com_dataProduct_Product_v1_...` | 2025-11-07 |
| 4 | **Journal Entry Header** | `_SAP_DATAPRODUCT_sap_s4com_dataProduct_JournalEntryHeader_v1_...` | 2025-11-04 |
| 5 | **Journal Entry Codes** | `_SAP_DATAPRODUCT_sap_s4com_dataProduct_JournalEntryCodes_v1_...` | 2025-11-04 |
| 6 | **Journal Entry Item Codes** | `_SAP_DATAPRODUCT_sap_s4com_dataProduct_JournalEntryItemCodes_v1_...` | 2025-11-07 |
| 7 | **Entry View Journal Entry** | `_SAP_DATAPRODUCT_sap_s4com_dataProduct_EntryViewJournalEntry_v1_...` | 2025-11-07 |
| 8 | **Company Code** | `_SAP_DATAPRODUCT_sap_s4com_dataProduct_CompanyCode_v1_...` | 2025-11-07 |
| 9 | **Company** | `_SAP_DATAPRODUCT_sap_s4com_dataProduct_Company_v1_...` | 2025-11-04 |
| 10 | **Cost Center** | `_SAP_DATAPRODUCT_sap_s4com_dataProduct_CostCenter_v1_...` | 2025-11-07 |
| 11 | **Cost Center Activity Type** | `_SAP_DATAPRODUCT_sap_s4com_dataProduct_CostCenterActivityType_v1_...` | 2025-11-04 |
| 12 | **Controlling Area** | `_SAP_DATAPRODUCT_sap_s4com_dataProduct_ControllingArea_v1_...` | 2025-11-04 |
| 13 | **Controlling Object** | `_SAP_DATAPRODUCT_sap_s4com_dataProduct_ControllingObject_v1_...` | 2025-11-07 |
| 14 | **General Ledger Account** | `_SAP_DATAPRODUCT_sap_s4com_dataProduct_GeneralLedgerAccount_v1_...` | 2025-11-04 |
| 15 | **Ledger** | `_SAP_DATAPRODUCT_sap_s4com_dataProduct_Ledger_v1_...` | 2025-11-03 |
| 16 | **Profit Center** | `_SAP_DATAPRODUCT_sap_s4com_dataProduct_ProfitCenter_v1_...` | 2025-11-04 |
| 17 | **Business Area** | `_SAP_DATAPRODUCT_sap_s4com_dataProduct_BusinessArea_v1_...` | 2025-11-04 |
| 18 | **Functional Area** | `_SAP_DATAPRODUCT_sap_s4com_dataProduct_FunctionalArea_v1_...` | 2025-11-04 |
| 19 | **Segment** | `_SAP_DATAPRODUCT_sap_s4com_dataProduct_Segment_v1_...` | 2025-11-04 |
| 20 | **Purchasing Organization** | `_SAP_DATAPRODUCT_sap_s4com_dataProduct_PurchasingOrganization_v1_...` | 2025-11-07 |
| 21 | **Plant** (not listed earlier) | Schema exists | 2025-10-08 |
| 22 | **Country** | `_SAP_DATAPRODUCT_sap_s4com_dataProduct_Country_v1_...` | 2025-11-04 |
| 23 | **Fiscal Year** | `_SAP_DATAPRODUCT_sap_s4com_dataProduct_FiscalYear_v1_...` | 2025-11-04 |
| 24 | **HANA Currency** | `_SAP_DATAPRODUCT_sap_s4com_dataProduct_HANACurrency_v1_...` | 2025-11-04 |
| 25 | **House Bank** | `_SAP_DATAPRODUCT_sap_s4com_dataProduct_HouseBank_v1_...` | 2025-11-07 |
| 26 | **Consolidation** (multiple) | Various consolidation schemas | 2025-11-04/07 |
| 27 | **Project** (S/4PCE) | `_SAP_DATAPRODUCT_sap_s4pce_dataProduct_Project_v1_...` | 2025-11-04 |

### P2P-Relevant Data Products (Currently Installed)

For **Procure-to-Pay (P2P)** processes, you have these relevant data products:

✅ **Supplier** - Business partners who provide materials/services  
✅ **Purchasing Organization** - Organizational unit for purchasing  
❌ **Purchase Order** - NOT installed (needed for P2P!)  
❌ **Supplier Invoice** - NOT installed (needed for P2P!)  
❌ **Service Entry Sheet** - NOT installed (needed for P2P!)  
❌ **Payment Terms** - NOT installed (needed for P2P!)  
❌ **Sales Order** - NOT installed (you mentioned you expected this)

---

## How to Query Installed Data Products

### Method 1: Via BDC MCP Server (Remote Access - Easiest)

This is what I've been using - it connects to YOUR HANA instance remotely.

**Example: Query Supplier Data**
```sql
SELECT TOP 5 
    Supplier,
    SupplierName,
    BPAddrCityName,
    Country,
    CreationDate
FROM "_SAP_DATAPRODUCT_sap_s4com_dataProduct_Supplier_v1_c8f5c255-6ddd-444a-8f90-01baa10b87d3"."_SAP_DATAPRODUCT_b6d7050b-8c9a-4c4d-9689-346e4ab14855_supplier.Supplier"
```

**Result**:
```
Supplier    | SupplierName        | City     | Country | CreationDate
------------|---------------------|----------|---------|-------------
0001026704  | Small Victory53148  | New York | US      | 2025-11-04
0001026511  | Small Victory22190  | New York | US      | 2025-09-21
0001026468  | Small Victory91753  | New York | US      | 2025-09-08
```

### Method 2: Via Database Explorer (GUI)

1. **Access Database Explorer**:
   - URL: https://hanacloud.ondemand.com
   - Login with your credentials
   - Select your instance

2. **Navigate to Data Products**:
   - Click "Data Products" tab
   - Browse installed products
   - Click on "Supplier" (or any product)
   - View tables and data

3. **Open SQL Console**:
   - Click "Open SQL Console"
   - Run queries directly

### Method 3: Via Your Backend (Node.js)

Once your IP is added to the allowlist, you can query via your backend:

```javascript
// In your backend code
const query = `
  SELECT TOP 10 
    Supplier,
    SupplierName,
    Country
  FROM "_SAP_DATAPRODUCT_sap_s4com_dataProduct_Supplier_v1_c8f5c255-6ddd-444a-8f90-01baa10b87d3"."_SAP_DATAPRODUCT_b6d7050b-8c9a-4c4d-9689-346e4ab14855_supplier.Supplier"
`;

const result = await connection.executeQuery(query);
console.log(result);
```

---

## Understanding Data Product Schema Names

### Schema Naming Pattern

Data product schemas follow this pattern:
```
_SAP_DATAPRODUCT_[namespace]_dataProduct_[name]_v[version]_[UUID]
```

**Example**:
```
_SAP_DATAPRODUCT_sap_s4com_dataProduct_Supplier_v1_c8f5c255-6ddd-444a-8f90-01baa10b87d3
                  └─namespace─┘              └─name─┘ └─ver─┘ └──────────UUID──────────┘
```

### Table Naming Pattern

Within each schema, tables follow this pattern:
```
_SAP_DATAPRODUCT_[productID]_[namespace].[EntityName]
```

**Example**:
```
_SAP_DATAPRODUCT_b6d7050b-8c9a-4c4d-9689-346e4ab14855_supplier.Supplier
                  └────────────productID────────────┘ └─ns─┘  └─entity─┘
```

### Discovering Tables in a Data Product

**Query**:
```sql
SELECT TABLE_NAME 
FROM SYS.TABLES 
WHERE SCHEMA_NAME = '_SAP_DATAPRODUCT_sap_s4com_dataProduct_Supplier_v1_c8f5c255-6ddd-444a-8f90-01baa10b87d3'
ORDER BY TABLE_NAME;
```

**Result** (Supplier data product has 4 tables):
- `_SAP_DATAPRODUCT_..._supplier.Supplier` (main table)
- `_SAP_DATAPRODUCT_..._supplier.SupplierCompanyCode`
- `_SAP_DATAPRODUCT_..._supplier.SupplierPurchasingOrganization`
- `_SAP_DATAPRODUCT_..._supplier.SupplierWithHoldingTax`

---

## Sample Queries for Installed Data Products

### 1. Supplier Data

```sql
-- Get all suppliers
SELECT 
    Supplier,
    SupplierName,
    Country,
    BPAddrCityName,
    CreationDate
FROM "_SAP_DATAPRODUCT_sap_s4com_dataProduct_Supplier_v1_c8f5c255-6ddd-444a-8f90-01baa10b87d3"."_SAP_DATAPRODUCT_b6d7050b-8c9a-4c4d-9689-346e4ab14855_supplier.Supplier"
WHERE Country = 'US'
ORDER BY CreationDate DESC;
```

### 2. Customer Data

```sql
-- Query customer data
SELECT TOP 10 *
FROM "_SAP_DATAPRODUCT_sap_s4com_dataProduct_Customer_v1_307606c4-96f8-413d-b8c7-177af9413f88"."<table_name>"
```

### 3. Product Data

```sql
-- Query product catalog
SELECT TOP 10 *
FROM "_SAP_DATAPRODUCT_sap_s4com_dataProduct_Product_v1_5fa50ca7-d759-420f-8871-aa7dd60d20d8"."<table_name>"
```

### 4. Journal Entry Data

```sql
-- Query accounting journal entries
SELECT TOP 10 *
FROM "_SAP_DATAPRODUCT_sap_s4com_dataProduct_JournalEntryHeader_v1_c2ea85d0-d2ed-44db-95df-837ded709483"."<table_name>"
```

---

## Missing Data Products for P2P

### What You Need but Don't Have

Based on your P2P project, you're **missing these critical data products**:

❌ **Purchase Order** (`sap.s4com:apiResource:PurchaseOrder:v1`)  
❌ **Supplier Invoice** (`sap.s4com:apiResource:SupplierInvoice:v1`)  
❌ **Service Entry Sheet** (`sap.s4com:apiResource:ServiceEntrySheet:v1`)  
❌ **Payment Terms** (`sap.s4com:apiResource:PaymentTerms:v1`)  
❌ **Sales Order** (`sap.s4com:apiResource:SalesOrder:v1`)

### How to Install Sales Order Data Product

Based on your screenshot, you can see **Sales Order** is available to install:

**Step-by-Step Installation**:

1. **In HANA Cloud Central UI** (your screenshot):
   - You're already on the "Data Products" tab ✓
   - You can see "Sales Order - Not Installed"
   - Package ID: `52ac1a26-a503-4f71-8dd2-857badd77e44`

2. **Click on "Sales Order"**:
   - Click the "Sales Order" row to open details
   - Review the data product information
   - Check schema name and tables

3. **Install the Data Product**:
   - Look for an "Install" or "Enable" button
   - Click to install
   - Wait for installation to complete (may take a few minutes)

4. **Verify Installation**:
   ```sql
   -- Check if Sales Order schema was created
   SELECT SCHEMA_NAME 
   FROM SYS.SCHEMAS 
   WHERE SCHEMA_NAME LIKE '%SalesOrder%';
   ```

5. **Query Sales Order Data**:
   ```sql
   -- Once installed, query the data
   SELECT TOP 10 * 
   FROM "<new_schema_name>"."<table_name>";
   ```

**Note**: The other 27 data products you see in your HANA instance were installed from OTHER S/4HANA systems shared in your BDC formation, which is why they don't appear in the "Available" list on this page.

---

## Current Data Product Contents

### Supplier Tables (Example)

The Supplier data product contains **4 tables**:

```
_SAP_DATAPRODUCT_..._supplier.Supplier
_SAP_DATAPRODUCT_..._supplier.SupplierCompanyCode
_SAP_DATAPRODUCT_..._supplier.SupplierPurchasingOrganization
_SAP_DATAPRODUCT_..._supplier.SupplierWithHoldingTax
```

### Sample Supplier Data

**Real data from YOUR HANA instance**:

| Supplier | SupplierName | City | Country | Created |
|----------|--------------|------|---------|---------|
| 0001026704 | Small Victory53148 | New York | US | 2025-11-04 |
| 0001026511 | Small Victory22190 | New York | US | 2025-09-21 |
| 0001026468 | Small Victory91753 | New York | US | 2025-09-08 |

**Supplier Record Fields** (120+ columns including):
- Supplier ID
- SupplierName
- SupplierFullName
- Country, Region, City
- Address, PostalCode
- TaxJurisdiction
- VATRegistration
- PaymentTerms
- PurchasingOrganization
- AccountIsBlockedForPosting
- CreationDate
- And many more...

---

## How to Work with Data Products

### Option 1: Query Directly (Read-Only)

Data products are **read-only virtual tables** - you can query but NOT modify:

```sql
-- ✅ ALLOWED: Read data
SELECT * FROM "_SAP_DATAPRODUCT_..._supplier.Supplier";

-- ❌ NOT ALLOWED: Modify data
INSERT INTO "_SAP_DATAPRODUCT_..._supplier.Supplier" VALUES (...);
UPDATE "_SAP_DATAPRODUCT_..._supplier.Supplier" SET ...;
DELETE FROM "_SAP_DATAPRODUCT_..._supplier.Supplier" WHERE ...;
```

### Option 2: Create Local Copies in P2P_SCHEMA

Copy data to your schema for processing:

```sql
-- Create local table based on data product
CREATE TABLE P2P_SCHEMA.LOCAL_SUPPLIERS AS (
    SELECT 
        Supplier,
        SupplierName,
        Country,
        BPAddrCityName,
        CreationDate
    FROM "_SAP_DATAPRODUCT_sap_s4com_dataProduct_Supplier_v1_c8f5c255-6ddd-444a-8f90-01baa10b87d3"."_SAP_DATAPRODUCT_b6d7050b-8c9a-4c4d-9689-346e4ab14855_supplier.Supplier"
);

-- Now you can modify local copy
INSERT INTO P2P_SCHEMA.LOCAL_SUPPLIERS VALUES (...);
UPDATE P2P_SCHEMA.LOCAL_SUPPLIERS SET ...;
```

### Option 3: Create Views Joining Data Products

Create analytical views:

```sql
-- Create view joining multiple data products
CREATE VIEW P2P_SCHEMA.SUPPLIER_ANALYSIS AS
SELECT 
    s.Supplier,
    s.SupplierName,
    s.Country,
    c.CompanyCodeName,
    cc.CostCenterDescription
FROM "_SAP_DATAPRODUCT_..._supplier.Supplier" s
LEFT JOIN "_SAP_DATAPRODUCT_..._companycode.CompanyCode" c
    ON s.CompanyCode = c.CompanyCode
LEFT JOIN "_SAP_DATAPRODUCT_..._costcenter.CostCenter" cc
    ON s.CostCenter = cc.CostCenter;
```

---

## Complete Query Examples

### Example 1: Get All Tables in a Data Product

```sql
-- Replace with your actual schema name
SELECT 
    TABLE_NAME,
    RECORD_COUNT
FROM SYS.TABLES
WHERE SCHEMA_NAME = '_SAP_DATAPRODUCT_sap_s4com_dataProduct_Supplier_v1_c8f5c255-6ddd-444a-8f90-01baa10b87d3'
ORDER BY TABLE_NAME;
```

### Example 2: Count Records in Supplier

```sql
SELECT COUNT(*) as TOTAL_SUPPLIERS
FROM "_SAP_DATAPRODUCT_sap_s4com_dataProduct_Supplier_v1_c8f5c255-6ddd-444a-8f90-01baa10b87d3"."_SAP_DATAPRODUCT_b6d7050b-8c9a-4c4d-9689-346e4ab14855_supplier.Supplier";
```

### Example 3: Get Column Definitions

```sql
SELECT 
    COLUMN_NAME,
    DATA_TYPE_NAME,
    LENGTH,
    IS_NULLABLE
FROM SYS.TABLE_COLUMNS
WHERE SCHEMA_NAME = '_SAP_DATAPRODUCT_sap_s4com_dataProduct_Supplier_v1_c8f5c255-6ddd-444a-8f90-01baa10b87d3'
  AND TABLE_NAME LIKE '%Supplier'
ORDER BY POSITION;
```

### Example 4: Join Supplier with Company Code

```sql
SELECT 
    s.Supplier,
    s.SupplierName,
    s.Country,
    cc.CompanyCodeName
FROM "_SAP_DATAPRODUCT_sap_s4com_dataProduct_Supplier_v1_c8f5c255-6ddd-444a-8f90-01baa10b87d3"."_SAP_DATAPRODUCT_..._supplier.Supplier" s
INNER JOIN "_SAP_DATAPRODUCT_sap_s4com_dataProduct_CompanyCode_v1_911b4aaf-9af8-4da5-8bdb-aba5f09a1046"."_SAP_DATAPRODUCT_..._companycode.CompanyCode" cc
    ON s.CompanyCode = cc.CompanyCode
WHERE s.Country = 'US'
LIMIT 10;
```

---

## Why No Sales Order?

### Your Expectation vs. Reality

You mentioned:
> "there should be actually only exactly one data product available which is the Sales Order"

### Reality

- ❌ **Sales Order is NOT installed** in your HANA instance
- ✅ **27 OTHER data products ARE installed** (mostly finance/accounting)
- ❓ **Who installed these?** Likely someone else in your organization

### Possible Reasons

1. **Wrong Instance**: You might have expected a different HANA instance
2. **Not Yet Installed**: Sales Order needs to be installed
3. **Different Formation**: Sales Order might be in a different formation/instance
4. **Previous Setup**: Someone else installed these 27 products before

### How to Get Sales Order

**Option A: Install via HANA Cloud Central**
1. Go to https://hanacloud.ondemand.com
2. Data Products → Browse Catalog
3. Find "Sales Order" (`sap.s4com:apiResource:SalesOrder:v1`)
4. Click "Install"

**Option B: Check Different Instance**
- You might have multiple HANA instances
- Check if Sales Order is in a different instance
- Verify which instance should have Sales Order

**Option C: Request from BDC Admin**
- Contact your SAP BDC administrator
- Request Sales Order data product
- They can share/install it for you

---

## Quick Start: Access Supplier Data Now

### Step 1: List All Supplier Tables

```sql
SELECT TABLE_NAME 
FROM SYS.TABLES 
WHERE SCHEMA_NAME LIKE '%Supplier%'
ORDER BY TABLE_NAME;
```

### Step 2: Query Main Supplier Table

```sql
SELECT TOP 10
    Supplier,
    SupplierName,
    Country,
    BPAddrCityName as City,
    PostalCode,
    CreationDate
FROM "_SAP_DATAPRODUCT_sap_s4com_dataProduct_Supplier_v1_c8f5c255-6ddd-444a-8f90-01baa10b87d3"."_SAP_DATAPRODUCT_b6d7050b-8c9a-4c4d-9689-346e4ab14855_supplier.Supplier"
WHERE Country = 'US'
ORDER BY CreationDate DESC;
```

### Step 3: Explore Supplier Details

```sql
-- Get column list
SELECT COLUMN_NAME, DATA_TYPE_NAME
FROM SYS.TABLE_COLUMNS
WHERE SCHEMA_NAME = '_SAP_DATAPRODUCT_sap_s4com_dataProduct_Supplier_v1_c8f5c255-6ddd-444a-8f90-01baa10b87d3'
  AND TABLE_NAME LIKE '%Supplier'
  AND TABLE_NAME NOT LIKE '%Company%'
  AND TABLE_NAME NOT LIKE '%Purchasing%'
  AND TABLE_NAME NOT LIKE '%Tax%'
ORDER BY POSITION;
```

---

## Summary

### Current State of Your HANA Instance

**✅ What You HAVE**:
- 27 installed SAP data products
- Mostly finance/accounting data (GL, Cost Center, Ledger, etc.)
- Supplier, Customer, Product master data
- Accessible via BDC MCP server (remote queries)
- P2P_SCHEMA (empty, ready for your custom tables)

**❌ What You DON'T HAVE**:
- Sales Order data product (you expected this)
- Purchase Order data product (needed for P2P)
- Supplier Invoice data product (needed for P2P)
- Service Entry Sheet (needed for P2P)
- Payment Terms (needed for P2P)

### How BDC MCP Server Works

```
┌─────────────────────────────────────────────────────┐
│  BDC MCP Server (Tool)                              │
│  - Authenticates to your HANA instance              │
│  - Executes SQL queries remotely                    │
│  - Returns results back to you                      │
│  - NO separate database involved                    │
└──────────────────┬──────────────────────────────────┘
                   │
                   ▼ (SQL queries over TLS/443)
┌─────────────────────────────────────────────────────┐
│  YOUR HANA Cloud Instance                           │
│  Host: e7decab9-3e98-41cf-bbf7-d0a8c13d7fb9...     │
│                                                     │
│  ✅ 27 Data Product Schemas (installed)            │
│  ✅ P2P_SCHEMA (your custom schema)                │
│  ✅ Real SAP S/4HANA data (Supplier, etc.)         │
└─────────────────────────────────────────────────────┘
```

### Next Actions

1. **Clarify Expectations**:
   - Did you expect Sales Order to be the ONLY product?
   - Or did you expect Sales Order to be INSTALLED (but it's not)?
   - Should I help install Sales Order?

2. **Use Current Data**:
   - You have Supplier data available NOW
   - You can start building P2P analytics with existing data
   - Query Supplier, Customer, Product, etc.

3. **Install Missing Products**:
   - Install Purchase Order, Supplier Invoice, etc.
   - Build complete P2P workflow
   - Create comprehensive P2P application

**Which path would you like to take?**

---

**Last Updated**: January 22, 2026, 2:31 AM  
**Status**: 27 data products installed, Sales Order NOT found
