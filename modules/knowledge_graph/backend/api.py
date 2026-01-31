"""
Knowledge Graph API Blueprint

Provides REST API endpoints for building and retrieving data relationship graphs.

@author P2P Development Team
@version 1.0.0
"""

from flask import Blueprint, request, jsonify, current_app
import logging

logger = logging.getLogger(__name__)

# Create blueprint
knowledge_graph_api = Blueprint('knowledge_graph', __name__)


@knowledge_graph_api.route('/', methods=['GET'])
def get_knowledge_graph():
    """
    Get knowledge graph visualization
    
    Query Parameters:
        source (str): Data source ('sqlite' or 'hana'), default 'sqlite'
        mode (str): Visualization mode ('schema' or 'data'), default 'schema'
            - schema: Shows data products and tables (architecture view)
            - data: Shows actual data records and relationships (data view)
        max_records (int): Maximum records per table (data mode only), default 20
        filter_orphans (bool): Hide nodes with no connections (data mode only), default True
    
    Returns:
        JSON with nodes, edges, and statistics
    """
    try:
        from modules.knowledge_graph.backend.data_graph_service import DataGraphService
        
        # Get parameters
        source = request.args.get('source', 'sqlite').lower()
        mode = request.args.get('mode', 'schema').lower()
        max_records = request.args.get('max_records', 20, type=int)
        filter_orphans = request.args.get('filter_orphans', 'true').lower() in ['true', '1', 'yes']
        
        # Validate source
        if source not in ['sqlite', 'hana']:
            return jsonify({
                'success': False,
                'error': {
                    'code': 'INVALID_SOURCE',
                    'message': f"Invalid source '{source}'. Must be 'sqlite' or 'hana'"
                }
            }), 400
        
        # Validate mode
        if mode not in ['schema', 'data']:
            return jsonify({
                'success': False,
                'error': {
                    'code': 'INVALID_MODE',
                    'message': f"Invalid mode '{mode}'. Must be 'schema' or 'data'"
                }
            }), 400
        
        # Validate max_records
        if max_records < 1 or max_records > 100:
            return jsonify({
                'success': False,
                'error': {
                    'code': 'INVALID_PARAMETER',
                    'message': 'max_records must be between 1 and 100'
                }
            }), 400
        
        # Get data source from app
        if source == 'sqlite':
            data_source = current_app.sqlite_data_source
        else:
            data_source = current_app.hana_data_source
            if not data_source:
                return jsonify({
                    'success': False,
                    'error': {
                        'code': 'SOURCE_NOT_CONFIGURED',
                        'message': 'HANA data source not configured'
                    }
                }), 503
        
        # Build graph
        logger.info(f"Building {mode} knowledge graph from {source} (max {max_records} records)")
        graph_service = DataGraphService(data_source)
        
        if mode == 'schema':
            result = graph_service.build_schema_graph()
        else:  # mode == 'data'
            result = graph_service.build_data_graph(
                max_records_per_table=max_records,
                filter_orphans=filter_orphans
            )
        
        # Log stats (handle both nested and flat structure)
        if 'stats' in result:
            stats = result['stats']
            logger.info(f"Knowledge graph built: {stats['node_count']} nodes, {stats['edge_count']} edges")
        else:
            logger.info(f"Knowledge graph built: {len(result.get('nodes', []))} nodes, {len(result.get('edges', []))} edges")
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Error in get_knowledge_graph: {e}", exc_info=True)
        return jsonify({
            'success': False,
            'error': {
                'code': 'SERVER_ERROR',
                'message': str(e)
            }
        }), 500


@knowledge_graph_api.route('/health', methods=['GET'])
def health_check():
    """
    Health check endpoint
    
    Returns:
        JSON with module status
    """
    return jsonify({
        'success': True,
        'module': 'knowledge_graph',
        'status': 'healthy',
        'endpoints': ['/', '/stats', '/health']
    })


