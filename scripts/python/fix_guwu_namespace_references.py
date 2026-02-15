"""
Fix all remaining tests.guwu → tools.guwu references.

Run after migrating Gu Wu from tests/ to tools/.
"""

import re
from pathlib import Path

# Files to fix with their search/replace patterns
FIXES = {
    # Python files
    'tools/guwu/intelligence/dashboard.py': [
        ('python -m tests.guwu.intelligence.recommendations', 'python -m tools.guwu recommend'),
    ],
    'tools/guwu/intelligence/intelligence_hub.py': [
        ('python -m tests.guwu.intelligence.recommendations', 'python -m tools.guwu recommend'),
        ('python -m tests.guwu.intelligence.predictive', 'python -m tools.guwu predict'),
    ],
}

def fix_file(file_path: str, replacements: list):
    """Apply replacements to a file"""
    path = Path(file_path)
    if not path.exists():
        print(f"⚠️  Skipped: {file_path} (not found)")
        return False
    
    content = path.read_text(encoding='utf-8')
    original = content
    
    for old, new in replacements:
        content = content.replace(old, new)
    
    if content != original:
        path.write_text(content, encoding='utf-8')
        print(f"✅ Fixed: {file_path}")
        return True
    else:
        print(f"ℹ️  No changes: {file_path}")
        return False

def main():
    """Fix all files"""
    print("\n" + "="*70)
    print("Fixing Gu Wu Namespace References (tests.guwu → tools.guwu)")
    print("="*70 + "\n")
    
    fixed_count = 0
    for file_path, replacements in FIXES.items():
        if fix_file(file_path, replacements):
            fixed_count += 1
    
    print(f"\n{'='*70}")
    print(f"✅ Fixed {fixed_count}/{len(FIXES)} files")
    print("="*70 + "\n")
    
    print("NOTE: Documentation files (.md) contain many old references.")
    print("These are historical/archival and can be updated in a future cleanup.")
    print("\nKey fix: Intelligence engines now use unified CLI commands:")
    print("  • python -m tools.guwu recommend (not tests.guwu.intelligence.recommendations)")
    print("  • python -m tools.guwu intelligence (comprehensive)")
    print("  • python -m tools.guwu dashboard")
    print("  • python -m tools.guwu predict")

if __name__ == "__main__":
    main()