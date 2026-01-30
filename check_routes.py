"""Check Flask registered routes"""
import sys
import os

# Add both project root and app directory to path
project_root = 'c:/Users/D031182/gitrepo/steel_thread_on_sap'
sys.path.insert(0, project_root)
sys.path.insert(0, os.path.join(project_root, 'app'))

# Import app module first, then get app from it
import app.app as app_module
app = app_module.app

print("Registered Flask Routes:")
print("=" * 60)
for rule in app.url_map.iter_rules():
    methods = ','.join(rule.methods - {'HEAD', 'OPTIONS'})
    print(f"{methods:10} {rule.rule:50} -> {rule.endpoint}")
print("=" * 60)
print(f"Total routes: {len(list(app.url_map.iter_rules()))}")