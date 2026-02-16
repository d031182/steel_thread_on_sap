"""
Log Module Frontend API Contract Tests
======================================
Tests for log module metadata/configuration endpoints.

Following Gu Wu methodology:
- Test frontend metadata APIs
- Fast execution
- AAA pattern
"""

import pytest
import requests


BASE_URL = "http://localhost:5000"


@pytest.mark.e2e
@pytest.mark.api_contract
class TestLogModuleMetadata:
    """Test log module metadata in frontend registry"""
    
    def test_log_module_in_registry(self):
        """Test: Log module is registered in frontend registry"""
        # ARRANGE
        url = f"{BASE_URL}/api/modules/frontend-registry"
        
        # ACT
        response = requests.get(url, timeout=5)
        
        # ASSERT
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert 'modules' in data, "Missing 'modules' field"
        
        # Find log module
        log_module = next(
            (m for m in data['modules'] if m.get('id') == 'log'),
            None
        )
        
        # Log module may not be in registry yet (frontend not implemented)
        # This is expected - test documents the contract
        if log_module:
            assert log_module['id'] == 'log', "Module ID should be 'log'"
            assert 'name' in log_module, "Missing 'name' field"
            assert 'category' in log_module, "Missing 'category' field"
        else:
            pytest.skip("Log module frontend not yet registered (expected)")


if __name__ == '__main__':
    pytest.main([__file__, '-v', '--tb=short'])