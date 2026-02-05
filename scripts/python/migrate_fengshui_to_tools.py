#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Migrate Feng Shui Framework: core/quality/ -> tools/fengshui/

This script updates all import references throughout the codebase after
moving Feng Shui framework to follow SoC principles (dev tools separate from runtime).

Run after:
    git mv core/quality/feng_shui_score.py tools/fengshui/
    git mv core/quality/module_quality_gate.py tools/fengshui/
"""

import os
import re
import sys
from pathlib import Path

# Force UTF-8 encoding for Windows
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

# Project root
PROJECT_ROOT = Path(__file__).parent.parent.parent

# Files that need import updates
FILES_TO_UPDATE = [
    # Documentation that references old paths
    "docs/knowledge/guidelines/feng-shui-separation-of-concerns.md",
    "docs/knowledge/guidelines/feng-shui-phase5-file-organization.md",
    "docs/knowledge/guidelines/module-quality-gate.md",
    "docs/knowledge/architecture/feng-shui-guwu-separation.md",
    "docs/knowledge/INDEX.md",
    ".clinerules",
    "README.md",
    
    # Any Python files that might import these modules
    # (None currently, but included for completeness)
]

def update_file(file_path: Path):
    """Update import statements and path references in a file"""
    if not file_path.exists():
        print(f"[WARN] Skipping {file_path} (not found)")
        return False
    
    content = file_path.read_text(encoding='utf-8')
    original = content
    
    # Update import statements
    content = re.sub(
        r'from core\.quality import',
        'from tools.fengshui import',
        content
    )
    content = re.sub(
        r'import core\.quality\.',
        'import tools.fengshui.',
        content
    )
    
    # Update CLI command paths
    content = re.sub(
        r'python core/quality/feng_shui_score\.py',
        'python tools/fengshui/feng_shui_score.py',
        content
    )
    content = re.sub(
        r'python core/quality/module_quality_gate\.py',
        'python tools/fengshui/module_quality_gate.py',
        content
    )
    
    # Update markdown code blocks with paths
    content = re.sub(
        r'core/quality/',
        'tools/fengshui/',
        content
    )
    
    if content != original:
        file_path.write_text(content, encoding='utf-8')
        print(f"[OK] Updated {file_path.relative_to(PROJECT_ROOT)}")
        return True
    else:
        print(f"    No changes needed in {file_path.relative_to(PROJECT_ROOT)}")
        return False

def main():
    print("=" * 70)
    print("FENG SHUI MIGRATION: core/quality/ -> tools/fengshui/")
    print("=" * 70)
    print()
    
    updated_count = 0
    
    for file_rel_path in FILES_TO_UPDATE:
        file_path = PROJECT_ROOT / file_rel_path
        if update_file(file_path):
            updated_count += 1
    
    print()
    print("=" * 70)
    print(f"Migration complete: {updated_count} files updated")
    print("=" * 70)
    print()
    print("Next steps:")
    print("  1. Remove empty core/quality directory: git rm -r core/quality")
    print("  2. Test Feng Shui commands:")
    print("     python tools/fengshui/feng_shui_score.py")
    print("     python tools/fengshui/module_quality_gate.py knowledge_graph")
    print("  3. Stage changes: git add tools/ docs/ .clinerules")
    print("  4. Commit: git commit -m 'refactor: move Feng Shui to tools/ (SoC)'")

if __name__ == '__main__':
    main()