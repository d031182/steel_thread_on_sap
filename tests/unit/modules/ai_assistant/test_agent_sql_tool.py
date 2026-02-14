"""
Unit tests for AI Agent SQL execution tool

Tests the execute_sql_impl tool integration with JouleAgent
"""

import pytest
from unittest.mock import MagicMock, patch
from modules.ai_assistant.backend.services.agent_service import (
    JouleAgent,
    AgentDependencies,
    get_sql_execution_service
)


@pytest.mark.unit
@pytest.mark.fast
class TestAgentSQLTool:
    """Test SQL execution tool in agent context"""
    
    def test_sql_execution_service_singleton(self):
        """
        Test: SQL execution service singleton is initialized correctly
        
        ARRANGE/ACT
        """
        service = get_sql_execution_service()
        
        # ASSERT
        assert service is not None
        assert hasattr(service, 'execute_query')
        
        # Singleton behavior
        service2 = get_sql_execution_service()
        assert service is service2
    
    def test_agent_system_prompt_mentions_sql_capability(self):
        """
        Test: System prompts mention SQL execution capability
        
        ARRANGE/ACT
        """
        with patch('modules.ai_assistant.backend.services.agent_service.get_sql_execution_service'), \
             patch.dict('os.environ', {'GROQ_API_KEY': 'test-key'}):
            agent = JouleAgent()
            structured_prompt = agent._get_system_prompt()
            streaming_prompt = agent._get_streaming_prompt()
        
        # ASSERT
        assert "SQL" in structured_prompt or "sql" in structured_prompt.lower()
        assert "SQL" in streaming_prompt or "sql" in streaming_prompt.lower()
        assert "Execute SQL queries" in structured_prompt or "execute sql" in structured_prompt.lower()
        assert "Execute SQL queries" in streaming_prompt or "execute sql" in streaming_prompt.lower()


@pytest.mark.unit
@pytest.mark.fast
class TestAgentDependenciesWithSQL:
    """Test AgentDependencies dataclass includes SQL service"""
    
    def test_agent_dependencies_has_sql_service_field(self):
        """
        Test: AgentDependencies includes sql_execution_service
        
        ARRANGE/ACT
        """
        deps = AgentDependencies(
            datasource="p2p_data",
            data_product_service=MagicMock(),
            sql_execution_service=MagicMock(),
            conversation_context={}
        )
        
        # ASSERT
        assert hasattr(deps, 'sql_execution_service')
        assert deps.sql_execution_service is not None
    
    def test_get_sql_execution_service_creates_instance(self):
        """
        Test: get_sql_execution_service creates SQLExecutionService with correct db_path
        
        ARRANGE/ACT
        """
        service = get_sql_execution_service()
        
        # ASSERT
        assert service is not None
        assert str(service.db_path) == "database"
        assert hasattr(service, 'execute_query')
        assert hasattr(service, 'validator')
