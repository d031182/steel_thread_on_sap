# Knowledge Graph Module v2.0 - Clean Architecture Proposal

**Date**: 2026-02-08  
**Status**: 🟢 PROPOSAL  
**Author**: AI Assistant + User Discussion  
**Purpose**: Redesign knowledge_graph module using industry DDD patterns

---

## 🎯 Executive Summary

**Problem**: Current knowledge_graph module is "lousily implemented" with:
- ❌ Multiple builders with overlapping responsibilities (3 builders, confusing)
- ❌ Two conflicting cache systems (VisJsTranslator vs GraphCacheService)
- ❌ Facade with 300+ LOC doing too much
- ❌ No clear domain model (just dict manipulation)
- ❌ Hard to test (tightly coupled to infrastructure)
- ❌ 60+ min debugging sessions for simple cache bugs

**Proposed Solution**: **knowledge_graph_v2** module using Cosmic Python + Industry best practices:
- ✅ **Clean layered architecture** (Domain → Service → Repository → API)
- ✅ **100% test coverage** from day 1 (TDD approach)
- ✅ **Single responsibility** per class
- ✅ **Dependency injection** throughout
- ✅ **Side-by-side deployment** (v1 stays operational during v2 development)

---

## 📊 Current State Analysis

### What's Wrong with v1?

| Component | Issues | Impact |
|-----------|--------|--------|
| **Builders (3)** | SchemaGraphBuilder, DataGraphBuilder, CSNSchemaGraphBuilder overlap | Duplicate FK discovery logic, confusing which to use |
| **Facade** | 300+ LOC, orchestrates builders + cache + query | Too much responsibility, hard to test |
| **Cache** | Two systems (VisJsTranslator vs GraphCacheService) | Conflicting, "no such table" errors |
| **Testing** | Only 12 integration tests, no unit tests | Bugs like cache persistence take 60+ min to find |
| **Domain Model** | None (just dicts) | Business logic scattered, hard to maintain |
| **Coupling** | Facade creates builders, knows about cache DB paths | Hard to swap implementations |

### What's Good in v1?

| Component | Strengths | Keep in v2? |
|-----------|-----------|-------------|
| **Facade Pattern** | Simplifies API layer | ✅ YES (improve it) |
| **GraphCacheService** | Clean cache interface | ✅ YES (move to Repository) |
| **NetworkX integration** | Graph algorithms work | ✅ YES (wrap in Service) |
| **vis.js format** | Frontend integration proven | ✅ YES (Presenter layer) |

---

## 🏗️ Proposed v2 Architecture

### Industry-Standard Layered Design

```
┌─────────────────────────────────────────────────────────────┐
│                     API LAYER (Flask)                       │
│              api_v2.py (20-30 LOC per endpoint)             │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                    FACADE (Simplified)                      │
│          KnowledgeGraphFacade (80-100 LOC total)            │
│     Purpose: Coordinate services, handle cross-cutting      │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                   SERVICE LAYER (Core)                      │
│  ┌────────────────┬────────────────┬────────────────────┐  │
│  │ GraphBuilder   │ GraphQuery     │ GraphVisualization │  │
│  │   Service      │   Service      │     Service        │  │
│  │ (build graphs) │ (neighbors,    │  (format for UI)   │  │
│  │                │  paths)        │                    │  │
│  └────────────────┴────────────────┴────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                  DOMAIN MODEL LAYER                         │
│  ┌──────────────┬──────────────┬─────────────────────────┐ │
│  │ Graph        │ GraphNode    │ GraphEdge               │ │
│  │ (aggregate)  │ (entity)     │ (value object)          │ │
│  └──────────────┴──────────────┴─────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                 REPOSITORY LAYER (Data)                     │
│  ┌────────────────┬────────────────┬────────────────────┐  │
│  │ GraphCache     │ SchemaMetadata │ DataRecord         │  │
│  │   Repository   │   Repository   │   Repository       │  │
│  │ (cache CRUD)   │ (table info)   │ (actual data)      │  │
│  └────────────────┴────────────────┴────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│              INFRASTRUCTURE (Hidden)                        │
│     SQLite, HANA, NetworkX, CSN Parser, vis.js              │
└─────────────────────────────────────────────────────────────┘
```

### Key Design Principles

1. **Dependency Inversion**: High-level (services) depend on abstractions, not implementations
2. **Single Responsibility**: Each class does ONE thing well
3. **Open/Closed**: Extend via composition, not modification
4. **Interface Segregation**: Small, focused interfaces (not "god interfaces")
5. **Dependency Injection**: Constructor injection, no hardwired dependencies

---

## 📦 Detailed Component Design

### 1. Domain Model Layer (NEW in v2)

**Purpose**: Rich objects with business logic (not just data bags)

