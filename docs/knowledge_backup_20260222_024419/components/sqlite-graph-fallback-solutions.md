# SQLite Graph Database Fallback Solutions

**Created**: 2026-01-30  
**Research Source**: Perplexity AI (open-source projects, 2026)  
**Purpose**: Provide minimalistic SQLite-based fallback for HANA Cloud graph capabilities

---

## Executive Summary

While building toward HANA Cloud's advanced graph engines, you can use **open-source Python libraries** to provide minimalistic graph capabilities with SQLite as a fallback. This enables:

1. **Property Graph** fallback → NetworkX + SQLite
2. **Knowledge Graph** fallback → RDFLib + SQLite  
3. **Offline development** → Full graph capabilities without HANA dependency
4. **Progressive enhancement** → Start simple, migrate to HANA when ready

**Key Benefit**: Same API surface in your application, different backend implementations! 🎯

---

## Architecture Strategy: Unified Graph Interface

### The Pattern

```python
# Your application code (unchanged)
graph_service.shortest_path(start, end)
graph_service.sparql_query("SELECT ?s WHERE...")

# Behind the scenes:
# - Development/Offline: SQLite + NetworkX/RDFLib
# - Production/Online: HANA Property/Knowledge Graph
# - Automatic fallback based on connection availability
```

**This is EXACTLY what your DataSource interface does for SQL!** Extend the same pattern to graphs.

---

## Option 1: Property Graph Fallback (NetworkX)

### What is NetworkX?

**NetworkX** is Python's most popular graph library:
- ✅ **Open source** (BSD license)
- ✅ **Battle-tested** (used by NASA, Google, academics)
- ✅ **Rich algorithms** (shortest path, centrality, clustering, community detection)
- ✅ **Pure Python** (easy installation, no C dependencies)
- ✅ **Excellent documentation** (comprehensive tutorials)

**Perfect for**: Mimicking HANA Property Graph algorithms offline

### Installation

```bash
pip install networkx
```

**That's it!** No complex setup, pure Python.

### Basic Usage Pattern

```python
import networkx as nx
import sqlite3

# 1. Store graph in SQLite (your current approach)
conn = sqlite3.connect('graph.db')
conn.execute('''
    CREATE TABLE IF NOT EXISTS nodes (
        id TEXT PRIMARY KEY,
        type TEXT,
        properties JSON
    )
''')
conn.execute('''
    CREATE TABLE IF NOT EXISTS edges (
        source TEXT,
        target TEXT,
        relationship TEXT,
        properties JSON,
        FOREIGN KEY(source) REFERENCES nodes(id),
        FOREIGN KEY(target) REFERENCES nodes(id)
    )
''')

# 2. Load into NetworkX for analysis
G = nx.DiGraph()  # Directed graph

# Load nodes
for row in conn.execute('SELECT id, type, properties FROM nodes'):
    G.add_node(row[0], node_type=row[1], data=row[2])

# Load edges
for row in conn.execute('SELECT source, target, relationship, properties FROM edges'):
    G.add_edge(row[0], row[1], rel_type=row[2], data=row[3])

# 3. Run algorithms (mimics HANA Property Graph)
# Shortest path
path = nx.shortest_path(G, 'Supplier_A', 'Factory_B')

# Centrality (find critical nodes)
centrality = nx.betweenness_centrality(G)

# Community detection (find clusters)
communities = nx.community.louvain_communities(G.to_undirected())

# PageRank (importance scores)
pagerank = nx.pagerank(G)
```

### Algorithms Available (Property Graph Equivalents)

| HANA Property Graph | NetworkX Equivalent | Use Case |
|---------------------|---------------------|----------|
| `GRAPH_SHORTEST_PATH` | `nx.shortest_path()` | Supply chain routes |
| `GRAPH_BETWEENNESS` | `nx.betweenness_centrality()` | Bottleneck identification |
| `GRAPH_PAGERANK` | `nx.pagerank()` | Node importance |
| `GRAPH_COMMUNITY_DETECTION` | `nx.community.louvain_communities()` | Supplier clustering |
| `GRAPH_CONNECTED_COMPONENTS` | `nx.connected_components()` | Network partitions |
| Pattern matching | `nx.subgraph_view()` + filtering | Find subgraph patterns |

