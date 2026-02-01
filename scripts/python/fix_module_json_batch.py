#!/usr/bin/env python3
"""
Batch fix module.json files for feng shui compliance
Adds missing 'enabled' field and 'backend' section where needed
"""

import json
import os
import sys
from pathlib import Path

# Force UTF-8 output on Windows
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

# Define modules that need fixes
FIXES = {
    'debug_mode': {
        'add_enabled': True,
        'backend_section': False  # No backend directory
    },
    'csn_validation': {
        'add_enabled': True,
        'backend_section': True,
        'backend_type': 'api'
    },
    'data_products': {
        'add_enabled': True,
        'backend_section': True,
        'backend_type': 'api'
    },
    'sql_execution': {
        'add_enabled': True,
        'backend_section': True,
        'backend_type': 'api'
    },
    'hana_connection': {
        'add_enabled': False,  # Already has it
        'backend_section': True,
        'backend_type': 'data_source'
    }
}

def fix_module_json(module_name, fixes):
    """Fix a single module.json file"""
    module_path = Path(f'modules/{module_name}/module.json')
    
    if not module_path.exists():
        print(f"[ERROR] {module_name}: module.json not found")
        return False
    
    try:
        with open(module_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        modified = False
        
        # Add 'enabled' field if needed
        if fixes.get('add_enabled') and 'enabled' not in config:
            config['enabled'] = True
            modified = True
            print(f"[OK] {module_name}: Added 'enabled: true'")
        
        # Add backend section if needed
        if fixes.get('backend_section'):
            # Add structure if missing
            if 'structure' not in config:
                config['structure'] = {'backend': 'backend/'}
                modified = True
            
            # Add backend config if missing
            if 'backend' not in config:
                backend_type = fixes.get('backend_type', 'api')
                
                if backend_type == 'api':
                    # For API modules, try to detect blueprint name from api.py
                    backend_config = {
                        'type': 'api',
                        'module_path': f'modules.{module_name}.backend',
                        'note': 'Blueprint name should be verified in backend/api.py'
                    }
                else:
                    # For data source modules
                    backend_config = {
                        'type': 'data_source',
                        'module_path': f'modules.{module_name}.backend',
                        'note': 'No Blueprint - this is a data source implementation'
                    }
                
                config['backend'] = backend_config
                modified = True
                print(f"[OK] {module_name}: Added backend section")
        
        if modified:
            # Write back
            with open(module_path, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
            
            print(f"[FIXED] {module_name}: Fixed and saved")
            return True
        else:
            print(f"[SKIP] {module_name}: No changes needed")
            return False
            
    except Exception as e:
        print(f"[ERROR] {module_name}: Error - {e}")
        return False

def main():
    print("=" * 80)
    print("BATCH FIX: module.json Files")
    print("=" * 80)
    print()
    
    fixed_count = 0
    for module_name, fixes in FIXES.items():
        if fix_module_json(module_name, fixes):
            fixed_count += 1
        print()
    
    print("=" * 80)
    print(f"SUMMARY: Fixed {fixed_count}/{len(FIXES)} modules")
    print("=" * 80)

if __name__ == '__main__':
    main()