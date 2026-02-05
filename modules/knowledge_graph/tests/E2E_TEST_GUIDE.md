# Knowledge Graph End-to-End Integration Test

**Purpose**: Verify that the cache integration architecture works correctly after SoC refactoring (v3.15).

**Last Updated**: 2026-02-03

---

## New: Graph Ontology v4.0 Schema Validation

**Added**: 2026-02-03

The project now has a v4 composite FK schema for graph ontology persistence (separate from the visualization cache). To validate the schema:

```bash
# Run v4 schema validation
python scripts/python/test_fk_with_pragma.py
```

**Expected Output**:
```
[PASS] Node inserted
[PASS] FK constraint blocked invalid insert
[PASS] Edge inserted
[PASS] FK constraint blocked invalid insert
Composite FK (data_source, mode) is working correctly!
```

**What This Tests**:
- ✅ graph_ontology table with composite PK (data_source, mode)
- ✅ graph_nodes/graph_edges with composite FK enforcement
- ✅ CASCADE DELETE functionality
- ✅ Data integrity across 4 combinations: (sqlite/hana) × (schema/data)

**Note**: This is for the NEW persistence layer (`graph_ontology` tables), which is separate from the visualization cache (`graph_visjs_cache`) tested in the main E2E test below.

---

## What This Test Verifies

This E2E test verifies the **cache integration architecture**:

1. ✅ Cache stores FK relationships correctly (`graph_cache_ontology` table)
2. ✅ Data graph builder reads FROM cache (not rediscovering)
3. ✅ Schema graph builder reads FROM cache (not rediscovering)
4. ✅ Both builders share the same cache source (single source of truth)
5. ✅ **Data and schema modes create DISJUNCT (independent) graphs**

### Why This Order Matters

The test sequence verifies the data flow:
```
Refresh Cache → Populates cache table with 31 FK relationships
     ↓
     ├─→ Data Graph    → Reads FROM cache, builds 18 green edges (data records)
     └─→ Schema Graph  → Reads FROM cache, builds 26 orange edges (table schemas)
         
         TWO INDEPENDENT GRAPHS FROM ONE CACHE
```

**Critical Points**:
- Cache must be populated FIRST, then builders consume FROM it
- Data mode and schema mode create SEPARATE, INDEPENDENT graphs
- Data mode: Shows actual data records with FK links (18 edges)
- Schema mode: Shows table schemas with FK definitions (26 edges)
- Both modes read FROM the same cache of 31 FK relationships

---

## Prerequisites

1. Server must be running: `python server.py` (port 5000)
2. SQLite database with P2P data: `app/p2p_data.db`
3. All modules loaded (especially knowledge_graph module)

---

## Test Steps

### Step 1: Refresh Ontology Cache

**Purpose**: Populate `graph_cache_ontology` table with FK relationships

```bash
curl -X POST http://localhost:5000/api/knowledge-graph/cache/refresh \
  -H "Content-Type: application/json" \
  -d '{"source":"sqlite"}'
```

**Expected Result**:
```json
{
  "success": true,
  "message": "Cache refreshed successfully. Discovered 31 relationships in ~775ms",
  "statistics": {
    "cleared": 31,
    "discovered": 31,
    "inserted": 31,
    "updated": 0,
    "discovery_time_ms": 775
  }
}
```

**Verifies**: Cache discovery and storage working

---

### Step 2: Build Data Graph

**Purpose**: Verify data builder reads FK relationships FROM cache

```bash
curl "http://localhost:5000/api/knowledge-graph/?source=sqlite&mode=data&max_records=20&filter_orphans=true"
```

**Expected Result**:
- ✅ 18+ edges with color `#4caf50` (GREEN - data mode FK edges)
- ✅ 23+ nodes (PurchaseOrder, Supplier, SupplierInvoiceItem)
- ✅ Fast response (~8 seconds)

**Verifies**: Data builder successfully reads FROM cache table

**Check For**:
```json
{
  "edges": [
    {
      "color": {"color": "#4caf50"},
      "title": "PurchaseOrder.Supplier = SUP001 → Supplier"
    }
  ],
  "stats": {
    "edge_count": 18,
    "node_count": 23
  }
}
```

---

### Step 3: Build Schema Graph

**Purpose**: Verify schema builder reads FK relationships FROM cache

```bash
curl "http://localhost:5000/api/knowledge-graph/?source=sqlite&mode=schema"
```

**Expected Result**:
- ✅ 26+ edges with color `#ff9800` (ORANGE - schema mode FK edges)
- ✅ 79+ total edges
- ✅ Fast response (~2 seconds)

**Verifies**: Schema builder successfully reads FROM cache table

**Check For**:
```bash
# Quick check for orange edges
curl "http://localhost:5000/api/knowledge-graph/?source=sqlite&mode=schema" | findstr /C:"#ff9800"
```

Should show 26+ lines with `"color": "#ff9800"`

---

### Step 4: Verify System Logs ⭐ MANDATORY

**Purpose**: Ensure no critical errors occurred during test execution

**Command** (check for errors since server start):
```bash
python -c "import sqlite3; conn = sqlite3.connect('logs/app_logs.db'); cursor = conn.cursor(); cursor.execute('SELECT timestamp, level, logger, message FROM application_logs WHERE level IN (\"ERROR\", \"CRITICAL\") AND timestamp > datetime(\"now\", \"-10 minutes\") ORDER BY timestamp DESC LIMIT 20'); rows = cursor.fetchall(); print('\n'.join([f\"{row[0]} - {row[1]} - {row[2]} - {row[3]}\" for row in rows]) if rows else 'No critical errors found in last 10 minutes'); conn.close()"
```

