# GoF Pattern Enhancement for Feng Shui ArchitectAgent

**Status**: 📋 PROPOSED (Feb 13, 2026)  
**Depends On**: Feng Shui ArchitectAgent v4.11 ✅  
**Estimated Effort**: 2-3 hours  
**Priority**: P2 (Enhancement, not critical)

## Overview

Enhance Feng Shui ArchitectAgent to **contextually suggest GoF design patterns** when detecting architecture violations, without building a separate tracking system.

## Philosophy

**"Don't track patterns. Suggest them where they solve problems."**

---

## Current State (ArchitectAgent v4.11)

✅ **Existing Detectors**:
1. DI Violations (`.connection`, `.service`, `.db_path`)
2. SOLID Violations (Large classes >500 LOC)
3. Repository Pattern violations
4. Facade Pattern violations
5. Backend Structure violations
6. Unit of Work violations
7. Service Layer violations
8. Service Locator anti-pattern
9. Stale Reference anti-pattern

**What's Missing**: Contextual GoF pattern suggestions

---

## Proposed Enhancement

### Goal

When ArchitectAgent finds a violation, **suggest the appropriate GoF pattern** to fix it.

### Approach: Pattern → Violation Mapping

**Not a new detector**. Enhance **existing detectors** with GoF suggestions.

---

## Implementation Design

### 1. Violation → GoF Pattern Mapping

| Existing Violation | GoF Pattern Suggestion | Why It Helps |
|--------------------|------------------------|--------------|
| Direct `.connection` access | **Factory Pattern** | Encapsulate complex object creation |
| Hardcoded instantiation | **Factory Pattern** | Single point for creation logic |
| Large classes (>500 LOC) | **Strategy Pattern** | Extract algorithms to separate classes |
| Tight coupling | **Adapter Pattern** | Interface-based decoupling |
| Complex conditional logic | **Strategy Pattern** | Replace if/else with polymorphism |
| Multiple responsibilities | **Facade Pattern** | Simplify complex subsystem |
| Direct database calls | **Adapter Pattern** | Wrap external dependencies |
| Event handling scattered | **Observer Pattern** | Centralize event distribution |
| Repetitive initialization | **Builder Pattern** | Fluent interface for complex objects |

### 2. Enhanced Finding Structure

**Current Finding**:
```python
Finding(
    category="DI Violation",
    severity=Severity.HIGH,
    description="Direct access to .connection",
    recommendation="Use constructor injection",
    code_snippet="conn = self.app.connection"
)
```

**Enhanced Finding** (NEW):
```python
Finding(
    category="DI Violation",
    severity=Severity.HIGH,
    description="Direct access to .connection",
    recommendation="Use constructor injection",
    code_snippet="conn = self.app.connection",
    # NEW FIELDS:
    gof_pattern_suggestion="Factory Pattern",  # ⭐ NEW
    gof_pattern_rationale="Encapsulates connection creation logic",  # ⭐ NEW
    gof_pattern_example="""
# Apply Factory Pattern:
class ConnectionFactory:
    @staticmethod
    def create(config):
        if config['type'] == 'hana':
            return HanaConnection(config)
        return SqliteConnection(config)

# Usage:
factory = ConnectionFactory()
conn = factory.create(app.config)  # Clean, testable
"""  # ⭐ NEW
)
```

---

## 3. GoF Patterns to Implement

### 3.1 Factory Pattern (Creational)

**When to Suggest**:
- ✅ Direct `.connection` access
- ✅ Direct database instantiation (`sqlite3.connect()`)
- ✅ Hardcoded `if config['type'] == 'hana': ... else: ...`

**Example Suggestion**:
```python
# Problem: Direct instantiation
conn = sqlite3.connect(db_path)  # Hardcoded

# Solution: Factory Pattern
class DatabaseFactory:
    @staticmethod
    def create_connection(config):
        if config['type'] == 'hana':
            return hdbcli.connect(**config['hana'])
        return sqlite3.connect(config['sqlite_path'])

# Benefits:
# - Single point for creation logic
# - Easy to add new database types
# - Testable (mock factory)
```

