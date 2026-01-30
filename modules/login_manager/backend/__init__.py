"""
Login Manager Module
====================
User authentication and session management.

Exports:
    - login_manager_api: Flask blueprint for REST API
    - AuthenticationService: Authentication business logic
    - SessionManager: Session management
    - get_current_user: Helper function to get current user
"""

from .api import login_manager_api
from .auth_service import AuthenticationService, User
from .session_manager import SessionManager, get_session_manager


def get_current_user() -> User:
    """
    Helper function to get current authenticated user
    
    Returns:
        Current user from session (auto-login if no session)
    """
    session_mgr = get_session_manager()
    return session_mgr.get_current_user()


__all__ = [
    'login_manager_api',
    'AuthenticationService',
    'SessionManager',
    'User',
    'get_current_user',
    'get_session_manager'
]