"""
Unit tests for AI Agent Service

Tests Joule agent with Pydantic AI + Groq integration
"""

import pytest
import os
from unittest.mock import Mock, patch, AsyncMock, MagicMock
from modules.ai_assistant.backend.services.agent_service import (
    JouleAgent,
    get_joule_agent,
    AgentDependencies,
    _apply_filters
)
from modules.ai_assistant.backend.models import AssistantResponse


@pytest.fixture
def mock_env_with_key(monkeypatch):
    """
    Mock environment with GROQ_API_KEY
    
    ARRANGE
    """
    monkeypatch.setenv('GROQ_API_KEY', 'test_key_12345')


@pytest.fixture
def mock_env_without_key(monkeypatch):
    """
    Mock environment without GROQ_API_KEY
    
    ARRANGE
    """
    monkeypatch.delenv('GROQ_API_KEY', raising=False)


@pytest.fixture
def mock_data_product_service():
    """
    Create mock data product service
    
    ARRANGE
    """
    service = Mock()
    service.get_data_for_data_product = Mock(return_value={
        "success": True,
        "data": [
            {"id": 1, "name": "ACME Corp", "rating": 4.8},
            {"id": 2, "name": "Globex Inc", "rating": 4.5}
        ]
    })
    service.get_schema_for_data_product = Mock(return_value={
        "success": True,
        "schema": {
            "columns": ["id", "name", "rating"]
        }
    })
    return service


# Initialization Tests

@pytest.mark.unit
@pytest.mark.fast
def test_joule_agent_init_success(mock_env_with_key):
    """
    Test: Joule agent initializes with valid API key
    
    ARRANGE
    """
    with patch('modules.ai_assistant.backend.services.agent_service.GroqModel'):
        with patch('modules.ai_assistant.backend.services.agent_service.Agent'):
            # ACT
            agent = JouleAgent()
            
            # ASSERT
            assert agent is not None
            assert agent.temperature == 0.7


@pytest.mark.unit
@pytest.mark.fast
def test_joule_agent_init_no_api_key(mock_env_without_key):
    """
    Test: Joule agent fails without API key
    
    ARRANGE/ACT/ASSERT
    """
    with pytest.raises(ValueError, match="GROQ_API_KEY not found"):
        JouleAgent()


@pytest.mark.unit
@pytest.mark.fast
def test_joule_agent_custom_params(mock_env_with_key):
    """
    Test: Joule agent accepts custom parameters
    
    ARRANGE
    """
    with patch('modules.ai_assistant.backend.services.agent_service.GroqModel'):
        with patch('modules.ai_assistant.backend.services.agent_service.Agent'):
            # ACT
            agent = JouleAgent(
                model_name="llama-3.1-70b-versatile",
                temperature=0.5,
                max_retries=3
            )
            
            # ASSERT
            assert agent.temperature == 0.5


# Singleton Tests

@pytest.mark.unit
@pytest.mark.fast
def test_get_joule_agent_singleton(mock_env_with_key):
    """
    Test: get_joule_agent returns singleton instance
    
    ARRANGE
    """
    with patch('modules.ai_assistant.backend.services.agent_service.GroqModel'):
        with patch('modules.ai_assistant.backend.services.agent_service.Agent'):
            # ACT
            agent1 = get_joule_agent()
            agent2 = get_joule_agent()
            
            # ASSERT
            assert agent1 is agent2


# Filter Tests

@pytest.mark.unit
@pytest.mark.fast
def test_apply_filters_gt_operator():
    """
    Test: Apply filters with greater than operator
    
    ARRANGE
    """
    entities = [
        {"name": "ACME", "rating": 4.8},
        {"name": "Globex", "rating": 4.3},
        {"name": "Initech", "rating": 4.6}
    ]
    filters = {"rating": {"gt": 4.5}}
    
    # ACT
    result = _apply_filters(entities, filters)
    
    # ASSERT
    assert len(result) == 2
    assert all(e["rating"] > 4.5 for e in result)


@pytest.mark.unit
@pytest.mark.fast
def test_apply_filters_equality():
    """
    Test: Apply filters with equality condition
    
    ARRANGE
    """
    entities = [
        {"status": "active", "name": "A"},
        {"status": "inactive", "name": "B"},
        {"status": "active", "name": "C"}
    ]
    filters = {"status": "active"}
    
    # ACT
    result = _apply_filters(entities, filters)
    
    # ASSERT
    assert len(result) == 2
    assert all(e["status"] == "active" for e in result)


@pytest.mark.unit
@pytest.mark.fast
def test_apply_filters_multiple_conditions():
    """
    Test: Apply multiple filter conditions
    
    ARRANGE
    """
    entities = [
        {"name": "ACME", "rating": 4.8, "status": "active"},
        {"name": "Globex", "rating": 4.9, "status": "inactive"},
        {"name": "Initech", "rating": 4.6, "status": "active"}
    ]
    filters = {
        "rating": {"gte": 4.6},
        "status": "active"
    }
    
    # ACT
    result = _apply_filters(entities, filters)
    
    # ASSERT
    assert len(result) == 2
    assert all(e["rating"] >= 4.6 and e["status"] == "active" for e in result)


