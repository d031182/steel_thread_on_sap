# -*- coding: utf-8 -*-
"""
Check Quality Gate Status for All Modules
==========================================
Windows-compatible script to check quality status across all modules.
"""

import sys
import os
import subprocess

# Windows UTF-8 encoding fix
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

# Add project root to path
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(script_dir))
sys.path.insert(0, project_root)

# List of modules to check
MODULES = [
    'api_playground',
    'csn_validation',
    'data_products',
    'debug_mode',
    'feature_manager',
    'hana_connection',
    'knowledge_graph',
    'login_manager',
    'log_manager',
    'sqlite_connection',
    'sql_execution'
]

def check_module(module_name):
    """Run quality gate on a module and return status"""
    cmd = [sys.executable, 'core/quality/module_quality_gate.py', module_name]
    
    try:
        result = subprocess.run(
            cmd,
            cwd=project_root,
            capture_output=True,
            text=True,
            timeout=30
        )
        
        output = result.stdout
        
        # Parse output for status
        passed = failed = errors = warnings = 0
        
        for line in output.split('\n'):
            if 'PASSED:' in line:
                passed = int(line.split(':')[1].strip())
            elif 'ERRORS:' in line:
                errors = int(line.split(':')[1].strip())
            elif 'WARNINGS:' in line:
                warnings = int(line.split(':')[1].strip())
            elif 'QUALITY GATE: FAILED' in line:
                failed = 1
            elif 'QUALITY GATE: PASSED' in line:
                failed = 0
        
        status = '✅ PASSED' if failed == 0 else '❌ FAILED'
        
        return {
            'module': module_name,
            'status': status,
            'passed': passed,
            'errors': errors,
            'warnings': warnings,
            'output': output
        }
        
    except Exception as e:
        return {
            'module': module_name,
            'status': '⚠️ ERROR',
            'passed': 0,
            'errors': 999,
            'warnings': 0,
            'output': str(e)
        }

def main():
    print("=" * 80)
    print("MODULE QUALITY GATE - ALL MODULES CHECK")
    print("=" * 80)
    print()
    
    results = []
    
    for module in MODULES:
        print(f"Checking {module}...", end=' ', flush=True)
        result = check_module(module)
        results.append(result)
        print(result['status'])
    
    print()
    print("=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print()
    
    passed_count = sum(1 for r in results if '✅' in r['status'])
    failed_count = sum(1 for r in results if '❌' in r['status'])
    
    print(f"{'Module':<20} {'Status':<12} {'Passed':<8} {'Errors':<8} {'Warnings':<8}")
    print("-" * 80)
    
    for r in results:
        print(f"{r['module']:<20} {r['status']:<12} {r['passed']:<8} {r['errors']:<8} {r['warnings']:<8}")
    
    print()
    print(f"✅ PASSING: {passed_count}/{len(MODULES)} modules ({passed_count*100//len(MODULES)}%)")
    print(f"❌ FAILING: {failed_count}/{len(MODULES)} modules ({failed_count*100//len(MODULES)}%)")
    print()
    
    if failed_count > 0:
        print("FAILED MODULES DETAILS:")
        print("=" * 80)
        for r in results:
            if '❌' in r['status']:
                print(f"\n### {r['module']} ###")
                # Print only ERROR and WARNING lines
                for line in r['output'].split('\n'):
                    if 'ERROR' in line or 'WARNING' in line or 'FAILED' in line:
                        print(f"  {line}")

if __name__ == '__main__':
    main()