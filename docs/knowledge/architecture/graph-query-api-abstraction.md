# Graph Query API Abstraction Layer

## Overview

**Principle**: Create a generic, reusable Graph Query API that abstracts over multiple graph backends:
- **HANA Property Graph** (production, cloud)
- **SQLite + NetworkX** (development, local fallback)

This follows our established data abstraction pattern and enables seamless transitions between environments.

## Architecture Pattern

### Interface-Based Design

```python
# core/interfaces/graph_query.py

from abc import ABC, abstractmethod
from typing import List, Dict, Optional
from dataclasses import dataclass

@dataclass
class GraphNode:
    """Standard node representation"""
    id: str
    label: str
    properties: Dict
    
@dataclass
class GraphEdge:
    """Standard edge representation"""
    id: str
    source_id: str
    target_id: str
    label: str
    properties: Dict

@dataclass
class GraphPath:
    """Standard path representation"""
    nodes: List[GraphNode]
    edges: List[GraphEdge]
    length: int

class IGraphQueryEngine(ABC):
    """
    Interface for graph query engines.
    
    Implementations:
    - HANAGraphQueryEngine (HANA Property Graph SQL)
    - NetworkXGraphQueryEngine (SQLite + NetworkX)
    """
    
    @abstractmethod
    def get_neighbors(
        self, 
        node_id: str, 
        direction: str = 'outgoing',
        edge_types: Optional[List[str]] = None
    ) -> List[GraphNode]:
        """Get adjacent nodes"""
        pass
    
    @abstractmethod
    def shortest_path(
        self,
        start_id: str,
        end_id: str,
        max_hops: int = 10
    ) -> Optional[GraphPath]:
        """Find shortest path between nodes"""
        pass
    
    @abstractmethod
    def traverse(
        self,
        start_id: str,
        depth: int = 2,
        direction: str = 'outgoing'
    ) -> List[GraphNode]:
        """Breadth-first traversal"""
        pass
    
    @abstractmethod
    def pattern_match(
        self,
        pattern: str
    ) -> List[Dict]:
        """
        Pattern matching query.
        
        HANA: Uses SQL MATCH syntax
        NetworkX: Converts to graph algorithms
        """
        pass
    
    @abstractmethod
    def subgraph(
        self,
        node_ids: List[str],
        include_edges: bool = True
    ) -> Dict:
        """Extract subgraph"""
        pass
```

## Implementation Strategy

### 1. HANA Property Graph Implementation

```python
# modules/hana_connection/backend/hana_graph_query_engine.py

class HANAGraphQueryEngine(IGraphQueryEngine):
    """
    HANA Property Graph SQL implementation.
    
    Uses HANA's native graph features:
    - GRAPH WORKSPACE
    - MATCH ... WHERE ... syntax
    - Shortest path algorithms
    - Graph traversal functions
    """
    
    def __init__(self, connection, graph_workspace: str):
        self.conn = connection
        self.workspace = graph_workspace
    
    def get_neighbors(self, node_id, direction='outgoing', edge_types=None):
        """
        HANA SQL:
        SELECT target FROM GRAPH WORKSPACE P2P_GRAPH
        MATCH (source) -[edge]-> (target)
        WHERE source.id = :node_id
        """
        sql = f"""
            SELECT target.id, target.label, target.properties
            FROM GRAPH WORKSPACE {self.workspace}
            MATCH (source) -[edge]-> (target)
            WHERE source.id = ?
        """
        if edge_types:
            sql += f" AND edge.type IN ({','.join(['?']*len(edge_types))})"
        
        cursor = self.conn.cursor()
        cursor.execute(sql, [node_id] + (edge_types or []))
        
        return [
            GraphNode(id=row[0], label=row[1], properties=json.loads(row[2]))
            for row in cursor.fetchall()
        ]
    
    def shortest_path(self, start_id, end_id, max_hops=10):
        """
        HANA SQL:
        SELECT * FROM GRAPH WORKSPACE P2P_GRAPH
        MATCH (start) -[path:1..10]-> (end)
        WHERE start.id = :start AND end.id = :end
        """
        sql = f"""
            SELECT VERTICES, EDGES
            FROM GRAPH WORKSPACE {self.workspace}
            MATCH (start) -[path:1..{max_hops}]-> (end)
            WHERE start.id = ? AND end.id = ?
            RETURN path
            ORDER BY LENGTH(path)
            LIMIT 1
        """
        # Parse result into GraphPath
        ...
```

### 2. NetworkX Fallback Implementation

