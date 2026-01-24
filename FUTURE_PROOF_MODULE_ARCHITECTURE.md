# Future-Proof Module Architecture

**Date**: 2026-01-24  
**Purpose**: Make modules resistant to folder restructuring  
**Status**: 📋 DESIGN SPECIFICATION

---

## 🎯 Goal: Zero-Disruption Restructuring

**Problem**: Hardcoded paths break when folders are renamed/moved

**Solution**: Configuration-driven architecture where all paths are defined in `module.json`

---

## 🛡️ Core Principles

### 1. **Configuration Over Convention**
- ✅ All paths in `module.json` (single source of truth)
- ✅ No hardcoded paths in code
- ✅ Registry discovers via configuration
- ❌ No assumptions about folder names

### 2. **Relative Path Resolution**
- ✅ All paths relative to module root
- ✅ Module root discovered by `module.json` location
- ✅ Portable between environments

### 3. **Dynamic Discovery**
- ✅ Modules auto-discovered at runtime
- ✅ No manual registration needed
- ✅ Scan for `module.json` files

---

## 📋 Enhanced module.json Schema

```json
{
  // Module Identity
  "name": "csn-validation",
  "displayName": "CSN Validation", 
  "version": "1.0.0",
  "description": "Validate CSN definitions against data sources",
  
  // ⭐ FLEXIBLE STRUCTURE - All paths configurable
  "structure": {
    "root": ".",                    // Module root (relative to module.json)
    "backend": "backend",           // Can be "api", "server", "src/backend"
    "frontend": "frontend",         // Can be "ui", "views", "src/frontend"
    "docs": "docs",                 // Can be "documentation", "doc"
    "tests": "tests",               // Can be "test", "__tests__", "spec"
    "config": "config"              // Can be "configuration", "settings"
  },
  
  // ⭐ BACKEND DISCOVERY - Entry point relative to backend folder
  "backend": {
    "type": "flask",                // flask, fastapi, express, etc.
    "entryPoint": "api.py",         // Relative to structure.backend
    "blueprintName": "api",         // Name of blueprint variable
    "routes": {
      "prefix": "/api/csn-validation",  // API route prefix
      "version": "v1"                   // Optional versioning
    },
    "dependencies": [
      "hdbcli",
      "pyyaml"
    ]
  },
  
  // ⭐ FRONTEND DISCOVERY - Entry point relative to frontend folder  
  "frontend": {
    "type": "sapui5",               // sapui5, react, vue, angular
    "views": [
      "CSNValidator.view.xml"       // Relative to structure.frontend
    ],
    "controllers": [
      "CSNValidator.controller.js"
    ],
    "navigation": {
      "title": "CSN Validation",
      "icon": "sap-icon://validate",
      "route": "csn-validation"
    }
  },
  
  // ⭐ DOCUMENTATION DISCOVERY
  "docs": {
    "readme": "README.md",          // Relative to structure.docs
    "api": "API_REFERENCE.md",
    "userGuide": "USER_GUIDE.md",
    "devGuide": "DEVELOPER_GUIDE.md"
  },
  
  // ⭐ TEST DISCOVERY
  "tests": {
    "unit": [
      "test_validator.py",          // Relative to structure.tests
      "test_hana_connector.py"
    ],
    "integration": [
      "test_integration.py"
    ]
  },
  
  // Module Metadata
  "category": "Development Tools",
  "author": "P2P Team",
  "license": "MIT",
  "homepage": "https://github.com/d031182/steel_thread_on_sap",
  
  // Runtime Configuration
  "requiresHana": false,
  "dependencies": [
    "feature-manager"
  ],
  "enabled": true
}
```

---

## 🔧 Path Resolver Utility

