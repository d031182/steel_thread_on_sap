# DDD Patterns → Quality Ecosystem Integration Proposal

**Date**: 2026-02-07  
**Purpose**: How Cosmic Python DDD patterns can enhance Feng Shui, Gu Wu, and Shi Fu  
**Status**: ✅ APPROVED - Option 1: Start Phase 1 Now (User decision: 2026-02-07)

---

## 🎯 Executive Summary

**The Opportunity**: Now that we've documented all 8 Cosmic Python DDD patterns, we can teach our quality tools to detect, enforce, and guide their implementation.

**The Vision**: 
- **Feng Shui** detects DDD pattern violations (like it now does for Repository Pattern)
- **Gu Wu** generates pattern-aware tests (Unit of Work tests, Aggregate tests)
- **Shi Fu** correlates pattern adoption with code/test quality metrics

**Key Insight**: Our quality tools should **learn from our architectural evolution**, just as they learned Repository Pattern v3.0.0.

---

## 📊 Pattern-by-Pattern Analysis

### Which Patterns Should Be Integrated? (Priority Order)

| Pattern | Feng Shui | Gu Wu | Shi Fu | Priority | Reason |
|---------|-----------|-------|--------|----------|--------|
| **Unit of Work** | ⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐ | **HIGH** | Next implementation (1-2 days) |
| **Service Layer** | ⭐⭐⭐ | ⭐⭐ | ⭐⭐ | **HIGH** | Already partial, need enforcement |
| **Aggregate** | ⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐ | **MEDIUM** | Data integrity critical |
| **Domain Events** | ⭐⭐ | ⭐⭐ | ⭐⭐⭐ | **MEDIUM** | Shi Fu already tracks events! |
| **Repository** | ✅ DONE | ⭐ | ⭐ | - | Already implemented v4.6 |
| **Domain Model** | ⭐ | ⭐⭐ | ⭐ | **LOW** | Too abstract to detect |
| **Message Bus** | ⭐ | ⭐ | ⭐⭐ | **LOW** | Future (not implemented yet) |
| **CQRS** | ⭐ | ⭐ | ⭐⭐ | **LOW** | Future (not implemented yet) |

---

## 🏛️ PART 1: FENG SHUI ENHANCEMENTS

### Philosophy
> "Feng Shui learns from our architecture evolution. When we implement patterns, Feng Shui learns to detect violations."

### 1.1 Unit of Work Pattern Detector ⭐ **HIGHEST PRIORITY**

**Why This Matters**:
- We're about to implement Unit of Work (Priority 1 HIGH)
- Feng Shui should detect violations once pattern is live
- Prevents regression to manual transaction management

**What Feng Shui Would Detect**:

#### Violation 1: Manual Commit/Rollback (HIGH)
```python
# ❌ BAD: Manual transaction management
def create_invoice(data):
    connection = get_connection()
    try:
        connection.execute("INSERT INTO invoices ...")
        connection.execute("UPDATE purchase_orders ...")
        connection.commit()  # Manual commit!
    except:
        connection.rollback()  # Manual rollback!

# ✅ GOOD: Unit of Work pattern
def create_invoice(data, uow: AbstractUnitOfWork):
    with uow:
        uow.repos.invoices.create(data)
        uow.repos.purchase_orders.update(...)
        uow.commit()  # Explicit UoW commit
```

**Detection Strategy**:
- ✅ AST parsing for `.commit()` and `.rollback()` on connection objects
- ✅ Check if inside `with uow:` context manager
- ✅ Recommend Unit of Work pattern if violations found

#### Violation 2: Missing Transaction Boundary (MEDIUM)
```python
# ❌ BAD: No transaction for multi-repo operations
def process_invoice(invoice_data):
    invoice = repo1.create(invoice_data)
    po = repo2.update(invoice.po_id)  # Not atomic!
    log.record("invoice_created")      # If this fails, inconsistent!

# ✅ GOOD: Atomic transaction
def process_invoice(invoice_data, uow: AbstractUnitOfWork):
    with uow:
        invoice = uow.repos.invoices.create(invoice_data)
        po = uow.repos.purchase_orders.update(invoice.po_id)
        uow.repos.audit_log.record("invoice_created")
        uow.commit()  # All or nothing!
```

**Detection Strategy**:
- ✅ Detect multiple repository operations in same function
- ✅ Check if wrapped in Unit of Work context
- ✅ Flag as atomicity risk if not

**Implementation Effort**: 4-6 hours (similar to Repository Pattern detector)

