"""
Data Products API Blueprint
============================
Flask blueprint for Data Products REST API endpoints.

Provides endpoints for:
- Listing data products from HANA/SQLite
- Getting schema tables
- Getting table structure
- Querying table data
- Executing SQL queries
- Managing connections

Author: P2P Development Team
Version: 2.0.0 - Modular Blueprint Architecture
Date: 2026-01-25
"""

from flask import Blueprint, request, jsonify, current_app
import logging
import traceback
from datetime import datetime

# Create blueprint
data_products_api = Blueprint('data_products', __name__, url_prefix='/api')

# Logger
logger = logging.getLogger(__name__)


def get_data_source(source_name: str):
    """
    Get data source from Flask app context
    
    Args:
        source_name: 'hana' or 'sqlite'
    
    Returns:
        DataSource instance
    
    Raises:
        ValueError: If source is invalid or not configured
    """
    if source_name == 'sqlite':
        return current_app.sqlite_data_source
    elif source_name == 'hana':
        if not current_app.hana_data_source:
            raise ValueError("HANA data source not configured")
        return current_app.hana_data_source
    else:
        raise ValueError(f"Invalid data source: {source_name}")


@data_products_api.route('/data-products', methods=['GET'])
def list_data_products():
    """
    List all data products from specified source
    
    Query Parameters:
        source: 'hana' or 'sqlite' (default: 'hana')
    
    Returns:
        JSON with list of data products
    """
    try:
        source = request.args.get('source', 'hana').lower()
        
        if source not in ['hana', 'sqlite']:
            return jsonify({
                'success': False,
                'error': {'message': 'Invalid source. Use "hana" or "sqlite"', 'code': 'INVALID_SOURCE'}
            }), 400
        
        logger.info(f"[{source.upper()}] Loading data products")
        
        data_source = get_data_source(source)
        data_products = data_source.get_data_products()
        
        logger.info(f"[{source.upper()}] Found {len(data_products)} data products")
        
        return jsonify({
            'success': True,
            'count': len(data_products),
            'data_products': data_products,
            'source': source
        })
        
    except ValueError as e:
        logger.error(f"Data source error: {str(e)}")
        return jsonify({
            'success': False,
            'error': {'message': str(e), 'code': 'NOT_CONFIGURED'}
        }), 500
    except Exception as e:
        logger.error(f"Error in list_data_products: {str(e)}\n{traceback.format_exc()}")
        error_message = str(e) if current_app.config.get('ENV') == 'development' else 'Internal server error'
        return jsonify({
            'success': False,
            'error': {'message': error_message, 'code': 'SERVER_ERROR'}
        }), 500


@data_products_api.route('/data-products/<schema_name>/tables', methods=['GET'])
def get_schema_tables(schema_name):
    """
    Get tables in a data product schema
    
    Query Parameters:
        source: 'hana' or 'sqlite' (default: 'hana')
    """
    try:
        source = request.args.get('source', 'hana').lower()
        logger.info(f"[{source.upper()}] Getting tables for schema: {schema_name}")
        
        data_source = get_data_source(source)
        tables = data_source.get_tables(schema_name)
        
        logger.info(f"[{source.upper()}] Found {len(tables)} tables")
        
        return jsonify({
            'success': True,
            'count': len(tables),
            'schemaName': schema_name,
            'tables': tables,
            'source': source
        })
        
    except ValueError as e:
        logger.error(f"Data source error: {str(e)}")
        return jsonify({
            'success': False,
            'error': {'message': str(e), 'code': 'NOT_CONFIGURED'}
        }), 500
    except Exception as e:
        logger.error(f"Error in get_schema_tables: {str(e)}\n{traceback.format_exc()}")
        error_message = str(e) if current_app.config.get('ENV') == 'development' else 'Internal server error'
        return jsonify({
            'success': False,
            'error': {'message': error_message, 'code': 'SERVER_ERROR'}
        }), 500


