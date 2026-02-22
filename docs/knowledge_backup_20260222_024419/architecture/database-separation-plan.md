# Database Separation Plan (SoC Compliance)

**Problem**: Graph cache tables mixed with P2P data product tables  
**Violation**: Separation of Concerns principle  
**Solution**: Split into two module-specific databases  
**Priority**: 🔴 HIGH (architecture cleanup)

---

## 🎯 Current Violation

### **Single Database** (WRONG ❌):
```
modules/data_products/database/p2p_sample.db
├── [49 P2P tables]    ← Data Products concern
│   ├── CompanyCode
│   ├── Product
│   ├── PurchaseOrder
│   └── ... (46 more)
└── [3 Graph tables]   ← Knowledge Graph concern
    ├── graph_edges
    ├── graph_nodes
    └── graph_ontology
```

**Why This Is Wrong**:
1. ❌ **Mixed Concerns**: Business data + visualization cache in same database
2. ❌ **Module Coupling**: Knowledge Graph depends on Data Products database
3. ❌ **Cannot Test Independently**: KG tests require P2P database
4. ❌ **Cannot Deploy Separately**: Modules share storage
5. ❌ **Violates Single Responsibility**: Database serves two purposes

---

## ✅ Target Architecture

### **Two Separate Databases** (CORRECT ✅):

```
modules/
├── data_products/
│   └── database/
│       └── p2p_data.db          ← 49 P2P tables ONLY
│
└── knowledge_graph/
    └── database/
        └── graph_cache.db       ← 3 graph cache tables ONLY
```

**Why This Is Correct**:
1. ✅ **Clear Separation**: Each module owns its database
2. ✅ **Loose Coupling**: Modules independent
3. ✅ **Independent Testing**: KG tests don't need P2P data
4. ✅ **Independent Deployment**: Deploy modules separately
5. ✅ **Single Responsibility**: Each database serves one purpose

---

## 🔨 Implementation Plan

### **Step 1: Create Knowledge Graph Database** (15 min)

Create new database structure:
```
modules/knowledge_graph/database/
├── graph_cache.db           # Graph cache database (NEW)
└── schema/                  # Schema definitions (NEW)
    ├── graph_cache.sql      # DDL for graph_cache.db
    └── README.md            # Schema documentation
```

SQL schema (`modules/knowledge_graph/database/schema/graph_cache.sql`):
```sql
-- Graph Cache Schema (Knowledge Graph Module)
-- Purpose: Store pre-computed graph visualizations
-- Version: 1.0

CREATE TABLE IF NOT EXISTS graph_ontology (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    type TEXT NOT NULL,           -- 'schema' or 'data'
    data_source TEXT NOT NULL,    -- 'sqlite' or 'hana'
    metadata TEXT,                -- JSON metadata
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS graph_nodes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ontology_id INTEGER NOT NULL,
    node_id TEXT NOT NULL,
    label TEXT NOT NULL,
    group_name TEXT,
    node_data TEXT,               -- JSON: full vis.js node definition
    FOREIGN KEY (ontology_id) REFERENCES graph_ontology(id) ON DELETE CASCADE,
    UNIQUE (ontology_id, node_id)
);

CREATE TABLE IF NOT EXISTS graph_edges (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ontology_id INTEGER NOT NULL,
    from_node TEXT NOT NULL,
    to_node TEXT NOT NULL,
    relationship_type TEXT NOT NULL,
    edge_data TEXT,               -- JSON: full vis.js edge definition
    FOREIGN KEY (ontology_id) REFERENCES graph_ontology(id) ON DELETE CASCADE
);

CREATE INDEX idx_graph_nodes_ontology ON graph_nodes(ontology_id);
CREATE INDEX idx_graph_edges_ontology ON graph_edges(ontology_id);
```

---

### **Step 2: Create Migration Script** (30 min)

