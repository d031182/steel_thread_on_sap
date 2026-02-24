"""
Query Template API Endpoints

Provides RESTful API for managing and executing query templates.
Templates enable reusable, parameterized queries for common graph operations.

API Endpoints:
    GET    /api/knowledge-graph/query-templates              - List all templates
    GET    /api/knowledge-graph/query-templates/<id>         - Get template details
    GET    /api/knowledge-graph/query-templates/search       - Search templates
    POST   /api/knowledge-graph/query-templates/<id>/validate - Validate parameters
    POST   /api/knowledge-graph/query-templates/<id>/render   - Render query

Architecture:
    - Blueprint Pattern: Flask blueprint for modular routing
    - Service Layer: Delegates business logic to QueryTemplateService
    - Singleton Pattern: Reuses service instance across requests
    - REST Compliance: Standard HTTP methods and status codes

Version: 2.0.0
Last Updated: 2026-02-24
"""
from flask import Blueprint, request, jsonify
from core.services.query_template_service import QueryTemplateService

query_template_bp = Blueprint('query_templates', __name__)

# Global service instance
_template_service = None


def get_template_service() -> QueryTemplateService:
    """
    Get or create template service instance.
    
    Implements singleton pattern to reuse service instance across requests,
    avoiding repeated initialization overhead.
    
    Returns:
        QueryTemplateService: Singleton service instance
        
    Thread Safety:
        Not thread-safe (acceptable for Flask dev server)
        Use application factory pattern for production
    """
    global _template_service
    if _template_service is None:
        _template_service = QueryTemplateService()
    return _template_service


@query_template_bp.route('', methods=['GET'])
def list_templates():
    """
    GET /api/knowledge-graph/query-templates
    
    List all available query templates with optional category filtering.
    Returns template metadata including parameters, categories, and usage examples.
    
    Query Parameters:
        category (str, optional): Filter templates by category
            Available categories: 'relationships', 'entities', 'analytics', 'traversal'
            Example: ?category=relationships
    
    Response Format:
        {
            "success": true,
            "templates": [
                {
                    "id": "find_entity_relationships",
                    "name": "Find Entity Relationships",
                    "description": "Find all relationships for an entity",
                    "category": "relationships",
                    "parameters": {
                        "entity_id": {"type": "string", "required": true},
                        "max_depth": {"type": "integer", "required": false, "default": 1}
                    },
                    "metadata": {
                        "author": "system",
                        "version": "1.0.0",
                        "tags": ["relationships", "entity"]
                    }
                },
                ...
            ],
            "count": 15,
            "filtered_by": "relationships"
        }
    
    Returns:
        200: Success with templates array
        
    Examples:
        - List all templates:
          GET /api/knowledge-graph/query-templates
          Response: 15 templates across all categories
          
        - Filter by category:
          GET /api/knowledge-graph/query-templates?category=relationships
          Response: 5 templates in 'relationships' category
          
    Use Cases:
        - Template discovery for UI template selector
        - API documentation generation
        - Query builder initialization
        
    Performance:
        - Fast response (< 50ms typical)
        - Templates loaded from in-memory registry
        - No database queries
    """
    # PARSE: Extract request parameters
    category = request.args.get('category')
    
    # CALL SERVICE: Delegate to service layer
    service = get_template_service()
    result = service.list_templates_with_metadata(category=category)
    
    # RETURN: Return service response directly
    return jsonify(result)


