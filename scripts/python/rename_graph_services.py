"""
Rename DataGraphService → DataGraphBuilder and SchemaGraphService → SchemaGraphBuilder
across all import statements
"""

import os
import re

def rename_in_file(filepath, replacements):
    """Apply multiple replacements to a file"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original = content
        for old, new in replacements:
            content = content.replace(old, new)
        
        if content != original:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            return True
        return False
    except Exception as e:
        print(f"Error processing {filepath}: {e}")
        return False

# Files to update
files = [
    'modules/knowledge_graph/backend/api.py',
    'modules/knowledge_graph/__init__.py',
    'modules/knowledge_graph/backend/__init__.py'
]

# Replacements to make
replacements = [
    ('from modules.knowledge_graph.backend.schema_graph_service import SchemaGraphService', 
     'from modules.knowledge_graph.backend.schema_graph_builder import SchemaGraphBuilder'),
    ('from modules.knowledge_graph.backend.data_graph_service import DataGraphService',
     'from modules.knowledge_graph.backend.data_graph_builder import DataGraphBuilder'),
    ('SchemaGraphService', 'SchemaGraphBuilder'),
    ('DataGraphService', 'DataGraphBuilder')
]

print("Renaming graph services...")
updated_count = 0

for filepath in files:
    if os.path.exists(filepath):
        if rename_in_file(filepath, replacements):
            print(f"[OK] Updated {filepath}")
            updated_count += 1
        else:
            print(f"[SKIP] No changes in {filepath}")
    else:
        print(f"[WARN] File not found: {filepath}")

print(f"\n[COMPLETE] Updated {updated_count} files")