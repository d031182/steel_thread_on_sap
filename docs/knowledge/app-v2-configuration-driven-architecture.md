# App V2: Configuration-Driven Architecture Proposal

**Date**: 2026-02-08  
**Status**: PROPOSAL  
**Author**: P2P Development Team

## Problem Statement

Current implementation has **fragile hardcoded dependencies**:

### Issues Encountered (Last 2 Hours)
1. ❌ Database path hardcoded in multiple places
2. ❌ API URLs hardcoded (`/api/data_products` vs `/api/v2/data-products`)
3. ❌ Module-specific adapter logic in bootstrap
4. ❌ Manual script loading in index.html
5. ❌ Tight coupling between modules and infrastructure

### Root Cause
**Service Locator Pattern** instead of proper **Dependency Injection**:
- ModuleBootstrap manually checks for modules and registers adapters
- Hardcoded if-checks: `if (registry.hasModule('data_products_v2'))`
- Configuration scattered across code, not centralized

---

## Industry Best Practices (2024)

### Research Findings (via Perplexity)

**Key Insights**:
1. ✅ **DI > Service Locator**: Explicit dependencies, better testability
2. ✅ **Configuration-Driven**: Centralize config, avoid scattered constants
3. ✅ **Self-Describing Modules**: Modules declare their own needs
4. ✅ **Inversion of Control**: Framework controls dependency flow
5. ✅ **Convention over Configuration**: Reduce boilerplate

### Comparison

| Aspect | Current (Service Locator) | Proposed (DI + Config) |
|--------|---------------------------|------------------------|
| **Coupling** | Tight (hardcoded checks) | Loose (declared deps) |
| **Testability** | Hard (global state) | Easy (mock injection) |
| **Scalability** | Manual per module | Auto-discovery |
| **Maintenance** | Fragile (scattered) | Robust (centralized) |
| **Debugging** | Implicit dependencies | Explicit contracts |

---

## Proposed Solution: Configuration-Driven DI

### Architecture Overview

```
Module declares needs → Registry validates → Container auto-wires → Module receives deps
```

### Core Principles

1. **Self-Describing Modules**: Each module declares dependencies in `module.json`
2. **Convention over Configuration**: Standard patterns reduce boilerplate
3. **Auto-Discovery**: No manual if-checks in bootstrap
4. **Centralized Config**: Single source of truth
5. **Graceful Degradation**: Fallbacks when deps unavailable

---

## Implementation Design

### 1. Enhanced module.json (Self-Describing)

```json
{
  "id": "data_products_v2",
  "name": "Data Products V2",
  "app_version": "v2",
  
  "frontend": {
    "page_name": "data-products-v2",
    "route": "/data-products-v2",
    "scripts": [
      "/v2/modules/data_products_v2/frontend/module.js",
      "/v2/modules/data_products_v2/frontend/views/dataProductsPageV2.js"
    ],
    "entry_point": {
      "factory": "DataProductsV2Factory",
      "create_function": "createDataProductsV2Page"
    }
  },
  
  "dependencies": {
    "required": ["IDataSource"],
    "optional": ["ILogger", "ICache"],
    
    "providers": {
      "IDataSource": {
        "implementation": "DataProductsV2Adapter",
        "config": {
          "baseUrl": "/api/v2/data-products",
          "source": "sqlite",
          "timeout": 30000
        }
      }
    }
  },
  
  "backend": {
    "type": "api",
    "blueprint": "modules.data_products_v2.backend:data_products_v2_api",
    "mount_path": "/api/v2/data-products"
  }
}
```

**Key Additions**:
- `dependencies.providers`: Module declares HOW to satisfy its needs
- `config`: All configuration in one place
- `backend.mount_path`: API URL declared, not hardcoded

### 2. Smart ModuleBootstrap (Auto-Wiring)

```javascript
class ModuleBootstrap {
    async initialize() {
        // 1. Register fallbacks (always available)
        this._registerFallbacks();
        
        // 2. Load module registry from backend
        await this._registry.initialize();
        
        // 3. Auto-wire dependencies (NO manual if-checks)
        await this._autoWireDependencies();
        
        // 4. Build navigation & router
        this._navBuilder = new NavigationBuilder(this._registry);
        this._router = new RouterService(this._registry, this._container);
        
        // 5. Render app
        this._app = this._createAppShell();
        this._router.initialize(this._app);
        
        // 6. Navigate to default module
        await this._router.navigateTo(this._registry.getDefaultModule());
    }
    
    /**
     * Auto-wire dependencies based on module declarations
     * NO MANUAL IF-CHECKS!
     */
    async _autoWireDependencies() {
        const modules = this._registry.getAllModules();
        
        for (const module of modules) {
            const providers = module.dependencies?.providers || {};
            
            // Register each provider declared by module
            for (const [interface, config] of Object.entries(providers)) {
                await this._registerProvider(interface, config);
            }
        }
    }
    
    /**
     * Register a provider based on configuration
     */
    async _registerProvider(interfaceName, config) {
        const { implementation, config: providerConfig } = config;
        
        // Load implementation class (dynamic import)
        const AdapterClass = await this._loadAdapter(implementation);
        
        // Register in container
        this._container.register(interfaceName, () => {
            return new AdapterClass(providerConfig);
        });
        
        console.log(`[Bootstrap] Registered ${interfaceName} → ${implementation}`);
    }
    
    /**
     * Dynamic adapter loading (convention-based)
     */
    async _loadAdapter(adapterName) {
        // Convention: adapters in /v2/js/adapters/{AdapterName}.js
        const scriptPath = `/v2/js/adapters/${adapterName}.js`;
        
        // Check if already loaded
        if (window[adapterName]) {
            return window[adapterName];
        }
        
        // Dynamic script loading
        await this._loadScript(scriptPath);
        return window[adapterName];
    }
}
```

