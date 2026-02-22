# Knowledge Graph v2 - API Design & Separation of Concerns

**Date**: 2026-02-08  
**Context**: Supplement to [[Knowledge Graph v2 Architecture Proposal]]  
**Topic**: Why vis.js formatting belongs in FRONTEND, not backend

---

## 🎯 The User's Excellent Point

**User Question**: "vis.js is actually a UX element. why do we handle it here?"

**Answer**: You're **100% correct**! This is a **separation of concerns violation** in the original proposal.

---

## 🏗️ Correct Architecture: Backend Agnostic, Frontend Decides

### The Right Way (Backend Agnostic)

```
┌────────────────────────────────────────────────────┐
│              BACKEND (Python/Flask)                │
│                                                    │
│  Returns GENERIC graph data:                      │
│  {                                                 │
│    "nodes": [                                      │
│      {"id": "n1", "label": "Supplier",            │
│       "type": "table", "row_count": 10}           │
│    ],                                              │
│    "edges": [                                      │
│      {"source": "n2", "target": "n1",             │
│       "type": "fk", "label": "FK_Supplier"}       │
│    ]                                               │
│  }                                                 │
│                                                    │
│  ↓ JSON over HTTP                                 │
└────────────────────────────────────────────────────┘
                      ↓
┌────────────────────────────────────────────────────┐
│           FRONTEND (JavaScript)                    │
│                                                    │
│  Adapts generic data to visualization library:    │
│                                                    │
│  Option 1: vis.js Network                         │
│    nodes: [{id, label, group: type}]              │
│    edges: [{from: source, to: target}]            │
│                                                    │
│  Option 2: D3.js Force                            │
│    nodes: [{id, label}]                           │
│    links: [{source, target}]                      │
│                                                    │
│  Option 3: Cytoscape.js                           │
│    elements: [{data: {id, label, source, target}}]│
│                                                    │
│  Frontend chooses library, not backend!           │
└────────────────────────────────────────────────────┘
```

---

## ❌ What's Wrong with Current Approach

### Problem 1: Backend Knows About vis.js

**Bad (v1 & original v2 proposal)**:
```python
# Backend returns vis.js-specific format
def to_dict(self) -> Dict[str, Any]:
    return {
        'nodes': [...],
        'edges': [
            {'from': 'n1', 'to': 'n2'}  # ❌ 'from'/'to' is vis.js specific!
        ]
    }
```

**Why bad**:
- ❌ Backend coupled to frontend library (vis.js)
- ❌ Can't switch to D3.js without changing backend
- ❌ Backend shouldn't know about UX concerns
- ❌ Violates separation of concerns

---

### Problem 2: Frontend Can't Choose Library

**Bad**:
```javascript
// Frontend forced to use vis.js
fetch('/api/knowledge-graph/graph')
  .then(res => res.json())
  .then(data => {
    // Data is already in vis.js format
    // Can't use D3.js or Cytoscape without backend change!
    new vis.Network(container, data.graph, options);
  });
```

---

## ✅ Correct Approach: Generic Backend, Adaptable Frontend

### Backend Returns Generic Format

```python
# domain/graph.py
class Graph:
    def to_dict(self) -> Dict[str, Any]:
        """
        Returns GENERIC graph format
        
        NOT vis.js specific! Works with ANY visualization library.
        """
        return {
            'nodes': [
                {
                    'id': n.id,
                    'label': n.label,
                    'type': n.type.value,  # Generic 'type', not 'group'
                    'properties': n.properties
                }
                for n in self._nodes.values()
            ],
            'edges': [
                {
                    'source': e.source_id,  # Generic 'source', not 'from'
                    'target': e.target_id,  # Generic 'target', not 'to'
                    'type': e.type.value,
                    'label': e.label,
                    'properties': e.properties
                }
                for e in self._edges
            ]
        }


# facade/knowledge_graph_facade_v2.py
class KnowledgeGraphFacadeV2:
    def get_graph(self, graph_type, use_cache=True):
        # ... load/build graph ...
        
        # Return GENERIC format (NOT vis.js!)
        return {
            'success': True,
            'graph': graph.to_dict(),  # Generic format
            'cache_used': cache_hit,
            'metadata': {
                'node_count': len(graph.nodes),
                'edge_count': len(graph.edges),
                'graph_type': graph.type.value
            }
        }
```

