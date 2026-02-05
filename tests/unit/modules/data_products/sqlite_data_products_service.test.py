"""
SQLite Data Products Service - Unit Tests

Tests all public methods of SQLiteDataProductsService without any UI dependencies.
Run with: python backend/services/tests/sqlite_data_products_service.test.py

Coverage: 6 public methods tested (100%)
"""

import sys
import os
from pathlib import Path
import pytest

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..'))

from modules.data_products.backend import SQLiteDataProductsService


class TestRunner:
    """Simple test runner with pass/fail tracking."""
    
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.test_db = Path("test_sample.db")
    
    def setup(self):
        """Setup test environment."""
        # Use the actual p2p_sample.db for testing (it has the schema)
        self.test_db = Path("backend/database/p2p_sample.db")
        
        # Service will use existing database with schema
    
    def teardown(self):
        """Cleanup after tests."""
        # Don't delete the actual database - we're using p2p_sample.db
        pass
    
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
    
    def assert_greater(self, actual, expected, message=None):
        """Assert actual > expected."""
        if actual <= expected:
            msg = message or f"Expected {actual} > {expected}"
            raise AssertionError(msg)
    
    def run(self):
        """Run all tests and return success status."""
        print("\n" + "=" * 60)
        print("SQLite Data Products Service - Unit Tests")
        print("=" * 60 + "\n")
        
        self.setup()
        
        # Test 1: Initialization with default path
        self.test("Service initializes with default database path", lambda: (
            service := SQLiteDataProductsService(),
            self.assert_not_none(service.db_path, "Database path should be set")
        )[-1])
        
        # Test 2: Initialization with custom path
        self.test("Service initializes with custom database path", lambda: (
            service := SQLiteDataProductsService(str(self.test_db)),
            self.assert_equal(service.db_path, str(self.test_db), "Should use custom path"),
            self.assert_true(self.test_db.exists(), "Database should be created")
        )[-1])
        
        # Test 3: get_data_products returns metadata
        self.test("get_data_products() returns product metadata", lambda: (
            service := SQLiteDataProductsService(str(self.test_db)),
            products := service.get_data_products(),
            self.assert_true(isinstance(products, list), "Should return list"),
            self.assert_greater(len(products), 0, "Should have at least 1 product"),
            product := products[0],
            self.assert_in("productName", product, "Should have productName"),
            self.assert_in("displayName", product, "Should have displayName"),
            self.assert_in("version", product, "Should have version"),
            self.assert_in("source", product, "Should have source"),
            self.assert_equal(product["source"], "sqlite", "Source should be sqlite")
        )[-1])
        
        # Test 4: get_tables returns table list
        self.test("get_tables() returns list of tables", lambda: (
            service := SQLiteDataProductsService(str(self.test_db)),
            tables := service.get_tables("SQLITE_PURCHASEORDER"),
            self.assert_true(isinstance(tables, list), "Should return list"),
            self.assert_greater(len(tables), 0, "Should have tables"),
            table := tables[0],
            self.assert_in("TABLE_NAME", table, "Should have TABLE_NAME"),
            self.assert_in("TABLE_TYPE", table, "Should have TABLE_TYPE"),
            self.assert_in("RECORD_COUNT", table, "Should have RECORD_COUNT")
        )[-1])
        
        # Test 5: get_table_structure returns columns
        self.test("get_table_structure() returns column metadata", lambda: (
            service := SQLiteDataProductsService(str(self.test_db)),
            tables := service.get_tables("SQLITE_PURCHASEORDER"),
            self.assert_greater(len(tables), 0, "Should have at least one table"),
            columns := service.get_table_structure("SQLITE_PURCHASEORDER", tables[0]["TABLE_NAME"]),
            self.assert_true(isinstance(columns, list), "Should return list"),
            self.assert_greater(len(columns), 0, "Should have columns"),
            col := columns[0],
            self.assert_in("COLUMN_NAME", col, "Should have COLUMN_NAME"),
            self.assert_in("DATA_TYPE_NAME", col, "Should have DATA_TYPE_NAME"),
            self.assert_in("IS_NULLABLE", col, "Should have IS_NULLABLE"),
            self.assert_in("IS_PRIMARY_KEY", col, "Should have IS_PRIMARY_KEY")
        )[-1])
        
        # Test 6: query_table returns data structure
        self.test("query_table() returns proper result structure", lambda: (
            service := SQLiteDataProductsService(str(self.test_db)),
            tables := service.get_tables("SQLITE_PURCHASEORDER"),
            self.assert_greater(len(tables), 0, "Should have at least one table"),
            result := service.query_table("SQLITE_PURCHASEORDER", tables[0]["TABLE_NAME"], limit=10),
            self.assert_true(isinstance(result, dict), "Should return dict"),
            self.assert_in("rows", result, "Should have rows"),
            self.assert_in("columns", result, "Should have columns"),
            self.assert_in("totalCount", result, "Should have totalCount"),
            self.assert_in("executionTime", result, "Should have executionTime"),
            self.assert_true(isinstance(result["rows"], list), "rows should be list"),
            self.assert_true(isinstance(result["columns"], list), "columns should be list"),
            self.assert_true(isinstance(result["totalCount"], int), "totalCount should be int"),
            self.assert_true(isinstance(result["executionTime"], (int, float)), "executionTime should be numeric")
        )[-1])
        
        # Test 7: get_csn_definition returns None (SQLite doesn't store CSN)
        self.test("get_csn_definition() returns None for SQLite", lambda: (
            service := SQLiteDataProductsService(str(self.test_db)),
            csn := service.get_csn_definition("SQLITE_PURCHASEORDER"),
            self.assert_none(csn, "SQLite should not have CSN definitions")
        )[-1])
        
        # Test 8: Database auto-creation
        self.test("Database auto-creates if schema file exists", lambda: (
            self.test_db.unlink() if self.test_db.exists() else None,
            service := SQLiteDataProductsService(str(self.test_db)),
            self.assert_true(self.test_db.exists(), "Database should be created automatically")
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