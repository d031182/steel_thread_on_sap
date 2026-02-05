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
        try:
            print(f"🎯 Gu Wu: Prioritized {high_priority_count} likely-to-fail tests\n")
        except UnicodeEncodeError:
            print(f"[*] Gu Wu: Prioritized {high_priority_count} likely-to-fail tests\n")


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
    
    # AUTO-RUN ALL GU WU AUTONOMOUS TOOLS
    _run_autonomous_analysis(session)


def _run_autonomous_analysis(session):
    """
    Run Gu Wu tools intelligently based on context.
    
    Smart Decision Logic:
    - Gap Analyzer: Run when new code added or tests failed
    - Predictor: Run when failures occurred
    - Lifecycle: Run weekly or when significant test changes
    - Reflection: Run when patterns detected
    - Redundancy: Run monthly or when many new tests added
    
    Gu Wu decides which tools to use based on:
    1. Test results (passed/failed counts)
    2. Time since last run (each tool has schedule)
    3. Code changes detected (new files, modified files)
    4. Historical patterns (learning from past runs)
    """
    
    # Gather context for smart decisions
    context = _gather_analysis_context(session)
    
    # Decide which tools to run
    tools_to_run = _decide_which_tools(context)
    
    if not tools_to_run:
        return  # Nothing to do - Gu Wu staying efficient
    
    # Run only selected tools
    if 'gap_analyzer' in tools_to_run:
        _run_gap_analyzer_autonomous(session, context)
    
    if 'predictor' in tools_to_run:
        _run_predictor_autonomous(session, context)
    
    if 'lifecycle' in tools_to_run:
        _run_lifecycle_autonomous(session, context)
    
    if 'reflection' in tools_to_run:
        _run_reflection_autonomous(session, context)
    
    if 'redundancy' in tools_to_run:
        _run_redundancy_detector_autonomous(session, context)


def _gather_analysis_context(session):
    """Gather context to make smart decisions"""
    from datetime import datetime, timedelta
    import os
    
    context = {
        'test_results': {
            'total': session.testscollected,
            'passed': session.testscollected - session.testsfailed,
            'failed': session.testsfailed,
            'has_failures': session.testsfailed > 0
        },
        'last_run_times': {},
        'code_changes_detected': False,
        'significant_test_changes': False
    }
    
    # Check last run times for each tool
    reports_dir = Path("tests/guwu")
    for tool, report_file in [
        ('gap_analyzer', 'gap_analysis_report.txt'),
        ('predictor', 'prediction_report.txt'),
        ('lifecycle', 'lifecycle_report.txt'),
        ('reflection', 'reflection_report.txt'),
        ('redundancy', 'redundancy_report.txt')
    ]:
        report_path = reports_dir / report_file
        if report_path.exists():
            last_modified = datetime.fromtimestamp(os.path.getmtime(report_path))
            hours_since = (datetime.now() - last_modified).total_seconds() / 3600
            context['last_run_times'][tool] = hours_since
        else:
            context['last_run_times'][tool] = float('inf')  # Never run
    
    return context


def _decide_which_tools(context):
    """
    Smart decision logic - which tools should run?
    
    Returns: List of tool names to execute
    """
    tools = []
    
    # 1. Gap Analyzer - Run if:
    #    - Failures occurred (might indicate missing tests)
    #    - Never run before
    #    - Haven't run in 24+ hours AND code is changing
    if (context['test_results']['has_failures'] or
        context['last_run_times']['gap_analyzer'] > 24 or
        context['last_run_times']['gap_analyzer'] == float('inf')):
        tools.append('gap_analyzer')
    
    # 2. Predictor - Run if:
    #    - Failures occurred (learn patterns)
    #    - Haven't run in 12+ hours
    if (context['test_results']['has_failures'] or
        context['last_run_times']['predictor'] > 12):
        tools.append('predictor')
    
    # 3. Lifecycle - Run if:
    #    - Haven't run in 168+ hours (1 week)
    #    - Never run before
    if context['last_run_times']['lifecycle'] > 168:
        tools.append('lifecycle')
    
    # 4. Reflection - Run if:
    #    - Failures occurred (learn from mistakes)
    #    - Haven't run in 24+ hours
    if (context['test_results']['has_failures'] or
        context['last_run_times']['reflection'] > 24):
        tools.append('reflection')
    
    # 5. Redundancy - Run if:
    #    - Haven't run in 720+ hours (30 days)
    #    - Never run before
    if context['last_run_times']['redundancy'] > 720:
        tools.append('redundancy')
    
    return tools


