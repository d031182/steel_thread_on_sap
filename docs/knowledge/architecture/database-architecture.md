# Database Architecture Guide

**Purpose**: Complete guide to database structure, locations, and reconstruction
**Last Updated**: 2026-02-05
**Version**: 1.0

---

## 📍 1. Current Active Database

### **Answer**: `modules/data_products/database/p2p_sample.db`

**Location**: `modules/data_products/database/p2p_sample.db`  
**Size**: ~several MB (contains P2P data products)  
**Purpose**: Primary data source for Data Products module  
**Code Reference**: `modules/data_products/backend/sqlite_data_products_service.py` line 35

```python
# Default database path in SQLiteDataProductsService.__init__()
db_path = os.path.join(
    os.path.dirname(__file__),  # modules/data_products/backend/
    '..',                        # modules/data_products/
    'database',                  # modules/data_products/database/
    'p2p_sample.db'             # ← ACTIVE DATABASE
)
```

---

## 🗂️ 2. All Databases Found (Current State)

### **Production Databases** (Active Use):
1. **`modules/data_products/database/p2p_sample.db`** ⭐ PRIMARY
   - Data Products module (P2P tables)
   - Purchase Orders, Suppliers, Invoices, etc.
   
2. **`p2p_data.db`** (root) ⚠️ DUPLICATE
   - Legacy/orphaned database in root
   - Should be removed or consolidated

3. **`logs/app_logs.db`**
   - Application logging
   - Log Manager module

4. **`tests/guwu/metrics.db`**
   - Gu Wu testing metrics
   - Test framework data

### **Legacy/Backup Databases** (Not Active):
5. **`app/database/p2p_data_products.db`** 
   - Old location (before module structure)
   
6. **`database_cleanup_backup_20260205/`** (7 databases)
   - Historical backups
   - Can be archived/removed after verification

---

## 📂 3. Where Should Database Reside Best?

### **✅ CORRECT (Current)**:
```
modules/data_products/database/p2p_sample.db
```

**Why This Location**:
1. ✅ **Module Co-location**: Database lives with module that uses it
2. ✅ **Clean Separation**: Each module owns its data
3. ✅ **Testability**: Easy to swap for testing (module-specific)
4. ✅ **Portability**: Module can be deployed independently
5. ✅ **Version Control**: `.gitignore` can exclude per-module

### **❌ AVOID**:
```
❌ /database/          # Generic folder, no module ownership
❌ /app/database/      # Couples to app, not module
❌ / (root)            # Clutters root directory
```

### **Module-Specific Database Pattern** (Best Practice):
```
modules/
├── data_products/
│   ├── backend/
│   ├── database/              ← Database lives here
│   │   ├── p2p_sample.db      ← Active database
│   │   └── schema/            ← Schema definitions
│   │       └── *.sql
│   └── module.json
├── knowledge_graph/
│   ├── backend/
│   ├── database/              ← KG database (if needed)
│   │   └── ontology_cache.db
│   └── module.json
└── log_manager/
    ├── backend/
    └── database/              ← Logs database
        └── app_logs.db
```

---

## 🔨 4. How to Reconstruct Database

### **Option A: From SQL Scripts** (Recommended)

**Step 1**: Create SQL schema file
```sql
-- modules/data_products/database/schema/p2p_complete.sql
-- Generated from CSN files

-- Purchase Order tables
CREATE TABLE IF NOT EXISTS PurchaseOrder (
    PurchaseOrder TEXT PRIMARY KEY,
    ...
);

CREATE TABLE IF NOT EXISTS PurchaseOrderItem (
    PurchaseOrder TEXT,
    PurchaseOrderItem TEXT,
    ...
    FOREIGN KEY (PurchaseOrder) REFERENCES PurchaseOrder(PurchaseOrder),
    PRIMARY KEY (PurchaseOrder, PurchaseOrderItem)
);

-- Supplier tables
CREATE TABLE IF NOT EXISTS Supplier (
    SupplierID TEXT PRIMARY KEY,
    ...
);

-- ... other tables
```

