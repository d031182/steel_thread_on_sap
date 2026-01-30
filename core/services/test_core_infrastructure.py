"""
Unit Tests for Core Infrastructure

Tests:
1. ModuleRegistry - Auto-discovery and module management
2. PathResolver - Configuration-driven path resolution

Run with: python core/backend/test_core_infrastructure.py
"""

import sys
import os
import json
import tempfile
import shutil
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from core.services.module_registry import ModuleRegistry, get_registry, reload_registry
from core.services.path_resolver import PathResolver, GlobalPathResolver


class TestRunner:
    """Simple test runner without external dependencies."""
    
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.tests = []
    
    def test(self, name, fn):
        """Run a single test."""
        try:
            fn()
            self.passed += 1
            print(f"✅ {name}")
            self.tests.append((name, True, None))
        except AssertionError as e:
            self.failed += 1
            print(f"❌ {name}")
            print(f"   {str(e)}")
            self.tests.append((name, False, str(e)))
        except Exception as e:
            self.failed += 1
            print(f"❌ {name} (Unexpected error)")
            print(f"   {str(e)}")
            self.tests.append((name, False, f"Unexpected: {str(e)}"))
    
    def assert_equal(self, actual, expected, message=""):
        """Assert two values are equal."""
        if actual != expected:
            raise AssertionError(
                f"{message}\n  Expected: {expected}\n  Got: {actual}"
            )
    
    def assert_true(self, condition, message="Condition is not True"):
        """Assert condition is True."""
        if not condition:
            raise AssertionError(message)
    
    def assert_false(self, condition, message="Condition is not False"):
        """Assert condition is False."""
        if condition:
            raise AssertionError(message)
    
    def assert_not_none(self, value, message="Value is None"):
        """Assert value is not None."""
        if value is None:
            raise AssertionError(message)
    
    def assert_is_none(self, value, message="Value is not None"):
        """Assert value is None."""
        if value is not None:
            raise AssertionError(message)
    
    def assert_in(self, item, container, message=""):
        """Assert item is in container."""
        if item not in container:
            raise AssertionError(f"{message}\n  '{item}' not found in {container}")
    
    def summary(self):
        """Print test summary."""
        total = self.passed + self.failed
        print(f"\n{'='*60}")
        print(f"Test Results: {self.passed}/{total} passed")
        if self.failed > 0:
            print(f"\nFailed tests:")
            for name, success, error in self.tests:
                if not success:
                    print(f"  - {name}: {error}")
        print(f"{'='*60}\n")
        return self.failed == 0


def create_test_module(base_dir, module_name, module_config):
    """Helper to create a test module directory with module.json."""
    module_dir = Path(base_dir) / module_name
    module_dir.mkdir(parents=True, exist_ok=True)
    
    # Create module.json
    with open(module_dir / "module.json", 'w') as f:
        json.dump(module_config, f, indent=2)
    
    # Create standard directories
    (module_dir / "backend").mkdir(exist_ok=True)
    (module_dir / "frontend").mkdir(exist_ok=True)
    (module_dir / "tests").mkdir(exist_ok=True)
    (module_dir / "docs").mkdir(exist_ok=True)
    
    return module_dir


