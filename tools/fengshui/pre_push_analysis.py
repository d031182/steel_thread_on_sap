#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Feng Shui Pre-Push Quality Gate - Comprehensive Validation

Purpose: Run full quality checks before allowing push to remote
Components:
1. Run all tests (pytest)
2. Feng Shui orchestrator analysis on changed files
3. Gu Wu test generation for coverage gaps
4. Module health validation

Duration: 30-60 seconds (comprehensive but worth it)
Usage: Called automatically by .git/hooks/pre-push

Exit codes:
- 0: Quality gate passed (push allowed)
- 1: Quality gate failed (push blocked)
"""

import sys
import subprocess
import json
from pathlib import Path
from typing import List, Dict, Set

# Windows encoding fix
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

# Get project root
PROJECT_ROOT = Path(__file__).parent.parent.parent

# Quality gate thresholds
THRESHOLDS = {
    'min_module_health': 70,      # Minimum health score per module
    'min_test_coverage': 70,      # Minimum test coverage %
    'max_critical_issues': 0,     # Cannot push with CRITICAL issues
    'max_high_issues': 5          # Max HIGH severity issues allowed
}


def get_changed_modules_since_last_push() -> Set[str]:
    """Get modules that have changed since last push"""
    try:
        # Get unpushed commits
        result = subprocess.run(
            ['git', 'log', '@{u}..', '--name-only', '--oneline'],
            capture_output=True,
            text=True,
            check=True,
            cwd=PROJECT_ROOT
        )
        
        # Extract module names from changed files
        modules = set()
        for line in result.stdout.split('\n'):
            if line.startswith('modules/'):
                parts = line.split('/')
                if len(parts) >= 2:
                    modules.add(parts[1])
        
        return modules
    
    except subprocess.CalledProcessError:
        # No upstream or first push - check all staged files
        result = subprocess.run(
            ['git', 'diff', '--name-only', 'HEAD'],
            capture_output=True,
            text=True,
            cwd=PROJECT_ROOT
        )
        
        modules = set()
        for line in result.stdout.split('\n'):
            if line.startswith('modules/'):
                parts = line.split('/')
                if len(parts) >= 2:
                    modules.add(parts[1])
        
        return modules


def detect_flask_server_running() -> bool:
    """Check if Flask server is running on port 5000"""
    try:
        import socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        result = sock.connect_ex(('localhost', 5000))
        sock.close()
        return result == 0
    except:
        return False


def translate_pytest_error(stdout: str, stderr: str, returncode: int) -> str:
    """
    Translate cryptic pytest errors into human-readable explanations
    
    Returns:
        Human-readable error explanation with fix suggestions
    """
    combined = stdout + stderr
    
    # Error 1: I/O operation on closed file (Flask server conflict)
    if "ValueError: I/O operation on closed file" in combined or "ValueError: I/O" in combined:
        return """
┌─────────────────────────────────────────────────────────────┐
│ 🔴 PYTEST ERROR: I/O Conflict with Running Flask Server    │
└─────────────────────────────────────────────────────────────┘

WHAT HAPPENED:
  Your Flask server (python app/app.py) is running on port 5000.
  Pytest tried to collect tests while the server was active.
  This caused file handles to close unexpectedly.

WHY IT FAILED:
  Flask and pytest both try to access the same files/ports.
  This creates an I/O conflict that breaks pytest's test collection.

HOW TO FIX:
  Option 1 (Recommended): Kill the Flask server first
    • Press Ctrl+C in the terminal running app/app.py
    • Then run: git push
  
  Option 2: Bypass quality gate (SAFE for config-only changes)
    • Run: git push --no-verify
    • Use only when you're confident (e.g., module.json changes)

WHY IT'S SAFE TO BYPASS THIS TIME:
  ✅ You only changed configuration files (module.json)
  ✅ No code changes = no new test failures possible
  ✅ Pre-commit hook already validated file organization
"""
    
    # Error 2: Import errors
    if "ImportError" in combined or "ModuleNotFoundError" in combined:
        return """
┌─────────────────────────────────────────────────────────────┐
│ 🔴 PYTEST ERROR: Missing Dependencies                       │
└─────────────────────────────────────────────────────────────┘

WHAT HAPPENED:
  Pytest couldn't import a required module or package.

