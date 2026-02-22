# Feng Shui Phase 4: GoF Design Pattern Compliance Checks

**Purpose**: Detect and prevent GoF design pattern violations  
**Created**: 2026-02-06  
**Integration**: Part of Feng Shui Phase 4 Architecture Review  
**Reference**: [[GoF Design Patterns Guide]]

---

## 🎯 Overview

Phase 4 of Feng Shui now includes automated checks for **Gang of Four (GoF) Design Pattern** compliance. This ensures the codebase follows established best practices and prevents anti-patterns from accumulating.

---

## 🔍 Pattern Compliance Checks

### 1. God Object Detection 🔴 CRITICAL

**Anti-Pattern**: Classes that do too much (Single Responsibility Principle violation)

**Detection Rule**:
```python
# Check: Class file > 300 lines OR class has > 15 public methods
if file_lines > 300 or public_methods > 15:
    flag_as_god_object()
```

**What to Look For**:
- ❌ Classes mixing multiple concerns (database + business logic + UI)
- ❌ Files with > 300 lines of code
- ❌ Classes with > 15 public methods
- ❌ Classes named "Manager", "Handler", "Util" (often god objects)

**Example Violation**:
```python
# BAD: God Object
class DataProductManager:
    def __init__(self):
        self.db = connect_db()
        self.logger = Logger()
        self.validator = Validator()
    
    def validate_data(self): ...
    def save_to_db(self): ...
    def send_notification(self): ...
    def generate_report(self): ...
    def export_csv(self): ...
    # ... 10 more methods
```

**Correct Pattern** (Single Responsibility):
```python
# GOOD: Separated concerns
class DataProductValidator: ...
class DataProductRepository: ...
class DataProductNotifier: ...
class DataProductReporter: ...
```

---

### 2. Factory Pattern Compliance 🟡 MEDIUM

**Pattern**: Encapsulate object creation logic

**Detection Rule**:
```python
# Check: Direct instantiation of complex objects in business logic
if "= ClassName(" in business_logic_file and not in_factory:
    flag_missing_factory()
```

**What to Look For**:
- ❌ Direct instantiation: `service = HanaConnectionService(...)`
- ❌ Complex constructor calls scattered across codebase
- ❌ Conditional object creation in business logic
- ✅ Factory functions: `get_service()`, `create_instance()`

**Example Violation**:
```python
# BAD: Direct instantiation everywhere
def process_data():
    service = DataService(config, logger, db)  # Complex!
    service.process()
```

**Correct Pattern** (Factory):
```python
# GOOD: Factory encapsulates creation
def get_data_service() -> DataService:
    return DataService(
        config=get_config(),
        logger=get_logger(),
        db=get_database()
    )

def process_data():
    service = get_data_service()  # Simple!
    service.process()
```

**Project Examples** (Follow these):
- ✅ `get_hana_connection_service()` - Factory for HANA connections
- ✅ `get_playground_service()` - Factory for API playground
- ✅ `DatabasePathResolverFactory` - Factory for path resolvers

---

### 3. Strategy Pattern Opportunities 🟡 MEDIUM

**Pattern**: Encapsulate interchangeable algorithms/behaviors

**Detection Rule**:
```python
# Check: Complex if-else chains for behavior selection
if conditional_depth > 3 or elif_count > 4:
    flag_strategy_opportunity()
```

**What to Look For**:
- ❌ Long if-else chains selecting behaviors
- ❌ Switch statements on type/mode
- ❌ Repeated conditional logic across methods
- ✅ Strategy classes with common interface

**Example Violation**:
```python
# BAD: Hard-coded conditionals
def build_graph(mode):
    if mode == "schema":
        # 50 lines of schema logic
    elif mode == "data":
        # 50 lines of data logic
    elif mode == "csn":
        # 50 lines of CSN logic
```