---

### 1.2 Service Layer Pattern Detector ⭐ **HIGH PRIORITY**

**Why This Matters**:
- We already have partial Service Layer (kpi_service.py)
- Need to enforce pattern across all modules
- Prevents business logic leaking into Flask routes

**What Feng Shui Would Detect**:

#### Violation 1: Business Logic in Flask Routes (HIGH)
```python
# ❌ BAD: Business logic in controller
@app.route('/api/invoice', methods=['POST'])
def create_invoice():
    data = request.json
    # Business logic in route! ❌
    if data['total'] > 10000:
        send_approval_email()
    invoice = repo.create(data)
    return jsonify(invoice)

# ✅ GOOD: Thin controller, fat service
@app.route('/api/invoice', methods=['POST'])
def create_invoice():
    data = request.json
    invoice_service = InvoiceService(current_app.repository)
    invoice = invoice_service.create_invoice(data)  # Business logic in service ✅
    return jsonify(invoice)
```

**Detection Strategy**:
- ✅ Detect Flask route functions with >10 lines
- ✅ Check for business logic keywords (if/for/while, calculations)
- ✅ Recommend extracting to Service Layer

#### Violation 2: Direct Repository Access from Routes (MEDIUM)
```python
# ❌ BAD: Controller calls repository directly
@app.route('/api/kpis')
def get_kpis():
    repo = current_app.repository
    orders = repo.execute_query("SELECT ...")  # Direct DB access! ❌
    return jsonify(calculate_kpis(orders))

# ✅ GOOD: Controller calls service
@app.route('/api/kpis')
def get_kpis():
    kpi_service = KPIService(current_app.repository)
    return jsonify(kpi_service.calculate_kpis())  # Service handles it ✅
```

**Detection Strategy**:
- ✅ Detect repository usage in Flask routes
- ✅ Recommend Service Layer extraction
- ✅ Suggest interface: `SomeService(repository)`

**Implementation Effort**: 4-6 hours

---

### 1.3 Aggregate Pattern Detector 💡 **MEDIUM PRIORITY**

**Why This Matters**:
- Enforces consistency boundaries (PO total = sum(items))
- Prevents direct manipulation of child entities
- Critical for data integrity

**What Feng Shui Would Detect**:

#### Violation 1: Direct Child Entity Access (HIGH)
```python
# ❌ BAD: Directly modify child entities
def add_item_to_order(order_id, item_data):
    order = order_repo.get(order_id)
    item = OrderItem(**item_data)
    order_item_repo.add(item)  # Bypasses aggregate root! ❌
    order.total += item.price  # Manual consistency! ❌

# ✅ GOOD: Aggregate root enforces invariants
def add_item_to_order(order_id, item_data):
    order = order_repo.get(order_id)  # Aggregate Root
    order.add_item(item_data)  # Invariant: total = sum(items) ✅
    order_repo.save(order)  # Saves order + items atomically ✅
```

**Detection Strategy**:
- ✅ Detect child entity repositories (OrderItem, PurchaseOrderItem)
- ✅ Check if accessed directly or through Aggregate Root
- ✅ Recommend Aggregate pattern for consistency

#### Violation 2: Manual Invariant Enforcement (MEDIUM)
```python
# ❌ BAD: Manual consistency checks
def update_order_total(order):
    total = sum(item.price for item in order.items)
    order.total = total  # Manual sync! ❌

# ✅ GOOD: Aggregate enforces automatically
class Order:  # Aggregate Root
    @property
    def total(self):
        return sum(item.price for item in self._items)  # Always consistent! ✅
```

**Detection Strategy**:
- ✅ Detect manual calculations of derived fields
- ✅ Recommend moving to Aggregate Root properties

**Implementation Effort**: 6-8 hours (more complex pattern)

---

### 1.4 Domain Events Pattern Detector 💡 **MEDIUM PRIORITY**

**Why This Matters**:
- Decouples side effects from business logic
- Extensible (add handlers without changing domain)
- Shi Fu already tracks correlation patterns!

**What Feng Shui Would Detect**:

#### Violation 1: Side Effects in Domain Logic (MEDIUM)
```python
# ❌ BAD: Side effects coupled to domain
def approve_invoice(invoice_id):
    invoice = repo.get(invoice_id)
    invoice.status = "approved"
    send_email(invoice.supplier)  # Side effect! ❌
    log_approval(invoice)  # Side effect! ❌
    notify_accounting(invoice)  # Side effect! ❌

# ✅ GOOD: Domain raises events, handlers react
def approve_invoice(invoice_id, uow, bus):
    with uow:
        invoice = uow.repos.invoices.get(invoice_id)
        invoice.approve()  # Raises InvoiceApproved event ✅
        uow.commit()
    bus.handle(invoice.events)  # Handlers react ✅
```