### 3.2 Strategy Pattern (Behavioral)

**When to Suggest**:
- ✅ Large classes (>500 LOC) with conditional logic
- ✅ Multiple `if/elif/else` chains for algorithms
- ✅ Switch statements on type/mode

**Example Suggestion**:
```python
# Problem: Large class with algorithm variants
class DataProcessor:
    def process(self, data, mode):
        if mode == 'fast':
            # 50 lines of fast algorithm
        elif mode == 'accurate':
            # 50 lines of accurate algorithm
        # 500 lines total

# Solution: Strategy Pattern
class IProcessingStrategy(ABC):
    @abstractmethod
    def process(self, data): pass

class FastStrategy(IProcessingStrategy):
    def process(self, data):
        # 50 lines - focused

class AccurateStrategy(IProcessingStrategy):
    def process(self, data):
        # 50 lines - focused

class DataProcessor:
    def __init__(self, strategy: IProcessingStrategy):
        self.strategy = strategy
    
    def process(self, data):
        return self.strategy.process(data)  # Delegate

# Benefits:
# - Each strategy < 100 LOC (SRP)
# - Easy to add new strategies
# - Testable in isolation
```

### 3.3 Adapter Pattern (Structural)

**When to Suggest**:
- ✅ Direct external library usage (`sqlite3`, `hdbcli`, `requests`)
- ✅ Tight coupling to third-party APIs
- ✅ Interface incompatibility

**Example Suggestion**:
```python
# Problem: Direct library usage
import sqlite3
def query(sql):
    conn = sqlite3.connect('db.db')  # Tight coupling
    cursor = conn.cursor()
    cursor.execute(sql)
    return cursor.fetchall()

# Solution: Adapter Pattern
class IDatabaseAdapter(ABC):
    @abstractmethod
    def execute_query(self, sql): pass

class SqliteAdapter(IDatabaseAdapter):
    def __init__(self, db_path):
        self.db_path = db_path
    
    def execute_query(self, sql):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(sql)
        return cursor.fetchall()

# Benefits:
# - Interface-based (swap implementations)
# - Mock for testing
# - Isolates library-specific code
```

### 3.4 Observer Pattern (Behavioral)

**When to Suggest**:
- ✅ Manual callback management
- ✅ Tight coupling via event handlers
- ✅ No EventBus (app_v2 has this)

**Example Suggestion**:
```python
# Problem: Manual event distribution
class DataService:
    def update_data(self, data):
        result = self.repository.update(data)
        # Manual notification
        self.ui.refresh()
        self.cache.invalidate()
        self.logger.log(result)

# Solution: Observer Pattern (EventBus)
class DataService:
    def __init__(self, event_bus):
        self.event_bus = event_bus
    
    def update_data(self, data):
        result = self.repository.update(data)
        self.event_bus.publish('data.updated', result)  # Decoupled

# Subscribers listen independently:
event_bus.subscribe('data.updated', lambda e: ui.refresh())
event_bus.subscribe('data.updated', lambda e: cache.invalidate())

# Benefits:
# - Loose coupling
# - Easy to add/remove subscribers
# - Single Responsibility (service doesn't know about UI/cache)
```

### 3.5 Singleton Pattern (Creational)

**When to Suggest**:
- ✅ Multiple instantiations of expensive resources
- ✅ Global state needed (database connections)
- ⚠️ **WITH WARNING**: Can become Service Locator anti-pattern

**Example Suggestion**:
```python
# Problem: Multiple connection instances
conn1 = sqlite3.connect('db.db')
conn2 = sqlite3.connect('db.db')  # Wasteful

# Solution: Singleton Pattern (USE SPARINGLY)
class DatabaseConnection:
    _instance = None
    
    def __new__(cls, db_path):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.connection = sqlite3.connect(db_path)
        return cls._instance

# ⚠️ WARNING: Prefer Dependency Injection over Singleton
# Better: Inject single connection instance via DI
# Singleton useful for: Config, Logger, ConnectionPool
```

