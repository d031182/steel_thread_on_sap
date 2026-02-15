"""
Module Federation Agent - Validates Module Federation Standard Compliance

Validates modules against the Module Federation Standard v1.0:
- module.json schema and required fields
- Naming conventions (snake_case, kebab-case, PascalCase)
- Directory structure (backend/, frontend/, tests/)
- Required files (README.md, api.py, module.js)

Author: Feng Shui Quality System
Date: February 15, 2026
Standard: docs/knowledge/module-federation-standard.md
"""

import json
import re
import time
from pathlib import Path
from typing import List, Dict, Optional

from .base_agent import BaseAgent, AgentReport, Finding, Severity


class ModuleFederationAgent(BaseAgent):
    """
    Validates Module Federation Standard compliance
    
    Checks:
    1. module.json exists and is valid JSON
    2. Required fields present (id, name, version, description, enabled)
    3. Naming conventions (snake_case, kebab-case, PascalCase)
    4. Directory structure (backend/, frontend/, tests/)
    5. Required files exist (README.md, api.py, module.js)
    6. API contracts tested
    """
    
    # Required fields in module.json
    REQUIRED_FIELDS = {'id', 'name', 'version', 'description', 'category', 'enabled'}
    
    # Valid categories
    VALID_CATEGORIES = {
        'infrastructure',  # Core services (logger, feature_manager)
        'data_management', # Data access and processing
        'analytics',       # Visualization and analysis
        'configuration',   # System configuration
        'system'          # System utilities
    }
    
    def __init__(self):
        super().__init__('module_federation')
    
    def get_capabilities(self) -> List[str]:
        """Return list of what this agent can detect"""
        return [
            "module.json existence and validity",
            "Required fields validation",
            "Naming convention compliance (snake_case, kebab-case, PascalCase)",
            "Directory structure validation",
            "Required file existence",
            "API contract test presence",
            "Backend/frontend separation",
            "Documentation completeness"
        ]
    
    def analyze_module(self, module_path: Path) -> AgentReport:
        """
        Analyze module for Module Federation Standard compliance
        
        Args:
            module_path: Path to module directory
            
        Returns:
            AgentReport with findings
        """
        start_time = time.time()
        findings = []
        
        if not self.validate_module_path(module_path):
            return self._create_empty_report(module_path, "Invalid module path")
        
        # Load module.json
        module_json_path = module_path / 'module.json'
        module_config = self._load_module_json(module_json_path, findings)
        
        if module_config:
            # Validate required fields
            self._validate_required_fields(module_config, module_json_path, findings)
            
            # Validate naming conventions
            self._validate_naming_conventions(module_config, module_json_path, findings)
            
            # Validate directory structure
            self._validate_directory_structure(module_path, module_config, findings)
            
            # Validate required files
            self._validate_required_files(module_path, module_config, findings)
            
            # Validate testing
            self._validate_testing(module_path, findings)
        
        execution_time = time.time() - start_time
        
        # Generate summary
        summary = self._generate_summary(findings, module_path)
        
        # Calculate compliance score
        metrics = self._calculate_metrics(findings, module_config)
        
        return AgentReport(
            agent_name=self.name,
            module_path=module_path,
            execution_time_seconds=execution_time,
            findings=findings,
            metrics=metrics,
            summary=summary
        )
    
    def _load_module_json(self, module_json_path: Path, findings: List[Finding]) -> Optional[Dict]:
        """Load and validate module.json file"""
        if not module_json_path.exists():
            findings.append(Finding(
                category="Missing module.json",
                severity=Severity.CRITICAL,
                file_path=module_json_path,
                line_number=None,
                description="module.json file not found",
                recommendation="Create module.json with required fields (id, name, version, description, category, enabled)",
                issue_explanation="module.json is the single source of truth for module configuration",
                fix_example='Create modules/[name]/module.json with:\n{\n  "id": "module_name",\n  "name": "Module Name",\n  "version": "1.0.0",\n  "description": "Module description",\n  "category": "data_management",\n  "enabled": true\n}',
                impact_estimate="Module won't be discovered by system",
                effort_estimate="10 min"
            ))
            return None
        
        try:
            with open(module_json_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except json.JSONDecodeError as e:
            findings.append(Finding(
                category="Invalid JSON",
                severity=Severity.CRITICAL,
                file_path=module_json_path,
                line_number=e.lineno if hasattr(e, 'lineno') else None,
                description=f"module.json is not valid JSON: {str(e)}",
                recommendation="Fix JSON syntax errors",
                issue_explanation="Invalid JSON prevents module from being loaded",
                impact_estimate="Module completely broken",
                effort_estimate="5 min"
            ))
            return None
    
    def _validate_required_fields(self, config: Dict, file_path: Path, findings: List[Finding]):
        """Validate required fields in module.json"""
        missing_fields = self.REQUIRED_FIELDS - set(config.keys())
        
        for field in missing_fields:
            findings.append(Finding(
                category="Missing Required Field",
                severity=Severity.HIGH,
                file_path=file_path,
                line_number=None,
                description=f"Required field '{field}' missing from module.json",
                recommendation=f"Add '{field}' field to module.json",
                issue_explanation=f"'{field}' is required by Module Federation Standard v1.0",
                fix_example=f'Add to module.json:\n"{field}": "value"',
                impact_estimate="Module may not load correctly",
                effort_estimate="2 min"
            ))
        
        # Validate category value
        if 'category' in config and config['category'] not in self.VALID_CATEGORIES:
            findings.append(Finding(
                category="Invalid Category",
                severity=Severity.MEDIUM,
                file_path=file_path,
                line_number=None,
                description=f"Category '{config['category']}' not in valid categories: {', '.join(self.VALID_CATEGORIES)}",
                recommendation=f"Use one of: {', '.join(self.VALID_CATEGORIES)}",
                issue_explanation="Invalid category affects module organization and navigation",
                impact_estimate="Minor navigation issues",
                effort_estimate="1 min"
            ))
    
    def _validate_naming_conventions(self, config: Dict, file_path: Path, findings: List[Finding]):
        """Validate naming conventions per standard"""
        
        # 1. Module ID: snake_case
        if 'id' in config:
            module_id = config['id']
            if not re.match(r'^[a-z][a-z0-9_]*$', module_id):
                findings.append(Finding(
                    category="Naming Convention Violation",
                    severity=Severity.HIGH,
                    file_path=file_path,
                    line_number=None,
                    description=f"Module ID '{module_id}' not in snake_case format",
                    recommendation="Use snake_case for module IDs (e.g., 'ai_assistant', 'data_products_v2')",
                    code_snippet=f'"id": "{module_id}"',
                    issue_explanation="Module Federation Standard requires snake_case for module IDs",
                    fix_example=f'"id": "{self._to_snake_case(module_id)}"',
                    impact_estimate="Module discovery may fail",
                    effort_estimate="5 min"
                ))
        
        # 2. Frontend route: /kebab-case
        if 'frontend' in config and 'route' in config['frontend']:
            route = config['frontend']['route']
            if route and not re.match(r'^/[a-z][a-z0-9-]*$', route):
                findings.append(Finding(
                    category="Naming Convention Violation",
                    severity=Severity.MEDIUM,
                    file_path=file_path,
                    line_number=None,
                    description=f"Frontend route '{route}' not in /kebab-case format",
                    recommendation="Use /kebab-case for routes (e.g., '/ai-assistant', '/data-products-v2')",
                    code_snippet=f'"route": "{route}"',
                    issue_explanation="Module Federation Standard requires kebab-case for routes",
                    fix_example=f'"route": "/{self._to_kebab_case(route.lstrip("/"))}"',
                    impact_estimate="Routing may not work correctly",
                    effort_estimate="2 min"
                ))
        
        # 3. Backend mount_path: /api/kebab-case
        if 'backend' in config and 'mount_path' in config['backend']:
            mount_path = config['backend']['mount_path']
            if mount_path and not re.match(r'^/api/[a-z][a-z0-9-]*$', mount_path):
                findings.append(Finding(
                    category="Naming Convention Violation",
                    severity=Severity.MEDIUM,
                    file_path=file_path,
                    line_number=None,
                    description=f"Backend mount_path '{mount_path}' not in /api/kebab-case format",
                    recommendation="Use /api/kebab-case for mount paths (e.g., '/api/ai-assistant')",
                    code_snippet=f'"mount_path": "{mount_path}"',
                    issue_explanation="Module Federation Standard requires /api/kebab-case for API paths",
                    fix_example=f'"mount_path": "/api/{self._to_kebab_case(mount_path.replace("/api/", ""))}"',
                    impact_estimate="API routing may not work",
                    effort_estimate="2 min"
                ))
        
        # 4. Factory name: PascalCase + Module/Factory
        if 'frontend' in config and 'entry_point' in config['frontend']:
            factory = config['frontend']['entry_point'].get('factory')
            if factory:
                if not re.match(r'^[A-Z][a-zA-Z0-9]+(Module|Factory)$', factory):
                    findings.append(Finding(
                        category="Naming Convention Violation",
                        severity=Severity.MEDIUM,
                        file_path=file_path,
                        line_number=None,
                        description=f"Factory name '{factory}' not in PascalCase format ending with 'Module' or 'Factory'",
                        recommendation="Use PascalCase + 'Module' or 'Factory' (e.g., 'AIAssistantModule', 'DataProductsFactory')",
                        code_snippet=f'"factory": "{factory}"',
                        issue_explanation="Module Federation Standard requires PascalCase for factory names",
                        fix_example=f'"factory": "{self._to_pascal_case(factory)}Module"',
                        impact_estimate="Module may not initialize",
                        effort_estimate="2 min"
                    ))
    
    def _validate_directory_structure(self, module_path: Path, config: Dict, findings: List[Finding]):
        """Validate directory structure"""
        
        # Check backend/ if module has backend
        if config.get('backend'):
            backend_dir = module_path / 'backend'
            if not backend_dir.exists():
                findings.append(Finding(
                    category="Missing Directory",
                    severity=Severity.HIGH,
                    file_path=backend_dir,
                    line_number=None,
                    description="backend/ directory missing but module.json declares backend",
                    recommendation="Create backend/ directory with __init__.py and api.py",
                    issue_explanation="Module Federation Standard requires backend/ for modules with backend logic",
                    fix_example="mkdir backend && touch backend/__init__.py backend/api.py",
                    impact_estimate="Backend won't load",
                    effort_estimate="5 min"
                ))
        
        # Check frontend/ if module has frontend
        if config.get('frontend'):
            frontend_dir = module_path / 'frontend'
            if not frontend_dir.exists():
                findings.append(Finding(
                    category="Missing Directory",
                    severity=Severity.HIGH,
                    file_path=frontend_dir,
                    line_number=None,
                    description="frontend/ directory missing but module.json declares frontend",
                    recommendation="Create frontend/ directory with module.js",
                    issue_explanation="Module Federation Standard requires frontend/ for modules with UI",
                    fix_example="mkdir frontend && touch frontend/module.js",
                    impact_estimate="Frontend won't load",
                    effort_estimate="5 min"
                ))
        
        # NOTE: Tests are validated in _validate_testing() which checks Gu Wu standard locations:
        # - /tests/unit/modules/[module_name]/ (PREFERRED)
        # - /tests/e2e/app_v2/ (for API contract tests)
        # - module_path/tests/ (legacy, acceptable)
        # We don't require module/tests/ here since root /tests is the standard.
    
    def _validate_required_files(self, module_path: Path, config: Dict, findings: List[Finding]):
        """Validate required files exist"""
        
        # README.md (REQUIRED)
        readme_path = module_path / 'README.md'
        if not readme_path.exists():
            findings.append(Finding(
                category="Missing Required File",
                severity=Severity.MEDIUM,
                file_path=readme_path,
                line_number=None,
                description="README.md missing",
                recommendation="Create README.md with module description, usage, and API documentation",
                issue_explanation="Module Federation Standard requires README.md for all modules",
                fix_example="Create README.md with module overview, features, and usage instructions",
                impact_estimate="Poor documentation",
                effort_estimate="30 min"
            ))
        
        # backend/api.py (if backend exists)
        if config.get('backend'):
            api_path = module_path / 'backend' / 'api.py'
            if not api_path.exists():
                findings.append(Finding(
                    category="Missing Required File",
                    severity=Severity.HIGH,
                    file_path=api_path,
                    line_number=None,
                    description="backend/api.py missing but module has backend",
                    recommendation="Create backend/api.py with Flask Blueprint",
                    issue_explanation="Module Federation Standard requires api.py for backend modules",
                    fix_example="Create backend/api.py with: from flask import Blueprint\nblueprint = Blueprint('module_name_api', __name__)",
                    impact_estimate="Backend won't work",
                    effort_estimate="15 min"
                ))
        
        # frontend/module.js (if frontend exists)
        if config.get('frontend'):
            module_js_path = module_path / 'frontend' / 'module.js'
            if not module_js_path.exists():
                findings.append(Finding(
                    category="Missing Required File",
                    severity=Severity.HIGH,
                    file_path=module_js_path,
                    line_number=None,
                    description="frontend/module.js missing but module has frontend",
                    recommendation="Create frontend/module.js with factory function",
                    issue_explanation="Module Federation Standard requires module.js for frontend modules",
                    fix_example="Create frontend/module.js with factory function exporting to window scope",
                    impact_estimate="Frontend won't load",
                    effort_estimate="30 min"
                ))
    
    def _validate_testing(self, module_path: Path, findings: List[Finding]):
        """
        Validate API contract tests exist per Gu Wu standard
        
        Gu Wu Standard Test Locations:
        1. /tests/unit/modules/[module_name]/ - Unit tests (PREFERRED)
        2. /tests/e2e/app_v2/ - E2E/API contract tests
        3. module_path/tests/ - Legacy module-local tests (acceptable)
        
        We check project root /tests first, fall back to module-local tests/
        """
        # Get module name
        module_id = module_path.name
        
        # Get project root (assume modules/ is 2 levels deep)
        project_root = module_path.parent.parent if module_path.parent.name == 'modules' else module_path.parent
        
        # Check Gu Wu standard locations
        root_tests_dir = project_root / 'tests'
        module_unit_tests = root_tests_dir / 'unit' / 'modules' / module_id if root_tests_dir.exists() else None
        module_e2e_tests = root_tests_dir / 'e2e' / 'app_v2' if root_tests_dir.exists() else None
        module_local_tests = module_path / 'tests'
        
        # Look for test files matching this module
        backend_tests_found = False
        frontend_tests_found = False
        test_location = None
        
        # Check /tests/unit/modules/[module_name]/
        if module_unit_tests and module_unit_tests.exists():
            backend_files = list(module_unit_tests.glob('test_*.py'))
            if backend_files:
                backend_tests_found = True
                test_location = "root /tests/unit/modules/"
        
        # Check /tests/e2e/app_v2/ for API contract tests
        if module_e2e_tests and module_e2e_tests.exists():
            api_test_pattern = f'test_{module_id}*.py'
            e2e_files = list(module_e2e_tests.glob(api_test_pattern))
            if e2e_files:
                backend_tests_found = True
                frontend_tests_found = True  # E2E tests cover both
                test_location = "root /tests/e2e/app_v2/"
        
        # Check module-local tests/ (legacy)
        if module_local_tests.exists():
            backend_files = list(module_local_tests.glob('**/test_*backend*.py')) + \
                           list(module_local_tests.glob('**/test_*api*.py'))
            frontend_files = list(module_local_tests.glob('**/test_*frontend*.py'))
            
            if backend_files:
                backend_tests_found = True
                test_location = "module-local tests/"
            if frontend_files:
                frontend_tests_found = True
        
        # Report missing tests
        if not backend_tests_found:
            findings.append(Finding(
                category="Missing API Tests",
                severity=Severity.MEDIUM,
                file_path=root_tests_dir / 'unit' / 'modules' / module_id if root_tests_dir else module_local_tests,
                line_number=None,
                description="No backend API contract tests found",
                recommendation=f"Create /tests/unit/modules/{module_id}/test_api.py with @pytest.mark.api_contract tests",
                issue_explanation="Gu Wu standard requires API contract tests at /tests/unit/modules/[module_name]/",
                fix_example=f"Create /tests/unit/modules/{module_id}/test_api.py testing all API endpoints",
                impact_estimate="API changes may break system",
                effort_estimate="1 hour"
            ))
        
        if not frontend_tests_found and not backend_tests_found:
            findings.append(Finding(
                category="Missing API Tests",
                severity=Severity.LOW,
                file_path=root_tests_dir / 'unit' / 'modules' / module_id if root_tests_dir else module_local_tests,
                line_number=None,
                description="No frontend API contract tests found",
                recommendation=f"Create /tests/unit/modules/{module_id}/test_frontend_api.py testing metadata endpoint",
                issue_explanation="Gu Wu standard recommends testing /api/modules/frontend-registry endpoint",
                fix_example=f"Create test_frontend_api.py testing module metadata",
                impact_estimate="Module metadata may be incorrect",
                effort_estimate="30 min"
            ))
    
    def _generate_summary(self, findings: List[Finding], module_path: Path) -> str:
        """Generate human-readable summary"""
        if not findings:
            return f"✅ Module '{module_path.name}' fully compliant with Module Federation Standard v1.0"
        
        critical = sum(1 for f in findings if f.severity == Severity.CRITICAL)
        high = sum(1 for f in findings if f.severity == Severity.HIGH)
        medium = sum(1 for f in findings if f.severity == Severity.MEDIUM)
        low = sum(1 for f in findings if f.severity == Severity.LOW)
        
        summary_parts = [f"Module '{module_path.name}' has {len(findings)} Module Federation Standard violations:"]
        
        if critical:
            summary_parts.append(f"- {critical} CRITICAL issues (blocks module loading)")
        if high:
            summary_parts.append(f"- {high} HIGH issues (functionality broken)")
        if medium:
            summary_parts.append(f"- {medium} MEDIUM issues (should fix)")
        if low:
            summary_parts.append(f"- {low} LOW issues (nice to have)")
        
        return "\n".join(summary_parts)
    
    def _calculate_metrics(self, findings: List[Finding], config: Optional[Dict]) -> Dict[str, float]:
        """Calculate compliance metrics"""
        total_checks = 20  # Total possible checks
        failed_checks = len(findings)
        compliance_score = max(0, (total_checks - failed_checks) / total_checks * 100)
        
        return {
            'compliance_score': round(compliance_score, 2),
            'total_findings': len(findings),
            'critical_findings': sum(1 for f in findings if f.severity == Severity.CRITICAL),
            'high_findings': sum(1 for f in findings if f.severity == Severity.HIGH),
            'medium_findings': sum(1 for f in findings if f.severity == Severity.MEDIUM),
            'low_findings': sum(1 for f in findings if f.severity == Severity.LOW)
        }
    
    # Helper methods for naming conversion
    def _to_snake_case(self, text: str) -> str:
        """Convert to snake_case"""
        text = re.sub(r'[^a-zA-Z0-9_]', '_', text)
        text = re.sub(r'([A-Z]+)([A-Z][a-z])', r'\1_\2', text)
        text = re.sub(r'([a-z\d])([A-Z])', r'\1_\2', text)
        return text.lower()
    
    def _to_kebab_case(self, text: str) -> str:
        """Convert to kebab-case"""
        text = self._to_snake_case(text)
        return text.replace('_', '-')
    
    def _to_pascal_case(self, text: str) -> str:
        """Convert to PascalCase"""
        parts = re.split(r'[_\-\s]+', text)
        return ''.join(word.capitalize() for word in parts if word)