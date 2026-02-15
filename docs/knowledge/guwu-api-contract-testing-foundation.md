# Gu Wu API Contract Testing Foundation

**Date**: 2026-02-15
**Version**: 1.0
**Status**: Core Methodology
**Related**: [[API-First Contract Testing Methodology]], [[Gu Wu Testing Framework]], [[Frontend API Testing Breakthrough]]

---

## Core Principle

> "The foundation of Gu Wu is to test the backend APIs and frontend APIs.  
> By testing consistently this API contract, you test implicitly all other  
> contributing functions without testing them explicitly."

This is the **fundamental insight** that transforms testing from a burden into an efficient, elegant practice.

---

## The Two API Layers

### 1. Backend APIs - Business Logic

**What**: Endpoints that execute business operations

**Examples**:
- `POST /api/ai-assistant/chat` - Send message, get AI response
- `GET /api/data-products` - Retrieve data products list
- `POST /api/knowledge-graph/query` - Execute graph query

**What Gets Tested Implicitly**:
```
API Test (1 request)
  ↓
Flask Route Handler
  ↓
Service Layer (e.g., AgentService.generate_response())
  ↓
Repository Layer (e.g., ConversationRepository.get())
  ↓
Database Layer (e.g., SQLite query execution)
  ↓
All validated by ONE API contract test!
```

### 2. Frontend APIs - Metadata & Configuration

**What**: Endpoints that provide module configuration, feature flags, UI metadata

**Examples**:
- `GET /api/modules/frontend-registry` - Module metadata for bootstrap
- `GET /api/feature-flags` - Feature toggle states
- `GET /api/modules/[name]/config` - Module-specific configuration

**What Gets Tested Implicitly**:
```
API Test (1 request)
  ↓
FrontendModuleRegistry.get_all_modules()
  ↓
ModuleLoader.load_module()
  ↓
module.json parsing
  ↓
Blueprint registration
  ↓
All validated by ONE API contract test!
```

---

## Philosophy: Test the Contract, Trust the Implementation

### The Old Way (Explicit Testing) ❌

```python
# Too granular - maintenance burden
def test_service_method():
    service = MyService()
    result = service.process()
    assert result == expected

def test_repository_method():
    repo = MyRepository()
    result = repo.query()
    assert result == expected

def test_database_query():
    db = Database()
    result = db.execute()
    assert result == expected

# Result: 3 tests, brittle, refactoring breaks tests
```

### The Gu Wu Way (API Contract Testing) ✅

```python
# One test validates entire chain
@pytest.mark.api_contract
def test_api_endpoint_contract():
    """Test: API endpoint returns valid contract"""
    # This ONE test validates:
    # - Controller routing
    # - Service logic
    # - Repository queries
    # - Database execution
    # - Response serialization
    
    response = requests.post(url, json=payload)
    assert response.status_code == 200
    assert 'success' in response.json()
    assert 'data' in response.json()

# Result: 1 test, robust, refactoring preserves test
```

---

## Speed Advantage: 60-300x Faster

### API Testing
- **Execution**: < 1 second (requests library)
- **Setup**: None (just HTTP request)
- **Reliability**: 99.9% (no browser crashes)
- **Automation**: CI/CD friendly

### Browser Testing
- **Execution**: 60-300 seconds (Puppeteer/Playwright)
- **Setup**: Launch browser, wait for page load, wait for JavaScript
- **Reliability**: 70-80% (browser crashes, timing issues)
- **Automation**: Complex, resource-intensive

### Real Example (HIGH-19)
```
Bug: Frontend not loading module metadata

API Test Approach:
  1. curl http://localhost:5000/api/modules/frontend-registry (1 second)
  2. See missing field immediately
  3. Fix backend API
  4. Re-test (1 second)
  Total: 30 minutes

Browser Test Approach:
  1. Launch browser (30 seconds)
  2. Wait for page load (30 seconds)
  3. Open console (10 seconds)
  4. Click through UI (60 seconds)
  5. Debug JavaScript (3-4 hours!)
  6. Realize backend API issue
  Total: 4-6 hours

Savings: 88% time saved (30 min vs 4-6 hours)
```

---

## Implicit Coverage Principle

### How It Works

When you test an API endpoint, you **automatically exercise**:

1. **Request Handling**
   - Route parsing
   - Parameter validation
   - Authentication/authorization

2. **Business Logic**
   - Service methods
   - Business rules
   - Data transformations