**Correct Pattern** (Strategy):
```python
# GOOD: Strategy Pattern
class GraphBuilder(ABC):
    @abstractmethod
    def build(self) -> Graph: ...

class SchemaGraphBuilder(GraphBuilder): ...
class DataGraphBuilder(GraphBuilder): ...
class CsnGraphBuilder(GraphBuilder): ...

def build_graph(builder: GraphBuilder):
    return builder.build()  # Clean!
```

**Project Examples** (Follow these):
- ✅ `GraphBuilder` base class + strategy implementations
- ✅ `DatabasePathResolver` interface + implementations
- ✅ `GraphQueryEngine` interface + HANA/NetworkX strategies

---

### 4. Observer Pattern Usage 🟢 LOW

**Pattern**: Notify dependents of state changes

**Detection Rule**:
```python
# Check: Manual notification calls scattered in code
if "notify_" or "on_change" calls found across multiple files:
    flag_observer_opportunity()
```

**What to Look For**:
- ❌ Manual notification calls scattered everywhere
- ❌ Tight coupling between notifier and listeners
- ❌ Missing event system for state changes
- ✅ Event bus or observer registry

**When to Use**:
- Cache invalidation notifications
- UI state synchronization
- Module lifecycle events
- Log aggregation

---

### 5. Singleton Pattern Correctness 🟡 MEDIUM

**Pattern**: Ensure only one instance exists

**Detection Rule**:
```python
# Check: Global variable pattern without proper singleton implementation
if "_instance" in code and not proper_singleton_pattern:
    flag_singleton_violation()
```

**What to Look For**:
- ❌ Multiple global instances created
- ❌ No thread-safety in singleton
- ❌ Singleton not reset in tests
- ✅ Proper singleton with factory function

**Project Examples** (Follow these):
```python
# GOOD: Singleton Pattern (from hana_connection_service.py)
_hana_service_instance: Optional[HanaConnectionService] = None

def get_hana_connection_service(storage_file: str = "...") -> HanaConnectionService:
    global _hana_service_instance
    
    if _hana_service_instance is None:
        _hana_service_instance = HanaConnectionService(storage_file)
    
    return _hana_service_instance
```

**Test Consideration**: Tests must reset singleton:
```python
@pytest.fixture
def reset_singleton():
    import module
    module._instance = None
    yield
    module._instance = None
```

---

### 6. Adapter Pattern for Integrations 🟢 LOW

**Pattern**: Convert interface of class to another interface

**Detection Rule**:
```python
# Check: Direct API calls to external services
if external_api_call and not in_adapter_layer:
    flag_missing_adapter()
```

**What to Look For**:
- ❌ Direct calls to external APIs in business logic
- ❌ Hard-coded API formats/protocols
- ❌ No abstraction for external dependencies
- ✅ Adapter classes wrapping external services

**Example**: HANA Cloud integration should use adapter pattern

---

## 📊 Audit Report Format

When GoF violations are detected, report them like this:

```markdown
## Phase 4.5: GoF Design Pattern Compliance 🎨

### God Objects Detected (3)
1. **modules/knowledge_graph/backend/knowledge_graph_facade.py** (824 lines)
   - Issue: Mixing graph building, caching, and API logic
   - Solution: Split into GraphBuilder, GraphCache, GraphAPI
   - Priority: 🟡 MEDIUM
   - Effort: 4 hours

2. **core/services/hana_graph_query_engine.py** (592 lines)
   - Issue: HANA connection + query building + result processing
   - Solution: Extract HanaQueryBuilder, HanaResultProcessor
   - Priority: 🟢 LOW (works well, just large)
   - Effort: 3 hours

### Missing Factory Pattern (2)
1. **modules/data_products/backend/api.py**
   - Issue: Direct SqliteDataProductsService() instantiation
   - Solution: Add get_data_products_service() factory
   - Priority: 🔴 HIGH (prevents DI violations)
   - Effort: 1 hour

### Strategy Pattern Opportunities (1)
1. **Graph layout algorithms**
   - Issue: if-else for force/hierarchical/circular
   - Solution: LayoutStrategy interface + implementations
   - Priority: 🟢 LOW (already clean enough)
   - Effort: 2 hours
```

