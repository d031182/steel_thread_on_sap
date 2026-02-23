# Database Fallback Quick Reference

**TLDR**: Switch databases via `DATABASE_TYPE` environment variable

---

## 🚀 Quick Start (5 Minutes)

### Step 1: Rebuild SQLite from HANA
```bash
python scripts/python/rebuild_sqlite_from_hana.py --force
```

### Step 2: Configure Database
```bash
# Edit .env
DATABASE_TYPE=sqlite   # Use SQLite fallback
# OR
DATABASE_TYPE=hana     # Use HANA Cloud
```

### Step 3: Restart Server
```bash
python server.py
```

### Step 4: Verify
```bash
# Test API works
curl http://localhost:5000/api/data-products

# Run contract tests
pytest tests/data_products_v2/test_database_fallback.py -m api_contract -v
```

---

## 🔄 Common Workflows

### Switch to SQLite (Fallback)
```bash
# 1. Update environment
DATABASE_TYPE=sqlite

# 2. Restart server
python server.py

# 3. Verify (should see "Using SQLite" in logs)
curl http://localhost:5000/api/data-products
```

### Switch to HANA (Primary)
```bash
# 1. Update environment
DATABASE_TYPE=hana

# 2. Restart server
python server.py

# 3. Verify (should see "Using HANA" in logs)
curl http://localhost:5000/api/data-products
```

### Rebuild After Schema Change
```bash
# When HANA schema updated
python scripts/python/rebuild_sqlite_from_hana.py --force

# Validate structure matches
python scripts/python/rebuild_sqlite_from_hana.py --validate-only
```

---

## 🧪 Testing Both Databases

```bash
# Test with SQLite
DATABASE_TYPE=sqlite pytest tests/data_products_v2/ -v

# Test with HANA
DATABASE_TYPE=hana pytest tests/data_products_v2/ -v

# Both should pass identically
```

---

## 📝 Script Options

| Option | Purpose | Example |
|--------|---------|---------|
| `--force` | Overwrite existing SQLite | `--force` |
| `--validate-only` | Check without rebuilding | `--validate-only` |
| `--dry-run` | Show plan without executing | `--dry-run` |
| `--verbose` | Detailed logging | `--verbose` |
| `--csn-path` | Custom CSN file | `--csn-path path/to/csn.json` |
| `--sqlite-path` | Custom SQLite location | `--sqlite-path path/to/db.db` |

---

## ⚠️ Troubleshooting

### "Table already exists"
```bash
# Use --force to overwrite
python scripts/python/rebuild_sqlite_from_hana.py --force
```

### "Validation failed"
```bash
# Check CSN file path correct
python scripts/python/rebuild_sqlite_from_hana.py --csn-path docs/csn/p2p-cap-model.json --verbose
```

### "API returns empty data"
```bash
# SQLite has structure but no data
# Populate test data:
python scripts/python/populate_p2p_comprehensive.py
```

---

## 📚 Full Documentation

See [[database-fallback-guide]] for complete details.