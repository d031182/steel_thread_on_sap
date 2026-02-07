#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Query Knowledge Graph Script
Handles large knowledge graph JSON files by streaming/chunking data
Prevents SSE stream errors from reading huge files directly
"""

import json
import sys
import io
from pathlib import Path
from typing import Dict, List, Optional
import ijson  # For streaming JSON parsing

# Fix Windows encoding issue
if sys.platform == 'win32':
    try:
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')
    except (AttributeError, io.UnsupportedOperation):
        pass  # Already wrapped or not supported


class KnowledgeGraphQuery:
    """Query large knowledge graph files efficiently"""
    
    def __init__(self, kg_file_path: str):
        self.kg_path = Path(kg_file_path)
        if not self.kg_path.exists():
            raise FileNotFoundError(f"Knowledge graph file not found: {kg_file_path}")
    
    def search_entities(self, query: str, limit: int = 10) -> List[Dict]:
        """Search for entities matching query string"""
        results = []
        query_lower = query.lower()
        
        try:
            with open(self.kg_path, 'r', encoding='utf-8') as f:
                # JSONL format - one JSON object per line
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    
                    try:
                        obj = json.loads(line)
                        
                        # Check if this is an entity
                        if obj.get('type') == 'entity':
                            name = obj.get('name', '').lower()
                            entity_type = obj.get('entityType', '').lower()
                            observations = obj.get('observations', [])
                            
                            # Check if query matches name, type, or observations
                            if (query_lower in name or 
                                query_lower in entity_type or
                                any(query_lower in str(obs).lower() for obs in observations)):
                                
                                results.append({
                                    'name': obj.get('name'),
                                    'type': obj.get('entityType'),
                                    'observations': observations[:3]  # First 3 observations only
                                })
                                
                                if len(results) >= limit:
                                    break
                    except json.JSONDecodeError:
                        continue  # Skip malformed lines
                            
        except Exception as e:
            print(f"Error searching entities: {e}", file=sys.stderr)
            return []
        
        return results
    
    def get_entity_details(self, entity_name: str) -> Optional[Dict]:
        """Get full details for a specific entity"""
        try:
            with open(self.kg_path, 'rb') as f:
                parser = ijson.items(f, 'entities.item')
                
                for entity in parser:
                    if entity.get('name', '').lower() == entity_name.lower():
                        return entity
                        
        except Exception as e:
            print(f"Error getting entity details: {e}", file=sys.stderr)
            return None
        
        return None
    
    def list_entity_types(self) -> Dict[str, int]:
        """Get count of entities by type"""
        type_counts = {}
        
        try:
            with open(self.kg_path, 'rb') as f:
                parser = ijson.items(f, 'entities.item')
                
                for entity in parser:
                    entity_type = entity.get('entityType', 'Unknown')
                    type_counts[entity_type] = type_counts.get(entity_type, 0) + 1
                    
        except Exception as e:
            print(f"Error listing entity types: {e}", file=sys.stderr)
            return {}
        
        return type_counts
    
    def get_relations(self, entity_name: Optional[str] = None, limit: int = 20) -> List[Dict]:
        """Get relations, optionally filtered by entity name"""
        results = []
        
        try:
            with open(self.kg_path, 'rb') as f:
                parser = ijson.items(f, 'relations.item')
                
                for relation in parser:
                    # If entity_name specified, filter relations
                    if entity_name:
                        from_entity = relation.get('from', '').lower()
                        to_entity = relation.get('to', '').lower()
                        
                        if entity_name.lower() not in [from_entity, to_entity]:
                            continue
                    
                    results.append({
                        'from': relation.get('from'),
                        'to': relation.get('to'),
                        'type': relation.get('relationType')
                    })
                    
                    if len(results) >= limit:
                        break
                        
        except Exception as e:
            print(f"Error getting relations: {e}", file=sys.stderr)
            return []
        
        return results
    
    def get_stats(self) -> Dict:
        """Get overall knowledge graph statistics"""
        stats = {
            'total_entities': 0,
            'total_relations': 0,
            'total_observations': 0,
            'entity_types': {}
        }
        
        try:
            with open(self.kg_path, 'rb') as f:
                # Count entities
                parser = ijson.items(f, 'entities.item')
                for entity in parser:
                    stats['total_entities'] += 1
                    stats['total_observations'] += len(entity.get('observations', []))
                    
                    entity_type = entity.get('entityType', 'Unknown')
                    stats['entity_types'][entity_type] = stats['entity_types'].get(entity_type, 0) + 1
            
            with open(self.kg_path, 'rb') as f:
                # Count relations
                parser = ijson.items(f, 'relations.item')
                for _ in parser:
                    stats['total_relations'] += 1
                    
        except Exception as e:
            print(f"Error getting stats: {e}", file=sys.stderr)
        
        return stats


def main():
    """CLI interface for querying knowledge graph"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Query large knowledge graph files')
    parser.add_argument('--kg-file', default='knowledge_graph.json', 
                       help='Path to knowledge graph JSON file')
    parser.add_argument('--search', help='Search for entities')
    parser.add_argument('--entity', help='Get details for specific entity')
    parser.add_argument('--types', action='store_true', help='List entity types')
    parser.add_argument('--relations', help='Get relations for entity')
    parser.add_argument('--stats', action='store_true', help='Show knowledge graph stats')
    parser.add_argument('--limit', type=int, default=10, help='Limit results')
    
    args = parser.parse_args()
    
    try:
        kg = KnowledgeGraphQuery(args.kg_file)
        
        if args.search:
            print(f"\n🔍 Searching for: {args.search}")
            results = kg.search_entities(args.search, limit=args.limit)
            print(f"Found {len(results)} results:\n")
            for r in results:
                print(f"📌 {r['name']} ({r['type']})")
                for obs in r['observations']:
                    print(f"   - {obs}")
                print()
        
        elif args.entity:
            print(f"\n📖 Entity Details: {args.entity}")
            entity = kg.get_entity_details(args.entity)
            if entity:
                print(f"Type: {entity.get('entityType')}")
                print(f"\nObservations ({len(entity.get('observations', []))}):")
                for i, obs in enumerate(entity.get('observations', []), 1):
                    print(f"  {i}. {obs}")
            else:
                print("Entity not found")
        
        elif args.types:
            print("\n📊 Entity Types:")
            types = kg.list_entity_types()
            for entity_type, count in sorted(types.items(), key=lambda x: x[1], reverse=True):
                print(f"  {entity_type}: {count}")
        
        elif args.relations:
            print(f"\n🔗 Relations for: {args.relations}")
            relations = kg.get_relations(args.relations, limit=args.limit)
            for r in relations:
                print(f"  {r['from']} --[{r['type']}]--> {r['to']}")
        
        elif args.stats:
            print("\n📊 Knowledge Graph Statistics:")
            stats = kg.get_stats()
            print(f"  Total Entities: {stats['total_entities']}")
            print(f"  Total Relations: {stats['total_relations']}")
            print(f"  Total Observations: {stats['total_observations']}")
            print(f"\n  Entity Types:")
            for entity_type, count in sorted(stats['entity_types'].items(), 
                                            key=lambda x: x[1], reverse=True):
                print(f"    {entity_type}: {count}")
        
        else:
            parser.print_help()
    
    except Exception as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()