---

## 🛠️ Implementation Guide

### How AI Should Run This Check

```python
# Pseudo-code for Phase 4.5
def check_gof_patterns():
    violations = []
    
    # 1. Scan all Python files in modules/ and core/
    for file in scan_python_files():
        # Check God Objects
        if count_lines(file) > 300:
            violations.append({
                'type': 'God Object',
                'file': file,
                'lines': count_lines(file),
                'priority': 'MEDIUM'
            })
        
        # Check Factory Pattern
        if has_direct_instantiation(file) and is_business_logic(file):
            violations.append({
                'type': 'Missing Factory',
                'file': file,
                'priority': 'HIGH'
            })
        
        # Check Strategy Pattern
        if has_complex_conditionals(file):
            violations.append({
                'type': 'Strategy Opportunity',
                'file': file,
                'priority': 'LOW'
            })
    
    # 2. Generate work packages for violations
    for violation in violations:
        create_work_package(violation)
    
    return violations
```

---

## ✅ Success Criteria

**Phase 4.5 passes when**:
- ✅ No files > 500 lines (god object threshold)
- ✅ No critical factory pattern violations
- ✅ Singleton pattern used correctly
- ✅ Complex conditionals explained or refactored

**Acceptable Violations**:
- 🟢 Files 300-500 lines (if cohesive)
- 🟢 Strategy opportunities (if code is still clean)
- 🟢 Missing adapters (if not integrating external APIs)

---

## 🎯 Integration with Feng Shui Workflow

**Phase 4 Architecture Review** now includes:

1. **Phase 4.1**: Modular Architecture (existing)
2. **Phase 4.2**: DI Violations (existing)
3. **Phase 4.3**: Interface Usage (existing)
4. **Phase 4.4**: GoF Pattern Compliance (NEW)

**Audit Report Section**:
```markdown
## Phase 4: Architecture Review 🏗️

### 4.1 Modular Architecture ✅
[Existing checks...]

### 4.2 DI Violations ✅
[Existing checks...]

### 4.3 Interface Usage ✅
[Existing checks...]

### 4.4 GoF Design Pattern Compliance 🎨 NEW
- God Objects: [N] detected
- Factory Pattern: [N] missing
- Strategy Opportunities: [N] found
- Singleton Issues: [N] detected

[Detailed findings with work packages...]
```

---

## 📚 References

**Project Documentation**:
- [[GoF Design Patterns Guide]] - Complete pattern catalog
- [[GoF Design Patterns Analysis]] - Project-specific analysis
- [[Module Quality Gate]] - Includes pattern checks
- [[Feng Shui Separation of Concerns]] - Related principle

**External Resources**:
- "Design Patterns: Elements of Reusable Object-Oriented Software" (GoF book)
- Python Design Patterns: https://refactoring.guru/design-patterns/python

---

## 🌱 Evolution Notes

**Why This Was Added**:
- User question: "Do you check for GoF pattern violations?"
- Answer: No, currently missing from Phase 4
- Decision: Add as Phase 4.4 to make architecture review comprehensive

**Expected Benefits**:
1. **Quality**: Catch design issues early
2. **Consistency**: Enforce project-wide patterns
3. **Maintainability**: Easier to understand and modify code
4. **Teaching**: AI learns which patterns to apply automatically

**Like Feng Shui itself**: The system continuously improves! 🧘💤✨

---

**Status**: ✅ Active as of 2026-02-06  
**Part Of**: Feng Shui Phase 4 Architecture Review  
**Frequency**: Every feng shui audit (monthly recommended)  
**Next Steps**: Implement Phase 4.5-4.7 enhancements (see below)

---

## 🚀 Future Enhancements: Feng Shui Phase 4.5-4.7

**Vision**: Transform Feng Shui from validator → architecture improvement engine

### Phase 4.5: Template Method + Chain of Responsibility 🎯 NEXT