```python
# domain/graph.py (Aggregate Root)
class Graph:
    """
    Aggregate root for knowledge graph
    
    Enforces invariants:
    - All edges reference existing nodes
    - No duplicate edges
    - Node IDs are unique
    """
    
    def __init__(self, graph_id: str, graph_type: GraphType):
        self.id = graph_id
        self.type = graph_type  # Enum: SCHEMA | DATA | CSN
        self._nodes: Dict[str, GraphNode] = {}
        self._edges: List[GraphEdge] = []
    
    def add_node(self, node: GraphNode) -> None:
        """Add node, enforce uniqueness"""
        if node.id in self._nodes:
            raise ValueError(f"Node {node.id} already exists")
        self._nodes[node.id] = node
    
    def add_edge(self, edge: GraphEdge) -> None:
        """Add edge, enforce referential integrity"""
        if edge.source_id not in self._nodes:
            raise ValueError(f"Source node {edge.source_id} not found")
        if edge.target_id not in self._nodes:
            raise ValueError(f"Target node {edge.target_id} not found")
        
        # Check for duplicate
        if self._has_edge(edge.source_id, edge.target_id, edge.type):
            return  # Idempotent
        
        self._edges.append(edge)
    
    def get_node(self, node_id: str) -> Optional[GraphNode]:
        """Retrieve node"""
        return self._nodes.get(node_id)
    
    @property
    def nodes(self) -> List[GraphNode]:
        """All nodes (immutable view)"""
        return list(self._nodes.values())
    
    @property
    def edges(self) -> List[GraphEdge]:
        """All edges (immutable view)"""
        return list(self._edges)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to vis.js format (Presenter concern, but needed for now)"""
        return {
            'nodes': [n.to_dict() for n in self._nodes.values()],
            'edges': [e.to_dict() for e in self._edges]
        }


# domain/graph_node.py (Entity)
@dataclass
class GraphNode:
    """
    Graph node entity
    
    Immutable after creation (value object semantics)
    """
    id: str
    label: str
    type: NodeType  # Enum: TABLE | RECORD | PRODUCT | COLUMN
    properties: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to vis.js node format"""
        return {
            'id': self.id,
            'label': self.label,
            'group': self.type.value,
            **self.properties
        }


# domain/graph_edge.py (Value Object)
@dataclass(frozen=True)
class GraphEdge:
    """
    Graph edge value object
    
    Immutable (value objects can't change after creation)
    """
    source_id: str
    target_id: str
    type: EdgeType  # Enum: FK | CONTAINS | REFERENCES
    label: Optional[str] = None
    properties: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to vis.js edge format"""
        return {
            'from': self.source_id,
            'to': self.target_id,
            'label': self.label,
            'type': self.type.value,
            **self.properties
        }


# domain/enums.py
class GraphType(Enum):
    SCHEMA = 'schema'
    DATA = 'data'
    CSN = 'csn'

class NodeType(Enum):
    TABLE = 'table'
    RECORD = 'record'
    PRODUCT = 'product'
    COLUMN = 'column'

class EdgeType(Enum):
    FOREIGN_KEY = 'fk'
    CONTAINS = 'contains'
    REFERENCES = 'references'
```

**Benefits**:
- ✅ **Type safety**: Enums prevent invalid values
- ✅ **Validation**: Enforces invariants (e.g., edges reference existing nodes)
- ✅ **Testability**: Pure Python objects, no DB needed
- ✅ **Immutability**: Value objects can't be mutated accidentally

---

### 2. Repository Layer (Clean Separation)

**Purpose**: Abstract data access, hide infrastructure

```python
# repositories/graph_cache_repository.py
class AbstractGraphCacheRepository(abc.ABC):
    """Interface for graph cache persistence"""
    
    @abc.abstractmethod
    def save(self, graph: Graph) -> None:
        """Save graph to cache"""
        pass
    
    @abc.abstractmethod
    def load(self, graph_type: GraphType) -> Optional[Graph]:
        """Load graph from cache"""
        pass
    
    @abc.abstractmethod
    def clear(self, graph_type: Optional[GraphType] = None) -> int:
        """Clear cache"""
        pass


class SqliteGraphCacheRepository(AbstractGraphCacheRepository):
    """SQLite implementation of cache repository"""
    
    def __init__(self, db_path: str):
        self.db_path = db_path
        self._ensure_schema()
    
    def save(self, graph: Graph) -> None:
        """Save graph aggregate to SQLite"""
        conn = sqlite3.connect(self.db_path)
        try:
            # Delete old (if exists)
            cursor = conn.cursor()
            cursor.execute(
                "DELETE FROM graph_ontology WHERE graph_type = ?",
                (graph.type.value,)
            )
            
            # Insert ontology
            cursor.execute(
                "INSERT INTO graph_ontology (graph_type) VALUES (?)",
                (graph.type.value,)
            )
            ontology_id = cursor.lastrowid
            
            # Insert nodes
            for node in graph.nodes:
                cursor.execute("""
                    INSERT INTO graph_nodes (ontology_id, node_key, node_label, node_type, properties_json)
                    VALUES (?, ?, ?, ?, ?)
                """, (ontology_id, node.id, node.label, node.type.value, json.dumps(node.properties)))
            
            # Insert edges
            for edge in graph.edges:
                cursor.execute("""
                    INSERT INTO graph_edges (ontology_id, from_node_key, to_node_key, edge_type, edge_label, properties_json)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (ontology_id, edge.source_id, edge.target_id, edge.type.value, edge.label, json.dumps(edge.properties)))
            
            conn.commit()
        finally:
            conn.close()
    
    def load(self, graph_type: GraphType) -> Optional[Graph]:
        """Load graph from SQLite"""
        conn = sqlite3.connect(self.db_path)
        try:
            cursor = conn.cursor()
            
            # Get ontology
            cursor.execute(
                "SELECT ontology_id FROM graph_ontology WHERE graph_type = ?",
                (graph_type.value,)
            )
            row = cursor.fetchone()
            if not row:
                return None
            
            ontology_id = row[0]
            
            # Load nodes
            cursor.execute("""
                SELECT node_key, node_label, node_type, properties_json
                FROM graph_nodes WHERE ontology_id = ?
            """, (ontology_id,))
            
            graph = Graph(f"cached-{graph_type.value}", graph_type)
            
            for node_key, node_label, node_type, props_json in cursor.fetchall():
                node = GraphNode(
                    id=node_key,
                    label=node_label,
                    type=NodeType(node_type),
                    properties=json.loads(props_json) if props_json else {}
                )
                graph.add_node(node)
            
            # Load edges
            cursor.execute("""
                SELECT from_node_key, to_node_key, edge_type, edge_label, properties_json
                FROM graph_edges WHERE ontology_id = ?
            """, (ontology_id,))
            
            for from_key, to_key, edge_type, edge_label, props_json in cursor.fetchall():
                edge = GraphEdge(
                    source_id=from_key,
                    target_id=to_key,
                    type=EdgeType(edge_type),
                    label=edge_label,
                    properties=json.loads(props_json) if props_json else {}
                )
                graph.add_edge(edge)
            
            return graph
            
        finally:
            conn.close()


# repositories/schema_metadata_repository.py
class AbstractSchemaMetadataRepository(abc.ABC):
    """Interface for schema metadata access"""
    
    @abc.abstractmethod
    def get_tables(self, schema: str) -> List[TableMetadata]:
        pass
    
    @abc.abstractmethod
    def get_foreign_keys(self, schema: str, table: str) -> List[ForeignKey]:
        pass


class SqliteSchemaMetadataRepository(AbstractSchemaMetadataRepository):
    """SQLite implementation using DataSource"""
    
    def __init__(self, data_source: DataSource):
        self.data_source = data_source
    
    def get_tables(self, schema: str) -> List[TableMetadata]:
        """Get tables with metadata"""
        tables_raw = self.data_source.get_tables(schema)
        return [
            TableMetadata(
                name=t['TABLE_NAME'],
                schema=schema,
                row_count=t.get('ROW_COUNT', 0)
            )
            for t in tables_raw
        ]
    
    def get_foreign_keys(self, schema: str, table: str) -> List[ForeignKey]:
        """Discover FK relationships"""
        structure = self.data_source.get_table_structure(schema, table)
        fks = []
        
        for col in structure:
            col_name = col['COLUMN_NAME']
            if self._looks_like_fk(col_name):
                target_table = self._infer_target(col_name, table)
                if target_table:
                    fks.append(ForeignKey(
                        source_table=table,
                        source_column=col_name,
                        target_table=target_table
                    ))
        
        return fks
```

