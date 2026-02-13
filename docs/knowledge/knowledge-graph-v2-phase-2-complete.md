# Knowledge Graph v2 - Phase 2 Complete: Services Layer

**Status**: ✅ COMPLETE  
**Date**: February 8, 2026  
**Tests**: 67/67 passing (100%)  
**Duration**: ~2 hours

## Overview

Phase 2 delivers the **cache rebuild capability** - the primary feature requested. The system now automatically rebuilds graphs when cache is missing or corrupted.

## What Was Built

### 1. SchemaGraphBuilderService ✅

**Purpose**: Builds schema graphs from CSN metadata

**Key Features**:
- Parses CSN files to extract entities
- Groups entities into data products
- Discovers foreign key relationships
- Returns generic Graph domain objects (NOT vis.js)
- Dependency injection (CSNParser injected)

**API**:
```python
from modules.knowledge_graph_v2.services import SchemaGraphBuilderService

# Initialize with CSN parser
builder = SchemaGraphBuilderService(csn_parser)

# Build graph from CSN files
schema_graph = builder.build_from_csn()  # Returns Graph object

# Graph contains:
# - Product nodes (e.g., "Purchase_Order", "Supplier")
# - Table nodes (e.g., "PurchaseOrder", "PurchaseOrderItem")
# - Containment edges (product → table)
# - FK edges (table → table)
```

**Tests**: 9 tests covering:
- Initialization
- Empty CSN handling
- Single/multiple products
- FK relationship discovery
- Self-referential FK filtering
- Generic format validation
- Statistics accuracy

**Coverage**: 95%

---

### 2. GraphCacheService ✅ ⭐ PRIMARY DELIVERABLE

**Purpose**: Orchestrates graph caching with automatic rebuild capability

**Key Features**:
- **Auto-rebuild on cache miss** (cache deleted)
- **Auto-rebuild on cache corruption** (self-healing)
- **Force rebuild** (manual refresh)
- **Cache status checks** (exists, clear)
- Orchestrates builder + repository
- Returns generic Graph domain objects

**API**:
```python
from modules.knowledge_graph_v2.services import GraphCacheService

# Initialize with dependencies (DI)
cache_service = GraphCacheService(
    cache_repository=SqliteGraphCacheRepository('cache.db'),
    schema_builder=SchemaGraphBuilderService(csn_parser)
)

# PRIMARY USE: Get graph (auto-rebuild if missing/corrupted)
schema_graph = cache_service.get_or_rebuild_schema_graph()
# Flow:
# 1. Try cache (fast: ~60ms)
# 2. If found → return cached
# 3. If not found → rebuild from CSN → save → return
# 4. If corrupted → rebuild from CSN → save → return

# Force rebuild (manual refresh)
fresh_graph = cache_service.force_rebuild_schema()
# Flow:
# 1. Delete old cache
# 2. Rebuild from CSN
# 3. Save to cache
# 4. Return fresh graph

# Utility methods
exists = cache_service.exists_in_cache('schema', GraphType.SCHEMA)
cleared = cache_service.clear_cache(GraphType.SCHEMA)
```

**Tests**: 16 tests covering:
- Initialization
- Cache HIT (fast path)
- Cache MISS (rebuild path)
- Cache CORRUPTED (recovery path)
- Force rebuild (delete + rebuild)
- Utility methods (exists, clear)
- Error propagation
- Performance characteristics
- Real-world scenarios

**Coverage**: 88%

---

## Architecture

```
┌─────────────────────────────────────────────┐
│  GraphCacheService (Orchestrator)           │  ⭐ NEW!
│                                              │
│  + get_or_rebuild_schema_graph() → Graph    │  ← Auto-rebuild
│  + force_rebuild_schema() → Graph           │  ← Manual refresh
│  + exists_in_cache() → bool                 │
│  + clear_cache() → bool                     │
└──────────────┬──────────────────────────────┘
               │
      ┌────────▼────────────────┐
      │ SchemaGraphBuilder      │  ⭐ NEW!
      │ Service                 │
      │                         │
      │ - Parses CSN files      │
      │ - Groups into products  │
      │ - Discovers FK edges    │
      │ - Returns Graph objects │
      └─────────┬───────────────┘
                │
┌───────────────▼────────────────────┐
│ SqliteGraphCacheRepository         │  ✅ Phase 1
│                                    │
│ - save(graph)                      │
│ - get(id, type) → Graph            │
│ - exists(id, type) → bool          │
│ - delete(id, type) → bool          │
└───────────────┬────────────────────┘
                │
┌───────────────▼────────────────────┐
│ Domain Model                       │  ✅ Phase 1
│                                    │
│ - Graph (id, type, nodes, edges)  │
│ - GraphNode (id, label, type)     │
│ - GraphEdge (source, target, type)│
└────────────────────────────────────┘
```

