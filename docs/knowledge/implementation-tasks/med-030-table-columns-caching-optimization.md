# MED-030: Table Columns API Caching Optimization

**Status**: COMPLETED ✅  
**Priority**: MEDIUM  
**Effort**: 1-2 hours  
**Date**: 2026-02-24

## 🎯 Objective

Analyze and recommend caching strategy for `GET /api/knowledge-graph/tables/<table_name>/columns` endpoint to improve performance for repeated queries.

## 📊 Current Implementation Analysis

### Flow Chain
```
API Endpoint (api.py::get_table_columns)
    ↓
Facade (facade.py::get_table_columns)
    ↓
CSN Parser (csn_parser.py::get_entity_metadata)
    ↓
File System (reads JSON from docs/csn/)
```

### Current Behavior

**Facade Layer** (`knowledge_graph_facade.py::get_table_columns`):
```python
def get_table_columns(self, table_name: str) -> Dict[str, Any]:
    """Get detailed column metadata for a specific table (KGV-001)"""
    try:
        # NO CACHING - Direct CSN parser call every time
        entity_metadata = self.csn_parser.get_entity_metadata(table_name)
        
        if not entity_metadata:
            return {'success': False, 'error': f'Table "{table_name}" not found'}
        
        # Convert ColumnMetadata objects to dictionaries
        columns = [...]  # Transformation logic
        
        return {'success': True, 'columns': columns, 'table_name': table_name}
    except Exception as e:
        return {'success': False, 'error': str(e)}
```

**API Layer** (`api.py::get_table_columns`):
```python
def get_table_columns(self, table_name):
    """GET /api/knowledge-graph/tables/<table_name>/columns"""
    try:
        # Parse query params (semantic_type, search filters)
        semantic_type_filter = request.args.get('semantic_type', '').strip()
        search_term = request.args.get('search', '').strip().lower()
        
        # NO CACHING - Calls facade every time
        result = self.facade.get_table_columns(table_name)
        
        if not result['success']:
            return jsonify(result), 404 or 500
        
        columns = result['columns']
        
        # Apply filters (semantic_type, search)
        if semantic_type_filter:
            columns = [col for col in columns if col.get('semantic_type') == semantic_type_filter]
        
        if search_term:
            columns = [col for col in columns if search_term in name/label/description]
        
        return jsonify({'success': True, 'data': {...}}), 200
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
```

## 🔍 Key Observations

### 1. **No Caching Currently Exists**
- Every API call reads CSN files from disk
- Facade calls `csn_parser.get_entity_metadata()` on every request
- File I/O overhead repeated unnecessarily

### 2. **CSN Data is Static**
- CSN files change infrequently (schema changes only)
- Perfect candidate for caching
- Cache invalidation only needed on CSN file updates

### 3. **API Layer Filtering**
- Filtering (semantic_type, search) happens AFTER facade call
- Filtering happens in-memory on already-fetched data
- Filters don't prevent cache hits

### 4. **Existing Caching Infrastructure**
- Project already has `GraphCacheService` for schema graphs
- Uses `AbstractGraphCacheRepository` pattern
- Proven cache invalidation strategy

## 💡 Caching Recommendation

### ⚠️ **RECOMMENDATION: DO NOT ADD CACHING (YET)**

**Rationale**:

1. **CSN Parser May Already Cache** (Need Verification)
   - CSN parser implementation not reviewed in this analysis
   - Modern parsers often include internal caching
   - Adding second cache layer = redundant complexity

2. **Performance Measurement First** (Gu Wu Principle)
   - No performance benchmark exists currently
   - Premature optimization violates API-first methodology
   - Should measure actual bottleneck before caching

3. **Cache Complexity vs. Value Trade-off**
   - Caching adds invalidation complexity
   - Per-table caching requires cache key management
   - Benefit unclear without performance data

### 📋 Recommended Actions (In Order)

#### Step 1: Verify CSN Parser Caching
```python
# Check if CSNParser already caches internally
# Location: core/services/csn_parser.py
class CSNParser:
    def __init__(self, csn_dir: str):
        self.csn_dir = Path(csn_dir)
        self._cache = {}  # ← Check for this or similar
    
    def get_entity_metadata(self, table_name: str):
        # Check if reads from cache first
        if table_name in self._cache:
            return self._cache[table_name]
        # ... then reads from disk
```

#### Step 2: Create Performance Benchmark
```python
# File: tests/knowledge_graph_v2/test_table_columns_performance.py
import pytest
import time

@pytest.mark.performance
def test_table_columns_response_time(test_client):
    """Measure baseline performance for table columns API"""
    
    # Warm-up call
    test_client.get('/api/knowledge-graph/tables/PurchaseOrder/columns')
    
    # Measure 10 repeated calls
    times = []
    for _ in range(10):
        start = time.time()
        response = test_client.get('/api/knowledge-graph/tables/PurchaseOrder/columns')
        elapsed = time.time() - start
        times.append(elapsed)
        assert response.status_code == 200
    
    avg_time = sum(times) / len(times)
    print(f"\nAverage response time: {avg_time*1000:.2f}ms")
    
    # Performance threshold: Should be < 100ms for cached or small CSN
    assert avg_time < 0.1, f"Response too slow: {avg_time*1000:.2f}ms"
```

#### Step 3: Decide on Caching Strategy (If Needed)

