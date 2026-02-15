"""
Conversation Service

Business logic for conversation management with context injection
"""

from typing import Optional, Dict, Any, List
from datetime import datetime

from ..models import (
    ConversationSession,
    ConversationContext,
    ConversationMessage,
    MessageRole,
    AssistantResponse
)
from ..repositories import get_conversation_repository


class ConversationService:
    """
    Conversation management service
    
    Handles conversation lifecycle, context management, and message history
    """
    
    def __init__(self, repository=None, max_context_messages: int = 10):
        """
        Initialize service
        
        Args:
            repository: Optional repository for dependency injection (for testing)
            max_context_messages: Max messages to include in context window
        """
        self._repository = repository if repository is not None else get_conversation_repository()
        self._max_context_messages = max_context_messages
    
    def create_conversation(
        self,
        context: Optional[ConversationContext] = None
    ) -> ConversationSession:
        """
        Create new conversation session
        
        Args:
            context: Initial context (optional)
        
        Returns:
            New conversation session
        """
        return self._repository.create(context)
    
    def get_conversation(self, conversation_id: str) -> Optional[ConversationSession]:
        """
        Get conversation by ID
        
        Args:
            conversation_id: Conversation ID
        
        Returns:
            Conversation session or None if not found
        """
        return self._repository.get(conversation_id)
    
    def add_user_message(
        self,
        conversation_id: str,
        message: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Optional[ConversationMessage]:
        """
        Add user message to conversation
        
        Args:
            conversation_id: Conversation ID
            message: User message content
            metadata: Optional metadata
        
        Returns:
            Created message or None if conversation not found
        """
        return self._repository.add_message(
            conversation_id,
            MessageRole.USER,
            message,
            metadata
        )
    
    def add_assistant_message(
        self,
        conversation_id: str,
        response: AssistantResponse
    ) -> Optional[ConversationMessage]:
        """
        Add assistant response to conversation
        
        Args:
            conversation_id: Conversation ID
            response: Assistant response
        
        Returns:
            Created message or None if conversation not found
        """
        metadata = {
            "confidence": response.confidence,
            "sources": response.sources,
            "suggested_actions": [action.dict() for action in (response.suggested_actions or [])],
            "requires_clarification": response.requires_clarification
        }
        
        if response.metadata:
            metadata.update(response.metadata)
        
        return self._repository.add_message(
            conversation_id,
            MessageRole.ASSISTANT,
            response.message,
            metadata
        )
    
    def update_context(
        self,
        conversation_id: str,
        context: ConversationContext
    ) -> bool:
        """
        Update conversation context
        
        Args:
            conversation_id: Conversation ID
            context: New context
        
        Returns:
            True if updated, False if conversation not found
        """
        return self._repository.update_context(conversation_id, context)
    
    def delete_conversation(self, conversation_id: str) -> bool:
        """
        Delete conversation
        
        Args:
            conversation_id: Conversation ID
        
        Returns:
            True if deleted, False if not found
        """
        return self._repository.delete(conversation_id)
    
    def get_conversation_history(
        self,
        conversation_id: str,
        limit: Optional[int] = None
    ) -> Optional[List[ConversationMessage]]:
        """
        Get conversation message history
        
        Args:
            conversation_id: Conversation ID
            limit: Max messages to return (optional, returns all if None)
        
        Returns:
            List of messages or None if conversation not found
        """
        session = self._repository.get(conversation_id)
        if not session:
            return None
        
        messages = session.messages
        if limit and limit > 0:
            messages = messages[-limit:]
        
        return messages
    
    def get_context_window(
        self,
        conversation_id: str
    ) -> Optional[List[ConversationMessage]]:
        """
        Get recent messages for AI context window
        
        Args:
            conversation_id: Conversation ID
        
        Returns:
            Recent messages (up to max_context_messages) or None if conversation not found
        """
        return self.get_conversation_history(conversation_id, self._max_context_messages)
    
    def build_context_summary(self, conversation_id: str) -> Optional[str]:
        """
        Build human-readable context summary
        
        Args:
            conversation_id: Conversation ID
        
        Returns:
            Context summary or None if conversation not found
        """
        session = self._repository.get(conversation_id)
        if not session:
            return None
        
        parts = []
        parts.append(f"Conversation: {conversation_id[:8]}...")
        parts.append(f"Messages: {session.get_message_count()}")
        parts.append(session.get_context_summary())
        
        return " | ".join(parts)
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Get repository statistics
        
        Returns:
            Statistics dictionary
        """
        all_conversations = self._repository.list_all()
        
        total_messages = sum(len(conv.messages) for conv in all_conversations)
        avg_messages = total_messages / len(all_conversations) if all_conversations else 0
        
        return {
            "total_conversations": len(all_conversations),
            "total_messages": total_messages,
            "avg_messages_per_conversation": round(avg_messages, 2)
        }


# Singleton instance
_service = ConversationService(max_context_messages=10)


def get_conversation_service() -> ConversationService:
    """
    Get conversation service instance
    
    Returns:
        Singleton conversation service
    """
    return _service