### 3.6 Decorator Pattern (Structural)

**When to Suggest**:
- ✅ Cross-cutting concerns (logging, caching, timing)
- ✅ Repetitive wrapper logic
- ✅ Need to enhance behavior dynamically

**Example Suggestion**:
```python
# Problem: Repetitive logging/caching
def get_products():
    log("Fetching products")
    result = repository.get_products()
    cache.set('products', result)
    return result

# Solution: Decorator Pattern
class LoggedRepository:
    def __init__(self, repository, logger):
        self._repository = repository
        self._logger = logger
    
    def get_products(self):
        self._logger.log("Fetching products")
        return self._repository.get_products()

class CachedRepository:
    def __init__(self, repository, cache):
        self._repository = repository
        self._cache = cache
    
    def get_products(self):
        cached = self._cache.get('products')
        if cached:
            return cached
        result = self._repository.get_products()
        self._cache.set('products', result)
        return result

# Compose:
repo = SqliteRepository()
repo = LoggedRepository(repo, logger)
repo = CachedRepository(repo, cache)
result = repo.get_products()  # Logging + caching transparent

# Benefits:
# - Composable behaviors
# - Single Responsibility
# - No duplicate logic
```

---

## Implementation Plan

### Phase 1: Add GoF Suggestion Engine (1 hour)

**File**: `tools/fengshui/agents/architect_agent.py`

**Add method**:
```python
def _suggest_gof_pattern(self, finding: Finding) -> Finding:
    """
    Enhance finding with GoF pattern suggestion
    
    Args:
        finding: Original finding from detector
    
    Returns:
        Enhanced finding with GoF fields
    """
    # Map violation category → GoF pattern
    gof_mappings = {
        'DI Violation': {
            'pattern': 'Factory Pattern',
            'rationale': 'Encapsulates complex object creation',
            'example': FACTORY_EXAMPLE
        },
        'Large Class (SRP Violation)': {
            'pattern': 'Strategy Pattern',
            'rationale': 'Extracts algorithms to separate classes',
            'example': STRATEGY_EXAMPLE
        },
        # ... more mappings
    }
    
    mapping = gof_mappings.get(finding.category)
    if mapping:
        finding.gof_pattern_suggestion = mapping['pattern']
        finding.gof_pattern_rationale = mapping['rationale']
        finding.gof_pattern_example = mapping['example']
    
    return finding
```

### Phase 2: Update Finding Dataclass (30 min)

**File**: `tools/fengshui/agents/base_agent.py`

**Add fields to Finding**:
```python
@dataclass
class Finding:
    # ... existing fields ...
    
    # NEW: GoF Pattern Suggestions
    gof_pattern_suggestion: Optional[str] = None
    gof_pattern_rationale: Optional[str] = None
    gof_pattern_example: Optional[str] = None
```

### Phase 3: Enhance Output Formatting (30 min)

**File**: `tools/fengshui/utils/finding_formatter.py`

**Update formatter** to show GoF suggestions:
```python
if finding.gof_pattern_suggestion:
    output.append(f"   💡 GoF Pattern: {finding.gof_pattern_suggestion}")
    output.append(f"      Why: {finding.gof_pattern_rationale}")
    if finding.gof_pattern_example:
        output.append(f"      Example:")
        output.append(textwrap.indent(finding.gof_pattern_example, '      '))
```

### Phase 4: Write Tests (1 hour)

**File**: `tests/unit/tools/fengshui/test_gof_suggestions.py`

**Test cases**:
- DI violation → Factory suggestion
- Large class → Strategy suggestion
- External library → Adapter suggestion
- Event handling → Observer suggestion

---

## Example Output

