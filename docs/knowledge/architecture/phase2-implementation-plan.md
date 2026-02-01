# Phase 2 Implementation Plan

**Status**: Ready to implement  
**Approach**: Option A (Minimal refactor)

---

## Changes Required

### 1. Create GraphCacheService (NEW)

**File**: `core/services/graph_cache_service.py`

**Purpose**: Helper to save/load graph cache

```python
class GraphCacheService:
    def __init__(self, db_path):
        self.db_path = db_path
    
    def save_graph(self, nodes, edges, graph_type='data'):
        """Save graph to cache (creates ontology + nodes + edges)"""
        # 1. Delete old ontology (CASCADE deletes nodes/edges)
        # 2. INSERT new ontology
        # 3. INSERT nodes with properties_json
        # 4. INSERT edges with properties_json
    
    def clear_cache(self, graph_type='data'):
        """Delete cache for graph type"""
        # DELETE from graph_ontology WHERE graph_type = ?
```

---

### 2. Update DataGraphService (MODIFY)

**File**: `modules/knowledge_graph/backend/data_graph_service.py`

**Add at end of `build_schema_graph()` and `build_data_graph()`**:

```python
# NEW: Save to cache (Phase 2)
if self.db_path and nodes:
    try:
        from core.services.graph_cache_service import GraphCacheService
        cache = GraphCacheService(self.db_path)
        cache.save_graph(nodes, edges, graph_type='schema')  # or 'data'
        logger.info(f"✓ Saved {len(nodes)} nodes to cache")
    except Exception as e:
        logger.warning(f"Cache save failed: {e}")
```

---

### 3. Update API Endpoint (MODIFY)

**File**: `modules/knowledge_graph/backend/api.py`

**Current**:
```python
@knowledge_graph_api.route('/', methods=['GET'])
def get_knowledge_graph():
    mode = request.args.get('mode', 'schema')
    
    if mode == 'schema':
        result = data_graph_service.build_schema_graph()
    else:
        result = data_graph_service.build_data_graph()
```

**NEW**:
```python
@knowledge_graph_api.route('/', methods=['GET'])
def get_knowledge_graph():
    mode = request.args.get('mode', 'schema')
    use_cache = request.args.get('use_cache', 'true').lower() == 'true'
    
    # Try cache first
    if use_cache:
        from core.services.visjs_translator import VisJsTranslator
        translator = VisJsTranslator(current_app.config.get('DATABASE_PATH'))
        graph = translator.get_visjs_graph(mode)
        
        if graph['stats'].get('cache_exists'):
            return jsonify(graph)
    
    # Cache miss - build from scratch
    if mode == 'schema':
        result = data_graph_service.build_schema_graph()
    else:
        result = data_graph_service.build_data_graph()
```

---

### 4. Add Rebuild Endpoint (NEW)

**File**: `modules/knowledge_graph/backend/api.py`

```python
@knowledge_graph_api.route('/rebuild', methods=['POST'])
def rebuild_cache():
    """Rebuild graph cache (triggered by 'Refresh Cache' button)"""
    mode = request.args.get('mode', 'data')
    
    # Clear existing cache
    from core.services.graph_cache_service import GraphCacheService
    cache = GraphCacheService(current_app.config.get('DATABASE_PATH'))
    cache.clear_cache(mode)
    
    # Rebuild
    if mode == 'schema':
        result = data_graph_service.build_schema_graph()
    else:
        result = data_graph_service.build_data_graph()
    
    return jsonify(result)
```

---

## Implementation Order

1. ✅ Create `GraphCacheService` (50 lines)
2. ✅ Add cache save to `DataGraphService` (10 lines in 2 places)
3. ✅ Update API endpoint (20 lines)
4. ✅ Add rebuild endpoint (15 lines)
5. ✅ Test: Build graph → saves cache
6. ✅ Test: Refresh graph → loads cache (<1s)
7. ✅ Test: Rebuild → clears + rebuilds

**Total code**: ~95 lines  
**Risk**: Low (minimal changes to existing code)

---

## Testing Plan

```bash
# 1. Build graph (first time - slow)
GET /api/knowledge-graph/?mode=data
# Expected: 27s, saves to cache

# 2. Refresh graph (cached - fast)
GET /api/knowledge-graph/?mode=data&use_cache=true
# Expected: <1s, loads from cache

# 3. Check cache status
python -c "from core.services.visjs_translator import VisJsTranslator; \
           t = VisJsTranslator('app/database/p2p_data_products.db'); \
           print(t.check_cache_status('data'))"

# 4. Rebuild cache
POST /api/knowledge-graph/rebuild?mode=data
# Expected: 27s, clears + rebuilds

# 5. Verify cache updated
GET /api/knowledge-graph/?mode=data&use_cache=true
# Expected: <1s, new cache
```

---

## Next Steps

**Ready to implement?** If approved, I'll:
1. Create GraphCacheService
2. Add cache saves to DataGraphService  
3. Update API endpoints
4. Test all workflows
5. Commit

**Estimate**: 30 minutes implementation + 15 minutes testing