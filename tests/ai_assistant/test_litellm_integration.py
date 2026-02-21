"""
Test LiteLLM integration with AI Assistant
"""

import os
import pytest
from unittest.mock import patch, Mock
from modules.ai_assistant.backend.services.agent_service import JouleAgent


class TestLiteLLMIntegration:
    """Test LiteLLM provider integration"""
    
    def test_litellm_provider_initialization(self):
        """Test that LiteLLM provider initializes correctly with proper environment variables"""
        with patch.dict(os.environ, {
            'AI_PROVIDER': 'litellm',
            'LITELLM_BASE_URL': 'http://localhost:6655/litellm/v1',
            'LITELLM_API_KEY': 'test-api-key',
            'LITELLM_MODEL_NAME': 'gpt-4.1-mini'
        }):
            agent = JouleAgent(provider='litellm')
            
            # Verify provider is set correctly
            assert agent.provider == 'litellm'
            assert agent.model_name == 'gpt-4.1-mini'
            
            # Verify environment variables are set for OpenAI model
            assert os.environ.get('OPENAI_API_KEY') == 'test-api-key'
            assert os.environ.get('OPENAI_BASE_URL') == 'http://localhost:6655/litellm/v1'
    
    def test_litellm_provider_missing_base_url(self):
        """Test that LiteLLM provider fails gracefully when BASE_URL is missing"""
        with patch.dict(os.environ, {
            'AI_PROVIDER': 'litellm',
            'LITELLM_API_KEY': 'test-api-key'
        }, clear=False):
            # Remove LITELLM_BASE_URL if it exists
            if 'LITELLM_BASE_URL' in os.environ:
                del os.environ['LITELLM_BASE_URL']
            
            with pytest.raises(ValueError, match="LITELLM_BASE_URL required for LiteLLM provider"):
                JouleAgent(provider='litellm')
    
    def test_litellm_provider_missing_api_key(self):
        """Test that LiteLLM provider fails gracefully when API_KEY is missing"""
        with patch.dict(os.environ, {
            'AI_PROVIDER': 'litellm',
            'LITELLM_BASE_URL': 'http://localhost:6655/litellm/v1'
        }, clear=False):
            # Remove LITELLM_API_KEY if it exists
            if 'LITELLM_API_KEY' in os.environ:
                del os.environ['LITELLM_API_KEY']
            
            with pytest.raises(ValueError, match="LITELLM_API_KEY required for LiteLLM provider"):
                JouleAgent(provider='litellm')
    
    def test_litellm_provider_default_model(self):
        """Test that LiteLLM uses default model when none specified"""
        with patch.dict(os.environ, {
            'AI_PROVIDER': 'litellm',
            'LITELLM_BASE_URL': 'http://localhost:6655/litellm/v1',
            'LITELLM_API_KEY': 'test-api-key'
        }, clear=False):
            # Remove LITELLM_MODEL_NAME if it exists
            if 'LITELLM_MODEL_NAME' in os.environ:
                del os.environ['LITELLM_MODEL_NAME']
            
            agent = JouleAgent(provider='litellm')
            
            # Should use default model
            assert agent.model_name == 'gpt-4.1-mini'
    
    def test_litellm_provider_custom_model(self):
        """Test that LiteLLM uses custom model when specified"""
        with patch.dict(os.environ, {
            'AI_PROVIDER': 'litellm',
            'LITELLM_BASE_URL': 'http://localhost:6655/litellm/v1',
            'LITELLM_API_KEY': 'test-api-key',
            'LITELLM_MODEL_NAME': 'custom-model'
        }):
            agent = JouleAgent(provider='litellm')
            
            # Should use custom model
            assert agent.model_name == 'custom-model'
    
    def test_litellm_provider_explicit_model_override(self):
        """Test that explicit model_name parameter overrides environment variable"""
        with patch.dict(os.environ, {
            'AI_PROVIDER': 'litellm',
            'LITELLM_BASE_URL': 'http://localhost:6655/litellm/v1',
            'LITELLM_API_KEY': 'test-api-key',
            'LITELLM_MODEL_NAME': 'env-model'
        }):
            agent = JouleAgent(provider='litellm', model_name='override-model')
            
            # Should use explicit model name
            assert agent.model_name == 'override-model'
    
    def test_provider_auto_detection_litellm(self):
        """Test that provider auto-detection works for LiteLLM"""
        with patch.dict(os.environ, {
            'AI_PROVIDER': 'litellm',
            'LITELLM_BASE_URL': 'http://localhost:6655/litellm/v1',
            'LITELLM_API_KEY': 'test-api-key'
        }):
            # Don't specify provider, should auto-detect from AI_PROVIDER
            agent = JouleAgent()
            
            assert agent.provider == 'litellm'
    
    def test_supported_providers_list_includes_litellm(self):
        """Test that LiteLLM is included in the supported providers error message"""
        with pytest.raises(ValueError) as excinfo:
            JouleAgent(provider='unsupported_provider')
        
        error_message = str(excinfo.value)
        assert 'litellm' in error_message
        assert 'Supported: groq, github, ai_core, litellm' in error_message


if __name__ == '__main__':
    pytest.main([__file__, '-v'])