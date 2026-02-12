# Feng Shui False Positives & Tuning Guide

**Version**: 1.0  
**Date**: 2026-02-12  
**Purpose**: Document known false positives to improve Feng Shui detection accuracy

## Overview

Feng Shui's multi-agent system is powerful but can flag legitimate patterns as violations. This document helps tune detection rules to reduce false positives while maintaining quality standards.

---

## False Positive #1: Adapter Pattern Repository Wrapping

### What Feng Shui Flags
**Violation**: "Repository Pattern Violation - Direct import of _HanaRepository"  
**Severity**: CRITICAL  
**Location**: `modules/data_products_v2/repositories/hana_data_product_repository.py:22`

### Why It's a False Positive

**This is Adapter Pattern, not violation**:
```python
# modules/data_products_v2/repositories/hana_data_product_repository.py
from core.repositories._hana_repository import _HanaRepository  # ← Flagged as violation

class HANADataProductRepository(IDataProductRepository):
    """Adapts _HanaRepository to IDataProductRepository interface"""
    
    def __init__(self, host, port, user, password):
        self._repository = _HanaRepository(host, port, user, password)  # ← Necessary wrapping
```

**WHY this is correct**:
1. `HANADataProductRepository` implements **different interface** (`IDataProductRepository`)
2. `_HanaRepository` implements **different interface** (`AbstractRepository`)
3. Adapter Pattern **requires direct wrapping** of adapted class
4. This is NOT bypassing factory - adapter IS the abstraction layer

**Correct Architecture**:
```
Module uses: IDataProductRepository (interface)
      ↓
Adapter implements: HANADataProductRepository
      ↓
Adapter wraps: _HanaRepository (core repository)
      ↓
Core repository implements: AbstractRepository
```

### How to Fix Detection

**Option A**: Whitelist adapter files
```python
# In architect_agent.py _detect_repository_violations()
if 'adapter' in file_path.name.lower() or 'repository' in str(file_path.parent):
    # Skip adapter pattern implementations
    continue
```

**Option B**: Check if class implements different interface
```python
# If wrapping class AND wrapped class have different interfaces → Adapter Pattern (OK)
if self._implements_adapter_pattern(content):
    continue  # Not a violation
```

**Option C**: Document pattern in code
```python
# Add comment Feng Shui can detect
# ADAPTER_PATTERN: Wraps _HanaRepository for IDataProductRepository interface
from core.repositories._hana_repository import _HanaRepository
```

---

## False Positive #2: N+1 Queries in Adapters

### What Feng Shui Flags
**Violation**: "N+1 Query Pattern"  
**Severity**: HIGH  
**Location**: Multiple locations in `hana_data_product_repository.py`, `sqlite_data_product_repository.py`

**Example**:
```python
# Line 77: get_data_products()
for p in products_dict:  # ← Flagged as N+1
    products.append(DataProduct(...))
```

### Why It's a False Positive

**This is NOT an N+1 query - it's in-memory transformation**:
1. `products_dict` already fetched from DB (single query in `_repository.get_data_products()`)
2. Loop is transforming Dict → DataProduct domain models (CPU operation, not DB query)
3. No additional DB calls inside loop

**Actual N+1 pattern looks like**:
```python
# BAD - This IS N+1
products = db.query("SELECT * FROM products")  # 1 query
for p in products:
    details = db.query(f"SELECT * FROM details WHERE product_id={p.id}")  # N queries ❌
```

**Current code is GOOD**:
```python
# GOOD - Single query + in-memory transform
products_dict = self._repository.get_data_products()  # 1 query ✅
for p in products_dict:  # In-memory loop
    products.append(DataProduct(...))  # No DB call ✅
```

### How to Fix Detection

**Option A**: Detect if loop body contains DB calls
```python
# In performance_agent.py _detect_n_plus_one_patterns()
if not self._loop_contains_db_operations(loop_body):
    continue  # In-memory transformation, not N+1
```

**Option B**: Check context (is data pre-fetched?)
```python
# If variable comes from single query outside loop → not N+1
if self._data_prefetched_before_loop(loop_var, loop_start_line):
    continue
```

