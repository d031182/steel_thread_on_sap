"""
Unit Tests for Database Path Resolver Strategies

Tests Strategy pattern implementation for database path resolution.
Validates all concrete strategies and factory logic.

@author P2P Development Team
@version 1.0.0 (v3.25 - Database Path Strategy Pattern)
"""

import os
import json
import pytest
import tempfile
from unittest.mock import patch, MagicMock

from core.interfaces.database_path_resolver import IDatabasePathResolver
from core.services.database_path_resolvers import (
    ModuleOwnedPathResolver,
    SharedPathResolver,
    ConfigurablePathResolver,
    TemporaryPathResolver
)
from core.services.database_path_resolver_factory import DatabasePathResolverFactory


# ============================================================================
# Strategy Pattern Tests
# ============================================================================

@pytest.mark.unit
@pytest.mark.fast
class TestModuleOwnedPathResolver:
    """Test production strategy: module-owned database paths"""
    
    def test_resolve_known_module_paths(self):
        """Test path resolution for known modules with custom DB names"""
        # ARRANGE
        resolver = ModuleOwnedPathResolver()
        
        # ACT & ASSERT
        assert resolver.resolve_path("knowledge_graph") == \
               "modules/knowledge_graph/database/graph_cache.db"
        
        assert resolver.resolve_path("data_products") == \
               "modules/data_products/database/p2p_data.db"
        
        assert resolver.resolve_path("log_manager") == \
               "modules/log_manager/database/logs.db"
    
    def test_resolve_unknown_module_default(self):
        """Test default path for unknown modules"""
        # ARRANGE
        resolver = ModuleOwnedPathResolver()
        
        # ACT
        path = resolver.resolve_path("new_module")
        
        # ASSERT
        assert path == "modules/new_module/database/new_module.db"
    
    def test_implements_interface(self):
        """Test that resolver implements IDatabasePathResolver"""
        # ARRANGE
        resolver = ModuleOwnedPathResolver()
        
        # ASSERT
        assert isinstance(resolver, IDatabasePathResolver)
        assert hasattr(resolver, 'resolve_path')


@pytest.mark.unit
@pytest.mark.fast
class TestSharedPathResolver:
    """Test legacy/test strategy: shared database path"""
    
    def test_all_modules_same_path_default(self):
        """Test that all modules resolve to default shared path"""
        # ARRANGE
        resolver = SharedPathResolver()
        
        # ACT & ASSERT
        path1 = resolver.resolve_path("knowledge_graph")
        path2 = resolver.resolve_path("data_products")
        path3 = resolver.resolve_path("any_module")
        
        assert path1 == "data/shared.db"
        assert path2 == "data/shared.db"
        assert path3 == "data/shared.db"
        assert path1 == path2 == path3  # All same
    
    def test_custom_shared_path(self):
        """Test custom shared path configuration"""
        # ARRANGE
        resolver = SharedPathResolver("test/custom.db")
        
        # ACT
        path = resolver.resolve_path("any_module")
        
        # ASSERT
        assert path == "test/custom.db"
    
    def test_implements_interface(self):
        """Test that resolver implements IDatabasePathResolver"""
        # ARRANGE
        resolver = SharedPathResolver()
        
        # ASSERT
        assert isinstance(resolver, IDatabasePathResolver)