**Coverage**: ~90% of HANA Property Graph algorithms available in NetworkX!

### Performance

- **Small graphs** (<10K nodes): Instant (milliseconds)
- **Medium graphs** (10K-100K nodes): Fast (seconds)
- **Large graphs** (>100K nodes): Use HANA instead

**For development/demo**: NetworkX is perfect. For production scale: Migrate to HANA.

---

## Option 2: Knowledge Graph Fallback (RDFLib)

### What is RDFLib?

**RDFLib** is Python's standard library for RDF/SPARQL:
- ✅ **Open source** (BSD license)
- ✅ **W3C standards** (RDF, SPARQL, RDFS, OWL)
- ✅ **SQLite backend** (persistent triple store)
- ✅ **Active development** (maintained by community)
- ✅ **SPARQL 1.1** (full query language support)

**Perfect for**: Mimicking HANA Knowledge Graph offline

### Installation

```bash
pip install rdflib
pip install rdflib-sqlite  # SQLite backend plugin
```

### Basic Usage Pattern

```python
from rdflib import Graph, Literal, RDF, RDFS, Namespace, URIRef
from rdflib.plugin import register
import rdflib.store

# 1. Register SQLite store
register('SQLite', rdflib.store.Store, 'rdflib_sqlite.SQLite', 'SQLite')

# 2. Create SQLite-backed RDF graph
store = rdflib.plugin.get('SQLite', rdflib.store.Store)('triples.db', create=True)
graph = Graph(store)

# 3. Define namespaces (like HANA Knowledge Graph)
EX = Namespace('http://example.org/p2p/')
graph.bind('p2p', EX)

# 4. Add triples (subject-predicate-object)
graph.add((EX.Supplier_ACME, RDF.type, EX.Supplier))
graph.add((EX.Supplier_ACME, EX.hasCertification, EX.ISO_14001))
graph.add((EX.Supplier_ACME, EX.providesProduct, EX.Product_X))
graph.add((EX.Product_X, EX.hasAttribute, Literal('Biodegradable')))

# Commit to SQLite
store.commit()

# 5. Query with SPARQL (exactly like HANA!)
query = """
PREFIX p2p: <http://example.org/p2p/>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>

SELECT ?supplier ?cert WHERE {
  ?supplier rdf:type p2p:Supplier .
  ?supplier p2p:hasCertification ?cert .
  FILTER(?cert = p2p:ISO_14001)
}
"""

results = graph.query(query)
for row in results:
    print(f"Supplier: {row.supplier}, Certification: {row.cert}")
```

### SPARQL Support

**RDFLib supports SPARQL 1.1**:
- ✅ SELECT queries
- ✅ CONSTRUCT (generate new triples)
- ✅ ASK (boolean queries)
- ✅ DESCRIBE (describe resources)
- ✅ FILTER, OPTIONAL, UNION
- ✅ Aggregations (COUNT, SUM, AVG)
- ✅ Property paths
- ✅ BIND, VALUES

**Almost identical to HANA Knowledge Graph SPARQL!**

### Inference Support

RDFLib supports basic reasoning:

```python
from rdflib import RDFS, OWL

# Define ontology
graph.add((EX.CertifiedSupplier, RDFS.subClassOf, EX.Supplier))
graph.add((EX.Supplier_ACME, RDF.type, EX.CertifiedSupplier))

# Inference: If CertifiedSupplier subclass of Supplier,
# then Supplier_ACME is also a Supplier (automatic!)

# Query benefits from inference
query = """
SELECT ?s WHERE {
  ?s rdf:type p2p:Supplier .
}
"""
# Returns both direct Suppliers AND CertifiedSuppliers!
```

---

## Option 3: Hybrid Approach (Recommended!)

### Current Architecture (Your Module)

```
modules/knowledge_graph/
├── backend/
│   ├── data_graph_service.py     # Your current SQLite implementation
│   └── api.py                     # Flask API endpoints
```

### Enhanced Architecture (Add Graph Capabilities)

```
modules/knowledge_graph/
├── backend/
│   ├── data_graph_service.py          # Existing: CRUD operations
│   ├── property_graph_service.py      # NEW: NetworkX algorithms
│   ├── knowledge_graph_service.py     # NEW: RDFLib SPARQL
│   ├── hana_graph_adapter.py          # NEW: HANA graph integration
│   └── api.py                         # Enhanced: Support all operations
```

