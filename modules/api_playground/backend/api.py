"""
API Playground Blueprint
========================
Flask blueprint for API Playground discovery endpoints.
Provides REST API for auto-discovering module APIs.

Author: P2P Development Team
Version: 1.0.0
"""

from flask import Blueprint, jsonify
import logging

from .playground_service import get_playground_service

# Create blueprint
api_playground_api = Blueprint(
    'api_playground',
    __name__,
    url_prefix='/api/playground'
)

logger = logging.getLogger(__name__)

@api_playground_api.route('/discover', methods=['GET'])
def discover_apis():
    """
    Discover all module APIs
    
    Returns:
        JSON with discovered APIs and statistics
        {
            "success": true,
            "apis": {
                "module_name": {
                    "displayName": "...",
                    "category": "...",
                    "baseUrl": "...",
                    "endpoints": [...]
                }
            },
            "stats": {
                "total_modules": 5,
                "total_endpoints": 25,
                "categories": ["Infrastructure", "Business Logic"]
            }
        }
    """
    try:
        # Get playground service instance
        playground = get_playground_service()
        
        # Re-discover APIs (in case modules changed)
        playground.discover_apis()
        
        # Get all APIs and stats
        apis = playground.get_all_apis()
        stats = playground.get_summary_stats()
        
        logger.info(f"API discovery successful: {stats['total_modules']} modules, {stats['total_endpoints']} endpoints")
        
        return jsonify({
            'success': True,
            'apis': apis,
            'stats': stats
        })
        
    except Exception as e:
        logger.error(f"Error discovering APIs: {str(e)}")
        return jsonify({
            'success': False,
            'error': {
                'message': str(e),
                'code': 'DISCOVERY_ERROR'
            }
        }), 500


@api_playground_api.route('/modules/<module_name>', methods=['GET'])
def get_module_api(module_name: str):
    """
    Get API configuration for a specific module
    
    Args:
        module_name: Name of the module
    
    Returns:
        JSON with module API configuration
    """
    try:
        playground = get_playground_service()
        api_config = playground.get_api(module_name)
        
        if api_config is None:
            return jsonify({
                'success': False,
                'error': {
                    'message': f'Module "{module_name}" not found or has no API',
                    'code': 'MODULE_NOT_FOUND'
                }
            }), 404
        
        return jsonify({
            'success': True,
            'module': module_name,
            'api': api_config
        })
        
    except Exception as e:
        logger.error(f"Error getting module API: {str(e)}")
        return jsonify({
            'success': False,
            'error': {
                'message': str(e),
                'code': 'SERVER_ERROR'
            }
        }), 500


@api_playground_api.route('/categories', methods=['GET'])
def get_categories():
    """
    Get all API categories
    
    Returns:
        JSON with list of categories
    """
    try:
        playground = get_playground_service()
        categories = playground.get_categories()
        
        return jsonify({
            'success': True,
            'categories': categories
        })
        
    except Exception as e:
        logger.error(f"Error getting categories: {str(e)}")
        return jsonify({
            'success': False,
            'error': {
                'message': str(e),
                'code': 'SERVER_ERROR'
            }
        }), 500


@api_playground_api.route('/categories/<category>', methods=['GET'])
def get_apis_by_category(category: str):
    """
    Get all APIs in a specific category
    
    Args:
        category: Category name
    
    Returns:
        JSON with APIs in the category
    """
    try:
        playground = get_playground_service()
        apis = playground.get_apis_by_category(category)
        
        return jsonify({
            'success': True,
            'category': category,
            'count': len(apis),
            'apis': apis
        })
        
    except Exception as e:
        logger.error(f"Error getting APIs by category: {str(e)}")
        return jsonify({
            'success': False,
            'error': {
                'message': str(e),
                'code': 'SERVER_ERROR'
            }
        }), 500


@api_playground_api.route('/stats', methods=['GET'])
def get_stats():
    """
    Get API discovery statistics
    
    Returns:
        JSON with statistics
    """
    try:
        playground = get_playground_service()
        stats = playground.get_summary_stats()
        
        return jsonify({
            'success': True,
            'stats': stats
        })
        
    except Exception as e:
        logger.error(f"Error getting stats: {str(e)}")
        return jsonify({
            'success': False,
            'error': {
                'message': str(e),
                'code': 'SERVER_ERROR'
            }
        }), 500