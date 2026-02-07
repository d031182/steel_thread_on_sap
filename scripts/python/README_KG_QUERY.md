h Knowledge Graph Query Script

## Problem
The knowledge graph JSON file can become too large, causing SSE stream errors when Cline tries to read it directly. This is similar to the issue we had with CSN files.

## Solution
Use `query_knowledge_graph.py` script to query the knowledge graph efficiently using streaming JSON parsing (ijson library).

## Usage

### Find Knowledge Graph Location
The MCP memory server stores the knowledge graph. Common locations:
- Windows: `%APPDATA%\.mcp\memory\knowledge_graph.json`
- Mac/Linux: `~/.mcp/memory/knowledge_graph.json`

Or check MCP server config in VS Code settings.

### Query Examples

```bash
# Get statistics about the knowledge graph
python scripts/python/query_knowledge_graph.py --kg-file "path/to/knowledge_graph.json" --stats

# Search for entities containing "Feng Shui"
python scripts/python/query_knowledge_graph.py --kg-file "path/to/knowledge_graph.json" --search "Feng Shui" --limit 5

# Get details for a specific entity
python scripts/python/query_knowledge_graph.py --kg-file "path/to/knowledge_graph.json" --entity "Feng Shui Architecture Tool"

# List all entity types
python scripts/python/query_knowledge_graph.py --kg-file "path/to/knowledge_graph.json" --types

# Get relations for an entity
python scripts/python/query_knowledge_graph.py --kg-file "path/to/knowledge_graph.json" --relations "Project Architecture" --limit 20
```

## Python API Usage

```python
from scripts.python.query_knowledge_graph import KnowledgeGraphQuery

# Initialize
kg = KnowledgeGraphQuery("path/to/knowledge_graph.json")

# Search entities
results = kg.search_entities("AI Assistant", limit=10)

# Get entity details
entity = kg.get_entity_details("AI Assistant Module")

# Get statistics
stats = kg.get_stats()
print(f"Total entities: {stats['total_entities']}")
print(f"Total relations: {stats['total_relations']}")

# List entity types
types = kg.list_entity_types()

# Get relations
relations = kg.get_relations("User Preferences", limit=20)
```

## Benefits

1. **Memory Efficient**: Streams JSON instead of loading entire file
2. **Fast**: Only parses relevant sections
3. **No SSE Errors**: Prevents stream failures from large files
4. **Flexible**: CLI and Python API available

## Dependencies

```bash
pip install ijson
```

Already installed in this project.