@query_template_bp.route('/<template_id>', methods=['GET'])
def get_template(template_id: str):
    """
    GET /api/knowledge-graph/query-templates/<template_id>
    
    Get detailed information about a specific query template.
    Returns full template specification including parameters, examples, and metadata.
    
    Path Parameters:
        template_id (str): Unique template identifier
            Examples: 'find_entity_relationships', 'count_by_type'
    
    Response Format (Success):
        {
            "success": true,
            "template": {
                "id": "find_entity_relationships",
                "name": "Find Entity Relationships",
                "description": "Find all relationships for an entity within specified depth",
                "category": "relationships",
                "query_template": "MATCH (n)-[r*1..{max_depth}]->(m) WHERE n.id = '{entity_id}'...",
                "parameters": {
                    "entity_id": {
                        "type": "string",
                        "required": true,
                        "description": "Entity ID to find relationships for"
                    },
                    "max_depth": {
                        "type": "integer",
                        "required": false,
                        "default": 1,
                        "constraint": "1-10"
                    }
                },
                "examples": [...],
                "metadata": {...}
            }
        }
    
    Response Format (Not Found):
        {
            "success": false,
            "error": "Template not found: unknown_template"
        }
    
    Returns:
        200: Success with template details
        404: Template not found
        
    Examples:
        GET /api/knowledge-graph/query-templates/find_entity_relationships
        
    Use Cases:
        - Template documentation display
        - Parameter form generation
        - Query builder UI
    """
    # CALL SERVICE: Delegate to service layer
    service = get_template_service()
    result, status_code = service.get_template_with_metadata(template_id)
    
    # RETURN: Return service response with status code
    return jsonify(result), status_code


@query_template_bp.route('/search', methods=['GET'])
def search_templates():
    """
    GET /api/knowledge-graph/query-templates/search
    
    Search templates by keyword across name, description, and tags.
    Provides fuzzy matching for template discovery.
    
    Query Parameters:
        q (str, required): Search query string
            Examples: 'relationship', 'entity count', 'analytics'
    
    Response Format (Success):
        {
            "success": true,
            "query": "relationship",
            "results": [
                {
                    "id": "find_entity_relationships",
                    "name": "Find Entity Relationships",
                    "description": "...",
                    "relevance_score": 0.95,
                    "matched_fields": ["name", "description"]
                },
                ...
            ],
            "count": 3
        }
    
    Response Format (Missing Query):
        {
            "error": "Query parameter required"
        }
    
    Returns:
        200: Success with search results
        400: Query parameter missing
        
    Examples:
        - Search by keyword:
          GET /api/knowledge-graph/query-templates/search?q=relationship
          Response: 3 templates related to relationships
          
        - Search by category:
          GET /api/knowledge-graph/query-templates/search?q=analytics
          Response: 5 templates in analytics category
          
    Use Cases:
        - Template discovery
        - Autocomplete suggestions
        - Context-aware template recommendations
    """
    # PARSE: Extract and validate request parameters
    query = request.args.get('q', '')
    
    if not query:
        return jsonify({'error': 'Query parameter required'}), 400
    
    # CALL SERVICE: Delegate to service layer
    service = get_template_service()
    result = service.search_templates_with_metadata(query)
    
    # RETURN: Return service response directly
    return jsonify(result)


@query_template_bp.route('/<template_id>/validate', methods=['POST'])
def validate_parameters(template_id: str):
    """
    POST /api/knowledge-graph/query-templates/<template_id>/validate
    
    Validate parameters against template schema before rendering query.
    Performs type checking, required field validation, and constraint verification.
    
    Path Parameters:
        template_id (str): Unique template identifier
            Examples: 'find_entity_relationships', 'count_by_type'
    
    Request Body:
        {
            "parameters": {
                "entity_id": "PurchaseOrder.123",
                "max_depth": 2,
                "include_types": ["Invoice", "Payment"]
            }
        }
    
    Response Format (Valid):
        {
            "success": true,
            "valid": true,
            "template_id": "find_entity_relationships",
            "provided_parameters": ["entity_id", "max_depth", "include_types"],
            "validation_details": {
                "entity_id": {"valid": true, "type": "string", "value": "PurchaseOrder.123"},
                "max_depth": {"valid": true, "type": "integer", "value": 2, "constraint": "1-10"},
                "include_types": {"valid": true, "type": "array", "length": 2}
            }
        }
    
    Response Format (Invalid):
        {
            "success": true,
            "valid": false,
            "template_id": "find_entity_relationships",
            "errors": [
                {
                    "parameter": "entity_id",
                    "error": "Required parameter missing",
                    "expected_type": "string"
                },
                {
                    "parameter": "max_depth",
                    "error": "Must be between 1 and 10",
                    "provided_value": 15
                }
            ],
            "missing_required": ["entity_id"],
            "invalid_values": ["max_depth"]
        }
    
    Returns:
        200: Validation completed (success=true, check 'valid' field)
        404: Template not found
        
    Examples:
        - Valid parameters:
          POST /api/knowledge-graph/query-templates/find_entity_relationships/validate
          Body: {"parameters": {"entity_id": "PurchaseOrder.123"}}
          Response: {"success": true, "valid": true, ...}
          
        - Invalid parameters:
          POST /api/knowledge-graph/query-templates/find_entity_relationships/validate
          Body: {"parameters": {"max_depth": "invalid"}}
          Response: {"success": true, "valid": false, "errors": [...]}
        
    Use Cases:
        - Pre-flight validation before expensive query rendering
        - Client-side form validation (progressive enhancement)
        - API contract testing (validate before render)
        - Parameter debugging (understand why render fails)
        
    Performance:
        - Fast validation (< 10ms typical)
        - No database queries performed
        - Pure schema validation
    """
    # PARSE: Extract request body
    data = request.get_json() or {}
    params = data.get('parameters', {})
    
    # CALL SERVICE: Delegate to service layer
    service = get_template_service()
    result = service.validate_parameters_with_metadata(template_id, params)
    
    # RETURN: Return service response directly
    return jsonify(result)


