#!/usr/bin/env python3
"""
Audit all modules for proper blueprint registration
"""
import os
import json
from pathlib import Path

def audit_modules():
    """Check all modules for blueprint registration"""
    modules_dir = Path('modules')
    
    print("=" * 80)
    print("MODULE BLUEPRINT AUDIT")
    print("=" * 80)
    
    issues_found = []
    modules_checked = 0
    
    for module_dir in sorted(modules_dir.iterdir()):
        if not module_dir.is_dir() or module_dir.name.startswith('.'):
            continue
        
        modules_checked += 1
        module_name = module_dir.name
        module_json_path = module_dir / 'module.json'
        backend_dir = module_dir / 'backend'
        backend_init = backend_dir / '__init__.py'
        
        print(f"\n[Module: {module_name}]")
        print(f"   Path: {module_dir}")
        
        # Check 1: Does module.json exist?
        if not module_json_path.exists():
            print(f"   X No module.json found")
            issues_found.append(f"{module_name}: Missing module.json")
            continue
        
        # Load module.json
        try:
            with open(module_json_path) as f:
                config = json.load(f)
        except Exception as e:
            print(f"   X Cannot parse module.json: {e}")
            issues_found.append(f"{module_name}: Invalid module.json")
            continue
        
        # Check 2: Does backend/ directory exist?
        has_backend_dir = backend_dir.exists()
        print(f"   Backend directory: {'YES' if has_backend_dir else 'NO'}")
        
        if not has_backend_dir:
            print(f"   INFO: No backend (frontend-only or config module)")
            continue
        
        # Check 3: Does module.json have backend.blueprint config?
        has_blueprint_config = 'backend' in config and 'blueprint' in config.get('backend', {})
        print(f"   Blueprint config: {'YES' if has_blueprint_config else 'MISSING'}")
        
        if not has_blueprint_config:
            print(f"   WARNING: Has backend/ but no backend.blueprint in module.json")
            issues_found.append(f"{module_name}: Has backend/ but missing backend.blueprint config")
            continue
        
        # Check 4: Does backend/__init__.py exist and export blueprint?
        if not backend_init.exists():
            print(f"   X backend/__init__.py doesn't exist")
            issues_found.append(f"{module_name}: Missing backend/__init__.py")
            continue
        
        blueprint_name = config['backend']['blueprint']
        print(f"   Blueprint name: {blueprint_name}")
        
        # Check 5: Verify blueprint is exported
        try:
            with open(backend_init) as f:
                init_content = f.read()
                
            # Look for blueprint import/export
            if blueprint_name in init_content:
                print(f"   ✓ Blueprint '{blueprint_name}' referenced in __init__.py")
            else:
                print(f"   X Blueprint '{blueprint_name}' not found in __init__.py")
                issues_found.append(f"{module_name}: Blueprint '{blueprint_name}' not exported in __init__.py")
        except Exception as e:
            print(f"   X Cannot read __init__.py: {e}")
            issues_found.append(f"{module_name}: Cannot read __init__.py")
        
        # Check 6: Verify blueprint is registered in app.py
        app_py_path = Path('app') / 'app.py'
        if app_py_path.exists():
            try:
                with open(app_py_path) as f:
                    app_content = f.read()
                
                # Check if this module's blueprint is registered
                module_path_pattern = f"modules.{module_name}.backend"
                if module_path_pattern in app_content and blueprint_name in app_content:
                    print(f"   ✓ Registered in app.py")
                else:
                    print(f"   X NOT registered in app.py")
                    issues_found.append(f"{module_name}: Blueprint '{blueprint_name}' not registered in app.py")
            except Exception as e:
                print(f"   ? Cannot check app.py: {e}")
        else:
            print(f"   ? app.py not found")
    
    print("\n" + "=" * 80)
    print("AUDIT SUMMARY")
    print("=" * 80)
    print(f"Modules checked: {modules_checked}")
    print(f"Issues found: {len(issues_found)}")
    
    if issues_found:
        print("\nISSUES REQUIRING ATTENTION:")
        for i, issue in enumerate(issues_found, 1):
            print(f"  {i}. {issue}")
        return 1
    else:
        print("\nAll modules properly configured!")
        return 0

if __name__ == '__main__':
    exit(audit_modules())