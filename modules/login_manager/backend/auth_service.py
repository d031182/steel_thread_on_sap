"""
Authentication Service

Handles user authentication logic with support for:
- Auto-login with default user (HANA_DP_USER)
- Manual authentication
- User session management
"""

import os
from typing import Optional, Dict
from datetime import datetime


class User:
    """User model for authenticated sessions"""
    
    def __init__(self, username: str, role: str = "user", source: str = "auto"):
        self.username = username
        self.role = role
        self.source = source  # 'auto' or 'manual'
        self.authenticated_at = datetime.utcnow()
    
    def to_dict(self) -> Dict:
        """Convert user to dictionary"""
        return {
            'username': self.username,
            'role': self.role,
            'source': self.source,
            'authenticated_at': self.authenticated_at.isoformat()
        }
    
    @staticmethod
    def from_dict(data: Dict) -> 'User':
        """Create user from dictionary"""
        user = User(
            username=data['username'],
            role=data.get('role', 'user'),
            source=data.get('source', 'auto')
        )
        if 'authenticated_at' in data:
            user.authenticated_at = datetime.fromisoformat(data['authenticated_at'])
        return user


class AuthenticationService:
    """
    Authentication service with auto-login support
    
    By default, auto-logs in with HANA_DP_USER from environment.
    Supports manual authentication for future extensibility.
    """
    
    def __init__(self):
        self.default_username = os.getenv('HANA_USER', 'HANA_DP_USER')
    
    def get_default_user(self) -> User:
        """
        Get default auto-login user
        
        Returns:
            User object for default user (HANA_DP_USER)
        """
        return User(
            username=self.default_username,
            role='data_viewer',
            source='auto'
        )
    
    def authenticate(self, username: str, password: str) -> Optional[User]:
        """
        Authenticate user with credentials
        
        Currently validates against HANA environment variables.
        Future: Could integrate with LDAP, OAuth, etc.
        
        Args:
            username: Username to authenticate
            password: Password to validate
            
        Returns:
            User object if authenticated, None otherwise
        """
        # Check against environment variables
        hana_user = os.getenv('HANA_USER')
        hana_password = os.getenv('HANA_PASSWORD')
        hana_admin_user = os.getenv('HANA_ADMIN_USER')
        hana_admin_password = os.getenv('HANA_ADMIN_PASSWORD')
        
        # Validate HANA_USER
        if username == hana_user and password == hana_password:
            return User(
                username=username,
                role='data_viewer',
                source='manual'
            )
        
        # Validate HANA_ADMIN_USER
        if username == hana_admin_user and password == hana_admin_password:
            return User(
                username=username,
                role='admin',
                source='manual'
            )
        
        return None
    
    def validate_user(self, user: User) -> bool:
        """
        Validate that user is still valid
        
        Args:
            user: User to validate
            
        Returns:
            True if user is valid
        """
        if not user or not user.username:
            return False
        
        # User is valid if username matches environment
        return user.username in [
            os.getenv('HANA_USER'),
            os.getenv('HANA_ADMIN_USER')
        ]