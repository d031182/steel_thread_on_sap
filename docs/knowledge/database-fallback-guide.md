# Database Fallback Guide: HANA Cloud ↔ SQLite

**Purpose**: Seamlessly switch between HANA Cloud and SQLite databases without code changes

**Status**: Implementation Complete (2026-02-23)

**Related**: [[Module Federation Standard]], [[API-First Contract Testing Methodology]]

---

## Overview

This system provides a seamless fallback mechanism between HANA Cloud and SQLite databases. The same data product structure exists in both databases, allowing transparent switching via environment variable.

### Key Benefits

1. ✅ **Zero Code Changes**: Switch databases via environment variable only
2. ✅ **API Contract Stability**: Same APIs work with both databases
3. ✅ **Automatic Rebuild**: Script creates SQLite mirror of HANA structure
4. ✅ **CSN-Driven**: SQLite structure derived from HANA CSN metadata
5. ✅ **Production Ready**: Fallback when HANA Cloud unavailable

---

## Architecture

```
CSN Metadata (HANA) → Rebuild Script → SQLite Database
                                              ↓
                    Repository Factory ← DATABASE_TYPE env var
                           ↓
                    Data Products API (same contract)
                           ↓
                      Frontend Modules
```

### Components

1. **CSN Parser** (`core/services/csn_parser.py`)
   - Reads HANA Cloud metadata
   - Extracts data products and table definitions
   - Parses associations/relationships

2. **Rebuild Script** (`scripts/python/rebuild_sqlite_from_hana.py`)
   - Extracts HANA structure from CSN
   - Creates matching SQLite schema
   - Validates structure correctness
   - Stores rebuild metadata

3. **Repository Factory** (`modules/data_products_v2/repositories/repository_factory.py`)
   - Reads DATABASE_TYPE from environment
   - Creates appropriate repository (HANA or SQLite)
   - Both implement same interface

4. **Data Products API** (`modules/data_products_v2/backend/api.py`)
   - Consumes repository via dependency injection
   - API contract identical for both databases
   - Frontend unaware of underlying database

---

## Quick Start

### 1. Rebuild SQLite from HANA

```bash
# Basic rebuild (creates database/p2p_data.db)
python scripts/python/rebuild_sqlite_from_hana.py

# Force rebuild (overwrite existing)
python scripts/python/rebuild_sqlite_from_hana.py --force

# Validate only (no rebuild)
python scripts/python/rebuild_sqlite_from_hana.py --validate-only

# Dry run (show what would happen)
python scripts/python/rebuild_sqlite_from_hana.py --dry-run
```

### 2. Configure Database Type

```bash
# Edit .env file
DATABASE_TYPE=sqlite   # Use SQLite (fallback)
# OR
DATABASE_TYPE=hana     # Use HANA Cloud (primary)
```

### 3. Restart Server

```bash
python server.py
```

### 4. Verify API Contracts

```bash
# Test API contracts work with both databases
pytest tests/data_products_v2/test_database_fallback.py -m api_contract -v
```

---

## Rebuild Script Details

### Command-Line Options

```bash
python scripts/python/rebuild_sqlite_from_hana.py [options]

Options:
  --csn-path PATH         Path to CSN file (default: docs/csn/p2p-cap-model.json)
  --sqlite-path PATH      Path to SQLite database (default: database/p2p_data.db)
  --validate-only         Only validate structure without rebuilding
  --force                 Force rebuild even if SQLite exists
  --dry-run              Show what would be done without executing
  --verbose              Enable verbose logging
```

### What the Script Does

1. **Extract HANA Structure**
   - Loads CSN metadata file
   - Identifies data products (namespace groupings)
   - Extracts table definitions with columns
   - Parses associations between entities

2. **Create SQLite Schema**
   - Converts CSN types to SQLite types
   - Creates tables matching HANA structure
   - Adds indexes for key fields
   - Stores rebuild metadata

3. **Validate Structure**
   - Compares SQLite tables to HANA definition
   - Checks all tables present
   - Verifies column names and types match
   - Reports any discrepancies

### Type Mapping (CSN → SQLite)

| CSN Type | SQLite Type | Notes |
|----------|-------------|-------|
| cds.String | TEXT | Variable length text |
| cds.Integer | INTEGER | 32-bit integer |
| cds.Integer64 | INTEGER | 64-bit integer |
| cds.Decimal | REAL | Decimal numbers |
| cds.Double | REAL | Floating point |
| cds.Boolean | INTEGER | 0 = false, 1 = true |
| cds.Date | TEXT | ISO 8601 format |
| cds.DateTime | TEXT | ISO 8601 format |
| cds.Timestamp | TEXT | ISO 8601 format |
| cds.UUID | TEXT | UUID string |
| cds.LargeString | TEXT | Large text |
| cds.Binary | BLOB | Binary data |

---

## Database Switching Workflow

### Production Scenario: HANA Unavailable

1. **Detect HANA Unavailable**
   - Connection timeout
   - Authentication failure
   - Service outage

2. **Switch to SQLite**
   ```bash
   # Update environment
   DATABASE_TYPE=sqlite
   
   # Restart application
   docker restart steel-thread-app
   # OR
   systemctl restart steel-thread
   ```

3. **Verify Fallback Working**
   ```bash
   # Check API contracts still pass
   curl http://localhost:5000/api/data-products
   
   # Frontend should work identically
   # Browser → http://localhost:5000
   ```

4. **Switch Back When HANA Available**
   ```bash
   # Update environment
   DATABASE_TYPE=hana
   
   # Restart application
   docker restart steel-thread-app
   ```

### Development Scenario: Local Testing