@data_products_api.route('/data-products/<schema_name>/<table_name>/structure', methods=['GET'])
def get_table_structure(schema_name, table_name):
    """
    Get table structure (columns, types, constraints)
    
    Query Parameters:
        source: 'hana' or 'sqlite' (default: 'hana')
    """
    try:
        source = request.args.get('source', 'hana').lower()
        logger.info(f"[{source.upper()}] Getting structure for table: {table_name}")
        
        data_source = get_data_source(source)
        columns = data_source.get_table_structure(schema_name, table_name)
        
        logger.info(f"[{source.upper()}] Found {len(columns)} columns")
        
        return jsonify({
            'success': True,
            'schemaName': schema_name,
            'tableName': table_name,
            'columnCount': len(columns),
            'columns': columns,
            'source': source
        })
        
    except ValueError as e:
        logger.error(f"Data source error: {str(e)}")
        return jsonify({
            'success': False,
            'error': {'message': str(e), 'code': 'NOT_CONFIGURED'}
        }), 500
    except Exception as e:
        logger.error(f"Error in get_table_structure: {str(e)}\n{traceback.format_exc()}")
        error_message = str(e) if current_app.config.get('ENV') == 'development' else 'Internal server error'
        return jsonify({
            'success': False,
            'error': {'message': error_message, 'code': 'SERVER_ERROR'}
        }), 500


@data_products_api.route('/data-products/<schema_name>/<table_name>/query', methods=['POST'])
def query_table(schema_name, table_name):
    """
    Query data from a table
    
    Query Parameters:
        source: 'hana' or 'sqlite' (default: 'hana')
    """
    try:
        source = request.args.get('source', 'hana').lower()
        data = request.get_json() or {}
        limit = min(int(data.get('limit', 100)), 1000)
        offset = max(int(data.get('offset', 0)), 0)
        
        logger.info(f"[{source.upper()}] Querying table: {table_name} (limit={limit}, offset={offset})")
        
        data_source = get_data_source(source)
        result = data_source.query_table(schema_name, table_name, limit, offset)
        
        logger.info(f"[{source.upper()}] Retrieved {len(result['rows'])} rows")
        
        return jsonify({
            'success': True,
            'schemaName': schema_name,
            'tableName': table_name,
            'rows': result['rows'],
            'rowCount': len(result['rows']),
            'totalCount': result['totalCount'],
            'limit': limit,
            'offset': offset,
            'columns': result['columns'],
            'executionTime': result['executionTime'],
            'source': source
        })
        
    except ValueError as e:
        logger.error(f"Data source error: {str(e)}")
        return jsonify({
            'success': False,
            'error': {'message': str(e), 'code': 'NOT_CONFIGURED'}
        }), 500
    except Exception as e:
        logger.error(f"Error in query_table: {str(e)}\n{traceback.format_exc()}")
        error_message = str(e) if current_app.config.get('ENV') == 'development' else 'Internal server error'
        return jsonify({
            'success': False,
            'error': {'message': error_message, 'code': 'SERVER_ERROR'}
        }), 500


@data_products_api.route('/execute-sql', methods=['POST'])
def execute_sql():
    """Execute arbitrary SQL query on HANA"""
    try:
        if not current_app.hana_data_source:
            return jsonify({
                'success': False,
                'error': {'message': 'HANA not configured', 'code': 'NOT_CONFIGURED'}
            }), 500
        
        data = request.get_json()
        sql = data.get('sql', '').strip()
        
        if not sql:
            return jsonify({
                'success': False,
                'error': {'message': 'SQL query is required', 'code': 'MISSING_SQL'}
            }), 400
        
        if len(sql) > 50000:
            return jsonify({
                'success': False,
                'error': {'message': 'SQL query too long (max 50000 characters)', 'code': 'QUERY_TOO_LONG'}
            }), 400
        
        logger.info(f"Executing SQL: {sql[:100]}..." if len(sql) > 100 else f"Executing SQL: {sql}")
        
        # Direct execution via HANAConnection for arbitrary SQL
        result = current_app.hana_data_source.connection.execute_query(sql)
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Error in execute_sql: {str(e)}\n{traceback.format_exc()}")
        error_message = str(e) if current_app.config.get('ENV') == 'development' else 'Internal server error'
        return jsonify({
            'success': False,
            'error': {'message': error_message, 'code': 'SERVER_ERROR'}
        }), 500


@data_products_api.route('/connections', methods=['GET'])
def list_connections():
    """List available connections"""
    connections = []
    
    if current_app.hana_data_source:
        # Get HANA config from app config or environment
        connections.append({
            'id': 'default',
            'name': f'{current_app.config.get("HANA_USER", "unknown")}@{current_app.config.get("HANA_HOST", "unknown")}',
            'host': current_app.config.get("HANA_HOST", "unknown"),
            'port': current_app.config.get("HANA_PORT", 443),
            'user': current_app.config.get("HANA_USER", "unknown"),
            'schema': current_app.config.get("HANA_SCHEMA", "P2P_SCHEMA"),
            'type': 'hana'
        })
    
    return jsonify({
        'success': True,
        'connections': connections
    })