**Expected Result**:
```
No critical errors found in last 10 minutes
```

**If Errors Found**:
- ✅ **Historical errors** (timestamp BEFORE test start): Ignore - these are from previous sessions
- ❌ **New errors** (timestamp AFTER test start): Investigate and resolve before declaring test passed

**Verifies**: 
- No backend errors during cache refresh
- No backend errors during graph building
- No frontend JavaScript errors
- System is stable and error-free

**Why This Matters**:
- API tests may pass, but frontend could have JavaScript errors
- Errors logged to `application_logs` table reveal runtime issues
- Ensures end-to-end system health, not just API functionality

---

### Step 5: Cleanup

**Windows**:
```bash
taskkill /F /IM python.exe
```

**Linux/Mac**:
```bash
pkill python
```

---

## Success Criteria

| Test Step | Success Indicator |
|-----------|-------------------|
| Cache Refresh | 31 relationships discovered & stored |
| Data Graph | 18+ GREEN edges (#4caf50) |
| Schema Graph | 26+ ORANGE edges (#ff9800) |
| System Logs | No NEW critical errors since test start |
| Integration | Both graphs read from SAME cache |

---

## What Failure Indicates

| Symptom | Problem |
|---------|---------|
| Cache refresh fails | Database schema issue or relationship_discovery broken |
| Data graph has no green edges | DataGraphBuilder not reading from cache |
| Schema graph has no orange edges | SchemaGraphBuilder not reading from cache |
| Different edge counts between runs | Cache not persisting correctly |
| Critical errors in logs | Frontend JavaScript errors or backend exceptions |

---

## Troubleshooting

### Common Issues

**1. Frontend JavaScript Errors**

**Symptom**: Errors in `application_logs` with `[CLIENT]` prefix
```
[CLIENT] ERROR: TypeError: Cannot read properties of undefined
```

**Cause**: JavaScript code accessing undefined object properties

**Solution**: 
- Check the error stack trace for file and line number
- Review the JavaScript code for unsafe property access
- Add defensive null/undefined checks before accessing nested properties

**Example Fix**:
```javascript
// UNSAFE:
const msg = data.error.message;  // Crashes if data.error is undefined

// SAFE:
let msg = 'Unknown error';
if (data.error) {
    if (typeof data.error === 'object' && data.error.message) {
        msg = data.error.message;
    } else if (typeof data.error === 'string') {
        msg = data.error;
    }
}
```

**2. ResizeObserver Errors**

**Symptom**: `ResizeObserver loop completed with undelivered notifications`

**Cause**: Benign browser warning from UI layout changes (SAP UI5 controls)

**Solution**: Can be safely ignored - not a critical error

---

**3. System Log Check Returns Errors**

**Action Required**:
1. Check error timestamps
2. If BEFORE test start → Ignore (historical errors)
3. If AFTER test start → Investigate and resolve
4. Re-run E2E test after fix to confirm resolution

---

## Architecture Being Tested

```
┌─────────────────────────────────────────────────┐
│  Step 1: Refresh Cache                          │
│  ┌──────────────────────────────────────┐       │
│  │ RelationshipDiscoveryDB              │       │
│  │  - Discovers 31 FK relationships     │       │
│  │  - Stores in graph_cache_ontology    │       │
│  └──────────────────────────────────────┘       │
│                    ↓                             │
│  Step 2: Build Data Graph                       │
│  ┌──────────────────────────────────────┐       │
│  │ DataGraphBuilder                     │       │
│  │  - Reads FROM cache (not DB)         │       │
│  │  - Builds 18 green FK edges          │       │
│  └──────────────────────────────────────┘       │
│                    ↓                             │
│  Step 3: Build Schema Graph                     │
│  ┌──────────────────────────────────────┐       │
│  │ SchemaGraphBuilder                   │       │
│  │  - Reads FROM cache (not DB)         │       │
│  │  - Builds 26 orange FK edges         │       │
│  └──────────────────────────────────────┘       │
└─────────────────────────────────────────────────┘
```

**Key**: Cache is the single source of truth for FK relationships. Both builders must read FROM cache, not rediscover from database.

---

## Related Files

### Visualization Cache Architecture
- **Implementation**: `modules/knowledge_graph/backend/`
  - `relationship_discovery_db.py` - Cache population
  - `data_graph_builder.py` - Data graph construction
  - `schema_graph_builder.py` - Schema graph construction
  - `api.py` - HTTP endpoints
- **Interface**: `core/interfaces/relationship_discovery.py`
- **Schema**: `sql/sqlite/create_graph_visjs_cache.sql`

### Graph Ontology v4.0 Persistence Layer (NEW)
- **Schema**: `sql/sqlite/create_graph_ontology_tables_v4.sql`
- **Creation Script**: `scripts/python/recreate_ontology_v4.py`
- **Validation**: `scripts/python/test_fk_with_pragma.py`
- **Structure Check**: `scripts/python/verify_composite_fk.py`

### Obsolete/Deprecated Files
The following test scripts are **deprecated** due to Windows Unicode encoding issues:
- ❌ `scripts/python/test_graph_integration_e2e.py` (replaced by curl-based manual testing)
- ❌ `scripts/test_graph_e2e.sh` (Linux/Mac only)
- ❌ `scripts/test_graph_e2e.ps1` (Unicode encoding issues)

**Use the curl-based manual test steps documented above instead.**

---

## Notes

- Manual testing with `curl` is more reliable than automated scripts (avoids Windows Unicode encoding issues)
- The test sequence order IS the test specification - it tests the integration path
- Server must be running because we're testing the full HTTP → Service → Cache flow
- Graph ontology v4.0 schema is validated separately (see top of document)
