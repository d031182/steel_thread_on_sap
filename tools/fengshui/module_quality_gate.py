"""
Feng Shui Phase 4.15: Module Quality Gate

Purpose:
    Validates module compliance with architecture standards before deployment.
    Enforces ALL modular architecture principles from .clinerules section 5.

Validation Rules:
    ✅ Module structure completeness (module.json, backend/, tests/, README.md)
    ✅ Blueprint registration (module.json defines backend.blueprint)
    ✅ No DI violations (.connection, .service, .db_path direct access)
    ✅ Interface compliance (uses core.interfaces)
    ✅ Loose coupling (no direct module imports)

Exit Codes:
    0 = PASSED (all validations passed, module ready for deployment)
    1 = FAILED (critical violations found, module cannot be deployed)

Usage:
    python tools/fengshui/module_quality_gate.py [module_name]
    
Example:
    python tools/fengshui/module_quality_gate.py knowledge_graph
    # Output: PASSED/FAILED + detailed validation report
"""

import sys
import json
import re
from pathlib import Path
from typing import Dict, List, Tuple, Any
from dataclasses import dataclass, field


@dataclass
class ValidationResult:
    """Result of a single validation check"""
    passed: bool
    score: float  # 0.0 to 1.0
    issues: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    details: Dict[str, Any] = field(default_factory=dict)


