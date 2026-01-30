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