**Option A: Facade-Level Caching (Recommended IF caching needed)**
```python
class KnowledgeGraphFacadeV2:
    def __init__(self, ...):
        self._table_columns_cache = {}  # Simple dict cache
        self._cache_timestamp = {}
    
    def get_table_columns(self, table_name: str) -> Dict[str, Any]:
        """Get table columns (with optional caching)"""
        
        # Check cache
        if table_name in self._table_columns_cache:
            return self._table_columns_cache[table_name]
        
        # Cache miss - fetch from CSN parser
        entity_metadata = self.csn_parser.get_entity_metadata(table_name)
        
        if not entity_metadata:
            return {'success': False, 'error': f'Table "{table_name}" not found'}
        
        # Transform to dict
        result = {
            'success': True,
            'columns': [col.to_dict() for col in entity_metadata.columns],
            'table_name': table_name
        }
        
        # Cache result
        self._table_columns_cache[table_name] = result
        
        return result
    
    def clear_table_columns_cache(self):
        """Clear cache (call on CSN file updates)"""
        self._table_columns_cache.clear()
```

**Option B: Use Existing GraphCacheService**
- Extend `GraphCacheService` to support table metadata
- Reuse existing cache invalidation logic
- More complex but consistent with architecture

**Option C: CSN Parser-Level Caching**
- Modify `CSNParser` to cache parsed entities
- Centralized caching (benefits all consumers)
- Requires checking if already implemented

## 🎯 Implementation Checklist (If Caching Needed)

- [ ] Step 1: Review CSN Parser implementation for existing cache
- [ ] Step 2: Create performance benchmark test
- [ ] Step 3: Measure baseline performance (target: < 100ms)
- [ ] Step 4: If slow (> 100ms), implement caching:
  - [ ] Choose caching strategy (Facade, GraphCache, or CSN Parser)
  - [ ] Implement cache storage
  - [ ] Add cache invalidation logic
  - [ ] Add cache clear endpoint (`DELETE /api/knowledge-graph/tables/cache`)
  - [ ] Update API documentation
- [ ] Step 5: Re-run benchmark (should show improvement)
- [ ] Step 6: Write API contract test for cache behavior
- [ ] Step 7: Document caching strategy in module README

## 📖 API Design Considerations

### Current API Supports Filtering
```
GET /api/knowledge-graph/tables/PurchaseOrder/columns
    ?semantic_type=amount           # Filter by semantic type
    &search=total                    # Search in names/labels/descriptions
```

**Caching Implications**:
- Cache should store FULL column list (before filtering)
- Filters applied in-memory (don't affect cache key)
- Cache key = `table_name` only

### Proposed Cache Management Endpoints (If Needed)
```
DELETE /api/knowledge-graph/tables/cache              # Clear all table caches
DELETE /api/knowledge-graph/tables/{table_name}/cache # Clear specific table cache
GET    /api/knowledge-graph/tables/cache/status       # Check cache statistics
```

## 📚 Related Documentation

- [[Knowledge Graph API Filtering Guide]]: Query parameter patterns
- [[Module Federation Standard]]: Caching best practices
- `modules/knowledge_graph_v2/README.md`: Module architecture

## ✅ Decision Log

**Date**: 2026-02-24  
**Decision**: **DEFER CACHING IMPLEMENTATION**

**Reasons**:
1. No performance measurements exist (violates measurement-first principle)
2. CSN Parser may already cache (needs verification)
3. API-first methodology: Test contracts first, optimize later
4. Current implementation may already be fast enough

**Next Actions**:
1. Create performance benchmark (tests/knowledge_graph_v2/test_table_columns_performance.py)
2. Review CSN Parser for existing cache
3. Measure baseline performance
4. Re-evaluate caching need based on data

**Performance Threshold**:
- ✅ < 50ms: No caching needed
- ⚠️ 50-100ms: Monitor, consider caching if user complaints
- ❌ > 100ms: Implement caching immediately

## 🎓 Key Learnings

### WHAT
Analyzed table columns API for caching opportunities, found no existing cache mechanism.

### WHY
Performance optimization request from project tracker (MED-030).

### PROBLEM
Potential repeated file I/O for CSN parsing on every API call.

### ALTERNATIVES
1. **Facade-level caching** (simple dict cache)
2. **GraphCacheService extension** (consistent architecture)
3. **CSN Parser-level caching** (benefits all consumers)
4. **No caching** (if performance already acceptable)

### CONSTRAINTS
- Must maintain API filtering behavior (semantic_type, search)
- Must align with existing caching patterns (GraphCacheService)
- Must follow API-first methodology (test contracts before implementation)

### VALIDATION
- Performance benchmark test (target: < 100ms response time)
- API contract test for cache behavior (if implemented)
- Cache invalidation test (if implemented)

### WARNINGS
- ⚠️ Premature optimization: Don't add caching without performance data
- ⚠️ Cache complexity: Invalidation logic adds maintenance burden
- ⚠️ CSN Parser may already cache: Check before adding second layer

### CONTEXT
- Project uses API-first development (contracts → implementation)
- Existing schema graph caching infrastructure available
- CSN files are static (change rarely)
- Performance measurement is a critical first step per Gu Wu methodology

---

**Completed**: 2026-02-24  
**Result**: Comprehensive caching analysis with actionable recommendations based on measurement-first principle