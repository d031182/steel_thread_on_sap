"""
Frontend Module Registry API
=============================

REST API endpoints for frontend module discovery.

Exposes module metadata for frontend auto-discovery, enabling:
- Dynamic navigation generation
- On-demand module loading
- Feature flag awareness
- Dependency management

Endpoints:
- GET /api/modules/frontend-registry - List all enabled frontend modules
- GET /api/modules/frontend-registry/<module_id> - Get specific module
- GET /api/modules/frontend-registry/stats - Get registry statistics
- POST /api/modules/frontend-registry/refresh - Force cache refresh

@author P2P Development Team
@version 1.0.0
"""

import logging
from flask import Blueprint, jsonify, request
from core.services.frontend_module_registry import FrontendModuleRegistry

logger = logging.getLogger(__name__)

# Create blueprint
frontend_registry_bp = Blueprint('frontend_registry', __name__)

# Initialize registry service (singleton)
_registry = None


def get_registry() -> FrontendModuleRegistry:
    """Get or create registry singleton"""
    global _registry
    if _registry is None:
        _registry = FrontendModuleRegistry()
    return _registry


@frontend_registry_bp.route('/api/modules/frontend-registry', methods=['GET'])
def list_modules():
    """
    Get list of all enabled frontend modules
    
    Query Parameters:
        category: Filter by category (optional)
        force_refresh: Force cache refresh (optional, default: false)
        base_path: Base path to prepend to scripts (optional, e.g. "/v2" for App V2)
    
    Returns:
        JSON array of module metadata objects
    
    Example Response:
        [
            {
                "id": "knowledge_graph_v2",
                "name": "Knowledge Graph V2",
                "description": "Interactive data relationship visualization",
                "version": "2.0.0",
                "icon": "sap-icon://chain-link",
                "order": 10,
                "category": "analytics",
                "frontend": {
                    "entry_point": "modules/knowledge_graph_v2/main.js",
                    "styles": "modules/knowledge_graph_v2/styles.css",
                    "route": "/knowledge-graph-v2",
                    "requires_auth": false,
                    "dependencies": ["ILogger", "IDataSource"]
                },
                "backend": {
                    "base_url": "/api/knowledge-graph-v2",
                    "available": true
                },
                "features": {}
            }
        ]
    """
    try:
        registry = get_registry()
        
        # Check for force refresh
        force_refresh = request.args.get('force_refresh', 'false').lower() == 'true'
        
        # Get base path for script prefixing (for App V2)
        base_path = request.args.get('base_path', '')
        
        # Get modules
        modules = registry.get_frontend_modules(force_refresh=force_refresh)
        
        # Prepend base_path to scripts if specified
        if base_path:
            for module in modules:
                if module.get('frontend', {}).get('scripts'):
                    module['frontend']['scripts'] = [
                        f"{base_path}/{script}" if not script.startswith('/') else script
                        for script in module['frontend']['scripts']
                    ]
        
        # Filter by category if specified
        category = request.args.get('category')
        if category:
            modules = [m for m in modules if m.get('category') == category]
        
        return jsonify({
            'success': True,
            'count': len(modules),
            'modules': modules
        })
        
    except Exception as e:
        logger.error(f"Error listing modules: {e}", exc_info=True)
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@frontend_registry_bp.route('/api/modules/frontend-registry/<module_id>', methods=['GET'])
def get_module(module_id: str):
    """
    Get metadata for a specific module
    
    Path Parameters:
        module_id: Module identifier (directory name)
    
    Returns:
        JSON object with module metadata
    
    Status Codes:
        200: Module found
        404: Module not found
        500: Server error
    """
    try:
        registry = get_registry()
        module = registry.get_module_by_id(module_id)
        
        if module:
            return jsonify({
                'success': True,
                'module': module
            })
        else:
            return jsonify({
                'success': False,
                'error': f"Module '{module_id}' not found"
            }), 404
            
    except Exception as e:
        logger.error(f"Error getting module {module_id}: {e}", exc_info=True)
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@frontend_registry_bp.route('/api/modules/frontend-registry/stats', methods=['GET'])
def get_stats():
    """
    Get registry statistics
    
    Returns:
        JSON object with statistics about the module registry
    
    Example Response:
        {
            "success": true,
            "stats": {
                "total_modules": 5,
                "categories": {
                    "analytics": 2,
                    "utilities": 2,
                    "admin": 1
                },
                "with_backend": 4,
                "without_backend": 1
            }
        }
    """
    try:
        registry = get_registry()
        stats = registry.get_registry_stats()
        
        return jsonify({
            'success': True,
            'stats': stats
        })
        
    except Exception as e:
        logger.error(f"Error getting stats: {e}", exc_info=True)
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@frontend_registry_bp.route('/api/modules/frontend-registry/refresh', methods=['POST'])
def refresh_cache():
    """
    Force refresh of module cache
    
    This endpoint triggers a re-scan of all module.json files
    and rebuilds the registry cache.
    
    Returns:
        JSON object with refresh results
    
    Example Response:
        {
            "success": true,
            "message": "Registry cache refreshed",
            "modules_loaded": 5
        }
    """
    try:
        registry = get_registry()
        count = registry.refresh_cache()
        
        return jsonify({
            'success': True,
            'message': 'Registry cache refreshed',
            'modules_loaded': count
        })
        
    except Exception as e:
        logger.error(f"Error refreshing cache: {e}", exc_info=True)
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@frontend_registry_bp.route('/api/modules/frontend-registry/health', methods=['GET'])
def health_check():
    """
    Health check endpoint
    
    Returns:
        JSON object with service health status
    """
    try:
        registry = get_registry()
        modules = registry.get_frontend_modules()
        
        return jsonify({
            'success': True,
            'status': 'healthy',
            'modules_available': len(modules)
        })
        
    except Exception as e:
        logger.error(f"Health check failed: {e}", exc_info=True)
        return jsonify({
            'success': False,
            'status': 'unhealthy',
            'error': str(e)
        }), 500