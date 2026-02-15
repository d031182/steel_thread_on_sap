"""
AI Assistant Frontend API Contract Tests
=========================================
Tests for AI Assistant frontend API endpoints (metadata, configuration).

Following Gu Wu standards + API-First Contract Testing (HIGH-20):
- AAA pattern (Arrange, Act, Assert)
- pytest markers
- API contract validation
- Tests run via requests (< 1 second)
"""

import pytest
import requests


class TestAIAssistantFrontendAPI:
    """Test AI Assistant frontend metadata API"""
    
    @pytest.mark.e2e
    @pytest.mark.api_contract
    def test_module_metadata_endpoint_exists(self):
        """
        Test: /api/modules/frontend-registry returns AI Assistant metadata
        
        Frontend Dependency: AIAssistantAdapter.getModuleMetadata()
        
        Contract:
        - Must return 200 status
        - Must have 'success' field
        - Must have 'modules' array
        
        ARRANGE
        """
        url = "http://localhost:5000/api/modules/frontend-registry"
        
        # ACT
        try:
            response = requests.get(url, timeout=5)
        except requests.ConnectionError:
            pytest.skip("Server not running - skipping API test")
        
        # ASSERT
        assert response.status_code == 200
        data = response.json()
        assert 'success' in data
        assert data['success'] is True
        assert 'modules' in data
        assert isinstance(data['modules'], list)
    
    @pytest.mark.e2e
    @pytest.mark.api_contract
    def test_ai_assistant_module_in_registry(self):
        """
        Test: AI Assistant module is present in frontend registry
        
        Frontend Dependency: Module bootstrap process
        
        Contract:
        - AI Assistant must be in modules list
        - Must have required metadata fields
        
        ARRANGE
        """
        url = "http://localhost:5000/api/modules/frontend-registry"
        
        # ACT
        try:
            response = requests.get(url, timeout=5)
        except requests.ConnectionError:
            pytest.skip("Server not running - skipping API test")
        
        # ASSERT
        data = response.json()
        modules = data.get('modules', [])
        
        ai_assistant = next(
            (m for m in modules if m.get('id') == 'ai_assistant'),
            None
        )
        
        assert ai_assistant is not None, "AI Assistant module not found in registry"
        assert 'name' in ai_assistant
        assert 'version' in ai_assistant
        assert 'id' in ai_assistant
        assert ai_assistant['id'] == 'ai_assistant'
    
    @pytest.mark.e2e
    @pytest.mark.api_contract
    def test_conversations_list_endpoint(self):
        """
        Test: /api/ai-assistant/conversations returns conversation list
        
        Frontend Dependency: AIAssistantAdapter.loadConversations()
        
        Contract:
        - Must return 200 status
        - Must have 'success' field
        - Must have 'conversations' array
        
        ARRANGE
        """
        url = "http://localhost:5000/api/ai-assistant/conversations"
        
        # ACT
        try:
            response = requests.get(url, timeout=5)
        except requests.ConnectionError:
            pytest.skip("Server not running - skipping API test")
        
        # ASSERT
        assert response.status_code == 200
        data = response.json()
        assert 'success' in data
        assert 'conversations' in data
        assert isinstance(data['conversations'], list)
    
    @pytest.mark.e2e
    @pytest.mark.api_contract
    def test_create_conversation_endpoint(self):
        """
        Test: POST /api/ai-assistant/conversations creates new conversation
        
        Frontend Dependency: AIAssistantAdapter.createConversation()
        
        Contract:
        - Must return 201 status
        - Must have 'success' field
        - Must have 'conversation_id' field
        
        ARRANGE
        """
        url = "http://localhost:5000/api/ai-assistant/conversations"
        
        # ACT
        try:
            response = requests.post(url, json={}, timeout=5)
        except requests.ConnectionError:
            pytest.skip("Server not running - skipping API test")
        
        # ASSERT
        assert response.status_code == 201
        data = response.json()
        assert 'success' in data
        assert data['success'] is True
        assert 'conversation_id' in data
        assert data['conversation_id'] is not None


class TestAIAssistantChatAPI:
    """Test AI Assistant chat API endpoints"""
    
    @pytest.mark.e2e
    @pytest.mark.api_contract  
    def test_chat_endpoint_structure(self):
        """
        Test: POST /api/ai-assistant/chat has correct request/response structure
        
        Frontend Dependency: AIAssistantAdapter.sendMessage()
        
        Contract:
        - Must accept conversation_id + message
        - Must return response with content
        
        ARRANGE
        """
        url = "http://localhost:5000/api/ai-assistant/chat"
        payload = {
            "conversation_id": "test-conversation-id",
            "message": "Hello"
        }
        
        # ACT
        try:
            response = requests.post(url, json=payload, timeout=10)
        except requests.ConnectionError:
            pytest.skip("Server not running - skipping API test")
        
        # ASSERT
        # Should return 404 for non-existent conversation OR 200 with response
        assert response.status_code in [200, 404]
        
        if response.status_code == 200:
            data = response.json()
            assert 'content' in data or 'response' in data


class TestAIAssistantSQLAPI:
    """Test AI Assistant SQL execution API"""
    
    @pytest.mark.e2e
    @pytest.mark.api_contract
    def test_sql_execute_endpoint_exists(self):
        """
        Test: POST /api/ai-assistant/sql/execute endpoint exists
        
        Frontend Dependency: AIAssistantAdapter.executeSQL()
        
        Contract:
        - Must accept SQL query
        - Must return results or error
        
        ARRANGE
        """
        url = "http://localhost:5000/api/ai-assistant/sql/execute"
        payload = {
            "query": "SELECT 1 as test"
        }
        
        # ACT
        try:
            response = requests.post(url, json=payload, timeout=5)
        except requests.ConnectionError:
            pytest.skip("Server not running - skipping API test")
        
        # ASSERT
        # Should return 200 or 400 (validation error) or 500 (execution error)
        assert response.status_code in [200, 400, 500]
        
        data = response.json()
        # Must have either success indicator or error message
        assert 'success' in data or 'error' in data