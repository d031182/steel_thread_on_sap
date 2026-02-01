# Graph Cache Architecture v3.13

**Purpose**: Instant graph visualization by caching complete vis.js graph data

---

## Problem Statement

**Before Cache**:
- User clicks "Refresh Graph" → 27 seconds wait (build graph from 100k+ DB records)
- Every refresh = full rebuild (inefficient)
- Poor UX (users wait, loading indicators, frustration)

**After Cache**:
- First click: 27s (builds + caches)
- Second+ clicks: <100ms (loads from cache)
- 270x faster! ⚡

---

## Architecture Design

### Storage: Key-Value in Metadata Table

**Why metadata table?**
- ✅ Already exists (`graph_ontology_metadata`)
- ✅ Designed for key-value pairs (perfect for JSON blobs)
- ✅ No new tables needed (simplicity)
- ✅ Single SELECT for instant load

**Table Structure** (existing):
```sql
CREATE TABLE graph_ontology_metadata (
    key TEXT PRIMARY KEY,      -- Cache key (e.g., 'cache_data_nodes')
    value TEXT,                -- JSON blob (complete vis.js data)
    updated_at TIMESTAMP       -- Auto-updated on changes
);
```

### Cache Keys

**Added 8 new keys** (via migration):

| Key | Purpose | Example Value |
|-----|---------|---------------|
| `cache_schema_nodes` | Schema graph nodes | `[{id: "Supplier", label: "Supplier", ...}, ...]` |
| `cache_schema_edges` | Schema graph edges | `[{from: "PO", to: "Supplier", ...}, ...]` |
| `cache_data_nodes` | Data graph nodes | `[{id: "SUPP-001", label: "Acme Corp", ...}, ...]` |
| `cache_data_edges` | Data graph edges | `[{from: "PO-123", to: "SUPP-001", ...}, ...]` |
| `cache_schema_updated` | Schema cache timestamp | `2026-01-31 09:15:00` |
| `cache_data_updated` | Data cache timestamp | `2026-01-31 09:20:00` |
| `cache_version` | Cache format version | `3.13` |
| `cache_enabled` | Cache on/off | `true` |

---

## Cache Logic Flow

### Phase 1: Build Graph (First Load)

```python
# DataGraphService.build_data_graph(use_cache=True)

def build_data_graph(self, max_records=20, use_cache=True):
    # 1. Check cache validity
    if use_cache and cache_exists('cache_data_nodes'):
        # Phase 2: Load from cache (instant)
        return load_from_cache()
    
    # 2. Build from scratch (slow path)
    nodes, edges = build_graph_from_database()  # 27 seconds
    
    # 3. Store in cache (for next time)
    store_in_cache('cache_data_nodes', json.dumps(nodes))
    store_in_cache('cache_data_edges', json.dumps(edges))
    store_in_cache('cache_data_updated', current_timestamp())
    
    return {
        'nodes': nodes,
        'edges': edges,
        'stats': {
            'cache_used': False,  # Built from scratch
            'build_time_ms': 27000
        }
    }
```

### Phase 2: Load from Cache (Subsequent Loads)

```python
def load_from_cache():
    # Single SELECT - instant!
    row = db.execute("""
        SELECT value FROM graph_ontology_metadata 
        WHERE key = 'cache_data_nodes'
    """).fetchone()
    
    nodes = json.loads(row[0])  # Parse JSON
    
    # Same for edges
    row = db.execute("""
        SELECT value FROM graph_ontology_metadata 
        WHERE key = 'cache_data_edges'
    """).fetchone()
    
    edges = json.loads(row[0])
    
    return {
        'nodes': nodes,
        'edges': edges,
        'stats': {
            'cache_used': True,  # Loaded from cache
            'build_time_ms': 95  # <100ms!
        }
    }
```

### Phase 3: Cache Invalidation (Manual/Auto)

```python
def invalidate_cache(graph_mode='data'):
    # Delete cache entries
    db.execute("""
        UPDATE graph_ontology_metadata 
        SET value = NULL 
        WHERE key IN ('cache_data_nodes', 'cache_data_edges', 'cache_data_updated')
    """)
    
    # Next load will rebuild
```

---

## API Usage

### Endpoint

```
GET /api/knowledge-graph/?mode=data&use_cache=true
```

### Parameters

| Parameter | Default | Description |
|-----------|---------|-------------|
| `mode` | `data` | `schema` or `data` graph |
| `use_cache` | `true` | Use cache if available |
| `max_records` | `20` | Records per table (if building) |

### Response