@knowledge_graph_api.route('/stats', methods=['GET'])
def get_graph_stats():
    """
    Get statistics about available data for graphing
    
    Query Parameters:
        source (str): Data source ('sqlite' or 'hana'), default 'sqlite'
    
    Returns:
        JSON with table count and record counts
    """
    try:
        source = request.args.get('source', 'sqlite').lower()
        
        # Get data source
        if source == 'sqlite':
            data_source = current_app.sqlite_data_source
        else:
            data_source = current_app.hana_data_source
            if not data_source:
                return jsonify({
                    'success': False,
                    'error': {
                        'code': 'SOURCE_NOT_CONFIGURED',
                        'message': 'HANA data source not configured'
                    }
                }), 503
        
        # Get table count
        products = data_source.get_data_products()
        
        total_tables = 0
        for product in products:
            tables = data_source.get_tables(product['schemaName'])
            total_tables += len(tables) if tables else 0
        
        return jsonify({
            'success': True,
            'stats': {
                'source': source,
                'product_count': len(products),
                'table_count': total_tables
            }
        })
        
    except Exception as e:
        logger.error(f"Error in get_graph_stats: {e}", exc_info=True)
        return jsonify({
            'success': False,
            'error': {
                'code': 'SERVER_ERROR',
                'message': str(e)
            }
        }), 500


@knowledge_graph_api.route('/algorithms/centrality', methods=['POST'])
def calculate_centrality():
    """
    Calculate node centrality (criticality/importance)
    
    Request Body:
        {
            "source": "sqlite" | "hana",
            "algorithm": "betweenness" | "pagerank" | "degree" | "closeness"
        }
    
    Returns:
        JSON with centrality scores for each node
    """
    try:
        from modules.knowledge_graph.backend.data_graph_service import DataGraphService
        from modules.knowledge_graph.backend.property_graph_service import NetworkXPropertyGraph
        
        data = request.get_json()
        source = data.get('source', 'sqlite').lower()
        algorithm = data.get('algorithm', 'betweenness').lower()
        
        # Validate algorithm
        valid_algorithms = ['betweenness', 'pagerank', 'degree', 'closeness']
        if algorithm not in valid_algorithms:
            return jsonify({
                'success': False,
                'error': {
                    'code': 'INVALID_ALGORITHM',
                    'message': f"Algorithm must be one of: {', '.join(valid_algorithms)}"
                }
            }), 400
        
        # Get data source
        data_source = current_app.sqlite_data_source if source == 'sqlite' else current_app.hana_data_source
        if not data_source:
            return jsonify({
                'success': False,
                'error': {
                    'code': 'SOURCE_NOT_CONFIGURED',
                    'message': f'{source.upper()} data source not configured'
                }
            }), 503
        
        # Build schema graph
        graph_service = DataGraphService(data_source)
        graph_dict = graph_service.build_schema_graph()
        
        if not graph_dict.get('success'):
            return jsonify(graph_dict), 500
        
        # Load into NetworkX and calculate centrality
        property_graph = NetworkXPropertyGraph()
        property_graph.load_from_dict(graph_dict)
        scores = property_graph.centrality(algorithm)
        
        # Sort by score (highest first)
        sorted_scores = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        
        logger.info(f"Calculated {algorithm} centrality: {len(scores)} nodes")
        
        return jsonify({
            'success': True,
            'algorithm': algorithm,
            'scores': dict(sorted_scores),
            'top_10': [{'node': node, 'score': score} for node, score in sorted_scores[:10]]
        })
        
    except Exception as e:
        logger.error(f"Error calculating centrality: {e}", exc_info=True)
        return jsonify({
            'success': False,
            'error': {
                'code': 'SERVER_ERROR',
                'message': str(e)
            }
        }), 500


