# Configuration-Based Dependency Injection Pattern

**Created**: 2026-02-15  
**Status**: ✅ ACTIVE STANDARD  
**Applies To**: All backend modules with dependencies

---

## Core Principle

> **"Configure in module.json, wire in server.py"**

All module configuration (database paths, API keys, feature flags) lives in `module.json`. The DI container in `server.py` reads this configuration and wires dependencies at startup.

---

## Architecture Pattern

```
module.json (config) → server.py (DI container) → Module layers
                              ↓
                   Repository → Facade → API
                   (leaf)      (middle)  (top)
```

### Benefits

✅ **Centralized Configuration**: All module settings in one place  
✅ **No Hardcoded Values**: Server reads from module.json  
✅ **Testable**: Easy to inject mock dependencies  
✅ **Maintainable**: Change config without touching code  
✅ **Consistent**: Same pattern across all modules  
✅ **Clear Dependencies**: Explicit at every layer  

---

## Implementation Pattern

### 1. Define Configuration in module.json

```json
{
  "name": "my_module",
  "version": "1.0.0",
  "backend": {
    "database_path": "database/my_module.db",
    "api_key": "${API_KEY}",
    "cache_ttl": 3600
  }
}
```

**Configuration Fields**:
- `database_path`: Database file location (relative to project root)
- Environment variables: Use `${VAR_NAME}` syntax
- Feature flags: Boolean or string values
- Resource paths: CSN directories, cache locations, etc.

### 2. Create DI Container in server.py

```python
def configure_my_module(app):
    """
    Configure my_module with proper Dependency Injection
    
    Architecture:
        Repository (leaf) → Facade (middle) → API (top)
    
    Benefits:
    - No Service Locator anti-pattern
    - Configuration from module.json (centralized)
    - Easy to test (inject mocks)
    - Clear dependencies
    """
    import json
    from pathlib import Path
    from modules.my_module.repositories import MyRepository
    from modules.my_module.facade import MyFacade
    from modules.my_module.backend import MyAPI, create_blueprint
    
    # 1. Load configuration from module.json
    module_json_path = Path('modules/my_module/module.json')
    with open(module_json_path, 'r') as f:
        config = json.load(f)
    
    # 2. Create repository (leaf dependency) with config
    db_path = Path(config['backend']['database_path'])
    repository = MyRepository(db_path)
    
    # 3. Create facade (middle layer) with injected repository
    facade = MyFacade(repository)
    
    # 4. Create API instance (top layer) with injected facade
    api_instance = MyAPI(facade)
    
    # 5. Create and register blueprint
    blueprint = create_blueprint(api_instance)
    app.register_blueprint(blueprint)
    
    print(f"✅ {config['name']} module configured with Dependency Injection")
    return api_instance

# Wire up module
configure_my_module(app)
```

### 3. Repository Layer (Leaf - No DI Needed)

```python
class MyRepository:
    """Repository with simple constructor - no DI needed at this layer"""
    
    def __init__(self, db_path: Path):
        """
        Args:
            db_path: Database file path (from module.json config)
        """
        self.db_path = db_path
        self.connection = sqlite3.connect(str(db_path))
```

**Why no DI here?**: Repository is the leaf node - it just needs configuration values.

### 4. Facade Layer (Middle - Constructor Injection)

```python
class MyFacade:
    """Facade with constructor injection"""
    
    def __init__(self, repository: MyRepository):
        """
        Args:
            repository: Injected repository instance
        """
        self.repository = repository
    
    def get_data(self) -> Dict:
        """Business logic using injected repository"""
        return self.repository.query_data()
```

### 5. API Layer (Top - Constructor Injection)

```python
class MyAPI:
    """API with constructor injection"""
    
    def __init__(self, facade: MyFacade):
        """
        Args:
            facade: Injected facade instance
        """
        self.facade = facade
    
    def handle_request(self):
        """Endpoint logic using injected facade"""
        result = self.facade.get_data()
        return jsonify(result), 200

def create_blueprint(api_instance: MyAPI) -> Blueprint:
    """Factory to create blueprint with injected API"""
    bp = Blueprint('my_module', __name__)
    
    @bp.route('/data')
    def get_data():
        return api_instance.handle_request()
    
    return bp
```

### 6. Module Exports (__init__.py)

```python
"""My Module Backend"""
from .api import MyAPI, create_blueprint

__all__ = ['MyAPI', 'create_blueprint']
```

---

## Real-World Examples

### Example 1: data_products_v2

**module.json**:
```json
{
  "backend": {
    "database_path": "database/p2p_data.db"
  }
}
```

