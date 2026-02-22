# Knowledge Graph API Filtering Guide

**Purpose**: Overcome large response limitations by using filtering, pagination, and summary endpoints

## Problem

The full schema endpoint `/api/knowledge-graph/schema` can return very large responses (10K+ nodes) that exceed Cline's context window and slow down clients.

## Solution: Use Existing Filtering Capabilities

You already have comprehensive filtering implemented! Here's how to use it:

---

## 1. Summary Endpoint (Fastest - Recommended First Step)

Get high-level statistics without loading the full graph:

```bash
GET /api/knowledge-graph/schema?summary=true
```

**Returns**:
```json
{
  "success": true,
  "data": {
    "summary": {
      "total_nodes": 1543,
      "total_edges": 2876,
      "entity_types": {
        "PurchaseOrder": 234,
        "Invoice": 456,
        "Material": 853
      },
      "relationship_types": {
        "CONTAINS": 1234,
        "REFERENCES": 876,
        "DERIVED_FROM": 766
      }
    }
  }
}
```

**Performance**: < 2 seconds (tested in `test_schema_summary_performance`)

---

## 2. Pagination (Load in Chunks)

Request data in manageable chunks:

```bash
# First page (10 nodes)
GET /api/knowledge-graph/schema?limit=10&offset=0

# Second page (next 10 nodes)
GET /api/knowledge-graph/schema?limit=10&offset=10

# Third page
GET /api/knowledge-graph/schema?limit=10&offset=20
```

**Returns**:
```json
{
  "success": true,
  "data": {
    "pagination": {
      "total_nodes": 1543,
      "returned_nodes": 10,
      "offset": 0,
      "limit": 10
    },
    "graph": {
      "nodes": [...10 nodes...],
      "edges": [...]
    }
  }
}
```

**Use Case**: Progressive loading in UI, processing large datasets in batches

---

## 3. Entity Type Filtering

Request only specific entity types:

```bash
# Single entity type
GET /api/knowledge-graph/schema?entity_types=PurchaseOrder

# Multiple entity types (comma-separated)
GET /api/knowledge-graph/schema?entity_types=PurchaseOrder,Invoice
```

**Returns**: Only nodes matching specified entity types

**Use Case**: Focus on specific business objects (e.g., only purchase orders)

---

## 4. Exclude Edges (Nodes Only)

Get node metadata without relationships:

```bash
GET /api/knowledge-graph/schema?include_edges=false
```

**Returns**: Nodes only, empty edges array

**Use Case**: When you only need entity metadata, not relationships (faster response)

---

## 5. Combined Filters (Most Powerful)

Combine multiple filters for precise control:

```bash
# Example: First 5 purchase orders, no edges
GET /api/knowledge-graph/schema?entity_types=PurchaseOrder&limit=5&include_edges=false

# Example: Page 2 of invoices (nodes 10-19)
GET /api/knowledge-graph/schema?entity_types=Invoice&limit=10&offset=10
```

**Use Case**: Targeted data retrieval with minimal response size

---

## Recommended Workflow for Cline/AI Tools

### Step 1: Get Summary
```bash
curl "http://localhost:5000/api/knowledge-graph/schema?summary=true"
```
- Understand total scope (node count, entity types)
- Decide on filtering strategy

### Step 2: Request Specific Data
```bash
# Option A: Filter by entity type
curl "http://localhost:5000/api/knowledge-graph/schema?entity_types=PurchaseOrder&limit=50"

# Option B: Paginate through all
curl "http://localhost:5000/api/knowledge-graph/schema?limit=50&offset=0"
```

### Step 3: Process in Batches
- Process first batch
- Request next batch with incremented offset
- Repeat until all data processed

---

## Error Handling

### Invalid Limit (< 1)
```bash
GET /api/knowledge-graph/schema?limit=0
# Returns: 400 Bad Request
# Error: "limit must be >= 1"
```

### Invalid Offset (< 0)
```bash
GET /api/knowledge-graph/schema?offset=-1
# Returns: 400 Bad Request
# Error: "offset must be >= 0"
```

---

## Performance Comparison

| Approach | Response Time | Response Size | Use Case |
|----------|--------------|---------------|----------|
| Full graph | 10-60s | 10+ MB | Full analysis (avoid!) |
| Summary | < 2s | < 1 KB | Quick overview |
| Paginated (limit=50) | < 5s | ~500 KB | Progressive loading |
| Filtered by entity type | < 5s | Variable | Focused analysis |
| Combined filters | < 3s | ~100-500 KB | Optimal balance |

---

## Python Example (Programmatic Access)

```python
import requests

# Step 1: Get summary
response = requests.get(
    "http://localhost:5000/api/knowledge-graph/schema?summary=true",
    timeout=10
)
summary = response.json()['data']['summary']
print(f"Total nodes: {summary['total_nodes']}")
print(f"Entity types: {list(summary['entity_types'].keys())}")

# Step 2: Paginate through specific entity type
entity_type = "PurchaseOrder"
limit = 50
offset = 0

all_nodes = []
while True:
    url = (
        f"http://localhost:5000/api/knowledge-graph/schema"
        f"?entity_types={entity_type}&limit={limit}&offset={offset}"
    )
    response = requests.get(url, timeout=10)
    data = response.json()['data']
    
    nodes = data['graph']['nodes']
    all_nodes.extend(nodes)
    
    if len(nodes) < limit:
        break  # Last page
    
    offset += limit

print(f"Retrieved {len(all_nodes)} {entity_type} nodes")
```

---

## JavaScript Example (Frontend)

```javascript
// Lazy loading with pagination
async function loadSchemaInChunks(entityType, limit = 50) {
    const allNodes = [];
    let offset = 0;
    
    while (true) {
        const url = `/api/knowledge-graph/schema?entity_types=${entityType}&limit=${limit}&offset=${offset}`;
        const response = await fetch(url);
        const data = await response.json();
        
        const nodes = data.data.graph.nodes;
        allNodes.push(...nodes);
        
        // Update UI with current batch
        renderNodes(nodes);
        
        if (nodes.length < limit) {
            break; // Last page
        }
        
        offset += limit;
    }
    
    return allNodes;
}
```

---

## Testing

All filtering capabilities are tested in:
- `tests/knowledge_graph_v2/test_schema_filtering_api.py`

Run tests:
```bash
pytest tests/knowledge_graph_v2/test_schema_filtering_api.py -v
```

---

## Key Takeaways

✅ **DO**:
- Start with `?summary=true` to understand scope
- Use pagination (`?limit=50&offset=0`) for large datasets
- Filter by entity type when focusing on specific business objects
- Combine filters for optimal response size

❌ **DON'T**:
- Request full graph without filters (causes timeouts/memory issues)
- Use limit=0 or offset=-1 (validation errors)
- Assume all data fits in one request

---

**Last Updated**: 2026-02-22  
**Implementation**: HIGH-50 (Schema Filtering & Pagination)  
**Tests**: `test_schema_filtering_api.py` (11 test cases, all passing)