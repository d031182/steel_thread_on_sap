# Interface Segregation & SQL Execution Pattern

## Industry Standard Solution

**Problem**: Module needs to execute raw SQL against multiple backends (SQLite, HANA), but interface only supports structured queries.

**Best Practice**: **Interface Segregation Principle (ISP)** from SOLID

---

## ✅ Recommended Solution: Extend Interface with Optional Capability

### Pattern: Capability Interface Extension

```python
# core/interfaces/data_product_repository.py

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional

class IDataProductRepository(ABC):
    """Base interface - Required methods for ALL implementations"""
    
    @abstractmethod
    def get_data_products(self) -> List[DataProduct]:
        pass
    
    @abstractmethod
    def query_table_data(self, product_name: str, table_name: str, ...) -> Dict[str, Any]:
        """Structured query - ALL backends MUST support"""
        pass


class ISQLExecutor(ABC):
    """Optional capability - Only for backends that support raw SQL"""
    
    @abstractmethod
    def execute_sql(self, sql: str) -> Dict[str, Any]:
        """Execute raw SQL query (SELECT only)"""
        pass


class IDataProductRepositoryWithSQL(IDataProductRepository, ISQLExecutor):
    """Composite interface for backends with SQL support"""
    pass
```

### Implementation

```python
# SQLite Repository - Supports raw SQL
class SQLiteDataProductRepository(IDataProductRepositoryWithSQL):
    def get_data_products(self): ...
    def query_table_data(self, ...): ...
    
    def execute_sql(self, sql: str) -> Dict[str, Any]:
        # Direct SQL execution via SQLite connection
        conn = sqlite3.connect(self.db_path)
        cursor = conn.execute(sql)
        ...


# HANA Repository - Structured queries only
class HANADataProductRepository(IDataProductRepository):
    def get_data_products(self): ...
    def query_table_data(self, ...): ...
    
    # NO execute_sql() - This backend doesn't support it!
```

### Consumer Usage (AI Agent)

```python
# Agent checks capability at runtime
async def execute_sql_impl(ctx, sql_query: str):
    repository = ctx.deps.data_product_repository
    
    # Check if repository supports raw SQL
    if isinstance(repository, ISQLExecutor):
        return repository.execute_sql(sql_query)
    else:
        return {
            "success": False,
            "error": f"Current datasource ({type(repository).__name__}) does not support raw SQL. Use structured queries instead."
        }
```

---

## 🎯 Why This is Best Practice

### 1. **Interface Segregation Principle (SOLID)**
   - Don't force implementations to provide methods they can't support
   - Optional capabilities via separate interfaces
   - Clients depend only on interfaces they use

### 2. **Liskov Substitution Principle (SOLID)**
   - All `IDataProductRepository` implementations work correctly
   - Optional `ISQLExecutor` adds capability without breaking base contract
   - Type-safe runtime capability checking

### 3. **Open/Closed Principle (SOLID)**
   - Open for extension (add ISQLExecutor)
   - Closed for modification (base interface unchanged)

---

## 📚 Industry Examples

### Example 1: Java JDBC (Connection Interface)

```java
// Base interface - All connections have
interface Connection {
    Statement createStatement();
    PreparedStatement prepareStatement(String sql);
}

// Optional capability - Only some connections have
interface Wrapper {
    <T> T unwrap(Class<T> iface);
    boolean isWrapperFor(Class<?> iface);
}

// Check capability at runtime
if (connection.isWrapperFor(OracleConnection.class)) {
    OracleConnection oracle = connection.unwrap(OracleConnection.class);
    oracle.setDefaultRowPrefetch(100); // Oracle-specific
}
```

### Example 2: Python Collections (Duck Typing)

```python
# Check capability at runtime
if hasattr(obj, '__iter__'):
    for item in obj:
        process(item)
else:
    process_single(obj)
```

### Example 3: C# IDisposable Pattern

