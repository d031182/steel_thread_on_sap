"""
Debug script to check what keys are in table_to_product dict
"""
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from core.services.csn_parser import CSNParser
from modules.knowledge_graph_v2.services.schema_graph_builder_service import SchemaGraphBuilderService

def main():
    print("=" * 80)
    print("DEBUG: table_to_product Keys")
    print("=" * 80)
    
    # Build graph and capture table_to_product
    csn_parser = CSNParser()
    builder = SchemaGraphBuilderService(csn_parser)
    
    # Get entity names
    entity_names = csn_parser.list_entities()
    print(f"\n1. Entity names from CSN (first 10):")
    for name in entity_names[:10]:
        print(f"   - {name}")
    
    # Infer products
    products_map = builder._infer_products_from_entities(entity_names)
    print(f"\n2. Products map (first 3 products):")
    for product, tables in list(products_map.items())[:3]:
        print(f"   Product: {product}")
        print(f"   Tables: {tables}")
    
    print("\n" + "=" * 80)

if __name__ == '__main__':
    main()