**Priority**: 🔴 HIGH | **Effort**: 4-5 hours | **Impact**: Modular, extensible validation

#### 1. Template Method Pattern for Phase Execution
**Problem**: Each phase (Scripts, Vault, Quality, Architecture, Files) has similar structure but different implementation

**Solution**:
```python
class FengShuiPhaseTemplate(ABC):
    def execute(self):
        """Template method defining phase workflow"""
        self.analyze()
        self.detect_issues()
        self.generate_work_packages()
        self.create_report()
    
    @abstractmethod
    def analyze(self): pass
    
    @abstractmethod
    def detect_issues(self): pass

class Phase4ArchitectureReview(FengShuiPhaseTemplate):
    def analyze(self):
        self.check_gof_patterns()
        self.check_di_violations()
        self.check_interfaces()
```

**Benefits**:
- Consistent execution across all phases
- Easy to add new phases
- Shared reporting/work package logic
- Parallel execution possible

#### 2. Chain of Responsibility for Quality Gate
**Problem**: 22 checks in module_quality_gate.py are sequential, hard to extend

**Solution**:
```python
class QualityCheck(ABC):
    def __init__(self, next_check=None):
        self.next = next_check
    
    def check(self, module):
        result = self._do_check(module)
        if self.next:
            result.merge(self.next.check(module))
        return result

# Chain: DI → Blueprint → GoF → Tests → ...
gate = DependencyInjectionCheck(
    BlueprintCheck(
        GoFPatternCheck(
            TestCoverageCheck(None)
        )
    )
)
```

**Benefits**:
- Modular checks (add/remove easily)
- Each check is independent
- Can skip checks conditionally
- Better separation of concerns

**Work Package**: WP-FS-001 (see PROJECT_TRACKER.md)

---

### Phase 4.6: Visitor + Composite Patterns 🎯 MEDIUM

**Priority**: 🟡 MEDIUM | **Effort**: 6-8 hours | **Impact**: Multi-level analysis

#### 3. Composite Pattern for Hierarchical Validation
**Problem**: Need to validate at multiple levels (project → module → file → class)

**Solution**:
```python
class ArchitectureComponent(ABC):
    @abstractmethod
    def validate(self) -> ValidationResult: pass

class Project(ArchitectureComponent):
    def __init__(self):
        self.modules = []  # Composite
    
    def validate(self):
        results = [m.validate() for m in self.modules]
        return ValidationResult.combine(results)

class Module(ArchitectureComponent):
    def __init__(self):
        self.files = []  # Composite
```

**Benefits**:
- Hierarchical validation (project → module → file → class)
- Aggregate results naturally
- Same interface at all levels

#### 4. Visitor Pattern for Cross-Cutting Analysis
**Problem**: Multiple analyses (patterns, complexity, dependencies) without modifying code

**Solution**:
```python
class CodeVisitor(ABC):
    @abstractmethod
    def visit_module(self, module): pass
    
    @abstractmethod
    def visit_class(self, cls): pass

class GoFPatternVisitor(CodeVisitor):
    def visit_class(self, cls):
        if cls.lines > 300:
            self.report_god_object(cls)

class ComplexityVisitor(CodeVisitor):
    def visit_method(self, method):
        if calculate_complexity(method) > 10:
            self.report_high_complexity(method)

# Single pass, multiple analyses
ast = parse_codebase()
ast.accept(GoFPatternVisitor())
ast.accept(ComplexityVisitor())
```

**Benefits**:
- Add analyses without changing code
- Separate concerns
- Multiple analyses in one pass

**Work Package**: WP-FS-002 (see PROJECT_TRACKER.md)

---

### Phase 4.7: Command + Memento + Builder 🎯 AMBITIOUS

**Priority**: 🟢 LOW (ambitious) | **Effort**: 12-15 hours | **Impact**: Automation + history

#### 5. Command Pattern for Automated Fixes
**Problem**: Feng Shui detects issues but can't fix them

