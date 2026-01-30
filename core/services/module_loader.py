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