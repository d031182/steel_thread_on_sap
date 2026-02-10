"""AI Agent Service using Pydantic AI + Groq

Modern AI agent implementation using Pydantic AI framework with Groq inference.
Replaces the old ctransformers-based LLM service with cloud-based inference.

Features:
- Natural language queries with database access via DataSource interface
- SQL generation and execution
- Data product analysis
- Tool-based architecture (agent can query any data source - SQLite or HANA)
- Dependency injection for data sources
"""

import os
from typing import Optional, Dict, Any, List
from dataclasses import dataclass
from pydantic_ai import Agent, RunContext
from pydantic_ai.exceptions import UserError
from dotenv import load_dotenv

from core.interfaces.data_source import DataSource

# Load environment variables
load_dotenv()


@dataclass
class AgentConfig:
    """Configuration for AI Agent"""
    model: str = "groq:llama-3.3-70b-versatile"
    temperature: float = 0.1
    max_tokens: int = 1000
    system_prompt: str = """You are a helpful AI assistant for P2P Data Products analysis.

You have access to a SQLite database with these EXACT table names (case-sensitive):
- SupplierInvoice: SupplierInvoiceID, SupplierInvoiceStatus, DocumentDate, NetAmount, Supplier
- Supplier: SupplierID, SupplierName, Country
- PurchaseOrder: PurchaseOrderID, Status, Supplier

CRITICAL SQL RULES:
1. Table/column names are CamelCase (e.g., "SupplierInvoice", "NetAmount")
2. Use single quotes for string values (e.g., WHERE Status = 'Final')
3. DO NOT escape quotes in SQL strings - use plain single quotes only
4. Common queries:
   - Count invoices: SELECT COUNT(*) FROM SupplierInvoice
   - Sum amounts: SELECT SUM(NetAmount) FROM SupplierInvoice
   - Filter by status: WHERE SupplierInvoiceStatus = 'Final'

When user asks about data, use the query_database tool with correct SQL.
Be conversational and provide clear answers based on actual results."""


