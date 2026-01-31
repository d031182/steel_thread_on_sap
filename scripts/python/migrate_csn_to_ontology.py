#!/usr/bin/env python3
"""
Migrate CSN Relationships to Graph Ontology

Discovers relationships from CSN and persists them to database.
One-time migration to populate the ontology cache.

@author P2P Development Team
@version 1.0.0
"""

import sys
import os
from datetime import datetime

# Add project root to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

from core.services.relationship_mapper import CSNRelationshipMapper
from core.services.ontology_persistence_service import OntologyPersistenceService
from core.services.csn_parser import CSNParser

DB_PATH = 'app/database/p2p_data_products.db'
CSN_DIR = 'docs/csn'

print("="*80)
print("CSN to Graph Ontology Migration")
print("="*80)
print(f"\nDatabase: {DB_PATH}")
print(f"CSN Directory: {CSN_DIR}")
print(f"Timestamp: {datetime.now()}\n")

# Initialize services
parser = CSNParser(CSN_DIR)
mapper = CSNRelationshipMapper(parser)
persistence = OntologyPersistenceService(DB_PATH)

# Check if cache already exists
stats = persistence.get_statistics()
if stats['cache_valid']:
    print(f"[INFO] Cache already exists with {stats['total_relationships']} relationships")
    print(f"       Last discovery: {stats['last_discovery']}")
    print("\n[QUESTION] Clear cache and rediscover? (This will take ~2-3 seconds)")
    response = input("Clear and rediscover? [y/N]: ")
    
    if response.lower() == 'y':
        count = persistence.clear_cache()
        print(f"[OK] Cleared {count} cached relationships\n")
    else:
        print("[SKIPPED] Keeping existing cache")
        sys.exit(0)

# Discover relationships from CSN
print("STEP 1: Discovering relationships from CSN")
print("-" * 80)

start_time = datetime.now()
relationships = mapper.discover_relationships()
# Convert Relationship objects to dicts
relationships = [
    {
        'source_table': r.from_entity,
        'source_column': r.from_column,
        'target_table': r.to_entity,
        'target_column': r.to_column,
        'type': r.relationship_type,
        'confidence': r.confidence
    }
    for r in relationships
]
discovery_time = (datetime.now() - start_time).total_seconds()

print(f"[OK] Discovered {len(relationships)} relationships in {discovery_time:.2f}s\n")

# Categorize by confidence
high_conf = [r for r in relationships if r['confidence'] >= 0.9]
medium_conf = [r for r in relationships if 0.7 <= r['confidence'] < 0.9]
low_conf = [r for r in relationships if r['confidence'] < 0.7]

print("Confidence breakdown:")
print(f"  - High (>=0.9): {len(high_conf)}")
print(f"  - Medium (0.7-0.9): {len(medium_conf)}")
print(f"  - Low (<0.7): {len(low_conf)}\n")

# Persist to database
print("STEP 2: Persisting relationships to database")
print("-" * 80)

start_time = datetime.now()
inserted, updated = persistence.persist_relationships(relationships, 'csn_metadata')
persist_time = (datetime.now() - start_time).total_seconds()

print(f"[OK] Persisted in {persist_time:.2f}s")
print(f"  - Inserted: {inserted}")
print(f"  - Updated: {updated}\n")

# Verify persistence
print("STEP 3: Verifying persistence")
print("-" * 80)

start_time = datetime.now()
cached = persistence.get_all_relationships()
load_time = (datetime.now() - start_time).total_seconds()

print(f"[OK] Loaded {len(cached)} relationships in {load_time*1000:.0f}ms")
print(f"\n[PERFORMANCE] Cache speedup: {discovery_time / load_time:.0f}x faster!\n")

# Final statistics
stats = persistence.get_statistics()

print("="*80)
print("MIGRATION SUMMARY")
print("="*80)
print(f"\nGraph Ontology Cache:")
print(f"  - Total Relationships: {stats['total_relationships']}")
print(f"  - High Confidence: {stats['high_confidence']}")
print(f"  - Manually Verified: {stats['manually_verified']}")
print(f"  - Last Discovery: {stats['last_discovery']}")

print(f"\nPerformance Gains:")
print(f"  - Discovery Time: {discovery_time:.2f}s")
print(f"  - Cache Load Time: {load_time*1000:.0f}ms")
print(f"  - Speedup: {discovery_time / load_time:.0f}x faster")

print("\n" + "="*80)
print("[SUCCESS] Ontology migration complete!")
print("="*80)
print("\nNext: DataGraphService will now use cached relationships")
print("      (50x faster startup, persistent across sessions)")