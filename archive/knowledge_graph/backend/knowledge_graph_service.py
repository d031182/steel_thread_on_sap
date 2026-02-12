"""
Knowledge Graph Service (RDFLib Implementation)

Implements semantic RDF/SPARQL capabilities using RDFLib library.
Provides knowledge graph operations for P2P business domain modeling.

Uses RDFLib for offline/development mode. Future: Can swap to HANA Knowledge Graph.

@author P2P Development Team
@version 1.0.0
"""

from rdflib import Graph, Namespace, Literal, URIRef, RDF, RDFS
from typing import List, Dict, Any, Optional
import logging
from core.interfaces.graph import KnowledgeGraphInterface

logger = logging.getLogger(__name__)


class RDFLibKnowledgeGraph(KnowledgeGraphInterface):
    """
    RDFLib implementation of Knowledge Graph interface
    
    Provides RDF triple store with SPARQL query support:
    - Add/query RDF triples
    - Execute SPARQL queries
    - Semantic reasoning (basic RDFS inference)
    - W3C standards compliant
    
    Works offline with in-memory store. Future: Swap to HANA Knowledge Graph for scale.
    """
    
    def __init__(self, store_path: Optional[str] = None):
        """
        Initialize RDF graph
        
        Args:
            store_path: Optional path for persistent storage (not used in memory mode)
        """
        # Use in-memory store for now (fast, simple)
        self.graph = Graph()
        
        # Define P2P namespace
        self.P2P = Namespace('http://sap.com/p2p/')
        self.graph.bind('p2p', self.P2P)
        
        # Bind common namespaces
        self.graph.bind('rdf', RDF)
        self.graph.bind('rdfs', RDFS)
        
        logger.info("RDFLibKnowledgeGraph initialized with in-memory store")
    
    def add_triple(self, subject: str, predicate: str, obj: str) -> None:
        """
        Add RDF triple to knowledge graph
        
        Args:
            subject: Subject URI or ID
            predicate: Predicate URI or ID
            obj: Object URI, ID, or literal value
        """
        try:
            # Convert strings to URIRef or Literal
            s = self._to_uri(subject)
            p = self._to_uri(predicate)
            o = self._to_uri_or_literal(obj)
            
            self.graph.add((s, p, o))
            logger.debug(f"Added triple: {subject} {predicate} {obj}")
            
        except Exception as e:
            logger.error(f"Error adding triple: {e}", exc_info=True)
            raise
    
    def get_triples(
        self, 
        subject: Optional[str] = None,
        predicate: Optional[str] = None,
        obj: Optional[str] = None
    ) -> List[tuple]:
        """
        Query triples matching pattern (None = wildcard)
        
        Args:
            subject: Subject to match (None = any)
            predicate: Predicate to match (None = any)
            obj: Object to match (None = any)
            
        Returns:
            List of (subject, predicate, object) tuples
        """
        try:
            # Convert strings to URIRef (None stays None for wildcard)
            s = self._to_uri(subject) if subject else None
            p = self._to_uri(predicate) if predicate else None
            o = self._to_uri_or_literal(obj) if obj else None
            
            # Query triples
            triples = list(self.graph.triples((s, p, o)))
            
            # Convert back to strings
            result = [(str(s), str(p), str(o)) for s, p, o in triples]
            
            logger.info(f"Found {len(result)} triples matching pattern")
            return result
            
        except Exception as e:
            logger.error(f"Error querying triples: {e}", exc_info=True)
            return []
    
    def sparql_query(self, query: str) -> List[Dict[str, Any]]:
        """
        Execute SPARQL query and return results
        
        Args:
            query: SPARQL query string (SELECT, CONSTRUCT, ASK, DESCRIBE)
            
        Returns:
            List of result dictionaries
        """
        try:
            # Execute SPARQL query
            results = self.graph.query(query)
            
            # Convert results to list of dicts
            output = []
            
            if results.type == 'SELECT':
                # SELECT query - return bindings
                for row in results:
                    row_dict = {}
                    for var in results.vars:
                        value = row[var]
                        row_dict[str(var)] = str(value) if value else None
                    output.append(row_dict)
                    
            elif results.type == 'ASK':
                # ASK query - return boolean
                output = [{'result': bool(results)}]
                
            elif results.type == 'CONSTRUCT' or results.type == 'DESCRIBE':
                # CONSTRUCT/DESCRIBE - return triples
                for s, p, o in results:
                    output.append({
                        'subject': str(s),
                        'predicate': str(p),
                        'object': str(o)
                    })
            
            logger.info(f"SPARQL query returned {len(output)} results")
            return output
            
        except Exception as e:
            logger.error(f"Error executing SPARQL query: {e}", exc_info=True)
            raise
    
    def load_from_data_products(self, data_products: List[Dict]) -> None:
        """
        Load Data Products into RDF knowledge graph
        
        Converts relational data to RDF triples for semantic querying.
        
        Args:
            data_products: List of data product dictionaries
        """
        try:
            for product in data_products:
                product_name = product.get('productName')
                if not product_name:
                    continue
                
                # Create product entity
                product_uri = self.P2P[f"DataProduct_{product_name}"]
                
                # Add type
                self.graph.add((product_uri, RDF.type, self.P2P.DataProduct))
                
                # Add properties
                if product.get('displayName'):
                    self.graph.add((product_uri, self.P2P.displayName, 
                                   Literal(product['displayName'])))
                
                if product.get('description'):
                    self.graph.add((product_uri, self.P2P.description, 
                                   Literal(product['description'])))
                
                if product.get('schemaName'):
                    self.graph.add((product_uri, self.P2P.schemaName, 
                                   Literal(product['schemaName'])))
            
            logger.info(f"Loaded {len(data_products)} data products into RDF graph")
            
        except Exception as e:
            logger.error(f"Error loading data products: {e}", exc_info=True)
            raise
    
    def load_from_graph_dict(self, graph_dict: Dict[str, Any]) -> None:
        """
        Load graph structure (nodes/edges) into RDF
        
        Converts property graph to RDF for semantic querying.
        
        Args:
            graph_dict: Dictionary with 'nodes' and 'edges' lists
        """
        try:
            nodes = graph_dict.get('nodes', [])
            edges = graph_dict.get('edges', [])
            
            # Add nodes as entities
            for node in nodes:
                node_id = node.get('id')
                if not node_id:
                    continue
                
                node_uri = self.P2P[node_id.replace('-', '_')]
                
                # Add type based on group
                group = node.get('group', 'node')
                if group == 'product':
                    self.graph.add((node_uri, RDF.type, self.P2P.DataProduct))
                elif group == 'table':
                    self.graph.add((node_uri, RDF.type, self.P2P.Table))
                else:
                    self.graph.add((node_uri, RDF.type, self.P2P.Node))
                
                # Add label
                if node.get('label'):
                    self.graph.add((node_uri, RDFS.label, Literal(node['label'])))
            
            # Add edges as relationships
            for edge in edges:
                from_node = edge.get('from')
                to_node = edge.get('to')
                if not from_node or not to_node:
                    continue
                
                from_uri = self.P2P[from_node.replace('-', '_')]
                to_uri = self.P2P[to_node.replace('-', '_')]
                
                # Create relationship based on label or default
                rel_label = edge.get('label', 'relatedTo')
                rel_uri = self.P2P[rel_label.replace(' ', '_')]
                
                self.graph.add((from_uri, rel_uri, to_uri))
            
            logger.info(f"Loaded {len(nodes)} nodes and {len(edges)} edges into RDF graph")
            
        except Exception as e:
            logger.error(f"Error loading graph dict: {e}", exc_info=True)
            raise
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get knowledge graph statistics
        
        Returns:
            Dictionary with triple count and other metrics
        """
        try:
            stats = {
                'triple_count': len(self.graph),
                'namespace_count': len(list(self.graph.namespaces())),
                'namespaces': [str(ns) for prefix, ns in self.graph.namespaces()]
            }
            
            # Count entities by type
            type_counts = {}
            for s, p, o in self.graph.triples((None, RDF.type, None)):
                type_name = str(o).split('/')[-1]  # Get last part of URI
                type_counts[type_name] = type_counts.get(type_name, 0) + 1
            
            stats['entity_types'] = type_counts
            
            logger.info(f"Knowledge graph stats: {stats['triple_count']} triples")
            return stats
            
        except Exception as e:
            logger.error(f"Error getting stats: {e}", exc_info=True)
            return {'triple_count': 0, 'error': str(e)}
    
    def clear(self) -> None:
        """Clear all triples from the graph"""
        self.graph = Graph()
        self.graph.bind('p2p', self.P2P)
        self.graph.bind('rdf', RDF)
        self.graph.bind('rdfs', RDFS)
        logger.info("Knowledge graph cleared")
    
    def export_turtle(self) -> str:
        """
        Export graph in Turtle format
        
        Returns:
            String containing Turtle-formatted RDF
        """
        try:
            return self.graph.serialize(format='turtle')
        except Exception as e:
            logger.error(f"Error exporting Turtle: {e}", exc_info=True)
            return ""
    
    def _to_uri(self, value: str) -> URIRef:
        """Convert string to URI (use P2P namespace if not absolute URI)"""
        if value.startswith('http://') or value.startswith('https://'):
            return URIRef(value)
        else:
            # Use P2P namespace, replace spaces/dashes with underscores
            clean_value = value.replace(' ', '_').replace('-', '_')
            return self.P2P[clean_value]
    
    def _to_uri_or_literal(self, value: str) -> Any:
        """Convert string to URI or Literal based on format"""
        if value.startswith('http://') or value.startswith('https://'):
            return URIRef(value)
        elif value.startswith('p2p:') or '_' in value or '-' in value:
            # Looks like an ID - make it a URI
            clean_value = value.replace('p2p:', '').replace(' ', '_').replace('-', '_')
            return self.P2P[clean_value]
        else:
            # Treat as literal value
            return Literal(value)