@pytest.mark.unit
@pytest.mark.fast
class TestConfigurablePathResolver:
    """Test development strategy: configuration-based paths"""
    
    def test_resolve_from_valid_config(self, tmp_path):
        """Test path resolution from valid JSON config"""
        # ARRANGE
        config_file = tmp_path / "db_config.json"
        config_data = {
            "knowledge_graph": "/custom/graph.db",
            "data_products": "/custom/data.db"
        }
        config_file.write_text(json.dumps(config_data), encoding='utf-8')
        
        resolver = ConfigurablePathResolver(str(config_file))
        
        # ACT
        kg_path = resolver.resolve_path("knowledge_graph")
        dp_path = resolver.resolve_path("data_products")
        
        # ASSERT
        assert kg_path == "/custom/graph.db"
        assert dp_path == "/custom/data.db"
    
    def test_fallback_for_unconfigured_module(self, tmp_path):
        """Test fallback to module-owned path for unconfigured modules"""
        # ARRANGE
        config_file = tmp_path / "db_config.json"
        config_file.write_text('{"knowledge_graph": "/custom/graph.db"}', encoding='utf-8')
        
        resolver = ConfigurablePathResolver(str(config_file))
        
        # ACT
        path = resolver.resolve_path("unconfigured_module")
        
        # ASSERT
        assert path == "modules/unconfigured_module/database/unconfigured_module.db"
    
    def test_missing_config_file_fallback(self):
        """Test graceful fallback when config file missing"""
        # ARRANGE
        resolver = ConfigurablePathResolver("nonexistent/config.json")
        
        # ACT
        path = resolver.resolve_path("knowledge_graph")
        
        # ASSERT - Falls back to module-owned path
        assert path == "modules/knowledge_graph/database/graph_cache.db"
    
    def test_invalid_json_fallback(self, tmp_path):
        """Test graceful fallback when config JSON invalid"""
        # ARRANGE
        config_file = tmp_path / "bad_config.json"
        config_file.write_text("{invalid json}", encoding='utf-8')
        
        resolver = ConfigurablePathResolver(str(config_file))
        
        # ACT
        path = resolver.resolve_path("knowledge_graph")
        
        # ASSERT - Falls back to module-owned path
        assert path == "modules/knowledge_graph/database/graph_cache.db"


@pytest.mark.unit
@pytest.mark.fast
class TestTemporaryPathResolver:
    """Test testing strategy: temporary isolated paths"""
    
    def test_resolve_to_temp_directory(self):
        """Test path resolution to temporary directory"""
        # ARRANGE
        with tempfile.TemporaryDirectory() as temp_dir:
            resolver = TemporaryPathResolver(temp_dir)
            
            # ACT
            kg_path = resolver.resolve_path("knowledge_graph")
            dp_path = resolver.resolve_path("data_products")
            
            # ASSERT
            assert kg_path.startswith(temp_dir)
            assert kg_path.endswith("knowledge_graph_test.db")
            
            assert dp_path.startswith(temp_dir)
            assert dp_path.endswith("data_products_test.db")
            
            # Different paths for isolation
            assert kg_path != dp_path
    
    def test_implements_interface(self):
        """Test that resolver implements IDatabasePathResolver"""
        # ARRANGE
        with tempfile.TemporaryDirectory() as temp_dir:
            resolver = TemporaryPathResolver(temp_dir)
            
            # ASSERT
            assert isinstance(resolver, IDatabasePathResolver)


# ============================================================================
# Factory Pattern Tests
# ============================================================================

