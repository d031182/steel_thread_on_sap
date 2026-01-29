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
knowledge_graph_api = Blueprint('knowledge_graph', __name__, url_prefix='/api/knowledge-graph')


@knowledge_graph_api.route('/', methods=['GET'])
def get_knowledge_graph():
    """
    Get knowledge graph of actual data relationships
    
    Query Parameters:
        source (str): Data source ('sqlite' or 'hana'), default 'sqlite'
        max_records (int): Maximum records per table, default 20
    
    Returns:
        JSON with nodes, edges, and statistics
    """
    try:
        from modules.knowledge_graph.backend.data_graph_service import DataGraphService
        
        # Get parameters
        source = request.args.get('source', 'sqlite').lower()
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
        logger.info(f"Building knowledge graph from {source} (max {max_records} records)")
        graph_service = DataGraphService(data_source)
        result = graph_service.build_data_graph(max_records_per_table=max_records)
        
        logger.info(f"Knowledge graph built: {result['stats']['node_count']} nodes, {result['stats']['edge_count']} edges")
        
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