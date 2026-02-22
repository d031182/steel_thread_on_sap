# P2P Database Creation Workflow

**Purpose**: Complete guide for creating HANA-compatible SQLite test databases

**Last Updated**: 2026-02-07  
**Related**: [[P2P Dashboard Design]], [[Repository Pattern Modular Architecture]]

---

## Overview

This workflow creates SQLite test databases that are **schema-compatible with HANA Cloud**, enabling seamless switching between SQLite (development) and HANA (production).

**Key Principle**: Use CSN (Core Schema Notation) as the single source of truth for schema definitions.

---

## The Workflow (3 Steps)

### Step 1: Create Schema from CSN Files ⭐

**Script**: `scripts/python/rebuild_sqlite_from_csn.py`

**What it does**:
- Reads CSN definitions from `docs/csn/*.json`
- Generates SQLite tables with HANA-compatible field names
- Includes PRIMARY KEY constraints from CSN metadata
- Creates 11 core P2P entities

**Usage**:
```bash
python scripts/python/rebuild_sqlite_from_csn.py
```

**Output**: `app/database/p2p_data_products.db` with empty tables

**Tables Created**:
- `PurchaseOrder` (58 columns, PK: PurchaseOrder)
- `PurchaseOrderItem` (75 columns, PK: PurchaseOrder + PurchaseOrderItem)
- `Supplier` (135 columns, PK: Supplier)
- `SupplierInvoice` (20 columns, PK: SupplierInvoice + FiscalYear)
- `SupplierInvoiceItem` (39 columns, PK: SupplierInvoice + FiscalYear + SupplierInvoiceItem)
- `ServiceEntrySheet` (22 columns, PK: ServiceEntrySheet)
- `PaymentTerms` (4 columns, PK: PaymentTerms)
- `CompanyCode` (24 columns, PK: CompanyCode)
- `CostCenter` (88 columns, PK: ControllingArea + CostCenter + ValidityEndDate)
- `JournalEntry` (106 columns, PK: CompanyCode + FiscalYear + AccountingDocument)
- `Product` (166 columns, PK: Product)

---

### Step 2: Populate with Test Data

**Option A: Sync from HANA** (Recommended for realistic data) ⭐

**Script**: `scripts/python/regenerate_complete_p2p_data.py`

**Prerequisites**: 
- HANA Cloud instance running
- `.env` file configured with HANA credentials
- Server running at `http://localhost:5000`

**What it does**:
1. Syncs master data from HANA (Suppliers, PaymentTerms, CompanyCode)
2. Generates synthetic transactional data (POs, Invoices, Service Sheets)
3. Creates complete P2P workflow with 100% FK integrity

**Usage**:
```bash
# Start server first (for HANA API access)
python server.py

# In another terminal:
python scripts/python/regenerate_complete_p2p_data.py
```

**Output**: 
- 10+ Suppliers (from HANA)
- 10 Purchase Orders with 20 items
- 10 Supplier Invoices (7 posted, 3 blocked)
- 5 Service Entry Sheets
- 10 Journal Entries
- Complete P2P workflow visualization

---

**Option B: Pure Synthetic Data** (No HANA required)

**Script**: `scripts/python/populate_p2p_comprehensive.py`

**Prerequisites**: None (fully offline)

**What it does**:
- Creates synthetic master data (10 suppliers, 5 payment terms)
- Generates 20 POs with 40 items
- Creates 30 invoices (26 posted, 4 pending)
- Adds 5 service entry sheets
- All data uses correct HANA field names

**Usage**:
```bash
python scripts/python/populate_p2p_comprehensive.py
```

**Output**:
- 10 Suppliers (synthetic)
- 20 Purchase Orders with 40 items
- 30 Invoices (10+ as requested) ⭐
- 5 Service Entry Sheets
- Total value: €200K+

---

### Step 3: Copy to Module Location

After database is populated, copy it to the module:

```bash
# Copy to sqlite_connection module
copy app\database\p2p_data_products.db modules\sqlite_connection\database\p2p_test_data.db
```

**Why**: Modular architecture - database lives with the module that owns it.

---

## Schema Compatibility

### HANA vs SQLite Field Name Mapping

The CSN-based approach ensures 100% field name compatibility:

**SupplierInvoice**:
- ✅ `SupplierInvoiceStatus` (HANA field name)
- ❌ NOT `InvoiceStatus` (simplified SQLite)

**PurchaseOrderItem**:
- ✅ `IsCompletelyDelivered` (HANA field name)
- ❌ NOT `IsCompleted` (simplified)
- ✅ `IsFinallyInvoiced` (HANA field name)
- ✅ `LastChangeDateTime` (HANA field name)
- ✅ `CreationDate` (HANA field name)
- ✅ `NetAmount` (HANA field name)
- ✅ `CompanyCode` (HANA field name)

**PurchaseOrderScheduleLine**:
- ✅ `IsCompletelyDelivered` (HANA field name)
- ✅ `DelivDateCategory` (HANA field name)

**Supplier**:
- ✅ `PurchasingIsBlocked` (HANA field name)
- ❌ NOT `IsBlocked` (simplified)

---