@pytest.mark.unit
@pytest.mark.fast
class TestDatabasePathResolverFactory:
    """Test factory pattern for resolver creation"""
    
    def test_create_production_resolver(self):
        """Test factory creates production resolver correctly"""
        # ARRANGE & ACT
        resolver = DatabasePathResolverFactory.create_resolver(env="production")
        
        # ASSERT
        assert isinstance(resolver, ModuleOwnedPathResolver)
        
        path = resolver.resolve_path("knowledge_graph")
        assert path == "modules/knowledge_graph/database/graph_cache.db"
    
    def test_create_test_resolver(self):
        """Test factory creates test resolver correctly"""
        # ARRANGE & ACT
        resolver = DatabasePathResolverFactory.create_resolver(env="test")
        
        # ASSERT
        assert isinstance(resolver, SharedPathResolver)
        
        # All modules use same path
        path1 = resolver.resolve_path("knowledge_graph")
        path2 = resolver.resolve_path("data_products")
        assert path1 == path2
    
    def test_create_development_resolver(self, tmp_path):
        """Test factory creates development resolver correctly"""
        # ARRANGE
        config_file = tmp_path / "dev_config.json"
        config_file.write_text('{"knowledge_graph": "/dev/graph.db"}', encoding='utf-8')
        
        # ACT
        resolver = DatabasePathResolverFactory.create_resolver(
            env="development",
            config_path=str(config_file)
        )
        
        # ASSERT
        assert isinstance(resolver, ConfigurablePathResolver)
        
        path = resolver.resolve_path("knowledge_graph")
        assert path == "/dev/graph.db"
    
    def test_create_pytest_resolver(self):
        """Test factory creates pytest resolver correctly"""
        # ARRANGE & ACT
        resolver = DatabasePathResolverFactory.create_resolver(
            env="pytest",
            temp_dir="/tmp/test_123"
        )
        
        # ASSERT
        assert isinstance(resolver, TemporaryPathResolver)
        
        path = resolver.resolve_path("knowledge_graph")
        assert path == "/tmp/test_123/knowledge_graph_test.db"
    
    def test_auto_detect_pytest_environment(self):
        """Test automatic pytest environment detection"""
        # ARRANGE & ACT
        with patch.dict(os.environ, {"PYTEST_CURRENT_TEST": "test_example.py::test_func"}):
            resolver = DatabasePathResolverFactory.create_resolver()  # No env specified
            
            # ASSERT
            assert isinstance(resolver, TemporaryPathResolver)
    
    def test_auto_detect_app_env_variable(self):
        """Test automatic detection from APP_ENV variable"""
        # ARRANGE & ACT
        with patch.dict(os.environ, {"APP_ENV": "development"}, clear=False):
            resolver = DatabasePathResolverFactory.create_resolver()  # No env specified
            
            # ASSERT
            assert isinstance(resolver, ConfigurablePathResolver)
    
    def test_default_to_production(self):
        """Test factory defaults to production when no environment detected"""
        # ARRANGE & ACT
        with patch.dict(os.environ, {}, clear=True):
            resolver = DatabasePathResolverFactory.create_resolver()
            
            # ASSERT
            assert isinstance(resolver, ModuleOwnedPathResolver)
    
    def test_unknown_environment_defaults_production(self):
        """Test unknown environment falls back to production"""
        # ARRANGE & ACT
        resolver = DatabasePathResolverFactory.create_resolver(env="unknown_env")
        
        # ASSERT
        assert isinstance(resolver, ModuleOwnedPathResolver)
    
    def test_convenience_method_test_resolver(self):
        """Test convenience method for test resolver"""
        # ARRANGE & ACT
        resolver = DatabasePathResolverFactory.create_test_resolver(":memory:")
        
        # ASSERT
        assert isinstance(resolver, SharedPathResolver)
        assert resolver.resolve_path("any_module") == ":memory:"
    
    def test_convenience_method_production_resolver(self):
        """Test convenience method for production resolver"""
        # ARRANGE & ACT
        resolver = DatabasePathResolverFactory.create_production_resolver()
        
        # ASSERT
        assert isinstance(resolver, ModuleOwnedPathResolver)


# ============================================================================
# Integration Tests (Strategy + Factory)
# ============================================================================

@pytest.mark.integration
class TestStrategyPatternIntegration:
    """Test full strategy pattern integration"""
    
    def test_swap_strategies_at_runtime(self):
        """Test ability to swap strategies without code changes"""
        # ARRANGE
        prod_resolver = ModuleOwnedPathResolver()
        test_resolver = SharedPathResolver(":memory:")
        
        # ACT - Production
        prod_path = prod_resolver.resolve_path("knowledge_graph")
        
        # ACT - Testing  
        test_path = test_resolver.resolve_path("knowledge_graph")
        
        # ASSERT - Different paths for different strategies
        assert prod_path == "modules/knowledge_graph/database/graph_cache.db"
        assert test_path == ":memory:"
        assert prod_path != test_path
    
    def test_factory_creates_correct_strategy_for_environment(self):
        """Test factory creates appropriate strategy for each environment"""
        # ARRANGE
        environments = ["production", "test", "development", "pytest"]
        expected_types = [
            ModuleOwnedPathResolver,
            SharedPathResolver,
            ConfigurablePathResolver,
            TemporaryPathResolver
        ]
        
        # ACT & ASSERT
        for env, expected_type in zip(environments, expected_types):
            if env == "pytest":
                resolver = DatabasePathResolverFactory.create_resolver(
                    env=env,
                    temp_dir="/tmp/test"
                )
            else:
                resolver = DatabasePathResolverFactory.create_resolver(env=env)
            
            assert isinstance(resolver, expected_type), \
                f"Expected {expected_type.__name__} for env='{env}'"


# ============================================================================
# GraphBuilderBase Integration Tests
# ============================================================================

