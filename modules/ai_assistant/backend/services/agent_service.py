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
from openai import AsyncOpenAI
import httpx

from ..models import AssistantResponse, SuggestedAction
from core.interfaces.data_product_repository import IDataProductRepository
from core.services.ontology_service import get_ontology_service
from .ai_core_auth import get_ai_core_auth


class SAPAICoreOpenAI(OpenAIModel):
    """
    Custom Pydantic AI model for SAP AI Core with AI-Resource-Group header
    
    Subclasses OpenAIChatModel to inject custom httpx client with SAP-specific headers.
    This is the OFFICIAL pattern per Perplexity research (Feb 16, 2026).
    
    Source: "Extend OpenAIChatModel by subclassing and overriding request logic"
    
    Implementation: We set environment variables first, then init parent, then override provider's client
    """
    
    def __init__(self, model: str, ai_resource_group: str, access_token: str, deployment_url: str):
        """
        Initialize SAP AI Core model with custom headers
        
        Args:
            model: Model name (e.g., 'gpt-4o-mini')
            ai_resource_group: SAP AI Core resource group (e.g., 'default')
            access_token: OAuth2 access token
            deployment_url: SAP AI Core deployment URL (includes deployment ID)
        """
        # Set environment variables for parent initialization
        os.environ["OPENAI_API_KEY"] = access_token
        os.environ["OPENAI_BASE_URL"] = deployment_url
        
        # Initialize parent (creates provider with default client)
        super().__init__(model)
        
        # NOW override the provider's client with our custom one
        # CRITICAL: Use default_headers to add to ALL requests (including internal OpenAI SDK requests)
        http_client = httpx.AsyncClient(
            timeout=30.0
        )
        
        # Set default headers that will be added to every request
        http_client.headers["AI-Resource-Group"] = ai_resource_group
        
        custom_client = AsyncOpenAI(
            base_url=deployment_url,
            api_key=access_token,
            http_client=http_client,
            default_headers={"AI-Resource-Group": ai_resource_group}  # OpenAI SDK's own header mechanism
        )
        
        # Store custom client for re-injection
        self._custom_client = custom_client
        self._ai_resource_group = ai_resource_group
        
        # Replace provider's internal client (it's a private attribute)
        self._provider._client = custom_client
        
        print(f"[SAP AI Core] Initialized with custom OpenAIChatModel subclass")
        print(f"[SAP AI Core] Model: {model}, Resource Group: {ai_resource_group}")
        print(f"[SAP AI Core] Custom client stored for re-injection on every call")
    
    def _ensure_headers(self):
        """Re-inject headers before each API call (call this before agent.run)"""
        # Force provider to use our custom client again
        self._provider._client = self._custom_client
        print(f"[SAP AI Core] Headers re-injected: AI-Resource-Group={self._ai_resource_group}")


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
    
    Multi-Provider Support:
    - LiteLLM (default): OpenAI-compatible proxy for multiple models
    - Groq: Ultra-fast llama-3.3-70b via LPU
    - OpenAI: GPT-4o-mini via GitHub Models
    - SAP AI Core: Enterprise gpt-4o-mini via Azure
    
    Configuration via .env:
    - AI_PROVIDER: "groq" | "github" | "ai_core" | "litellm" (default: litellm)
    - Model-specific keys (GROQ_API_KEY, GITHUB_TOKEN, AI_CORE_*, LITELLM_*)
    
    Features:
    - Type-safe structured outputs (non-streaming)
    - Real-time text streaming (streaming mode)
    - Conversation context awareness
    - P2P database query capabilities
    """
    
    def __init__(
        self,
        model_name: Optional[str] = None,
        temperature: float = 0.7,
        max_retries: int = 2,
        provider: Optional[str] = None  # Auto-detect from env if None
    ):
        """
        Initialize Joule agent with auto-provider detection
        
        Args:
            model_name: Model name (provider-specific, uses defaults if None)
            temperature: Response randomness (0-1)
            max_retries: Validation retry attempts
            provider: Force specific provider ("groq" | "github" | "ai_core")
                     If None, reads from AI_PROVIDER env var (default: "groq")
        
        Environment Variables:
            AI_PROVIDER: Default provider ("groq" | "github" | "ai_core" | "litellm")
            
            For Groq:
            - GROQ_API_KEY: Required
            
            For GitHub Models (OpenAI):
            - GITHUB_TOKEN: Required
            - GITHUB_MODEL_NAME: Optional (default: gpt-4o-mini)
            
            For SAP AI Core:
            - AI_CORE_CLIENT_ID: Required
            - AI_CORE_CLIENT_SECRET: Required
            - AI_CORE_DEPLOYMENT_URL: Required
            - AI_CORE_RESOURCE_GROUP: Optional (default: "default")
            - AI_CORE_MODEL_NAME: Optional (default: gpt-4o-mini)
            
            For LiteLLM:
            - LITELLM_BASE_URL: Required (e.g., http://localhost:6655/litellm/v1)
            - LITELLM_API_KEY: Required
            - LITELLM_MODEL_NAME: Optional (default: gpt-4.1-mini)
        """
        # Auto-detect provider from environment
        if provider is None:
            provider = os.getenv("AI_PROVIDER", "litellm").lower()
        
        print(f"[JouleAgent] Initializing with provider: {provider}")
        
        if provider == "ai_core":
            # SAP AI Core OAuth2 configuration
            auth = get_ai_core_auth()
            access_token = auth.get_access_token()
            resource_group = os.getenv("AI_CORE_RESOURCE_GROUP", "default")
            
            # Use deployment URL directly (includes deployment ID in path)
            deployment_url = os.getenv("AI_CORE_DEPLOYMENT_URL")
            model_name = os.getenv("AI_CORE_MODEL_NAME", "gpt-4o-mini")
            
            if not deployment_url:
                raise ValueError("AI_CORE_DEPLOYMENT_URL required in .env")
            
            # Use custom SAPAICoreOpenAI subclass (Perplexity-verified pattern)
            # This injects AI-Resource-Group header via custom httpx client
            self.model = SAPAICoreOpenAI(
                model=model_name,
                ai_resource_group=resource_group,
                access_token=access_token,
                deployment_url=deployment_url
            )
        elif provider == "github":
            # GitHub Models (OpenAI-compatible with GitHub token)
            github_token = os.getenv("GITHUB_TOKEN")
            if not github_token:
                raise ValueError("GITHUB_TOKEN required for GitHub Models provider")
            
            # Default to gpt-4o-mini if not specified
            if model_name is None:
                model_name = os.getenv("GITHUB_MODEL_NAME", "gpt-4o-mini")
            
            # Use OpenAI model with GitHub endpoint
            os.environ["OPENAI_API_KEY"] = github_token
            os.environ["OPENAI_BASE_URL"] = "https://models.inference.ai.azure.com"
            
            self.model = OpenAIModel(model_name)
            print(f"[GitHub Models] Using model: {model_name}")
            print(f"[GitHub Models] Endpoint: https://models.inference.ai.azure.com")
        
        elif provider == "litellm":
            # LiteLLM (OpenAI-compatible proxy for multiple models)
            litellm_base_url = os.getenv("LITELLM_BASE_URL")
            litellm_api_key = os.getenv("LITELLM_API_KEY")
            
            if not litellm_base_url:
                raise ValueError("LITELLM_BASE_URL required for LiteLLM provider")
            if not litellm_api_key:
                raise ValueError("LITELLM_API_KEY required for LiteLLM provider")
            
            # Default to gpt-4.1-mini if not specified
            if model_name is None:
                model_name = os.getenv("LITELLM_MODEL_NAME", "gpt-4.1-mini")
            
            # Set environment variables for OpenAI model initialization
            os.environ["OPENAI_API_KEY"] = litellm_api_key
            os.environ["OPENAI_BASE_URL"] = litellm_base_url
            
            # Use OpenAI model with LiteLLM endpoint
            self.model = OpenAIModel(model_name)
            print(f"[LiteLLM] Using model: {model_name}")
            print(f"[LiteLLM] Endpoint: {litellm_base_url}")
        
        elif provider == "groq":
            # Groq (ultra-fast, LPU-powered)
            from pydantic_ai.models.groq import GroqModel
            
            groq_api_key = os.getenv("GROQ_API_KEY")
            if not groq_api_key:
                raise ValueError("GROQ_API_KEY required for Groq provider")
            
            # Default to llama-3.3-70b if not specified
            if model_name is None:
                model_name = "llama-3.3-70b-versatile"
            
            # Create Groq model instance (uses GROQ_API_KEY from environment)
            self.model = GroqModel(model_name)
            print(f"[Groq] Using model: {model_name}")
        
        else:
            raise ValueError(f"Unknown provider: {provider}. Supported: groq, github, ai_core, litellm")
        
        # Store provider for debugging
        self.provider = provider
        self.model_name = model_name if model_name else "default"
        
        # Create agents (works for both providers)
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
        return """You are Joule, an AI assistant specialized in SAP Procure-to-Pay (P2P) data analysis and business intelligence.

**FORMATTING INSTRUCTION**: Use compact markdown formatting suitable for chat interfaces:
- Use **bold** for field names/labels (e.g., **Invoice ID:** value)
- Use bullet lists with `-` for data items
- Keep spacing minimal - avoid unnecessary blank lines
- Format data inline when possible (e.g., **Field**: value on same line)
- Example: **Invoice ID**: 5100000015, **Amount**: 5900 EUR, **Status**: PENDING

## 🎯 YOUR CORE CAPABILITIES

### 1. **Data Product Discovery**
- List all available data products across sources (SQLite & HANA Cloud)
- Show data product metadata (table count, version, description)
- Explore table structures and relationships

### 2. **Smart P2P Queries**
You can automatically answer questions like:
- "Show me all data products" → Use `list_data_products` tool
- "Show number of invoices" → Generate: `SELECT COUNT(*) FROM SupplierInvoice`
- "Show invoice with highest value" → Generate: `SELECT * FROM SupplierInvoice ORDER BY InvoiceAmount DESC LIMIT 1`
- "Which supplier has most orders?" → Generate complex JOIN queries automatically
- "Show overdue invoices" → Generate date-based filters

### 3. **Multi-Source Data Access**
- **SQLite**: Local development data (P2P_data.db)
- **HANA Cloud**: Production SAP data (P2P_DATAPRODUCT_sap_bdc_*_V1 tables)
- Automatic source detection and appropriate SQL syntax

### 4. **Business Intelligence**
- Calculate KPIs (cycle time, spend under management, approval rates)
- Generate insights and recommendations
- Identify trends and anomalies
- Suggest follow-up actions

## 🏛️ DATA ARCHITECTURE

**Table Naming Conventions:**
- **SQLite**: PascalCase (e.g., PurchaseOrder, SupplierInvoice, Supplier)
- **HANA**: SAP format (e.g., P2P_DATAPRODUCT_sap_bdc_PurchaseOrder_V1)

**Key P2P Entities:**
- **PurchaseOrder** - Purchase order headers
- **PurchaseOrderItem** - Line item details  
- **Supplier** - Vendor master data
- **SupplierInvoice** - Invoice headers
- **SupplierInvoiceItem** - Invoice line items
- **PaymentTerms** - Payment conditions

## 🔧 TOOLS AT YOUR DISPOSAL

1. **list_data_products()** - Show all available data products
2. **query_p2p(entity_type, filters, limit)** - Query specific entities
3. **execute_sql(sql_query)** - Run custom SQL (SELECT only)

## 📋 INTERACTION GUIDELINES

**When user asks:**
- "Show data products" → Use `list_data_products` tool
- "Show me invoices" → Use `query_p2p` with entity_type="invoice"
- "How many suppliers?" → Use `execute_sql` with COUNT query
- Complex questions → Break down into SQL and explain approach

**Response Quality:**
- Provide confidence scores (0.0-1.0)
- Cite data sources
- Suggest follow-up questions
- Include sample queries for learning
- Format results clearly with headers and totals

**Security:** Only SELECT queries allowed. All SQL is validated and sanitized.

Response format: AssistantResponse with message, confidence, sources, suggested_actions"""
    
    def _get_streaming_prompt(self) -> str:
        """System prompt for streaming agent (text-only)"""
        return """You are Joule, an AI assistant specialized in SAP Procure-to-Pay (P2P) data analysis and business intelligence.

**FORMATTING INSTRUCTION**: Use compact markdown formatting suitable for chat interfaces:
- Use **bold** for field names/labels (e.g., **Invoice ID:** value)  
- Use bullet lists with `-` for data items
- Keep spacing minimal - avoid unnecessary blank lines
- Format data inline when possible (e.g., **Field**: value on same line)
- Example: **Invoice ID**: 5100000015, **Amount**: 5900 EUR, **Status**: PENDING

## 🎯 YOUR CORE CAPABILITIES

### 1. **Data Product Discovery**
- List all available data products across sources (SQLite & HANA Cloud)
- Show data product metadata (table count, version, description)
- Explore table structures and relationships

### 2. **Smart P2P Queries**
You can automatically answer questions like:
- "Show me all data products" → Use `list_data_products` tool
- "Show number of invoices" → Generate: `SELECT COUNT(*) FROM SupplierInvoice`
- "Show invoice with highest value" → Generate: `SELECT * FROM SupplierInvoice ORDER BY InvoiceAmount DESC LIMIT 1`
- "Which supplier has most orders?" → Generate complex JOIN queries automatically
- "Show overdue invoices" → Generate date-based filters

### 3. **Multi-Source Data Access**
- **SQLite**: Local development data (P2P_data.db)
- **HANA Cloud**: Production SAP data (P2P_DATAPRODUCT_sap_bdc_*_V1 tables)
- Automatic source detection and appropriate SQL syntax

### 4. **Business Intelligence**
- Calculate KPIs (cycle time, spend under management, approval rates)
- Generate insights and recommendations
- Identify trends and anomalies
- Suggest follow-up actions

## 🏛️ DATA ARCHITECTURE

**Table Naming Conventions:**
- **SQLite**: PascalCase (e.g., PurchaseOrder, SupplierInvoice, Supplier)
- **HANA**: SAP format (e.g., P2P_DATAPRODUCT_sap_bdc_PurchaseOrder_V1)

**Key P2P Entities:**
- **PurchaseOrder** - Purchase order headers
- **PurchaseOrderItem** - Line item details  
- **Supplier** - Vendor master data
- **SupplierInvoice** - Invoice headers
- **SupplierInvoiceItem** - Invoice line items
- **PaymentTerms** - Payment conditions

## 🔧 TOOLS AT YOUR DISPOSAL

1. **list_data_products()** - Show all available data products
2. **query_p2p(entity_type, filters, limit)** - Query specific entities
3. **execute_sql(sql_query)** - Run custom SQL (SELECT only)

## 📋 INTERACTION GUIDELINES

**When user asks:**
- "Show data products" → Use `list_data_products` tool
- "Show me invoices" → Use `query_p2p` with entity_type="invoice"
- "How many suppliers?" → Use `execute_sql` with COUNT query
- Complex questions → Break down into SQL and explain approach

**Response Quality:**
- Use natural conversation style
- When showing code, use markdown code fences (```python, ```sql, etc.)
- When showing SQL queries in responses, always use ```sql code fences
- Provide helpful, actionable information
- Include sample queries for learning
- Format results clearly with headers and totals

**Security:** Only SELECT queries allowed. All SQL is validated and sanitized."""
    
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
            datasource: Optional[str] = None
        ) -> Dict[str, Any]:
            """
            Execute a SQL query against P2P databases
            
            Args:
                sql_query: SELECT query to execute (validated for security)
                datasource: Database to query (defaults to context datasource)
            
            Returns:
                Dict with success, rows, columns, row_count, execution_time_ms
            
            Security:
            - Only SELECT queries allowed
            - Automatic LIMIT 1000 enforcement
            - SQL injection prevention
            - No DROP/INSERT/UPDATE/DELETE allowed
            """
            # Use datasource from context if not explicitly provided
            if datasource is None:
                datasource = ctx.deps.datasource
            
            try:
                # Use repository's execute_sql method directly
                # Repository already knows the correct table names for its datasource
                # The AI should use the table names from the enhanced context
                repository = ctx.deps.data_product_repository
                result = repository.execute_sql(sql_query)
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
        datasource = context.get("datasource", "p2p_data")
        
        deps = AgentDependencies(
            datasource=datasource,
            data_product_repository=repository,
            sql_execution_service=sql_execution_service,
            conversation_context=context
        )
        
        # Use enhanced context that includes HANA table names when needed
        message_context = self._build_enhanced_message_context(
            user_message, 
            conversation_history,
            datasource,
            repository
        )
        
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
        # DEBUG: Check if model still has custom client before API call
        print(f"[STREAM DEBUG] About to call streaming agent")
        print(f"[STREAM DEBUG] Model type: {type(self.streaming_agent.model)}")
        print(f"[STREAM DEBUG] Model has _provider: {hasattr(self.streaming_agent.model, '_provider')}")
        if hasattr(self.streaming_agent.model, '_provider'):
            print(f"[STREAM DEBUG] Provider client type: {type(self.streaming_agent.model._provider._client)}")
            print(f"[STREAM DEBUG] Provider client base_url: {self.streaming_agent.model._provider._client.base_url}")
            if hasattr(self.streaming_agent.model._provider._client, '_client'):
                print(f"[STREAM DEBUG] HTTP client headers: {self.streaming_agent.model._provider._client._client.headers}")
        
        datasource = context.get("datasource", "p2p_data")
        
        deps = AgentDependencies(
            datasource=datasource,
            data_product_repository=repository,
            sql_execution_service=sql_execution_service,
            conversation_context=context
        )
        
        # Use enhanced context that includes HANA table names when needed
        message_context = self._build_enhanced_message_context(
            user_message,
            conversation_history,
            datasource,
            repository
        )
        
        # CRITICAL: Re-inject headers before making API call
        if hasattr(self.streaming_agent.model, '_ensure_headers'):
            self.streaming_agent.model._ensure_headers()
        
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
    
    def _build_enhanced_message_context(
        self,
        user_message: str,
        conversation_history: List[Dict[str, str]],
        datasource: str,
        repository: IDataProductRepository
    ) -> str:
        """
        Build enhanced message context with dynamic HANA table names
        
        When datasource is 'hana', fetches actual data products and injects
        HANA-specific table names (P2P_DATAPRODUCT_sap_bdc_*_V1) into prompt.
        
        Args:
            user_message: User's question
            conversation_history: Previous messages
            datasource: Current data source ('hana', 'sqlite', 'p2p_data', etc.)
            repository: Repository for querying available data products
            
        Returns:
            Enhanced message context with data source specific information
        """
        # Start with conversation history
        base_context = self._build_message_context(user_message, conversation_history)
        
        # Add HANA-specific context if needed
        if datasource == 'hana':
            try:
                # Fetch actual data products from HANA
                products = repository.get_data_products()
                
                if products:
                    hana_context = "\n\n**IMPORTANT: HANA Cloud Data Source Active**\n"
                    hana_context += "Table names follow SAP naming convention: P2P_DATAPRODUCT_sap_bdc_[ProductName]_V1\n\n"
                    hana_context += "Available HANA tables:\n"
                    
                    # List first 10 products with actual table names from metadata
                    for product in products[:10]:
                        # product_name already contains the full HANA table name from repository
                        hana_context += f"- {product.display_name}: {product.product_name}\n"
                    
                    hana_context += "\nWhen generating SQL, ALWAYS use the full table names shown above.\n"
                    
                    # Prepend HANA context before user message
                    return hana_context + "\n" + base_context
                    
            except Exception as e:
                print(f"[JouleAgent] Warning: Could not fetch HANA data products: {e}")
        
        return base_context


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