**Benefits**:
- ✅ Backend is visualization-library agnostic
- ✅ Frontend can choose ANY library (vis.js, D3, Cytoscape)
- ✅ Proper separation of concerns
- ✅ Backend focuses on BUSINESS LOGIC, not UX

---

### Frontend Adapts to Visualization Library

```javascript
// frontend/adapters/visjs_adapter.js
class VisJsAdapter {
    /**
     * Adapts generic graph to vis.js format
     * 
     * Backend returns: {nodes: [{id, label, type}], edges: [{source, target}]}
     * vis.js expects: {nodes: [{id, label, group}], edges: [{from, to}]}
     */
    static adapt(genericGraph) {
        return {
            nodes: genericGraph.nodes.map(n => ({
                id: n.id,
                label: n.label,
                group: n.type,  // Map 'type' → 'group' (vis.js term)
                title: this._createTooltip(n),
                ...n.properties
            })),
            edges: genericGraph.edges.map(e => ({
                from: e.source,  // Map 'source' → 'from' (vis.js term)
                to: e.target,    // Map 'target' → 'to' (vis.js term)
                label: e.label,
                arrows: 'to',
                ...e.properties
            }))
        };
    }
    
    static _createTooltip(node) {
        return `${node.label} (${node.type})`;
    }
}


// frontend/knowledge_graph_client.js
class KnowledgeGraphClient {
    async getGraph(graphType = 'schema') {
        // 1. Fetch GENERIC graph from backend
        const response = await fetch(
            `/api/knowledge-graph/graph?type=${graphType}`
        );
        const data = await response.json();
        
        // 2. Adapt to vis.js format (frontend concern!)
        const visJsGraph = VisJsAdapter.adapt(data.graph);
        
        // 3. Render with vis.js
        const network = new vis.Network(
            container,
            visJsGraph,  // vis.js format
            options
        );
        
        return network;
    }
}
```

**Benefits**:
- ✅ Backend unchanged if we switch to D3.js
- ✅ Frontend controls visualization format
- ✅ Clear separation: Backend = data, Frontend = presentation
- ✅ Easy to support multiple libraries simultaneously

---

## 📊 Comparison: Wrong vs Right

### Wrong Approach (Coupling)

```
Backend (Python)
  ├── Returns vis.js format ❌
  │   └── {from: 'n1', to: 'n2'}
  └── Knows about UX library ❌

Frontend (JavaScript)
  └── Uses vis.js directly
      └── No adaptation needed
      
Problem: Can't change visualization library!
```

### Right Approach (Decoupling)

```
Backend (Python)
  ├── Returns GENERIC format ✅
  │   └── {source: 'n1', target: 'n2'}
  └── Library-agnostic ✅

Frontend (JavaScript)
  ├── Adapter Layer ✅
  │   ├── VisJsAdapter (generic → vis.js)
  │   ├── D3Adapter (generic → D3)
  │   └── CytoscapeAdapter (generic → Cytoscape)
  └── Chooses library dynamically ✅
  
Benefit: Switch libraries without backend changes!
```

---

## 🎯 Updated v2 Architecture

### Remove GraphVisualizationService

**Original proposal had** (WRONG):
```python
# services/graph_visualization_service.py
class GraphVisualizationService:
    def format_for_visjs(self, graph):  # ❌ Backend knows vis.js!
        pass
```

**Correct v2** (RIGHT):
```python
# services/ - NO visualization service!
# Backend doesn't know about vis.js, D3, or any UX library

# Just return generic graph data:
class GraphBuilderService:
    def build_schema_graph(self, schema: str) -> Graph:
        # Returns Graph domain object
        pass  # Graph.to_dict() returns generic format
```

### Updated Service Layer

```
┌─────────────────────────────────────────────────┐
│          SERVICE LAYER (v2 Corrected)           │
│  ┌────────────────┬────────────────┐            │
│  │ GraphBuilder   │ GraphQuery     │            │
│  │   Service      │   Service      │            │
│  │ (build graphs) │ (neighbors,    │            │
│  │                │  paths)        │            │
│  └────────────────┴────────────────┘            │
│                                                  │
│  ❌ REMOVED: GraphVisualizationService          │
│     (moved to frontend adapter layer)           │
└─────────────────────────────────────────────────┘
```

