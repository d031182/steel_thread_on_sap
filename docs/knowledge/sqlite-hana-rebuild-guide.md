# SQLite Database Rebuild from HANA Cloud Structure

**Guide for rebuilding SQLite databases from HANA Cloud CSN files**

## Overview

This guide explains how to rebuild SQLite databases (p2p_data.db, p2p_graph.db) by extracting structure from HANA Cloud CSN (Core Schema Notation) files. This creates a fallback database with identical structure, enabling seamless switching when HANA Cloud is unavailable.

## Key Concepts

### Data Products
- **Data Product**: Logical grouping of related tables (e.g., "P2P" contains PurchaseOrder, Invoice, etc.)
- **CSN Namespace**: Data products identified by namespace prefix (e.g., "P2P.PurchaseOrder" → data product "P2P")
- **Database Separation**: Business data (p2p_data.db) vs. graph data (p2p_graph.db)

### Type Mapping (HANA → SQLite)
```python
'cds.String' → 'TEXT'
'cds.Integer' → 'INTEGER'
'cds.Decimal' → 'REAL'
'cds.Date' → 'TEXT'
'cds.Boolean' → 'INTEGER'
'cds.UUID' → 'TEXT'
```

## Usage

### Script: `rebuild_sqlite_from_hana_structure.py`

**Location**: `scripts/python/rebuild_sqlite_from_hana_structure.py`

### Basic Usage

```bash
# Rebuild from single CSN file
python scripts/python/rebuild_sqlite_from_hana_structure.py \
    --csn docs/csn/P2P_COMBINED.csn

# Rebuild from multiple CSN files
python scripts/python/rebuild_sqlite_from_hana_structure.py \
    --csn-dir docs/csn

# Dry run (preview without creating)
python scripts/python/rebuild_sqlite_from_hana_structure.py \
    --csn docs/csn/P2P_COMBINED.csn \
    --dry-run
```

### Advanced Usage

```bash
# Custom output paths
python scripts/python/rebuild_sqlite_from_hana_structure.py \
    --csn docs/csn/P2P_COMBINED.csn \
    --data-db database/custom_data.db \
    --graph-db database/custom_graph.db
```

## Workflow

### 1. Extract Structure from HANA

```bash
# Single CSN file
python scripts/python/rebuild_sqlite_from_hana_structure.py \
    --csn docs/csn/P2P_COMBINED.csn
```

**Output**:
```
🚀 Starting SQLite rebuild from HANA structure...
📖 Parsing CSN file: docs/csn/P2P_COMBINED.csn
🔍 Extracting data products...
✅ Found 1 data products:
   📦 P2P: 12 tables

📦 Creating p2p_data.db with 10 tables
   ✅ Creating table: PurchaseOrder
   ✅ Creating table: Invoice
   ...

🕸️  Creating p2p_graph.db with 2 tables
   ✅ Creating table: GraphEdge
   ✅ Creating table: GraphNode

============================================================
✅ SQLite Rebuild Complete!
============================================================
📊 Statistics:
   • Data Products: 1
   • Business Tables: 10
   • Graph Tables: 2
   • Total Tables: 12

📂 Databases created:
   • database/p2p_data.db
   • database/p2p_graph.db
============================================================
```

### 2. Verify Structure

```bash
# Compare HANA and SQLite schemas
python scripts/python/compare_hana_sqlite_schemas.py
```

### 3. Test Fallback

```bash
# Test database fallback mechanism
python -m pytest tests/data_products_v2/test_database_fallback.py -v
```

### 4. Populate Data (Optional)

```bash
# Populate with comprehensive P2P data
python scripts/python/populate_p2p_comprehensive.py
```

## Features

### ✅ Supported
- **CSN Parsing**: Extract entities, elements, keys from CSN files
- **Type Mapping**: Automatic HANA → SQLite type conversion
- **Primary Keys**: Preserved from CSN key definitions
- **Data Products**: Automatic grouping by namespace
- **Multiple CSN Files**: Merge structures from multiple sources
- **Dry Run**: Preview without creating databases
- **Metadata**: Rebuild metadata stored in `_rebuild_metadata` table

