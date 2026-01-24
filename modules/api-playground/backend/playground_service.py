"""
API Playground Service - Auto-discovers and manages module APIs

This service:
1. Uses Module Registry to discover all modules
2. Extracts API configuration from each module.json
3. Provides metadata for dynamic UI generation
4. Enables zero-configuration API testing

Part of: API Playground Module
Version: 1.0
"""

import sys
from pathlib import Path
from typing import Dict, List, Optional

# Add project root to path for imports
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from core.backend.module_registry import ModuleRegistry


class PlaygroundService:
    """
    Auto-discovers module APIs and provides testing metadata.
    
    This is the core innovation: reads API definitions from module.json
    files and generates test interfaces dynamically.
    """
    
    def __init__(self, modules_dir: str = "modules"):
        """
        Initialize playground service.
        
        Args:
            modules_dir: Directory containing modules (default: "modules")
        """
        self.registry = ModuleRegistry(modules_dir)
        self.discovered_apis: Dict[str, dict] = {}
        
        # Auto-discover on initialization
        self.discover_apis()
    
    def discover_apis(self) -> int:
        """
        Scan all modules and extract API configurations.
        
        Returns:
            Count of modules with APIs discovered
        """
        self.discovered_apis = {}
        
        all_modules = self.registry.get_all_modules()
        
        for module_name, module_config in all_modules.items():
            # Check if module has API configuration
            if 'api' in module_config:
                api_config = module_config['api']
                
                self.discovered_apis[module_name] = {
                    'displayName': module_config.get('displayName', module_name),
                    'description': module_config.get('description', ''),
                    'category': module_config.get('category', 'Uncategorized'),
                    'baseUrl': api_config.get('baseUrl', ''),
                    'endpoints': api_config.get('endpoints', []),
                    'enabled': module_config.get('enabled', True)
                }
                
                print(f"[PlaygroundService] ✓ Discovered API: {module_name} ({len(api_config.get('endpoints', []))} endpoints)")
        
        print(f"[PlaygroundService] ✓ Total modules with APIs: {len(self.discovered_apis)}")
        return len(self.discovered_apis)
    
    def get_all_apis(self) -> Dict[str, dict]:
        """
        Get all discovered module APIs.
        
        Returns:
            Dictionary of module_name -> API configuration
        """
        return self.discovered_apis.copy()
    
    def get_api(self, module_name: str) -> Optional[dict]:
        """
        Get API configuration for a specific module.
        
        Args:
            module_name: Name of the module
        
        Returns:
            API configuration dict or None if not found
        """
        return self.discovered_apis.get(module_name)
    
    def get_apis_by_category(self, category: str) -> Dict[str, dict]:
        """
        Get APIs in a specific category.
        
        Args:
            category: Category name (e.g., "Infrastructure", "Business Logic")
        
        Returns:
            Dictionary of modules in the category with APIs
        """
        return {
            name: config
            for name, config in self.discovered_apis.items()
            if config.get('category') == category
        }
    
    def get_categories(self) -> List[str]:
        """
        Get all unique categories that have APIs.
        
        Returns:
            List of category names
        """
        categories = set(
            config.get('category', 'Uncategorized')
            for config in self.discovered_apis.values()
        )
        return sorted(categories)
    
    def get_endpoint_count(self) -> int:
        """
        Get total count of all API endpoints across all modules.
        
        Returns:
            Total number of endpoints
        """
        return sum(
            len(config.get('endpoints', []))
            for config in self.discovered_apis.values()
        )
    
    def get_module_endpoint_count(self, module_name: str) -> int:
        """
        Get endpoint count for a specific module.
        
        Args:
            module_name: Name of the module
        
        Returns:
            Number of endpoints, or 0 if module not found
        """
        api = self.get_api(module_name)
        if api:
            return len(api.get('endpoints', []))
        return 0
    
    def build_endpoint_url(self, module_name: str, endpoint: dict) -> str:
        """
        Build complete URL for an endpoint.
        
        Args:
            module_name: Name of the module
            endpoint: Endpoint configuration dict
        
        Returns:
            Complete URL (baseUrl + endpoint path)
        """
        api = self.get_api(module_name)
        if not api:
            return ""
        
        base_url = api.get('baseUrl', '')
        path = endpoint.get('path', '')
        
        return f"{base_url}{path}"
    
    def get_endpoint_parameters(self, endpoint: dict) -> List[dict]:
        """
        Get parameters for an endpoint.
        
        Args:
            endpoint: Endpoint configuration dict
        
        Returns:
            List of parameter configurations
        """
        return endpoint.get('parameters', [])
    
    def get_summary_stats(self) -> dict:
        """
        Get summary statistics about discovered APIs.
        
        Returns:
            Dictionary with statistics
        """
        return {
            'total_modules': len(self.discovered_apis),
            'total_endpoints': self.get_endpoint_count(),
            'categories': self.get_categories(),
            'modules_by_category': {
                category: len(self.get_apis_by_category(category))
                for category in self.get_categories()
            }
        }
    
    def __repr__(self) -> str:
        """String representation."""
        return f"<PlaygroundService: {len(self.discovered_apis)} modules, {self.get_endpoint_count()} endpoints>"


# Global instance (singleton pattern)
_playground_service_instance: Optional[PlaygroundService] = None


def get_playground_service(modules_dir: str = "modules") -> PlaygroundService:
    """
    Get the global playground service instance.
    
    Args:
        modules_dir: Directory containing modules
    
    Returns:
        PlaygroundService instance
    """
    global _playground_service_instance
    
    if _playground_service_instance is None:
        _playground_service_instance = PlaygroundService(modules_dir)
    
    return _playground_service_instance


if __name__ == "__main__":
    # Test the playground service
    print("=" * 60)
    print("🎯 API PLAYGROUND SERVICE TEST")
    print("=" * 60)
    print()
    
    # Create instance
    playground = PlaygroundService()
    
    print(f"\n{playground}")
    print()
    
    # Show summary
    stats = playground.get_summary_stats()
    print("📊 Summary Statistics:")
    print(f"  Modules with APIs: {stats['total_modules']}")
    print(f"  Total Endpoints: {stats['total_endpoints']}")
    print(f"  Categories: {', '.join(stats['categories'])}")
    print()
    
    # Show each module
    print("📦 Discovered Modules:")
    for module_name, config in playground.get_all_apis().items():
        print(f"\n  {config['displayName']} ({module_name})")
        print(f"    Category: {config['category']}")
        print(f"    Base URL: {config['baseUrl']}")
        print(f"    Endpoints: {len(config['endpoints'])}")
        
        # Show first 3 endpoints
        for endpoint in config['endpoints'][:3]:
            method = endpoint.get('method', 'GET')
            path = endpoint.get('path', '')
            desc = endpoint.get('description', '')
            print(f"      {method:6} {path:30} {desc}")
        
        if len(config['endpoints']) > 3:
            remaining = len(config['endpoints']) - 3
            print(f"      ... and {remaining} more endpoint(s)")
    
    print()
    print("=" * 60)
    print("✅ API Playground Service Ready!")
    print("=" * 60)