**Benefits**:
- ✅ **Testable**: Mock repositories in unit tests (no DB)
- ✅ **Swappable**: Add HANAGraphCacheRepository without changing services
- ✅ **Single Responsibility**: Each repo handles ONE data source

---

### 3. Service Layer (Business Logic)

**Purpose**: Orchestrate graph building, use repositories

```python
# services/graph_builder_service.py
class GraphBuilderService:
    """
    Builds knowledge graphs from schema metadata
    
    Single Responsibility: Graph construction logic
    No caching, no persistence, no HTTP - just builds Graph aggregates
    """
    
    def __init__(
        self,
        schema_repo: AbstractSchemaMetadataRepository,
        fk_discovery: ForeignKeyDiscoveryService
    ):
        self.schema_repo = schema_repo
        self.fk_discovery = fk_discovery
    
    def build_schema_graph(self, schema: str) -> Graph:
        """
        Build schema-level graph (tables + FK relationships)
        
        Returns: Graph aggregate (domain model)
        """
        graph = Graph(f"schema-{schema}", GraphType.SCHEMA)
        
        # Get tables
        tables = self.schema_repo.get_tables(schema)
        
        # Create table nodes
        for table in tables:
            node = GraphNode(
                id=f"table-{table.name}",
                label=table.name,
                type=NodeType.TABLE,
                properties={'row_count': table.row_count}
            )
            graph.add_node(node)
        
        # Discover FK relationships
        for table in tables:
            fks = self.fk_discovery.discover(schema, table.name)
            
            for fk in fks:
                edge = GraphEdge(
                    source_id=f"table-{fk.source_table}",
                    target_id=f"table-{fk.target_table}",
                    type=EdgeType.FOREIGN_KEY,
                    label=fk.source_column
                )
                graph.add_edge(edge)
        
        return graph
    
    def build_data_graph(
        self,
        schema: str,
        max_records: int = 20,
        filter_orphans: bool = True
    ) -> Graph:
        """Build data-level graph (actual records)"""
        # Similar logic, but creates RECORD nodes instead of TABLE nodes
        pass


# services/graph_query_service.py (Already exists, keep it!)
class GraphQueryService:
    """Query operations on graphs (neighbors, paths, traversal)"""
    pass  # v1 implementation is good!


# services/graph_visualization_service.py
class GraphVisualizationService:
    """
    Format graphs for visualization
    
    Single Responsibility: Presentation logic
    """
    
    def format_for_visjs(self, graph: Graph) -> Dict[str, Any]:
        """Convert Graph aggregate to vis.js format"""
        return graph.to_dict()  # Delegate to domain
    
    def apply_layout(self, graph_dict: Dict, layout: str) -> Dict:
        """Apply layout algorithm (hierarchical, force-directed, etc.)"""
        # Layout-specific transformations
        pass
```

**Benefits**:
- ✅ **Thin**: Each service ~50-100 LOC (not 300+ like v1 facade)
- ✅ **Testable**: Constructor injection → mock repos in tests
- ✅ **Reusable**: Same service for API, CLI, background jobs
- ✅ **Clear**: Each service has ONE job

---

### 4. Simplified Facade (Coordination Only)

**Purpose**: Coordinate services, minimal logic

```python
# facade/knowledge_graph_facade_v2.py
class KnowledgeGraphFacadeV2:
    """
    Simplified facade for knowledge graph operations
    
    Responsibilities:
    - Coordinate services (builder + cache + query + visualization)
    - Handle caching strategy (try cache → build → save cache)
    - Convert domain models to API responses
    
    Does NOT:
    - Build graphs (delegated to GraphBuilderService)
    - Execute queries (delegated to GraphQueryService)
    - Format output (delegated to GraphVisualizationService)
    """
    
    def __init__(
        self,
        builder_service: GraphBuilderService,
        cache_repo: AbstractGraphCacheRepository,
        query_service: GraphQueryService,
        viz_service: GraphVisualizationService
    ):
        self.builder = builder_service
        self.cache = cache_repo
        self.query = query_service
        self.viz = viz_service
    
    def get_graph(
        self,
        graph_type: GraphType,
        schema: str = 'sqlite',
        use_cache: bool = True
    ) -> Dict[str, Any]:
        """
        Get graph visualization (orchestration method)
        
        Strategy: Try cache → Build → Save cache → Format for UI
        """
        # 1. Try cache
        if use_cache:
            cached_graph = self.cache.load(graph_type)
            if cached_graph:
                return {
                    'success': True,
                    'graph': self.viz.format_for_visjs(cached_graph),
                    'cache_used': True
                }
        
        # 2. Build from source
        if graph_type == GraphType.SCHEMA:
            graph = self.builder.build_schema_graph(schema)
        elif graph_type == GraphType.DATA:
            graph = self.builder.build_data_graph(schema)
        else:
            raise ValueError(f"Unsupported graph type: {graph_type}")
        
        # 3. Save to cache
        if use_cache:
            self.cache.save(graph)
        
        # 4. Format for UI
        return {
            'success': True,
            'graph': self.viz.format_for_visjs(graph),
            'cache_used': False
        }
    
    def query_neighbors(self, node_id: str) -> Dict[str, Any]:
        """Delegate to query service"""
        neighbors = self.query.get_neighbors(node_id)
        return {
            'success': True,
            'neighbors': [n.to_dict() for n in neighbors]
        }
```

