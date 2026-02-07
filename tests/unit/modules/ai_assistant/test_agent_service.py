"""Unit tests for AI Agent Service

Tests the Pydantic AI + Groq agent service functionality.
"""

import pytest
import os
from unittest.mock import Mock, patch, MagicMock
from modules.ai_assistant.backend.agent_service import (
    AgentService,
    AgentConfig
)


@pytest.fixture
def mock_env_with_key(monkeypatch):
    """Mock environment with GROQ_API_KEY"""
    monkeypatch.setenv('GROQ_API_KEY', 'test_key_12345')


@pytest.fixture
def mock_env_without_key(monkeypatch):
    """Mock environment without GROQ_API_KEY"""
    monkeypatch.delenv('GROQ_API_KEY', raising=False)


@pytest.fixture
def agent_config():
    """Create test agent configuration"""
    return AgentConfig(
        model="groq:llama-3.1-70b-versatile",
        temperature=0.1,
        max_tokens=500,
        system_prompt="Test system prompt"
    )


@pytest.fixture
def agent_service(mock_env_with_key, agent_config):
    """Create agent service with mocked environment"""
    return AgentService(config=agent_config)


# Configuration Tests

@pytest.mark.unit
def test_agent_config_defaults():
    """Test AgentConfig default values"""
    config = AgentConfig()
    
    assert config.model == "groq:llama-3.1-70b-versatile"
    assert config.temperature == 0.1
    assert config.max_tokens == 1000
    assert "helpful AI assistant" in config.system_prompt


@pytest.mark.unit
def test_agent_config_custom():
    """Test AgentConfig with custom values"""
    config = AgentConfig(
        model="groq:mixtral-8x7b",
        temperature=0.5,
        max_tokens=2000,
        system_prompt="Custom prompt"
    )
    
    assert config.model == "groq:mixtral-8x7b"
    assert config.temperature == 0.5
    assert config.max_tokens == 2000
    assert config.system_prompt == "Custom prompt"


# Initialization Tests

@pytest.mark.unit
def test_agent_service_init_success(mock_env_with_key, agent_config):
    """Test successful agent service initialization"""
    service = AgentService(config=agent_config)
    
    assert service.config == agent_config
    assert service._api_key == "test_key_12345"
    assert service._agent is None  # Lazy loading


@pytest.mark.unit
def test_agent_service_init_without_api_key(mock_env_without_key, agent_config):
    """Test agent service initialization fails without API key"""
    with pytest.raises(ValueError, match="GROQ_API_KEY not found"):
        AgentService(config=agent_config)


@pytest.mark.unit
def test_agent_service_init_with_defaults(mock_env_with_key):
    """Test agent service initialization with default config"""
    service = AgentService()
    
    assert isinstance(service.config, AgentConfig)
    assert service.config.model == "groq:llama-3.1-70b-versatile"


# Status Tests

@pytest.mark.unit
def test_get_status_not_initialized(agent_service):
    """Test status when agent not yet initialized"""
    status = agent_service.get_status()
    
    assert status["service"] == "AI Agent (Pydantic AI + Groq)"
    assert status["model"] == "groq:llama-3.1-70b-versatile"
    assert status["api_key_configured"] is True
    assert status["agent_initialized"] is False
    assert status["ready"] is True


@pytest.mark.unit
def test_get_status_after_initialization(agent_service):
    """Test status after agent initialization"""
    # Mock agent creation
    with patch('modules.ai_assistant.backend.agent_service.Agent') as mock_agent:
        mock_agent.return_value = MagicMock()
        agent_service._get_agent()
    
    status = agent_service.get_status()
    
    assert status["agent_initialized"] is True
    assert status["ready"] is True


# Query Tests

@pytest.mark.unit
def test_query_success(agent_service):
    """Test successful query execution"""
    # Mock the agent and its response
    mock_result = MagicMock()
    mock_result.data = "This is a test response from the AI agent."
    
    with patch('modules.ai_assistant.backend.agent_service.Agent') as mock_agent_class:
        mock_agent_instance = MagicMock()
        mock_agent_instance.run_sync.return_value = mock_result
        mock_agent_class.return_value = mock_agent_instance
        
        result = agent_service.query("Test prompt")
    
    assert result["success"] is True
    assert result["response"] == "This is a test response from the AI agent."
    assert result["tokens_used"] > 0
    assert result["error"] is None
    assert result["context_used"] == {}


