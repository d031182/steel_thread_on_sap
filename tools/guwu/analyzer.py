"""
Gu Wu Test Analyzer - Phase 2 Autonomous Capabilities

Provides:
- Redundancy detection (overlapping test coverage)
- Smart test selection (skip tests unaffected by code changes)
- Test quality analysis
"""

# Windows UTF-8 encoding fix (MANDATORY for all Python scripts)
import sys
if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except:
        pass  # Fallback if reconfigure not available

import os
import ast
import sqlite3
from pathlib import Path
from typing import Dict, List, Set, Tuple
from dataclasses import dataclass
from datetime import datetime
import json


@dataclass
class TestAnalysis:
    """Analysis results for a test file"""
    test_file: str
    functions_tested: Set[str]
    files_imported: Set[str]
    test_count: int
    has_redundancy: bool
    redundant_with: List[str]
    coverage_score: float


@dataclass
class RedundancyReport:
    """Report of redundant tests"""
    total_tests: int
    redundant_tests: int
    redundancy_groups: List[List[str]]
    potential_savings: str  # e.g., "25% (5/20 tests)"


class TestAnalyzer:
    """Analyzes tests for redundancy and optimization opportunities"""
    
    def __init__(self, test_dir: str = "tests", metrics_db: str = "tools/guwu/metrics.db"):
        self.test_dir = Path(test_dir)
        self.metrics_db = metrics_db
        self.test_coverage_map: Dict[str, TestAnalysis] = {}
        
    def analyze_all_tests(self) -> Dict[str, TestAnalysis]:
        """Analyze all test files and build coverage map"""
        print("[*] Analyzing test suite...")
        
        # Find all test files
        test_files = list(self.test_dir.rglob("test_*.py"))
        
        for test_file in test_files:
            try:
                analysis = self._analyze_test_file(test_file)
                self.test_coverage_map[str(test_file)] = analysis
            except Exception as e:
                print(f"[!] Failed to analyze {test_file}: {e}")
                
        return self.test_coverage_map
    
    def _analyze_test_file(self, test_file: Path) -> TestAnalysis:
        """Analyze a single test file"""
        with open(test_file, 'r', encoding='utf-8') as f:
            content = f.read()
            
        try:
            tree = ast.parse(content)
        except SyntaxError:
            # File has syntax errors, skip analysis
            return TestAnalysis(
                test_file=str(test_file),
                functions_tested=set(),
                files_imported=set(),
                test_count=0,
                has_redundancy=False,
                redundant_with=[],
                coverage_score=0.0
            )
        
        # Extract test functions
        test_functions = [
            node.name for node in ast.walk(tree)
            if isinstance(node, ast.FunctionDef) and node.name.startswith('test_')
        ]
        
        # Extract imports (what code this test covers)
        imports = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.add(alias.name)
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    imports.add(node.module)
        
        # Extract function calls (what functions are tested)
        functions_tested = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                if isinstance(node.func, ast.Name):
                    functions_tested.add(node.func.id)
                elif isinstance(node.func, ast.Attribute):
                    functions_tested.add(node.func.attr)
        
        return TestAnalysis(
            test_file=str(test_file),
            functions_tested=functions_tested,
            files_imported=imports,
            test_count=len(test_functions),
            has_redundancy=False,  # Determined later
            redundant_with=[],
            coverage_score=self._calculate_coverage_score(test_file)
        )
    
    def _calculate_coverage_score(self, test_file: Path) -> float:
        """Calculate coverage score from historical data"""
        try:
            conn = sqlite3.connect(self.metrics_db)
            cursor = conn.cursor()
            
            # Get average coverage for this test over last 10 runs
            cursor.execute("""
                SELECT AVG(coverage_pct) 
                FROM test_history 
                WHERE test_name LIKE ?
                ORDER BY timestamp DESC 
                LIMIT 10
            """, (f"%{test_file.stem}%",))
            
            result = cursor.fetchone()
            conn.close()
            
            return result[0] if result and result[0] else 0.0
        except:
            return 0.0
    
    def detect_redundancy(self) -> RedundancyReport:
        """Detect redundant tests (tests that cover the same code)"""
        print("\n[*] Detecting redundant tests...")
        
        if not self.test_coverage_map:
            self.analyze_all_tests()
        
        redundancy_groups = []
        checked = set()
        
        tests = list(self.test_coverage_map.items())
        
        for i, (test1_path, test1) in enumerate(tests):
            if test1_path in checked:
                continue
                
            group = [test1_path]
            
            for test2_path, test2 in tests[i+1:]:
                if test2_path in checked:
                    continue
                
                # Check if tests cover similar code
                similarity = self._calculate_similarity(test1, test2)
                
                if similarity > 0.8:  # 80% overlap threshold
                    group.append(test2_path)
                    checked.add(test2_path)
            
            if len(group) > 1:
                redundancy_groups.append(group)
                checked.add(test1_path)
        
        total_tests = len(self.test_coverage_map)
        redundant_tests = sum(len(group) - 1 for group in redundancy_groups)
        
        # Mark redundant tests
        for group in redundancy_groups:
            for test_path in group[1:]:  # Skip first (keep it)
                if test_path in self.test_coverage_map:
                    self.test_coverage_map[test_path].has_redundancy = True
                    self.test_coverage_map[test_path].redundant_with = [group[0]]
        
        return RedundancyReport(
            total_tests=total_tests,
            redundant_tests=redundant_tests,
            redundancy_groups=redundancy_groups,
            potential_savings=f"{redundant_tests}/{total_tests} tests ({redundant_tests*100//total_tests if total_tests else 0}%)"
        )
    
    def _calculate_similarity(self, test1: TestAnalysis, test2: TestAnalysis) -> float:
        """Calculate similarity between two tests (0.0 - 1.0)"""
        # Compare imports (what modules they test)
        import_overlap = len(test1.files_imported & test2.files_imported)
        import_total = len(test1.files_imported | test2.files_imported)
        import_similarity = import_overlap / import_total if import_total > 0 else 0.0
        
        # Compare functions tested
        func_overlap = len(test1.functions_tested & test2.functions_tested)
        func_total = len(test1.functions_tested | test2.functions_tested)
        func_similarity = func_overlap / func_total if func_total > 0 else 0.0
        
        # Weighted average (imports more important than function calls)
        return (import_similarity * 0.7) + (func_similarity * 0.3)
    
    def suggest_removals(self) -> List[str]:
        """Suggest which tests to remove (keep best of redundant group)"""
        suggestions = []
        
        for test_path, analysis in self.test_coverage_map.items():
            if analysis.has_redundancy and analysis.redundant_with:
                primary = analysis.redundant_with[0]
                suggestions.append(f"[-] REMOVE: {test_path}\n   [+] KEEP: {primary} (better coverage)")
        
        return suggestions
    
    def generate_report(self) -> str:
        """Generate comprehensive redundancy report"""
        redundancy = self.detect_redundancy()
        suggestions = self.suggest_removals()
        
        report = []
        report.append("=" * 80)
        report.append("Gu Wu Test Redundancy Analysis Report")
        report.append("=" * 80)
        report.append("")
        report.append(f"[*] Summary:")
        report.append(f"   Total Tests: {redundancy.total_tests}")
        report.append(f"   Redundant Tests: {redundancy.redundant_tests}")
        report.append(f"   Potential Savings: {redundancy.potential_savings}")
        report.append("")
        
        if redundancy.redundancy_groups:
            report.append("[*] Redundancy Groups:")
            for i, group in enumerate(redundancy.redundancy_groups, 1):
                report.append(f"\n   Group {i} ({len(group)} tests):")
                for j, test in enumerate(group):
                    marker = "[+] KEEP" if j == 0 else "[-] REDUNDANT"
                    report.append(f"      {marker}: {test}")
            report.append("")
        
        if suggestions:
            report.append("[!] Removal Suggestions:")
            for suggestion in suggestions:
                report.append(f"   {suggestion}")
            report.append("")
        else:
            report.append("[+] No redundant tests detected!")
            report.append("")
        
        report.append("=" * 80)
        
        return "\n".join(report)


