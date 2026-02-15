"""
E2E tests for ai_assistant module

Tests frontend UX code compliance with Gu Wu standards.
Following .clinerules section 7.2: UX Testing Enforcement

Generated for: AI Assistant module
Date: 2026-02-13
"""

import pytest
from pathlib import Path
import json


# Module under test
MODULE_NAME = "ai_assistant"
MODULE_PATH = Path(f"modules/{MODULE_NAME}")


@pytest.fixture
def module_config():
    """Load module.json configuration"""
    config_path = MODULE_PATH / "module.json"
    return json.loads(config_path.read_text())


@pytest.fixture
def app_v2_base_url():
    """Base URL for App V2 (assumes local development)"""
    return "http://localhost:5000"


@pytest.mark.e2e
@pytest.mark.app_v2
def test_module_registry_discovery():
    """
    Test: Module is discoverable by FrontendModuleRegistry
    
    ARRANGE
    """
    from core.services.frontend_module_registry import FrontendModuleRegistry
    
    registry = FrontendModuleRegistry()
    
    # ACT
    modules = registry.get_frontend_modules()
    module_ids = [m['id'] for m in modules]
    
    # ASSERT
    assert MODULE_NAME in module_ids, \
        f"Module '{MODULE_NAME}' not discovered by FrontendModuleRegistry. " \
        f"Found modules: {module_ids}"
    
    # Verify module metadata
    module_data = registry.get_module_by_id(MODULE_NAME)
    assert module_data is not None, f"Module '{MODULE_NAME}' has no metadata"
    
    # Verify required fields
    required_fields = ['id', 'name', 'version', 'icon', 'frontend']
    for field in required_fields:
        assert field in module_data, f"Module metadata missing field: {field}"


@pytest.mark.e2e
@pytest.mark.app_v2
def test_scripts_accessible(module_config, app_v2_base_url):
    """
    Test: Frontend scripts are accessible via HTTP
    
    ARRANGE
    """
    import requests
    
    if 'frontend' not in module_config:
        pytest.skip("Module has no frontend configuration")
    
    scripts = module_config['frontend'].get('scripts', [])
    
    # ACT & ASSERT
    for script in scripts:
        # Remove leading slash for file system check
        script_path = script.lstrip('/')
        script_url = f"{app_v2_base_url}/{script_path}"
        response = requests.get(script_url, timeout=5)
        
        assert response.status_code == 200, \
            f"Script not accessible: {script} ({response.status_code})"


@pytest.mark.e2e
@pytest.mark.app_v2
def test_module_configuration_valid(module_config):
    """
    Test: Module configuration is valid
    
    ARRANGE/ACT/ASSERT
    """
    # Verify essential configuration fields
    assert 'id' in module_config, "Module missing 'id'"
    assert 'name' in module_config, "Module missing 'name'"
    assert 'version' in module_config, "Module missing 'version'"
    assert 'enabled' in module_config, "Module missing 'enabled'"
    
    # Verify frontend configuration
    assert 'frontend' in module_config, "Module missing 'frontend' config"
    frontend = module_config['frontend']
    
    assert 'module_id' in frontend, "Frontend missing 'module_id'"
    assert 'scripts' in frontend, "Frontend missing 'scripts'"
    assert len(frontend['scripts']) > 0, "Frontend has no scripts"
    
    # Verify all scripts have leading slash (absolute paths)
    for script in frontend['scripts']:
        assert script.startswith('/'), \
            f"Script missing leading slash: {script} (required for HTTP loading)"


@pytest.mark.e2e
@pytest.mark.app_v2
def test_backend_api_registration():
    """
    Test: Backend API blueprint is properly registered
    
    ARRANGE
    """
    config_path = MODULE_PATH / "module.json"
    config = json.loads(config_path.read_text())
    
    # ACT - Verify backend configuration
    assert 'backend' in config, "Module missing backend configuration"
    backend_config = config['backend']
    
    # ASSERT - Verify required fields
    assert 'blueprint' in backend_config, "Backend config missing blueprint"
    assert 'mount_path' in backend_config, "Backend config missing mount_path"
    
    # Verify blueprint path format
    blueprint_spec = backend_config['blueprint']
    assert ':' in blueprint_spec, f"Invalid blueprint spec: {blueprint_spec}"
    
    module_path, blueprint_name = blueprint_spec.split(':')
    assert module_path.startswith('modules.ai_assistant.backend'), \
        f"Blueprint not in backend module: {module_path}"