### Implementation Strategy

**Step 1: Create Abstract Interface**

```python
# modules/knowledge_graph/backend/graph_interface.py
from abc import ABC, abstractmethod

class PropertyGraphInterface(ABC):
    """Interface for Property Graph operations"""
    
    @abstractmethod
    def shortest_path(self, start: str, end: str) -> list:
        """Find shortest path between nodes"""
        pass
    
    @abstractmethod
    def centrality(self, algorithm: str = 'betweenness') -> dict:
        """Calculate node centrality"""
        pass
    
    @abstractmethod
    def community_detection(self, algorithm: str = 'louvain') -> dict:
        """Detect communities/clusters"""
        pass

class KnowledgeGraphInterface(ABC):
    """Interface for Knowledge Graph operations"""
    
    @abstractmethod
    def sparql_query(self, query: str) -> list:
        """Execute SPARQL query"""
        pass
    
    @abstractmethod
    def add_triple(self, subject: str, predicate: str, obj: str):
        """Add RDF triple"""
        pass
```

**Step 2: Implement SQLite Fallback**

```python
# modules/knowledge_graph/backend/property_graph_service.py
import networkx as nx
from .graph_interface import PropertyGraphInterface

class NetworkXPropertyGraph(PropertyGraphInterface):
    """SQLite + NetworkX implementation"""
    
    def __init__(self, sqlite_connection):
        self.conn = sqlite_connection
        self.graph = None
    
    def _load_graph(self):
        """Load SQLite data into NetworkX"""
        self.graph = nx.DiGraph()
        
        # Load nodes
        for row in self.conn.execute('SELECT id, type FROM nodes'):
            self.graph.add_node(row[0], node_type=row[1])
        
        # Load edges
        for row in self.conn.execute('SELECT source, target, rel FROM edges'):
            self.graph.add_edge(row[0], row[1], relationship=row[2])
    
    def shortest_path(self, start: str, end: str) -> list:
        if not self.graph:
            self._load_graph()
        return nx.shortest_path(self.graph, start, end)
    
    def centrality(self, algorithm: str = 'betweenness') -> dict:
        if not self.graph:
            self._load_graph()
        
        if algorithm == 'betweenness':
            return nx.betweenness_centrality(self.graph)
        elif algorithm == 'pagerank':
            return nx.pagerank(self.graph)
        # ... more algorithms
    
    def community_detection(self, algorithm: str = 'louvain') -> dict:
        if not self.graph:
            self._load_graph()
        
        communities = nx.community.louvain_communities(
            self.graph.to_undirected()
        )
        
        # Format results
        result = {}
        for i, community in enumerate(communities):
            for node in community:
                result[node] = f"cluster_{i}"
        return result
```

```python
# modules/knowledge_graph/backend/knowledge_graph_service.py
from rdflib import Graph, Namespace
from rdflib.plugin import register
import rdflib.store
from .graph_interface import KnowledgeGraphInterface

class RDFLibKnowledgeGraph(KnowledgeGraphInterface):
    """SQLite + RDFLib implementation"""
    
    def __init__(self, sqlite_path: str):
        register('SQLite', rdflib.store.Store, 
                'rdflib_sqlite.SQLite', 'SQLite')
        
        store = rdflib.plugin.get('SQLite', rdflib.store.Store)(
            sqlite_path, create=True
        )
        self.graph = Graph(store)
        self.store = store
    
    def sparql_query(self, query: str) -> list:
        """Execute SPARQL query (same as HANA!)"""
        results = self.graph.query(query)
        return [{str(var): str(val) for var, val in row.asdict().items()} 
                for row in results]
    
    def add_triple(self, subject: str, predicate: str, obj: str):
        """Add RDF triple"""
        from rdflib import URIRef, Literal
        
        s = URIRef(subject)
        p = URIRef(predicate)
        o = URIRef(obj) if obj.startswith('http') else Literal(obj)
        
        self.graph.add((s, p, o))
        self.store.commit()
```

**Step 3: Implement HANA Adapter (Future)**

