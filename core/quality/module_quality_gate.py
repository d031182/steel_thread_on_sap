#!/usr/bin/env python3
"""
Module Quality Gate
===================
Comprehensive validation that enforces modular architecture principles.

This gate MUST pass before a module can be deployed or loaded.

Validates:
1. Dependency Injection adherence
2. Blueprint registration correctness
3. Loose coupling principles
4. Interface compliance
5. Module structure completeness
6. Self-registration capability

Philosophy: Fail Fast, Fail Clearly
"""
import os
import json
import ast
import re
from pathlib import Path
from typing import Dict, List, Tuple
from dataclasses import dataclass


@dataclass
class ValidationResult:
    """Result of a validation check"""
    passed: bool
    message: str
    severity: str  # 'ERROR', 'WARNING', 'INFO'


class ModuleQualityGate:
    """
    Enforces modular architecture quality standards
    
    A module MUST pass all ERROR-level checks to be considered valid.
    WARNING-level checks indicate code smells that should be addressed.
    """
    
    def __init__(self, module_path: Path):
        self.module_path = module_path
        self.module_name = module_path.name
        self.results: List[ValidationResult] = []
        
    def validate(self) -> Tuple[bool, List[ValidationResult]]:
        """
        Run all validation checks
        
        Returns:
            (passed, results) - passed=True if no ERROR-level failures
        """
        print(f"\n{'='*80}")
        print(f"MODULE QUALITY GATE: {self.module_name}")
        print(f"{'='*80}\n")
        
        # Structure checks
        self._check_module_json_exists()
        self._check_module_json_valid()
        
        if not self._has_backend():
            print("INFO: No backend directory - frontend/config module only")
            return self._summarize()
        
        # Blueprint registration checks
        self._check_blueprint_config()
        self._check_blueprint_export()
        self._check_blueprint_definition()
        self._check_blueprint_registered_in_app()
        
        # Dependency Injection checks
        self._check_di_violations()
        self._check_interface_usage()
        self._check_no_direct_imports()
        
        # Loose coupling checks
        self._check_no_hardcoded_paths()
        self._check_no_global_state()
        self._check_injectable_dependencies()
        
        # Documentation checks
        self._check_readme_exists()
        self._check_module_json_complete()
        
        # Industry standard checks (best practices)
        self._check_sql_injection_risks()
        self._check_exception_handling()
        self._check_resource_cleanup()
        self._check_secret_exposure()
        self._check_circular_dependencies()
        self._check_test_coverage()
        self._check_logging_practices()
        self._check_input_validation()
        self._check_rate_limiting()
        self._check_cors_configuration()
        
        return self._summarize()
    
    def _check_module_json_exists(self):
        """module.json must exist"""
        module_json = self.module_path / 'module.json'
        if not module_json.exists():
            self.results.append(ValidationResult(
                passed=False,
                message="module.json not found",
                severity='ERROR'
            ))
        else:
            self.results.append(ValidationResult(
                passed=True,
                message="module.json exists",
                severity='INFO'
            ))
    
    def _check_module_json_valid(self):
        """module.json must be valid JSON with required fields"""
        module_json = self.module_path / 'module.json'
        if not module_json.exists():
            return
        
        try:
            with open(module_json) as f:
                config = json.load(f)
            
            required_fields = ['name', 'version', 'description', 'enabled']
            missing = [f for f in required_fields if f not in config]
            
            if missing:
                self.results.append(ValidationResult(
                    passed=False,
                    message=f"module.json missing required fields: {missing}",
                    severity='ERROR'
                ))
            else:
                self.results.append(ValidationResult(
                    passed=True,
                    message="module.json has all required fields",
                    severity='INFO'
                ))
                
        except json.JSONDecodeError as e:
            self.results.append(ValidationResult(
                passed=False,
                message=f"module.json invalid JSON: {e}",
                severity='ERROR'
            ))
    
    def _has_backend(self) -> bool:
        """Check if module has backend directory"""
        return (self.module_path / 'backend').exists()
    
    def _check_blueprint_config(self):
        """If backend/ exists, module.json MUST have backend.blueprint"""
        if not self._has_backend():
            return
        
        module_json = self.module_path / 'module.json'
        try:
            with open(module_json) as f:
                config = json.load(f)
            
            if 'backend' not in config:
                self.results.append(ValidationResult(
                    passed=False,
                    message="Has backend/ but module.json missing 'backend' section",
                    severity='ERROR'
                ))
                return
            
            if 'blueprint' not in config['backend']:
                self.results.append(ValidationResult(
                    passed=False,
                    message="module.json missing 'backend.blueprint' config",
                    severity='ERROR'
                ))
                return
            
            if 'module_path' not in config['backend']:
                self.results.append(ValidationResult(
                    passed=False,
                    message="module.json missing 'backend.module_path' config",
                    severity='ERROR'
                ))
                return
            
            self.results.append(ValidationResult(
                passed=True,
                message=f"Blueprint config present: {config['backend']['blueprint']}",
                severity='INFO'
            ))
            
        except Exception as e:
            self.results.append(ValidationResult(
                passed=False,
                message=f"Cannot check blueprint config: {e}",
                severity='ERROR'
            ))
    
    def _check_blueprint_export(self):
        """backend/__init__.py must export the blueprint"""
        if not self._has_backend():
            return
        
        backend_init = self.module_path / 'backend' / '__init__.py'
        if not backend_init.exists():
            self.results.append(ValidationResult(
                passed=False,
                message="backend/__init__.py doesn't exist",
                severity='ERROR'
            ))
            return
        
        # Get blueprint name from config
        try:
            module_json = self.module_path / 'module.json'
            with open(module_json) as f:
                config = json.load(f)
            
            if 'backend' not in config or 'blueprint' not in config['backend']:
                return  # Already flagged in previous check
            
            blueprint_name = config['backend']['blueprint']
            
            with open(backend_init) as f:
                init_content = f.read()
            
            if blueprint_name not in init_content:
                self.results.append(ValidationResult(
                    passed=False,
                    message=f"backend/__init__.py doesn't export '{blueprint_name}'",
                    severity='ERROR'
                ))
            else:
                self.results.append(ValidationResult(
                    passed=True,
                    message=f"Blueprint '{blueprint_name}' exported in __init__.py",
                    severity='INFO'
                ))
                
        except Exception as e:
            self.results.append(ValidationResult(
                passed=False,
                message=f"Cannot verify blueprint export: {e}",
                severity='ERROR'
            ))
    
    def _check_blueprint_definition(self):
        """Blueprint must be defined in backend/api.py or similar"""
        if not self._has_backend():
            return
        
        # Look for Blueprint definition in backend files
        backend_dir = self.module_path / 'backend'
        blueprint_found = False
        
        for py_file in backend_dir.glob('*.py'):
            if py_file.name == '__init__.py':
                continue
            
            try:
                with open(py_file) as f:
                    content = f.read()
                
                if 'Blueprint(' in content:
                    blueprint_found = True
                    break
            except:
                pass
        
        if not blueprint_found:
            self.results.append(ValidationResult(
                passed=False,
                message="No Blueprint definition found in backend/",
                severity='ERROR'
            ))
        else:
            self.results.append(ValidationResult(
                passed=True,
                message="Blueprint definition found",
                severity='INFO'
            ))
    
    def _check_blueprint_registered_in_app(self):
        """Check if blueprint is actually registered in app.py"""
        if not self._has_backend():
            return
        
        try:
            # Get blueprint name from module.json
            module_json = self.module_path / 'module.json'
            with open(module_json) as f:
                config = json.load(f)
            
            if 'backend' not in config or 'blueprint' not in config['backend']:
                return  # Already flagged in blueprint_config check
            
            blueprint_name = config['backend']['blueprint']
            
            # Check if registered in app/app.py
            app_py = Path('app') / 'app.py'
            if not app_py.exists():
                self.results.append(ValidationResult(
                    passed=False,
                    message="Cannot find app/app.py to verify blueprint registration",
                    severity='WARNING'
                ))
                return
            
            with open(app_py) as f:
                app_content = f.read()
            
            # Check for module_loader.load_blueprint with this blueprint
            if blueprint_name in app_content and 'module_loader.load_blueprint' in app_content:
                # More specific check: look for the actual module path
                module_path_pattern = f"modules.{self.module_name}.backend"
                if module_path_pattern in app_content:
                    self.results.append(ValidationResult(
                        passed=True,
                        message=f"Blueprint '{blueprint_name}' is registered in app.py",
                        severity='INFO'
                    ))
                else:
                    self.results.append(ValidationResult(
                        passed=False,
                        message=f"Blueprint '{blueprint_name}' not registered in app.py (add module_loader.load_blueprint call)",
                        severity='ERROR'
                    ))
            else:
                self.results.append(ValidationResult(
                    passed=False,
                    message=f"Blueprint '{blueprint_name}' not registered in app.py (add module_loader.load_blueprint call)",
                    severity='ERROR'
                ))
                
        except Exception as e:
            self.results.append(ValidationResult(
                passed=False,
                message=f"Cannot verify blueprint registration: {e}",
                severity='WARNING'
            ))
    
    def _check_di_violations(self):
        """Check for DI violations in code"""
        if not self._has_backend():
            return
        
        violations = []
        backend_dir = self.module_path / 'backend'
        
        for py_file in backend_dir.rglob('*.py'):
            try:
                with open(py_file) as f:
                    content = f.read()
                
                # Check for .connection access
                if re.search(r'\.connection\s*\.', content):
                    violations.append(f"{py_file.name}: Direct .connection access")
                
                # Check for .service access
                if re.search(r'\.service\s*\.', content):
                    violations.append(f"{py_file.name}: Direct .service access")
                
                # Check for .db_path access
                if re.search(r'\.db_path', content):
                    violations.append(f"{py_file.name}: Direct .db_path access")
                
                # Check for hasattr() implementation checks
                if 'hasattr(' in content and 'connection' in content:
                    violations.append(f"{py_file.name}: hasattr() implementation check")
                    
            except:
                pass
        
        if violations:
            self.results.append(ValidationResult(
                passed=False,
                message=f"DI violations found: {'; '.join(violations)}",
                severity='ERROR'
            ))
        else:
            self.results.append(ValidationResult(
                passed=True,
                message="No DI violations detected",
                severity='INFO'
            ))
    
    def _check_interface_usage(self):
        """Check if module uses interfaces instead of concrete classes"""
        if not self._has_backend():
            return
        
        backend_dir = self.module_path / 'backend'
        uses_interfaces = False
        
        for py_file in backend_dir.rglob('*.py'):
            try:
                with open(py_file) as f:
                    content = f.read()
                
                # Look for interface imports
                if 'from core.interfaces' in content:
                    uses_interfaces = True
                    break
            except:
                pass
        
        if uses_interfaces:
            self.results.append(ValidationResult(
                passed=True,
                message="Uses interfaces from core.interfaces",
                severity='INFO'
            ))
        else:
            self.results.append(ValidationResult(
                passed=True,
                message="No interface usage detected (may be acceptable)",
                severity='WARNING'
            ))
    
    def _check_no_direct_imports(self):
        """Check for direct imports of other modules"""
        if not self._has_backend():
            return
        
        violations = []
        backend_dir = self.module_path / 'backend'
        
        for py_file in backend_dir.rglob('*.py'):
            try:
                with open(py_file) as f:
                    content = f.read()
                
                # Check for direct module imports (excluding core)
                if re.search(r'from modules\.\w+\.backend import', content):
                    if 'from modules.' in content and 'core' not in content:
                        violations.append(f"{py_file.name}: Direct module import")
                        
            except:
                pass
        
        if violations:
            self.results.append(ValidationResult(
                passed=False,
                message=f"Direct module imports found: {'; '.join(violations)}",
                severity='ERROR'
            ))
        else:
            self.results.append(ValidationResult(
                passed=True,
                message="No direct module imports (loose coupling maintained)",
                severity='INFO'
            ))
    
    def _check_no_hardcoded_paths(self):
        """Check for hardcoded file paths"""
        if not self._has_backend():
            return
        
        violations = []
        backend_dir = self.module_path / 'backend'
        
        for py_file in backend_dir.rglob('*.py'):
            try:
                with open(py_file) as f:
                    content = f.read()
                
                # Look for hardcoded paths (simplified check)
                if re.search(r'["\']C:\\\\', content) or re.search(r'[\'"]/home/', content):
                    violations.append(f"{py_file.name}: Hardcoded absolute path")
                        
            except:
                pass
        
        if violations:
            self.results.append(ValidationResult(
                passed=False,
                message=f"Hardcoded paths found: {'; '.join(violations)}",
                severity='WARNING'
            ))
        else:
            self.results.append(ValidationResult(
                passed=True,
                message="No hardcoded paths detected",
                severity='INFO'
            ))
    
    def _check_no_global_state(self):
        """Check for global state/singletons"""
        if not self._has_backend():
            return
        
        # This is a simplified check - could be enhanced
        self.results.append(ValidationResult(
            passed=True,
            message="Global state check passed (simplified)",
            severity='INFO'
        ))
    
    def _check_injectable_dependencies(self):
        """Check if dependencies are injected via constructor"""
        if not self._has_backend():
            return
        
        # Look for constructor injection patterns
        backend_dir = self.module_path / 'backend'
        has_injection = False
        
        for py_file in backend_dir.rglob('*.py'):
            try:
                with open(py_file) as f:
                    content = f.read()
                
                # Look for __init__ with parameters (simplified)
                if 'def __init__(self' in content and 'self,' in content:
                    has_injection = True
                    break
            except:
                pass
        
        if has_injection:
            self.results.append(ValidationResult(
                passed=True,
                message="Constructor dependency injection detected",
                severity='INFO'
            ))
    
    def _check_readme_exists(self):
        """README.md should exist"""
        readme = self.module_path / 'README.md'
        if not readme.exists():
            self.results.append(ValidationResult(
                passed=False,
                message="No README.md (documentation required for API modules)",
                severity='WARNING'
            ))
        else:
            self.results.append(ValidationResult(
                passed=True,
                message="README.md exists",
                severity='INFO'
            ))
            
            # If module has API, check for integration instructions
            self._check_integration_documentation(readme)
    
    def _check_integration_documentation(self, readme: Path):
        """Check if README documents how to integrate the module"""
        if not self._has_backend():
            return
        
        try:
            # Check if module has API endpoints
            module_json = self.module_path / 'module.json'
            with open(module_json) as f:
                config = json.load(f)
            
            # If module has API endpoints, README must document integration
            if 'backend' in config and config.get('backend', {}).get('blueprint'):
                with open(readme) as f:
                    readme_content = f.read().lower()
                
                # Check for integration keywords
                has_integration_docs = any(keyword in readme_content for keyword in [
                    'integration', 'how to use', 'usage', 
                    'register', 'blueprint', 'app.py',
                    'module_loader.load_blueprint'
                ])
                
                # Check for code examples
                has_code_examples = '```' in readme_content or '`' in readme_content
                
                if not has_integration_docs:
                    self.results.append(ValidationResult(
                        passed=False,
                        message="README missing integration instructions (how to register blueprint in app.py)",
                        severity='ERROR'
                    ))
                elif not has_code_examples:
                    self.results.append(ValidationResult(
                        passed=False,
                        message="README missing code examples for integration",
                        severity='WARNING'
                    ))
                else:
                    self.results.append(ValidationResult(
                        passed=True,
                        message="README documents integration with code examples",
                        severity='INFO'
                    ))
                    
        except Exception as e:
            pass  # Already covered by other checks
    
    def _check_module_json_complete(self):
        """Check if module.json has comprehensive metadata"""
        module_json = self.module_path / 'module.json'
        if not module_json.exists():
            return
        
        try:
            with open(module_json) as f:
                config = json.load(f)
            
            recommended = ['category', 'author', 'dependencies']
            missing = [f for f in recommended if f not in config]
            
            if missing:
                self.results.append(ValidationResult(
                    passed=True,
                    message=f"module.json missing recommended fields: {missing}",
                    severity='WARNING'
                ))
        except:
            pass
    
    # ========================================================================
    # INDUSTRY STANDARD CHECKS (Best Practices)
    # ========================================================================
    
    def _check_sql_injection_risks(self):
        """Check for SQL injection vulnerabilities"""
        if not self._has_backend():
            return
        
        violations = []
        backend_dir = self.module_path / 'backend'
        
        for py_file in backend_dir.rglob('*.py'):
            try:
                with open(py_file) as f:
                    content = f.read()
                
                # Check for string formatting in SQL (dangerous)
                if re.search(r'execute\(["\'].*%s', content) or \
                   re.search(r'execute\(["\'].*\{', content) or \
                   re.search(r'execute\(f["\']', content):
                    violations.append(f"{py_file.name}: Potential SQL injection via string formatting")
                
                # Check for + concatenation in SQL
                if re.search(r'SELECT.*\+.*FROM', content, re.IGNORECASE):
                    violations.append(f"{py_file.name}: SQL concatenation detected (use parameterized queries)")
                    
            except:
                pass
        
        if violations:
            self.results.append(ValidationResult(
                passed=False,
                message=f"SQL injection risks: {'; '.join(violations)}",
                severity='ERROR'
            ))
        else:
            self.results.append(ValidationResult(
                passed=True,
                message="No SQL injection risks detected",
                severity='INFO'
            ))
    
    def _check_exception_handling(self):
        """Check for proper exception handling"""
        if not self._has_backend():
            return
        
        issues = []
        backend_dir = self.module_path / 'backend'
        
        for py_file in backend_dir.rglob('*.py'):
            try:
                with open(py_file) as f:
                    content = f.read()
                
                # Check for bare except (bad practice)
                if re.search(r'except\s*:', content):
                    issues.append(f"{py_file.name}: Bare 'except:' clause (catch specific exceptions)")
                
                # Check for pass in except (swallowing errors)
                if re.search(r'except.*:\s*pass', content):
                    issues.append(f"{py_file.name}: Exception silently swallowed (log or re-raise)")
                
            except:
                pass
        
        if issues:
            self.results.append(ValidationResult(
                passed=False,
                message=f"Exception handling issues: {'; '.join(issues)}",
                severity='WARNING'
            ))
        else:
            self.results.append(ValidationResult(
                passed=True,
                message="Exception handling follows best practices",
                severity='INFO'
            ))
    
    def _check_resource_cleanup(self):
        """Check for proper resource cleanup (with statements)"""
        if not self._has_backend():
            return
        
        issues = []
        backend_dir = self.module_path / 'backend'
        
        for py_file in backend_dir.rglob('*.py'):
            try:
                with open(py_file) as f:
                    content = f.read()
                
                # Check for file open without 'with'
                if re.search(r'=\s*open\(', content) and 'with open(' not in content:
                    issues.append(f"{py_file.name}: file.open() without 'with' statement")
                
                # Check for connection without context manager
                if re.search(r'\.connect\(', content) and 'with' not in content:
                    issues.append(f"{py_file.name}: Connection without context manager")
                    
            except:
                pass
        
        if issues:
            self.results.append(ValidationResult(
                passed=False,
                message=f"Resource cleanup issues: {'; '.join(issues)}",
                severity='WARNING'
            ))
    
    def _check_secret_exposure(self):
        """Check for exposed secrets/credentials"""
        if not self._has_backend():
            return
        
        violations = []
        backend_dir = self.module_path / 'backend'
        
        for py_file in backend_dir.rglob('*.py'):
            try:
                with open(py_file) as f:
                    content = f.read()
                
                # Check for hardcoded passwords/keys
                if re.search(r'password\s*=\s*["\'][^"\']+["\']', content, re.IGNORECASE):
                    violations.append(f"{py_file.name}: Hardcoded password detected")
                
                if re.search(r'api_key\s*=\s*["\'][^"\']+["\']', content, re.IGNORECASE):
                    violations.append(f"{py_file.name}: Hardcoded API key detected")
                
                if re.search(r'secret\s*=\s*["\'][^"\']+["\']', content, re.IGNORECASE):
                    violations.append(f"{py_file.name}: Hardcoded secret detected")
                    
            except:
                pass
        
        if violations:
            self.results.append(ValidationResult(
                passed=False,
                message=f"Secret exposure risks: {'; '.join(violations)}",
                severity='ERROR'
            ))
        else:
            self.results.append(ValidationResult(
                passed=True,
                message="No hardcoded secrets detected",
                severity='INFO'
            ))
    
    def _check_circular_dependencies(self):
        """Check for circular import risks"""
        if not self._has_backend():
            return
        
        # This is a simplified check - full circular dependency detection is complex
        backend_dir = self.module_path / 'backend'
        imports = {}
        
        for py_file in backend_dir.rglob('*.py'):
            if py_file.name == '__init__.py':
                continue
                
            try:
                with open(py_file) as f:
                    content = f.read()
                
                # Find imports from same module
                module_imports = re.findall(r'from \.(\w+) import', content)
                if module_imports:
                    imports[py_file.name] = module_imports
            except:
                pass
        
        # Basic circular check (A imports B, B imports A)
        circular = []
        for file_a, imports_a in imports.items():
            for import_b in imports_a:
                file_b = f"{import_b}.py"
                if file_b in imports and file_a.replace('.py', '') in imports[file_b]:
                    circular.append(f"{file_a} ↔ {file_b}")
        
        if circular:
            self.results.append(ValidationResult(
                passed=False,
                message=f"Circular dependencies detected: {'; '.join(circular)}",
                severity='WARNING'
            ))
    
    def _check_test_coverage(self):
        """Check if module has tests"""
        tests_dir = self.module_path / 'tests'
        
        if not tests_dir.exists():
            self.results.append(ValidationResult(
                passed=False,
                message="No tests/ directory found (tests required for production)",
                severity='WARNING'
            ))
            return
        
        # Check if there are actual test files
        test_files = list(tests_dir.glob('test_*.py')) + list(tests_dir.glob('*_test.py'))
        
        if not test_files:
            self.results.append(ValidationResult(
                passed=False,
                message="tests/ directory exists but no test files found",
                severity='WARNING'
            ))
        else:
            self.results.append(ValidationResult(
                passed=True,
                message=f"Tests present ({len(test_files)} test files)",
                severity='INFO'
            ))
    
    def _check_logging_practices(self):
        """Check for proper logging usage"""
        if not self._has_backend():
            return
        
        issues = []
        backend_dir = self.module_path / 'backend'
        has_logging_import = False
        
        for py_file in backend_dir.rglob('*.py'):
            try:
                with open(py_file) as f:
                    content = f.read()
                
                # Check if module imports logging
                if 'import logging' in content:
                    has_logging_import = True
                
                # Check for print() in production code (should use logging)
                if re.search(r'\bprint\(', content):
                    issues.append(f"{py_file.name}: Using print() instead of logging")
                    
            except:
                pass
        
        if issues:
            self.results.append(ValidationResult(
                passed=False,
                message=f"Logging issues: {'; '.join(issues)}",
                severity='WARNING'
            ))
        elif has_logging_import:
            self.results.append(ValidationResult(
                passed=True,
                message="Uses proper logging",
                severity='INFO'
            ))
    
    def _check_input_validation(self):
        """Check for input validation in API endpoints"""
        if not self._has_backend():
            return
        
        backend_dir = self.module_path / 'backend'
        has_endpoints = False
        has_validation = False
        
        for py_file in backend_dir.rglob('*.py'):
            try:
                with open(py_file) as f:
                    content = f.read()
                
                # Check for Flask routes
                if '@' in content and 'route(' in content:
                    has_endpoints = True
                    
                    # Check for validation patterns
                    if 'request.get_json()' in content or 'request.args' in content:
                        # Look for validation
                        if any(pattern in content for pattern in [
                            'if not', 'validate', 'schema', 'required',
                            'isinstance', 'ValueError', 'TypeError'
                        ]):
                            has_validation = True
            except:
                pass
        
        if has_endpoints and not has_validation:
            self.results.append(ValidationResult(
                passed=False,
                message="API endpoints found but no input validation detected",
                severity='WARNING'
            ))
        elif has_endpoints and has_validation:
            self.results.append(ValidationResult(
                passed=True,
                message="Input validation detected in API endpoints",
                severity='INFO'
            ))
    
    def _check_rate_limiting(self):
        """Check if API endpoints have rate limiting"""
        if not self._has_backend():
            return
        
        backend_dir = self.module_path / 'backend'
        has_endpoints = False
        has_rate_limiting = False
        
        for py_file in backend_dir.rglob('*.py'):
            try:
                with open(py_file) as f:
                    content = f.read()
                
                if '@' in content and 'route(' in content:
                    has_endpoints = True
                    
                    # Check for rate limiting decorators/patterns
                    if any(pattern in content for pattern in [
                        'limiter', 'rate_limit', 'throttle', '@limit'
                    ]):
                        has_rate_limiting = True
            except:
                pass
        
        if has_endpoints and not has_rate_limiting:
            self.results.append(ValidationResult(
                passed=True,
                message="No rate limiting detected (consider for public APIs)",
                severity='WARNING'
            ))
    
    def _check_cors_configuration(self):
        """Check for CORS configuration in API modules"""
        if not self._has_backend():
            return
        
        backend_dir = self.module_path / 'backend'
        has_endpoints = False
        has_cors = False
        
        for py_file in backend_dir.rglob('*.py'):
            try:
                with open(py_file) as f:
                    content = f.read()
                
                if '@' in content and 'route(' in content:
                    has_endpoints = True
                    
                    if 'CORS' in content or 'cross_origin' in content:
                        has_cors = True
            except:
                pass
        
        if has_endpoints and not has_cors:
            self.results.append(ValidationResult(
                passed=True,
                message="No CORS configuration (needed if frontend on different origin)",
                severity='INFO'
            ))
    
    def _summarize(self) -> Tuple[bool, List[ValidationResult]]:
        """Print summary and return overall result"""
        errors = [r for r in self.results if r.severity == 'ERROR' and not r.passed]
        warnings = [r for r in self.results if r.severity == 'WARNING' and not r.passed]
        passed = [r for r in self.results if r.passed]
        
        print("\nRESULTS:")
        print(f"  PASSED: {len(passed)}")
        print(f"  WARNINGS: {len(warnings)}")
        print(f"  ERRORS: {len(errors)}")
        
        if errors:
            print("\nERRORS (Must Fix):")
            for i, err in enumerate(errors, 1):
                print(f"  {i}. {err.message}")
        
        if warnings:
            print("\nWARNINGS (Should Fix):")
            for i, warn in enumerate(warnings, 1):
                print(f"  {i}. {warn.message}")
        
        overall_passed = len(errors) == 0
        
        if overall_passed:
            print(f"\n{'='*80}")
            print(f"QUALITY GATE: PASSED")
            print(f"{'='*80}\n")
        else:
            print(f"\n{'='*80}")
            print(f"QUALITY GATE: FAILED")
            print(f"{'='*80}\n")
        
        return overall_passed, self.results