**Solution**:
```python
class ArchitectureFix(ABC):
    @abstractmethod
    def execute(self): pass
    
    @abstractmethod
    def undo(self): pass

class SplitGodObjectFix(ArchitectureFix):
    def execute(self):
        self.backup = self.file.content
        new_files = split_responsibilities(self.file)
        for f in new_files:
            f.save()
    
    def undo(self):
        self.file.content = self.backup

class FixExecutor:
    def execute(self, fix):
        fix.execute()
        self.history.append(fix)
    
    def undo_last(self):
        self.history.pop().undo()
```

**Benefits**:
- Automated fixes (like Gu Wu Auto-Fix)
- Safe undo capability
- Batch operations

#### 6. Memento Pattern for Architecture Evolution
**Problem**: No tracking of how architecture changes over time

**Solution**:
```python
class ArchitectureSnapshot:
    def __init__(self, date, metrics, violations):
        self.date = date
        self.metrics = metrics
        self.violations = violations

class FengShuiAudit:
    def save_snapshot(self):
        snapshot = ArchitectureSnapshot(
            date=today(),
            metrics=self.collect_metrics(),
            violations=self.find_violations()
        )
        self.history.append(snapshot)
    
    def compare_last_two_audits(self):
        return self.history[-1].compare_with(self.history[-2])
```

**Benefits**:
- Track architecture evolution
- Measure improvement
- Identify recurring issues
- Prove ROI

#### 7. Builder Pattern for Work Packages
**Problem**: Complex work package construction with many fields

**Solution**:
```python
class WorkPackageBuilder:
    def set_title(self, title):
        self.package.title = title
        return self
    
    def set_priority(self, priority):
        self.package.priority = priority
        return self
    
    def estimate_effort(self):
        self.package.effort = self._calculate_effort()
        return self
    
    def build(self):
        return self.package

# Fluent interface
wp = (WorkPackageBuilder()
      .set_title("Fix God Object")
      .set_priority("HIGH")
      .add_finding(violation)
      .estimate_effort()
      .build())
```

**Benefits**:
- Fluent, readable interface
- Auto-calculation
- Consistent packages

**Work Package**: WP-FS-003 (see PROJECT_TRACKER.md)

---

## 📊 Enhancement Roadmap

| Phase | Patterns | Priority | Effort | Impact | Status |
|-------|----------|----------|--------|--------|--------|
| 4.4 | Detection | 🔴 HIGH | 2h | HIGH | ✅ DONE |
| 4.5 | Template + Chain | 🔴 HIGH | 4-5h | HIGH | 📋 Planned |
| 4.6 | Visitor + Composite | 🟡 MEDIUM | 6-8h | MEDIUM | 📋 Planned |
| 4.7 | Command + Memento + Builder | 🟢 LOW | 12-15h | HIGH | 📋 Future |

**Total Investment**: 24-30 hours  
**Expected ROI**: Transform Feng Shui into architecture improvement engine

---

## 🎯 Implementation Strategy

**Short-term** (Next session):
1. Implement Template Method for phase consistency
2. Add Chain of Responsibility to quality gate
3. Test with current modules

**Medium-term** (Next sprint):
1. Build Visitor-based analysis engine
2. Implement Composite for hierarchical validation
3. Integration testing

**Long-term** (Future):
1. Implement Command for auto-fixes
2. Add Memento for audit history tracking
3. Build Builder for work package generation

---

## 🌟 Vision: Feng Shui as Architecture Engine

**Current State**: Validator
- Detects violations ✅
- Generates reports ✅
- Manual fixes required ⚠️

**Future State**: Architecture Improvement Engine
- Detects violations ✅
- Suggests improvements ✅
- Automated fixes ✅ (Phase 4.7)
- Tracks evolution ✅ (Phase 4.7)
- Measures ROI ✅ (Phase 4.7)
- Self-improving ✅ (Learning from fixes)

**Like Gu Wu for tests, Feng Shui becomes self-optimizing for architecture!** 🧘💤✨