**Benefits**:
- ✅ **Thin**: 80-100 LOC (was 300+ LOC in v1)
- ✅ **Clear**: Just coordinates, doesn't do the work
- ✅ **Testable**: Mock all dependencies
- ✅ **Maintainable**: Easy to understand flow

---

### 5. API Layer (Ultra-Thin)

**Purpose**: HTTP concerns only (parsing, validation, responses)

```python
# api_v2.py
@bp.route('/graph', methods=['GET'])
def get_graph():
    """
    GET /api/knowledge-graph/graph?type=schema&use_cache=true
    
    Thin controller: Parse → Call facade → Return
    """
    # 1. Parse request
    graph_type_str = request.args.get('type', 'schema')
    use_cache = request.args.get('use_cache', 'true').lower() == 'true'
    
    try:
        graph_type = GraphType(graph_type_str)
    except ValueError:
        return jsonify({'error': f'Invalid type: {graph_type_str}'}), 400
    
    # 2. Call facade (DI)
    facade = get_facade()  # From app context
    result = facade.get_graph(graph_type, use_cache=use_cache)
    
    # 3. Return response
    if result['success']:
        return jsonify(result), 200
    else:
        return jsonify(result), 500
```

**Benefits**:
- ✅ **Ultra-thin**: 10-20 LOC per endpoint
- ✅ **No business logic**: Just HTTP plumbing
- ✅ **Easy to read**: Request → Facade → Response

---

## 🧪 Testing Strategy (TDD from Day 1)

### Test Pyramid for v2

```
        /\
       /  \      10% E2E (Flask test client)
      /    \     
     /──────\    20% Integration (real DB)
    /        \   
   /──────────\  70% Unit (mocks, fast)
  /____________\ 
```

### Unit Tests (Fast, Isolated)

```python
# tests/unit/domain/test_graph.py
def test_graph_enforces_node_uniqueness():
    """Graph prevents duplicate node IDs"""
    graph = Graph("test", GraphType.SCHEMA)
    node1 = GraphNode("n1", "Node 1", NodeType.TABLE)
    
    graph.add_node(node1)
    
    # Adding same node again should raise
    with pytest.raises(ValueError, match="already exists"):
        graph.add_node(node1)


def test_graph_enforces_referential_integrity():
    """Graph prevents edges to non-existent nodes"""
    graph = Graph("test", GraphType.SCHEMA)
    edge = GraphEdge("n1", "n2", EdgeType.FOREIGN_KEY)
    
    # Edge references nodes that don't exist
    with pytest.raises(ValueError, match="not found"):
        graph.add_edge(edge)


# tests/unit/services/test_graph_builder_service.py
def test_build_schema_graph():
    """GraphBuilderService builds valid graph"""
    # Mock repositories
    mock_schema_repo = Mock(spec=AbstractSchemaMetadataRepository)
    mock_schema_repo.get_tables.return_value = [
        TableMetadata("Supplier", "sqlite", 10),
        TableMetadata("PurchaseOrder", "sqlite", 5)
    ]
    
    mock_fk_service = Mock()
    mock_fk_service.discover.return_value = [
        ForeignKey("PurchaseOrder", "Supplier", "FK_Supplier")
    ]
    
    # Build graph
    service = GraphBuilderService(mock_schema_repo, mock_fk_service)
    graph = service.build_schema_graph("sqlite")
    
    # Verify
    assert len(graph.nodes) == 2
    assert len(graph.edges) == 1
    assert graph.type == GraphType.SCHEMA
```

### Integration Tests (Real DB, Slower)

```python
# tests/integration/test_graph_cache_repository.py
def test_save_and_load_roundtrip(temp_db):
    """Save graph → Load graph → Same data"""
    repo = SqliteGraphCacheRepository(temp_db)
    
    # Create graph
    graph = Graph("test", GraphType.SCHEMA)
    graph.add_node(GraphNode("n1", "Node 1", NodeType.TABLE))
    graph.add_node(GraphNode("n2", "Node 2", NodeType.TABLE))
    graph.add_edge(GraphEdge("n1", "n2", EdgeType.FOREIGN_KEY, "fk_col"))
    
    # Save
    repo.save(graph)
    
    # Load
    loaded = repo.load(GraphType.SCHEMA)
    
    # Verify
    assert loaded is not None
    assert len(loaded.nodes) == 2
    assert len(loaded.edges) == 1
    assert loaded.nodes[0].id == "n1"
```

### E2E Tests (Full Stack)

```python
# tests/e2e/test_knowledge_graph_api_v2.py
def test_get_graph_full_workflow(client):
    """Test complete API workflow: request → build → cache → response"""
    # First request: builds and caches
    response1 = client.get('/api/knowledge-graph-v2/graph?type=schema')
    assert response1.status_code == 200
    data1 = response1.json
    assert data1['success'] is True
    assert 'graph' in data1
    
    # Second request: loads from cache
    response2 = client.get('/api/knowledge-graph-v2/graph?type=schema')
    assert response2.status_code == 200
    data2 = response2.json
    assert data2['cache_used'] is True  # Verify cache hit
```

---

## 📁 File Structure (Side-by-Side with v1)

