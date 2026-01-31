# HANA Property Graph Workspace Setup Guide

**Created**: 2026-01-31  
**Purpose**: Step-by-step guide to create P2P graph workspace in HANA Cloud  
**Prerequisites**: P2P tables exist in HANA Cloud, user has CREATE GRAPH WORKSPACE privilege

---

## Overview

This guide walks through creating a **HANA Property Graph Workspace** that maps your existing P2P tables to a graph structure, enabling native HANA graph algorithms.

**Benefits**:
- 10-100x faster than NetworkX for large graphs
- Native SQL integration
- Production-scale graph analytics
- Shortest path, centrality, clustering algorithms built-in

---

## Step 1: Access HANA Database Explorer

### Option A: Via SAP BTP Cockpit
1. Open SAP BTP Cockpit
2. Navigate to your HANA Cloud instance
3. Click "Open in SAP HANA Database Explorer"

### Option B: Direct URL
```
https://hana-cockpit.cfapps.eu10.hana.ondemand.com/sap/hana/cst/catalog/cockpit-index.html
```

**Login**: Use your DBADMIN or P2P_DEV_USER credentials

---

## Step 2: Verify Prerequisites

### Check Tables Exist

Run in SQL Console:
```sql
-- List P2P tables in current schema
SELECT TABLE_NAME, TABLE_TYPE, RECORD_COUNT
FROM SYS.TABLES
WHERE SCHEMA_NAME = CURRENT_SCHEMA
  AND TABLE_NAME IN (
    'Supplier', 'Product', 'PurchaseOrder', 'PurchaseOrderItem',
    'SupplierInvoice', 'SupplierInvoiceItem', 'JournalEntry',
    'ServiceEntrySheet', 'CompanyCode', 'CostCenter', 'PaymentTerms'
  )
ORDER BY TABLE_NAME;
```

**Expected**: All 11 tables should be listed

### Check Primary Keys

```sql
-- Verify PRIMARY KEY constraints exist
SELECT 
    i.TABLE_NAME,
    STRING_AGG(ic.COLUMN_NAME, ', ') as PRIMARY_KEY_COLUMNS
FROM SYS.INDEXES i
JOIN SYS.INDEX_COLUMNS ic
    ON i.SCHEMA_NAME = ic.SCHEMA_NAME
    AND i.TABLE_NAME = ic.TABLE_NAME
    AND i.INDEX_NAME = ic.INDEX_NAME
WHERE i.SCHEMA_NAME = CURRENT_SCHEMA
    AND i.CONSTRAINT = 'PRIMARY KEY'
    AND i.TABLE_NAME IN ('Supplier', 'Product', 'PurchaseOrder', 
                         'PurchaseOrderItem', 'SupplierInvoice', 
                         'SupplierInvoiceItem')
GROUP BY i.TABLE_NAME
ORDER BY i.TABLE_NAME;
```

**Expected**: Each table should have PRIMARY KEY columns listed

### Check Graph Privilege

```sql
-- Check if user has CREATE GRAPH WORKSPACE privilege
SELECT * FROM SYS.GRANTED_PRIVILEGES
WHERE GRANTEE = CURRENT_USER
  AND PRIVILEGE = 'CREATE GRAPH WORKSPACE';
```

**If missing**: Ask admin to grant via:
```sql
GRANT CREATE GRAPH WORKSPACE TO <your_user>;
```

---

## Step 3: Execute Graph Workspace Script

### Load Script

1. In Database Explorer, click "SQL Console" (green play button)
2. Open file: `sql/hana/create_p2p_graph_workspace.sql`
3. Copy entire contents to SQL Console

### Execute

**Option 1: Execute All** (Recommended first time)
- Click "Run" button (F8)
- All statements execute sequentially

**Option 2: Execute Step-by-Step** (For debugging)
- Highlight DROP statement → Execute (F8)
- Highlight CREATE GRAPH WORKSPACE → Execute (F8)
- Highlight verification queries → Execute (F8)

### Expected Output

**CREATE statement**:
```
Statement 'DROP GRAPH WORKSPACE...' successfully executed
Statement 'CREATE GRAPH WORKSPACE...' successfully executed
```

**Verification queries**:
```
WORKSPACE_NAME: P2P_GRAPH
VERTEX_COUNT: 9
EDGE_COUNT: 2
```

---

## Step 4: Verify Workspace Created

### Check Workspace Metadata

```sql
-- Workspace details
SELECT * FROM SYS.GRAPH_WORKSPACES 
WHERE WORKSPACE_NAME = 'P2P_GRAPH';
```

**Expected fields**:
- `WORKSPACE_NAME`: P2P_GRAPH
- `SCHEMA_NAME`: (your schema)
- `OWNER`: (your user)
- `CREATE_TIME`: (current timestamp)

### List Vertices (Nodes)

```sql
-- All vertex tables in workspace
SELECT 
    TABLE_NAME,
    KEY_COLUMN_NAMES,
    VERTEX_COUNT
FROM SYS.GRAPH_WORKSPACE_VERTICES
WHERE WORKSPACE_NAME = 'P2P_GRAPH'
ORDER BY TABLE_NAME;
```

**Expected**: 9 vertex tables (Supplier, Product, PurchaseOrder, etc.)

### List Edges (Relationships)

