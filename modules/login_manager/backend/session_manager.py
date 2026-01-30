"""
Session Manager

Manages user sessions using Flask session storage.
Handles auto-login with default user on first access.
"""

from flask import session
from typing import Optional
from .auth_service import User, AuthenticationService


class SessionManager:
    """
    Session manager for user authentication
    
    Uses Flask session for storage.
    Auto-initializes with default user if no session exists.
    """
    
    SESSION_KEY = 'authenticated_user'
    
    def __init__(self, auth_service: AuthenticationService):
        self.auth_service = auth_service
    
    def get_current_user(self) -> User:
        """
        Get currently authenticated user
        
        If no session exists, auto-login with default user.
        
        Returns:
            Current authenticated user
        """
        # Check if user in session
        user_data = session.get(self.SESSION_KEY)
        
        if user_data:
            return User.from_dict(user_data)
        
        # No session - auto-login with default user
        default_user = self.auth_service.get_default_user()
        self.set_current_user(default_user)
        return default_user
    
    def set_current_user(self, user: User) -> None:
        """
        Set current authenticated user in session
        
        Args:
            user: User to store in session
        """
        session[self.SESSION_KEY] = user.to_dict()
        session.modified = True
    
    def login(self, username: str, password: str) -> Optional[User]:
        """
        Authenticate and login user
        
        Args:
            username: Username to authenticate
            password: Password to validate
            
        Returns:
            User object if successful, None otherwise
        """
        user = self.auth_service.authenticate(username, password)
        
        if user:
            self.set_current_user(user)
            return user
        
        return None
    
    def logout(self) -> bool:
        """
        Logout current user and revert to default auto-login
        
        Returns:
            True if logout successful
        """
        # Remove user from session
        if self.SESSION_KEY in session:
            session.pop(self.SESSION_KEY)
            session.modified = True
        
        # Auto-login with default user
        default_user = self.auth_service.get_default_user()
        self.set_current_user(default_user)
        
        return True
    
    def is_authenticated(self) -> bool:
        """
        Check if user is authenticated
        
        Returns:
            True if user session exists
        """
        return self.SESSION_KEY in session
    
    def validate_session(self) -> bool:
        """
        Validate current session
        
        Returns:
            True if session is valid
        """
        user = self.get_current_user()
        return self.auth_service.validate_user(user)


# Global instance to be initialized by app
_session_manager: Optional[SessionManager] = None


def init_session_manager(auth_service: AuthenticationService) -> SessionManager:
    """
    Initialize global session manager
    
    Args:
        auth_service: Authentication service instance
        
    Returns:
        SessionManager instance
    """
    global _session_manager
    _session_manager = SessionManager(auth_service)
    return _session_manager


def get_session_manager() -> SessionManager:
    """
    Get global session manager instance
    
    Returns:
        SessionManager instance
        
    Raises:
        RuntimeError: If session manager not initialized
    """
    if _session_manager is None:
        raise RuntimeError(
            "SessionManager not initialized. "
            "Call init_session_manager() first."
        )
    return _session_manager