# Service Locator Anti-Pattern: Solution Guide

**Date**: 2026-02-09  
**Status**: BEST PRACTICE  
**Author**: P2P Development Team  
**Source**: Perplexity Research + Industry Best Practices 2024

## Problem: Service Locator Anti-Pattern

### What is Service Locator?
Service Locator is an **anti-pattern** where dependencies are fetched on-demand from a global registry instead of being explicitly injected. This creates **hidden dependencies** that violate SOLID principles.

### Example: Our `db_path` Issue
```python
# ❌ BAD: Service Locator Pattern
def get_facade(source: str):
    # API reads from Flask config (Service Locator)
    db_path = current_app.config.get('SQLITE_DB_PATH')
    return DataProductsFacade('sqlite', db_path=db_path)

# API → Facade → Factory → Repository: All pass db_path string
# Result: Hardcoded, not testable, violates DIP
```

### Why Service Locator Fails
1. **Hidden Dependencies**: Reader must guess what services are needed
2. **Runtime Errors**: Dependencies not declared upfront (no compile-time check)
3. **Violates ISP**: Interfaces become bloated with unused methods
4. **Testing Difficulties**: Shared singletons, hard to mock
5. **Tight Coupling**: Modules depend on global registry

**Sources**: [Service Locator violates SOLID](https://blog.ploeh.dk/2014/05/15/service-locator-violates-solid/), [Anti-pattern analysis](https://stitcher.io/blog/service-locator-anti-pattern)

---

## Solution: Configuration-Driven Dependency Injection

### Industry Best Practice (2024)
Replace Service Locator with **explicit DI** using **configuration files** (YAML/JSON) to declare and wire dependencies at startup.

**Key Principles**:
1. ✅ **Explicit Dependencies**: Declare in constructor, not fetch at runtime
2. ✅ **Configuration-Driven**: Centralize config in files (not scattered in code)
3. ✅ **Inversion of Control**: Framework controls dependency flow
4. ✅ **Convention over Configuration**: Standard patterns reduce boilerplate

---

## Python Backend Solution

### Approach: module.json + ModuleLoader DI

Each module declares dependencies in `module.json`, and `ModuleLoader` auto-wires them at app startup.

### 1. Declare Dependencies in module.json

```json
{
  "id": "data_products_v2",
  "name": "Data Products V2",
  "version": "2.0.0",
  
  "backend": {
    "blueprint": "modules.data_products_v2.backend:data_products_v2_api",
    "mount_path": "/api/v2/data-products",
    
    "dependencies": {
      "path_resolver": {
        "interface": "IDatabasePathResolver",
        "implementation": "ModuleOwnedPathResolver",
        "config": {
          "module_name": "data_products_v2"
        }
      }
    }
  }
}
```

**Key Addition**: `backend.dependencies` section declares:
- Interface needed (`IDatabasePathResolver`)
- Implementation to use (`ModuleOwnedPathResolver`)
- Configuration (module-specific settings)

### 2. ModuleLoader Reads Config & Auto-Wires

```python
# core/services/module_loader.py (ENHANCED)

class ModuleLoader:
    """
    Loads modules and auto-wires dependencies from module.json
    """
    
    def load_backend_module(self, module_name: str, module_config: dict):
        """
        Load backend module and inject dependencies
        
        Reads backend.dependencies from module.json and creates
        instances of required services, then injects them into
        the module's initialization.
        """
        backend_config = module_config.get('backend', {})
        
        # 1. Read dependency declarations
        deps_config = backend_config.get('dependencies', {})
        
        # 2. Resolve and instantiate dependencies
        resolved_deps = {}
        for dep_name, dep_spec in deps_config.items():
            interface = dep_spec['interface']
            impl_class = dep_spec['implementation']
            config = dep_spec.get('config', {})
            
            # 3. Create dependency instance
            resolver = self._create_dependency(impl_class, config)
            resolved_deps[dep_name] = resolver
        
        # 4. Import blueprint
        blueprint_path = backend_config['blueprint']
        blueprint = self._import_blueprint(blueprint_path)
        
        # 5. Inject dependencies into blueprint
        # Store in Flask app's DI container
        self.app.extensions[f'{module_name}_path_resolver'] = resolved_deps.get('path_resolver')
        
        # 6. Register blueprint with mount path
        mount_path = backend_config.get('mount_path', f'/api/{module_name}')
        self.app.register_blueprint(blueprint, url_prefix=mount_path)
        
        logger.info(f"Loaded {module_name} with injected dependencies: {list(resolved_deps.keys())}")
    
    def _create_dependency(self, class_name: str, config: dict):
        """
        Dynamically create dependency instance from config
        
        Example:
            class_name = "ModuleOwnedPathResolver"
            config = {"module_name": "data_products_v2"}
            → Returns: ModuleOwnedPathResolver() instance
        """
        # Import class dynamically
        if class_name == 'ModuleOwnedPathResolver':
            from core.services.database_path_resolvers import ModuleOwnedPathResolver
            return ModuleOwnedPathResolver()
        
        elif class_name == 'ConfigurablePathResolver':
            from core.services.database_path_resolvers import ConfigurablePathResolver
            config_path = config.get('config_path', 'config/database_paths.json')
            return ConfigurablePathResolver(config_path)
        
        # Add more as needed...
        else:
            raise ValueError(f"Unknown dependency class: {class_name}")
```

### 3. API Layer Gets Resolver from DI Container

```python
# modules/data_products_v2/backend/api.py (REFACTORED)

from flask import Blueprint, request, jsonify, current_app
from core.interfaces.database_path_resolver import IDatabasePathResolver

data_products_v2_api = Blueprint('data_products_v2', __name__)

def get_facade(source: str):
    """
    Get facade with injected dependencies (NO SERVICE LOCATOR)
    """
    # ✅ Get resolver from DI container (injected by ModuleLoader)
    path_resolver: IDatabasePathResolver = current_app.extensions['data_products_v2_path_resolver']
    
    if source == 'sqlite':
        # ✅ Pass resolver (not string path)
        return DataProductsFacade('sqlite', path_resolver=path_resolver)
    
    elif source == 'hana':
        # HANA doesn't need path resolver
        return DataProductsFacade('hana', host=..., port=..., ...)
```

**Key Changes**:
- ❌ OLD: `db_path = current_app.config.get('SQLITE_DB_PATH')` (Service Locator)
- ✅ NEW: `path_resolver = current_app.extensions['...']` (DI Container)

### 4. Facade Accepts Resolver (Not String)

```python
# modules/data_products_v2/facade/data_products_facade.py (REFACTORED)

from core.interfaces.database_path_resolver import IDatabasePathResolver

class DataProductsFacade:
    def __init__(
        self,
        source_type: str,
        path_resolver: IDatabasePathResolver = None,  # ✅ Interface injection
        host: str = None,
        port: int = None,
        ...
    ):
        """Initialize with injected dependencies"""
        self._repository = DataProductRepositoryFactory.create(
            source_type=source_type,
            path_resolver=path_resolver,  # ✅ Pass resolver
            host=host,
            port=port,
            ...
        )
```

### 5. Factory Accepts Resolver

```python
# modules/data_products_v2/repositories/repository_factory.py (REFACTORED)

from core.interfaces.database_path_resolver import IDatabasePathResolver

class DataProductRepositoryFactory:
    @staticmethod
    def create(
        source_type: str,
        path_resolver: IDatabasePathResolver = None,  # ✅ Interface injection
        host: str = None,
        ...
    ):
        if source_type == 'sqlite':
            if not path_resolver:
                raise ValueError("SQLite requires path_resolver")
            
            return SQLiteDataProductRepository(path_resolver)  # ✅ Inject resolver
        
        elif source_type == 'hana':
            return HANADataProductRepository(host, port, user, password)
```

### 6. Repository Uses Resolver

```python
# modules/data_products_v2/repositories/sqlite_data_product_repository.py (REFACTORED)

from core.interfaces.database_path_resolver import IDatabasePathResolver

class SQLiteDataProductRepository:
    def __init__(self, path_resolver: IDatabasePathResolver):  # ✅ Interface injection
        """Initialize with path resolver (not hardcoded path)"""
        # ✅ Resolve path using strategy pattern
        db_path = path_resolver.resolve_path('data_products_v2')
        
        # Pass resolved path to V1 service
        self._service = SQLiteDataProductsService(db_path)
```

---

## Benefits of Configuration-Driven DI

### 1. Testability
```python
# ✅ EASY: Mock resolver in tests
def test_facade():
    mock_resolver = Mock(spec=IDatabasePathResolver)
    mock_resolver.resolve_path.return_value = '/tmp/test.db'
    
    facade = DataProductsFacade('sqlite', path_resolver=mock_resolver)
    # Test in isolation!
```

### 2. Flexibility
```json
// Switch strategies per environment (no code changes)
{
  "dependencies": {
    "path_resolver": {
      "implementation": "ConfigurablePathResolver",  // Dev: custom paths
      // Or: "ModuleOwnedPathResolver"  // Prod: standard paths
      // Or: "TemporaryPathResolver"    // Test: temp paths
    }
  }
}
```

### 3. Explicit Dependencies
```python
# ✅ Reader sees exactly what's needed
def __init__(self, path_resolver: IDatabasePathResolver):
    # Clear: "I need a path resolver"
```

### 4. Centralized Configuration
```json
// Single source of truth (not scattered in code)
{
  "backend": {
    "dependencies": {
      "path_resolver": {...},
      "logger": {...},
      "cache": {...}
    }
  }
}
```

---

## Comparison: Before vs After

### Before (Service Locator)
```python
# API layer (hardcoded config access)
db_path = current_app.config.get('SQLITE_DB_PATH')

# Facade (accepts string)
def __init__(self, source, db_path: str):
    
# Factory (accepts string)
def create(source, db_path: str):

# Repository (accepts string)
def __init__(self, db_path: str):

# Issues:
# ❌ Hardcoded, scattered config
# ❌ Not testable (global state)
# ❌ Violates DIP (depend on concrete)
# ❌ 7 Feng Shui violations detected
```

### After (Configuration-Driven DI)
```python
# module.json (declare dependencies)
{
  "dependencies": {
    "path_resolver": {
      "interface": "IDatabasePathResolver",
      "implementation": "ModuleOwnedPathResolver"
    }
  }
}

# ModuleLoader (auto-wire at startup)
resolver = ModuleOwnedPathResolver()
app.extensions['data_products_v2_path_resolver'] = resolver

# API (get from DI container)
resolver = current_app.extensions['data_products_v2_path_resolver']

# Facade (accept interface)
def __init__(self, source, path_resolver: IDatabasePathResolver):

# Factory (accept interface)
def create(source, path_resolver: IDatabasePathResolver):

# Repository (accept interface)
def __init__(self, path_resolver: IDatabasePathResolver):
    db_path = path_resolver.resolve_path('module_name')

# Benefits:
# ✅ Centralized config (module.json)
# ✅ Testable (inject mocks)
# ✅ Follows DIP (depend on interface)
# ✅ 0 Feng Shui violations
```

---

## Implementation Checklist

### Phase 1: Add Configuration (Non-Breaking)
- [ ] Add `backend.dependencies` to module.json
- [ ] Enhance ModuleLoader to read dependencies config
- [ ] ModuleLoader instantiates resolvers at startup
- [ ] Store in `app.extensions` DI container
- [ ] Keep existing db_path as fallback

### Phase 2: Refactor Layers (Breaking)
- [ ] API: Get resolver from `current_app.extensions`
- [ ] Facade: Accept `path_resolver: IDatabasePathResolver`
- [ ] Factory: Accept `path_resolver: IDatabasePathResolver`
- [ ] Repository: Accept `path_resolver: IDatabasePathResolver`
- [ ] Remove `db_path` string parameters

### Phase 3: Testing
- [ ] Write unit tests with mock resolvers
- [ ] Integration tests with TemporaryPathResolver
- [ ] Verify 0 Feng Shui Service Locator violations

---

## Feng Shui Detection (v4.10)

Feng Shui ArchitectAgent now automatically detects Service Locator violations:

```bash
# Run Feng Shui on module
python -m tools.fengshui.react_agent

# Detects:
# 1. db_path string parameters in __init__
# 2. Flask config access for database paths
# 3. Missing IDatabasePathResolver imports
# 4. Factory.create() with db_path strings
```

**Example Output**:
```
Found 7 Service Locator violations:
[HIGH] api.py:33 - Flask config access for db_path
[HIGH] facade.py:35 - Constructor accepts db_path string
[HIGH] factory.py:36 - Factory.create() accepts db_path
[HIGH] repository.py:43 - Constructor accepts db_path string
```

Each finding includes:
- Severity level (HIGH/MEDIUM)
- File and line number
- Clear description
- Actionable recommendation with code example

---

## Key Takeaways

### Service Locator (Anti-Pattern)
- ❌ Hidden dependencies (fetched at runtime)
- ❌ Violates SOLID (especially DIP, ISP)
- ❌ Not testable (global state)
- ❌ Runtime errors (not compile-time)

### Dependency Injection (Best Practice)
- ✅ Explicit dependencies (declared upfront)
- ✅ Follows SOLID principles
- ✅ Testable (inject mocks)
- ✅ Compile-time safety (type hints)

### Configuration-Driven DI (Industry Standard 2024)
- ✅ Centralized config (module.json)
- ✅ Auto-wiring (ModuleLoader reads config)
- ✅ Self-describing modules (declare their needs)
- ✅ Flexible (swap implementations per environment)

---

## References

### Industry Research
- **Perplexity**: "Service Locator anti-pattern solution dependency injection Python Flask 2024"
- **Blog Post**: [Service Locator violates SOLID](https://blog.ploeh.dk/2014/05/15/service-locator-violates-solid/)
- **Blog Post**: [Service Locator anti-pattern explained](https://stitcher.io/blog/service-locator-anti-pattern)
- **GitHub**: [DI anti-patterns](https://lab.abilian.com/Tech/Architecture%20&%20Software%20Design/Dependency%20Inversion/DI%20anti-patterns/)

### Project Documentation
- [[App V2 Configuration-Driven Architecture]] - Frontend DI with module.json
- [[Repository Pattern Modular Architecture]] - Repository Pattern v3.0.0
- [[Cosmic Python Patterns]] - Unit of Work, Service Layer patterns
- `core/services/database_path_resolvers.py` - Available resolver implementations

### Related Patterns
- **Strategy Pattern**: IDatabasePathResolver (4 implementations)
- **Factory Pattern**: DataProductRepositoryFactory
- **Facade Pattern**: DataProductsFacade (orchestration)

---

## Migration Example: data_products_v2

### Current State (Feng Shui Detected)
```
7 Service Locator violations:
- API reads Flask config for db_path
- Facade accepts db_path string
- Factory accepts db_path string
- Repository accepts db_path string
```

### Migration Path
1. ✅ Add `backend.dependencies` to `modules/data_products_v2/module.json`
2. ✅ Enhance ModuleLoader to auto-wire path_resolver
3. ✅ Refactor API to get resolver from DI container
4. ✅ Refactor Facade/Factory/Repository to accept resolver interface
5. ✅ Run Feng Shui: 0 violations ✅

**Estimated Time**: 2-3 hours (4 files + tests)

---

## Conclusion

**The Problem**: Passing `db_path` strings through layers = Service Locator anti-pattern

**The Solution**: Declare resolver in `module.json`, ModuleLoader auto-wires at startup

**The Benefit**: 
- Testable (inject mocks)
- Flexible (swap resolvers per environment)
- Maintainable (centralized config)
- Industry-standard DI pattern

**Feng Shui Advantage**: Automatically detects violations, guides refactoring 🎯

---

**Next Steps**:
1. Read this guide when refactoring modules
2. Use Feng Shui to detect Service Locator violations
3. Follow module.json + ModuleLoader pattern for DI
4. Achieve 0 violations for clean architecture ✅