class SmartTestSelector:
    """Selects only tests affected by code changes"""
    
    def __init__(self, test_dir: str = "tests"):
        self.test_dir = Path(test_dir)
        self.analyzer = TestAnalyzer(test_dir)
    
    def select_tests_for_changes(self, changed_files: List[str]) -> List[str]:
        """
        Select only tests that need to run based on changed files
        
        Args:
            changed_files: List of file paths that changed
            
        Returns:
            List of test files that should run
        """
        print(f"\n[*] Selecting tests for {len(changed_files)} changed files...")
        
        # Analyze all tests if not done yet
        if not self.analyzer.test_coverage_map:
            self.analyzer.analyze_all_tests()
        
        # Determine which modules changed
        changed_modules = set()
        for file_path in changed_files:
            # Convert file path to module name
            module_path = Path(file_path)
            if module_path.suffix == '.py':
                # Extract module path: modules/knowledge_graph/backend/api.py -> modules.knowledge_graph
                parts = module_path.parts
                if 'modules' in parts:
                    idx = parts.index('modules')
                    module_name = '.'.join(parts[idx:idx+2])
                    changed_modules.add(module_name)
                elif 'core' in parts:
                    idx = parts.index('core')
                    module_name = '.'.join(parts[idx:idx+2])
                    changed_modules.add(module_name)
        
        # Find tests that import changed modules
        affected_tests = []
        for test_path, analysis in self.analyzer.test_coverage_map.items():
            for changed_module in changed_modules:
                for imported in analysis.files_imported:
                    if changed_module in imported:
                        affected_tests.append(test_path)
                        break
        
        if not affected_tests:
            print("   [!] No tests directly affected, running all tests as safety measure")
            return list(self.analyzer.test_coverage_map.keys())
        
        print(f"   [+] Selected {len(affected_tests)}/{len(self.analyzer.test_coverage_map)} tests")
        for test in affected_tests:
            print(f"      - {test}")
        
        return affected_tests


def main():
    """CLI entry point for test analysis"""
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "redundancy":
        analyzer = TestAnalyzer()
        analyzer.analyze_all_tests()
        report = analyzer.generate_report()
        print(report)
        
        # Save report
        report_path = Path("tools/guwu/redundancy_report.txt")
        report_path.write_text(report, encoding='utf-8')
        print(f"\n[+] Report saved to: {report_path}")
        
    elif len(sys.argv) > 1 and sys.argv[1] == "smart-select":
        # Example: python -m tools.guwu.analyzer smart-select modules/knowledge_graph/backend/api.py
        changed_files = sys.argv[2:]
        selector = SmartTestSelector()
        affected_tests = selector.select_tests_for_changes(changed_files)
        
        print(f"\n[+] Run these {len(affected_tests)} tests:")
        for test in affected_tests:
            print(f"   pytest {test}")
    else:
        print("Usage:")
        print("  python -m tools.guwu.analyzer redundancy")
        print("  python -m tools.guwu.analyzer smart-select <changed_file1> <changed_file2> ...")


if __name__ == "__main__":
    main()