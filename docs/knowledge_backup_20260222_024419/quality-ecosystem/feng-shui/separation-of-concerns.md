# Feng Shui: Separation of Concerns Principle

**Added**: February 1, 2026  
**Philosophy**: Each component should have ONE clear responsibility  
**Status**: Core Feng Shui principle for architecture validation  

---

## Core Principle

**Separation of Concerns (SoC)** is a fundamental Feng Shui principle:
- Each service/class should do ONE thing well
- Clear boundaries prevent tangled dependencies
- Easy to understand, test, and maintain
- Changes to one concern don't ripple to others

**Like physical spaces**: Kitchen for cooking, bedroom for sleeping, office for working.  
**Not**: Kitchen+bedroom+office in one room (chaos!)

---

## SoC in Knowledge Graph Module

### Example: Current Architecture Analysis

**Current Structure** (needs improvement):
```python
DataGraphService:
  - build_schema_graph()    # Schema visualization
  - build_data_graph()      # Data visualization  
  - _discover_fk_mappings() # Relationship discovery
  - _get_color_for_table()  # UI styling
```

**Problem**: ONE service handles 3+ concerns!
- Schema graph building (CSN-driven)
- Data graph building (database-driven)
- Visualization formatting (vis.js)
- Relationship discovery (metadata analysis)

**Proposed: Better Separation** ✅
```python
SchemaGraphService:       # CONCERN: Schema/architecture view
  - build_from_csn()      # Pure CSN-based (data source agnostic!)
  - discover_relationships()

DataGraphService:         # CONCERN: Data/record view
  - build_from_records()  # Database-driven
  - apply_fk_mappings()

GraphVisualizationService: # CONCERN: UI presentation
  - format_for_visjs()    # Shared formatting logic
  - apply_colors()        # Styling
```

**Benefits**:
- ✅ Schema graph works everywhere (CSN-only, no data source needed)
- ✅ Data graph focuses on records only
- ✅ Visualization logic reusable
- ✅ Each service has ONE clear purpose
- ✅ Easy to test in isolation

---

## SoC Violations to Check For

### 1. God Classes/Services
**Symptom**: One class does everything  
**Example**: Service with 10+ public methods doing unrelated things  
**Fix**: Split into focused services (Single Responsibility Principle)

### 2. Mixed Concerns in Methods
**Symptom**: Method does business logic + data access + formatting  
**Example**: 
```python
def get_data():
    # Business logic
    if not valid: return error
    
    # Data access
    rows = db.query("SELECT...")
    
    # Formatting
    return {"html": format_html(rows)}
```
**Fix**: Separate into 3 methods/layers

### 3. Leaky Abstractions
**Symptom**: Service exposes implementation details  
**Example**: `service.connection.execute()` (internal detail leaked!)  
**Fix**: Expose only interface methods (DI principle)

### 4. Tangled Dependencies
**Symptom**: ServiceA calls ServiceB calls ServiceC calls ServiceA (circular!)  
**Example**: data_graph → property_graph → data_graph  
**Fix**: Introduce interfaces, inversion of control

### 5. Wrong Level of Abstraction
**Symptom**: High-level service contains low-level implementation  
**Example**: API endpoint with inline SQL queries  
**Fix**: Delegate to appropriate layer (API → Service → Repository)

---

## Quality Gate Integration

### New SoC Checks (to be added)

**Check 1: Service Method Count**
```python
# Services with >10 public methods may violate SoC
if public_method_count > 10:
    warning("Service may have too many responsibilities")
```

**Check 2: Lines of Code per Service**
```python
# Services >500 lines likely doing too much
if lines_of_code > 500:
    warning("Service may be too large (consider splitting)")
```

**Check 3: Dependency Count**
```python
# Services depending on >5 other services = concern
if dependency_count > 5:
    warning("Service has too many dependencies")
```

**Check 4: Cross-Concern Patterns**
```python
# Check for mixed concerns in same file
patterns = {
    'database_access': r'\.execute\(|\.query\(',
    'http_requests': r'requests\.|urllib\.',
    'file_io': r'open\(|read\(|write\(',
    'ui_rendering': r'render_|format_html|to_json'
}
# If >2 patterns in one file → potential SoC violation
```

---

## SoC Score Component (New!)

**Add to Feng Shui Scorer** (5-10 points):

```python
# Separation of Concerns (10 points max)
SOC_CHECKS = [
    'Service has <10 public methods',
    'Service <500 lines of code',
    'Service <5 dependencies',
    'No mixed concerns detected',
    'Clear single responsibility'
]
```

**Scoring**:
- Architecture (35%) ← reduced from 40%
- Code Quality (30%)
- Security (20%)
- Documentation (10%)
- **Separation of Concerns (5%)** ← NEW!

---

## Industry Standards (SOLID Principles)

### Single Responsibility Principle (SRP)
**"A class should have one, and only one, reason to change"**

**Example - WRONG** ❌:
```python
class UserService:
    def save_user()      # Database concern
    def send_email()     # Email concern
    def log_activity()   # Logging concern
    # 3 reasons to change!
```

