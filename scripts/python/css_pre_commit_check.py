#!/usr/bin/env python3
"""
CSS Pre-Commit Validation Hook
================================
Validates CSS files for proper variable usage before commit.
Part of CSS-005: Implement Pre-Commit CSS Checks

Usage:
    python scripts/python/css_pre_commit_check.py [files...]
    Or add to .git/hooks/pre-commit:
    python scripts/python/css_pre_commit_check.py $(git diff --cached --name-only --diff-filter=ACM | grep '.css$')
"""

import re
import sys
from pathlib import Path


def check_css_file(filepath):
    """
    Validate a CSS file for proper variable usage.
    
    Returns: (passed: bool, violations: list[str])
    """
    violations = []
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        return False, [f"Failed to read {filepath}: {e}"]
    
    # Skip css-variables.css itself (definitions, not usage)
    if filepath.endswith('css-variables.css'):
        return True, []
    
    # Check 1: Magic number detection (spacing/sizing)
    magic_pattern = r':\s*(\d+(?:\.\d+)?)(px|rem|em)\s*(?:;|!important)'
    magic_matches = re.findall(magic_pattern, content)
    
    if magic_matches:
        # Count violations (allow some in special cases)
        magic_count = len(magic_matches)
        if magic_count > 5:  # Threshold for warnings
            violations.append(
                f"WARNING: Found {magic_count} magic number values. "
                f"Consider using CSS variables from css-variables.css"
            )
    
    # Check 2: Ensure CSS imports variables file (for non-variable files)
    if 'static/css/' in filepath and not filepath.endswith('css-variables.css'):
        if "@import url('css-variables.css')" not in content:
            violations.append(
                "ERROR: CSS file should import css-variables.css at the top"
            )
    
    # Check 3: Timing values should use variables
    timing_pattern = r':\s*(0\.\d+s|[\d]+m?s)\s*(?:;|!important)'
    if 'dialog' in filepath.lower() or 'assistant' in filepath.lower():
        timing_matches = re.findall(timing_pattern, content)
        if timing_matches:
            violations.append(
                f"WARNING: Found {len(timing_matches)} timing values. "
                f"Consider using --duration-* variables"
            )
    
    # Check 4: Color values consistency
    color_pattern = r'color:\s*(#[0-9a-fA-F]{3}|#[0-9a-fA-F]{6})\b'
    color_matches = re.findall(color_pattern, content)
    if color_matches and len(color_matches) > 3:
        violations.append(
            f"INFO: Found {len(color_matches)} hardcoded colors. "
            f"Consider using --color-* variables for consistency"
        )
    
    # Check 5: No !important flag abuse (should be minimal)
    important_count = content.count('!important')
    if important_count > 10:
        violations.append(
            f"WARNING: Found {important_count} !important declarations. "
            f"Use CSS specificity instead where possible"
        )
    
    passed = len([v for v in violations if v.startswith('ERROR')]) == 0
    return passed, violations


def main():
    """Run CSS validation checks on provided files."""
    if len(sys.argv) < 2:
        print("CSS Pre-Commit Checker")
        print("Usage: python css_pre_commit_check.py file1.css file2.css ...")
        print("\nNo files provided. Checking common CSS files...")
        css_files = [
            'app_v2/static/css/ai-assistant.css',
            'modules/knowledge_graph_v2/frontend/styles/knowledge-graph-v2.css',
            'modules/ai_assistant/frontend/styles/markdown.css',
        ]
    else:
        css_files = [f for f in sys.argv[1:] if f.endswith('.css')]
    
    if not css_files:
        print("No CSS files to check")
        return 0
    
    all_passed = True
    total_violations = []
    
    for filepath in css_files:
        path = Path(filepath)
        if not path.exists():
            print(f"⚠️  File not found: {filepath}")
            continue
        
        passed, violations = check_css_file(filepath)
        
        if passed and not violations:
            print(f"✅ {filepath}")
        elif passed:
            print(f"⚠️  {filepath}")
            for violation in violations:
                print(f"   {violation}")
        else:
            print(f"❌ {filepath}")
            all_passed = False
            for violation in violations:
                print(f"   {violation}")
        
        total_violations.extend(violations)
    
    # Summary
    print("\n" + "="*60)
    error_count = len([v for v in total_violations if v.startswith('ERROR')])
    warning_count = len([v for v in total_violations if v.startswith('WARNING')])
    info_count = len([v for v in total_violations if v.startswith('INFO')])
    
    if error_count:
        print(f"❌ ERRORS: {error_count}")
    if warning_count:
        print(f"⚠️  WARNINGS: {warning_count}")
    if info_count:
        print(f"ℹ️  INFO: {info_count}")
    
    if all_passed:
        print("✅ All CSS files passed validation")
        return 0
    else:
        print("❌ CSS validation failed")
        return 1


if __name__ == '__main__':
    sys.exit(main())