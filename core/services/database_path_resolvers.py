"""
Database Path Resolver Strategies

Concrete implementations of IDatabasePathResolver strategy pattern.
Each strategy provides different path resolution logic for different environments.

@author P2P Development Team
@version 1.0.0 (v3.25 - Database Path Strategy Pattern)
@date 2026-02-05
"""

import os
import json
import logging
from typing import Dict, Optional
from core.interfaces.database_path_resolver import IDatabasePathResolver

logger = logging.getLogger(__name__)


class ModuleOwnedPathResolver(IDatabasePathResolver):
    """
    Production strategy: Each module owns its database in its directory.
    
    Benefits:
    - Clear ownership (module owns its data)
    - SoC compliant (separation of concerns)
    - Independent deployment (module + its database)
    
    Path Pattern: modules/{module_name}/database/{db_name}.db
    
    Examples:
        knowledge_graph → modules/knowledge_graph/database/graph_cache.db
        data_products → modules/data_products/database/p2p_data.db
        log_manager → modules/log_manager/database/logs.db
    """
    
    # Mapping of module names to their specific database filenames
    DATABASE_NAMES = {
        'knowledge_graph': 'graph_cache.db',
        'data_products': 'p2p_data.db',
        'log_manager': 'logs.db',
        'sqlite_connection': 'sqlite.db',
    }
    
    def resolve_path(self, module_name: str) -> str:
        """
        Resolve path to module-owned database.
        
        Args:
            module_name: Name of module
            
        Returns:
            Path to module's database file
            
        Example:
            >>> resolver = ModuleOwnedPathResolver()
            >>> resolver.resolve_path("knowledge_graph")
            'modules/knowledge_graph/database/graph_cache.db'
        """
        # Get specific database name or use module name as default
        db_name = self.DATABASE_NAMES.get(module_name, f"{module_name}.db")
        
        path = os.path.join('modules', module_name, 'database', db_name)
        
        logger.debug(f"ModuleOwnedPathResolver: {module_name} → {path}")
        
        return path


class SharedPathResolver(IDatabasePathResolver):
    """
    Legacy/Test strategy: All modules share a central database.
    
    Use Cases:
    - Unit testing (temporary test database)
    - Legacy systems (pre-separation architecture)
    - Simple deployments (single database file)
    
    Benefits:
    - Simple setup (one database)
    - Easy testing (clear shared DB)
    - Backward compatibility
    
    Drawbacks:
    - Violates SoC (mixed concerns)
    - Not independently deployable
    - Migration complexity
    """
    
    def __init__(self, shared_db_path: str = "data/shared.db"):
        """
        Initialize with shared database path.
        
        Args:
            shared_db_path: Path to shared database (default: data/shared.db)
        """
        self.shared_db_path = shared_db_path
    
    def resolve_path(self, module_name: str) -> str:
        """
        All modules resolve to same shared database.
        
        Args:
            module_name: Name of module (ignored - all use same DB)
            
        Returns:
            Shared database path
            
        Example:
            >>> resolver = SharedPathResolver("test/temp.db")
            >>> resolver.resolve_path("knowledge_graph")
            'test/temp.db'
            >>> resolver.resolve_path("data_products")
            'test/temp.db'  # Same path!
        """
        logger.debug(f"SharedPathResolver: {module_name} → {self.shared_db_path}")
        
        return self.shared_db_path