```
modules/knowledge_graph_v2/
├── module.json                      # Enable/disable v2
├── README.md                        # v2 documentation
│
├── domain/                          # NEW: Rich domain model
│   ├── __init__.py
│   ├── graph.py                     # Graph aggregate root
│   ├── graph_node.py                # Node entity
│   ├── graph_edge.py                # Edge value object
│   ├── enums.py                     # GraphType, NodeType, EdgeType
│   └── value_objects.py             # TableMetadata, ForeignKey
│
├── repositories/                    # NEW: Clean abstractions
│   ├── __init__.py
│   ├── graph_cache_repository.py    # Cache persistence
│   └── schema_metadata_repository.py # Schema access
│
├── services/                        # NEW: Business logic
│   ├── __init__.py
│   ├── graph_builder_service.py     # Graph construction
│   ├── fk_discovery_service.py      # FK inference
│   └── graph_visualization_service.py # Format for UI
│
├── facade/                          # Simplified orchestration
│   ├── __init__.py
│   └── knowledge_graph_facade_v2.py # 80-100 LOC
│
├── backend/                         # API endpoints
│   ├── __init__.py
│   └── api_v2.py                    # Ultra-thin endpoints
│
└── tests/                           # Comprehensive test suite
    ├── unit/                        # 70% of tests (fast)
    │   ├── domain/
    │   ├── repositories/
    │   └── services/
    ├── integration/                 # 20% of tests (DB)
    │   ├── test_cache_roundtrip.py
    │   └── test_builder_integration.py
    └── e2e/                         # 10% of tests (full stack)
        └── test_api_v2.py

# v1 stays operational
modules/knowledge_graph/
├── backend/                         # Keep v1 files
│   ├── api.py                       # Old API
│   ├── knowledge_graph_facade.py    # Old facade
│   └── ...                          # Rest of v1
```

---

## 🚀 Implementation Plan

### Phase 1: Foundation (Week 1) - Domain + Repos

**Goal**: Core domain model + repository interfaces

**Tasks**:
1. Create `domain/` layer (Graph, GraphNode, GraphEdge, Enums)
2. Write domain unit tests (20 tests, 100% coverage)
3. Create repository interfaces (AbstractGraphCacheRepository, AbstractSchemaMetadataRepository)
4. Implement SqliteGraphCacheRepository
5. Write repository integration tests (10 tests)

**Deliverable**: Solid foundation, 30 tests passing

**Effort**: 2-3 days

---

### Phase 2: Services (Week 2) - Business Logic

**Goal**: Service layer with graph building logic

**Tasks**:
1. Create GraphBuilderService (uses repos)
2. Create ForeignKeyDiscoveryService (extracted from builders)
3. Create GraphVisualizationService (formatting)
4. Write service unit tests (30 tests with mocked repos)

**Deliverable**: Testable business logic, 60 tests total

**Effort**: 2-3 days

---

### Phase 3: Facade + API (Week 3) - Integration

**Goal**: Working v2 module side-by-side with v1

**Tasks**:
1. Create simplified KnowledgeGraphFacadeV2 (80-100 LOC)
2. Create api_v2.py endpoints (thin controllers)
3. Add DI setup in module.__init__.py
4. Write E2E tests (10 tests, full stack)
5. Add feature flag: `knowledge_graph_v2_enabled`

**Deliverable**: Full v2 module, 70 tests total

**Effort**: 2-3 days

---

### Phase 4: Migration (Week 4) - Cutover

**Goal**: Migrate users from v1 to v2

**Tasks**:
1. Enable v2 by default (feature flag)
2. Monitor for issues (1-2 weeks)
3. Deprecate v1 endpoints
4. Delete v1 code after proven stable

**Deliverable**: v2 is production, v1 removed

**Effort**: 1 week monitoring + 1 day cleanup

---

## 📊 Comparison: v1 vs v2

| Aspect | v1 (Current) | v2 (Proposed) | Improvement |
|--------|--------------|---------------|-------------|
| **Architecture** | Ad-hoc, scattered | Layered (DDD) | ✅ 10x clearer |
| **LOC** | 300+ facade + 3 builders | 80 facade + focused services | ✅ 50% reduction |
| **Test Coverage** | 12 integration tests | 70 tests (unit+integration+e2e) | ✅ 6x more |
| **Testability** | Hard (tightly coupled) | Easy (DI + mocks) | ✅ Minutes vs hours |
| **Bug Discovery** | 60+ min (cache bug) | 5 min (unit tests fail fast) | ✅ 12x faster |
| **Maintainability** | Complex (hard to modify) | Simple (SOLID principles) | ✅ Sustainable |
| **Onboarding** | Days (understand spaghetti) | Hours (clear layers) | ✅ Faster |

---

## 💡 Why This Design is Better

### 1. Testability (TDD from Day 1)

**v1 Problem**:
```python
# Hard to test (tightly coupled)
facade = KnowledgeGraphFacade(data_source)  # Needs real DB
result = facade.get_graph(mode='schema')    # 27s to execute
```

**v2 Solution**:
```python
# Easy to test (DI + mocks)
mock_repo = Mock(spec=AbstractSchemaMetadataRepository)
mock_repo.get_tables.return_value = [test_table]

service = GraphBuilderService(mock_repo, mock_fk_service)
graph = service.build_schema_graph("test")  # 0.001s to execute!

assert len(graph.nodes) == 1  # Fast, deterministic
```

### 2. Single Responsibility

**v1 Problem**: Facade does EVERYTHING
- Builds graphs
- Manages cache
- Executes queries
- Formats output
- **Result**: 300+ LOC, hard to understand

**v2 Solution**: Each class does ONE thing
- `GraphBuilderService`: Build graphs
- `GraphCacheRepository`: Persist cache
- `GraphQueryService`: Execute queries (already good!)
- `GraphVisualizationService`: Format output
- `Facade`: ONLY coordinates the above
- **Result**: 50-100 LOC per class, crystal clear

### 3. Dependency Injection

**v1 Problem**: Hardwired dependencies
```python
class KnowledgeGraphFacade:
    def __init__(self, data_source):
        # Creates its own cache (hardwired path!)
        self._cache_service = GraphCacheService('modules/.../graph_cache.db')
```

**v2 Solution**: Injected dependencies
```python
class KnowledgeGraphFacadeV2:
    def __init__(
        self,
        builder: GraphBuilderService,  # Injected
        cache: AbstractGraphCacheRepository,  # Injected (interface!)
        query: GraphQueryService,  # Injected
        viz: GraphVisualizationService  # Injected
    ):
        # No hardwired paths, no "new" keyword
        self.builder = builder
        self.cache = cache
        # ...
```

### 4. Domain Model (NEW)

