# Knowledge Graph v2: Services Layer Design

**Status**: Design Phase  
**Date**: 2026-02-08  
**Related**: [[Knowledge Graph v2 Architecture Proposal]], [[Knowledge Graph v2 API Design]]

---

## 🎯 Goals

**Primary Goal**: Build services layer that orchestrates graph building with cache rebuild capability

**Key Requirements**:
1. ✅ Automatic cache rebuild if deleted/corrupted
2. ✅ Force rebuild capability (manual refresh)
3. ✅ Clean separation from v1 (no vis.js in services)
4. ✅ Dependency injection (testable)
5. ✅ Generic format (NOT vis.js-specific)

---

## 📐 Architecture

### Layer Separation

```
┌─────────────────────────────────────┐
│     Facade Layer (Phase 3)          │  Public API
├─────────────────────────────────────┤
│   Services Layer (Phase 2) ⭐       │  Business Logic
│   - SchemaGraphBuilderService       │
│   - DataGraphBuilderService         │
│   - GraphCacheService               │
├─────────────────────────────────────┤
│   Repository Layer (Phase 1) ✅     │  Data Persistence
│   - SqliteGraphCacheRepository      │
│   - InMemoryGraphCacheRepository    │
├─────────────────────────────────────┤
│   Domain Layer (Phase 1) ✅         │  Core Models
│   - Graph, GraphNode, GraphEdge     │
└─────────────────────────────────────┘
```

---

## 🔧 Service Designs

### 1. SchemaGraphBuilderService

**Responsibility**: Build schema graphs from CSN or database

**Key Differences from v1**:
- ❌ NO vis.js format (returns generic Graph domain object)
- ✅ Uses v2 domain models (Graph, GraphNode, GraphEdge)
- ✅ Returns generic format (source/target, not from/to)
- ✅ Dependency injection (CSNParser injected)

**Interface**:
```python
class SchemaGraphBuilderService:
    def __init__(self, csn_parser: CSNParser):
        """Inject CSN parser (no hardcoded paths)"""
        
    def build_from_csn(self) -> Graph:
        """Build schema graph from CSN files"""
        # Returns: Graph domain object (generic format)
        
    def build_from_database(self, data_source) -> Graph:
        """Build schema graph from database (alternative)"""
```

**Reuse from v1**:
- ✅ CSN parsing logic (CSNParser, RelationshipMapper)
- ✅ FK discovery patterns
- ✅ Product grouping logic
- ❌ NOT vis.js formatting (that's frontend's job)

---

### 2. DataGraphBuilderService

**Responsibility**: Build data graphs from SQLite/HANA records

**Key Differences from v1**:
- ❌ NO vis.js format (returns generic Graph domain object)
- ✅ Uses v2 domain models
- ✅ Returns generic format
- ✅ Dependency injection (DataSource injected)

**Interface**:
```python
class DataGraphBuilderService:
    def __init__(self, data_source):
        """Inject data source (HANA or SQLite)"""
        
    def build_from_database(self, limit: int = 100) -> Graph:
        """Build data graph from database records"""
        # Returns: Graph domain object (generic format)
```

**Reuse from v1**:
- ✅ Record querying logic
- ✅ Relationship discovery patterns
- ❌ NOT vis.js formatting

---

### 3. GraphCacheService ⭐ **CACHE REBUILD LOGIC**

**Responsibility**: Orchestrate cache operations with rebuild capability

**This is the KEY service for your concern!**