```sql
-- All edge tables in workspace
SELECT 
    TABLE_NAME,
    SOURCE_VERTEX_TABLE,
    TARGET_VERTEX_TABLE,
    EDGE_COUNT
FROM SYS.GRAPH_WORKSPACE_EDGES
WHERE WORKSPACE_NAME = 'P2P_GRAPH'
ORDER BY TABLE_NAME;
```

**Expected**: 2 edge tables (PurchaseOrderItem, SupplierInvoiceItem)

---

## Step 5: Test Graph Queries

### Test 1: Shortest Path

```sql
-- Find shortest path between two suppliers (via purchase orders)
SELECT * FROM GRAPH_SHORTEST_PATH(
    GRAPH => 'P2P_GRAPH',
    START_VERTEX => 'Supplier:SUP001',
    END_VERTEX => 'Supplier:SUP002',
    MAX_HOPS => 5
);
```

**What it does**: Finds how two suppliers are connected through products/POs

### Test 2: Neighbor Discovery

```sql
-- Find all products connected to a supplier
SELECT * FROM GRAPH_NEIGHBORS(
    GRAPH => 'P2P_GRAPH',
    START_VERTEX => 'Supplier:SUP001',
    DIRECTION => 'OUTGOING',
    MIN_DEPTH => 1,
    MAX_DEPTH => 2
);
```

**What it does**: Lists products ordered from a specific supplier

### Test 3: Centrality Analysis

```sql
-- Find most connected suppliers (network hubs)
SELECT * FROM GRAPH_BETWEENNESS_CENTRALITY(
    GRAPH => 'P2P_GRAPH',
    VERTEX_TABLE => 'Supplier',
    TOP_K => 10
) 
ORDER BY CENTRALITY DESC;
```

**What it does**: Ranks suppliers by their importance in the network

---

## Troubleshooting

### Error: "Table not found"

**Cause**: P2P tables don't exist or are in different schema

**Fix**:
```sql
-- Check which schema has the tables
SELECT SCHEMA_NAME, TABLE_NAME
FROM SYS.TABLES
WHERE TABLE_NAME = 'Supplier';

-- If in different schema, add schema prefix:
-- VERTEX TABLE "OTHER_SCHEMA"."Supplier" KEY ("Supplier")
```

### Error: "Insufficient privilege"

**Cause**: Missing CREATE GRAPH WORKSPACE privilege

**Fix**: Ask admin to execute:
```sql
GRANT CREATE GRAPH WORKSPACE TO YOUR_USER;
```

### Error: "Primary key constraint missing"

**Cause**: Tables created without PRIMARY KEY

**Fix**: 
1. Drop and recreate tables with PK constraints
2. Or use script: `scripts/python/rebuild_sqlite_with_pk.py` (adapt for HANA)

### Error: "Workspace already exists"

**Cause**: Trying to create duplicate workspace

**Fix**:
```sql
-- Drop existing first
DROP GRAPH WORKSPACE P2P_GRAPH CASCADE;

-- Then create
CREATE GRAPH WORKSPACE P2P_GRAPH ...
```

---

## Performance Tuning

### Index Optimization

Graph workspaces benefit from indexes on key columns:

```sql
-- Create indexes on foreign key columns (if not exist)
CREATE INDEX IDX_POI_MATERIAL ON "PurchaseOrderItem"("Material");
CREATE INDEX IDX_SII_PO ON "SupplierInvoiceItem"("PurchaseOrder");
```

### Statistics Update

Keep statistics current for query optimizer:

```sql
-- Update statistics on graph tables
UPDATE STATISTICS FOR "PurchaseOrder";
UPDATE STATISTICS FOR "PurchaseOrderItem";
UPDATE STATISTICS FOR "Supplier";
UPDATE STATISTICS FOR "SupplierInvoice";
UPDATE STATISTICS FOR "SupplierInvoiceItem";
```

---

## Next Steps

### Phase 4B: Implement HANAGraphQueryEngine

Now that workspace exists, implement Python interface:

1. Create `core/services/hana_graph_query_engine.py`
2. Implement `IGraphQueryEngine` interface
3. Use HANA SQL graph functions
4. Add fallback to NetworkX when HANA unavailable

### Phase 4C: Integration

Update Knowledge Graph module:

1. Detect data source type (HANA vs SQLite)
2. Use HANAGraphQueryEngine for HANA
3. Use NetworkXGraphQueryEngine for SQLite
4. Transparent switching (hybrid architecture)

---

## Reference

**HANA Documentation**:
- [SAP HANA Cloud Graph Guide](https://help.sap.com/docs/HANA_CLOUD_DATABASE/f381aa9c4b99457fb3c6b53a2fd29c02/30d1d8cfd5d0470dbaac2ebe20cefb8f.html)
- [Graph Algorithms Reference](https://help.sap.com/docs/HANA_CLOUD_DATABASE/f381aa9c4b99457fb3c6b53a2fd29c02/7a2c19b6e21a4db4a6cf64c62f28c5a0.html)

**Project Docs**:
- [[SAP HANA Graph Engines Comparison]]
- [[Graph Backend Integration Plan]]
- [[Graph Query API Abstraction]]

---

**Status**: Phase 4A Complete ✅  
**Next**: Execute script in HANA Database Explorer, then proceed to Phase 4B