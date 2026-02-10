#!/usr/bin/env python3
"""
Rename Python interfaces to use 'i_' prefix for consistency with JavaScript
Preserves git history by using 'git mv'
"""

import subprocess
import sys
from pathlib import Path

# Interface files to rename
INTERFACES = [
    'data_product_repository.py',
    'data_source.py',
    'database_path_resolver.py',
    'graph_cache.py',
    'graph_query.py',
    'graph.py',
    'log_intelligence.py',
    'logger.py',
    'relationship_discovery.py'
]

def main():
    project_root = Path(__file__).parent.parent
    interfaces_dir = project_root / 'core' / 'interfaces'
    
    print("=" * 60)
    print("RENAMING PYTHON INTERFACES (i_ prefix)")
    print("=" * 60)
    print()
    
    success_count = 0
    fail_count = 0
    
    for old_name in INTERFACES:
        # Generate new name with i_ prefix
        new_name = f'i_{old_name}'
        
        old_path = interfaces_dir / old_name
        new_path = interfaces_dir / new_name
        
        if not old_path.exists():
            print(f"⚠️  SKIP: {old_name} (file doesn't exist)")
            continue
        
        # Use git mv to preserve history
        try:
            result = subprocess.run(
                ['git', 'mv', str(old_path), str(new_path)],
                capture_output=True,
                text=True,
                check=True
            )
            print(f"✅ {old_name} → {new_name}")
            success_count += 1
        except subprocess.CalledProcessError as e:
            print(f"❌ FAILED: {old_name}")
            print(f"   Error: {e.stderr}")
            fail_count += 1
    
    print()
    print("=" * 60)
    print(f"SUMMARY: {success_count} renamed, {fail_count} failed")
    print("=" * 60)
    
    return 0 if fail_count == 0 else 1

if __name__ == '__main__':
    sys.exit(main())