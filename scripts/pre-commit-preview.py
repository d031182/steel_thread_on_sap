#!/usr/bin/env python3
"""
Pre-commit hook for Preview Mode validation.

Validates module designs before allowing commits to proceed.
Runs quickly (<1s per module) to maintain developer flow.

Usage:
    # Install as git hook
    ln -s ../../scripts/pre-commit-preview.py .git/hooks/pre-commit
    
    # Or run manually
    python scripts/pre-commit-preview.py
"""

import sys
import subprocess
import json
from pathlib import Path
from typing import List, Dict, Any


def get_staged_module_files() -> List[str]:
    """Get list of staged files in modules/ directory."""
    try:
        result = subprocess.run(
            ['git', 'diff', '--cached', '--name-only', '--diff-filter=ACM'],
            capture_output=True,
            text=True,
            check=True
        )
        
        files = result.stdout.strip().split('\n')
        module_files = [f for f in files if f.startswith('modules/') and f]
        return module_files
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Error getting staged files: {e}")
        return []


def extract_changed_modules(files: List[str]) -> List[str]:
    """Extract unique module names from file paths."""
    modules = set()
    for file_path in files:
        parts = Path(file_path).parts
        if len(parts) >= 2 and parts[0] == 'modules':
            module_name = parts[1]
            # Check if module.json exists
            module_json = Path('modules') / module_name / 'module.json'
            if module_json.exists():
                modules.add(module_name)
    
    return sorted(modules)


def validate_module(module_name: str) -> Dict[str, Any]:
    """
    Validate a single module using Preview Mode.
    
    Returns:
        dict: Validation result with structure:
            {
                'module_name': str,
                'success': bool,
                'has_blockers': bool,
                'findings': list,
                'error': str (if failed)
            }
    """
    try:
        # Run Preview Mode validation
        result = subprocess.run(
            [
                sys.executable, '-m', 'tools.fengshui.preview',
                '--module', module_name,
                '--format', 'json'
            ],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if result.returncode == 0:
            # Parse JSON output
            data = json.loads(result.stdout)
            return {
                'module_name': module_name,
                'success': True,
                'has_blockers': data.get('has_blockers', False),
                'findings': data.get('findings', []),
                'validation_time': data.get('validation_time_seconds', 0)
            }
        else:
            return {
                'module_name': module_name,
                'success': False,
                'has_blockers': True,
                'error': result.stderr or 'Validation failed',
                'findings': []
            }
            
    except subprocess.TimeoutExpired:
        return {
            'module_name': module_name,
            'success': False,
            'has_blockers': True,
            'error': 'Validation timeout (>10s)',
            'findings': []
        }
    except json.JSONDecodeError as e:
        return {
            'module_name': module_name,
            'success': False,
            'has_blockers': True,
            'error': f'Invalid JSON response: {e}',
            'findings': []
        }
    except Exception as e:
        return {
            'module_name': module_name,
            'success': False,
            'has_blockers': True,
            'error': str(e),
            'findings': []
        }


def format_finding(finding: Dict[str, Any]) -> str:
    """Format a single finding for console output."""
    severity_icons = {
        'CRITICAL': '🔴',
        'HIGH': '🟠',
        'MEDIUM': '🟡',
        'LOW': '🔵',
        'INFO': '⚪'
    }
    
    icon = severity_icons.get(finding.get('severity', 'INFO'), '⚪')
    category = finding.get('category', 'Unknown')
    location = finding.get('location', '')
    message = finding.get('message', '')
    suggestion = finding.get('suggestion', '')
    
    output = f"  {icon} [{category}] {location}\n"
    output += f"     {message}\n"
    if suggestion:
        output += f"     💡 {suggestion}\n"
    
    return output


def main() -> int:
    """
    Main pre-commit validation logic.
    
    Returns:
        int: Exit code (0 = success, 1 = validation failed)
    """
    print("🔮 Preview Mode Pre-Commit Validation")
    print("=" * 60)
    
    # Get staged module files
    staged_files = get_staged_module_files()
    
    if not staged_files:
        print("✅ No module changes detected - skipping validation")
        return 0
    
    # Extract changed modules
    changed_modules = extract_changed_modules(staged_files)
    
    if not changed_modules:
        print(f"ℹ️  {len(staged_files)} file(s) staged in modules/, but no module.json found")
        print("   Skipping validation")
        return 0
    
    print(f"📦 Validating {len(changed_modules)} module(s): {', '.join(changed_modules)}")
    print()
    
    # Validate each module
    results = []
    total_blockers = 0
    
    for module_name in changed_modules:
        print(f"Validating module: {module_name}...", end=" ")
        result = validate_module(module_name)
        results.append(result)
        
        if result['success']:
            if result['has_blockers']:
                print("❌ BLOCKERS DETECTED")
                total_blockers += 1
            else:
                print(f"✅ PASSED ({result['validation_time']:.3f}s)")
        else:
            print("❌ VALIDATION ERROR")
            total_blockers += 1
    
    print()
    print("=" * 60)
    print("VALIDATION RESULTS")
    print("=" * 60)
    print()
    
    # Display detailed results
    for result in results:
        module_name = result['module_name']
        
        if not result['success']:
            print(f"❌ Module: {module_name} - VALIDATION ERROR")
            print(f"   Error: {result.get('error', 'Unknown error')}")
            print()
            continue
        
        if result['has_blockers']:
            print(f"❌ Module: {module_name} - BLOCKERS DETECTED")
        else:
            print(f"✅ Module: {module_name} - PASSED")
        
        findings = result.get('findings', [])
        if findings:
            # Group by severity
            by_severity = {}
            for finding in findings:
                severity = finding.get('severity', 'INFO')
                if severity not in by_severity:
                    by_severity[severity] = []
                by_severity[severity].append(finding)
            
            # Display critical/high findings
            for severity in ['CRITICAL', 'HIGH']:
                if severity in by_severity:
                    print(f"\n  {severity} Findings ({len(by_severity[severity])}):")
                    for finding in by_severity[severity]:
                        print(format_finding(finding))
            
            # Summarize medium/low/info
            for severity in ['MEDIUM', 'LOW', 'INFO']:
                if severity in by_severity:
                    count = len(by_severity[severity])
                    print(f"  {severity}: {count} finding(s)")
        
        print()
    
    # Final decision
    print("=" * 60)
    
    if total_blockers > 0:
        print(f"❌ COMMIT BLOCKED: {total_blockers} module(s) with violations")
        print()
        print("Please resolve CRITICAL/HIGH findings before committing.")
        print("Run 'python -m tools.fengshui.preview --module <name>' for details.")
        print()
        print("To bypass this check (NOT RECOMMENDED):")
        print("  git commit --no-verify")
        return 1
    else:
        print(f"✅ ALL VALIDATIONS PASSED: {len(changed_modules)} module(s) validated")
        print()
        print("Your commit meets module design standards.")
        return 0


if __name__ == '__main__':
    sys.exit(main())