@pytest.mark.unit
def test_query_with_context(agent_service):
    """Test query with context data"""
    context = {
        "data_products": ["Product1", "Product2"],
        "current_schema": "test_schema"
    }
    
    mock_result = MagicMock()
    mock_result.data = "Response with context"
    
    with patch('modules.ai_assistant.backend.agent_service.Agent') as mock_agent_class:
        mock_agent_instance = MagicMock()
        mock_agent_instance.run_sync.return_value = mock_result
        mock_agent_class.return_value = mock_agent_instance
        
        result = agent_service.query("Test prompt", context=context)
    
    assert result["success"] is True
    assert result["context_used"] == context
    
    # Verify context was included in prompt
    call_args = mock_agent_instance.run_sync.call_args[0][0]
    assert "Product1" in call_args
    assert "test_schema" in call_args


@pytest.mark.unit
def test_query_error_handling(agent_service):
    """Test query error handling"""
    with patch('modules.ai_assistant.backend.agent_service.Agent') as mock_agent_class:
        mock_agent_instance = MagicMock()
        mock_agent_instance.run_sync.side_effect = Exception("Test error")
        mock_agent_class.return_value = mock_agent_instance
        
        result = agent_service.query("Test prompt")
    
    assert result["success"] is False
    assert result["response"] is None
    assert result["tokens_used"] == 0
    assert "Test error" in result["error"]


# Context Building Tests

@pytest.mark.unit
def test_build_prompt_with_context_empty(agent_service):
    """Test prompt building with no context"""
    prompt = "Simple question"
    result = agent_service._build_prompt_with_context(prompt, None)
    
    assert result == prompt


@pytest.mark.unit
def test_build_prompt_with_context_data_products(agent_service):
    """Test prompt building with data products context"""
    prompt = "Question about products"
    context = {"data_products": ["Product1", "Product2"]}
    
    result = agent_service._build_prompt_with_context(prompt, context)
    
    assert "Available Data Products: Product1, Product2" in result
    assert "Question: " + prompt in result


@pytest.mark.unit
def test_build_prompt_with_context_multiple_fields(agent_service):
    """Test prompt building with multiple context fields"""
    prompt = "Complex question"
    context = {
        "data_products": ["Product1"],
        "current_schema": "test_schema",
        "custom_field": "custom_value"
    }
    
    result = agent_service._build_prompt_with_context(prompt, context)
    
    assert "Available Data Products: Product1" in result
    assert "Current Schema: test_schema" in result
    assert "custom_field: custom_value" in result
    assert "Question: " + prompt in result


# Data Product Analysis Tests

@pytest.mark.unit
def test_analyze_data_product_basic(agent_service):
    """Test basic data product analysis"""
    mock_result = MagicMock()
    mock_result.data = "Analysis of SupplierInvoice"
    
    with patch('modules.ai_assistant.backend.agent_service.Agent') as mock_agent_class:
        mock_agent_instance = MagicMock()
        mock_agent_instance.run_sync.return_value = mock_result
        mock_agent_class.return_value = mock_agent_instance
        
        result = agent_service.analyze_data_product("SupplierInvoice")
    
    assert result["success"] is True
    assert "SupplierInvoice" in result["context_used"]["data_product"]


@pytest.mark.unit
def test_analyze_data_product_with_question(agent_service):
    """Test data product analysis with specific question"""
    mock_result = MagicMock()
    mock_result.data = "Specific analysis"
    
    schema_info = {"fields": ["field1", "field2"]}
    
    with patch('modules.ai_assistant.backend.agent_service.Agent') as mock_agent_class:
        mock_agent_instance = MagicMock()
        mock_agent_instance.run_sync.return_value = mock_result
        mock_agent_class.return_value = mock_agent_instance
        
        result = agent_service.analyze_data_product(
            "SupplierInvoice",
            schema_info=schema_info,
            question="What are the key fields?"
        )
    
    assert result["success"] is True
    assert result["context_used"]["schema"] == schema_info


