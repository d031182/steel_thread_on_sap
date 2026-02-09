#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Gu Wu Human-Readable Error Reporter Plugin

Purpose: Translate cryptic pytest errors into clear, actionable explanations
Integrates: With pytest's reporting system for better developer experience

Philosophy: "The student sees errors. The master sees opportunities to learn."
"""

import pytest
import sys
from typing import Optional


class HumanReadableErrorReporter:
    """Pytest plugin for human-readable error reporting"""
    
    def __init__(self):
        self.errors_detected = []
        self.collection_errors = []
    
    @pytest.hookimpl(hookwrapper=True)
    def pytest_collectreport(self, report):
        """Capture collection errors as they happen"""
        outcome = yield
        
        if report.failed:
            # Collection error occurred
            if hasattr(report, 'longrepr') and report.longrepr:
                error_text = str(report.longrepr)
                
                # Check for I/O error pattern
                if "I/O operation on closed file" in error_text or "ValueError: I/O" in error_text:
                    self.collection_errors.append(('io_error', error_text))
                elif "ImportError" in error_text or "ModuleNotFoundError" in error_text:
                    self.collection_errors.append(('import_error', error_text))
                else:
                    self.collection_errors.append(('generic', error_text))
    
    @pytest.hookimpl(tryfirst=True)
    def pytest_exception_interact(self, node, call, report):
        """Hook into exception handling to translate errors"""
        if call.excinfo:
            error_type = call.excinfo.typename
            error_msg = str(call.excinfo.value)
            
            explanation = self._translate_error(error_type, error_msg, node)
            if explanation:
                self.errors_detected.append(explanation)
    
    @pytest.hookimpl(trylast=True)
    def pytest_terminal_summary(self, terminalreporter, exitstatus):
        """Add human-readable explanations at end of test run"""
        
        # Handle collection errors
        if self.collection_errors:
            terminalreporter.write_sep("=", "HUMAN-READABLE ERROR EXPLANATIONS", bold=True, red=True)
            terminalreporter.write_line("")
            
            for error_type, error_text in self.collection_errors:
                if error_type == 'io_error':
                    terminalreporter.write_line(self._format_flask_conflict_error())
                elif error_type == 'import_error':
                    # Try to extract module name
                    module_name = "unknown"
                    if "No module named" in error_text:
                        parts = error_text.split("'")
                        if len(parts) >= 2:
                            module_name = parts[1]
                    terminalreporter.write_line(self._format_import_error(module_name))
                else:
                    terminalreporter.write_line(self._format_collection_error())
                
                terminalreporter.write_line("")
        
        # Handle runtime errors
        elif self.errors_detected:
            terminalreporter.write_sep("=", "HUMAN-READABLE ERROR EXPLANATIONS", bold=True, red=True)
            terminalreporter.write_line("")
            
            for i, explanation in enumerate(self.errors_detected, 1):
                terminalreporter.write_line(explanation)
                if i < len(self.errors_detected):
                    terminalreporter.write_line("")
    
    def _translate_error(self, error_type: str, error_msg: str, node) -> Optional[str]:
        """Translate error to human-readable format"""
        
        # Error 1: I/O operation on closed file (Flask server conflict)
        if "I/O operation on closed file" in error_msg or error_type == "ValueError":
            if "closed file" in error_msg:
                return self._format_flask_conflict_error()
        
        # Error 2: Import errors
        if error_type in ("ImportError", "ModuleNotFoundError"):
            return self._format_import_error(error_msg)
        
        # Error 3: Assertion errors (test failures)
        if error_type == "AssertionError":
            return self._format_assertion_error(error_msg, node)
        
        # Error 4: Fixture errors
        if "fixture" in error_msg.lower():
            return self._format_fixture_error(error_msg)
        
        return None
    
    def _format_flask_conflict_error(self) -> str:
        """Format Flask server conflict error"""
        return """
┌────────────────────────────────────────────────────────────────┐
│ 🔴 ERROR: Flask Server Interfering with Tests                 │
└────────────────────────────────────────────────────────────────┘

WHAT HAPPENED:
  Your Flask development server is running (python app/app.py).
  Pytest tried to run tests while the server was active.
  This creates file handle conflicts.

WHY THIS BREAKS TESTS:
  • Flask locks files/ports that pytest needs to access
  • Both try to use the same SQLite database
  • Results in "I/O operation on closed file" errors

HOW TO FIX:
  
  ✅ Option 1: Stop Flask server first (RECOMMENDED)
     1. Find terminal running: python app/app.py
     2. Press Ctrl+C to stop the server
     3. Run: pytest
  
  ✅ Option 2: Use separate test database
     1. Configure pytest to use test-specific database
     2. Isolate test environment from dev server
  
  ✅ Option 3: Run tests in isolated terminal
     1. Open new terminal (not the one with Flask)
     2. Run: pytest
     3. Flask server continues in background (different process)

