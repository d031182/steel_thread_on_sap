"""
Gu Wu Testing Framework - Shared Fixtures and Configuration

This file is automatically loaded by pytest and provides:
1. Shared fixtures for all tests
2. Gu Wu plugin integration (metrics collection, auto-optimization)
3. Test session hooks for self-learning
"""

import pytest
import sys
import time
from pathlib import Path
from datetime import datetime

# Add project root and tests directory to Python path
project_root = Path(__file__).parent.parent
tests_root = Path(__file__).parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(tests_root))

# Import Gu Wu components (using relative path)
from guwu.metrics import get_collector, TestMetric


# ============================================================================
# GU WU PLUGIN INTEGRATION - Self-Learning & Auto-Optimization
# ============================================================================

def pytest_configure(config):
    """Initialize Gu Wu at session start"""
    config.guwu_collector = get_collector()
    config.guwu_session_start = time.time()
    config.guwu_enabled = True  # Always enabled in Phase 1
    
    try:
        print("\n🥋 Gu Wu (顾武) Testing Framework - Active")
        print("   Self-learning and auto-optimization enabled\n")
    except UnicodeEncodeError:
        # Fallback for Windows terminals that don't support emojis
        print("\n[Gu Wu] Testing Framework - Active")
        print("   Self-learning and auto-optimization enabled\n")


def pytest_collection_modifyitems(config, items):
    """
    Auto-prioritize tests based on Gu Wu learning (Phase 1).
    
    Tests are reordered to run likely-to-fail tests first for faster feedback.
    """
    if not config.guwu_enabled:
        return
    
    collector = config.guwu_collector
    priorities = dict(collector.get_test_priorities())
    
    if not priorities:
        return  # No historical data yet
    
    # Reorder tests: High priority (likely to fail) → Low priority
    items.sort(key=lambda item: priorities.get(item.nodeid, 0.0), reverse=True)
    
    high_priority_count = sum(1 for item in items if priorities.get(item.nodeid, 0.0) > 0.5)
    if high_priority_count > 0:
        print(f"🎯 Gu Wu: Prioritized {high_priority_count} likely-to-fail tests\n")


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """Collect metrics for each test execution"""
    outcome = yield
    report = outcome.get_result()
    
    if report.when == 'call':  # Only record actual test execution (not setup/teardown)
        config = item.config
        if not config.guwu_enabled:
            return
        
        collector = config.guwu_collector
        
        # Extract test information
        test_id = item.nodeid
        test_name = item.name
        
        # Determine module and layer
        path_parts = Path(test_id).parts
        if 'modules' in path_parts:
            module_idx = path_parts.index('modules') + 1
            module = path_parts[module_idx] if module_idx < len(path_parts) else 'unknown'
        elif 'core' in path_parts:
            module = 'core'
        else:
            module = 'unknown'
        
        # Determine layer from path
        if 'unit' in path_parts:
            layer = 'unit'
        elif 'integration' in path_parts:
            layer = 'integration'
        elif 'e2e' in path_parts:
            layer = 'e2e'
        else:
            layer = 'unit'  # Default assumption
        
        # Get markers
        markers = ','.join(mark.name for mark in item.iter_markers())
        
        # Create metric
        metric = TestMetric(
            test_id=test_id,
            test_name=test_name,
            module=module,
            layer=layer,
            duration=report.duration,
            outcome=report.outcome,
            timestamp=datetime.now().isoformat(),
            markers=markers,
            coverage_delta=0.0,  # Will be updated from coverage report
            error_message=str(report.longrepr) if report.failed else None
        )
        
        # Record in Gu Wu
        collector.record_test(metric)


def pytest_sessionfinish(session, exitstatus):
    """Generate Gu Wu insights at session end"""
    config = session.config
    if not config.guwu_enabled:
        return
    
    collector = config.guwu_collector
    
    # Calculate session summary
    session_duration = time.time() - config.guwu_session_start
    
    # Get test results summary
    passed = session.testscollected - session.testsfailed
    failed = session.testsfailed
    
    # Get pyramid compliance
    pyramid = collector.get_pyramid_compliance()
    
    session_summary = {
        'total': session.testscollected,
        'passed': passed,
        'failed': failed,
        'errors': 0,  # TODO: Extract from session
        'skipped': 0,  # TODO: Extract from session
        'duration': session_duration,
        'coverage': None,  # TODO: Extract from coverage report
        'pyramid_score': pyramid.get('compliance_score', 0.0)
    }
    
    collector.finalize_session(session_summary)
    
    # Generate and display insights
    insights = collector.generate_insights()
    
    if insights:
        print("\n" + "=" * 80)
        print("🥋 GU WU INSIGHTS - Autonomous Learning & Recommendations")
        print("=" * 80)
        
        for insight in insights:
            severity_icon = {
                'high': '🔴',
                'medium': '🟡',
                'low': '🟢'
            }.get(insight['severity'], '⚪')
            
            print(f"\n{severity_icon} {insight['type'].upper()}")
            print(f"   {insight['description']}")
            print(f"   💡 {insight['recommendation']}")
            print(f"   Confidence: {insight['confidence']:.0%}")
        
        print("\n" + "=" * 80)
        print(f"📊 Pyramid Compliance: {pyramid['unit_pct']}% unit / {pyramid['integration_pct']}% integration / {pyramid['e2e_pct']}% e2e")
        print(f"   Target: 70% / 20% / 10% | Score: {pyramid['compliance_score']:.0%}")
        print("=" * 80 + "\n")


