# Full Graph Cache Implementation (v3.13)

**Created**: 2026-02-01  
**Priority**: HIGH  
**Estimated Effort**: 2-3 hours  
**Performance Impact**: 60x faster (27s → <500ms)

## Problem Statement

Currently, "Refresh Graph" in data mode takes 27 seconds because:
- ✅ FK relationships cached (4ms) - Working
- ❌ Nodes NOT cached (25+ seconds) - **Problem**
- ❌ Graph queried fresh every time - **Wasteful**

**User Expectation**: "Refresh Graph" should load cached graph instantly, not rebuild from scratch.

## Current Architecture (Incomplete Cache)

```
User clicks "Refresh Graph"
  ↓
Backend API: /api/knowledge-graph/?mode=data
  ↓
build_data_graph():
  ├─ Load FK relationships from cache (4ms) ✅ Fast
  ├─ Query all data products (5s) ❌ Slow
  ├─ Query all tables (8s) ❌ Slow
  ├─ Build nodes dynamically (12s) ❌ Slow
  └─ Create graph structure (2s)
  ↓
Total: 27 seconds ❌
```

## Target Architecture (Full Cache)

```
User clicks "Refresh Graph"
  ↓
Backend API: /api/knowledge-graph/?mode=data&use_cache=true
  ↓
Check cache validity:
  ├─ graph_schema_nodes exists? → Load nodes (50ms) ✅
  ├─ graph_schema_edges exists? → Load edges (4ms) ✅
  └─ Combine into graph (10ms) ✅
  ↓
Total: <100ms ✅ (270x faster!)
```

## Implementation Plan

### Phase 1: Extend OntologyPersistenceService (30 min)

**File**: `core/services/ontology_persistence_service.py`

Add methods for node caching:

```python
def persist_nodes(
    self, 
    nodes: List[Dict],
    mode: str  # 'schema' or 'data'
) -> int:
    """
    Cache graph nodes to database.
    
    Args:
        nodes: List of vis.js node objects
        mode: Graph mode (schema/data)
    
    Returns:
        Number of nodes persisted
    """
    conn = sqlite3.connect(self.db_path)
    cursor = conn.cursor()
    
    # Clear old nodes for this mode
    cursor.execute("""
        DELETE FROM graph_schema_nodes 
        WHERE graph_mode = ?
    """, (mode,))
    
    # Insert new nodes
    for node in nodes:
        cursor.execute("""
            INSERT INTO graph_schema_nodes (
                node_id, label, node_type, graph_mode,
                metadata_json, visual_properties_json
            ) VALUES (?, ?, ?, ?, ?, ?)
        """, (
            node['id'],
            node['label'],
            node.get('group', 'unknown'),
            mode,
            json.dumps(node),  # Store complete node
            json.dumps({
                'color': node.get('color'),
                'shape': node.get('shape'),
                'size': node.get('size')
            })
        ))
    
    conn.commit()
    conn.close()
    
    return len(nodes)

def get_cached_nodes(self, mode: str) -> List[Dict]:
    """
    Load cached nodes from database.
    
    Args:
        mode: Graph mode (schema/data)
    
    Returns:
        List of vis.js node objects
    """
    conn = sqlite3.connect(self.db_path)
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT metadata_json
        FROM graph_schema_nodes
        WHERE graph_mode = ?
        ORDER BY node_id
    """, (mode,))
    
    rows = cursor.fetchall()
    conn.close()
    
    return [json.loads(row[0]) for row in rows]

def is_graph_cache_valid(self, mode: str) -> bool:
    """Check if complete graph cache exists"""
    conn = sqlite3.connect(self.db_path)
    cursor = conn.cursor()
    
    # Check nodes exist
    cursor.execute("""
        SELECT COUNT(*) 
        FROM graph_schema_nodes 
        WHERE graph_mode = ?
    """, (mode,))
    node_count = cursor.fetchone()[0]
    
    # Check edges exist
    cursor.execute("SELECT COUNT(*) FROM graph_schema_edges")
    edge_count = cursor.fetchone()[0]
    
    conn.close()
    
    return node_count > 0 and edge_count > 0
```

### Phase 2: Modify DataGraphService (45 min)

**File**: `modules/knowledge_graph/backend/data_graph_service.py`

Add cache-first logic to `build_data_graph()`:

```python
def build_data_graph(
    self,
    mode: str = 'data',
    max_records: int = 20,
    use_cache: bool = True  # NEW parameter
) -> Dict:
    """Build data-level knowledge graph (with optional caching)"""
    
    import time
    start_time = time.time()
    
    # PHASE 1: Try cached graph first (if requested)
    if use_cache and self.db_path:
        persistence = OntologyPersistenceService(self.db_path)
        
        if persistence.is_graph_cache_valid(mode):
            logger.info(f"✓ Using cached graph ({mode} mode)")
            
            # Load cached nodes & edges
            nodes = persistence.get_cached_nodes(mode)
            edges = self._get_cached_edges_as_visjs(persistence)
            
            cache_time = (time.time() - start_time) * 1000
            logger.info(f"✓ Cache load: {cache_time:.0f}ms (270x faster!)")
            
            return {
                'nodes': nodes,
                'edges': edges,
                'stats': self._calculate_stats(nodes, edges),
                'cache_used': True,
                'load_time_ms': cache_time
            }
    
    # PHASE 2: Build graph from scratch (cache miss or disabled)
    logger.info(f"Building fresh graph ({mode} mode)...")
    
    # ... existing build logic ...
    nodes = []
    edges = []
    
    # ... query data products, build nodes, etc. ...
    
    # PHASE 3: Cache the built graph for next time
    if self.db_path:
        persistence = OntologyPersistenceService(self.db_path)
        node_count = persistence.persist_nodes(nodes, mode)
        logger.info(f"✓ Cached {node_count} nodes for next request")
    
    build_time = (time.time() - start_time) * 1000
    logger.info(f"✓ Fresh build: {build_time:.0f}ms")
    
    return {
        'nodes': nodes,
        'edges': edges,
        'stats': self._calculate_stats(nodes, edges),
        'cache_used': False,
        'load_time_ms': build_time
    }
```