**Detection Strategy**:
- ✅ Detect side effects in domain methods (email, logging, HTTP calls)
- ✅ Recommend Domain Events pattern for decoupling

**Implementation Effort**: 4-6 hours

---

## 🧪 PART 2: GU WU ENHANCEMENTS

### Philosophy
> "Gu Wu generates pattern-aware tests. When patterns are implemented, Gu Wu knows how to test them."

### 2.1 Unit of Work Test Generator ⭐ **HIGHEST PRIORITY**

**Why This Matters**:
- Unit of Work requires specific test patterns
- FakeUnitOfWork for unit tests (fast, no DB)
- Real UnitOfWork for integration tests (slow, real DB)

**What Gu Wu Would Generate**:

#### Test Template 1: Unit Test with FakeUnitOfWork
```python
# Gu Wu Auto-Generated Test
def test_create_invoice_commits_transaction():
    """Test invoice creation commits all changes atomically."""
    # ARRANGE
    fake_uow = FakeUnitOfWork()
    invoice_service = InvoiceService(fake_uow)
    
    # ACT
    invoice_service.create_invoice({
        "supplier_id": "S001",
        "total": 1000.0
    })
    
    # ASSERT
    assert fake_uow.committed == True  # Transaction committed
    assert len(fake_uow.repos.invoices.data) == 1  # Invoice created
    assert fake_uow.repos.purchase_orders.updated  # PO updated
```

#### Test Template 2: Atomicity Test (Rollback)
```python
# Gu Wu Auto-Generated Test
def test_create_invoice_rolls_back_on_error():
    """Test transaction rolls back if any operation fails."""
    # ARRANGE
    fake_uow = FakeUnitOfWork()
    fake_uow.repos.invoices.should_fail = True  # Simulate error
    invoice_service = InvoiceService(fake_uow)
    
    # ACT & ASSERT
    with pytest.raises(Exception):
        invoice_service.create_invoice({"total": 1000.0})
    
    assert fake_uow.rolled_back == True  # Transaction rolled back
    assert len(fake_uow.repos.invoices.data) == 0  # No invoice created
```

**Gu Wu Intelligence**:
- ✅ Detects Unit of Work usage in code
- ✅ Generates FakeUnitOfWork fixture automatically
- ✅ Creates atomicity tests (commit + rollback)
- ✅ Validates transaction boundaries

**Implementation Effort**: 6-8 hours

---

### 2.2 Aggregate Test Generator 💡 **MEDIUM PRIORITY**

**Why This Matters**:
- Aggregates enforce invariants (need tests!)
- Test consistency boundaries
- Prevent regression on invariant violations

**What Gu Wu Would Generate**:

#### Test Template 1: Invariant Enforcement
```python
# Gu Wu Auto-Generated Test
def test_order_total_always_equals_sum_of_items():
    """Test aggregate enforces total = sum(items) invariant."""
    # ARRANGE
    order = Order(order_id="O001")
    
    # ACT
    order.add_item("SKU1", qty=2, price=10.0)
    order.add_item("SKU2", qty=1, price=5.0)
    
    # ASSERT
    assert order.total == 25.0  # Invariant holds
    assert len(order.items) == 2
```

#### Test Template 2: Boundary Protection
```python
# Gu Wu Auto-Generated Test
def test_cannot_modify_items_directly():
    """Test child entities cannot be modified bypassing aggregate root."""
    # ARRANGE
    order = Order(order_id="O001")
    order.add_item("SKU1", qty=1, price=10.0)
    
    # ACT & ASSERT
    with pytest.raises(AttributeError):
        order._items.append(...)  # Cannot access private ._items
    
    # Must use aggregate root method
    order.add_item("SKU2", qty=1, price=5.0)  # ✅ Correct way
```

**Gu Wu Intelligence**:
- ✅ Detects Aggregate Root classes
- ✅ Identifies invariants (calculated properties)
- ✅ Generates invariant enforcement tests
- ✅ Creates boundary protection tests

**Implementation Effort**: 6-8 hours

---

### 2.3 Service Layer Test Generator ⭐ **HIGH PRIORITY**

