# Graph Cache Architecture - Clean Design

**Author**: User  
**Date**: 2026-02-01

---

## Core Concept

**Pre-compute and store graph structure** (nodes + edges) in database tables, then **translate on-demand** to vis.js format.

---

## Database Schema

### 3 Tables with Foreign Keys

```sql
-- Ontology: Defines graph type (schema vs data)
CREATE TABLE graph_ontology (
    ontology_id INTEGER PRIMARY KEY,
    graph_type TEXT NOT NULL,  -- 'schema' or 'data'
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Nodes: Stored in normalized form
CREATE TABLE graph_nodes (
    node_id INTEGER PRIMARY KEY,
    ontology_id INTEGER NOT NULL,  -- FK to graph_ontology
    node_key TEXT NOT NULL,         -- Business key (e.g., 'SUPP-001')
    node_label TEXT,
    node_type TEXT,
    properties_json TEXT,           -- Additional properties as JSON
    FOREIGN KEY (ontology_id) REFERENCES graph_ontology(ontology_id) ON DELETE CASCADE
);

-- Edges: Relationships between nodes
CREATE TABLE graph_edges (
    edge_id INTEGER PRIMARY KEY,
    ontology_id INTEGER NOT NULL,  -- FK to graph_ontology
    from_node_key TEXT NOT NULL,
    to_node_key TEXT NOT NULL,
    edge_type TEXT,
    properties_json TEXT,           -- Additional properties as JSON
    FOREIGN KEY (ontology_id) REFERENCES graph_ontology(ontology_id) ON DELETE CASCADE
);
```

**Benefits**:
- ✅ Normalized (no redundancy)
- ✅ Cascade delete (delete ontology → auto-delete nodes/edges)
- ✅ Flexible (properties_json for vis.js-specific data)

---

## Services

### 1. CacheBuilder Service

**Purpose**: Build/rebuild graph cache from source data

**For Schema Graph**:
```python
def rebuild_schema_graph():
    # 1. Query CSN metadata (tables, columns, relationships)
    # 2. Create ontology record
    ontology_id = insert("graph_ontology", {"graph_type": "schema"})
    
    # 3. Populate graph_nodes (one per table)
    for table in csn_tables:
        insert("graph_nodes", {
            "ontology_id": ontology_id,
            "node_key": table.name,
            "node_label": table.label,
            "node_type": "table",
            "properties_json": json.dumps({"color": "blue", "shape": "box"})
        })
    
    # 4. Populate graph_edges (relationships)
    for relationship in csn_relationships:
        insert("graph_edges", {
            "ontology_id": ontology_id,
            "from_node_key": relationship.source,
            "to_node_key": relationship.target,
            "edge_type": "foreign_key"
        })
    
    # Takes ~27s, but only done once or on "Refresh Cache"
```

**For Data Graph**: Similar, but source = actual data records (Suppliers, POs, etc.)

---

### 2. VisJsTranslator Service

**Purpose**: Fast translation from cache to vis.js format

```python
def get_visjs_graph(graph_type='schema'):
    # 1. Get ontology
    ontology = select("graph_ontology WHERE graph_type = ?", [graph_type])
    
    # 2. Load nodes (simple query)
    nodes_rows = select("graph_nodes WHERE ontology_id = ?", [ontology.id])
    
    # 3. Transform to vis.js format
    visjs_nodes = []
    for row in nodes_rows:
        props = json.loads(row.properties_json)
        visjs_nodes.append({
            "id": row.node_key,
            "label": row.node_label,
            "color": props.get("color"),
            "shape": props.get("shape")
        })
    
    # 4. Load edges
    edges_rows = select("graph_edges WHERE ontology_id = ?", [ontology.id])
    visjs_edges = [{"from": e.from_node_key, "to": e.to_node_key} for e in edges_rows]
    
    return {"nodes": visjs_nodes, "edges": visjs_edges}
    
    # Takes <1s (simple SELECT + JSON parse)
```

---

## User Workflows

### Workflow 1: Switch Between Graph Modes

**User clicks**: "Schema" → "Data" (toggle in UI)

```
User Action: Toggle to "Data" graph
    ↓
API Call: GET /api/graph?type=data
    ↓
VisJsTranslator.get_visjs_graph('data')
    ↓
SELECT from graph_nodes/edges WHERE ontology.graph_type='data'
    ↓
Transform to vis.js format (<1s)
    ↓
Return to UI → Render
```

**Fast**: No rebuilding, just query + transform

---

### Workflow 2: Refresh Graph (Use Existing Cache)

**User clicks**: "Refresh Graph"

```
User Action: Refresh button
    ↓
API Call: GET /api/graph?type=data
    ↓
Same as Workflow 1 (uses existing cache)
    ↓
Return to UI → Render (<1s)
```

**Fast**: Same as switching modes (cache already exists)

---

### Workflow 3: Refresh Cache (Rebuild)

**User clicks**: "Refresh Cache" (new button)

```
User Action: "Refresh Cache" button
    ↓
API Call: POST /api/graph/rebuild?type=data
    ↓
CacheBuilder.rebuild_data_graph()
    ↓
DELETE from graph_ontology WHERE graph_type='data'
  (cascade deletes nodes/edges automatically)
    ↓
Rebuild from source data (27s)
    ↓
INSERT new ontology + nodes + edges
    ↓
Return success
    ↓
UI automatically calls GET /api/graph?type=data
    ↓
Display updated graph
```

**Slow**: 27s, but only when explicitly requested

---

## Performance

| Action | Old (No Cache) | New (With Cache) | Speedup |
|--------|----------------|------------------|---------|
| Switch Mode | 27s | <1s | 27x |
| Refresh Graph | 27s | <1s | 27x |
| Refresh Cache | N/A | 27s | One-time cost |

---

## Benefits

1. **Clean Separation**
   - Cache storage (normalized tables)
   - Presentation logic (vis.js translation)

2. **Flexibility**
   - Can change vis.js format without invalidating cache
   - Just update VisJsTranslator logic

3. **Efficient**
   - Simple SELECTs (no complex joins)
   - Minimal transformation overhead

4. **Maintainable**
   - Cascade deletes (auto-cleanup)
   - Clear responsibilities (2 services)

---

## API Endpoints

```
GET  /api/graph?type=schema|data
     → Returns vis.js graph (fast, uses cache)

POST /api/graph/rebuild?type=schema|data
     → Rebuilds cache (slow, 27s)

GET  /api/graph/status?type=schema|data
     → Returns cache metadata (last_updated, node_count, etc.)
```

---

## Migration Strategy

**Current State**: Tables `graph_schema_nodes`, `graph_schema_edges`, `graph_ontology_metadata` exist

**Option A**: Keep existing, add new cache tables
- Keep: `graph_schema_nodes/edges` (relationship discovery, not visualization)
- Add: `graph_ontology`, `graph_nodes`, `graph_edges` (visualization cache)

**Option B**: Rename existing tables
- Rename: `graph_schema_nodes` → `csn_schema_nodes` (clarify purpose)
- Create: `graph_ontology`, `graph_nodes`, `graph_edges` (clean start)

**Recommendation**: Option B (clean separation of concerns)

---

## Questions

1. ✅ Is this design cleaner than the previous JSON blob approach?
2. ✅ Does the Foreign Key cascade make sense?
3. ✅ Are 2 services (CacheBuilder + VisJsTranslator) clear?
4. ✅ Should we add "Refresh Cache" button in UI?

**Ready to implement?**