---

## 🔄 How Frontend Adapts (3 Examples)

### Example 1: vis.js Network (Current)

```javascript
// frontend/adapters/visjs_adapter.js
const genericGraph = await fetch('/api/knowledge-graph/graph').then(r => r.json());

const visJsGraph = {
    nodes: genericGraph.graph.nodes.map(n => ({
        id: n.id,
        label: n.label,
        group: n.type,  // Map 'type' → 'group'
        title: `${n.label} (${n.properties.row_count} rows)`
    })),
    edges: genericGraph.graph.edges.map(e => ({
        from: e.source,  // Map 'source' → 'from'
        to: e.target,    // Map 'target' → 'to'
        label: e.label,
        arrows: 'to'
    }))
};

new vis.Network(container, visJsGraph, options);
```

### Example 2: D3.js Force Layout (Alternative)

```javascript
// frontend/adapters/d3_adapter.js
const genericGraph = await fetch('/api/knowledge-graph/graph').then(r => r.json());

const d3Graph = {
    nodes: genericGraph.graph.nodes,  // D3 uses 'id' directly
    links: genericGraph.graph.edges.map(e => ({
        source: e.source,  // D3 expects 'source'
        target: e.target,  // D3 expects 'target'
        value: 1
    }))
};

const simulation = d3.forceSimulation(d3Graph.nodes)
    .force('link', d3.forceLink(d3Graph.links).id(d => d.id))
    .force('charge', d3.forceManyBody())
    .force('center', d3.forceCenter(width / 2, height / 2));
```

### Example 3: Cytoscape.js (Another Alternative)

```javascript
// frontend/adapters/cytoscape_adapter.js
const genericGraph = await fetch('/api/knowledge-graph/graph').then(r => r.json());

const cytoscapeGraph = {
    elements: [
        // Nodes
        ...genericGraph.graph.nodes.map(n => ({
            data: {id: n.id, label: n.label}
        })),
        // Edges
        ...genericGraph.graph.edges.map(e => ({
            data: {source: e.source, target: e.target}
        }))
    ]
};

cytoscape({container, elements: cytoscapeGraph.elements});
```

---

## 🎓 Why This Separation Matters

### Benefit 1: Flexibility

**With separation**:
```
User: "Let's try D3.js instead of vis.js"
Dev: "Sure! Just swap adapter, backend unchanged"
Time: 30 minutes (frontend only)
```

**Without separation** (current v1):
```
User: "Let's try D3.js instead of vis.js"
Dev: "Need to change backend to return D3 format"
Time: 4 hours (backend + frontend + testing)
```

### Benefit 2: Multi-Library Support

**With separation**:
```javascript
// User can choose visualization library!
if (userPreference === 'vis.js') {
    graph = VisJsAdapter.adapt(genericData);
} else if (userPreference === 'd3') {
    graph = D3Adapter.adapt(genericData);
}
```

**Without separation**:
- Backend hardcoded to vis.js format
- Can't support multiple libraries

### Benefit 3: Backend Focus

**With separation**:
- Backend focuses on: Building graphs, caching, querying
- Frontend focuses on: Visualization, interaction, UX

**Without separation**:
- Backend mixed with UX concerns
- Harder to test, maintain, modify

---

## 🔧 Updated v2 Design (Corrected)

### Backend: Generic Format Only