```python
# core/backend/path_resolver.py
import os
from pathlib import Path
from typing import Dict, Optional

class ModulePathResolver:
    """
    Resolves module paths from module.json configuration.
    Makes modules resistant to folder restructuring.
    """
    
    def __init__(self, module_config: Dict, module_root: str):
        """
        Args:
            module_config: Parsed module.json
            module_root: Absolute path to module root directory
        """
        self.config = module_config
        self.module_root = Path(module_root).resolve()
        self.structure = module_config.get('structure', {})
    
    def get_backend_path(self) -> Path:
        """Get absolute path to backend folder"""
        backend_rel = self.structure.get('backend', 'backend')
        return self.module_root / backend_rel
    
    def get_frontend_path(self) -> Path:
        """Get absolute path to frontend folder"""
        frontend_rel = self.structure.get('frontend', 'frontend')
        return self.module_root / frontend_rel
    
    def get_docs_path(self) -> Path:
        """Get absolute path to docs folder"""
        docs_rel = self.structure.get('docs', 'docs')
        return self.module_root / docs_rel
    
    def get_tests_path(self) -> Path:
        """Get absolute path to tests folder"""
        tests_rel = self.structure.get('tests', 'tests')
        return self.module_root / tests_rel
    
    def get_backend_entry_point(self) -> Path:
        """Get absolute path to backend entry point file"""
        backend_config = self.config.get('backend', {})
        entry_point = backend_config.get('entryPoint', 'api.py')
        return self.get_backend_path() / entry_point
    
    def get_frontend_view(self, view_name: str) -> Path:
        """Get absolute path to specific frontend view"""
        return self.get_frontend_path() / view_name
    
    def get_doc_file(self, doc_type: str) -> Optional[Path]:
        """Get absolute path to documentation file"""
        docs_config = self.config.get('docs', {})
        doc_file = docs_config.get(doc_type)
        if doc_file:
            return self.get_docs_path() / doc_file
        return None
    
    def get_test_files(self, test_type: str = 'unit') -> list[Path]:
        """Get absolute paths to test files"""
        tests_config = self.config.get('tests', {})
        test_files = tests_config.get(test_type, [])
        return [self.get_tests_path() / f for f in test_files]
    
    def exists(self, path_type: str) -> bool:
        """Check if a path type exists"""
        path_getters = {
            'backend': self.get_backend_path,
            'frontend': self.get_frontend_path,
            'docs': self.get_docs_path,
            'tests': self.get_tests_path
        }
        getter = path_getters.get(path_type)
        if getter:
            return getter().exists()
        return False
```

---

## 🔍 Enhanced Module Registry

```python
# core/backend/module_registry.py (UPDATED)
import os
import json
from pathlib import Path
from typing import Dict, List, Optional
from .path_resolver import ModulePathResolver

class ModuleRegistry:
    """
    Central registry with path resolution.
    Resistant to folder restructuring.
    """
    
    def __init__(self, modules_base_dir: str = 'modules'):
        self.modules_base_dir = Path(modules_base_dir).resolve()
        self.modules = self._discover_modules()
    
    def _discover_modules(self) -> Dict:
        """
        Auto-discover modules by finding module.json files.
        Supports nested structures and custom folder names.
        """
        modules = {}
        
        if not self.modules_base_dir.exists():
            return modules
        
        # Recursively search for module.json files
        for module_json_path in self.modules_base_dir.rglob('module.json'):
            try:
                with open(module_json_path, 'r') as f:
                    config = json.load(f)
                
                # Module root is parent directory of module.json
                module_root = module_json_path.parent
                module_name = config.get('name')
                
                if module_name:
                    # Create path resolver for this module
                    path_resolver = ModulePathResolver(config, str(module_root))
                    
                    modules[module_name] = {
                        'config': config,
                        'root': str(module_root),
                        'manifest_path': str(module_json_path),
                        'path_resolver': path_resolver
                    }
            except Exception as e:
                print(f"⚠️  Error loading module from {module_json_path}: {e}")
        
        return modules
    
    def get_module_path_resolver(self, module_name: str) -> Optional[ModulePathResolver]:
        """Get path resolver for specific module"""
        module_info = self.modules.get(module_name)
        if module_info:
            return module_info['path_resolver']
        return None
    
    def get_backend_entry_point(self, module_name: str) -> Optional[Path]:
        """Get backend entry point path for module"""
        resolver = self.get_module_path_resolver(module_name)
        if resolver:
            return resolver.get_backend_entry_point()
        return None
    
    def get_module_config(self, module_name: str) -> Dict:
        """Get configuration for specific module"""
        return self.modules.get(module_name, {}).get('config', {})
    
    def list_modules(self) -> List[Dict]:
        """List all modules with metadata"""
        return [
            {
                'name': name,
                'root': info['root'],
                **info['config']
            }
            for name, info in self.modules.items()
        ]
    
    def validate_module_structure(self, module_name: str) -> Dict:
        """
        Validate that module structure matches configuration.
        Useful for detecting missing files after restructuring.
        """
        resolver = self.get_module_path_resolver(module_name)
        if not resolver:
            return {'valid': False, 'errors': ['Module not found']}
        
        errors = []
        warnings = []
        
        # Check required paths
        if not resolver.exists('backend'):
            errors.append(f"Backend path not found: {resolver.get_backend_path()}")
        
        if not resolver.get_backend_entry_point().exists():
            errors.append(f"Backend entry point not found: {resolver.get_backend_entry_point()}")
        
        if not resolver.exists('frontend'):
            warnings.append(f"Frontend path not found: {resolver.get_frontend_path()}")
        
        # Check documentation
        readme_path = resolver.get_doc_file('readme')
        if readme_path and not readme_path.exists():
            warnings.append(f"README not found: {readme_path}")
        
        return {
            'valid': len(errors) == 0,
            'errors': errors,
            'warnings': warnings
        }

# Global instance
module_registry = ModuleRegistry()
```

