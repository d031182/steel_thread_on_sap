"""
App V2 Test Generator

Generates pytest tests for App V2 modules from Feng Shui validation reports.
"""

from pathlib import Path
from typing import Dict, Any, List, Union
from .base_generator import BaseTestGenerator


class AppV2TestGenerator(BaseTestGenerator):
    """
    Generate pytest tests for App V2 modules
    
    Converts Feng Shui AgentReport into pytest tests.
    """
    
    def generate_from_report(self, report: Union['AgentReport', Dict[str, Any]]) -> Path:
        """
        Generate pytest tests from Feng Shui AgentReport
        
        Creates tests for:
        1. Scripts accessibility
        2. Navigation consistency
        3. Interface compliance
        4. Dynamic loading compatibility
        5. SAPUI5 rendering safety
        
        Args:
            report: Feng Shui AgentReport object or dict
            
        Returns:
            Path to generated test file
        """
        # Handle both AgentReport object and dict
        if hasattr(report, 'to_dict'):
            report_dict = report.to_dict()
            module_name = report.module_path.name
            findings = report.findings
        else:
            report_dict = report
            module_name = Path(report_dict['module_path']).name
            # Convert findings dicts back to objects for easier processing
            findings = report_dict['findings']
        
        # Group findings by category (5 check types)
        checks = self._group_findings_by_category(findings)
        
        # Generate test file
        test_content = self._generate_test_header(module_name)
        
        # Add fixtures
        test_content += self._generate_fixtures(module_name)
        
        # Generate tests for each check
        for check in checks:
            test_content += self._generate_test_for_check(check, module_name)
        
        # Add footer
        test_content += self._generate_test_footer()
        
        # Write to file
        output_file = self.output_dir / f"test_{module_name}.py"
        output_file.write_text(test_content)
        
        return output_file
    
    def _group_findings_by_category(self, findings: List) -> List[Dict]:
        """
        Group findings by the 5 App V2 check categories
        
        Args:
            findings: List of Finding objects or dicts
            
        Returns:
            List of check dicts with grouped findings
        """
        # Define category mappings
        category_mapping = {
            "Scripts Not Accessible": "Scripts Accessible",
            "Server Not Running": "Scripts Accessible",
            "Navigation Configuration": "Navigation Consistency",
            "Interface Compliance": "Interface Compliance",
            "Dynamic Loading Compatibility": "Dynamic Loading Compatibility",
            "SAPUI5 Rendering Safety": "SAPUI5 Rendering Safety"
        }
        
        # Group findings by check name
        checks_dict = {
            "Scripts Accessible": [],
            "Navigation Consistency": [],
            "Interface Compliance": [],
            "Dynamic Loading Compatibility": [],
            "SAPUI5 Rendering Safety": []
        }
        
        for finding in findings:
            # Handle both Finding objects and dicts
            if hasattr(finding, 'category'):
                category = finding.category
            else:
                category = finding['category']
            
            check_name = category_mapping.get(category, category)
            if check_name in checks_dict:
                checks_dict[check_name].append(finding)
        
        # Convert to check list format
        checks = []
        for check_name, check_findings in checks_dict.items():
            checks.append({
                "name": check_name,
                "status": "FAIL" if check_findings else "PASS",
                "issues": check_findings
            })
        
        return checks
    
    def _generate_fixtures(self, module_name: str) -> str:
        """Generate pytest fixtures"""
        return f'''

@pytest.fixture
def module_config():
    """Load module.json configuration"""
    config_path = MODULE_PATH / "module.json"
    return json.loads(config_path.read_text())


@pytest.fixture
def app_v2_base_url():
    """Base URL for App V2 (assumes local development)"""
    return "http://localhost:5000"

'''
    
    def _generate_test_for_check(self, check: Dict[str, Any], module_name: str) -> str:
        """Generate pytest test for a specific check"""
        check_name = check['name']
        status = check['status']
        issues = check['issues']
        
        # Map check names to test methods
        test_mapping = {
            "Scripts Accessible": self._generate_scripts_test,
            "Navigation Consistency": self._generate_navigation_test,
            "Interface Compliance": self._generate_interface_test,
            "Dynamic Loading Compatibility": self._generate_loading_test,
            "SAPUI5 Rendering Safety": self._generate_rendering_test,
        }
        
        generator = test_mapping.get(check_name)
        if generator:
            return generator(check, module_name, issues)
        else:
            return f"\n# TODO: Test for {check_name} not yet implemented\n"
    
    def _generate_scripts_test(self, check: Dict, module_name: str, issues: List[Dict]) -> str:
        """Generate test for scripts accessibility"""
        return f'''

@pytest.mark.e2e
@pytest.mark.app_v2
def test_scripts_accessible(module_config, app_v2_base_url):
    """
    Test: Frontend scripts are accessible via HTTP
    
    Feng Shui Check: Scripts Accessible
    Status: {check['status']}
    Issues Found: {len(issues)}
    """
    import requests
    
    if 'frontend' not in module_config:
        pytest.skip("Module has no frontend configuration")
    
    scripts = module_config['frontend'].get('scripts', [])
    
    for script in scripts:
        script_url = f"{{app_v2_base_url}}/v2/{{script}}"
        response = requests.get(script_url, timeout=5)
        
        assert response.status_code == 200, \\
            f"Script not accessible: {{script}} ({{response.status_code}})"
'''
    
    def _generate_navigation_test(self, check: Dict, module_name: str, issues: List[Dict]) -> str:
        """Generate test for navigation consistency"""
        return f'''

@pytest.mark.e2e
@pytest.mark.app_v2
def test_navigation_consistency(module_config):
    """
    Test: Navigation structure is consistent
    
    Feng Shui Check: Navigation Consistency
    Status: {check['status']}
    Issues Found: {len(issues)}
    """
    if 'frontend' not in module_config:
        pytest.skip("Module has no frontend configuration")
    
    frontend_config = module_config['frontend']
    
    # Verify module has required navigation fields
    assert 'entry_point' in frontend_config, "Missing entry_point in frontend config"
    assert 'scripts' in frontend_config, "Missing scripts in frontend config"
    
    # If category is declared, ensure it's valid
    if 'category' in frontend_config:
        category = frontend_config['category']
        valid_categories = ['infrastructure', 'features', 'analytics']
        assert category in valid_categories, \\
            f"Invalid category: {{category}}. Must be one of {{valid_categories}}"
'''
    
    def _generate_interface_test(self, check: Dict, module_name: str, issues: List[Dict]) -> str:
        """Generate test for interface compliance"""
        return f'''

@pytest.mark.e2e
@pytest.mark.app_v2
def test_interface_compliance():
    """
    Test: Implementations match their interfaces
    
    Feng Shui Check: Interface Compliance
    Status: {check['status']}
    Issues Found: {len(issues)}
    """
    # Check NoOpLogger implements complete ILogger interface
    noop_logger = Path("app_v2/static/js/adapters/NoOpLogger.js")
    ilogger = Path("app_v2/static/js/interfaces/ILogger.js")
    
    assert noop_logger.exists(), "NoOpLogger.js not found"
    assert ilogger.exists(), "ILogger.js not found"
    
    # Extract methods from interface
    import re
    ilogger_content = ilogger.read_text()
    interface_methods = set(re.findall(r'^\\s*(\\w+)\\s*\\([^)]*\\)\\s*{{', ilogger_content, re.MULTILINE))
    
    # Extract methods from implementation
    noop_content = noop_logger.read_text()
    impl_methods = set(re.findall(r'^\\s*(\\w+)\\s*\\([^)]*\\)\\s*{{', noop_content, re.MULTILINE))
    
    # Verify all interface methods are implemented
    missing_methods = interface_methods - impl_methods
    assert not missing_methods, \\
        f"NoOpLogger missing methods: {{', '.join(missing_methods)}}"
'''
    
    def _generate_loading_test(self, check: Dict, module_name: str, issues: List[Dict]) -> str:
        """Generate test for dynamic loading compatibility"""
        return f'''

@pytest.mark.e2e
@pytest.mark.app_v2
def test_dynamic_loading_compatibility(module_config):
    """
    Test: Module exports are compatible with dynamic loading
    
    Feng Shui Check: Dynamic Loading Compatibility
    Status: {check['status']}
    Issues Found: {len(issues)}
    """
    if 'frontend' not in module_config:
        pytest.skip("Module has no frontend configuration")
    
    scripts = module_config['frontend'].get('scripts', [])
    
    for script in scripts:
        script_path = Path(script)
        
        if not script_path.exists():
            pytest.skip(f"Script not found: {{script}}")
        
        content = script_path.read_text()
        
        # Check for problematic ES6 exports
        problematic_patterns = ['export function', 'export const', 'export class']
        found_patterns = [p for p in problematic_patterns if p in content]
        
        assert not found_patterns, \\
            f"ES6 exports detected in {{script}}: {{found_patterns}} " \\
            f"(incompatible with dynamic <script> loading). " \\
            f"Use window.FunctionName = ... instead."
'''
    
    def _generate_rendering_test(self, check: Dict, module_name: str, issues: List[Dict]) -> str:
        """Generate test for SAPUI5 rendering safety"""
        return f'''

@pytest.mark.e2e
@pytest.mark.app_v2
def test_sapui5_rendering_safety():
    """
    Test: SAPUI5 rendering follows safe patterns
    
    Feng Shui Check: SAPUI5 Rendering Safety
    Status: {check['status']}
    Issues Found: {len(issues)}
    """
    router_service = Path("app_v2/static/js/core/RouterService.js")
    
    assert router_service.exists(), "RouterService.js not found"
    
    content = router_service.read_text()
    
    # Check for problematic patterns
    problematic_patterns = {{
        'document.createElement': 'Temp DOM element creation',
        'placeAt': 'placeAt() usage (can cause lifecycle issues)',
    }}
    
    warnings = []
    for pattern, description in problematic_patterns.items():
        if pattern in content:
            warnings.append(f"{{description}} detected in RouterService")
    
    # This is a warning, not a failure (may be intentional)
    if warnings:
        import warnings as warn_module
        warn_module.warn(
            "Potential SAPUI5 rendering issues detected:\\n" + 
            "\\n".join(f"  - {{w}}" for w in warnings),
            UserWarning
        )
'''


# CLI interface for standalone usage
if __name__ == '__main__':
    import sys
    import json
    
    if len(sys.argv) < 2:
        print("Usage: python -m tools.guwu.generators.app_v2_test_generator <report.json>")
        sys.exit(1)
    
    report_path = Path(sys.argv[1])
    report = json.loads(report_path.read_text())
    
    generator = AppV2TestGenerator()
    output_file = generator.generate_from_report(report)
    
    print(f"✅ Generated tests: {output_file}")