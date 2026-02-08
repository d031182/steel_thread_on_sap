"""
App V2 Migration Agent

Specialized Feng Shui agent for validating App V2 module migrations.
Detects the 5 critical issues that occur during frontend migration:
1. Scripts not accessible (404 errors)
2. Navigation inconsistencies
3. Interface compliance issues
4. Dynamic loading incompatibilities
5. SAPUI5 rendering problems
"""

import time
import json
import requests
from pathlib import Path
from typing import List
from .base_agent import BaseAgent, AgentReport, Finding, Severity


class AppV2Agent(BaseAgent):
    """
    App V2 Migration Validator Agent
    
    Validates modules being migrated to App V2 architecture.
    Catches common migration issues before manual browser testing.
    """
    
    def __init__(self, base_url: str = "http://localhost:5000"):
        """
        Initialize App V2 agent
        
        Args:
            base_url: Base URL for App V2 server (default: http://localhost:5000)
        """
        super().__init__("app_v2")
        self.base_url = base_url
    
    def analyze_module(self, module_path: Path) -> AgentReport:
        """
        Analyze module for App V2 migration issues
        
        Args:
            module_path: Path to module directory
            
        Returns:
            AgentReport with findings
        """
        start_time = time.time()
        
        if not self.validate_module_path(module_path):
            return self._create_empty_report(module_path)
        
        findings: List[Finding] = []
        
        # Load module.json
        module_json_path = module_path / "module.json"
        if not module_json_path.exists():
            findings.append(Finding(
                category="Module Configuration",
                severity=Severity.CRITICAL,
                file_path=module_json_path,
                line_number=None,
                description="module.json not found",
                recommendation="Create module.json with frontend configuration"
            ))
            return AgentReport(
                agent_name=self.name,
                module_path=module_path,
                execution_time_seconds=time.time() - start_time,
                findings=findings,
                summary="Module configuration missing"
            )
        
        module_config = json.loads(module_json_path.read_text())
        
        # Run 5 validation checks
        findings.extend(self._check_scripts_accessible(module_path, module_config))
        findings.extend(self._check_navigation_consistency(module_path, module_config))
        findings.extend(self._check_interface_compliance(module_path, module_config))
        findings.extend(self._check_dynamic_loading(module_path, module_config))
        findings.extend(self._check_sapui5_rendering(module_path, module_config))
        
        execution_time = time.time() - start_time
        
        return AgentReport(
            agent_name=self.name,
            module_path=module_path,
            execution_time_seconds=execution_time,
            findings=findings,
            metrics={
                'total_checks': 5,
                'scripts_checked': len(module_config.get('frontend', {}).get('scripts', [])),
                'issues_found': len(findings)
            },
            summary=f"Found {len(findings)} App V2 migration issues"
        )
    
    def get_capabilities(self) -> List[str]:
        """Return list of capabilities"""
        return [
            "Frontend script accessibility validation",
            "Navigation structure consistency checks",
            "Interface implementation compliance",
            "Dynamic loading compatibility verification",
            "SAPUI5 rendering safety analysis"
        ]
    
    def _check_scripts_accessible(self, module_path: Path, config: dict) -> List[Finding]:
        """Check if frontend scripts are accessible via HTTP"""
        findings = []
        
        if 'frontend' not in config:
            return findings
        
        scripts = config['frontend'].get('scripts', [])
        
        for script in scripts:
            script_url = f"{self.base_url}/v2/{script}"
            
            try:
                response = requests.get(script_url, timeout=5)
                
                if response.status_code == 404:
                    findings.append(Finding(
                        category="Scripts Not Accessible",
                        severity=Severity.CRITICAL,
                        file_path=Path(script),
                        line_number=None,
                        description=f"Frontend script not accessible: {script} (404 NOT FOUND)",
                        recommendation="Add Flask route: @app.route('/v2/<path:filepath>') or verify file path"
                    ))
                    
            except requests.exceptions.ConnectionError:
                findings.append(Finding(
                    category="Server Not Running",
                    severity=Severity.CRITICAL,
                    file_path=module_path,
                    line_number=None,
                    description=f"App V2 server not reachable at {self.base_url}",
                    recommendation="Start server: python app.py"
                ))
                break  # Don't check remaining scripts if server is down
        
        return findings
    
    def _check_navigation_consistency(self, module_path: Path, config: dict) -> List[Finding]:
        """Check navigation structure consistency"""
        findings = []
        
        if 'frontend' not in config:
            return findings
        
        frontend_config = config['frontend']
        
        # Check required fields
        if 'entry_point' not in frontend_config:
            findings.append(Finding(
                category="Navigation Configuration",
                severity=Severity.HIGH,
                file_path=module_path / "module.json",
                line_number=None,
                description="Missing 'entry_point' in frontend configuration",
                recommendation="Add 'entry_point': 'window.ModuleName' to frontend config"
            ))
        
        if 'scripts' not in frontend_config or not frontend_config['scripts']:
            findings.append(Finding(
                category="Navigation Configuration",
                severity=Severity.HIGH,
                file_path=module_path / "module.json",
                line_number=None,
                description="Missing or empty 'scripts' array in frontend configuration",
                recommendation="Add 'scripts': ['modules/.../frontend/script.js'] to frontend config"
            ))
        
        # Validate category if present
        if 'category' in frontend_config:
            valid_categories = ['infrastructure', 'features', 'analytics']
            if frontend_config['category'] not in valid_categories:
                findings.append(Finding(
                    category="Navigation Configuration",
                    severity=Severity.MEDIUM,
                    file_path=module_path / "module.json",
                    line_number=None,
                    description=f"Invalid category: {frontend_config['category']}",
                    recommendation=f"Use one of: {', '.join(valid_categories)}"
                ))
        
        return findings
    
    def _check_interface_compliance(self, module_path: Path, config: dict) -> List[Finding]:
        """Check if implementations match their interfaces"""
        findings = []
        
        # Check NoOpLogger implements ILogger (common issue)
        noop_logger = Path("app_v2/static/js/adapters/NoOpLogger.js")
        ilogger = Path("app_v2/static/js/interfaces/ILogger.js")
        
        if noop_logger.exists() and ilogger.exists():
            import re
            
            ilogger_content = ilogger.read_text()
            noop_content = noop_logger.read_text()
            
            # Extract method names
            interface_methods = set(re.findall(r'^\s*(\w+)\s*\([^)]*\)\s*{', ilogger_content, re.MULTILINE))
            impl_methods = set(re.findall(r'^\s*(\w+)\s*\([^)]*\)\s*{', noop_content, re.MULTILINE))
            
            missing = interface_methods - impl_methods
            
            if missing:
                findings.append(Finding(
                    category="Interface Compliance",
                    severity=Severity.HIGH,
                    file_path=noop_logger,
                    line_number=None,
                    description=f"NoOpLogger missing methods: {', '.join(missing)}",
                    recommendation=f"Implement missing methods in NoOpLogger: {', '.join(missing)}"
                ))
        
        return findings
    
    def _check_dynamic_loading(self, module_path: Path, config: dict) -> List[Finding]:
        """Check dynamic loading compatibility"""
        findings = []
        
        if 'frontend' not in config:
            return findings
        
        scripts = config['frontend'].get('scripts', [])
        
        for script in scripts:
            script_path = Path(script)
            
            if not script_path.exists():
                continue
            
            content = script_path.read_text()
            
            # Check for ES6 export statements (incompatible with dynamic <script> loading)
            problematic_patterns = ['export function', 'export const', 'export class']
            found_patterns = [p for p in problematic_patterns if p in content]
            
            if found_patterns:
                findings.append(Finding(
                    category="Dynamic Loading Compatibility",
                    severity=Severity.CRITICAL,
                    file_path=script_path,
                    line_number=None,
                    description=f"ES6 exports detected: {', '.join(found_patterns)} (incompatible with dynamic loading)",
                    recommendation="Replace 'export function X' with 'window.X = function' for dynamic <script> compatibility"
                ))
        
        return findings
    
    def _check_sapui5_rendering(self, module_path: Path, config: dict) -> List[Finding]:
        """Check SAPUI5 rendering safety"""
        findings = []
        
        # Check RouterService for problematic patterns
        router_path = Path("app_v2/static/js/core/RouterService.js")
        
        if not router_path.exists():
            return findings
        
        content = router_path.read_text()
        
        # Check for problematic patterns
        issues_found = []
        if 'document.createElement' in content:
            issues_found.append('Temporary DOM element creation detected')
        if 'placeAt' in content:
            issues_found.append('placeAt() usage detected (can cause lifecycle issues)')
        
        if issues_found:
            findings.append(Finding(
                category="SAPUI5 Rendering Safety",
                severity=Severity.MEDIUM,
                file_path=router_path,
                line_number=None,
                description='; '.join(issues_found),
                recommendation="Ensure SAPUI5 controls rendered directly to stable containers (avoid temp → placeAt → move DOM pattern)"
            ))
        
        return findings