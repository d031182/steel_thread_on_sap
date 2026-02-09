#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Feng Shui Critical Security Check - Fast Pre-Commit Validation

Purpose: Detect CRITICAL security issues in staged files before commit
Speed: < 1 second (regex-based pattern matching only)
Usage: Called automatically by .git/hooks/pre-commit

Exit codes:
- 0: No critical issues (commit allowed)
- 1: Critical issues found (commit blocked)
"""

import sys
import subprocess
import re
from pathlib import Path
from typing import List, Dict, Tuple

# Windows encoding fix
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

# Get project root
PROJECT_ROOT = Path(__file__).parent.parent.parent

# Critical security patterns (high confidence, fast checks)
CRITICAL_PATTERNS = {
    'hardcoded_password': {
        'pattern': r'password\s*=\s*["\'][^"\']{3,}["\']',
        'message': 'Hardcoded password detected',
        'severity': 'CRITICAL'
    },
    'hardcoded_api_key': {
        'pattern': r'api[_-]?key\s*=\s*["\'][^"\']{10,}["\']',
        'message': 'Hardcoded API key detected',
        'severity': 'CRITICAL'
    },
    'hardcoded_secret': {
        'pattern': r'secret\s*=\s*["\'][^"\']{10,}["\']',
        'message': 'Hardcoded secret detected',
        'severity': 'CRITICAL'
    },
    'sql_injection': {
        'pattern': r'\.execute\s*\(\s*["\'].*%s.*["\'].*%',
        'message': 'Potential SQL injection (string formatting in query)',
        'severity': 'CRITICAL'
    },
    'command_injection': {
        'pattern': r'os\.system\s*\(.*\+',
        'message': 'Potential command injection (concatenation in os.system)',
        'severity': 'CRITICAL'
    },
    'eval_injection': {
        'pattern': r'eval\s*\(\s*input\s*\(',
        'message': 'Code injection via eval(input())',
        'severity': 'CRITICAL'
    }
}


def get_staged_files() -> List[str]:
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
        return [f for f in files if f.endswith('.py')]
    
    except subprocess.CalledProcessError as e:
        print(f"[ERROR] Failed to get staged files: {e}")
        sys.exit(1)


def scan_file_for_patterns(
    file_path: Path,
    patterns: Dict
) -> List[Tuple[str, int, str, str]]:
    """
    Scan file for critical security patterns
    
    Returns:
        List of (pattern_name, line_number, line_content, message)
    """
    violations = []
    
    try:
        content = file_path.read_text(encoding='utf-8')
        lines = content.split('\n')
        
        for line_num, line in enumerate(lines, 1):
            # Skip comments
            if line.strip().startswith('#'):
                continue
            
            for pattern_name, pattern_info in patterns.items():
                if re.search(pattern_info['pattern'], line, re.IGNORECASE):
                    violations.append((
                        pattern_name,
                        line_num,
                        line.strip(),
                        pattern_info['message']
                    ))
    
    except Exception as e:
        print(f"[WARNING] Could not scan {file_path}: {e}")
    
    return violations


def main():
    """Main critical security check"""
    print("[FENG SHUI] Critical Security Check")
    print("=" * 60)
    
    # Get staged Python files
    staged_files = get_staged_files()
    
    if not staged_files:
        print("[OK] No Python files staged")
        sys.exit(0)
    
    print(f"[>] Scanning {len(staged_files)} Python file(s)...")
    print()
    
    # Scan all staged files
    all_violations = {}
    for file_path_str in staged_files:
        file_path = PROJECT_ROOT / file_path_str
        
        if not file_path.exists():
            continue
        
        violations = scan_file_for_patterns(file_path, CRITICAL_PATTERNS)
        
        if violations:
            all_violations[file_path_str] = violations
    
    # Report results
    if all_violations:
        print("[X] CRITICAL SECURITY ISSUES FOUND")
        print("=" * 60)
        
        for file_path, violations in all_violations.items():
            print(f"\n📄 {file_path}")
            for pattern_name, line_num, line_content, message in violations:
                print(f"   Line {line_num}: {message}")
                print(f"   → {line_content}")
        
        print("\n" + "=" * 60)
        print("[!] CANNOT COMMIT - Fix security issues first")
        print()
        print("[FIX] How to fix:")
        print("   1. Move secrets to environment variables (.env)")
        print("   2. Use parameterized queries (not string formatting)")
        print("   3. Avoid eval() with user input")
        print("   4. Review and fix issues above")
        print()
        print("[!] To bypass (DANGEROUS!): git commit --no-verify")
        print("=" * 60)
        sys.exit(1)
    
    else:
        print("[OK] No critical security issues found!")
        print("=" * 60)
        sys.exit(0)


if __name__ == '__main__':
    main()