**v1 Problem**: Just dicts everywhere
```python
node = {'id': 'n1', 'label': 'Test', 'group': 'table'}  # No validation!
edge = {'from': 'n1', 'to': 'n99'}  # Can reference non-existent node!
```

**v2 Solution**: Rich domain objects
```python
node = GraphNode('n1', 'Test', NodeType.TABLE)  # Type-safe!
graph.add_edge(GraphEdge('n1', 'n99', EdgeType.FK))  # Validates node exists!
# Raises ValueError if n99 doesn't exist
```

---

## 🎯 Migration Strategy (Zero Downtime)

### Is Migration Easy? ✅ YES!

**Answer**: YES - v2 is designed to be **drop-in compatible** with v1 APIs!

**Key Design Decision**: v2 maintains v1's API contracts while improving internals

| Migration Aspect | Difficulty | Notes |
|------------------|------------|-------|
| **API Endpoints** | ✅ EASY | Same URLs, same parameters, same responses |
| **Cache Format** | ✅ EASY | v2 reads existing v1 cache (backward compatible) |
| **Frontend** | ✅ ZERO CHANGES | vis.js format unchanged |
| **Database** | ✅ ZERO CHANGES | v2 uses same graph_cache.db schema |
| **Data Migration** | ✅ NOT NEEDED | v2 reads v1 cache automatically |

---

### Migration Path: 3 Strategies

#### **Strategy 1: Feature Flag (RECOMMENDED)** ⭐

**Approach**: Both modules coexist, toggle via feature flag

**v1 stays operational, v2 opt-in**:
```json
// feature_flags.json
{
  "knowledge_graph_v2_enabled": false  // Start disabled
}
```

**API routing logic**:
```python
# app/app.py
from feature_flags import is_enabled

@app.route('/api/knowledge-graph/<path:endpoint>')
def knowledge_graph_proxy(endpoint):
    if is_enabled('knowledge_graph_v2_enabled'):
        # Route to v2
        from modules.knowledge_graph_v2.backend import api_v2
        return api_v2.handle_request(endpoint)
    else:
        # Route to v1 (current)
        from modules.knowledge_graph.backend import api
        return api.handle_request(endpoint)
```

**Benefits**:
- ✅ Instant rollback (flip flag back)
- ✅ A/B testing (10% users on v2)
- ✅ No code deletion until proven
- ✅ Zero downtime

**Timeline**:
- Week 1: Dev environment (flag=true for devs only)
- Week 2: 10% users (canary deployment)
- Week 3: 50% users (wider testing)
- Week 4: 100% users (full migration)
- Week 5-6: Monitor (no issues? delete v1)

---

#### **Strategy 2: Parallel Endpoints**

**Approach**: v1 and v2 have different URLs

**v1 endpoints** (keep existing):
```
GET /api/knowledge-graph/graph?type=schema
GET /api/knowledge-graph/neighbors?node=n1
```

**v2 endpoints** (new, parallel):
```
GET /api/knowledge-graph-v2/graph?type=schema
GET /api/knowledge-graph-v2/neighbors?node=n1
```

**Migration workflow**:
1. Deploy v2 alongside v1
2. Test v2 thoroughly (different URLs)
3. Update frontend to call v2 URLs
4. Monitor v2 for 1-2 weeks
5. Delete v1 code

**Benefits**:
- ✅ Explicit testing (call v2 URLs manually)
- ✅ No feature flag complexity
- ✅ Clear separation

**Drawbacks**:
- ⚠️ Frontend changes needed (URL updates)
- ⚠️ Two modules operational longer

---

#### **Strategy 3: Big Bang (NOT RECOMMENDED)**

**Approach**: Replace v1 with v2 in one commit

**Why NOT recommended**:
- ❌ High risk (no gradual rollout)
- ❌ No easy rollback (git revert = downtime)
- ❌ Can't A/B test
- ❌ All users affected if bugs

**Only use if**: v2 has 100% test coverage + extensive QA testing

---

### Data Migration: NOT NEEDED! ✅

**v2 Cache is Backward Compatible**

**v1 cache schema** (existing):
```sql
CREATE TABLE graph_ontology (
    ontology_id INTEGER PRIMARY KEY,
    graph_type TEXT  -- 'schema' | 'data' | 'csn'
);

CREATE TABLE graph_nodes (
    node_id INTEGER PRIMARY KEY,
    ontology_id INTEGER,
    node_key TEXT,
    node_label TEXT,
    node_type TEXT,
    properties_json TEXT
);

CREATE TABLE graph_edges (
    edge_id INTEGER PRIMARY KEY,
    ontology_id INTEGER,
    from_node_key TEXT,
    to_node_key TEXT,
    edge_type TEXT,
    edge_label TEXT,
    properties_json TEXT
);
```

**v2 reads same schema!**

```python
# v2 repository (backward compatible)
class SqliteGraphCacheRepository:
    def load(self, graph_type: GraphType) -> Optional[Graph]:
        """Loads from v1 cache format (same schema)"""
        cursor.execute(
            "SELECT ontology_id FROM graph_ontology WHERE graph_type = ?",
            (graph_type.value,)  # Same query as v1!
        )
        # ... rest of load logic
```

**What this means**:
- ✅ v2 reads existing v1 cache on first run
- ✅ No data migration scripts needed
- ✅ No cache rebuild required
- ✅ Instant cutover

**When v2 saves new cache**:
- v2 writes to same schema (compatible)
- v1 can still read it (if we rollback)
- Format is identical

---

### Frontend: ZERO CHANGES! ✅

**Why no frontend changes?**

**v1 returns vis.js format**:
```json
{
  "nodes": [
    {"id": "n1", "label": "Supplier", "group": "table"},
    {"id": "n2", "label": "PurchaseOrder", "group": "table"}
  ],
  "edges": [
    {"from": "n2", "to": "n1", "label": "FK_Supplier"}
  ]
}
```

**v2 returns SAME format**:
```python
# v2 facade
def get_graph(self, graph_type, use_cache=True):
    # ... build/load graph ...
    
    # Format for vis.js (SAME as v1!)
    return {
        'success': True,
        'graph': self.viz.format_for_visjs(graph),  # vis.js format
        'cache_used': cache_hit
    }
```