**server.py**:
```python
def configure_data_products_v2(app):
    # Load config from module.json
    config = load_module_config('data_products_v2')
    
    # Create repository with config
    sqlite_repo = SQLiteDataProductRepository(
        db_path=Path(config['backend']['database_path'])
    )
    
    # Inject into facade
    facade = DataProductsFacade(repository=sqlite_repo)
    
    # Inject into API
    api = DataProductsV2API(sqlite_facade=facade)
    
    # Register
    blueprint = create_blueprint(api)
    app.register_blueprint(blueprint)
```

### Example 2: knowledge_graph_v2

**module.json**:
```json
{
  "backend": {
    "database_path": "database/p2p_graph.db",
    "csn_directory": "docs/csn"
  }
}
```

**server.py**:
```python
def configure_knowledge_graph_v2(app):
    # Load config from module.json
    config = load_module_config('knowledge_graph_v2')
    
    # Create repository with config
    cache_repo = SqliteGraphCacheRepository(
        Path(config['backend']['database_path'])
    )
    
    # Create facade with config + injected repo
    facade = KnowledgeGraphFacadeV2(
        cache_repo,
        Path(config['backend'].get('csn_directory', 'docs/csn'))
    )
    
    # Inject into API
    api = KnowledgeGraphV2API(facade)
    
    # Register
    blueprint = create_blueprint(api)
    app.register_blueprint(blueprint)
```

---

## Anti-Patterns to Avoid

### ❌ DON'T: Hardcode Paths in server.py

```python
# ❌ BAD: Hardcoded configuration
def configure_module(app):
    db_path = Path('database/my_data.db')  # HARDCODED
    repo = MyRepository(db_path)
```

### ❌ DON'T: Service Locator Pattern

```python
# ❌ BAD: Service Locator
class MyAPI:
    def handle_request(self):
        facade = get_facade()  # Global lookup
        return facade.get_data()
```

### ❌ DON'T: Factory Methods in API

```python
# ❌ BAD: Factory method instead of DI
class MyAPI:
    @staticmethod
    def get_facade():
        repo = MyRepository('hardcoded.db')
        return MyFacade(repo)
```

### ✅ DO: Configuration + Constructor Injection

```python
# ✅ GOOD: Config from module.json + Constructor injection
def configure_module(app):
    config = load_module_config('my_module')
    db_path = Path(config['backend']['database_path'])
    repo = MyRepository(db_path)
    facade = MyFacade(repo)
    api = MyAPI(facade)
    blueprint = create_blueprint(api)
    app.register_blueprint(blueprint)
```

---

## Testing Benefits

### Unit Tests (Mock Dependencies)

```python
def test_api_endpoint():
    # ✅ Easy to mock with DI
    mock_facade = Mock(spec=MyFacade)
    mock_facade.get_data.return_value = {'status': 'ok'}
    
    api = MyAPI(mock_facade)  # Inject mock
    result = api.handle_request()
    
    assert result['status'] == 'ok'
```

### Integration Tests (Real Dependencies)

```python
@pytest.fixture
def configured_module():
    # ✅ Use test configuration
    test_config = {
        'backend': {
            'database_path': 'test_data.db'
        }
    }
    
    repo = MyRepository(Path(test_config['backend']['database_path']))
    facade = MyFacade(repo)
    return MyAPI(facade)
```

---

## Migration Checklist

When refactoring a module to configuration-based DI:

- [ ] Add `backend.database_path` to module.json
- [ ] Add other config fields as needed (API keys, paths, etc.)
- [ ] Create `configure_[module]()` function in server.py
- [ ] Load configuration from module.json
- [ ] Create Repository with config values
- [ ] Inject Repository into Facade
- [ ] Inject Facade into API
- [ ] Remove any hardcoded paths/values from code
- [ ] Update module `__init__.py` exports
- [ ] Remove factory methods from API class
- [ ] Write unit tests with mocked dependencies
- [ ] Verify smoke test passes
- [ ] Run Feng Shui quality gate

---

## Configuration Schema Guidelines

### Required Fields in module.json

```json
{
  "name": "module_name",
  "version": "1.0.0",
  "backend": {
    "database_path": "database/module.db"  // REQUIRED if uses database
  }
}
```

### Optional Fields

```json
{
  "backend": {
    "database_path": "database/module.db",
    "cache_ttl": 3600,                    // Cache time-to-live
    "api_endpoint": "https://api.example.com",
    "feature_flags": {
      "enable_cache": true,
      "enable_async": false
    },
    "resource_paths": {
      "csn_directory": "docs/csn",
      "templates": "modules/my_module/templates"
    }
  }
}
```

### Environment Variables

Use `${VAR_NAME}` syntax for secrets:

```json
{
  "backend": {
    "api_key": "${MY_API_KEY}",
    "database_url": "${DATABASE_URL}"
  }
}
```

Then resolve in DI container:

