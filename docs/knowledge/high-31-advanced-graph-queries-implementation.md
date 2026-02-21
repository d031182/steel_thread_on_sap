# HIGH-31: Advanced Graph Queries Implementation

**Task**: Knowledge Graph V2 - Phase 3: Advanced Queries  
**Priority**: HIGH  
**Status**: In Progress  
**Date**: 2026-02-21

## Overview

Implement advanced graph query capabilities for Knowledge Graph V2 module, exposing powerful analytics through REST API endpoints.

## Current State Analysis

### ✅ What We Have (Excellent Foundation)

1. **NetworkXGraphQueryEngine** (`core/services/networkx_graph_query_engine.py`):
   - ✅ PageRank calculation
   - ✅ Betweenness centrality
   - ✅ Degree centrality
   - ✅ Connected components
   - ✅ Cycle detection
   - ✅ Export to JSON

2. **HANAGraphQueryEngine** (`core/services/hana_graph_query_engine.py`):
   - ✅ Native HANA `GRAPH_PAGERANK()`
   - ✅ Native HANA `GRAPH_BETWEENNESS_CENTRALITY()`
   - ✅ Native HANA `GRAPH_LOUVAIN_COMMUNITY_DETECTION()`
   - ✅ Native HANA `GRAPH_LABEL_PROPAGATION_COMMUNITY_DETECTION()`

3. **GraphQueryService** (`core/services/graph_query_service.py`):
   - ✅ Delegation facade that routes to correct engine (HANA/NetworkX)

4. **Knowledge Graph V2 API** (`modules/knowledge_graph_v2/backend/api.py`):
   - ✅ Schema graph endpoints
   - ✅ Constructor injection pattern
   - ❌ Missing advanced query endpoints

### 🔨 What We Need to Build

**NEW API Endpoints** (Phase 3 focus):
1. `POST /api/knowledge-graph/query/pagerank` - Calculate PageRank scores
2. `POST /api/knowledge-graph/query/centrality` - Calculate centrality metrics
3. `POST /api/knowledge-graph/query/communities` - Detect communities
4. `POST /api/knowledge-graph/query/cycles` - Find cycles
5. `POST /api/knowledge-graph/query/connected-components` - Find connected components
6. `GET /api/knowledge-graph/query/statistics` - Get graph statistics

**Enhancement** (HIGH-29/HIGH-30 Integration):
- Add semantic metadata support to query results (CSN annotations, labels, descriptions)

## Implementation Plan

### Phase 1: Facade Enhancement (KnowledgeGraphFacadeV2)

**File**: `modules/knowledge_graph_v2/facade/knowledge_graph_facade.py`

Add methods that delegate to GraphQueryService:
```python
def get_pagerank(self, top_k: int = 10) -> Dict:
    """Calculate PageRank scores"""
    
def get_centrality(self, metric: str = 'betweenness', top_k: int = 10) -> Dict:
    """Calculate centrality metrics (betweenness, degree, closeness)"""
    
def detect_communities(self, algorithm: str = 'louvain') -> Dict:
    """Detect communities using specified algorithm"""
    
def find_cycles(self) -> Dict:
    """Find all cycles in graph"""
    
def get_connected_components(self) -> Dict:
    """Find connected components"""
    
def get_graph_statistics(self) -> Dict:
    """Get comprehensive graph statistics"""
```

### Phase 2: API Endpoints (KnowledgeGraphV2API)

**File**: `modules/knowledge_graph_v2/backend/api.py`

Add new endpoints following existing patterns:
```python
def query_pagerank(self):
    """POST /api/knowledge-graph/query/pagerank"""
    
def query_centrality(self):
    """POST /api/knowledge-graph/query/centrality"""
    
def query_communities(self):
    """POST /api/knowledge-graph/query/communities"""
    
def query_cycles(self):
    """POST /api/knowledge-graph/query/cycles"""
    
def query_connected_components(self):
    """POST /api/knowledge-graph/query/connected-components"""
    
def query_statistics(self):
    """GET /api/knowledge-graph/query/statistics"""
```

### Phase 3: Semantic Enhancement (Optional - HIGH-29/HIGH-30 Integration)

**Enhancement**: Enrich query results with semantic metadata from CSN

**Example**:
```python
# Before (raw node IDs)
{
  "PurchaseOrder:PO000001": 0.85,
  "Supplier:SUP001": 0.72
}

# After (with semantic metadata)
{
  "PurchaseOrder:PO000001": {
    "score": 0.85,
    "label": "Purchase Order",
    "description": "Procurement document for goods/services",
    "entity_type": "PurchaseOrder"
  },
  "Supplier:SUP001": {
    "score": 0.72,
    "label": "Supplier",
    "description": "Business partner providing goods/services",
    "entity_type": "Supplier"
  }
}
```

**Implementation**: Query CSN metadata service for entity labels/descriptions

### Phase 4: API Contract Tests

**File**: `tests/knowledge_graph_v2/test_knowledge_graph_v2_advanced_queries_api.py`

Test each endpoint:
```python
@pytest.mark.api_contract
def test_pagerank_endpoint():
    """Test: POST /api/knowledge-graph/query/pagerank returns scores"""

@pytest.mark.api_contract
def test_centrality_endpoint():
    """Test: POST /api/knowledge-graph/query/centrality returns metrics"""

@pytest.mark.api_contract
def test_communities_endpoint():
    """Test: POST /api/knowledge-graph/query/communities returns clusters"""
    
# etc.
```

