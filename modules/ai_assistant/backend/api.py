"""
AI Assistant v2 API

Flask Blueprint for conversational AI assistant with conversation management
"""

from flask import Blueprint, request, jsonify, Response, stream_with_context
import time
from datetime import datetime
import json

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
from .services import get_conversation_service, get_joule_agent
from .services.sql_execution_service import get_sql_execution_service
import asyncio

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
        # REAL AI with Pydantic AI + Groq (Phase 2c)
        # ========================================
        
        try:
            # Get Joule agent
            agent = get_joule_agent()
            
            # Get conversation history for context
            history_messages = conversation_service.get_context_window(conversation_id)
            history = []
            if history_messages:
                for msg in history_messages[:-1]:  # Exclude last message (current user message)
                    history.append({
                        "role": msg.role.value,
                        "content": msg.content
                    })
            
            # Process message with agent (async)
            ai_response = asyncio.run(agent.process_message(
                user_message=user_message,
                conversation_history=history,
                context=session.context.dict()
            ))
            
        except Exception as e:
            # Fallback to error response if AI fails
            ai_response = AssistantResponse(
                message=f"I apologize, but I encountered an error processing your request: {str(e)}\n\n"
                       "Please try rephrasing your question or contact support if the issue persists.",
                confidence=0.0,
                sources=["Error handler"],
                suggested_actions=[],
                requires_clarification=True,
                metadata={"error": str(e), "error_type": type(e).__name__}
            )
        
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


@blueprint.route('/chat/stream', methods=['POST'])
def chat_stream():
    """
    Streaming chat endpoint with Server-Sent Events (SSE)
    
    Provides real-time streaming responses with typing indicator effect.
    Maintains all Phase 2c features (tools, type safety, validation).
    
    Request:
        {
            "message": "User message",
            "conversation_id": "optional-uuid",
            "context": {...}
        }
    
    Response: SSE stream
        data: {"type": "delta", "content": "text chunk"}
        data: {"type": "tool_call", "tool_name": "query_p2p_datasource", "status": "started"}
        data: {"type": "done", "response": {...}, "conversation_id": "uuid"}
    """
    try:
        data = request.get_json()
        
        if not data or 'message' not in data:
            return jsonify({
                "success": False,
                "error": "Missing 'message' in request body"
            }), 400
        
        user_message = data['message']
        conversation_id = data.get('conversation_id')
        context = data.get('context', {})
        
        # Get or create conversation
        if conversation_id:
            session = conversation_service.get_conversation(conversation_id)
            if not session:
                # Conversation doesn't exist, create new one
                session = conversation_service.create_conversation(context)
                conversation_id = session.id
        else:
            # Create new conversation
            session = conversation_service.create_conversation(context)
            conversation_id = session.id
        
        # Add user message
        conversation_service.add_user_message(conversation_id, user_message)
        
        # Get conversation history for context
        history_messages = conversation_service.get_context_window(conversation_id)
        history = []
        if history_messages:
            for msg in history_messages[:-1]:  # Exclude last message (current user message)
                history.append({
                    "role": msg.role.value,
                    "content": msg.content
                })
        
        def generate():
            """Generator function for SSE streaming"""
            try:
                # Get Joule agent
                agent = get_joule_agent()
                
                # Stream response
                async def stream_response():
                    """Async generator for streaming"""
                    nonlocal conversation_id
                    
                    full_message = ""
                    final_response = None
                    
                    async for event in agent.process_message_stream(
                        user_message=user_message,
                        conversation_history=history,
                        context=session.context.dict()
                    ):
                        
                        if event['type'] == 'delta':
                            # Accumulate message content
                            full_message += event['content']
                            # Send delta to client
                            yield f"data: {json.dumps(event)}\n\n"
                        
                        elif event['type'] == 'tool_call':
                            # Send tool call notification
                            yield f"data: {json.dumps(event)}\n\n"
                        
                        elif event['type'] == 'done':
                            # Final result
                            final_response = event['response']
                            # Add conversation_id to response
                            event['conversation_id'] = conversation_id
                            yield f"data: {json.dumps(event)}\n\n"
                    
                    # Save assistant response to conversation
                    if final_response:
                        from .models import AssistantResponse
                        assistant_resp = AssistantResponse(**final_response)
                        conversation_service.add_assistant_message(conversation_id, assistant_resp)
                    
                    # Send completion signal
                    yield "data: [DONE]\n\n"
                
                # Use asyncio.run() with proper event loop management
                # This avoids the "cancel scope" error by using a single event loop
                import asyncio
                import sys
                
                # Collect all chunks from async generator
                async def collect_chunks():
                    chunks = []
                    async for chunk in stream_response():
                        chunks.append(chunk)
                    return chunks
                
                # Run in new event loop (Windows-safe)
                if sys.platform == 'win32':
                    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
                
                chunks = asyncio.run(collect_chunks())
                
                # Yield all chunks
                for chunk in chunks:
                    yield chunk
                
            except Exception as e:
                # Send error event
                error_event = {
                    "type": "error",
                    "error": str(e)
                }
                yield f"data: {json.dumps(error_event)}\n\n"
        
        return Response(
            stream_with_context(generate()),
            mimetype='text/event-stream',
            headers={
                'Cache-Control': 'no-cache',
                'Connection': 'keep-alive',
                'X-Accel-Buffering': 'no',  # Disable nginx buffering
                'Access-Control-Allow-Origin': '*'
            }
        )
        
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
        
        # ========================================
        # REAL AI with Pydantic AI + Groq (Phase 2c)
        # ========================================
        
        try:
            # Get Joule agent
            agent = get_joule_agent()
            
            # Get conversation history for context
            history_messages = conversation_service.get_context_window(conversation_id)
            history = []
            if history_messages:
                for msg in history_messages[:-1]:  # Exclude last message (current user message)
                    history.append({
                        "role": msg.role.value,
                        "content": msg.content
                    })
            
            # Process message with agent (async)
            ai_response = asyncio.run(agent.process_message(
                user_message=req.message,
                conversation_history=history,
                context=session.context.dict()
            ))
            
        except Exception as e:
            # Fallback to error response if AI fails
            ai_response = AssistantResponse(
                message=f"I apologize, but I encountered an error processing your request: {str(e)}\n\n"
                       "Please try rephrasing your question or contact support if the issue persists.",
                confidence=0.0,
                sources=["Error handler"],
                suggested_actions=[],
                requires_clarification=True,
                metadata={"error": str(e), "error_type": type(e).__name__}
            )
        
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