class ModuleQualityGate:
    """
    Module Quality Gate - Phase 4.15
    
    Validates module architecture compliance with these critical rules:
    1. Complete module structure (all required files/directories)
    2. Blueprint self-registration (module.json + api.py)
    3. Zero DI violations (no .connection, .service, .db_path access)
    4. Interface usage (core.interfaces for abstractions)
    5. Loose coupling (no direct module imports)
    """
    
    # Validation weights (sum to 1.0)
    WEIGHTS = {
        'structure': 0.25,      # Module structure completeness
        'blueprint': 0.20,      # Blueprint registration
        'di_compliance': 0.30,  # DI violation check (CRITICAL)
        'interface_usage': 0.15, # Interface compliance
        'coupling': 0.10        # Loose coupling check
    }
    
    # DI violation patterns (from .clinerules)
    DI_VIOLATIONS = [
        r'self\.connection\b',
        r'self\.service\b',
        r'self\.db_path\b',
        r'app\.connection\b',
        r'direct_access\.\w+\.connection',
    ]
    
    # Required module files
    REQUIRED_FILES = [
        'module.json',
        'backend/__init__.py',
        'README.md'
    ]
    
    # Optional but recommended files
    RECOMMENDED_FILES = [
        'backend/api.py',
        'backend/service.py',
        'tests/',
        'docs/'
    ]
    
    def __init__(self):
        self.results = {}
        self.overall_score = 0.0
        self.critical_issues = []
    
    def validate(self, module_path: Path) -> Dict[str, Any]:
        """
        Run complete quality gate validation on a module
        
        Args:
            module_path: Path to module directory (e.g., modules/knowledge_graph)
            
        Returns:
            Dict with validation results and overall score
        """
        if not module_path.exists():
            return {
                'passed': False,
                'overall_score': 0.0,
                'error': f'Module not found: {module_path}'
            }
        
        print(f"\n{'='*60}")
        print(f"Feng Shui Phase 4.15: Module Quality Gate")
        print(f"Module: {module_path.name}")
        print(f"{'='*60}\n")
        
        # Run all validations
        self.results['structure'] = self._validate_structure(module_path)
        self.results['blueprint'] = self._validate_blueprint(module_path)
        self.results['di_compliance'] = self._validate_di_compliance(module_path)
        self.results['interface_usage'] = self._validate_interface_usage(module_path)
        self.results['coupling'] = self._validate_coupling(module_path)
        
        # Calculate overall score
        self.overall_score = self._calculate_overall_score()
        
        # Determine pass/fail
        passed = self.overall_score >= 0.7 and len(self.critical_issues) == 0
        
        # Print report
        self._print_report(passed)
        
        return {
            'passed': passed,
            'overall_score': self.overall_score,
            'results': self.results,
            'critical_issues': self.critical_issues
        }
    
    def _validate_structure(self, module_path: Path) -> ValidationResult:
        """Validate module structure completeness"""
        issues = []
        warnings = []
        missing_required = []
        missing_recommended = []
        
        # Check required files
        for file_path in self.REQUIRED_FILES:
            full_path = module_path / file_path
            if not full_path.exists():
                missing_required.append(file_path)
                issues.append(f"REQUIRED: Missing {file_path}")
        
        # Check recommended files
        for file_path in self.RECOMMENDED_FILES:
            full_path = module_path / file_path
            if not full_path.exists():
                missing_recommended.append(file_path)
                warnings.append(f"RECOMMENDED: Missing {file_path}")
        
        # Calculate score
        total_files = len(self.REQUIRED_FILES) + len(self.RECOMMENDED_FILES)
        present_files = total_files - len(missing_required) - len(missing_recommended)
        score = present_files / total_files
        
        # Critical if required files missing
        if missing_required:
            self.critical_issues.extend(issues)
        
        passed = len(missing_required) == 0
        
        return ValidationResult(
            passed=passed,
            score=score,
            issues=issues,
            warnings=warnings,
            details={
                'missing_required': missing_required,
                'missing_recommended': missing_recommended
            }
        )
    
    def _validate_blueprint(self, module_path: Path) -> ValidationResult:
        """Validate blueprint registration in module.json and api.py"""
        issues = []
        warnings = []
        
        module_json_path = module_path / 'module.json'
        api_py_path = module_path / 'backend' / 'api.py'
        
        # Check if module.json exists
        if not module_json_path.exists():
            return ValidationResult(
                passed=False,
                score=0.0,
                issues=['module.json not found - cannot validate blueprint'],
                warnings=[]
            )
        
        # Load module.json
        try:
            with open(module_json_path, 'r', encoding='utf-8') as f:
                module_config = json.load(f)
        except Exception as e:
            return ValidationResult(
                passed=False,
                score=0.0,
                issues=[f'Failed to parse module.json: {e}'],
                warnings=[]
            )
        
        # Check if backend.blueprint is defined
        blueprint_defined = False
        backend_config = module_config.get('backend', {})
        
        if 'blueprint' in backend_config:
            blueprint_defined = True
            blueprint_path = backend_config['blueprint']
        else:
            issues.append('CRITICAL: module.json missing backend.blueprint field')
            self.critical_issues.append('Missing blueprint registration in module.json')
        
        # Check if api.py exports blueprint
        blueprint_exported = False
        if api_py_path.exists() and blueprint_defined:
            try:
                with open(api_py_path, 'r', encoding='utf-8') as f:
                    api_content = f.read()
                
                # Look for blueprint definition
                if re.search(r'blueprint\s*=\s*Blueprint\(', api_content):
                    blueprint_exported = True
                else:
                    issues.append('CRITICAL: api.py does not define Blueprint()')
                    self.critical_issues.append('Blueprint not defined in api.py')
            except Exception as e:
                warnings.append(f'Could not read api.py: {e}')
        elif not api_py_path.exists() and blueprint_defined:
            issues.append('CRITICAL: module.json references blueprint but api.py not found')
            self.critical_issues.append('api.py missing but blueprint configured')
        
        # Calculate score
        score = 0.0
        if blueprint_defined:
            score += 0.5
        if blueprint_exported:
            score += 0.5
        
        passed = blueprint_defined and blueprint_exported
        
        return ValidationResult(
            passed=passed,
            score=score,
            issues=issues,
            warnings=warnings,
            details={
                'blueprint_defined': blueprint_defined,
                'blueprint_exported': blueprint_exported
            }
        )
    
    def _validate_di_compliance(self, module_path: Path) -> ValidationResult:
        """Validate no DI violations (critical check)"""
        issues = []
        warnings = []
        violations = []
        
        backend_path = module_path / 'backend'
        
        if not backend_path.exists():
            return ValidationResult(
                passed=True,
                score=1.0,
                issues=[],
                warnings=['No backend/ directory - skipping DI check']
            )
        
        # Scan all Python files in backend/
        for py_file in backend_path.rglob('*.py'):
            if py_file.name == '__init__.py':
                continue
            
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Check for DI violations
                for pattern in self.DI_VIOLATIONS:
                    matches = re.finditer(pattern, content)
                    for match in matches:
                        line_num = content[:match.start()].count('\n') + 1
                        violations.append({
                            'file': py_file.relative_to(module_path),
                            'line': line_num,
                            'pattern': pattern,
                            'code': content[match.start():match.end()]
                        })
                        
            except Exception as e:
                warnings.append(f'Could not scan {py_file.name}: {e}')
        
        # Report violations
        for v in violations:
            issue = f"DI VIOLATION: {v['file']}:{v['line']} - {v['code']}"
            issues.append(issue)
            self.critical_issues.append(issue)
        
        # Calculate score (DI compliance is binary - 0 violations or fail)
        score = 1.0 if len(violations) == 0 else max(0.0, 1.0 - (len(violations) * 0.2))
        passed = len(violations) == 0
        
        return ValidationResult(
            passed=passed,
            score=score,
            issues=issues,
            warnings=warnings,
            details={'violations': violations}
        )
    
    def _validate_interface_usage(self, module_path: Path) -> ValidationResult:
        """Validate module uses core.interfaces for abstractions"""
        issues = []
        warnings = []
        interface_imports = []
        
        backend_path = module_path / 'backend'
        
        if not backend_path.exists():
            return ValidationResult(
                passed=True,
                score=0.5,
                issues=[],
                warnings=['No backend/ directory - cannot check interface usage']
            )
        
        # Scan for interface imports
        for py_file in backend_path.rglob('*.py'):
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Look for core.interfaces imports
                interface_pattern = r'from core\.interfaces\.\w+ import'
                matches = re.findall(interface_pattern, content)
                interface_imports.extend(matches)
                
            except Exception as e:
                warnings.append(f'Could not scan {py_file.name}: {e}')
        
        # Calculate score based on interface usage
        score = min(1.0, len(interface_imports) * 0.25) if interface_imports else 0.5
        
        if not interface_imports:
            warnings.append('No core.interfaces imports found - consider using abstractions')
        
        return ValidationResult(
            passed=True,  # Not critical, just recommended
            score=score,
            issues=issues,
            warnings=warnings,
            details={'interface_imports': len(interface_imports)}
        )
    
    def _validate_coupling(self, module_path: Path) -> ValidationResult:
        """Validate loose coupling (no direct module imports)"""
        issues = []
        warnings = []
        direct_imports = []
        
        backend_path = module_path / 'backend'
        
        if not backend_path.exists():
            return ValidationResult(
                passed=True,
                score=1.0,
                issues=[],
                warnings=['No backend/ directory - skipping coupling check']
            )
        
        # Scan for direct module imports (e.g., from modules.X import Y)
        for py_file in backend_path.rglob('*.py'):
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Look for direct module imports
                direct_import_pattern = r'from modules\.\w+\.\w+ import'
                matches = re.findall(direct_import_pattern, content)
                if matches:
                    direct_imports.append({
                        'file': py_file.relative_to(module_path),
                        'imports': matches
                    })
                    
            except Exception as e:
                warnings.append(f'Could not scan {py_file.name}: {e}')
        
        # Report direct imports as warnings (not critical, but discouraged)
        for import_info in direct_imports:
            warning = f"LOOSE COUPLING: {import_info['file']} has direct module imports"
            warnings.append(warning)
        
        # Calculate score (penalize direct imports)
        score = max(0.5, 1.0 - (len(direct_imports) * 0.15))
        
        return ValidationResult(
            passed=True,  # Not critical
            score=score,
            issues=issues,
            warnings=warnings,
            details={'direct_imports': direct_imports}
        )
    
    def _calculate_overall_score(self) -> float:
        """Calculate weighted overall score"""
        total_score = 0.0
        
        for category, weight in self.WEIGHTS.items():
            if category in self.results:
                total_score += self.results[category].score * weight
        
        return round(total_score, 2)
    
    def _print_report(self, passed: bool):
        """Print detailed validation report"""
        print(f"\n{'='*60}")
        print(f"VALIDATION REPORT")
        print(f"{'='*60}\n")
        
        # Print category results
        for category, result in self.results.items():
            status = "✅ PASS" if result.passed else "❌ FAIL"
            print(f"{category.upper()}: {status} (Score: {result.score:.2f})")
            
            if result.issues:
                for issue in result.issues:
                    print(f"  ❌ {issue}")
            
            if result.warnings:
                for warning in result.warnings:
                    print(f"  ⚠️  {warning}")
            
            print()
        
        # Print overall result
        print(f"{'='*60}")
        print(f"OVERALL SCORE: {self.overall_score:.2f}")
        print(f"RESULT: {'✅ PASSED' if passed else '❌ FAILED'}")
        
        if self.critical_issues:
            print(f"\nCRITICAL ISSUES ({len(self.critical_issues)}):")
            for issue in self.critical_issues:
                print(f"  🔴 {issue}")
        
        print(f"{'='*60}\n")
        
        # Exit code guidance
        if passed:
            print("✅ Module ready for deployment")
            print("   Exit code: 0")
        else:
            print("❌ Module CANNOT be deployed until issues are fixed")
            print("   Exit code: 1")
        
        print()


def main():
    """CLI entry point"""
    if len(sys.argv) < 2:
        print("Usage: python tools/fengshui/module_quality_gate.py [module_name]")
        print("\nExample:")
        print("  python tools/fengshui/module_quality_gate.py knowledge_graph")
        sys.exit(1)
    
    module_name = sys.argv[1]
    module_path = Path('modules') / module_name
    
    gate = ModuleQualityGate()
    result = gate.validate(module_path)
    
    # Exit with appropriate code
    sys.exit(0 if result['passed'] else 1)


if __name__ == '__main__':
    main()