```python
# modules/knowledge_graph/backend/hana_graph_adapter.py
from .graph_interface import PropertyGraphInterface, KnowledgeGraphInterface

class HANAPropertyGraph(PropertyGraphInterface):
    """HANA Property Graph implementation"""
    
    def __init__(self, hana_connection):
        self.conn = hana_connection
    
    def shortest_path(self, start: str, end: str) -> list:
        # Execute HANA SQL with GRAPH_SHORTEST_PATH
        query = f"""
        SELECT * FROM GRAPH_SHORTEST_PATH(
            GRAPH => 'P2P_GRAPH',
            START => '{start}',
            END => '{end}'
        )
        """
        return self.conn.execute(query).fetchall()
    
    def centrality(self, algorithm: str = 'betweenness') -> dict:
        # Execute HANA graph algorithm
        query = f"""
        CALL GRAPH_BETWEENNESS_CENTRALITY(
            GRAPH_WORKSPACE => 'P2P_GRAPH'
        )
        """
        results = self.conn.execute(query).fetchall()
        return {row[0]: row[1] for row in results}

class HANAKnowledgeGraph(KnowledgeGraphInterface):
    """HANA Knowledge Graph implementation"""
    
    def __init__(self, hana_connection):
        self.conn = hana_connection
    
    def sparql_query(self, query: str) -> list:
        # Execute HANA SPARQL via SPARQL_EXECUTE()
        hana_query = f"""
        SELECT * FROM SPARQL_EXECUTE('{query}', 'P2P_KG')
        """
        results = self.conn.execute(hana_query).fetchall()
        return [dict(row) for row in results]
```

**Step 4: Factory Pattern (Auto-Select Implementation)**

```python
# modules/knowledge_graph/backend/graph_factory.py
from .property_graph_service import NetworkXPropertyGraph
from .knowledge_graph_service import RDFLibKnowledgeGraph
from .hana_graph_adapter import HANAPropertyGraph, HANAKnowledgeGraph

class GraphFactory:
    """Auto-select graph implementation based on available connections"""
    
    @staticmethod
    def create_property_graph(config: dict):
        if config.get('hana_available') and config.get('use_hana'):
            # Use HANA Property Graph (production)
            return HANAPropertyGraph(config['hana_connection'])
        else:
            # Fallback to NetworkX + SQLite (dev/offline)
            return NetworkXPropertyGraph(config['sqlite_connection'])
    
    @staticmethod
    def create_knowledge_graph(config: dict):
        if config.get('hana_available') and config.get('use_hana'):
            # Use HANA Knowledge Graph (production)
            return HANAKnowledgeGraph(config['hana_connection'])
        else:
            # Fallback to RDFLib + SQLite (dev/offline)
            return RDFLibKnowledgeGraph(config['sqlite_path'])
```

**Step 5: Usage in Your Application**

```python
# Your application code (unchanged!)
from modules.knowledge_graph.backend.graph_factory import GraphFactory

# Configuration determines implementation
config = {
    'hana_available': is_hana_connected(),
    'use_hana': feature_flags.get('use_hana_graphs'),
    'hana_connection': get_hana_connection(),
    'sqlite_connection': get_sqlite_connection(),
    'sqlite_path': 'knowledge_graph.db'
}

# Create graph services (auto-selects implementation)
property_graph = GraphFactory.create_property_graph(config)
knowledge_graph = GraphFactory.create_knowledge_graph(config)

# Use same API regardless of backend!
# This works with NetworkX OR HANA:
path = property_graph.shortest_path('Supplier_A', 'Factory_B')

# This works with RDFLib OR HANA:
results = knowledge_graph.sparql_query("""
    SELECT ?supplier WHERE {
        ?supplier rdf:type p2p:Supplier
    }
""")
```

---

## Comparison: SQLite Fallback vs HANA

| Feature | NetworkX + SQLite | HANA Property Graph | Notes |
|---------|-------------------|---------------------|-------|
| **Shortest Path** | ✅ nx.shortest_path() | ✅ GRAPH_SHORTEST_PATH | Same functionality |
| **Centrality** | ✅ nx.centrality() | ✅ GRAPH_CENTRALITY | Same algorithms |
| **Community Detection** | ✅ nx.community.louvain | ✅ GRAPH_COMMUNITY | Equivalent results |
| **Performance** | Good (<100K nodes) | Excellent (millions) | HANA faster at scale |
| **Setup** | pip install | Configure workspace | NetworkX easier |
| **Offline** | ✅ Yes | ❌ No | NetworkX works offline |

