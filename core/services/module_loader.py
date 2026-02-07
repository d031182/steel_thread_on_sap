"""
Module Loader with Industry-Standard Error Handling
====================================================

Provides centralized module loading with proper error handling following best practices:
- Try-catch-log-reraise pattern for critical errors
- Detailed error logging with stack traces
- Graceful degradation for non-critical modules
- Clear error messages for debugging

Based on industry standards:
- Python logging best practices
- Flask blueprint registration patterns
- Fail-fast for critical components
- Graceful degradation for optional features

@author P2P Development Team
@version 1.0.0
"""

import logging
import sys
import traceback
import json
import shutil
from pathlib import Path
from typing import Optional, Callable, Any, Dict
from flask import Flask

logger = logging.getLogger(__name__)


class ModuleLoadError(Exception):
    """Custom exception for module loading failures"""
    def __init__(self, module_name: str, error: Exception, is_critical: bool = False):
        self.module_name = module_name
        self.original_error = error
        self.is_critical = is_critical
        super().__init__(f"Failed to load module '{module_name}': {error}")


class ModuleLoader:
    """
    Centralized module loader with industry-standard error handling
    
    Features:
    - Detailed error logging with full context
    - Critical vs non-critical module handling
    - Blueprint registration tracking
    - Startup diagnostics
    """
    
    def __init__(self, app: Flask):
        """
        Initialize module loader
        
        Args:
            app: Flask application instance
        """
        self.app = app
        self.loaded_modules: Dict[str, bool] = {}
        self.failed_modules: Dict[str, Exception] = {}
        self.critical_failures: list = []
    
    def load_blueprint(
        self,
        module_name: str,
        import_path: str,
        blueprint_name: str,
        endpoint: str,
        is_critical: bool = False
    ) -> bool:
        """
        Load and register a Flask blueprint with proper error handling
        
        Args:
            module_name: Human-readable module name for logging
            import_path: Python import path (e.g., 'modules.data_products.backend')
            blueprint_name: Name of blueprint variable to import
            endpoint: API endpoint where blueprint is mounted
            is_critical: If True, raises exception on failure; if False, logs warning
        
        Returns:
            True if loaded successfully, False otherwise
        
        Raises:
            ModuleLoadError: If is_critical=True and loading fails
        """
        try:
            logger.info(f"Loading {module_name} from {import_path}...")
            
            # Dynamic import with proper error context
            module = __import__(import_path, fromlist=[blueprint_name])
            blueprint = getattr(module, blueprint_name)
            
            # Register blueprint with url_prefix
            self.app.register_blueprint(blueprint, url_prefix=endpoint)
            
            # Track success
            self.loaded_modules[module_name] = True
            logger.info(f"✓ {module_name} registered at {endpoint}")
            
            return True
            
        except ImportError as e:
            error_msg = f"Import error for {module_name}: {type(e).__name__}: {e}"
            return self._handle_load_failure(module_name, e, error_msg, is_critical)
            
        except AttributeError as e:
            error_msg = f"Blueprint '{blueprint_name}' not found in {import_path}: {e}"
            return self._handle_load_failure(module_name, e, error_msg, is_critical)
            
        except Exception as e:
            error_msg = f"Unexpected error loading {module_name}: {type(e).__name__}: {e}"
            return self._handle_load_failure(module_name, e, error_msg, is_critical)
    
    def _handle_load_failure(
        self,
        module_name: str,
        error: Exception,
        error_msg: str,
        is_critical: bool
    ) -> bool:
        """
        Handle module loading failure with proper logging and optionally re-raise
        
        Args:
            module_name: Name of module that failed
            error: Original exception
            error_msg: Detailed error message
            is_critical: Whether to raise exception
        
        Returns:
            False (always)
        
        Raises:
            ModuleLoadError: If is_critical=True
        """
        # Log with full stack trace for debugging
        logger.error(error_msg, exc_info=True)
        
        # Track failure
        self.loaded_modules[module_name] = False
        self.failed_modules[module_name] = error
        
        if is_critical:
            self.critical_failures.append(module_name)
            # Re-raise with enhanced context
            raise ModuleLoadError(module_name, error, is_critical=True)
        else:
            # Non-critical: log warning and continue
            logger.warning(f"⚠ {module_name} not loaded - application will continue without it")
        
        return False
    
    def get_load_summary(self) -> Dict[str, Any]:
        """
        Get summary of module loading results
        
        Returns:
            Dictionary with loading statistics and details
        """
        total = len(self.loaded_modules)
        successful = sum(1 for v in self.loaded_modules.values() if v)
        failed = total - successful
        
        return {
            'total_modules': total,
            'loaded': successful,
            'failed': failed,
            'critical_failures': len(self.critical_failures),
            'loaded_modules': [k for k, v in self.loaded_modules.items() if v],
            'failed_modules': [k for k, v in self.loaded_modules.items() if not v],
            'critical_failures_list': self.critical_failures
        }
    
    def auto_discover_modules(self, modules_dir: str = 'modules') -> int:
        """
        Auto-discover and load all modules with module.json configuration
        
        Scans the modules directory for module.json files and automatically
        loads modules that have backend.blueprint configured.
        
        Args:
            modules_dir: Path to modules directory (default: 'modules')
        
        Returns:
            Number of modules successfully loaded
        """
        modules_path = Path(modules_dir)
        if not modules_path.exists():
            logger.warning(f"Modules directory not found: {modules_dir}")
            return 0
        
        loaded_count = 0
        
        # Scan for module.json files
        for module_json_path in modules_path.rglob('module.json'):
            try:
                module_dir = module_json_path.parent
                module_name = module_dir.name
                
                # Read module configuration
                with open(module_json_path, 'r') as f:
                    config = json.load(f)
                
                # Skip if module is disabled
                if not config.get('enabled', True):
                    logger.info(f"Skipping disabled module: {module_name}")
                    continue
                
                # Check if module has backend configuration
                backend_config = config.get('backend', {})
                if not backend_config:
                    logger.debug(f"Module {module_name} has no backend configuration, skipping")
                    continue
                
                # Extract blueprint configuration
                blueprint_path = backend_config.get('blueprint')
                mount_path = backend_config.get('mount_path')
                
                if not blueprint_path or not mount_path:
                    logger.warning(f"Module {module_name} missing blueprint or mount_path configuration")
                    continue
                
                # Parse blueprint path (format: "modules.module_name.backend:blueprint_var")
                if ':' in blueprint_path:
                    import_path, blueprint_name = blueprint_path.rsplit(':', 1)
                else:
                    # Fallback: old format with separate module_path
                    import_path = backend_config.get('module_path', f'modules.{module_name}.backend')
                    blueprint_name = blueprint_path
                
                # Determine if module is critical
                is_critical = config.get('critical', False)
                
                # Get display name
                display_name = config.get('name', module_name).replace('_', ' ').title()
                
                # Load the blueprint
                logger.info(f"Auto-discovering: {display_name}")
                success = self.load_blueprint(
                    display_name,
                    import_path,
                    blueprint_name,
                    mount_path,
                    is_critical=is_critical
                )
                
                if success:
                    loaded_count += 1
                    
            except json.JSONDecodeError as e:
                logger.error(f"Invalid JSON in {module_json_path}: {e}")
            except Exception as e:
                logger.error(f"Error processing {module_json_path}: {e}", exc_info=True)
        
        logger.info(f"Auto-discovery complete: {loaded_count} modules loaded")
        return loaded_count
    
    def deploy_frontend_assets(self, modules_dir: str = 'modules') -> int:
        """
        Deploy frontend assets for enabled modules (Clean Slate approach)
        
        Cleans all previous deployments, then deploys only enabled modules.
        This ensures disabled modules are completely removed.
        
        Args:
            modules_dir: Path to modules directory (default: 'modules')
        
        Returns:
            Number of modules successfully deployed
        """
        deploy_root = Path('app/static/modules')
        
        # STEP 1: Clean ALL previous deployments (Clean Slate)
        if deploy_root.exists():
            try:
                shutil.rmtree(deploy_root)
                logger.info("✓ Cleaned previous frontend deployments")
            except Exception as e:
                logger.error(f"Failed to clean deployments: {e}")
                return 0
        
        # STEP 2: Deploy ONLY enabled modules
        deployed_count = 0
        modules_path = Path(modules_dir)
        
        if not modules_path.exists():
            logger.warning(f"Modules directory not found: {modules_dir}")
            return 0
        
        for module_json_path in modules_path.rglob('module.json'):
            try:
                config = self._load_module_config(module_json_path)
                
                # Skip if module is disabled
                if not config.get('enabled', True):
                    logger.info(f"Skipping disabled module: {config.get('name', module_json_path.parent.name)}")
                    continue
                
                # Check for frontend configuration
                frontend_config = config.get('frontend', {})
                if not frontend_config:
                    continue
                
                # Deploy frontend assets
                module_dir = module_json_path.parent
                if self._deploy_module_assets(module_dir, config):
                    deployed_count += 1
                    
            except Exception as e:
                logger.error(f"Error deploying {module_json_path}: {e}", exc_info=True)
        
        logger.info(f"✓ Frontend deployment complete: {deployed_count} module(s) deployed")
        return deployed_count
    
    def _load_module_config(self, module_json_path: Path) -> Dict[str, Any]:
        """
        Load and parse module.json configuration
        
        Args:
            module_json_path: Path to module.json file
        
        Returns:
            Parsed configuration dictionary
        
        Raises:
            json.JSONDecodeError: If JSON is invalid
        """
        with open(module_json_path, 'r') as f:
            return json.load(f)
    
    def _deploy_module_assets(self, module_dir: Path, config: Dict[str, Any]) -> bool:
        """
        Deploy frontend assets for a single module
        
        Copies files from modules/[name]/frontend/ to app/static/modules/[name]/
        
        Args:
            module_dir: Path to module directory
            config: Module configuration dictionary
        
        Returns:
            True if deployed successfully, False otherwise
        """
        try:
            frontend_config = config.get('frontend', {})
            if not frontend_config:
                return False
            
            module_name = config.get('name', module_dir.name)
            source_dir = module_dir / 'frontend'
            
            # Check if frontend directory exists
            if not source_dir.exists():
                logger.warning(f"Frontend directory not found for {module_name}: {source_dir}")
                return False
            
            # Determine deployment target
            deploy_to = frontend_config.get('deploy_to', f'modules/{module_name}')
            target_dir = Path('app/static') / deploy_to
            
            # Copy assets
            shutil.copytree(source_dir, target_dir, dirs_exist_ok=True)
            
            logger.info(f"✓ Deployed frontend: {module_name} → {target_dir}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to deploy frontend for {module_dir.name}: {e}", exc_info=True)
            return False
    
    def log_startup_summary(self):
        """Log a summary of module loading at application startup"""
        summary = self.get_load_summary()
        
        logger.info("=" * 60)
        logger.info("MODULE LOADING SUMMARY")
        logger.info("=" * 60)
        logger.info(f"Total modules: {summary['total_modules']}")
        logger.info(f"✓ Loaded: {summary['loaded']}")
        
        if summary['failed'] > 0:
            logger.warning(f"⚠ Failed: {summary['failed']}")
            for module in summary['failed_modules']:
                error = self.failed_modules.get(module)
                logger.warning(f"  - {module}: {type(error).__name__}: {error}")
        
        if summary['critical_failures'] > 0:
            logger.error(f"✗ Critical failures: {summary['critical_failures']}")
            for module in summary['critical_failures_list']:
                logger.error(f"  - {module} (CRITICAL)")
        
        logger.info("=" * 60)


# Convenience function for backward compatibility
def safe_load_blueprint(
    app: Flask,
    module_name: str,
    import_path: str,
    blueprint_name: str,
    endpoint: str,
    is_critical: bool = False
) -> bool:
    """
    Standalone function to load a blueprint with error handling
    
    This is a convenience function that doesn't require creating a ModuleLoader instance.
    For batch loading, use ModuleLoader class directly.
    
    Args:
        app: Flask application
        module_name: Human-readable module name
        import_path: Python import path
        blueprint_name: Blueprint variable name
        endpoint: API endpoint
        is_critical: Whether failure should stop application
    
    Returns:
        True if successful, False if failed (and not critical)
    
    Raises:
        ModuleLoadError: If is_critical=True and loading fails
    """
    loader = ModuleLoader(app)
    return loader.load_blueprint(module_name, import_path, blueprint_name, endpoint, is_critical)