@blueprint.route('/execute-sql', methods=['POST'])
def execute_sql():
    """
    Execute SQL query with validation (Phase 4.5)
    
    Request:
        {
            "sql": "SELECT * FROM suppliers WHERE rating > 4.5",
            "datasource": "p2p_data"  (optional, default: p2p_data)
        }
    
    Response:
        {
            "success": true,
            "rows": [...],
            "columns": ["id", "name", "rating"],
            "row_count": 10,
            "execution_time_ms": 15.5,
            "warnings": ["Query modified to enforce LIMIT 1000"]
        }
    """
    try:
        data = request.get_json()
        
        if not data or 'sql' not in data:
            return jsonify({
                "success": False,
                "error": "Missing 'sql' in request body"
            }), 400
        
        sql = data['sql']
        datasource = data.get('datasource', 'p2p_data')
        
        # Get SQL execution service
        sql_service = get_sql_execution_service(datasource)
        
        # Execute query
        result = sql_service.execute_query(sql)
        
        # Return result
        return jsonify({
            "success": result.success,
            "rows": result.rows if result.success else [],
            "columns": result.columns,
            "row_count": result.row_count,
            "execution_time_ms": result.execution_time_ms,
            "error": result.error,
            "warnings": result.warnings
        }), 200 if result.success else 400
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@blueprint.route('/health', methods=['GET'])
def health():
    """Health check endpoint with statistics"""
    stats = conversation_service.get_statistics()
    
    # Try to get agent info
    agent_status = "unknown"
    try:
        agent = get_joule_agent()
        agent_status = "initialized" if agent else "not_initialized"
    except Exception as e:
        agent_status = f"error: {str(e)}"
    
    return jsonify({
        "status": "healthy",
        "version": "2.1.0",
        "phase": "Phase 4.5 - SQL Execution from Chat (In Progress)",
        "backend": {
            "conversation_storage": "In-memory with conversation context",
            "ai_engine": "Pydantic AI v1.56.0 + Groq llama-3.3-70b-versatile",
            "tools": ["query_p2p_datasource", "calculate_kpi", "get_schema_info", "execute_sql"],
            "features": ["Type-safe responses", "P2P data access", "Conversation context", "Error fallback", "SQL execution"]
        },
        "agent_status": agent_status,
        "statistics": stats
    })