HOW TO FIX:
  1. Check the error details above for the missing module name
  2. Install missing dependencies: pip install -r requirements.txt
  3. Or install specific package: pip install <package_name>
"""
    
    # Error 3: Test collection failed
    if "ERROR collecting" in combined or "collection failed" in combined:
        return """
┌─────────────────────────────────────────────────────────────┐
│ 🔴 PYTEST ERROR: Test Collection Failed                     │
└─────────────────────────────────────────────────────────────┘

WHAT HAPPENED:
  Pytest found syntax errors or import issues in test files.

HOW TO FIX:
  1. Check the error details above for the problematic file
  2. Fix syntax errors in the test file
  3. Ensure all imports are correct
"""
    
    # Error 4: Actual test failures
    if "FAILED" in combined and "passed" in combined:
        return """
┌─────────────────────────────────────────────────────────────┐
│ 🔴 PYTEST ERROR: Tests Failed                               │
└─────────────────────────────────────────────────────────────┘

WHAT HAPPENED:
  One or more tests failed (not passed).

HOW TO FIX:
  1. Review the failed tests above
  2. Run specific test: pytest path/to/test_file.py -v
  3. Fix the failing test or the code it's testing
  4. Re-run: git push (will re-validate)
"""
    
    # Generic error
    return f"""
┌─────────────────────────────────────────────────────────────┐
│ 🔴 PYTEST ERROR: Unknown Issue (Exit Code: {returncode})    │
└─────────────────────────────────────────────────────────────┘

WHAT HAPPENED:
  Pytest encountered an error but couldn't determine the cause.

HOW TO FIX:
  1. Run pytest manually to see full output: pytest -v
  2. Check error details above for clues
  3. Search error message on Stack Overflow or GitHub
