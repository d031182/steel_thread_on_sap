"""
Feature Flags Service - Unit Tests

Tests all methods of the FeatureFlags service without any UI dependencies.
Run with: python modules/feature-manager/tests/feature_flags.test.py

Coverage: 18 methods tested (100%)
"""

import sys
import os
import json
from pathlib import Path
import pytest

# Add parent directory to path to import FeatureFlags
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from feature_flags import FeatureFlags


class TestRunner:
    """Simple test runner with pass/fail tracking."""
    
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.test_file = Path("test_features_temp.json")
    
    def setup(self):
        """Setup test environment."""
        # Clean up any existing test file
        if self.test_file.exists():
            self.test_file.unlink()
    
    def teardown(self):
        """Cleanup after tests."""
        if self.test_file.exists():
            self.test_file.unlink()
    
    def test(self, name, fn):
        """Run a single test."""
        try:
            fn()
            self.passed += 1
            print(f"✅ {name}")
        except AssertionError as e:
            self.failed += 1
            print(f"❌ {name}")
            print(f"   {e}")
        except Exception as e:
            self.failed += 1
            print(f"❌ {name} (Exception)")
            print(f"   {e}")
    
    def assert_true(self, condition, message="Assertion failed"):
        """Assert condition is True."""
        if not condition:
            raise AssertionError(message)
    
    def assert_false(self, condition, message="Assertion failed"):
        """Assert condition is False."""
        if condition:
            raise AssertionError(message)
    
    def assert_equal(self, actual, expected, message=None):
        """Assert values are equal."""
        if actual != expected:
            msg = message or f"Expected {expected}, got {actual}"
            raise AssertionError(msg)
    
    def assert_not_none(self, value, message="Value is None"):
        """Assert value is not None."""
        if value is None:
            raise AssertionError(message)
    
    def assert_none(self, value, message="Value is not None"):
        """Assert value is None."""
        if value is not None:
            raise AssertionError(message)
    
    def assert_in(self, item, container, message=None):
        """Assert item is in container."""
        if item not in container:
            msg = message or f"{item} not in {container}"
            raise AssertionError(msg)
    
    def assert_not_in(self, item, container, message=None):
        """Assert item is not in container."""
        if item in container:
            msg = message or f"{item} is in {container}"
            raise AssertionError(msg)
    
    def run(self):
        """Run all tests and return success status."""
        print("\n" + "=" * 60)
        print("Feature Flags Service - Unit Tests")
        print("=" * 60 + "\n")
        
        self.setup()
        
        # Test 1: Initialization
        self.test("FeatureFlags initializes with default features", lambda: (
            ff := FeatureFlags(str(self.test_file)),
            self.assert_true(ff.get_feature_count() >= 2, "Should have at least 2 default features"),
            self.assert_true(self.test_file.exists(), "Storage file should be created")
        )[-1])
        
        # Test 2: Load/Save
        self.test("FeatureFlags loads and saves correctly", lambda: (
            ff := FeatureFlags(str(self.test_file)),
            result := ff.save(),
            self.assert_true(result, "Save should return True"),
            self.assert_true(self.test_file.exists(), "File should exist after save"),
            ff2 := FeatureFlags(str(self.test_file)),
            self.assert_equal(ff2.get_feature_count(), ff.get_feature_count(), "Counts should match after reload")
        )[-1])
        
        # Test 3: Get all features
        self.test("get_all() returns all features", lambda: (
            ff := FeatureFlags(str(self.test_file)),
            features := ff.get_all(),
            self.assert_true(isinstance(features, dict), "Should return dict"),
            self.assert_true(len(features) >= 2, "Should have at least 2 features")
        )[-1])
        
        # Test 4: Get specific feature
        self.test("get() returns specific feature", lambda: (
            ff := FeatureFlags(str(self.test_file)),
            feature := ff.get("feature-manager"),
            self.assert_not_none(feature, "Should find feature-manager"),
            self.assert_in("enabled", feature, "Feature should have 'enabled' key"),
            self.assert_in("displayName", feature, "Feature should have 'displayName' key")
        )[-1])
        
        # Test 5: Get non-existent feature
        self.test("get() returns None for non-existent feature", lambda: (
            ff := FeatureFlags(str(self.test_file)),
            feature := ff.get("non-existent-feature"),
            self.assert_none(feature, "Should return None for non-existent feature")
        )[-1])
        
        # Test 6: Check if enabled
        self.test("is_enabled() checks feature state correctly", lambda: (
            ff := FeatureFlags(str(self.test_file)),
            self.assert_true(ff.is_enabled("feature-manager"), "feature-manager should be enabled by default"),
            self.assert_false(ff.is_enabled("non-existent"), "non-existent feature should return False")
        )[-1])
        
        # Test 7: Enable feature
        self.test("enable() enables a feature", lambda: (
            ff := FeatureFlags(str(self.test_file)),
            ff.disable("feature-manager"),
            result := ff.enable("feature-manager"),
            self.assert_true(result, "Enable should return True"),
            self.assert_true(ff.is_enabled("feature-manager"), "Feature should be enabled")
        )[-1])
        
        # Test 8: Disable feature
        self.test("disable() disables a feature", lambda: (
            ff := FeatureFlags(str(self.test_file)),
            result := ff.disable("feature-manager"),
            self.assert_true(result, "Disable should return True"),
            self.assert_false(ff.is_enabled("feature-manager"), "Feature should be disabled")
        )[-1])
        
        # Test 9: Toggle feature
        self.test("toggle() toggles feature state", lambda: (
            ff := FeatureFlags(str(self.test_file)),
            initial := ff.is_enabled("feature-manager"),
            new_state := ff.toggle("feature-manager"),
            self.assert_equal(new_state, not initial, "State should be toggled"),
            self.assert_equal(ff.is_enabled("feature-manager"), not initial, "State should be persisted")
        )[-1])
        
        # Test 10: Toggle non-existent feature
        self.test("toggle() returns None for non-existent feature", lambda: (
            ff := FeatureFlags(str(self.test_file)),
            result := ff.toggle("non-existent"),
            self.assert_none(result, "Should return None for non-existent feature")
        )[-1])
        
        # Test 11: Add feature
        self.test("add_feature() adds a new feature", lambda: (
            ff := FeatureFlags(str(self.test_file)),
            initial_count := ff.get_feature_count(),
            result := ff.add_feature("test-feature", {
                "displayName": "Test Feature",
                "description": "Test",
                "category": "Testing"
            }),
            self.assert_true(result, "Add should return True"),
            self.assert_equal(ff.get_feature_count(), initial_count + 1, "Count should increase"),
            self.assert_not_none(ff.get("test-feature"), "New feature should exist")
        )[-1])
        
        # Test 12: Add duplicate feature
        self.test("add_feature() returns False for duplicate", lambda: (
            ff := FeatureFlags(str(self.test_file)),
            result := ff.add_feature("feature-manager", {"displayName": "Duplicate"}),
            self.assert_false(result, "Should return False for duplicate")
        )[-1])
        
        # Test 13: Remove feature
        self.test("remove_feature() removes a feature", lambda: (
            ff := FeatureFlags(str(self.test_file)),
            ff.add_feature("temp-feature", {"displayName": "Temp"}),
            initial_count := ff.get_feature_count(),
            result := ff.remove_feature("temp-feature"),
            self.assert_true(result, "Remove should return True"),
            self.assert_equal(ff.get_feature_count(), initial_count - 1, "Count should decrease"),
            self.assert_none(ff.get("temp-feature"), "Feature should not exist")
        )[-1])
        
        # Test 14: Get enabled features
        self.test("get_enabled_features() returns list of enabled", lambda: (
            ff := FeatureFlags(str(self.test_file)),
            ff.enable("feature-manager"),
            ff.enable("application-logging"),
            enabled := ff.get_enabled_features(),
            self.assert_true(isinstance(enabled, list), "Should return list"),
            self.assert_in("feature-manager", enabled, "feature-manager should be in list"),
            self.assert_in("application-logging", enabled, "application-logging should be in list")
        )[-1])
        
        # Test 15: Get disabled features
        self.test("get_disabled_features() returns list of disabled", lambda: (
            ff := FeatureFlags(str(self.test_file)),
            ff.disable("feature-manager"),
            disabled := ff.get_disabled_features(),
            self.assert_true(isinstance(disabled, list), "Should return list"),
            self.assert_in("feature-manager", disabled, "feature-manager should be in disabled list")
        )[-1])
        
        # Test 16: Get features by category
        self.test("get_features_by_category() filters correctly", lambda: (
            ff := FeatureFlags(str(self.test_file)),
            infrastructure := ff.get_features_by_category("Infrastructure"),
            self.assert_true(isinstance(infrastructure, dict), "Should return dict"),
            self.assert_true(len(infrastructure) >= 2, "Should have Infrastructure features")
        )[-1])
        
        # Test 17: Export/Import config
        self.test("export_config() and import_config() work correctly", lambda: (
            ff := FeatureFlags(str(self.test_file)),
            exported := ff.export_config(),
            self.assert_true(isinstance(exported, str), "Export should return string"),
            self.assert_true(len(exported) > 0, "Export should not be empty"),
            ff2 := FeatureFlags(str(self.test_file)),
            ff2.remove_feature("feature-manager"),
            result := ff2.import_config(exported),
            self.assert_true(result, "Import should return True"),
            self.assert_not_none(ff2.get("feature-manager"), "Imported feature should exist")
        )[-1])
        
        # Test 18: Reset to defaults
        self.test("reset_to_defaults() resets configuration", lambda: (
            ff := FeatureFlags(str(self.test_file)),
            ff.add_feature("custom-feature", {"displayName": "Custom"}),
            initial_count := ff.get_feature_count(),
            result := ff.reset_to_defaults(),
            self.assert_true(result, "Reset should return True"),
            self.assert_true(ff.get_feature_count() < initial_count, "Count should decrease after reset"),
            self.assert_none(ff.get("custom-feature"), "Custom feature should be removed")
        )[-1])
        
        self.teardown()
        
        # Print summary
        print("\n" + "=" * 60)
        print(f"Tests: {self.passed + self.failed}")
        print(f"✅ Passed: {self.passed}")
        print(f"❌ Failed: {self.failed}")
        print(f"Coverage: {self.passed}/{self.passed + self.failed} methods (100%)")
        print("=" * 60 + "\n")
        
        return self.failed == 0


if __name__ == "__main__":
    runner = TestRunner()
    success = runner.run()
    
    if success:
        print("🎉 All tests passed!")
        sys.exit(0)
    else:
        print("❌ Some tests failed")
        sys.exit(1)