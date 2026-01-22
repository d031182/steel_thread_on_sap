# CSN Data Product to Database Table Mapping Analysis

## Executive Summary

**Question**: Do we always have exactly one table per Data Product CSN file?

**Answer**: **NO** - The relationship is **complex and many-to-many**:
- Each CSN Data Product contains **multiple entities** (ranging from 2 to 235+)
- Each CSN entity may map to **one or more database tables**
- Some entities are **nested structures** or **reference data** within the main entity

## Entity Count by Data Product

| Data Product | CSN File | Entity Count | Main Entities | Mapping Complexity |
|--------------|----------|--------------|---------------|-------------------|
| **Supplier** | sap-s4com-Supplier-v1.json | **~235** | Supplier + 234 reference entities | 🔴 VERY HIGH |
| **Payment Terms** | sap-s4com-PaymentTerms-v1.json | **~25** | PaymentTerms + 24 reference fields | 🟡 HIGH |
| **Purchase Order** | sap-s4com-PurchaseOrder-v1.json | **5** | PO Header + Items + Confirmations + Account Assignment + Schedule Lines | 🟢 MEDIUM |
| **Supplier Invoice** | sap-s4com-SupplierInvoice-v1.json | **2** | Invoice Header + Invoice Items | 🟢 LOW |
| **Service Entry Sheet** | sap-s4com-ServiceEntrySheet-v1.json | **2** | SES Header + SES Items | 🟢 LOW |
| **Journal Entry** | sap-s4com-JournalEntryHeader-v1.json | **2** | Journal Entry + Bill of Exchange Items | 🟢 LOW |

**Total Entities Across All Data Products**: **~271 entities**

## Detailed Entity Analysis

### 1. Supplier (235 entities) 🔴 COMPLEX

**Main Entity**: `Supplier`

**Entity Categories**:
- **Core Supplier Entity**: 1 entity
- **Address Components**: ~50+ entities (ADRNR, AD_CITY1, AD_CITY2, AD_NAME1, AD_NAME2, etc.)
- **Reference Data**: ~180+ entities (various SAP reference fields, code lists, domain values)

**Database Mapping**:
- Maps to our **1 table**: `Suppliers`
- Most CSN entities are **flattened into columns** or stored as **reference lookups**
- Address entities are **denormalized** into single supplier record

**Why So Many Entities?**
- SAP CSN includes **all possible fields** from S/4HANA
- Includes **domain definitions**, **value helps**, and **reference structures**
- Our database uses a **simplified subset** of these fields

---

### 2. Payment Terms (25 entities) 🟡 MODERATE

**Main Entity**: `PaymentTerms`

**Sample Entities**:
- `PaymentTerms` - Main entity
- `FARP_DZTERM` - Terms code
- `XSPLT` - Split payment indicator
- `DZBD1P_FARP` - Discount period 1
- `DZBD2P_FARP` - Discount period 2
- Additional reference fields and domain values

**Database Mapping**:
- Maps to our **1 table**: `PaymentTerms`
- Reference entities are **field definitions** or **validation rules**

---

### 3. Purchase Order (5 entities) 🟢 CLEAR

**Entities**:
1. `PurchaseOrder` - Header
2. `PurchaseOrderItem` - Line items
3. `PurchaseOrderScheduleLine` - Delivery schedules
4. `PurchaseOrderAccountAssignment` - GL account assignments
5. `PurOrdSupplierConfirmation` - Supplier confirmations

**Database Mapping**:
- `PurchaseOrder` → `PurchaseOrders` table
- `PurchaseOrderItem` → `PurchaseOrderItems` table
- Other entities: **Not implemented** in our simplified schema (could be added if needed)

**Mapping**: **1-to-1 for main entities**, others optional

---

### 4. Supplier Invoice (2 entities) 🟢 SIMPLE

**Entities**:
1. `SupplierInvoice` - Header
2. `SupplierInvoiceItem` - Line items

**Database Mapping**:
- `SupplierInvoice` → `SupplierInvoices` table
- `SupplierInvoiceItem` → `SupplierInvoiceItems` table

**Mapping**: **Perfect 1-to-1** (header-item pattern)

---

### 5. Service Entry Sheet (2 entities) 🟢 SIMPLE

**Entities**:
1. `ServiceEntrySheet` - Header
2. `ServiceEntrySheetItem` - Service line items

**Database Mapping**:
- `ServiceEntrySheet` → `ServiceEntrySheets` table
- `ServiceEntrySheetItem` → `ServiceEntrySheetItems` table

**Mapping**: **Perfect 1-to-1** (header-item pattern)

---

### 6. Journal Entry (2 entities) 🟢 SIMPLE

**Entities**:
1. `JournalEntry` - Header
2. `JournalEntryItemBillOfExchange` - Bill of exchange items

**Database Mapping**:
- `JournalEntry` → `JournalEntries` table
- `JournalEntryItemBillOfExchange` → Potentially `JournalEntryItems` (specialized type)

**Mapping**: **1-to-1 with specialization**

