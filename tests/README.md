# Tests Directory - Gu Wu API Contract Testing

**Reset**: February 15, 2026
**Philosophy**: Test API contracts, not implementation details
**Reference**: [[Gu Wu API Contract Testing Foundation]]

---

## Core Principle ⭐

> "The foundation of Gu Wu is to test the backend APIs and frontend APIs.  
> By testing consistently this API contract, you test implicitly all other  
> contributing functions without testing them explicitly."

**What This Means**:
- ✅ Write API contract tests (backend + frontend endpoints)
- ✅ ONE API test validates entire call chain (controller → service → repository → database)
- ❌ DON'T test every internal function explicitly
- ✅ Trust implementation, test the public contract

---

## Test Structure (API-Focused)

```
tests/
├── test_[module]_backend_api.py      # Backend business logic APIs
├── test_[module]_frontend_api.py     # Frontend metadata APIs
├── test_smoke.py                      # Module import validation
└── conftest.py                        # Minimal configuration
```

---

## Writing Tests (API Contract Focus)

### Backend API Test Template

```python
import pytest
import requests

@pytest.mark.e2e
@pytest.mark.api_contract
def test_endpoint_contract():
    """
    Test: [Endpoint] returns valid contract
    
    Frontend Dependency: [Adapter].[method]()
    
    Contract:
    - Must return 200 status
    - Must have 'success' field
    - Must have 'data' object
    
    ARRANGE
    """
    url = "http://localhost:5000/api/[module]/[endpoint]"
    
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
```

### Frontend API Test Template

```python
@pytest.mark.e2e
@pytest.mark.api_contract
def test_metadata_endpoint():
    """
    Test: Module metadata endpoint returns configuration
    
    Frontend Dependency: ModuleRegistry.loadModules()
    
    Contract:
    - Must have module in registry
    - Must have required metadata fields
    
    ARRANGE
    """
    url = "http://localhost:5000/api/modules/frontend-registry"
    
    # ACT
    response = requests.get(url, timeout=5)
    
    # ASSERT
    data = response.json()
    modules = data['modules']
    assert len(modules) > 0
```

---

## Running Tests

### All Tests
```bash
pytest tests/ -v
```

### API Contract Tests Only
```bash
pytest tests/ -v -m api_contract
```

### Specific Module
```bash
pytest tests/test_ai_assistant_backend_api.py -v
```

### With Gu Wu Intelligence
```bash
python -m tools.guwu run tests/
```

---

## What to Test (API-Focused)

### ✅ REQUIRED: API Contract Tests

**Backend APIs** (business logic):
- All endpoints that execute operations
- Request/response structure validation
- Error scenarios
- Example: `POST /api/ai-assistant/chat`

**Frontend APIs** (metadata/configuration):
- Module registry endpoints
- Feature flag endpoints
- Configuration endpoints
- Example: `GET /api/modules/frontend-registry`

### ✅ OPTIONAL: Smoke Tests

**Module Imports**:
- Verify modules can be imported
- Fast sanity checks
- Example: `from modules.ai_assistant.backend import api`

### ❌ NOT NEEDED: Internal Function Tests

**Don't Test Explicitly**:
- ❌ Service methods (tested via API)
- ❌ Repository queries (tested via API)
- ❌ Database helpers (tested via API)
- ❌ Utility functions used in API chain (tested via API)

**Exception**: Complex algorithms NOT in any API chain

---

## Benefits of API-First Testing

### 1. Speed: 60-300x Faster
- API test: < 1 second
- Browser test: 60-300 seconds
- **Real Example**: HIGH-19 saved 88% time (30 min vs 4-6 hours)

### 2. Implicit Coverage
- One API test validates entire call chain
- Controller, Service, Repository, Database all tested automatically
- 80-90% fewer tests needed

### 3. Refactoring-Friendly
- Internal changes don't break tests
- Only contract matters
- Maintenance burden reduced dramatically

### 4. Clear Documentation
- Tests document what API promises
- Frontend dependencies visible
- Contract requirements explicit

---

## Current Test Files

### 1. test_ai_assistant_backend.py (8 tests, 6 passing)
**Purpose**: Backend models & repositories
**Status**: 2 minor failures in ConversationService (signature mismatch)

### 2. test_smoke.py (9 tests, 9 passing ✅)
**Purpose**: Module import validation, infrastructure sanity checks
**Status**: All passing, fast execution (< 2 seconds)

### 3. test_ai_assistant_frontend_api.py (6 tests, server-optional)
**Purpose**: AI Assistant API contract validation
**Endpoints Tested**:
- Module registry (`/api/modules/frontend-registry`)
- Conversations CRUD (`/api/ai-assistant/conversations`)
- Chat API (`/api/ai-assistant/chat`)
- SQL execution (`/api/ai-assistant/sql/execute`)

---

## Old Tests

**Location**: `archive/tests_backup_2026_02_15/`
**Count**: 198 tests
**Status**: Preserved for reference (had pytest I/O errors)

**Can be restored selectively** if specific tests valuable:
```bash
cp archive/tests_backup_2026_02_15/unit/[specific_test].py tests/
```

---

## Next Steps

### Immediate
1. Add API contract tests for data_products_v2 module
2. Add API contract tests for knowledge_graph_v2 module
3. Fix 2 ConversationService test failures

### Future
1. Gradually add API tests for all modules
2. Remove redundant internal function tests from archive
3. Maintain API-first testing discipline

---

## References

- [[Gu Wu API Contract Testing Foundation]] - Core methodology
- [[API-First Contract Testing Methodology]] - Complete guide
- [[Frontend API Testing Breakthrough]] - HIGH-16/19 lessons
- `.clinerules` Section 4 - Gu Wu testing standards
- `docs/knowledge/INDEX.md` - All documentation