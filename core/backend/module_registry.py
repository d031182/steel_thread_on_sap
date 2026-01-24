"""
Module Registry - Auto-discovery and management of application modules

This registry enables:
1. Auto-discovery of modules from modules/ directory
2. Module metadata parsing from module.json files
3. Dynamic module loading based on feature flags
4. Path resolution for module resources

Part of: Modular Application Architecture
Version: 1.0
"""

import os
import json
from pathlib import Path
from typing import Dict, List, Optional


class ModuleRegistry:
    """
    Central registry for all application modules.
    
    Discovers modules by scanning the modules/ directory and
    reading their module.json configuration files.
    """
    
    def __init__(self, modules_dir: str = "modules"):
        """
        Initialize the module registry.
        
        Args:
            modules_dir: Root directory containing modules (default: "modules")
        """
        self.modules_dir = Path(modules_dir)
        self.modules: Dict[str, dict] = {}
        self._discover_modules()
    
    def _discover_modules(self) -> None:
        """
        Scan modules directory and load module.json from each module.
        
        Populates self.modules with discovered module metadata.
        """
        if not self.modules_dir.exists():
            print(f"[ModuleRegistry] Warning: Modules directory not found: {self.modules_dir}")
            return
        
        # Scan for module directories
        for module_path in self.modules_dir.iterdir():
            if not module_path.is_dir():
                continue
            
            # Look for module.json
            module_json_path = module_path / "module.json"
            if not module_json_path.exists():
                continue
            
            try:
                with open(module_json_path, 'r', encoding='utf-8') as f:
                    module_config = json.load(f)
                
                module_name = module_config.get('name', module_path.name)
                self.modules[module_name] = {
                    **module_config,
                    'path': str(module_path),
                    'absolute_path': str(module_path.resolve())
                }
                
                print(f"[ModuleRegistry] ✓ Discovered module: {module_name}")
                
            except json.JSONDecodeError as e:
                print(f"[ModuleRegistry] ✗ Invalid module.json in {module_path.name}: {e}")
            except Exception as e:
                print(f"[ModuleRegistry] ✗ Error loading module {module_path.name}: {e}")
    
    def get_module(self, module_name: str) -> Optional[dict]:
        """
        Get module metadata by name.
        
        Args:
            module_name: Name of the module
            
        Returns:
            Module metadata dict or None if not found
        """
        return self.modules.get(module_name)
    
    def get_all_modules(self) -> Dict[str, dict]:
        """
        Get all discovered modules.
        
        Returns:
            Dictionary of module_name -> module_metadata
        """
        return self.modules.copy()
    
    def get_enabled_modules(self, feature_flags: Optional[dict] = None) -> Dict[str, dict]:
        """
        Get only enabled modules based on feature flags.
        
        Args:
            feature_flags: Dictionary of feature flags (name -> enabled)
                          If None, uses module's default 'enabled' property
        
        Returns:
            Dictionary of enabled modules
        """
        enabled = {}
        
        for name, module in self.modules.items():
            if feature_flags:
                # Check feature flag
                is_enabled = feature_flags.get(name, module.get('enabled', True))
            else:
                # Use module's default
                is_enabled = module.get('enabled', True)
            
            if is_enabled:
                enabled[name] = module
        
        return enabled
    
    def get_modules_by_category(self, category: str) -> Dict[str, dict]:
        """
        Get all modules in a specific category.
        
        Args:
            category: Category name (e.g., "Infrastructure", "Business Logic")
        
        Returns:
            Dictionary of modules in the category
        """
        return {
            name: module
            for name, module in self.modules.items()
            if module.get('category') == category
        }
    
    def get_module_path(self, module_name: str, subpath: str = "") -> Optional[Path]:
        """
        Get the absolute path to a module or its subdirectory.
        
        Args:
            module_name: Name of the module
            subpath: Optional subdirectory within module (e.g., "backend", "frontend")
        
        Returns:
            Path object or None if module not found
        """
        module = self.get_module(module_name)
        if not module:
            return None
        
        base_path = Path(module['absolute_path'])
        
        if subpath:
            return base_path / subpath
        
        return base_path
    
    def list_module_names(self) -> List[str]:
        """
        Get list of all module names.
        
        Returns:
            List of module names
        """
        return list(self.modules.keys())
    
    def refresh(self) -> None:
        """
        Re-scan modules directory and reload registry.
        
        Useful for detecting newly added modules without restart.
        """
        self.modules.clear()
        self._discover_modules()
    
    def get_module_count(self) -> int:
        """
        Get total number of discovered modules.
        
        Returns:
            Count of modules
        """
        return len(self.modules)
    
    def __repr__(self) -> str:
        """String representation of registry."""
        return f"<ModuleRegistry: {self.get_module_count()} modules>"


# Global registry instance (singleton pattern)
_registry_instance: Optional[ModuleRegistry] = None


def get_registry(modules_dir: str = "modules") -> ModuleRegistry:
    """
    Get the global module registry instance.
    
    Creates registry on first call, returns cached instance on subsequent calls.
    
    Args:
        modules_dir: Root directory containing modules
    
    Returns:
        ModuleRegistry instance
    """
    global _registry_instance
    
    if _registry_instance is None:
        _registry_instance = ModuleRegistry(modules_dir)
    
    return _registry_instance


def reload_registry(modules_dir: str = "modules") -> ModuleRegistry:
    """
    Force reload of the module registry.
    
    Args:
        modules_dir: Root directory containing modules
    
    Returns:
        New ModuleRegistry instance
    """
    global _registry_instance
    _registry_instance = ModuleRegistry(modules_dir)
    return _registry_instance


if __name__ == "__main__":
    # Test module discovery
    print("=== Module Registry Test ===")
    registry = ModuleRegistry()
    
    print(f"\nDiscovered {registry.get_module_count()} modules:")
    for name in registry.list_module_names():
        module = registry.get_module(name)
        print(f"  - {name}: {module.get('displayName', name)}")
        print(f"    Category: {module.get('category', 'N/A')}")
        print(f"    Version: {module.get('version', 'N/A')}")
        print(f"    Path: {module.get('path')}")