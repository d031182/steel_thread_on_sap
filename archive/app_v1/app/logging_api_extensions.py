"""
Logging API Extensions - Dual-Mode Support
===========================================
Additional endpoints for logging mode management.

This file contains the enhanced /api/logs/client endpoint and
new /api/logging/mode endpoints that were too large to cleanly
integrate into app.py via replace operations.

Integration: Import and register these endpoints in app.py

Author: P2P Development Team
Version: 1.0.0
Date: 2026-02-07
"""

from flask import request, jsonify
from datetime import datetime
import logging

# This will be imported from app.py context
# from modules.log_manager.backend.logging_modes import logging_mode_manager, LoggingMode

logger = logging.getLogger(__name__)


def register_logging_extensions(app, logging_mode_manager, LoggingMode):
    """
    Register enhanced logging endpoints with Flask app.
    
    Args:
        app: Flask application instance
        logging_mode_manager: LoggingModeManager instance
        LoggingMode: LoggingMode enum class
    """
    
    @app.route('/api/logs/client', methods=['POST'])
    def log_client_activity():
        """
        Log client-side errors and activities.
        
        Behavior depends on logging mode:
        - DEFAULT: Only ERROR level logs accepted
        - FLIGHT_RECORDER: All levels (INFO, WARNING, ERROR) accepted
        """
        try:
            data = request.get_json()
            
            level = data.get('level', 'ERROR').upper()
            message = data.get('message', 'No message')
            category = data.get('category', 'UNKNOWN')
            details = data.get('details', {})
            
            # Check if should log based on mode
            if not logging_mode_manager.should_log_frontend_activity(level):
                # Default mode: Only accept errors
                return jsonify({
                    'success': True,
                    'message': 'Log ignored (mode: default, non-error level)',
                    'mode': logging_mode_manager.mode.value
                })
            
            # Legacy support for old format
            url = data.get('url', details.get('url', 'unknown'))
            line = data.get('line', details.get('lineno', 0))
            column = data.get('column', details.get('colno', 0))
            error_stack = data.get('stack', details.get('stack', ''))
            timestamp = data.get('timestamp', datetime.now().isoformat())
            user_agent = request.headers.get('User-Agent', 'unknown')
            session_id = details.get('sessionId', 'unknown')
            
            log_func = logger.error if level == 'ERROR' else (logger.warning if level == 'WARNING' else logger.info)
            
            # Format message based on category
            if category in ['CLICK', 'API', 'CONSOLE', 'SAPUI5', 'PERFORMANCE']:
                log_func(f"[CLIENT-{category}] {message}")
                if details:
                    log_func(f"[CLIENT-{category}] Details: {details}")
            else:
                # Legacy error format
                log_func(f"[CLIENT] {level}: {message}")
                log_func(f"[CLIENT] Location: {url}:{line}:{column}")
                if error_stack:
                    log_func(f"[CLIENT] Stack:\n{error_stack}")
            
            log_func(f"[CLIENT] Session: {session_id}, User Agent: {user_agent}")
            
            return jsonify({
                'success': True,
                'message': 'Client log recorded',
                'mode': logging_mode_manager.mode.value
            })
            
        except Exception as e:
            logger.error(f"Error logging client activity: {str(e)}")
            return jsonify({
                'success': False,
                'error': {'message': str(e), 'code': 'SERVER_ERROR'}
            }), 500
    
    
    @app.route('/api/logging/mode', methods=['GET'])
    def get_logging_mode():
        """
        Get current logging mode status.
        
        Returns:
            JSON with current mode, settings, and behavior flags
        """
        try:
            status = logging_mode_manager.get_status()
            return jsonify({
                'success': True,
                'status': status
            })
        except Exception as e:
            logger.error(f"Error getting logging mode: {str(e)}")
            return jsonify({
                'success': False,
                'error': {'message': str(e), 'code': 'SERVER_ERROR'}
            }), 500
    
    
    @app.route('/api/logging/mode', methods=['POST'])
    def set_logging_mode():
        """
        Set logging mode (DEFAULT or FLIGHT_RECORDER).
        
        Request body:
            {
                "mode": "default" or "flight_recorder"
            }
        
        Returns:
            JSON with success status and new mode
        """
        try:
            data = request.get_json()
            mode_str = data.get('mode', '').lower()
            
            if not mode_str:
                return jsonify({
                    'success': False,
                    'error': {'message': 'Mode is required', 'code': 'MISSING_MODE'}
                }), 400
            
            # Validate and convert to enum
            try:
                new_mode = LoggingMode.from_string(mode_str)
            except ValueError as e:
                return jsonify({
                    'success': False,
                    'error': {'message': str(e), 'code': 'INVALID_MODE'}
                }), 400
            
            # Set the mode
            old_mode = logging_mode_manager.mode.value
            logging_mode_manager.set_mode(new_mode)
            
            logger.info(f"Logging mode changed: {old_mode} → {new_mode.value}")
            
            return jsonify({
                'success': True,
                'message': f'Logging mode changed to {new_mode.value}',
                'old_mode': old_mode,
                'new_mode': new_mode.value,
                'status': logging_mode_manager.get_status()
            })
            
        except Exception as e:
            logger.error(f"Error setting logging mode: {str(e)}")
            return jsonify({
                'success': False,
                'error': {'message': str(e), 'code': 'SERVER_ERROR'}
            }), 500
    
    
    @app.route('/api/logging/mode', methods=['DELETE'])
    def clear_logging_mode_override():
        """
        Clear runtime logging mode override.
        
        Returns to environment-configured mode.
        
        Returns:
            JSON with success status
        """
        try:
            old_mode = logging_mode_manager.mode.value
            logging_mode_manager.clear_override()
            new_mode = logging_mode_manager.mode.value
            
            logger.info(f"Logging mode override cleared: {old_mode} → {new_mode}")
            
            return jsonify({
                'success': True,
                'message': 'Logging mode override cleared',
                'old_mode': old_mode,
                'new_mode': new_mode,
                'status': logging_mode_manager.get_status()
            })
            
        except Exception as e:
            logger.error(f"Error clearing logging mode override: {str(e)}")
            return jsonify({
                'success': False,
                'error': {'message': str(e), 'code': 'SERVER_ERROR'}
            }), 500
    
    logger.info("Logging API extensions registered (dual-mode support)")