**Frontend code unchanged**:
```javascript
// modules/knowledge_graph/frontend/knowledgeGraphPage.js
fetch('/api/knowledge-graph/graph?type=schema')
  .then(res => res.json())
  .then(data => {
    // SAME data structure from v1 or v2!
    network = new vis.Network(container, data.graph, options);
  });
```

**Benefit**: Deploy v2, no frontend rebuild needed!

---

### API Compatibility Matrix

| Endpoint | v1 Signature | v2 Signature | Compatible? |
|----------|--------------|--------------|-------------|
| **GET /graph** | `?type=schema&use_cache=true` | `?type=schema&use_cache=true` | ✅ YES |
| **GET /neighbors** | `?node=n1&max_distance=1` | `?node=n1&max_distance=1` | ✅ YES |
| **GET /path** | `?start=n1&end=n2` | `?start=n1&end=n2` | ✅ YES |
| **POST /refresh** | `{}` | `{}` | ✅ YES |

**Response format compatibility**:
```python
# v1 response
{
    'success': True,
    'graph': {'nodes': [...], 'edges': [...]},
    'cache_used': False
}

# v2 response (IDENTICAL!)
{
    'success': True,
    'graph': {'nodes': [...], 'edges': [...]},
    'cache_used': False
}
```

---

### Approach: Side-by-Side Deployment (Detailed)

**Step 1**: Develop v2 module (modules/knowledge_graph_v2/)
- v1 stays operational
- No risk to production
- **Duration**: 2-3 weeks (Phases 1-3)

**Step 2**: Deploy v2 alongside v1
```
modules/
├── knowledge_graph/        # v1 (operational)
│   └── backend/api.py      # Existing endpoints
├── knowledge_graph_v2/     # v2 (new, disabled)
│   └── backend/api_v2.py   # New endpoints
```

**Step 3**: Feature flag rollout
```json
// feature_flags.json
{
  "knowledge_graph_v2_enabled": false  // Start disabled
}
```

**Step 4**: Gradual migration
- **Week 1**: v2 enabled for dev environment only (test internally)
- **Week 2**: v2 enabled for 10% users (canary - detect issues early)
- **Week 3**: v2 enabled for 50% users (wider testing)
- **Week 4**: v2 enabled for 100% users (full migration)

**Step 5**: Monitoring period
- **Week 5-6**: Monitor v2 (watch for issues, performance, bugs)
- Check Gu Wu Intelligence Hub for test health
- Check Feng Shui scores (should improve from v1)
- Check user feedback (any complaints?)

**Step 6**: v1 deprecation
- **Week 7**: Delete v1 code (if no issues in Week 5-6)
- Archive v1 in git history (can recover if needed)
- Update documentation (remove v1 references)

**Benefits**:
- ✅ Zero downtime (both run simultaneously)
- ✅ Easy rollback (flip feature flag to false)
- ✅ Learn from v2 in production before deleting v1
- ✅ Gradual risk reduction (10% → 50% → 100%)

---

### Rollback Plan (If v2 Has Issues)

**Scenario**: v2 deployed, but critical bug discovered

**Rollback Steps** (< 5 minutes):

1. **Flip feature flag**:
   ```json
   {"knowledge_graph_v2_enabled": false}
   ```

2. **Restart Flask** (if needed):
   ```bash
   pkill python  # Kill current process
   python server.py  # Restart
   ```

3. **Verify v1 operational**:
   ```bash
   curl http://localhost:5000/api/knowledge-graph/graph?type=schema
   # Should return v1 response
   ```

4. **Communicate to users**:
   - "Brief v2 issue detected, rolled back to v1"
   - "Service operational, investigating issue"