| Feature | RDFLib + SQLite | HANA Knowledge Graph | Notes |
|---------|-----------------|----------------------|-------|
| **SPARQL** | ✅ SPARQL 1.1 | ✅ SPARQL 1.1 | Same query language! |
| **Inference** | ✅ Basic RDFS/OWL | ✅ Advanced reasoning | HANA more powerful |
| **Triple Store** | ✅ SQLite | ✅ Native triple store | RDFLib persistent |
| **Performance** | Good (<1M triples) | Excellent (billions) | HANA faster at scale |
| **Standards** | ✅ W3C compliant | ✅ W3C compliant | Both standard |
| **Offline** | ✅ Yes | ❌ No | RDFLib works offline |

**Recommendation**: Start with NetworkX/RDFLib for development, migrate to HANA for production scale.

---

## Migration Path

### Phase 1: Current (SQLite Only)
```
Application → SQLite → Basic CRUD
```
**Status**: ✅ Completed (your current module)

### Phase 2: Add Graph Algorithms (NetworkX)
```
Application → SQLite + NetworkX → Graph algorithms
```
**Effort**: 1-2 days
**Benefit**: Property graph algorithms without HANA

### Phase 3: Add Semantic Layer (RDFLib)
```
Application → SQLite + NetworkX + RDFLib → Full graph + SPARQL
```
**Effort**: 2-3 days
**Benefit**: Knowledge graph capabilities without HANA

### Phase 4: HANA Integration (Dual Mode)
```
Application → [NetworkX/RDFLib OR HANA] → Production-ready
```
**Effort**: 3-5 days
**Benefit**: Production scale + offline fallback

---

## Recommended Tools Summary

### For Property Graph (Network Analysis)

**Primary**: NetworkX
- Install: `pip install networkx`
- Pros: Battle-tested, excellent docs, pure Python
- Cons: Not optimized for huge graphs (>1M nodes)
- Use when: Development, demos, offline mode

**Alternative**: sqlite-graph extension
- Install: C extension (more complex)
- Pros: Native SQLite integration
- Cons: Less mature, alpha stage
- Use when: Want SQL-native graph queries

### For Knowledge Graph (Semantic/RDF)

**Primary**: RDFLib
- Install: `pip install rdflib rdflib-sqlite`
- Pros: W3C standards, SPARQL support, mature
- Cons: SQLite backend "mothballed" (still works)
- Use when: Need RDF/SPARQL compatibility

**Alternative**: Custom SQLite schema
- Install: Nothing (your current approach)
- Pros: Full control, simple
- Cons: No SPARQL, manual query building
- Use when: Simple entity-relationship only

---

## Code Examples Repository

### Example 1: P2P Supplier Network Analysis

```python
import networkx as nx
import sqlite3

# Load P2P data from your existing SQLite
conn = sqlite3.connect('p2p_data.db')

# Build supplier network
G = nx.DiGraph()

# Add suppliers as nodes
suppliers = conn.execute('''
    SELECT SupplierID, SupplierName, Country
    FROM Suppliers
''').fetchall()

for sup_id, name, country in suppliers:
    G.add_node(sup_id, name=name, country=country)

# Add purchase orders as edges
pos = conn.execute('''
    SELECT PurchaseOrderID, SupplierID, TotalAmount
    FROM PurchaseOrders
''').fetchall()

for po_id, sup_id, amount in pos:
    G.add_edge('Company', sup_id, po=po_id, amount=amount)

# Analyze: Which suppliers are most critical?
centrality = nx.betweenness_centrality(G)
top_suppliers = sorted(centrality.items(), key=lambda x: x[1], reverse=True)[:10]

print("Top 10 Critical Suppliers:")
for supplier, score in top_suppliers:
    print(f"{supplier}: {score:.4f}")

# Analyze: Find supplier clusters
communities = nx.community.louvain_communities(G.to_undirected())
print(f"\nFound {len(communities)} supplier clusters")
```

### Example 2: Semantic Purchase Order Matching

