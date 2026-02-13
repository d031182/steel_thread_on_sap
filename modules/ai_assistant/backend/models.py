"""
AI Assistant Backend Models

Pydantic models for conversation management and responses
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from uuid import UUID, uuid4
from enum import Enum


class MessageRole(str, Enum):
    """Message role enumeration"""
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


class ConversationMessage(BaseModel):
    """Individual message in a conversation"""
    id: str = Field(default_factory=lambda: str(uuid4()), description="Unique message ID")
    role: MessageRole = Field(description="Message role (user/assistant/system)")
    content: str = Field(min_length=1, max_length=10000, description="Message content")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Message timestamp")
    metadata: Optional[Dict[str, Any]] = Field(default=None, description="Additional metadata (tokens, sources, etc.)")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class ConversationContext(BaseModel):
    """Context information for conversation"""
    datasource: Optional[str] = Field(default="p2p_data", description="Active datasource")
    current_page: Optional[str] = Field(default=None, description="Current page in app")
    data_product: Optional[str] = Field(default=None, description="Selected data product")
    schema: Optional[str] = Field(default=None, description="Current schema")
    table: Optional[str] = Field(default=None, description="Current table")
    user_id: Optional[str] = Field(default=None, description="User identifier")
    additional: Optional[Dict[str, Any]] = Field(default=None, description="Additional context")


class ConversationSession(BaseModel):
    """Complete conversation session"""
    id: str = Field(default_factory=lambda: str(uuid4()), description="Unique conversation ID")
    messages: List[ConversationMessage] = Field(default_factory=list, description="Conversation messages")
    context: ConversationContext = Field(default_factory=ConversationContext, description="Conversation context")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Session creation time")
    updated_at: datetime = Field(default_factory=datetime.utcnow, description="Last update time")
    metadata: Optional[Dict[str, Any]] = Field(default=None, description="Session metadata")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
    
    def add_message(self, role: MessageRole, content: str, metadata: Optional[Dict[str, Any]] = None) -> ConversationMessage:
        """Add a message to the conversation"""
        message = ConversationMessage(role=role, content=content, metadata=metadata)
        self.messages.append(message)
        self.updated_at = datetime.utcnow()
        return message
    
    def get_message_count(self) -> int:
        """Get total message count"""
        return len(self.messages)
    
    def get_context_summary(self) -> str:
        """Get human-readable context summary"""
        parts = []
        if self.context.data_product:
            parts.append(f"Data Product: {self.context.data_product}")
        if self.context.schema:
            parts.append(f"Schema: {self.context.schema}")
        if self.context.table:
            parts.append(f"Table: {self.context.table}")
        return " | ".join(parts) if parts else "No context"


class SuggestedAction(BaseModel):
    """Suggested action for user"""
    text: str = Field(description="Action button text")
    action: str = Field(description="Action identifier")
    params: Optional[Dict[str, Any]] = Field(default=None, description="Action parameters")


class AssistantResponse(BaseModel):
    """AI assistant response structure"""
    message: str = Field(description="AI response text")
    confidence: float = Field(ge=0.0, le=1.0, description="Response confidence score")
    sources: List[str] = Field(default_factory=list, description="Data sources used")
    suggested_actions: Optional[List[SuggestedAction]] = Field(default=None, description="Suggested next actions")
    requires_clarification: bool = Field(default=False, description="Whether response needs clarification")
    metadata: Optional[Dict[str, Any]] = Field(default=None, description="Additional metadata")


# ========================================
# API Request/Response Models
# ========================================

class ChatRequest(BaseModel):
    """Request to send chat message"""
    message: str = Field(min_length=1, max_length=2000, description="User message")
    conversation_id: Optional[str] = Field(default=None, description="Existing conversation ID (optional)")
    context: Optional[ConversationContext] = Field(default=None, description="Context information")


class ChatResponse(BaseModel):
    """Response from chat endpoint"""
    success: bool = Field(description="Whether request succeeded")
    response: Optional[AssistantResponse] = Field(default=None, description="AI response (if successful)")
    error: Optional[str] = Field(default=None, description="Error message (if failed)")
    conversation_id: str = Field(description="Conversation ID")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Response timestamp")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class CreateConversationRequest(BaseModel):
    """Request to create new conversation"""
    context: Optional[ConversationContext] = Field(default=None, description="Initial context")


class CreateConversationResponse(BaseModel):
    """Response from create conversation endpoint"""
    success: bool = Field(description="Whether creation succeeded")
    conversation_id: str = Field(description="New conversation ID")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Creation timestamp")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class ConversationHistoryResponse(BaseModel):
    """Response from get conversation history endpoint"""
    success: bool = Field(description="Whether request succeeded")
    conversation: Optional[ConversationSession] = Field(default=None, description="Conversation data")
    error: Optional[str] = Field(default=None, description="Error message (if failed)")


class ConversationContextResponse(BaseModel):
    """Response from get conversation context endpoint"""
    success: bool = Field(description="Whether request succeeded")
    context: Optional[ConversationContext] = Field(default=None, description="Context data")
    context_summary: Optional[str] = Field(default=None, description="Human-readable context summary")
    error: Optional[str] = Field(default=None, description="Error message (if failed)")