**Step 2**: Create reconstruction script
```python
# scripts/python/rebuild_database.py
import sqlite3
import os

def rebuild_database(db_path: str, schema_path: str):
    """Rebuild database from SQL schema."""
    # Backup existing database
    if os.path.exists(db_path):
        backup = f"{db_path}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        shutil.copy2(db_path, backup)
        print(f"Backup created: {backup}")
    
    # Create fresh database
    conn = sqlite3.connect(db_path)
    with open(schema_path, 'r', encoding='utf-8') as f:
        schema_sql = f.read()
    
    conn.executescript(schema_sql)
    conn.commit()
    conn.close()
    print(f"Database rebuilt: {db_path}")

if __name__ == '__main__':
    rebuild_database(
        'modules/data_products/database/p2p_sample.db',
        'modules/data_products/database/schema/p2p_complete.sql'
    )
```

**Step 3**: Store SQL safely
```
modules/data_products/database/schema/
├── p2p_complete.sql           # Full schema (all products)
├── purchaseorder.sql          # PurchaseOrder product only
├── supplierinvoice.sql        # SupplierInvoice product only
└── master_data.sql            # Master data (Supplier, Product, etc.)
```

**Git Best Practices**:
```gitignore
# .gitignore
*.db                           # Exclude binary databases
!modules/*/database/schema/    # Include schema definitions
modules/*/database/*.sql       # Include SQL scripts
```

---

### **Option B: From CSN Files** (HANA-Compatible)

**YES** - You CAN reconstruct data product tables from CSN files with HANA compatibility!

**CSN → SQLite Mapping Strategy**:

```python
# scripts/python/csn_to_sqlite.py
import json
import sqlite3

def csn_to_sqlite_ddl(csn_file: str) -> str:
    """Convert CSN definition to SQLite DDL."""
    with open(csn_file, 'r', encoding='utf-8') as f:
        csn = json.load(f)
    
    ddl_statements = []
    
    # Get entities from CSN
    entities = csn.get('definitions', {})
    
    for entity_name, entity_def in entities.items():
        if entity_def.get('kind') != 'entity':
            continue
        
        # Extract table name
        table_name = entity_name.split('.')[-1]
        
        # Build column definitions
        columns = []
        primary_keys = []
        foreign_keys = []
        
        for field_name, field_def in entity_def.get('elements', {}).items():
            # Map CSN type to SQLite type
            csn_type = field_def.get('type', 'String')
            sqlite_type = map_csn_to_sqlite_type(csn_type)
            
            # Handle constraints
            constraints = []
            if field_def.get('key'):
                primary_keys.append(field_name)
            if field_def.get('notNull'):
                constraints.append('NOT NULL')
            
            # Check for foreign key (association)
            if 'target' in field_def:
                target_entity = field_def['target']
                target_table = target_entity.split('.')[-1]
                target_key = field_def.get('keys', [{}])[0].get('ref', [field_name])[0]
                foreign_keys.append(
                    f"FOREIGN KEY ({field_name}) REFERENCES {target_table}({target_key})"
                )
            
            column_def = f"{field_name} {sqlite_type} {' '.join(constraints)}"
            columns.append(column_def)
        
        # Add PRIMARY KEY constraint if multiple keys
        if len(primary_keys) > 1:
            columns.append(f"PRIMARY KEY ({', '.join(primary_keys)})")
        elif len(primary_keys) == 1:
            # Add to column definition
            pk_col = primary_keys[0]
            for i, col in enumerate(columns):
                if col.startswith(pk_col + ' '):
                    columns[i] += ' PRIMARY KEY'
        
        # Add foreign key constraints
        columns.extend(foreign_keys)
        
        # Create table statement
        ddl = f"CREATE TABLE IF NOT EXISTS {table_name} (\n"
        ddl += ",\n".join(f"  {col}" for col in columns)
        ddl += "\n);"
        
        ddl_statements.append(ddl)
    
    return "\n\n".join(ddl_statements)

def map_csn_to_sqlite_type(csn_type: str) -> str:
    """Map CSN data types to SQLite types."""
    mapping = {
        'String': 'TEXT',
        'Integer': 'INTEGER',
        'Integer64': 'INTEGER',
        'Decimal': 'REAL',
        'Double': 'REAL',
        'Date': 'TEXT',  # Store as ISO date string
        'DateTime': 'TEXT',  # Store as ISO datetime string
        'Time': 'TEXT',
        'Boolean': 'INTEGER',  # 0 or 1
        'UUID': 'TEXT',
        'Binary': 'BLOB',
        'LargeBinary': 'BLOB',
        'LargeString': 'TEXT'
    }
    return mapping.get(csn_type, 'TEXT')

# Example usage:
if __name__ == '__main__':
    csn_files = [
        'data-products/sap-s4com-PurchaseOrder-v1.en.json',
        'data-products/sap-s4com-Supplier-v1.en.json',
        # ... other CSN files
    ]
    
    all_ddl = []
    for csn_file in csn_files:
        ddl = csn_to_sqlite_ddl(csn_file)
        all_ddl.append(ddl)
    
    # Write to schema file
    with open('modules/data_products/database/schema/from_csn.sql', 'w') as f:
        f.write('\n\n'.join(all_ddl))
    
    print("Schema generated from CSN files!")
```

