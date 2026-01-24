# Tests Directory

Root-level tests for the P2P Data Products project.

## 📁 Structure

```
tests/
├── integration/     - Integration tests for modules and APIs
└── manual/          - Manual test files and HTML test pages
```

## 🧪 Integration Tests

**Location**: `tests/integration/`

### Available Tests

1. **test_feature_manager.py** - Feature Manager module tests
   ```bash
   python tests/integration/test_feature_manager.py
   ```

2. **test_api_playground.py** - API Playground test server
   ```bash
   python tests/integration/test_api_playground.py
   # Opens test server on http://localhost:5002
   ```

3. **test_server_simple.py** - Simple test server for Feature Manager API
   ```bash
   python tests/integration/test_server_simple.py
   # Opens test server on http://localhost:5001
   ```

## 🎨 Manual Tests

**Location**: `tests/manual/`

### Available Test Pages

1. **test_feature_manager_ui.html** - Feature Manager UI manual test
   - Open in browser to test Feature Manager frontend
   - Tests API integration and UI components

## 📝 Running Tests

### Quick Start

```bash
# Run Feature Manager tests
python tests/integration/test_feature_manager.py

# Start API Playground (test all module APIs)
python tests/integration/test_api_playground.py

# Start simple test server (Feature Manager only)
python tests/integration/test_server_simple.py
```

### Test Coverage

- **Core Infrastructure**: `core/backend/test_core_infrastructure.py` (19 tests)
- **Feature Manager**: `tests/integration/test_feature_manager.py`
- **API Playground**: `tests/integration/test_api_playground.py`
- **Module-specific**: Each module has its own `tests/` directory

## 🎯 Test Standards

All tests follow the project's development guidelines:

- ✅ **API-First**: Tests run without UI dependencies
- ✅ **100% Coverage**: All public methods tested
- ✅ **Fast**: Tests complete in < 5 seconds
- ✅ **Isolated**: Use mocks for external dependencies
- ✅ **Clear**: Test names describe what they test

## 📚 Additional Testing

### Module Tests

Each module has its own test directory:
- `modules/feature-manager/tests/`
- `modules/api-playground/tests/`
- `modules/[module-name]/tests/`

### Core Tests

Core infrastructure tests:
- `core/backend/test_core_infrastructure.py`

---

**Total Integration Tests**: 3 test files  
**Total Manual Tests**: 1 test page  
**Organization**: By test type (integration vs manual)  
**Purpose**: Ensure quality and catch regressions early