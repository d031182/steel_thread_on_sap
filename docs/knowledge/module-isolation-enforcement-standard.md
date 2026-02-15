# Module Isolation Enforcement Standard

**Status**: ✅ ACTIVE STANDARD  
**Version**: 1.0  
**Date**: February 15, 2026  
**Enforcement**: Automated via Feng Shui Module Isolation Agent

---

## Executive Summary

**CRITICAL RULE**: Modules MUST NEVER import from each other directly.

All inter-module communication MUST use:
1. **`core/interfaces`** - Shared abstractions (Python)
2. **`app_v2/static/js/interfaces`** - Shared contracts (JavaScript)
3. **Dependency Injection** - Constructor injection via interfaces
4. **EventBus** - Publish/subscribe for loose coupling (frontend)

This is **industry standard** (Hexagonal Architecture, Clean Architecture, SOLID).

---

## The Rule (Zero Tolerance)

### ❌ FORBIDDEN - Direct Module Imports

```python
# modules/ai_assistant/backend/services/agent_service.py
from modules.data_products_v2.backend.services import DataProductsService  # ❌ VIOLATION

class AgentService:
    def __init__(self):
        self.data_service = DataProductsService()  # ❌ Tight coupling
```

**Problems**:
- ❌ Tight coupling (can't change one without breaking the other)
- ❌ Circular dependencies
- ❌ Can't test in isolation
- ❌ Can't deploy independently
- ❌ Violates SOLID principles

### ✅ REQUIRED - Interface-Based Communication

```python
# 1. Define interface in core/interfaces/data_product_repository.py
class IDataProductRepository:
    """Interface for data product access"""
    def get_products(self) -> List[DataProduct]:
        pass

# 2. Implementation in modules/data_products_v2/
class SqliteDataProductRepository(IDataProductRepository):
    def get_products(self) -> List[DataProduct]:
        return self.db.query("SELECT * FROM products")

# 3. Consumer depends on INTERFACE in modules/ai_assistant/
class AgentService:
    def __init__(self, data_repo: IDataProductRepository):  # ✅ Depends on interface
        self.data_repo = data_repo
    
    def get_available_data(self):
        return self.data_repo.get_products()

# 4. Wire in server.py (DI Container)
from core.interfaces.data_product_repository import IDataProductRepository
from modules.data_products_v2.repositories import SqliteDataProductRepository
from modules.ai_assistant.backend.services import AgentService

data_repo: IDataProductRepository = SqliteDataProductRepository()
agent_service = AgentService(data_repo)  # ✅ Inject via constructor
```

**Benefits**:
- ✅ Loose coupling
- ✅ Easy to test (inject mocks)
- ✅ Easy to swap implementations
- ✅ No circular dependencies
- ✅ Follows SOLID principles

---

## Enforcement Mechanisms

### 1. Feng Shui Module Isolation Agent (AUTOMATED)

```bash
# Run analysis on all modules
python -m tools.fengshui analyze --check=module-isolation

# Or analyze specific module
python -m tools.fengshui analyze --module ai_assistant --check=module-isolation
```

**What it detects**:
- `from modules.other_module import ...`
- `import modules.other_module`

**Output example**:
```
❌ CRITICAL: modules/ai_assistant/backend/services/agent_service.py:285
   Cross-module import: 'ai_assistant' imports from 'data_products_v2'
   
   Fix:
   1. Create interface in core/interfaces/
   2. Have 'data_products_v2' implement interface
   3. Inject interface via constructor in 'ai_assistant'
   4. Wire dependency in server.py (DI container)
```

### 2. Python Import Hooks (RUNTIME - Optional)

For **strict enforcement at runtime**, add to `server.py`:

```python
import sys
import importlib.abc

class ModuleImportGuard(importlib.abc.MetaPathFinder):
    """Prevent cross-module imports at runtime"""
    
    def find_spec(self, fullname, path, target=None):
        if fullname.startswith('modules.') and '.' in fullname[8:]:
            parts = fullname.split('.')
            importing_module = parts[1]
            
            frame = sys._getframe(1)
            current_file = frame.f_globals.get('__file__', '')
            
            if 'modules/' in current_file:
                current_module = current_file.split('modules/')[1].split('/')[0]
                
                if current_module != importing_module:
                    raise ImportError(
                        f"VIOLATION: Module '{current_module}' cannot import from '{importing_module}'. "
                        f"Use core/interfaces with DI instead."
                    )
        
        return None

# Install guard
sys.meta_path.insert(0, ModuleImportGuard())
```

### 3. Pre-commit Hook (GIT)

```bash
# .git/hooks/pre-commit
#!/bin/bash

echo "Checking for cross-module imports..."

for file in $(git diff --cached --name-only --diff-filter=ACM | grep '\.py$'); do
    if [[ $file == modules/* ]]; then
        module=$(echo $file | cut -d'/' -f2)
        violations=$(grep -E "from modules\\.(?!${module})" "$file" | grep -v "^#")
        
        if [[ ! -z "$violations" ]]; then
            echo "❌ VIOLATION in $file:"
            echo "$violations"
            exit 1
        fi
    fi
done

echo "✅ No cross-module imports"
exit 0
```

### 4. CI/CD Quality Gate

```yaml
# .github/workflows/quality-gate.yml
- name: Module Isolation Check
  run: |
    python -m tools.fengshui analyze --check=module-isolation --strict
    if [ $? -ne 0 ]; then
      echo "❌ Module isolation violations detected"
      exit 1
    fi
```

---

## Python Language-Level Enforcement

### Q: Can Python prevent imports programmatically?

**Answer**: Yes, but with limitations. Here are the options:

### Option 1: Module-Level `__all__` (Weak Protection)

```python
# modules/data_products_v2/__init__.py
__all__ = []  # Export nothing at module level

# This won't prevent: from modules.data_products_v2.backend.services import X
# Only prevents: from modules.data_products_v2 import X
```

**Effectiveness**: ⭐ (1/5) - Easy to bypass

### Option 2: Import Hooks (Strong Protection)

```python
# Install in server.py (shown above)
sys.meta_path.insert(0, ModuleImportGuard())
```

**Effectiveness**: ⭐⭐⭐⭐ (4/5) - Catches at runtime, but after load

### Option 3: Private Classes/Functions (Weak Protection)

```python
# modules/data_products_v2/backend/services/_internal_service.py
class _InternalService:  # Leading underscore = "private"
    pass

# This is CONVENTION only - Python doesn't enforce it
```

**Effectiveness**: ⭐ (1/5) - Convention, not enforcement

### Option 4: `sys.modules` Manipulation (Extreme)

```python
# In module __init__.py
import sys

# Remove module from sys.modules after import
# This prevents further imports
del sys.modules['modules.data_products_v2.backend.services']
```

**Effectiveness**: ⭐⭐ (2/5) - Breaks legitimate uses

### ✅ RECOMMENDED: Feng Shui Agent + Import Hooks

**Best practice**: Use **multiple layers**:

1. **Feng Shui Agent** (static analysis) - Catches violations before runtime
2. **Import Hooks** (runtime guard) - Prevents accidental violations
3. **Pre-commit Hook** (developer workflow) - Catches before commit
4. **CI/CD Gate** (deployment pipeline) - Final safety net

**This gives 99.9% protection** without breaking legitimate module internals.

---

## Current Violations (Found by Agent)

As of Feb 15, 2026, we have **2 violations**:

```
1. modules/ai_assistant/backend/services/agent_service.py:285
   'ai_assistant' imports from 'data_products_v2'
   
2. modules/ai_assistant/backend/services/agent_service.py:319
   'ai_assistant' imports from 'data_products_v2'
```

**Action Required**: These MUST be fixed by:
1. Creating `IDataProductRepository` interface in `core/interfaces/`
2. Having ai_assistant depend on interface
3. Injecting implementation via DI in `server.py`

---

## Why This Matters

### Industry Standards
- ✅ **Hexagonal Architecture** (Alistair Cockburn)
- ✅ **Clean Architecture** (Robert C. Martin)
- ✅ **SOLID Principles** (Dependency Inversion)
- ✅ **Micro-services** (Bounded Contexts)

### Real-World Benefits
- ✅ Netflix: Modular deployments
- ✅ Amazon: Independent team ownership
- ✅ Google: Hermetic builds
- ✅ Microsoft: Plugin architectures

### Our Benefits
- ✅ **Test in isolation** - Mock interfaces, no real dependencies
- ✅ **Deploy independently** - Change one module without touching others
- ✅ **Team autonomy** - Teams own modules, coordinate via interfaces
- ✅ **Swap implementations** - SQLite → HANA without changing consumers

---

## Quick Reference

### ✅ DO
- Define interfaces in `core/interfaces/`
- Depend on interfaces via constructor injection
- Wire dependencies in `server.py`
- Use EventBus for loosely-coupled events

### ❌ DON'T
- Import from `modules.other_module`
- Use Service Locator pattern
- Access other module's internals directly
- Skip DI in favor of "convenience"

---

## Related Standards

- [[Module Federation Standard]] - Module structure & naming
- [[Configuration-Based Dependency Injection]] - DI patterns
- [[Service Locator Antipattern Solution]] - Why Service Locator is wrong

---

## Approval

**Approved By**: User  
**Date**: February 15, 2026  
**Status**: ✅ ACTIVE STANDARD  
**Enforcement**: MANDATORY (automated checks)

---

**End of Document**