### ⚠️ Limitations
- **Foreign Keys**: Not automatically extracted (manual addition needed)
- **Indexes**: Not created (add manually for performance)
- **Associations**: CSN associations not converted to SQLite FKs
- **Data Population**: Only creates structure, not data

## Metadata Table

Each rebuilt database includes `_rebuild_metadata`:

```sql
CREATE TABLE _rebuild_metadata (
    rebuild_date TEXT NOT NULL,
    source_type TEXT NOT NULL,      -- 'HANA_CSN'
    data_product TEXT NOT NULL,     -- 'P2P_DATA' | 'GRAPH'
    table_count INTEGER NOT NULL,
    csn_source TEXT                  -- Source description
)
```

**Query metadata**:
```sql
SELECT * FROM _rebuild_metadata;
-- rebuild_date | source_type | data_product | table_count | csn_source
-- 2026-02-23... | HANA_CSN    | P2P_DATA     | 10          | CSN files from docs/csn
```

## Architecture

### SQLiteSchemaBuilder Class

**Responsibilities**:
1. Parse CSN files (JSON format)
2. Extract data products and tables
3. Map HANA types to SQLite types
4. Generate CREATE TABLE SQL
5. Create database structures
6. Insert rebuild metadata

**Key Methods**:
```python
builder = SQLiteSchemaBuilder(dry_run=False)
builder.rebuild_from_csn(csn_path, data_db_path, graph_db_path)
```

### Database Separation Logic

**Business Data** (p2p_data.db):
- Tables NOT containing: 'graph', 'edge', 'node' (case-insensitive)
- Examples: PurchaseOrder, Invoice, Supplier

**Graph Data** (p2p_graph.db):
- Tables containing: 'graph', 'edge', 'node'
- Examples: GraphEdge, GraphNode, SchemaGraph

## Integration with Fallback System

### 1. Database Connection Factory

```python
from core.services.database_connection_factory import DatabaseConnectionFactory

# Automatically uses SQLite if HANA unavailable
factory = DatabaseConnectionFactory()
connection = factory.get_connection('hana')  # Falls back to SQLite
```

### 2. Environment Configuration

```bash
# .env file
DB_TYPE=hana  # or 'sqlite' to force SQLite

# HANA credentials (optional, falls back to SQLite if missing)
HANA_ADDRESS=...
HANA_PORT=...
```

### 3. Testing

```python
# tests/data_products_v2/test_database_fallback.py
def test_hana_to_sqlite_fallback():
    """Test seamless fallback from HANA to SQLite"""
    # Simulates HANA unavailable, verifies SQLite works
```

## Troubleshooting

### Error: "CSN file not found"
```bash
# Verify CSN file exists
dir docs\csn

# Use correct path
python scripts/python/rebuild_sqlite_from_hana_structure.py \
    --csn docs/csn/P2P_COMBINED.csn
```

### Error: "No CSN files found in directory"
```bash
# Check directory contents
dir docs\csn\*.csn

# Ensure CSN files have .csn extension
```

### Error: "No schema found for table"
```bash
# Likely malformed CSN file
# Verify CSN structure:
python -c "import json; print(json.load(open('docs/csn/P2P_COMBINED.csn')))"
```

## Related Documentation

- [[Database Fallback Guide]] - Complete fallback system documentation
- [[Database Fallback Quick Reference]] - Quick start guide
- [[SQLite Rebuild Summary]] - Summary of rebuild capabilities
- [[Module Federation Standard]] - Architecture standard

## Next Steps

1. **Verify Structure**: Use `compare_hana_sqlite_schemas.py` to verify schema match
2. **Test Fallback**: Run `pytest tests/data_products_v2/test_database_fallback.py`
3. **Populate Data**: Use population scripts if needed
4. **Configure Fallback**: Set up environment variables for automatic fallback

---

**Last Updated**: 2026-02-23
**Version**: 1.0.0
**Status**: ✅ Production Ready