```python
# domain/graph_node.py
@dataclass
class GraphNode:
    id: str
    label: str
    type: NodeType
    properties: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Returns GENERIC node format
        
        Frontend adapts this to vis.js, D3, Cytoscape, etc.
        Backend doesn't know which library will be used!
        """
        return {
            'id': self.id,
            'label': self.label,
            'type': self.type.value,  # Generic (not 'group')
            'properties': self.properties
        }


# domain/graph_edge.py
@dataclass(frozen=True)
class GraphEdge:
    source_id: str
    target_id: str
    type: EdgeType
    label: Optional[str] = None
    properties: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Returns GENERIC edge format
        
        Uses 'source'/'target' (generic graph terms)
        NOT 'from'/'to' (vis.js specific terms)
        """
        return {
            'source': self.source_id,  # Generic
            'target': self.target_id,  # Generic
            'type': self.type.value,
            'label': self.label,
            'properties': self.properties
        }


# facade/knowledge_graph_facade_v2.py
class KnowledgeGraphFacadeV2:
    def __init__(
        self,
        builder_service: GraphBuilderService,
        cache_repo: AbstractGraphCacheRepository,
        query_service: GraphQueryService
        # ❌ NO viz_service (removed!)
    ):
        self.builder = builder_service
        self.cache = cache_repo
        self.query = query_service
    
    def get_graph(self, graph_type, use_cache=True):
        # ... load/build graph ...
        
        # Return GENERIC format (frontend decides visualization)
        return {
            'success': True,
            'graph': graph.to_dict(),  # Generic format
            'cache_used': cache_hit,
            'metadata': {
                'node_count': len(graph.nodes),
                'edge_count': len(graph.edges),
                'graph_type': graph.type.value
            }
        }
```

---

### Frontend: Adapter Pattern

```javascript
// frontend/adapters/graph_adapter.js
class GraphAdapter {
    /**
     * Factory: Creates adapter based on library choice
     */
    static create(library) {
        switch (library) {
            case 'vis.js':
                return new VisJsAdapter();
            case 'd3':
                return new D3Adapter();
            case 'cytoscape':
                return new CytoscapeAdapter();
            default:
                throw new Error(`Unknown library: ${library}`);
        }
    }
}


// frontend/adapters/visjs_adapter.js
class VisJsAdapter {
    /**
     * Adapts generic backend format to vis.js
     * 
     * Generic: {source, target, type}
     * vis.js: {from, to, group}
     */
    adapt(genericGraph) {
        return {
            nodes: genericGraph.nodes.map(n => ({
                id: n.id,
                label: n.label,
                group: n.type,      // Generic 'type' → vis.js 'group'
                title: this._tooltip(n),
                color: this._getColor(n.type),
                font: {size: 14, face: 'Arial'}
            })),
            edges: genericGraph.edges.map(e => ({
                from: e.source,     // Generic 'source' → vis.js 'from'
                to: e.target,       // Generic 'target' → vis.js 'to'
                label: e.label,
                arrows: 'to',
                color: {color: '#848484', highlight: '#2B7CE9'}
            }))
        };
    }
    
    _tooltip(node) {
        return `${node.label}\nType: ${node.type}\nRows: ${node.properties.row_count || 0}`;
    }
    
    _getColor(nodeType) {
        const colors = {
            'table': '#7BE141',
            'record': '#FB7E81',
            'product': '#6E6EFD'
        };
        return {background: colors[nodeType] || '#97C2FC'};
    }
}


// frontend/knowledge_graph_client.js
class KnowledgeGraphClient {
    constructor(library = 'vis.js') {
        this.adapter = GraphAdapter.create(library);
    }
    
    async renderGraph(container, graphType = 'schema') {
        // 1. Fetch GENERIC graph from backend
        const response = await fetch(
            `/api/knowledge-graph/graph?type=${graphType}`
        );
        const data = await response.json();
        
        // 2. Adapt to chosen library (UX concern!)
        const libraryGraph = this.adapter.adapt(data.graph);
        
        // 3. Render
        if (this.library === 'vis.js') {
            return new vis.Network(container, libraryGraph, this.options);
        } else if (this.library === 'd3') {
            return this._renderD3(container, libraryGraph);
        }
        // ... other libraries
    }
}
```

---

## 🎯 Benefits of Correct Separation

### 1. Backend Simplicity

**Without separation**:
```python
# Backend knows about vis.js colors, layouts, tooltips
def format_for_visjs(graph):
    # 50+ LOC of vis.js specific logic ❌
    pass
```

**With separation**:
```python
# Backend returns generic data (10 LOC)
def to_dict(graph):
    return {'nodes': [...], 'edges': [...]}  # ✅ Simple!
```

### 2. Frontend Flexibility

**Without separation**:
- Can only use vis.js (backend hardcoded)
- Switching libraries = backend + frontend rewrite

**With separation**:
- Use any library (just add adapter)
- Switching libraries = frontend adapter only (30 min)

