"""
API Playground Unit Tests
=========================
Comprehensive tests for API Playground blueprint endpoints.

Test Coverage:
- Blueprint creation and configuration
- API discovery endpoint (/discover)
- Module-specific API endpoint (/modules/<name>)
- Category endpoints (/categories, /categories/<name>)
- Module list endpoint (/modules)
- Stats endpoint (/stats)
- Error handling

Author: P2P Development Team
Created: 2026-02-05 (WP-GW-002 Phase 3)
"""

import pytest
from flask import Flask
from unittest.mock import Mock, patch, MagicMock

from modules.api_playground.backend.api import api_playground_api


# ============================================================================
# Test Fixtures
# ============================================================================

@pytest.fixture
def app():
    """Create Flask test app with api_playground blueprint."""
    app = Flask(__name__)
    app.register_blueprint(api_playground_api)
    app.config['TESTING'] = True
    return app


@pytest.fixture
def client(app):
    """Create Flask test client."""
    return app.test_client()


@pytest.fixture
def mock_playground_service():
    """Mock PlaygroundService for testing."""
    with patch('modules.api_playground.backend.api.get_playground_service') as mock:
        service = Mock()
        mock.return_value = service
        yield service


# ============================================================================
# Test Suite: Blueprint Creation
# ============================================================================

class TestCreateBlueprint:
    """Test blueprint creation and configuration."""
    
    @pytest.mark.unit
    @pytest.mark.fast
    def test_create_blueprint_returns_valid_blueprint(self):
        """
        Test that api_playground_api is a valid Flask Blueprint.
        
        AAA Pattern:
        - ARRANGE: Import blueprint
        - ACT: Check blueprint type and properties
        - ASSERT: Is valid Blueprint with correct configuration
        """
        # ARRANGE
        from flask import Blueprint
        
        # ACT
        blueprint = api_playground_api
        
        # ASSERT
        assert isinstance(blueprint, Blueprint)
        assert blueprint.name == 'api_playground'
        assert blueprint.url_prefix == '/api/playground'
    
    @pytest.mark.unit
    @pytest.mark.fast
    def test_blueprint_has_all_required_routes(self, app):
        """
        Test that blueprint registers all required routes.
        
        AAA Pattern:
        - ARRANGE: Create Flask app with blueprint
        - ACT: Get all registered routes
        - ASSERT: All 6 endpoints present
        """
        # ARRANGE
        rules = [rule.rule for rule in app.url_map.iter_rules()]
        
        # ACT & ASSERT
        expected_routes = [
            '/api/playground/discover',
            '/api/playground/modules/<module_name>',
            '/api/playground/categories',
            '/api/playground/categories/<category>',
            '/api/playground/modules',
            '/api/playground/stats'
        ]
        
        for route in expected_routes:
            assert route in rules


# ============================================================================
# Test Suite: Discover APIs Endpoint
# ============================================================================

class TestDiscoverAPIsEndpoint:
    """Test /discover endpoint."""
    
    @pytest.mark.unit
    @pytest.mark.fast
    def test_discover_apis_success(self, client, mock_playground_service):
        """
        Test /discover endpoint returns APIs and stats.
        
        AAA Pattern:
        - ARRANGE: Mock service with sample APIs and stats
        - ACT: GET /api/playground/discover
        - ASSERT: Returns success with APIs and stats
        """
        # ARRANGE
        mock_playground_service.get_all_apis.return_value = {
            'data_products': {'displayName': 'Data Products'},
            'knowledge_graph': {'displayName': 'Knowledge Graph'}
        }
        mock_playground_service.get_summary_stats.return_value = {
            'total_modules': 2,
            'total_endpoints': 10,
            'categories': ['Business Logic']
        }
        
        # ACT
        response = client.get('/api/playground/discover')
        data = response.get_json()
        
        # ASSERT
        assert response.status_code == 200
        assert data['success'] is True
        assert 'apis' in data
        assert 'stats' in data
        assert data['stats']['total_modules'] == 2
    
    @pytest.mark.unit
    @pytest.mark.fast
    def test_discover_apis_handles_exception(self, client, mock_playground_service):
        """
        Test /discover endpoint handles service exceptions.
        
        AAA Pattern:
        - ARRANGE: Mock service to raise exception
        - ACT: GET /api/playground/discover
        - ASSERT: Returns 500 error with message
        """
        # ARRANGE
        mock_playground_service.discover_apis.side_effect = Exception("Service error")
        
        # ACT
        response = client.get('/api/playground/discover')
        data = response.get_json()
        
        # ASSERT
        assert response.status_code == 500
        assert data['success'] is False
        assert 'error' in data
        assert data['error']['code'] == 'DISCOVERY_ERROR'


