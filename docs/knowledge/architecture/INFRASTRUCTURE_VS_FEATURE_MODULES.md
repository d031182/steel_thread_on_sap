# Module Blueprint Requirements

**Date**: 2026-01-30 (Updated 21:40)  
**Context**: Clarified blueprint requirements based on HTTP endpoint presence, not module type

## The Golden Rule

**Blueprint requirement is determined by HTTP endpoints, NOT by module classification.**

### Modules WITH HTTP Endpoints → Blueprint Required

**Any module that exposes REST API endpoints MUST:**
- ✅ Have `backend/api.py` with Flask Blueprint
- ✅ Have `backend.blueprint` config in module.json
- ✅ Export blueprint in backend/__init__.py
- ✅ Be registered in app/app.py via `module_loader.load_blueprint()`

**This applies to BOTH feature AND infrastructure modules!**

### Modules WITHOUT HTTP Endpoints → No Blueprint

**Modules that only provide Python classes/services:**
- ❌ NO `backend/api.py` needed
- ❌ NO blueprint config in module.json
- ❌ NO app.py registration
- ✅ Export classes in backend/__init__.py (for Python imports)

---

## Why HTTP Endpoints Require Blueprints

Flask cannot route HTTP requests to endpoints unless the blueprint is registered:

```python
# Module defines endpoint
@login_manager_api.route('/current-user')
def get_current_user():
    return jsonify(...)

# But Flask doesn't know about it until:
app.register_blueprint(login_manager_api, url_prefix='/api/login-manager')
```

**Without registration** → `GET /api/login-manager/current-user` → **404 Not Found**

---

## Module Classification (For Understanding Only)

Module classification (infrastructure vs feature) describes the **purpose**, not the blueprint requirement:

### Infrastructure Modules
**Purpose**: Provide reusable services/utilities for other modules

**Examples**:
- **WITH HTTP**: `login_manager`, `log_manager` (need blueprint!)
- **WITHOUT HTTP**: `hana_connection`, `sqlite_connection` (no blueprint)

### Feature Modules  
**Purpose**: Provide user-facing functionality

**Examples**:
- **WITH HTTP**: `data_products`, `sql_execution`, `api_playground` (need blueprint!)

**Key Point**: Infrastructure modules can have HTTP endpoints (and thus need blueprints)!

---

## Why This Matters

### Example: login_manager

**Classification**: Infrastructure (provides authentication service)  
**Has HTTP API**: Yes (frontend needs to call it)  
**Needs Blueprint**: YES

```javascript
// Frontend MUST use HTTP to get current user
fetch('/api/login-manager/current-user')

// Browser cannot do this:
// import { get_current_user } from 'modules.login_manager.backend'  ← Impossible!
```

Even though `login_manager` is infrastructure, it needs blueprint because **frontend accesses it via HTTP**.

---

## DI Violations (Unrelated to Blueprints)

### Real Violation
Reaching into implementation internals:
```python
# ❌ BAD: Accessing internal properties
return self.data_source.service.db_path
```

### Not a Violation
Calling public methods on injected dependencies:
```python
# ✅ GOOD: Using public interface
return self.connection.execute_query(sql)
```

## Current Module Inventory

### Modules WITH HTTP Endpoints (Blueprint Required)
| Module | Type | Has backend/api.py | Blueprint Status |
|--------|------|-------------------|------------------|
| api_playground | Feature | ✅ | ✅ Registered |
| csn_validation | Feature | ✅ | ✅ Registered |
| data_products | Feature | ✅ | ✅ Registered |
| sql_execution | Feature | ✅ | ✅ Registered |
| knowledge_graph | Feature | ✅ | ✅ Registered |
| log_manager | Infrastructure | ✅ | ✅ Registered |
| login_manager | Infrastructure | ✅ | ✅ Registered |

**Total: 7 modules with HTTP endpoints**

### Modules WITHOUT HTTP Endpoints (No Blueprint)
| Module | Type | Backend Structure | Python-Only |
|--------|------|-------------------|-------------|
| hana_connection | Infrastructure | Classes only | ✅ Yes |
| sqlite_connection | Infrastructure | Classes only | ✅ Yes |
| feature_manager | Infrastructure | Services only | ✅ Yes |
| debug_mode | Utility | Config/tools | ✅ Yes |

**Total: 4 modules without HTTP endpoints**

---

## Quality Gate Enforcement

The quality gate (`core/quality/module_quality_gate.py`) now properly validates:

1. ✅ If module has `backend/api.py` → Blueprint config REQUIRED
2. ✅ If blueprint exists → MUST be registered in app.py
3. ✅ Prevents 404 errors from missing registration
4. ✅ Works for both infrastructure AND feature modules

## References
- [[Modular Architecture]]
- [[DI_AUDIT_2026-01-29]]
- [[MODULE_SELF_REGISTRATION_FAILURE]]