# ============================================================================
# SHARED FIXTURES - Available to All Tests
# ============================================================================

@pytest.fixture(scope="session")
def test_app():
    """
    Create Flask test application (session-scoped, created once).
    
    Usage:
        def test_api_endpoint(test_app):
            response = test_app.get('/api/endpoint')
            assert response.status_code == 200
    """
    from flask import Flask
    from app.app import create_app
    
    app = create_app()
    app.config['TESTING'] = True
    app.config['DATABASE'] = ':memory:'  # Use in-memory DB for tests
    
    with app.test_client() as client:
        with app.app_context():
            yield client


@pytest.fixture
def sample_data_product():
    """
    Create sample data product (function-scoped, fresh for each test).
    
    Usage:
        def test_data_product_creation(sample_data_product):
            assert sample_data_product['name'] == 'TestProduct'
    """
    product = {
        'name': 'TestProduct',
        'version': '1.0.0',
        'description': 'Test data product for automated testing',
        'entities': ['Entity1', 'Entity2'],
        'csn_url': 'https://example.com/csn/TestProduct.json'
    }
    
    yield product
    
    # Cleanup (if needed)
    # cleanup_data_product(product['name'])


@pytest.fixture
def mock_database(monkeypatch):
    """
    Mock database for isolated testing (function-scoped).
    
    Usage:
        def test_database_query(mock_database):
            mock_database.set_return_value([{'id': 1, 'name': 'Test'}])
            result = query_database('SELECT * FROM table')
            assert len(result) == 1
    """
    class MockDatabase:
        def __init__(self):
            self.return_value = []
            self.queries_executed = []
        
        def execute(self, query, params=None):
            self.queries_executed.append((query, params))
            return self.return_value
        
        def set_return_value(self, value):
            self.return_value = value
    
    mock_db = MockDatabase()
    # monkeypatch.setattr('app.database.get_connection', lambda: mock_db)
    
    return mock_db


@pytest.fixture
def mock_hana_connection(monkeypatch):
    """
    Mock HANA connection for testing without actual HANA access.
    
    Usage:
        def test_hana_query(mock_hana_connection):
            result = execute_hana_query('SELECT * FROM table')
            assert result is not None
    """
    class MockHANAConnection:
        def __init__(self):
            self.connected = False
            self.queries = []
        
        def connect(self):
            self.connected = True
            return True
        
        def execute(self, query):
            self.queries.append(query)
            return [{'id': 1, 'name': 'Mock Data'}]
        
        def close(self):
            self.connected = False
    
    mock = MockHANAConnection()
    # monkeypatch.setattr('modules.hana_connection.backend.connection', mock)
    
    return mock


@pytest.fixture
def temp_test_db(tmp_path):
    """
    Create temporary SQLite database for testing (function-scoped).
    
    Automatically cleaned up after test.
    
    Usage:
        def test_database_operations(temp_test_db):
            # temp_test_db is a Path object to temporary database
            # Use it for testing without affecting real database
            pass
    """
    db_path = tmp_path / "test.db"
    yield db_path
    # Automatic cleanup by pytest's tmp_path fixture


@pytest.fixture(scope="session")
def test_data_directory(tmp_path_factory):
    """
    Create temporary directory for test data (session-scoped).
    
    Usage:
        def test_file_operations(test_data_directory):
            test_file = test_data_directory / "test.json"
            test_file.write_text('{"key": "value"}')
            assert test_file.exists()
    """
    data_dir = tmp_path_factory.mktemp("test_data")
    return data_dir


# ============================================================================
# TEST MARKERS EXAMPLES
# ============================================================================

# To use markers in tests:
#
# @pytest.mark.unit
# @pytest.mark.fast
# def test_simple_function():
#     assert 2 + 2 == 4
#
# @pytest.mark.integration
# @pytest.mark.slow
# def test_module_interaction():
#     # Test that takes > 1 second
#     pass
#
# @pytest.mark.e2e
# @pytest.mark.critical
# def test_user_workflow():
#     # Critical user path - never skip
#     pass


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def assert_api_response_structure(response, required_fields):
    """
    Helper to validate API response structure.
    
    Usage:
        response = client.get('/api/products')
        assert_api_response_structure(response.json(), ['products', 'total', 'page'])
    """
    data = response if isinstance(response, dict) else response.json()
    
    for field in required_fields:
        assert field in data, f"Missing required field: {field}"
    
    return True


def create_test_user(**kwargs):
    """Helper to create test user with defaults"""
    defaults = {
        'username': 'testuser',
        'email': 'test@example.com',
        'role': 'user'
    }
    defaults.update(kwargs)
    return defaults


# ============================================================================
# GU WU STATUS INDICATOR
# ============================================================================

print("=" * 80)
print("🥋 GU WU (顾武) TESTING FRAMEWORK")
print("=" * 80)
print("Philosophy: Attending to martial affairs with discipline")
print("Status: Self-learning and auto-optimization ACTIVE")
print("=" * 80)