# ============================================================================
# Test Suite: Module-Specific API Endpoint
# ============================================================================

class TestGetModuleAPIEndpoint:
    """Test /modules/<module_name> endpoint."""
    
    @pytest.mark.unit
    @pytest.mark.fast
    def test_get_module_api_success(self, client, mock_playground_service):
        """
        Test /modules/<name> endpoint returns module API.
        
        AAA Pattern:
        - ARRANGE: Mock service with module API config
        - ACT: GET /api/playground/modules/data_products
        - ASSERT: Returns success with API config
        """
        # ARRANGE
        mock_playground_service.get_api.return_value = {
            'displayName': 'Data Products',
            'endpoints': ['/api/data-products/list']
        }
        
        # ACT
        response = client.get('/api/playground/modules/data_products')
        data = response.get_json()
        
        # ASSERT
        assert response.status_code == 200
        assert data['success'] is True
        assert data['module'] == 'data_products'
        assert 'api' in data
    
    @pytest.mark.unit
    @pytest.mark.fast
    def test_get_module_api_not_found(self, client, mock_playground_service):
        """
        Test /modules/<name> endpoint returns 404 for non-existent module.
        
        AAA Pattern:
        - ARRANGE: Mock service to return None (module not found)
        - ACT: GET /api/playground/modules/nonexistent
        - ASSERT: Returns 404 with MODULE_NOT_FOUND error
        """
        # ARRANGE
        mock_playground_service.get_api.return_value = None
        
        # ACT
        response = client.get('/api/playground/modules/nonexistent')
        data = response.get_json()
        
        # ASSERT
        assert response.status_code == 404
        assert data['success'] is False
        assert data['error']['code'] == 'MODULE_NOT_FOUND'
    
    @pytest.mark.unit
    @pytest.mark.fast
    def test_get_module_api_handles_exception(self, client, mock_playground_service):
        """
        Test /modules/<name> endpoint handles service exceptions.
        
        AAA Pattern:
        - ARRANGE: Mock service to raise exception
        - ACT: GET /api/playground/modules/data_products
        - ASSERT: Returns 500 error
        """
        # ARRANGE
        mock_playground_service.get_api.side_effect = Exception("Service error")
        
        # ACT
        response = client.get('/api/playground/modules/data_products')
        data = response.get_json()
        
        # ASSERT
        assert response.status_code == 500
        assert data['success'] is False
        assert data['error']['code'] == 'SERVER_ERROR'


# ============================================================================
# Test Suite: Categories Endpoints
# ============================================================================

class TestCategoriesEndpoints:
    """Test category-related endpoints."""
    
    @pytest.mark.unit
    @pytest.mark.fast
    def test_get_categories_success(self, client, mock_playground_service):
        """
        Test /categories endpoint returns all categories.
        
        AAA Pattern:
        - ARRANGE: Mock service with categories list
        - ACT: GET /api/playground/categories
        - ASSERT: Returns success with categories
        """
        # ARRANGE
        mock_playground_service.get_categories.return_value = [
            'Infrastructure',
            'Business Logic',
            'Data Management'
        ]
        
        # ACT
        response = client.get('/api/playground/categories')
        data = response.get_json()
        
        # ASSERT
        assert response.status_code == 200
        assert data['success'] is True
        assert len(data['categories']) == 3
    
    @pytest.mark.unit
    @pytest.mark.fast
    def test_get_apis_by_category_success(self, client, mock_playground_service):
        """
        Test /categories/<name> endpoint returns APIs in category.
        
        AAA Pattern:
        - ARRANGE: Mock service with APIs for category
        - ACT: GET /api/playground/categories/Business%20Logic
        - ASSERT: Returns success with filtered APIs
        """
        # ARRANGE
        mock_playground_service.get_apis_by_category.return_value = {
            'data_products': {'displayName': 'Data Products'},
            'knowledge_graph': {'displayName': 'Knowledge Graph'}
        }
        
        # ACT
        response = client.get('/api/playground/categories/Business%20Logic')
        data = response.get_json()
        
        # ASSERT
        assert response.status_code == 200
        assert data['success'] is True
        assert data['category'] == 'Business Logic'
        assert data['count'] == 2
    
    @pytest.mark.unit
    @pytest.mark.fast
    def test_get_categories_handles_exception(self, client, mock_playground_service):
        """
        Test /categories endpoint handles service exceptions.
        
        AAA Pattern:
        - ARRANGE: Mock service to raise exception
        - ACT: GET /api/playground/categories
        - ASSERT: Returns 500 error
        """
        # ARRANGE
        mock_playground_service.get_categories.side_effect = Exception("Service error")
        
        # ACT
        response = client.get('/api/playground/categories')
        data = response.get_json()
        
        # ASSERT
        assert response.status_code == 500
        assert data['success'] is False


