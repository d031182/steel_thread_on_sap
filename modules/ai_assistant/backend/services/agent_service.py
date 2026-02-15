"""
AI Agent Service - Pydantic AI + Groq Integration

Phase 2c: Real AI with P2P datasource query capabilities
Phase 4.4: Streaming support
"""

import os
from typing import Optional, List, Dict, Any
from dataclasses import dataclass
from pydantic_ai import Agent, RunContext
from pydantic_ai.models.openai import OpenAIModel

from ..models import AssistantResponse, SuggestedAction
from core.interfaces.data_product_repository import IDataProductRepository


@dataclass
class AgentDependencies:
    """
    Dependencies injected into agent tools
    
    NOT exposed to LLM schema - only available in tool implementations
    """
    datasource: str
    data_product_repository: IDataProductRepository  # Repository for P2P data queries (interface)
    sql_execution_service: Any  # SQL query execution service
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
        # Verify GitHub token exists in environment
        github_token = os.getenv("GITHUB_TOKEN")
        if not github_token:
            raise ValueError("GITHUB_TOKEN not found in environment")
        
        # Set environment variables for GitHub Models
        os.environ["OPENAI_API_KEY"] = github_token
        os.environ["OPENAI_BASE_URL"] = "https://models.inference.ai.azure.com"
        
        # Create GitHub Models instance with GPT-4o-mini (Best for SQL generation)
        self.model = OpenAIModel("gpt-4o-mini")
        
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
- Execute SQL queries against P2P databases (read-only, validated)
- Calculate KPIs (cycle time, spend under management, approval rates)
- Provide insights and recommendations

Database: P2P datasource (syntax varies by backend)
IMPORTANT: Table names use PascalCase (e.g., PurchaseOrder, SupplierInvoice, Supplier)

Key P2P tables with data:
- PurchaseOrder (10 rows) - Header data
- PurchaseOrderItem (20 rows) - Line items
- Supplier (10 rows) - Vendor master data
- SupplierInvoice (15 rows) - Invoice headers
- SupplierInvoiceItem (15 rows) - Invoice line items
- PaymentTerms (5 rows) - Payment terms

Available queries:
Example queries:
- SELECT * FROM PurchaseOrder LIMIT 10;
- SELECT * FROM Supplier WHERE CityName='New York';
- SELECT COUNT(*) as total_invoices FROM SupplierInvoice;

Guidelines:
- Be concise and professional
- Provide confidence scores (0.0-1.0)
- Cite sources
- Suggest follow-up actions
- Ask for clarification if needed
- When user asks about tables/schema, use SQLite system catalog queries above
- ALWAYS use PascalCase table names (PurchaseOrder, NOT purchase_orders)

Security: Only SELECT queries allowed (no INSERT/UPDATE/DELETE/DROP/CREATE)

Response format: AssistantResponse with message, confidence, sources, suggested_actions"""
    
    def _get_streaming_prompt(self) -> str:
        """System prompt for streaming agent (text-only)"""
        return """You are Joule, an AI assistant for SAP Procure-to-Pay (P2P) data analysis.

Your capabilities:
- Query P2P datasource (suppliers, invoices, purchase orders)
- Execute SQL queries against P2P databases (read-only, validated)
- Calculate KPIs (cycle time, spend under management, approval rates)
- Provide insights and recommendations

Database: P2P datasource (syntax varies by backend)
IMPORTANT: Table names use PascalCase (e.g., PurchaseOrder, SupplierInvoice, Supplier)

Key P2P tables with data:
- PurchaseOrder (10 rows) - Header data
- PurchaseOrderItem (20 rows) - Line items
- Supplier (10 rows) - Vendor master data
- SupplierInvoice (15 rows) - Invoice headers
- SupplierInvoiceItem (15 rows) - Invoice line items
- PaymentTerms (5 rows) - Payment terms

Available queries:
Example queries:
- SELECT * FROM PurchaseOrder LIMIT 10;
- SELECT * FROM Supplier WHERE CityName='New York';
- SELECT COUNT(*) as total_invoices FROM SupplierInvoice;