# SQL Generation Tests

@pytest.mark.unit
def test_generate_sql_basic(agent_service):
    """Test basic SQL generation"""
    mock_result = MagicMock()
    mock_result.data = "SELECT * FROM invoices WHERE date > '2023-01-01'"
    
    with patch('modules.ai_assistant.backend.agent_service.Agent') as mock_agent_class:
        mock_agent_instance = MagicMock()
        mock_agent_instance.run_sync.return_value = mock_result
        mock_agent_class.return_value = mock_agent_instance
        
        result = agent_service.generate_sql("Get all invoices from last year")
    
    assert result["success"] is True
    assert "SELECT" in result["response"]


@pytest.mark.unit
def test_generate_sql_with_schema(agent_service):
    """Test SQL generation with schema information"""
    mock_result = MagicMock()
    mock_result.data = "SELECT invoice_id, amount FROM invoices"
    
    table_schema = {
        "invoices": {
            "columns": ["invoice_id", "amount", "date"]
        }
    }
    
    with patch('modules.ai_assistant.backend.agent_service.Agent') as mock_agent_class:
        mock_agent_instance = MagicMock()
        mock_agent_instance.run_sync.return_value = mock_result
        mock_agent_class.return_value = mock_agent_instance
        
        result = agent_service.generate_sql(
            "Get invoice IDs and amounts",
            table_schema=table_schema
        )
    
    assert result["success"] is True
    assert result["context_used"]["schema"] == table_schema


# Configuration Update Tests

@pytest.mark.unit
def test_update_config_model(agent_service):
    """Test updating model configuration"""
    original_model = agent_service.config.model
    
    agent_service.update_config(model="groq:mixtral-8x7b")
    
    assert agent_service.config.model == "groq:mixtral-8x7b"
    assert agent_service.config.model != original_model
    assert agent_service._agent is None  # Agent reset


@pytest.mark.unit
def test_update_config_multiple_params(agent_service):
    """Test updating multiple configuration parameters"""
    agent_service.update_config(
        temperature=0.5,
        max_tokens=2000,
        system_prompt="Updated prompt"
    )
    
    assert agent_service.config.temperature == 0.5
    assert agent_service.config.max_tokens == 2000
    assert agent_service.config.system_prompt == "Updated prompt"


@pytest.mark.unit
def test_update_config_invalid_param(agent_service):
    """Test updating with invalid parameter (should be ignored)"""
    original_config = agent_service.config
    
    agent_service.update_config(invalid_param="value")
    
    # Config should remain unchanged
    assert agent_service.config == original_config


# Edge Cases

@pytest.mark.unit
def test_query_empty_prompt(agent_service):
    """Test query with empty prompt"""
    mock_result = MagicMock()
    mock_result.data = "Empty response"
    
    with patch('modules.ai_assistant.backend.agent_service.Agent') as mock_agent_class:
        mock_agent_instance = MagicMock()
        mock_agent_instance.run_sync.return_value = mock_result
        mock_agent_class.return_value = mock_agent_instance
        
        result = agent_service.query("")
    
    # Should still work (Groq handles empty prompts)
    assert result["success"] is True


@pytest.mark.unit
def test_query_very_long_prompt(agent_service):
    """Test query with very long prompt"""
    long_prompt = "Test " * 1000  # 5000 characters
    
    mock_result = MagicMock()
    mock_result.data = "Response to long prompt"
    
    with patch('modules.ai_assistant.backend.agent_service.Agent') as mock_agent_class:
        mock_agent_instance = MagicMock()
        mock_agent_instance.run_sync.return_value = mock_result
        mock_agent_class.return_value = mock_agent_instance
        
        result = agent_service.query(long_prompt)
    
    assert result["success"] is True
    assert result["tokens_used"] > 1000  # Long prompt → many tokens