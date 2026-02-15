"""
Tests for ModuleFederationAgent

Tests validation of Module Federation Standard v1.0 compliance.
"""

import pytest
import json
import tempfile
from pathlib import Path

from tools.fengshui.agents.module_federation_agent import ModuleFederationAgent
from tools.fengshui.agents.base_agent import Severity


@pytest.fixture
def agent():
    """Create ModuleFederationAgent instance"""
    return ModuleFederationAgent()


@pytest.fixture
def temp_module_dir():
    """Create temporary module directory"""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def valid_module_json():
    """Valid module.json configuration"""
    return {
        "id": "test_module",
        "name": "Test Module",
        "version": "1.0.0",
        "description": "Test module for validation",
        "category": "data_management",
        "enabled": True,
        "frontend": {
            "page_name": "test-module",
            "nav_title": "Test Module",
            "nav_icon": "sap-icon://test",
            "route": "/test-module",
            "show_in_navigation": True,
            "scripts": ["/modules/test_module/frontend/module.js"],
            "entry_point": {
                "factory": "TestModule"
            }
        },
        "backend": {
            "blueprint": "modules.test_module.backend:blueprint",
            "mount_path": "/api/test-module"
        }
    }


class TestModuleFederationAgent:
    """Test suite for ModuleFederationAgent"""
    
    def test_agent_initialization(self, agent):
        """Test: Agent initializes correctly"""
        assert agent.name == 'module_federation'
        assert len(agent.get_capabilities()) > 0
    
    def test_get_capabilities(self, agent):
        """Test: Agent reports correct capabilities"""
        capabilities = agent.get_capabilities()
        
        assert "module.json existence and validity" in capabilities
        assert "Required fields validation" in capabilities
        # Check for naming convention with any additional details
        assert any("Naming convention compliance" in cap for cap in capabilities)
        assert "Directory structure validation" in capabilities
    
    def test_missing_module_json(self, agent, temp_module_dir):
        """Test: Detects missing module.json"""
        # Don't create module.json
        
        report = agent.analyze_module(temp_module_dir)
        
        assert len(report.findings) > 0
        critical_findings = [f for f in report.findings if f.severity == Severity.CRITICAL]
        assert len(critical_findings) > 0
        assert any('module.json' in f.description.lower() for f in critical_findings)
    
    def test_invalid_json_syntax(self, agent, temp_module_dir):
        """Test: Detects invalid JSON syntax"""
        # Create invalid JSON
        module_json_path = temp_module_dir / 'module.json'
        module_json_path.write_text('{ invalid json }')
        
        report = agent.analyze_module(temp_module_dir)
        
        critical_findings = [f for f in report.findings if f.severity == Severity.CRITICAL]
        assert len(critical_findings) > 0
        assert any('not valid JSON' in f.description for f in critical_findings)
    
    def test_missing_required_fields(self, agent, temp_module_dir):
        """Test: Detects missing required fields"""
        # Create module.json with missing fields
        module_json_path = temp_module_dir / 'module.json'
        module_json_path.write_text(json.dumps({
            "id": "test_module",
            "name": "Test Module"
            # Missing: version, description, category, enabled
        }))
        
        report = agent.analyze_module(temp_module_dir)
        
        # Should find missing fields
        high_findings = [f for f in report.findings if f.severity == Severity.HIGH]
        assert len(high_findings) >= 4  # At least 4 missing fields
        
        missing_fields = {'version', 'description', 'category', 'enabled'}
        found_missing = set()
        for finding in high_findings:
            for field in missing_fields:
                if field in finding.description:
                    found_missing.add(field)
        
        assert len(found_missing) == 4
    
    def test_invalid_category(self, agent, temp_module_dir):
        """Test: Detects invalid category value"""
        # Create module.json with invalid category
        module_json_path = temp_module_dir / 'module.json'
        module_json_path.write_text(json.dumps({
            "id": "test_module",
            "name": "Test Module",
            "version": "1.0.0",
            "description": "Test",
            "category": "invalid_category",  # Invalid
            "enabled": True
        }))
        
        report = agent.analyze_module(temp_module_dir)
        
        # Should find invalid category
        category_findings = [f for f in report.findings if 'category' in f.description.lower()]
        assert len(category_findings) > 0
    
    def test_snake_case_module_id(self, agent, temp_module_dir):
        """Test: Validates snake_case for module ID"""
        # Test invalid module IDs
        invalid_ids = [
            "TestModule",      # PascalCase
            "test-module",     # kebab-case
            "test.module",     # dot notation
            "TestModule123",   # Mixed case
            "123test"          # Starts with number
        ]
        
        for invalid_id in invalid_ids:
            module_json_path = temp_module_dir / 'module.json'
            module_json_path.write_text(json.dumps({
                "id": invalid_id,
                "name": "Test",
                "version": "1.0.0",
                "description": "Test",
                "category": "data_management",
                "enabled": True
            }))
            
            report = agent.analyze_module(temp_module_dir)
            naming_findings = [f for f in report.findings 
                             if 'Naming Convention' in f.category and 'snake_case' in f.description]
            assert len(naming_findings) > 0, f"Failed to detect invalid ID: {invalid_id}"
    
    def test_kebab_case_routes(self, agent, temp_module_dir):
        """Test: Validates kebab-case for routes"""
        # Test invalid routes
        invalid_routes = [
            "/TestModule",      # PascalCase
            "/test_module",     # snake_case
            "/Test-Module",     # Mixed case
            "test-module",      # Missing leading /
        ]
        
        for invalid_route in invalid_routes:
            module_json_path = temp_module_dir / 'module.json'
            module_json_path.write_text(json.dumps({
                "id": "test_module",
                "name": "Test",
                "version": "1.0.0",
                "description": "Test",
                "category": "data_management",
                "enabled": True,
                "frontend": {
                    "route": invalid_route
                }
            }))
            
            report = agent.analyze_module(temp_module_dir)
            naming_findings = [f for f in report.findings 
                             if 'Naming Convention' in f.category and 'kebab-case' in f.description]
            assert len(naming_findings) > 0, f"Failed to detect invalid route: {invalid_route}"
    
    def test_api_mount_path_validation(self, agent, temp_module_dir):
        """Test: Validates /api/kebab-case for API paths"""
        # Test invalid mount paths
        invalid_paths = [
            "/api/TestModule",     # PascalCase
            "/api/test_module",    # snake_case
            "/test-module",        # Missing /api/
            "api/test-module",     # Missing leading /
        ]
        
        for invalid_path in invalid_paths:
            module_json_path = temp_module_dir / 'module.json'
            module_json_path.write_text(json.dumps({
                "id": "test_module",
                "name": "Test",
                "version": "1.0.0",
                "description": "Test",
                "category": "data_management",
                "enabled": True,
                "backend": {
                    "mount_path": invalid_path
                }
            }))
            
            report = agent.analyze_module(temp_module_dir)
            naming_findings = [f for f in report.findings 
                             if 'Naming Convention' in f.category and 'mount_path' in f.description]
            assert len(naming_findings) > 0, f"Failed to detect invalid mount_path: {invalid_path}"
    
    def test_factory_name_validation(self, agent, temp_module_dir):
        """Test: Validates PascalCase + Module/Factory for factory names"""
        # Test invalid factory names
        invalid_factories = [
            "testModule",          # camelCase
            "test_module",         # snake_case
            "TestModuleClass",     # Wrong suffix
            "testmodule",          # lowercase
        ]
        
        for invalid_factory in invalid_factories:
            module_json_path = temp_module_dir / 'module.json'
            module_json_path.write_text(json.dumps({
                "id": "test_module",
                "name": "Test",
                "version": "1.0.0",
                "description": "Test",
                "category": "data_management",
                "enabled": True,
                "frontend": {
                    "entry_point": {
                        "factory": invalid_factory
                    }
                }
            }))
            
            report = agent.analyze_module(temp_module_dir)
            naming_findings = [f for f in report.findings 
                             if 'Naming Convention' in f.category and 'factory' in f.description.lower()]
            assert len(naming_findings) > 0, f"Failed to detect invalid factory: {invalid_factory}"
    
    def test_missing_backend_directory(self, agent, temp_module_dir, valid_module_json):
        """Test: Detects missing backend/ directory when declared"""
        # Create module.json with backend declared
        module_json_path = temp_module_dir / 'module.json'
        module_json_path.write_text(json.dumps(valid_module_json))
        
        # Don't create backend/ directory
        
        report = agent.analyze_module(temp_module_dir)
        
        backend_findings = [f for f in report.findings 
                          if 'backend/' in f.description.lower() and 'directory' in f.description.lower()]
        assert len(backend_findings) > 0
    
    def test_missing_frontend_directory(self, agent, temp_module_dir, valid_module_json):
        """Test: Detects missing frontend/ directory when declared"""
        # Create module.json with frontend declared
        module_json_path = temp_module_dir / 'module.json'
        module_json_path.write_text(json.dumps(valid_module_json))
        
        # Don't create frontend/ directory
        
        report = agent.analyze_module(temp_module_dir)
        
        frontend_findings = [f for f in report.findings 
                           if 'frontend/' in f.description.lower() and 'directory' in f.description.lower()]
        assert len(frontend_findings) > 0
    
    def test_missing_tests_directory(self, agent, temp_module_dir, valid_module_json):
        """Test: Detects missing tests/ directory (required for all modules)"""
        # Create module.json
        module_json_path = temp_module_dir / 'module.json'
        module_json_path.write_text(json.dumps(valid_module_json))
        
        # Don't create tests/ directory
        
        report = agent.analyze_module(temp_module_dir)
        
        tests_findings = [f for f in report.findings 
                        if 'tests/' in f.description.lower() and 'directory' in f.description.lower()]
        assert len(tests_findings) > 0
    
    def test_missing_readme(self, agent, temp_module_dir, valid_module_json):
        """Test: Detects missing README.md"""
        # Create module.json
        module_json_path = temp_module_dir / 'module.json'
        module_json_path.write_text(json.dumps(valid_module_json))
        
        # Don't create README.md
        
        report = agent.analyze_module(temp_module_dir)
        
        readme_findings = [f for f in report.findings 
                         if 'readme' in f.description.lower()]
        assert len(readme_findings) > 0
    
    def test_missing_backend_api_file(self, agent, temp_module_dir, valid_module_json):
        """Test: Detects missing backend/api.py"""
        # Create module.json with backend
        module_json_path = temp_module_dir / 'module.json'
        module_json_path.write_text(json.dumps(valid_module_json))
        
        # Create backend/ dir but not api.py
        backend_dir = temp_module_dir / 'backend'
        backend_dir.mkdir()
        
        report = agent.analyze_module(temp_module_dir)
        
        api_findings = [f for f in report.findings 
                      if 'api.py' in f.description.lower()]
        assert len(api_findings) > 0
    
    def test_missing_frontend_module_file(self, agent, temp_module_dir, valid_module_json):
        """Test: Detects missing frontend/module.js"""
        # Create module.json with frontend
        module_json_path = temp_module_dir / 'module.json'
        module_json_path.write_text(json.dumps(valid_module_json))
        
        # Create frontend/ dir but not module.js
        frontend_dir = temp_module_dir / 'frontend'
        frontend_dir.mkdir()
        
        report = agent.analyze_module(temp_module_dir)
        
        module_js_findings = [f for f in report.findings 
                            if 'module.js' in f.description.lower()]
        assert len(module_js_findings) > 0
    
    def test_missing_api_tests(self, agent, temp_module_dir, valid_module_json):
        """Test: Detects missing API contract tests"""
        # Create module.json
        module_json_path = temp_module_dir / 'module.json'
        module_json_path.write_text(json.dumps(valid_module_json))
        
        # Create tests/ dir but no test files
        tests_dir = temp_module_dir / 'tests'
        tests_dir.mkdir()
        
        report = agent.analyze_module(temp_module_dir)
        
        test_findings = [f for f in report.findings 
                       if 'test' in f.description.lower() and 'api' in f.description.lower()]
        assert len(test_findings) > 0
    
    def test_fully_compliant_module(self, agent, temp_module_dir, valid_module_json):
        """Test: Fully compliant module has no findings"""
        # Create complete module structure
        module_json_path = temp_module_dir / 'module.json'
        module_json_path.write_text(json.dumps(valid_module_json))
        
        # Create README
        (temp_module_dir / 'README.md').write_text('# Test Module')
        
        # Create backend structure
        backend_dir = temp_module_dir / 'backend'
        backend_dir.mkdir()
        (backend_dir / '__init__.py').touch()
        (backend_dir / 'api.py').write_text('from flask import Blueprint\nblueprint = Blueprint("test", __name__)')
        
        # Create frontend structure
        frontend_dir = temp_module_dir / 'frontend'
        frontend_dir.mkdir()
        (frontend_dir / 'module.js').write_text('class TestModule {}')
        
        # Create tests structure
        tests_dir = temp_module_dir / 'tests'
        tests_dir.mkdir()
        (tests_dir / 'test_backend_api.py').write_text('def test_api(): pass')
        (tests_dir / 'test_frontend_api.py').write_text('def test_frontend(): pass')
        
        report = agent.analyze_module(temp_module_dir)
        
        # Should have no findings for compliant module
        assert len(report.findings) == 0
        assert report.metrics['compliance_score'] == 100.0
    
    def test_compliance_score_calculation(self, agent, temp_module_dir):
        """Test: Compliance score calculated correctly"""
        # Create module.json with only ID (many violations)
        module_json_path = temp_module_dir / 'module.json'
        module_json_path.write_text(json.dumps({"id": "test_module"}))
        
        report = agent.analyze_module(temp_module_dir)
        
        # Should have compliance score < 100
        assert report.metrics['compliance_score'] < 100.0
        assert report.metrics['total_findings'] > 0
    
    def test_helper_to_snake_case(self, agent):
        """Test: snake_case conversion helper"""
        assert agent._to_snake_case('TestModule') == 'test_module'
        assert agent._to_snake_case('test-module') == 'test_module'
        assert agent._to_snake_case('test.module') == 'test_module'
        assert agent._to_snake_case('AIAssistant') == 'ai_assistant'
    
    def test_helper_to_kebab_case(self, agent):
        """Test: kebab-case conversion helper"""
        assert agent._to_kebab_case('test_module') == 'test-module'
        assert agent._to_kebab_case('TestModule') == 'test-module'
        assert agent._to_kebab_case('ai_assistant') == 'ai-assistant'
    
    def test_helper_to_pascal_case(self, agent):
        """Test: PascalCase conversion helper"""
        assert agent._to_pascal_case('test_module') == 'TestModule'
        assert agent._to_pascal_case('test-module') == 'TestModule'
        assert agent._to_pascal_case('ai assistant') == 'AiAssistant'
    
    def test_report_structure(self, agent, temp_module_dir):
        """Test: Report has correct structure"""
        # Create minimal module
        module_json_path = temp_module_dir / 'module.json'
        module_json_path.write_text(json.dumps({"id": "test"}))
        
        report = agent.analyze_module(temp_module_dir)
        
        # Check report structure
        assert report.agent_name == 'module_federation'
        assert report.module_path == temp_module_dir
        assert isinstance(report.execution_time_seconds, float)
        assert isinstance(report.findings, list)
        assert isinstance(report.metrics, dict)
        assert 'compliance_score' in report.metrics
        assert 'total_findings' in report.metrics
    
    def test_finding_has_actionable_fields(self, agent, temp_module_dir):
        """Test: Findings include actionable reporting fields"""
        # Create module with violations
        module_json_path = temp_module_dir / 'module.json'
        module_json_path.write_text('{}')  # Empty
        
        report = agent.analyze_module(temp_module_dir)
        
        # Check findings have actionable fields
        for finding in report.findings:
            assert finding.category is not None
            assert finding.severity is not None
            assert finding.description is not None
            assert finding.recommendation is not None
            # Optional fields may or may not be present
            assert hasattr(finding, 'issue_explanation')
            assert hasattr(finding, 'fix_example')
            assert hasattr(finding, 'impact_estimate')
            assert hasattr(finding, 'effort_estimate')