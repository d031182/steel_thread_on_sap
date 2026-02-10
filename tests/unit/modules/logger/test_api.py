"""
Unit tests for Logger API endpoints

Tests REST API endpoints for logging operations.

Author: P2P Development Team
Version: 1.0.0
Date: 2026-02-10
"""

import pytest
from unittest.mock import Mock, AsyncMock, patch
from flask import Flask
from modules.logger.backend.api import create_blueprint


@pytest.fixture
def app():
    """Create Flask app for testing"""
    app = Flask(__name__)
    app.register_blueprint(create_blueprint(), url_prefix='/api')
    app.config['TESTING'] = True
    
    # Mock the logging service
    mock_service = Mock()
    mock_service.get_logs = Mock(return_value=[])
    mock_service.get_log_count = Mock(return_value=0)
    mock_service.get_stats = Mock(return_value={'total': 0, 'by_level': {}})
    mock_service.clear_logs = Mock(return_value=0)
    app.logging_service = mock_service
    
    return app


@pytest.fixture
def client(app):
    """Create test client"""
    return app.test_client()


@pytest.mark.unit
@pytest.mark.fast
def test_get_logs_endpoint(client, app):
    """Test GET /api/logs endpoint"""
    # ARRANGE
    expected_logs = [
        {'id': 1, 'level': 'INFO', 'message': 'Test log'}
    ]
    app.logging_service.get_logs.return_value = expected_logs
    app.logging_service.get_log_count.return_value = 1
    
    # ACT
    response = client.get('/api/logs')
    
    # ASSERT
    assert response.status_code == 200
    data = response.get_json()
    assert data['success'] is True
    assert 'logs' in data
    assert data['logs'] == expected_logs


@pytest.mark.unit
@pytest.mark.fast
def test_get_logs_with_limit(client, app):
    """Test GET /api/logs with limit parameter"""
    # ARRANGE
    app.logging_service.get_logs.return_value = []
    
    # ACT
    response = client.get('/api/logs?limit=50')
    
    # ASSERT
    assert response.status_code == 200
    app.logging_service.get_logs.assert_called_once()


@pytest.mark.unit
@pytest.mark.fast
def test_get_logs_with_level_filter(client, app):
    """Test GET /api/logs with level filter"""
    # ARRANGE
    app.logging_service.get_logs.return_value = []
    
    # ACT
    response = client.get('/api/logs?level=ERROR')
    
    # ASSERT
    assert response.status_code == 200
    app.logging_service.get_logs.assert_called_once()


@pytest.mark.unit
@pytest.mark.fast
def test_get_stats_endpoint(client, app):
    """Test GET /api/logs/stats endpoint"""
    # ARRANGE
    app.logging_service.get_log_count = Mock(side_effect=[100, 60, 30, 10])
    
    # ACT
    response = client.get('/api/logs/stats')
    
    # ASSERT
    assert response.status_code == 200
    data = response.get_json()
    assert data['success'] is True
    assert data['stats']['total'] == 100


@pytest.mark.unit
@pytest.mark.fast
def test_clear_logs_endpoint(client, app):
    """Test POST /api/logs/clear endpoint"""
    # ACT
    response = client.post('/api/logs/clear')
    
    # ASSERT
    assert response.status_code == 200
    data = response.get_json()
    assert data['success'] is True
    app.logging_service.clear_logs.assert_called_once()


@pytest.mark.unit
@pytest.mark.fast
def test_client_log_endpoint_success(client):
    """Test POST /api/logs/client with valid data"""
    # ARRANGE
    log_data = {
        'level': 'ERROR',
        'message': 'Client error',
        'url': 'http://example.com',
        'line': 42
    }
    
    # ACT
    response = client.post('/api/logs/client', json=log_data)
    
    # ASSERT
    assert response.status_code == 200
    data = response.get_json()
    assert data['success'] is True


@pytest.mark.unit
@pytest.mark.fast
def test_client_log_suppression(client):
    """Test suppression of known harmless browser warnings"""
    # ARRANGE
    log_data = {
        'level': 'WARNING',
        'message': 'ResizeObserver loop completed with undelivered notifications',
        'url': 'http://example.com'
    }
    
    # ACT
    response = client.post('/api/logs/client', json=log_data)
    
    # ASSERT
    assert response.status_code == 200
    data = response.get_json()
    assert data['success'] is True
    assert 'Suppressed' in data['message']
