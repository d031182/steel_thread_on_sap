# Cache System Consolidation Plan

**Status**: APPROVED - Ready for Implementation  
**Priority**: HIGH - Prevents redundant table creation  
**Created**: 2026-02-01  
**Issue**: Two parallel cache systems create 6 tables instead of 3

---

## Problem Statement

### Current State (Redundant Architecture)

**System 1: OntologyPersistenceService (LEGACY)**
- File: `core/services/ontology_persistence_service.py`
- Tables: `graph_schema_nodes`, `graph_schema_edges`, `graph_ontology_metadata`
- Purpose: Original cache system (pre-v3.13)

**System 2: GraphCacheService (CURRENT)**
- File: `core/services/graph_cache_service.py`
- Tables: `graph_ontology`, `graph_nodes`, `graph_edges`
- Purpose: Unified cache design (v3.13+)

**Problem**: Both systems run simultaneously = **6 tables created** (100% redundant)

---

## Files Requiring Changes

### 1. modules/knowledge_graph/backend/data_graph_builder.py ⚠️ CRITICAL
**Lines 218-241**: PHASE 1 cache loading uses `OntologyPersistenceService`
```python
# REMOVE THIS (lines 218-241):
from core.services.ontology_persistence_service import OntologyPersistenceService
persistence = OntologyPersistenceService(self.db_path)
if persistence.is_graph_cache_valid('data'):
    nodes = persistence.get_cached_graph_nodes('data')
```

**REPLACE WITH**:
```python
# Use GraphCacheService instead:
from core.services.graph_cache_service import GraphCacheService
cache = GraphCacheService(self.db_path)
cached_graph = cache.load_graph(graph_type='data')
if cached_graph and cached_graph.get('nodes'):
    return cached_graph
```

**Lines 394-401**: Already uses GraphCacheService correctly (keep as-is)

---

### 2. modules/knowledge_graph/backend/graph_builder_base.py
**Search for**: `OntologyPersistenceService` imports/usage
**Action**: Remove all references, ensure FK discovery doesn't depend on it

---

### 3. modules/knowledge_graph/backend/api.py
**Lines with**: `from core.services.ontology_persistence_service`
**Action**: 
- Remove imports
- Replace `persistence.get_statistics()` with GraphCacheService equivalent
- Update clear_cache endpoint

---

### 4. core/services/networkx_graph_query_engine.py
**Issue**: Queries `graph_schema_edges` table directly
**Action**: Update to query `graph_edges` table instead
**Lines**: Search for `graph_schema_edges` references

---

### 5. scripts/python/init_graph_ontology_schema.py
**Purpose**: Creates OLD schema
**Action**: Update to create NEW schema (graph_ontology/nodes/edges only)
**OR**: Delete if no longer needed (GraphCacheService auto-creates tables)

---

## Implementation Steps

### Phase 1: Code Cleanup (No Database Impact)
1. ✅ Remove `OntologyPersistenceService` imports from data_graph_builder.py
2. ✅ Replace cache loading logic with GraphCacheService
3. ✅ Remove imports from graph_builder_base.py
4. ✅ Remove imports from api.py
5. ✅ Update networkx_graph_query_engine.py to use new tables

### Phase 2: File Deletion
6. ✅ Delete `core/services/ontology_persistence_service.py` (780 lines)
7. ✅ Update/delete `scripts/python/init_graph_ontology_schema.py`
8. ✅ Remove references from migration scripts

### Phase 3: Testing
9. ✅ Test schema graph loading (should use graph_ontology/nodes/edges)
10. ✅ Test data graph loading (should use graph_ontology/nodes/edges)
11. ✅ Verify only 3 tables created (not 6)
12. ✅ Test graph clearing/refresh
13. ✅ Test API endpoints

### Phase 4: Cleanup Scripts
14. ✅ Create migration script for existing deployments
15. ✅ Add deprecation warnings if old tables detected
16. ✅ Document the change

---

## Testing Checklist

