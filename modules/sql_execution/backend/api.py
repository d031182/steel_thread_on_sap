"""
SQL Execution API Blueprint
============================
Flask blueprint for executing arbitrary SQL queries on HANA.

Routes:
- POST /api/sql/execute - Execute SQL query
- GET /api/sql/connections - List available connections

This module provides SQL execution capabilities with:
- Query validation
- Result formatting
- Error handling
- Connection management

Part of: SQL Execution Module
Version: 1.0
"""

from flask import Blueprint, request, jsonify, current_app
import logging
import traceback

# Create blueprint
sql_execution_api = Blueprint('sql_execution', __name__)

# Logger
logger = logging.getLogger(__name__)


@sql_execution_api.route('/execute', methods=['POST'])
def execute_sql():
    """
    Execute arbitrary SQL query on HANA
    
    Request Body:
        {
            "sql": "SELECT * FROM ...",
            "connection_id": "default" (optional)
        }
    
    Returns:
        JSON with query results or error
    """
    try:
        # Get HANA data source from app
        hana_data_source = current_app.hana_data_source
        
        if not hana_data_source:
            return jsonify({
                'success': False,
                'error': {'message': 'HANA not configured', 'code': 'NOT_CONFIGURED'}
            }), 500
        
        data = request.get_json()
        sql = data.get('sql', '').strip()
        
        # Validation
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
        
        # Execute via DataSource interface (works with HANA, SQLite, PostgreSQL, etc.)
        result = hana_data_source.execute_query(sql)
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Error in execute_sql: {str(e)}\n{traceback.format_exc()}")
        
        # Get ENV from app config
        env = current_app.config.get('ENV', 'production')
        error_message = str(e) if env == 'development' else 'Internal server error'
        
        return jsonify({
            'success': False,
            'error': {'message': error_message, 'code': 'SERVER_ERROR'}
        }), 500


@sql_execution_api.route('/connections', methods=['GET'])
def list_connections():
    """
    List available HANA connections
    
    Returns:
        JSON with list of connections
    """
    try:
        connections = []
        
        # Get HANA data source from app
        hana_data_source = current_app.hana_data_source
        
        if hana_data_source:
            # Get config from app
            hana_host = current_app.config.get('HANA_HOST', '')
            hana_port = current_app.config.get('HANA_PORT', 443)
            hana_user = current_app.config.get('HANA_USER', '')
            hana_schema = current_app.config.get('HANA_SCHEMA', '')
            
            connections.append({
                'id': 'default',
                'name': f'{hana_user}@{hana_host}',
                'host': hana_host,
                'port': hana_port,
                'user': hana_user,
                'schema': hana_schema,
                'type': 'hana'
            })
        
        return jsonify({
            'success': True,
            'connections': connections
        })
        
    except Exception as e:
        logger.error(f"Error in list_connections: {str(e)}")
        return jsonify({
            'success': False,
            'error': {'message': str(e), 'code': 'SERVER_ERROR'}
        }), 500


# Health check for this module
@sql_execution_api.route('/health', methods=['GET'])
def health():
    """Module health check"""
    hana_available = current_app.hana_data_source is not None
    
    return jsonify({
        'success': True,
        'module': 'sql_execution',
        'status': 'healthy' if hana_available else 'hana_not_configured',
        'hana_available': hana_available
    })