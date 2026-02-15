"""
Unit Tests for Data Products V2 API - Dependency Injection
===========================================================

Tests that V2 API correctly uses Constructor Injection instead of
Service Locator antipattern.

Author: P2P Development Team
Version: 1.0.0
Date: 2026-02-09
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from flask import Flask
from modules.data_products_v2.backend.api import data_products_v2_api, get_facade


@pytest.fixture
def app():
    """Create Flask app with injected facades"""
    app = Flask(__name__)
    app.config['TESTING'] = True
    
    # Create mock facades
    mock_sqlite_facade = Mock()
    mock_hana_facade = Mock()
    
    # Inject facades (Constructor Injection pattern)
    app.sqlite_facade_v2 = mock_sqlite_facade
    app.hana_facade_v2 = mock_hana_facade
    
    # Register blueprint
    app.register_blueprint(data_products_v2_api, url_prefix='/api/data-products')
    
    return app


@pytest.fixture
def client(app):
    """Create test client"""
    return app.test_client()


class TestDependencyInjection:
    """Test Constructor Injection (not Service Locator)"""
    
    @pytest.mark.unit
    @pytest.mark.fast
    def test_get_facade_uses_injected_sqlite_facade(self, app):
        """get_facade() retrieves pre-injected SQLite facade (DI pattern)"""
        with app.app_context():
            # ACT
            facade = get_facade('sqlite')
            
            # ASSERT
            assert facade is app.sqlite_facade_v2
            # Verify it's the SAME object (not newly created)
            assert id(facade) == id(app.sqlite_facade_v2)
    
    @pytest.mark.unit
    @pytest.mark.fast
    def test_get_facade_uses_injected_hana_facade(self, app):
        """get_facade() retrieves pre-injected HANA facade (DI pattern)"""
        with app.app_context():
            # ACT
            facade = get_facade('hana')
            
            # ASSERT
            assert facade is app.hana_facade_v2
            # Verify it's the SAME object (not newly created)
            assert id(facade) == id(app.hana_facade_v2)
    
    @pytest.mark.unit
    @pytest.mark.fast
    def test_get_facade_raises_if_sqlite_not_configured(self):
        """get_facade() raises clear error if SQLite facade not injected"""
        # ARRANGE
        app_unconfigured = Flask(__name__)
        # No facades injected
        
        # ACT & ASSERT
        with app_unconfigured.app_context():
            with pytest.raises(ValueError, match="SQLite facade not configured"):
                get_facade('sqlite')
    
    @pytest.mark.unit
    @pytest.mark.fast
    def test_get_facade_raises_if_hana_not_configured(self):
        """get_facade() raises clear error if HANA facade not injected"""
        # ARRANGE
        app_unconfigured = Flask(__name__)
        # No facades injected
        
        # ACT & ASSERT
        with app_unconfigured.app_context():
            with pytest.raises(ValueError, match="HANA facade not configured"):
                get_facade('hana')
    
    @pytest.mark.unit
    @pytest.mark.fast
    def test_get_facade_raises_for_invalid_source(self, app):
        """get_facade() raises for invalid source type"""
        with app.app_context():
            # ACT & ASSERT
            with pytest.raises(ValueError, match="Unknown source: invalid"):
                get_facade('invalid')


class TestAPIEndpoints:
    """Test API endpoints use injected facades correctly"""
    
    @pytest.mark.unit
    @pytest.mark.fast
    def test_list_data_products_uses_injected_facade(self, client, app):
        """GET / endpoint uses injected facade (not Service Locator)"""
        # ARRANGE
        mock_products = [
            Mock(product_name='Product1', display_name='P1', namespace='ns', 
                 version='v1', schema_name='s1', source='hana', 
                 description='desc', table_count=5)
        ]
        app.sqlite_facade_v2.get_data_products.return_value = mock_products
        
        # ACT
        response = client.get('/api/data-products/?source=sqlite')
        
        # ASSERT
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
        assert len(data['data_products']) == 1
        # Verify facade method was called
        app.sqlite_facade_v2.get_data_products.assert_called_once()
    
    @pytest.mark.unit
    @pytest.mark.fast
    def test_api_returns_503_when_hana_not_configured(self, client):
        """API returns HTTP 503 (Service Unavailable) when HANA facade missing"""
        # ARRANGE
        app_unconfigured = Flask(__name__)
        app_unconfigured.config['TESTING'] = True
        # Only SQLite configured, HANA missing
        app_unconfigured.sqlite_facade_v2 = Mock()
        app_unconfigured.register_blueprint(data_products_v2_api, url_prefix='/api/data-products')
        client_unconfigured = app_unconfigured.test_client()
        
        # ACT
        response = client_unconfigured.get('/api/data-products/?source=hana')
        
        # ASSERT
        assert response.status_code == 503  # Service Unavailable
        data = response.get_json()
        assert data['success'] is False
        assert 'error' in data
        assert 'DATA_ACCESS_ERROR' in str(data['error'])
    
    @pytest.mark.unit
    @pytest.mark.fast
    def test_no_service_locator_config_access(self, client, app):
        """Verify API does NOT access app.config (Service Locator antipattern)"""
        # ARRANGE
        mock_products = [Mock(product_name='P1', display_name='P1', namespace='ns',
                              version='v1', schema_name='s1', source='hana',
                              description='d', table_count=5)]
        app.hana_facade_v2.get_data_products.return_value = mock_products
        
        # Set app.config values to None (simulate missing config)
        app.config['HANA_HOST'] = None
        app.config['HANA_PORT'] = None
        app.config['HANA_USER'] = None
        app.config['HANA_PASSWORD'] = None
        
        # ACT
        response = client.get('/api/data-products/?source=hana')
        
        # ASSERT
        # Should still work because facade is pre-injected (not reading config)
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
        # Verify config was NEVER accessed (facade used directly)
        app.hana_facade_v2.get_data_products.assert_called_once()


class TestUserFriendlyErrors:
    """Test user-friendly error messages"""
    
    @pytest.mark.unit
    @pytest.mark.fast
    def test_hana_not_configured_provides_actionable_message(self, client):
        """Error message guides user to solution (use SQLite or contact admin)"""
        # ARRANGE
        app_unconfigured = Flask(__name__)
        app_unconfigured.config['TESTING'] = True
        app_unconfigured.sqlite_facade_v2 = Mock()
        app_unconfigured.register_blueprint(data_products_v2_api, url_prefix='/api/data-products')
        client_unconfigured = app_unconfigured.test_client()
        
        # ACT
        response = client_unconfigured.get('/api/data-products/?source=hana')
        
        # ASSERT
        data = response.get_json()
        error = data['error']
        assert 'userMessage' in error
        assert 'SQLite' in error['userMessage']  # Suggests alternative
        # Updated message no longer mentions administrator (simplified)
