# Ontology Cache Management

**Version**: 1.0.0  
**Created**: 2026-01-31  
**Related**: [[Graph Ontology Persistence]], [[CSN-Driven Knowledge Graph]]

## Overview

The Knowledge Graph uses a **persistent ontology cache** to achieve 103x faster load times (4ms vs 410ms). This cache stores pre-discovered relationships between data products and tables.

## Performance Impact

- **Without Cache**: 410ms to discover relationships from CSN files
- **With Cache**: 4ms to load from database
- **Speedup**: 103x faster (102.5x exact)

## When to Refresh Cache

The cache needs to be refreshed when:

1. **Database schema changes**
   - New tables added
   - Tables renamed/dropped
   - Foreign keys modified

2. **CSN files updated**
   - New data products added
   - Entity definitions changed
   - Relationship metadata updated

3. **Manual refresh needed**
   - Cache appears stale
   - Testing relationship discovery
   - Troubleshooting graph issues

## API Endpoints

### Get Cache Status

```http
GET /api/knowledge-graph/cache/status?source=sqlite
```

**Response**:
```json
{
  "success": true,
  "source": "sqlite",
  "cache": {
    "cache_valid": true,
    "total_relationships": 31,
    "high_confidence": 28,
    "manually_verified": 0,
    "last_discovery": "2026-01-31 19:57:24"
  }
}
```

### Refresh Cache

```http
POST /api/knowledge-graph/cache/refresh
Content-Type: application/json

{
  "source": "sqlite"
}
```

**Response**:
```json
{
  "success": true,
  "statistics": {
    "cleared": 31,
    "discovered": 31,
    "inserted": 31,
    "updated": 0,
    "discovery_time_ms": 88.19
  },
  "message": "Cache refreshed successfully. Discovered 31 relationships in 88ms"
}
```

## Usage Examples

### Using curl

```bash
# Check cache status
curl http://localhost:5000/api/knowledge-graph/cache/status

# Refresh cache
curl -X POST http://localhost:5000/api/knowledge-graph/cache/refresh \
  -H "Content-Type: application/json" \
  -d '{"source": "sqlite"}'
```

### Using Python

```python
import requests

# Check status
response = requests.get('http://localhost:5000/api/knowledge-graph/cache/status')
print(response.json())

# Refresh cache
response = requests.post(
    'http://localhost:5000/api/knowledge-graph/cache/refresh',
    json={'source': 'sqlite'}
)
print(response.json())
```

## Cache Invalidation Strategy

The cache uses **explicit invalidation** (manual refresh) rather than automatic time-based expiration because:

1. **Schema changes are explicit events** - you know when you add tables
2. **Prevents unexpected slowdowns** - automatic expiration could cause 410ms delays randomly
3. **Developer control** - you decide when to pay the 88ms refresh cost
4. **Production stability** - predictable performance (always 4ms after cache valid)

## Workflow Integration

### After Schema Changes

```bash
# 1. Add new CSN file to docs/csn/
# 2. Rebuild database with new schema
python scripts/python/rebuild_sqlite_from_csn.py

# 3. Refresh ontology cache
curl -X POST http://localhost:5000/api/knowledge-graph/cache/refresh \
  -H "Content-Type: application/json" -d '{}'

# 4. Verify graph loads fast
curl "http://localhost:5000/api/knowledge-graph/?source=sqlite&mode=schema"
```

### Monitoring Cache Health

```bash
# Quick status check
curl http://localhost:5000/api/knowledge-graph/cache/status | python -m json.tool
```

Look for:
- `cache_valid: true` - Cache exists and has relationships
- `total_relationships` - Should match expected count (31 for current schema)
- `high_confidence` - Most relationships should be high confidence (28/31)
- `last_discovery` - When cache was last refreshed

## Cache Storage

**Location**: Same database as data products
- SQLite: `app/database/p2p_data_products.db`
- Tables: `graph_schema_edges`, `graph_ontology_metadata`

**Size**: Minimal (~5KB for 31 relationships)

**Persistence**: Survives server restarts, only cleared by explicit refresh

## Technical Details

### Cache Structure

```sql
-- Stores discovered relationships
CREATE TABLE graph_schema_edges (
    edge_id INTEGER PRIMARY KEY,
    source_table TEXT NOT NULL,
    source_column TEXT NOT NULL,
    target_table TEXT NOT NULL,
    target_column TEXT,
    relationship_type TEXT,
    confidence REAL,
    discovery_method TEXT,
    is_active INTEGER DEFAULT 1,
    notes TEXT,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT DEFAULT CURRENT_TIMESTAMP
);

-- Stores cache metadata
CREATE TABLE graph_ontology_metadata (
    key TEXT PRIMARY KEY,
    value TEXT,
    updated_at TEXT DEFAULT CURRENT_TIMESTAMP
);
```

### Discovery Methods

- `csn_metadata` - Discovered automatically from CSN files (most common)
- `manual_override` - Manually added relationships
- `manual_verified` - Automatically discovered but manually verified

### Confidence Scores

- `1.0` - Perfect match (exact name, type match)
- `0.9` - High confidence (name match, type compatible)
- `0.7` - Good match (name match)
- `0.5` - Weak match (partial name match)

Only relationships with confidence ≥ 0.5 are cached.

## Future Enhancements

Potential improvements (not yet implemented):

1. **Automatic invalidation** - Detect CSN file changes
2. **Incremental updates** - Only refresh changed entities
3. **Manual relationship editor** - UI for adding/verifying relationships
4. **Cache warming** - Refresh cache on server startup
5. **Multi-source caching** - Separate caches for SQLite vs HANA

## References

- [[Graph Ontology Persistence]] - Architecture design
- [[CSN-Driven Knowledge Graph]] - Overall graph strategy
- `core/services/ontology_persistence_service.py` - Implementation
- `modules/knowledge_graph/backend/api.py` - API endpoints