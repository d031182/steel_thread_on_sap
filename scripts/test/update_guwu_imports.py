#!/usr/bin/env python3
"""
Automated script to update all imports from tools.guwu -> tools.guwu
Part of Gu Wu framework reorganization (Issue #12)
"""

import re
from pathlib import Path
from typing import List, Tuple

def find_files_to_update(root_dir: Path) -> List[Path]:
    """Find all Python and config files that might contain guwu imports"""
    patterns = ['**/*.py', '**/*.md', '**/*.ini', '**/*.txt']
    files = []
    
    exclude_dirs = {'.git', 'node_modules', '__pycache__', '.pytest_cache', 
                   'htmlcov', 'test-results', 'steel_thread_on_sap.egg-info'}
    
    for pattern in patterns:
        for file_path in root_dir.rglob(pattern):
            # Skip excluded directories
            if any(excluded in file_path.parts for excluded in exclude_dirs):
                continue
            files.append(file_path)
    
    return files

def update_file_imports(file_path: Path) -> Tuple[bool, int]:
    """
    Update imports in a single file
    
    Returns:
        (changed, count) - Whether file was modified and number of replacements
    """
    try:
        content = file_path.read_text(encoding='utf-8')
        original_content = content
        
        # Pattern 1: from tools.guwu -> from tools.guwu
        content = re.sub(r'from tests\.guwu', 'from tools.guwu', content)
        
        # Pattern 2: import tools.guwu -> import tools.guwu
        content = re.sub(r'import tests\.guwu', 'import tools.guwu', content)
        
        # Pattern 3: tools/guwu/ paths -> tools/guwu/
        content = re.sub(r'tools/guwu/', 'tools/guwu/', content)
        
        # Pattern 4: tools\guwu\ paths (Windows) -> tools\\guwu\\
        content = re.sub(r'tests\\\\guwu\\\\', r'tools\\guwu\\', content)
        
        # Count changes
        changes = len(re.findall(r'tools\.guwu|tools/guwu', content)) - \
                 len(re.findall(r'tools\.guwu|tools/guwu', original_content))
        
        if content != original_content:
            file_path.write_text(content, encoding='utf-8')
            return True, changes
        
        return False, 0
    
    except Exception as e:
        print(f"  [ERROR] Processing {file_path}: {e}")
        return False, 0

def main():
    """Main execution"""
    print("=" * 70)
    print("Gu Wu Import Updater: tests.guwu -> tools.guwu")
    print("=" * 70)
    
    root_dir = Path(__file__).parent.parent.parent
    print(f"\nScanning project: {root_dir}")
    
    # Find files
    files = find_files_to_update(root_dir)
    print(f"Found {len(files)} files to check")
    
    # Update files
    modified_count = 0
    total_changes = 0
    
    print("\nUpdating files...")
    for file_path in files:
        changed, count = update_file_imports(file_path)
        if changed:
            modified_count += 1
            total_changes += count
            print(f"  [OK] {file_path.relative_to(root_dir)} ({count} changes)")
    
    # Summary
    print("\n" + "=" * 70)
    print(f"Import Update Complete!")
    print("=" * 70)
    print(f"Files modified: {modified_count}")
    print(f"Total replacements: {total_changes}")
    print("\nNext steps:")
    print("1. Run: pytest --collect-only  (verify imports work)")
    print("2. Run: pytest tests/unit/guwu/  (run Gu Wu unit tests)")
    print("3. Commit changes if tests pass")
    print("=" * 70)

if __name__ == '__main__':
    main()