"""
Test Coverage Agent - Test Quality & API Contract Validation

Specializes in:
- API contract test detection (Gu Wu methodology enforcement)
- Backend API test validation (@pytest.mark.api_contract)
- Frontend API test validation (metadata endpoints)
- General test coverage analysis
- Test quality assessment

Based on: Gu Wu API-First Contract Testing Foundation (Feb 15, 2026)
Philosophy: "Test the API contract, trust the implementation"
"""

import json
from pathlib import Path
from typing import List, Dict, Optional
import time

from .base_agent import BaseAgent, AgentReport, Finding, Severity


class TestCoverageAgent(BaseAgent):
    """
    Validates test coverage and enforces API-First Contract Testing
    
    Ensures:
    - Modules with APIs have backend contract tests (CRITICAL)
    - Modules have frontend metadata tests (HIGH)
    - Tests use @pytest.mark.api_contract marker
    - Tests use HTTP calls (requests), not internal imports
    - General test coverage exists
    """
    
    def __init__(self):
        super().__init__("test_coverage")
        
        # Project root for test file paths
        self.project_root = Path(__file__).parent.parent.parent.parent
    
    def analyze_module(self, module_path: Path) -> AgentReport:
        """
        Analyze test coverage for a module
        
        For modules/ analysis: Checks API contract tests + general coverage
        For project root analysis: Checks all modules
        
        Args:
            module_path: Path to module directory
            
        Returns:
            AgentReport with test coverage findings
        """
        start_time = time.time()
        findings = []
        
        if not self.validate_module_path(module_path):
            return AgentReport(
                agent_name=self.name,
                module_path=module_path,
                execution_time_seconds=0,
                findings=[],
                metrics={},
                summary="Invalid module path"
            )
        
        self.logger.info(f"Analyzing test coverage of {module_path}")
        
        # Determine if we're analyzing a single module or entire project
        is_single_module = (module_path.parent.name == 'modules')
        
        if is_single_module:
            # Analyze single module
            findings.extend(self._check_api_contract_tests(module_path))
            findings.extend(self._check_general_test_coverage(module_path))
        else:
            # Analyze entire project (all modules)
            modules_dir = module_path / 'modules'
            if modules_dir.exists():
                for module_dir in modules_dir.iterdir():
                    if module_dir.is_dir() and not module_dir.name.startswith(('_', '.')):
                        findings.extend(self._check_api_contract_tests(module_dir))
                        findings.extend(self._check_general_test_coverage(module_dir))
        
        execution_time = time.time() - start_time
        
        # Calculate metrics
        metrics = {
            'total_findings': len(findings),
            'critical_count': sum(1 for f in findings if f.severity == Severity.CRITICAL),
            'high_count': sum(1 for f in findings if f.severity == Severity.HIGH),
            'medium_count': sum(1 for f in findings if f.severity == Severity.MEDIUM),
            'low_count': sum(1 for f in findings if f.severity == Severity.LOW),
            'modules_analyzed': 1 if is_single_module else len(list((module_path / 'modules').iterdir())) if (module_path / 'modules').exists() else 0,
            'api_contract_gaps': sum(1 for f in findings if 'API' in f.category),
            'general_coverage_gaps': sum(1 for f in findings if 'Coverage' in f.category)
        }
        
        summary = self._generate_summary(findings, metrics)
        
        self.logger.info(f"Test coverage analysis complete: {summary}")
        
        return AgentReport(
            agent_name=self.name,
            module_path=module_path,
            execution_time_seconds=execution_time,
            findings=findings,
            metrics=metrics,
            summary=summary
        )
    
    def get_capabilities(self) -> List[str]:
        """Return list of test coverage capabilities"""
        return [
            "API contract test detection (Gu Wu methodology)",
            "Backend API test validation (@pytest.mark.api_contract + requests)",
            "Frontend API test validation (metadata endpoints)",
            "Test file existence checking",
            "Test marker validation",
            "HTTP vs internal import detection",
            "General test coverage analysis",
            "Test quality assessment"
        ]
    
    def _check_api_contract_tests(self, module_path: Path) -> List[Finding]:
        """
        Check if module has proper API contract tests
        
        Gu Wu Foundation (Feb 15, 2026):
        "Test the API contract, trust the implementation"
        
        Backend API: Tests /api/{module}/endpoints via HTTP
        Frontend API: Tests /api/modules/frontend-registry
        
        One API test validates entire call chain implicitly:
        Controller → Service → Repository → Database
        """
        findings = []
        
        try:
            # Check if module has backend API
            api_file = module_path / "backend" / "api.py"
            if not api_file.exists():
                return findings  # No API to test
            
            module_name = module_path.name
            
            # Check backend API contract test
            backend_test = self.project_root / f"tests/test_{module_name}_backend.py"
            if not backend_test.exists():
                findings.append(Finding(
                    category="Missing Backend API Contract Test",
                    severity=Severity.CRITICAL,
                    file_path=api_file,
                    line_number=None,
                    description=f"Module '{module_name}' has API but no backend contract test",
                    recommendation=(
                        f"CREATE tests/test_{module_name}_backend.py with:\n"
                        f"  @pytest.mark.api_contract\n"
                        f"  @pytest.mark.e2e\n"
                        f"  requests.post/get() (HTTP calls)\n"
                        f"  Test endpoints as black boxes\n\n"
                        f"Example:\n"
                        f"  @pytest.mark.api_contract\n"
                        f"  @pytest.mark.e2e\n"
                        f"  def test_{module_name}_endpoint():\n"
                        f"      response = requests.post('http://localhost:5000/api/{module_name}/endpoint')\n"
                        f"      assert response.status_code == 200"
                    ),
                    issue_explanation=(
                        "API-First Contract Testing requires HTTP-level tests. "
                        "One API test validates the entire call chain implicitly "
                        "(Controller → Service → Repository → Database)."
                    ),
                    impact_estimate="Prevents regression in API contracts (60-300x faster than browser tests)",
                    effort_estimate="15-30 minutes to create contract test"
                ))
            else:
                # Verify test has proper markers and uses HTTP
                validation_issues = self._validate_api_contract_test(backend_test, module_name, 'backend')
                findings.extend(validation_issues)
            
            # Check frontend API contract test (metadata)
            frontend_test = self.project_root / f"tests/test_{module_name}_frontend_api.py"
            if not frontend_test.exists():
                findings.append(Finding(
                    category="Missing Frontend API Contract Test",
                    severity=Severity.HIGH,
                    file_path=module_path,
                    line_number=None,
                    description=f"Module '{module_name}' missing frontend metadata test",
                    recommendation=(
                        f"CREATE tests/test_{module_name}_frontend_api.py to test:\n"
                        f"  @pytest.mark.api_contract\n"
                        f"  @pytest.mark.e2e\n"
                        f"  /api/modules/frontend-registry endpoint\n"
                        f"  Module metadata structure\n\n"
                        f"Example:\n"
                        f"  @pytest.mark.api_contract\n"
                        f"  @pytest.mark.e2e\n"
                        f"  def test_{module_name}_metadata():\n"
                        f"      response = requests.get('http://localhost:5000/api/modules/frontend-registry')\n"
                        f"      data = response.json()\n"
                        f"      assert '{module_name}' in [m['id'] for m in data['modules']]"
                    ),
                    issue_explanation=(
                        "Frontend API tests validate module metadata structure. "
                        "Ensures frontend can discover and load the module correctly."
                    ),
                    impact_estimate="Prevents module registration failures",
                    effort_estimate="10-15 minutes to create metadata test"
                ))
            else:
                # Verify frontend test
                validation_issues = self._validate_api_contract_test(frontend_test, module_name, 'frontend')
                findings.extend(validation_issues)
        
        except Exception as e:
            self.logger.warning(f"Could not check API contract tests for {module_path.name}: {str(e)}")
        
        return findings
    
    def _validate_api_contract_test(self, test_file: Path, module_name: str, test_type: str) -> List[Finding]:
        """
        Validate that test file has proper API contract test structure
        
        Checks:
        - Has @pytest.mark.api_contract marker
        - Uses requests library (HTTP calls)
        - Does NOT use internal imports (testing contracts, not implementation)
        """
        findings = []
        
        try:
            content = test_file.read_text(encoding='utf-8')
            
            # Check for @pytest.mark.api_contract
            if '@pytest.mark.api_contract' not in content:
                findings.append(Finding(
                    category="Invalid API Contract Test",
                    severity=Severity.HIGH,
                    file_path=test_file,
                    line_number=None,
                    description=f"{test_type.capitalize()} test missing @pytest.mark.api_contract marker",
                    recommendation=(
                        "Add @pytest.mark.api_contract decorator to test functions:\n"
                        "  @pytest.mark.api_contract\n"
                        "  @pytest.mark.e2e\n"
                        "  def test_function():\n"
                        "      ..."
                    ),
                    issue_explanation=(
                        "The @pytest.mark.api_contract marker identifies tests that validate "
                        "API contracts. This allows selective test execution and coverage reporting."
                    )
                ))
            
            # Check for HTTP calls (requests library)
            has_http_calls = (
                'requests.post(' in content or 
                'requests.get(' in content or
                'requests.put(' in content or
                'requests.delete(' in content
            )
            
            if not has_http_calls:
                findings.append(Finding(
                    category="Missing HTTP Calls",
                    severity=Severity.HIGH,
                    file_path=test_file,
                    line_number=None,
                    description=f"{test_type.capitalize()} test not using HTTP calls (requests library)",
                    recommendation=(
                        "Use requests library for HTTP calls (NOT internal imports):\n"
                        "  response = requests.post('http://localhost:5000/api/...')\n"
                        "  assert response.status_code == 200\n\n"
                        "DO NOT import internal modules - test the API contract as a black box"
                    ),
                    issue_explanation=(
                        "API contract tests must use HTTP calls to test the public interface, "
                        "not internal imports. This ensures you test what external clients see."
                    )
                ))
            
            # Check for internal imports (anti-pattern for API tests)
            has_internal_imports = (
                f'from modules.{module_name}' in content or
                f'import modules.{module_name}' in content or
                f'from core.' in content  # Accessing core directly
            )
            
            if has_internal_imports:
                findings.append(Finding(
                    category="Internal Imports in API Test",
                    severity=Severity.MEDIUM,
                    file_path=test_file,
                    line_number=None,
                    description=f"{test_type.capitalize()} test uses internal imports (anti-pattern)",
                    recommendation=(
                        "REMOVE internal imports from API contract tests.\n"
                        "Test the API as a black box via HTTP only.\n\n"
                        "BAD:  from modules.{module_name}.backend import service\n"
                        "GOOD: response = requests.post('http://localhost:5000/api/...')"
                    ),
                    issue_explanation=(
                        "API contract tests should NOT access internal implementation. "
                        "Using internal imports couples tests to implementation details, "
                        "defeating the purpose of contract testing."
                    )
                ))
        
        except Exception as e:
            self.logger.warning(f"Could not validate test file {test_file}: {str(e)}")
        
        return findings
    
    def _check_general_test_coverage(self, module_path: Path) -> List[Finding]:
        """
        Check general test coverage (beyond API contracts)
        
        This is a lighter check for:
        - Unit test files existence
        - Test directory structure
        """
        findings = []
        
        try:
            module_name = module_path.name
            
            # Check if module has any tests at all
            tests_dir = self.project_root / "tests"
            if not tests_dir.exists():
                return findings  # No tests directory
            
            # Look for any test files mentioning this module
            module_test_files = list(tests_dir.rglob(f"*{module_name}*.py"))
            
            # Filter out __pycache__ and other non-test files
            module_test_files = [
                f for f in module_test_files 
                if '__pycache__' not in str(f) and f.name.startswith('test_')
            ]
            
            if len(module_test_files) == 0:
                # Module has NO tests at all (not even unit tests)
                findings.append(Finding(
                    category="No Test Coverage",
                    severity=Severity.HIGH,
                    file_path=module_path,
                    line_number=None,
                    description=f"Module '{module_name}' has NO test files",
                    recommendation=(
                        f"CREATE test files for {module_name}:\n"
                        f"  1. API contract tests (if has API)\n"
                        f"  2. Unit tests for complex logic\n"
                        f"  3. Integration tests for workflows"
                    ),
                    issue_explanation=(
                        "Modules without tests are prone to regressions. "
                        "Start with API contract tests (if module has API), "
                        "then add unit tests for complex business logic."
                    )
                ))
            elif len(module_test_files) < 2:
                # Module has some tests but might need more coverage
                findings.append(Finding(
                    category="Limited Test Coverage",
                    severity=Severity.MEDIUM,
                    file_path=module_path,
                    line_number=None,
                    description=f"Module '{module_name}' has only {len(module_test_files)} test file(s)",
                    recommendation=(
                        f"CONSIDER adding more test coverage:\n"
                        f"  - API contract tests (backend + frontend)\n"
                        f"  - Unit tests for business logic\n"
                        f"  - Integration tests for workflows\n\n"
                        f"Current tests: {[f.name for f in module_test_files]}"
                    ),
                    issue_explanation=(
                        "Comprehensive test coverage includes API contracts, "
                        "unit tests, and integration tests. Balance test pyramid."
                    )
                ))
        
        except Exception as e:
            self.logger.warning(f"Could not check general test coverage for {module_path.name}: {str(e)}")
        
        return findings
    
    def _generate_summary(self, findings: List[Finding], metrics: Dict) -> str:
        """Generate human-readable summary"""
        if not findings:
            return f"Test coverage validated: {metrics['modules_analyzed']} module(s) analyzed, all have proper tests"
        
        api_gaps = metrics.get('api_contract_gaps', 0)
        coverage_gaps = metrics.get('general_coverage_gaps', 0)
        
        return (
            f"TEST COVERAGE ISSUES: "
            f"{metrics['total_findings']} finding(s) in {metrics['modules_analyzed']} module(s) - "
            f"{metrics['critical_count']} CRITICAL, {metrics['high_count']} HIGH, "
            f"{metrics['medium_count']} MEDIUM, {metrics['low_count']} LOW "
            f"({api_gaps} API contract gap(s), {coverage_gaps} general coverage gap(s))"
        )