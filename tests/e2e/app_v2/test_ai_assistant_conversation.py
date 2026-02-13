"""
E2E tests for AI Assistant Phase 2b: Multi-turn conversation frontend integration

Tests conversation management via frontend-to-backend flow
"""
import pytest
import json
import time


@pytest.mark.e2e
@pytest.mark.app_v2
def test_conversation_creation_and_messaging():
    """
    Test: Create conversation and send messages via API
    
    ARRANGE: Import requests for API testing
    ACT: Create conversation, send messages, get history
    ASSERT: Conversation persists, messages stored correctly
    """
    import requests
    
    # ARRANGE
    base_url = "http://localhost:5000/api/ai-assistant"
    
    # ACT 1: Create conversation
    create_response = requests.post(
        f"{base_url}/conversations",
        json={"context": {"datasource": "p2p_data"}},
        timeout=5
    )
    
    # ASSERT 1: Conversation created successfully
    assert create_response.status_code == 201
    create_data = create_response.json()
    assert create_data["success"] is True
    assert "conversation_id" in create_data
    conversation_id = create_data["conversation_id"]
    
    # ACT 2: Send first message
    msg1_response = requests.post(
        f"{base_url}/conversations/{conversation_id}/messages",
        json={"message": "What is P2P data?"},
        timeout=5
    )
    
    # ASSERT 2: First message sent successfully
    assert msg1_response.status_code == 200
    msg1_data = msg1_response.json()
    assert msg1_data["success"] is True
    assert "response" in msg1_data
    assert msg1_data["response"]["message"]  # AI responded
    
    # Wait briefly to ensure message processing
    time.sleep(0.1)
    
    # ACT 3: Send second message (multi-turn)
    msg2_response = requests.post(
        f"{base_url}/conversations/{conversation_id}/messages",
        json={"message": "Tell me more"},
        timeout=5
    )
    
    # ASSERT 3: Second message sent successfully
    assert msg2_response.status_code == 200
    msg2_data = msg2_response.json()
    assert msg2_data["success"] is True
    
    # ACT 4: Get conversation history
    history_response = requests.get(
        f"{base_url}/conversations/{conversation_id}",
        timeout=5
    )
    
    # ASSERT 4: History contains all messages
    assert history_response.status_code == 200
    history_data = history_response.json()
    assert history_data["success"] is True
    assert "conversation" in history_data
    
    conversation = history_data["conversation"]
    assert conversation["id"] == conversation_id
    assert len(conversation["messages"]) == 4  # 2 user + 2 assistant
    
    # ASSERT 5: Message roles correct
    messages = conversation["messages"]
    assert messages[0]["role"] == "user"
    assert messages[1]["role"] == "assistant"
    assert messages[2]["role"] == "user"
    assert messages[3]["role"] == "assistant"


@pytest.mark.e2e
@pytest.mark.app_v2
def test_conversation_deletion():
    """
    Test: Delete conversation via API
    
    ARRANGE: Create conversation
    ACT: Delete conversation
    ASSERT: Conversation no longer accessible
    """
    import requests
    
    # ARRANGE: Create conversation
    base_url = "http://localhost:5000/api/ai-assistant"
    create_response = requests.post(
        f"{base_url}/conversations",
        json={"context": {}},
        timeout=5
    )
    conversation_id = create_response.json()["conversation_id"]
    
    # ACT: Delete conversation
    delete_response = requests.delete(
        f"{base_url}/conversations/{conversation_id}",
        timeout=5
    )
    
    # ASSERT 1: Deletion successful
    assert delete_response.status_code == 200
    delete_data = delete_response.json()
    assert delete_data["success"] is True
    
    # ASSERT 2: Conversation no longer accessible
    get_response = requests.get(
        f"{base_url}/conversations/{conversation_id}",
        timeout=5
    )
    assert get_response.status_code == 404  # Not found


@pytest.mark.e2e
@pytest.mark.app_v2
def test_conversation_context_retrieval():
    """
    Test: Get conversation context via API
    
    ARRANGE: Create conversation with context
    ACT: Retrieve conversation context
    ASSERT: Context matches initial context
    """
    import requests
    
    # ARRANGE: Create conversation with specific context
    base_url = "http://localhost:5000/api/ai-assistant"
    initial_context = {
        "datasource": "p2p_data",
        "data_product": "SupplierInvoice",
        "schema": "sap_s4com_supplierinvoice_v1"
    }
    
    create_response = requests.post(
        f"{base_url}/conversations",
        json={"context": initial_context},
        timeout=5
    )
    conversation_id = create_response.json()["conversation_id"]
    
    # ACT: Get conversation context
    context_response = requests.get(
        f"{base_url}/conversations/{conversation_id}/context",
        timeout=5
    )
    
    # ASSERT: Context matches initial context
    assert context_response.status_code == 200
    context_data = context_response.json()
    assert context_data["success"] is True
    assert "context" in context_data
    
    retrieved_context = context_data["context"]
    assert retrieved_context["datasource"] == initial_context["datasource"]
    assert retrieved_context["data_product"] == initial_context["data_product"]
    assert retrieved_context["schema"] == initial_context["schema"]


@pytest.mark.e2e
@pytest.mark.app_v2
def test_multiple_conversations_isolation():
    """
    Test: Multiple conversations remain isolated
    
    ARRANGE: Create two separate conversations
    ACT: Send different messages to each
    ASSERT: Conversations remain independent
    """
    import requests
    
    # ARRANGE: Create two conversations
    base_url = "http://localhost:5000/api/ai-assistant"
    
    conv1_response = requests.post(
        f"{base_url}/conversations",
        json={"context": {"datasource": "p2p_data"}},
        timeout=5
    )
    conv1_id = conv1_response.json()["conversation_id"]
    
    conv2_response = requests.post(
        f"{base_url}/conversations",
        json={"context": {"datasource": "knowledge_graph"}},
        timeout=5
    )
    conv2_id = conv2_response.json()["conversation_id"]
    
    # ACT: Send messages to each conversation
    requests.post(
        f"{base_url}/conversations/{conv1_id}/messages",
        json={"message": "Message for conversation 1"},
        timeout=5
    )
    
    requests.post(
        f"{base_url}/conversations/{conv2_id}/messages",
        json={"message": "Message for conversation 2"},
        timeout=5
    )
    
    # ASSERT: Conversations remain isolated
    conv1_history = requests.get(f"{base_url}/conversations/{conv1_id}", timeout=5).json()
    conv2_history = requests.get(f"{base_url}/conversations/{conv2_id}", timeout=5).json()
    
    # Each conversation should have exactly 2 messages (1 user + 1 assistant)
    assert len(conv1_history["conversation"]["messages"]) == 2
    assert len(conv2_history["conversation"]["messages"]) == 2
    
    # Verify messages are different
    conv1_user_msg = conv1_history["conversation"]["messages"][0]["content"]
    conv2_user_msg = conv2_history["conversation"]["messages"][0]["content"]
    
    assert conv1_user_msg == "Message for conversation 1"
    assert conv2_user_msg == "Message for conversation 2"
    assert conv1_user_msg != conv2_user_msg