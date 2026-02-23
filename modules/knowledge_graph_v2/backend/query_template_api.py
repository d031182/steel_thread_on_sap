from flask import Blueprint, request, jsonify
from core.services.query_template_service import QueryTemplateService

query_template_bp = Blueprint('query_templates', __name__)

# Global service instance
_template_service = None


def get_template_service() -> QueryTemplateService:
    """
    Get or create template service instance.
    
    Returns:
        QueryTemplateService: Singleton service instance
    """
    global _template_service
    if _template_service is None:
        _template_service = QueryTemplateService()
    return _template_service


@query_template_bp.route('', methods=['GET'])
def list_templates():
    """
    List all available query templates.
    
    Query Parameters:
        category (str, optional): Filter templates by category
    
    Returns:
        JSON response with templates array
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
    Get template details by ID.
    
    Args:
        template_id (str): Template identifier
    
    Returns:
        JSON response with template details or 404 error
    """
    # CALL SERVICE: Delegate to service layer
    service = get_template_service()
    result, status_code = service.get_template_with_metadata(template_id)
    
    # RETURN: Return service response with status code
    return jsonify(result), status_code


@query_template_bp.route('/search', methods=['GET'])
def search_templates():
    """
    Search templates by query string.
    
    Query Parameters:
        q (str, required): Search query
    
    Returns:
        JSON response with search results or 400 error
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
    Validate template parameters.
    
    Args:
        template_id (str): Template identifier
    
    Request Body:
        parameters (dict): Parameters to validate
    
    Returns:
        JSON response with validation result
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
    Render query from template with parameters.
    
    Args:
        template_id (str): Template identifier
    
    Request Body:
        parameters (dict): Parameters for rendering
    
    Returns:
        JSON response with rendered query or error (400/404)
    """
    # PARSE: Extract request body
    data = request.get_json() or {}
    params = data.get('parameters', {})
    
    # CALL SERVICE: Delegate to service layer
    service = get_template_service()
    result, status_code = service.render_query_with_metadata(template_id, params)
    
    # RETURN: Return service response with status code
    return jsonify(result), status_code
