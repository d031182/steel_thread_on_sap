# Graph Ontology Persistence Strategy

## Overview

**Question**: Should we persist graph ontologies (schema graph + data graph) in the database?

**Answer**: **YES** - This aligns with HANA Cloud Property Graph engine architecture and provides significant benefits.

## What HANA Cloud Does

### HANA Property Graph Engine
HANA's Property Graph engine **persists graph definitions** as metadata:

1. **Graph Workspace**: Stores graph schema definitions
2. **Vertex/Edge Types**: Defined as metadata tables
3. **Property Definitions**: Stored with type information
4. **Relationship Mappings**: Persisted FK relationships

**Example HANA Graph Definition**:
```sql
CREATE GRAPH WORKSPACE P2P_GRAPH
    VERTEX TABLE Supplier
        KEY (Supplier)
    VERTEX TABLE PurchaseOrder  
        KEY (PurchaseOrder)
    EDGE TABLE SupplierInvoiceItem
        SOURCE PurchaseOrder(PurchaseOrder)
        TARGET SupplierInvoice(SupplierInvoice)
        KEY (SupplierInvoice, FiscalYear, SupplierInvoiceItem);
```

This metadata is **stored in HANA system tables** and persists across sessions.

## Our Current Approach (In-Memory)

### What We Do Now
```python
# RelationshipMapper discovers relationships at runtime
relationships = relationship_mapper.discover_relationships(csn_data)
# Stored in memory, rediscovered each session
```

**Limitations**:
- ❌ Rediscovered every session (wasted computation)
- ❌ No audit trail of relationship changes
- ❌ Can't track relationship quality over time
- ❌ No manual overrides/adjustments persistence

## Proposed Architecture: Persistent Ontologies

### Database Schema

```sql
-- Schema Graph (Tables & Columns)
CREATE TABLE graph_schema_nodes (
    node_id INTEGER PRIMARY KEY,
    node_type TEXT,  -- 'table' or 'column'
    name TEXT,
    parent_table TEXT,
    data_type TEXT,
    is_key BOOLEAN,
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);

CREATE TABLE graph_schema_edges (
    edge_id INTEGER PRIMARY KEY,
    source_table TEXT,
    source_column TEXT,
    target_table TEXT,
    target_column TEXT,
    relationship_type TEXT,  -- 'foreign_key', 'one_to_many', etc.
    confidence REAL,
    discovery_method TEXT,  -- 'csn_metadata', 'manual', 'inferred'
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);

-- Data Graph (Actual Records & Relationships)
CREATE TABLE graph_data_nodes (
    node_id TEXT PRIMARY KEY,  -- e.g., 'PurchaseOrder:PO000001'
    table_name TEXT,
    record_id TEXT,
    properties JSON,  -- Record fields as JSON
    created_at TIMESTAMP
);

CREATE TABLE graph_data_edges (
    edge_id INTEGER PRIMARY KEY,
    source_node_id TEXT,
    target_node_id TEXT,
    relationship_type TEXT,
    properties JSON,  -- Edge attributes
    created_at TIMESTAMP,
    FOREIGN KEY (source_node_id) REFERENCES graph_data_nodes(node_id),
    FOREIGN KEY (target_node_id) REFERENCES graph_data_nodes(node_id)
);

-- Metadata
CREATE TABLE graph_ontology_metadata (
    key TEXT PRIMARY KEY,
    value TEXT,
    updated_at TIMESTAMP
);
```

### Benefits of Persistence

#### 1. Performance
- **Before**: Discover 31 relationships every session (~2-3 seconds)
- **After**: Load from database (~50ms)
- **Impact**: 50x faster startup

#### 2. Auditability
```sql
-- Track when relationships were discovered
SELECT * FROM graph_schema_edges 
WHERE created_at > '2026-01-01'
ORDER BY confidence DESC;

-- See relationship changes over time
SELECT relationship_type, COUNT(*) 
FROM graph_schema_edges 
GROUP BY relationship_type;
```

