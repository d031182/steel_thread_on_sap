"""
Path Resolver - Configuration-driven path resolution for modules

This resolver enables:
1. Configuration-based path resolution (restructure-resistant)
2. Automatic path adaptation when project structure changes
3. Module resource location without hardcoded paths
4. Path aliasing and shortcuts

Part of: Future-Proof Module Architecture
Version: 1.0
"""

from pathlib import Path
from typing import Optional, Dict
import json


class PathResolver:
    """
    Resolves paths to module resources using configuration.
    
    Instead of hardcoding paths like "modules/feature-manager/backend",
    use configuration to make paths restructure-resistant.
    """
    
    def __init__(self, module_config: dict, module_base_path: Path):
        """
        Initialize path resolver for a module.
        
        Args:
            module_config: Module configuration from module.json
            module_base_path: Base path to the module directory
        """
        self.config = module_config
        self.base_path = Path(module_base_path)
        self.structure = module_config.get('structure', {})
        
        # Default structure if not specified
        self.default_structure = {
            'backend': 'backend',
            'frontend': 'frontend',
            'tests': 'tests',
            'docs': 'docs',
            'assets': 'assets',
            'config': 'config'
        }
    
    def resolve(self, resource_type: str, filename: str = "") -> Path:
        """
        Resolve path to a module resource.
        
        Args:
            resource_type: Type of resource (e.g., 'backend', 'frontend', 'tests')
            filename: Optional filename within the resource directory
        
        Returns:
            Resolved Path object
        
        Example:
            resolver.resolve('backend', 'api.py')
            # Returns: Path('modules/feature-manager/backend/api.py')
        """
        # Get path from configuration or use default
        subpath = self.structure.get(
            resource_type,
            self.default_structure.get(resource_type, resource_type)
        )
        
        resolved_path = self.base_path / subpath
        
        if filename:
            resolved_path = resolved_path / filename
        
        return resolved_path
    
    def backend(self, filename: str = "") -> Path:
        """Shortcut for resolving backend resources."""
        return self.resolve('backend', filename)
    
    def frontend(self, filename: str = "") -> Path:
        """Shortcut for resolving frontend resources."""
        return self.resolve('frontend', filename)
    
    def tests(self, filename: str = "") -> Path:
        """Shortcut for resolving test resources."""
        return self.resolve('tests', filename)
    
    def docs(self, filename: str = "") -> Path:
        """Shortcut for resolving documentation resources."""
        return self.resolve('docs', filename)
    
    def assets(self, filename: str = "") -> Path:
        """Shortcut for resolving asset resources."""
        return self.resolve('assets', filename)
    
    def config(self, filename: str = "") -> Path:
        """Shortcut for resolving configuration resources."""
        return self.resolve('config', filename)
    
    def exists(self, resource_type: str, filename: str = "") -> bool:
        """
        Check if a resource exists.
        
        Args:
            resource_type: Type of resource
            filename: Optional filename
        
        Returns:
            True if resource exists, False otherwise
        """
        path = self.resolve(resource_type, filename)
        return path.exists()
    
    def list_resources(self, resource_type: str, pattern: str = "*") -> list:
        """
        List all resources of a given type.
        
        Args:
            resource_type: Type of resource
            pattern: Glob pattern for filtering (default: all files)
        
        Returns:
            List of Path objects
        """
        resource_dir = self.resolve(resource_type)
        
        if not resource_dir.exists():
            return []
        
        return list(resource_dir.glob(pattern))
    
    def get_relative_path(self, resource_type: str, filename: str = "") -> str:
        """
        Get path relative to project root.
        
        Args:
            resource_type: Type of resource
            filename: Optional filename
        
        Returns:
            Relative path as string (using forward slashes)
        """
        path = self.resolve(resource_type, filename)
        return str(path).replace('\\', '/')
    
    def __repr__(self) -> str:
        """String representation."""
        module_name = self.config.get('name', 'unknown')
        return f"<PathResolver for '{module_name}'>"


class GlobalPathResolver:
    """
    Global path resolver that works with module registry.
    
    Provides unified path resolution across all modules.
    """
    
    def __init__(self, module_registry):
        """
        Initialize global path resolver.
        
        Args:
            module_registry: ModuleRegistry instance
        """
        self.registry = module_registry
        self._resolvers: Dict[str, PathResolver] = {}
    
    def get_resolver(self, module_name: str) -> Optional[PathResolver]:
        """
        Get path resolver for a specific module.
        
        Args:
            module_name: Name of the module
        
        Returns:
            PathResolver instance or None if module not found
        """
        # Check cache
        if module_name in self._resolvers:
            return self._resolvers[module_name]
        
        # Get module from registry
        module = self.registry.get_module(module_name)
        if not module:
            return None
        
        # Create and cache resolver
        resolver = PathResolver(
            module_config=module,
            module_base_path=Path(module['absolute_path'])
        )
        self._resolvers[module_name] = resolver
        
        return resolver
    
    def resolve(self, module_name: str, resource_type: str, filename: str = "") -> Optional[Path]:
        """
        Resolve path for any module.
        
        Args:
            module_name: Name of the module
            resource_type: Type of resource
            filename: Optional filename
        
        Returns:
            Resolved Path or None if module not found
        """
        resolver = self.get_resolver(module_name)
        if not resolver:
            return None
        
        return resolver.resolve(resource_type, filename)
    
    def clear_cache(self) -> None:
        """Clear resolver cache (useful after module updates)."""
        self._resolvers.clear()
    
    def __repr__(self) -> str:
        """String representation."""
        return f"<GlobalPathResolver: {len(self._resolvers)} cached resolvers>"


# Example module.json structure for reference
EXAMPLE_MODULE_JSON = {
    "name": "feature-manager",
    "displayName": "Feature Manager",
    "version": "1.0.0",
    "description": "Feature toggle system",
    "category": "Infrastructure",
    "structure": {
        "backend": "backend",
        "frontend": "frontend",
        "tests": "tests",
        "docs": "docs"
    },
    "backend": {
        "entryPoint": "api.py",
        "blueprintName": "api"
    },
    "frontend": {
        "views": ["Configurator.view.xml"],
        "controllers": ["Configurator.controller.js"]
    },
    "enabled": True,
    "requiresHana": False
}


if __name__ == "__main__":
    # Test path resolution
    print("=== Path Resolver Test ===\n")
    
    # Create example module config
    module_config = EXAMPLE_MODULE_JSON
    module_base = Path("modules/feature-manager")
    
    # Create resolver
    resolver = PathResolver(module_config, module_base)
    
    # Test path resolution
    print("Resolved paths:")
    print(f"  Backend: {resolver.backend()}")
    print(f"  Backend API: {resolver.backend('api.py')}")
    print(f"  Frontend: {resolver.frontend()}")
    print(f"  Frontend view: {resolver.frontend('Configurator.view.xml')}")
    print(f"  Tests: {resolver.tests()}")
    print(f"  Docs: {resolver.docs('README.md')}")
    
    print(f"\nRelative paths:")
    print(f"  Backend API: {resolver.get_relative_path('backend', 'api.py')}")
    print(f"  Frontend view: {resolver.get_relative_path('frontend', 'Configurator.view.xml')}")