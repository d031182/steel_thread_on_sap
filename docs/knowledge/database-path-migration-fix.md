# Database Path Migration Fix

**Date**: 2026-02-23  
**Status**: ✅ RESOLVED  
**Related**: [[Database Fallback Guide]], [[Module Federation Standard]]

## Problem

Database files (`p2p_graph.db`, `p2p_data.db`) were being created in the **wrong location**:
- ❌ **Incorrect**: `database/p2p_graph.db` (root-level `/database/` directory)
- ✅ **Correct**: `modules/knowledge_graph_v2/database/p2p_graph.db` (module-owned)

This violated the **Module Federation Standard** principle that modules own their data.

## Root Cause

`core/services/database_path_resolvers.py` had two issues:

1. **Default strategy was "legacy"** instead of "module_owned"
2. **Directory creation logic** was missing for module-owned paths

```python
# BEFORE (WRONG)
DEFAULT_STRATEGY = "legacy"  # ❌ Points to root-level /database/

def get_database_path(self, db_name: str, db_type: str = "sqlite") -> str:
    if self.strategy == "module_owned":
        module_name = self.module_name or "unknown_module"
        path = self.project_root / "modules" / module_name / "database" / db_name
        # ❌ Missing: path.parent.mkdir(parents=True, exist_ok=True)
        return str(path)
    # ...legacy fallback
```

## Solution

### 1. Changed Default Strategy to "module_owned"

```python
# AFTER (CORRECT)
DEFAULT_STRATEGY = "module_owned"  # ✅ Module-owned by default
```

**Impact**: All new database instances default to module-owned paths unless explicitly overridden.

### 2. Added Directory Creation Logic

```python
def get_database_path(self, db_name: str, db_type: str = "sqlite") -> str:
    if self.strategy == "module_owned":
        module_name = self.module_name or "unknown_module"
        path = self.project_root / "modules" / module_name / "database" / db_name
        
        # ✅ Create directory if it doesn't exist
        path.parent.mkdir(parents=True, exist_ok=True)
        
        return str(path)
```

**Impact**: Module database directories auto-created on first access.

### 3. Updated .gitignore

Added explicit rule to prevent root-level `/database/` directory:

```gitignore
# Database files (prevent root-level sprawl)
# Only allow databases in designated locations:
# - modules/*/database/*.db (module-owned production data)
# - logs/*.db (application logs)
# - tools/guwu/metrics.db (test metrics)
# Note: /database/ directory removed - databases now live in modules/*/database/
/*.db
/database/*.db  # ✅ Block root-level database directory
```

## Migration Steps

1. **Stop server**: Ensure no processes accessing databases
2. **Copy databases to module location**:
   ```bash
   copy database\p2p_data.db modules\knowledge_graph_v2\database\p2p_data.db
   copy database\p2p_graph.db modules\knowledge_graph_v2\database\p2p_graph.db
   ```
3. **Delete old root-level databases**:
   ```bash
   del database\p2p_graph.db
   del database\p2p_data.db
   ```
4. **Restart server**: Verify databases loaded from correct location

## Verification

```bash
# Start server
python server.py

# Check logs for database paths
# Should show: modules/knowledge_graph_v2/database/p2p_graph.db
# NOT: database/p2p_graph.db
```

## Architecture Principle

**Module Federation Standard**: Modules own their data
- ✅ `modules/knowledge_graph_v2/database/` - Module-owned databases
- ✅ `modules/ai_assistant/database/` - Module-owned databases
- ❌ `database/` - Root-level sprawl (violates modularity)

## Key Learnings

1. **Default strategy matters**: Setting `DEFAULT_STRATEGY = "legacy"` caused all new instances to use wrong path
2. **Auto-create directories**: `path.parent.mkdir(parents=True, exist_ok=True)` prevents runtime errors
3. **Explicit .gitignore**: Block root-level `/database/` directory to prevent future violations

## Files Changed

1. `core/services/database_path_resolvers.py` - Changed default strategy + added mkdir
2. `.gitignore` - Added `/database/*.db` rule
3. Migrated databases from `database/` to `modules/knowledge_graph_v2/database/`

## Related Standards

- [[Module Federation Standard]] - Module ownership principles
- [[Database Fallback Guide]] - Database path resolution logic
- [[Database Fallback Quick Reference]] - Path resolver usage

---

**Status**: ✅ Complete - Databases now correctly located in module-owned paths