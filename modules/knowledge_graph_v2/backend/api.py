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
        
        Get schema graph with optional filtering and pagination
        
        Query Parameters:
        - use_cache: bool (default: true) - Whether to use cache or force rebuild
        - entity_types: str (comma-separated) - Filter by entity types (e.g., "PurchaseOrder,Invoice")
        - limit: int - Limit number of nodes returned
        - offset: int (default: 0) - Offset for pagination
        - include_edges: bool (default: true) - Include edges in response
        - summary: bool (default: false) - Return summary only (counts, no graph data)
        
        Examples:
        - Get summary: /api/knowledge-graph/schema?summary=true
        - Filter entities: /api/knowledge-graph/schema?entity_types=PurchaseOrder,Invoice
        - Paginate: /api/knowledge-graph/schema?limit=100&offset=0
        - Nodes only: /api/knowledge-graph/schema?include_edges=false
        
        Returns:
            200: Success with graph data (or summary) wrapped in 'data'
            400: Invalid parameters
            500: Error
        """
        try:
            # Parse query parameters
            use_cache_param = request.args.get('use_cache', 'true').lower()
            use_cache = use_cache_param not in ('false', '0', 'no')
            
            summary_only = request.args.get('summary', 'false').lower() in ('true', '1', 'yes')
            entity_types_param = request.args.get('entity_types', '')
            entity_types = [t.strip() for t in entity_types_param.split(',') if t.strip()] if entity_types_param else None
            
            limit = request.args.get('limit', type=int)
            offset = request.args.get('offset', type=int, default=0)
            
            include_edges_param = request.args.get('include_edges', 'true').lower()
            include_edges = include_edges_param not in ('false', '0', 'no')
            
            # Validate parameters
            if limit is not None and limit < 1:
                return jsonify({
                    'success': False,
                    'error': 'limit must be >= 1'
                }), 400
            
            if offset < 0:
                return jsonify({
                    'success': False,
                    'error': 'offset must be >= 0'
                }), 400
            
            # Get full graph from facade
            result = self.facade.get_schema_graph(use_cache=use_cache)
            
            if not result['success']:
                return jsonify(result), 500
            
            graph = result['graph']
            metadata = result['metadata']
            
            # Handle summary request
            if summary_only:
                return jsonify({
                    'success': True,
                    'data': {
                        'summary': {
                            'total_nodes': len(graph.get('nodes', [])),
                            'total_edges': len(graph.get('edges', [])),
                            'entity_types': self._get_entity_type_counts(graph.get('nodes', [])),
                            'relationship_types': self._get_relationship_type_counts(graph.get('edges', []))
                        },
                        'metadata': metadata
                    },
                    'cache_used': result.get('cache_used', False)
                }), 200
            
            # Filter nodes by entity types
            nodes = graph.get('nodes', [])
            if entity_types:
                nodes = [n for n in nodes if n.get('type') in entity_types or n.get('entity_type') in entity_types]
            
            # Apply pagination to nodes
            total_nodes = len(nodes)
            if limit is not None:
                nodes = nodes[offset:offset + limit]
            
            # Filter edges if needed
            edges = graph.get('edges', [])
            if not include_edges:
                edges = []
            elif entity_types or limit is not None:
                # Only include edges where both nodes are in the filtered set
                node_ids = {n.get('id') for n in nodes}
                edges = [e for e in edges if e.get('from') in node_ids and e.get('to') in node_ids]
            
            # Build response
            filtered_graph = {
                'nodes': nodes,
                'edges': edges
            }
            
            response = {
                'success': True,
                'data': {
                    'graph': filtered_graph,
                    'metadata': metadata,
                    'pagination': {
                        'total_nodes': total_nodes,
                        'returned_nodes': len(nodes),
                        'offset': offset,
                        'limit': limit
                    }
                },
                'cache_used': result.get('cache_used', False)
            }
            
            return jsonify(response), 200
            
        except Exception as e:
            return jsonify({
                'success': False,
                'error': str(e),
                'error_type': type(e).__name__
            }), 500
    
    def _get_entity_type_counts(self, nodes):
        """Helper to count nodes by entity type"""
        counts = {}
        for node in nodes:
            entity_type = node.get('type') or node.get('entity_type', 'Unknown')
            counts[entity_type] = counts.get(entity_type, 0) + 1
        return counts
    
    def _get_relationship_type_counts(self, edges):
        """Helper to count edges by relationship type"""
        counts = {}
        for edge in edges:
            rel_type = edge.get('label') or edge.get('type', 'Unknown')
            counts[rel_type] = counts.get(rel_type, 0) + 1
        return counts
    
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
    
    def get_table_columns(self, table_name):
        """
        GET /api/knowledge-graph/tables/<table_name>/columns
        
        Get detailed column metadata for a specific table (KGV-001)
        
        Query Parameters:
        - semantic_type: str (optional) - Filter by semantic type (e.g., "amount", "currencyCode")
        - search: str (optional) - Search in column names, labels, or descriptions
        
        Returns:
            200: Success with column details
            404: Table not found
            500: Error
        """
        try:
            # Get query parameters
            semantic_type_filter = request.args.get('semantic_type', '').strip()
            search_term = request.args.get('search', '').strip().lower()
            
            # Get columns from facade
            result = self.facade.get_table_columns(table_name)
            
            if not result['success']:
                status_code = 404 if 'not found' in result.get('error', '').lower() else 500
                return jsonify(result), status_code
            
            columns = result['columns']
            
            # Apply semantic type filter
            if semantic_type_filter:
                columns = [
                    col for col in columns 
                    if col.get('semantic_type') == semantic_type_filter
                ]
            
            # Apply search filter
            if search_term:
                filtered_columns = []
                for col in columns:
                    # Search in name, label, description (handle None values)
                    name = (col.get('name') or '').lower()
                    label = (col.get('display_label') or '').lower()
                    description = (col.get('description') or '').lower()
                    
                    if (search_term in name or
                        search_term in label or
                        search_term in description):
                        filtered_columns.append(col)
                columns = filtered_columns
            
            # Build response
            response = {
                'success': True,
                'data': {
                    'table_name': table_name,
                    'columns': columns,
                    'total_columns': len(columns),
                    'filters_applied': {
                        'semantic_type': semantic_type_filter if semantic_type_filter else None,
                        'search': search_term if search_term else None
                    }
                }
            }
            
            return jsonify(response), 200
            
        except Exception as e:
            return jsonify({
                'success': False,
                'error': str(e),
                'error_type': type(e).__name__
            }), 500
    
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
    
    @blueprint.route('/tables/<table_name>/columns', methods=['GET'])
    @handle_errors
    def get_table_columns(table_name):
        """KGV-001: Get detailed column metadata for table"""
        return api_instance.get_table_columns(table_name)
    
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