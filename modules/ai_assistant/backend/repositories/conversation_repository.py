"""
Conversation Repository

In-memory storage for conversation sessions (Phase 2a)
Future: Migrate to SQLite/PostgreSQL for persistence
"""

from typing import Optional, Dict, List
from datetime import datetime, timedelta
from ..models import ConversationSession, ConversationContext, ConversationMessage, MessageRole


class ConversationRepository:
    """
    In-memory conversation storage
    
    Phase 2a: Simple dict-based storage
    Phase 3: Migrate to SQLite for persistence
    """
    
    def __init__(self, ttl_hours: int = 24):
        """
        Initialize repository
        
        Args:
            ttl_hours: Time-to-live for conversations (hours)
        """
        self._conversations: Dict[str, ConversationSession] = {}
        self._ttl_hours = ttl_hours
    
    def create(self, context: Optional[ConversationContext] = None) -> ConversationSession:
        """
        Create new conversation session
        
        Args:
            context: Initial context (optional)
        
        Returns:
            New conversation session
        """
        session = ConversationSession(context=context or ConversationContext())
        self._conversations[session.id] = session
        return session
    
    def get(self, conversation_id: str) -> Optional[ConversationSession]:
        """
        Get conversation by ID
        
        Args:
            conversation_id: Conversation ID
        
        Returns:
            Conversation session or None if not found
        """
        # Auto-cleanup expired conversations
        self._cleanup_expired()
        
        return self._conversations.get(conversation_id)
    
    def exists(self, conversation_id: str) -> bool:
        """Check if conversation exists"""
        return conversation_id in self._conversations
    
    def add_message(
        self,
        conversation_id: str,
        role: MessageRole,
        content: str,
        metadata: Optional[Dict] = None
    ) -> Optional[ConversationMessage]:
        """
        Add message to conversation
        
        Args:
            conversation_id: Conversation ID
            role: Message role
            content: Message content
            metadata: Optional metadata
        
        Returns:
            Created message or None if conversation not found
        """
        session = self.get(conversation_id)
        if not session:
            return None
        
        message = session.add_message(role, content, metadata)
        return message
    
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
        session = self.get(conversation_id)
        if not session:
            return False
        
        session.context = context
        session.updated_at = datetime.utcnow()
        return True
    
    def delete(self, conversation_id: str) -> bool:
        """
        Delete conversation
        
        Args:
            conversation_id: Conversation ID
        
        Returns:
            True if deleted, False if not found
        """
        if conversation_id in self._conversations:
            del self._conversations[conversation_id]
            return True
        return False
    
    def list_all(self) -> List[ConversationSession]:
        """
        List all conversations
        
        Returns:
            List of all conversation sessions
        """
        self._cleanup_expired()
        return list(self._conversations.values())
    
    def get_count(self) -> int:
        """Get total conversation count"""
        return len(self._conversations)
    
    def _cleanup_expired(self):
        """Remove expired conversations (TTL-based)"""
        now = datetime.utcnow()
        expired_ids = []
        
        for conv_id, session in self._conversations.items():
            age = now - session.updated_at
            if age > timedelta(hours=self._ttl_hours):
                expired_ids.append(conv_id)
        
        for conv_id in expired_ids:
            del self._conversations[conv_id]
    
    def clear_all(self):
        """Clear all conversations (for testing)"""
        self._conversations.clear()


# Singleton instance (for Phase 2a simplicity)
_repository = ConversationRepository(ttl_hours=24)


def get_conversation_repository() -> ConversationRepository:
    """
    Get conversation repository instance
    
    Returns:
        Singleton conversation repository
    """
    return _repository