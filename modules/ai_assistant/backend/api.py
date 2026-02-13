"""
AI Assistant v2 API

Flask Blueprint for conversational AI assistant with conversation management
"""

from flask import Blueprint, request, jsonify
import time
from datetime import datetime

from .models import (
    ChatRequest,
    ChatResponse,
    CreateConversationRequest,
    CreateConversationResponse,
    ConversationHistoryResponse,
    ConversationContextResponse,
    ConversationContext,
    AssistantResponse
)
from .services import get_conversation_service

# Create blueprint
blueprint = Blueprint('ai_assistant', __name__, url_prefix='/api/ai-assistant')

# Get service instance
conversation_service = get_conversation_service()


@blueprint.route('/conversations', methods=['POST'])
def create_conversation():
    """
    Create new conversation session
    
    Request:
        {
            "context": {
                "datasource": "p2p_data",
                "data_product": "SupplierInvoice",
                ...
            }
        }
    
    Response:
        {
            "success": true,
            "conversation_id": "uuid",
            "timestamp": "2026-02-13T20:30:00Z"
        }
    """
    try:
        data = request.get_json() or {}
        
        # Parse request
        req = CreateConversationRequest(**data)
        
        # Create conversation
        session = conversation_service.create_conversation(req.context)
        
        # Return response
        response = CreateConversationResponse(
            success=True,
            conversation_id=session.id
        )
        
        return jsonify(response.dict()), 201
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@blueprint.route('/conversations/<conversation_id>', methods=['GET'])
def get_conversation_history(conversation_id):
    """
    Get conversation history
    
    Response:
        {
            "success": true,
            "conversation": {
                "id": "uuid",
                "messages": [...],
                "context": {...},
                ...
            }
        }
    """
    try:
        session = conversation_service.get_conversation(conversation_id)
        
        if not session:
            return jsonify({
                "success": False,
                "error": "Conversation not found"
            }), 404
        
        response = ConversationHistoryResponse(
            success=True,
            conversation=session
        )
        
        return jsonify(response.dict())
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@blueprint.route('/conversations/<conversation_id>/messages', methods=['POST'])
def send_message(conversation_id):
    """
    Send message in existing conversation
    
    Request:
        {
            "message": "User message"
        }
    
    Response:
        {
            "success": true,
            "response": {...},
            "conversation_id": "uuid",
            "timestamp": "..."
        }
    """
    try:
        data = request.get_json()
        
        if not data or 'message' not in data:
            return jsonify({
                "success": False,
                "error": "Missing 'message' in request body"
            }), 400
        
        user_message = data['message']
        
        # Check if conversation exists
        session = conversation_service.get_conversation(conversation_id)
        if not session:
            return jsonify({
                "success": False,
                "error": "Conversation not found"
            }), 404
        
        # Add user message
        user_msg = conversation_service.add_user_message(conversation_id, user_message)
        if not user_msg:
            return jsonify({
                "success": False,
                "error": "Failed to add message"
            }), 500
        
        # ========================================
        # MOCK RESPONSE (Replace with Pydantic AI in Phase 2b)
        # ========================================
        
        # Simulate AI processing
        time.sleep(0.5)
        
        # Generate mock response
        ai_response_data = _generate_mock_response(user_message, session.context.dict())
        ai_response = AssistantResponse(**ai_response_data)
        
        # Add assistant response
        conversation_service.add_assistant_message(conversation_id, ai_response)
        
        # Return response
        response = ChatResponse(
            success=True,
            response=ai_response,
            conversation_id=conversation_id
        )
        
        return jsonify(response.dict())
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@blueprint.route('/conversations/<conversation_id>', methods=['DELETE'])
def delete_conversation(conversation_id):
    """
    Delete conversation
    
    Response:
        {
            "success": true,
            "message": "Conversation deleted"
        }
    """
    try:
        deleted = conversation_service.delete_conversation(conversation_id)
        
        if not deleted:
            return jsonify({
                "success": False,
                "error": "Conversation not found"
            }), 404
        
        return jsonify({
            "success": True,
            "message": "Conversation deleted"
        })
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@blueprint.route('/conversations/<conversation_id>/context', methods=['GET'])
def get_conversation_context(conversation_id):
    """
    Get conversation context
    
    Response:
        {
            "success": true,
            "context": {...},
            "context_summary": "..."
        }
    """
    try:
        session = conversation_service.get_conversation(conversation_id)
        
        if not session:
            return jsonify({
                "success": False,
                "error": "Conversation not found"
            }), 404
        
        summary = conversation_service.build_context_summary(conversation_id)
        
        response = ConversationContextResponse(
            success=True,
            context=session.context,
            context_summary=summary
        )
        
        return jsonify(response.dict())
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@blueprint.route('/chat', methods=['POST'])
def chat():
    """
    Legacy chat endpoint (backwards compatible)
    
    Automatically creates conversation if needed
    
    Request:
        {
            "message": "User message",
            "conversation_id": "optional-uuid",
            "context": {...}
        }
    
    Response:
        {
            "success": true,
            "response": {...},
            "conversation_id": "uuid",
            "timestamp": "..."
        }
    """
    try:
        data = request.get_json()
        
        if not data or 'message' not in data:
            return jsonify({
                "success": False,
                "error": "Missing 'message' in request body"
            }), 400
        
        # Parse request
        req = ChatRequest(**data)
        
        # Get or create conversation
        conversation_id = req.conversation_id
        if conversation_id:
            session = conversation_service.get_conversation(conversation_id)
            if not session:
                # Conversation doesn't exist, create new one
                session = conversation_service.create_conversation(req.context)
                conversation_id = session.id
        else:
            # Create new conversation
            session = conversation_service.create_conversation(req.context)
            conversation_id = session.id
        
        # Add user message
        conversation_service.add_user_message(conversation_id, req.message)
        
        # Generate mock response
        time.sleep(0.5)
        ai_response_data = _generate_mock_response(req.message, session.context.dict())
        ai_response = AssistantResponse(**ai_response_data)
        
        # Add assistant response
        conversation_service.add_assistant_message(conversation_id, ai_response)
        
        # Return response
        response = ChatResponse(
            success=True,
            response=ai_response,
            conversation_id=conversation_id
        )
        
        return jsonify(response.dict())
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


