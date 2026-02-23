# Database Rebuild Scripts

**Purpose**: Tools for rebuilding SQLite database from HANA Cloud source

---

## Primary Script

### `rebuild_sqlite_from_hana.py` ⭐ RECOMMENDED

**Purpose**: Comprehensive rebuild tool with validation and testing support

**Features**:
- ✅ Extract HANA structure from CSN metadata
- ✅ Create matching SQLite schema
- ✅ Validate structure correctness
- ✅ Store rebuild metadata
- ✅ Automatic backup of existing database
- ✅ Multiple operation modes (rebuild, validate, dry-run)

**Usage**:
```bash
# Basic rebuild
python scripts/python/rebuild_sqlite_from_hana.py

# Force overwrite existing
python scripts/python/rebuild_sqlite_from_hana.py --force

# Validate only (no rebuild)
python scripts/python/rebuild_sqlite_from_hana.py --validate-only

# Dry run (show plan)
python scripts/python/rebuild_sqlite_from_hana.py --dry-run

# Verbose logging
python scripts/python/rebuild_sqlite_from_hana.py --verbose

# Help
python scripts/python/rebuild_sqlite_from_hana.py --help
```

**Output**:
- SQLite database: `database/p2p_data.db`
- Backup (if exists): `database/p2p_data.db.backup`
- Metadata table: `_rebuild_metadata`

---

## Legacy Scripts

### `rebuild_sqlite_from_hana_csn.py`

**Status**: Legacy (use `rebuild_sqlite_from_hana.py` instead)

**Differences**:
- Older implementation
- Less validation
- No dry-run mode
- No metadata storage

**Migration**:
Replace calls to `rebuild_sqlite_from_hana_csn.py` with `rebuild_sqlite_from_hana.py`

---

## Related Scripts

### Data Population

After rebuilding structure, populate data:

```bash
# Comprehensive P2P test data
python scripts/python/populate_p2p_comprehensive.py

# Master data from HANA
python scripts/python/populate_master_data_from_hana.py

# Invoice data only
python scripts/python/add_invoices_only.py
```

### Validation

```bash
# Compare HANA and SQLite schemas
python scripts/python/compare_hana_sqlite_schemas.py

# Validate CSN compliance
python scripts/python/validate_hana_csn_compliance.py
```

### Maintenance

```bash
# Cleanup graph database
python scripts/python/cleanup_graph_database.py

# Cleanup P2P data
python scripts/python/cleanup_p2p_data_database.py
```

---

## Database Switching

After rebuild, switch databases via environment variable:

```bash
# Edit .env
DATABASE_TYPE=sqlite   # Use SQLite fallback
# OR
DATABASE_TYPE=hana     # Use HANA Cloud

# Restart server
python server.py
```

See [[database-fallback-guide]] for complete documentation.

---

## Testing

Verify rebuild worked correctly:

```bash
# Run API contract tests
pytest tests/data_products_v2/test_database_fallback.py -m api_contract -v

# Test with SQLite
DATABASE_TYPE=sqlite pytest tests/data_products_v2/ -v

# Test with HANA
DATABASE_TYPE=hana pytest tests/data_products_v2/ -v
```

---

## Architecture

```
CSN Metadata (docs/csn/p2p-cap-model.json)
    ↓
rebuild_sqlite_from_hana.py
    ↓
SQLite Database (database/p2p_data.db)
    ↓
Repository Factory (DATABASE_TYPE env var)
    ↓
Data Products API (same contract for both)
```

---

## Troubleshooting

See [[database-fallback-guide]] troubleshooting section for common issues.

Quick fixes:

```bash
# Table exists error
python scripts/python/rebuild_sqlite_from_hana.py --force

# Validation errors
python scripts/python/rebuild_sqlite_from_hana.py --verbose

# Empty data after rebuild
python scripts/python/populate_p2p_comprehensive.py
```

---

## Summary

1. ⭐ Use `rebuild_sqlite_from_hana.py` (recommended)
2. Run with `--force` to overwrite existing database
3. Validate with `--validate-only`
4. Switch databases via `DATABASE_TYPE` in `.env`
5. Test APIs work with both databases

**Key Insight**: SQLite mirrors HANA structure exactly, enabling seamless fallback via environment variable.