@pytest.mark.integration
class TestGraphBuilderBaseStrategyIntegration:
    """Test strategy pattern integration in GraphBuilderBase"""
    
    def test_explicit_db_path_overrides_strategy(self):
        """Test explicit db_path takes precedence over strategy"""
        # ARRANGE
        from modules.knowledge_graph.backend.graph_builder_base import GraphBuilderBase
        mock_data_source = MagicMock()
        
        # ACT
        builder = GraphBuilderBase(
            data_source=mock_data_source,
            db_path="/explicit/path.db"  # Explicit override
        )
        
        # ASSERT
        assert builder.db_path == "/explicit/path.db"
    
    def test_uses_resolver_strategy_when_no_explicit_path(self):
        """Test builder uses strategy when no explicit path provided"""
        # ARRANGE
        from modules.knowledge_graph.backend.graph_builder_base import GraphBuilderBase
        
        # Set test resolver
        test_resolver = SharedPathResolver(":memory:")
        GraphBuilderBase.set_path_resolver(test_resolver)
        
        mock_data_source = MagicMock()
        
        # ACT
        builder = GraphBuilderBase(data_source=mock_data_source)
        
        # ASSERT
        assert builder.db_path == ":memory:"
        
        # Cleanup
        GraphBuilderBase.set_path_resolver(None)
    
    def test_defaults_to_production_when_no_resolver(self):
        """Test builder defaults to production strategy"""
        # ARRANGE
        from modules.knowledge_graph.backend.graph_builder_base import GraphBuilderBase
        
        # Reset resolver
        GraphBuilderBase.set_path_resolver(None)
        
        mock_data_source = MagicMock()
        
        # ACT
        builder = GraphBuilderBase(data_source=mock_data_source)
        
        # ASSERT
        assert builder.db_path == "modules/knowledge_graph/database/graph_cache.db"


# ============================================================================
# Edge Cases & Error Handling
# ============================================================================

@pytest.mark.unit
class TestEdgeCases:
    """Test edge cases and error handling"""
    
    def test_empty_module_name(self):
        """Test handling of empty module name"""
        # ARRANGE
        resolver = ModuleOwnedPathResolver()
        
        # ACT
        path = resolver.resolve_path("")
        
        # ASSERT
        assert path == "modules//database/.db"  # Graceful degradation
    
    def test_module_name_with_special_chars(self):
        """Test module names with special characters"""
        # ARRANGE
        resolver = ModuleOwnedPathResolver()
        
        # ACT
        path = resolver.resolve_path("my-module_v2")
        
        # ASSERT
        assert path == "modules/my-module_v2/database/my-module_v2.db"
    
    def test_configurable_resolver_empty_config(self, tmp_path):
        """Test ConfigurablePathResolver with empty config file"""
        # ARRANGE
        config_file = tmp_path / "empty.json"
        config_file.write_text('{}', encoding='utf-8')
        
        resolver = ConfigurablePathResolver(str(config_file))
        
        # ACT
        path = resolver.resolve_path("knowledge_graph")
        
        # ASSERT - Falls back to module-owned
        assert path == "modules/knowledge_graph/database/graph_cache.db"


# ============================================================================
# Performance Tests
# ============================================================================

@pytest.mark.performance
class TestResolverPerformance:
    """Test performance characteristics of resolvers"""
    
    def test_module_owned_resolver_fast(self):
        """Test ModuleOwnedPathResolver is fast (no I/O)"""
        # ARRANGE
        resolver = ModuleOwnedPathResolver()
        
        # ACT - Measure 1000 resolutions
        import time
        start = time.time()
        for _ in range(1000):
            resolver.resolve_path("knowledge_graph")
        elapsed = time.time() - start
        
        # ASSERT - Should be < 10ms for 1000 calls
        assert elapsed < 0.01, f"Too slow: {elapsed}s for 1000 calls"
    
    def test_shared_resolver_fast(self):
        """Test SharedPathResolver is fast (no I/O)"""
        # ARRANGE
        resolver = SharedPathResolver(":memory:")
        
        # ACT - Measure 1000 resolutions
        import time
        start = time.time()
        for _ in range(1000):
            resolver.resolve_path("knowledge_graph")
        elapsed = time.time() - start
        
        # ASSERT - Should be < 10ms for 1000 calls
        assert elapsed < 0.01, f"Too slow: {elapsed}s for 1000 calls"