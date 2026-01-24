"""
Feature Manager REST API - Flask Blueprint

Provides REST endpoints for feature flag management:
- GET /api/features - List all features
- POST /api/features/<name>/enable - Enable a feature
- POST /api/features/<name>/disable - Disable a feature
- POST /api/features/<name>/toggle - Toggle a feature
- GET /api/features/export - Export configuration
- POST /api/features/import - Import configuration
- POST /api/features/reset - Reset to defaults

Part of: Feature Manager Module
Version: 1.0
"""

from flask import Blueprint, jsonify, request
from feature_flags import get_feature_flags


# Create Flask Blueprint
api = Blueprint('feature_manager_api', __name__, url_prefix='/api/features')

# Get feature flags instance
feature_flags = get_feature_flags()


@api.route('/', methods=['GET'])
def get_all_features():
    """
    Get all features with their status.
    
    Returns:
        JSON response with all features
    """
    try:
        features = feature_flags.get_all()
        
        return jsonify({
            'success': True,
            'count': len(features),
            'features': features
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@api.route('/<feature_name>', methods=['GET'])
def get_feature(feature_name):
    """
    Get a specific feature.
    
    Args:
        feature_name: Name of the feature
    
    Returns:
        JSON response with feature details
    """
    try:
        feature = feature_flags.get(feature_name)
        
        if feature:
            return jsonify({
                'success': True,
                'feature': feature
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': f'Feature not found: {feature_name}'
            }), 404
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@api.route('/<feature_name>/enable', methods=['POST'])
def enable_feature(feature_name):
    """
    Enable a feature.
    
    Args:
        feature_name: Name of the feature
    
    Returns:
        JSON response with success status
    """
    try:
        success = feature_flags.enable(feature_name)
        
        if success:
            return jsonify({
                'success': True,
                'message': f'Feature enabled: {feature_name}',
                'feature': feature_flags.get(feature_name)
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': f'Feature not found: {feature_name}'
            }), 404
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@api.route('/<feature_name>/disable', methods=['POST'])
def disable_feature(feature_name):
    """
    Disable a feature.
    
    Args:
        feature_name: Name of the feature
    
    Returns:
        JSON response with success status
    """
    try:
        success = feature_flags.disable(feature_name)
        
        if success:
            return jsonify({
                'success': True,
                'message': f'Feature disabled: {feature_name}',
                'feature': feature_flags.get(feature_name)
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': f'Feature not found: {feature_name}'
            }), 404
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@api.route('/<feature_name>/toggle', methods=['POST'])
def toggle_feature(feature_name):
    """
    Toggle a feature on/off.
    
    Args:
        feature_name: Name of the feature
    
    Returns:
        JSON response with new state
    """
    try:
        new_state = feature_flags.toggle(feature_name)
        
        if new_state is not None:
            return jsonify({
                'success': True,
                'message': f'Feature toggled: {feature_name}',
                'enabled': new_state,
                'feature': feature_flags.get(feature_name)
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': f'Feature not found: {feature_name}'
            }), 404
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@api.route('/export', methods=['GET'])
def export_config():
    """
    Export feature configuration as JSON.
    
    Returns:
        JSON response with exported configuration
    """
    try:
        config = feature_flags.export_config()
        
        return jsonify({
            'success': True,
            'config': config
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@api.route('/import', methods=['POST'])
def import_config():
    """
    Import feature configuration from JSON.
    
    Expected payload:
        {
            "config": "{...json string...}"
        }
    
    Returns:
        JSON response with success status
    """
    try:
        data = request.get_json()
        
        if not data or 'config' not in data:
            return jsonify({
                'success': False,
                'error': 'Missing config in request body'
            }), 400
        
        config_json = data['config']
        success = feature_flags.import_config(config_json)
        
        if success:
            return jsonify({
                'success': True,
                'message': 'Configuration imported successfully',
                'count': feature_flags.get_feature_count()
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': 'Failed to import configuration'
            }), 400
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@api.route('/reset', methods=['POST'])
def reset_to_defaults():
    """
    Reset all features to default configuration.
    
    Returns:
        JSON response with success status
    """
    try:
        success = feature_flags.reset_to_defaults()
        
        if success:
            return jsonify({
                'success': True,
                'message': 'Features reset to defaults',
                'count': feature_flags.get_feature_count()
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': 'Failed to reset features'
            }), 500
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@api.route('/categories', methods=['GET'])
def get_categories():
    """
    Get all unique categories.
    
    Returns:
        JSON response with categories
    """
    try:
        features = feature_flags.get_all()
        categories = list(set(f.get('category', 'Uncategorized') for f in features.values()))
        
        return jsonify({
            'success': True,
            'categories': sorted(categories)
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@api.route('/category/<category_name>', methods=['GET'])
def get_features_by_category(category_name):
    """
    Get features in a specific category.
    
    Args:
        category_name: Category name
    
    Returns:
        JSON response with features in category
    """
    try:
        features = feature_flags.get_features_by_category(category_name)
        
        return jsonify({
            'success': True,
            'category': category_name,
            'count': len(features),
            'features': features
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500