3. **Data Access**
   - Repository queries
   - Database operations
   - Cache interactions

4. **Response Generation**
   - Serialization
   - Error handling
   - Status codes

**All from ONE API test!**

### What You DON'T Need to Test Explicitly

❌ **Internal Service Methods** - Tested via API call
❌ **Repository Queries** - Tested via API call
❌ **Database Helpers** - Tested via API call
❌ **Utility Functions** - Tested via API call (if used in API chain)

✅ **ONLY Test Explicitly**:
- Complex algorithms used OUTSIDE API chain
- Standalone utilities with no API endpoint
- Critical edge cases not covered by API workflows

---

## Test Structure (API-Focused)

```
tests/
├── test_[module]_backend_api.py      # Backend business logic APIs
│   ├── TestChatAPI
│   ├── TestDataProductsAPI
│   └── TestKnowledgeGraphAPI
│
├── test_[module]_frontend_api.py     # Frontend metadata APIs
│   ├── TestModuleRegistryAPI
│   ├── TestFeatureFlagsAPI
│   └── TestConfigurationAPI
│
├── test_smoke.py                      # Module import validation
│   ├── TestModuleImports
│   ├── TestCoreServices
│   └── TestToolsAvailable
│
└── conftest.py                        # Shared fixtures
```

---

## Contract Test Template

```python
"""
[Module] API Contract Tests
============================
Tests for [module] API endpoints.

Following Gu Wu API Contract Testing:
- Test contracts, not implementation
- Use requests (< 1 second execution)
- AAA pattern
"""

import pytest
import requests


class Test[Module]BackendAPI:
    """Test [module] backend business logic API"""
    
    @pytest.mark.e2e
    @pytest.mark.api_contract
    def test_endpoint_returns_valid_contract(self):
        """
        Test: [Endpoint] returns valid contract structure
        
        Frontend Dependency: [Adapter].[method]()
        
        Contract:
        - Must return 200 status
        - Must have 'success' field (boolean)
        - Must have 'data' object
        - [Additional requirements]
        
        ARRANGE
        """
        url = "http://localhost:5000/api/[module]/[endpoint]"
        payload = {"key": "value"}
        
        # ACT
        try:
            response = requests.post(url, json=payload, timeout=5)
        except requests.ConnectionError:
            pytest.skip("Server not running")
        
        # ASSERT
        assert response.status_code == 200
        data = response.json()
        assert 'success' in data
        assert data['success'] is True
        assert 'data' in data


class Test[Module]FrontendAPI:
    """Test [module] frontend metadata API"""
    
    @pytest.mark.e2e
    @pytest.mark.api_contract
    def test_metadata_endpoint_returns_config(self):
        """
        Test: Metadata endpoint returns module configuration
        
        Frontend Dependency: ModuleRegistry.loadModules()
        
        Contract:
        - Must return 200 status
        - Must have module in modules list
        - Must have required metadata fields
        
        ARRANGE
        """
        url = "http://localhost:5000/api/modules/frontend-registry"
        
        # ACT
        try:
            response = requests.get(url, timeout=5)
        except requests.ConnectionError:
            pytest.skip("Server not running")
        
        # ASSERT
        data = response.json()
        modules = data.get('modules', [])
        
        module = next((m for m in modules if m['name'] == '[module_name]'), None)
        assert module is not None
        assert 'version' in module
        assert 'enabled' in module
```

---

## Benefits

### 1. Efficiency
- **One test validates entire stack**
- **Implicit coverage** of all functions in call chain
- **No redundant tests** for internal functions

### 2. Speed
- **60-300x faster** than browser testing
- **< 1 second** per API test
- **Rapid feedback** during development

