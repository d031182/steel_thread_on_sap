"""
Unit tests for Conversation Service

Tests business logic for conversation management
"""

import pytest

from modules.ai_assistant.backend.models import (
    ConversationContext,
    MessageRole,
    AssistantResponse,
    SuggestedAction
)
from modules.ai_assistant.backend.services import ConversationService
from modules.ai_assistant.backend.repositories import get_conversation_repository


@pytest.fixture
def service():
    """
    Create fresh service for each test
    
    ARRANGE
    """
    # Clear repository before each test
    repo = get_conversation_repository()
    repo.clear_all()
    
    return ConversationService(max_context_messages=10)


@pytest.mark.unit
@pytest.mark.fast
def test_create_conversation_succeeds(service):
    """
    Test: Service creates new conversation
    
    ARRANGE
    """
    context = ConversationContext(datasource="test_db")
    
    # ACT
    session = service.create_conversation(context)
    
    # ASSERT
    assert session is not None
    assert session.id is not None
    assert session.context.datasource == "test_db"


@pytest.mark.unit
@pytest.mark.fast
def test_get_conversation_returns_existing(service):
    """
    Test: Service retrieves existing conversation
    
    ARRANGE
    """
    session = service.create_conversation()
    conversation_id = session.id
    
    # ACT
    retrieved = service.get_conversation(conversation_id)
    
    # ASSERT
    assert retrieved is not None
    assert retrieved.id == conversation_id


@pytest.mark.unit
@pytest.mark.fast
def test_add_user_message_succeeds(service):
    """
    Test: Service adds user message to conversation
    
    ARRANGE
    """
    session = service.create_conversation()
    conversation_id = session.id
    
    # ACT
    message = service.add_user_message(conversation_id, "Test message")
    
    # ASSERT
    assert message is not None
    assert message.role == MessageRole.USER
    assert message.content == "Test message"
    
    # Verify message in session
    retrieved = service.get_conversation(conversation_id)
    assert len(retrieved.messages) == 1


@pytest.mark.unit
@pytest.mark.fast
def test_add_assistant_message_succeeds(service):
    """
    Test: Service adds assistant response with metadata
    
    ARRANGE
    """
    session = service.create_conversation()
    conversation_id = session.id
    
    response = AssistantResponse(
        message="AI response",
        confidence=0.95,
        sources=["source1"],
        suggested_actions=[SuggestedAction(text="Action", action="do_something")],
        requires_clarification=False
    )
    
    # ACT
    message = service.add_assistant_message(conversation_id, response)
    
    # ASSERT
    assert message is not None
    assert message.role == MessageRole.ASSISTANT
    assert message.content == "AI response"
    assert message.metadata is not None
    assert message.metadata["confidence"] == 0.95
    assert "source1" in message.metadata["sources"]


@pytest.mark.unit
@pytest.mark.fast
def test_update_context_succeeds(service):
    """
    Test: Service updates conversation context
    
    ARRANGE
    """
    session = service.create_conversation()
    conversation_id = session.id
    
    new_context = ConversationContext(data_product="NewProduct")
    
    # ACT
    result = service.update_context(conversation_id, new_context)
    
    # ASSERT
    assert result is True
    
    retrieved = service.get_conversation(conversation_id)
    assert retrieved.context.data_product == "NewProduct"


@pytest.mark.unit
@pytest.mark.fast
def test_delete_conversation_succeeds(service):
    """
    Test: Service deletes conversation
    
    ARRANGE
    """
    session = service.create_conversation()
    conversation_id = session.id
    
    # ACT
    result = service.delete_conversation(conversation_id)
    
    # ASSERT
    assert result is True
    assert service.get_conversation(conversation_id) is None


