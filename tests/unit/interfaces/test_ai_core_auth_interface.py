"""
Unit tests for IAICoreLLMAuthentication interface contract

Tests verify that the interface contract is properly implemented
and can be used across modules without direct dependencies.
"""

import pytest
from abc import ABC
from core.interfaces.ai_core_auth import IAICoreLLMAuthentication
from modules.ai_assistant.backend.services.ai_core_auth import AICoreLLMAuthentication


class TestAICoreLLMAuthenticationInterface:
    """Verify AICoreLLMAuthentication implements IAICoreLLMAuthentication."""

    def test_interface_implementation(self):
        """Test that AICoreLLMAuthentication is a proper subclass."""
        assert issubclass(AICoreLLMAuthentication, IAICoreLLMAuthentication)

    def test_interface_is_abstract(self):
        """Test that IAICoreLLMAuthentication is an abstract base class."""
        assert issubclass(IAICoreLLMAuthentication, ABC)

    def test_required_methods_exist(self):
        """Test that all required interface methods are implemented."""
        required_methods = ['get_oauth_token', 'check_oauth_token_expiry']
        for method in required_methods:
            assert hasattr(AICoreLLMAuthentication, method), \
                f"Missing required method: {method}"
            assert callable(getattr(AICoreLLMAuthentication, method)), \
                f"Method {method} is not callable"

    def test_instantiation_via_interface_type(self):
        """Test that instances can be treated as IAICoreLLMAuthentication."""
        auth = AICoreLLMAuthentication(
            client_id='test',
            client_secret='test',
            auth_url='https://test'
        )
        assert isinstance(auth, IAICoreLLMAuthentication)

    def test_get_oauth_token_method_signature(self):
        """Test that get_oauth_token has correct signature."""
        import inspect
        auth = AICoreLLMAuthentication(
            client_id='test',
            client_secret='test',
            auth_url='https://test'
        )
        sig = inspect.signature(auth.get_oauth_token)
        # Should take no parameters (besides self)
        assert len(sig.parameters) == 0

    def test_check_oauth_token_expiry_method_signature(self):
        """Test that check_oauth_token_expiry has correct signature."""
        import inspect
        auth = AICoreLLMAuthentication(
            client_id='test',
            client_secret='test',
            auth_url='https://test'
        )
        sig = inspect.signature(auth.check_oauth_token_expiry)
        # Should take no parameters (besides self)
        assert len(sig.parameters) == 0

    def test_interface_dependency_injection_pattern(self):
        """Test that interface can be used for dependency injection."""
        def service_function(auth: IAICoreLLMAuthentication) -> str:
            """Simulates a service that accepts the interface."""
            return f"Service using {type(auth).__name__}"

        auth = AICoreLLMAuthentication(
            client_id='test',
            client_secret='test',
            auth_url='https://test'
        )
        result = service_function(auth)
        assert "AICoreLLMAuthentication" in result

    def test_interface_decouples_modules(self):
        """Test that modules can depend on interface, not implementation."""
        # This test verifies the architectural principle:
        # data_products_v2 should import IAICoreLLMAuthentication
        # not AICoreLLMAuthentication directly
        from modules.data_products_v2.backend import api

        # Verify the import uses the interface
        import inspect
        source = inspect.getsource(api)
        assert 'core.interfaces.ai_core_auth' in source, \
            "data_products_v2 should import from core.interfaces"
        assert 'from modules.ai_assistant' not in source, \
            "data_products_v2 should not directly import from ai_assistant"