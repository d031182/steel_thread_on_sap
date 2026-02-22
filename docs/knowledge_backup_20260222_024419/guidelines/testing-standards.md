# Testing Standards

**Type**: Guideline  
**Category**: Quality Assurance  
**Created**: 2026-01-24  
**Updated**: 2026-01-25  
**Status**: Active

## Overview

Comprehensive testing standards to prevent production bugs through multi-layer testing strategy. These standards ensure code quality, catch integration issues, and validate data contracts before deployment.

## Related Documentation

- [[SAP UI5 Common Pitfalls]] - UI testing considerations
- [[Modular Architecture]] - Testing modular components
- [[HANA Connection Module]] - Example with 100% test coverage

## The Problem We Solve

### Root Cause: Insufficient Test Coverage

**What happened**: Feature Manager JSON structure mismatch
- Unit tests passed (15/15) ✅
- Production failed ❌
- Tests used mock data, not real file
- No integration testing
- No schema validation

**Lesson**: Unit tests alone aren't enough

## 5-Layer Testing Pyramid

```
                ┌─────────────────┐
                │   E2E Tests     │  ← Full user workflows
                └─────────────────┘
            ┌───────────────────────┐
            │  Integration Tests    │  ← API + File + DB
            └───────────────────────┘
        ┌───────────────────────────────┐
        │    Component Tests            │  ← Module interactions
        └───────────────────────────────┘
    ┌───────────────────────────────────────┐
    │        Unit Tests                     │  ← Individual functions
    └───────────────────────────────────────┘
┌───────────────────────────────────────────────┐
│         Schema/Contract Tests                 │  ← Data validation
└───────────────────────────────────────────────┘
```

### Layer Purposes

| Layer | Purpose | Coverage | Priority |
|-------|---------|----------|----------|
| **Schema/Contract** | Validate data structures | 100% | ⭐ Critical |
| **Unit** | Test individual functions | 100% | ⭐ Critical |
| **Component** | Test module interactions | 80% | High |
| **Integration** | Test system boundaries | 80% | ⭐ Critical |
| **E2E** | Test user workflows | 50% | Medium |

## Layer 1: Schema Validation Tests

### Purpose
Catch JSON/data structure mismatches immediately

### Implementation

**JSON Schema Definition**:
```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "required": ["version", "features"],
  "properties": {
    "version": {"type": "string"},
    "features": {
      "type": "object",
      "patternProperties": {
        "^[a-z-]+$": {
          "type": "object",
          "required": ["enabled", "displayName"],
          "properties": {
            "enabled": {"type": "boolean"},
            "displayName": {"type": "string"}
          }
        }
      }
    }
  }
}
```

**Validation Test**:
```python
# tests/schema_validation.test.py
import json
import jsonschema

def test_actual_json_file_structure():
    """Test real production file loads correctly"""
    # Use REAL file, not mock
    with open("feature_flags.json", 'r') as f:
        data = json.load(f)
    
    # Verify structure
    assert 'features' in data
    assert len(data['features']) > 0
    
    # Validate each feature
    for name, config in data['features'].items():
        assert 'enabled' in config
        assert 'displayName' in config
        assert 'description' in config

def test_json_schema_validation():
    """Validate against JSON schema"""
    with open("feature_flags.json", 'r') as f:
        data = json.load(f)
    
    with open("schemas/feature_flags_schema.json", 'r') as f:
        schema = json.load(f)
    
    jsonschema.validate(data, schema)
```

**Benefit**: Would have caught the Feature Manager bug! ✅

## Layer 2: Unit Tests

### Purpose
Test individual functions in isolation

### Standards

**Coverage Requirements**:
- ✅ 100% method coverage (all public methods)
- ✅ 100% branch coverage (all conditions)
- ✅ Test success scenarios
- ✅ Test error scenarios
- ✅ Test edge cases

### Example

```python
# tests/unit/feature_manager.test.py
from modules.feature_manager.backend import FeatureManager

class TestFeatureManager:
    def test_get_feature_exists(self):
        """Test retrieving existing feature"""
        fm = FeatureManager()
        feature = fm.get_feature("application-logging")
        
        assert feature is not None
        assert 'enabled' in feature
        assert 'displayName' in feature
    
    def test_get_feature_not_exists(self):
        """Test retrieving non-existent feature"""
        fm = FeatureManager()
        feature = fm.get_feature("nonexistent")
        
        assert feature is None
    
    def test_toggle_feature(self):
        """Test toggling feature state"""
        fm = FeatureManager()
        
        initial = fm.get_feature("test-feature")['enabled']
        fm.toggle_feature("test-feature")
        new = fm.get_feature("test-feature")['enabled']
        
        assert new != initial
```

**Run Tests**:
```bash
python -m pytest tests/unit/ -v --cov=modules
```

## Layer 3: Component Tests

### Purpose
Test module interactions and dependencies

### Example