### 3. Robustness
- **Refactoring-friendly** (only contract matters)
- **Less brittle** (internal changes don't break tests)
- **Maintenance-light** (fewer tests to update)

### 4. Clarity
- **Tests document contracts** (what API promises)
- **Clear boundaries** (public vs private)
- **Intent-focused** (what matters to users)

---

## Anti-Patterns to Avoid

### ❌ Testing Every Internal Function

```python
# DON'T DO THIS - Redundant
def test_service_method():
    service = AgentService()
    result = service.generate_response("hello")
    assert result is not None

def test_repository_method():
    repo = ConversationRepository()
    session = repo.create()
    assert session is not None

# These are ALREADY tested via:
@pytest.mark.api_contract
def test_chat_api():
    response = requests.post("/api/ai-assistant/chat", json={"message": "hello"})
    assert response.status_code == 200
    # ^ This test exercises generate_response() and create() implicitly!
```

### ❌ Micro-Testing Implementation Details

```python
# DON'T DO THIS - Too granular
def test_format_response_adds_timestamp():
    formatted = _format_response(data)
    assert 'timestamp' in formatted

# DO THIS - Test at API level
@pytest.mark.api_contract
def test_api_response_has_timestamp():
    response = requests.get(url)
    assert 'timestamp' in response.json()
    # ^ This tests _format_response() implicitly AND ensures it's used correctly!
```

---

## When to Test Internal Functions Explicitly

**ONLY test explicitly if**:

1. **Complex Algorithm** - Not part of API chain
   ```python
   # Complex calculation utility
   def calculate_risk_score(factors):
       # 50 lines of complex logic
       pass
   
   # Worth explicit testing (not in API chain)
   def test_risk_score_calculation():
       score = calculate_risk_score(factors)
       assert score == expected
   ```

2. **Shared Utility** - Used across multiple APIs
   ```python
   # Date formatting utility
   def format_date(dt, format):
       pass
   
   # Test once, used by many APIs
   def test_date_formatting():
       formatted = format_date(dt, "YYYY-MM-DD")
       assert formatted == "2026-02-15"
   ```

3. **Critical Edge Cases** - Not covered by normal API workflows
   ```python
   # Edge case: Division by zero
   def test_handles_zero_division():
       result = calculate_percentage(0, 0)
       assert result == 0.0
   ```

**Rule of Thumb**: If a function is ONLY called from API chain → Test via API, not explicitly.

---

## Migration Guide (From Old Testing to Gu Wu)

### Before (Old Approach)
```python
# 50 tests for internal functions
tests/unit/modules/ai_assistant/
├── test_agent_service.py           # 10 tests
├── test_conversation_repository.py # 10 tests
├── test_conversation_service.py    # 10 tests
├── test_sql_execution_service.py   # 10 tests
└── test_api.py                     # 10 tests

# Maintenance burden: 50 tests to update when refactoring
```

### After (Gu Wu Approach)
```python
# 10 API contract tests cover same functionality
tests/
├── test_ai_assistant_backend_api.py   # 5 backend API tests
├── test_ai_assistant_frontend_api.py  # 5 frontend API tests
└── test_smoke.py                      # 3 smoke tests

# Maintenance: 10 tests, internal refactoring doesn't break tests
```

---

## Validation Checklist

**For AI Assistant to Use Before attempt_completion**:

1. ❓ Have I designed API contracts (backend + frontend)?
2. ❓ Have I written API contract tests with `@pytest.mark.api_contract`?
3. ❓ Have I tested APIs via `requests` (< 1 second execution)?
4. ❓ Are all API contract tests passing?
5. ❓ Am I testing internal functions that are already covered by API tests?
6. ❓ Did I avoid browser testing (use API testing instead)?

**If testing internal functions**: Ask: "Is this already tested via API contract?"

---

## Success Metrics

### Speed
- API test execution: < 1 second
- Browser test execution: 60-300 seconds
- **Result**: 60-300x faster debugging

### Coverage
- 1 API test = entire call chain
- Traditional: 5-10 tests for same coverage
- **Result**: 80-90% fewer tests needed

### Maintenance
- API contract preserved = tests stay green
- Internal refactoring = zero test changes
- **Result**: Refactoring-friendly codebase

---

## Real-World Evidence

### HIGH-19: 88% Time Savings
**Problem**: Frontend not loading module metadata
- **API Test Approach**: 30 minutes (curl → see issue → fix → verify)
- **Browser Approach**: 4-6 hours (launch → debug JS → find backend issue)
- **Savings**: 88% (30 min vs 4-6 hours)

### HIGH-16: Instant Root Cause
**Problem**: Button click not working
- **API Test**: `curl /api/modules/frontend-registry` (1 second)
- **Found**: Missing `eager_init` field in response
- **Fixed**: Add field to API response
- **Verified**: curl again (1 second)
- **Total**: 5 minutes vs 60+ minutes browser debugging

---

## Implementation Guide

### Step 1: Design API Contracts

```python
# Document expected contract
"""
POST /api/ai-assistant/chat

Request:
{
  "conversation_id": "uuid",
  "message": "string"
}

Response:
{
  "success": true,
  "content": "string",
  "timestamp": "ISO8601"
}
"""
```

### Step 2: Write Contract Test

```python
@pytest.mark.e2e
@pytest.mark.api_contract
def test_chat_api_contract():
    """Test: Chat API returns valid contract"""
    # ARRANGE
    url = "http://localhost:5000/api/ai-assistant/chat"
    payload = {
        "conversation_id": "test-id",
        "message": "Hello"
    }
    
    # ACT
    response = requests.post(url, json=payload, timeout=5)
    
    # ASSERT
    assert response.status_code == 200
    data = response.json()
    assert 'success' in data
    assert 'content' in data
    assert 'timestamp' in data
```

### Step 3: Implement API

```python
@app.route('/api/ai-assistant/chat', methods=['POST'])
def chat():
    data = request.json
    
    # Entire call chain executed here:
    # controller → service → repository → database
    result = agent_service.generate_response(
        conversation_id=data['conversation_id'],
        message=data['message']
    )
    
    return jsonify({
        'success': True,
        'content': result,
        'timestamp': datetime.utcnow().isoformat()
    })
```

### Step 4: Run Test

```bash
pytest tests/test_ai_assistant_backend_api.py::test_chat_api_contract -v

# < 1 second execution
# Validates entire stack automatically
```

---

## Common Questions

### Q: "But what if my service has complex logic?"

**A**: The API test will catch if that logic breaks. You don't need separate tests unless it's a standalone algorithm.

### Q: "What about edge cases in internal functions?"

**A**: Cover edge cases via API tests with different payloads. If API handles edge case, internal functions do too.

### Q: "Should I ever write unit tests for services?"

**A**: Only if service has complex logic NOT reachable via any API endpoint. 95% of time, API tests suffice.

### Q: "How do I test database layer?"

**A**: API tests execute real database queries. No need for explicit database tests.

### Q: "What about mocking?"

**A**: Minimize mocking. Use real dependencies when possible. API tests should exercise real stack.

---

## Integration with Gu Wu Intelligence

### Phase 7 Intelligence Engines

Even with API-focused testing, Gu Wu Intelligence provides:

1. **Recommendations Engine**
   - Identifies missing API contract tests
   - Suggests consolidation of redundant tests
   - Prioritizes test creation by risk

2. **Dashboard**
   - API test execution trends
   - Coverage via API tests
   - Performance metrics

3. **Predictive Analytics**
   - ML-powered failure forecasting
   - Pre-flight checks before commit

### Using Intelligence with API Tests

```bash
# Check if API tests cover all endpoints
python -m tools.guwu gaps

# Get recommendations for API test improvements
python -m tools.guwu recommend

# Predict which API tests might fail
python -m tools.guwu predict --pre-flight
```

---

## Migration Strategy

### Phase 1: Start with API Tests (Week 1)
1. Identify all API endpoints (backend + frontend)
2. Write contract tests for each endpoint
3. Run tests, verify APIs stable

### Phase 2: Remove Redundant Tests (Week 2)
1. Identify internal function tests covered by API tests
2. Delete redundant tests (keep only complex algorithms)
3. Verify coverage maintained via API tests

### Phase 3: New Development (Ongoing)
1. Design API contract FIRST
2. Write contract test
3. Implement API
4. Test via requests
5. Build UX on stable API

---

## Success Indicators

**You're doing it right when**:
- ✅ < 1 second per test execution
- ✅ Refactoring internal code doesn't break tests
- ✅ 80% fewer tests than before, same coverage
- ✅ Tests document API contracts clearly
- ✅ New developers understand API via tests

**You're doing it wrong when**:
- ❌ Tests break when refactoring internal functions
- ❌ Tests take >5 seconds to run
- ❌ 100+ tests for simple module
- ❌ Tests don't match actual API usage

---

## Key Takeaways

1. **Test contracts, not implementations** - APIs are the contract
2. **One API test validates entire chain** - Implicit coverage is powerful
3. **60-300x faster than browser testing** - Speed enables rapid iteration
4. **Refactoring-friendly** - Internal changes don't break tests
5. **Less is more** - Fewer, better tests beat many brittle tests

---

## References

- [[API-First Contract Testing Methodology]] - Complete workflow
- [[Gu Wu Testing Framework]] - Testing infrastructure
- [[Frontend API Testing Breakthrough]] - HIGH-16/19 lessons
- `.clinerules` Section 4 - Gu Wu API Contract Testing Foundation
- `tests/test_ai_assistant_frontend_api.py` - Example implementation