**Benefits**:
- ✅ No hardcoded module checks
- ✅ Modules declare their needs
- ✅ Auto-discovery via convention
- ✅ Easy to add new modules (just add module.json)

### 3. Convention-Based Script Loading

Instead of manual `<script>` tags in index.html:

```javascript
/**
 * Auto-load scripts based on module registry
 */
async _loadModuleScripts() {
    const modules = this._registry.getAllModules();
    
    for (const module of modules) {
        const scripts = module.frontend?.scripts || [];
        
        for (const scriptPath of scripts) {
            await this._loadScript(scriptPath);
        }
    }
}

/**
 * Dynamic script loader (returns promise)
 */
_loadScript(src) {
    return new Promise((resolve, reject) => {
        if (document.querySelector(`script[src="${src}"]`)) {
            resolve(); // Already loaded
            return;
        }
        
        const script = document.createElement('script');
        script.src = src;
        script.onload = resolve;
        script.onerror = reject;
        document.head.appendChild(script);
    });
}
```

### 4. Centralized Configuration File

Create `app_v2/static/config.json`:

```json
{
  "app": {
    "name": "P2P Data Products",
    "version": "2.0.0",
    "defaultModule": "data_products_v2"
  },
  
  "api": {
    "baseUrl": "/api",
    "timeout": 30000,
    "retries": 3
  },
  
  "database": {
    "sqlite": {
      "path": "core/databases/sqlite/p2p_data.db"
    },
    "hana": {
      "host": "${HANA_HOST}",
      "port": 443,
      "schema": "P2P_SCHEMA"
    }
  },
  
  "features": {
    "caching": true,
    "logging": true,
    "debug": false
  }
}
```

**Benefits**:
- ✅ Single source of truth
- ✅ Environment variable support
- ✅ Easy to change without code edits
- ✅ Can be fetched from backend

---

## Migration Path (Phased Approach)

### Phase 1: Add Configuration Support (Non-Breaking)
- [ ] Add `dependencies.providers` to existing module.json files
- [ ] Create config.json with current hardcoded values
- [ ] Add ConfigService to load config
- [ ] Keep existing hardcoded paths as fallback

### Phase 2: Implement Auto-Wiring (Parallel to Existing)
- [ ] Add `_autoWireDependencies()` to ModuleBootstrap
- [ ] Keep manual `_registerRealImplementations()` as fallback
- [ ] Test both paths work

### Phase 3: Switch to Auto-Wiring (Breaking Change)
- [ ] Remove manual if-checks from ModuleBootstrap
- [ ] Remove hardcoded adapter registration
- [ ] All modules use providers in module.json

### Phase 4: Dynamic Script Loading
- [ ] Implement `_loadModuleScripts()`
- [ ] Remove manual `<script>` tags from index.html
- [ ] Keep core scripts (DI, EventBus) in HTML

---

## Benefits Summary

### Developer Experience
- ✅ Add new module: Just create module.json (no code changes)
- ✅ Change API URL: Edit config.json (not scattered in code)
- ✅ Switch database: Change config (not hunt for paths)
- ✅ Debug: Explicit dependency tree visible

### Maintainability
- ✅ Centralized configuration
- ✅ Convention over configuration
- ✅ Self-documenting (module.json shows all needs)
- ✅ Less fragile (no hardcoded checks)

### Testability
- ✅ Mock any dependency easily
- ✅ Test modules in isolation
- ✅ No global state pollution

### Scalability
- ✅ Supports 100+ modules without code changes
- ✅ Parallel module development
- ✅ Micro-frontend ready

---

## Industry Alignment

| Best Practice | Current | Proposed |
|---------------|---------|----------|
| Explicit Dependencies | ❌ Hidden | ✅ Declared in module.json |
| Inversion of Control | ❌ Manual | ✅ Container controls flow |
| Configuration Centralized | ❌ Scattered | ✅ config.json |
| Convention over Config | ❌ Manual setup | ✅ Auto-discovery |
| Loose Coupling | ❌ Tight | ✅ Interface-based |

---

## Next Steps

### Immediate (Fix Current Pain)
1. Document current hardcoded paths in module.json
2. Add ConfigService to load centralized config

### Short-Term (1-2 Weeks)
1. Implement Phase 1: Add provider declarations
2. Add auto-wiring alongside existing manual registration

### Long-Term (1-2 Months)
1. Migrate all modules to self-describing pattern
2. Remove all hardcoded checks from bootstrap
3. Implement dynamic script loading

---

## Conclusion

**Current approach is fragile** (Service Locator anti-pattern)  
**Proposed approach is robust** (DI + Configuration-Driven)

**Key Insight from Research**:
> "Dependency Injection excels in modular setups by making dependencies visible and swappable, aligning with micro-frontend independence."

**This proposal eliminates**:
- ❌ Hardcoded paths
- ❌ Manual if-checks
- ❌ Scattered configuration
- ❌ Fragile bootstrapping

**And provides**:
- ✅ Self-describing modules
- ✅ Auto-discovery
- ✅ Centralized configuration
- ✅ Industry-standard DI pattern

---

## References

- Perplexity Research: "Frontend modular architecture dependency injection 2024"
- Industry consensus: DI > Service Locator for modern apps
- Micro-frontend best practices: Self-contained, explicit dependencies
- Angular DI pattern: Providers + Modules (proven at scale)