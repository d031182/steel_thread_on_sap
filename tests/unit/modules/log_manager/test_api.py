"""
Unit Tests for Log Manager API Blueprint
=========================================
Comprehensive tests for log_manager API endpoints and blueprint creation.

Tests cover:
- Blueprint creation and configuration
- GET /logs endpoint with filtering
- GET /logs/stats endpoint
- POST /logs/clear endpoint
- POST /logs/client endpoint with suppression
- Error handling scenarios

Author: P2P Development Team
Date: 2026-02-05
"""

import pytest
from unittest.mock import Mock, MagicMock
from datetime import datetime
from modules.log_manager.backend.api import create_blueprint


@pytest.mark.unit
@pytest.mark.fast
class TestCreateBlueprint:
    """Test suite for create_blueprint function (CRITICAL gap)"""
    
    def test_create_blueprint_returns_valid_blueprint(self):
        """Test create_blueprint returns configured Flask Blueprint"""
        # ARRANGE
        mock_handler = Mock()
        
        # ACT
        blueprint = create_blueprint(mock_handler)
        
        # ASSERT
        assert blueprint is not None
        assert blueprint.name == 'log_manager_api'
        assert hasattr(blueprint, 'route')
    
    def test_blueprint_has_all_required_routes(self):
        """Test blueprint registers all required API endpoints"""
        # ARRANGE
        mock_handler = Mock()
        
        # ACT
        blueprint = create_blueprint(mock_handler)
        
        # Register blueprint to test routes
        from flask import Flask
        app = Flask(__name__)
        app.register_blueprint(blueprint, url_prefix='/api')
        
        # ASSERT
        # Blueprint should have 4 endpoints
        rules = [rule.rule for rule in app.url_map.iter_rules() if rule.rule.startswith('/api/logs')]
        assert len(rules) == 4  # /logs, /logs/stats, /logs/clear, /logs/client
        assert '/api/logs' in rules
        assert '/api/logs/stats' in rules
        assert '/api/logs/clear' in rules
        assert '/api/logs/client' in rules
    
    def test_blueprint_name_is_correct(self):
        """Test blueprint has correct name for registration"""
        # ARRANGE
        mock_handler = Mock()
        
        # ACT
        blueprint = create_blueprint(mock_handler)
        
        # ASSERT
        assert blueprint.name == 'log_manager_api'