**Interface**:
```python
class GraphCacheService:
    def __init__(
        self,
        cache_repo: AbstractGraphCacheRepository,
        schema_builder: SchemaGraphBuilderService,
        data_builder: DataGraphBuilderService
    ):
        """Inject all dependencies (DI)"""
        
    def get_or_rebuild_schema_graph(self) -> Graph:
        """
        Get schema graph from cache, rebuild if missing/corrupted
        
        Logic:
        1. Try to load from cache
        2. If found → return cached
        3. If not found → rebuild from CSN → save → return
        """
        
    def get_or_rebuild_data_graph(self) -> Graph:
        """
        Get data graph from cache, rebuild if missing/corrupted
        
        Logic:
        1. Try to load from cache
        2. If found → return cached
        3. If not found → rebuild from database → save → return
        """
        
    def force_rebuild_schema(self) -> Graph:
        """
        Force rebuild schema graph (ignore cache)
        
        Use case: Manual refresh when CSN files change
        """
        
    def force_rebuild_data(self) -> Graph:
        """
        Force rebuild data graph (ignore cache)
        
        Use case: Manual refresh when data changes
        """
        
    def clear_cache(self, graph_type: GraphType) -> bool:
        """Delete cached graph (administrative operation)"""
```

**Usage Example**:
```python
# Automatic rebuild on cache miss/corruption
graph = cache_service.get_or_rebuild_schema_graph()

# Force rebuild (manual refresh)
graph = cache_service.force_rebuild_schema()

# Check cache status
if cache_service.exists(GraphType.SCHEMA):
    print("Cache valid")
```

---

## 🔄 v1 → v2 Migration Strategy

### What to Reuse

**✅ Reuse (business logic)**:
- CSN parsing (CSNParser)
- Relationship discovery (RelationshipMapper)
- FK analysis patterns
- Product grouping logic
- Record querying logic

**❌ Do NOT reuse (presentation logic)**:
- vis.js formatting code
- Color/shape/size definitions
- Frontend-specific properties
- Direct cache access (use repository instead)

### What to Change

**v1 Pattern** (mixes concerns):
```python
# v1: Returns vis.js format directly
def build_schema_graph() -> Dict:
    nodes = []
    nodes.append({
        'id': 'table-1',
        'label': 'Table',
        'shape': 'ellipse',      # ❌ Frontend concern
        'color': {'background': '#e3f2fd'},  # ❌ Frontend concern
        'from': 'n1',  # ❌ vis.js-specific
        'to': 'n2'     # ❌ vis.js-specific
    })
    return {'nodes': nodes, 'edges': edges}
```

**v2 Pattern** (clean separation):
```python
# v2: Returns generic domain object
def build_from_csn() -> Graph:
    graph = Graph('schema', GraphType.SCHEMA)
    
    # Add nodes (generic)
    node = GraphNode('table-1', 'Table', NodeType.TABLE)
    graph.add_node(node)
    
    # Add edges (generic: source/target)
    edge = GraphEdge('n1', 'n2', EdgeType.FOREIGN_KEY, 'fk_id')
    graph.add_edge(edge)
    
    return graph  # ✅ Generic domain object
```

---

## 🧪 Testing Strategy

### Service Tests (Unit)

**Test with mocks** (no real database):
```python
def test_get_or_rebuild_uses_cache_when_available():
    # Mock repository returns cached graph
    mock_repo = Mock(AbstractGraphCacheRepository)
    mock_repo.get.return_value = mock_graph
    
    # Mock builder NOT called (cache hit)
    mock_builder = Mock(SchemaGraphBuilderService)
    
    service = GraphCacheService(mock_repo, mock_builder, None)
    result = service.get_or_rebuild_schema_graph()
    
    # Assert: Used cache, did NOT call builder
    mock_repo.get.assert_called_once()
    mock_builder.build_from_csn.assert_not_called()

def test_get_or_rebuild_rebuilds_when_cache_missing():
    # Mock repository returns None (cache miss)
    mock_repo = Mock(AbstractGraphCacheRepository)
    mock_repo.get.return_value = None
    
    # Mock builder returns fresh graph
    mock_builder = Mock(SchemaGraphBuilderService)
    mock_builder.build_from_csn.return_value = fresh_graph
    
    service = GraphCacheService(mock_repo, mock_builder, None)
    result = service.get_or_rebuild_schema_graph()
    
    # Assert: Built fresh graph, saved to cache
    mock_builder.build_from_csn.assert_called_once()
    mock_repo.save.assert_called_once_with(fresh_graph)
```