```python
# tests/component/hana_data_products.test.py
from modules.hana_connection.backend import HanaConnectionService
from modules.data_products.backend import DataProductsService

def test_data_products_uses_hana_connection():
    """Test Data Products module uses HANA connection"""
    hana = HanaConnectionService()
    dp = DataProductsService(hana)
    
    # Query data product
    result = dp.get_data_product("Supplier")
    
    assert result is not None
    assert 'data' in result
    assert len(result['data']) > 0
```

## Layer 4: Integration Tests

### Purpose
Test system boundaries (API ↔ File, API ↔ Database)

### Critical Areas to Test

**1. File System Integration**:
```python
# tests/integration/file_operations.test.py
import requests
import json

def test_toggle_feature_updates_file():
    """Test API → File → Reload workflow"""
    
    # 1. Toggle via API
    response = requests.post(
        "http://localhost:5000/api/features/test/toggle"
    )
    assert response.status_code == 200
    new_state = response.json()['enabled']
    
    # 2. Verify file updated
    with open("feature_flags.json", 'r') as f:
        data = json.load(f)
        file_state = data['features']['test']['enabled']
        assert file_state == new_state
    
    # 3. Reload service (simulate restart)
    response = requests.post("/api/reload")
    
    # 4. Verify state persisted
    response = requests.get("/api/features/test")
    persisted = response.json()['feature']['enabled']
    assert persisted == new_state
```

**2. Database Integration**:
```python
# tests/integration/hana_queries.test.py
from modules.hana_connection.backend import HanaConnectionService

def test_query_data_products():
    """Test real HANA query execution"""
    conn = HanaConnectionService()
    
    result = conn.execute_query("""
        SELECT * FROM "_SAP_DB_ACCESS_DATA_PRODUCT_GATEWAY"
        ."_SAP_DATAPRODUCT_DELTA_CSN"
        WHERE REMOTE_SOURCE_NAME LIKE '%Supplier%'
        LIMIT 1
    """)
    
    assert result is not None
    assert 'CSN_JSON' in result[0]
```

**3. API Integration**:
```python
# tests/integration/api_workflows.test.py
import requests

def test_complete_feature_workflow():
    """Test complete user workflow"""
    
    # Get all features
    response = requests.get("/api/features")
    assert response.status_code == 200
    features = response.json()['features']
    assert len(features) > 0
    
    # Toggle a feature
    feature_id = list(features.keys())[0]
    response = requests.post(f"/api/features/{feature_id}/toggle")
    assert response.status_code == 200
    
    # Export config
    response = requests.get("/api/features/export")
    assert response.status_code == 200
    exported = response.json()
    
    # Reset to defaults
    response = requests.post("/api/features/reset")
    assert response.status_code == 200
```

## Layer 5: E2E UI Tests

### Purpose
Test actual browser interactions and user workflows

### Tools
- **Playwright** (recommended)
- Puppeteer
- Selenium

### Example

```javascript
// tests/e2e/feature-manager-ui.test.js
const { chromium } = require('playwright');

async function testToggleFeature() {
    const browser = await chromium.launch();
    const page = await browser.newPage();
    
    // Navigate
    await page.goto('http://localhost:5000/feature-manager');
    
    // Wait for load
    await page.waitForSelector('[data-feature="application-logging"]');
    
    // Get initial state
    const toggle = page.locator('[data-feature="application-logging"] .sapMSwitch');
    const initialState = await toggle.getAttribute('aria-checked');
    
    // Click toggle
    await toggle.click();
    
    // Wait for success message
    await page.waitForSelector('.sapMMessageStrip--Success');
    
    // Verify state changed
    const newState = await toggle.getAttribute('aria-checked');
    assert(newState !== initialState);
    
    await browser.close();
}
```

## Best Practices

### Rule 1: Test with Real Data ⭐ CRITICAL

**DON'T**:
```python
# ❌ Mock everything
def test_load_features():
    mock_data = {"test": {"enabled": True}}
    fm = FeatureManager(mock_data)
    assert fm.get_feature_count() == 1
```

**DO**:
```python
# ✅ Use actual production files
def test_load_features():
    fm = FeatureManager("feature_flags.json")  # Real file!
    assert fm.get_feature_count() > 0
    
    # Verify actual features exist
    assert "application-logging" in fm.features
    assert "feature-manager" in fm.features
```

### Rule 2: Test Integration Points ⭐ HIGH

Test where components meet:
- ✅ API ↔ File System
- ✅ API ↔ Database
- ✅ Module ↔ Module
- ✅ Frontend ↔ Backend

### Rule 3: Validate Data Structures ⭐ HIGH

**Use JSON Schemas**:
```python
# Define contract
schema = {
    "type": "object",
    "required": ["enabled", "displayName"]
}

# Validate
jsonschema.validate(feature_data, schema)
```

### Rule 4: Automate Everything ⭐ MEDIUM

**Pre-commit Hooks**:
```bash
#!/bin/sh
# .git/hooks/pre-commit

echo "Running tests..."
python -m pytest tests/ || exit 1
echo "✅ Tests passed!"
```

