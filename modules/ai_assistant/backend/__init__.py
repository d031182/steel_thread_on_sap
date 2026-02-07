"""AI Assistant Module - Flask Blueprint

Provides REST API endpoints for AI agent operations.
Uses Pydantic AI + Groq for natural language processing.
Uses dependency injection for data sources (SQLite or HANA).
"""

from flask import Blueprint, request, jsonify, current_app
from functools import wraps
import logging

from .agent_service import AgentService, AgentConfig

# Create blueprint
bp = Blueprint('ai_assistant', __name__, url_prefix='/api/ai-assistant')

# Initialize logger
logger = logging.getLogger(__name__)

# Global agent service instances (per data source)
_agent_services = {}


def get_agent_service(source: str = 'sqlite') -> AgentService:
    """Get or create agent service instance with injected data source
    
    Args:
        source: Data source type ('sqlite' or 'hana')
    
    Returns:
        Configured AgentService instance with injected DataSource
    """
    global _agent_services
    
    if source not in _agent_services:
        try:
            # Get data source from Flask app (dependency injection)
            if source == 'sqlite':
                data_source = current_app.sqlite_data_source
            elif source == 'hana':
                data_source = current_app.hana_data_source
                if data_source is None:
                    raise ValueError("HANA data source not configured")
            else:
                raise ValueError(f"Invalid source: {source}")
            
            # Create agent service with injected data source
            _agent_services[source] = AgentService(data_source)
            logger.info(f"AI Agent service initialized with {source} data source")
            
        except ValueError as e:
            logger.error(f"Failed to initialize AI Agent service: {e}")
            raise
    
    return _agent_services[source]


def handle_errors(f):
    """Decorator to handle errors consistently"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except ValueError as e:
            return jsonify({
                "success": False,
                "error": str(e)
            }), 400
        except Exception as e:
            logger.error(f"Unexpected error in {f.__name__}: {e}", exc_info=True)
            return jsonify({
                "success": False,
                "error": f"Internal server error: {str(e)}"
            }), 500
    return decorated_function


@bp.route('/status', methods=['GET'])
@handle_errors
def get_status():
    """Get AI assistant status
    
    Returns:
        JSON with service status
    """
    try:
        agent = get_agent_service()
        status = agent.get_status()
        return jsonify(status)
    except ValueError as e:
        # Service not initialized (no API key)
        return jsonify({
            "service": "AI Agent (Pydantic AI + Groq)",
            "ready": False,
            "error": str(e)
        })


@bp.route('/query', methods=['POST'])
@handle_errors
def query():
    """Execute a natural language query
    
    Request body:
        {
            "prompt": "Your question here",
            "source": "sqlite",  // Optional: 'sqlite' or 'hana' (default: 'sqlite')
            "context": {  // Optional
                "data_products": ["product1", "product2"],
                "current_schema": "schema_name",
                "custom_field": "value"
            },
            "temperature": 0.1,  // Optional
            "max_tokens": 1000   // Optional
        }
    
    Returns:
        JSON with query results
    """
    data = request.get_json()
    
    # Validate required fields
    if not data or 'prompt' not in data:
        logger.warning("Query request missing 'prompt' field")
        return jsonify({
            "success": False,
            "error": "Missing required field: 'prompt'"
        }), 400
    
    prompt = data['prompt']
    source = data.get('source', 'sqlite')
    context = data.get('context')
    temperature = data.get('temperature')
    max_tokens = data.get('max_tokens')
    
    logger.info(f"AI query request: prompt='{prompt[:50]}...', source={source}")
    
    # Get agent with appropriate data source and execute query
    agent = get_agent_service(source)
    result = agent.query(
        prompt=prompt,
        context=context,
        temperature=temperature,
        max_tokens=max_tokens
    )
    
    # Log result status
    if result.get('success'):
        logger.info(f"AI query succeeded: tokens={result.get('tokens_used', 0)}")
    else:
        logger.error(f"AI query failed: {result.get('error', 'Unknown error')}")
    
    return jsonify(result)


@bp.route('/analyze-product', methods=['POST'])
@handle_errors
def analyze_product():
    """Analyze a specific data product
    
    Request body:
        {
            "data_product_name": "SupplierInvoice",
            "schema_info": {  // Optional
                "tables": ["table1", "table2"],
                "fields": ["field1", "field2"]
            },
            "question": "What insights can you provide?"  // Optional
        }
    
    Returns:
        JSON with analysis results
    """
    data = request.get_json()
    
    # Validate required fields
    if not data or 'data_product_name' not in data:
        return jsonify({
            "success": False,
            "error": "Missing required field: 'data_product_name'"
        }), 400
    
    data_product_name = data['data_product_name']
    schema_info = data.get('schema_info')
    question = data.get('question')
    
    # Get agent and analyze
    agent = get_agent_service()
    result = agent.analyze_data_product(
        data_product_name=data_product_name,
        schema_info=schema_info,
        question=question
    )
    
    return jsonify(result)


@bp.route('/generate-sql', methods=['POST'])
@handle_errors
def generate_sql():
    """Generate SQL query from natural language
    
    Request body:
        {
            "query": "Get all invoices from last month",
            "table_schema": {  // Optional
                "tables": {
                    "invoices": {
                        "columns": ["id", "date", "amount"]
                    }
                }
            }
        }
    
    Returns:
        JSON with generated SQL and explanation
    """
    data = request.get_json()
    
    # Validate required fields
    if not data or 'query' not in data:
        return jsonify({
            "success": False,
            "error": "Missing required field: 'query'"
        }), 400
    
    natural_language_query = data['query']
    table_schema = data.get('table_schema')
    
    # Get agent and generate SQL
    agent = get_agent_service()
    result = agent.generate_sql(
        natural_language_query=natural_language_query,
        table_schema=table_schema
    )
    
    return jsonify(result)


@bp.route('/config', methods=['GET'])
@handle_errors
def get_config():
    """Get current agent configuration
    
    Returns:
        JSON with configuration
    """
    agent = get_agent_service()
    config = agent.config
    
    return jsonify({
        "model": config.model,
        "temperature": config.temperature,
        "max_tokens": config.max_tokens,
        "system_prompt": config.system_prompt
    })


@bp.route('/config', methods=['POST'])
@handle_errors
def update_config():
    """Update agent configuration
    
    Request body:
        {
            "model": "groq:llama-3.1-70b-versatile",  // Optional
            "temperature": 0.1,  // Optional
            "max_tokens": 1000,  // Optional
            "system_prompt": "Your system prompt"  // Optional
        }
    
    Returns:
        JSON with updated configuration
    """
    data = request.get_json()
    
    if not data:
        return jsonify({
            "success": False,
            "error": "No configuration data provided"
        }), 400
    
    # Get agent and update config
    agent = get_agent_service()
    agent.update_config(**data)
    
    # Return updated config
    return get_config()


# Health check endpoint
@bp.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint
    
    Returns:
        JSON with health status
    """
    return jsonify({
        "status": "healthy",
        "module": "ai_assistant",
        "version": "1.0.0"
    })