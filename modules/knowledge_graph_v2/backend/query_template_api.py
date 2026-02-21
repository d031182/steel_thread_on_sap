from flask import Blueprint, request, jsonify
from core.services.query_template_service import QueryTemplateService

query_template_bp = Blueprint('query_templates', __name__)

# Global service instance
_template_service = None


def get_template_service() -> QueryTemplateService:
    """Get or create template service"""
    global _template_service
    if _template_service is None:
        _template_service = QueryTemplateService()
    return _template_service


@query_template_bp.route('', methods=['GET'])
def list_templates():
    """List all available query templates"""
    service = get_template_service()
    category = request.args.get('category')
    
    templates = service.list_templates(category=category)
    
    return jsonify({
        'templates': [
            {
                'id': t.id,
                'name': t.name,
                'description': t.description,
                'category': t.category.value,
                'tags': t.tags
            }
            for t in templates
        ]
    })


@query_template_bp.route('/<template_id>', methods=['GET'])
def get_template(template_id: str):
    """Get template details"""
    service = get_template_service()
    template = service.get_template(template_id)
    
    if not template:
        return jsonify({'error': f'Template {template_id} not found'}), 404
    
    return jsonify({
        'id': template.id,
        'name': template.name,
        'description': template.description,
        'category': template.category.value,
        'sql_template': template.sql_template,
        'parameters': [
            {
                'name': p.name,
                'type': p.type,
                'required': p.required,
                'description': p.description,
                'validation_rule': p.validation_rule,
                'default_value': p.default_value
            }
            for p in template.parameters
        ],
        'result_schema': template.result_schema,
        'examples': template.examples,
        'tags': template.tags
    })


@query_template_bp.route('/search', methods=['GET'])
def search_templates():
    """Search templates"""
    service = get_template_service()
    query = request.args.get('q', '')
    
    if not query:
        return jsonify({'error': 'Query parameter required'}), 400
    
    templates = service.search_templates(query)
    
    return jsonify({
        'query': query,
        'results': [
            {
                'id': t.id,
                'name': t.name,
                'description': t.description,
                'category': t.category.value,
                'tags': t.tags
            }
            for t in templates
        ]
    })


@query_template_bp.route('/<template_id>/validate', methods=['POST'])
def validate_parameters(template_id: str):
    """Validate template parameters"""
    service = get_template_service()
    data = request.get_json() or {}
    params = data.get('parameters', {})
    
    is_valid, errors = service.validate_parameters(template_id, params)
    
    return jsonify({
        'template_id': template_id,
        'valid': is_valid,
        'errors': errors
    })


@query_template_bp.route('/<template_id>/render', methods=['POST'])
def render_query(template_id: str):
    """Render query from template with parameters"""
    service = get_template_service()
    data = request.get_json() or {}
    params = data.get('parameters', {})
    
    try:
        query = service.render_query(template_id, params)
        
        if query is None:
            return jsonify({'error': f'Template {template_id} not found'}), 404
        
        return jsonify({
            'template_id': template_id,
            'query': query,
            'parameters': params
        })
    except ValueError as e:
        return jsonify({'error': str(e)}), 400