5. **Debug v2 offline**:
   - Check Gu Wu Intelligence Hub (which tests failing?)
   - Check logs (what's the error?)
   - Fix bug in v2 code
   - Re-deploy v2 when ready

**Rollback time**: **< 5 minutes** (flip flag + restart)

**Compare to "Big Bang" rollback**:
- Big Bang: Git revert commit → Rebuild → Redeploy (30+ min)
- Feature Flag: Change one line → Restart (< 5 min)

---

### Migration Checklist

**Before enabling v2 for users**:

- [ ] All 70 tests passing (unit + integration + E2E)
- [ ] Feng Shui score ≥ 90 (better than v1's ~85)
- [ ] Gu Wu Intelligence Hub shows healthy tests
- [ ] Cache roundtrip tested (save v2 → load v2 → same data)
- [ ] Backward compat tested (v2 loads v1 cache correctly)
- [ ] Frontend tested (graphs render correctly)
- [ ] Performance tested (v2 ≤ v1 response times)
- [ ] Feature flag ready (can toggle instantly)
- [ ] Rollback procedure documented (< 5 min)
- [ ] Monitoring in place (logs, metrics, alerts)

**During migration (per milestone)**:

- [ ] Enable flag for target % (10% / 50% / 100%)
- [ ] Monitor for 24-48 hours
- [ ] Check error rates (v2 vs v1)
- [ ] Check response times (v2 vs v1)
- [ ] Check user feedback (any complaints?)
- [ ] If issues: Rollback, fix, re-deploy
- [ ] If healthy: Proceed to next %

**After 100% migration**:

- [ ] Monitor for 1-2 weeks (ensure stable)
- [ ] Compare v1 vs v2 metrics (improvements?)
- [ ] Delete v1 code (archive in git)
- [ ] Update docs (remove v1 references)
- [ ] Celebrate! 🎉

---

### Migration Risk Assessment

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| **v2 bugs** | Medium | High | Feature flag (instant rollback) |
| **Performance regression** | Low | Medium | Load testing before migration |
| **Cache corruption** | Low | High | Backward compatible schema |
| **Frontend breaks** | Very Low | High | vis.js format unchanged |
| **User confusion** | Low | Low | Transparent migration (same URLs) |

**Overall Risk**: **LOW** (due to feature flag + backward compat + extensive testing)

---

### Success Criteria

**v2 is successful if**:

1. ✅ **Faster development**: New features take 50% less time (better architecture)
2. ✅ **Fewer bugs**: Bug discovery < 5 min (unit tests fail fast)
3. ✅ **Better quality**: Feng Shui score ≥ 90 (vs v1's ~85)
4. ✅ **Same UX**: Users don't notice migration (transparent)
5. ✅ **Zero downtime**: No production incidents during migration

**Measured by**:
- Feng Shui scores (pre vs post migration)
- Gu Wu test coverage (70+ tests vs 12 tests)
- Time to add new feature (track development time)
- Bug count in first 30 days (v2 vs v1 historical)
- User complaints (should be zero)

---

## 📋 Effort Estimation

| Phase | Tasks | Effort | Tests Written |
|-------|-------|--------|---------------|
| **Phase 1** | Domain + Repos | 2-3 days | 30 tests |
| **Phase 2** | Services | 2-3 days | 30 tests |
| **Phase 3** | Facade + API | 2-3 days | 10 tests |
| **Phase 4** | Migration | 1 week | - |
| **TOTAL** | Full v2 module | **2-3 weeks** | **70 tests** |

**Comparison**:
- v1 development: 4-6 weeks (trial-and-error, refactoring)
- v2 development: 2-3 weeks (TDD, upfront design)
- **v2 is FASTER because we're doing it RIGHT the first time**

---

## 🎓 Key Design Decisions

### 1. Domain Model First

**Why**: Enforces invariants, makes testing trivial

**Example**:
```python
# v1: Dicts (no validation)
edge = {'from': 'missing_node', 'to': 'n2'}  # ❌ No error!

# v2: Domain objects (automatic validation)
graph.add_edge(GraphEdge('missing_node', 'n2', EdgeType.FK))
# ✅ Raises ValueError immediately!
```

### 2. Repository Pattern

**Why**: Already proven in p2p_dashboard v3.0.0

**Benefit**: Swap cache backends (SQLite → Redis) without changing services

### 3. Service Layer

**Why**: Cosmic Python proven pattern

**Benefit**: Reuse same service for API, CLI, background jobs

### 4. Simplified Facade

**Why**: v1 facade is 300+ LOC (too much)

**Benefit**: 80-100 LOC (coordination only), easier to understand

### 5. Test-Driven Development

**Why**: v1 bugs take 60+ min to find (no unit tests)

**Benefit**: v2 bugs found in <5 min (unit tests fail immediately)

---

## 🔥 Quick Wins in v2

### Win 1: Bug-Free Cache (Day 1)

**v1**: 3 conflicting cache systems, 60 min debugging  
**v2**: ONE GraphCacheRepository, tested from day 1

### Win 2: Fast Tests (Day 1)

**v1**: Only integration tests (slow, brittle)  
**v2**: 70% unit tests with mocks (0.001s per test)

### Win 3: Clear Architecture (Day 1)

**v1**: "Where does graph building happen?" (confusing)  
**v2**: GraphBuilderService (obvious!)

### Win 4: Type Safety (Day 1)

**v1**: `mode='schemaa'` (typo! No error until runtime)  
**v2**: `GraphType.SCHEMA` (typo caught by IDE/mypy immediately)

---

## 🎯 Decision Framework

### Should We Build v2?

**Pain exists?**
- ✅ YES: 60+ min debugging sessions, cache bugs, confusion

**Simpler alternative?**
- ❌ NO: Refactoring v1 would break production, take just as long

**Team ready?**
- ✅ YES: We understand Repository Pattern (p2p_dashboard v3.0.0)
- ✅ YES: We have Cosmic Python patterns documented
- ✅ YES: Feng Shui/Gu Wu enforce quality automatically

**User appetite?**
- ✅ YES: User said "entire module has been lousily implemented"
- ✅ YES: User wants "better design pattern, less error prone, well tested"

**Decision**: ⭐ **STRONG YES** - Build knowledge_graph_v2

---

## 📚 References

**Patterns Used**:
- [[Cosmic Python DDD Patterns]] - Domain Model, Repository, Service Layer
- [[Repository Pattern Modular Architecture]] - Our v3.0.0 implementation
- Perplexity research: Graph viz best practices (Python + DI + testing)

**Similar Modules**:
- `modules/p2p_dashboard` - Uses Repository Pattern v3.0.0 (proven successful)
- `modules/ai_assistant` - Clean service layer architecture

**Quality Tools**:
- Feng Shui: Will validate v2 architecture automatically
- Gu Wu: Will enforce 100% test coverage
- Shi Fu: Will track v2 adoption vs v1 issues

---

## 🚦 Next Steps

### Option A: Start Immediately (Recommended)

**Effort**: 2-3 weeks  
**Risk**: Low (side-by-side deployment)  
**Value**: Eliminate knowledge_graph technical debt permanently

**Workflow**:
1. User approves proposal
2. Create `modules/knowledge_graph_v2/` directory
3. Start Phase 1 (Domain + Repos) with TDD
4. Build incrementally with 100% test coverage

### Option B: Defer Until After Security Fixes

**Rationale**: Security is P0 blocker (45 SQL injection vulnerabilities)  
**Timeline**: Start v2 in 2-3 weeks after security complete

### Option C: Hybrid (Incremental)

**Approach**: 
- Fix immediate v1 bugs (cache persistence - DONE ✅)
- Build v2 in background (1 hour/day over 3-4 weeks)
- Migrate when ready

---

## 💬 Discussion Questions

1. **Timing**: Start v2 now or after security fixes?
2. **Scope**: Full v2 (all features) or MVP (just schema graph)?
3. **Testing**: TDD from day 1 or add tests later?
4. **Migration**: Gradual rollout or big bang cutover?

---

**Recommendation**: ⭐ **Build knowledge_graph_v2 using Cosmic Python patterns**

**Why**: 
- Current v1 is technical debt (proven by 60+ min debugging)
- v2 will be 10x more maintainable (layered architecture)
- 2-3 weeks investment prevents future pain
- Side-by-side deployment = zero risk

**Philosophy**:
> "Slow is smooth. Smooth is fast."  
> "Invest 2-3 weeks in solid architecture → Save months of debugging."