def test_module_registry(runner):
    """Test suite for ModuleRegistry."""
    print("\n" + "="*60)
    print("Testing ModuleRegistry")
    print("="*60 + "\n")
    
    # Create temporary modules directory
    temp_dir = tempfile.mkdtemp()
    modules_dir = Path(temp_dir) / "modules"
    modules_dir.mkdir()
    
    try:
        # Create test modules
        feature_manager_config = {
            "name": "feature-manager",
            "displayName": "Feature Manager",
            "version": "1.0.0",
            "category": "Infrastructure",
            "enabled": True
        }
        
        logging_config = {
            "name": "application-logging",
            "displayName": "Application Logging",
            "version": "1.0.0",
            "category": "Infrastructure",
            "enabled": True
        }
        
        hana_config = {
            "name": "hana-connection",
            "displayName": "HANA Connection",
            "version": "1.0.0",
            "category": "Business Logic",
            "enabled": False
        }
        
        create_test_module(modules_dir, "feature-manager", feature_manager_config)
        create_test_module(modules_dir, "application-logging", logging_config)
        create_test_module(modules_dir, "hana-connection", hana_config)
        
        # Test 1: Registry initialization and discovery
        def test_init():
            registry = ModuleRegistry(str(modules_dir))
            runner.assert_equal(registry.get_module_count(), 3, "Should discover 3 modules")
        
        runner.test("Registry discovers all modules", test_init)
        
        # Test 2: Get specific module
        def test_get_module():
            registry = ModuleRegistry(str(modules_dir))
            module = registry.get_module("feature-manager")
            runner.assert_not_none(module, "Should find feature-manager")
            runner.assert_equal(module['name'], "feature-manager")
            runner.assert_equal(module['displayName'], "Feature Manager")
        
        runner.test("Get module by name", test_get_module)
        
        # Test 3: Get non-existent module
        def test_get_nonexistent():
            registry = ModuleRegistry(str(modules_dir))
            module = registry.get_module("non-existent")
            runner.assert_is_none(module, "Should return None for non-existent module")
        
        runner.test("Get non-existent module returns None", test_get_nonexistent)
        
        # Test 4: List module names
        def test_list_names():
            registry = ModuleRegistry(str(modules_dir))
            names = registry.list_module_names()
            runner.assert_equal(len(names), 3)
            runner.assert_in("feature-manager", names)
            runner.assert_in("application-logging", names)
            runner.assert_in("hana-connection", names)
        
        runner.test("List all module names", test_list_names)
        
        # Test 5: Get modules by category
        def test_by_category():
            registry = ModuleRegistry(str(modules_dir))
            infra_modules = registry.get_modules_by_category("Infrastructure")
            runner.assert_equal(len(infra_modules), 2, "Should find 2 Infrastructure modules")
            runner.assert_in("feature-manager", infra_modules)
            runner.assert_in("application-logging", infra_modules)
        
        runner.test("Get modules by category", test_by_category)
        
        # Test 6: Get enabled modules (default)
        def test_enabled_default():
            registry = ModuleRegistry(str(modules_dir))
            enabled = registry.get_enabled_modules()
            runner.assert_equal(len(enabled), 2, "Should have 2 enabled by default")
            runner.assert_in("feature-manager", enabled)
            runner.assert_in("application-logging", enabled)
        
        runner.test("Get enabled modules (default)", test_enabled_default)
        
        # Test 7: Get enabled modules with feature flags
        def test_enabled_with_flags():
            registry = ModuleRegistry(str(modules_dir))
            flags = {
                "feature-manager": True,
                "application-logging": False,
                "hana-connection": True
            }
            enabled = registry.get_enabled_modules(flags)
            runner.assert_equal(len(enabled), 2)
            runner.assert_in("feature-manager", enabled)
            runner.assert_in("hana-connection", enabled)
        
        runner.test("Get enabled modules with feature flags", test_enabled_with_flags)
        
        # Test 8: Get module path
        def test_module_path():
            registry = ModuleRegistry(str(modules_dir))
            path = registry.get_module_path("feature-manager")
            runner.assert_not_none(path)
            runner.assert_true(path.exists(), "Module path should exist")
        
        runner.test("Get module path", test_module_path)
        
        # Test 9: Refresh registry
        def test_refresh():
            registry = ModuleRegistry(str(modules_dir))
            initial_count = registry.get_module_count()
            
            # Add new module
            new_config = {
                "name": "new-module",
                "displayName": "New Module",
                "version": "1.0.0"
            }
            create_test_module(modules_dir, "new-module", new_config)
            
            # Refresh
            registry.refresh()
            runner.assert_equal(registry.get_module_count(), initial_count + 1)
        
        runner.test("Refresh registry discovers new modules", test_refresh)
        
    finally:
        # Cleanup
        shutil.rmtree(temp_dir, ignore_errors=True)


