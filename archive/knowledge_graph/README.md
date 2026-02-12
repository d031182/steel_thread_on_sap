# Knowledge Graph Module

**Version:** 1.0.0  
**Category:** Data Management  
**Status:** Production Ready

## Overview

The Knowledge Graph module visualizes data relationships as an interactive graph, showing how records are connected via foreign keys. It analyzes actual data in tables to build a real-world relationship graph rather than just showing schema definitions.

## Features

- **Actual Data Relationships**: Analyzes real data records to show connections via foreign keys
- **Interactive Visualization**: Force-directed, circular, and hierarchical graph layouts
- **Multi-Source Support**: Works with both SQLite and HANA Cloud data sources
- **Performance Optimized**: Configurable record limits to prevent overload
- **Real-Time Analysis**: Dynamically builds graph from current database state

## API Endpoints

### GET `/api/knowledge-graph`

Build and retrieve knowledge graph of data relationships.

**Query Parameters:**
- `source` (string, optional): Data source - 'sqlite' (default) or 'hana'
- `max_records` (integer, optional): Maximum records per table to analyze (default: 20, max: 100)

**Response:**
```json
{
  "success": true,
  "nodes": [
    {
      "id": "table_name_record_id",
      "label": "Record display name",
      "group": "table",
      "table": "table_name"
    }
  ],
  "edges": [
    {
      "from": "source_node_id",
      "to": "target_node_id",
      "label": "relationship_name"
    }
  ],
  "stats": {
    "node_count": 150,
    "edge_count": 200,
    "table_count": 10
  }
}
```

### GET `/api/knowledge-graph/stats`

Get statistics about available data for graphing.

**Query Parameters:**
- `source` (string, optional): Data source - 'sqlite' or 'hana'

**Response:**
```json
{
  "success": true,
  "stats": {
    "source": "sqlite",
    "product_count": 5,
    "table_count": 62
  }
}
```

## Architecture

### Backend Components

1. **api.py** - Flask blueprint providing REST endpoints
2. **data_graph_service.py** - Core graph building logic
   - Discovers tables via system catalogs
   - Analyzes foreign key relationships
   - Samples data records
   - Builds nodes and edges

### Frontend Integration

The Knowledge Graph page (`app/static/js/ui/pages/knowledgeGraphPage.js`) uses:
- **vis.js** - Graph visualization library
- **SAP UI5** - UI controls and layout
- **Force-directed layout** - Default visualization mode

### Graph Building Algorithm

1. **Table Discovery**
   - Query `sqlite_master` (SQLite) or `SYS.TABLES` (HANA)
   - Filter system tables
   
2. **Foreign Key Detection**
   - Query `PRAGMA foreign_key_list` (SQLite)
   - Query `SYS.REFERENTIAL_CONSTRAINTS` (HANA)
   
3. **Data Sampling**
   - Sample up to `max_records` from each table
   - Create nodes for each record
   
4. **Edge Creation**
   - Match foreign key values to create edges
   - Label edges with relationship name

## Configuration

In `module.json`:

```json
{
  "enabled": true,
  "requiresHana": false,
  "dependencies": {
    "modules": ["sqlite_connection", "hana_connection"]
  }
}
```

## Usage Examples

### Basic Usage

```javascript
// Fetch graph with default settings (SQLite, 20 records)
const response = await fetch('/api/knowledge-graph');
const data = await response.json();

// Render graph
renderGraph(data.nodes, data.edges);
```

### Custom Configuration

```javascript
// Fetch from HANA with 50 records per table
const response = await fetch('/api/knowledge-graph?source=hana&max_records=50');
const data = await response.json();
```

### Statistics Only

```javascript
// Check available data before building graph
const response = await fetch('/api/knowledge-graph/stats?source=sqlite');
const stats = await response.json();
console.log(`${stats.stats.table_count} tables available`);
```

## Performance Considerations

- **Record Limit**: Default 20 records per table prevents memory issues
- **Table Filtering**: Automatically excludes system tables
- **Lazy Loading**: Graph built on-demand, not pre-computed
- **Frontend Caching**: vis.js library loaded once and reused

## Dependencies

### Python
- `sqlite3` (built-in)
- `hdbcli` (for HANA, optional)

### JavaScript
- vis.js 9.1.2 (CDN)
- SAP UI5 (provided by application)

### Modules
- `sqlite_connection` - SQLite data access
- `hana_connection` - HANA Cloud data access (optional)

## Future Enhancements

- [ ] Graph filtering by table/relationship type
- [ ] Export graph as image (PNG/SVG)
- [ ] Save/load graph layouts
- [ ] Record detail panel on node click
- [ ] Relationship strength visualization
- [ ] Schema-only mode (no data sampling)

## Troubleshooting

### Empty Graph

**Symptom**: `node_count: 0, edge_count: 0`

**Solutions:**
- Check database has data: Query tables directly
- Verify foreign keys defined: Check schema definitions
- Increase `max_records`: More data = more relationships
- Check logs: Look for SQL errors

### Slow Performance

**Symptom**: Graph takes > 10 seconds to load

**Solutions:**
- Reduce `max_records` parameter (try 10 or 5)
- Check table sizes: Large tables slow sampling
- Verify indexes: Foreign key columns should be indexed
- Consider HANA: Better for large datasets

### Missing Relationships

**Symptom**: Nodes exist but few edges

**Solutions:**
- Verify foreign key constraints: Must be defined in schema
- Check data integrity: Foreign key values must match
- Increase `max_records`: More samples = more matches

## Version History

### 1.0.0 (2026-01-29)
- Initial modular release
- Moved from inline code to module architecture
- Added stats endpoint
- Improved error handling
- Added comprehensive documentation

## Related Documentation

- [[Modular Architecture]] - Module system overview
- [[Data Products Module]] - Related data visualization
- [[Testing Standards]] - Module testing guide

## Author

P2P Development Team  
Contact: Via GitHub issues

## License

Internal SAP project - All rights reserved