def _generate_mock_response(user_message: str, context: dict) -> dict:
    """
    Generate mock AI response (temporary, for UI testing)
    
    TODO Phase 2: Replace with Pydantic AI agent
    """
    message_lower = user_message.lower()
    
    # Pattern-based mock responses
    if any(word in message_lower for word in ['supplier', 'vendor']):
        return {
            "message": "I found information about suppliers in the P2P datasource. "
                      "Currently, there are 5 active suppliers: ACME Corp (rating: 4.8), "
                      "Globex Inc (rating: 4.7), Initech LLC (rating: 4.6), "
                      "Hooli Technologies (rating: 4.5), and Massive Dynamic (rating: 4.3).\n\n"
                      "Would you like me to provide more details about any specific supplier?",
            "confidence": 0.92,
            "sources": ["Supplier table", "Rating calculation"],
            "suggested_actions": [
                {"text": "Show supplier details", "action": "view_suppliers"}
            ],
            "requires_clarification": False
        }
    
    elif any(word in message_lower for word in ['invoice', 'bill']):
        return {
            "message": "Based on the P2P datasource, there are currently 23 pending invoices "
                      "totaling $145,230.45. The oldest invoice is 12 days overdue.\n\n"
                      "Here's a breakdown by status:\n"
                      "- Pending approval: 15 invoices ($98,120.30)\n"
                      "- Overdue: 5 invoices ($32,450.15)\n"
                      "- In review: 3 invoices ($14,660.00)",
            "confidence": 0.95,
            "sources": ["Invoice header table", "Payment status"],
            "suggested_actions": [],
            "requires_clarification": False
        }
    
    elif any(word in message_lower for word in ['order', 'po', 'purchase']):
        return {
            "message": "Purchase order data shows 42 active orders with a total value of $523,890.00. "
                      "Most orders are in 'Approved' status (35 orders), with 7 orders awaiting approval.\n\n"
                      "Top suppliers by PO value:\n"
                      "1. ACME Corp - $145,230 (8 POs)\n"
                      "2. Globex Inc - $98,450 (12 POs)\n"
                      "3. Initech LLC - $76,120 (15 POs)",
            "confidence": 0.90,
            "sources": ["Purchase order table", "Supplier statistics"],
            "suggested_actions": [
                {"text": "View PO details", "action": "view_pos"}
            ],
            "requires_clarification": False
        }
    
    elif any(word in message_lower for word in ['kpi', 'metric', 'analytics', 'performance']):
        return {
            "message": "Here are the current P2P performance metrics:\n\n"
                      "**Cycle Time**: 14.5 days (target: 12 days) ⚠️\n"
                      "**Invoice Processing Time**: 3.2 days (target: 3 days) ✅\n"
                      "**Approval Rate**: 92% (target: 95%) ⚠️\n"
                      "**Spend Under Management**: 87% (target: 90%) ⚠️\n\n"
                      "Recommendation: Focus on reducing approval bottlenecks to improve cycle time.",
            "confidence": 0.88,
            "sources": ["KPI calculation engine", "Historical data"],
            "suggested_actions": [
                {"text": "View detailed analytics", "action": "view_analytics"}
            ],
            "requires_clarification": False
        }
    
    elif 'help' in message_lower or '?' in user_message:
        return {
            "message": "I'm Joule, your P2P data assistant! I can help you with:\n\n"
                      "📊 **Queries**: Ask about suppliers, invoices, purchase orders\n"
                      "📈 **Analytics**: Request KPIs, metrics, and performance data\n"
                      "🔍 **Search**: Find specific data in the P2P datasource\n"
                      "💡 **Insights**: Get recommendations and analysis\n\n"
                      "Try asking:\n"
                      "- 'Show me suppliers with rating above 4.5'\n"
                      "- 'What are my pending invoices?'\n"
                      "- 'Calculate current cycle time KPI'",
            "confidence": 1.0,
            "sources": [],
            "suggested_actions": [],
            "requires_clarification": False
        }
    
    else:
        # Generic response
        return {
            "message": f"I understand you're asking about: '{user_message}'\n\n"
                      "I'm currently in Phase 1 (UI testing) with mock responses. "
                      "In Phase 2, I'll be powered by Pydantic AI and Groq to provide "
                      "real-time analysis of your P2P datasource.\n\n"
                      "Try asking about suppliers, invoices, purchase orders, or KPIs!",
            "confidence": 0.75,
            "sources": ["Mock response generator"],
            "suggested_actions": [
                {"text": "Ask about suppliers", "action": "suppliers"},
                {"text": "Ask about invoices", "action": "invoices"}
            ],
            "requires_clarification": True
        }


@blueprint.route('/health', methods=['GET'])
def health():
    """Health check endpoint with statistics"""
    stats = conversation_service.get_statistics()
    
    return jsonify({
        "status": "healthy",
        "version": "2.0.0",
        "phase": "Phase 2a - Conversation Management (Mock AI responses)",
        "backend": "In-memory conversation storage + Mock AI (Pydantic AI coming in Phase 2b)",
        "statistics": stats
    })