```python
import os

def configure_module(app):
    config = load_module_config('my_module')
    
    # Resolve environment variables
    api_key = os.getenv(config['backend']['api_key'].strip('${}'))
    
    # Use in dependency creation
    service = MyService(api_key=api_key)
```

---

## Quality Validation

### Feng Shui Checks

✅ **No hardcoded paths** in Python code  
✅ **No Service Locator** (`get_*()` factory calls)  
✅ **Constructor Injection** at Facade and API layers  
✅ **Configuration in module.json** (not scattered)  

### Gu Wu Checks

✅ **Unit tests use mocked dependencies**  
✅ **Integration tests use test configuration**  
✅ **No global state access in tests**  

---

## Frontend Configuration Pattern

Frontend modules receive dependencies via **DependencyContainer** and **EventBus** (NOT a separate config file).

### Current Pattern (App V2)

**Frontend modules use DI via factory pattern:**

```javascript
// modules/my_module/frontend/module.js

window.MyModuleFactory = function(container, eventBus) {
    
    // 1. RESOLVE DEPENDENCIES from DI container
    const dataSource = container.get('IDataSource');
    const logger = container.has('ILogger') 
        ? container.get('ILogger')
        : console;  // Fallback
    const cache = container.has('ICache') 
        ? container.get('ICache') 
        : null;  // Optional
    
    // 2. MODULE STATE (can include config)
    let currentView = null;
    let isInitialized = false;
    const config = {
        apiBaseUrl: '/api/my-module',
        cacheEnabled: true,
        refreshInterval: 30000
    };
    
    // 3. PUBLIC API
    return {
        getMetadata: function() {
            return {
                id: 'my_module',
                name: 'My Module',
                version: '1.0.0'
            };
        },
        
        initialize: async function() {
            // Use injected dependencies
            logger.log('Initializing...');
            const data = await dataSource.query('data');
            isInitialized = true;
        },
        
        render: function() {
            // Return SAPUI5 control
            return createMyView(dataSource, logger);
        }
    };
};
```

### Key Differences from Backend

| Aspect | Backend | Frontend |
|--------|---------|----------|
| **Config Source** | module.json loaded by server.py | Hardcoded in module.js OR passed via ModuleBootstrap |
| **DI Method** | Constructor injection (classes) | Factory function parameters |
| **Container** | server.py creates instances | DependencyContainer.get() |
| **Wiring** | Explicit in configure_[module]() | Implicit via factory parameters |

### Real Example: data_products_v2 Frontend

```javascript
window.DataProductsV2Factory = function(container, eventBus) {
    
    // ✅ Resolve dependencies from DI container
    const dataSource = container.get('IDataSource');
    const logger = container.has('ILogger') 
        ? container.get('ILogger')
        : console;
    
    // ✅ Module state (config hardcoded for now)
    let currentSource = 'sqlite';
    const defaultTimeout = 30000;
    
    // ✅ Public API
    return {
        initialize: async function() {
            await loadDataProducts();
        },
        render: function() {
            return createDataProductsV2Page(dataProducts, currentSource);
        }
    };
};
```

### Future Enhancement: Frontend Config from module.json

**Could be enhanced** to read config from module.json:

```javascript
window.MyModuleFactory = async function(container, eventBus) {
    // 1. Load module.json
    const response = await fetch('/modules/my_module/module.json');
    const moduleConfig = await response.json();
    const config = moduleConfig.frontend.config || {};
    
    // 2. Resolve dependencies
    const dataSource = container.get('IDataSource');
    
    // 3. Use config
    const apiBaseUrl = config.api_base_url || '/api/my-module';
    const refreshInterval = config.refresh_interval || 30000;
    
    return {
        initialize: async function() {
            // Use config values
            setInterval(() => refresh(), refreshInterval);
        }
    };
};
```

**Benefits**:
- ✅ Centralized configuration in module.json
- ✅ No hardcoded URLs/timeouts in JavaScript
- ✅ Environment-specific configs possible

**Note**: This is a future enhancement - current modules have config hardcoded in module.js

---

## Related Patterns

- [[Service Locator Anti-Pattern Solution]] - What NOT to do
- [[Data Products V2 DI Refactoring]] - Complete example
- [[Repository Pattern Modular Architecture]] - Repository layer design
- [[App v2 Configuration-Driven Architecture]] - Frontend configuration patterns

---

## Summary

**The Golden Rule**:
1. ✅ Define configuration in `module.json`
2. ✅ Load configuration in `configure_[module](app)`
3. ✅ Use configuration to create dependencies
4. ✅ Inject dependencies via constructors (not factories)
5. ✅ Register blueprint with Flask app

**Result**: Maintainable, testable, configurable modules with zero hardcoded values.