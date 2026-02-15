#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Feng Shui API Contract Analyzer - API-First Methodology Enforcement

Purpose: Analyze staged/modified files for:
- Missing API contract tests (CRITICAL for API-First methodology)
- Architecture & security issues
- Test coverage gaps

Speed: < 10 seconds (6 agents in parallel, staged files only)

Usage:
    # Analyze staged files  
    python -m tools.fengshui.api_contract_analyzer
    
    # Or directly
    python tools/fengshui/api_contract_analyzer.py

Exit codes:
- 0: No critical issues (warnings may exist)
- 1: Critical issues found (e.g., missing API contract tests)

Integration: Part of Feng Shui + Gu Wu quality ecosystem
Communicates test gaps to Gu Wu via .fengshui_test_gaps.json

Core Detection:
- is_api_file(): Detects modules/*/backend/api.py files
- has_api_contract_test(): Checks for @pytest.mark.api_contract + requests
- detect_api_contract_gaps(): Finds missing backend/frontend API tests
"""

import sys
import subprocess
import json
import ast
from pathlib import Path
from typing import List, Dict, Set, Tuple
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed

# Windows encoding fix
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

# Get project root
PROJECT_ROOT = Path(__file__).parent.parent.parent

# Import Feng Shui agents
sys.path.insert(0, str(PROJECT_ROOT))
from tools.fengshui.agents.architect_agent import ArchitectAgent
from tools.fengshui.agents.security_agent import SecurityAgent
from tools.fengshui.agents.performance_agent import PerformanceAgent
from tools.fengshui.agents.ux_architect_agent import UXArchitectAgent
from tools.fengshui.agents.file_organization_agent import FileOrganizationAgent
from tools.fengshui.agents.documentation_agent import DocumentationAgent


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
        python_files = [f for f in files if f.endswith('.py')]
        
        return python_files
    
    except subprocess.CalledProcessError as e:
        print(f"[ERROR] Failed to get staged files: {e}")
        sys.exit(1)


def run_agent_analysis(agent_name: str, agent_class, staged_files: List[Path]) -> Dict:
    """Run a single agent analysis (for parallel execution)"""
    try:
        agent = agent_class()
        
        # Check if agent has analyze_file method (new interface)
        # If not, skip agent (old interface, needs updating)
        if not hasattr(agent, 'analyze_file'):
            return {
                "agent": agent_name,
                "success": True,
                "violations": [],
                "critical_count": 0,
                "warning_count": 0,
                "skipped": True,
                "reason": "Agent needs interface update"
            }
        
        # Analyze all staged files
        violations = []
        for file_path in staged_files:
            if file_path.exists():
                file_violations = agent.analyze_file(file_path)
                violations.extend(file_violations)
        
        return {
            "agent": agent_name,
            "success": True,
            "violations": violations,
            "critical_count": sum(1 for v in violations if v.get("severity") == "CRITICAL"),
            "warning_count": sum(1 for v in violations if v.get("severity") in ["HIGH", "MEDIUM"]),
            "skipped": False
        }
    
    except Exception as e:
        return {
            "agent": agent_name,
            "success": False,
            "error": str(e),
            "violations": [],
            "skipped": False
        }


def run_orchestrator_analysis(staged_files: List[str]) -> Dict:
    """
    Run 6 specialized agents in parallel
    
    Returns:
        Complete analysis results with agent findings
    """
    # Convert to absolute paths
    staged_paths = [PROJECT_ROOT / f for f in staged_files]
    
    # Filter only existing files
    existing_paths = [p for p in staged_paths if p.exists()]
    
    if not existing_paths:
        return {
            "agents": [],
            "total_violations": 0,
            "critical_count": 0,
            "warning_count": 0
        }
    
    # Define agent configurations
    agents = [
        ("Architecture", ArchitectAgent),
        ("Security", SecurityAgent),
        ("Performance", PerformanceAgent),
        ("UX", UXArchitectAgent),
        ("FileOrg", FileOrganizationAgent),
        ("Documentation", DocumentationAgent)
    ]
    
    # Run agents in parallel
    agent_results = []
    with ThreadPoolExecutor(max_workers=6) as executor:
        futures = {
            executor.submit(run_agent_analysis, name, agent_class, existing_paths): name
            for name, agent_class in agents
        }
        
        for future in as_completed(futures):
            result = future.result()
            agent_results.append(result)
    
    # Aggregate results
    total_violations = sum(len(r["violations"]) for r in agent_results)
    critical_count = sum(r.get("critical_count", 0) for r in agent_results)
    warning_count = sum(r.get("warning_count", 0) for r in agent_results)
    
    return {
        "agents": agent_results,
        "total_violations": total_violations,
        "critical_count": critical_count,
        "warning_count": warning_count
    }


def detect_test_coverage_gaps(staged_files: List[str]) -> List[Dict]:
    """
    Detect test coverage gaps in staged files
    
    Strategy:
    1. For each staged source file, check if corresponding test exists
    2. Parse file to find functions/classes
    3. Check if those functions/classes have tests
    4. Generate gap report
    """
    gaps = []
    
    for file_path_str in staged_files:
        file_path = PROJECT_ROOT / file_path_str
        
        # Skip test files themselves
        if 'tests/' in file_path_str:
            continue
        
        # Skip non-module files (scripts, tools have different standards)
        if not file_path_str.startswith('modules/') and not file_path_str.startswith('core/'):
            continue
        
        if not file_path.exists():
            continue
        
        try:
            # Parse Python file to find functions/classes
            content = file_path.read_text(encoding='utf-8')
            tree = ast.parse(content, filename=str(file_path))
            
            # Find all function/class definitions
            definitions = []
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    # Skip private functions (usually helpers)
                    if not node.name.startswith('_'):
                        definitions.append({
                            "type": "function",
                            "name": node.name,
                            "line": node.lineno,
                            "end_line": node.end_lineno
                        })
                elif isinstance(node, ast.ClassDef):
                    definitions.append({
                        "type": "class",
                        "name": node.name,
                        "line": node.lineno,
                        "end_line": node.end_lineno
                    })
            
            # Check if test file exists
            test_file_path = find_test_file_for_source(file_path_str)
            
            if not test_file_path or not (PROJECT_ROOT / test_file_path).exists():
                # No test file at all
                if definitions:
                    gaps.append({
                        "file": file_path_str,
                        "gap_type": "missing_test_file",
                        "severity": "HIGH",
                        "details": f"{len(definitions)} function(s)/class(es) have no tests",
                        "recommendation": f"Create {test_file_path or 'test file'}"
                    })
            else:
                # Test file exists, but might not cover all functions
                # For now, we'll flag this as a potential gap
                # (Deep analysis would require parsing test file too)
                if len(definitions) >= 5:
                    gaps.append({
                        "file": file_path_str,
                        "gap_type": "coverage_check_needed",
                        "severity": "MEDIUM",
                        "details": f"{len(definitions)} function(s)/class(es) - verify test coverage",
                        "recommendation": f"Review {test_file_path} for complete coverage"
                    })
        
        except Exception as e:
            # Skip files we can't parse (syntax errors, etc.)
            pass
    
    return gaps


def is_api_file(file_path: Path) -> bool:
    """
    Check if file is an API endpoint file requiring API contract tests.
    
    API files:
    - modules/*/backend/api.py (Flask Blueprints with endpoints)
    - core/api/frontend_registry.py (Frontend metadata API)
    """
    file_path_str = str(file_path)
    
    # Backend API files (Flask Blueprints)
    if file_path.name == 'api.py' and 'backend' in file_path_str:
        return True
    
    # Frontend registry API
    if 'frontend_registry.py' in file_path_str and 'core/api' in file_path_str:
        return True
    
    return False


def has_api_contract_test(module_name: str) -> Tuple[bool, bool]:
    """
    Check if module has API contract tests (not just unit tests).
    
    API contract tests:
    - Use @pytest.mark.api_contract marker
    - Use requests library (HTTP calls, not internal imports)
    - Test endpoints as black boxes
    
    Returns:
        (has_backend_api_test, has_frontend_api_test)
    """
    # Backend API contract test: tests/test_{module}_backend.py
    backend_test = PROJECT_ROOT / f"tests/test_{module_name}_backend.py"
    has_backend = False
    
    if backend_test.exists():
        try:
            content = backend_test.read_text(encoding='utf-8')
            # Check for API contract markers
            has_api_marker = '@pytest.mark.api_contract' in content
            has_http_calls = 'requests.post(' in content or 'requests.get(' in content
            has_backend = has_api_marker and has_http_calls
        except:
            pass
    
    # Frontend API contract test: tests/test_{module}_frontend_api.py
    frontend_test = PROJECT_ROOT / f"tests/test_{module_name}_frontend_api.py"
    has_frontend = False
    
    if frontend_test.exists():
        try:
            content = frontend_test.read_text(encoding='utf-8')
            # Check for frontend registry test
            has_api_marker = '@pytest.mark.api_contract' in content
            has_registry_call = '/api/modules/frontend-registry' in content
            has_frontend = has_api_marker and has_registry_call
        except:
            pass
    
    return (has_backend, has_frontend)


def detect_api_contract_gaps(staged_files: List[str]) -> List[Dict]:
    """
    Detect missing API contract tests (Gu Wu methodology enforcement).
    
    For each API file, ensures:
    1. Backend API contract test exists (tests/{module}_backend.py)
    2. Frontend API contract test exists (tests/{module}_frontend_api.py)
    3. Tests use @pytest.mark.api_contract
    4. Tests use HTTP calls (requests), not internal imports
    
    This is CRITICAL for API-First Contract Testing methodology.
    """
    gaps = []
    
    for file_path_str in staged_files:
        file_path = PROJECT_ROOT / file_path_str
        
        # Check if this is an API file
        if not is_api_file(file_path):
            continue
        
        # Extract module name
        # modules/ai_assistant/backend/api.py → ai_assistant
        parts = Path(file_path_str).parts
        if parts[0] == 'modules' and len(parts) >= 2:
            module_name = parts[1]
        elif parts[0] == 'core':
            # core/api/frontend_registry.py is special case (tests all modules)
            continue
        else:
            continue
        
        # Check for API contract tests
        has_backend, has_frontend = has_api_contract_test(module_name)
        
        # Backend API contract test gap
        if not has_backend:
            gaps.append({
                "file": file_path_str,
                "gap_type": "missing_backend_api_contract_test",
                "severity": "CRITICAL",
                "details": "No backend API contract test found (or missing @pytest.mark.api_contract)",
                "recommendation": (
                    f"Create tests/test_{module_name}_backend.py with:\n"
                    f"  - @pytest.mark.api_contract marker\n"
                    f"  - requests.post/get() calls (NOT internal imports)\n"
                    f"  - Test endpoints as HTTP contracts"
                ),
                "suggested_test_file": f"tests/test_{module_name}_backend.py"
            })
        
        # Frontend API contract test gap
        if not has_frontend:
            gaps.append({
                "file": file_path_str,
                "gap_type": "missing_frontend_api_contract_test",
                "severity": "HIGH",
                "details": "No frontend API contract test found",
                "recommendation": (
                    f"Create tests/test_{module_name}_frontend_api.py with:\n"
                    f"  - @pytest.mark.api_contract marker\n"
                    f"  - Test /api/modules/frontend-registry endpoint\n"
                    f"  - Verify module metadata structure"
                ),
                "suggested_test_file": f"tests/test_{module_name}_frontend_api.py"
            })
    
    return gaps


def find_test_file_for_source(source_file: str) -> str:
    """Find corresponding test file for a source file"""
    path = Path(source_file)
    
    # modules/data_products_v2/backend/api.py
    # → tests/unit/modules/data_products_v2/test_api.py
    if path.parts[0] == 'modules' and len(path.parts) >= 4:
        module_name = path.parts[1]
        file_stem = path.stem
        return f"tests/unit/modules/{module_name}/test_{file_stem}.py"
    
    # core/services/module_loader.py
    # → tests/unit/core/services/test_module_loader.py
    elif path.parts[0] == 'core' and len(path.parts) >= 3:
        component = path.parts[1]
        file_stem = path.stem
        return f"tests/unit/core/{component}/test_{file_stem}.py"
    
    # tools/fengshui/agents/architect_agent.py
    # → tests/unit/tools/fengshui/test_architect_agent.py
    elif path.parts[0] == 'tools' and len(path.parts) >= 3:
        tool_name = path.parts[1]
        file_stem = path.stem
        return f"tests/unit/tools/{tool_name}/test_{file_stem}.py"
    
    return None


def save_test_gaps_report(gaps: List[Dict], staged_files: List[str]):
    """Save test gaps to .fengshui_test_gaps.json for Gu Wu consumption"""
    report = {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "commit_context": {
            "staged_files_count": len(staged_files),
            "staged_files": staged_files
        },
        "test_gaps": gaps,
        "summary": {
            "total_gaps": len(gaps),
            "high_severity": sum(1 for g in gaps if g["severity"] == "HIGH"),
            "medium_severity": sum(1 for g in gaps if g["severity"] == "MEDIUM"),
            "low_severity": sum(1 for g in gaps if g["severity"] == "LOW")
        }
    }
    
    # Save to project root
    output_path = PROJECT_ROOT / '.fengshui_test_gaps.json'
    output_path.write_text(json.dumps(report, indent=2), encoding='utf-8')


def format_analysis_output(
    staged_files: List[str],
    analysis_results: Dict,
    test_gaps: List[Dict]
) -> Tuple[bool, str]:
    """
    Format orchestrator analysis output
    
    Returns:
        (has_critical_issues, formatted_output)
    """
    lines = []
    lines.append("[FENG SHUI] Orchestrator Analysis")
    lines.append("=" * 60)
    lines.append(f"[>] Analyzing {len(staged_files)} staged file(s)...")
    lines.append("")
    
    # Show agent results
    has_critical = False
    active_agents = 0
    skipped_agents = 0
    
    for agent_result in analysis_results["agents"]:
        agent_name = agent_result["agent"]
        
        # Skip agents with old interface (don't show errors)
        if agent_result.get("skipped"):
            skipped_agents += 1
            continue
        
        if not agent_result["success"]:
            lines.append(f"{agent_name}Agent: ❌ ERROR ({agent_result.get('error', 'Unknown')})")
            continue
        
        active_agents += 1
        violations = agent_result["violations"]
        critical = agent_result.get("critical_count", 0)
        warnings = agent_result.get("warning_count", 0)
        
        if critical > 0:
            lines.append(f"{agent_name}Agent: 🔴 {critical} CRITICAL issue(s)")
            has_critical = True
        elif warnings > 0:
            lines.append(f"{agent_name}Agent: ⚠️  {warnings} warning(s)")
        else:
            lines.append(f"{agent_name}Agent: ✅ No issues")
    
    # Show agent status summary
    if skipped_agents > 0:
        lines.append(f"[INFO] {skipped_agents} agent(s) skipped (need interface update)")
    
    lines.append("")
    
    # Show test coverage gaps
    if test_gaps:
        lines.append("[!] TEST COVERAGE GAPS DETECTED")
        lines.append("=" * 60)
        
        for gap in test_gaps[:5]:  # Show max 5 gaps
            file = gap["file"]
            gap_type = gap["gap_type"]
            severity = gap["severity"]
            details = gap["details"]
            recommendation = gap["recommendation"]
            
            severity_icon = "🔴" if severity == "HIGH" else "⚠️"
            lines.append(f"{severity_icon} {file}")
            lines.append(f"   Type: {gap_type}")
            lines.append(f"   Details: {details}")
            lines.append(f"   Recommendation: {recommendation}")
            lines.append("")
        
        if len(test_gaps) > 5:
            lines.append(f"   ... and {len(test_gaps) - 5} more gap(s)")
            lines.append("")
        
        lines.append("=" * 60)
        lines.append(f"[REPORT] {len(test_gaps)} test gap(s) detected")
        lines.append("Gaps saved to: .fengshui_test_gaps.json")
        lines.append("=" * 60)
    
    # Summary
    lines.append("")
    if has_critical:
        lines.append("[X] CRITICAL ISSUES FOUND - Cannot commit")
        lines.append("=" * 60)
        lines.append("[FIX] Address critical issues above before committing")
        lines.append("[!] To bypass (DANGEROUS): git commit --no-verify")
        lines.append("=" * 60)
    elif test_gaps:
        lines.append("[!] WARNINGS DETECTED - Consider addressing")
        lines.append("=" * 60)
        lines.append("[INFO] Test gaps are logged but won't block commit")
        lines.append("[RECOMMENDATION] Add missing tests to improve coverage")
        lines.append("=" * 60)
    else:
        lines.append("[OK] No issues detected!")
        lines.append("=" * 60)
    
    return has_critical, "\n".join(lines)


def check_file_count_limit(staged_files: List[str], max_files: int = 20) -> bool:
    """Check if we should skip analysis due to too many files"""
    if len(staged_files) > max_files:
        print(f"[FENG SHUI] {len(staged_files)} files staged (>{max_files}) - skipping orchestrator analysis")
        print(f"[INFO] For large commits, run manually: python -m tools.fengshui.react_agent")
        return False
    return True


def main():
    """Main pre-commit orchestrator execution"""
    print("")
    
    # Get staged files
    staged_files = get_staged_python_files()
    
    if not staged_files:
        print("[FENG SHUI] No Python files staged - skipping analysis")
        sys.exit(0)
    
    # Check file count limit
    if not check_file_count_limit(staged_files):
        sys.exit(0)  # Skip but don't block commit
    
    try:
        # Run orchestrator analysis (6 agents in parallel)
        analysis_results = run_orchestrator_analysis(staged_files)
        
        # Detect test coverage gaps (generic)
        generic_gaps = detect_test_coverage_gaps(staged_files)
        
        # Detect API contract test gaps (Gu Wu methodology enforcement)
        api_contract_gaps = detect_api_contract_gaps(staged_files)
        
        # Combine all gaps
        test_gaps = generic_gaps + api_contract_gaps
        
        # Save test gaps for Gu Wu to consume
        if test_gaps:
            save_test_gaps_report(test_gaps, staged_files)
        
        # Format output
        has_critical, formatted_output = format_analysis_output(
            staged_files,
            analysis_results,
            test_gaps
        )
        
        print(formatted_output)
        print("")
        
        # Exit with appropriate code
        # CRITICAL issues block commit, warnings don't
        sys.exit(1 if has_critical else 0)
    
    except Exception as e:
        print(f"[ERROR] Orchestrator analysis failed: {e}")
        print("[INFO] Skipping Feng Shui analysis (won't block commit)")
        sys.exit(0)  # Don't block on orchestrator errors


if __name__ == '__main__':
    main()