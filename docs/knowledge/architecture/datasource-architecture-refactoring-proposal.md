# DataSource Architecture Refactoring Proposal

**Date**: 2026-02-07  
**Status**: PROPOSAL - Awaiting User Approval  
**Priority**: CRITICAL - "Heart Surgery" Architecture Change

---

## 🎯 Problem Statement

**Current Issues**:
1. ❌ `sqlite_connection` and `hana_connection` modules are **exposed globally** via `app.py`
2. ❌ Other modules can access these connection modules directly (breaks encapsulation)
3. ❌ Tight coupling: `app.sqlite_data_source` → `SQLiteDataSource` → exposes `get_connection()`
4. ❌ No clear boundary: Connection management leaks outside DataSource layer

**User's Architecture Requirements**:
> "HANA Cloud and SQLite modules should NOT be exposed to others, except for DataSource."
> "HANA Cloud DataSource and SQLiteDataSource are basically sub-modules of DataSource."
> "We could actually merge HANA Cloud DataSource with HANA Connection and SQLiteDataSource with SQLiteConnection."

---

## 📚 Industry Best Practices (Perplexity Research)

### Repository Pattern (Recommended for Our Use Case)

**What It Is**:
- **Collection-like interface** for domain entities (add, get, list, query)
- **Hides database specifics** from business logic
- **Domain-Driven Design (DDD)** pattern for persistence abstraction
- **Multi-backend support** via adapter pattern (SQLite dev → HANA prod)

**Key Benefits**:
- ✅ Full decoupling: Business layer sees "in-memory collections"
- ✅ Easy testing: Mock `FakeRepository` without real DB
- ✅ Swappable backends: SQLAlchemy dialects (SQLite/HANA)
- ✅ Centralized queries: <50 LOC per entity repository
- ✅ Dependency Injection: Request-scoped sessions in Flask

**Industry Consensus**:
> "Repository pattern provides higher-level abstraction over Data Access Layer by encapsulating data operations for specific domain entities, decoupling business logic from persistence details." - Cosmic Python, GraphApp.AI

### Repository vs Generic DAL

| Aspect | Repository Pattern | Generic DAL (Current) |
|--------|-------------------|----------------------|
| Abstraction | Domain-entity focused | Query/ORM focused |
| Decoupling | Full (collections) | Partial (exposes SQL) |
| Testing | Mock interfaces easily | Requires DB mocks |
| Multi-Backend | Swap adapters cleanly | Often ties to drivers |

---

## 🏗️ Proposed Architecture

### Option 1: Repository Pattern (RECOMMENDED ⭐)

**Structure**:
```
core/
└── repositories/
    ├── __init__.py
    ├── base.py              # AbstractRepository interface
    ├── sqlite_repository.py # SQLite implementation (internal)
    └── hana_repository.py   # HANA implementation (internal)

app/app.py:
    repository = get_repository(backend='sqlite')  # Factory pattern
    app.repository = repository  # Single public interface

modules/p2p_dashboard/:
    data_source = current_app.repository  # Access via DI
```

**Key Changes**:
1. ✅ **Single Public Interface**: `AbstractRepository` (or `DataSource` interface)
2. ✅ **Private Implementations**: `sqlite_repository` and `hana_repository` are internal
3. ✅ **Factory Pattern**: `get_repository(backend)` creates correct implementation
4. ✅ **No Exposed Modules**: Connection modules completely hidden
5. ✅ **Dependency Injection**: Repository injected via `current_app.repository`

**Benefits**:
- ✅ **Industry Standard**: Used by DDD practitioners, Cosmic Python book
- ✅ **Clean Separation**: Business logic never sees connections
- ✅ **Easy Testing**: `FakeRepository` for unit tests
- ✅ **Multi-Backend**: Config-driven (no code changes)
- ✅ **Scalable**: Add PostgreSQL/MongoDB without changing consumers

---

### Option 2: Unified DataSource with Private Adapters

**Structure**:
```
core/
└── data_access/
    ├── __init__.py          # Exports only DataSource interface
    ├── data_source.py       # Main DataSource facade
    ├── _adapters/           # Private adapters (underscore prefix)
    │   ├── __init__.py
    │   ├── _sqlite_adapter.py
    │   └── _hana_adapter.py

app/app.py:
    data_source = DataSource(backend='sqlite')
    app.data_source = data_source

modules/:
    # ONLY access via app.data_source (no direct adapter access)
```

**Key Changes**:
1. ✅ **Single DataSource Facade**: One public class, multiple internal adapters
2. ✅ **Private Adapters**: Underscore prefix signals "internal use only"
3. ✅ **No Module Exposure**: `sqlite_connection`/`hana_connection` become `_adapters`
4. ✅ **Factory Inside DataSource**: `DataSource(backend)` selects adapter internally

**Benefits**:
- ✅ **Simpler**: Less moving parts than full Repository pattern
- ✅ **Python Convention**: Underscore prefix for private modules
- ✅ **Encapsulation**: Adapters hidden from other modules
- ✅ **Minimal Refactor**: Closer to current structure

---

### Option 3: Current Structure with Access Control (Minimal Change)

**Structure** (Keep current, add enforcement):
```
modules/
├── sqlite_connection/    # Keep as module
└── hana_connection/      # Keep as module

core/interfaces/data_source.py:
    # Add warning docstring: "DO NOT import connection modules directly"

app/app.py:
    # Keep current exposure but add Feng Shui rule
```

**Key Changes**:
1. ✅ **Feng Shui Validation**: Detect direct imports of connection modules
2. ✅ **Documentation**: Warn developers not to access connections
3. ✅ **Convention Over Code**: Rely on team discipline

**Benefits**:
- ✅ **Zero Refactor**: No code changes needed
- ✅ **Fast Implementation**: Just add validation rules

