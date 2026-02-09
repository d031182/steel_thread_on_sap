"""
Data Products V2 API Blueprint

REST API for data products with source switching capability.
Uses Facade pattern for business logic.

Author: P2P Development Team
Version: 2.0.0
Date: 2026-02-08
"""

from flask import Blueprint, request, jsonify, current_app
import logging

# Create blueprint
data_products_v2_api = Blueprint('data_products_v2', __name__)
logger = logging.getLogger(__name__)


def get_facade(source: str):
    """
    Get facade from Flask app context (Dependency Injection)
    
    Uses pre-configured facades injected by app.py instead of
    Service Locator antipattern (reaching into current_app.config).
    
    Args:
        source: 'hana' or 'sqlite'
    
    Returns:
        Pre-configured facade instance
    
    Raises:
        ValueError: If source invalid or facade not configured
    """
    if source == 'sqlite':
        if not hasattr(current_app, 'sqlite_facade_v2'):
            raise ValueError("SQLite facade not configured")
        return current_app.sqlite_facade_v2
    
    elif source == 'hana':
        if not hasattr(current_app, 'hana_facade_v2'):
            raise ValueError("HANA facade not configured")
        return current_app.hana_facade_v2
    
    else:
        raise ValueError(f"Unknown source: {source}")


@data_products_v2_api.route('/', methods=['GET'])
def list_data_products():
    """
    List data products from specified source
    
    Query Parameters:
        source: 'hana' or 'sqlite' (default: 'sqlite')
    
    Returns:
        JSON with list of data products
    """
    try:
        source = request.args.get('source', 'sqlite').lower()
        
        if source not in ['hana', 'sqlite']:
            return jsonify({
                'success': False,
                'error': 'Invalid source. Use "hana" or "sqlite"'
            }), 400
        
        # Get facade and fetch data
        facade = get_facade(source)
        products = facade.get_data_products()
        
        # Convert domain models to dict
        products_dict = [
            {
                'product_name': p.product_name,
                'display_name': p.display_name,
                'namespace': p.namespace,
                'version': p.version,
                'schema_name': p.schema_name,
                'source': p.source,
                'description': p.description,
                'table_count': p.table_count
            }
            for p in products
        ]
        
        return jsonify({
            'success': True,
            'count': len(products_dict),
            'data_products': products_dict,
            'source': source
        })
        
    except ValueError as e:
        logger.error(f"Facade error: {str(e)}")
        # HTTP 503 Service Unavailable (industry standard for service not configured)
        return jsonify({
            'success': False,
            'error': {
                'message': f'HANA Cloud connection not available: {str(e)}',
                'code': 'NOT_CONFIGURED',
                'userMessage': 'HANA Cloud is not configured. Please contact your administrator or use SQLite as data source.'
            }
        }), 503
    except Exception as e:
        logger.error(f"Error listing data products: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@data_products_v2_api.route('/<product_name>/tables', methods=['GET'])
def get_tables(product_name):
    """Get tables in a data product"""
    try:
        source = request.args.get('source', 'sqlite').lower()
        facade = get_facade(source)
        tables = facade.get_tables(product_name)
        
        tables_dict = [
            {
                'table_name': t.table_name,
                'table_type': t.table_type,
                'record_count': t.record_count,
                'schema_name': t.schema_name
            }
            for t in tables
        ]
        
        return jsonify({
            'success': True,
            'count': len(tables_dict),
            'tables': tables_dict,
            'source': source
        })
        
    except ValueError as e:
        logger.error(f"Facade error: {str(e)}")
        return jsonify({
            'success': False,
            'error': {
                'message': f'HANA Cloud connection not available: {str(e)}',
                'code': 'NOT_CONFIGURED',
                'userMessage': 'HANA Cloud is not configured. Please use SQLite as data source.'
            }
        }), 503
    except Exception as e:
        logger.error(f"Error getting tables: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@data_products_v2_api.route('/<product_name>/<table_name>/structure', methods=['GET'])
def get_table_structure(product_name, table_name):
    """Get table structure (columns)"""
    try:
        source = request.args.get('source', 'sqlite').lower()
        facade = get_facade(source)
        columns = facade.get_table_structure(product_name, table_name)
        
        columns_dict = [
            {
                'column_name': c.column_name,
                'data_type': c.data_type,
                'length': c.length,
                'is_nullable': c.is_nullable,
                'is_primary_key': c.is_primary_key,
                'foreign_key': c.foreign_key
            }
            for c in columns
        ]
        
        return jsonify({
            'success': True,
            'columns': columns_dict,
            'source': source
        })
        
    except ValueError as e:
        logger.error(f"Facade error: {str(e)}")
        return jsonify({
            'success': False,
            'error': {
                'message': f'HANA Cloud connection not available: {str(e)}',
                'code': 'NOT_CONFIGURED',
                'userMessage': 'HANA Cloud is not configured. Please use SQLite as data source.'
            }
        }), 503
    except Exception as e:
        logger.error(f"Error getting structure: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@data_products_v2_api.route('/<product_name>/<table_name>/query', methods=['POST'])
def query_table(product_name, table_name):
    """Query table data"""
    try:
        source = request.args.get('source', 'sqlite').lower()
        data = request.get_json() or {}
        
        facade = get_facade(source)
        result = facade.query_table(
            product_name,
            table_name,
            limit=min(int(data.get('limit', 100)), 1000),
            offset=max(int(data.get('offset', 0)), 0)
        )
        
        result['success'] = True
        result['source'] = source
        return jsonify(result)
        
    except ValueError as e:
        logger.error(f"Facade error: {str(e)}")
        return jsonify({
            'success': False,
            'error': {
                'message': f'HANA Cloud connection not available: {str(e)}',
                'code': 'NOT_CONFIGURED',
                'userMessage': 'HANA Cloud is not configured. Please use SQLite as data source.'
            }
        }), 503
    except Exception as e:
        logger.error(f"Error querying table: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500
