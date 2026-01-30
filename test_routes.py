#!/usr/bin/env python3
"""Test script to print all registered Flask routes"""
import sys
import os

# Add paths
backend_dir = os.path.join(os.path.dirname(__file__), 'app')
project_root = os.path.dirname(__file__)
sys.path.insert(0, backend_dir)
sys.path.insert(0, project_root)

# Import app
from app import app

print("\n" + "="*60)
print("REGISTERED FLASK ROUTES")
print("="*60)

for rule in app.url_map.iter_rules():
    methods = ','.join(sorted(rule.methods - {'HEAD', 'OPTIONS'}))
    print(f"{methods:10} {rule.rule:50} -> {rule.endpoint}")

print("="*60)
print(f"Total routes: {len(list(app.url_map.iter_rules()))}")
print("="*60)