PREVENTION:
  Always stop dev server before running full test suite.
  Or use pytest-flask plugin for better server/test isolation.
"""
    
    def _format_import_error(self, module_name: str) -> str:
        """Format import/module not found error"""
        return f"""
┌────────────────────────────────────────────────────────────────┐
│ 🔴 ERROR: Missing Python Module                               │
└────────────────────────────────────────────────────────────────┘

WHAT HAPPENED:
  Pytest tried to import module '{module_name}' but it's not installed.

WHY THIS HAPPENS:
  • Package not installed in current environment
  • Typo in module name
  • Module moved/renamed without updating imports

HOW TO FIX:
  
  ✅ Option 1: Install missing package
     pip install {module_name}
  
  ✅ Option 2: Install all project dependencies
     pip install -r requirements.txt
  
  ✅ Option 3: Check for typos
     Review the import statement in the test file
     Ensure module name spelling is correct

VERIFY:
  Run: python -c "import {module_name}"
  If no error, package is installed correctly.
"""
    
    def _format_assertion_error(self, error_msg: str, node) -> str:
        """Format assertion/test failure error"""
        test_name = node.name if hasattr(node, 'name') else "unknown"
        
        return f"""
┌────────────────────────────────────────────────────────────────┐
│ 🔴 ERROR: Test Assertion Failed                               │
└────────────────────────────────────────────────────────────────┘

TEST: {test_name}

WHAT HAPPENED:
  The test's assertion failed - expected value didn't match actual value.

WHY THIS MATTERS:
  • Test caught a bug in the code
  • OR test expectations are incorrect
  • OR test data changed unexpectedly

HOW TO FIX:
  
  ✅ Step 1: Review the assertion
     Look at the "AssertionError" details above
     Compare: Expected vs Actual values
  
  ✅ Step 2: Debug the test
     Run single test: pytest {node.nodeid if hasattr(node, 'nodeid') else ''} -v
     Add print() statements to see values
     Use debugger: pytest --pdb
  
  ✅ Step 3: Fix root cause
     • If code is wrong → Fix the code
     • If test is wrong → Fix the test expectations
     • If data changed → Update test fixtures

DEBUGGING TIPS:
  • Run with -vv for more detailed output
  • Use --tb=long for full traceback
  • Add breakpoint() in test for interactive debugging
"""
    
    def _format_fixture_error(self, error_msg: str) -> str:
        """Format fixture-related error"""
        return """
┌────────────────────────────────────────────────────────────────┐
│ 🔴 ERROR: Test Fixture Problem                                │
└────────────────────────────────────────────────────────────────┘

WHAT HAPPENED:
  A pytest fixture failed to initialize or has an error.

COMMON CAUSES:
  • Fixture not defined (typo in fixture name)
  • Fixture dependency missing (fixture needs another fixture)
  • Fixture scope mismatch (function vs module vs session)
  • Error in fixture setup code

HOW TO FIX:
  
  ✅ Step 1: Check fixture name spelling
     Ensure test function parameter matches fixture name exactly
  
  ✅ Step 2: Verify fixture is defined
     Check conftest.py files in test directory and parent directories
     Run: pytest --fixtures | grep fixture_name
  
  ✅ Step 3: Check fixture dependencies
     Ensure all fixtures that this fixture depends on are defined
     Verify fixture scope is compatible (function < module < session)
  
  ✅ Step 4: Debug fixture code
     Add print() in fixture to see if it's being called
     Check for errors in fixture setup/teardown

WHERE TO LOOK:
  • tests/conftest.py (project-level fixtures)
  • tests/[category]/conftest.py (category-level fixtures)
  • Same directory as test file (local fixtures)
"""
    
    def _format_collection_error(self) -> str:
        """Format generic collection error"""
        return """
┌────────────────────────────────────────────────────────────────┐
│ 🔴 ERROR: Test Collection Failed                              │
└────────────────────────────────────────────────────────────────┘

WHAT HAPPENED:
  Pytest found errors while discovering/collecting tests.

COMMON CAUSES:
  • Syntax errors in test files
  • Import errors (missing modules)
  • Duplicate test names
  • Invalid pytest markers

HOW TO FIX:
  
  ✅ Step 1: Check syntax errors
     Look for Python syntax errors in test files
     Run: python -m py_compile path/to/test_file.py
  
  ✅ Step 2: Verify imports
     Ensure all imported modules are installed
     Check for circular imports
  
  ✅ Step 3: Run collection only
     pytest --collect-only
     This shows which tests pytest found without running them
  
  ✅ Step 4: Check test markers
     Ensure all @pytest.mark.X markers are registered in pytest.ini

DEBUGGING:
  Run with -vv to see which file caused collection to fail
"""