@pytest.mark.unit
@pytest.mark.fast
def test_get_conversation_history_returns_all_messages(service):
    """
    Test: Service returns full conversation history
    
    ARRANGE
    """
    session = service.create_conversation()
    conversation_id = session.id
    
    service.add_user_message(conversation_id, "Message 1")
    service.add_user_message(conversation_id, "Message 2")
    service.add_user_message(conversation_id, "Message 3")
    
    # ACT
    history = service.get_conversation_history(conversation_id)
    
    # ASSERT
    assert history is not None
    assert len(history) == 3
    assert history[0].content == "Message 1"
    assert history[2].content == "Message 3"


@pytest.mark.unit
@pytest.mark.fast
def test_get_conversation_history_respects_limit(service):
    """
    Test: Service respects limit parameter for history
    
    ARRANGE
    """
    session = service.create_conversation()
    conversation_id = session.id
    
    for i in range(5):
        service.add_user_message(conversation_id, f"Message {i+1}")
    
    # ACT
    history = service.get_conversation_history(conversation_id, limit=3)
    
    # ASSERT
    assert len(history) == 3
    # Should return last 3 messages
    assert history[0].content == "Message 3"
    assert history[2].content == "Message 5"


@pytest.mark.unit
@pytest.mark.fast
def test_get_context_window_returns_recent_messages(service):
    """
    Test: Service returns context window for AI
    
    ARRANGE
    """
    service_with_limit = ConversationService(max_context_messages=3)
    session = service_with_limit.create_conversation()
    conversation_id = session.id
    
    for i in range(5):
        service_with_limit.add_user_message(conversation_id, f"Message {i+1}")
    
    # ACT
    context_window = service_with_limit.get_context_window(conversation_id)
    
    # ASSERT
    assert len(context_window) == 3
    # Should return last 3 messages
    assert context_window[0].content == "Message 3"
    assert context_window[2].content == "Message 5"


@pytest.mark.unit
@pytest.mark.fast
def test_build_context_summary_includes_key_info(service):
    """
    Test: Service builds human-readable context summary
    
    ARRANGE
    """
    context = ConversationContext(
        data_product="TestProduct",
        schema="test_schema",
        table="test_table"
    )
    session = service.create_conversation(context)
    conversation_id = session.id
    
    service.add_user_message(conversation_id, "Message 1")
    service.add_user_message(conversation_id, "Message 2")
    
    # ACT
    summary = service.build_context_summary(conversation_id)
    
    # ASSERT
    assert summary is not None
    assert "Messages: 2" in summary
    assert "TestProduct" in summary
    assert "test_schema" in summary
    assert "test_table" in summary


@pytest.mark.unit
@pytest.mark.fast
def test_get_statistics_returns_correct_counts(service):
    """
    Test: Service returns accurate statistics
    
    ARRANGE
    """
    # Create 3 conversations with different message counts
    session1 = service.create_conversation()
    service.add_user_message(session1.id, "Msg 1")
    service.add_user_message(session1.id, "Msg 2")
    
    session2 = service.create_conversation()
    service.add_user_message(session2.id, "Msg 1")
    
    session3 = service.create_conversation()
    service.add_user_message(session3.id, "Msg 1")
    service.add_user_message(session3.id, "Msg 2")
    service.add_user_message(session3.id, "Msg 3")
    
    # ACT
    stats = service.get_statistics()
    
    # ASSERT
    assert stats["total_conversations"] == 3
    assert stats["total_messages"] == 6  # 2 + 1 + 3
    assert stats["avg_messages_per_conversation"] == 2.0  # 6/3


@pytest.mark.unit
@pytest.mark.fast
def test_operations_return_none_for_nonexistent_conversation(service):
    """
    Test: Service handles non-existent conversation gracefully
    
    ARRANGE/ACT/ASSERT
    """
    # All these should return None or False
    assert service.get_conversation("fake-id") is None
    assert service.add_user_message("fake-id", "test") is None
    assert service.get_conversation_history("fake-id") is None
    assert service.get_context_window("fake-id") is None
    assert service.build_context_summary("fake-id") is None
    assert service.delete_conversation("fake-id") is False