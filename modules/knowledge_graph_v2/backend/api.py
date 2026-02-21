"""
Knowledge Graph v2 API Endpoints

RESTful API for knowledge graph operations with dependency injection.
Version 2.0.0 - Constructor Injection Pattern
"""
from flask import Blueprint, jsonify, request
from functools import wraps

from ..facade import KnowledgeGraphFacadeV2
from .query_template_api import query_template_bp


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
            200: Success with graph data wrapped in 'data'
            500: Error
        """
        # Get query parameter (default to true)
        use_cache_param = request.args.get('use_cache', 'true').lower()
        use_cache = use_cache_param not in ('false', '0', 'no')
        
        # Get facade and execute
        result = self.facade.get_schema_graph(use_cache=use_cache)
        
        # Wrap graph and metadata in 'data' for consistency
        if result['success']:
            response = {
                'success': True,
                'data': {
                    'graph': result['graph'],
                    'metadata': result['metadata']
                },
                'cache_used': result.get('cache_used', False)
            }
        else:
            response = result
        
        # Return appropriate status code
        status_code = 200 if result['success'] else 500
        return jsonify(response), status_code
    
    def rebuild_schema_graph(self):
        """
        POST /api/knowledge-graph/schema/rebuild
        
        Force rebuild of schema graph (ignores cache)
        
        Returns:
            200: Success with rebuilt graph wrapped in 'data'
            500: Error
        """
        result = self.facade.rebuild_schema_graph()
        
        # Wrap graph and metadata in 'data' for consistency
        if result['success']:
            response = {
                'success': True,
                'data': {
                    'graph': result['graph'],
                    'metadata': result['metadata']
                },
                'cache_used': result.get('cache_used', False)
            }
        else:
            response = result
        
        status_code = 200 if result['success'] else 500
        return jsonify(response), status_code
    
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
    
    # ========================================================================
    # Advanced Query Endpoints (HIGH-31: Phase 3)
    # ========================================================================
    
    def get_pagerank(self):
        """
        GET /api/knowledge-graph/analytics/pagerank
        
        Calculate PageRank centrality scores
        
        Query Parameters:
        - top_k: int (default: 10) - Number of top nodes to return
        - damping_factor: float (default: 0.85) - PageRank damping factor
        
        Returns:
            200: Success with PageRank scores
            400: Invalid parameters
            500: Error
        """
        try:
            top_k = int(request.args.get('top_k', 10))
            damping_factor = float(request.args.get('damping_factor', 0.85))
            
            if top_k < 1:
                return jsonify({
                    'success': False,
                    'error': 'top_k must be >= 1'
                }), 400
            
            if not (0.0 < damping_factor < 1.0):
                return jsonify({
                    'success': False,
                    'error': 'damping_factor must be between 0 and 1'
                }), 400
            
            result = self.facade.get_pagerank(top_k, damping_factor)
            status_code = 200 if result['success'] else 500
            return jsonify(result), status_code
            
        except ValueError as e:
            return jsonify({
                'success': False,
                'error': str(e),
                'error_type': 'ValueError'
            }), 400
    
    def get_centrality(self):
        """
        GET /api/knowledge-graph/analytics/centrality
        
        Calculate centrality metrics
        
        Query Parameters:
        - metric: str (default: betweenness) - Centrality type
        - top_k: int (default: 10) - Number of top nodes to return
        
        Returns:
            200: Success with centrality scores
            400: Invalid parameters
            500: Error
        """
        try:
            metric = request.args.get('metric', 'betweenness')
            top_k = int(request.args.get('top_k', 10))
            
            if top_k < 1:
                return jsonify({
                    'success': False,
                    'error': 'top_k must be >= 1'
                }), 400
            
            result = self.facade.get_centrality(metric, top_k)
            status_code = 200 if result['success'] else 500
            return jsonify(result), status_code
            
        except ValueError as e:
            return jsonify({
                'success': False,
                'error': str(e),
                'error_type': 'ValueError'
            }), 400
    
    def detect_communities(self):
        """
        GET /api/knowledge-graph/analytics/communities
        
        Detect communities in graph
        
        Query Parameters:
        - algorithm: str (default: louvain) - Detection algorithm
        
        Returns:
            200: Success with community assignments
            400: Invalid parameters
            500: Error
        """
        algorithm = request.args.get('algorithm', 'louvain')
        
        result = self.facade.detect_communities(algorithm)
        status_code = 200 if result['success'] else 500
        return jsonify(result), status_code
    
    def find_cycles(self):
        """
        GET /api/knowledge-graph/analytics/cycles
        
        Find all cycles in graph
        
        Returns:
            200: Success with cycles
            500: Error (or not implemented)
        """
        result = self.facade.find_cycles()
        status_code = 200 if result['success'] else 500
        return jsonify(result), status_code
    
    def get_connected_components(self):
        """
        GET /api/knowledge-graph/analytics/components
        
        Find connected components in graph
        
        Returns:
            200: Success with components
            500: Error (or not implemented)
        """
        result = self.facade.get_connected_components()
        status_code = 200 if result['success'] else 500
        return jsonify(result), status_code
    
    def get_graph_statistics(self):
        """
        GET /api/knowledge-graph/analytics/statistics
        
        Get comprehensive graph statistics
        
        Returns:
            200: Success with statistics
            500: Error
        """
        result = self.facade.get_graph_statistics()
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
        Flask Blueprint ready to register with app (with query template blueprint registered)
    
    Example:
        # In server.py
        facade = KnowledgeGraphFacadeV2(cache_repo, csn_dir)
        api = KnowledgeGraphV2API(facade)
        blueprint = create_blueprint(api)
        app.register_blueprint(blueprint)
    """
    blueprint = Blueprint('knowledge_graph_v2', __name__, url_prefix='/api/knowledge-graph')
    
    # Register query templates blueprint with correct url_prefix
    blueprint.register_blueprint(query_template_bp, url_prefix='/query-templates')
    
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
    
    # ========================================================================
    # Advanced Analytics Routes (HIGH-31: Phase 3)
    # ========================================================================
    
    @blueprint.route('/analytics/pagerank', methods=['GET'])
    @handle_errors
    def get_pagerank():
        return api_instance.get_pagerank()
    
    @blueprint.route('/analytics/centrality', methods=['GET'])
    @handle_errors
    def get_centrality():
        return api_instance.get_centrality()
    
    @blueprint.route('/analytics/communities', methods=['GET'])
    @handle_errors
    def detect_communities():
        return api_instance.detect_communities()
    
    @blueprint.route('/analytics/cycles', methods=['GET'])
    @handle_errors
    def find_cycles():
        return api_instance.find_cycles()
    
    @blueprint.route('/analytics/components', methods=['GET'])
    @handle_errors
    def get_connected_components():
        return api_instance.get_connected_components()
    
    @blueprint.route('/analytics/statistics', methods=['GET'])
    @handle_errors
    def get_graph_statistics():
        return api_instance.get_graph_statistics()
    
    return blueprint