def test_path_resolver(runner):
    """Test suite for PathResolver."""
    print("\n" + "="*60)
    print("Testing PathResolver")
    print("="*60 + "\n")
    
    # Create test module config
    module_config = {
        "name": "test-module",
        "displayName": "Test Module",
        "version": "1.0.0",
        "structure": {
            "backend": "backend",
            "frontend": "frontend",
            "tests": "tests",
            "docs": "documentation"  # Custom path
        }
    }
    
    base_path = Path("modules/test-module")
    
    # Test 1: Basic path resolution
    def test_basic_resolve():
        resolver = PathResolver(module_config, base_path)
        backend_path = resolver.resolve('backend')
        runner.assert_equal(str(backend_path), "modules\\test-module\\backend" if os.name == 'nt' else "modules/test-module/backend")
    
    runner.test("Resolve basic path", test_basic_resolve)
    
    # Test 2: Path resolution with filename
    def test_resolve_with_file():
        resolver = PathResolver(module_config, base_path)
        api_path = resolver.resolve('backend', 'api.py')
        expected = str(base_path / "backend" / "api.py")
        runner.assert_equal(str(api_path), expected)
    
    runner.test("Resolve path with filename", test_resolve_with_file)
    
    # Test 3: Shortcut methods
    def test_shortcuts():
        resolver = PathResolver(module_config, base_path)
        runner.assert_equal(resolver.backend(), resolver.resolve('backend'))
        runner.assert_equal(resolver.frontend(), resolver.resolve('frontend'))
        runner.assert_equal(resolver.tests(), resolver.resolve('tests'))
        runner.assert_equal(resolver.docs(), resolver.resolve('docs'))
    
    runner.test("Shortcut methods work", test_shortcuts)
    
    # Test 4: Custom structure path
    def test_custom_structure():
        resolver = PathResolver(module_config, base_path)
        docs_path = resolver.resolve('docs')
        # Should use custom "documentation" path from config
        runner.assert_true("documentation" in str(docs_path))
    
    runner.test("Custom structure paths from config", test_custom_structure)
    
    # Test 5: Relative path
    def test_relative_path():
        resolver = PathResolver(module_config, base_path)
        rel_path = resolver.get_relative_path('backend', 'api.py')
        runner.assert_true('/' in rel_path, "Should use forward slashes")
        runner.assert_true(rel_path.startswith('modules/test-module'))
    
    runner.test("Get relative path with forward slashes", test_relative_path)
    
    # Test 6: Default structure fallback
    def test_default_fallback():
        minimal_config = {"name": "minimal"}
        resolver = PathResolver(minimal_config, base_path)
        # Should use default structure
        backend_path = resolver.backend()
        runner.assert_true("backend" in str(backend_path))
    
    runner.test("Default structure fallback", test_default_fallback)


def test_global_path_resolver(runner):
    """Test suite for GlobalPathResolver."""
    print("\n" + "="*60)
    print("Testing GlobalPathResolver")
    print("="*60 + "\n")
    
    # Create temporary modules
    temp_dir = tempfile.mkdtemp()
    modules_dir = Path(temp_dir) / "modules"
    modules_dir.mkdir()
    
    try:
        # Create test module
        config = {
            "name": "test-module",
            "displayName": "Test Module",
            "version": "1.0.0",
            "structure": {"backend": "backend"}
        }
        create_test_module(modules_dir, "test-module", config)
        
        # Test 1: Get resolver for module
        def test_get_resolver():
            registry = ModuleRegistry(str(modules_dir))
            global_resolver = GlobalPathResolver(registry)
            
            resolver = global_resolver.get_resolver("test-module")
            runner.assert_not_none(resolver)
        
        runner.test("Get resolver for module", test_get_resolver)
        
        # Test 2: Resolve path through global resolver
        def test_global_resolve():
            registry = ModuleRegistry(str(modules_dir))
            global_resolver = GlobalPathResolver(registry)
            
            path = global_resolver.resolve("test-module", "backend", "api.py")
            runner.assert_not_none(path)
            runner.assert_true("backend" in str(path))
            runner.assert_true("api.py" in str(path))
        
        runner.test("Resolve path through global resolver", test_global_resolve)
        
        # Test 3: Cache resolvers
        def test_resolver_cache():
            registry = ModuleRegistry(str(modules_dir))
            global_resolver = GlobalPathResolver(registry)
            
            # First call
            resolver1 = global_resolver.get_resolver("test-module")
            # Second call (should be cached)
            resolver2 = global_resolver.get_resolver("test-module")
            
            runner.assert_true(resolver1 is resolver2, "Should return cached resolver")
        
        runner.test("Resolver caching works", test_resolver_cache)
        
        # Test 4: Clear cache
        def test_clear_cache():
            registry = ModuleRegistry(str(modules_dir))
            global_resolver = GlobalPathResolver(registry)
            
            global_resolver.get_resolver("test-module")
            runner.assert_equal(len(global_resolver._resolvers), 1)
            
            global_resolver.clear_cache()
            runner.assert_equal(len(global_resolver._resolvers), 0)
        
        runner.test("Clear resolver cache", test_clear_cache)
        
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)


def main():
    """Run all tests."""
    print("\n" + "="*60)
    print("CORE INFRASTRUCTURE TEST SUITE")
    print("="*60)
    
    runner = TestRunner()
    
    # Run test suites
    test_module_registry(runner)
    test_path_resolver(runner)
    test_global_path_resolver(runner)
    
    # Print summary
    success = runner.summary()
    
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())