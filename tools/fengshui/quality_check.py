#!/usr/bin/env python3
"""
Feng Shui Quality Check - Chain of Responsibility Pattern
==========================================================

Base class and implementations for modular quality checks.

GoF Pattern: Chain of Responsibility
- Each check is independent and can be added/removed easily
- Checks can be skipped conditionally
- Results are aggregated automatically
"""
import re
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Optional, List
from dataclasses import dataclass


@dataclass
class ValidationResult:
    """Result of a validation check"""
    passed: bool
    message: str
    severity: str  # 'ERROR', 'WARNING', 'INFO'
    check_name: str = ""


class QualityCheck(ABC):
    """
    Abstract base class for quality checks (Chain of Responsibility pattern)
    
    Each check:
    1. Performs its validation
    2. Passes control to next check in chain
    3. Returns aggregated results
    """
    
    def __init__(self, next_check: Optional['QualityCheck'] = None):
        """
        Initialize quality check
        
        Args:
            next_check: Next check in the chain (None = last check)
        """
        self.next = next_check
    
    def check(self, context: 'ModuleContext') -> List[ValidationResult]:
        """
        Execute this check and chain to next
        
        Args:
            context: Module validation context
            
        Returns:
            List of validation results (this check + all following checks)
        """
        # Execute this check
        results = self._do_check(context)
        
        # Chain to next check
        if self.next:
            results.extend(self.next.check(context))
        
        return results
    
    @abstractmethod
    def _do_check(self, context: 'ModuleContext') -> List[ValidationResult]:
        """
        Perform the actual validation logic
        
        Args:
            context: Module validation context
            
        Returns:
            List of validation results from this check only
        """
        pass
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Human-readable check name"""
        pass


@dataclass
class ModuleContext:
    """
    Context object passed through quality check chain
    
    Contains all information needed for validation:
    - Module path and metadata
    - Config data (module.json)
    - File contents cache (avoid re-reading)
    """
    module_path: Path
    module_name: str
    has_backend: bool
    config: dict
    _file_cache: dict = None
    
    def __post_init__(self):
        if self._file_cache is None:
            self._file_cache = {}
    
    def read_file(self, file_path: Path) -> Optional[str]:
        """
        Read file with caching
        
        Args:
            file_path: Path to file
            
        Returns:
            File content or None if error
        """
        if file_path in self._file_cache:
            return self._file_cache[file_path]
        
        try:
            with open(file_path, encoding='utf-8') as f:
                content = f.read()
            self._file_cache[file_path] = content
            return content
        except:
            return None
    
    def get_backend_files(self) -> List[Path]:
        """Get all Python files in backend/"""
        if not self.has_backend:
            return []
        
        backend_dir = self.module_path / 'backend'
        return list(backend_dir.rglob('*.py'))


# ============================================================================
# CONCRETE CHECK IMPLEMENTATIONS
# ============================================================================

class ModuleJsonExistsCheck(QualityCheck):
    """Check that module.json exists"""
    
    @property
    def name(self) -> str:
        return "Module JSON Exists"
    
    def _do_check(self, context: ModuleContext) -> List[ValidationResult]:
        module_json = context.module_path / 'module.json'
        
        if not module_json.exists():
            return [ValidationResult(
                passed=False,
                message="module.json not found",
                severity='ERROR',
                check_name=self.name
            )]
        
        return [ValidationResult(
            passed=True,
            message="module.json exists",
            severity='INFO',
            check_name=self.name
        )]


class ModuleJsonValidCheck(QualityCheck):
    """Check that module.json is valid JSON with required fields"""
    
    @property
    def name(self) -> str:
        return "Module JSON Valid"
    
    def _do_check(self, context: ModuleContext) -> List[ValidationResult]:
        required_fields = ['name', 'version', 'description', 'enabled']
        missing = [f for f in required_fields if f not in context.config]
        
        if missing:
            return [ValidationResult(
                passed=False,
                message=f"module.json missing required fields: {missing}",
                severity='ERROR',
                check_name=self.name
            )]
        
        return [ValidationResult(
            passed=True,
            message="module.json has all required fields",
            severity='INFO',
            check_name=self.name
        )]


class BlueprintConfigCheck(QualityCheck):
    """Check blueprint configuration in module.json"""
    
    @property
    def name(self) -> str:
        return "Blueprint Config"
    
    def _do_check(self, context: ModuleContext) -> List[ValidationResult]:
        if not context.has_backend:
            return []  # Skip for frontend-only modules
        
        if 'backend' not in context.config:
            return [ValidationResult(
                passed=False,
                message="Has backend/ but module.json missing 'backend' section",
                severity='ERROR',
                check_name=self.name
            )]
        
        if 'blueprint' not in context.config['backend']:
            return [ValidationResult(
                passed=False,
                message="module.json missing 'backend.blueprint' config",
                severity='ERROR',
                check_name=self.name
            )]
        
        if 'module_path' not in context.config['backend']:
            return [ValidationResult(
                passed=False,
                message="module.json missing 'backend.module_path' config",
                severity='ERROR',
                check_name=self.name
            )]
        
        return [ValidationResult(
            passed=True,
            message=f"Blueprint config present: {context.config['backend']['blueprint']}",
            severity='INFO',
            check_name=self.name
        )]


class BlueprintExportCheck(QualityCheck):
    """Check that blueprint is exported from backend/__init__.py"""
    
    @property
    def name(self) -> str:
        return "Blueprint Export"
    
    def _do_check(self, context: ModuleContext) -> List[ValidationResult]:
        if not context.has_backend:
            return []
        
        backend_init = context.module_path / 'backend' / '__init__.py'
        if not backend_init.exists():
            return [ValidationResult(
                passed=False,
                message="backend/__init__.py doesn't exist",
                severity='ERROR',
                check_name=self.name
            )]
        
        if 'backend' not in context.config or 'blueprint' not in context.config['backend']:
            return []  # Already flagged by BlueprintConfigCheck
        
        blueprint_name = context.config['backend']['blueprint']
        init_content = context.read_file(backend_init)
        
        if not init_content or blueprint_name not in init_content:
            return [ValidationResult(
                passed=False,
                message=f"backend/__init__.py doesn't export '{blueprint_name}'",
                severity='ERROR',
                check_name=self.name
            )]
        
        return [ValidationResult(
            passed=True,
            message=f"Blueprint '{blueprint_name}' exported in __init__.py",
            severity='INFO',
            check_name=self.name
        )]


class BlueprintDefinitionCheck(QualityCheck):
    """Check that Blueprint is actually defined in backend files"""
    
    @property
    def name(self) -> str:
        return "Blueprint Definition"
    
    def _do_check(self, context: ModuleContext) -> List[ValidationResult]:
        if not context.has_backend:
            return []
        
        backend_files = context.get_backend_files()
        blueprint_found = False
        
        for py_file in backend_files:
            if py_file.name == '__init__.py':
                continue
            
            content = context.read_file(py_file)
            if content and 'Blueprint(' in content:
                blueprint_found = True
                break
        
        if not blueprint_found:
            return [ValidationResult(
                passed=False,
                message="No Blueprint definition found in backend/",
                severity='ERROR',
                check_name=self.name
            )]
        
        return [ValidationResult(
            passed=True,
            message="Blueprint definition found",
            severity='INFO',
            check_name=self.name
        )]


class DependencyInjectionCheck(QualityCheck):
    """Check for DI violations (accessing internal implementation details)"""
    
    @property
    def name(self) -> str:
        return "Dependency Injection"
    
    def _do_check(self, context: ModuleContext) -> List[ValidationResult]:
        if not context.has_backend:
            return []
        
        violations = []
        
        for py_file in context.get_backend_files():
            content = context.read_file(py_file)
            if not content:
                continue
            
            # Check for .connection access
            if re.search(r'\.connection\s*\.', content):
                violations.append(f"{py_file.name}: Direct .connection access")
            
            # Check for .service access
            if re.search(r'\.service\s*\.', content):
                violations.append(f"{py_file.name}: Direct .service access")
            
            # Check for .db_path access (but not self.db_path)
            if re.search(r'(?<!self)\.db_path', content):
                violations.append(f"{py_file.name}: Direct .db_path access")
            
            # Check for hasattr() implementation checks
            if 'hasattr(' in content and 'connection' in content:
                violations.append(f"{py_file.name}: hasattr() implementation check")
        
        if violations:
            return [ValidationResult(
                passed=False,
                message=f"DI violations found: {'; '.join(violations)}",
                severity='ERROR',
                check_name=self.name
            )]
        
        return [ValidationResult(
            passed=True,
            message="No DI violations detected",
            severity='INFO',
            check_name=self.name
        )]


class InterfaceUsageCheck(QualityCheck):
    """Check if module uses interfaces"""
    
    @property
    def name(self) -> str:
        return "Interface Usage"
    
    def _do_check(self, context: ModuleContext) -> List[ValidationResult]:
        if not context.has_backend:
            return []
        
        uses_interfaces = False
        
        for py_file in context.get_backend_files():
            content = context.read_file(py_file)
            if content and 'from core.interfaces' in content:
                uses_interfaces = True
                break
        
        if uses_interfaces:
            return [ValidationResult(
                passed=True,
                message="Uses interfaces from core.interfaces",
                severity='INFO',
                check_name=self.name
            )]
        
        return [ValidationResult(
            passed=True,
            message="No interface usage detected (may be acceptable)",
            severity='WARNING',
            check_name=self.name
        )]


class DirectModuleImportsCheck(QualityCheck):
    """Check for direct imports of other modules (loose coupling)"""
    
    @property
    def name(self) -> str:
        return "Loose Coupling"
    
    def _do_check(self, context: ModuleContext) -> List[ValidationResult]:
        if not context.has_backend:
            return []
        
        violations = []
        
        for py_file in context.get_backend_files():
            content = context.read_file(py_file)
            if not content:
                continue
            
            # Check for direct module imports (excluding core)
            if re.search(r'from modules\.\w+\.backend import', content):
                if 'from modules.' in content and 'core' not in content:
                    violations.append(f"{py_file.name}: Direct module import")
        
        if violations:
            return [ValidationResult(
                passed=False,
                message=f"Direct module imports found: {'; '.join(violations)}",
                severity='ERROR',
                check_name=self.name
            )]
        
        return [ValidationResult(
            passed=True,
            message="No direct module imports (loose coupling maintained)",
            severity='INFO',
            check_name=self.name
        )]


class HardcodedPathsCheck(QualityCheck):
    """Check for hardcoded file paths"""
    
    @property
    def name(self) -> str:
        return "No Hardcoded Paths"
    
    def _do_check(self, context: ModuleContext) -> List[ValidationResult]:
        if not context.has_backend:
            return []
        
        violations = []
        
        for py_file in context.get_backend_files():
            content = context.read_file(py_file)
            if not content:
                continue
            
            # Look for hardcoded paths
            if re.search(r'["\']C:\\\\', content) or re.search(r'[\'"]/home/', content):
                violations.append(f"{py_file.name}: Hardcoded absolute path")
        
        if violations:
            return [ValidationResult(
                passed=False,
                message=f"Hardcoded paths found: {'; '.join(violations)}",
                severity='WARNING',
                check_name=self.name
            )]
        
        return [ValidationResult(
            passed=True,
            message="No hardcoded paths detected",
            severity='INFO',
            check_name=self.name
        )]


class ReadmeExistsCheck(QualityCheck):
    """Check that README.md exists"""
    
    @property
    def name(self) -> str:
        return "README Exists"
    
    def _do_check(self, context: ModuleContext) -> List[ValidationResult]:
        readme = context.module_path / 'README.md'
        
        if not readme.exists():
            return [ValidationResult(
                passed=False,
                message="No README.md (documentation required for API modules)",
                severity='WARNING',
                check_name=self.name
            )]
        
        return [ValidationResult(
            passed=True,
            message="README.md exists",
            severity='INFO',
            check_name=self.name
        )]


class SqlInjectionCheck(QualityCheck):
    """Check for SQL injection vulnerabilities"""
    
    @property
    def name(self) -> str:
        return "SQL Injection Prevention"
    
    def _do_check(self, context: ModuleContext) -> List[ValidationResult]:
        if not context.has_backend:
            return []
        
        violations = []
        
        for py_file in context.get_backend_files():
            content = context.read_file(py_file)
            if not content:
                continue
            
            # Check for string formatting in SQL
            if re.search(r'execute\(["\'].*%s', content) or \
               re.search(r'execute\(["\'].*\{', content) or \
               re.search(r'execute\(f["\']', content):
                violations.append(f"{py_file.name}: Potential SQL injection via string formatting")
            
            # Check for + concatenation in SQL
            if re.search(r'SELECT.*\+.*FROM', content, re.IGNORECASE):
                violations.append(f"{py_file.name}: SQL concatenation detected")
        
        if violations:
            return [ValidationResult(
                passed=False,
                message=f"SQL injection risks: {'; '.join(violations)}",
                severity='ERROR',
                check_name=self.name
            )]
        
        return [ValidationResult(
            passed=True,
            message="No SQL injection risks detected",
            severity='INFO',
            check_name=self.name
        )]


class ExceptionHandlingCheck(QualityCheck):
    """Check for proper exception handling"""
    
    @property
    def name(self) -> str:
        return "Exception Handling"
    
    def _do_check(self, context: ModuleContext) -> List[ValidationResult]:
        if not context.has_backend:
            return []
        
        issues = []
        
        for py_file in context.get_backend_files():
            content = context.read_file(py_file)
            if not content:
                continue
            
            # Check for bare except
            if re.search(r'except\s*:', content):
                issues.append(f"{py_file.name}: Bare 'except:' clause")
            
            # Check for pass in except
            if re.search(r'except.*:\s*pass', content):
                issues.append(f"{py_file.name}: Exception silently swallowed")
        
        if issues:
            return [ValidationResult(
                passed=False,
                message=f"Exception handling issues: {'; '.join(issues)}",
                severity='WARNING',
                check_name=self.name
            )]
        
        return [ValidationResult(
            passed=True,
            message="Exception handling follows best practices",
            severity='INFO',
            check_name=self.name
        )]


class SecretExposureCheck(QualityCheck):
    """Check for exposed secrets/credentials"""
    
    @property
    def name(self) -> str:
        return "Secret Exposure Prevention"
    
    def _do_check(self, context: ModuleContext) -> List[ValidationResult]:
        if not context.has_backend:
            return []
        
        violations = []
        
        for py_file in context.get_backend_files():
            content = context.read_file(py_file)
            if not content:
                continue
            
            # Check for hardcoded credentials
            if re.search(r'password\s*=\s*["\'][^"\']+["\']', content, re.IGNORECASE):
                violations.append(f"{py_file.name}: Hardcoded password")
            
            if re.search(r'api_key\s*=\s*["\'][^"\']+["\']', content, re.IGNORECASE):
                violations.append(f"{py_file.name}: Hardcoded API key")
            
            if re.search(r'secret\s*=\s*["\'][^"\']+["\']', content, re.IGNORECASE):
                violations.append(f"{py_file.name}: Hardcoded secret")
        
        if violations:
            return [ValidationResult(
                passed=False,
                message=f"Secret exposure risks: {'; '.join(violations)}",
                severity='ERROR',
                check_name=self.name
            )]
        
        return [ValidationResult(
            passed=True,
            message="No hardcoded secrets detected",
            severity='INFO',
            check_name=self.name
        )]


class TestCoverageCheck(QualityCheck):
    """Check if module has tests"""
    
    @property
    def name(self) -> str:
        return "Test Coverage"
    
    def _do_check(self, context: ModuleContext) -> List[ValidationResult]:
        tests_dir = context.module_path / 'tests'
        
        if not tests_dir.exists():
            return [ValidationResult(
                passed=False,
                message="No tests/ directory found (tests required for production)",
                severity='WARNING',
                check_name=self.name
            )]
        
        # Check for actual test files
        test_files = list(tests_dir.glob('test_*.py')) + list(tests_dir.glob('*_test.py'))
        
        if not test_files:
            return [ValidationResult(
                passed=False,
                message="tests/ directory exists but no test files found",
                severity='WARNING',
                check_name=self.name
            )]
        
        return [ValidationResult(
            passed=True,
            message=f"Tests present ({len(test_files)} test files)",
            severity='INFO',
            check_name=self.name
        )]


class LoggingPracticesCheck(QualityCheck):
    """Check for proper logging usage"""
    
    @property
    def name(self) -> str:
        return "Logging Practices"
    
    def _do_check(self, context: ModuleContext) -> List[ValidationResult]:
        if not context.has_backend:
            return []
        
        issues = []
        
        for py_file in context.get_backend_files():
            content = context.read_file(py_file)
            if not content:
                continue
            
            # Check for print() in production code
            if re.search(r'\bprint\(', content):
                issues.append(f"{py_file.name}: Using print() instead of logging")
        
        if issues:
            return [ValidationResult(
                passed=False,
                message=f"Logging issues: {'; '.join(issues)}",
                severity='WARNING',
                check_name=self.name
            )]
        
        return [ValidationResult(
            passed=True,
            message="Uses proper logging",
            severity='INFO',
            check_name=self.name
        )]


class InputValidationCheck(QualityCheck):
    """Check for input validation in API endpoints"""
    
    @property
    def name(self) -> str:
        return "Input Validation"
    
    def _do_check(self, context: ModuleContext) -> List[ValidationResult]:
        if not context.has_backend:
            return []
        
        has_endpoints = False
        has_validation = False
        
        for py_file in context.get_backend_files():
            content = context.read_file(py_file)
            if not content:
                continue
            
            # Check for Flask routes
            if '@' in content and 'route(' in content:
                has_endpoints = True
                
                # Check for validation patterns
                if 'request.get_json()' in content or 'request.args' in content:
                    if any(pattern in content for pattern in [
                        'if not', 'validate', 'schema', 'required',
                        'isinstance', 'ValueError', 'TypeError'
                    ]):
                        has_validation = True
        
        if has_endpoints and not has_validation:
            return [ValidationResult(
                passed=False,
                message="API endpoints found but no input validation detected",
                severity='WARNING',
                check_name=self.name
            )]
        
        if has_endpoints and has_validation:
            return [ValidationResult(
                passed=True,
                message="Input validation detected in API endpoints",
                severity='INFO',
                check_name=self.name
            )]
        
        return []  # No endpoints, check not applicable


# ============================================================================
# CHAIN BUILDER
# ============================================================================

def build_quality_check_chain() -> QualityCheck:
    """
    Build the complete quality check chain
    
    Returns:
        First check in the chain (all checks linked)
    """
    # Build chain from last to first (reverse order)
    chain = InputValidationCheck(None)
    chain = LoggingPracticesCheck(chain)
    chain = TestCoverageCheck(chain)
    chain = SecretExposureCheck(chain)
    chain = ExceptionHandlingCheck(chain)
    chain = SqlInjectionCheck(chain)
    chain = ReadmeExistsCheck(chain)
    chain = HardcodedPathsCheck(chain)
    chain = DirectModuleImportsCheck(chain)
    chain = InterfaceUsageCheck(chain)
    chain = DependencyInjectionCheck(chain)
    chain = BlueprintDefinitionCheck(chain)
    chain = BlueprintExportCheck(chain)
    chain = BlueprintConfigCheck(chain)
    chain = ModuleJsonValidCheck(chain)
    chain = ModuleJsonExistsCheck(chain)
    
    return chain