# Modular Architecture Evolution

**Type**: Architecture  
**Category**: Design Evolution  
**Created**: 2026-01-24  
**Updated**: 2026-01-25  
**Status**: Planning/In Progress

## Overview

Evolution plan for transforming the application into a fully modular, feature-toggleable architecture. Extends [[Modular Architecture]] with feature management, dynamic loading, and configuration systems.

## Related Documentation

- [[Modular Architecture]] - Current modular backend structure
- [[Testing Standards]] - Testing requirements for modules
- [[SAP Fiori Design Standards]] - UI standards for module interfaces

## Vision

**Every capability = Self-contained, toggleable module**

### What This Means

**Current State**:
- Backend modules in `modules/*/backend/`
- Frontend as monolithic application
- Features always enabled

**Target State**:
- Backend AND frontend modular
- Feature flags control module visibility
- Dynamic route/navigation registration
- Plug-and-play architecture

## Feature Manager (Core Module)

### Purpose
Centralized system controlling which modules are active.

### Capabilities
- Enable/disable features via API
- Persist configuration (JSON file)
- Provide configurator UI
- Dynamic navigation updates
- Import/export configurations

### Backend API

**Endpoints**:
```python
GET  /api/features              # List all features
GET  /api/features/{key}        # Check feature state
POST /api/features/{key}/toggle # Toggle feature
POST /api/features/{key}/enable # Enable feature
POST /api/features/{key}/disable # Disable feature
POST /api/features/reset        # Reset to defaults
GET  /api/features/export       # Export config
POST /api/features/import       # Import config
```

### Frontend UI

**Configurator Components**:
- Settings dialog (IconTabBar by category)
- Feature list with switches
- Import/export buttons
- Reset to defaults action

**SAP UI5 Pattern**: InputListItem + Switch
- See [[InputListItem Control Decision]] for rationale
- Clean, professional appearance
- Built-in Fiori spacing

### Configuration Structure

```json
{
  "version": "1.0",
  "lastModified": "2026-01-25T15:00:00Z",
  "features": {
    "application-logging": {
      "enabled": true,
      "displayName": "Application Logging",
      "description": "SQLite-based logging system",
      "category": "System",
      "requiresHana": false
    },
    "feature-manager": {
      "enabled": true,
      "displayName": "Feature Manager",
      "description": "Module configuration interface",
      "category": "System",
      "requiresHana": false
    }
  }
}
```

## Module Structure

### Standard Module Layout

```
modules/[module-name]/
├── module.json           # Metadata
├── backend/              # Python services
│   ├── __init__.py
│   ├── service.py
│   └── api.py
├── frontend/             # UI5 components (optional)
│   ├── views/
│   └── controllers/
├── docs/                 # Module docs
│   ├── README.md
│   └── API_REFERENCE.md
├── tests/                # Module tests
│   ├── unit/
│   └── integration/
└── README.md             # Module entry point
```

### Module Metadata (module.json)

```json
{
  "name": "module-name",
  "displayName": "Human Readable Name",
  "version": "1.0.0",
  "description": "What this module does",
  "category": "Development Tools",
  "requiresHana": false,
  "dependencies": ["feature-manager"],
  "backend": {
    "entryPoint": "backend/api.py",
    "routes": "/api/module-name/*"
  },
  "frontend": {
    "views": ["ModuleName.view.xml"],
    "navigation": {
      "title": "Module Name",
      "icon": "sap-icon://icon-name",
      "route": "module-name"
    }
  },
  "enabled": true
}
```

## Dynamic Loading System

### Module Registry

**Purpose**: Auto-discover and manage modules

```python
# core/backend/module_registry.py
class ModuleRegistry:
    def __init__(self, modules_dir='modules'):
        self.modules = self._discover_modules()
    
    def _discover_modules(self):
        """Scan modules/ for module.json files"""
        modules = {}
        for module_name in os.listdir(self.modules_dir):
            manifest = os.path.join(
                self.modules_dir, 
                module_name, 
                'module.json'
            )
            if os.path.exists(manifest):
                with open(manifest) as f:
                    modules[module_name] = json.load(f)
        return modules
    
    def get_enabled_modules(self, feature_flags):
        """Return list of enabled modules"""
        return [
            name for name in self.modules
            if feature_flags.is_enabled(name)
        ]
```

### Dynamic Route Registration

```python
# core/backend/app.py
def register_module_routes():
    """Register Flask blueprints for enabled modules"""
    enabled = module_registry.get_enabled_modules(feature_flags)
    
    for module_name in enabled:
        config = module_registry.get_module_config(module_name)
        if 'backend' in config:
            # Import module blueprint
            module_path = f"modules.{module_name}.backend.api"
            module = __import__(module_path, fromlist=['api'])
            app.register_blueprint(module.api)
```

### Dynamic Navigation

```javascript
// core/frontend/Shell.controller.js
async _updateNavigation(features) {
    const navList = this.byId("navigationList");
    
    // Show/hide items based on feature flags
    navList.getItems().forEach(item => {
        const featureKey = item.data("feature");
        if (featureKey && features[featureKey]) {
            item.setVisible(features[featureKey].enabled);
        }
    });
}
```

## Implementation Status

### Completed ✅
- [[Modular Architecture]] - Backend module structure
- [[HANA Connection Module]] - First modular backend
- Data Products module migration
- Feature Manager backend implemented
- Feature Manager UI with InputListItem pattern

### In Progress 🟡
- Feature flag persistence (JSON file)
- Dynamic navigation based on flags
- Module registry system
- Configurator UI refinements

### Planned 📋
- Frontend module structure
- Dynamic view loading
- Module documentation templates
- Complete module migration
- Integration testing

## Migration Strategy

### Phase 1: Infrastructure (Week 1)
- Feature Manager module complete
- Module registry system
- Shell integration for dynamic navigation

### Phase 2: Module Migration (Weeks 2-3)
Migrate existing features to modules:
1. CSN Validation
2. Data Products Viewer
3. SQL Execution
4. HANA Connection Manager
5. SQLite Fallback

### Phase 3: Documentation (Week 3)
- Module-specific docs
- Architecture guides
- Developer onboarding

### Phase 4: Testing & Polish (Week 4)
- Integration testing
- UX refinement
- Performance optimization

## Benefits

### For Users
- ✅ Customizable experience
- ✅ Faster load times (disabled modules don't load)
- ✅ Less clutter
- ✅ Easy feature discovery

### For Developers
- ✅ Clear boundaries
- ✅ Parallel development possible
- ✅ Easier testing (isolation)
- ✅ Safer changes (isolated impact)

### For Operations
- ✅ Selective deployment
- ✅ Feature flags without code changes
- ✅ A/B testing capability
- ✅ Gradual rollout support

## References

- Current architecture: [[Modular Architecture]]
- Feature Manager: `modules/feature-manager/`
- Core infrastructure: `core/backend/module_registry.py`
- Planning document: `docs/planning/architecture/MODULAR_APPLICATION_ARCHITECTURE_PLAN.md` (detailed 51KB plan)

## Status

🟡 **IN PROGRESS** - Infrastructure established, migration ongoing

**Completed**:
- Backend modular structure
- Feature Manager backend
- Feature Manager UI
- Feature flag system

**Next Steps**:
- Complete feature flag persistence
- Migrate remaining modules
- Document module patterns
- Integration testing