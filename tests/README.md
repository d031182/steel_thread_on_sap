# Gu Wu (顾武) Testing Framework

**Version**: 1.0.0  
**Philosophy**: "Attending to martial affairs with discipline and continuous improvement"  
**Status**: Phase 1 - Foundation Setup ✅

---

## 🎯 What is Gu Wu?

Gu Wu is a **self-healing, self-optimizing testing framework** that learns from test execution patterns to continuously improve test quality and efficiency - similar to how Feng Shui auto-corrects code organization.

### Core Principles

1. **Self-Learning**: Learn from test patterns, failures, and performance
2. **Self-Healing**: Auto-detect and suggest fixes for flaky/slow tests
3. **Self-Prioritizing**: Reorder tests based on failure probability
4. **Self-Optimizing**: Continuously improve test execution efficiency

### Parallel to Feng Shui

| Aspect | Feng Shui | Gu Wu |
|--------|-----------|-------|
| **Target** | Code Organization | Test Execution |
| **Method** | Auto-correction | Auto-optimization |
| **Goal** | Clean, organized code | Efficient, reliable tests |
| **Philosophy** | Continuous improvement | Continuous refinement |

---

## 📊 Test Pyramid Structure

```
        /\
       /  \      E2E Tests (10%)
      /____\     tests/e2e/
     /      \    - Critical user paths
    /________\   - Smoke tests
   /          \  
  /____________\ Integration Tests (20%)
 /              \ tests/integration/
/______________\  - Module interactions
                  - API contracts
                  
                  Unit Tests (70%)
                  tests/unit/
                  - Fast, isolated
                  - High coverage
```

---

## 📁 Directory Structure

```
tests/
├── unit/                   # 70% - Unit tests (< 5 seconds)
│   ├── modules/            # Per-module unit tests
│   │   ├── knowledge_graph/
│   │   ├── data_products/
│   │   └── login_manager/
│   └── core/               # Core infrastructure tests
│
├── integration/            # 20% - Integration tests (< 30 seconds)
│   ├── test_module_interactions.py
│   ├── test_api_contracts.py
│   ├── test_graph_cache_refresh_sync.py  # Example: cache sync
│   └── test_database_access.py
│
├── e2e/                    # 10% - E2E tests (< 10 minutes)
│   ├── critical_paths/     # Must-pass scenarios
│   └── smoke_tests/        # Quick validation
│
├── performance/            # Performance/load tests
│   └── test_api_load.py
│
├── security/               # Security tests
│   ├── test_authentication.py
│   └── test_authorization.py
│
├── guwu/                   # 🔥 Gu Wu Engine (Self-Optimization)
│   ├── __init__.py         # Core engine
│   ├── engine.py           # Main optimization engine
│   ├── metrics.py          # Metrics collection
│   ├── optimizer.py        # Test optimization logic
│   ├── insights.py         # Insights generation
│   ├── metrics.db          # Historical metrics (SQLite)
│   ├── coverage.json       # Coverage data
│   └── insights.html       # Generated insights report
│
├── conftest.py             # Shared fixtures
└── README.md               # This file
```

## ⚠️ Test Placement Rules (MANDATORY)

**❌ NEVER place tests in these locations:**
- `scripts/python/test_*.py` - Wrong location!
- Root directory `test_*.py` - Wrong location!
- `modules/[module]/tests/` alone - Must ALSO add to `tests/`

**✅ ALWAYS place tests in these locations:**

### Unit Tests → `tests/unit/modules/[module]/`
Tests single component in isolation.
```python
# tests/unit/modules/knowledge_graph/test_facade.py
@pytest.mark.unit
def test_facade_get_graph_returns_nodes():
    """Test facade returns graph with nodes"""
    # Test single component
```

### Integration Tests → `tests/integration/`
Tests interaction between 2+ components.
```python
# tests/integration/test_graph_cache_refresh_sync.py
@pytest.mark.integration
def test_cache_refresh_clears_both_caches():
    """Test that refresh clears ontology AND vis.js caches"""
    # Test component interaction
```

### E2E Tests → `tests/e2e/`
Tests complete user workflows.
```python
# tests/e2e/test_full_p2p_workflow.py
@pytest.mark.e2e
def test_user_can_complete_purchase_order_flow():
    """Test complete P2P workflow from PO to invoice"""
    # Test full workflow
```

---

## 🚀 Quick Start

### 1. Install Dependencies

```bash
pip install pytest pytest-cov pytest-mock pytest-asyncio pytest-timeout
```

### 2. Run All Tests

