# Knowledge Graph V2 Module

**Version**: 2.0.0  
**Status**: Active  
**Author**: P2P Development Team

## Overview

Knowledge Graph V2 provides enterprise-grade graph visualization and querying capabilities for SAP data products with runtime source switching (HANA/SQLite).

## Features

- **Multi-Backend Support**: HANA Cloud / SQLite (config-driven)
- **Graph Caching**: Optimized with SQLite cache layer
- **Cytoscape Integration**: Interactive graph visualization
- **Force-Directed Layout**: Automatic node positioning
- **Schema + Data Graphs**: Visualize both structure and content
- **RESTful API**: Clean JSON endpoints

## Architecture

```
knowledge_graph_v2/
├── backend/
│   ├── api.py                          # Flask Blueprint
│   ├── graph.py                        # Graph service (uses repository)
│   ├── schema_graph_builder_service.py # Schema graph logic
│   └── repositories/                   # Data access layer
│       └── sqlite_graph_cache_repository.py
├── frontend/
│   ├── views/knowledgeGraphPageV2.js   # SAPUI5 page
│   ├── adapters/KnowledgeGraphApiClient.js
│   └── module.js
└── module.json                          # Feature flag + metadata
```

## API Endpoints

### GET `/api/knowledge-graph-v2/graph`
Get graph data (nodes + edges)

**Query Parameters**:
- `source`: 'hana' or 'sqlite' (default: sqlite)
- `mode`: 'schema' or 'data' (default: schema)
- `product_name`: For data mode
- `use_cache`: true/false (default: true)

**Response**:
```json
{
  "nodes": [...],
  "edges": [...],
  "metadata": {...}
}
```

### GET `/api/knowledge-graph-v2/health`
Health check

## Usage

### Frontend (SAPUI5)
```javascript
const client = new KnowledgeGraphApiClient();
const graph = await client.getGraph('hana', 'schema');
```

### Backend (Python)
```python
from modules.knowledge_graph_v2.backend.graph import GraphService

service = GraphService()
graph_data = service.get_graph(source='hana', mode='schema')
```

## Dependencies

- **Backend**: Flask, NetworkX, SQLite3
- **Frontend**: SAPUI5, Cytoscape.js
- **Core**: IGraphQueryEngine, IGraphCacheRepository

## Testing

```bash
# Unit tests
pytest tests/unit/modules/knowledge_graph_v2/

# Integration tests
pytest tests/integration/test_knowledge_graph_v2.py

# E2E tests
pytest tests/e2e/app_v2/test_knowledge_graph_v2.py
```

## Configuration

**module.json**:
```json
{
  "name": "knowledge_graph_v2",
  "enabled": true,
  "version": "2.0.0",
  "backend": {
    "blueprint": "modules.knowledge_graph_v2.backend.api:knowledge_graph_v2_bp"
  }
}
```

## Performance

- **Caching**: SQLite cache for schema graphs (90% hit rate)
- **Layout**: Force-directed calculation (1-2s for 50 nodes)
- **Query Optimization**: Bulk fetches for related entities

## Migration from V1

- V1 archived to `archive/knowledge_graph/`
- V2 uses repository pattern (vs direct DB access)
- V2 has runtime source switching
- V2 follows modular architecture standards

## Related Documentation

- [[Knowledge Graph V2 Architecture Proposal]]
- [[Knowledge Graph V2 API Design]]
- [[Knowledge Graph V2 Services Design]]
- [[Knowledge Graph V2 Phase 5 Frontend Architecture]]

## Known Issues

None currently.

## Future Enhancements

1. Real-time graph updates (WebSocket)
2. Graph query language (Cypher-like)
3. Historical graph snapshots
4. Advanced filters and search