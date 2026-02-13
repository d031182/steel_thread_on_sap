"""
Logger API Endpoints
===================
Flask routes for logging management and client log submission
"""

from flask import request, jsonify
from datetime import datetime
import logging

from . import logger_api
from .logging_modes import logging_mode_manager, LoggingMode


# Configure Python logger
logger = logging.getLogger(__name__)


@logger_api.route('/mode', methods=['GET'])
def get_logging_mode():
    """
    Get current logging mode configuration
    
    Returns:
        JSON: Current mode and feature flags
    """
    try:
        return jsonify({
            'status': 'success',
            'data': logging_mode_manager.to_dict()
        }), 200
    except Exception as e:
        logger.error(f"Failed to get logging mode: {e}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


@logger_api.route('/mode', methods=['POST'])
def set_logging_mode():
    """
    Set logging mode (default or flight_recorder)
    
    Request Body:
        {
            "mode": "default" | "flight_recorder"
        }
    
    Returns:
        JSON: Updated mode configuration
    """
    try:
        data = request.get_json()
        
        if not data or 'mode' not in data:
            return jsonify({
                'status': 'error',
                'message': 'Missing required field: mode'
            }), 400
        
        mode_str = data['mode'].lower()
        
        try:
            new_mode = LoggingMode(mode_str)
        except ValueError:
            return jsonify({
                'status': 'error',
                'message': f'Invalid mode: {mode_str}. Must be "default" or "flight_recorder"'
            }), 400
        
        # Update mode
        logging_mode_manager.mode = new_mode
        
        logger.info(f"Logging mode changed to: {new_mode.value}")
        
        return jsonify({
            'status': 'success',
            'message': f'Logging mode changed to {new_mode.value}',
            'data': logging_mode_manager.to_dict()
        }), 200
        
    except Exception as e:
        logger.error(f"Failed to set logging mode: {e}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


@logger_api.route('/client', methods=['POST'])
def receive_client_log():
    """
    Receive log entries from frontend (Flight Recorder mode)
    
    Request Body:
        {
            "level": "INFO" | "WARN" | "ERROR",
            "category": "CLICK" | "API" | "CONSOLE" | "ERROR" | "SAPUI5",
            "message": "Log message",
            "details": {
                // Category-specific details
            }
        }
    
    Returns:
        JSON: Acknowledgment
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'status': 'error',
                'message': 'Empty request body'
            }), 400
        
        # Validate required fields
        required_fields = ['level', 'category', 'message']
        missing = [f for f in required_fields if f not in data]
        if missing:
            return jsonify({
                'status': 'error',
                'message': f'Missing required fields: {", ".join(missing)}'
            }), 400
        
        level = data['level'].upper()
        category = data['category'].upper()
        message = data['message']
        details = data.get('details', {})
        
        # Filter based on logging mode
        frontend_filter = logging_mode_manager.get_frontend_log_filter()
        
        if frontend_filter == 'ERROR' and level != 'ERROR':
            # Default mode: Only accept ERROR logs from frontend
            return jsonify({
                'status': 'success',
                'message': 'Log filtered (default mode accepts ERROR only)'
            }), 200
        
        # Log to Python logger with appropriate level
        log_message = f"[FRONTEND] [{category}] {message}"
        
        if level == 'ERROR':
            logger.error(log_message, extra={'details': details})
        elif level == 'WARN':
            logger.warning(log_message, extra={'details': details})
        else:
            logger.info(log_message, extra={'details': details})
        
        # TODO: Persist to database (LogRepository)
        # For now, logs go to Python logger (file/console)
        
        return jsonify({
            'status': 'success',
            'message': 'Log received'
        }), 200
        
    except Exception as e:
        logger.error(f"Failed to process client log: {e}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


@logger_api.route('/logs', methods=['GET'])
def get_logs():
    """
    Retrieve application logs (paginated)
    
    Query Parameters:
        - level: Filter by level (INFO, WARN, ERROR)
        - category: Filter by category
        - limit: Max results (default: 100)
        - offset: Pagination offset (default: 0)
    
    Returns:
        JSON: Log entries array
    """
    try:
        # Query parameters
        level = request.args.get('level', '').upper()
        category = request.args.get('category', '').upper()
        limit = int(request.args.get('limit', 100))
        offset = int(request.args.get('offset', 0))
        
        # TODO: Implement LogRepository.query()
        # For now, return empty (logs from Python logger file)
        
        return jsonify({
            'status': 'success',
            'data': {
                'logs': [],
                'total': 0,
                'limit': limit,
                'offset': offset,
                'message': 'Log retrieval not yet implemented (see logs/ directory)'
            }
        }), 200
        
    except Exception as e:
        logger.error(f"Failed to retrieve logs: {e}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


@logger_api.route('/health', methods=['GET'])
def health_check():
    """
    Health check endpoint
    
    Returns:
        JSON: Module health status
    """
    return jsonify({
        'status': 'healthy',
        'module': 'logger',
        'version': '1.0.0',
        'mode': logging_mode_manager.mode.value,
        'timestamp': datetime.utcnow().isoformat()
    }), 200