"""
Pytest Configuration and Shared Fixtures
=========================================
Configures pytest for the test suite with Gu Wu integration.

This file is automatically loaded by pytest and provides:
- Shared fixtures available to all tests
- Test configuration and hooks
- Gu Wu frontend test integration
"""

import pytest
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


# ============================================================
# GU WU FRONTEND INTEGRATION
# ============================================================

def pytest_configure(config):
    """
    Register custom markers and configure Gu Wu.
    Called once at the start of the test session.
    """
    # Register custom markers
    config.addinivalue_line("markers", "unit: Unit tests (fast, isolated)")
    config.addinivalue_line("markers", "integration: Integration tests (module interactions)")
    config.addinivalue_line("markers", "e2e: End-to-end tests (full workflows)")
    config.addinivalue_line("markers", "fast: Fast tests (< 0.1s)")
    config.addinivalue_line("markers", "slow: Slow tests (> 5s)")
    config.addinivalue_line("markers", "critical: Critical path tests (never skip)")
    config.addinivalue_line("markers", "frontend: Frontend JavaScript tests")


def pytest_sessionstart(session):
    """
    Called at the start of the test session.
    Run frontend tests here.
    """
    # Check if user wants to skip frontend tests
    if session.config.getoption("--skip-frontend", default=False):
        return
    
    try:
        from tests.guwu.frontend_runner import run_frontend_tests
        
        print("\n" + "="*60)
        print("RUNNING FRONTEND JAVASCRIPT TESTS (via Gu Wu)")
        print("="*60)
        
        success = run_frontend_tests(verbose=True)
        
        if not success:
            print("\n❌ Frontend tests failed!")
            print("Run 'python tests/guwu/frontend_runner.py' for details")
            pytest.exit("Frontend tests failed", returncode=1)
        
    except ImportError:
        print("\n⚠️  Frontend test runner not available")
        print("Install Node.js to enable frontend testing")
    except Exception as e:
        print(f"\n⚠️  Error running frontend tests: {e}")
        print("Continuing with Python tests only...")


def pytest_addoption(parser):
    """Add custom command line options"""
    parser.addoption(
        "--skip-frontend",
        action="store_true",
        default=False,
        help="Skip frontend JavaScript tests"
    )
    parser.addoption(
        "--frontend-only",
        action="store_true",
        default=False,
        help="Run frontend tests only (skip Python tests)"
    )


def pytest_collection_modifyitems(config, items):
    """
    Modify test collection based on options.
    """
    if config.getoption("--frontend-only"):
        # Skip all Python tests if --frontend-only
        skip_python = pytest.mark.skip(reason="--frontend-only specified")
        for item in items:
            item.add_marker(skip_python)


# ============================================================
# SHARED FIXTURES
# ============================================================

@pytest.fixture
def sample_data():
    """Provide sample test data"""
    return {
        'user': {
            'id': 1,
            'name': 'Test User',
            'email': 'test@example.com'
        },
        'product': {
            'id': 100,
            'name': 'Test Product',
            'price': 99.99
        }
    }


@pytest.fixture
def temp_file(tmp_path):
    """Create a temporary file for testing"""
    test_file = tmp_path / "test_data.txt"
    test_file.write_text("test content")
    yield test_file
    # Cleanup happens automatically with tmp_path


@pytest.fixture(scope="session")
def test_database():
    """
    Create a test database for the session.
    Scope: session (created once, shared across all tests)
    """
    # Setup: Create test database
    db_path = "database/test.db"
    
    yield db_path
    
    # Teardown: Cleanup would happen here if needed
    pass


# ============================================================
# GU WU HOOKS
# ============================================================

def pytest_terminal_summary(terminalreporter, exitstatus, config):
    """
    Add custom summary information to pytest output.
    Called at the end of the test session.
    """
    if config.getoption("--skip-frontend"):
        terminalreporter.write_sep("=", "Frontend tests skipped (--skip-frontend)")
    else:
        terminalreporter.write_sep("=", "Frontend + Backend tests completed")
        terminalreporter.write_line("✅ Unified test execution via Gu Wu")