#!/usr/bin/env python3
"""
Script to examine CSN associations with ON conditions.
"""

import json
import sys

def examine_associations(csn_file: str):
    """Examine associations with ON conditions in a CSN file."""
    with open(csn_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    definitions = data[0]['definitions']
    
    # Find first entity with associations
    for entity_name, entity_def in definitions.items():
        if entity_def.get('kind') != 'entity':
            continue
            
        elements = entity_def.get('elements', {})
        
        # Find first association with ON condition
        for field_name, field_def in elements.items():
            if isinstance(field_def.get('type'), dict) and 'on' in field_def:
                print(f"Entity: {entity_name}")
                print(f"Field: {field_name}")
                print(f"Association structure:")
                print(json.dumps(field_def, indent=2))
                return
    
    print("No associations with ON conditions found")

if __name__ == "__main__":
    examine_associations('docs/csn/Purchase_Order_CSN.json')