@knowledge_graph_api.route('/algorithms/communities', methods=['POST'])
def detect_communities():
    """
    Detect communities/clusters in graph
    
    Request Body:
        {
            "source": "sqlite" | "hana",
            "algorithm": "louvain" | "label_propagation" | "greedy_modularity"
        }
    
    Returns:
        JSON with community assignments and cluster statistics
    """
    try:
        from modules.knowledge_graph.backend.data_graph_service import DataGraphService
        from modules.knowledge_graph.backend.property_graph_service import NetworkXPropertyGraph
        
        data = request.get_json()
        source = data.get('source', 'sqlite').lower()
        algorithm = data.get('algorithm', 'louvain').lower()
        
        # Validate algorithm
        valid_algorithms = ['louvain', 'label_propagation', 'greedy_modularity']
        if algorithm not in valid_algorithms:
            return jsonify({
                'success': False,
                'error': {
                    'code': 'INVALID_ALGORITHM',
                    'message': f"Algorithm must be one of: {', '.join(valid_algorithms)}"
                }
            }), 400
        
        # Get data source
        data_source = current_app.sqlite_data_source if source == 'sqlite' else current_app.hana_data_source
        if not data_source:
            return jsonify({
                'success': False,
                'error': {
                    'code': 'SOURCE_NOT_CONFIGURED',
                    'message': f'{source.upper()} data source not configured'
                }
            }), 503
        
        # Build schema graph
        graph_service = DataGraphService(data_source)
        graph_dict = graph_service.build_schema_graph()
        
        if not graph_dict.get('success'):
            return jsonify(graph_dict), 500
        
        # Load into NetworkX and detect communities
        property_graph = NetworkXPropertyGraph()
        property_graph.load_from_dict(graph_dict)
        communities = property_graph.community_detection(algorithm)
        
        # Calculate cluster statistics
        cluster_stats = {}
        for node, cluster in communities.items():
            if cluster not in cluster_stats:
                cluster_stats[cluster] = {'count': 0, 'nodes': []}
            cluster_stats[cluster]['count'] += 1
            cluster_stats[cluster]['nodes'].append(node)
        
        logger.info(f"Detected {len(cluster_stats)} communities using {algorithm}")
        
        return jsonify({
            'success': True,
            'algorithm': algorithm,
            'communities': communities,
            'cluster_stats': cluster_stats,
            'num_clusters': len(cluster_stats)
        })
        
    except Exception as e:
        logger.error(f"Error detecting communities: {e}", exc_info=True)
        return jsonify({
            'success': False,
            'error': {
                'code': 'SERVER_ERROR',
                'message': str(e)
            }
        }), 500


@knowledge_graph_api.route('/algorithms/shortest-path', methods=['POST'])
def find_shortest_path():
    """
    Find shortest path between two nodes
    
    Request Body:
        {
            "source": "sqlite" | "hana",
            "start": "node_id_start",
            "end": "node_id_end"
        }
    
    Returns:
        JSON with path as list of node IDs
    """
    try:
        from modules.knowledge_graph.backend.data_graph_service import DataGraphService
        from modules.knowledge_graph.backend.property_graph_service import NetworkXPropertyGraph
        
        data = request.get_json()
        source = data.get('source', 'sqlite').lower()
        start = data.get('start')
        end = data.get('end')
        
        # Validate inputs
        if not start or not end:
            return jsonify({
                'success': False,
                'error': {
                    'code': 'MISSING_PARAMETER',
                    'message': 'Both start and end node IDs are required'
                }
            }), 400
        
        # Get data source
        data_source = current_app.sqlite_data_source if source == 'sqlite' else current_app.hana_data_source
        if not data_source:
            return jsonify({
                'success': False,
                'error': {
                    'code': 'SOURCE_NOT_CONFIGURED',
                    'message': f'{source.upper()} data source not configured'
                }
            }), 503
        
        # Build schema graph
        graph_service = DataGraphService(data_source)
        graph_dict = graph_service.build_schema_graph()
        
        if not graph_dict.get('success'):
            return jsonify(graph_dict), 500
        
        # Load into NetworkX and find path
        property_graph = NetworkXPropertyGraph()
        property_graph.load_from_dict(graph_dict)
        path = property_graph.shortest_path(start, end)
        
        if path:
            logger.info(f"Found path from {start} to {end}: {len(path)} nodes")
            return jsonify({
                'success': True,
                'path': path,
                'length': len(path)
            })
        else:
            return jsonify({
                'success': False,
                'error': {
                    'code': 'NO_PATH',
                    'message': f'No path exists between {start} and {end}'
                }
            }), 404
        
    except Exception as e:
        logger.error(f"Error finding shortest path: {e}", exc_info=True)
        return jsonify({
            'success': False,
            'error': {
                'code': 'SERVER_ERROR',
                'message': str(e)
            }
        }), 500