@query_template_bp.route('/<template_id>/render', methods=['POST'])
def render_query(template_id: str):
    """
    POST /api/knowledge-graph/query-templates/<template_id>/render
    
    Render a parameterized query from template with provided parameters.
    Validates parameters, substitutes values, and returns executable query.
    
    Path Parameters:
        template_id (str): Unique template identifier
            Examples: 'find_entity_relationships', 'count_by_type'
    
    Request Body:
        {
            "parameters": {
                "entity_id": "PurchaseOrder.123",
                "max_depth": 2,
                "relationship_types": ["CONTAINS", "REFERENCES"]
            }
        }
    
    Response Format (Success):
        {
            "success": true,
            "template_id": "find_entity_relationships",
            "rendered_query": "MATCH (n)-[r:CONTAINS|REFERENCES*1..2]->(m) WHERE n.id = 'PurchaseOrder.123' RETURN n, r, m",
            "parameters_used": {
                "entity_id": "PurchaseOrder.123",
                "max_depth": 2,
                "relationship_types": ["CONTAINS", "REFERENCES"]
            },
            "metadata": {
                "template_version": "1.0.0",
                "rendered_at": "2026-02-24T12:40:00Z",
                "estimated_complexity": "medium"
            }
        }
    
    Response Format (Validation Error):
        {
            "success": false,
            "error": "Parameter validation failed",
            "validation_errors": [
                {
                    "parameter": "entity_id",
                    "error": "Required parameter missing"
                }
            ]
        }
    
    Response Format (Template Not Found):
        {
            "success": false,
            "error": "Template not found: unknown_template"
        }
    
    Returns:
        200: Success with rendered query
        400: Parameter validation failed
        404: Template not found
        
    Examples:
        - Basic rendering:
          POST /api/knowledge-graph/query-templates/find_entity_relationships/render
          Body: {"parameters": {"entity_id": "PurchaseOrder.123"}}
          
        - With optional parameters:
          POST /api/knowledge-graph/query-templates/find_entity_relationships/render
          Body: {
              "parameters": {
                  "entity_id": "PurchaseOrder.123",
                  "max_depth": 3,
                  "relationship_types": ["CONTAINS"]
              }
          }
    
    Use Cases:
        - Generate queries for graph visualization
        - Build dynamic analytics queries
        - Query builder UI backend
        - API-driven graph exploration
        
    Performance:
        - Fast rendering (< 20ms typical)
        - No database queries during render
        - Ready-to-execute query output
        
    Security:
        - Parameter sanitization applied
        - SQL injection prevention
        - Query complexity limits enforced
    """
    # PARSE: Extract request body
    data = request.get_json() or {}
    params = data.get('parameters', {})
    
    # CALL SERVICE: Delegate to service layer
    service = get_template_service()
    result, status_code = service.render_query_with_metadata(template_id, params)
    
    # RETURN: Return service response with status code
    return jsonify(result), status_code