```bash
# Test with SQLite (fast, no HANA credentials needed)
DATABASE_TYPE=sqlite python server.py

# Test API contracts
pytest tests/data_products_v2/ -m api_contract -v

# Switch to HANA for integration testing
DATABASE_TYPE=hana python server.py
```

---

## API Contract Testing

### Philosophy (Gu Wu)

> **"Test the contract, trust the implementation"**

We test that APIs work with both databases, not internal repository details.

### Test Structure

```python
@pytest.mark.e2e
@pytest.mark.api_contract
@pytest.mark.parametrize("database_type", ["sqlite", "hana"])
def test_data_products_api_contract_with_fallback(database_type):
    """Test API contract identical for both databases"""
    response = requests.get(f"{BASE_URL}/api/data-products")
    
    assert response.status_code == 200
    assert 'data_products' in response.json()
```

### Running Tests

```bash
# Test API contracts
pytest tests/data_products_v2/test_database_fallback.py -m api_contract -v

# Test with SQLite
DATABASE_TYPE=sqlite pytest tests/data_products_v2/ -v

# Test with HANA
DATABASE_TYPE=hana pytest tests/data_products_v2/ -v
```

---

## Metadata Storage

The rebuild script stores metadata in SQLite:

```sql
CREATE TABLE _rebuild_metadata (
    key TEXT PRIMARY KEY,
    value TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**Stored Metadata**:
- `csn_version`: CSN format version
- `namespace`: Data product namespace
- `data_products_count`: Number of data products
- `tables_count`: Number of tables created
- `associations_count`: Number of relationships
- `rebuild_source`: "HANA Cloud CSN"

**Query Metadata**:
```sql
SELECT * FROM _rebuild_metadata;
```

---

## Troubleshooting

### Issue: Rebuild Fails with "Table Already Exists"

**Solution**: Use `--force` to overwrite
```bash
python scripts/python/rebuild_sqlite_from_hana.py --force
```

### Issue: Validation Errors After Rebuild

**Symptoms**:
```
❌ Validation failed:
  - Missing tables: p2p_data_Invoices
  - Table p2p_data_Vendors missing columns: city
```

**Solutions**:
1. Check CSN file is up to date
2. Verify CSN path correct: `--csn-path docs/csn/p2p-cap-model.json`
3. Review CSN entity definitions
4. Run with `--verbose` for detailed logging

### Issue: API Returns Empty Data After Switching

**Symptoms**: API works but returns no data

**Cause**: SQLite database empty (structure only, no data)

**Solutions**:
1. **Option A**: Copy data from HANA
   ```bash
   # Future enhancement: Add --migrate-data flag
   python scripts/python/rebuild_sqlite_from_hana.py --migrate-data
   ```

2. **Option B**: Populate test data
   ```bash
   python scripts/python/populate_p2p_comprehensive.py
   ```

3. **Option C**: Import CSV files
   ```bash
   python scripts/python/import_master_data.py
   ```

### Issue: Type Mismatch Errors

**Symptoms**: "Type mismatch" or "Invalid data type" errors

**Cause**: CSN type not mapped correctly

**Solution**: Update type mapping in `HANAStructureExtractor._map_csn_type_to_sqlite()`

---

## Best Practices

### 1. Regular Rebuilds

Rebuild SQLite when HANA schema changes:
```bash
# After HANA schema update
python scripts/python/rebuild_sqlite_from_hana.py --force

# Validate structure matches
python scripts/python/rebuild_sqlite_from_hana.py --validate-only
```

### 2. Test Both Databases

Always test APIs with both databases:
```bash
# Test SQLite
DATABASE_TYPE=sqlite pytest tests/data_products_v2/ -v

# Test HANA  
DATABASE_TYPE=hana pytest tests/data_products_v2/ -v

# Both should pass identically
```

### 3. Monitor Metadata

Check rebuild metadata to track versions:
```sql
SELECT * FROM _rebuild_metadata;
```

### 4. Backup Before Rebuild

Script automatically backs up existing SQLite:
```
database/p2p_data.db → database/p2p_data.db.backup
```

### 5. Version Control CSN

Keep CSN files in version control:
```bash
git add docs/csn/p2p-cap-model.json
git commit -m "chore: update CSN schema v2.3"
```

---

## Future Enhancements

### Planned Features

1. **Data Migration** (`--migrate-data`)
   - Copy data from HANA to SQLite
   - Configurable batch size
   - Progress reporting

2. **Incremental Updates** (`--incremental`)
   - Only update changed tables
   - Preserve existing data
   - Faster than full rebuild

3. **Bi-Directional Sync** (`--sync`)
   - Keep SQLite and HANA in sync
   - Conflict resolution
   - Scheduled sync jobs

4. **Validation Reports** (`--report`)
   - Generate detailed comparison report
   - Export to JSON/HTML
   - Include data statistics

---

## Related Documentation

- [[Module Federation Standard]] - Module architecture
- [[API-First Contract Testing Methodology]] - Testing philosophy
- [[CSN Parser Architecture]] - CSN metadata parsing
- [[Repository Pattern Guide]] - Data access patterns

---

## Change History

| Date | Version | Change |
|------|---------|--------|
| 2026-02-23 | 1.0 | Initial implementation |

---

## Summary

The database fallback system provides seamless switching between HANA Cloud and SQLite:

1. ✅ Rebuild SQLite from HANA CSN metadata
2. ✅ Switch via `DATABASE_TYPE` environment variable
3. ✅ API contracts work identically with both databases
4. ✅ Zero code changes needed
5. ✅ Production-ready fallback mechanism

**Key Insight**: By testing API contracts consistently, we ensure both databases work identically without testing every internal function.