"""
Unit tests for Conversation Repository

Tests in-memory conversation storage
"""

import pytest
from datetime import datetime, timedelta

from modules.ai_assistant.backend.models import (
    ConversationSession,
    ConversationContext,
    MessageRole
)
from modules.ai_assistant.backend.repositories import (
    ConversationRepository,
    get_conversation_repository
)


@pytest.fixture
def repository():
    """
    Create fresh repository for each test
    
    ARRANGE
    """
    repo = ConversationRepository(ttl_hours=1)
    repo.clear_all()
    return repo


@pytest.mark.unit
@pytest.mark.fast
def test_create_conversation_succeeds(repository):
    """
    Test: Repository creates new conversation with unique ID
    
    ARRANGE
    """
    context = ConversationContext(datasource="test_db")
    
    # ACT
    session = repository.create(context)
    
    # ASSERT
    assert session is not None
    assert session.id is not None
    assert len(session.id) > 0
    assert session.context.datasource == "test_db"
    assert len(session.messages) == 0


@pytest.mark.unit
@pytest.mark.fast
def test_get_conversation_returns_existing(repository):
    """
    Test: Repository retrieves existing conversation by ID
    
    ARRANGE
    """
    session = repository.create()
    conversation_id = session.id
    
    # ACT
    retrieved = repository.get(conversation_id)
    
    # ASSERT
    assert retrieved is not None
    assert retrieved.id == conversation_id


@pytest.mark.unit
@pytest.mark.fast
def test_get_conversation_returns_none_for_missing(repository):
    """
    Test: Repository returns None for non-existent conversation
    
    ARRANGE/ACT
    """
    retrieved = repository.get("non-existent-id")
    
    # ASSERT
    assert retrieved is None


@pytest.mark.unit
@pytest.mark.fast
def test_add_message_succeeds(repository):
    """
    Test: Repository adds message to conversation
    
    ARRANGE
    """
    session = repository.create()
    conversation_id = session.id
    
    # ACT
    message = repository.add_message(
        conversation_id,
        MessageRole.USER,
        "Test message"
    )
    
    # ASSERT
    assert message is not None
    assert message.role == MessageRole.USER
    assert message.content == "Test message"
    assert message.id is not None
    
    # Verify message added to session
    retrieved = repository.get(conversation_id)
    assert len(retrieved.messages) == 1
    assert retrieved.messages[0].content == "Test message"


@pytest.mark.unit
@pytest.mark.fast
def test_add_message_returns_none_for_missing_conversation(repository):
    """
    Test: Repository returns None when adding message to non-existent conversation
    
    ARRANGE/ACT
    """
    message = repository.add_message(
        "non-existent-id",
        MessageRole.USER,
        "Test"
    )
    
    # ASSERT
    assert message is None


@pytest.mark.unit
@pytest.mark.fast
def test_update_context_succeeds(repository):
    """
    Test: Repository updates conversation context
    
    ARRANGE
    """
    session = repository.create()
    conversation_id = session.id
    
    new_context = ConversationContext(
        datasource="new_db",
        data_product="TestProduct"
    )
    
    # ACT
    result = repository.update_context(conversation_id, new_context)
    
    # ASSERT
    assert result is True
    
    retrieved = repository.get(conversation_id)
    assert retrieved.context.datasource == "new_db"
    assert retrieved.context.data_product == "TestProduct"


@pytest.mark.unit
@pytest.mark.fast
def test_update_context_returns_false_for_missing(repository):
    """
    Test: Repository returns False when updating non-existent conversation
    
    ARRANGE/ACT
    """
    result = repository.update_context(
        "non-existent-id",
        ConversationContext()
    )
    
    # ASSERT
    assert result is False


@pytest.mark.unit
@pytest.mark.fast
def test_delete_conversation_succeeds(repository):
    """
    Test: Repository deletes existing conversation
    
    ARRANGE
    """
    session = repository.create()
    conversation_id = session.id
    
    # ACT
    result = repository.delete(conversation_id)
    
    # ASSERT
    assert result is True
    assert repository.get(conversation_id) is None


@pytest.mark.unit
@pytest.mark.fast
def test_delete_returns_false_for_missing(repository):
    """
    Test: Repository returns False when deleting non-existent conversation
    
    ARRANGE/ACT
    """
    result = repository.delete("non-existent-id")
    
    # ASSERT
    assert result is False


@pytest.mark.unit
@pytest.mark.fast
def test_list_all_returns_all_conversations(repository):
    """
    Test: Repository lists all conversations
    
    ARRANGE
    """
    session1 = repository.create()
    session2 = repository.create()
    session3 = repository.create()
    
    # ACT
    all_conversations = repository.list_all()
    
    # ASSERT
    assert len(all_conversations) == 3
    ids = [conv.id for conv in all_conversations]
    assert session1.id in ids
    assert session2.id in ids
    assert session3.id in ids


@pytest.mark.unit
@pytest.mark.fast
def test_get_count_returns_correct_count(repository):
    """
    Test: Repository returns correct conversation count
    
    ARRANGE
    """
    repository.create()
    repository.create()
    repository.create()
    
    # ACT
    count = repository.get_count()
    
    # ASSERT
    assert count == 3


@pytest.mark.unit
@pytest.mark.fast
def test_exists_returns_true_for_existing(repository):
    """
    Test: Repository exists() returns True for existing conversation
    
    ARRANGE
    """
    session = repository.create()
    
    # ACT
    result = repository.exists(session.id)
    
    # ASSERT
    assert result is True


@pytest.mark.unit
@pytest.mark.fast
def test_exists_returns_false_for_missing(repository):
    """
    Test: Repository exists() returns False for non-existent conversation
    
    ARRANGE/ACT
    """
    result = repository.exists("non-existent-id")
    
    # ASSERT
    assert result is False


@pytest.mark.unit
@pytest.mark.fast
def test_clear_all_removes_all_conversations(repository):
    """
    Test: Repository clear_all() removes all conversations
    
    ARRANGE
    """
    repository.create()
    repository.create()
    repository.create()
    
    # ACT
    repository.clear_all()
    
    # ASSERT
    assert repository.get_count() == 0


@pytest.mark.unit
@pytest.mark.fast
def test_singleton_returns_same_instance():
    """
    Test: get_conversation_repository() returns singleton instance
    
    ARRANGE/ACT
    """
    instance1 = get_conversation_repository()
    instance2 = get_conversation_repository()
    
    # ASSERT
    assert instance1 is instance2