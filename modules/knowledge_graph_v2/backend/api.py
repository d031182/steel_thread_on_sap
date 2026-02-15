"""
Knowledge Graph v2 API Endpoints

RESTful API for knowledge graph operations with dependency injection.
Version 2.0.0 - Constructor Injection Pattern
"""
from flask import Blueprint, jsonify, request
from functools import wraps

from ..facade import KnowledgeGraphFacadeV2


class KnowledgeGraphV2API:
    """
    API class with dependency injection
    
    Follows Constructor Injection pattern - facade is injected via constructor.
    This avoids Service Locator anti-pattern and enables proper testing.
    
    Usage:
        facade = KnowledgeGraphFacadeV2(cache_repo, csn_dir)
        api = KnowledgeGraphV2API(facade)
        blueprint = create_blueprint(api)
    """
    
    def __init__(self, facade: KnowledgeGraphFacadeV2):
        """
        Initialize API with injected facade
        
        Args:
            facade: Configured KnowledgeGraphFacadeV2 instance
        """
        self.facade = facade
    
    def get_schema_graph(self):
        """
        GET /api/knowledge-graph/schema
        
        Get schema graph (with optional cache bypass)
        
        Query Parameters:
        - use_cache: bool (default: true) - Whether to use cache or force rebuild
        
        Returns:
            200: Success with graph data
            500: Error
        """
        # Get query parameter (default to true)
        use_cache_param = request.args.get('use_cache', 'true').lower()
        use_cache = use_cache_param not in ('false', '0', 'no')
        
        # Get facade and execute
        result = self.facade.get_schema_graph(use_cache=use_cache)
        
        # Return appropriate status code
        status_code = 200 if result['success'] else 500
        return jsonify(result), status_code
    
    def rebuild_schema_graph(self):
        """
        POST /api/knowledge-graph/schema/rebuild
        
        Force rebuild of schema graph (ignores cache)
        
        Returns:
            200: Success with rebuilt graph
            500: Error
        """
        result = self.facade.rebuild_schema_graph()
        
        status_code = 200 if result['success'] else 500
        return jsonify(result), status_code
    
    def get_status(self):
        """
        GET /api/knowledge-graph/status
        
        Get cache status and CSN information
        
        Returns:
            200: Success
            500: Error
        """
        result = self.facade.get_schema_status()
        
        status_code = 200 if result['success'] else 500
        return jsonify(result), status_code
    
    def clear_cache(self):
        """
        DELETE /api/knowledge-graph/cache
        
        Clear schema graph cache (admin operation)
        
        Returns:
            200: Success
            500: Error
        """
        result = self.facade.clear_schema_cache()
        
        status_code = 200 if result['success'] else 500
        return jsonify(result), status_code


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


def create_blueprint(api_instance: KnowledgeGraphV2API) -> Blueprint:
    """
    Factory function to create Flask blueprint with injected API instance
    
    This is the composition root - dependencies are wired here.
    
    Args:
        api_instance: Configured KnowledgeGraphV2API with facade injected
    
    Returns:
        Flask Blueprint ready to register with app
    
    Example:
        # In server.py
        facade = KnowledgeGraphFacadeV2(cache_repo, csn_dir)
        api = KnowledgeGraphV2API(facade)
        blueprint = create_blueprint(api)
        app.register_blueprint(blueprint)
    """
    blueprint = Blueprint('knowledge_graph_v2', __name__, url_prefix='/api/knowledge-graph')
    
    @blueprint.route('/schema', methods=['GET'])
    @handle_errors
    def get_schema_graph():
        return api_instance.get_schema_graph()
    
    @blueprint.route('/schema/rebuild', methods=['POST'])
    @handle_errors
    def rebuild_schema_graph():
        return api_instance.rebuild_schema_graph()
    
    @blueprint.route('/status', methods=['GET'])
    @handle_errors
    def get_status():
        return api_instance.get_status()
    
    @blueprint.route('/cache', methods=['DELETE'])
    @handle_errors
    def clear_cache():
        return api_instance.clear_cache()
    
    @blueprint.route('/health', methods=['GET'])
    def health_check():
        """Health check endpoint (no authentication required)"""
        return jsonify({
            'status': 'healthy',
            'version': '2.0.0',
            'api': 'knowledge-graph-v2'
        }), 200
    
    return blueprint