```csharp
// Optional capability interface
interface IDisposable {
    void Dispose();
}

// Consumer checks before using
if (obj is IDisposable disposable) {
    disposable.Dispose();
}
```

---

## 🔧 Implementation Plan

### Phase 1: Add Interface (No Breaking Changes)

```python
# core/interfaces/data_product_repository.py

class ISQLExecutor(ABC):
    """Optional SQL execution capability"""
    @abstractmethod
    def execute_sql(self, sql: str) -> Dict[str, Any]:
        pass
```

### Phase 2: Update SQLite Repository

```python
class SQLiteDataProductRepository(IDataProductRepository, ISQLExecutor):
    def execute_sql(self, sql: str) -> Dict[str, Any]:
        # Implementation
        pass
```

### Phase 3: Update AI Agent

```python
if isinstance(repository, ISQLExecutor):
    return repository.execute_sql(sql)
else:
    return {"error": "Backend does not support raw SQL"}
```

### Phase 4: Future - Add to HANA (Optional)

```python
class HANADataProductRepository(IDataProductRepository, ISQLExecutor):
    def execute_sql(self, sql: str) -> Dict[str, Any]:
        # Use hdbcli to execute SQL
        pass
```

---

## ⚖️ Alternative Approaches (Not Recommended)

### ❌ Antipattern 1: Force All Implementations

```python
class IDataProductRepository(ABC):
    @abstractmethod
    def execute_sql(self, sql: str):
        pass

# PROBLEM: HANA repo must throw NotImplementedError
class HANARepo(IDataProductRepository):
    def execute_sql(self, sql: str):
        raise NotImplementedError("HANA doesn't support raw SQL")
```

**Why Bad**: Violates Liskov Substitution Principle (LSP)

### ❌ Antipattern 2: Return Type Checking

```python
def process(repo: Union[SQLiteRepo, HANARepo]):
    if isinstance(repo, SQLiteRepo):
        repo.execute_sql(...)
    elif isinstance(repo, HANARepo):
        repo.query_table_data(...)
```

**Why Bad**: Tight coupling to concrete classes, not interfaces

### ❌ Antipattern 3: Try/Except

```python
try:
    repo.execute_sql(sql)
except AttributeError:
    # Fallback
    pass
```

**Why Bad**: Uses exceptions for control flow, error-prone

---

## 📊 Comparison

| Approach | SOLID | Type Safety | Runtime Check | Breaking Change |
|----------|-------|-------------|---------------|-----------------|
| **Interface Segregation** ✅ | ✅ Yes | ✅ Yes | ✅ isinstance() | ❌ No |
| Force Implementation ❌ | ❌ Violates LSP | ✅ Yes | ❌ Must call | ✅ Yes |
| Type Checking ❌ | ❌ Violates OCP | ⚠️ Weak | ✅ isinstance() | ❌ No |
| Try/Except ❌ | ⚠️ Okay | ❌ No | ❌ Runtime error | ❌ No |

---

## 🎓 Key Takeaways

1. **Use Interface Segregation** for optional capabilities
2. **Check capability at runtime** with `isinstance()`
3. **Never force** unsupported methods on implementations
4. **Follow SOLID principles** for maintainable architecture
5. **Type hints help** IDEs catch errors early

---

## 📖 References

- **SOLID Principles**: Robert C. Martin, "Clean Architecture"
- **Interface Segregation**: Martin Fowler, "Refactoring"
- **Python Protocols**: PEP 544 (Structural Subtyping)
- **Java Patterns**: "Effective Java" by Joshua Bloch
- **Design Patterns**: Gang of Four (Adapter, Strategy patterns)

---

## ✅ Summary

**Best Practice**: Extend interface with optional `ISQLExecutor` capability

**Why**: Follows SOLID principles, no breaking changes, type-safe

**Implementation**: 30 minutes (add interface + update SQLite repo)

**Result**: Clean architecture with proper module isolation