"""
AI Agent Service - Pydantic AI + Groq Integration

Phase 2c: Real AI with P2P datasource query capabilities
Phase 4.4: Streaming support
"""

import os
from typing import Optional, List, Dict, Any
from dataclasses import dataclass
from pydantic_ai import Agent, RunContext
from pydantic_ai.models.groq import GroqModel

from ..models import AssistantResponse, SuggestedAction
from core.services.sqlite_data_products_service import SQLiteDataProductsService


@dataclass
class AgentDependencies:
    """
    Dependencies injected into agent tools
    
    NOT exposed to LLM schema - only available in tool implementations
    """
    datasource: str
    data_product_service: Any  # Repository for P2P data queries
    conversation_context: Dict[str, Any]  # Current conversation context


class JouleAgent:
    """
    Joule AI Assistant Agent
    
    Powered by:
    - Pydantic AI (type-safe agent framework)
    - Groq llama-3.3-70b-versatile (ultra-fast inference)
    - P2P datasource tools (real data access)
    
    Features:
    - Type-safe structured outputs (non-streaming)
    - Real-time text streaming (streaming mode)
    - Conversation context awareness
    - P2P database query capabilities
    """
    
    def __init__(
        self,
        model_name: str = "llama-3.3-70b-versatile",
        temperature: float = 0.7,
        max_retries: int = 2
    ):
        """
        Initialize Joule agent
        
        Args:
            model_name: Groq model name
            temperature: Response randomness (0-1)
            max_retries: Validation retry attempts
        """
        # Verify Groq API key exists in environment
        groq_api_key = os.getenv("GROQ_API_KEY")
        if not groq_api_key:
            raise ValueError("GROQ_API_KEY not found in environment")
        
        # Create Groq model instance
        self.model = GroqModel(model_name)
        
        # Structured agent (with validation) - for non-streaming
        self.agent = Agent(
            self.model,
            output_type=AssistantResponse,
            retries=max_retries,
            system_prompt=self._get_system_prompt()
        )
        
        # Text streaming agent (no structured output) - for streaming
        self.streaming_agent = Agent(
            self.model,
            system_prompt=self._get_streaming_prompt()
        )
        
        # Register tools
        self._register_tools()
        
        # Configuration
        self.temperature = temperature
    
    def _get_system_prompt(self) -> str:
        """System prompt for structured (non-streaming) agent"""
        return """You are Joule, an AI assistant for SAP Procure-to-Pay (P2P) data analysis.

Your capabilities:
- Query P2P datasource (suppliers, invoices, purchase orders)
- Calculate KPIs (cycle time, spend under management, approval rates)
- Provide insights and recommendations

Guidelines:
- Be concise and professional
- Provide confidence scores (0.0-1.0)
- Cite sources
- Suggest follow-up actions
- Ask for clarification if needed

Response format: AssistantResponse with message, confidence, sources, suggested_actions"""
    
    def _get_streaming_prompt(self) -> str:
        """System prompt for streaming agent (text-only)"""
        return """You are Joule, an AI assistant for SAP Procure-to-Pay (P2P) data analysis.

Your capabilities:
- Query P2P datasource (suppliers, invoices, purchase orders)
- Calculate KPIs (cycle time, spend under management, approval rates)
- Provide insights and recommendations

Guidelines:
- Be concise and professional
- Use natural conversation style
- When showing code, use markdown code fences (```python, ```sql, etc.)
- Provide helpful, actionable information"""
    
    def _register_tools(self):
        """Register tools for both agents"""
        
        # Define tool implementation once
        async def query_p2p_impl(
            ctx: RunContext[AgentDependencies],
            entity_type: str,
            filters: Optional[Dict[str, Any]] = None,
            limit: int = 100
        ) -> List[Dict[str, Any]]:
            """Query P2P datasource for entities"""
            service = ctx.deps.data_product_service
            datasource = ctx.deps.datasource
            
            try:
                entity_map = {
                    "supplier": "Supplier",
                    "invoice": "SupplierInvoice",
                    "purchase_order": "PurchaseOrder"
                }
                
                data_product = entity_map.get(entity_type.lower())
                if not data_product:
                    return [{"error": f"Unknown entity type: {entity_type}"}]
                
                result = service.get_data_for_data_product(datasource, data_product)
                
                if not result.get("success"):
                    return [{"error": result.get("error", "Query failed")}]
                
                entities = result.get("data", [])
                
                if filters:
                    entities = _apply_filters(entities, filters)
                
                return entities[:limit]
                
            except Exception as e:
                return [{"error": str(e)}]
        
        # Register on structured agent
        self.agent.tool(query_p2p_impl)
        
        # Register on streaming agent
        self.streaming_agent.tool(query_p2p_impl)
    
    async def process_message(
        self,
        user_message: str,
        conversation_history: List[Dict[str, str]],
        context: Dict[str, Any]
    ) -> AssistantResponse:
        """Process message with structured output (non-streaming)"""
        deps = AgentDependencies(
            datasource=context.get("datasource", "p2p_data"),
            data_product_service=get_sqlite_data_products_service(),
            conversation_context=context
        )
        
        message_context = self._build_message_context(user_message, conversation_history)
        
        result = await self.agent.run(message_context, deps=deps)
        
        return result.output
    
    async def process_message_stream(
        self,
        user_message: str,
        conversation_history: List[Dict[str, str]],
        context: Dict[str, Any]
    ):
        """
        Process message with streaming text output
        
        Yields:
            Dict with 'type' and 'content' for delta events
            Dict with 'type' and 'response' for done event
        """
        deps = AgentDependencies(
            datasource=context.get("datasource", "p2p_data"),
            data_product_service=get_sqlite_data_products_service(),
            conversation_context=context
        )
        
        message_context = self._build_message_context(user_message, conversation_history)
        
        # Use streaming agent (text output, not structured)
        full_text = ""
        async with self.streaming_agent.run_stream(message_context, deps=deps) as result:
            # Stream text chunks as they arrive
            async for text_chunk in result.stream_text(delta=True):
                full_text += text_chunk
                yield {
                    'type': 'delta',
                    'content': text_chunk
                }
            
            # Create AssistantResponse manually from final text
            final_response = AssistantResponse(
                message=full_text,
                confidence=1.0,
                sources=[],
                suggested_actions=[],
                requires_clarification=False,
                metadata=None
            )
            
            yield {
                'type': 'done',
                'response': final_response.dict()
            }
    
    def _build_message_context(
        self,
        user_message: str,
        conversation_history: List[Dict[str, str]]
    ) -> str:
        """Build message context with conversation history"""
        if not conversation_history:
            return user_message
        
        history_text = "Conversation history:\n"
        for msg in conversation_history[-5:]:
            role = msg.get("role", "user")
            content = msg.get("content", "")
            history_text += f"{role.capitalize()}: {content}\n"
        
        history_text += f"\nUser: {user_message}"
        
        return history_text


