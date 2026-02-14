"""
AI Agent Service - Pydantic AI + Groq Integration

Phase 2c: Real AI with P2P datasource query capabilities
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
    - Type-safe structured outputs
    - Conversation context awareness
    - P2P database query capabilities
    - Confidence scoring
    - Source attribution
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
        
        # Create Groq model instance (uses GROQ_API_KEY from environment automatically)
        self.model = GroqModel(model_name)
        
        # Create Pydantic AI agent
        self.agent = Agent(
            self.model,
            output_type=AssistantResponse,
            retries=max_retries,
            system_prompt=self._get_system_prompt()
        )
        
        # Register tools
        self._register_tools()
        
        # Configuration
        self.temperature = temperature
    
    def _get_system_prompt(self) -> str:
        """
        Get system prompt for Joule
        
        Returns:
            System prompt defining Joule's behavior
        """
        return """You are Joule, an AI assistant for SAP Procure-to-Pay (P2P) data analysis.

Your capabilities:
- Query P2P datasource (suppliers, invoices, purchase orders)
- Calculate KPIs (cycle time, spend under management, approval rates)
- Provide insights and recommendations
- Answer questions about P2P processes

Guidelines:
- Be concise and professional
- Provide confidence scores (0.0-1.0) for your answers
- Cite sources (table names, calculations used)
- Suggest follow-up actions when helpful
- Ask for clarification if query is ambiguous

Response format:
- Always return structured AssistantResponse
- Include: message, confidence, sources, suggested_actions
- Set requires_clarification=true if user query unclear