**Drawbacks**:
- ❌ **Not Enforceable**: Conventions can be violated
- ❌ **Not Industry Standard**: Relies on discipline, not architecture
- ❌ **Leak Potential**: Modules still exposed globally

---

## 📊 Comparison Matrix

| Criterion | Repository Pattern | Unified DataSource | Current + Rules |
|-----------|-------------------|-------------------|----------------|
| **Encapsulation** | ✅✅✅ Perfect | ✅✅ Good | ❌ Weak |
| **Industry Standard** | ✅✅✅ Yes (DDD) | ✅✅ Yes (Facade) | ❌ No |
| **Testability** | ✅✅✅ Excellent | ✅✅ Good | ✅ Fair |
| **Multi-Backend** | ✅✅✅ Native | ✅✅ Native | ✅ Supported |
| **Refactor Effort** | ⚠️ Medium (2-3h) | ⚠️ Low (1-2h) | ✅ Minimal |
| **Scalability** | ✅✅✅ Excellent | ✅✅ Good | ⚠️ Limited |
| **Learning Curve** | ⚠️ Medium | ✅ Low | ✅ None |
| **Your Requirements** | ✅✅✅ Fully Met | ✅✅ Fully Met | ❌ Partially Met |

**Scoring**: ✅✅✅ Excellent, ✅✅ Good, ✅ Fair, ⚠️ Moderate, ❌ Poor

---

## 🎯 Recommendation

### **Option 1: Repository Pattern** ⭐ RECOMMENDED

**Why**:
1. ✅ **Industry Best Practice**: Validated by DDD community, Cosmic Python
2. ✅ **Fully Meets Requirements**: Connection modules completely hidden
3. ✅ **Future-Proof**: Add new backends without touching consumers
4. ✅ **Testing Excellence**: Mock repositories trivially easy
5. ✅ **Clean Architecture**: Business logic decoupled from persistence

**Implementation Plan**:
1. Create `core/repositories/` directory
2. Define `AbstractRepository` interface (same as current `DataSource`)
3. Move `SQLiteDataSource` → `SqliteRepository` (private)
4. Move `HANADataSource` → `HanaRepository` (private)
5. Create `RepositoryFactory.get(backend)` factory method
6. Update `app.py` to use factory
7. Update all modules to use `current_app.repository`
8. Mark old connection modules as deprecated
9. Run Gu Wu tests (ensure 100% passing)
10. Commit with detailed git tag

**Estimated Time**: 2-3 hours (includes testing)

---

## 🤔 Questions for User

1. **Preference**: Which option do you prefer? (1, 2, or 3)
2. **Naming**: Keep `DataSource` name or rename to `Repository`?
3. **Migration**: Move connection modules inside `core/` or delete entirely?
4. **Backward Compat**: Keep old modules as deprecated, or clean break?
5. **Timeline**: When to implement? (Now vs after current tasks)

---

## 📝 Implementation Details (Option 1 - If Approved)

### Step 1: Create Repository Interface

```python
# core/repositories/base.py
from abc import ABC, abstractmethod
from typing import List, Dict, Optional

class AbstractRepository(ABC):
    """
    Repository interface for data access.
    
    Consumers should ONLY use this interface, never concrete implementations.
    """
    
    @abstractmethod
    def get_data_products(self) -> List[Dict]: ...
    
    @abstractmethod
    def execute_query(self, sql: str, params: tuple = None) -> Dict: ...
    
    # ... other methods from current DataSource interface
```

### Step 2: Concrete Implementations (Private)

```python
# core/repositories/_sqlite_repository.py (underscore = private)
from .base import AbstractRepository

class _SqliteRepository(AbstractRepository):
    """Private SQLite implementation - DO NOT import directly."""
    
    def __init__(self, db_path: str):
        self._db_path = db_path
        self._connection = None  # Managed internally
    
    def execute_query(self, sql: str, params: tuple = None) -> Dict:
        # Implementation here (current SQLiteDataSource logic)
        pass
```

### Step 3: Factory Pattern

```python
# core/repositories/__init__.py
from .base import AbstractRepository
from ._sqlite_repository import _SqliteRepository
from ._hana_repository import _HanaRepository

def create_repository(backend: str, **config) -> AbstractRepository:
    """
    Factory for creating repository instances.
    
    Args:
        backend: 'sqlite' or 'hana'
        **config: Backend-specific configuration
    
    Returns:
        Repository instance (concrete type hidden)
    """
    if backend == 'sqlite':
        return _SqliteRepository(db_path=config['db_path'])
    elif backend == 'hana':
        return _HanaRepository(**config)
    else:
        raise ValueError(f"Unknown backend: {backend}")

# ONLY export interface and factory
__all__ = ['AbstractRepository', 'create_repository']
```

### Step 4: Update app.py

```python
# app/app.py
from core.repositories import create_repository, AbstractRepository

# Create repository (hidden implementation)
repository: AbstractRepository = create_repository(
    backend='sqlite',
    db_path='database/p2p_data_products.db'
)

# Inject into app
app.repository = repository

# Modules access via current_app.repository
```

### Step 5: Update Modules

```python
# modules/p2p_dashboard/backend/__init__.py
from flask import current_app

# Get repository via DI (no knowledge of SQLite/HANA)
repository = current_app.repository
kpi_service = KPIService(repository)
```

---

## 🏷️ Related Documents

- [[P2P Dashboard Clean DI Architecture]] - Current v4.4 architecture
- [[Modular Architecture]] - Module structure standards
- [[DataSource Interface]] - Current interface definition
- [[Repository Pattern]] - DDD best practices (to be created if approved)

---

**Awaiting User Decision**: Please review options and provide feedback! 🙏