class ConfigurablePathResolver(IDatabasePathResolver):
    """
    Development strategy: Paths from configuration file.
    
    Use Cases:
    - Development environments (custom paths)
    - CI/CD pipelines (temporary paths)
    - Multi-environment deployments (dev/staging/prod)
    
    Benefits:
    - Flexible (configure per environment)
    - No code changes (update config only)
    - Easy testing (different configs for different tests)
    
    Configuration Format (config/database_paths.json):
    {
        "knowledge_graph": "path/to/graph_cache.db",
        "data_products": "path/to/p2p_data.db",
        "log_manager": "path/to/logs.db"
    }
    """
    
    def __init__(self, config_path: str = "config/database_paths.json"):
        """
        Initialize with configuration file.
        
        Args:
            config_path: Path to JSON config file
            
        Raises:
            FileNotFoundError: If config file doesn't exist
            json.JSONDecodeError: If config is invalid JSON
        """
        self.config_path = config_path
        self.config: Optional[Dict[str, str]] = None
        self._load_config()
    
    def _load_config(self):
        """Load configuration from file"""
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                self.config = json.load(f)
            
            logger.info(f"ConfigurablePathResolver: Loaded config from {self.config_path}")
            logger.debug(f"Configured paths: {list(self.config.keys())}")
            
        except FileNotFoundError:
            logger.warning(
                f"ConfigurablePathResolver: Config file not found: {self.config_path}. "
                "Using module-owned paths as fallback."
            )
            self.config = {}
        
        except json.JSONDecodeError as e:
            logger.error(
                f"ConfigurablePathResolver: Invalid JSON in {self.config_path}: {e}. "
                "Using module-owned paths as fallback."
            )
            self.config = {}
    
    def resolve_path(self, module_name: str) -> str:
        """
        Resolve path from configuration file.
        
        Args:
            module_name: Name of module
            
        Returns:
            Configured path, or falls back to module-owned path
            
        Example:
            # config/database_paths.json:
            # {
            #   "knowledge_graph": "/tmp/test_graph.db",
            #   "data_products": "/tmp/test_data.db"
            # }
            
            >>> resolver = ConfigurablePathResolver()
            >>> resolver.resolve_path("knowledge_graph")
            '/tmp/test_graph.db'
            
            >>> resolver.resolve_path("unknown_module")
            'modules/unknown_module/database/unknown_module.db'  # Fallback
        """
        # Try configured path first
        if self.config and module_name in self.config:
            path = self.config[module_name]
            logger.debug(f"ConfigurablePathResolver: {module_name} → {path} (from config)")
            return path
        
        # Fallback to module-owned path
        fallback_resolver = ModuleOwnedPathResolver()
        path = fallback_resolver.resolve_path(module_name)
        
        logger.debug(
            f"ConfigurablePathResolver: {module_name} → {path} "
            "(fallback - not in config)"
        )
        
        return path


class TemporaryPathResolver(IDatabasePathResolver):
    """
    Testing strategy: Use temporary paths for isolated tests.
    
    Use Cases:
    - Unit tests (clean state per test)
    - Integration tests (isolated from production)
    - CI/CD pipelines (temporary test databases)
    
    Benefits:
    - Isolation (each test gets own DB)
    - Cleanup (automatic temp file cleanup)
    - Parallelization (tests don't interfere)
    
    Example Usage:
        >>> import tempfile
        >>> temp_dir = tempfile.mkdtemp()
        >>> resolver = TemporaryPathResolver(temp_dir)
        >>> path = resolver.resolve_path("knowledge_graph")
        >>> # path = "/tmp/xyz/knowledge_graph_test.db"
    """
    
    def __init__(self, temp_dir: str):
        """
        Initialize with temporary directory.
        
        Args:
            temp_dir: Path to temporary directory (e.g., from tempfile.mkdtemp())
        """
        self.temp_dir = temp_dir
    
    def resolve_path(self, module_name: str) -> str:
        """
        Resolve to temporary path for testing.
        
        Args:
            module_name: Name of module
            
        Returns:
            Temporary database path
            
        Example:
            >>> resolver = TemporaryPathResolver("/tmp/test_123")
            >>> resolver.resolve_path("knowledge_graph")
            '/tmp/test_123/knowledge_graph_test.db'
        """
        path = os.path.join(self.temp_dir, f"{module_name}_test.db")
        
        logger.debug(f"TemporaryPathResolver: {module_name} → {path}")
        
        return path