**HANA Compatibility**:
- ✅ **Table Names**: CSN entity names → SQLite table names (same)
- ✅ **Column Names**: CSN element names → SQLite columns (same)
- ✅ **Primary Keys**: CSN `key: true` → SQLite PRIMARY KEY (same)
- ✅ **Foreign Keys**: CSN associations → SQLite FOREIGN KEY (mapped)
- ✅ **Data Types**: CSN types → SQLite types (mapped, lossy but functional)

**Limitations**:
- ⚠️ **Type Precision**: HANA `DECIMAL(10,2)` → SQLite `REAL` (less precise)
- ⚠️ **Annotations**: CSN `@` annotations not stored in SQLite
- ⚠️ **Calculated Fields**: CSN calculated elements need manual handling

**Recommendation**: Use CSN as SOURCE OF TRUTH for schema, but generate SQLite-compatible DDL from it.

---

## 🎯 5. Recommended Database Strategy

### **Phase 1: Current (Development)**
```
modules/data_products/database/p2p_sample.db
```
- Local SQLite for fast development
- No HANA Cloud dependency

### **Phase 2: HANA-Compatible Schema**
```
modules/data_products/database/schema/
├── from_csn.sql           # Generated from CSN files
├── p2p_complete.sql       # Manual optimizations
└── rebuild.py             # Reconstruction script
```
- Schema versioned in git
- Can rebuild database anytime
- HANA-compatible structure

### **Phase 3: Production (HANA Cloud)**
```
hana_data_source.py → HANA Cloud tables
sqlite_data_source.py → Local tables
```
- Swap data sources via DI
- Same interface for both

---

## 📋 6. Database Cleanup Checklist

### **Immediate Actions**:
- [ ] Move `p2p_data.db` (root) → archive or delete
- [ ] Move `app/database/p2p_data_products.db` → archive
- [ ] Archive `database_cleanup_backup_20260205/` folder
- [ ] Document active databases in this file

### **Best Practices**:
- [ ] Create SQL schema files from current database
- [ ] Add schema files to git (`.sql` only, not `.db`)
- [ ] Create reconstruction script
- [ ] Test reconstruction on clean system
- [ ] Document CSN → SQLite mapping strategy

---

## 🔗 Related Documents

- [[CSN-Driven Knowledge Graph]] - CSN as source of truth
- [[Data Abstraction Layers]] - DataSource interface pattern
- [[Module Quality Gate]] - Module structure standards

---

## 📝 Summary

**1. Active Database**: `modules/data_products/database/p2p_sample.db`  
**2. Best Location**: Module-specific (`modules/[name]/database/`)  
**3. Reconstruction**: From SQL scripts (stored in `schema/` folder)  
**4. CSN Compatibility**: YES - generate SQLite DDL from CSN files  
**5. HANA Parity**: Schema structure matches, types mapped

**Key Principle**: Module owns its database, schema versioned in git, binary excluded.