IMPORTANT - Code Formatting (Phase 4.1):
- When showing code, ALWAYS use markdown code fences with language specifier
- Format: ```language\\ncode here\\n```
- Supported languages: python, sql, javascript, json, yaml, bash, etc.
- Example Python: ```python\\ndef calculate_kpi():\\n    return result\\n```
- Example SQL: ```sql\\nSELECT * FROM suppliers WHERE rating > 4.5;\\n```
- This enables syntax highlighting in the UI for better readability
"""
    
    def _register_tools(self):
        """Register tools for agent"""
        
        @self.agent.tool
        async def query_p2p_datasource(
            ctx: RunContext[AgentDependencies],
            entity_type: str,
            filters: Optional[Dict[str, Any]] = None,
            limit: int = 100
        ) -> List[Dict[str, Any]]:
            """
            Query P2P datasource for entities
            
            Args:
                entity_type: Entity type (supplier, invoice, purchase_order, etc.)
                filters: Filter conditions (e.g., {"rating": {"gt": 4.5}})
                limit: Maximum results to return
            
            Returns:
                List of matching entities
            """
            service = ctx.deps.data_product_service
            datasource = ctx.deps.datasource
            
            try:
                # Map entity type to data product
                entity_map = {
                    "supplier": "Supplier",
                    "invoice": "SupplierInvoice",
                    "purchase_order": "PurchaseOrder",
                    "service_entry_sheet": "ServiceEntrySheet"
                }
                
                data_product = entity_map.get(entity_type.lower())
                if not data_product:
                    return [{
                        "error": f"Unknown entity type: {entity_type}",
                        "available_types": list(entity_map.keys())
                    }]
                
                # Get data
                result = service.get_data_for_data_product(
                    datasource=datasource,
                    data_product=data_product
                )
                
                if not result.get("success"):
                    return [{"error": result.get("error", "Query failed")}]
                
                entities = result.get("data", [])
                
                # Apply filters if provided
                if filters:
                    entities = _apply_filters(entities, filters)
                
                # Apply limit
                return entities[:limit]
                
            except Exception as e:
                return [{"error": f"Query failed: {str(e)}"}]
        
        @self.agent.tool
        async def calculate_kpi(
            ctx: RunContext[AgentDependencies],
            kpi_name: str,
            period: Optional[str] = "current_month"
        ) -> Dict[str, Any]:
            """
            Calculate P2P KPI metric
            
            Args:
                kpi_name: KPI to calculate (cycle_time, approval_rate, spend_under_management)
                period: Time period (current_month, last_quarter, ytd)
            
            Returns:
                KPI calculation result with value and metadata
            """
            # TODO: Implement KPI calculation service
            # For now, return mock data structure
            
            kpi_values = {
                "cycle_time": {"value": 14.5, "unit": "days", "target": 12.0},
                "approval_rate": {"value": 92, "unit": "%", "target": 95},
                "spend_under_management": {"value": 87, "unit": "%", "target": 90}
            }
            
            if kpi_name in kpi_values:
                return {
                    "kpi": kpi_name,
                    "period": period,
                    **kpi_values[kpi_name],
                    "status": "below_target" if kpi_values[kpi_name]["value"] < kpi_values[kpi_name]["target"] else "on_target"
                }
            else:
                return {
                    "error": f"Unknown KPI: {kpi_name}",
                    "available_kpis": list(kpi_values.keys())
                }
        
        @self.agent.tool
        async def get_schema_info(
            ctx: RunContext[AgentDependencies],
            data_product: str
        ) -> Dict[str, Any]:
            """
            Get schema information for data product
            
            Args:
                data_product: Data product name (Supplier, SupplierInvoice, etc.)
            
            Returns:
                Schema metadata (columns, types, descriptions)
            """
            service = ctx.deps.data_product_service
            datasource = ctx.deps.datasource
            
            try:
                # Get schema from service
                schema_result = service.get_schema_for_data_product(
                    datasource=datasource,
                    data_product=data_product
                )
                
                if not schema_result.get("success"):
                    return {"error": schema_result.get("error", "Schema not found")}
                
                return schema_result.get("schema", {})
                
            except Exception as e:
                return {"error": f"Failed to get schema: {str(e)}"}
    
    async def process_message(
        self,
        user_message: str,
        conversation_history: List[Dict[str, str]],
        context: Dict[str, Any]
    ) -> AssistantResponse:
        """
        Process user message with conversation context
        
        Args:
            user_message: User's message
            conversation_history: Previous messages (last N messages)
            context: Conversation context (datasource, data_product, etc.)
        
        Returns:
            Validated AssistantResponse
        """
        # Prepare dependencies
        deps = AgentDependencies(
            datasource=context.get("datasource", "p2p_data"),
            data_product_service=get_sqlite_data_products_service(),
            conversation_context=context
        )
        
        # Build context from history
        message_context = self._build_message_context(
            user_message,
            conversation_history
        )
        
        # Run agent with dependency injection
        result = await self.agent.run(
            message_context,
            deps=deps
        )
        
        # Return validated response
        return result.output
    
    async def process_message_stream(
        self,
        user_message: str,
        conversation_history: List[Dict[str, str]],
        context: Dict[str, Any]
    ):
        """
        Process user message with streaming response
        
        Yields SSE-formatted events:
        - text deltas (incremental response text)
        - tool calls (when agent uses P2P tools)
        - final result (complete AssistantResponse)
        
        Args:
            user_message: User's message
            conversation_history: Previous messages
            context: Conversation context
        
        Yields:
            Dict with event type and data
        """
        # Prepare dependencies
        deps = AgentDependencies(
            datasource=context.get("datasource", "p2p_data"),
            data_product_service=get_sqlite_data_products_service(),
            conversation_context=context
        )
        
        # Build context from history
        message_context = self._build_message_context(
            user_message,
            conversation_history
        )
        
        # Stream agent response
        async with self.agent.run_stream(message_context, deps=deps) as result:
            # Stream events as they arrive
            async for event in result.stream():
                # Text delta events (incremental response text)
                if hasattr(event, 'delta') and event.delta:
                    yield {
                        'type': 'delta',
                        'content': event.delta
                    }
                
                # Tool call events (when agent queries P2P data)
                elif hasattr(event, 'tool_name'):
                    yield {
                        'type': 'tool_call',
                        'tool_name': event.tool_name,
                        'status': 'started'
                    }
                
                # Handle other event types as needed
            
            # Final result with complete AssistantResponse
            final_result = await result.get_output()
            yield {
                'type': 'done',
                'response': final_result.dict() if hasattr(final_result, 'dict') else final_result
            }
    
    def _build_message_context(
        self,
        user_message: str,
        conversation_history: List[Dict[str, str]]
    ) -> str:
        """
        Build full message context including conversation history
        
        Args:
            user_message: Current user message
            conversation_history: Previous messages
        
        Returns:
            Full context string for agent
        """
        if not conversation_history:
            return user_message
        
        # Format conversation history
        history_text = "Conversation history:\n"
        for msg in conversation_history[-5:]:  # Last 5 messages
            role = msg.get("role", "user")
            content = msg.get("content", "")
            history_text += f"{role.capitalize()}: {content}\n"
        
        history_text += f"\nUser: {user_message}"
        
        return history_text


def _apply_filters(entities: List[Dict[str, Any]], filters: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Apply filter conditions to entity list
    
    Args:
        entities: List of entities
        filters: Filter conditions
    
    Returns:
        Filtered entities
    """
    filtered = []
    
    for entity in entities:
        matches = True
        
        for field, condition in filters.items():
            if field not in entity:
                matches = False
                break
            
            entity_value = entity[field]
            
            if isinstance(condition, dict):
                # Comparison operators
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
                # Direct equality
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
    """
    Get singleton SQLite data products service instance
    
    Returns:
        SQLiteDataProductsService instance
    """
    global _data_product_service
    if _data_product_service is None:
        _data_product_service = SQLiteDataProductsService()
    return _data_product_service


def get_joule_agent() -> JouleAgent:
    """
    Get singleton Joule agent instance
    
    Returns:
        JouleAgent instance
    """
    global _agent
    if _agent is None:
        _agent = JouleAgent()
    return _agent