**Option C**: Whitelist adapter transformations
```python
# If loop is DataProduct/Table/Column construction → transformation, not query
if 'DataProduct(' in loop_body or 'Table(' in loop_body:
    continue  # Domain model construction
```

---

## False Positive #3: Service Locator in Factory Methods

### What Feng Shui Flags
**Violation**: "Service Locator Anti-Pattern - db_path parameter"  
**Severity**: HIGH  
**Location**: `repository_factory.py:36`

**Example**:
```python
def create(source_type: str, db_path: Optional[str] = None):  # ← Flagged
    if source_type == 'sqlite':
        return SQLiteDataProductRepository(db_path)
```

### Why It's a False Positive

**Factory methods NEED config parameters**:
1. Factory Pattern **requires** accepting configuration for object creation
2. `db_path` is **injected from caller**, not fetched from global service locator
3. Factory creates objects based on params → NOT service locator antipattern

**Service Locator antipattern looks like**:
```python
# BAD - Service Locator
def create():
    db_path = ServiceLocator.get('db_path')  # ← Global access ❌
    return SQLiteRepository(db_path)
```

**Current code is Factory Pattern (GOOD)**:
```python
# GOOD - Factory with DI
def create(source_type: str, db_path: Optional[str] = None):  # ← Injected ✅
    return SQLiteDataProductRepository(db_path)  # ← Uses injected param ✅
```

### How to Fix Detection

**Option A**: Distinguish factory parameters from service locator
```python
# In architect_agent.py _detect_service_locator_violations()
if self._is_factory_method(function_name):
    # Factory methods legitimately accept config params
    continue
```

**Option B**: Check if parameter is used (not fetched from global)
```python
# If db_path is function parameter → DI (OK)
# If db_path = ServiceLocator.get() → Service Locator (BAD)
if param_is_function_argument(db_path):
    continue  # Not service locator
```

---

## Summary of Tuning Recommendations

### High Priority (Reduce Noise)
1. ✅ **Whitelist Adapter Pattern** - Don't flag legitimate repository wrapping
2. ✅ **Improve N+1 Detection** - Distinguish DB queries from in-memory loops
3. ✅ **Whitelist Factory Parameters** - Factory config ≠ service locator

### Medium Priority (Future Enhancement)
4. **Context-Aware Analysis** - Consider calling code, not just implementation
5. **Pattern Recognition** - Learn common patterns (Adapter, Factory, Facade)
6. **Confidence Scoring** - Flag high-confidence violations only

### Low Priority (Nice to Have)
7. **Suppression Comments** - Allow `# FENG_SHUI_IGNORE: reason`
8. **Auto-Learning** - Track user accepts/rejects of findings
9. **Suggested Fixes** - Provide code snippets for common violations

---

## How to Apply These Fixes

### Step 1: Update ArchitectAgent
```python
# tools/fengshui/agents/architect_agent.py

def _detect_repository_violations(self, module_path: Path):
    # ADD: Skip adapter pattern files
    if 'adapter' in file_path.stem.lower():
        continue  # Adapter pattern legitimately wraps repositories
```

### Step 2: Update PerformanceAgent
```python
# tools/fengshui/agents/performance_agent.py

def _detect_n_plus_one_patterns(self, module_path: Path):
    # ADD: Check if loop contains DB operations
    if not self._loop_has_query_calls(loop_body):
        continue  # In-memory transformation, not N+1
```

### Step 3: Add Helper Methods
```python
def _loop_has_query_calls(self, code: str) -> bool:
    """Check if loop body contains database query calls"""
    query_patterns = [
        r'\.execute\(', r'\.query\(', r'\.fetchall\(',
        r'\.get\(', r'\.filter\(', r'session\.'
    ]
    return any(re.search(p, code) for p in query_patterns)
```

---

## Testing False Positive Fixes

```bash
# Before: 30 findings (3 CRIT, 8 HIGH)
python -m tools.fengshui.agents.orchestrator modules/data_products_v2

# After tuning: ~15 findings (0 CRIT, 4 HIGH)
# Should eliminate adapter + factory false positives
```

---

## Related Documentation

- [[Repository Pattern Modular Architecture]]
- [[Service Locator Antipattern Solution]]
- [[Cosmic Python Patterns]]

## Version History

- **v1.0** (2026-02-12): Initial documentation of v4.31 analysis findings