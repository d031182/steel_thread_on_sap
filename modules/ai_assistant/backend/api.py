"""
AI Assistant v2 API

Flask Blueprint for conversational AI assistant
"""

from flask import Blueprint, request, jsonify
import time
import uuid
from datetime import datetime

# Create blueprint
blueprint = Blueprint('ai_assistant', __name__, url_prefix='/api/ai-assistant')

# In-memory conversation storage (temporary, for testing)
conversations = {}


@blueprint.route('/chat', methods=['POST'])
def chat():
    """
    Handle chat messages
    
    Request:
        {
            "message": "User message",
            "conversation_id": "optional-uuid",
            "context": {"datasource": "p2p_data"}
        }
    
    Response:
        {
            "success": true,
            "response": {
                "message": "AI response",
                "confidence": 0.95,
                "sources": ["..."],
                "suggested_actions": [],
                "requires_clarification": false
            },
            "conversation_id": "uuid",
            "timestamp": "2026-02-13T20:30:00Z"
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
        conversation_id = data.get('conversation_id') or str(uuid.uuid4())
        context = data.get('context', {})
        
        # Initialize conversation if new
        if conversation_id not in conversations:
            conversations[conversation_id] = []
        
        # Add user message to history
        conversations[conversation_id].append({
            "role": "user",
            "message": user_message,
            "timestamp": datetime.utcnow().isoformat()
        })
        
        # ========================================
        # MOCK RESPONSE (Replace with Pydantic AI in Phase 2)
        # ========================================
        
        # Simulate AI processing time
        time.sleep(0.5)
        
        # Generate mock response based on user message
        ai_response = _generate_mock_response(user_message, context)
        
        # Add AI response to history
        conversations[conversation_id].append({
            "role": "assistant",
            "message": ai_response["message"],
            "timestamp": datetime.utcnow().isoformat()
        })
        
        # Return response
        return jsonify({
            "success": True,
            "response": ai_response,
            "conversation_id": conversation_id,
            "timestamp": datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@blueprint.route('/conversation/<conversation_id>', methods=['GET'])
def get_conversation(conversation_id):
    """Get conversation history"""
    if conversation_id not in conversations:
        return jsonify({
            "success": False,
            "error": "Conversation not found"
        }), 404
    
    return jsonify({
        "success": True,
        "conversation_id": conversation_id,
        "messages": conversations[conversation_id]
    })


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


# Health check endpoint
@blueprint.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "version": "1.0.0",
        "phase": "Phase 1 - UI Testing (Mock API)",
        "backend": "Mock responses (Pydantic AI coming in Phase 2)"
    })