## API Contracts (Design)

### 1. PageRank Query

**Endpoint**: `POST /api/knowledge-graph/query/pagerank`

**Request**:
```json
{
  "top_k": 10,
  "damping_factor": 0.85
}
```

**Response**:
```json
{
  "success": true,
  "data": {
    "scores": {
      "PurchaseOrder:PO000001": 0.85,
      "Supplier:SUP001": 0.72,
      "Invoice:INV001": 0.68
    },
    "top_k": 10,
    "total_nodes": 1523
  }
}
```

### 2. Centrality Query

**Endpoint**: `POST /api/knowledge-graph/query/centrality`

**Request**:
```json
{
  "metric": "betweenness",
  "top_k": 10
}
```

**Response**:
```json
{
  "success": true,
  "data": {
    "metric": "betweenness",
    "scores": {
      "PurchaseOrder:PO000001": 0.42,
      "Supplier:SUP001": 0.38
    },
    "top_k": 10
  }
}
```

### 3. Community Detection

**Endpoint**: `POST /api/knowledge-graph/query/communities`

**Request**:
```json
{
  "algorithm": "louvain"
}
```

**Response**:
```json
{
  "success": true,
  "data": {
    "algorithm": "louvain",
    "communities": {
      "1": ["PurchaseOrder:PO000001", "Supplier:SUP001"],
      "2": ["Invoice:INV001", "GoodsReceipt:GR001"]
    },
    "community_count": 2
  }
}
```

### 4. Cycle Detection

**Endpoint**: `POST /api/knowledge-graph/query/cycles`

**Response**:
```json
{
  "success": true,
  "data": {
    "cycles": [
      ["PurchaseOrder:PO000001", "GoodsReceipt:GR001", "PurchaseOrder:PO000001"]
    ],
    "cycle_count": 1
  }
}
```

### 5. Connected Components

**Endpoint**: `POST /api/knowledge-graph/query/connected-components`

**Response**:
```json
{
  "success": true,
  "data": {
    "components": [
      ["PurchaseOrder:PO000001", "Supplier:SUP001", "Invoice:INV001"],
      ["Employee:EMP001", "Department:DEPT001"]
    ],
    "component_count": 2
  }
}
```

### 6. Graph Statistics

**Endpoint**: `GET /api/knowledge-graph/query/statistics`

**Response**:
```json
{
  "success": true,
  "data": {
    "nodes": 1523,
    "edges": 3842,
    "density": 0.0032,
    "avg_degree": 5.04,
    "is_directed": true,
    "engine": "NetworkX",
    "load_time_ms": 145
  }
}
```

## Testing Strategy

### API Contract Tests (PRIMARY FOCUS)

**Gu Wu Methodology**: Test API contracts, trust implementation

```python
# tests/knowledge_graph_v2/test_knowledge_graph_v2_advanced_queries_api.py

@pytest.mark.e2e
@pytest.mark.api_contract
def test_pagerank_api_contract():
    """Test: PageRank API returns valid contract"""
    response = requests.post(
        "http://localhost:5000/api/knowledge-graph/query/pagerank",
        json={"top_k": 5},
        timeout=5
    )
    assert response.status_code == 200
    data = response.json()
    assert data['success'] == True
    assert 'scores' in data['data']
    assert len(data['data']['scores']) <= 5
```

**Rationale**: Each API test validates entire chain:
- API endpoint → Facade → GraphQueryService → Engine (HANA/NetworkX)
- 60-300x faster than browser testing (< 1 second)
- Implementation functions tested implicitly

### No Internal Function Tests

❌ Don't test:
- `facade.get_pagerank()` explicitly (tested via API)
- `engine.get_pagerank()` explicitly (tested via API)
- Internal utility functions (tested via API)

✅ Trust implementation, test contract

## Success Criteria

### ✅ Definition of Done

1. **API Endpoints**: All 6 endpoints implemented and functional
2. **API Tests**: Contract tests passing for all endpoints
3. **Documentation**: API documentation updated
4. **Performance**: Queries execute in < 5 seconds for typical graphs
5. **Error Handling**: Graceful failures with proper HTTP status codes

### ✅ Testing Validation

```bash
# Run API contract tests
pytest tests/knowledge_graph_v2/test_knowledge_graph_v2_advanced_queries_api.py -v -m api_contract

# Expected: All tests green, < 1 second each
```

## Next Steps After HIGH-31

1. **Frontend Integration**: Add UI components to visualize advanced queries
2. **Caching**: Add caching for expensive queries (PageRank, centrality)
3. **Streaming**: Support streaming for large result sets
4. **Filters**: Add filtering options (entity types, date ranges)

## References

- [[Knowledge Graph V2 Architecture Proposal]]
- [[Gu Wu API Contract Testing Foundation]]
- [[Module Federation Standard]]
- Phase 3 specification: `docs/knowledge/knowledge-graph-semantic-enhancement-implementation-plan.md`
- HIGH-29: CSN Association Parser
- HIGH-30: Semantic Annotations Enhancement

## Key Insights

1. **Solid Foundation**: Both engines already have advanced algorithms implemented
2. **Clean Architecture**: Delegation pattern (Facade → Service → Engine) ready for extension
3. **Gu Wu Approach**: Focus on API contracts, not internal functions
4. **Performance**: HANA engine uses native graph functions (10-100x faster)
5. **Semantic Integration**: Can enhance with HIGH-29/HIGH-30 metadata (optional)