@pytest.mark.unit
@pytest.mark.fast
class TestGetLogsEndpoint:
    """Test suite for GET /logs endpoint"""
    
    def test_get_logs_default_parameters(self):
        """Test GET /logs with default parameters"""
        # ARRANGE
        mock_handler = Mock()
        mock_handler.get_logs.return_value = [
            {'level': 'INFO', 'message': 'Test log', 'timestamp': '2026-02-05T23:00:00'}
        ]
        mock_handler.get_log_count.return_value = 1
        
        blueprint = create_blueprint(mock_handler)
        
        # Create test client
        from flask import Flask
        app = Flask(__name__)
        app.register_blueprint(blueprint, url_prefix='/api')
        client = app.test_client()
        
        # ACT
        response = client.get('/api/logs')
        data = response.get_json()
        
        # ASSERT
        assert response.status_code == 200
        assert data['success'] is True
        assert data['count'] == 1
        assert data['totalCount'] == 1
        assert len(data['logs']) == 1
        
        # Verify handler called with defaults
        mock_handler.get_logs.assert_called_once_with(
            level=None,
            limit=100,
            offset=0,
            start_date=None,
            end_date=None
        )
    
    def test_get_logs_with_level_filter(self):
        """Test GET /logs filters by log level"""
        # ARRANGE
        mock_handler = Mock()
        mock_handler.get_logs.return_value = []
        mock_handler.get_log_count.return_value = 0
        
        blueprint = create_blueprint(mock_handler)
        
        from flask import Flask
        app = Flask(__name__)
        app.register_blueprint(blueprint, url_prefix='/api')
        client = app.test_client()
        
        # ACT
        response = client.get('/api/logs?level=ERROR')
        data = response.get_json()
        
        # ASSERT
        assert response.status_code == 200
        assert data['filters']['level'] == 'ERROR'
        mock_handler.get_logs.assert_called_once_with(
            level='ERROR',
            limit=100,
            offset=0,
            start_date=None,
            end_date=None
        )
    
    def test_get_logs_invalid_level_returns_400(self):
        """Test GET /logs rejects invalid log level"""
        # ARRANGE
        mock_handler = Mock()
        blueprint = create_blueprint(mock_handler)
        
        from flask import Flask
        app = Flask(__name__)
        app.register_blueprint(blueprint, url_prefix='/api')
        client = app.test_client()
        
        # ACT
        response = client.get('/api/logs?level=INVALID')
        data = response.get_json()
        
        # ASSERT
        assert response.status_code == 400
        assert data['success'] is False
        assert 'Invalid log level' in data['error']['message']
    
    def test_get_logs_respects_limit_cap(self):
        """Test GET /logs caps limit at 1000"""
        # ARRANGE
        mock_handler = Mock()
        mock_handler.get_logs.return_value = []
        mock_handler.get_log_count.return_value = 0
        
        blueprint = create_blueprint(mock_handler)
        
        from flask import Flask
        app = Flask(__name__)
        app.register_blueprint(blueprint, url_prefix='/api')
        client = app.test_client()
        
        # ACT
        response = client.get('/api/logs?limit=9999')
        
        # ASSERT
        assert response.status_code == 200
        # Verify capped at 1000
        mock_handler.get_logs.assert_called_once()
        call_args = mock_handler.get_logs.call_args
        assert call_args.kwargs['limit'] == 1000
    
    def test_get_logs_handles_exception(self):
        """Test GET /logs handles handler exceptions gracefully"""
        # ARRANGE
        mock_handler = Mock()
        mock_handler.get_logs.side_effect = Exception("Database error")
        
        blueprint = create_blueprint(mock_handler)
        
        from flask import Flask
        app = Flask(__name__)
        app.register_blueprint(blueprint, url_prefix='/api')
        client = app.test_client()
        
        # ACT
        response = client.get('/api/logs')
        data = response.get_json()
        
        # ASSERT
        assert response.status_code == 500
        assert data['success'] is False
        assert 'Database error' in data['error']['message']


@pytest.mark.unit
@pytest.mark.fast
class TestLogStatsEndpoint:
    """Test suite for GET /logs/stats endpoint"""
    
    def test_get_log_stats_returns_counts(self):
        """Test GET /logs/stats returns statistics for all levels"""
        # ARRANGE
        mock_handler = Mock()
        mock_handler.get_log_count.side_effect = [150, 100, 30, 20]  # total, info, warning, error
        
        blueprint = create_blueprint(mock_handler)
        
        from flask import Flask
        app = Flask(__name__)
        app.register_blueprint(blueprint, url_prefix='/api')
        client = app.test_client()
        
        # ACT
        response = client.get('/api/logs/stats')
        data = response.get_json()
        
        # ASSERT
        assert response.status_code == 200
        assert data['success'] is True
        assert data['stats']['total'] == 150
        assert data['stats']['info'] == 100
        assert data['stats']['warning'] == 30
        assert data['stats']['error'] == 20
    
    def test_get_log_stats_handles_exception(self):
        """Test GET /logs/stats handles exceptions gracefully"""
        # ARRANGE
        mock_handler = Mock()
        mock_handler.get_log_count.side_effect = Exception("Stats error")
        
        blueprint = create_blueprint(mock_handler)
        
        from flask import Flask
        app = Flask(__name__)
        app.register_blueprint(blueprint, url_prefix='/api')
        client = app.test_client()
        
        # ACT
        response = client.get('/api/logs/stats')
        data = response.get_json()
        
        # ASSERT
        assert response.status_code == 500
        assert data['success'] is False


