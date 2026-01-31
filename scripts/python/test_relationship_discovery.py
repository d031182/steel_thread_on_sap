#!/usr/bin/env python3
"""
Test CSN Relationship Discovery

Tests the CSNRelationshipMapper to see what relationships it discovers
from the P2P schema CSN files.
"""

import sys
import os

# Fix Windows encoding
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Add project root to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

from core.services.csn_parser import CSNParser
from core.services.relationship_mapper import CSNRelationshipMapper

print("="*80)
print("CSN Relationship Discovery Test")
print("="*80)

# Initialize parser and mapper
print("\n1. Initializing CSN parser...")
parser = CSNParser('docs/csn')
entities = parser.list_entities()
print(f"   Found {len(entities)} entities in CSN")

print("\n2. Discovering relationships...")
mapper = CSNRelationshipMapper(parser)
relationships = mapper.discover_relationships()

print(f"   Discovered {len(relationships)} relationships!")

# Group by confidence
high_conf = [r for r in relationships if r.confidence >= 0.9]
medium_conf = [r for r in relationships if 0.7 <= r.confidence < 0.9]
low_conf = [r for r in relationships if r.confidence < 0.7]

print(f"\n   Confidence breakdown:")
print(f"   - High confidence (>=0.9): {len(high_conf)}")
print(f"   - Medium confidence (0.7-0.9): {len(medium_conf)}")
print(f"   - Low confidence (<0.7): {len(low_conf)}")

# Show top 20 relationships
print("\n3. Top 20 Discovered Relationships")
print("-" * 80)
for i, rel in enumerate(relationships[:20], 1):
    print(f"{i:2d}. {rel.from_entity}.{rel.from_column} -> "
          f"{rel.to_entity}.{rel.to_column} "
          f"(confidence: {rel.confidence:.2f})")

# Show relationships for key entities
print("\n4. Relationships for Key Entities")
print("-" * 80)

key_entities = ['PurchaseOrderItem', 'SupplierInvoice', 'JournalEntry']
for entity in key_entities:
    outgoing = mapper.get_outgoing_relationships(entity)
    if outgoing:
        print(f"\n{entity} references:")
        for rel in outgoing:
            print(f"  -> {rel.to_entity} (via {rel.from_column})")

# Export for inspection
print("\n5. Exporting Relationships")
print("-" * 80)
export = mapper.export_relationships()
print(f"Total relationships exported: {len(export)}")

# Show some examples
print("\nExample relationships (first 5):")
for i, rel_dict in enumerate(export[:5], 1):
    print(f"{i}. {rel_dict}")

print("\n" + "="*80)
print("✓ Test Complete!")
print("="*80)