#### 3. Manual Overrides
```python
# Admin can override low-confidence relationships
UPDATE graph_schema_edges 
SET confidence = 1.0, 
    discovery_method = 'manual_verified'
WHERE source_table = 'SupplierInvoice' 
AND target_table = 'PurchaseOrder';
```

#### 4. Incremental Updates
```python
# Only update changed relationships
new_tables = detect_schema_changes(csn_data)
for table in new_tables:
    relationships = discover_relationships(table)
    upsert_to_db(relationships)  # Only changed data
```

#### 5. Graph Query Optimization
```sql
-- Pre-computed graph for fast traversal
SELECT * FROM graph_data_edges 
WHERE source_node_id = 'PurchaseOrder:PO000001';

-- vs. Runtime discovery with JOINs
SELECT ... FROM PurchaseOrder po
JOIN SupplierInvoiceItem sii ON po.PurchaseOrder = sii.PurchaseOrder
...  -- Multiple joins, slower
```

## Implementation Strategy

### Phase 1: Schema Graph Persistence (Priority)
1. Create `graph_schema_*` tables
2. Store discovered relationships from CSN
3. Add manual override capability
4. Update RelationshipMapper to use DB cache

**Effort**: 2-3 hours
**Impact**: High (startup performance, auditability)

### Phase 2: Data Graph Persistence (Optional)
1. Create `graph_data_*` tables
2. Materialize nodes/edges on demand
3. Add graph traversal APIs
4. Optimize for common queries

**Effort**: 4-6 hours
**Impact**: Medium (query performance for large datasets)

### Phase 3: HANA Integration (Future)
1. Export schema to HANA Property Graph DDL
2. Sync ontology to HANA Graph Workspace
3. Bidirectional schema updates

**Effort**: 6-8 hours
**Impact**: High (HANA native graph features)

## Comparison: In-Memory vs. Persistent

| Aspect | In-Memory (Current) | Persistent (Proposed) |
|--------|-------------------|---------------------|
| **Discovery Speed** | 2-3s every session | 50ms (cached) |
| **Audit Trail** | None | Full history |
| **Manual Overrides** | Lost on restart | Persisted |
| **Schema Changes** | Full rediscovery | Incremental updates |
| **Query Performance** | Runtime JOINs | Pre-computed graph |
| **HANA Alignment** | No | Yes ✅ |
| **Complexity** | Low | Medium |

## Recommendation

**DO persist graph ontologies** for these reasons:

1. ✅ **HANA Alignment**: Matches Property Graph engine architecture
2. ✅ **Performance**: 50x faster startup
3. ✅ **Auditability**: Track relationship changes
4. ✅ **Flexibility**: Manual overrides + incremental updates
5. ✅ **Scalability**: Pre-computed graphs scale better

### Start With
- **Schema Graph** (high value, low effort)
- Store in SQLite for POC
- Later migrate to HANA Property Graph

### Defer
- **Data Graph** (until performance becomes issue)
- Full HANA integration (until production deployment)

## Migration Path

### Current State
```python
# In-memory discovery
relationships = relationship_mapper.discover_relationships(csn)
return relationships  # Lost after session
```

### Future State
```python
# Check DB cache first
cached = db.query("SELECT * FROM graph_schema_edges")
if cached and not schema_changed:
    return cached  # Fast path
else:
    # Discover and persist
    relationships = relationship_mapper.discover_relationships(csn)
    db.upsert("graph_schema_edges", relationships)
    return relationships
```

## Conclusion

**YES**, persist graph ontologies in the database. This:
- Aligns with HANA Cloud Property Graph architecture
- Provides significant performance benefits
- Enables auditability and manual overrides
- Creates a migration path to HANA native graphs

**Next Step**: Implement Phase 1 (Schema Graph Persistence) as a natural evolution of the current RelationshipMapper.

---

**Related Documents**:
- [[csn-driven-knowledge-graph]]
- [[sap-hana-graph-engines-comparison]]
- [[data-abstraction-layers]]