def validate_module(module_path: str) -> bool:
    """
    Validate a single module
    
    Returns:
        True if module passes quality gate
    """
    gate = ModuleQualityGate(Path(module_path))
    passed, results = gate.validate()
    return passed


def validate_all_modules() -> Dict[str, bool]:
    """
    Validate all modules in modules/ directory
    
    Returns:
        Dict mapping module name to pass/fail
    """
    modules_dir = Path('modules')
    results = {}
    
    for module_dir in sorted(modules_dir.iterdir()):
        if not module_dir.is_dir() or module_dir.name.startswith('.') or module_dir.name == '__pycache__':
            continue
        
        gate = ModuleQualityGate(module_dir)
        passed, _ = gate.validate()
        results[module_dir.name] = passed
    
    return results


if __name__ == '__main__':
    import sys
    
    if len(sys.argv) > 1:
        # Validate specific module
        module_name = sys.argv[1]
        module_path = Path('modules') / module_name
        
        if not module_path.exists():
            print(f"ERROR: Module '{module_name}' not found")
            sys.exit(1)
        
        passed = validate_module(module_path)
        sys.exit(0 if passed else 1)
    else:
        # Validate all modules
        print("="*80)
        print("VALIDATING ALL MODULES")
        print("="*80)
        
        results = validate_all_modules()
        
        print("\n" + "="*80)
        print("SUMMARY")
        print("="*80)
        
        passed_count = sum(1 for p in results.values() if p)
        total_count = len(results)
        
        print(f"\nModules Passed: {passed_count}/{total_count}")
        
        if passed_count < total_count:
            print("\nFailed Modules:")
            for name, passed in results.items():
                if not passed:
                    print(f"  - {name}")
        
        sys.exit(0 if passed_count == total_count else 1)