**CI/CD Pipeline**:
```yaml
# .github/workflows/test.yml
name: Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - run: pip install -r requirements.txt
      - run: pytest tests/ --cov=modules
```

### Rule 5: Test Like a User ⭐ MEDIUM

- ✅ Click buttons, don't just call APIs
- ✅ Test in actual browser
- ✅ Test edge cases (slow network, errors)
- ✅ Test responsive behavior
- ✅ Test keyboard navigation

## Testing Checklist

### For Every New Feature

- [ ] **Schema/Contract Tests**
  - [ ] JSON schema defined
  - [ ] Validation test created
  - [ ] Test with actual production files

- [ ] **Unit Tests**
  - [ ] All public methods tested
  - [ ] Success scenarios covered
  - [ ] Error scenarios covered
  - [ ] Edge cases covered
  - [ ] 100% coverage achieved

- [ ] **Integration Tests**
  - [ ] File system integration tested
  - [ ] Database integration tested (if applicable)
  - [ ] API integration tested
  - [ ] Complete workflows tested

- [ ] **UI Tests** (if UI exists)
  - [ ] User workflows automated
  - [ ] Visual regression tested
  - [ ] Responsive behavior verified

- [ ] **Documentation**
  - [ ] Test patterns documented
  - [ ] Edge cases documented
  - [ ] Known limitations documented

## Test Organization

### Directory Structure

```
tests/
├── schema_validation/     # Contract tests
│   ├── feature_flags.test.py
│   └── schemas/
│       └── feature_flags.json
│
├── unit/                  # Unit tests
│   ├── feature_manager.test.py
│   ├── hana_connection.test.py
│   └── ...
│
├── integration/           # Integration tests
│   ├── file_operations.test.py
│   ├── api_workflows.test.py
│   └── hana_queries.test.py
│
├── e2e/                   # End-to-end tests
│   ├── feature-manager-ui.test.js
│   └── hana-connection-ui.test.js
│
└── README.md              # Test documentation
```

## Coverage Goals

| Test Type | Target | Current | Status |
|-----------|--------|---------|--------|
| Schema Validation | 100% | 100% | ✅ |
| Unit Tests | 100% | 100% | ✅ |
| Component Tests | 80% | 60% | 🟡 |
| Integration Tests | 80% | 40% | 🔴 |
| E2E UI Tests | 50% | 20% | 🔴 |

## Common Test Scenarios

### Scenario 1: JSON File Loading
```python
def test_json_loading_scenarios():
    # Test nested structure (production)
    fm1 = FeatureManager("feature_flags.json")
    assert fm1.get_feature_count() > 0
    
    # Test flat structure (legacy)
    fm2 = FeatureManager("legacy_flags.json")
    assert fm2.get_feature_count() > 0
    
    # Test missing file (default initialization)
    fm3 = FeatureManager("nonexistent.json")
    assert fm3.get_feature_count() == 0
    
    # Test corrupt file (graceful fallback)
    fm4 = FeatureManager("corrupt.json")
    assert fm4.get_feature_count() == 0
```

### Scenario 2: Concurrent Operations
```python
import threading

def test_concurrent_toggles():
    """Test race condition handling"""
    fm = FeatureManager()
    
    def toggle_feature():
        fm.toggle_feature("test-feature")
    
    # Create 10 threads toggling same feature
    threads = [threading.Thread(target=toggle_feature) for _ in range(10)]
    
    # Start all threads
    for t in threads:
        t.start()
    
    # Wait for completion
    for t in threads:
        t.join()
    
    # Verify data integrity
    feature = fm.get_feature("test-feature")
    assert 'enabled' in feature  # No corruption
```

### Scenario 3: Error Recovery
```python
def test_error_recovery():
    """Test system recovery from errors"""
    fm = FeatureManager()
    
    # Simulate disk full error
    with mock.patch('builtins.open', side_effect=IOError("Disk full")):
        result = fm.save_feature("test", {"enabled": True})
        assert result['success'] == False
        assert 'error' in result
    
    # Verify state rollback
    feature = fm.get_feature("test")
    assert feature['enabled'] == False  # Original state preserved
```

## Tools and Libraries

### Python
- **pytest**: Unit and integration testing
- **pytest-cov**: Code coverage
- **jsonschema**: Schema validation
- **requests**: API testing
- **mock**: Mocking dependencies

### JavaScript
- **Playwright**: E2E browser testing
- **Jest**: Unit testing
- **jsdom**: DOM simulation

### CI/CD
- **GitHub Actions**: Automated testing
- **Pre-commit hooks**: Local validation

## Status

✅ **ACTIVE GUIDELINES** - Apply to all development

**Last Updated**: 2026-01-25  
**Next Review**: After major feature implementations  
**Compliance**: Required for all code changes

## References

- **Testing Best Practices**: [[SAP UI5 Common Pitfalls]]
- **Module Examples**: [[HANA Connection Module]]
- **Architecture**: [[Modular Architecture]]
- pytest docs: https://pytest.org
- JSON Schema: https://json-schema.org
- Playwright: https://playwright.dev