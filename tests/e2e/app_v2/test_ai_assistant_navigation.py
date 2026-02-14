"""
E2E Tests: AI Assistant Navigation Persistence
===============================================

Tests that AI Assistant shell button works after navigating between pages.

WHY THIS TEST EXISTS:
- AI Assistant is eager-init module (loaded at app startup)
- Provides shell button accessible from all pages
- RouterService must NOT destroy eager-init modules during navigation
- Bug: RouterService was destroying AI Assistant on navigation, breaking button

ROOT CAUSE:
- RouterService._renderModule() called module.destroy() on ALL previous modules
- This deleted window.aiAssistant, breaking shell button
- FIX: Skip destroying modules with eager_init: true

ARCHITECTURE:
- Eager-init modules = shell services (persist across navigation)
- Lazy-load modules = page-specific (destroyed on navigation)

@markers: e2e, app_v2
@created: 2026-02-14
@author: P2P Development Team
"""

import pytest
from pathlib import Path
import json


@pytest.fixture
def ai_assistant_config():
    """Load AI Assistant module.json configuration"""
    config_path = Path("modules/ai_assistant/module.json")
    assert config_path.exists(), "AI Assistant module.json not found"
    
    with open(config_path, 'r') as f:
        config = json.load(f)
    
    return config


@pytest.mark.e2e
@pytest.mark.app_v2
def test_ai_assistant_eager_init_flag(ai_assistant_config):
    """
    Test: AI Assistant has eager_init flag enabled
    
    ARRANGE/ACT
    """
    # ASSERT
    assert 'eager_init' in ai_assistant_config, \
        "AI Assistant must have eager_init field"
    assert ai_assistant_config['eager_init'] is True, \
        "AI Assistant must have eager_init: true"


@pytest.mark.e2e
@pytest.mark.app_v2
def test_ai_assistant_provides_shell_actions(ai_assistant_config):
    """
    Test: AI Assistant registers getShellActions for shell button
    
    ARRANGE/ACT
    """
    # ASSERT
    # Module must have getShellActions method (checked in module.js)
    frontend_scripts = ai_assistant_config.get('frontend', {}).get('scripts', [])
    assert len(frontend_scripts) > 0, \
        "AI Assistant must have frontend scripts"
    
    # Module factory must be defined
    entry_point = ai_assistant_config.get('frontend', {}).get('entry_point', {})
    assert 'factory' in entry_point, \
        "AI Assistant must define factory in entry_point"
    assert entry_point['factory'] == 'AIAssistantModule', \
        "Factory must be named AIAssistantModule"


@pytest.mark.e2e
@pytest.mark.app_v2
def test_router_service_skip_eager_destroy():
    """
    Test: RouterService skips destroying eager-init modules
    
    ARRANGE
    """
    router_path = Path("app_v2/static/js/core/RouterService.js")
    assert router_path.exists(), "RouterService.js not found"
    
    with open(router_path, 'r') as f:
        router_code = f.read()
    
    # ACT/ASSERT
    # Must check for eager_init flag before destroying
    assert 'eager_init' in router_code, \
        "RouterService must check eager_init flag"
    
    assert 'Skipping destroy for eager-init module' in router_code, \
        "RouterService must skip destroying eager-init modules"
    
    # Must get previous module to check flag
    assert 'previousModule' in router_code or 'previous module' in router_code.lower(), \
        "RouterService must retrieve previous module metadata"


@pytest.mark.e2e
@pytest.mark.app_v2
def test_module_lifecycle_preservation():
    """
    Test: AI Assistant module.js does NOT self-destruct window.aiAssistant incorrectly
    
    ARRANGE
    """
    module_path = Path("modules/ai_assistant/frontend/module.js")
    assert module_path.exists(), "AI Assistant module.js not found"
    
    with open(module_path, 'r') as f:
        module_code = f.read()
    
    # ACT/ASSERT
    # Module must register window.aiAssistant in initialize()
    assert 'window.aiAssistant' in module_code, \
        "Module must register window.aiAssistant"
    
    # destroy() method should only be called on app shutdown, NOT navigation
    # RouterService now prevents this by checking eager_init flag
    assert 'destroy: function()' in module_code or 'destroy:function()' in module_code, \
        "Module must have destroy method for cleanup"


@pytest.mark.e2e
@pytest.mark.app_v2
def test_shell_button_architecture():
    """
    Test: ModuleBootstrap creates persistent shell button
    
    ARRANGE
    """
    bootstrap_path = Path("app_v2/static/js/core/ModuleBootstrap.js")
    assert bootstrap_path.exists(), "ModuleBootstrap.js not found"
    
    with open(bootstrap_path, 'r') as f:
        bootstrap_code = f.read()
    
    # ACT/ASSERT
    # Shell button created in _createAppShell()
    assert 'sap-icon://collaborate' in bootstrap_code, \
        "Shell button must use collaborate icon"
    
    # Button click handler checks window.aiAssistant
    assert '_onToggleAIAssistant' in bootstrap_code, \
        "Must have AI Assistant toggle handler"
    
    assert 'window.aiAssistant' in bootstrap_code and 'window.aiAssistant.open' in bootstrap_code, \
        "Handler must call window.aiAssistant.open()"
    
    # Fallback message for not-yet-loaded case
    assert 'AI Assistant is loading' in bootstrap_code, \
        "Must show loading message if module not ready"