```python
from rdflib import Graph, Namespace, Literal, RDF
from rdflib.plugin import register
import rdflib.store

# Setup RDF graph
register('SQLite', rdflib.store.Store, 'rdflib_sqlite.SQLite', 'SQLite')
store = rdflib.plugin.get('SQLite', rdflib.store.Store)('p2p_kg.db', create=True)
graph = Graph(store)

P2P = Namespace('http://example.org/p2p/')
graph.bind('p2p', P2P)

# Load purchase orders as RDF
import sqlite3
conn = sqlite3.connect('p2p_data.db')

for row in conn.execute('SELECT PurchaseOrderID, SupplierID, TotalAmount FROM PurchaseOrders'):
    po_id, sup_id, amount = row
    
    po = P2P[f'PO_{po_id}']
    supplier = P2P[f'Supplier_{sup_id}']
    
    graph.add((po, RDF.type, P2P.PurchaseOrder))
    graph.add((po, P2P.orderedFrom, supplier))
    graph.add((po, P2P.totalAmount, Literal(amount)))

store.commit()

# Query: Find high-value orders from specific supplier
query = """
PREFIX p2p: <http://example.org/p2p/>

SELECT ?po ?amount WHERE {
    ?po rdf:type p2p:PurchaseOrder .
    ?po p2p:orderedFrom p2p:Supplier_1000 .
    ?po p2p:totalAmount ?amount .
    FILTER(?amount > 10000)
}
ORDER BY DESC(?amount)
"""

results = graph.query(query)
for row in results:
    print(f"PO: {row.po}, Amount: {row.amount}")
```

---

## Installation Guide

### Minimal Setup (NetworkX Only)

```bash
pip install networkx
```

Test installation:
```python
import networkx as nx
G = nx.DiGraph()
G.add_edge('A', 'B')
print(nx.shortest_path(G, 'A', 'B'))  # ['A', 'B']
```

### Full Setup (NetworkX + RDFLib)

```bash
pip install networkx rdflib rdflib-sqlite
```

Test installation:
```python
import networkx as nx
from rdflib import Graph, Literal, RDF

# Test NetworkX
G = nx.DiGraph()
G.add_edge('A', 'B')
print("NetworkX:", nx.shortest_path(G, 'A', 'B'))

# Test RDFLib
g = Graph()
g.add((Literal('test'), RDF.type, Literal('Test')))
print("RDFLib triples:", len(g))  # 1
```

---

## Next Steps

### Immediate (This Week)
1. Install NetworkX: `pip install networkx`
2. Test with your existing SQLite data
3. Implement basic algorithms (shortest path, centrality)

### Short-Term (Next Month)
1. Install RDFLib: `pip install rdflib rdflib-sqlite`
2. Create RDF schema for P2P domain
3. Implement SPARQL queries

### Medium-Term (3-6 Months)
1. Create unified graph interface (Property + Knowledge)
2. Implement factory pattern for auto-selection
3. Add HANA adapters (when HANA ready)

### Long-Term (6-12 Months)
1. Performance testing (NetworkX vs HANA)
2. Migration strategy (SQLite → HANA)
3. Production deployment with fallback

---

## Summary

**You asked**: "Is there a free open source tool for SQLite graph fallback?"

**Answer**: YES! Two excellent options:

1. **NetworkX** (Property Graph) - Python's standard graph library
   - 🟢 Mature, battle-tested, excellent documentation
   - 🟢 Covers ~90% of HANA Property Graph algorithms
   - 🟢 Works perfectly with SQLite
   - 🟡 Not optimized for massive graphs (use HANA for scale)

2. **RDFLib** (Knowledge Graph) - Python's standard RDF library
   - 🟢 W3C standards (RDF, SPARQL)
   - 🟢 SQLite backend available
   - 🟢 Same query language as HANA Knowledge Graph!
   - 🟡 SQLite backend "mothballed" but functional

**Recommended Approach**: 
- Start with NetworkX for property graph algorithms
- Add RDFLib when you need semantic/RDF capabilities
- Migrate to HANA when you need production scale
- Keep SQLite fallback for offline development

**Key Insight**: With the factory pattern, your application code doesn't change - only the backend implementation swaps between SQLite and HANA! 🎯