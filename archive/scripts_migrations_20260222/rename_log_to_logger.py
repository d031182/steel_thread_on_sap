#!/usr/bin/env python3
"""
Rename module: log → logger

This script performs a comprehensive rename of the log module to logger.
"""

import os
from pathlib import Path

def replace_in_file(filepath, replacements):
    """Replace text in file using string replacement"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        for old_text, new_text in replacements:
            content = content.replace(old_text, new_text)
        
        if content != original_content:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            return True
        return False
    except Exception as e:
        print(f"Error processing {filepath}: {e}")
        return False

def main():
    base_path = Path(__file__).parent.parent.parent
    os.chdir(base_path)
    
    # Define simple string replacements (order matters!)
    replacements = [
        # Module paths (Windows)
        ('modules\\log\\', 'modules\\logger\\'),
        # Module paths (Unix)
        ('modules/log/', 'modules/logger/'),
        # Python imports
        ('modules.log.', 'modules.logger.'),
        ('from modules.log ', 'from modules.logger '),
        
        # Test paths (Windows)
        ('tests\\log\\', 'tests\\logger\\'),
        # Test paths (Unix)  
        ('tests/log/', 'tests/logger/'),
        
        # Module IDs
        ('"id": "log"', '"id": "logger"'),
        
        # API routes
        ('/api/log/', '/api/logger/'),
        ('/api/log"', '/api/logger"'),
        ("/api/log'", "/api/logger'"),
        
        # Blueprint names
        ('Blueprint("log")', 'Blueprint("logger")'),
        ("Blueprint('log')", "Blueprint('logger')"),
        ('url_prefix="log"', 'url_prefix="logger"'),
        ("url_prefix='log'", "url_prefix='logger'"),
    ]
    
    # Files to update (excluding archive and generated files)
    patterns_to_scan = [
        'server.py',
        'app_v2/static/index.html',
        'modules/*/module.json',
        'modules/*/README.md',
        'modules/*/backend/**/*.py',
        'modules/*/frontend/**/*.js',
        'tests/**/*.py',
        'docs/knowledge/*.md',
        'core/**/*.py',
        '.clinerules',
    ]
    
    files_updated = []
    
    for pattern in patterns_to_scan:
        for filepath in Path('.').glob(pattern):
            if 'archive' in str(filepath) or '__pycache__' in str(filepath):
                continue
            
            if replace_in_file(filepath, replacements):
                files_updated.append(str(filepath))
                print(f"✓ Updated: {filepath}")
    
    print(f"\n{'='*60}")
    print(f"Files updated: {len(files_updated)}")
    print(f"{'='*60}")
    
    print("\nNext steps:")
    print("1. Run: git mv modules/log modules/logger")
    print("2. Run: git mv tests/log tests/logger")
    print("3. Review changes: git diff")
    print("4. Test: pytest tests/logger/ -v")
    print("5. Commit changes")

if __name__ == '__main__':
    main()