### Phase 3: Update API Endpoint (15 min)

**File**: `modules/knowledge_graph/backend/api.py`

Add `use_cache` parameter:

```python
@knowledge_graph_api.route('/', methods=['GET'])
def get_knowledge_graph():
    """Get knowledge graph data"""
    source = request.args.get('source', 'sqlite')
    mode = request.args.get('mode', 'schema')
    use_cache = request.args.get('use_cache', 'true').lower() == 'true'
    
    # ... existing code ...
    
    if mode == 'schema':
        result = service.build_schema_graph()
    else:
        result = service.build_data_graph(
            mode='data',
            max_records=max_records,
            use_cache=use_cache  # Pass through
        )
    
    return jsonify({
        'success': True,
        'nodes': result['nodes'],
        'edges': result['edges'],
        'stats': result['stats'],
        'cache_used': result.get('cache_used', False),
        'load_time_ms': result.get('load_time_ms')
    })
```

### Phase 4: Add Cache Invalidation (30 min)

**When to invalidate cache**:
- New data products added
- Schema changes detected
- Manual "Refresh Cache" button clicked

**Implementation**:

```python
# In OntologyPersistenceService
def invalidate_cache(self, mode: str = None):
    """Clear cached graph"""
    conn = sqlite3.connect(self.db_path)
    cursor = conn.cursor()
    
    if mode:
        cursor.execute("""
            DELETE FROM graph_schema_nodes 
            WHERE graph_mode = ?
        """, (mode,))
    else:
        cursor.execute("DELETE FROM graph_schema_nodes")
        cursor.execute("DELETE FROM graph_schema_edges")
    
    conn.commit()
    conn.close()
```

### Phase 5: Testing & Validation (30 min)

**Test Cases**:
1. ✅ First load (no cache) → builds fresh, caches result
2. ✅ Second load (with cache) → loads from cache (<100ms)
3. ✅ Cache invalidation → rebuilds fresh
4. ✅ Schema mode vs Data mode → separate caches
5. ✅ Performance comparison: cache vs no-cache

**Performance Targets**:
- Cache hit: <100ms (vs 27,000ms = 270x faster)
- Cache miss: ~27s (builds + caches for next time)
- Cache invalidation: <50ms

## Database Schema (Already Exists)

```sql
CREATE TABLE graph_schema_nodes (
    node_id TEXT PRIMARY KEY,
    label TEXT NOT NULL,
    node_type TEXT,
    graph_mode TEXT CHECK(graph_mode IN ('schema', 'data')),
    metadata_json TEXT,
    visual_properties_json TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_graph_mode ON graph_schema_nodes(graph_mode);
```

## Benefits

### Performance
- **270x faster** repeated loads (<100ms vs 27s)
- Reduces server load (no repeated queries)
- Better user experience (instant refresh)

### Architecture
- Proper separation: build once, load many times
- Cache invalidation on schema changes
- Supports multiple graph modes independently

### User Experience
- "Refresh Graph" button: Instant (uses cache)
- "Refresh Cache" button: Rebuilds (updates cache)
- Visual feedback: "Loaded from cache (64ms)"

## Risks & Mitigations

### Risk 1: Stale Cache
**Problem**: Cache not updated after data changes  
**Mitigation**: Auto-invalidate on schema changes, manual "Refresh Cache" button

### Risk 2: Cache Size
**Problem**: Large graphs = large cache  
**Mitigation**: JSON compression, TTL-based cleanup

### Risk 3: Mode Confusion
**Problem**: Schema cache loaded for data mode  
**Mitigation**: Separate caches by `graph_mode` column

## Success Criteria

- ✅ "Refresh Graph" loads in <100ms (cache hit)
- ✅ "Refresh Cache" rebuilds fresh (~27s)
- ✅ Schema & Data modes cached independently
- ✅ Cache auto-invalidates on data changes
- ✅ User feedback shows cache status

## Future Enhancements (v3.14+)

- **Smart Cache**: Only rebuild changed nodes
- **Compression**: Store nodes as compressed JSON
- **TTL**: Auto-expire cache after 24h
- **Preloading**: Build cache in background on startup

## Implementation Checklist

- [ ] Extend OntologyPersistenceService with node methods
- [ ] Modify build_data_graph() with cache-first logic
- [ ] Update API endpoint with use_cache parameter
- [ ] Add cache invalidation logic
- [ ] Test performance (cache vs no-cache)
- [ ] Update frontend to show cache status
- [ ] Document in knowledge vault
- [ ] Commit with v3.13 tag

---

**Estimated ROI**: 2-3 hours work → 270x performance improvement → Major UX win! 🚀