**Why This Matters**:
- Service Layer orchestrates use cases
- Should be tested without Flask (fast unit tests)
- Mock repositories for speed

**What Gu Wu Would Generate**:

#### Test Template: Pure Service Test (No Flask)
```python
# Gu Wu Auto-Generated Test
def test_calculate_kpis_orchestrates_correctly():
    """Test KPI service orchestrates repository calls."""
    # ARRANGE
    mock_repo = Mock()
    mock_repo.get_orders.return_value = [...]
    mock_repo.get_invoices.return_value = [...]
    kpi_service = KPIService(mock_repo)
    
    # ACT
    kpis = kpi_service.calculate_kpis(date_range=("2026-01-01", "2026-01-31"))
    
    # ASSERT
    mock_repo.get_orders.assert_called_once()
    mock_repo.get_invoices.assert_called_once()
    assert kpis['total_orders'] == 10
    assert kpis['invoice_accuracy'] > 90.0
```

**Gu Wu Intelligence**:
- ✅ Detects Service Layer classes (pattern: *Service)
- ✅ Generates tests without Flask framework
- ✅ Uses mocks for fast execution
- ✅ Validates orchestration logic

**Implementation Effort**: 4-6 hours

---

## 🧘‍♂️ PART 3: SHI FU ENHANCEMENTS

### Philosophy
> "Shi Fu correlates pattern adoption with quality metrics. Shows the business value of DDD patterns."

### 3.1 Pattern Adoption Tracker ⭐ **HIGH VALUE**

**Why This Matters**:
- Quantifies impact of pattern adoption
- Proves DDD patterns improve quality
- Guides future architectural decisions

**What Shi Fu Would Track**:

#### Metric 1: Pattern Adoption vs Test Flakiness
```python
# Shi Fu Correlation Pattern
def analyze_uow_adoption_impact():
    """Correlate Unit of Work adoption with test flakiness reduction."""
    
    # BEFORE Unit of Work
    modules_without_uow = analyze_modules(pattern="no_unit_of_work")
    flaky_tests_before = count_flaky_tests(modules_without_uow)
    
    # AFTER Unit of Work
    modules_with_uow = analyze_modules(pattern="unit_of_work")
    flaky_tests_after = count_flaky_tests(modules_with_uow)
    
    # CORRELATION
    improvement = (flaky_tests_before - flaky_tests_after) / flaky_tests_before
    
    return {
        "pattern": "Unit of Work",
        "impact": f"{improvement*100:.1f}% reduction in flaky tests",
        "confidence": calculate_correlation_confidence(),
        "teaching": "Unit of Work eliminates test flakiness from transaction issues"
    }
```

**Metrics to Track**:
- ✅ Unit of Work → Test flakiness (expect: 30-50% reduction)
- ✅ Aggregate → Data integrity bugs (expect: 70-90% reduction)
- ✅ Service Layer → Controller complexity (expect: 40-60% reduction)
- ✅ Domain Events → Coupling metrics (expect: 50-70% reduction)

#### Metric 2: Pattern Coverage Score
```python
# Shi Fu Health Metric
def calculate_pattern_coverage():
    """Calculate how well codebase follows DDD patterns."""
    
    return {
        "repository_pattern": 95,  # ✅ v3.0.0 implemented
        "service_layer": 40,       # 💡 Partial (kpi_service only)
        "unit_of_work": 0,         # ❌ Not implemented
        "aggregate": 0,            # ❌ Not implemented
        "domain_events": 0,        # ❌ Not implemented
        "overall_ddd_score": 27    # (95+40+0+0+0)/5 = 27/100
    }
```

**Shi Fu Teaching**:
> "Your DDD score is 27/100. Implementing Unit of Work (Priority 1) would raise it to 46/100 and reduce test flakiness by ~40%."

---

### 3.2 Pattern Impact Dashboard 💡 **MEDIUM VALUE**

**Why This Matters**:
- Visualizes pattern adoption over time
- Shows return on investment for DDD patterns
- Guides prioritization decisions

**What Shi Fu Would Display**:

