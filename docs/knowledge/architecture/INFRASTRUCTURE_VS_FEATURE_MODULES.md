# Infrastructure vs Feature Modules

**Date**: 2026-01-30  
**Context**: Quality gate analysis revealed different module types require different validation rules

## Module Types

### Feature Modules
Modules that provide REST API endpoints for application features.

**Requirements**:
- ✅ `backend.blueprint` in module.json
- ✅ Blueprint exported in backend/__init__.py  
- ✅ Blueprint defined in backend/api.py
- ✅ Self-register with Flask app

**Examples**: `feature_manager`, `data_products`, `sql_execution`, `api_playground`, `knowledge_graph`

### Infrastructure Modules
Modules that provide classes, services, or utilities (not REST endpoints).

**Requirements**:
- ✅ `structure.backend` in module.json
- ✅ Classes exported in backend/__init__.py
- ❌ NO blueprint needed (provide classes, not endpoints)
- ❌ NO self-registration (consumed by other modules)

**Examples**: `log_manager`, `hana_connection`, `sqlite_connection`

## Quality Gate False Positives

The quality gate currently expects ALL modules with backend/ to have blueprints. This is **incorrect** for infrastructure modules.

### False Positive: "No Blueprint definition found"
- **For infrastructure modules**: This is EXPECTED ✅
- **For feature modules**: This is an ERROR ❌

### False Positive: "DI violations - Direct .connection access"
- Pattern match: Detects `.connection`, `.service`, `.db_path` in code
- **Real violation**: Accessing implementation internals (e.g., `data_source.service.db_path`)
- **False positive**: Calling methods on injected dependencies (e.g., `self.connection.execute_query()`)

**Example of CORRECT DI**:
```python
class HANADataSource:
    def __init__(self, connection: HANAConnection):
        self.connection = connection  # ✅ Dependency injection
    
    def query_table(self, schema, table):
        return self.connection.execute_query(sql)  # ✅ Calling public method
```

**Example of DI VIOLATION**:
```python
class DataProductService:
    def __init__(self, data_source: DataSource):
        self.data_source = data_source
    
    def get_db_path(self):
        return self.data_source.service.db_path  # ❌ Reaching into internals
```

## Current Module Status

| Module | Type | Blueprint | DI | Status |
|--------|------|-----------|-----|--------|
| feature_manager | Feature | ✅ | ✅ | PASS |
| data_products | Feature | ✅ | ✅ | PASS |
| sql_execution | Feature | ✅ | ✅ | PASS |
| api_playground | Feature | ✅ | ✅ | PASS |
| csn_validation | Feature | ✅ | ✅ | PASS |
| knowledge_graph | Feature | ✅ | ✅ | PASS |
| log_manager | Infrastructure | N/A | ✅ | PASS |
| hana_connection | Infrastructure | N/A | ✅ | PASS |
| sqlite_connection | Infrastructure | N/A | ✅ | PASS |

**Result**: All 9 modules are architecturally compliant ✅

## Recommendations

1. **Update quality gate** to distinguish module types
2. **Skip blueprint checks** for infrastructure modules
3. **Refine DI violation detection** to avoid false positives
4. **Document module type** in module.json (`"type": "feature"|"infrastructure"`)

## References
- [[Modular Architecture]]
- [[DI_AUDIT_2026-01-29]]
- [[MODULE_SELF_REGISTRATION_FAILURE]]