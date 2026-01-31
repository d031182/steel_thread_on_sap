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
    
    Returns:
        JSON with nodes, edges, and statistics
    """
    try:
        from modules.knowledge_graph.backend.data_graph_service import DataGraphService
        
        # Get parameters
        source = request.args.get('source', 'sqlite').lower()
        mode = request.args.get('mode', 'schema').lower()
        max_records = request.args.get('max_records', 20, type=int)
        
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
            result = graph_service.build_data_graph(max_records_per_table=max_records)
        
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


@knowledge_graph_api.route('/algorithms/neighbors', methods=['POST'])
def get_neighbors():
    """
    Get neighbors of a node within specified distance
    
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
