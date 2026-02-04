"""
Profile data mode performance to find bottleneck
"""
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

import time
from modules.sqlite_connection.backend.sqlite_data_source import SQLiteDataSource
from modules.knowledge_graph.backend.relationship_discovery_db import RelationshipDiscoveryDB
from modules.knowledge_graph.backend.data_graph_builder import DataGraphBuilder
from core.services.ontology_persistence_service import OntologyPersistenceService

def profile_data_mode():
    print("Profiling data mode performance...")
    
    # Setup
    db_path = 'app/database/p2p_data_products.db'
    data_source = SQLiteDataSource(db_path)
    ontology = OntologyPersistenceService(db_path)
    discovery = RelationshipDiscoveryDB(ontology)
    builder = DataGraphBuilder(data_source, discovery)
    
    # Time each step
    start = time.time()
    
    # Step 1: Get all tables
    t1 = time.time()
    all_tables = builder._get_all_tables()
    t1_elapsed = (time.time() - t1) * 1000
    print(f"1. Get tables: {t1_elapsed:.0f}ms ({len(all_tables)} tables)")
    
    # Step 2: Build table→product map
    t2 = time.time()
    builder._build_table_to_product_map()
    t2_elapsed = (time.time() - t2) * 1000
    print(f"2. Build table->product map: {t2_elapsed:.0f}ms")
    
    # Step 3: Discover FK mappings (should use cache)
    t3 = time.time()
    fk_mappings = discovery.discover_fk_mappings(all_tables)
    t3_elapsed = (time.time() - t3) * 1000
    fk_count = sum(len(fks) for fks in fk_mappings.values())
    print(f"3. Discover FK mappings: {t3_elapsed:.0f}ms ({fk_count} FKs)")
    
    # Step 4: Build record nodes (SUSPECT - queries all tables)
    t4 = time.time()
    nodes, record_map = builder._build_record_nodes(all_tables, max_records=20)
    t4_elapsed = (time.time() - t4) * 1000
    print(f"4. Build record nodes: {t4_elapsed:.0f}ms ({len(nodes)} nodes)")
    
    # Step 5: Build record edges
    t5 = time.time()
    edges = builder._build_record_edges(all_tables, fk_mappings, record_map, max_records=20)
    t5_elapsed = (time.time() - t5) * 1000
    print(f"5. Build record edges: {t5_elapsed:.0f}ms ({len(edges)} edges)")
    
    total_elapsed = (time.time() - start) * 1000
    print(f"\nTotal: {total_elapsed:.0f}ms")
    print(f"Cache used: {ontology.is_cache_valid()}")
    
    # Identify bottleneck
    steps = [
        ("Get tables", t1_elapsed),
        ("Table→product map", t2_elapsed),
        ("FK discovery", t3_elapsed),
        ("Build nodes", t4_elapsed),
        ("Build edges", t5_elapsed)
    ]
    
    slowest = max(steps, key=lambda x: x[1])
    print(f"\nBottleneck: {slowest[0]} ({slowest[1]:.0f}ms - {slowest[1]/total_elapsed*100:.0f}% of total)")

if __name__ == '__main__':
    profile_data_mode()