**Example - RIGHT** ✅:
```python
class UserRepository:     # Database concern
    def save_user()

class EmailService:       # Email concern
    def send_email()

class ActivityLogger:     # Logging concern
    def log_activity()
# Each has 1 reason to change!
```

### Interface Segregation Principle (ISP)
**"Clients shouldn't depend on methods they don't use"**

**Example - WRONG** ❌:
```python
class IDataSource:
    def get_data()        # All clients need
    def execute_sql()     # Only advanced clients need
    def backup_db()       # Only admin clients need
```

**Example - RIGHT** ✅:
```python
class IDataReader:        # Basic clients
    def get_data()

class ISQLExecutor:       # Advanced clients
    def execute_sql()

class IDataSourceAdmin:   # Admin clients
    def backup_db()
```

---

## Real-World Examples from This Project

### Good SoC ✅
```python
# core/services/csn_parser.py
# CONCERN: Parse CSN files only
class CSNParser:
    def parse_csn_file()
    def get_entities()
    # Clear, focused responsibility!

# core/services/relationship_mapper.py  
# CONCERN: Discover relationships only
class CSNRelationshipMapper:
    def discover_relationships()
    # Single, clear purpose!
```

### Needs Improvement 🟡
```python
# modules/knowledge_graph/backend/data_graph_service.py
# CONCERN: Too many responsibilities!
class DataGraphService:
    # Schema concern
    def build_schema_graph()
    
    # Data concern
    def build_data_graph()
    
    # Visualization concern
    def _get_color_for_table()
    
    # Discovery concern
    def _discover_fk_mappings()
    
# Should be 3 services!
```

---

## Migration Pattern

**When splitting a service**:

1. **Identify concerns** (what are the distinct responsibilities?)
2. **Extract interfaces** (what should each service expose?)
3. **Create new services** (one per concern)
4. **Refactor clients** (use new services)
5. **Delete old service** (once all clients migrated)
6. **Run quality gate** (verify no violations)

**Example**: DataGraphService → 3 services
```
Step 1: Create SchemaGraphService (CSN-only)
Step 2: Create DataGraphService v2 (records-only)  
Step 3: Create GraphVisualizationService (formatting)
Step 4: Update KnowledgeGraphService to use all 3
Step 5: Delete old DataGraphService
Step 6: Run quality gate + tests
```

---

## Benefits of Good SoC

**Development**:
- ✅ Easier to understand (small, focused)
- ✅ Easier to test (isolated concerns)
- ✅ Easier to change (minimal ripple effects)
- ✅ Easier to reuse (general-purpose)

**Maintenance**:
- ✅ Bug fixes localized (change one service)
- ✅ New features clean (extend one concern)
- ✅ Refactoring safe (affect one area)

**Team**:
- ✅ Parallel development (different concerns)
- ✅ Clear ownership (concern = responsibility)
- ✅ Onboarding faster (understand one piece at a time)

---

## Feng Shui Philosophy

**Physical Space Analogy**:
- Kitchen: Cooking tools, ingredients, appliances
- Office: Computer, desk, documents
- NOT: Kitchen+office+bedroom in one room!

**Code Space Analogy**:
- DataService: Data access only
- BusinessService: Business logic only  
- UIService: Presentation only
- NOT: All mixed in one "MegaService"!

**Result**: 
- Clear mental model
- Easy navigation
- Efficient development
- Maintainable over time

---

## Integration with Quality Gate

**Add SoC checks to quality gate**:
```python
def _check_separation_of_concerns(self):
    """Check if services follow SoC principle"""
    
    issues = []
    backend_dir = self.module_path / 'backend'
    
    for py_file in backend_dir.rglob('*.py'):
        # Check 1: File too large (>500 lines)
        with open(py_file) as f:
            lines = len(f.readlines())
        if lines > 500:
            issues.append(f"{py_file.name}: >500 lines (may violate SoC)")
        
        # Check 2: Too many public methods
        with open(py_file) as f:
            content = f.read()
        public_methods = len(re.findall(r'^\s{4}def [^_]', content, re.MULTILINE))
        if public_methods > 10:
            issues.append(f"{py_file.name}: {public_methods} public methods (SoC risk)")
    
    if issues:
        self.results.append(ValidationResult(
            passed=False,
            message=f"SoC violations: {'; '.join(issues)}",
            severity='WARNING'
        ))
```

---

## Future Work

**WP-FENG-001**: Add SoC checks to quality gate
- Service method count check
- Lines of code check  
- Dependency count check
- Mixed concern pattern detection

**WP-KG-002**: Refactor DataGraphService per SoC
- Split into SchemaGraphService + DataGraphService + GraphVisualizationService
- Each service: one clear responsibility
- Improve Feng Shui score from 93 → 95+ (A/S grade)

---

**Status**: ✅ Documented principle, ready for quality gate integration  
**Priority**: High - Core Feng Shui philosophy  
**Impact**: Improves architecture quality across all modules  
**References**: [[Module Quality Gate]], [[Modular Architecture]], [[Feng Shui Phase 5]]