@knowledge_graph_api.route('/cache/refresh', methods=['POST'])
def refresh_ontology_cache():
    """
    Refresh the ontology cache by rediscovering relationships from CSN
    
    Use this endpoint when:
    - Database schema changes (new tables added)
    - CSN files updated
    - You want to force cache invalidation
    
    Request Body:
        {
            "source": "sqlite" | "hana" (optional, default "sqlite")
        }
    
    Returns:
        JSON with refresh statistics
    """
    try:
        from core.services.ontology_persistence_service import OntologyPersistenceService
        from core.services.csn_parser import CSNParser
        from core.services.relationship_mapper import CSNRelationshipMapper
        
        data = request.get_json() or {}
        source = data.get('source', 'sqlite').lower()
        
        # Get data source
        data_source = current_app.sqlite_data_source if source == 'sqlite' else current_app.hana_data_source
        if not data_source:
            return jsonify({
                'success': False,
                'error': {
                    'code': 'SOURCE_NOT_CONFIGURED',
                    'message': f'{source.upper()} data source not configured'
                }
            }), 503
        
        # Get database path from data source
        if hasattr(data_source, 'service') and hasattr(data_source.service, 'db_path'):
            db_path = data_source.service.db_path
        else:
            db_path = 'app/database/p2p_data_products.db'
        
        # Initialize services
        persistence = OntologyPersistenceService(db_path)
        csn_parser = CSNParser('docs/csn')
        mapper = CSNRelationshipMapper(csn_parser)
        
        # Clear existing cache
        logger.info("Clearing ontology cache...")
        cleared_count = persistence.clear_cache()
        
        # Rediscover relationships from CSN
        logger.info("Rediscovering relationships from CSN...")
        import time
        start = time.time()
        
        relationships = mapper.discover_relationships()
        discovery_time = (time.time() - start) * 1000
        
        # Convert to persistence format
        rel_dicts = [
            {
                'source_table': rel.from_entity,
                'source_column': rel.from_column,
                'target_table': rel.to_entity,
                'target_column': rel.to_column,
                'type': rel.relationship_type,
                'confidence': rel.confidence
            }
            for rel in relationships
        ]
        
        # Persist new relationships
        inserted, updated = persistence.persist_relationships(rel_dicts, 'csn_metadata')
        
        logger.info(f"Cache refreshed: {inserted} new, {updated} updated relationships")
        
        return jsonify({
            'success': True,
            'statistics': {
                'cleared': cleared_count,
                'discovered': len(relationships),
                'inserted': inserted,
                'updated': updated,
                'discovery_time_ms': round(discovery_time, 2)
            },
            'message': f'Cache refreshed successfully. Discovered {len(relationships)} relationships in {discovery_time:.0f}ms'
        })
        
    except Exception as e:
        logger.error(f"Error refreshing cache: {e}", exc_info=True)
        return jsonify({
            'success': False,
            'error': {
                'code': 'REFRESH_ERROR',
                'message': str(e)
            }
        }), 500