# ============================================================================
# Test Suite: Modules List Endpoint
# ============================================================================

class TestModulesListEndpoint:
    """Test /modules endpoint."""
    
    @pytest.mark.unit
    @pytest.mark.fast
    def test_get_modules_success(self, client, mock_playground_service):
        """
        Test /modules endpoint returns list of module names.
        
        AAA Pattern:
        - ARRANGE: Mock service with module APIs
        - ACT: GET /api/playground/modules
        - ASSERT: Returns success with module list
        """
        # ARRANGE
        mock_playground_service.get_all_apis.return_value = {
            'data_products': {'displayName': 'Data Products'},
            'knowledge_graph': {'displayName': 'Knowledge Graph'},
            'log_manager': {'displayName': 'Log Manager'}
        }
        
        # ACT
        response = client.get('/api/playground/modules')
        data = response.get_json()
        
        # ASSERT
        assert response.status_code == 200
        assert data['success'] is True
        assert data['count'] == 3
        assert 'data_products' in data['modules']
        assert 'knowledge_graph' in data['modules']
    
    @pytest.mark.unit
    @pytest.mark.fast
    def test_get_modules_handles_exception(self, client, mock_playground_service):
        """
        Test /modules endpoint handles service exceptions.
        
        AAA Pattern:
        - ARRANGE: Mock service to raise exception
        - ACT: GET /api/playground/modules
        - ASSERT: Returns 500 error
        """
        # ARRANGE
        mock_playground_service.get_all_apis.side_effect = Exception("Service error")
        
        # ACT
        response = client.get('/api/playground/modules')
        data = response.get_json()
        
        # ASSERT
        assert response.status_code == 500
        assert data['success'] is False


# ============================================================================
# Test Suite: Stats Endpoint
# ============================================================================

class TestStatsEndpoint:
    """Test /stats endpoint."""
    
    @pytest.mark.unit
    @pytest.mark.fast
    def test_get_stats_success(self, client, mock_playground_service):
        """
        Test /stats endpoint returns discovery statistics.
        
        AAA Pattern:
        - ARRANGE: Mock service with stats
        - ACT: GET /api/playground/stats
        - ASSERT: Returns success with stats
        """
        # ARRANGE
        mock_playground_service.get_summary_stats.return_value = {
            'total_modules': 5,
            'total_endpoints': 25,
            'categories': ['Infrastructure', 'Business Logic']
        }
        
        # ACT
        response = client.get('/api/playground/stats')
        data = response.get_json()
        
        # ASSERT
        assert response.status_code == 200
        assert data['success'] is True
        assert data['stats']['total_modules'] == 5
        assert data['stats']['total_endpoints'] == 25
    
    @pytest.mark.unit
    @pytest.mark.fast
    def test_get_stats_handles_exception(self, client, mock_playground_service):
        """
        Test /stats endpoint handles service exceptions.
        
        AAA Pattern:
        - ARRANGE: Mock service to raise exception
        - ACT: GET /api/playground/stats
        - ASSERT: Returns 500 error
        """
        # ARRANGE
        mock_playground_service.get_summary_stats.side_effect = Exception("Service error")
        
        # ACT
        response = client.get('/api/playground/stats')
        data = response.get_json()
        
        # ASSERT
        assert response.status_code == 500
        assert data['success'] is False
        assert data['error']['code'] == 'SERVER_ERROR'