### Before (Current)
```
[ARCH-042] DI Violation (HIGH)
  File: modules/data_products/backend/api.py:45
  Description: Direct access to .connection
  Recommendation: Use constructor injection

  Code:
    conn = self.app.connection
```

### After (Enhanced)
```
[ARCH-042] DI Violation (HIGH)
  File: modules/data_products/backend/api.py:45
  Description: Direct access to .connection
  Recommendation: Use constructor injection
  
  💡 GoF Pattern: Factory Pattern
     Why: Encapsulates connection creation logic, enables swappable implementations
     
     Example:
     # Apply Factory Pattern:
     class ConnectionFactory:
         @staticmethod
         def create(config):
             if config['type'] == 'hana':
                 return HanaConnection(config)
             return SqliteConnection(config)
     
     # Usage:
     factory = ConnectionFactory()
     conn = factory.create(app.config)  # Clean, testable

  Code:
    conn = self.app.connection
```

---

## Benefits

### For Developers
✅ **Contextual Learning**: See patterns where they apply
✅ **Copy-Paste Examples**: Ready-to-use code
✅ **WHY Explained**: Understand pattern value
✅ **No Tracking Overhead**: Just suggestions, no metrics

### For Architects
✅ **Educational**: Team learns patterns naturally
✅ **Consistent**: Same patterns suggested project-wide
✅ **Actionable**: Tied to real code issues
✅ **Lightweight**: No separate tracking system

### vs Separate GoF Tracker
✅ **Simpler**: 2-3h vs 8-12h
✅ **Contextual**: Suggestions where needed
✅ **No Overhead**: No metrics, no dashboard
✅ **Leverages Existing**: Feng Shui already analyzes code

---

## Scope

### In Scope (6 GoF Patterns)

**Creational**:
1. **Factory Pattern** - Object creation
2. **Builder Pattern** - Complex object construction
3. **Singleton Pattern** - Single instance (with warning)

**Structural**:
4. **Adapter Pattern** - Interface compatibility
5. **Decorator Pattern** - Enhance behavior dynamically
6. **Facade Pattern** - Simplify subsystem (already detected)

**Behavioral**:
7. **Strategy Pattern** - Algorithm variants
8. **Observer Pattern** - Event handling

### Out of Scope (15 Other GoF Patterns)

**Why**: Less commonly needed in Python web apps:
- Prototype, Abstract Factory (complex creational)
- Bridge, Composite, Flyweight, Proxy (structural)
- Chain of Responsibility, Command, Interpreter, Iterator, Mediator, Memento, State, Template Method, Visitor (behavioral)

**Can add later if violations detected**

---

## Example Mappings

### Mapping 1: DI Violation → Factory Pattern

**Violation Detected**:
```python
# Bad: Direct instantiation
conn = sqlite3.connect(app.config['DB_PATH'])
```

**GoF Suggestion**:
```
💡 GoF Pattern: Factory Pattern
   Why: Encapsulates connection creation, enables testing with mocks
   
   Example:
   class ConnectionFactory:
       def create(self, db_type, config):
           if db_type == 'hana':
               return HanaConnection(config)
           return SqliteConnection(config)
```

### Mapping 2: Large Class → Strategy Pattern

**Violation Detected**:
```python
# Bad: 700-line class with multiple algorithms
class DataProcessor:
    def process(self, data, mode):
        if mode == 'fast': ...  # 200 lines
        elif mode == 'accurate': ...  # 300 lines
        elif mode == 'secure': ...  # 200 lines
```

**GoF Suggestion**:
```
💡 GoF Pattern: Strategy Pattern
   Why: Extracts algorithms into focused classes (each <100 LOC)
   
   Example:
   class IProcessingStrategy(ABC):
       @abstractmethod
       def process(self, data): pass
   
   class FastStrategy(IProcessingStrategy):
       def process(self, data): ...  # 50 lines
   
   class AccurateStrategy(IProcessingStrategy):
       def process(self, data): ...  # 80 lines
   
   # Usage:
   processor = DataProcessor(strategy=FastStrategy())
```