class AgentService:
    """Service for AI agent operations using Pydantic AI + Groq
    
    This service provides:
    - Natural language queries on data products
    - Data analysis assistance
    - Code generation for SQL/Python
    - Documentation help
    - Direct data source querying via tools (SQLite or HANA)
    
    Uses dependency injection for data sources.
    """
    
    def __init__(self, data_source: DataSource, config: Optional[AgentConfig] = None):
        """Initialize AI Agent service with dependency injection
        
        Args:
            data_source: DataSource instance (SQLite or HANA) - REQUIRED
            config: Agent configuration (uses defaults if None)
        """
        self.data_source = data_source
        self.config = config or AgentConfig()
        self._agent = None
        self._api_key = os.getenv('GROQ_API_KEY')
        
        # Validate API key
        if not self._api_key:
            raise ValueError(
                "GROQ_API_KEY not found in environment. "
                "Please set it in .env file or environment variables."
            )
    
    def _get_agent(self) -> Agent:
        """Get or create agent instance (lazy loading)
        
        Returns:
            Configured Pydantic AI agent with data source tools
        """
        if self._agent is None:
            agent = Agent(
                self.config.model,
                system_prompt=self.config.system_prompt
            )
            
            # Capture self reference for tool closures
            data_source = self.data_source
            
            # Register data source tools using DataSource interface
            @agent.tool_plain
            def query_database(sql: str) -> Dict[str, Any]:
                """Execute a SQL query on the P2P data source (SQLite or HANA).
                
                Args:
                    sql: SQL SELECT query to execute
                
                Returns:
                    Dictionary with query results
                """
                try:
                    # Use DataSource interface execute_query method
                    result = data_source.execute_query(sql)
                    
                    if result.get('success'):
                        return {
                            "rows": result.get('rows', []),
                            "columns": result.get('columns', []),
                            "count": result.get('rowCount', 0),
                            "execution_time_ms": result.get('executionTime', 0)
                        }
                    else:
                        error_info = result.get('error', {})
                        return {
                            "error": error_info.get('message', 'Query failed'),
                            "code": error_info.get('code', 'UNKNOWN')
                        }
                except Exception as e:
                    return {"error": str(e)}
            
            @agent.tool_plain
            def get_schema_info(schema: Optional[str] = None, table_name: Optional[str] = None) -> Dict[str, Any]:
                """Get data source schema information.
                
                Args:
                    schema: Optional schema/data product name (e.g., 'SQLITE_SUPPLIERINVOICE')
                    table_name: Optional specific table name within schema
                
                Returns:
                    Dictionary with schema information
                """
                try:
                    if not schema:
                        # Get all data products
                        products = data_source.get_data_products()
                        return {
                            "data_products": [p.get('productName') for p in products],
                            "count": len(products)
                        }
                    elif table_name:
                        # Get specific table structure
                        columns = data_source.get_table_structure(schema, table_name)
                        return {
                            "schema": schema,
                            "table": table_name,
                            "columns": columns
                        }
                    else:
                        # Get tables in schema
                        tables = data_source.get_tables(schema)
                        return {
                            "schema": schema,
                            "tables": [t.get('TABLE_NAME') for t in tables],
                            "count": len(tables)
                        }
                except Exception as e:
                    return {"error": str(e)}
            
            self._agent = agent
        
        return self._agent
    
    def query(
        self,
        prompt: str,
        context: Optional[Dict[str, Any]] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None
    ) -> Dict[str, Any]:
        """Execute a query with the AI agent
        
        Args:
            prompt: User's question or request
            context: Optional context data (e.g., current data products, schema info)
            temperature: Override default temperature
            max_tokens: Override default max tokens
            
        Returns:
            Dictionary with:
                - success (bool): Whether query succeeded
                - response (str): Agent's response text
                - tokens_used (int): Estimated tokens used
                - error (str): Error message if failed
                - context_used (dict): Context that was provided to agent
        """
        import logging
        logger = logging.getLogger(__name__)
        
        try:
            agent = self._get_agent()
            
            # Build full prompt with context if provided
            full_prompt = self._build_prompt_with_context(prompt, context)
            
            logger.info(f"AI Agent query: {prompt[:100]}...")
            logger.info(f"Data source type: {self.data_source.get_connection_info().get('type', 'unknown')}")
            
            # Run agent synchronously
            result = agent.run_sync(full_prompt)
            
            logger.info(f"Agent result type: {type(result)}")
            logger.info(f"Agent result: {str(result)[:200]}...")
            
            # Extract response (Pydantic AI returns RunResult object)
            # Handle different response formats
            if hasattr(result, 'data'):
                response_text = result.data
            elif hasattr(result, 'output'):
                response_text = result.output
            else:
                # Parse from string representation
                result_str = str(result)
                if 'output=' in result_str:
                    # Extract from AgentRunResult(output='...')
                    import re
                    match = re.search(r"output=['\"](.+?)['\"](?:\)|,)", result_str, re.DOTALL)
                    if match:
                        response_text = match.group(1)
                    else:
                        response_text = result_str
                else:
                    response_text = result_str
            
            # Estimate tokens (rough approximation: 1 token ≈ 4 characters)
            tokens_used = (len(full_prompt) + len(response_text)) // 4
            
            return {
                "success": True,
                "response": response_text,
                "tokens_used": tokens_used,
                "error": None,
                "context_used": context or {}
            }
            
        except UserError as e:
            logger.error(f"User error in AI agent: {e}", exc_info=True)
            return {
                "success": False,
                "response": None,
                "tokens_used": 0,
                "error": f"User error: {str(e)}",
                "context_used": context or {}
            }
        except Exception as e:
            logger.error(f"Agent error: {e}", exc_info=True)
            return {
                "success": False,
                "response": None,
                "tokens_used": 0,
                "error": f"Agent error: {str(e)}",
                "context_used": context or {}
            }
    
    def _build_prompt_with_context(
        self,
        prompt: str,
        context: Optional[Dict[str, Any]]
    ) -> str:
        """Build prompt with context information
        
        Args:
            prompt: User's question
            context: Optional context data
            
        Returns:
            Enhanced prompt with context
        """
        if not context:
            return prompt
        
        # Build context section
        context_parts = []
        
        if "data_products" in context:
            products = context["data_products"]
            context_parts.append(
                f"Available Data Products: {', '.join(products)}"
            )
        
        if "current_schema" in context:
            schema = context["current_schema"]
            context_parts.append(
                f"Current Schema: {schema}"
            )
        
        if "recent_queries" in context:
            queries = context["recent_queries"]
            context_parts.append(
                f"Recent Queries: {queries}"
            )
        
        # Additional context fields
        for key, value in context.items():
            if key not in ["data_products", "current_schema", "recent_queries"]:
                context_parts.append(f"{key}: {value}")
        
        # Combine context with prompt
        if context_parts:
            context_str = "\n".join(context_parts)
            return f"Context:\n{context_str}\n\nQuestion: {prompt}"
        
        return prompt
    
    def analyze_data_product(
        self,
        data_product_name: str,
        schema_info: Optional[Dict[str, Any]] = None,
        question: Optional[str] = None
    ) -> Dict[str, Any]:
        """Analyze a specific data product
        
        Args:
            data_product_name: Name of the data product
            schema_info: Schema information for the data product
            question: Specific question about the data product
            
        Returns:
            Analysis results
        """
        # Build context
        context = {
            "data_product": data_product_name,
            "schema": schema_info or {}
        }
        
        # Build prompt
        if question:
            prompt = f"Analyze the data product '{data_product_name}': {question}"
        else:
            prompt = f"Provide an overview and analysis of the data product '{data_product_name}'."
        
        return self.query(prompt, context=context)
    
    def generate_sql(
        self,
        natural_language_query: str,
        table_schema: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Generate SQL from natural language
        
        Args:
            natural_language_query: Question in natural language
            table_schema: Schema information for relevant tables
            
        Returns:
            Generated SQL query and explanation
        """
        context = {
            "task": "sql_generation",
            "schema": table_schema or {}
        }
        
        prompt = (
            f"Generate a SQL query for the following request:\n{natural_language_query}\n\n"
            "Provide the SQL query and a brief explanation of what it does."
        )
        
        return self.query(prompt, context=context)
    
    def get_status(self) -> Dict[str, Any]:
        """Get agent service status
        
        Returns:
            Service status information
        """
        return {
            "service": "AI Agent (Pydantic AI + Groq)",
            "model": self.config.model,
            "api_key_configured": bool(self._api_key),
            "agent_initialized": self._agent is not None,
            "ready": bool(self._api_key)
        }
    
    def update_config(self, **kwargs) -> None:
        """Update agent configuration
        
        Args:
            **kwargs: Configuration parameters to update
                (model, temperature, max_tokens, system_prompt)
        """
        for key, value in kwargs.items():
            if hasattr(self.config, key):
                setattr(self.config, key, value)
        
        # Reset agent to pick up new config
        self._agent = None