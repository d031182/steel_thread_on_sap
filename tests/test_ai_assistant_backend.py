"""
Unit Tests for AI Assistant Backend
====================================
Simple smoke tests to verify pytest works after reset.

Following Gu Wu standards:
- AAA pattern (Arrange, Act, Assert)
- pytest markers
- Descriptive docstrings
"""

import pytest
from modules.ai_assistant.backend.models import (
    ConversationSession,
    ConversationMessage,
    MessageRole,
    ConversationContext
)
from modules.ai_assistant.backend.repositories.conversation_repository import (
    ConversationRepository,
    get_conversation_repository
)
from modules.ai_assistant.backend.services.conversation_service import (
    ConversationService
)


class TestConversationMessage:
    """Test ConversationMessage model"""
    
    @pytest.mark.unit
    def test_create_user_message(self):
        """
        Test: ConversationMessage can be created for user role
        
        ARRANGE
        """
        content = "Hello, AI!"
        
        # ACT
        message = ConversationMessage(
            role=MessageRole.USER,
            content=content
        )
        
        # ASSERT
        assert message.id is not None
        assert message.role == MessageRole.USER
        assert message.content == content
        assert message.timestamp is not None
    
    @pytest.mark.unit
    def test_create_assistant_message(self):
        """
        Test: ConversationMessage can be created for assistant role
        
        ARRANGE
        """
        content = "Hello, human!"
        
        # ACT
        message = ConversationMessage(
            role=MessageRole.ASSISTANT,
            content=content
        )
        
        # ASSERT
        assert message.role == MessageRole.ASSISTANT
        assert message.content == content


class TestConversationRepository:
    """Test ConversationRepository"""
    
    @pytest.mark.unit
    def test_create_conversation(self):
        """
        Test: Repository can create a new conversation
        
        ARRANGE
        """
        repo = ConversationRepository()
        repo.clear_all()  # Clean slate
        
        # ACT
        session = repo.create()
        
        # ASSERT
        assert session is not None
        assert session.id is not None
        assert repo.get_count() >= 1
    
    @pytest.mark.unit
    def test_get_existing_conversation(self):
        """
        Test: Repository can retrieve existing conversation by ID
        
        ARRANGE
        """
        repo = ConversationRepository()
        repo.clear_all()
        created_session = repo.create()
        
        # ACT
        retrieved_session = repo.get(created_session.id)
        
        # ASSERT
        assert retrieved_session is not None
        assert retrieved_session.id == created_session.id
    
    @pytest.mark.unit
    def test_get_nonexistent_conversation_returns_none(self):
        """
        Test: Repository returns None for non-existent conversation ID
        
        ARRANGE
        """
        repo = ConversationRepository()
        
        # ACT
        result = repo.get("nonexistent-id-12345")
        
        # ASSERT
        assert result is None
    
    @pytest.mark.unit
    def test_delete_conversation(self):
        """
        Test: Repository can delete a conversation
        
        ARRANGE
        """
        repo = ConversationRepository()
        repo.clear_all()
        session = repo.create()
        session_id = session.id
        
        # ACT
        result = repo.delete(session_id)
        
        # ASSERT
        assert result is True
        assert repo.get(session_id) is None


class TestConversationService:
    """Test ConversationService"""
    
    @pytest.mark.unit
    def test_create_conversation_via_service(self):
        """
        Test: Service can create a new conversation
        
        ARRANGE
        """
        repo = get_conversation_repository()
        repo.clear_all()
        service = ConversationService(repository=repo)
        
        # ACT
        session_id = service.create_conversation()
        
        # ASSERT
        assert session_id is not None
        session = repo.get(session_id)
        assert session is not None
    
    @pytest.mark.unit
    def test_add_message_to_conversation(self):
        """
        Test: Service can add a message to existing conversation
        
        ARRANGE
        """
        repo = get_conversation_repository()
        repo.clear_all()
        service = ConversationService(repository=repo)
        session_id = service.create_conversation()
        
        # ACT
        service.add_message(
            conversation_id=session_id,
            role=MessageRole.USER,
            content="Test message"
        )
        
        # ASSERT
        session = repo.get(session_id)
        assert len(session.messages) == 1
        assert session.messages[0].content == "Test message"
        assert session.messages[0].role == MessageRole.USER