```
═══════════════════════════════════════════════════════════════
                  DDD PATTERN ADOPTION DASHBOARD
═══════════════════════════════════════════════════════════════

PATTERN COVERAGE:
┌─────────────────┬──────────┬────────────┬─────────────────┐
│ Pattern         │ Adoption │ Impact     │ Recommendation  │
├─────────────────┼──────────┼────────────┼─────────────────┤
│ Repository      │ 95% ✅   │ HIGH       │ Maintain        │
│ Service Layer   │ 40% 💡   │ MEDIUM     │ Expand usage    │
│ Unit of Work    │  0% ❌   │ HIGH       │ ⭐ Implement now│
│ Aggregate       │  0% ❌   │ HIGH       │ After UoW       │
│ Domain Events   │  0% ❌   │ MEDIUM     │ After Aggregate │
└─────────────────┴──────────┴────────────┴─────────────────┘

QUALITY IMPACT FORECAST:
- Implement Unit of Work → +40% test reliability
- Implement Aggregate → +70% data integrity
- Implement Domain Events → +50% decoupling

PRIORITY RECOMMENDATION:
⭐ Unit of Work (1-2 days) → Highest ROI
```

**Implementation Effort**: 6-8 hours

---

## 🎯 IMPLEMENTATION ROADMAP

### Phase 1: Foundation (HIGH Priority) - 2-3 days

**Goal**: Enable quality tools to detect and guide Unit of Work + Service Layer

**Feng Shui**:
1. ✅ Unit of Work Pattern Detector (4-6 hours)
2. ✅ Service Layer Pattern Detector (4-6 hours)

**Gu Wu**:
3. ✅ Unit of Work Test Generator (6-8 hours)
4. ✅ Service Layer Test Generator (4-6 hours)

**Shi Fu**:
5. ✅ Pattern Adoption Tracker (4-6 hours)

**Total Effort**: 22-32 hours (2-3 days full-time, 1-2 weeks part-time)

**Benefits**:
- ✅ Feng Shui prevents Unit of Work violations
- ✅ Gu Wu generates atomic transaction tests
- ✅ Shi Fu tracks pattern impact
- ✅ Ready when we implement Unit of Work (Priority 1)

---

### Phase 2: Advanced Patterns (MEDIUM Priority) - 2-3 days

**Goal**: Expand to Aggregate + Domain Events detection

**Feng Shui**:
1. ✅ Aggregate Pattern Detector (6-8 hours)
2. ✅ Domain Events Pattern Detector (4-6 hours)

**Gu Wu**:
3. ✅ Aggregate Test Generator (6-8 hours)
4. ✅ Domain Events Test Generator (4-6 hours)

**Shi Fu**:
5. ✅ Pattern Impact Dashboard (6-8 hours)

**Total Effort**: 26-36 hours (2-3 days full-time, 1-2 weeks part-time)

**Benefits**:
- ✅ Feng Shui enforces data integrity (Aggregate)
- ✅ Gu Wu tests invariants automatically
- ✅ Shi Fu quantifies pattern ROI

---

### Phase 3: Future Patterns (LOW Priority) - 1-2 days

**Goal**: Support Message Bus + CQRS (when needed)

**Implementation**: Only when patterns are actually used in codebase

---

## 💡 STRATEGIC BENEFITS

### For Each Tool

**Feng Shui Benefits**:
- ✅ **Learns from architecture**: As we implement patterns, Feng Shui learns
- ✅ **Prevents regression**: Can't accidentally revert to old patterns
- ✅ **Educational**: Teaches team DDD best practices
- ✅ **Proactive**: Catches violations at commit time (pre-commit hook)

**Gu Wu Benefits**:
- ✅ **Pattern-aware testing**: Knows how to test each DDD pattern
- ✅ **Auto-generates fixtures**: FakeUnitOfWork, mock aggregates, etc.
- ✅ **Faster tests**: Mocks for unit tests, real for integration
- ✅ **Coverage guidance**: "You need atomicity tests for this UoW"

**Shi Fu Benefits**:
- ✅ **Quantifies value**: Shows ROI of DDD patterns (data!)
- ✅ **Guides decisions**: "Implement UoW next for 40% test improvement"
- ✅ **Proves impact**: Before/after metrics for stakeholders
- ✅ **Long-term vision**: Tracks DDD maturity over time

---

### For The Codebase

**Quality Improvements**:
- ✅ **+40% test reliability** (Unit of Work eliminates transaction flakiness)
- ✅ **+70% data integrity** (Aggregate enforces invariants)
- ✅ **+50% decoupling** (Domain Events separate concerns)
- ✅ **+30% maintainability** (Service Layer clarity)

**Developer Experience**:
- ✅ **Pre-commit feedback**: Feng Shui catches violations instantly
- ✅ **Auto-generated tests**: Gu Wu creates pattern-specific tests
- ✅ **Clear guidance**: Shi Fu recommends next best pattern
- ✅ **Data-driven decisions**: Metrics prove patterns work