```python
# scripts/python/split_graph_cache_database.py
"""
Database Separation Migration
==============================
Splits graph cache tables from P2P data products database.

BEFORE: p2p_sample.db contains 49 P2P tables + 3 graph tables
AFTER:  p2p_data.db contains 49 P2P tables only
        graph_cache.db contains 3 graph tables only
"""

import sys
import os
import sqlite3
import shutil
from datetime import datetime

# Windows UTF-8 support
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

def split_databases():
    """Split graph cache from P2P data products."""
    
    # Paths
    source_db = 'modules/data_products/database/p2p_sample.db'
    p2p_db = 'modules/data_products/database/p2p_data.db'
    graph_db = 'modules/knowledge_graph/database/graph_cache.db'
    
    print("[*] Database Separation Migration")
    print("=" * 60)
    
    # Step 1: Backup original
    backup = f"{source_db}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    shutil.copy2(source_db, backup)
    print(f"[+] Backup created: {backup}")
    
    # Step 2: Create KG database directory
    kg_db_dir = os.path.dirname(graph_db)
    os.makedirs(kg_db_dir, exist_ok=True)
    print(f"[+] Created directory: {kg_db_dir}")
    
    # Step 3: Copy graph tables to KG database
    source_conn = sqlite3.connect(source_db)
    graph_conn = sqlite3.connect(graph_db)
    
    graph_tables = ['graph_ontology', 'graph_nodes', 'graph_edges']
    
    for table in graph_tables:
        # Get CREATE statement
        cursor = source_conn.cursor()
        cursor.execute(f"SELECT sql FROM sqlite_master WHERE type='table' AND name='{table}'")
        create_sql = cursor.fetchone()
        
        if create_sql:
            # Create table in graph database
            graph_conn.execute(create_sql[0])
            
            # Copy data
            cursor.execute(f"SELECT * FROM {table}")
            rows = cursor.fetchall()
            
            if rows:
                # Get column count
                placeholders = ','.join(['?'] * len(rows[0]))
                graph_conn.executemany(
                    f"INSERT INTO {table} VALUES ({placeholders})",
                    rows
                )
            
            print(f"[+] Copied {table}: {len(rows)} rows")
    
    graph_conn.commit()
    graph_conn.close()
    
    # Step 4: Create P2P database without graph tables
    shutil.copy2(source_db, p2p_db)
    p2p_conn = sqlite3.connect(p2p_db)
    
    for table in graph_tables:
        p2p_conn.execute(f"DROP TABLE IF EXISTS {table}")
        print(f"[-] Removed {table} from P2P database")
    
    # Also remove indexes
    p2p_conn.execute("DROP INDEX IF EXISTS idx_graph_nodes_ontology")
    p2p_conn.execute("DROP INDEX IF EXISTS idx_graph_edges_ontology")
    
    p2p_conn.commit()
    p2p_conn.close()
    source_conn.close()
    
    # Step 5: Verify separation
    print("\n[*] Verification:")
    print("-" * 60)
    
    p2p_conn = sqlite3.connect(p2p_db)
    cursor = p2p_conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM sqlite_master WHERE type='table'")
    p2p_count = cursor.fetchone()[0]
    p2p_conn.close()
    
    graph_conn = sqlite3.connect(graph_db)
    cursor = graph_conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM sqlite_master WHERE type='table'")
    graph_count = cursor.fetchone()[0]
    graph_conn.close()
    
    print(f"[+] P2P Database: {p2p_count} tables (should be ~49)")
    print(f"[+] Graph Database: {graph_count} tables (should be 3)")
    
    print("\n[*] Migration Complete!")
    print("=" * 60)
    print(f"[+] P2P Data: {p2p_db}")
    print(f"[+] Graph Cache: {graph_db}")
    print(f"[+] Original Backup: {backup}")

if __name__ == '__main__':
    split_databases()
```

---

### **Step 3: Update Module Configurations** (20 min)

**A. Data Products Module** (`modules/data_products/backend/sqlite_data_products_service.py`):
```python
# Change default database path
db_path = os.path.join(
    os.path.dirname(__file__),
    '..',
    'database',
    'p2p_data.db'  # ← Changed from p2p_sample.db
)
```

**B. Knowledge Graph Module** (create new service if needed):
```python
# modules/knowledge_graph/backend/graph_cache_db_service.py
class GraphCacheDBService:
    """SQLite service for graph cache storage."""
    
    def __init__(self, db_path: str = None):
        if db_path is None:
            db_path = os.path.join(
                os.path.dirname(__file__),
                '..',
                'database',
                'graph_cache.db'  # ← NEW graph cache database
            )
        self.db_path = db_path
```

**C. Update GraphCacheService** (`core/services/graph_cache_service.py`):
```python
# Change initialization to use KG module database
def __init__(self, db_path: str = None):
    if db_path is None:
        # Default to knowledge_graph module database
        db_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)),  # core/
            '..',                                         # root
            'modules',
            'knowledge_graph',
            'database',
            'graph_cache.db'  # ← Use KG module database
        )
    self.db_path = db_path
```