### Integration Tests

**Test with real repository**:
```python
def test_rebuild_with_real_sqlite():
    # Real repository (temp database)
    repo = SqliteGraphCacheRepository(temp_db_path)
    
    # Real builders
    schema_builder = SchemaGraphBuilderService(csn_parser)
    
    service = GraphCacheService(repo, schema_builder, None)
    
    # First call: Rebuilds (cache empty)
    graph1 = service.get_or_rebuild_schema_graph()
    assert len(graph1.nodes) > 0
    
    # Second call: Uses cache (no rebuild)
    graph2 = service.get_or_rebuild_schema_graph()
    assert graph2.id == graph1.id
```

---

## 📊 Performance Considerations

### Cache Hit vs Rebuild

**Cache Hit** (fast):
- Load from SQLite: ~50ms
- Deserialize domain objects: ~10ms
- **Total: ~60ms**

**Cache Rebuild** (slower):
- Parse CSN files: ~200ms
- Build graph: ~100ms
- Save to cache: ~50ms
- **Total: ~350ms**

**Ratio**: Cache is **5-6x faster** than rebuild

### When to Force Rebuild

**Automatic triggers**:
- ✅ Cache file deleted
- ✅ Cache corrupted (exception during load)
- ✅ Cache empty (no data)

**Manual triggers**:
- ✅ CSN files updated (schema changes)
- ✅ Data refreshed (new records added)
- ✅ User requests refresh (UI button)

---

## 🔗 Dependencies

### External (from core/)
- ✅ CSNParser (core/services/csn_parser.py)
- ✅ RelationshipMapper (core/services/relationship_mapper.py)
- ✅ DataSource interface (core/interfaces/data_source.py)

### Internal (from v2/)
- ✅ Graph, GraphNode, GraphEdge (domain layer)
- ✅ AbstractGraphCacheRepository (repository layer)
- ✅ GraphType, NodeType, EdgeType (enums)

### NEW (to create)
- ⏳ SchemaGraphBuilderService
- ⏳ DataGraphBuilderService
- ⏳ GraphCacheService

---

## 🎯 Success Criteria

**Phase 2 Complete When**:
1. ✅ SchemaGraphBuilderService returns generic Graph objects
2. ✅ DataGraphBuilderService returns generic Graph objects
3. ✅ GraphCacheService has get_or_rebuild() methods
4. ✅ GraphCacheService has force_rebuild() methods
5. ✅ All services use dependency injection
6. ✅ NO vis.js format in services (generic only)
7. ✅ Service unit tests passing (mocked dependencies)
8. ✅ Integration tests passing (real repository)

---

## 📝 Implementation Order

1. **SchemaGraphBuilderService** (2-3 hours)
   - Port CSN parsing logic from v1
   - Return generic Graph objects
   - Write unit tests (10-15 tests)

2. **DataGraphBuilderService** (2-3 hours)
   - Port record querying logic from v1
   - Return generic Graph objects
   - Write unit tests (10-15 tests)

3. **GraphCacheService** (2-3 hours)
   - Implement get_or_rebuild logic
   - Implement force_rebuild logic
   - Write unit tests (15-20 tests)

4. **Integration Tests** (1-2 hours)
   - Test with real SQLite repository
   - Test rebuild scenarios
   - Test performance

**Total Estimated Time**: 8-12 hours (1-2 days)

---

## 🔍 Next Steps

After Phase 2 complete:
1. **Phase 3**: KnowledgeGraphFacadeV2 (public API)
2. **Phase 4**: Frontend adapter (vis.js formatting)
3. **Phase 5**: Migration from v1 to v2

**Ready to implement!** 🚀