---

## 🔌 Dynamic Backend Loading

```python
# core/backend/app.py (UPDATED)
from flask import Flask
from pathlib import Path
import importlib.util

app = Flask(__name__)

def load_module_blueprint(module_name: str, entry_point_path: Path, blueprint_name: str):
    """
    Dynamically load Flask blueprint from any path.
    Path-agnostic loading.
    """
    try:
        # Load module from file path (not package name)
        spec = importlib.util.spec_from_file_location(
            f"{module_name}.backend",
            entry_point_path
        )
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        
        # Get blueprint by name
        blueprint = getattr(module, blueprint_name, None)
        if blueprint:
            app.register_blueprint(blueprint)
            print(f"✅ Loaded module: {module_name} from {entry_point_path}")
            return True
        else:
            print(f"⚠️  Blueprint '{blueprint_name}' not found in {module_name}")
            return False
    except Exception as e:
        print(f"❌ Failed to load {module_name}: {e}")
        return False

def register_enabled_modules():
    """Register all enabled modules using path resolver"""
    from .module_registry import module_registry
    from modules.feature_manager.backend.feature_flags import feature_flags
    
    enabled_modules = []
    
    for module_name in feature_flags.get_enabled_features():
        module_config = module_registry.get_module_config(module_name)
        if not module_config or 'backend' not in module_config:
            continue
        
        # Get entry point via path resolver (resistant to restructuring!)
        entry_point = module_registry.get_backend_entry_point(module_name)
        if not entry_point or not entry_point.exists():
            print(f"⚠️  Backend entry point not found for {module_name}")
            continue
        
        # Get blueprint name from config
        backend_config = module_config['backend']
        blueprint_name = backend_config.get('blueprintName', 'api')
        
        # Load blueprint
        if load_module_blueprint(module_name, entry_point, blueprint_name):
            enabled_modules.append(module_name)
    
    print(f"✅ Registered {len(enabled_modules)} modules: {', '.join(enabled_modules)}")

# Register modules
register_enabled_modules()
```

---

## 🎨 Frontend Path Resolution

```javascript
// core/frontend/ModuleLoader.js
class ModuleLoader {
    /**
     * Load module view dynamically using module configuration.
     * Path-agnostic loading.
     */
    static async loadModuleView(moduleName) {
        try {
            // Fetch module configuration
            const response = await fetch(`/api/modules/${moduleName}/config`);
            const config = await response.json();
            
            if (!config.success || !config.frontend) {
                throw new Error('Module frontend configuration not found');
            }
            
            // Get view path from configuration
            const viewName = config.frontend.views[0];
            const viewPath = `/modules/${moduleName}/${config.structure.frontend}/${viewName}`;
            
            // Load view dynamically
            return await sap.ui.view({
                viewName: viewPath,
                type: sap.ui.core.mvc.ViewType.XML,
                async: true
            });
        } catch (error) {
            console.error(`Failed to load module ${moduleName}:`, error);
            throw error;
        }
    }
    
    /**
     * Get module navigation configuration
     */
    static async getModuleNav(moduleName) {
        const response = await fetch(`/api/modules/${moduleName}/config`);
        const config = await response.json();
        return config.frontend?.navigation || {};
    }
}

export default ModuleLoader;
```

---

## 📝 Migration Script Example

```python
# scripts/migrate_module_structure.py
"""
Script to safely migrate module structure.
Updates module.json to reflect new folder names.
"""

import json
from pathlib import Path

def migrate_module_structure(module_name: str, structure_changes: dict):
    """
    Migrate module folder structure.
    
    Example:
        migrate_module_structure('csn-validation', {
            'backend': 'api',      # Rename backend → api
            'frontend': 'ui',      # Rename frontend → ui
            'docs': 'documentation' # Rename docs → documentation
        })
    """
    module_path = Path(f'modules/{module_name}')
    module_json_path = module_path / 'module.json'
    
    # Load current config
    with open(module_json_path, 'r') as f:
        config = json.load(f)
    
    # Get current structure
    current_structure = config.get('structure', {
        'root': '.',
        'backend': 'backend',
        'frontend': 'frontend',
        'docs': 'docs',
        'tests': 'tests'
    })
    
    # Apply changes
    for key, new_name in structure_changes.items():
        old_name = current_structure.get(key)
        if old_name and old_name != new_name:
            old_path = module_path / old_name
            new_path = module_path / new_name
            
            # Rename folder if exists
            if old_path.exists():
                print(f"Renaming {old_path} → {new_path}")
                old_path.rename(new_path)
            
            # Update config
            current_structure[key] = new_name
    
    # Save updated config
    config['structure'] = current_structure
    with open(module_json_path, 'w') as f:
        json.dump(config, f, indent=2)
    
    print(f"✅ Migrated {module_name} structure")
    print(f"Updated module.json with new paths")
    
    # Validate
    from core.backend.module_registry import ModuleRegistry
    registry = ModuleRegistry()
    validation = registry.validate_module_structure(module_name)
    
    if validation['valid']:
        print("✅ Module structure validated successfully")
    else:
        print("⚠️  Validation issues:")
        for error in validation['errors']:
            print(f"  - {error}")

# Usage examples
if __name__ == '__main__':
    # Example 1: Rename backend → api
    migrate_module_structure('csn-validation', {
        'backend': 'api'
    })
    
    # Example 2: Reorganize everything
    migrate_module_structure('data-products-viewer', {
        'backend': 'server',
        'frontend': 'views',
        'docs': 'documentation',
        'tests': '__tests__'
    })
```