@knowledge_graph_api.route('/cache/status', methods=['GET'])
def get_cache_status():
    """
    Get current status of the ontology cache
    
    Query Parameters:
        source (str): Data source ('sqlite' or 'hana'), default 'sqlite'
    
    Returns:
        JSON with cache statistics
    """
    try:
        from core.services.ontology_persistence_service import OntologyPersistenceService
        
        source = request.args.get('source', 'sqlite').lower()
        
        # Get data source
        data_source = current_app.sqlite_data_source if source == 'sqlite' else current_app.hana_data_source
        if not data_source:
            return jsonify({
                'success': False,
                'error': {
                    'code': 'SOURCE_NOT_CONFIGURED',
                    'message': f'{source.upper()} data source not configured'
                }
            }), 503
        
        # Get database path
        if hasattr(data_source, 'service') and hasattr(data_source.service, 'db_path'):
            db_path = data_source.service.db_path
        else:
            db_path = 'app/database/p2p_data_products.db'
        
        # Get statistics
        persistence = OntologyPersistenceService(db_path)
        stats = persistence.get_statistics()
        
        return jsonify({
            'success': True,
            'source': source,
            'cache': stats
        })
        
    except Exception as e:
        logger.error(f"Error getting cache status: {e}", exc_info=True)
        return jsonify({
            'success': False,
            'error': {
                'code': 'STATUS_ERROR',
                'message': str(e)
            }
        }), 500


@knowledge_graph_api.route('/query/neighbors', methods=['POST'])
def query_neighbors():
    """
    Get neighbors using unified GraphQueryService (10-100x faster for HANA)
    
    NEW in v3.15: Uses GraphQueryService with automatic backend selection
    - HANA → HANAGraphQueryEngine (native Property Graph queries)
    - SQLite → NetworkXGraphQueryEngine (optimized local queries)
    
    Request Body:
        {
            "source": "sqlite" | "hana",
            "node_id": "PurchaseOrder:12345",
            "direction": "outgoing" | "incoming" | "both" (optional, default "outgoing"),
            "edge_types": ["contains", "references"] (optional),
            "limit": 10 (optional)
        }
    
    Returns:
        JSON with list of neighbor nodes (GraphNode objects)
    """
    try:
        from core.services.graph_query_service import GraphQueryService
        from core.interfaces.graph_query import TraversalDirection
        
        data = request.get_json()
        source = data.get('source', 'sqlite').lower()
        node_id = data.get('node_id')
        direction_str = data.get('direction', 'outgoing').lower()
        edge_types = data.get('edge_types')
        limit = data.get('limit')
        
        # Validate inputs
        if not node_id:
            return jsonify({
                'success': False,
                'error': {
                    'code': 'MISSING_PARAMETER',
                    'message': 'node_id is required'
                }
            }), 400
        
        # Map direction string to enum
        direction_map = {
            'outgoing': TraversalDirection.OUTGOING,
            'incoming': TraversalDirection.INCOMING,
            'both': TraversalDirection.BOTH
        }
        direction = direction_map.get(direction_str, TraversalDirection.OUTGOING)
        
        # Get data source
        data_source = current_app.sqlite_data_source if source == 'sqlite' else current_app.hana_data_source
        if not data_source:
            return jsonify({
                'success': False,
                'error': {
                    'code': 'SOURCE_NOT_CONFIGURED',
                    'message': f'{source.upper()} data source not configured'
                }
            }), 503
        
        # Use GraphQueryService (auto-selects engine)
        graph_service = GraphQueryService(data_source)
        backend_info = graph_service.get_backend_info()
        
        # Execute query
        neighbors = graph_service.get_neighbors(node_id, direction, edge_types, limit)
        
        # Convert GraphNode objects to JSON-serializable dicts
        neighbors_data = [
            {
                'id': n.id,
                'label': n.label,
                'properties': n.properties
            }
            for n in neighbors
        ]
        
        logger.info(f"Found {len(neighbors_data)} neighbors for {node_id} using {backend_info['backend']}")
        
        return jsonify({
            'success': True,
            'node_id': node_id,
            'direction': direction_str,
            'neighbors': neighbors_data,
            'count': len(neighbors_data),
            'backend': backend_info
        })
        
    except Exception as e:
        logger.error(f"Error in query_neighbors: {e}", exc_info=True)
        return jsonify({
            'success': False,
            'error': {
                'code': 'SERVER_ERROR',
                'message': str(e)
            }
        }), 500


