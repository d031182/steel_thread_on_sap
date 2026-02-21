#!/usr/bin/env python3
"""
Script to find CSN files with associations that have ON conditions.
"""

import json
import os
from pathlib import Path

def find_associations_in_all_csn_files():
    """Search all CSN files for associations with ON conditions."""
    csn_dir = Path('docs/csn')
    
    files_with_associations = []
    
    for csn_file in csn_dir.glob('*.json'):
        print(f"\nChecking {csn_file.name}...")
        
        try:
            with open(csn_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            definitions = data[0]['definitions']
            
            # Find entities with associations
            for entity_name, entity_def in definitions.items():
                if entity_def.get('kind') != 'entity':
                    continue
                    
                elements = entity_def.get('elements', {})
                
                # Find associations with ON condition
                for field_name, field_def in elements.items():
                    # Check if field has 'on' condition
                    if 'on' in field_def:
                        print(f"  ✓ Found association in {entity_name}.{field_name}")
                        files_with_associations.append({
                            'file': csn_file.name,
                            'entity': entity_name,
                            'field': field_name,
                            'definition': field_def
                        })
                        break  # Found one, move to next entity
                        
        except Exception as e:
            print(f"  ✗ Error reading {csn_file.name}: {e}")
    
    print("\n" + "="*80)
    print("SUMMARY")
    print("="*80)
    
    if files_with_associations:
        print(f"\nFound {len(files_with_associations)} CSN file(s) with associations:\n")
        for item in files_with_associations:
            print(f"  • {item['file']}")
            print(f"    Entity: {item['entity']}")
            print(f"    Field: {item['field']}")
        
        # Show detailed structure of first association found
        if files_with_associations:
            print("\n" + "="*80)
            print("EXAMPLE ASSOCIATION STRUCTURE")
            print("="*80)
            first = files_with_associations[0]
            print(f"\nFile: {first['file']}")
            print(f"Entity: {first['entity']}")
            print(f"Field: {first['field']}")
            print("\nFull definition:")
            print(json.dumps(first['definition'], indent=2))
    else:
        print("\n⚠ No associations with ON conditions found in any CSN file")

if __name__ == "__main__":
    find_associations_in_all_csn_files()