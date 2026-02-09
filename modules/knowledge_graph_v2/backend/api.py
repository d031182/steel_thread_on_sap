"""
Knowledge Graph v2 API Endpoints

RESTful API for knowledge graph operations with dependency injection.
"""
from flask import Blueprint, jsonify, request
from pathlib import Path
from functools import wraps

from ..facade import KnowledgeGraphFacadeV2
from ..repositories import SqliteGraphCacheRepository


# Create blueprint
blueprint = Blueprint('knowledge_graph_v2', __name__, url_prefix='/api/v2/knowledge-graph')


def get_facade() -> KnowledgeGraphFacadeV2:
    """
    Factory function to create facade with proper dependencies
    
    Uses dependency injection:
    - SQLite repository (production)
    - CSN directory from docs/csn/
    
    Returns:
        Configured KnowledgeGraphFacadeV2 instance
    """
    # Use default database path (database/p2p_data.db)
    db_path = Path('database/p2p_data.db')
    
    # Create SQLite repository
    cache_repo = SqliteGraphCacheRepository(db_path)
    
    # CSN directory
    csn_dir = Path('docs/csn')
    
    # Create and return facade
    return KnowledgeGraphFacadeV2(cache_repo, csn_dir)


def handle_errors(f):
    """
    Decorator for consistent error handling across all endpoints
    
    Catches exceptions and returns proper HTTP status codes:
    - 200: Success
    - 400: Bad Request (validation errors)
    - 500: Internal Server Error
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except ValueError as e:
            return jsonify({
                'success': False,
                'error': str(e),
                'error_type': 'ValueError'
            }), 400
        except Exception as e:
            return jsonify({
                'success': False,
                'error': str(e),
                'error_type': type(e).__name__
            }), 500
    
    return decorated_function


@blueprint.route('/schema', methods=['GET'])
@handle_errors
def get_schema_graph():
    """
    GET /api/v2/knowledge-graph/schema
    
    Get schema graph (with optional cache bypass)
    
    Query Parameters:
    - use_cache: bool (default: true) - Whether to use cache or force rebuild
    
    Returns:
        200: Success with graph data
        {
            "success": true,
            "graph": {
                "nodes": [...],  // Generic format
                "edges": [...]   // Generic format
            },
            "cache_used": true,
            "metadata": {
                "node_count": 10,
                "edge_count": 15,
                ...
            }
        }
        
        500: Error
        {
            "success": false,
            "error": "Error message",
            "error_type": "ExceptionType"
        }
    
    Example:
        # Get with cache
        curl http://localhost:5001/api/v2/knowledge-graph/schema
        
        # Force rebuild
        curl http://localhost:5001/api/v2/knowledge-graph/schema?use_cache=false
    """
    # Get query parameter (default to true)
    use_cache_param = request.args.get('use_cache', 'true').lower()
    use_cache = use_cache_param not in ('false', '0', 'no')
    
    # Get facade and execute
    facade = get_facade()
    result = facade.get_schema_graph(use_cache=use_cache)
    
    # Return appropriate status code
    status_code = 200 if result['success'] else 500
    return jsonify(result), status_code


@blueprint.route('/schema/rebuild', methods=['POST'])
@handle_errors
def rebuild_schema_graph():
    """
    POST /api/v2/knowledge-graph/schema/rebuild
    
    Force rebuild of schema graph (ignores cache)
    
    Use when:
    - CSN files have been updated
    - Cache is known to be stale
    - Admin requests manual refresh
    
    Returns:
        200: Success with rebuilt graph
        {
            "success": true,
            "graph": {...},
            "cache_used": false,
            "metadata": {...}
        }
        
        500: Error
        {
            "success": false,
            "error": "Error message"
        }
    
    Example:
        curl -X POST http://localhost:5001/api/v2/knowledge-graph/schema/rebuild
    """
    facade = get_facade()
    result = facade.rebuild_schema_graph()
    
    status_code = 200 if result['success'] else 500
    return jsonify(result), status_code


@blueprint.route('/status', methods=['GET'])
@handle_errors
def get_status():
    """
    GET /api/v2/knowledge-graph/status
    
    Get cache status and CSN information
    
    Returns:
        200: Success
        {
            "success": true,
            "cached": true,
            "csn_files_count": 8,
            "csn_directory": "docs/csn"
        }
        
        500: Error
        {
            "success": false,
            "error": "Error message"
        }
    
    Example:
        curl http://localhost:5001/api/v2/knowledge-graph/status
    """
    facade = get_facade()
    result = facade.get_schema_status()
    
    status_code = 200 if result['success'] else 500
    return jsonify(result), status_code


@blueprint.route('/cache', methods=['DELETE'])
@handle_errors
def clear_cache():
    """
    DELETE /api/v2/knowledge-graph/cache
    
    Clear schema graph cache (admin operation)
    
    Returns:
        200: Success
        {
            "success": true,
            "cleared": true
        }
        
        500: Error
        {
            "success": false,
            "error": "Error message"
        }
    
    Example:
        curl -X DELETE http://localhost:5001/api/v2/knowledge-graph/cache
    """
    facade = get_facade()
    result = facade.clear_schema_cache()
    
    status_code = 200 if result['success'] else 500
    return jsonify(result), status_code


@blueprint.route('/health', methods=['GET'])
def health_check():
    """
    GET /api/v2/knowledge-graph/health
    
    Health check endpoint (no authentication required)
    
    Returns:
        200: API is healthy
        {
            "status": "healthy",
            "version": "2.0",
            "api": "knowledge-graph-v2"
        }
    
    Example:
        curl http://localhost:5001/api/v2/knowledge-graph/health
    """
    return jsonify({
        'status': 'healthy',
        'version': '2.0',
        'api': 'knowledge-graph-v2'
    }), 200