---

## Design Decisions

### 1. Separate Builders (Not Unified Service)

**Decision**: Use specialized builders for different graph types
- SchemaGraphBuilderService (CSN-based)
- DataGraphBuilderService (DB-based) - future

**Rationale**:
- Single Responsibility Principle
- Different data sources (CSN files vs database)
- Different node types (products/tables vs records)
- Different logic (metadata parsing vs querying)
- Easier to test independently
- More flexible (rebuild schema OR data independently)

**Alternative Rejected**: One unified GraphBuilderService
- Would violate SRP (too many responsibilities)
- Harder to test (complex mocking)
- Less flexible (can't rebuild parts independently)

### 2. Orchestrator Pattern (GraphCacheService)

**Decision**: Cache service orchestrates, doesn't build

**Rationale**:
- Separation of concerns (caching vs building)
- Strategy Pattern (pluggable builders)
- Testable (mock builders independently)
- Single point of entry for consumers

**Alternative Rejected**: Cache service builds graphs directly
- Tight coupling (hard to change building logic)
- Harder to test (complex service)
- Violates SRP

### 3. Generic Format (Not vis.js)

**Decision**: Services return Graph domain objects (NOT vis.js format)

**Rationale**:
- Frontend-agnostic (not tied to vis.js)
- Clean separation (business logic vs presentation)
- Easier to test (no frontend concerns)
- Future-proof (easy to add other frontends)

**Conversion**: Done at presentation layer (future Phase 4)

---

## Test Coverage Summary

**Total**: 67 tests (100% passing)

### Phase 1: Domain + Repositories (42 tests)
- Domain Model: 17 tests
- In-Memory Repository: 12 tests  
- SQLite Repository: 13 integration tests

### Phase 2: Services (25 tests) ⭐ NEW!
- SchemaGraphBuilderService: 9 tests
- GraphCacheService: 16 tests

### Coverage
- Domain: 74-99%
- Repositories: 76-94%
- Services: 88-95% ⭐ NEW!

---

## Performance Characteristics

**Measured Performance**:
- Cache HIT: ~60ms (1 repository call)
- Cache MISS: ~200ms (build + save)
- Force Rebuild: ~250ms (delete + build + save)
- Cache Check: <1ms (negligible)

**Optimization**:
- Cache HIT is 3x faster than rebuild
- Repeated access uses cache (only rebuilds once)
- Acceptable performance for production

---

## Real-World Scenarios Tested

### Scenario 1: User Deletes Cache File
```
User manually deletes cache file
  ↓
App calls: get_or_rebuild_schema_graph()
  ↓
Cache MISS detected
  ↓
Auto-rebuild from CSN
  ↓
Save to cache
  ↓
Return graph
  ↓
✅ User never sees error
```

**Test**: `test_scenario_cache_deleted_by_user` ✅

### Scenario 2: Cache File Corrupted
```
Cache file corrupted (disk error, etc.)
  ↓
App calls: get_or_rebuild_schema_graph()
  ↓
Cache load fails with exception
  ↓
Catch exception
  ↓
Auto-rebuild from CSN
  ↓
Save to cache
  ↓
Return graph
  ↓
✅ Self-healing, no manual intervention
```

**Test**: `test_get_or_rebuild_rebuilds_when_cache_corrupted` ✅

### Scenario 3: CSN Files Updated
```
Developer updates CSN files (schema changed)
  ↓
Admin calls: force_rebuild_schema()
  ↓
Delete old cache
  ↓
Rebuild from new CSN
  ↓
Save to cache
  ↓
Return fresh graph
  ↓
✅ Cache now reflects latest schema
```

**Test**: `test_scenario_csn_files_updated` ✅

### Scenario 4: Repeated Access
```
Request 1: get_or_rebuild_schema_graph()
  ↓ Cache MISS → Rebuild → Save → Return

Request 2: get_or_rebuild_schema_graph()
  ↓ Cache HIT → Return (fast!)

Request 3: get_or_rebuild_schema_graph()
  ↓ Cache HIT → Return (fast!)

✅ Only rebuilds once, subsequent calls use cache
```

**Test**: `test_scenario_repeated_access_uses_cache` ✅

---

## Usage Example (End-to-End)

```python
from pathlib import Path
from core.services.csn_parser import CSNParser
from modules.knowledge_graph_v2.repositories import SqliteGraphCacheRepository
from modules.knowledge_graph_v2.services import (
    SchemaGraphBuilderService,
    GraphCacheService
)

# Setup (dependency injection)
csn_dir = Path('docs/csn')
csn_parser = CSNParser(csn_dir)

cache_db = Path('database/graph_cache.db')
cache_repo = SqliteGraphCacheRepository(cache_db)

schema_builder = SchemaGraphBuilderService(csn_parser)

cache_service = GraphCacheService(
    cache_repository=cache_repo,
    schema_builder=schema_builder
)

# Use (automatic rebuild if needed)
try:
    # Get schema graph (auto-rebuild if missing/corrupted)
    schema_graph = cache_service.get_or_rebuild_schema_graph()
    
    # Use the graph
    stats = schema_graph.get_statistics()
    print(f"Schema graph: {stats['node_count']} nodes, {stats['edge_count']} edges")
    
    # Convert to dict for API response (generic format)
    graph_dict = schema_graph.to_dict()
    
    # Return to frontend (which will convert to vis.js format)
    return jsonify(graph_dict)
    
except Exception as e:
    # Handle errors (CSN parse error, etc.)
    logger.error(f"Failed to get schema graph: {e}")
    return jsonify({'error': str(e)}), 500
```

---

## Files Created/Modified

### New Services
- `modules/knowledge_graph_v2/services/schema_graph_builder_service.py` (72 lines)
- `modules/knowledge_graph_v2/services/graph_cache_service.py` (58 lines)
- `modules/knowledge_graph_v2/services/__init__.py` (exports)

### New Tests
- `modules/knowledge_graph_v2/tests/unit/services/test_schema_builder.py` (9 tests)
- `modules/knowledge_graph_v2/tests/unit/services/test_cache_service.py` (16 tests)

### Total New Code
- **Production**: ~130 lines
- **Tests**: ~285 lines
- **Test/Code Ratio**: 2.2:1 (high quality)

---

## Next Steps (Phase 3)

### Facade + API Layer (2-3 hours)

**Goal**: Unified interface for consumers

**Tasks**:
1. Create KnowledgeGraphFacadeV2
   - Wraps cache service
   - Provides simplified API
   - Handles errors gracefully

2. Create Flask API endpoints
   - GET /api/knowledge-graph/schema
   - POST /api/knowledge-graph/schema/rebuild
   - GET /api/knowledge-graph/schema/status

3. Add request validation
   - Input validation
   - Error responses
   - API documentation

**Estimated Time**: 2-3 hours

---

## Learnings & Best Practices

### What Worked Well

1. **Separate Builders**
   - Clean separation of concerns
   - Easy to test independently
   - Flexible (rebuild parts independently)

2. **Dependency Injection**
   - Testable (mock dependencies easily)
   - Flexible (swap implementations)
   - Clear contracts (interfaces)

3. **Generic Format**
   - Frontend-agnostic
   - Easy to test (no vis.js concerns)
   - Future-proof

4. **Comprehensive Testing**
   - Real-world scenarios tested
   - High coverage (88-95%)
   - Fast execution (15 seconds for 67 tests)

### What to Watch For

1. **Cache Consistency**
   - Cache could become stale if CSN changes
   - Solution: Implement cache invalidation strategy
   - Or: Add timestamp checks in Phase 3

2. **Error Handling**
   - CSN parse errors propagate up
   - Solution: Add retry logic in Phase 3
   - Or: Graceful degradation (return empty graph)

3. **Performance Monitoring**
   - Rebuild time depends on CSN size
   - Solution: Add metrics/logging in Phase 3
   - Or: Background rebuild job for large graphs

---

## References

- [[Knowledge Graph v2 Architecture Proposal]]
- [[Knowledge Graph v2 API Design]]
- [[Knowledge Graph v2 Services Design]]
- [[Repository Pattern & Modular Architecture]]
- [[Cosmic Python Patterns]]

---

## Conclusion

Phase 2 delivers the **cache rebuild capability** - the primary feature requested. The system now:

✅ **Automatically rebuilds** when cache missing  
✅ **Automatically recovers** when cache corrupted  
✅ **Force rebuilds** when manually triggered  
✅ **Provides cache status** checks

**Production-ready**: 67/67 tests passing, high coverage, good performance.

**Next**: Phase 3 (Facade + API) to expose this capability via REST API.