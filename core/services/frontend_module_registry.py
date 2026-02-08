"""
Frontend Module Registry Service
=================================

Provides module metadata for frontend auto-discovery.

This service reads module.json configurations and exposes them via API,
enabling the frontend to:
- Auto-discover available modules
- Build navigation dynamically
- Load modules on-demand
- Respect feature flags

Architecture:
- Backend: Reads module.json files (this service)
- API: Exposes /api/modules/frontend-registry endpoint
- Frontend: ModuleRegistry.js consumes API
- Result: True plugin architecture with auto-discovery

@author P2P Development Team
@version 1.0.0
"""

import logging
import json
from pathlib import Path
from typing import Dict, List, Any, Optional

logger = logging.getLogger(__name__)


class FrontendModuleRegistry:
    """
    Service for managing frontend module metadata
    
    Scans modules directory for module.json files and provides
    filtered metadata for frontend consumption.
    """
    
    def __init__(self, modules_dir: str = 'modules'):
        """
        Initialize registry
        
        Args:
            modules_dir: Path to modules directory (default: 'modules')
        """
        self.modules_dir = Path(modules_dir)
        self._cache: Optional[List[Dict[str, Any]]] = None
    
    def get_frontend_modules(self, force_refresh: bool = False) -> List[Dict[str, Any]]:
        """
        Get list of enabled modules with frontend configuration
        
        Args:
            force_refresh: If True, bypass cache and re-scan modules
        
        Returns:
            List of module metadata dictionaries
        """
        # Return cached result if available
        if self._cache is not None and not force_refresh:
            return self._cache
        
        modules = []
        
        if not self.modules_dir.exists():
            logger.warning(f"Modules directory not found: {self.modules_dir}")
            return modules
        
        # Scan for module.json files
        for module_json_path in self.modules_dir.rglob('module.json'):
            try:
                module_metadata = self._load_module_metadata(module_json_path)
                
                if module_metadata:
                    modules.append(module_metadata)
                    
            except Exception as e:
                logger.error(f"Error processing {module_json_path}: {e}", exc_info=True)
        
        # Sort by order (if specified) then by name
        modules.sort(key=lambda m: (m.get('order', 999), m.get('name', '')))
        
        # Cache result
        self._cache = modules
        
        logger.info(f"Frontend registry: {len(modules)} module(s) available")
        return modules
    
    def _load_module_metadata(self, module_json_path: Path) -> Optional[Dict[str, Any]]:
        """
        Load and filter module metadata for frontend consumption
        
        Args:
            module_json_path: Path to module.json file
        
        Returns:
            Filtered metadata dictionary or None if module should be excluded
        """
        try:
            # Read module configuration
            with open(module_json_path, 'r') as f:
                config = json.load(f)
            
            # Skip if module is disabled
            if not config.get('enabled', True):
                return None
            
            # Skip if no frontend configuration
            frontend_config = config.get('frontend', {})
            if not frontend_config:
                return None
            
            # Extract module directory name (used for paths)
            module_dir = module_json_path.parent
            module_id = module_dir.name
            
            # Build frontend metadata
            metadata = {
                'id': module_id,
                'name': frontend_config.get('nav_title') or config.get('name', module_id.replace('_', ' ').title()),
                'description': config.get('description', ''),
                'version': config.get('version', '1.0.0'),
                'icon': frontend_config.get('nav_icon') or frontend_config.get('icon', 'sap-icon://product'),
                'order': frontend_config.get('order', 999),
                'category': config.get('category', 'general'),
                
                # Frontend-specific configuration (preserve all fields from module.json)
                'frontend': {
                    'entry_point': frontend_config.get('entry_point', f'modules/{module_id}/main.js'),
                    'scripts': frontend_config.get('scripts', []),  # NEW: Include scripts array
                    'styles': frontend_config.get('styles', f'modules/{module_id}/styles.css'),
                    'route': frontend_config.get('route', f'/{module_id}'),
                    'requires_auth': frontend_config.get('requires_auth', False),
                    'dependencies': frontend_config.get('dependencies', [])
                },
                
                # Backend endpoints (if available)
                'backend': self._get_backend_endpoints(config.get('backend', {})),
                
                # Feature flags
                'features': config.get('features', {})
            }
            
            return metadata
            
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in {module_json_path}: {e}")
            return None
        except Exception as e:
            logger.error(f"Error loading {module_json_path}: {e}", exc_info=True)
            return None
    
    def _get_backend_endpoints(self, backend_config: Dict[str, Any]) -> Optional[Dict[str, str]]:
        """
        Extract backend API endpoints from configuration
        
        Args:
            backend_config: Backend configuration dictionary
        
        Returns:
            Dictionary with endpoint information or None
        """
        if not backend_config:
            return None
        
        mount_path = backend_config.get('mount_path')
        if not mount_path:
            return None
        
        return {
            'base_url': mount_path,
            'available': True
        }
    
    def get_module_by_id(self, module_id: str) -> Optional[Dict[str, Any]]:
        """
        Get metadata for a specific module
        
        Args:
            module_id: Module identifier (directory name)
        
        Returns:
            Module metadata or None if not found
        """
        modules = self.get_frontend_modules()
        
        for module in modules:
            if module['id'] == module_id:
                return module
        
        return None
    
    def get_modules_by_category(self, category: str) -> List[Dict[str, Any]]:
        """
        Get all modules in a specific category
        
        Args:
            category: Category name
        
        Returns:
            List of module metadata dictionaries
        """
        modules = self.get_frontend_modules()
        
        return [m for m in modules if m.get('category') == category]
    
    def refresh_cache(self) -> int:
        """
        Force refresh of module cache
        
        Returns:
            Number of modules loaded
        """
        self._cache = None
        modules = self.get_frontend_modules(force_refresh=True)
        return len(modules)
    
    def get_registry_stats(self) -> Dict[str, Any]:
        """
        Get statistics about module registry
        
        Returns:
            Dictionary with registry statistics
        """
        modules = self.get_frontend_modules()
        
        # Count by category
        categories = {}
        for module in modules:
            category = module.get('category', 'general')
            categories[category] = categories.get(category, 0) + 1
        
        # Count modules with backends
        with_backend = sum(1 for m in modules if m.get('backend') is not None)
        
        return {
            'total_modules': len(modules),
            'categories': categories,
            'with_backend': with_backend,
            'without_backend': len(modules) - with_backend
        }