def _apply_filters(entities: List[Dict[str, Any]], filters: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Apply filter conditions to entity list"""
    filtered = []
    
    for entity in entities:
        matches = True
        
        for field, condition in filters.items():
            if field not in entity:
                matches = False
                break
            
            entity_value = entity[field]
            
            if isinstance(condition, dict):
                if "gt" in condition and not (entity_value > condition["gt"]):
                    matches = False
                    break
                if "gte" in condition and not (entity_value >= condition["gte"]):
                    matches = False
                    break
                if "lt" in condition and not (entity_value < condition["lt"]):
                    matches = False
                    break
                if "lte" in condition and not (entity_value <= condition["lte"]):
                    matches = False
                    break
                if "eq" in condition and not (entity_value == condition["eq"]):
                    matches = False
                    break
            else:
                if entity_value != condition:
                    matches = False
                    break
        
        if matches:
            filtered.append(entity)
    
    return filtered


# Singleton instances
_agent = None
_data_product_service = None


def get_sqlite_data_products_service():
    """Get singleton SQLite data products service"""
    global _data_product_service
    if _data_product_service is None:
        _data_product_service = SQLiteDataProductsService()
    return _data_product_service


def get_joule_agent() -> JouleAgent:
    """Get singleton Joule agent instance"""
    global _agent
    if _agent is None:
        _agent = JouleAgent()
    return _agent