## Common Pitfalls ⚠️

### 1. Using Simplified Field Names

**Problem**: Creating SQLite tables with simplified field names (e.g., `IsBlocked` instead of `PurchasingIsBlocked`)

**Result**: SQL queries in `aggregations.py` fail with "no such column" errors

**Solution**: ALWAYS use `rebuild_sqlite_from_csn.py` to generate schema

---

### 2. Missing Schedule Line Data

**Problem**: Creating POs without `PurchaseOrderScheduleLine` records

**Result**: Late delivery KPIs show zero/null

**Solution**: Include schedule line creation in population scripts (see Step 7 in `populate_p2p_comprehensive.py`)

---

### 3. Missing Variance Columns

**Problem**: Using non-existent column names like `SuplrInvcItemHasAmountVariance`

**Correct Column**: `SuplrInvcItemHasAmountOutsdTol`

**Solution**: Check actual schema with `PRAGMA table_info(SupplierInvoiceItem)` before writing INSERT statements

---

## Quick Reference Commands

```bash
# 1. Create schema (ALWAYS first)
python scripts/python/rebuild_sqlite_from_csn.py

# 2. Populate data
# Option A: With HANA (realistic)
python scripts/python/regenerate_complete_p2p_data.py

# Option B: Without HANA (synthetic)
python scripts/python/populate_p2p_comprehensive.py

# 3. Verify data
python -c "import sqlite3; conn = sqlite3.connect('app/database/p2p_data_products.db'); \
cursor = conn.cursor(); \
print(f'Suppliers: {cursor.execute(\"SELECT COUNT(*) FROM Supplier\").fetchone()[0]}'); \
print(f'POs: {cursor.execute(\"SELECT COUNT(*) FROM PurchaseOrder\").fetchone()[0]}'); \
print(f'Invoices: {cursor.execute(\"SELECT COUNT(*) FROM SupplierInvoice\").fetchone()[0]}'); \
conn.close()"

# 4. Copy to module
copy app\database\p2p_data_products.db modules\sqlite_connection\database\p2p_test_data.db

# 5. Test
python server.py
# Navigate to: http://localhost:5000 → P2P Dashboard
```

---

## Why This Matters

### The Problem We Solved

**Before** (naive approach):
```sql
-- Simplified SQLite schema
CREATE TABLE Supplier (
    Supplier TEXT PRIMARY KEY,
    SupplierName TEXT,
    IsBlocked INTEGER  -- ❌ Wrong field name!
);
```

**Query fails**:
```python
# aggregations.py expects HANA field names
"WHERE s.PurchasingIsBlocked = 1"  # ❌ Column doesn't exist
```

**After** (CSN-based approach):
```sql
-- HANA-compatible schema from CSN
CREATE TABLE Supplier (
    Supplier TEXT PRIMARY KEY,
    SupplierName TEXT,
    PurchasingIsBlocked INTEGER,  -- ✅ Correct HANA field name
    -- ... 132 more columns
);
```

**Query succeeds**:
```python
"WHERE s.PurchasingIsBlocked = 1"  # ✅ Works perfectly
```

---

## Benefits

1. **Schema Compatibility**: SQLite ↔ HANA seamless switching
2. **Query Reuse**: Same SQL queries work on both databases
3. **Development Speed**: Test locally without HANA connection
4. **Production Ready**: Deploy to HANA without code changes
5. **Type Safety**: CSN provides data types and constraints
6. **Avoiding Memento Effect**: Document once, reference forever

---

## File Locations

**CSN Definitions**: `docs/csn/*.json` (single source of truth)

**Scripts**:
- Schema creation: `scripts/python/rebuild_sqlite_from_csn.py`
- Data population (HANA): `scripts/python/regenerate_complete_p2p_data.py`
- Data population (offline): `scripts/python/populate_p2p_comprehensive.py`
- Simple test data: `scripts/python/create_realistic_p2p_data.py`

**Database Locations**:
- Working database: `app/database/p2p_data_products.db`
- Module-owned database: `modules/sqlite_connection/database/p2p_test_data.db`

**SQL Queries**: `modules/p2p_dashboard/backend/aggregations.py` (uses HANA field names)

---

## Maintenance

### Adding New Entities

1. Add CSN definition to `docs/csn/[Entity]_CSN.json`
2. Update `CORE_ENTITIES` list in `rebuild_sqlite_from_csn.py`
3. Re-run schema creation
4. Update population scripts if needed

### Updating Existing Entities

1. Update CSN definition in `docs/csn/`
2. Re-run `rebuild_sqlite_from_csn.py` (drops and recreates)
3. Re-run population script to restore data

---

## Related Documentation

- [[P2P Dashboard Design]] - Dashboard requirements and KPIs
- [[Repository Pattern Modular Architecture]] - How repositories abstract data access
- [[DataSource Architecture Refactoring Proposal]] - Migration to Repository Pattern
- `core/services/csn_parser.py` - CSN parsing logic
- `docs/csn/` - CSN definition files

---

**Key Takeaway**: Never manually create SQLite schemas. Always use `rebuild_sqlite_from_csn.py` to ensure HANA compatibility.