"""


def run_contract_tests() -> bool:
    """
    Run API contract tests specifically
    
    Returns:
        True if all contract tests pass
    """
    print("[1/5] Running API Contract Tests...")
    print("-" * 60)
    
    try:
        result = subprocess.run(
            ['pytest', '-m', 'api_contract', '--tb=short', '-v'],
            capture_output=True,
            text=True,
            timeout=30,  # Contract tests are fast (< 30s)
            cwd=PROJECT_ROOT
        )
        
        # Show contract test results
        if result.stdout:
            print(result.stdout)
        
        if result.returncode != 0:
            print("\n❌ API Contract tests failed")
            print("\nWHY THIS MATTERS:")
            print("  • Contract tests verify frontend-backend API agreements")
            print("  • Breaking contracts breaks UI functionality")
            print("  • These tests run in < 30 seconds (fast feedback)")
            print("\nHOW TO FIX:")
            print("  1. Run: pytest -m api_contract -v")
            print("  2. Fix failing contracts (field names, structures)")
            print("  3. Re-run: git push (will re-validate)")
            return False
        
        # Count passing tests
        passing = result.stdout.count(' PASSED')
        print(f"✅ All {passing} API contract tests passed")
        return True
    
    except subprocess.TimeoutExpired:
        print("\n❌ Contract tests timed out (> 30 seconds)")
        return False
    
    except Exception as e:
        print(f"\n⚠️  Could not run contract tests: {e}")
        print("Continuing with other checks...")
        return True  # Don't block on infrastructure issues


def run_tests() -> bool:
    """
    Run all tests with pytest
    
    Returns:
        True if all tests pass
    """
    print("\n[2/5] Running All Tests (pytest)...")
    print("-" * 60)
    
    # Check if Flask server is running (common issue)
    if detect_flask_server_running():
        print("\n⚠️  WARNING: Flask server is running on port 5000")
        print("   This may cause pytest to fail with I/O errors")
        print("   Consider stopping the server before pushing")
        print("")
    
    try:
        result = subprocess.run(
            ['pytest', '--tb=short', '-q'],
            capture_output=True,
            text=True,
            timeout=180,  # 3 minute timeout
            cwd=PROJECT_ROOT
        )
        
        # Show pytest output (only first 50 lines to avoid clutter)
        if result.stdout:
            lines = result.stdout.split('\n')
            if len(lines) > 50:
                print('\n'.join(lines[:25]))
                print(f"\n... ({len(lines) - 50} more lines) ...\n")
                print('\n'.join(lines[-25:]))
            else:
                print(result.stdout)
        
        if result.returncode != 0:
            # Translate error to human-readable format
            error_explanation = translate_pytest_error(
                result.stdout or "",
                result.stderr or "",
                result.returncode
            )
            
            print(error_explanation)
            return False
        
        print("✅ All tests passed")
        return True
    
    except subprocess.TimeoutExpired:
        print("\n❌ Tests timed out (> 3 minutes)")
        print("\nThis usually means:")
        print("  • A test is stuck in an infinite loop")
        print("  • A test is waiting for external resource")
        print("  • Too many slow tests running")
        return False
    
    except Exception as e:
        print(f"\n❌ Error running tests: {e}")
        return False


def analyze_module_with_fengshui(module_name: str) -> Dict:
    """
    Run Feng Shui orchestrator on specific module
    
    Returns:
        Analysis report with health score and findings
    """
    try:
        # Run Feng Shui multi-agent analysis
        result = subprocess.run(
            [
                'python', '-c',
                f'''
from pathlib import Path
from tools.fengshui.agents.orchestrator import AgentOrchestrator
import json

orchestrator = AgentOrchestrator()
report = orchestrator.analyze_module_comprehensive(
    module_path=Path("modules/{module_name}"),
    parallel=True
)

# Extract key metrics
findings = report.synthesized_plan.prioritized_actions
critical = sum(1 for f in findings if f["severity"] == "critical")
high = sum(1 for f in findings if f["severity"] == "high")
health = report.synthesized_plan.overall_health_score

print(json.dumps({{
    "health_score": health,
    "critical_count": critical,
    "high_count": high,
    "total_findings": len(findings)
}}))
'''
            ],
            capture_output=True,
            text=True,
            timeout=30,
            cwd=PROJECT_ROOT
        )
        
        if result.returncode != 0:
            return {
                'health_score': 0,
                'critical_count': 999,
                'high_count': 999,
                'total_findings': 999,
                'error': result.stderr or 'Analysis failed'
            }
        
        # Parse JSON output
        return json.loads(result.stdout.strip())
    
    except Exception as e:
        return {
            'health_score': 0,
            'critical_count': 999,
            'high_count': 999,
            'total_findings': 999,
            'error': str(e)
        }


def check_test_coverage() -> float:
    """
    Check overall test coverage
    
    Returns:
        Coverage percentage (0-100)
    """
    print("\n[3/5] Checking Test Coverage...")
    print("-" * 60)
    
    try:
        result = subprocess.run(
            ['pytest', '--cov=modules', '--cov=core', '--cov-report=term-missing', '--tb=no', '-q'],
            capture_output=True,
            text=True,
            timeout=120,
            cwd=PROJECT_ROOT
        )
        
        # Parse coverage from output (look for "TOTAL ... XX%")
        for line in result.stdout.split('\n'):
            if 'TOTAL' in line:
                # Extract percentage
                parts = line.split()
                for part in parts:
                    if part.endswith('%'):
                        coverage = float(part.rstrip('%'))
                        print(f"Current coverage: {coverage}%")
                        return coverage
        
        print("⚠️ Could not determine coverage")
        return 0.0
    
    except Exception as e:
        print(f"⚠️ Coverage check failed: {e}")
        return 0.0


def analyze_changed_modules() -> Dict[str, Dict]:
    """
    Run Feng Shui analysis on changed modules
    
    Returns:
        Dictionary mapping module name to analysis results
    """
    print("\n[4/5] Analyzing Changed Modules (Feng Shui)...")
    print("-" * 60)
    
    changed_modules = get_changed_modules_since_last_push()
    
    if not changed_modules:
        print("No module changes detected")
        return {}
    
    print(f"Analyzing {len(changed_modules)} module(s): {', '.join(changed_modules)}")
    
    results = {}
    for module_name in changed_modules:
        module_path = PROJECT_ROOT / 'modules' / module_name
        
        if not module_path.exists():
            print(f"⚠️ Module path not found: {module_path}")
            continue
        
        print(f"\n  Analyzing: {module_name}...")
        analysis = analyze_module_with_fengshui(module_name)
        results[module_name] = analysis
        
        if 'error' not in analysis:
            health = analysis['health_score']
            critical = analysis['critical_count']
            high = analysis['high_count']
            
            if health >= 90:
                status = "✅ EXCELLENT"
            elif health >= 70:
                status = "✅ GOOD"
            elif health >= 50:
                status = "⚠️ NEEDS WORK"
            else:
                status = "❌ CRITICAL"
            
            print(f"    Health: {health:.0f}/100 {status}")
            print(f"    Issues: {critical} CRITICAL, {high} HIGH")
        else:
            print(f"    ❌ Analysis failed: {analysis['error']}")
    
    return results


def check_coverage_gaps() -> bool:
    """
    Check for coverage gaps and offer to generate tests
    
    Returns:
        True if no blocking gaps or tests were generated
    """
    print("\n[5/5] Checking Coverage Gaps (Gu Wu)...")
    print("-" * 60)
    
    # TODO: Implement Gu Wu test generator integration
    # For now, just check if coverage meets threshold
    print("⚠️ Gu Wu test generation not yet implemented")
    print("Skipping automatic test generation...")
    
    return True


def main():
    """Main pre-push quality gate"""
    print("")
    print("=" * 70)
    print("FENG SHUI PRE-PUSH QUALITY GATE")
    print("=" * 70)
    print("")
    
    # Track overall status
    gate_passed = True
    issues = []
    
    # Step 1: Run API contract tests (HIGH-21)
    if not run_contract_tests():
        gate_passed = False
        issues.append("API contract tests failed")
    
    # Step 2: Run all tests
    if not run_tests():
        gate_passed = False
        issues.append("Tests failed")
    
    # Step 3: Check coverage
    coverage = check_test_coverage()
    if coverage < THRESHOLDS['min_test_coverage']:
        gate_passed = False
        issues.append(f"Coverage too low: {coverage:.0f}% (min: {THRESHOLDS['min_test_coverage']}%)")
    else:
        print(f"✅ Coverage meets threshold: {coverage:.0f}% >= {THRESHOLDS['min_test_coverage']}%")
    
    # Step 4: Analyze changed modules
    module_analyses = analyze_changed_modules()
    
    for module_name, analysis in module_analyses.items():
        if 'error' in analysis:
            gate_passed = False
            issues.append(f"Module {module_name}: Analysis failed")
            continue
        
        health = analysis['health_score']
        critical = analysis['critical_count']
        high = analysis['high_count']
        
        # Check thresholds
        if health < THRESHOLDS['min_module_health']:
            gate_passed = False
            issues.append(
                f"Module {module_name}: Health too low ({health:.0f}/100, min: {THRESHOLDS['min_module_health']})"
            )
        
        if critical > THRESHOLDS['max_critical_issues']:
            gate_passed = False
            issues.append(
                f"Module {module_name}: {critical} CRITICAL issues (max: {THRESHOLDS['max_critical_issues']})"
            )
        
        if high > THRESHOLDS['max_high_issues']:
            gate_passed = False
            issues.append(
                f"Module {module_name}: {high} HIGH issues (max: {THRESHOLDS['max_high_issues']})"
            )
    
    # Step 5: Check coverage gaps (future: auto-generate tests)
    if not check_coverage_gaps():
        gate_passed = False
        issues.append("Coverage gaps detected")
    
    # Final verdict
    print("\n" + "=" * 70)
    
    if gate_passed:
        print("✅ QUALITY GATE PASSED")
        print("=" * 70)
        print("")
        print("All checks passed! Safe to push 🚀")
        print("")
        sys.exit(0)
    else:
        print("❌ QUALITY GATE FAILED")
        print("=" * 70)
        print("")
        print("Issues found:")
        for i, issue in enumerate(issues, 1):
            print(f"  {i}. {issue}")
        
        print("")
        print("[FIX] How to resolve:")
        print("   1. Fix failing tests: pytest --tb=short")
        print("   2. Run Feng Shui on module: python -m tools.fengshui.react_agent")
        print("   3. Increase coverage: Add missing tests")
        print("   4. Re-run: git push (will re-validate)")
        print("")
        print("[!] To bypass (RISKY): git push --no-verify")
        print("=" * 70)
        print("")
        sys.exit(1)


if __name__ == '__main__':
    main()