**D. Update OntologyPersistenceService** (`core/services/ontology_persistence_service.py`):
```python
# Same change as GraphCacheService
# Point to modules/knowledge_graph/database/graph_cache.db
```

**E. Update VisJsTranslator** (`core/services/visjs_translator.py`):
```python
# Same change - use graph_cache.db
```

---

### **Step 4: Update .gitignore** (5 min)

```gitignore
# Database files (binary, don't commit)
*.db

# EXCEPT: Keep schema definitions
!modules/*/database/schema/*.sql

# Allow schema directories
!modules/*/database/schema/
```

---

### **Step 5: Testing** (15 min)

**Test 1: Data Products Module**
```bash
python scripts/python/test_api_endpoints.py
# Should work with p2p_data.db
```

**Test 2: Knowledge Graph Module**
```bash
# Visit http://localhost:5000
# Click "Knowledge Graph" tab
# Click "Refresh Graph"
# Should work with graph_cache.db
```

**Test 3: Independent Module Testing**
```bash
# Test KG module without P2P database
rm modules/data_products/database/p2p_data.db
# KG should still work (has its own database)
```

---

## 📊 Migration Impact Analysis

### **Files to Modify** (8 files):
1. `modules/data_products/backend/sqlite_data_products_service.py` - Database path
2. `core/services/graph_cache_service.py` - Database path
3. `core/services/ontology_persistence_service.py` - Database path
4. `core/services/visjs_translator.py` - Database path
5. `modules/knowledge_graph/backend/relationship_discovery_db.py` - Database path (if uses graph_ontology)
6. `.gitignore` - Schema directory exceptions
7. `docs/knowledge/architecture/database-architecture.md` - Update locations
8. `PROJECT_TRACKER.md` - Document migration

### **Files to Create** (3 files):
1. `scripts/python/split_graph_cache_database.py` - Migration script
2. `modules/knowledge_graph/database/schema/graph_cache.sql` - Schema DDL
3. `modules/knowledge_graph/database/schema/README.md` - Documentation

### **Databases After Migration** (2 databases):
1. `modules/data_products/database/p2p_data.db` - 49 P2P tables ✅
2. `modules/knowledge_graph/database/graph_cache.db` - 3 graph tables ✅

---

## ⚠️ Safety Checkpoint Required

**This is a CRITICAL operation** (database migration, multi-file changes)

**Before proceeding**:
1. ✅ Check git status
2. ✅ Create safety checkpoint: `git add . && git commit && git push`
3. ✅ Get user approval to proceed
4. ✅ Run migration script
5. ✅ Test both modules independently
6. ✅ Commit separated databases

**Rollback Plan**: `git reset --hard HEAD~1` if migration fails

---

## 🎯 Benefits After Separation

### **Separation of Concerns** ✅:
- Data Products module: Business data storage
- Knowledge Graph module: Visualization cache storage
- Clear responsibility boundaries

### **Module Independence** ✅:
- Deploy KG module without P2P data
- Test KG module in isolation
- Swap data sources without affecting cache

### **Performance** ✅:
- Smaller databases (faster queries)
- Independent optimization
- Separate backup/restore strategies

### **Maintainability** ✅:
- Clear database ownership
- Easier to understand structure
- Module-specific schema evolution

---

## 📋 Execution Checklist

- [ ] Get user approval for database separation
- [ ] Create safety checkpoint (git push)
- [ ] Run migration script
- [ ] Update module configurations (5 files)
- [ ] Test data_products module independently
- [ ] Test knowledge_graph module independently
- [ ] Verify no references to old database
- [ ] Update documentation
- [ ] Commit all changes
- [ ] Archive old p2p_sample.db

**Estimated Time**: 90 minutes  
**Risk Level**: 🔴 HIGH (requires safety checkpoint)  
**Impact**: 8 files modified, 3 files created, architecture improved

---

## 🔗 Related Documents

- [[Database Architecture]] - Overall database strategy
- [[Feng Shui Separation of Concerns]] - SoC principle
- [[Module Quality Gate]] - Module independence checks

---

## 📝 Decision Record

**Date**: 2026-02-05  
**Issue**: Graph cache tables in Data Products database  
**Decision**: Split into module-specific databases  
**Rationale**: Separation of Concerns compliance  
**Impact**: Improved modularity, testability, maintainability