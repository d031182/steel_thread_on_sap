#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Feng Shui Pre-Commit Hook - Validates staged files against project standards

Purpose: Prevent violations from entering repository by checking at commit time
Usage: Called automatically by .git/hooks/pre-commit
Bypass: git commit --no-verify (use sparingly!)

Exit codes:
- 0: All checks passed (commit allowed)
- 1: Violations found (commit blocked)
"""

import sys
import subprocess
import os
from pathlib import Path
from typing import List

# Windows encoding fix (see docs/knowledge/guidelines/windows-encoding-standard.md)
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

# Get project root (2 levels up from this file)
PROJECT_ROOT = Path(__file__).parent.parent.parent

# Feng Shui rules based on docs/knowledge/guidelines/feng-shui-phase5-file-organization.md
ALLOWED_ROOT_FILES = {
    '.clinerules',
    'PROJECT_TRACKER.md',
    'README.md',
    '.gitignore',
    'package.json',
    'requirements.txt',
    'setup.py',
    'pyproject.toml',
    'pytest.ini',
    'conftest.py',
    'server.py',
    'playwright.config.js'
}


def get_staged_files() -> List[str]:
    """Get list of files staged for commit"""
    try:
        result = subprocess.run(
            ['git', 'diff', '--cached', '--name-only', '--diff-filter=ACM'],
            capture_output=True,
            text=True,
            check=True,
            cwd=PROJECT_ROOT
        )
        return [f.strip() for f in result.stdout.split('\n') if f.strip()]
    except subprocess.CalledProcessError as e:
        print(f"[ERROR] Error getting staged files: {e}")
        sys.exit(1)


def check_root_markdown_files(staged_files: List[str]) -> List[str]:
    """Check for unauthorized .md files in root"""
    violations = []
    
    for file in staged_files:
        if '/' not in file and file.endswith('.md'):
            if file not in ALLOWED_ROOT_FILES:
                violations.append(
                    f"[X] {file}: Markdown file not allowed in root\n"
                    f"   -> Move to docs/knowledge/ or delete\n"
                    f"   -> Allowed root files: {', '.join(sorted(ALLOWED_ROOT_FILES))}"
                )
    
    return violations


def check_test_file_locations(staged_files: List[str]) -> List[str]:
    """Check for test files in wrong locations"""
    violations = []
    
    for file in staged_files:
        # Check scripts/python/ for test files
        if file.startswith('scripts/python/'):
            filename = os.path.basename(file)
            if (filename.startswith('test_') or filename.endswith('_test.py') or
                filename.startswith('check_') or filename.startswith('verify_')):
                violations.append(
                    f"[X] {file}: Test/validation file in wrong location\n"
                    f"   -> Move to tests/integration/ or tests/unit/\n"
                    f"   -> See .clinerules Section 6 (Gu Wu Testing)"
                )
    
    return violations


def check_docs_location(staged_files: List[str]) -> List[str]:
    """Check for .md files in docs/ root (should be in docs/knowledge/)"""
    violations = []
    
    for file in staged_files:
        if file.startswith('docs/') and file.endswith('.md'):
            # Allow docs/archive/ and docs/knowledge/
            if not (file.startswith('docs/archive/') or 
                    file.startswith('docs/knowledge/') or
                    file in ['docs/FENG_SHUI_AUDIT_2026-02-01.md', 
                            'docs/FENG_SHUI_AUDIT_2026-02-05.md',
                            'docs/FENG_SHUI_ROUTINE_REQUIREMENTS.md',
                            'docs/PYTHON_MIGRATION_PLAN.md']):
                violations.append(
                    f"[X] {file}: Documentation file in wrong location\n"
                    f"   -> Move to docs/knowledge/ (see knowledge vault structure)\n"
                    f"   -> Allowed: docs/archive/, docs/knowledge/, audit docs"
                )
    
    return violations


def check_temporary_files(staged_files: List[str]) -> List[str]:
    """Check for temporary/debug files that shouldn't be committed"""
    violations = []
    
    for file in staged_files:
        filename = os.path.basename(file)
        
        # Temporary files
        if (filename.startswith('temp_') or 
            filename.startswith('debug_') or
            '_old' in filename or
            filename.endswith('.bak') or
            filename.endswith('~')):
            violations.append(
                f"[X] {file}: Temporary/backup file should not be committed\n"
                f"   -> Delete or add to .gitignore"
            )
    
    return violations


def main():
    """Main pre-commit validation"""
    print("[FENG SHUI] Pre-Commit Check")
    print("=" * 60)
    
    # Get staged files
    staged_files = get_staged_files()
    
    if not staged_files:
        print("[OK] No files staged for commit")
        sys.exit(0)
    
    print(f"[>] Checking {len(staged_files)} staged file(s)...")
    print()
    
    # Run all checks
    all_violations = []
    all_violations.extend(check_root_markdown_files(staged_files))
    all_violations.extend(check_test_file_locations(staged_files))
    all_violations.extend(check_docs_location(staged_files))
    all_violations.extend(check_temporary_files(staged_files))
    
    # Report results
    if all_violations:
        print("[X] FENG SHUI VIOLATIONS FOUND")
        print("=" * 60)
        for violation in all_violations:
            print(violation)
            print()
        
        print("=" * 60)
        print("[FIX] HOW TO FIX:")
        print("   1. Run: python tools/fengshui/autofix.py")
        print("   2. Or manually fix violations above")
        print("   3. Stage fixed files: git add <files>")
        print("   4. Commit again")
        print()
        print("[!] To bypass (use sparingly): git commit --no-verify")
        print("=" * 60)
        sys.exit(1)
    else:
        print("[OK] All Feng Shui checks passed!")
        print("=" * 60)
        sys.exit(0)


if __name__ == '__main__':
    main()