```bash
# Run complete test suite
pytest

# Run with coverage
pytest --cov=modules --cov=core

# Run specific layer
pytest tests/unit -m unit          # Unit tests only
pytest tests/integration -m integration  # Integration tests only
pytest tests/e2e -m e2e            # E2E tests only
```

### 3. Run Tests by Speed

```bash
pytest -m fast    # Fast tests (< 0.1s)
pytest -m "not slow"  # Exclude slow tests
```

### 4. View Coverage Report

```bash
pytest --cov=modules --cov=core --cov-report=html
# Open htmlcov/index.html in browser
```

---

## 🔥 Gu Wu Self-Optimization Features

### Phase 1 (Complete ✅)

- ✅ **Metrics Collection**: Track test timing, failures, coverage
- ✅ **Flaky Test Detection**: Auto-identify intermittent failures
- ✅ **Slow Test Detection**: Flag tests > 5 seconds
- ✅ **Coverage Tracking**: Monitor coverage trends
- ✅ **Test Prioritization**: Run likely-to-fail tests first

### Phase 2 (Complete ✅)

- ✅ **Redundancy Detection**: Identify overlapping test coverage (analyzer.py)
- ✅ **Smart Test Selection**: Skip tests unaffected by code changes (analyzer.py)
- 📋 **Auto-Parallelization**: Distribute slow tests across cores (Future)
- 📋 **Mutation Testing**: Validate test effectiveness (Future)
- 📋 **Performance Regression**: Detect test slowdowns (Future)

### Phase 3 (Future)

- 📋 **AI-Powered Insights**: ML-based test optimization suggestions
- 📋 **Predictive Failures**: Predict which tests will fail
- 📋 **Auto-Fix Suggestions**: Propose fixes for common failures
- 📋 **Test Generation**: Auto-generate missing tests

---

## 📝 Writing Tests

### Test Naming Convention

```python
# GOOD ✅
def test_login_with_valid_credentials_succeeds():
def test_get_products_when_database_empty_returns_empty_list():

# BAD ❌
def test_login():  # What about login?
def test_1():      # Meaningless
```

### Test Structure (AAA Pattern)

```python
import pytest

def test_feature_scenario_expected():
    """Clear description of what this test validates"""
    
    # ARRANGE - Setup test data
    user = create_test_user(username="testuser")
    product = create_test_product(name="TestProduct")
    
    # ACT - Execute the operation
    result = user.purchase(product)
    
    # ASSERT - Verify expected outcome
    assert result.status == "success"
    assert result.product == product
    assert user.purchased_products.contains(product)
```

### Using Fixtures

```python
import pytest

@pytest.fixture
def sample_user():
    """Create a test user (fresh for each test)"""
    user = User(username="testuser", email="test@example.com")
    yield user
    # Cleanup after test
    user.delete()

def test_user_can_login(sample_user):
    """Test uses the fixture"""
    result = sample_user.login("password123")
    assert result.success is True
```

### Parametrized Tests

```python
import pytest

@pytest.mark.parametrize("email,valid", [
    ("valid@email.com", True),
    ("invalid.email", False),
    ("no-at-sign.com", False),
])
def test_email_validation(email, valid):
    """Test email validation with multiple inputs"""
    assert validate_email(email) == valid
```

### Test Markers

```python
import pytest

@pytest.mark.unit  # Mark as unit test
@pytest.mark.fast  # Mark as fast test
def test_simple_calculation():
    assert 2 + 2 == 4

@pytest.mark.integration  # Mark as integration test
@pytest.mark.slow  # Mark as slow test
def test_database_integration():
    # Complex database test
    pass

@pytest.mark.critical  # Critical path - never skip
def test_user_can_purchase():
    pass
```

---

## 📊 Coverage Targets

| Component | Line Coverage | Branch Coverage | Status |
|-----------|---------------|-----------------|--------|
| **Core Services** | 90% | 85% | 🎯 Target |
| **Module APIs** | 85% | 80% | 🎯 Target |
| **Module Services** | 80% | 75% | 🎯 Target |
| **Integration Layer** | 70% | 65% | 🎯 Target |
| **E2E Critical Paths** | 100% | 100% | 🎯 Target |
| **Overall Minimum** | 70% | - | ✅ Enforced |

---

## 🔍 Gu Wu Insights

After running tests, Gu Wu generates insights:

```bash
# Run tests with Gu Wu enabled (default)
pytest

# View insights report
open tests/guwu/insights.html  # macOS/Linux
start tests/guwu/insights.html  # Windows
```

### Insights Include:

- 📈 **Coverage Trends**: Coverage over time
- ⚠️ **Flaky Tests**: Tests with intermittent failures
- 🐌 **Slow Tests**: Tests taking > 5 seconds
- 📊 **Test Distribution**: Pyramid compliance (70/20/10)
- 💡 **Recommendations**: Actionable improvement suggestions