```python
# modules/sqlite_connection/backend/networkx_graph_query_engine.py

import networkx as nx

class NetworkXGraphQueryEngine(IGraphQueryEngine):
    """
    SQLite + NetworkX fallback implementation.
    
    Uses:
    - SQLite for data storage
    - NetworkX for graph algorithms
    - Cached graph in memory
    """
    
    def __init__(self, db_path: str):
        self.db_path = db_path
        self._graph: Optional[nx.DiGraph] = None
    
    def _load_graph(self) -> nx.DiGraph:
        """Load graph from SQLite into NetworkX (cached)"""
        if self._graph is not None:
            return self._graph
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Build NetworkX graph from ontology tables
        G = nx.DiGraph()
        
        # Load nodes from data tables
        cursor.execute("SELECT DISTINCT source_table FROM graph_schema_edges")
        for (table,) in cursor.fetchall():
            cursor.execute(f"SELECT * FROM {table}")
            for row in cursor.fetchall():
                node_id = f"{table}:{row[0]}"
                G.add_node(node_id, label=table, properties=dict(zip(...)))
        
        # Load edges from ontology
        cursor.execute("""
            SELECT source_table, source_column, target_table, relationship_type
            FROM graph_schema_edges WHERE is_active = 1
        """)
        for src_table, src_col, tgt_table, rel_type in cursor.fetchall():
            # Query actual data relationships
            cursor.execute(f"""
                SELECT src.{src_col}, tgt.{tgt_table}
                FROM {src_table} src
                JOIN {tgt_table} tgt ON src.{src_col} = tgt.{tgt_table}
            """)
            for src_id, tgt_id in cursor.fetchall():
                G.add_edge(
                    f"{src_table}:{src_id}",
                    f"{tgt_table}:{tgt_id}",
                    type=rel_type
                )
        
        conn.close()
        self._graph = G
        return G
    
    def get_neighbors(self, node_id, direction='outgoing', edge_types=None):
        """Use NetworkX neighbors()"""
        G = self._load_graph()
        
        if direction == 'outgoing':
            neighbors = G.successors(node_id)
        elif direction == 'incoming':
            neighbors = G.predecessors(node_id)
        else:  # 'both'
            neighbors = set(G.successors(node_id)) | set(G.predecessors(node_id))
        
        # Filter by edge type if specified
        if edge_types:
            neighbors = [
                n for n in neighbors
                if G[node_id][n].get('type') in edge_types
            ]
        
        return [
            GraphNode(
                id=n,
                label=G.nodes[n]['label'],
                properties=G.nodes[n]['properties']
            )
            for n in neighbors
        ]
    
    def shortest_path(self, start_id, end_id, max_hops=10):
        """Use NetworkX shortest_path()"""
        G = self._load_graph()
        
        try:
            path_nodes = nx.shortest_path(G, start_id, end_id)
            
            if len(path_nodes) - 1 > max_hops:
                return None  # Exceeds max hops
            
            # Build GraphPath object
            nodes = [
                GraphNode(id=n, label=G.nodes[n]['label'], properties=G.nodes[n]['properties'])
                for n in path_nodes
            ]
            
            edges = [
                GraphEdge(
                    id=f"{path_nodes[i]}->{path_nodes[i+1]}",
                    source_id=path_nodes[i],
                    target_id=path_nodes[i+1],
                    label=G[path_nodes[i]][path_nodes[i+1]].get('type', 'related'),
                    properties=G[path_nodes[i]][path_nodes[i+1]]
                )
                for i in range(len(path_nodes) - 1)
            ]
            
            return GraphPath(nodes=nodes, edges=edges, length=len(edges))
        
        except nx.NetworkXNoPath:
            return None
    
    def traverse(self, start_id, depth=2, direction='outgoing'):
        """Use NetworkX BFS"""
        G = self._load_graph()
        
        if direction == 'outgoing':
            edges = G.edges()
        elif direction == 'incoming':
            edges = G.reverse().edges()
        else:
            edges = G.to_undirected().edges()
        
        # BFS to depth
        visited = set()
        queue = [(start_id, 0)]
        
        while queue:
            node, d = queue.pop(0)
            if d > depth or node in visited:
                continue
            
            visited.add(node)
            
            for neighbor in G.neighbors(node):
                if neighbor not in visited:
                    queue.append((neighbor, d + 1))
        
        return [
            GraphNode(id=n, label=G.nodes[n]['label'], properties=G.nodes[n]['properties'])
            for n in visited
        ]
```

### 3. Graph Query Service (Facade)

```python
# modules/graph_query/backend/graph_query_service.py

class GraphQueryService:
    """
    Unified graph query service.
    
    Auto-detects backend:
    - If HANA available: Use HANA Property Graph
    - Else: Use SQLite + NetworkX fallback
    """
    
    def __init__(self, config):
        self.config = config
        self.engine = self._create_engine()
    
    def _create_engine(self) -> IGraphQueryEngine:
        """Factory: Create appropriate engine"""
        if self.config.get('use_hana') and hana_available():
            from modules.hana_connection.backend.hana_graph_query_engine import HANAGraphQueryEngine
            return HANAGraphQueryEngine(
                connection=get_hana_connection(),
                graph_workspace='P2P_GRAPH'
            )
        else:
            from modules.sqlite_connection.backend.networkx_graph_query_engine import NetworkXGraphQueryEngine
            return NetworkXGraphQueryEngine(
                db_path=self.config['db_path']
            )
    
    # Proxy all IGraphQueryEngine methods
    def get_neighbors(self, node_id, direction='outgoing', edge_types=None):
        return self.engine.get_neighbors(node_id, direction, edge_types)
    
    def shortest_path(self, start_id, end_id, max_hops=10):
        return self.engine.shortest_path(start_id, end_id, max_hops)
    
    # ... etc for all interface methods
```

