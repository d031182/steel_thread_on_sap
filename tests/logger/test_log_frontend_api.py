"""
Logger Module Frontend API Contract Tests
=========================================
Tests for logger module metadata/configuration endpoints.

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
class TestLoggerModuleMetadata:
    """Test logger module metadata in frontend registry"""
    
    def test_logger_module_in_registry(self):
        """Test: Logger module is registered in frontend registry with correct metadata"""
        # ARRANGE
        url = f"{BASE_URL}/api/modules/frontend-registry"
        
        # ACT
        response = requests.get(url, timeout=5)
        
        # ASSERT
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert 'modules' in data, "Missing 'modules' field"
        assert isinstance(data['modules'], list), "'modules' should be a list"
        
        # Find logger module (id should be 'logger' not 'log')
        logger_module = next(
            (m for m in data['modules'] if m.get('id') == 'logger'),
            None
        )
        
        assert logger_module is not None, "Logger module should be registered in frontend registry"
        
        # Validate required fields
        assert logger_module['id'] == 'logger', "Module ID should be 'logger'"
        assert 'name' in logger_module, "Missing 'name' field"
        assert logger_module['name'] == 'Logger', "Module name should be 'Logger'"
        
        assert 'category' in logger_module, "Missing 'category' field"
        assert logger_module['category'] == 'System', "Module category should be 'System'"
        
        assert 'version' in logger_module, "Missing 'version' field"
        assert 'enabled' in logger_module, "Missing 'enabled' field"
        assert logger_module['enabled'] is True, "Module should be enabled"
        
        # Validate optional fields (if present)
        if 'icon' in logger_module:
            assert 'sap-icon' in logger_module['icon'], "Icon should be a SAP icon"
        
        if 'route' in logger_module:
            assert logger_module['route'].startswith('/'), "Route should start with /"
    
    def test_logger_module_scripts_present(self):
        """Test: Logger module has required scripts defined"""
        # ARRANGE
        url = f"{BASE_URL}/api/modules/frontend-registry"
        
        # ACT
        response = requests.get(url, timeout=5)
        
        # ASSERT
        data = response.json()
        logger_module = next(
            (m for m in data['modules'] if m.get('id') == 'logger'),
            None
        )
        
        assert logger_module is not None, "Logger module should be registered"
        
        # Check for scripts array
        if 'scripts' in logger_module:
            assert isinstance(logger_module['scripts'], list), "'scripts' should be a list"
            assert len(logger_module['scripts']) > 0, "Module should have at least one script"
            
            # Check that scripts contain expected paths
            scripts_str = ' '.join(logger_module['scripts'])
            assert 'logger' in scripts_str.lower(), "Scripts should reference logger module"


if __name__ == '__main__':
    pytest.main([__file__, '-v', '--tb=short'])