def _run_gap_analyzer_autonomous(session, context=None):
    """Find missing tests automatically"""
    try:
        from guwu.gap_analyzer import TestGapAnalyzer
        
        print("\n" + "=" * 80)
        print("🔍 GU WU GAP ANALYZER - Autonomous Test Gap Detection")
        print("=" * 80)
        
        analyzer = TestGapAnalyzer()
        gaps = analyzer.analyze_gaps(coverage_threshold=70.0)
        
        # Count gaps by priority
        critical_gaps = [g for g in gaps if g.priority.value == 'critical']
        high_gaps = [g for g in gaps if g.priority.value == 'high']
        
        print(f"\n📊 Gap Analysis Summary:")
        print(f"   Total gaps found: {len(gaps)}")
        print(f"   🔴 CRITICAL: {len(critical_gaps)}")
        print(f"   🟡 HIGH: {len(high_gaps)}")
        print(f"   🟢 MEDIUM/LOW: {len(gaps) - len(critical_gaps) - len(high_gaps)}")
        
        # Display only CRITICAL gaps (keep output concise)
        if critical_gaps:
            print(f"\n⚠️  CRITICAL GAPS REQUIRE ATTENTION:")
            for i, gap in enumerate(critical_gaps[:5], 1):  # Top 5 only
                print(f"\n{i}. {gap.target} ({gap.module})")
                print(f"   Reason: {gap.reason}")
                if gap.complexity:
                    print(f"   Complexity: {gap.complexity}")
        
        # Save full report
        report = analyzer.generate_gap_report(gaps)
        report_path = Path("tests/guwu/gap_analysis_report.txt")
        report_path.write_text(report, encoding='utf-8')
        
        print(f"\n📄 Full report: {report_path}")
        print("=" * 80 + "\n")
        
    except Exception as e:
        print(f"\n⚠️  Gap analyzer skipped: {e}\n")


def _run_predictor_autonomous(session, context=None):
    """Predict likely failures for next run"""
    try:
        from guwu.predictor import TestPredictor
        
        predictor = TestPredictor()
        predictions = predictor.predict_failures()
        
        high_risk = [p for p in predictions if p['failure_probability'] > 0.7]
        
        if high_risk:
            print("\n📊 GU WU PREDICTOR - High-Risk Tests for Next Run:")
            for i, pred in enumerate(high_risk[:3], 1):
                print(f"   {i}. {pred['test_name']} ({pred['failure_probability']:.0%} risk)")
        
        # Save full report
        report_path = Path("tests/guwu/prediction_report.txt")
        predictor.save_report(predictions, str(report_path))
        
    except Exception:
        pass  # Silent failure


def _run_lifecycle_autonomous(session, context=None):
    """Track test lifecycle health"""
    try:
        from guwu.lifecycle import TestLifecycleAnalyzer
        
        analyzer = TestLifecycleAnalyzer()
        lifecycle_data = analyzer.analyze_lifecycle()
        
        # Check for aging tests (not run in 30+ days)
        aging_tests = lifecycle_data.get('aging_tests', [])
        if len(aging_tests) > 10:
            print(f"\n⚠️  GU WU LIFECYCLE: {len(aging_tests)} tests not run in 30+ days")
            print(f"   Consider removing obsolete tests")
        
        # Save full report
        report_path = Path("tests/guwu/lifecycle_report.txt")
        analyzer.save_report(lifecycle_data, str(report_path))
        
    except Exception:
        pass  # Silent failure


def _run_reflection_autonomous(session, context=None):
    """Learn from test patterns"""
    try:
        from guwu.reflection import TestReflection
        
        reflection = TestReflection()
        learnings = reflection.reflect_on_session()
        
        # Display key learnings if significant
        if learnings and len(learnings) > 0:
            print(f"\n💡 GU WU REFLECTION: {len(learnings)} patterns learned")
        
        # Save full report
        report_path = Path("tests/guwu/reflection_report.txt")
        reflection.save_report(learnings, str(report_path))
        
    except Exception:
        pass  # Silent failure


def _run_redundancy_detector_autonomous(session, context=None):
    """Find duplicate/overlapping tests (runs weekly)"""
    try:
        # Only run once per week (check last run time)
        report_path = Path("tests/guwu/redundancy_report.txt")
        
        if report_path.exists():
            import os
            from datetime import datetime, timedelta
            
            last_modified = datetime.fromtimestamp(os.path.getmtime(report_path))
            if datetime.now() - last_modified < timedelta(days=7):
                return  # Skip - ran within last week
        
        from guwu.analyzer import TestAnalyzer
        
        analyzer = TestAnalyzer()
        redundancies = analyzer.find_redundant_tests()
        
        if redundancies and len(redundancies) > 5:
            print(f"\n⚠️  GU WU REDUNDANCY: {len(redundancies)} overlapping tests found")
            print(f"   Consider consolidating to reduce maintenance")
        
        # Save report
        analyzer.save_redundancy_report(redundancies, str(report_path))
        
    except Exception:
        pass  # Silent failure


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

try:
    print("=" * 80)
    print("🥋 GU WU (顾武) TESTING FRAMEWORK")
    print("=" * 80)
    print("Philosophy: Attending to martial affairs with discipline")
    print("Status: Self-learning and auto-optimization ACTIVE")
    print("=" * 80)
except UnicodeEncodeError:
    print("=" * 80)
    print("[GU WU] TESTING FRAMEWORK")
    print("=" * 80)
    print("Philosophy: Attending to martial affairs with discipline")
    print("Status: Self-learning and auto-optimization ACTIVE")
    print("=" * 80)
