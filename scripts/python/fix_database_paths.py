#!/usr/bin/env python3
"""
Fix incorrect database paths from core/databases/sqlite/*.db to databases/*.db
This updates all Python files that use the old path structure.
"""
import os
import re
from pathlib import Path

# Define the project root
PROJECT_ROOT = Path(__file__).parent.parent.parent

# Old pattern: core/databases/sqlite/*.db
# New pattern: databases/*.db
OLD_PATTERN = r'core/databases/sqlite/([^"\']+\.db)'
NEW_REPLACEMENT = r'databases/\1'

def fix_file(file_path: Path) -> tuple[bool, int]:
    """Fix database paths in a single file.
    
    Returns:
        (changed, count) - whether file was modified and number of replacements
    """
    try:
        content = file_path.read_text(encoding='utf-8')
        new_content, count = re.subn(OLD_PATTERN, NEW_REPLACEMENT, content)
        
        if count > 0:
            file_path.write_text(new_content, encoding='utf-8')
            return True, count
        return False, 0
    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return False, 0

def main():
    """Find and fix all files with incorrect database paths."""
    files_to_check = [
        'scripts/python/compare_hana_sqlite_schemas.py',
        'scripts/python/generate_p2p_transactions.py',
        'scripts/python/populate_master_data_from_hana.py',
        'scripts/python/populate_from_hana_master_data.py',
        'scripts/python/rebuild_sqlite_from_hana_csn.py',
    ]
    
    total_files = 0
    total_replacements = 0
    
    print("Fixing database paths...")
    print(f"OLD: core/databases/sqlite/*.db")
    print(f"NEW: databases/*.db")
    print("-" * 60)
    
    for file_rel in files_to_check:
        file_path = PROJECT_ROOT / file_rel
        if file_path.exists():
            changed, count = fix_file(file_path)
            if changed:
                total_files += 1
                total_replacements += count
                print(f"✓ {file_rel}: {count} replacement(s)")
            else:
                print(f"  {file_rel}: No changes needed")
        else:
            print(f"✗ {file_rel}: File not found")
    
    print("-" * 60)
    print(f"Summary: {total_files} file(s) modified, {total_replacements} replacement(s)")
    
    # Note about archived test file
    archived_test = 'archive/tests_backup_2026_02_15/integration/test_data_products_v2_database_path.py'
    if (PROJECT_ROOT / archived_test).exists():
        print(f"\nNote: {archived_test} also contains old path but is archived")

if __name__ == '__main__':
    main()