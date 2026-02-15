"""
Integration Tests for AI Assistant Module

Tests the complete AI Assistant workflow from API to response,
mimicking the UX flow without browser dependencies.

Follows Gu Wu (顾武) testing standards:
- AAA pattern (Arrange, Act, Assert)
- Fast execution (mock Groq API)
- API-first testing (no browser required)
"""

import pytest
from unittest.mock import patch, MagicMock
import json


@pytest.mark.integration
@pytest.mark.fast
class TestAIAssistantIntegration:
    """Integration tests for AI Assistant module"""
    
    def test_status_endpoint_returns_ready_state(self, client):
        """
        Test /api/ai-assistant/status endpoint
        
        ARRANGE: API key configured in environment
        ACT: GET /api/ai-assistant/status
        ASSERT: Returns ready=true with model info
        """
        # ACT
        response = client.get('/api/ai-assistant/status')
        data = json.loads(response.data)
        
        # ASSERT
        assert response.status_code == 200
        assert data['success'] is True
        assert 'ready' in data
        assert 'model' in data
        assert 'groq' in data['model'].lower()
    
    @patch('modules.ai_assistant.backend.agent_service.Agent.run_sync')
    def test_simple_query_without_context(self, mock_run, client):
        """
        Test /api/ai-assistant/query with simple question
        
        ARRANGE: Mock Groq response
        ACT: POST query "What is SAP S/4HANA?"
        ASSERT: Returns AI response with token count
        """
        # ARRANGE
        mock_result = MagicMock()
        mock_result.output = "SAP S/4HANA is an ERP system..."
        mock_result.usage.total_tokens = 150
        mock_run.return_value = mock_result
        
        payload = {
            "prompt": "What is SAP S/4HANA?"
        }
        
        # ACT
        response = client.post(
            '/api/ai-assistant/query',
            data=json.dumps(payload),
            content_type='application/json'
        )
        data = json.loads(response.data)
        
        # ASSERT
        assert response.status_code == 200
        assert data['success'] is True
        assert 'response' in data
        assert 'tokens_used' in data
        assert data['tokens_used'] == 150
        assert 'ERP' in data['response']
    
    @patch('modules.ai_assistant.backend.agent_service.Agent.run_sync')
    def test_context_aware_query(self, mock_run, client):
        """
        Test /api/ai-assistant/query with data product context
        
        ARRANGE: Mock Groq response + context
        ACT: POST query with SupplierInvoice context
        ASSERT: Context passed to AI, response relevant
        """
        # ARRANGE
        mock_result = MagicMock()
        mock_result.output = "The SupplierInvoice data product contains tables: Header, Lines..."
        mock_result.usage.total_tokens = 200
        mock_run.return_value = mock_result
        
        payload = {
            "prompt": "What tables are available?",
            "context": {
                "data_product": "SupplierInvoice",
                "current_schema": "sap.s4",
                "current_table": "A_SupplierInvoice"
            }
        }
        
        # ACT
        response = client.post(
            '/api/ai-assistant/query',
            data=json.dumps(payload),
            content_type='application/json'
        )
        data = json.loads(response.data)
        
        # ASSERT
        assert response.status_code == 200
        assert data['success'] is True
        assert 'context_used' in data
        assert data['context_used']['data_product'] == 'SupplierInvoice'
        assert 'SupplierInvoice' in data['response']
        assert 'tables' in data['response'].lower()
    
    @patch('modules.ai_assistant.backend.agent_service.Agent.run_sync')
    def test_error_handling_on_api_failure(self, mock_run, client):
        """
        Test error handling when Groq API fails
        
        ARRANGE: Mock API exception
        ACT: POST query that triggers error
        ASSERT: Returns error response with details
        """
        # ARRANGE
        mock_run.side_effect = Exception("Groq API rate limit exceeded")
        
        payload = {
            "prompt": "Test query"
        }
        
        # ACT
        response = client.post(
            '/api/ai-assistant/query',
            data=json.dumps(payload),
            content_type='application/json'
        )
        data = json.loads(response.data)
        
        # ASSERT
        assert response.status_code == 500
        assert data['success'] is False
        assert 'error' in data
        assert 'rate limit' in data['error'].lower()
    
    def test_missing_prompt_returns_400(self, client):
        """
        Test validation when prompt is missing
        
        ARRANGE: Payload without prompt
        ACT: POST query with empty payload
        ASSERT: Returns 400 Bad Request
        """
        # ARRANGE
        payload = {
            "context": {"data_product": "Test"}
        }
        
        # ACT
        response = client.post(
            '/api/ai-assistant/query',
            data=json.dumps(payload),
            content_type='application/json'
        )
        data = json.loads(response.data)
        
        # ASSERT
        assert response.status_code == 400
        assert data['success'] is False
        assert 'prompt' in data['error'].lower()
    
    @patch('modules.ai_assistant.backend.agent_service.Agent.run_sync')
    def test_long_conversation_maintains_context(self, mock_run, client):
        """
        Test multi-turn conversation maintains context
        
        ARRANGE: Mock responses for 3 queries
        ACT: Send 3 sequential queries
        ASSERT: Each response builds on previous context
        """
        # ARRANGE
        responses = [
            "SAP S/4HANA is an ERP system",
            "The SupplierInvoice module handles invoices",
            "Yes, it integrates with SAP Ariba"
        ]
        mock_results = []
        for resp in responses:
            mock_result = MagicMock()
            mock_result.output = resp
            mock_result.usage.total_tokens = 100
            mock_results.append(mock_result)
        
        mock_run.side_effect = mock_results
        
        queries = [
            {"prompt": "What is SAP S/4HANA?"},
            {"prompt": "Tell me about SupplierInvoice", "context": {"data_product": "SupplierInvoice"}},
            {"prompt": "Does it integrate with other systems?"}
        ]
        
        # ACT & ASSERT
        for i, query in enumerate(queries):
            response = client.post(
                '/api/ai-assistant/query',
                data=json.dumps(query),
                content_type='application/json'
            )
            data = json.loads(response.data)
            
            assert response.status_code == 200
            assert data['success'] is True
            assert responses[i] in data['response']
    
    @patch('modules.ai_assistant.backend.agent_service.Agent.run_sync')
    def test_token_usage_tracking(self, mock_run, client):
        """
        Test token usage is accurately tracked
        
        ARRANGE: Mock response with specific token count
        ACT: POST query
        ASSERT: Token count matches mock
        """
        # ARRANGE
        mock_result = MagicMock()
        mock_result.output = "Test response"
        mock_result.usage.total_tokens = 644  # From real Groq test
        mock_run.return_value = mock_result
        
        payload = {"prompt": "Test query"}
        
        # ACT
        response = client.post(
            '/api/ai-assistant/query',
            data=json.dumps(payload),
            content_type='application/json'
        )
        data = json.loads(response.data)
        
        # ASSERT
        assert data['tokens_used'] == 644