@pytest.mark.unit
@pytest.mark.fast
class TestClearLogsEndpoint:
    """Test suite for POST /logs/clear endpoint"""
    
    def test_clear_logs_success(self):
        """Test POST /logs/clear successfully clears logs"""
        # ARRANGE
        mock_handler = Mock()
        mock_handler.clear_logs.return_value = None
        
        blueprint = create_blueprint(mock_handler)
        
        from flask import Flask
        app = Flask(__name__)
        app.register_blueprint(blueprint, url_prefix='/api')
        client = app.test_client()
        
        # ACT
        response = client.post('/api/logs/clear')
        data = response.get_json()
        
        # ASSERT
        assert response.status_code == 200
        assert data['success'] is True
        assert 'cleared successfully' in data['message']
        mock_handler.clear_logs.assert_called_once()
    
    def test_clear_logs_handles_exception(self):
        """Test POST /logs/clear handles exceptions gracefully"""
        # ARRANGE
        mock_handler = Mock()
        mock_handler.clear_logs.side_effect = Exception("Clear failed")
        
        blueprint = create_blueprint(mock_handler)
        
        from flask import Flask
        app = Flask(__name__)
        app.register_blueprint(blueprint, url_prefix='/api')
        client = app.test_client()
        
        # ACT
        response = client.post('/api/logs/clear')
        data = response.get_json()
        
        # ASSERT
        assert response.status_code == 500
        assert data['success'] is False


@pytest.mark.unit
@pytest.mark.fast
class TestClientLogEndpoint:
    """Test suite for POST /logs/client endpoint"""
    
    def test_log_client_error_success(self):
        """Test POST /logs/client logs client errors successfully"""
        # ARRANGE
        mock_handler = Mock()
        blueprint = create_blueprint(mock_handler)
        
        from flask import Flask
        app = Flask(__name__)
        app.register_blueprint(blueprint, url_prefix='/api')
        client = app.test_client()
        
        # ACT
        response = client.post('/api/logs/client', json={
            'level': 'ERROR',
            'message': 'TypeError: Cannot read property',
            'url': 'http://localhost:5000/index.html',
            'line': 42,
            'column': 15,
            'stack': 'Error at line 42'
        })
        data = response.get_json()
        
        # ASSERT
        assert response.status_code == 200
        assert data['success'] is True
        assert 'logged successfully' in data['message']
    
    def test_log_client_suppresses_resize_observer(self):
        """Test POST /logs/client suppresses ResizeObserver warnings"""
        # ARRANGE
        mock_handler = Mock()
        blueprint = create_blueprint(mock_handler)
        
        from flask import Flask
        app = Flask(__name__)
        app.register_blueprint(blueprint, url_prefix='/api')
        client = app.test_client()
        
        # ACT
        response = client.post('/api/logs/client', json={
            'level': 'ERROR',
            'message': 'ResizeObserver loop completed with undelivered notifications',
            'url': 'http://localhost:5000/index.html'
        })
        data = response.get_json()
        
        # ASSERT
        assert response.status_code == 200
        assert data['success'] is True
        assert 'Suppressed' in data['message']
    
    def test_log_client_handles_missing_fields(self):
        """Test POST /logs/client handles missing optional fields"""
        # ARRANGE
        mock_handler = Mock()
        blueprint = create_blueprint(mock_handler)
        
        from flask import Flask
        app = Flask(__name__)
        app.register_blueprint(blueprint, url_prefix='/api')
        client = app.test_client()
        
        # ACT
        response = client.post('/api/logs/client', json={
            'message': 'Minimal error'
        })
        data = response.get_json()
        
        # ASSERT
        assert response.status_code == 200
        assert data['success'] is True
    
    def test_log_client_maps_log_levels_correctly(self):
        """Test POST /logs/client maps client log levels to Python levels"""
        # ARRANGE
        mock_handler = Mock()
        blueprint = create_blueprint(mock_handler)
        
        from flask import Flask
        app = Flask(__name__)
        app.register_blueprint(blueprint, url_prefix='/api')
        client = app.test_client()
        
        # ACT & ASSERT for each level
        for client_level in ['INFO', 'WARNING', 'WARN', 'ERROR']:
            response = client.post('/api/logs/client', json={
                'level': client_level,
                'message': f'Test {client_level} message'
            })
            assert response.status_code == 200
            assert response.get_json()['success'] is True
    
    def test_log_client_handles_exception(self):
        """Test POST /logs/client handles internal exceptions"""
        # ARRANGE
        mock_handler = Mock()
        blueprint = create_blueprint(mock_handler)
        
        from flask import Flask
        app = Flask(__name__)
        app.register_blueprint(blueprint, url_prefix='/api')
        client = app.test_client()
        
        # ACT - Send malformed JSON to trigger exception
        response = client.post(
            '/api/logs/client',
            data='invalid json',
            content_type='application/json'
        )
        data = response.get_json()
        
        # ASSERT
        assert response.status_code == 500
        assert data['success'] is False


