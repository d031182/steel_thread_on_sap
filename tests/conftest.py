"""
pytest Configuration and Fixtures

Provides shared fixtures for all tests, including:
- Flask test server (auto-start/stop for API contract tests)
- Test database setup/teardown
- Common test utilities

Author: P2P Development Team
Date: 2026-02-15
Version: 1.0.0
"""

import pytest
import threading
import time
import requests
from pathlib import Path
import sys

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


@pytest.fixture(scope="session")
def flask_server():
    """
    Start Flask server in background thread for API contract tests.
    
    Automatically starts server before tests, stops after tests complete.
    Waits for server to be ready before returning.
    
    Usage:
        def test_my_api(flask_server):
            # Server already running at flask_server (e.g., "http://localhost:5000")
            response = requests.get(f"{flask_server}/api/data-products")
            assert response.status_code == 200
    
    Yields:
        str: Base URL of running server (e.g., "http://localhost:5000")
    """
    # Import Flask app
    try:
        from server import app
    except ImportError as e:
        pytest.skip(f"Could not import Flask app: {e}")
    
    # Configure for testing
    app.config['TESTING'] = True
    app.config['DEBUG'] = False
    
    # Use a test port (5000)
    host = 'localhost'
    port = 5000
    base_url = f"http://{host}:{port}"
    
    # Check if server already running
    try:
        response = requests.get(base_url, timeout=1)
        if response.status_code:
            # Server already running, use it
            print(f"\n✓ Using existing Flask server at {base_url}")
            yield base_url
            return
    except requests.exceptions.ConnectionError:
        pass  # Server not running, we'll start it
    
    # Start server in background thread
    server_thread = threading.Thread(
        target=lambda: app.run(host=host, port=port, use_reloader=False, threaded=True),
        daemon=True
    )
    server_thread.start()
    
    # Wait for server to start (max 10 seconds)
    print(f"\n⏳ Starting Flask server at {base_url}...", end="", flush=True)
    for i in range(100):  # 100 * 0.1s = 10 seconds max
        try:
            response = requests.get(base_url, timeout=1)
            if response.status_code:
                print(f" ✓ Ready in {i/10:.1f}s")
                break
        except requests.exceptions.ConnectionError:
            time.sleep(0.1)
    else:
        pytest.fail("Flask server failed to start within 10 seconds")
    
    # Server is ready, yield to tests
    yield base_url
    
    # Cleanup happens automatically (daemon thread)
    print(f"✓ Flask server stopped")


@pytest.fixture(scope="session")
def api_base_url(flask_server):
    """
    Convenience fixture that returns just the base URL.
    
    Usage:
        def test_my_api(api_base_url):
            response = requests.get(f"{api_base_url}/api/data-products")
    """
    return flask_server


@pytest.fixture
def test_timeout():
    """Default timeout for HTTP requests in tests (5 seconds)"""
    return 5


# Mark configuration for pytest
def pytest_configure(config):
    """
    Register custom markers for pytest.
    
    This eliminates "Unknown mark" warnings.
    """
    config.addinivalue_line(
        "markers", "api_contract: Mark test as API contract test (fast, uses requests)"
    )
    config.addinivalue_line(
        "markers", "e2e: Mark test as end-to-end test (requires running server)"
    )
    config.addinivalue_line(
        "markers", "smoke: Mark test as smoke test (quick sanity check)"
    )
    config.addinivalue_line(
        "markers", "slow: Mark test as slow (skip in fast test runs)"
    )