### Mapping 3: External Library → Adapter Pattern

**Violation Detected**:
```python
# Bad: Direct library usage
import requests
result = requests.get(url)
```

**GoF Suggestion**:
```
💡 GoF Pattern: Adapter Pattern
   Why: Isolates external dependency, enables mocking
   
   Example:
   class IHttpClient(ABC):
       @abstractmethod
       def get(self, url): pass
   
   class RequestsAdapter(IHttpClient):
       def get(self, url):
           return requests.get(url)
   
   # Benefits: Swap implementations, mock for tests
```

---

## Impact Analysis

### Effort: 2-3 hours

**Breakdown**:
- 1h: Add GoF suggestion engine
- 30min: Update Finding dataclass
- 30min: Enhance formatter
- 1h: Write tests

### Value Delivered

**Educational**:
- Developers learn patterns in context
- No separate study needed
- Patterns tied to real code

**Practical**:
- Copy-paste ready examples
- Clear rationale (WHY pattern helps)
- Actionable (fix violation + apply pattern)

**Lightweight**:
- No tracking overhead
- No dashboard complexity
- Leverages existing Feng Shui

---

## Comparison: This vs Full GoF Tracker

| Feature | **GoF Tracker** (Rejected) | **GoF Suggestions** (This) |
|---------|----------------------------|----------------------------|
| **Effort** | 8-12 hours | 2-3 hours |
| **Detection** | Standalone system | Piggyback on Feng Shui |
| **Tracking** | Adoption metrics | None (just suggestions) |
| **Dashboard** | Separate UI | Integrated into violations |
| **Value** | Pattern compliance | Contextual learning |
| **Overlap** | High (Feng Shui) | None (enhancement) |

**Verdict**: GoF Suggestions = 4x faster, more practical, leverages existing work

---

## Success Criteria

### Must Have
- [x] 6-8 GoF patterns mapped to violations
- [x] Code examples for each pattern
- [x] Rationale explaining WHY pattern helps
- [x] Integrated into existing Feng Shui output
- [x] Zero breaking changes

### Nice to Have
- [ ] Pattern complexity scores (when to use vs not)
- [ ] Anti-pattern warnings (Singleton → Service Locator risk)
- [ ] Pattern combination suggestions (Factory + Strategy)

---

## Risk Assessment

### Risk 1: Overload Developers

**Mitigation**:
- Show GoF suggestion ONLY if violation detected
- Keep examples concise (< 20 lines)
- Use `--detailed` flag for full examples

### Risk 2: Incorrect Pattern Suggestions

**Mitigation**:
- Conservative mappings (only suggest when clear fit)
- Include rationale (developer can assess)
- Prefix with "Consider" not "Must use"

### Risk 3: Maintenance Burden

**Mitigation**:
- Only 6-8 patterns (manageable)
- Code examples as constants (easy to update)
- Unit tests ensure suggestions accurate

---

## Decision

### ✅ Proceed with Enhancement?

**Pros**:
- 2-3 hours (vs 8-12 for full tracker)
- Educational value
- Leverages existing Feng Shui
- No tracking overhead

**Cons**:
- Not comprehensive (only 6-8 patterns)
- Manual curation needed (map patterns)
- Limited to violations (no proactive tracking)

**My Recommendation**: ✅ **YES - Proceed**

**Rationale**:
1. Low effort (2-3h)
2. High educational value
3. Complements DDD tracker (DDD = strategic, GoF = tactical)
4. No redundancy (enhancement, not replacement)

---

## Next Steps

**If approved**:
1. Implement GoF suggestion engine (1h)
2. Update Finding dataclass (30min)
3. Enhance formatter (30min)
4. Write tests (1h)
5. Update ArchitectAgent README

**Total**: 2-3 hours

---

**Your thoughts?** Should we enhance ArchitectAgent with GoF suggestions?