@pytest.mark.unit
@pytest.mark.fast
class TestSuppressionLogic:
    """Test suite for should_suppress_log helper function"""
    
    def test_suppresses_resize_observer_loop_completed(self):
        """Test suppression of 'ResizeObserver loop completed' warnings"""
        # ARRANGE
        mock_handler = Mock()
        blueprint = create_blueprint(mock_handler)
        
        from flask import Flask
        app = Flask(__name__)
        app.register_blueprint(blueprint, url_prefix='/api')
        client = app.test_client()
        
        # ACT
        response = client.post('/api/logs/client', json={
            'message': 'ResizeObserver loop completed with undelivered notifications'
        })
        data = response.get_json()
        
        # ASSERT
        assert 'Suppressed' in data['message']
    
    def test_suppresses_resize_observer_loop_limit(self):
        """Test suppression of 'ResizeObserver loop limit exceeded' warnings"""
        # ARRANGE
        mock_handler = Mock()
        blueprint = create_blueprint(mock_handler)
        
        from flask import Flask
        app = Flask(__name__)
        app.register_blueprint(blueprint, url_prefix='/api')
        client = app.test_client()
        
        # ACT
        response = client.post('/api/logs/client', json={
            'message': 'ResizeObserver loop limit exceeded'
        })
        data = response.get_json()
        
        # ASSERT
        assert 'Suppressed' in data['message']
    
    def test_does_not_suppress_real_errors(self):
        """Test real errors are NOT suppressed"""
        # ARRANGE
        mock_handler = Mock()
        blueprint = create_blueprint(mock_handler)
        
        from flask import Flask
        app = Flask(__name__)
        app.register_blueprint(blueprint, url_prefix='/api')
        client = app.test_client()
        
        # ACT
        response = client.post('/api/logs/client', json={
            'message': 'TypeError: Cannot read property of undefined'
        })
        data = response.get_json()
        
        # ASSERT
        assert 'logged successfully' in data['message']  # Not suppressed


@pytest.mark.unit
@pytest.mark.fast
class TestPaginationLogic:
    """Test suite for pagination in GET /logs"""
    
    def test_pagination_with_offset(self):
        """Test GET /logs respects offset parameter"""
        # ARRANGE
        mock_handler = Mock()
        mock_handler.get_logs.return_value = []
        mock_handler.get_log_count.return_value = 500
        
        blueprint = create_blueprint(mock_handler)
        
        from flask import Flask
        app = Flask(__name__)
        app.register_blueprint(blueprint, url_prefix='/api')
        client = app.test_client()
        
        # ACT
        response = client.get('/api/logs?offset=200&limit=50')
        
        # ASSERT
        assert response.status_code == 200
        mock_handler.get_logs.assert_called_once_with(
            level=None,
            limit=50,
            offset=200,
            start_date=None,
            end_date=None
        )
    
    def test_pagination_prevents_negative_offset(self):
        """Test GET /logs prevents negative offset"""
        # ARRANGE
        mock_handler = Mock()
        mock_handler.get_logs.return_value = []
        mock_handler.get_log_count.return_value = 100
        
        blueprint = create_blueprint(mock_handler)
        
        from flask import Flask
        app = Flask(__name__)
        app.register_blueprint(blueprint, url_prefix='/api')
        client = app.test_client()
        
        # ACT
        response = client.get('/api/logs?offset=-50')
        
        # ASSERT
        assert response.status_code == 200
        # Verify offset clamped to 0
        call_args = mock_handler.get_logs.call_args
        assert call_args.kwargs['offset'] == 0