# ============================================================================
# Test Suite: Service Integration
# ============================================================================

class TestServiceIntegration:
    """Test proper integration with PlaygroundService."""
    
    @pytest.mark.unit
    @pytest.mark.fast
    def test_discover_calls_service_methods(self, client, mock_playground_service):
        """
        Test /discover endpoint calls service methods correctly.
        
        AAA Pattern:
        - ARRANGE: Mock service with return values
        - ACT: GET /api/playground/discover
        - ASSERT: Service methods called in correct order
        """
        # ARRANGE
        mock_playground_service.get_all_apis.return_value = {}
        mock_playground_service.get_summary_stats.return_value = {
            'total_modules': 0,
            'total_endpoints': 0,
            'categories': []
        }
        
        # ACT
        response = client.get('/api/playground/discover')
        
        # ASSERT
        mock_playground_service.discover_apis.assert_called_once()
        mock_playground_service.get_all_apis.assert_called_once()
        mock_playground_service.get_summary_stats.assert_called_once()
    
    @pytest.mark.unit
    @pytest.mark.fast
    def test_get_module_api_calls_service(self, client, mock_playground_service):
        """
        Test /modules/<name> endpoint calls service with module name.
        
        AAA Pattern:
        - ARRANGE: Mock service with API config
        - ACT: GET /api/playground/modules/test_module
        - ASSERT: Service called with correct module name
        """
        # ARRANGE
        mock_playground_service.get_api.return_value = {
            'displayName': 'Test Module'
        }
        
        # ACT
        response = client.get('/api/playground/modules/test_module')
        
        # ASSERT
        mock_playground_service.get_api.assert_called_once_with('test_module')
    
    @pytest.mark.unit
    @pytest.mark.fast
    def test_get_apis_by_category_calls_service(self, client, mock_playground_service):
        """
        Test /categories/<name> endpoint calls service with category name.
        
        AAA Pattern:
        - ARRANGE: Mock service with category APIs
        - ACT: GET /api/playground/categories/Infrastructure
        - ASSERT: Service called with correct category
        """
        # ARRANGE
        mock_playground_service.get_apis_by_category.return_value = {}
        
        # ACT
        response = client.get('/api/playground/categories/Infrastructure')
        
        # ASSERT
        mock_playground_service.get_apis_by_category.assert_called_once_with('Infrastructure')


# ============================================================================
# Test Suite: Response Format Validation
# ============================================================================

class TestResponseFormat:
    """Test response format consistency."""
    
    @pytest.mark.unit
    @pytest.mark.fast
    def test_successful_response_format(self, client, mock_playground_service):
        """
        Test that successful responses follow consistent format.
        
        AAA Pattern:
        - ARRANGE: Mock service with data
        - ACT: Call various endpoints
        - ASSERT: All responses have {success: true, ...data}
        """
        # ARRANGE
        mock_playground_service.get_all_apis.return_value = {}
        mock_playground_service.get_summary_stats.return_value = {
            'total_modules': 0,
            'total_endpoints': 0,
            'categories': []
        }
        mock_playground_service.get_categories.return_value = []
        
        # ACT
        responses = [
            client.get('/api/playground/discover'),
            client.get('/api/playground/categories'),
            client.get('/api/playground/modules'),
            client.get('/api/playground/stats')
        ]
        
        # ASSERT
        for response in responses:
            data = response.get_json()
            assert 'success' in data
            assert data['success'] is True
    
    @pytest.mark.unit
    @pytest.mark.fast
    def test_error_response_format(self, client, mock_playground_service):
        """
        Test that error responses follow consistent format.
        
        AAA Pattern:
        - ARRANGE: Mock service to raise exceptions
        - ACT: Call various endpoints
        - ASSERT: All errors have {success: false, error: {message, code}}
        """
        # ARRANGE
        mock_playground_service.get_all_apis.side_effect = Exception("Error")
        mock_playground_service.get_categories.side_effect = Exception("Error")
        
        # ACT
        responses = [
            client.get('/api/playground/discover'),
            client.get('/api/playground/categories')
        ]
        
        # ASSERT
        for response in responses:
            data = response.get_json()
            assert data['success'] is False
            assert 'error' in data
            assert 'message' in data['error']
            assert 'code' in data['error']