@knowledge_graph_api.route('/query/path', methods=['POST'])
def query_shortest_path():
    """
    Find shortest path using unified GraphQueryService (10-100x faster for HANA)
    
    NEW in v3.15: Uses GraphQueryService with automatic backend selection
    
    Request Body:
        {
            "source": "sqlite" | "hana",
            "start_id": "Supplier:SUP001",
            "end_id": "Invoice:INV123",
            "max_hops": 10 (optional)
        }
    
    Returns:
        JSON with path as list of nodes
    """
    try:
        from core.services.graph_query_service import GraphQueryService
        
        data = request.get_json()
        source = data.get('source', 'sqlite').lower()
        start_id = data.get('start_id')
        end_id = data.get('end_id')
        max_hops = data.get('max_hops', 10)
        
        # Validate inputs
        if not start_id or not end_id:
            return jsonify({
                'success': False,
                'error': {
                    'code': 'MISSING_PARAMETER',
                    'message': 'Both start_id and end_id are required'
                }
            }), 400
        
        # Get data source
        data_source = current_app.sqlite_data_source if source == 'sqlite' else current_app.hana_data_source
        if not data_source:
            return jsonify({
                'success': False,
                'error': {
                    'code': 'SOURCE_NOT_CONFIGURED',
                    'message': f'{source.upper()} data source not configured'
                }
            }), 503
        
        # Use GraphQueryService
        graph_service = GraphQueryService(data_source)
        backend_info = graph_service.get_backend_info()
        
        # Execute query
        path = graph_service.shortest_path(start_id, end_id, max_hops)
        
        if path:
            # Convert GraphPath to JSON
            path_data = {
                'nodes': [
                    {
                        'id': n.id,
                        'label': n.label,
                        'properties': n.properties
                    }
                    for n in path.nodes
                ],
                'edges': [
                    {
                        'from': e.source_id,
                        'to': e.target_id,
                        'type': e.edge_type,
                        'properties': e.properties
                    }
                    for e in path.edges
                ],
                'length': path.length,
                'total_cost': path.total_cost
            }
            
            logger.info(f"Found path from {start_id} to {end_id}: {path.length} hops using {backend_info['backend']}")
            
            return jsonify({
                'success': True,
                'start_id': start_id,
                'end_id': end_id,
                'path': path_data,
                'backend': backend_info
            })
        else:
            return jsonify({
                'success': False,
                'error': {
                    'code': 'NO_PATH',
                    'message': f'No path exists between {start_id} and {end_id} within {max_hops} hops'
                }
            }), 404
        
    except Exception as e:
        logger.error(f"Error in query_shortest_path: {e}", exc_info=True)
        return jsonify({
            'success': False,
            'error': {
                'code': 'SERVER_ERROR',
                'message': str(e)
            }
        }), 500