---

## 🧪 Testing Restructure Resistance

```python
# tests/test_restructure_resistance.py
import pytest
import tempfile
import shutil
from pathlib import Path
import json

def test_module_discovery_with_custom_structure():
    """Test that modules are discovered regardless of folder names"""
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create module with non-standard structure
        module_dir = Path(tmpdir) / 'my-custom-module'
        module_dir.mkdir()
        
        # Create custom folder structure
        (module_dir / 'api').mkdir()  # backend → api
        (module_dir / 'views').mkdir()  # frontend → views
        (module_dir / 'docs').mkdir()
        
        # Create module.json with custom structure
        module_config = {
            'name': 'custom-module',
            'structure': {
                'backend': 'api',
                'frontend': 'views',
                'docs': 'docs'
            },
            'backend': {
                'entryPoint': 'routes.py'
            }
        }
        
        with open(module_dir / 'module.json', 'w') as f:
            json.dump(module_config, f)
        
        # Create entry point
        (module_dir / 'api' / 'routes.py').write_text('# API code')
        
        # Test discovery
        from core.backend.module_registry import ModuleRegistry
        registry = ModuleRegistry(str(tmpdir))
        
        assert 'custom-module' in registry.modules
        resolver = registry.get_module_path_resolver('custom-module')
        assert resolver.get_backend_path().name == 'api'
        assert resolver.get_frontend_path().name == 'views'

def test_module_migration():
    """Test safe migration of module structure"""
    # Test implementation here
    pass
```

---

## ✅ Benefits Summary

### Change Resistance

**Rename backend → api**:
```json
// Only change module.json:
"structure": {
  "backend": "api"  // Changed
}
```
✅ Zero code changes needed!

**Move module to subfolder**:
```
modules/csn-validation → modules/tools/csn-validation
```
✅ Auto-discovered by recursive scan!

**Restructure completely**:
```json
"structure": {
  "backend": "src/server",
  "frontend": "src/client",
  "docs": "documentation",
  "tests": "__tests__"
}
```
✅ Still works perfectly!

### Impact Analysis

| Change Type | Files to Update | Restart Required | Downtime |
|-------------|-----------------|------------------|----------|
| Rename folder | 1 (module.json) | Yes | None |
| Move module | 0 | Yes (auto-scan) | None |
| Restructure all | 1 per module | Yes | None |
| Add new module | 1 (module.json) | Yes (auto-scan) | None |

---

## 📋 Migration Checklist

**Before Restructuring:**
- [ ] Backup current state (Git commit)
- [ ] Document current structure
- [ ] Test module discovery
- [ ] Run validation script

**During Restructuring:**
- [ ] Update module.json structure config
- [ ] Rename/move folders
- [ ] Run migration script
- [ ] Validate module structure

**After Restructuring:**
- [ ] Test module loading
- [ ] Verify all paths resolve correctly
- [ ] Run full test suite
- [ ] Update documentation
- [ ] Git commit with clear message

---

## 🎓 Best Practices

1. **Always update module.json first** before moving folders
2. **Use migration script** instead of manual renaming
3. **Validate after changes** using registry validation
4. **Test in development** before applying to production
5. **Document changes** in module changelog
6. **Use Git tags** for rollback points

---

## 📝 Conclusion

With this architecture:

✅ **Rename any folder** - Just update module.json  
✅ **Move modules anywhere** - Auto-discovered recursively  
✅ **Restructure freely** - Configuration drives everything  
✅ **Zero code changes** - Path resolver handles all lookups  
✅ **Safe migrations** - Scripts + validation ensure correctness  

**Your modules are now future-proof!** 🎉