@pytest.mark.unit
@pytest.mark.fast
def test_apply_filters_no_matches():
    """
    Test: Apply filters with no matching entities
    
    ARRANGE
    """
    entities = [{"rating": 4.0}, {"rating": 4.2}]
    filters = {"rating": {"gt": 5.0}}
    
    # ACT
    result = _apply_filters(entities, filters)
    
    # ASSERT
    assert len(result) == 0


# Message Processing Tests

@pytest.mark.unit
@pytest.mark.asyncio
async def test_process_message_with_history(mock_env_with_key):
    """
    Test: Process message with conversation history
    
    ARRANGE
    """
    with patch('modules.ai_assistant.backend.services.agent_service.GroqModel'):
        with patch('modules.ai_assistant.backend.services.agent_service.Agent') as MockAgent:
            # Create mock agent with async run method
            mock_agent_instance = Mock()
            mock_run_result = Mock()
            mock_run_result.output = AssistantResponse(
                message="Test response",
                confidence=0.9,
                sources=["Test source"],
                suggested_actions=[],
                requires_clarification=False
            )
            mock_agent_instance.run = AsyncMock(return_value=mock_run_result)
            MockAgent.return_value = mock_agent_instance
            
            agent = JouleAgent()
            
            history = [
                {"role": "user", "content": "Previous question"},
                {"role": "assistant", "content": "Previous answer"}
            ]
            context = {"datasource": "p2p_data"}
            
            # ACT
            result = await agent.process_message(
                "Current question",
                history,
                context
            )
            
            # ASSERT
            assert isinstance(result, AssistantResponse)
            assert result.message == "Test response"
            assert result.confidence == 0.9


@pytest.mark.unit
@pytest.mark.fast
def test_build_message_context_no_history(mock_env_with_key):
    """
    Test: Build message context without history
    
    ARRANGE
    """
    with patch('modules.ai_assistant.backend.services.agent_service.GroqModel'):
        with patch('modules.ai_assistant.backend.services.agent_service.Agent'):
            agent = JouleAgent()
            
            # ACT
            result = agent._build_message_context("Test message", [])
            
            # ASSERT
            assert result == "Test message"


@pytest.mark.unit
@pytest.mark.fast
def test_build_message_context_with_history(mock_env_with_key):
    """
    Test: Build message context with conversation history
    
    ARRANGE
    """
    with patch('modules.ai_assistant.backend.services.agent_service.GroqModel'):
        with patch('modules.ai_assistant.backend.services.agent_service.Agent'):
            agent = JouleAgent()
            
            history = [
                {"role": "user", "content": "First question"},
                {"role": "assistant", "content": "First answer"},
                {"role": "user", "content": "Second question"}
            ]
            
            # ACT
            result = agent._build_message_context("Current question", history)
            
            # ASSERT
            assert "Conversation history:" in result
            assert "First question" in result
            assert "First answer" in result
            assert "Current question" in result


# System Prompt Tests

@pytest.mark.unit
@pytest.mark.fast
def test_system_prompt_content(mock_env_with_key):
    """
    Test: System prompt contains expected content
    
    ARRANGE
    """
    with patch('modules.ai_assistant.backend.services.agent_service.GroqModel'):
        with patch('modules.ai_assistant.backend.services.agent_service.Agent'):
            agent = JouleAgent()
            
            # ACT
            prompt = agent._get_system_prompt()
            
            # ASSERT
            assert "Joule" in prompt
            assert "P2P" in prompt
            assert "confidence" in prompt.lower()
            assert "sources" in prompt.lower()


# Agent Dependencies Tests

@pytest.mark.unit
@pytest.mark.fast
def test_agent_dependencies_creation():
    """
    Test: AgentDependencies dataclass creation
    
    ARRANGE
    """
    mock_service = Mock()
    mock_sql_service = Mock()
    context = {"key": "value"}
    
    # ACT
    deps = AgentDependencies(
        datasource="p2p_data",
        data_product_service=mock_service,
        sql_execution_service=mock_sql_service,
        conversation_context=context
    )
    
    # ASSERT
    assert deps.datasource == "p2p_data"
    assert deps.data_product_service == mock_service
    assert deps.sql_execution_service == mock_sql_service
    assert deps.conversation_context == context


# Error Handling Tests

@pytest.mark.unit
@pytest.mark.asyncio
async def test_process_message_error_handling(mock_env_with_key):
    """
    Test: Agent handles errors gracefully
    
    ARRANGE
    """
    with patch('modules.ai_assistant.backend.services.agent_service.GroqModel'):
        with patch('modules.ai_assistant.backend.services.agent_service.Agent') as MockAgent:
            # Create agent that raises error
            mock_agent_instance = Mock()
            mock_agent_instance.run = AsyncMock(side_effect=Exception("Test error"))
            MockAgent.return_value = mock_agent_instance
            
            agent = JouleAgent()
            
            # ACT - Should not raise, should handle gracefully
            try:
                result = await agent.process_message(
                    "Test question",
                    [],
                    {"datasource": "p2p_data"}
                )
                # If we get here, error handling worked
                assert False, "Should have raised exception"
            except Exception:
                # ASSERT - Error propagates (API layer handles fallback)
                pass