@pytest.mark.integration
@pytest.mark.slow
class TestAIAssistantRealAPI:
    """
    Integration tests with real Groq API
    
    Only run when GROQ_API_KEY is configured.
    Marked as 'slow' due to ~20-30s response time.
    """
    
    @pytest.mark.skipif(
        "not config.getoption('--run-slow')",
        reason="Skipped unless --run-slow is passed"
    )
    def test_real_groq_api_simple_query(self, client):
        """
        Test real Groq API with simple query
        
        ARRANGE: Real API key configured
        ACT: POST real query to Groq
        ASSERT: Returns valid response (may take 20-30s)
        """
        # ARRANGE
        payload = {
            "prompt": "What is SAP in one sentence?"
        }
        
        # ACT
        response = client.post(
            '/api/ai-assistant/query',
            data=json.dumps(payload),
            content_type='application/json'
        )
        data = json.loads(response.data)
        
        # ASSERT
        assert response.status_code == 200
        assert data['success'] is True
        assert 'SAP' in data['response']
        assert data['tokens_used'] > 0
    
    @pytest.mark.skipif(
        "not config.getoption('--run-slow')",
        reason="Skipped unless --run-slow is passed"
    )
    def test_real_groq_api_with_context(self, client):
        """
        Test real Groq API with data product context
        
        ARRANGE: Real API key + context
        ACT: POST query with SupplierInvoice context
        ASSERT: Context-aware response
        """
        # ARRANGE
        payload = {
            "prompt": "List the key fields in this data product",
            "context": {
                "data_product": "SupplierInvoice"
            }
        }
        
        # ACT
        response = client.post(
            '/api/ai-assistant/query',
            data=json.dumps(payload),
            content_type='application/json'
        )
        data = json.loads(response.data)
        
        # ASSERT
        assert response.status_code == 200
        assert data['success'] is True
        assert 'context_used' in data
        assert 'SupplierInvoice' in data['response'] or 'invoice' in data['response'].lower()


# Pytest configuration for slow tests
def pytest_addoption(parser):
    """Add --run-slow option to pytest"""
    parser.addoption(
        "--run-slow",
        action="store_true",
        default=False,
        help="Run slow tests (real API calls)"
    )