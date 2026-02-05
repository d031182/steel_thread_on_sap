"""
Database Path Resolver Factory

Factory pattern for creating appropriate database path resolver strategy
based on environment and configuration.

@author P2P Development Team
@version 1.0.0 (v3.25 - Database Path Strategy Pattern)
@date 2026-02-05
"""

import os
import logging
from typing import Optional
from core.interfaces.database_path_resolver import IDatabasePathResolver
from core.services.database_path_resolvers import (
    ModuleOwnedPathResolver,
    SharedPathResolver,
    ConfigurablePathResolver,
    TemporaryPathResolver
)

logger = logging.getLogger(__name__)


class DatabasePathResolverFactory:
    """
    Factory for creating database path resolver strategies.
    
    Implements Factory pattern to encapsulate resolver creation logic.
    Selects appropriate strategy based on environment variables or explicit config.
    
    Environment Detection:
    - PYTEST_CURRENT_TEST → TemporaryPathResolver (during tests)
    - APP_ENV=development → ConfigurablePathResolver (dev mode)
    - APP_ENV=test → SharedPathResolver (integration tests)
    - Default → ModuleOwnedPathResolver (production)
    
    Usage:
        # Automatic (detects environment)
        resolver = DatabasePathResolverFactory.create_resolver()
        
        # Explicit (override detection)
        resolver = DatabasePathResolverFactory.create_resolver(env="test")
        
        # With config
        resolver = DatabasePathResolverFactory.create_resolver(
            env="development",
            config_path="config/custom_paths.json"
        )
    """
    
    @staticmethod
    def create_resolver(
        env: Optional[str] = None,
        config_path: Optional[str] = None,
        temp_dir: Optional[str] = None
    ) -> IDatabasePathResolver:
        """
        Create appropriate database path resolver for environment.
        
        Args:
            env: Environment name ("production", "development", "test", "pytest")
                 If None, auto-detects from APP_ENV or pytest detection
            config_path: Path to config file (for ConfigurablePathResolver)
            temp_dir: Temporary directory path (for TemporaryPathResolver)
            
        Returns:
            Appropriate IDatabasePathResolver implementation
            
        Examples:
            # Production (default)
            >>> resolver = DatabasePathResolverFactory.create_resolver()
            >>> type(resolver).__name__
            'ModuleOwnedPathResolver'
            
            # Testing
            >>> resolver = DatabasePathResolverFactory.create_resolver(env="test")
            >>> type(resolver).__name__
            'SharedPathResolver'
            
            # Development with config
            >>> resolver = DatabasePathResolverFactory.create_resolver(
            ...     env="development",
            ...     config_path="config/dev_paths.json"
            ... )
            >>> type(resolver).__name__
            'ConfigurablePathResolver'
        """
        # Auto-detect environment if not specified
        if env is None:
            env = DatabasePathResolverFactory._detect_environment()
        
        # Normalize environment name
        env = env.lower().strip()
        
        logger.info(f"DatabasePathResolverFactory: Creating resolver for env='{env}'")
        
        # Select strategy based on environment
        if env in ("pytest", "unit_test"):
            # Unit tests: Use temporary isolated databases
            if temp_dir is None:
                import tempfile
                temp_dir = tempfile.mkdtemp(prefix="pytest_db_")
            
            logger.info(f"Using TemporaryPathResolver (temp_dir={temp_dir})")
            return TemporaryPathResolver(temp_dir)
        
        elif env in ("test", "integration_test"):
            # Integration tests: Use shared test database
            shared_path = os.environ.get("TEST_DB_PATH", "test/test_shared.db")
            
            logger.info(f"Using SharedPathResolver (shared_path={shared_path})")
            return SharedPathResolver(shared_path)
        
        elif env == "development":
            # Development: Use configurable paths
            if config_path is None:
                config_path = os.environ.get(
                    "DB_CONFIG_PATH",
                    "config/database_paths.json"
                )
            
            logger.info(f"Using ConfigurablePathResolver (config={config_path})")
            return ConfigurablePathResolver(config_path)
        
        elif env == "production":
            # Production: Use module-owned paths (SoC compliant)
            logger.info("Using ModuleOwnedPathResolver (production)")
            return ModuleOwnedPathResolver()
        
        else:
            # Unknown environment: Default to production (safest)
            logger.warning(
                f"Unknown environment '{env}', defaulting to ModuleOwnedPathResolver"
            )
            return ModuleOwnedPathResolver()
    
    @staticmethod
    def _detect_environment() -> str:
        """
        Auto-detect current environment from various signals.
        
        Detection Logic:
        1. Check PYTEST_CURRENT_TEST → pytest
        2. Check APP_ENV variable → value
        3. Check FLASK_ENV variable → value
        4. Default → production
        
        Returns:
            Detected environment name
        """
        # Check if running under pytest
        if "PYTEST_CURRENT_TEST" in os.environ:
            logger.debug("Environment detected: pytest (PYTEST_CURRENT_TEST present)")
            return "pytest"
        
        # Check APP_ENV variable
        app_env = os.environ.get("APP_ENV")
        if app_env:
            logger.debug(f"Environment detected: {app_env} (from APP_ENV)")
            return app_env
        
        # Check FLASK_ENV variable (legacy)
        flask_env = os.environ.get("FLASK_ENV")
        if flask_env:
            logger.debug(f"Environment detected: {flask_env} (from FLASK_ENV)")
            return flask_env
        
        # Default to production
        logger.debug("Environment detected: production (default)")
        return "production"
    
    @staticmethod
    def create_test_resolver(shared_db_path: str = ":memory:") -> IDatabasePathResolver:
        """
        Convenience method for creating test resolver.
        
        Args:
            shared_db_path: Path to shared test database (default: in-memory)
            
        Returns:
            SharedPathResolver configured for testing
            
        Example:
            >>> resolver = DatabasePathResolverFactory.create_test_resolver()
            >>> resolver.resolve_path("any_module")
            ':memory:'  # All modules use in-memory DB
        """
        logger.info(f"Creating test resolver (shared_path={shared_db_path})")
        return SharedPathResolver(shared_db_path)
    
    @staticmethod
    def create_production_resolver() -> IDatabasePathResolver:
        """
        Convenience method for creating production resolver.
        
        Returns:
            ModuleOwnedPathResolver (production strategy)
            
        Example:
            >>> resolver = DatabasePathResolverFactory.create_production_resolver()
            >>> resolver.resolve_path("knowledge_graph")
            'modules/knowledge_graph/database/graph_cache.db'
        """
        logger.info("Creating production resolver (module-owned paths)")
        return ModuleOwnedPathResolver()