Guidelines:
- Be concise and professional
- Use natural conversation style
- When showing code, use markdown code fences (```python, ```sql, etc.)
- When showing SQL queries in responses, always use ```sql code fences
- Provide helpful, actionable information
- When user asks about tables/schema, use SQLite system catalog queries above
- ALWAYS use PascalCase table names (PurchaseOrder, NOT purchase_orders)

Security: Only SELECT queries allowed (no INSERT/UPDATE/DELETE/DROP/CREATE)"""
    
    def _register_tools(self):
        """Register tools for both agents"""
        
        # Tool 1: List available data products
        async def list_data_products_impl(
            ctx: RunContext[AgentDependencies]
        ) -> List[Dict[str, Any]]:
            """List all available data products"""
            repository = ctx.deps.data_product_repository
            
            try:
                products = repository.get_data_products()
                return [
                    {
                        "product_name": p.product_name,
                        "display_name": p.display_name,
                        "description": p.description,
                        "table_count": p.table_count,
                        "version": p.version
                    }
                    for p in products
                ]
            except Exception as e:
                return [{"error": str(e)}]
        
        # Tool 2: Query P2P entities (structured data product queries)
        async def query_p2p_impl(
            ctx: RunContext[AgentDependencies],
            entity_type: str,
            filters: Optional[Dict[str, Any]] = None,
            limit: int = 100
        ) -> List[Dict[str, Any]]:
            """Query P2P datasource for entities"""
            repository = ctx.deps.data_product_repository
            
            try:
                entity_map = {
                    "supplier": "Supplier",
                    "invoice": "SupplierInvoice",
                    "purchase_order": "PurchaseOrder"
                }
                
                table_name = entity_map.get(entity_type.lower())
                if not table_name:
                    return [{"error": f"Unknown entity type: {entity_type}"}]
                
                # Use repository.query_table_data() method
                result = repository.query_table_data(
                    product_name=table_name,  # For now, product_name = table_name
                    table_name=table_name,
                    limit=limit,
                    offset=0,
                    filters=filters
                )
                
                entities = result.get("rows", [])
                
                return entities
                
            except Exception as e:
                return [{"error": str(e)}]
        
        # Tool 2: Execute SQL queries (ad-hoc SQL queries)
        async def execute_sql_impl(
            ctx: RunContext[AgentDependencies],
            sql_query: str,
            datasource: str = "p2p_data"
        ) -> Dict[str, Any]:
            """
            Execute a SQL query against P2P databases
            
            Args:
                sql_query: SELECT query to execute (validated for security)
                datasource: Database to query ('p2p_data' or 'p2p_graph')
            
            Returns:
                Dict with success, rows, columns, row_count, execution_time_ms
            
            Security:
            - Only SELECT queries allowed
            - Automatic LIMIT 1000 enforcement
            - SQL injection prevention
            - No DROP/INSERT/UPDATE/DELETE allowed
            """
            service = ctx.deps.sql_execution_service
            
            try:
                result = service.execute_query(sql_query, datasource)
                return result
            except Exception as e:
                return {
                    "success": False,
                    "error": str(e),
                    "rows": [],
                    "columns": [],
                    "row_count": 0
                }
        
        # Register tools on both agents
        self.agent.tool(list_data_products_impl)
        self.agent.tool(query_p2p_impl)
        self.agent.tool(execute_sql_impl)
        
        self.streaming_agent.tool(list_data_products_impl)
        self.streaming_agent.tool(query_p2p_impl)
        self.streaming_agent.tool(execute_sql_impl)
    
    async def process_message(
        self,
        user_message: str,
        conversation_history: List[Dict[str, str]],
        context: Dict[str, Any],
        sql_execution_service: Any,
        repository: IDataProductRepository
    ) -> AssistantResponse:
        """
        Process message with structured output (non-streaming)
        
        Args:
            repository: REQUIRED - Data product repository (must be injected via DI)
        """
        deps = AgentDependencies(
            datasource=context.get("datasource", "p2p_data"),
            data_product_repository=repository,
            sql_execution_service=sql_execution_service,
            conversation_context=context
        )
        
        message_context = self._build_message_context(user_message, conversation_history)
        
        result = await self.agent.run(message_context, deps=deps)
        
        return result.output
    
    async def process_message_stream(
        self,
        user_message: str,
        conversation_history: List[Dict[str, str]],
        context: Dict[str, Any],
        sql_execution_service: Any,
        repository: IDataProductRepository
    ):
        """
        Process message with streaming text output
        
        Args:
            repository: REQUIRED - Data product repository (must be injected via DI)
        
        Yields:
            Dict with 'type' and 'content' for delta events
            Dict with 'type' and 'response' for done event
        """
        deps = AgentDependencies(
            datasource=context.get("datasource", "p2p_data"),
            data_product_repository=repository,
            sql_execution_service=sql_execution_service,
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
_sql_execution_service = None






def get_joule_agent() -> JouleAgent:
    """Get singleton Joule agent instance"""
    global _agent
    if _agent is None:
        _agent = JouleAgent()
    return _agent