---

## 🎓 Best Practices

### 1. Keep Unit Tests Fast

```python
# GOOD ✅ - Mock external dependencies
@pytest.fixture
def mock_database(monkeypatch):
    mock_db = MockDatabase()
    monkeypatch.setattr('app.database', mock_db)
    return mock_db

def test_get_user(mock_database):
    result = get_user(1)
    assert result.id == 1
```

### 2. Test One Thing Per Test

```python
# GOOD ✅ - Single responsibility
def test_user_creation_succeeds():
    user = create_user("test@example.com")
    assert user.email == "test@example.com"

def test_user_validation_fails_for_invalid_email():
    with pytest.raises(ValidationError):
        create_user("invalid-email")
```

### 3. Use Descriptive Assertions

```python
# GOOD ✅ - Clear failure messages
assert result.status == "success", f"Expected success, got {result.status}"
assert len(products) > 0, "Product list should not be empty"
```

### 4. Clean Up Test Data

```python
# GOOD ✅ - Use fixtures for cleanup
@pytest.fixture
def test_data():
    data = create_test_data()
    yield data
    cleanup_test_data(data)  # Auto cleanup after test
```

---

## 🚨 Common Pitfalls

### ❌ Don't Test Implementation Details

```python
# BAD ❌ - Tests internal implementation
def test_uses_cache():
    user = get_user(1)
    assert user._cache_hit is True  # Internal detail

# GOOD ✅ - Tests behavior
def test_get_user_returns_correct_data():
    user = get_user(1)
    assert user.id == 1
    assert user.email is not None
```

### ❌ Don't Use Sleep in Tests

```python
# BAD ❌ - Slow and unreliable
def test_async_operation():
    trigger_async_operation()
    time.sleep(5)  # Hope it's done by now
    assert operation_completed()

# GOOD ✅ - Use proper async or polling
@pytest.mark.asyncio
async def test_async_operation():
    await trigger_async_operation()
    result = await get_result()
    assert result.completed is True
```

---

## 🔥 Phase 2: Autonomous Capabilities

### Redundancy Detection

Analyzes test suite to find overlapping/redundant tests:

```bash
python -m tests.guwu.analyzer redundancy
```

**Output**: Report showing redundant tests with removal suggestions

**Example**:
```
[*] Summary:
   Total Tests: 19
   Redundant Tests: 1
   Potential Savings: 1/19 tests (5%)

[!] Removal Suggestions:
   [-] REMOVE: tests/unit/modules/sqlite_connection/test_sqlite_data_source.py
   [+] KEEP: tests/unit/modules/data_products/test_sqlite_data_source.py (better coverage)
```

### Smart Test Selection

Selects only tests affected by code changes:

```bash
python -m tests.guwu.analyzer smart-select <file1> <file2> ...
```

**Example**:
```bash
python -m tests.guwu.analyzer smart-select modules/knowledge_graph/backend/api.py
```

**Output**: Only runs tests that import the changed modules (typically 20-40% of suite)

**Benefits**:
- Faster CI/CD pipelines
- Quicker local testing
- Automatic test selection

---

## 📚 Related Documentation

- [[Comprehensive Testing Strategy]] - Full testing methodology
- [[Testing Standards]] - Detailed testing guidelines  
- [[Module Quality Gate]] - Quality enforcement tool
- `pytest.ini` - Gu Wu configuration
- `conftest.py` - Shared test fixtures
- `tests/guwu/analyzer.py` - Phase 2 autonomous capabilities

---

## 🆘 Troubleshooting

### Tests Not Found

```bash
# Verify pytest can discover tests
pytest --collect-only

# Check test file naming
# Must be: test_*.py or *_test.py
```

### Coverage Not Measuring

```bash
# Ensure pytest-cov is installed
pip install pytest-cov

# Run with explicit coverage
pytest --cov=modules --cov=core
```

### Gu Wu Not Working

```bash
# Check pytest.ini has Gu Wu enabled
# [guwu] section should have enabled = true

# Verify Gu Wu plugin loaded
pytest --version
```

---

## 📞 Support

**Questions?** Check these resources:
1. Read this README thoroughly
2. Review `docs/knowledge/guidelines/comprehensive-testing-strategy.md`
3. Check test examples in `tests/unit/modules/knowledge_graph/`
4. Ask in team chat

---

**Status**: ✅ Phase 1 & 2 Complete  
**Capabilities**: Metrics, Flaky Detection, Redundancy Analysis, Smart Selection  
**Version**: 2.0.0 (2026-02-05)