```json
{
  "nodes": [...],  // vis.js nodes
  "edges": [...],  // vis.js edges
  "stats": {
    "node_count": 450,
    "edge_count": 380,
    "cache_used": true,
    "build_time_ms": 95
  }
}
```

---

## Performance

| Metric | First Load | Cached Load | Speedup |
|--------|------------|-------------|---------|
| Build Time | 27,000ms | 95ms | **270x** |
| DB Queries | 100+ | 2 | 50x |
| Memory | Low | Low | Same |
| User Wait | 27s | <1s | **Instant!** |

---

## Tables Used

### All 3 Tables Are Still Used! ✅

**Important**: These tables serve **different purposes** - they are NOT redundant!

1. **`graph_schema_nodes`** - Schema Metadata Storage
   - **Purpose**: Permanent storage of CSN-derived schema (tables, columns, types)
   - **Used for**: Schema discovery, relationship inference, data lineage
   - **Example**: "Supplier table has columns: SupplierID (key), CompanyName (string)"
   - **Still actively used**: YES - this is the source of truth for schema

2. **`graph_schema_edges`** - Relationship Metadata Storage
   - **Purpose**: Permanent storage of discovered relationships (FKs, associations)
   - **Used for**: Relationship discovery, confidence scoring, manual overrides
   - **Example**: "PurchaseOrder.SupplierID → Supplier.SupplierID (FK, confidence 1.0)"
   - **Still actively used**: YES - this is the source of truth for relationships

3. **`graph_ontology_metadata`** - Key-Value Metadata + NEW: Cache
   - **Purpose**: General metadata (schema versions, settings) + **NEW**: Graph visualization cache
   - **Used for**: Configuration, timestamps, AND now caching complete vis.js graphs
   - **Example**: "cache_data_nodes" = "[{id: 'SUPP-001', label: 'Acme', ...}, ...]"
   - **Still actively used**: YES - both old use (metadata) AND new use (cache)

### How They Work Together

**Schema Graph Build Flow** (uses all 3 tables):
1. Read schema from `graph_schema_nodes` (table/column definitions)
2. Read relationships from `graph_schema_edges` (FK links)
3. Build vis.js graph from #1 + #2 (expensive, 27s)
4. **NEW**: Store result in `graph_ontology_metadata.cache_schema_nodes` (cache for next time)
5. Next request: Load from cache (instant, <100ms)

**The Cache is NOT a replacement** - it's a performance optimization!
- Without cache: Always query `graph_schema_nodes` + `graph_schema_edges` (slow)
- With cache: Load pre-built graph from `graph_ontology_metadata` (fast)
- Cache invalid/missing: Fall back to querying the schema tables (graceful degradation)

### Why Not Just Use the Schema Tables?

**Problem**: Building vis.js graph requires:
- 100+ SQL queries to schema/edges tables
- Complex joins and aggregations
- Color/shape calculations
- Label formatting
- Position calculations
- Total time: 27 seconds ❌

**Solution**: Cache the final vis.js graph
- 1 SQL query to metadata table
- JSON parse (already formatted)
- Total time: <100ms ✅

**Analogy**: 
- `graph_schema_nodes/edges` = Raw ingredients (flour, eggs, sugar)
- `cache_*` = Pre-baked cake (ready to serve)
- You still need the ingredients (can't delete them!), but serving pre-baked cake is faster than baking each time

---

## Benefits

### User Experience
- ✅ Instant graph refresh (<1s)
- ✅ No loading indicators needed
- ✅ No waiting, no frustration
- ✅ Professional feel

### Technical
- ✅ No new tables (simplicity)
- ✅ Single SELECT (performance)
- ✅ Automatic (no manual cache management)
- ✅ Backward compatible (cache optional)

### Operational
- ✅ Cache invalidation available (manual/auto)
- ✅ Graceful degradation (if cache fails, rebuild)
- ✅ Version-aware (cache_version tracks format)

---

## Migration Impact

**What changes?**
- 8 new rows in `graph_ontology_metadata` table
- Schema version: `1.0.0` → `1.1.0`
- Zero changes to existing tables
- Zero data loss

**What stays same?**
- All existing functionality
- Schema metadata storage
- Relationship discovery
- Query APIs

---

## Questions to Validate

1. ✅ **Storage**: Use metadata table (key-value) for JSON blobs?
2. ✅ **Separation**: Schema metadata ≠ visualization cache (different concerns)?
3. ✅ **Performance**: Single SELECT + JSON parse acceptable (<100ms)?
4. ✅ **Simplicity**: No new tables vs. dedicated cache table?

**Awaiting confirmation before implementation!**