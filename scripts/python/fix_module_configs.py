# -*- coding: utf-8 -*-
"""
Fix Module Configuration Issues
================================
Systematically fix module.json configurations across all modules.

Fixes:
1. Add missing backend.blueprint config
2. Validate module.json structure
"""

import sys
import os
import json

# Windows UTF-8 encoding fix
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

# Add project root to path
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(script_dir))
sys.path.insert(0, project_root)

# Modules that need backend config
MODULES_WITH_BACKEND = [
    'api_playground',
    'csn_validation',
    'data_products',
    'feature_manager',
    'hana_connection',
    'log_manager',
    'sqlite_connection',
    'sql_execution'
]

def fix_module_config(module_name):
    """Fix module.json for a specific module"""
    module_path = os.path.join(project_root, 'modules', module_name)
    config_path = os.path.join(module_path, 'module.json')
    
    if not os.path.exists(config_path):
        print(f"  ❌ {module_name}: module.json not found")
        return False
    
    # Read existing config
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
    except Exception as e:
        print(f"  ❌ {module_name}: Failed to read module.json - {e}")
        return False
    
    # Check if backend directory exists
    backend_path = os.path.join(module_path, 'backend')
    has_backend = os.path.exists(backend_path)
    
    if not has_backend:
        print(f"  ⚠️  {module_name}: No backend directory")
        return True  # Not an error, just no backend
    
    # Check if api.py exists (indicates blueprint)
    api_path = os.path.join(backend_path, 'api.py')
    has_api = os.path.exists(api_path)
    
    if not has_api:
        print(f"  ⚠️  {module_name}: No api.py (no blueprint)")
        return True  # Not all modules need blueprints
    
    # Add backend config if missing
    changes_made = False
    
    if 'backend' not in config:
        config['backend'] = {}
        changes_made = True
    
    # Determine blueprint name from api.py
    blueprint_name = f"{module_name}_api"
    
    if 'blueprint' not in config.get('backend', {}):
        config['backend']['blueprint'] = blueprint_name
        changes_made = True
        print(f"  ✅ {module_name}: Added backend.blueprint = '{blueprint_name}'")
    
    if 'module_path' not in config.get('backend', {}):
        config['backend']['module_path'] = f"modules.{module_name}.backend"
        changes_made = True
        print(f"  ✅ {module_name}: Added backend.module_path")
    
    # Ensure structure field exists
    if 'structure' not in config:
        config['structure'] = {}
        changes_made = True
    
    if 'backend' not in config.get('structure', {}):
        config['structure']['backend'] = 'backend/'
        changes_made = True
    
    # Save if changes were made
    if changes_made:
        try:
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"  ❌ {module_name}: Failed to write module.json - {e}")
            return False
    else:
        print(f"  ✓ {module_name}: Already configured correctly")
        return True

def main():
    print("=" * 80)
    print("FIX MODULE CONFIGURATIONS")
    print("=" * 80)
    print()
    
    fixed_count = 0
    failed_count = 0
    
    for module in MODULES_WITH_BACKEND:
        print(f"Processing {module}...")
        if fix_module_config(module):
            fixed_count += 1
        else:
            failed_count += 1
    
    print()
    print("=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f"✅ Fixed/Verified: {fixed_count} modules")
    print(f"❌ Failed: {failed_count} modules")
    print()
    
    if failed_count == 0:
        print("🎉 All module configurations fixed!")
    else:
        print("⚠️  Some modules need manual review")

if __name__ == '__main__':
    main()