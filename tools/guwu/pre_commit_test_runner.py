#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Gu Wu Pre-Commit Test Runner - Run tests for staged files

Purpose: Catch breaking tests BEFORE commit enters repository
Speed: < 10 seconds (unit tests only, incremental)
Usage: Called automatically by .git/hooks/pre-commit

Exit codes:
- 0: All tests passed (commit allowed)
- 1: Tests failed or error occurred (commit blocked)

Integration: Part of Feng Shui + Gu Wu intelligent pre-commit validation
"""

import sys
import subprocess
import json
from pathlib import Path
from typing import List, Set, Dict, Tuple

# Windows encoding fix
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

# Get project root
PROJECT_ROOT = Path(__file__).parent.parent.parent


def get_staged_python_files() -> List[str]:
    """Get list of staged Python files"""
    try:
        result = subprocess.run(
            ['git', 'diff', '--cached', '--name-only', '--diff-filter=ACM'],
            capture_output=True,
            text=True,
            check=True,
            cwd=PROJECT_ROOT
        )
        
        files = [f.strip() for f in result.stdout.split('\n') if f.strip()]
        # Filter Python files only
        python_files = [f for f in files if f.endswith('.py')]
        
        return python_files
    
    except subprocess.CalledProcessError as e:
        print(f"[ERROR] Failed to get staged files: {e}")
        sys.exit(1)


def find_related_test_files(staged_files: List[str]) -> Set[str]:
    """
    Find test files related to staged source files
    
    Strategy:
    1. If staged file is a test: include it
    2. If staged file is source: find corresponding unit test
    3. Use pytest's collection to discover tests
    """
    test_files = set()
    
    for file_path in staged_files:
        path = Path(file_path)
        
        # Case 1: Staged file is already a test
        if 'tests/' in file_path or file_path.startswith('test_'):
            test_files.add(file_path)
            continue
        
        # Case 2: Find corresponding test for source file
        # Example: modules/data_products_v2/backend/api.py
        #       → tests/unit/modules/data_products_v2/test_api.py
        
        if path.parts[0] == 'modules' and len(path.parts) >= 4:
            module_name = path.parts[1]  # e.g., data_products_v2
            file_stem = path.stem  # e.g., api (without .py)
            
            # Look for unit test
            unit_test = PROJECT_ROOT / 'tests' / 'unit' / 'modules' / module_name / f'test_{file_stem}.py'
            if unit_test.exists():
                test_files.add(str(unit_test.relative_to(PROJECT_ROOT)))
            
            # Look for integration test
            integration_test = PROJECT_ROOT / 'tests' / 'integration' / f'test_{module_name}_{file_stem}.py'
            if integration_test.exists():
                test_files.add(str(integration_test.relative_to(PROJECT_ROOT)))
        
        # Case 3: Core infrastructure (core/services/module_loader.py)
        elif path.parts[0] == 'core' and len(path.parts) >= 3:
            component = path.parts[1]  # e.g., services
            file_stem = path.stem
            
            # Look for unit test
            unit_test = PROJECT_ROOT / 'tests' / 'unit' / 'core' / component / f'test_{file_stem}.py'
            if unit_test.exists():
                test_files.add(str(unit_test.relative_to(PROJECT_ROOT)))
        
        # Case 4: Tools (tools/fengshui/agents/architect_agent.py)
        elif path.parts[0] == 'tools' and len(path.parts) >= 3:
            tool_name = path.parts[1]  # e.g., fengshui
            file_stem = path.stem
            
            # Look for unit test
            unit_test = PROJECT_ROOT / 'tests' / 'unit' / 'tools' / tool_name / f'test_{file_stem}.py'
            if unit_test.exists():
                test_files.add(str(unit_test.relative_to(PROJECT_ROOT)))
    
    return test_files


def run_tests(test_files: Set[str], timeout: int = 10) -> Tuple[bool, str, Dict]:
    """
    Run pytest on discovered test files
    
    Returns:
        (success, output, stats)
    """
    if not test_files:
        return True, "No tests to run", {"passed": 0, "failed": 0, "duration": 0}
    
    # Build pytest command (unit tests only for speed)
    test_paths = [str(PROJECT_ROOT / f) for f in test_files]
    cmd = [
        sys.executable, '-m', 'pytest',
        *test_paths,
        '-v',                    # Verbose
        '--tb=short',           # Short traceback
        '-m', 'unit',           # Unit tests only (fast)
        '--timeout', str(timeout),
        '--no-header',          # Less noise
        '--no-summary'          # We'll create our own summary
    ]
    
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout + 5,  # Give extra buffer
            cwd=PROJECT_ROOT
        )
        
        # Parse pytest output for statistics
        output = result.stdout + result.stderr
        stats = parse_pytest_output(output)
        
        success = result.returncode == 0
        return success, output, stats
    
    except subprocess.TimeoutExpired:
        return False, f"[ERROR] Tests timed out after {timeout}s", {"timeout": True}
    
    except Exception as e:
        return False, f"[ERROR] Failed to run tests: {e}", {"error": str(e)}


def parse_pytest_output(output: str) -> Dict:
    """Extract test statistics from pytest output"""
    stats = {
        "passed": 0,
        "failed": 0,
        "skipped": 0,
        "duration": 0.0
    }
    
    # Look for pytest summary line
    # Example: "====== 12 passed, 2 failed in 8.45s ======"
    import re
    
    passed_match = re.search(r'(\d+) passed', output)
    if passed_match:
        stats["passed"] = int(passed_match.group(1))
    
    failed_match = re.search(r'(\d+) failed', output)
    if failed_match:
        stats["failed"] = int(failed_match.group(1))
    
    skipped_match = re.search(r'(\d+) skipped', output)
    if skipped_match:
        stats["skipped"] = int(skipped_match.group(1))
    
    duration_match = re.search(r'in ([\d.]+)s', output)
    if duration_match:
        stats["duration"] = float(duration_match.group(1))
    
    return stats


def format_output(
    staged_files: List[str],
    test_files: Set[str],
    success: bool,
    output: str,
    stats: Dict
) -> str:
    """Format human-readable output"""
    lines = []
    lines.append("[GU WU] Pre-Commit Test Execution")
    lines.append("=" * 60)
    lines.append(f"[>] Staged files: {len(staged_files)} Python file(s)")
    lines.append(f"[>] Affected tests: {len(test_files)} test file(s)")
    lines.append("")
    
    if not test_files:
        lines.append("[OK] No tests found for staged files")
        lines.append("=" * 60)
        return "\n".join(lines)
    
    if "timeout" in stats:
        lines.append("[X] TESTS TIMED OUT")
        lines.append("=" * 60)
        lines.append("[!] Tests exceeded timeout limit")
        lines.append("[FIX] Possible causes:")
        lines.append("   • Slow test execution (check for network calls, large datasets)")
        lines.append("   • Infinite loops or deadlocks")
        lines.append("   • Too many tests staged (split into smaller commits)")
        lines.append("")
        lines.append("[!] To bypass: git commit --no-verify")
        lines.append("=" * 60)
        return "\n".join(lines)
    
    if "error" in stats:
        lines.append("[X] TEST EXECUTION ERROR")
        lines.append("=" * 60)
        lines.append(f"[!] {stats['error']}")
        lines.append("")
        lines.append("[!] To bypass: git commit --no-verify")
        lines.append("=" * 60)
        return "\n".join(lines)
    
    # Show test results
    if success:
        passed = stats.get('passed', 0)
        duration = stats.get('duration', 0)
        lines.append(f"[OK] {passed}/{passed} tests passed ({duration:.1f}s)")
        lines.append("=" * 60)
    else:
        passed = stats.get('passed', 0)
        failed = stats.get('failed', 0)
        total = passed + failed
        duration = stats.get('duration', 0)
        
        lines.append(f"[X] TESTS FAILED")
        lines.append("=" * 60)
        lines.append(f"[RESULT] {passed}/{total} tests passed ({duration:.1f}s)")
        lines.append("")
        
        # Extract failed test names from output
        failed_tests = extract_failed_tests(output)
        if failed_tests:
            lines.append("[FAILED TESTS]")
            for test_name, error_summary in failed_tests:
                lines.append(f"  • {test_name}")
                if error_summary:
                    lines.append(f"    → {error_summary}")
            lines.append("")
        
        lines.append("=" * 60)
        lines.append("[FIX] Fix failing tests before committing:")
        lines.append("   1. Run: pytest [test_file] -v")
        lines.append("   2. Debug and fix issues")
        lines.append("   3. Verify: python run_tests.py")
        lines.append("   4. Commit again")
        lines.append("")
        lines.append("[!] To bypass (NOT RECOMMENDED): git commit --no-verify")
        lines.append("=" * 60)
    
    return "\n".join(lines)


def extract_failed_tests(output: str) -> List[Tuple[str, str]]:
    """Extract failed test names and error summaries from pytest output"""
    import re
    
    failed_tests = []
    
    # Look for FAILED lines
    # Example: "tests/unit/test_api.py::test_create FAILED"
    failed_pattern = r'(tests/[^\s]+::[^\s]+)\s+FAILED'
    matches = re.finditer(failed_pattern, output)
    
    for match in matches:
        test_name = match.group(1)
        
        # Try to find error summary (next line after FAILED)
        # This is a simplification - real implementation would parse more carefully
        error_summary = "See output above for details"
        
        failed_tests.append((test_name, error_summary))
    
    return failed_tests


def main():
    """Main pre-commit test execution"""
    print("")
    
    # Get staged files
    staged_files = get_staged_python_files()
    
    if not staged_files:
        print("[GU WU] No Python files staged - skipping tests")
        sys.exit(0)
    
    # Check if too many files (performance limit)
    MAX_FILES = 20
    if len(staged_files) > MAX_FILES:
        print(f"[GU WU] {len(staged_files)} files staged (>{MAX_FILES}) - skipping pre-commit tests")
        print(f"[INFO] Run tests manually: python run_tests.py")
        sys.exit(0)
    
    # Find related tests
    test_files = find_related_test_files(staged_files)
    
    # Run tests
    success, output, stats = run_tests(test_files, timeout=10)
    
    # Format and display output
    formatted_output = format_output(staged_files, test_files, success, output, stats)
    print(formatted_output)
    print("")
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()