## Benefits of This Design

### 1. Environment Flexibility
```python
# Development (SQLite + NetworkX)
service = GraphQueryService({'use_hana': False, 'db_path': 'local.db'})

# Production (HANA Property Graph)
service = GraphQueryService({'use_hana': True})

# Same API, different backend!
path = service.shortest_path('PO:PO000001', 'Invoice:5100000001')
```

### 2. Seamless Migration
- Start development with SQLite + NetworkX
- Test with real data, real algorithms
- Deploy to HANA with zero code changes
- Fallback to SQLite if HANA unavailable

### 3. Performance Optimization
```python
# NetworkX: In-memory graph (fast for < 100K nodes)
# HANA: Native graph engine (scales to millions)

# Service auto-selects best option
if data_size < 100000:
    use NetworkX  # Faster for small graphs
else:
    use HANA  # Scales better
```

### 4. Testing Strategy
```python
# Test against both engines
@pytest.fixture(params=['networkx', 'hana'])
def graph_service(request):
    if request.param == 'networkx':
        return GraphQueryService({'use_hana': False})
    else:
        return GraphQueryService({'use_hana': True})

def test_shortest_path(graph_service):
    # Same test, both engines!
    path = graph_service.shortest_path('A', 'B')
    assert path is not None
```

## Implementation Phases

### Phase 1: Interface Definition ✅ (Design Complete)
- Create `core/interfaces/graph_query.py`
- Define standard data classes
- Document all methods

### Phase 2: NetworkX Implementation (Next)
- Implement SQLite + NetworkX engine
- Load graph from ontology cache
- Test all query operations
- **Effort**: 4-6 hours

### Phase 3: HANA Implementation (Production)
- Implement HANA Property Graph engine
- Create graph workspace DDL
- Sync ontology to HANA
- **Effort**: 6-8 hours

### Phase 4: Service Integration
- Create unified GraphQueryService
- Add auto-detection logic
- Update Knowledge Graph UI
- **Effort**: 2-3 hours

## Comparison: NetworkX vs HANA

| Feature | NetworkX (Local) | HANA Property Graph | Winner |
|---------|-----------------|-------------------|--------|
| **Setup** | Zero config | Requires workspace | NetworkX |
| **Development** | Fast iteration | Cloud dependency | NetworkX |
| **Performance (small)** | <1ms (in-memory) | ~10ms (network) | NetworkX |
| **Performance (large)** | Slows >100K nodes | Scales to millions | HANA |
| **Features** | Rich algorithms | Native SQL integration | Both |
| **Production** | Not recommended | Enterprise-grade | HANA |
| **Cost** | Free | Cloud costs | NetworkX |

**Strategy**: Start with NetworkX (fast development), deploy to HANA (production scale)

## Usage Examples

### Example 1: Find Invoice Chain
```python
# Works with both engines!
service = GraphQueryService(config)

# Find path: Supplier → PO → Invoice
path = service.shortest_path(
    start_id='Supplier:SUP001',
    end_id='Invoice:5100000001'
)

print(f"Path length: {path.length}")
for i, node in enumerate(path.nodes):
    print(f"  {i}: {node.label} {node.id}")
```

### Example 2: Explore Relationships
```python
# Get all invoices for a supplier
invoices = service.traverse(
    start_id='Supplier:SUP001',
    depth=2,  # Supplier → PO → Invoice
    direction='outgoing'
)

print(f"Found {len(invoices)} related nodes")
```

### Example 3: Pattern Matching
```python
# Find blocked invoices with price variance
results = service.pattern_match("""
    MATCH (po:PurchaseOrder) -[has_invoice]-> (invoice:SupplierInvoice)
    WHERE invoice.status = 'Blocked'
    AND invoice.amount > po.amount * 1.1
    RETURN po, invoice
""")
```

## Conclusion

**YES**, the Graph Query API should be a **generic, reusable module** that:
- ✅ Works with HANA Property Graph (production)
- ✅ Works with SQLite + NetworkX (development)
- ✅ Provides unified interface (IGraphQueryEngine)
- ✅ Enables seamless migration between backends
- ✅ Follows our data abstraction patterns

**Next Step**: Implement Phase 2 (NetworkX engine) to prove the pattern before investing in HANA integration.

---

**Related Documents**:
- [[data-abstraction-layers]]
- [[graph-ontology-persistence]]
- [[sap-hana-graph-engines-comparison]]
- [[sqlite-graph-fallback-solutions]]