@pytest.mark.e2e
@pytest.mark.app_v2
def test_backend_health_endpoint(app_v2_base_url):
    """
    Test: Backend health endpoint is functional
    
    ARRANGE
    """
    import requests
    
    # ACT
    response = requests.get(
        f"{app_v2_base_url}/api/ai-assistant/health",
        timeout=5
    )
    
    # ASSERT
    assert response.status_code == 200, \
        f"Health endpoint failed: {response.status_code}"
    
    data = response.json()
    assert 'status' in data, "Response missing 'status' field"
    assert data['status'] == 'healthy', "API not healthy"


@pytest.mark.e2e
@pytest.mark.app_v2
def test_chat_api_structure():
    """
    Test: Chat API endpoint follows proper structure
    
    ARRANGE
    """
    config_path = MODULE_PATH / "module.json"
    config = json.loads(config_path.read_text())
    
    # ACT - Check API endpoints configuration
    assert 'api_endpoints' in config, "Module missing api_endpoints config"
    
    # ASSERT - Verify chat endpoint exists
    chat_endpoint = next(
        (ep for ep in config['api_endpoints'] if 'chat' in ep['path']),
        None
    )
    
    assert chat_endpoint is not None, "No chat endpoint defined"
    assert chat_endpoint['method'] == 'POST', "Chat endpoint should use POST"
    assert '/api/ai-assistant/chat' in chat_endpoint['path'], \
        "Chat endpoint path incorrect"


@pytest.mark.e2e
@pytest.mark.app_v2
def test_frontend_scripts_exist(module_config):
    """
    Test: All declared frontend scripts exist on filesystem
    
    ARRANGE
    """
    if 'frontend' not in module_config:
        pytest.skip("Module has no frontend configuration")
    
    scripts = module_config['frontend'].get('scripts', [])
    
    # ACT & ASSERT
    for script in scripts:
        # Remove leading slash for file system check
        script_path = Path(script.lstrip('/'))
        
        assert script_path.exists(), \
            f"Script file not found: {script_path}"


@pytest.mark.e2e
@pytest.mark.app_v2
def test_no_di_violations_in_api():
    """
    Test: API layer has no dependency injection violations
    
    ARRANGE
    """
    api_path = MODULE_PATH / "backend/api.py"
    assert api_path.exists(), "API blueprint not found"
    
    # ACT - Read API code
    api_content = api_path.read_text()
    
    # ASSERT - Check for DI violations
    direct_access_patterns = [
        'sqlite3.connect',
        'hdbcli.dbapi.connect',
        'database/',
        '.connection.',
        '.db_path'
    ]
    
    violations = [p for p in direct_access_patterns if p in api_content]
    assert not violations, \
        f"API has direct resource access (DI violation): {violations}"


@pytest.mark.e2e
@pytest.mark.app_v2
def test_module_enabled_in_config(module_config):
    """
    Test: Module is enabled in configuration
    
    ARRANGE/ACT/ASSERT
    """
    assert module_config.get('enabled', False) is True, \
        f"Module '{MODULE_NAME}' is disabled in module.json"


@pytest.mark.e2e
@pytest.mark.app_v2
def test_shell_actions_configuration(module_config):
    """
    Test: Shell actions are properly configured
    
    ARRANGE
    """
    if 'frontend' not in module_config:
        pytest.skip("Module has no frontend configuration")
    
    frontend = module_config['frontend']
    
    # ACT - Check shell actions
    if 'shell_actions' in frontend:
        shell_actions = frontend['shell_actions']
        
        # ASSERT - Verify structure
        for action in shell_actions:
            assert 'id' in action, "Shell action missing 'id'"
            assert 'icon' in action, "Shell action missing 'icon'"
            assert 'text' in action, "Shell action missing 'text'"
            assert 'action' in action, "Shell action missing 'action'"


if __name__ == '__main__':
    pytest.main([__file__, '-v'])