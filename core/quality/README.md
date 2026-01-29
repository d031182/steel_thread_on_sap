# Module Quality Gate

## Purpose

**Enforces modular architecture principles through automated validation.**

This quality gate ensures every module adheres to:
- ✅ Dependency Injection principles
- ✅ Proper blueprint registration
- ✅ Loose coupling standards
- ✅ Interface-based programming
- ✅ Self-registration capability
- ✅ Complete module structure

## Philosophy

> **"Fail Fast, Fail Clearly"**

A module EITHER:
- ✅ Passes all checks and works completely
- ❌ Fails with clear error explaining what's wrong

**NEVER**:
- ❌ Silently partially works
- ❌ Appears enabled but doesn't function
- ❌ Requires manual debugging to discover issues

## Usage

### Validate Single Module

```bash
python core/quality/module_quality_gate.py [module_name]

# Example
python core/quality/module_quality_gate.py knowledge_graph
```

**Exit codes**:
- `0` = Quality gate PASSED (module ready for production)
- `1` = Quality gate FAILED (module has errors that must be fixed)

### Validate All Modules

```bash
python core/quality/module_quality_gate.py
```

Shows:
- Which modules pass
- Which modules fail
- Specific errors per module

## Validation Checks

### 1. Structure Checks (ERROR level)
- ✅ `module.json` exists
- ✅ `module.json` is valid JSON
- ✅ Required fields present: name, version, description, enabled

### 2. Blueprint Registration (ERROR level)
- ✅ If `backend/` exists → `module.json` MUST have `backend.blueprint`
- ✅ If `backend/` exists → `module.json` MUST have `backend.module_path`
- ✅ `backend/__init__.py` must exist
- ✅ `backend/__init__.py` must export the blueprint
- ✅ Blueprint must be defined in `backend/*.py`

### 3. Dependency Injection (ERROR level)
- ✅ No `.connection` access violations
- ✅ No `.service` access violations
- ✅ No `.db_path` access violations
- ✅ No `hasattr()` implementation checks

### 4. Loose Coupling (ERROR level)
- ✅ No direct imports from other modules
- ✅ Uses dependency injection for external dependencies

### 5. Code Quality (WARNING level)
- ⚠️ No hardcoded absolute paths
- ⚠️ No global state/singletons
- ⚠️ Uses interfaces from `core.interfaces`
- ⚠️ Has `README.md` documentation
- ⚠️ `module.json` has recommended fields (category, author, dependencies)

## Integration Points

### CI/CD Pipeline (Recommended)

```bash
# Pre-commit hook
python core/quality/module_quality_gate.py [changed_module]

# CI build step
python core/quality/module_quality_gate.py  # Validate all
```

### ModuleLoader Integration (Future)

```python
# In ModuleLoader.__init__():
from core.quality.module_quality_gate import ModuleQualityGate

for module in discovered_modules:
    gate = ModuleQualityGate(module.path)
    passed, results = gate.validate()
    
    if not passed:
        raise ModuleValidationError(
            f"Module '{module.name}' failed quality gate. "
            f"Run: python core/quality/module_quality_gate.py {module.name}"
        )
```

## Example Output

### Passing Module

```
================================================================================
MODULE QUALITY GATE: knowledge_graph
================================================================================

RESULTS:
  PASSED: 12
  WARNINGS: 0
  ERRORS: 0

================================================================================
QUALITY GATE: PASSED
================================================================================
```

### Failing Module

```
================================================================================
MODULE QUALITY GATE: api_playground
================================================================================

RESULTS:
  PASSED: 11
  WARNINGS: 0
  ERRORS: 1

ERRORS (Must Fix):
  1. module.json missing 'backend.blueprint' config

================================================================================
QUALITY GATE: FAILED
================================================================================
```

## Validation Rules

### ERROR Level (MUST Fix)
Blocks module from loading. Module is non-functional until fixed.

**Examples**:
- Missing `module.json`
- Missing blueprint registration
- DI violations (.connection, .service access)
- Direct imports of other modules

### WARNING Level (SHOULD Fix)
Module works but doesn't follow best practices. Should be addressed.

**Examples**:
- No README.md
- Hardcoded paths
- Missing recommended module.json fields

### INFO Level
Informational only. Shows what was checked.

## Benefits

### For Developers
- ✅ Clear checklist of requirements
- ✅ Fast feedback on violations
- ✅ Prevents hours of debugging
- ✅ Enforces consistency

### For Architecture
- ✅ Guarantees modular principles followed
- ✅ Prevents technical debt accumulation
- ✅ Maintains system quality over time
- ✅ Makes architecture real, not theoretical

### For Users
- ✅ Modules work or fail obviously
- ✅ No silent partial failures
- ✅ Consistent, predictable behavior
- ✅ Trust in the system

## Current Module Status

As of 2026-01-29:
- ✅ **knowledge_graph**: PASSED (12/12 checks)
- ❌ **api_playground**: FAILED (missing blueprint config)
- ❌ **data_products**: FAILED (missing blueprint config)
- ❌ **sql_execution**: FAILED (missing blueprint config)
- ❌ **log_manager**: FAILED (missing blueprint config)
- ❌ **feature_manager**: FAILED (missing blueprint config)
- ❌ **hana_connection**: FAILED (missing blueprint config)
- ❌ **sqlite_connection**: FAILED (missing blueprint config)
- ❌ **csn_validation**: FAILED (missing blueprint config)

**8 out of 10 modules need fixes** to pass quality gate.

## Next Steps

### Option 1: Fix All Modules Now
Run quality gate on each module, fix issues, commit

### Option 2: Add to CI/CD
Integrate into pre-commit hooks and build pipeline

### Option 3: Phased Approach
Fix critical modules first (those with user-facing APIs),
then address infrastructure modules

## Related Documentation

- [[MODULE_SELF_REGISTRATION_FAILURE]] - Why this tool was created
- [[DI_AUDIT_2026-01-29]] - DI violations audit
- `core/README.md` - Core infrastructure overview
- `.clinerules` - Development standards

---

**The quality gate exists to make architectural principles REAL, not just theoretical.**