---

## 🎓 INTEGRATION PHILOSOPHY

### Key Principles

**1. Learn from Evolution**
> "Quality tools should adapt as architecture evolves."

We implemented Repository Pattern v3.0.0 → Feng Shui learned to detect it (v4.6)  
We implement Unit of Work → Feng Shui learns that too

**2. Proactive, Not Reactive**
> "Catch violations before they enter codebase."

Pre-commit hooks prevent bad patterns from being committed

**3. Quantify Impact**
> "Show the business value of DDD patterns with data."

Shi Fu tracks: Pattern adoption → Quality metrics → ROI

**4. Teach, Don't Block**
> "Violations are teaching moments, not roadblocks."

Clear recommendations: "Use Unit of Work for atomicity (see cosmic-python-patterns.md)"

---

## 🚀 RECOMMENDED NEXT STEPS

### Option 1: Start Phase 1 Now ⭐ **RECOMMENDED**

**Why**: 
- Unit of Work is Priority 1 (we're about to implement it)
- Quality tools should be ready when pattern goes live
- 2-3 days investment, high ROI

**What**:
1. Feng Shui: Unit of Work + Service Layer detectors (8-12 hours)
2. Gu Wu: Unit of Work + Service Layer test generators (10-14 hours)
3. Shi Fu: Pattern Adoption Tracker (4-6 hours)

**Outcome**: Quality ecosystem ready for Unit of Work implementation

---

### Option 2: Implement Unit of Work First, Then Enhance Tools

**Why**:
- See real pattern in action before building detectors
- Learn from implementation challenges
- Tools can analyze real code

**What**:
1. Implement Unit of Work pattern (1-2 days)
2. Use it in P2P workflows (invoice + PO + audit log)
3. Then add quality tool support (Phase 1)

**Outcome**: Tools learn from real implementation

---

### Option 3: Incremental Approach

**Why**:
- Test integration incrementally
- Start with simplest detector (Service Layer)
- Expand as we gain confidence

**What**:
1. Week 1: Feng Shui Service Layer detector (4-6 hours)
2. Week 2: Gu Wu Service Layer test generator (4-6 hours)
3. Week 3: Shi Fu pattern tracker (4-6 hours)
4. Week 4: Unit of Work support (all tools)

**Outcome**: Gradual, low-risk integration

---

## 📊 SUCCESS METRICS

### How to Measure Success

**Feng Shui**:
- ✅ Detects 100% of Unit of Work violations
- ✅ Pre-commit hook prevents bad patterns
- ✅ Zero false positives on compliant code

**Gu Wu**:
- ✅ Auto-generates 80%+ of pattern tests
- ✅ Tests pass on first generation (no manual fixes)
- ✅ Coverage increases 15-20% from generated tests

**Shi Fu**:
- ✅ Tracks pattern adoption accurately
- ✅ Correlations show expected improvements (±10%)
- ✅ Recommendations guide team decisions

**Overall**:
- ✅ **+40% test reliability** after Unit of Work
- ✅ **+70% data integrity** after Aggregate
- ✅ **27 → 80+** DDD maturity score over 6 months

---

## 🎯 CONCLUSION

**The Opportunity**: Our quality ecosystem (Feng Shui, Gu Wu, Shi Fu) can become **DDD pattern-aware**, just like it became Repository Pattern-aware in v4.6.

**The Vision**: Quality tools that:
- ✅ Detect pattern violations proactively
- ✅ Generate pattern-specific tests automatically
- ✅ Quantify pattern impact with data
- ✅ Guide architectural evolution

**The ROI**:
- **Phase 1** (2-3 days) → Ready for Unit of Work (Priority 1)
- **Phase 2** (2-3 days) → Full DDD pattern support
- **Long-term** → +40-70% quality improvements

**The Question**: Should we integrate DDD patterns into quality tools **before** or **after** implementing Unit of Work?

---

**Related Documents**:
- [[Cosmic Python Patterns]] - The 8 DDD patterns
- [[Repository Pattern Modular Architecture]] - Our v3.0.0 implementation
- [[Feng Shui Phase 4-17 Multi-Agent]] - Current Feng Shui capabilities
- [[Gu Wu Phase 7 Intelligence]] - Current Gu Wu capabilities
- [[Shi Fu Phase 5 Growth Guidance]] - Current Shi Fu capabilities

**Status**: 🟡 PROPOSAL - Awaiting user decision