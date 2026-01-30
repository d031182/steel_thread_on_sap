"""
Login Manager API

REST API endpoints for authentication and session management.
"""

from flask import Blueprint, jsonify, request
from .auth_service import AuthenticationService
from .session_manager import SessionManager, get_session_manager


# Create blueprint
login_manager_api = Blueprint('login_manager_api', __name__)

# Module-level service instances (initialized by app)
_auth_service: AuthenticationService = None
_session_manager: SessionManager = None


def init_services():
    """Initialize module services"""
    global _auth_service, _session_manager
    _auth_service = AuthenticationService()
    _session_manager = SessionManager(_auth_service)


@login_manager_api.route('/current-user', methods=['GET'])
def get_current_user():
    """
    Get currently authenticated user
    
    Returns:
        JSON response with user details
    """
    try:
        # Initialize services if not done
        if _session_manager is None:
            init_services()
        
        user = _session_manager.get_current_user()
        
        return jsonify({
            'success': True,
            'user': user.to_dict()
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@login_manager_api.route('/login', methods=['POST'])
def login():
    """
    Authenticate user and create session
    
    Request Body:
        {
            "username": "HANA_DP_USER",
            "password": "password"
        }
    
    Returns:
        JSON response with authentication result
    """
    try:
        # Initialize services if not done
        if _session_manager is None:
            init_services()
        
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')
        
        if not username or not password:
            return jsonify({
                'success': False,
                'error': 'Username and password required'
            }), 400
        
        user = _session_manager.login(username, password)
        
        if user:
            return jsonify({
                'success': True,
                'user': user.to_dict(),
                'message': f'Logged in as {user.username}'
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Invalid credentials'
            }), 401
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@login_manager_api.route('/logout', methods=['POST'])
def logout():
    """
    Logout current user and revert to auto-login
    
    Returns:
        JSON response with logout result
    """
    try:
        # Initialize services if not done
        if _session_manager is None:
            init_services()
        
        _session_manager.logout()
        
        return jsonify({
            'success': True,
            'message': 'Logged out successfully (reverted to auto-login)'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@login_manager_api.route('/validate', methods=['GET'])
def validate_session():
    """
    Validate current session
    
    Returns:
        JSON response with validation result
    """
    try:
        # Initialize services if not done
        if _session_manager is None:
            init_services()
        
        is_valid = _session_manager.validate_session()
        
        return jsonify({
            'success': True,
            'valid': is_valid
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500