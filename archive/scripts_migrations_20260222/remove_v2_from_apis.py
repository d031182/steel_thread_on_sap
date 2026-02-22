#!/usr/bin/env python3
"""
Script to remove '/v2' from all API paths
Changes: /api/v2/ → /api/

Usage: python scripts/python/remove_v2_from_apis.py
"""

import os
import re
from pathlib import Path

# Files to update
FILE_PATTERNS = [
    "**/*.py",
    "**/*.js",
    "**/*.json",
    "**/*.md"
]

# Directories to exclude
EXCLUDE_DIRS = {
    ".git", "node_modules", "__pycache__", ".pytest_cache",
    "htmlcov", ".venv", "venv", "archive"
}

def should_process_file(file_path):
    """Check if file should be processed"""
    # Skip if in excluded directory
    for exclude_dir in EXCLUDE_DIRS:
        if exclude_dir in file_path.parts:
            return False
    
    # Skip this script itself
    if file_path.name == "remove_v2_from_apis.py":
        return False
    
    return True

def replace_in_file(file_path):
    """Replace /api/v2/ with /api/ in file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check if file contains /api/v2/
        if '/api/v2/' not in content:
            return 0
        
        # Replace all occurrences
        new_content = content.replace('/api/v2/', '/api/')
        
        # Count replacements
        count = content.count('/api/v2/')
        
        # Write back
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        return count
    
    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return 0

def main():
    """Main execution"""
    root = Path(".")
    total_files = 0
    total_replacements = 0
    
    print("=" * 60)
    print("Removing /v2 from API paths")
    print("=" * 60)
    print()
    
    # Process each file pattern
    for pattern in FILE_PATTERNS:
        for file_path in root.glob(pattern):
            if not file_path.is_file():
                continue
            
            if not should_process_file(file_path):
                continue
            
            count = replace_in_file(file_path)
            if count > 0:
                total_files += 1
                total_replacements += count
                print(f"✓ {file_path}: {count} replacement(s)")
    
    print()
    print("=" * 60)
    print(f"Complete: {total_replacements} replacements in {total_files} files")
    print("=" * 60)
    print()
    print("Next steps:")
    print("1. Review changes: git diff")
    print("2. Test application: python server.py")
    print("3. Run tests: pytest")
    print("4. Commit: git add . && git commit -m 'Remove /v2 from API paths'")

if __name__ == "__main__":
    main()