### Before Implementation
- [x] Database is empty (0 tables) - CONFIRMED
- [x] No existing deployments to migrate - CLEAN SLATE

### After Implementation
- [ ] Load schema graph → Check 3 tables created (graph_ontology, graph_nodes, graph_edges)
- [ ] Load data graph → Check no additional tables
- [ ] Clear cache → Verify tables empty but not deleted
- [ ] Refresh graph → Verify cache updates correctly
- [ ] Check logs → No OntologyPersistenceService references

---

## Expected Benefits

### Performance
- ✅ **50% fewer tables** (3 instead of 6)
- ✅ **No redundant writes** (single save operation)
- ✅ **Simpler queries** (no cross-system logic)

### Maintainability
- ✅ **Single source of truth** (GraphCacheService only)
- ✅ **Cleaner code** (remove 780 lines of legacy)
- ✅ **No confusion** (which cache is "real"?)

### Architecture
- ✅ **Unified design** (consistent with v3.13+ approach)
- ✅ **Future-proof** (remove technical debt early)
- ✅ **Easier HANA migration** (single cache interface)

---

## Rollback Plan

**If issues occur**:
1. Git revert to previous commit
2. Restore `ontology_persistence_service.py` from backup
3. Re-add imports to affected files
4. Run migration script if needed

**Risk Level**: LOW (database is currently empty, no data loss possible)

---

## Timeline

**Estimated Effort**: 2-3 hours
- Code changes: 1 hour
- Testing: 1 hour
- Documentation: 30 minutes

**Best Time**: NOW (database is empty, perfect timing)

---

## Code Snippets for Implementation

### data_graph_builder.py - PHASE 1 Replacement

**REMOVE** (lines 218-241):
```python
if use_cache and self.db_path:
    from core.services.ontology_persistence_service import OntologyPersistenceService
    persistence = OntologyPersistenceService(self.db_path)
    
    if persistence.is_graph_cache_valid('data'):
        logger.info("✓ Using cached data graph (nodes + edges)")
        nodes = persistence.get_cached_graph_nodes('data')
        # ... rest of old logic
```

**ADD**:
```python
if use_cache and self.db_path:
    try:
        from core.services.graph_cache_service import GraphCacheService
        cache = GraphCacheService(self.db_path)
        
        cached_graph = cache.load_graph(graph_type='data')
        
        if cached_graph and cached_graph.get('nodes'):
            cache_time = (time.time() - start_time) * 1000
            logger.info(f"✓ Using cached data graph ({len(cached_graph['nodes'])} nodes, {cache_time:.0f}ms)")
            
            return {
                'success': True,
                'nodes': cached_graph['nodes'],
                'edges': cached_graph.get('edges', []),
                'stats': {
                    'node_count': len(cached_graph['nodes']),
                    'edge_count': len(cached_graph.get('edges', [])),
                    'table_count': len(set(n.get('metadata', {}).get('table_name') for n in cached_graph['nodes'] if 'metadata' in n)),
                    'cache_used': True,
                    'load_time_ms': cache_time
                }
            }
        else:
            logger.info("Cache miss - building data graph from scratch")
    
    except Exception as e:
        logger.warning(f"Cache load failed: {e} - building from scratch")
```

---

## Success Criteria

✅ **Code**: No `OntologyPersistenceService` references remain  
✅ **Database**: Only 3 tables created (graph_ontology, graph_nodes, graph_edges)  
✅ **Functionality**: Both graph modes work correctly  
✅ **Performance**: Cache loading still fast (<50ms)  
✅ **Tests**: All existing tests pass  

---

## Next Actions

1. **User Approval**: ✅ APPROVED ("please proceed")
2. **Implementation**: Start with data_graph_builder.py
3. **Testing**: Verify each file change
4. **Commit**: Single atomic commit with all changes
5. **Documentation**: Update architecture docs

---

**Ready to implement**: This plan eliminates redundancy and future-proofs the cache architecture.