@knowledge_graph_api.route('/query/traverse', methods=['POST'])
def query_traverse():
    """
    Breadth-first traversal using unified GraphQueryService
    
    NEW in v3.15: Fast traversal with automatic backend selection
    
    Request Body:
        {
            "source": "sqlite" | "hana",
            "start_id": "PurchaseOrder:12345",
            "depth": 2 (optional, default 2),
            "direction": "outgoing" | "incoming" | "both" (optional),
            "edge_types": ["contains"] (optional)
        }
    
    Returns:
        JSON with list of reachable nodes
    """
    try:
        from core.services.graph_query_service import GraphQueryService
        from core.interfaces.graph_query import TraversalDirection
        
        data = request.get_json()
        source = data.get('source', 'sqlite').lower()
        start_id = data.get('start_id')
        depth = data.get('depth', 2)
        direction_str = data.get('direction', 'outgoing').lower()
        edge_types = data.get('edge_types')
        
        if not start_id:
            return jsonify({
                'success': False,
                'error': {
                    'code': 'MISSING_PARAMETER',
                    'message': 'start_id is required'
                }
            }), 400
        
        # Map direction
        direction_map = {
            'outgoing': TraversalDirection.OUTGOING,
            'incoming': TraversalDirection.INCOMING,
            'both': TraversalDirection.BOTH
        }
        direction = direction_map.get(direction_str, TraversalDirection.OUTGOING)
        
        # Get data source
        data_source = current_app.sqlite_data_source if source == 'sqlite' else current_app.hana_data_source
        if not data_source:
            return jsonify({
                'success': False,
                'error': {
                    'code': 'SOURCE_NOT_CONFIGURED',
                    'message': f'{source.upper()} data source not configured'
                }
            }), 503
        
        # Use GraphQueryService
        graph_service = GraphQueryService(data_source)
        backend_info = graph_service.get_backend_info()
        
        # Execute traversal
        nodes = graph_service.traverse(start_id, depth, direction, edge_types)
        
        # Convert to JSON
        nodes_data = [
            {
                'id': n.id,
                'label': n.label,
                'properties': n.properties
            }
            for n in nodes
        ]
        
        logger.info(f"Traversed from {start_id} depth {depth}: {len(nodes_data)} nodes using {backend_info['backend']}")
        
        return jsonify({
            'success': True,
            'start_id': start_id,
            'depth': depth,
            'direction': direction_str,
            'nodes': nodes_data,
            'count': len(nodes_data),
            'backend': backend_info
        })
        
    except Exception as e:
        logger.error(f"Error in query_traverse: {e}", exc_info=True)
        return jsonify({
            'success': False,
            'error': {
                'code': 'SERVER_ERROR',
                'message': str(e)
            }
        }), 500


@knowledge_graph_api.route('/algorithms/neighbors', methods=['POST'])
def get_neighbors():
    """
    Get neighbors of a node within specified distance
    
    DEPRECATED: Use /query/neighbors for better performance (10-100x faster)
    
    Request Body:
        {
            "source": "sqlite" | "hana",
            "node_id": "node_id",
            "max_distance": 1 (optional, default 1)
        }
    
    Returns:
        JSON with list of neighbor node IDs
    """
    try:
        from modules.knowledge_graph.backend.data_graph_service import DataGraphService
        from modules.knowledge_graph.backend.property_graph_service import NetworkXPropertyGraph
        
        data = request.get_json()
        source = data.get('source', 'sqlite').lower()
        node_id = data.get('node_id')
        max_distance = data.get('max_distance', 1)
        
        # Validate inputs
        if not node_id:
            return jsonify({
                'success': False,
                'error': {
                    'code': 'MISSING_PARAMETER',
                    'message': 'node_id is required'
                }
            }), 400
        
        # Get data source
        data_source = current_app.sqlite_data_source if source == 'sqlite' else current_app.hana_data_source
        if not data_source:
            return jsonify({
                'success': False,
                'error': {
                    'code': 'SOURCE_NOT_CONFIGURED',
                    'message': f'{source.upper()} data source not configured'
                }
            }), 503
        
        # Build schema graph
        graph_service = DataGraphService(data_source)
        graph_dict = graph_service.build_schema_graph()
        
        if not graph_dict.get('success'):
            return jsonify(graph_dict), 500
        
        # Load into NetworkX and get neighbors
        property_graph = NetworkXPropertyGraph()
        property_graph.load_from_dict(graph_dict)
        neighbors = property_graph.get_neighbors(node_id, max_distance)
        
        logger.info(f"Found {len(neighbors)} neighbors within distance {max_distance} of {node_id}")
        
        return jsonify({
            'success': True,
            'node_id': node_id,
            'max_distance': max_distance,
            'neighbors': neighbors,
            'count': len(neighbors)
        })
        
    except Exception as e:
        logger.error(f"Error getting neighbors: {e}", exc_info=True)
        return jsonify({
            'success': False,
            'error': {
                'code': 'SERVER_ERROR',
                'message': str(e)
            }
        }), 500
