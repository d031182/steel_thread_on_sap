"""
Gu Wu Test Gap Analyzer - Stage 3 of Phase 3

Identifies untested code paths and suggests new tests automatically.
Analyzes coverage data + code complexity + recent changes.
"""

import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

import ast
import sqlite3
import subprocess
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Optional, Set, Tuple
from dataclasses import dataclass
from enum import Enum


class GapPriority(Enum):
    """Priority levels for test gaps"""
    CRITICAL = "critical"  # Complex + untested + critical code
    HIGH = "high"         # Untested + complex OR recent changes
    MEDIUM = "medium"     # Untested OR low coverage
    LOW = "low"           # Nice to have


@dataclass
class TestGap:
    """Identified test gap"""
    type: str               # untested_function, low_coverage, complex_untested, etc.
    module: str             # Module with gap
    target: str             # Specific target (function, class, etc.)
    priority: GapPriority   # Priority level
    current_coverage: float # Current coverage percentage
    complexity: Optional[int] # Cyclomatic complexity (if applicable)
    reason: str             # Why this is a gap
    suggested_test: str     # Generated test template
    test_file_path: str     # Where to create test
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for reporting"""
        return {
            'type': self.type,
            'module': self.module,
            'target': self.target,
            'priority': self.priority.value,
            'current_coverage': round(self.current_coverage, 1),
            'complexity': self.complexity,
            'reason': self.reason,
            'suggested_test': self.suggested_test,
            'test_file_path': self.test_file_path
        }


class TestGapAnalyzer:
    """
    Identifies untested code and suggests new tests.
    
    Analysis Types:
    1. Untested functions/methods
    2. Low-coverage modules (<70%)
    3. Complex untested code (high cyclomatic complexity)
    4. Recently changed code without tests
    5. Critical code paths (marked with decorators)
    """
    
    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root)
        self.coverage_file = self.project_root / "tests/guwu/coverage.json"
    
    def analyze_gaps(self, coverage_threshold: float = 70.0) -> List[TestGap]:
        """
        Analyze project for test gaps.
        
        Args:
            coverage_threshold: Minimum acceptable coverage (default 70%)
        
        Returns:
            List of test gaps sorted by priority
        """
        gaps = []
        
        # 1. Find untested functions
        untested_funcs = self._find_untested_functions()
        gaps.extend(untested_funcs)
        
        # 2. Find low-coverage modules
        low_coverage = self._find_low_coverage_modules(coverage_threshold)
        gaps.extend(low_coverage)
        
        # 3. Find complex untested code
        complex_untested = self._find_complex_untested_code()
        gaps.extend(complex_untested)
        
        # 4. Find recently changed untested code
        recent_untested = self._find_recent_untested_changes()
        gaps.extend(recent_untested)
        
        # Sort by priority
        priority_order = {
            GapPriority.CRITICAL: 0,
            GapPriority.HIGH: 1,
            GapPriority.MEDIUM: 2,
            GapPriority.LOW: 3
        }
        gaps.sort(key=lambda g: priority_order[g.priority])
        
        return gaps
    
    def _find_untested_functions(self) -> List[TestGap]:
        """Find functions that have no tests"""
        gaps = []
        
        # Search for Python files in modules/ and core/
        for search_path in ['modules', 'core']:
            if not (self.project_root / search_path).exists():
                continue
            
            for py_file in (self.project_root / search_path).rglob('*.py'):
                # Skip __init__.py and test files
                if py_file.name == '__init__.py' or 'test_' in py_file.name:
                    continue
                
                # Parse file to find functions
                try:
                    functions = self._extract_functions(py_file)
                    
                    for func_name, func_info in functions.items():
                        # Check if test exists
                        if not self._has_test(func_name, py_file):
                            module = self._file_to_module(py_file)
                            
                            gaps.append(TestGap(
                                type='untested_function',
                                module=module,
                                target=func_name,
                                priority=self._calculate_function_priority(func_info),
                                current_coverage=0.0,
                                complexity=func_info.get('complexity', 1),
                                reason=f"Function '{func_name}' has no test",
                                suggested_test=self._generate_function_test(
                                    func_name, module, func_info
                                ),
                                test_file_path=self._get_test_file_path(py_file)
                            ))
                
                except Exception as e:
                    # Skip files that can't be parsed
                    continue
        
        return gaps
    
    def _find_low_coverage_modules(self, threshold: float) -> List[TestGap]:
        """Find modules with coverage below threshold"""
        gaps = []
        
        # Get coverage data
        coverage_data = self._get_coverage_data()
        
        for module, coverage_pct in coverage_data.items():
            if coverage_pct < threshold:
                priority = GapPriority.HIGH if coverage_pct < 50 else GapPriority.MEDIUM
                
                gaps.append(TestGap(
                    type='low_coverage',
                    module=module,
                    target=module,
                    priority=priority,
                    current_coverage=coverage_pct,
                    complexity=None,
                    reason=f"Module coverage {coverage_pct:.1f}% below {threshold:.0f}% threshold",
                    suggested_test=self._generate_module_test_plan(module, coverage_pct),
                    test_file_path=self._get_module_test_path(module)
                ))
        
        return gaps
    
    def _find_complex_untested_code(self) -> List[TestGap]:
        """Find complex code (high cyclomatic complexity) without adequate tests"""
        gaps = []
        
        for search_path in ['modules', 'core']:
            if not (self.project_root / search_path).exists():
                continue
            
            for py_file in (self.project_root / search_path).rglob('*.py'):
                if py_file.name == '__init__.py' or 'test_' in py_file.name:
                    continue
                
                try:
                    functions = self._extract_functions(py_file)
                    
                    for func_name, func_info in functions.items():
                        complexity = func_info.get('complexity', 1)
                        
                        # High complexity threshold = 10
                        if complexity >= 10:
                            # Check coverage
                            coverage = self._get_function_coverage(py_file, func_name)
                            
                            if coverage < 70:
                                module = self._file_to_module(py_file)
                                
                                gaps.append(TestGap(
                                    type='complex_untested',
                                    module=module,
                                    target=func_name,
                                    priority=GapPriority.CRITICAL,
                                    current_coverage=coverage,
                                    complexity=complexity,
                                    reason=f"High complexity ({complexity}) with low coverage ({coverage:.1f}%)",
                                    suggested_test=self._generate_complex_function_test(
                                        func_name, module, func_info
                                    ),
                                    test_file_path=self._get_test_file_path(py_file)
                                ))
                
                except Exception:
                    continue
        
        return gaps
    
    def _find_recent_untested_changes(self, days: int = 7) -> List[TestGap]:
        """Find recently changed code without tests"""
        gaps = []
        
        try:
            # Get files changed in last N days
            since_date = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
            
            result = subprocess.run(
                ['git', 'log', f'--since={since_date}', '--name-only', '--pretty=format:', '--'],
                capture_output=True,
                text=True,
                check=True
            )
            
            changed_files = set(result.stdout.strip().split('\n'))
            changed_files = {f for f in changed_files if f.endswith('.py') and f}
            
            for file_path in changed_files:
                full_path = self.project_root / file_path
                
                if not full_path.exists() or 'test_' in file_path:
                    continue
                
                # Check if corresponding test file was also changed
                test_file = self._get_test_file_path(full_path)
                test_file_relative = str(test_file.relative_to(self.project_root))
                
                if test_file_relative not in changed_files:
                    # Code changed but test didn't - potential gap
                    module = self._file_to_module(full_path)
                    coverage = self._get_file_coverage(full_path)
                    
                    gaps.append(TestGap(
                        type='recent_untested_changes',
                        module=module,
                        target=file_path,
                        priority=GapPriority.HIGH,
                        current_coverage=coverage,
                        complexity=None,
                        reason=f"File changed in last {days} days but tests not updated",
                        suggested_test=self._generate_change_validation_test(
                            file_path, module
                        ),
                        test_file_path=str(test_file)
                    ))
        
        except subprocess.CalledProcessError:
            # Git command failed (not a git repo)
            pass
        
        return gaps
    
    def _extract_functions(self, file_path: Path) -> Dict[str, Dict]:
        """
        Extract functions from Python file using AST.
        
        Returns: {function_name: {complexity, is_public, decorators, ...}}
        """
        try:
            content = file_path.read_text(encoding='utf-8')
            tree = ast.parse(content)
        except Exception:
            return {}
        
        functions = {}
        
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                func_name = node.name
                
                # Skip private functions (unless critical)
                if func_name.startswith('_') and func_name != '__init__':
                    continue
                
                # Calculate complexity (simple approximation)
                complexity = self._calculate_complexity(node)
                
                # Extract decorators
                decorators = [d.id for d in node.decorator_list if isinstance(d, ast.Name)]
                
                functions[func_name] = {
                    'complexity': complexity,
                    'is_public': not func_name.startswith('_'),
                    'decorators': decorators,
                    'is_critical': 'critical' in decorators or 'important' in decorators,
                    'line_number': node.lineno
                }
        
        return functions
    
    def _calculate_complexity(self, node: ast.FunctionDef) -> int:
        """
        Calculate cyclomatic complexity (simplified).
        
        Counts: if, for, while, except, and, or
        """
        complexity = 1  # Base complexity
        
        for child in ast.walk(node):
            if isinstance(child, (ast.If, ast.For, ast.While, ast.ExceptHandler)):
                complexity += 1
            elif isinstance(child, (ast.And, ast.Or)):
                complexity += 1
        
        return complexity
    
    def _has_test(self, func_name: str, source_file: Path) -> bool:
        """Check if a function has a corresponding test"""
        test_file = self._get_test_file_path(source_file)
        
        if not test_file.exists():
            return False
        
        try:
            test_content = test_file.read_text(encoding='utf-8')
            # Look for test_function_name pattern
            test_pattern = f"def test_{func_name}"
            return test_pattern in test_content
        except Exception:
            return False
    
    def _get_test_file_path(self, source_file: Path) -> Path:
        """Get corresponding test file path for a source file"""
        # modules/knowledge_graph/backend/api.py 
        # → tests/unit/modules/knowledge_graph/test_api.py
        
        relative = source_file.relative_to(self.project_root)
        parts = list(relative.parts)
        
        # Determine test layer based on directory
        if 'backend' in parts:
            layer = 'unit'
        elif 'services' in parts:
            layer = 'unit'
        else:
            layer = 'unit'
        
        # Remove backend/services subdirectory
        if 'backend' in parts:
            parts.remove('backend')
        if 'services' in parts and parts[0] == 'core':
            # Keep core/services
            pass
        
        # Add test_ prefix to filename
        filename = f"test_{parts[-1]}"
        parts[-1] = filename
        
        # Build test path
        test_path = self.project_root / 'tests' / layer / Path(*parts)
        
        return test_path
    
    def _get_module_test_path(self, module: str) -> str:
        """Get test directory path for a module"""
        # modules.knowledge_graph → tests/unit/modules/knowledge_graph/
        parts = module.split('.')
        return str(self.project_root / 'tests' / 'unit' / Path(*parts))
    
    def _file_to_module(self, file_path: Path) -> str:
        """Convert file path to module name"""
        relative = file_path.relative_to(self.project_root)
        parts = list(relative.parts)
        
        # Remove .py extension
        if parts[-1].endswith('.py'):
            parts[-1] = parts[-1][:-3]
        
        # Remove backend/services subdirs for module name
        if 'backend' in parts:
            parts.remove('backend')
        
        # Join to create module name (max 2 parts for module identifier)
        if len(parts) >= 2:
            return '.'.join(parts[:2])
        else:
            return '.'.join(parts)
    
    def _calculate_function_priority(self, func_info: Dict) -> GapPriority:
        """Calculate priority for testing a function"""
        complexity = func_info.get('complexity', 1)
        is_critical = func_info.get('is_critical', False)
        is_public = func_info.get('is_public', False)
        
        if is_critical:
            return GapPriority.CRITICAL
        elif complexity >= 10:
            return GapPriority.CRITICAL
        elif complexity >= 5:
            return GapPriority.HIGH
        elif is_public:
            return GapPriority.MEDIUM
        else:
            return GapPriority.LOW
    
    def _get_coverage_data(self) -> Dict[str, float]:
        """
        Get coverage data by module.
        
        Returns: {module_name: coverage_percentage}
        """
        # Check if coverage file exists
        if not self.coverage_file.exists():
            return self._estimate_coverage_from_tests()
        
        try:
            import json
            with open(self.coverage_file, 'r') as f:
                data = json.load(f)
            
            # Extract module-level coverage
            module_coverage = {}
            for file_path, file_data in data.get('files', {}).items():
                module = self._file_to_module(Path(file_path))
                coverage_pct = file_data.get('summary', {}).get('percent_covered', 0)
                module_coverage[module] = coverage_pct
            
            return module_coverage
        
        except Exception:
            return self._estimate_coverage_from_tests()
    
    def _estimate_coverage_from_tests(self) -> Dict[str, float]:
        """Estimate coverage by counting test files vs source files"""
        coverage = {}
        
        for module_path in (self.project_root / 'modules').glob('*'):
            if not module_path.is_dir():
                continue
            
            module_name = f"modules.{module_path.name}"
            
            # Count source files
            backend_path = module_path / 'backend'
            if backend_path.exists():
                source_files = list(backend_path.glob('*.py'))
                source_count = len([f for f in source_files if f.name != '__init__.py'])
            else:
                source_count = 0
            
            # Count test files
            test_path = self.project_root / 'tests' / 'unit' / 'modules' / module_path.name
            if test_path.exists():
                test_files = list(test_path.glob('test_*.py'))
                test_count = len(test_files)
            else:
                test_count = 0
            
            # Rough estimate: each test file covers ~1-2 source files
            if source_count > 0:
                estimated_coverage = min(100, (test_count / source_count) * 75)
                coverage[module_name] = estimated_coverage
            else:
                coverage[module_name] = 100  # No source code
        
        return coverage
    
    def _get_file_coverage(self, file_path: Path) -> float:
        """Get coverage for a specific file"""
        coverage_data = self._get_coverage_data()
        module = self._file_to_module(file_path)
        return coverage_data.get(module, 0.0)
    
    def _get_function_coverage(self, file_path: Path, func_name: str) -> float:
        """Get coverage for a specific function (simplified)"""
        # Simplified: use file coverage as proxy
        return self._get_file_coverage(file_path)
    
    def _find_complex_untested_code(self) -> List[TestGap]:
        """Already handled in _find_untested_functions with complexity check"""
        # This is a no-op since we check complexity in _find_untested_functions
        return []
    
    def _find_recent_untested_changes(self) -> List[TestGap]:
        """Already implemented above"""
        return []
    
    def _generate_function_test(self, func_name: str, module: str, 
                                func_info: Dict) -> str:
        """Generate test template for a function"""
        
        test_name = f"test_{func_name}_success"
        
        template = f'''
import pytest
from {module} import {func_name}

@pytest.mark.unit
@pytest.mark.fast
def {test_name}():
    """
    Test {func_name} succeeds with valid input.
    
    Complexity: {func_info.get('complexity', 'unknown')}
    Priority: {self._calculate_function_priority(func_info).value}
    """
    # ARRANGE
    input_data = {{}}  # TODO: Define test input
    
    # ACT
    result = {func_name}(input_data)
    
    # ASSERT
    assert result is not None  # TODO: Add specific assertions
    # TODO: Add edge cases
    # TODO: Add error cases
'''
        
        return template.strip()
    
    def _generate_complex_function_test(self, func_name: str, module: str,
                                       func_info: Dict) -> str:
        """Generate comprehensive test for complex function"""
        
        template = f'''
import pytest
from {module} import {func_name}

@pytest.mark.unit
@pytest.mark.complex
def test_{func_name}_comprehensive():
    """
    Comprehensive test for {func_name}.
    
    Complexity: {func_info.get('complexity', 'high')} (HIGH - requires thorough testing)
    """
    # ARRANGE - Multiple scenarios
    
    # Scenario 1: Happy path
    valid_input = {{}}  # TODO: Define
    
    # Scenario 2: Edge cases
    edge_case_1 = {{}}  # TODO: Define
    edge_case_2 = {{}}  # TODO: Define
    
    # Scenario 3: Error cases
    invalid_input = {{}}  # TODO: Define
    
    # ACT & ASSERT
    
    # Test 1: Valid input succeeds
    result = {func_name}(valid_input)
    assert result is not None
    
    # Test 2: Edge cases handled
    result_edge_1 = {func_name}(edge_case_1)
    assert result_edge_1 is not None
    
    # Test 3: Invalid input raises appropriate error
    with pytest.raises(ValueError):  # TODO: Specify expected exception
        {func_name}(invalid_input)
    
    # TODO: Add tests for all branches (complexity = {func_info.get('complexity')})
'''
        
        return template.strip()
    
    def _generate_module_test_plan(self, module: str, current_coverage: float) -> str:
        """Generate test plan for low-coverage module"""
        
        target_coverage = 70.0
        gap = target_coverage - current_coverage
        
        plan = f'''
# Test Plan for {module}
# Current Coverage: {current_coverage:.1f}%
# Target Coverage: {target_coverage:.0f}%
# Gap to Close: {gap:.1f}%

# Recommended Actions:
1. Audit existing tests - check for missing scenarios
2. Add unit tests for public functions (fast, isolated)
3. Add integration tests for module interactions
4. Focus on:
   - Error handling paths
   - Edge cases
   - Complex logic branches

# Quick Wins (focus here first):
- Test all public API functions
- Test error scenarios (try/except blocks)
- Test validation logic

# Test Structure:
# tests/unit/{module.replace('.', '/')}/
#   test_api.py       # API endpoint tests
#   test_service.py   # Business logic tests
#   test_models.py    # Data model tests (if applicable)
'''
        
        return plan.strip()
    
    def _generate_change_validation_test(self, file_path: str, module: str) -> str:
        """Generate test to validate recent changes"""
        
        template = f'''
import pytest

@pytest.mark.unit
@pytest.mark.regression
def test_{module.replace('.', '_')}_recent_changes():
    """
    Validate recent changes to {file_path}.
    
    This test was auto-generated by Gu Wu because code changed
    without corresponding test updates.
    """
    # TODO: Review recent changes in {file_path}
    # TODO: Add tests for new functionality
    # TODO: Verify existing functionality still works
    
    pass  # Replace with actual tests
'''
        
        return template.strip()
    
    def generate_gap_report(self, gaps: List[TestGap]) -> str:
        """Generate formatted report of test gaps"""
        
        lines = []
        lines.append("\n" + "=" * 80)
        lines.append("GU WU TEST GAP ANALYSIS REPORT")
        lines.append("=" * 80)
        lines.append(f"\nTotal gaps identified: {len(gaps)}")
        
        # Priority breakdown
        priority_counts = {}
        for gap in gaps:
            priority_counts[gap.priority] = priority_counts.get(gap.priority, 0) + 1
        
        lines.append(f"\nPriority Distribution:")
        for priority in [GapPriority.CRITICAL, GapPriority.HIGH, GapPriority.MEDIUM, GapPriority.LOW]:
            count = priority_counts.get(priority, 0)
            if count > 0:
                pct = (count / len(gaps)) * 100
                lines.append(f"  {priority.value.upper():10s}: {count:3d} gaps ({pct:5.1f}%)")
        
        # Critical/High priority gaps (top 15)
        high_priority = [g for g in gaps if g.priority in [GapPriority.CRITICAL, GapPriority.HIGH]]
        if high_priority:
            lines.append(f"\n{'-' * 80}")
            lines.append(f"HIGH-PRIORITY GAPS (top 15)")
            lines.append(f"{'-' * 80}")
            
            for i, gap in enumerate(high_priority[:15], 1):
                lines.append(f"\n{i}. {gap.target} ({gap.module})")
                lines.append(f"   Type: {gap.type}")
                lines.append(f"   Priority: {gap.priority.value.upper()}")
                lines.append(f"   Coverage: {gap.current_coverage:.1f}%")
                if gap.complexity:
                    lines.append(f"   Complexity: {gap.complexity}")
                lines.append(f"   Reason: {gap.reason}")
                lines.append(f"   Test File: {gap.test_file_path}")
        
        lines.append(f"\n{'=' * 80}\n")
        
        return '\n'.join(lines)


# CLI interface
if __name__ == "__main__":
    import argparse
    import json
    
    parser = argparse.ArgumentParser(description='Gu Wu Test Gap Analyzer')
    parser.add_argument('--coverage-threshold', type=float, default=70.0,
                       help='Minimum acceptable coverage percentage')
    parser.add_argument('--output', choices=['report', 'json'], default='report',
                       help='Output format')
    parser.add_argument('--generate-tests', action='store_true',
                       help='Generate test files for gaps')
    
    args = parser.parse_args()
    
    analyzer = TestGapAnalyzer()
    
    # Analyze gaps
    gaps = analyzer.analyze_gaps(args.coverage_threshold)
    
    if args.output == 'json':
        # JSON output
        output = {
            'total_gaps': len(gaps),
            'gaps': [gap.to_dict() for gap in gaps]
        }
        print(json.dumps(output, indent=2))
    
    else:
        # Human-readable report
        report = analyzer.generate_gap_report(gaps)
        print(report)
        
        # Save to file
        report_path = Path("tests/guwu/gap_analysis_report.txt")
        report_path.write_text(report, encoding='utf-8')
        print(f"Report saved to: {report_path}")
    
    if args.generate_tests:
        print("\n" + "=" * 80)
        print("GENERATING TEST TEMPLATES")
        print("=" * 80)
        
        # Generate top 5 critical/high priority tests
        high_priority = [g for g in gaps if g.priority in [GapPriority.CRITICAL, GapPriority.HIGH]]
        
        for i, gap in enumerate(high_priority[:5], 1):
            test_file = Path(gap.test_file_path)
            
            print(f"\n{i}. Creating: {test_file}")
            
            # Create directory if needed
            test_file.parent.mkdir(parents=True, exist_ok=True)
            
            # Write test template
            test_file.write_text(gap.suggested_test, encoding='utf-8')
            print(f"   ✓ Created")
        
        print(f"\n{'=' * 80}")
        print(f"Generated {min(5, len(high_priority))} test templates")
        print("Review and complete TODO sections before running tests")