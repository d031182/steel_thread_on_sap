"""
Application Logging API Endpoints
=================================
Flask Blueprint providing REST API for application log management.

Endpoints:
- GET /api/logs - Retrieve logs with filtering
- GET /api/logs/stats - Get log statistics
- POST /api/logs/clear - Clear all logs
- POST /api/logs/client - Log client-side errors

Author: P2P Development Team
Version: 1.0.0
Date: 2026-01-24
"""

from flask import Blueprint, request, jsonify
from datetime import datetime
import logging


def create_blueprint(log_handler):
    """
    Create Flask Blueprint for log management API
    
    Args:
        log_handler: SQLiteLogHandler instance
        
    Returns:
        Flask Blueprint configured with log endpoints
    """
    bp = Blueprint('log_manager_api', __name__)
    logger = logging.getLogger(__name__)
    
    @bp.route('/logs', methods=['GET'])
    def get_logs():
        """
        Get application logs from SQLite database
        
        Query Parameters:
            level: Filter by log level (INFO, WARNING, ERROR)
            limit: Maximum logs to return (default: 100, max: 1000)
            offset: Pagination offset (default: 0)
            start_date: Filter logs after this date (ISO format)
            end_date: Filter logs before this date (ISO format)
            
        Returns:
            JSON with logs array and pagination info
        """
        try:
            # Get query parameters
            level = request.args.get('level', None)
            limit = min(int(request.args.get('limit', 100)), 1000)
            offset = max(int(request.args.get('offset', 0)), 0)
            start_date = request.args.get('start_date', None)
            end_date = request.args.get('end_date', None)
            
            # Validate level
            if level and level not in ['INFO', 'WARNING', 'ERROR']:
                return jsonify({
                    'success': False,
                    'error': {'message': 'Invalid log level', 'code': 'INVALID_LEVEL'}
                }), 400
            
            # Get logs from handler
            logs = log_handler.get_logs(
                level=level,
                limit=limit,
                offset=offset,
                start_date=start_date,
                end_date=end_date
            )
            
            # Get total count for pagination
            total_count = log_handler.get_log_count(level=level)
            
            return jsonify({
                'success': True,
                'count': len(logs),
                'totalCount': total_count,
                'logs': logs,
                'filters': {
                    'level': level,
                    'limit': limit,
                    'offset': offset,
                    'start_date': start_date,
                    'end_date': end_date
                }
            })
            
        except Exception as e:
            logger.error(f"Error in get_logs: {str(e)}")
            return jsonify({
                'success': False,
                'error': {'message': str(e), 'code': 'SERVER_ERROR'}
            }), 500
    
    @bp.route('/logs/stats', methods=['GET'])
    def get_log_stats():
        """
        Get log statistics (counts by level)
        
        Returns:
            JSON with statistics for each log level
        """
        try:
            total = log_handler.get_log_count()
            info_count = log_handler.get_log_count(level='INFO')
            warning_count = log_handler.get_log_count(level='WARNING')
            error_count = log_handler.get_log_count(level='ERROR')
            
            return jsonify({
                'success': True,
                'stats': {
                    'total': total,
                    'info': info_count,
                    'warning': warning_count,
                    'error': error_count
                }
            })
        except Exception as e:
            logger.error(f"Error getting log stats: {str(e)}")
            return jsonify({
                'success': False,
                'error': {'message': str(e), 'code': 'SERVER_ERROR'}
            }), 500
    
    @bp.route('/logs/clear', methods=['POST'])
    def clear_logs():
        """
        Clear all stored logs
        
        Returns:
            JSON success response
        """
        try:
            log_handler.clear_logs()
            logger.info("Logs cleared by user request")
            return jsonify({
                'success': True,
                'message': 'Logs cleared successfully'
            })
        except Exception as e:
            logger.error(f"Error clearing logs: {str(e)}")
            return jsonify({
                'success': False,
                'error': {'message': str(e), 'code': 'SERVER_ERROR'}
            }), 500
    
    # Known harmless browser warnings to suppress
    SUPPRESSED_CLIENT_PATTERNS = [
        "ResizeObserver loop completed with undelivered notifications",
        "ResizeObserver loop limit exceeded",
    ]
    
    def should_suppress_log(message: str) -> bool:
        """Check if log message should be suppressed based on known harmless patterns"""
        for pattern in SUPPRESSED_CLIENT_PATTERNS:
            if pattern in message:
                return True
        return False
    
    @bp.route('/logs/client', methods=['POST'])
    def log_client_error():
        """
        Log client-side errors from browser console
        
        This endpoint receives JavaScript errors, warnings, and logs from the frontend
        and stores them in the application log for analysis.
        
        Filters out known harmless browser warnings (e.g., ResizeObserver timing issues).
        
        Request Body:
            level: Log level (ERROR, WARNING, INFO)
            message: Error message
            url: Page URL where error occurred
            line: Line number
            column: Column number
            stack: Stack trace (optional)
            timestamp: Client timestamp (optional)
            
        Returns:
            JSON success response
        """
        try:
            data = request.get_json()
            
            level = data.get('level', 'ERROR').upper()
            message = data.get('message', 'No message')
            url = data.get('url', 'unknown')
            line = data.get('line', 0)
            column = data.get('column', 0)
            error_stack = data.get('stack', '')
            timestamp = data.get('timestamp', datetime.now().isoformat())
            user_agent = request.headers.get('User-Agent', 'unknown')
            
            # Filter out known harmless warnings
            if should_suppress_log(message):
                return jsonify({
                    'success': True,
                    'message': 'Suppressed known harmless warning'
                })
            
            # Map client log levels to Python logging levels
            log_func = logger.error
            if level == 'WARNING' or level == 'WARN':
                log_func = logger.warning
            elif level == 'INFO':
                log_func = logger.info
            
            # Log with detailed context
            log_func(f"[CLIENT] {level}: {message}")
            log_func(f"[CLIENT] Location: {url}:{line}:{column}")
            if error_stack:
                log_func(f"[CLIENT] Stack trace:\n{error_stack}")
            log_func(f"[CLIENT] User Agent: {user_agent}")
            log_func(f"[CLIENT] Timestamp: {timestamp}")
            
            return jsonify({
                'success': True,
                'message': 'Client error logged successfully'
            })
            
        except Exception as e:
            logger.error(f"Error logging client error: {str(e)}")
            return jsonify({
                'success': False,
                'error': {'message': str(e), 'code': 'SERVER_ERROR'}
            }), 500
    
    return bp