### 3. Testing

**Without separation**:
```python
# Backend tests need to verify vis.js format ❌
def test_format_for_visjs():
    result = service.format_for_visjs(graph)
    assert 'from' in result['edges'][0]  # Testing UX format in backend!
```

**With separation**:
```python
# Backend tests verify generic format ✅
def test_to_dict():
    result = graph.to_dict()
    assert 'source' in result['edges'][0]  # Testing business data only
```

```javascript
// Frontend tests verify vis.js adaptation
test('VisJsAdapter maps source to from', () => {
    const generic = {edges: [{source: 'n1', target: 'n2'}]};
    const visjs = VisJsAdapter.adapt(generic);
    expect(visjs.edges[0].from).toBe('n1');  // UX testing in frontend!
});
```

---

## 📋 Updated File Structure

```
modules/knowledge_graph_v2/
├── backend/
│   ├── domain/          # Generic Graph, GraphNode, GraphEdge
│   ├── repositories/    # Data access
│   ├── services/        # Business logic
│   └── api_v2.py        # Returns GENERIC format
│
└── frontend/            # UX concerns ONLY
    ├── adapters/        # NEW: Visualization adapters
    │   ├── graph_adapter.js         # Factory
    │   ├── visjs_adapter.js         # vis.js specific
    │   ├── d3_adapter.js            # D3 specific (future)
    │   └── cytoscape_adapter.js     # Cytoscape specific (future)
    │
    ├── knowledge_graph_client.js    # API client + adapter coordination
    └── knowledgeGraphPage.js        # UI logic
```

---

## 🚀 Implementation Impact

### What Changes in Original Proposal?

**REMOVE** (these were wrong):
1. ❌ GraphVisualizationService (backend shouldn't format for UX)
2. ❌ `to_dict()` methods returning vis.js format
3. ❌ Backend knowledge of 'from'/'to', 'group' (vis.js terms)

**ADD** (proper separation):
1. ✅ Frontend adapter layer (adapters/ directory)
2. ✅ Generic backend format ('source'/'target', 'type')
3. ✅ Frontend controls visualization library choice

**EFFORT IMPACT**:
- Original: 2-3 weeks
- Corrected: **2 weeks** (actually LESS - simpler backend!)
  - Removed complexity: No GraphVisualizationService
  - Added complexity: Frontend adapters (30 min each)
  - Net: Faster, cleaner

---

## 🎓 Design Pattern: Adapter Pattern

**Gang of Four Definition**:
> "Convert the interface of a class into another interface clients expect."

**Our Use Case**:
- **Adaptee**: Generic backend graph format
- **Target**: vis.js format
- **Adapter**: VisJsAdapter (converts generic → vis.js)
- **Client**: Frontend visualization code

**Benefits**:
- ✅ Backend and frontend independently evolvable
- ✅ Support multiple libraries simultaneously
- ✅ Clear separation of concerns
- ✅ Each layer has single responsibility

---

## 📚 References

**Design Patterns**:
- **Adapter Pattern**: Gang of Four (GoF) Design Patterns
- **Separation of Concerns**: Clean Architecture (Robert C. Martin)
- **Layered Architecture**: DDD (Eric Evans)

**Related Docs**:
- [[Knowledge Graph v2 Architecture Proposal]] - Main proposal
- [[Cosmic Python DDD Patterns]] - Backend patterns
- [[Frontend Modular Architecture Proposal]] - Frontend patterns

---

## 💬 Key Takeaway

**Backend's Job**:
- ✅ Build graph (nodes + edges + relationships)
- ✅ Cache graph (save/load)
- ✅ Query graph (neighbors, paths, centrality)
- ✅ Return GENERIC JSON (library-agnostic)

**Frontend's Job**:
- ✅ Fetch generic graph from backend
- ✅ Choose visualization library (vis.js, D3, Cytoscape)
- ✅ Adapt generic format to library format
- ✅ Render and handle user interactions

**Never**: Backend shouldn't know about vis.js, D3, Cytoscape, or any UX library!

---

**User's Insight**: ⭐ Excellent catch! This correction improves the proposal significantly.

**Philosophy**:
> "Backend = business logic. Frontend = presentation logic."  
> "Never couple backend to frontend libraries."