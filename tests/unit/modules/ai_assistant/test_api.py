"""
Unit Tests for AI Assistant v2 API

Tests the Flask Blueprint and mock responses
"""

import pytest
import json
from modules.ai_assistant.backend.api import blueprint


@pytest.mark.unit
@pytest.mark.fast
def test_chat_endpoint_requires_message(client):
    """
    Test: Chat endpoint returns error when message is missing
    
    ARRANGE
    """
    # ACT
    response = client.post('/api/ai-assistant/chat', 
                          json={},
                          content_type='application/json')
    
    # ASSERT
    assert response.status_code == 400
    data = json.loads(response.data)
    assert data['success'] is False
    assert 'message' in data['error'].lower()


@pytest.mark.unit
@pytest.mark.fast
def test_chat_endpoint_accepts_valid_message(client):
    """
    Test: Chat endpoint accepts valid message and returns response
    
    ARRANGE
    """
    payload = {
        "message": "What suppliers do we have?",
        "context": {"datasource": "p2p_data"}
    }
    
    # ACT
    response = client.post('/api/ai-assistant/chat',
                          json=payload,
                          content_type='application/json')
    
    # ASSERT
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['success'] is True
    assert 'response' in data
    assert 'message' in data['response']
    assert 'conversation_id' in data
    assert 'timestamp' in data


@pytest.mark.unit
@pytest.mark.fast
def test_chat_response_structure(client):
    """
    Test: Chat response has correct Pydantic-style structure
    
    ARRANGE
    """
    payload = {"message": "Test message"}
    
    # ACT
    response = client.post('/api/ai-assistant/chat',
                          json=payload,
                          content_type='application/json')
    
    # ASSERT
    data = json.loads(response.data)
    ai_response = data['response']
    
    # Check all required fields
    assert 'message' in ai_response
    assert 'confidence' in ai_response
    assert 'sources' in ai_response
    assert 'requires_clarification' in ai_response
    
    # Check data types
    assert isinstance(ai_response['message'], str)
    assert isinstance(ai_response['confidence'], (int, float))
    assert isinstance(ai_response['sources'], list)
    assert isinstance(ai_response['requires_clarification'], bool)
    
    # Check confidence range
    assert 0.0 <= ai_response['confidence'] <= 1.0


@pytest.mark.unit
@pytest.mark.fast
def test_conversation_persistence(client):
    """
    Test: Conversation ID persists across multiple messages
    
    ARRANGE
    """
    # First message
    response1 = client.post('/api/ai-assistant/chat',
                           json={"message": "First message"},
                           content_type='application/json')
    data1 = json.loads(response1.data)
    conversation_id = data1['conversation_id']
    
    # ACT
    # Second message with same conversation_id
    response2 = client.post('/api/ai-assistant/chat',
                           json={
                               "message": "Second message",
                               "conversation_id": conversation_id
                           },
                           content_type='application/json')
    
    # ASSERT
    data2 = json.loads(response2.data)
    assert data2['conversation_id'] == conversation_id
    assert data2['success'] is True


@pytest.mark.unit
@pytest.mark.fast
def test_health_endpoint(client):
    """
    Test: Health endpoint returns status
    
    ARRANGE/ACT
    """
    response = client.get('/api/ai-assistant/health')
    
    # ASSERT
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['status'] == 'healthy'
    assert 'version' in data
    assert 'phase' in data


@pytest.fixture
def client():
    """Create test client with AI Assistant blueprint"""
    from flask import Flask
    app = Flask(__name__)
    app.register_blueprint(blueprint, url_prefix='/api/ai-assistant')
    app.config['TESTING'] = True
    
    with app.test_client() as client:
        yield client