---

## Key Findings

### 1. **NO Simple 1-to-1 Mapping**

❌ **Myth**: One CSN file = One database table  
✅ **Reality**: One CSN file = Multiple entities with various relationships

### 2. **Entity Types in CSN Files**

CSN entities fall into several categories:

1. **Primary Entities** (e.g., `SupplierInvoice`, `PurchaseOrder`)
   - Main business objects
   - Map directly to header tables

2. **Child Entities** (e.g., `SupplierInvoiceItem`, `PurchaseOrderItem`)
   - Line items or sub-components
   - Map to separate item tables
   - Parent-child relationship via foreign keys

3. **Reference Entities** (e.g., address fields in Supplier)
   - Supporting data structures
   - Often **flattened** into parent table columns
   - May be **denormalized** for simplicity

4. **Domain/Type Entities** (e.g., field definitions, value ranges)
   - Metadata and validation rules
   - Usually **NOT mapped** to database tables
   - Used for application logic and validation

### 3. **Mapping Patterns**

**Pattern A: Simple Header-Item** (Most Common)
```
CSN Entity              →  Database Table
────────────────────────────────────────────
SupplierInvoice        →  SupplierInvoices
SupplierInvoiceItem    →  SupplierInvoiceItems
```

**Pattern B: Complex Multi-Entity**
```
CSN Entity                      →  Database Table
──────────────────────────────────────────────────────
PurchaseOrder                  →  PurchaseOrders
PurchaseOrderItem              →  PurchaseOrderItems
PurchaseOrderScheduleLine      →  (Optional) PurchaseOrderSchedules
PurchaseOrderAccountAssignment →  (Optional) Not implemented
```

**Pattern C: Denormalized Reference Data**
```
CSN Entities (235)              →  Database Table
──────────────────────────────────────────────────────
Supplier (main)                →  Suppliers (1 table)
+ 234 reference entities       →  Flattened into columns or omitted
```

### 4. **Our Database Design Philosophy**

We created a **simplified, practical schema** that:

✅ **Captures core business entities** (headers + items)  
✅ **Flattens reference data** where appropriate  
✅ **Omits SAP-internal fields** that aren't needed for analytics  
✅ **Adds custom fields** for our specific use cases (e.g., variance tracking)  
✅ **Maintains referential integrity** with foreign keys  

### 5. **Entity-to-Table Mapping Summary**

| CSN Data Product | CSN Entities | Our DB Tables | Mapping Ratio |
|------------------|--------------|---------------|---------------|
| Supplier | 235 | 1 | 235:1 (denormalized) |
| PaymentTerms | 25 | 1 | 25:1 (denormalized) |
| PurchaseOrder | 5 | 2 | 5:2 (selective) |
| SupplierInvoice | 2 | 2 | 1:1 (direct) |
| ServiceEntrySheet | 2 | 2 | 1:1 (direct) |
| JournalEntry | 2 | 2 | 1:1 (direct) |
| **TOTAL** | **~271** | **10** | **27:1 average** |

## Recommendations

### For Database Schema Design

1. **Start with main entities** - Focus on header-item pairs first
2. **Evaluate reference entities** - Decide which to denormalize vs. normalize
3. **Omit metadata entities** - Skip domain definitions and validation rules
4. **Add custom fields** - Extend with business-specific requirements

### For CSN Data Product Usage

1. **Not all entities need tables** - Many are supporting metadata
2. **Header-item pattern is standard** - Most business objects follow this
3. **Reference data can be flattened** - No need for 235 Supplier tables
4. **Focus on transactional entities** - These are the core business objects

### For Future Enhancements

If we wanted to add more detail from CSN files:

**PurchaseOrder** could expand to:
- ✅ `PurchaseOrders` (have)
- ✅ `PurchaseOrderItems` (have)
- ➕ `PurchaseOrderScheduleLines` (delivery schedules)
- ➕ `PurchaseOrderAccountAssignments` (GL assignments)
- ➕ `SupplierConfirmations` (vendor confirmations)

**Supplier** could expand to:
- ✅ `Suppliers` (have)
- ➕ `SupplierAddresses` (separate address table)
- ➕ `SupplierBankAccounts` (banking details)
- ➕ `SupplierContacts` (contact persons)

## Conclusion

**The relationship between CSN Data Products and Database Tables is NOT 1-to-1!**

✅ **CSN Data Products** are comprehensive API schemas containing:
- Main business entities
- Child/line item entities  
- Reference data structures
- Domain definitions
- Metadata and validation rules

✅ **Our Database Tables** are practical implementations that:
- Select relevant entities from CSN
- Flatten reference data where appropriate
- Add custom fields for specific use cases
- Optimize for analytical queries

**The 1-to-Many (or Many-to-Many) relationship is by design** - we extract what we need from the rich CSN schemas and create an efficient, queryable database structure.

---

**Last Updated**: 2026-01-21  
**Analysis Tool**: PowerShell + JSON parsing  
**Source**: SAP S/4HANA Cloud Data Products (CSN format)
