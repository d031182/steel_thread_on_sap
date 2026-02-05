"""
Tests for Authentication Service

Run with: python -m pytest modules/login_manager/tests/test_auth_service.py -v
"""

import os
import pytest
from modules.login_manager.backend.auth_service import AuthenticationService, User


class TestUser:
    """Test User model"""
    
    @pytest.mark.unit
    @pytest.mark.fast
    def test_user_creation(self):
        """Test creating a user"""
        user = User('testuser', 'admin', 'manual')
        assert user.username == 'testuser'
        assert user.role == 'admin'
        assert user.source == 'manual'
    
    @pytest.mark.unit
    @pytest.mark.fast
    def test_user_to_dict(self):
        """Test converting user to dictionary"""
        user = User('testuser', 'admin', 'manual')
        data = user.to_dict()
        assert data['username'] == 'testuser'
        assert data['role'] == 'admin'
        assert data['source'] == 'manual'
        assert 'authenticated_at' in data
    
    @pytest.mark.unit
    @pytest.mark.fast
    def test_user_from_dict(self):
        """Test creating user from dictionary"""
        data = {
            'username': 'testuser',
            'role': 'admin',
            'source': 'manual'
        }
        user = User.from_dict(data)
        assert user.username == 'testuser'
        assert user.role == 'admin'
        assert user.source == 'manual'


class TestAuthenticationService:
    """Test Authentication Service"""
    
    @pytest.mark.unit
    @pytest.mark.fast
    def test_get_default_user(self):
        """Test getting default user"""
        service = AuthenticationService()
        user = service.get_default_user()
        assert user is not None
        assert user.role == 'data_viewer'
        assert user.source == 'auto'
    
    @pytest.mark.unit
    @pytest.mark.fast
    def test_authenticate_with_valid_credentials(self, monkeypatch):
        """Test authentication with valid credentials"""
        # Mock environment variables
        monkeypatch.setenv('HANA_USER', 'TEST_USER')
        monkeypatch.setenv('HANA_PASSWORD', 'TEST_PASS')
        
        service = AuthenticationService()
        user = service.authenticate('TEST_USER', 'TEST_PASS')
        
        assert user is not None
        assert user.username == 'TEST_USER'
        assert user.role == 'data_viewer'
        assert user.source == 'manual'
    
    @pytest.mark.unit
    @pytest.mark.fast
    def test_authenticate_with_invalid_credentials(self, monkeypatch):
        """Test authentication with invalid credentials"""
        monkeypatch.setenv('HANA_USER', 'TEST_USER')
        monkeypatch.setenv('HANA_PASSWORD', 'TEST_PASS')
        
        service = AuthenticationService()
        user = service.authenticate('WRONG_USER', 'WRONG_PASS')
        
        assert user is None
    
    @pytest.mark.unit
    @pytest.mark.fast
    def test_authenticate_admin_user(self, monkeypatch):
        """Test authentication with admin credentials"""
        monkeypatch.setenv('HANA_ADMIN_USER', 'ADMIN')
        monkeypatch.setenv('HANA_ADMIN_PASSWORD', 'ADMIN_PASS')
        
        service = AuthenticationService()
        user = service.authenticate('ADMIN', 'ADMIN_PASS')
        
        assert user is not None
        assert user.username == 'ADMIN'
        assert user.role == 'admin'
        assert user.source == 'manual'
    
    @pytest.mark.unit
    @pytest.mark.fast
    def test_validate_user(self, monkeypatch):
        """Test user validation"""
        monkeypatch.setenv('HANA_USER', 'TEST_USER')
        
        service = AuthenticationService()
        user = User('TEST_USER', 'data_viewer', 'auto')
        
        is_valid = service.validate_user(user)
        assert is_valid is True
    
    @pytest.mark.unit
    @pytest.mark.fast
    def test_validate_invalid_user(self, monkeypatch):
        """Test invalid user validation"""
        monkeypatch.setenv('HANA_USER', 'TEST_USER')
        
        service = AuthenticationService()
        user = User('UNKNOWN_USER', 'data_viewer', 'auto')
        
        is_valid = service.validate_user(user)
        assert is_valid is False


if __name__ == '__main__':
    pytest.main([__file__, '-v'])