"""
Log Module Backend API Contract Tests
=====================================
Tests for log module API endpoints following Gu Wu methodology.

Following Gu Wu API Contract Testing Foundation:
- Test the contract, trust the implementation
- Focus on API endpoints (backend business logic)
- Use AAA pattern (Arrange, Act, Assert)
- Fast execution (< 1 second per test)
"""

import pytest
import requests


BASE_URL = "http://localhost:5000"
LOG_API_BASE = f"{BASE_URL}/api/log"


@pytest.mark.e2e
@pytest.mark.api_contract
class TestLogModeEndpoints:
    """Test logging mode API contract"""
    
    def test_get_logging_mode_contract(self):
        """Test: GET /api/log/mode returns valid contract"""
        # ARRANGE
        url = f"{LOG_API_BASE}/mode"
        
        # ACT
        response = requests.get(url, timeout=5)
        
        # ASSERT
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert 'status' in data, "Missing 'status' field"
        assert data['status'] == 'success', "Status should be 'success'"
        assert 'data' in data, "Missing 'data' field"
        
        # Validate data structure
        mode_data = data['data']
        assert 'mode' in mode_data, "Missing 'mode' field"
        assert mode_data['mode'] in ['default', 'flight_recorder'], \
            f"Invalid mode: {mode_data['mode']}"
        assert 'is_default' in mode_data, "Missing 'is_default' field"
        assert 'is_flight_recorder' in mode_data, "Missing 'is_flight_recorder' field"
        assert 'features' in mode_data, "Missing 'features' field"
    
    def test_set_logging_mode_contract(self):
        """Test: POST /api/log/mode switches mode successfully"""
        # ARRANGE
        url = f"{LOG_API_BASE}/mode"
        payload = {"mode": "flight_recorder"}
        
        # ACT
        response = requests.post(url, json=payload, timeout=5)
        
        # ASSERT
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert 'status' in data, "Missing 'status' field"
        assert data['status'] == 'success', "Status should be 'success'"
        assert 'message' in data, "Missing 'message' field"
        assert 'data' in data, "Missing 'data' field"
        
        # Verify mode was changed
        mode_data = data['data']
        assert mode_data['mode'] == 'flight_recorder', \
            "Mode should be 'flight_recorder'"
        
        # CLEANUP: Reset to default mode
        reset_payload = {"mode": "default"}
        requests.post(url, json=reset_payload, timeout=5)
    
    def test_set_logging_mode_invalid_value(self):
        """Test: POST /api/log/mode rejects invalid mode"""
        # ARRANGE
        url = f"{LOG_API_BASE}/mode"
        payload = {"mode": "invalid_mode"}
        
        # ACT
        response = requests.post(url, json=payload, timeout=5)
        
        # ASSERT
        assert response.status_code == 400, f"Expected 400, got {response.status_code}"
        
        data = response.json()
        assert 'status' in data, "Missing 'status' field"
        assert data['status'] == 'error', "Status should be 'error'"
        assert 'message' in data, "Missing 'message' field"
        assert 'invalid' in data['message'].lower(), \
            "Error message should mention invalid mode"


@pytest.mark.e2e
@pytest.mark.api_contract
class TestClientLogEndpoint:
    """Test client log submission API contract"""
    
    def test_receive_client_log_contract(self):
        """Test: POST /api/log/client accepts valid log entry"""
        # ARRANGE
        url = f"{LOG_API_BASE}/client"
        payload = {
            "level": "INFO",
            "category": "CLICK",
            "message": "User clicked button",
            "details": {
                "element": "Button#submit",
                "x": 450,
                "y": 300
            }
        }
        
        # ACT
        response = requests.post(url, json=payload, timeout=5)
        
        # ASSERT
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert 'status' in data, "Missing 'status' field"
        assert data['status'] == 'success', "Status should be 'success'"
        assert 'message' in data, "Missing 'message' field"
    
    def test_receive_client_log_missing_fields(self):
        """Test: POST /api/log/client rejects incomplete log"""
        # ARRANGE
        url = f"{LOG_API_BASE}/client"
        payload = {
            "level": "INFO"
            # Missing 'category' and 'message'
        }
        
        # ACT
        response = requests.post(url, json=payload, timeout=5)
        
        # ASSERT
        assert response.status_code == 400, f"Expected 400, got {response.status_code}"
        
        data = response.json()
        assert 'status' in data, "Missing 'status' field"
        assert data['status'] == 'error', "Status should be 'error'"
        assert 'message' in data, "Missing 'message' field"
        assert 'missing' in data['message'].lower(), \
            "Error message should mention missing fields"
    
    def test_receive_client_log_error_level(self):
        """Test: POST /api/log/client accepts ERROR level logs"""
        # ARRANGE
        url = f"{LOG_API_BASE}/client"
        payload = {
            "level": "ERROR",
            "category": "API_ERROR",
            "message": "API request failed",
            "details": {
                "url": "/api/data-products",
                "status": 500
            }
        }
        
        # ACT
        response = requests.post(url, json=payload, timeout=5)
        
        # ASSERT
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert data['status'] == 'success', "Status should be 'success'"


@pytest.mark.e2e
@pytest.mark.api_contract
class TestHealthCheckEndpoint:
    """Test health check API contract"""
    
    def test_health_check_contract(self):
        """Test: GET /api/log/health returns valid health status"""
        # ARRANGE
        url = f"{LOG_API_BASE}/health"
        
        # ACT
        response = requests.get(url, timeout=5)
        
        # ASSERT
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert 'status' in data, "Missing 'status' field"
        assert data['status'] == 'healthy', "Status should be 'healthy'"
        assert 'module' in data, "Missing 'module' field"
        assert data['module'] == 'logger', "Module should be 'logger'"
        assert 'version' in data, "Missing 'version' field"
        assert 'mode' in data, "Missing 'mode' field"
        assert 'timestamp' in data, "Missing 'timestamp' field"


@pytest.mark.e2e
@pytest.mark.api_contract
class TestLogsRetrievalEndpoint:
    """Test logs retrieval API contract"""
    
    def test_get_logs_contract(self):
        """Test: GET /api/log/logs returns valid structure"""
        # ARRANGE
        url = f"{LOG_API_BASE}/logs"
        params = {
            "limit": 10,
            "offset": 0
        }
        
        # ACT
        response = requests.get(url, params=params, timeout=5)
        
        # ASSERT
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert 'status' in data, "Missing 'status' field"
        assert data['status'] == 'success', "Status should be 'success'"
        assert 'data' in data, "Missing 'data' field"
        
        # Validate data structure
        logs_data = data['data']
        assert 'logs' in logs_data, "Missing 'logs' field"
        assert 'total' in logs_data, "Missing 'total' field"
        assert 'limit' in logs_data, "Missing 'limit' field"
        assert 'offset' in logs_data, "Missing 'offset' field"
        assert isinstance(logs_data['logs'], list), "'logs' should be a list"


if __name__ == '__main__':
    pytest.main([__file__, '-v', '--tb=short'])